"""
awesome-agent-skills scraper.
Fetches skill listings from GitHub and imports them into the Nexus registry.
Falls back to a curated offline set if GitHub is unreachable.
"""
from __future__ import annotations

import re
import urllib.request
import urllib.error
import json
from dataclasses import dataclass

from db import insert_skill, get_skill
from frontmatter import extract_from_skill_md
from security_scanner import full_scan
from models import PermissionManifest

AWESOME_LIST_URL = (
    "https://raw.githubusercontent.com/simonweniger/awesome-agent-skills/main/README.md"
)

# Offline fallback skills for when GitHub is unreachable
OFFLINE_SKILLS = [
    {
        "skill_id": "skill-text-summarizer",
        "name": "Text Summarizer",
        "version": "1.0.0",
        "description": "Summarizes long documents and articles into concise bullet points or paragraphs using configurable length and style parameters.",
        "author": "awesome-agent-skills",
        "tags": ["nlp", "summarization", "text", "documents"],
        "skill_md_content": """---
name: Text Summarizer
version: 1.0.0
author: awesome-agent-skills
description: Summarizes long documents into concise bullet points.
tags: [nlp, summarization, text, documents]
network: none
filesystem: read-only
execution: sandboxed
price_per_use: 0.002
---

# Text Summarizer

## Description
Summarizes long documents and articles into concise bullet points or paragraphs.

## Capabilities
- Extractive and abstractive summarization
- Configurable output length (short/medium/long)
- Bullet point or paragraph output modes
- Multi-document summarization

## Usage
```
Input: { "text": "...", "style": "bullets", "length": "medium" }
Output: { "summary": "...", "word_count": 120 }
```
""",
        "permissions": {"network": "none", "filesystem": "read-only", "execution": "sandboxed"},
        "price_per_use": 0.002,
    },
    {
        "skill_id": "skill-web-scraper",
        "name": "Web Content Scraper",
        "version": "1.1.0",
        "description": "Scrapes and extracts structured content from web pages. Handles JavaScript-rendered pages, pagination, and rate limiting.",
        "author": "awesome-agent-skills",
        "tags": ["web", "scraping", "extraction", "html", "data"],
        "skill_md_content": """---
name: Web Content Scraper
version: 1.1.0
author: awesome-agent-skills
description: Scrapes structured content from web pages with JS rendering support.
tags: [web, scraping, extraction, html, data]
network: external
filesystem: read-write
execution: sandboxed
price_per_use: 0.005
---

# Web Content Scraper

## Description
Scrapes and extracts structured content from web pages with JavaScript support.

## Capabilities
- Static HTML parsing with CSS selectors
- JavaScript-rendered page support (Playwright)
- Automatic pagination handling
- Rate limiting and politeness delays
- Output as JSON, CSV, or Markdown

## Usage
```
Input: { "url": "https://example.com", "selector": "article.post" }
Output: { "items": [...], "count": 42 }
```
""",
        "permissions": {"network": "external", "filesystem": "read-write", "execution": "sandboxed"},
        "price_per_use": 0.005,
    },
    {
        "skill_id": "skill-email-composer",
        "name": "Email Composer",
        "version": "1.0.0",
        "description": "Drafts professional emails from intent descriptions. Supports tone adjustment, template application, and multi-recipient handling.",
        "author": "awesome-agent-skills",
        "tags": ["email", "writing", "communication", "drafting"],
        "skill_md_content": """---
name: Email Composer
version: 1.0.0
author: awesome-agent-skills
description: Drafts professional emails from intent descriptions.
tags: [email, writing, communication, drafting]
network: none
filesystem: none
execution: none
price_per_use: 0.003
---

# Email Composer

## Description
Drafts professional emails from natural language intent descriptions.

## Capabilities
- Tone adjustment (formal, casual, assertive, friendly)
- Template application for common scenarios
- Subject line generation
- CC/BCC recipient suggestions
- Reply drafting from thread context

## Usage
```
Input: { "intent": "Follow up on the proposal sent last week", "tone": "professional" }
Output: { "subject": "...", "body": "..." }
```
""",
        "permissions": {"network": "none", "filesystem": "none", "execution": "none"},
        "price_per_use": 0.003,
    },
    {
        "skill_id": "skill-sql-generator",
        "name": "Natural Language to SQL",
        "version": "2.0.0",
        "description": "Converts natural language questions into SQL queries. Supports PostgreSQL, MySQL, and SQLite with schema-aware generation.",
        "author": "awesome-agent-skills",
        "tags": ["sql", "database", "nlp", "query", "generation"],
        "skill_md_content": """---
name: Natural Language to SQL
version: 2.0.0
author: awesome-agent-skills
description: Converts natural language questions into accurate SQL queries.
tags: [sql, database, nlp, query, generation]
network: none
filesystem: read-only
execution: sandboxed
price_per_use: 0.004
---

# Natural Language to SQL

## Description
Converts natural language questions into SQL queries with schema awareness.

## Capabilities
- Schema-aware query generation
- JOIN inference from natural language
- Support for PostgreSQL, MySQL, SQLite
- Query explanation in plain English
- Query optimization suggestions

## Usage
```
Input: { "question": "Show top 10 customers by revenue last month", "schema": {...} }
Output: { "sql": "SELECT ...", "explanation": "..." }
```
""",
        "permissions": {"network": "none", "filesystem": "read-only", "execution": "sandboxed"},
        "price_per_use": 0.004,
    },
    {
        "skill_id": "skill-calendar-planner",
        "name": "Calendar & Schedule Planner",
        "version": "1.0.0",
        "description": "Analyzes availability and creates optimized meeting schedules. Handles time zones, recurring events, and conflict resolution.",
        "author": "awesome-agent-skills",
        "tags": ["calendar", "scheduling", "planning", "time-management"],
        "skill_md_content": """---
name: Calendar & Schedule Planner
version: 1.0.0
author: awesome-agent-skills
description: Creates optimized meeting schedules with timezone and conflict handling.
tags: [calendar, scheduling, planning, time-management]
network: internal-only
filesystem: none
execution: sandboxed
price_per_use: 0.002
---

# Calendar & Schedule Planner

## Description
Analyzes availability and creates optimized meeting schedules across time zones.

## Capabilities
- Multi-timezone availability analysis
- Conflict detection and resolution suggestions
- Recurring event pattern generation
- Meeting priority scoring
- Calendar export (iCal format)

## Usage
```
Input: { "participants": [...], "duration": 60, "preferences": {...} }
Output: { "slots": [...], "recommended": "2024-01-15T14:00Z" }
```
""",
        "permissions": {"network": "internal-only", "filesystem": "none", "execution": "sandboxed"},
        "price_per_use": 0.002,
    },
]


@dataclass
class ScrapeResult:
    added: int = 0
    skipped: int = 0
    errors: int = 0
    source: str = "github"
    details: list[str] = None

    def __post_init__(self):
        if self.details is None:
            self.details = []


def _fetch_url(url: str, timeout: int = 10) -> str | None:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "nexus-scraper/1.0"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.read().decode("utf-8")
    except Exception:
        return None


def _parse_awesome_list(readme: str) -> list[dict]:
    """Extract skill entries from awesome-agent-skills README format."""
    skills = []
    # Pattern: ## Section\n- [Name](url) - description
    for match in re.finditer(r'\[([^\]]+)\]\((https?://[^\)]+)\)\s*[-–]\s*([^\n]+)', readme):
        name, url, description = match.group(1), match.group(2), match.group(3).strip()
        if "github.com" in url and "SKILL.md" not in url:
            # Try fetching SKILL.md from the repo
            raw_url = url.replace("github.com", "raw.githubusercontent.com").replace("/tree/", "/") + "/main/SKILL.md"
            skills.append({"name": name, "url": url, "raw_url": raw_url, "description": description})
    return skills


def _import_skill_from_github(entry: dict) -> dict | None:
    """Fetch and parse a skill from a GitHub URL."""
    content = _fetch_url(entry["raw_url"])
    if not content:
        return None

    meta = extract_from_skill_md(content)
    skill_id = f"skill-{re.sub(r'[^a-z0-9]', '-', (meta.get('name') or entry['name']).lower())}"

    return {
        "skill_id": skill_id,
        "name": meta.get("name") or entry["name"],
        "version": str(meta.get("version", "1.0.0")),
        "description": meta.get("description") or entry["description"],
        "author": meta.get("author", "awesome-agent-skills"),
        "tags": meta.get("tags") or [],
        "skill_md_content": content,
        "permissions": {
            "network": meta.get("network", "none"),
            "filesystem": meta.get("filesystem", "none"),
            "execution": meta.get("execution", "none"),
        },
        "price_per_use": meta.get("price_per_use"),
        "license_fee": meta.get("license_fee"),
    }


def run_scrape(max_skills: int = 20) -> ScrapeResult:
    """
    Main scrape entry point.
    Tries GitHub first; falls back to offline skills if unavailable.
    """
    result = ScrapeResult()

    # Try fetching awesome-agent-skills list from GitHub
    readme = _fetch_url(AWESOME_LIST_URL)

    if readme:
        result.source = "github"
        entries = _parse_awesome_list(readme)[:max_skills]

        for entry in entries:
            skill_data = _import_skill_from_github(entry)
            if not skill_data:
                result.errors += 1
                result.details.append(f"Failed to fetch: {entry['name']}")
                continue

            if get_skill(skill_data["skill_id"]):
                result.skipped += 1
                result.details.append(f"Already exists: {skill_data['name']}")
                continue

            try:
                report = full_scan(
                    skill_data["skill_id"],
                    skill_data["skill_md_content"],
                    PermissionManifest(**skill_data["permissions"]),
                )
                skill_data["risk_score"] = report.risk_score
                insert_skill(skill_data)
                result.added += 1
                result.details.append(f"Added: {skill_data['name']}")
            except Exception as e:
                result.errors += 1
                result.details.append(f"Error importing {skill_data['name']}: {e}")
    else:
        # Offline fallback
        result.source = "offline"
        for skill_data in OFFLINE_SKILLS:
            if get_skill(skill_data["skill_id"]):
                result.skipped += 1
                result.details.append(f"Already exists: {skill_data['name']}")
                continue
            try:
                report = full_scan(
                    skill_data["skill_id"],
                    skill_data["skill_md_content"],
                    PermissionManifest(**skill_data["permissions"]),
                )
                skill_data["risk_score"] = report.risk_score
                insert_skill(skill_data)
                result.added += 1
                result.details.append(f"Added (offline): {skill_data['name']}")
            except Exception as e:
                result.errors += 1
                result.details.append(f"Error: {e}")

    return result


if __name__ == "__main__":
    from db import init_db
    init_db()
    r = run_scrape()
    print(f"Source: {r.source}")
    print(f"Added: {r.added}  Skipped: {r.skipped}  Errors: {r.errors}")
    for d in r.details:
        print(f"  {d}")

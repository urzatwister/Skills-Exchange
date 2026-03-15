from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uuid

from models import (
    SearchRequest, SearchResponse, SearchResult,
    PublishRequest, SkillMetadata, SecurityReport, PermissionManifest, DeveloperStats,
    NetworkScope, FilesystemScope, ExecutionScope,
)
from db import init_db, semantic_search, get_skill, list_skills, insert_skill, get_usage_stats, get_developer_stats
from security_scanner import full_scan
from payment import handle_skill_usage
from frontmatter import extract_from_skill_md
from scraper import run_scrape
from sandbox import SandboxFactory, ExecutionRequest

app = FastAPI(
    title="Nexus M2M Skill Exchange",
    description="Autonomous AI-to-AI Skill Marketplace API",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup():
    from generate_skills import generate_100_skills
    from seed import seed
    generated_skills = generate_100_skills()
    seed(generated_skills)


@app.post("/api/search", response_model=SearchResponse)
def search_skills(req: SearchRequest):
    results, total_count = semantic_search(req.problem_statement, req.offset, req.limit)
    return SearchResponse(
        results=[SearchResult(**r) for r in results],
        query=req.problem_statement,
        total=total_count,
        offset=req.offset,
        limit=req.limit,
    )


@app.get("/api/skills/{skill_id}")
def get_skill_detail(skill_id: str):
    skill = get_skill(skill_id)
    if skill is None:
        raise HTTPException(status_code=404, detail="Skill not found")
    stats = get_usage_stats(skill_id)
    return {**skill, "usage_stats": stats}


@app.get("/api/skills")
def get_all_skills(offset: int = 0, limit: int = 50):
    from db import get_total_skills_count
    skills = list_skills(offset, limit)
    total = get_total_skills_count()
    return {"skills": skills, "offset": offset, "limit": limit, "total": total}


@app.post("/api/skills/publish")
def publish_skill(req: PublishRequest):
    skill_id = f"skill-{uuid.uuid4().hex[:12]}"  # type: ignore[no-matching-overload]

    # Auto-extract frontmatter metadata if SKILL.md has embedded ---blocks---
    fm = extract_from_skill_md(req.skill_md_content)
    name = req.name or fm.get("name", "Unnamed Skill")
    description = req.description or fm.get("description", "")
    tags = req.tags or fm.get("tags") or []
    version = req.version or str(fm.get("version", "1.0.0"))

    # Merge frontmatter permissions if not explicitly set
    perms = req.permissions
    if fm.get("network") or fm.get("filesystem") or fm.get("execution"):
        perms = PermissionManifest(
            network=fm.get("network", perms.network),
            filesystem=fm.get("filesystem", perms.filesystem),
            execution=fm.get("execution", perms.execution),
        )

    report = full_scan(skill_id, req.skill_md_content, perms)

    skill_data = {
        "skill_id": skill_id,
        "name": name,
        "version": version,
        "description": description,
        "author": req.author or fm.get("author", "unknown"),
        "tags": tags,
        "skill_md_content": req.skill_md_content,
        "permissions": perms.model_dump(),
        "price_per_use": req.price_per_use or fm.get("price_per_use"),
        "license_fee": req.license_fee or fm.get("license_fee"),
        "risk_score": report.risk_score,
    }
    insert_skill(skill_data)

    return {
        "skill_id": skill_id,
        "security_report": report.model_dump(),
        "has_manifest": bool(fm),
        "status": "published" if report.passed else "published_with_warnings",
    }


@app.post("/api/skills/{skill_id}/scan", response_model=SecurityReport)
def scan_skill(skill_id: str):
    skill = get_skill(skill_id)
    if skill is None:
        raise HTTPException(status_code=404, detail="Skill not found")
    permissions = PermissionManifest(**skill.get("permissions", {}))
    return full_scan(skill_id, skill["skill_md_content"], permissions)


@app.post("/api/skills/{skill_id}/use")
def use_skill(skill_id: str, agent_id: str = "anonymous"):
    skill = get_skill(skill_id)
    if skill is None:
        raise HTTPException(status_code=404, detail="Skill not found")
    result = handle_skill_usage(skill_id, agent_id, "install")
    return {
        "skill": {
            "skill_id": skill["skill_id"],
            "name": skill["name"],
            "skill_md_content": skill["skill_md_content"],
            "permissions": skill["permissions"],
        },
        "usage": result,
    }


@app.get("/api/skills/{skill_id}/stats")
def skill_stats(skill_id: str):
    skill = get_skill(skill_id)
    if skill is None:
        raise HTTPException(status_code=404, detail="Skill not found")
    return get_usage_stats(skill_id)


@app.post("/api/skills/{skill_id}/execute")
def execute_skill(skill_id: str, code: str, language: str = "python", timeout: int = 10):
    """Execute a code snippet in the appropriate sandbox for this skill's permission level."""
    skill = get_skill(skill_id)
    if skill is None:
        raise HTTPException(status_code=404, detail="Skill not found")

    perms = skill.get("permissions", {})
    execution_scope = perms.get("execution", "none")
    allow_network = perms.get("network", "none") != "none"

    if execution_scope == "none":
        raise HTTPException(status_code=403, detail="Skill declares execution: none")

    try:
        executor = SandboxFactory.get(execution_scope)
        req = ExecutionRequest(
            code=code,
            language=language,
            timeout_seconds=timeout,
            allow_network=allow_network,
        )
        result = executor.execute(req)
        return {
            "sandbox": executor.name,
            "exit_code": result.exit_code,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "timed_out": result.timed_out,
            "success": result.success,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/developers/{author}/stats", response_model=DeveloperStats)
def developer_stats(author: str):
    """Aggregate earnings and usage stats for all skills by a given author."""
    stats = get_developer_stats(author)
    if stats["skill_count"] == 0:
        raise HTTPException(status_code=404, detail=f"No skills found for author: {author}")
    return DeveloperStats(**stats)


@app.post("/api/sync")
def sync_registry(max_skills: int = 20):
    """Scrape awesome-agent-skills and import new skills into the registry."""
    result = run_scrape(max_skills=max_skills)
    return {
        "source": result.source,
        "added": result.added,
        "skipped": result.skipped,
        "errors": result.errors,
        "details": result.details,
    }

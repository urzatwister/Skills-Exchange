"""Seed the database with sample skills for development."""
from db import init_db, insert_skill

SAMPLE_SKILLS = [
    {
        "skill_id": "skill-json-formatter",
        "name": "JSON Formatter & Validator",
        "version": "1.2.0",
        "description": "Formats, validates, and transforms JSON data. Supports JSONPath queries, schema validation, and pretty-printing with configurable indentation.",
        "author": "nexus-core",
        "tags": ["json", "formatting", "validation", "data-processing"],
        "skill_md_content": """# JSON Formatter & Validator

## Description
A comprehensive JSON processing skill that formats, validates, and transforms JSON data.

## Capabilities
- Pretty-print JSON with configurable indentation
- Validate JSON against JSON Schema
- Query JSON using JSONPath expressions
- Convert between JSON, YAML, and TOML
- Minify JSON for production use

## Usage
```
Input: { "data": "raw json string or object" }
Output: { "formatted": "...", "valid": true, "errors": [] }
```

## Requirements
- No network access needed
- Read-only filesystem access for schema files
""",
        "permissions": {"network": "none", "filesystem": "read-only", "execution": "sandboxed"},
        "price_per_use": 0.001,
        "risk_score": 5,
    },
    {
        "skill_id": "skill-csv-parser",
        "name": "CSV Data Parser",
        "version": "2.0.0",
        "description": "Parses CSV files with automatic delimiter detection, header inference, type casting, and streaming support for large files.",
        "author": "data-tools-org",
        "tags": ["csv", "parsing", "data", "etl", "streaming"],
        "skill_md_content": """# CSV Data Parser

## Description
High-performance CSV parser with intelligent type detection and streaming support.

## Capabilities
- Auto-detect delimiters (comma, tab, pipe, semicolon)
- Infer column types (string, number, date, boolean)
- Stream-process files larger than available memory
- Handle malformed CSV with configurable error policies
- Output as JSON, arrays, or typed objects

## Usage
```
Input: { "file_path": "data.csv", "options": { "header": true } }
Output: { "rows": [...], "columns": [...], "types": {...} }
```
""",
        "permissions": {"network": "none", "filesystem": "read-only", "execution": "sandboxed"},
        "price_per_use": 0.002,
        "risk_score": 8,
    },
    {
        "skill_id": "skill-api-tester",
        "name": "REST API Tester",
        "version": "1.0.0",
        "description": "Automatically tests REST API endpoints by generating requests, validating responses against OpenAPI specs, and producing test reports.",
        "author": "quality-labs",
        "tags": ["api", "testing", "rest", "openapi", "automation"],
        "skill_md_content": """# REST API Tester

## Description
Automated REST API testing skill that generates and executes test cases from OpenAPI specifications.

## Capabilities
- Parse OpenAPI/Swagger specs
- Generate test cases for all endpoints
- Validate response schemas and status codes
- Measure response times and detect regressions
- Generate HTML and JSON test reports

## Usage
```
Input: { "spec_url": "https://api.example.com/openapi.json" }
Output: { "passed": 42, "failed": 3, "report_url": "..." }
```

## Requirements
- Network access to target API required
- Filesystem write for report generation
""",
        "permissions": {"network": "external", "filesystem": "read-write", "execution": "sandboxed"},
        "price_per_use": 0.005,
        "risk_score": 25,
    },
    {
        "skill_id": "skill-code-reviewer",
        "name": "AI Code Reviewer",
        "version": "1.5.0",
        "description": "Reviews code for bugs, security vulnerabilities, performance issues, and style violations. Supports Python, JavaScript, TypeScript, Go, and Rust.",
        "author": "securedev-ai",
        "tags": ["code-review", "security", "linting", "bugs", "multi-language"],
        "skill_md_content": """# AI Code Reviewer

## Description
Comprehensive code review skill that identifies bugs, vulnerabilities, and improvements.

## Capabilities
- Detect common bug patterns (null refs, off-by-one, race conditions)
- OWASP Top 10 vulnerability scanning
- Performance anti-pattern detection
- Style and convention checking
- Suggested fixes with explanations

## Supported Languages
Python, JavaScript, TypeScript, Go, Rust

## Usage
```
Input: { "code": "...", "language": "python", "severity": "medium" }
Output: { "issues": [...], "score": 85, "suggestions": [...] }
```
""",
        "permissions": {"network": "none", "filesystem": "read-only", "execution": "none"},
        "price_per_use": 0.01,
        "risk_score": 0,
    },
    {
        "skill_id": "skill-db-migrator",
        "name": "Database Migration Generator",
        "version": "1.0.0",
        "description": "Generates database migration scripts by comparing schema states. Supports PostgreSQL, MySQL, and SQLite with rollback support.",
        "author": "db-tools",
        "tags": ["database", "migration", "sql", "schema", "postgresql", "mysql"],
        "skill_md_content": """# Database Migration Generator

## Description
Generates safe, reversible database migration scripts from schema diffs.

## Capabilities
- Compare two schema states and generate ALTER statements
- Support for PostgreSQL, MySQL, and SQLite
- Automatic rollback script generation
- Data migration helpers for column transforms
- Dry-run mode for safety

## Usage
```
Input: { "from_schema": "...", "to_schema": "...", "dialect": "postgresql" }
Output: { "up_migration": "...", "down_migration": "...", "warnings": [] }
```
""",
        "permissions": {"network": "internal-only", "filesystem": "read-write", "execution": "sandboxed"},
        "license_fee": 5.00,
        "risk_score": 15,
    },
    {
        "skill_id": "skill-image-optimizer",
        "name": "Image Optimizer",
        "version": "2.1.0",
        "description": "Optimizes images for web delivery with format conversion, resizing, compression, and responsive image set generation.",
        "author": "media-tools",
        "tags": ["image", "optimization", "compression", "webp", "responsive"],
        "skill_md_content": """# Image Optimizer

## Description
Automated image optimization for web performance.

## Capabilities
- Convert between PNG, JPEG, WebP, and AVIF
- Intelligent compression with quality targets
- Generate responsive image sets (srcset)
- Batch processing with progress tracking
- Metadata stripping for privacy

## Usage
```
Input: { "images": ["path1.png", "path2.jpg"], "target_format": "webp", "quality": 85 }
Output: { "optimized": [...], "savings_percent": 62 }
```
""",
        "permissions": {"network": "none", "filesystem": "read-write", "execution": "sandboxed"},
        "price_per_use": 0.003,
        "risk_score": 10,
    },
]

def seed(generated_skills=None):
    from generate_skills import generate_100_skills
    from db import init_db, insert_skill

    if generated_skills is None:
        generated_skills = generate_100_skills()

    all_skills = SAMPLE_SKILLS + generated_skills

    print("Initializing database...")
    init_db()
    
    print(f"Seeding {len(all_skills)} skills...")
    for skill in all_skills:
        insert_skill(skill)
        print(f"  + {skill['name']} ({skill['skill_id']})")
    print("Done!")

if __name__ == "__main__":
    seed()

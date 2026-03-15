"""SKILL.md YAML frontmatter parser — Agent Skills Specification compatible."""
import re
import yaml


def parse_frontmatter(content: str) -> tuple[dict, str]:
    """
    Parse YAML frontmatter from a SKILL.md file.

    Returns (metadata_dict, body_without_frontmatter).
    If no frontmatter is present, returns ({}, original_content).

    Frontmatter format:
        ---
        name: My Skill
        version: 1.0.0
        author: someone
        description: What it does
        tags: [tag1, tag2]
        network: none
        filesystem: read-only
        execution: sandboxed
        price_per_use: 0.001
        ---

        # My Skill
        ...rest of document...
    """
    match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
    if not match:
        return {}, content

    try:
        metadata = yaml.safe_load(match.group(1)) or {}
    except yaml.YAMLError:
        return {}, content

    body = content[match.end():]
    return metadata, body


def embed_frontmatter(metadata: dict, body: str) -> str:
    """Embed a metadata dict as YAML frontmatter into a SKILL.md body."""
    fm = yaml.dump(metadata, default_flow_style=False, allow_unicode=True).strip()
    return f"---\n{fm}\n---\n\n{body}"


def extract_from_skill_md(content: str) -> dict:
    """
    Extract all available metadata from a SKILL.md file.
    Tries frontmatter first, then falls back to heading/paragraph parsing.
    """
    fm, body = parse_frontmatter(content)

    # Fall back: name from first H1
    if "name" not in fm:
        m = re.search(r'^#\s+(.+)$', body or content, re.MULTILINE)
        if m:
            fm["name"] = m.group(1).strip()

    # Fall back: description from ## Description section or first paragraph
    if "description" not in fm:
        m = re.search(r'##\s+Description\s*\n+(.+?)(?:\n\n|\n#)', body or content, re.DOTALL)
        if m:
            fm["description"] = m.group(1).strip().replace("\n", " ")
        else:
            # First non-empty line after the heading
            lines = (body or content).split("\n")
            for line in lines:
                line = line.strip()
                if line and not line.startswith("#"):
                    fm["description"] = line
                    break

    return fm

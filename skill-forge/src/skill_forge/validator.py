"""Quality gates for skill validation."""

import re
from pathlib import Path

import yaml

from .constants import FRONTMATTER_RE, SEMVER_RE


def validate_frontmatter(path: str | Path) -> tuple[bool, str]:
    """Validate YAML frontmatter in a SKILL.md file.

    Required fields: name, description, version.
    Version must be valid semver.

    Returns:
        (passed, details) — details explains the result.
    """
    path = Path(path)

    try:
        content = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as e:
        return False, f"Cannot read file: {e}"

    fm_match = FRONTMATTER_RE.match(content)
    if not fm_match:
        # Check for empty frontmatter (--- followed immediately by ---)
        if content.startswith("---") and "\n---" in content[:10]:
            return False, "Empty frontmatter (no YAML content between --- markers)"
        return False, "Missing YAML frontmatter (file must start with ---\\n...\\n---\\n)"

    try:
        frontmatter = yaml.safe_load(fm_match.group(1))
    except yaml.YAMLError as e:
        return False, f"Invalid YAML: {e}"

    if frontmatter is None:
        return False, "Empty frontmatter (no YAML content between --- markers)"
    if not isinstance(frontmatter, dict):
        return False, f"Frontmatter must be a YAML mapping, got {type(frontmatter).__name__}"

    missing = []
    for field in ("name", "description", "version"):
        if field not in frontmatter or not str(frontmatter[field]).strip():
            missing.append(field)

    if missing:
        return False, f"Missing required field(s): {', '.join(missing)}"

    version = str(frontmatter["version"])
    if not SEMVER_RE.match(version):
        return False, f"Invalid version '{version}' — must be semver (e.g., 1.0.0)"

    return True, "Frontmatter valid"


def validate_structure(path: str | Path) -> tuple[bool, str]:
    """Validate SKILL.md has meaningful sections.

    Accepts any reasonable skill structure — Hermes skills use various
    section naming conventions (Trigger, When to Use, Prerequisites,
    Quick Reference, Overview, Steps, Usage, Role, Process, etc.)

    Only fails if: no ## sections at all, or file is unreadable.

    Returns:
        (passed, details)
    """
    path = Path(path)

    try:
        content = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as e:
        return False, f"Cannot read file: {e}"

    # Strip YAML frontmatter first
    fm_match = FRONTMATTER_RE.match(content)
    body = content[fm_match.end():] if fm_match else content

    # Find all ## headings
    headings = re.findall(r"^## (.+)$", body, re.MULTILINE)

    if not headings:
        return False, "No ## sections found — skill should have at least one section"

    # Check for empty sections
    warnings = []
    for heading in headings:
        pattern = rf"^## {re.escape(heading)}\s*\n(.*?)(?=^## |\Z)"
        section_match = re.search(pattern, body, re.MULTILINE | re.DOTALL)
        if section_match:
            section_body = section_match.group(1).strip()
            if not section_body:
                warnings.append(f"Section '## {heading}' is empty")
            elif len(section_body) < 30:
                warnings.append(f"Section '## {heading}' is very short ({len(section_body)} chars)")

    if warnings:
        return True, f"Structure OK with {len(warnings)} warning(s): {'; '.join(warnings[:3])}"

    return True, f"Structure valid ({len(headings)} sections)"


def validate_skill(path: str | Path) -> list[dict]:
    """Run all quality gates on a skill file.

    Returns list of check dicts: {check_name, passed, details}
    """
    results = []

    passed, details = validate_frontmatter(path)
    results.append({"check_name": "frontmatter", "passed": passed, "details": details})

    passed, details = validate_structure(path)
    results.append({"check_name": "structure", "passed": passed, "details": details})

    return results


def validate_all(skills_dir: str | Path) -> list[dict]:
    """Run quality gates on all skills in a directory.

    Returns list of {name, path, checks: [{check_name, passed, details}]}
    """
    skills_dir = Path(skills_dir).expanduser().resolve()
    results = []

    for skill_md in sorted(skills_dir.rglob("SKILL.md")):
        name = skill_md.parent.name
        checks = validate_skill(skill_md)
        results.append({
            "name": name,
            "path": str(skill_md),
            "checks": checks,
            "all_passed": all(c["passed"] for c in checks),
        })

    return results

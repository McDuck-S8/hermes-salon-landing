"""Hermes skill importer — scans a skills directory and registers all skills."""

import re
from pathlib import Path
from typing import Any

import yaml

from .constants import FRONTMATTER_RE
from .registry import Registry


def _parse_skill_file(path: Path) -> dict[str, Any] | None:
    """Parse a SKILL.md file into a skill dict.

    Returns None if the file cannot be parsed.
    """
    try:
        content = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None

    # Extract frontmatter
    fm_match = FRONTMATTER_RE.match(content)
    if not fm_match:
        return None

    try:
        frontmatter = yaml.safe_load(fm_match.group(1))
    except yaml.YAMLError:
        return None

    if not isinstance(frontmatter, dict):
        return None

    name = frontmatter.get("name", "")
    if not name:
        name = path.parent.name  # fallback: directory name

    # Body is everything after the frontmatter
    body = content[fm_match.end():].strip()

    return {
        "name": name,
        "category": frontmatter.get("category", ""),
        "version": str(frontmatter.get("version", "0.0.0")),
        "description": frontmatter.get("description", ""),
        "path": str(path),
        "body": body,
    }


def import_skills(
    registry: Registry,
    skills_dir: str | Path,
    verbose: bool = False,
) -> dict[str, int]:
    """Import all skills from a Hermes skills directory.

    Scans for */SKILL.md files, parses frontmatter, and registers in the database.

    Returns:
        dict with keys: imported, skipped, failed, total
    """
    skills_dir = Path(skills_dir).expanduser().resolve()

    if not skills_dir.is_dir():
        return {"imported": 0, "skipped": 0, "failed": 0, "total": 0}

    imported = 0
    skipped = 0
    failed = 0
    total = 0

    for skill_md in sorted(skills_dir.rglob("SKILL.md")):
        total += 1
        skill = _parse_skill_file(skill_md)

        if skill is None:
            failed += 1
            if verbose:
                print(f"  ✗ {skill_md.parent.name}: parse failed")
            continue

        try:
            existing = registry.get_skill(skill["name"])
            if existing and existing.get("path") == skill["path"]:
                # Same path — check if content actually changed
                if (existing.get("body") == skill["body"]
                        and existing.get("description") == skill.get("description", "")
                        and existing.get("version") == skill.get("version")):
                    skipped += 1
                    if verbose:
                        print(f"  ≈ {skill['name']}: unchanged, skipped")
                    continue

            registry.upsert_skill(
                name=skill["name"],
                category=skill.get("category"),
                version=skill.get("version"),
                path=skill["path"],
                body=skill["body"],
                description=skill.get("description", ""),
            )
            imported += 1
            if verbose:
                status = "updated" if existing else "imported"
                print(f"  ✓ {skill['name']}: {status}")

        except Exception:
            failed += 1
            if verbose:
                print(f"  ✗ {skill['name']}: database error")

    return {
        "imported": imported,
        "skipped": skipped,
        "failed": failed,
        "total": total,
    }

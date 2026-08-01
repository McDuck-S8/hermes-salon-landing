#!/usr/bin/env python3
"""
Validate that a skill declaring self_improving: true has all required eval infrastructure.
Used by self-improving-skills meta-skill before running improvement cycles.
"""
import sys
from pathlib import Path


REQUIRED_FILES = [
    "evals/cases.yaml",
    "evals/rubric.md",
    "evals/run_eval.py",
    "scripts/improve.py",
    "scripts/verify.py",
    "scripts/patch_applier.py",
]


def validate_skill(skill_dir: Path) -> tuple[bool, list[str]]:
    """Check if skill has all required eval infrastructure.
    Returns (is_valid, missing_files)."""
    missing = []
    for rel_path in REQUIRED_FILES:
        if not (skill_dir / rel_path).exists():
            missing.append(rel_path)
    return (len(missing) == 0, missing)


def main():
    if len(sys.argv) < 2:
        print("Usage: validate_eval_infrastructure.py <skill_dir>")
        sys.exit(1)

    skill_dir = Path(sys.argv[1]).resolve()
    if not skill_dir.exists():
        print(f"Error: {skill_dir} does not exist")
        sys.exit(1)

    valid, missing = validate_skill(skill_dir)
    if valid:
        print(f"✅ {skill_dir.name}: All eval infrastructure present")
        sys.exit(0)
    else:
        print(f"❌ {skill_dir.name}: Missing eval infrastructure:")
        for m in missing:
            print(f"   - {m}")
        sys.exit(1)


if __name__ == "__main__":
    main()
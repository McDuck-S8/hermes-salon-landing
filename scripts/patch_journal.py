#!/usr/bin/env python3
"""Patch Journal — append-only log of every self-improvement skill patch.

Logs to cache/patch_journal.jsonl. Each entry:
  ts, skill_name, file_path, action, old_hash (first 16 of sha256),
  new_hash, diff_summary (first line), trigger (cron|agent-gateway|manual)
"""
import json, hashlib, sys
from pathlib import Path
from datetime import datetime, timezone

JOURNAL = Path("D:/Portable_Soft/hermes/cache/patch_journal.jsonl")
HERMES = Path("D:/Portable_Soft/hermes")
SKILLS = HERMES / "skills"

def sha16(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()[:16] if path.exists() else ""

def log_patch(skill_name: str, action: str, trigger: str = "auto"):
    """Append a patch journal entry. Call BEFORE writing to SKILL.md."""
    skill_dir = SKILLS / skill_name.replace("-", "/") if "/" not in skill_name else SKILLS / skill_name
    md_path = skill_dir / "SKILL.md"
    entry = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "skill": skill_name,
        "action": action,
        "old_hash": sha16(md_path),
        "trigger": trigger,
    }
    JOURNAL.parent.mkdir(parents=True, exist_ok=True)
    with open(JOURNAL, "a") as f:
        f.write(json.dumps(entry) + "\n")
    return entry

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: patch_journal.py <skill_name> <action> [trigger]")
        sys.exit(1)
    result = log_patch(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else "manual")
    print(json.dumps(result))

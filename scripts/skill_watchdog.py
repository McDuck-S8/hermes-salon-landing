#!/usr/bin/env python3
"""Skill Watchdog — detects SKILL.md changes, validates them, auto-rollbacks bad patches.

Cycle (every 10m):
  1. Scan all skills/*/SKILL.md, compare sha256 with previous snapshot
  2. For changed files:
     a. Validate new content (YAML frontmatter, min size, structure)
     b. If VALID → log to patch_journal.jsonl, accept change
     c. If INVALID → log failure + ROLLBACK to last known-good backup
  3. Save snapshot + backup old content for next cycle

Auto-rollback: if background_review or any process corrupts a SKILL.md,
this watchdog silently reverts it within 10 minutes.
"""
import json, hashlib, sys, re
from pathlib import Path
from datetime import datetime, timezone
from shutil import copy2

HERMES = Path("D:/Portable_Soft/hermes")
SKILLS_DIR = HERMES / "skills"
SNAPSHOT_FILE = HERMES / "cache" / "skill_hashes.json"
JOURNAL_FILE = HERMES / "cache" / "patch_journal.jsonl"
BACKUPS_DIR = HERMES / "cache" / "skill_backups"
MAX_BACKUPS = 50  # keep last N backups per skill

def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()[:16]

# ── Validation ──────────────────────────────────────────────────────
MIN_SKILL_LINES = 10       # SKILL.md with <10 lines is truncated/corrupt
MAX_SKILL_LINES = 5000     # sanity cap

def validate_skill(content: str, path: Path) -> tuple[bool, str]:
    """Returns (is_valid, reason). Checks structural integrity of SKILL.md."""
    lines = content.split("\n")
    n = len(lines)

    if n < MIN_SKILL_LINES:
        return False, f"too short ({n} lines, min {MIN_SKILL_LINES})"
    if n > MAX_SKILL_LINES:
        return False, f"too long ({n} lines, max {MAX_SKILL_LINES})"

    # YAML frontmatter: must start with --- and have closing ---
    stripped = content.strip()
    if stripped.startswith("---"):
        end = stripped.find("---", 3)
        if end == -1:
            return False, "YAML frontmatter opened but never closed"
        yaml_block = stripped[3:end].strip()
        # Must have at least some content between --- ---
        if len(yaml_block) < 5:
            return False, f"YAML frontmatter too small ({len(yaml_block)} chars)"
        # Check basic YAML structure: name: field exists
        if not re.search(r'^name\s*:', yaml_block, re.MULTILINE):
            return False, "YAML frontmatter missing 'name:' field"
    else:
        # No frontmatter — still valid if it has substance
        if n < 20:
            return False, "no YAML frontmatter and too short"

    # Check for null bytes / binary corruption
    if "\x00" in content:
        return False, "null bytes detected — binary corruption"

    return True, "ok"

# ── Rollback ─────────────────────────────────────────────────────────
def rollback(skill_path: Path, skill_name: str, old_hash: str) -> bool:
    """Restore from latest backup. Returns True if restored."""
    backup_dir = BACKUPS_DIR / skill_name.replace("/", "_")
    if not backup_dir.exists():
        return False

    # Find the backup matching old_hash
    backups = sorted(backup_dir.glob("*.bak"))
    for bk in reversed(backups):
        if old_hash and old_hash in bk.stem:
            copy2(bk, skill_path)
            return True
    # Fallback: use most recent backup
    if backups:
        copy2(backups[-1], skill_path)
        return True
    return False

def save_backup(skill_path: Path, skill_name: str, hash_val: str):
    """Save current content as backup before change detection."""
    backup_dir = BACKUPS_DIR / skill_name.replace("/", "_")
    backup_dir.mkdir(parents=True, exist_ok=True)
    backup_path = backup_dir / f"{hash_val}.bak"
    if not backup_path.exists():
        copy2(skill_path, backup_path)
    # Prune old backups
    backups = sorted(backup_dir.glob("*.bak"), key=lambda p: p.stat().st_mtime)
    while len(backups) > MAX_BACKUPS:
        backups[0].unlink()
        backups = backups[1:]

# ── Main ─────────────────────────────────────────────────────────────
def main():
    if SNAPSHOT_FILE.exists():
        prev = json.loads(SNAPSHOT_FILE.read_text())
    else:
        prev = {}

    current = {}
    changes = []
    rollbacks = []

    for md_path in sorted(SKILLS_DIR.rglob("SKILL.md")):
        rel = str(md_path.relative_to(SKILLS_DIR))
        skill_name = rel.replace("\\", "/")[:-len("/SKILL.md")]  # remove /SKILL.md suffix

        try:
            new_content = md_path.read_text(encoding="utf-8")
            h = hashlib.sha256(new_content.encode()).hexdigest()[:16]
        except Exception:
            continue
        current[rel] = h

        # Always backup current content (pre-change snapshot for NEXT cycle)
        save_backup(md_path, skill_name, h)

        if rel in prev and prev[rel] != h:
            # CHANGE DETECTED — validate before accepting
            valid, reason = validate_skill(new_content, md_path)

            entry = {
                "ts": datetime.now(timezone.utc).isoformat(),
                "skill": skill_name,
                "action": "updated" if valid else "ROLLED_BACK",
                "old_hash": prev[rel],
                "new_hash": h if valid else "REVERTED",
                "trigger": "watchdog",
                "file": str(md_path),
            }

            if valid:
                changes.append(entry)
            else:
                # Auto-rollback
                restored = rollback(md_path, skill_name, prev[rel])
                if restored:
                    # Re-hash after rollback
                    try:
                        restored_hash = sha256_file(md_path)
                        current[rel] = restored_hash
                    except Exception:
                        current[rel] = prev[rel]
                    entry["new_hash"] = current[rel]
                    entry["reason"] = reason
                    entry["rolled_back"] = True
                else:
                    entry["reason"] = f"{reason} (NO BACKUP)"
                    entry["rolled_back"] = False
                rollbacks.append(entry)

        elif rel not in prev:
            # New file — save snapshot
            changes.append({
                "ts": datetime.now(timezone.utc).isoformat(),
                "skill": skill_name,
                "action": "created",
                "old_hash": "",
                "new_hash": h,
                "trigger": "watchdog",
                "file": str(md_path),
            })

    # Save snapshot
    SNAPSHOT_FILE.write_text(json.dumps(current, indent=2))

    # Write journal entries
    for c in changes + rollbacks:
        with open(JOURNAL_FILE, "a") as f:
            f.write(json.dumps(c) + "\n")

    # Output
    if not changes and not rollbacks:
        print("[SILENT]")
        return

    if changes:
        print(f"  Patches accepted ({len(changes)}):")
        for c in changes:
            print(f"    ✓ {c['skill']}  {c['old_hash']}->{c['new_hash']}")

    if rollbacks:
        print(f"  🚫 ROLLBACKS ({len(rollbacks)}):")
        for c in rollbacks:
            status = "restored" if c.get("rolled_back") else "FAILED"
            print(f"    ❌ {c['skill']}  {c['reason']} — {status}")

if __name__ == "__main__":
    main()

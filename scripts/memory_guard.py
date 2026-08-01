#!/usr/bin/env python3
"""
Memory Guard — проверяет MEMORY.md перед каждым ответом агента.


> Revisit: when MEMORY.md thresholds, backup strategy, or amnesia protection changes. Last touched: 2026-07-02.
Использование:
  python scripts/memory_guard.py --check    # проверка размера
  python scripts/memory_guard.py --fix      # автозаполнение если пустой
  python scripts/memory_guard.py --status   # статус
"""
import sys
from pathlib import Path

HERMES_HOME = Path(__file__).resolve().parent.parent
MEMORY_FILE = HERMES_HOME / "MEMORY.md"
BACKUP_FILE = HERMES_HOME / "_backup" / "2026-06-21_pre_update" / "MEMORY.md"
MIN_LINES = 10
MAX_LINES = 200


def check_memory():
    """Check MEMORY.md health."""
    if not MEMORY_FILE.exists():
        return {"status": "missing", "lines": 0, "size": 0}
    
    content = MEMORY_FILE.read_text(encoding="utf-8")
    lines = len([l for l in content.split("\n") if l.strip()])
    size = len(content.encode("utf-8"))
    
    status = "ok"
    if lines < MIN_LINES:
        status = "critical"
    elif lines < 20:
        status = "warning"
    elif lines > MAX_LINES:
        status = "overflow"
    
    return {"status": status, "lines": lines, "size": size}


def fix_memory():
    """Fix MEMORY.md if too small or corrupted."""
    health = check_memory()
    
    if health["status"] == "ok":
        print(f"MEMORY.md OK: {health['lines']} lines")
        return True
    
    if health["status"] == "missing" or health["lines"] < MIN_LINES:
        # Try backup first — but only if it has VALID content
        if BACKUP_FILE.exists():
            backup = BACKUP_FILE.read_text(encoding="utf-8")
            backup_valid = _validate_backup_content(backup)
            if backup_valid:
                MEMORY_FILE.write_text(backup, encoding="utf-8")
                print(f"Restored from backup: {len(backup.splitlines())} lines")
                return True
            else:
                print(f"Backup content invalid (broken fragments), skipping")
        
        # Auto-fill with system state — PREFERRED method
        auto_fill()
        # Verify auto_fill produced enough lines
        health2 = check_memory()
        if health2["status"] != "ok":
            print(f"WARNING: auto_fill produced {health2['lines']} lines (need {MIN_LINES})")
        return True
    
    if health["status"] == "overflow":
        # Archive old entries
        content = MEMORY_FILE.read_text(encoding="utf-8")
        lines = content.split("\n")
        # Keep last 150 lines
        archived = "\n".join(lines[:50])
        kept = "\n".join(lines[-150:])
        archive_file = HERMES_HOME / "cache" / f"memory_archive_{__import__('datetime').datetime.now().strftime('%Y%m%d')}.md"
        archive_file.write_text(archived, encoding="utf-8")
        MEMORY_FILE.write_text(kept, encoding="utf-8")
        print(f"Archived {50} lines to {archive_file.name}")
        return True
    
    return False


def _validate_backup_content(content: str) -> bool:
    """Validate that backup content is readable and structured.
    
    Returns True if content looks like valid MEMORY.md with proper sections.
    Returns False if content contains broken fragments, incomplete lines, or garbage.
    """
    lines = content.split("\n")
    
    # Must have at least one ## section header
    has_section = any(line.strip().startswith("## ") for line in lines)
    if not has_section:
        return False
    
    # Count lines that look like broken fragments (start with dash-space then garbage)
    broken_count = 0
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("- ") and len(stripped) > 50:
            # Long bullet points are suspicious
            if "`" in stripped or "—" in stripped or "skill**" in stripped:
                broken_count += 1
    
    # If more than 30% of content lines are broken fragments, it's garbage
    content_lines = [l for l in lines if l.strip() and not l.startswith("#")]
    if content_lines and broken_count / len(content_lines) > 0.3:
        return False
    
    return True


def auto_fill():
    """Auto-fill MEMORY.md with essential system state.

    Writes a complete, readable MEMORY.md with three sections:
    1) Environment facts (paths, cron, network)
    2) Conventions (coding style, user preferences)
    3) Lessons learned (from past sessions)
    """
    from datetime import datetime

    today = datetime.now().strftime("%Y-%m-%d")

    # ── Try to gather live environment data ──────────────────────────
    env_lines = []
    cron_lines = []
    try:
        import sqlite3
        state_db = HERMES_HOME / "state.db"
        if state_db.exists():
            conn = sqlite3.connect(str(state_db), timeout=3)
            tables = [r[0] for r in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()]
            env_lines.append(f"- State DB tables: {', '.join(tables[:10])}")
            conn.close()
    except Exception:
        pass

    # Try to read cron jobs summary
    jobs_json = HERMES_HOME / "cron" / "jobs.json"
    if jobs_json.exists():
        try:
            import json
            data = json.loads(jobs_json.read_text(encoding="utf-8"))
            jobs = data.get("jobs", [])
            active = [j for j in jobs if j.get("enabled")]
            cron_lines.append(f"- {len(active)} active cron jobs out of {len(jobs)} total")
            for j in active[:8]:
                name = j.get("name", "?")
                sched = j.get("schedule_display", j.get("schedule", {}).get("display", "?"))
                cron_lines.append(f"  - {name}: {sched}")
        except Exception:
            pass

    env_section = "\n".join(env_lines) if env_lines else "- HERMES_HOME: D:/Portable_Soft/hermes"
    cron_section = "\n".join(cron_lines) if cron_lines else "- (cron jobs unreadable)"

    content = f"""# Agent Memory
# Auto-filled by memory_guard.py on {today}
# Keep under 200 lines. Update when new patterns emerge.

## Environment

- OS: Windows 11, Python 3.13 (shell: git-bash/MSYS)
- HERMES_HOME: D:/Portable_Soft/hermes
- State DB: D:/Portable_Soft/hermes/state.db
- Cache: cache/, Logs: logs/, Memories: memories/
{env_section}
- Proxy: SOCKS5 127.0.0.1:10806, HTTP 127.0.0.1:10809
- Telegram channel: @ai_frontier_you

## Architecture

- Event-driven pipeline: signal_daemon.py -> event_bus.py -> processors
- Bayesian scorer: bayesian_scorer.py (P(H|E) = P(E|H) * P(H) / P(E))
- Session recall: BM25 semantic search over 2750+ messages
- Procedural executor: deterministic trigger->action->log (no LLM)
- Crystal: self-learning loop (observe -> diagnose -> will -> execute -> learn)

## Cron Jobs

{cron_section}

## Conventions

- Python 3.11+, minimal dependencies (stdlib when possible)
- FTS5/BM25 for search, JSON for state, SQLite for structured data
- User writes in Russian — respond in Russian
- FREE MODELS ONLY — no paid APIs without approval
- Event-driven over cron polling
- Use `patch` for edits, `read_file` for reading, `search_files` for grep

## Lessons Learned

- PySocks: Python 3.11 but not 3.13 — use curl subprocess for proxy
- HN API: 500 stories max, detail fetches slow
- memory tool: max 2200 chars per call, batch operations needed
- Cron jobs: pin provider/model to prevent drift errors
- auto_fill() must write complete, readable content — never fragments

## What I Track

- Every decision with reasoning
- Every error and its fix
- Every user correction (as a learning opportunity)
- Knowledge gaps and how I fill them
"""
    MEMORY_FILE.write_text(content, encoding="utf-8")
    line_count = len([l for l in content.split("\n") if l.strip()])
    print(f"Auto-filled MEMORY.md: {line_count} non-empty lines, {len(content)} bytes")


def main():
    args = sys.argv[1:]
    
    if "--check" in args:
        health = check_memory()
        print(f"Status: {health['status']}")
        print(f"Lines: {health['lines']}")
        print(f"Size: {health['size']} bytes")
    elif "--fix" in args:
        fix_memory()
    elif "--status" in args:
        health = check_memory()
        print(f"MEMORY.md: {health['status']} ({health['lines']} lines, {health['size']} bytes)")
    else:
        # Default: check and fix if needed
        health = check_memory()
        if health["status"] != "ok":
            print(f"MEMORY.md {health['status']} — fixing...")
            fix_memory()
        else:
            print(f"MEMORY.md OK: {health['lines']} lines")


if __name__ == "__main__":
    main()

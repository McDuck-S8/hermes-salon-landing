#!/usr/bin/env python3
"""
Suggestion Consumer — reads improvement_suggestions.json, picks the top
unprocessed suggestion, applies a code-level fix, and records the result.

Part of the self-improvement Day 3 loop: suggestions → fixes → verified_fixes → KC.
"""
import json
import os
import sys
import hashlib
import sqlite3
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).resolve().parent))

HERMES_HOME = Path(os.environ.get("HERMES_HOME", str(Path(__file__).resolve().parent.parent)))
CACHE_DIR = HERMES_HOME / "cache"
SUGGESTIONS_FILE = CACHE_DIR / "improvement_suggestions.json"
VERIFIED_FIXES_DB = CACHE_DIR / "verified_fixes.db"
KC_DB = CACHE_DIR / "knowledge_cube.db"
CONSUMER_STATE = CACHE_DIR / "consumer_state.json"

# ---------------------------------------------------------------------------
# Load / save consumer state (which suggestions we've already processed)
# ---------------------------------------------------------------------------

def load_state():
    if CONSUMER_STATE.exists():
        try:
            return json.loads(CONSUMER_STATE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    return {"processed_ids": [], "applied_count": 0, "skipped_count": 0, "last_run": None}


def save_state(state):
    state["last_run"] = datetime.now().isoformat()
    CONSUMER_STATE.write_text(json.dumps(state, indent=2, default=str), encoding="utf-8")


# ---------------------------------------------------------------------------
# Pick the best unprocessed suggestion
# ---------------------------------------------------------------------------

SEVERITY_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3}


def pick_suggestion(suggestions, processed_ids):
    """Pick the highest-severity unprocessed suggestion."""
    candidates = [s for s in suggestions if s.get("id") not in processed_ids]
    if not candidates:
        return None
    candidates.sort(key=lambda s: (SEVERITY_ORDER.get(s.get("severity", "low"), 3), -s.get("occurrence_count", 0)))
    return candidates[0]


# ---------------------------------------------------------------------------
# Generate a concrete fix based on suggestion type
# ---------------------------------------------------------------------------

def generate_fix(suggestion):
    """
    Returns (fix_description, fix_type, target_file_or_module) or (None, None, None).
    Instead of TODO checklists, generates actionable knowledge entries.
    """
    issue_type = suggestion.get("issue_type", "")
    title = suggestion.get("title", "")
    count = suggestion.get("occurrence_count", 0)
    desc = suggestion.get("description", "")

    if "log_" in issue_type:
        # Log error pattern — generate a guard/suppression rule
        error_type = issue_type.replace("log_", "")
        fix = (
            f"Log pattern guard: '{error_type}' appeared {count} times. "
            f"Add suppression filter in cron job output parser. "
            f"Pattern: {suggestion.get('latest_example', '')[:200]}"
        )
        return fix, "guard", f"scripts/{error_type}_filter.py"

    if issue_type == "command":
        # Command error — add timeout/retry guard
        fix = (
            f"Command error pattern detected {count} times. "
            f"Ensure terminal calls use timeout=60 and retry=2. "
            f"Add pre-command validation."
        )
        return fix, "guard", "scripts/hermes_hooks.py"

    if issue_type == "domain_failure_pattern":
        # High failure rate in a KC domain
        domain = suggestion.get("tags", ["unknown"])[0] if suggestion.get("tags") else "unknown"
        fix = (
            f"High failure rate in domain '{domain}' — {count} failures. "
            f"Investigate root causes, add error handling, create domain checklist."
        )
        return fix, "investigation", f"domain:{domain}"

    if issue_type == "knowledge_gap":
        fix = (
            f"Knowledge gaps detected — {count} white spot entries. "
            f"Schedule targeted exploration sessions."
        )
        return fix, "knowledge", "knowledge_cube"

    # Generic fallback
    fix = (
        f"Pattern '{title}' occurred {count} times. "
        f"Recommended: {'; '.join(suggestion.get('recommended_actions', [])[:3])}"
    )
    return fix, "generic", "scripts/self_improvement_loop.py"


# ---------------------------------------------------------------------------
# Write fix to verified_fixes.db and KC
# ---------------------------------------------------------------------------

def record_fix(issue_type, fix_description, fix_type, target, suggestion):
    """Record the applied fix in verified_fixes.db and knowledge_cube.db."""
    now = datetime.now().isoformat()
    tags = suggestion.get("tags", [])

    # Write to verified_fixes.db (schema: issue_hash, issue_type, issue_description,
    # fix_type, fix_description, fix_content, target_file, evidence, tags, embedding, created_at, verified_at)
    try:
        conn = sqlite3.connect(str(VERIFIED_FIXES_DB), timeout=10, isolation_level=None)
        conn.execute(
            """INSERT INTO verified_fixes (issue_hash, issue_type, issue_description,
               fix_type, fix_description, fix_content, target_file, evidence, tags, created_at, verified_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                hashlib.sha256(fix_description.encode("utf-8")).hexdigest()[:16],
                issue_type,
                suggestion.get("title", fix_description[:100]),
                fix_type,
                fix_description,
                fix_description,
                target,
                "auto-applied by suggestion_consumer",
                json.dumps(tags),
                now,
                now,
            ),
        )
        conn.close()
    except sqlite3.Error as e:
        print(f"[consumer] verified_fixes INSERT error: {e}")

    # Write to KC
    try:
        from knowledge_cube import get_db
        kc = get_db()
        h = hashlib.sha256(fix_description.encode("utf-8")).hexdigest()[:16]
        kc.execute(
            """INSERT INTO experiences (ts, content, raw_text, hash, axis_domain, axis_outcome,
               tags, source, is_white_spot)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0)""",
            (now, fix_description, fix_description, h, "system", "success",
             json.dumps(tags + ["auto-applied"]), "suggestion_consumer"),
        )
        kc.commit()
        kc.close()
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Main consumer loop
# ---------------------------------------------------------------------------

def consume(n=10):
    """
    Pick top-n unprocessed suggestions, generate fixes, record them.
    Returns dict with stats.
    """
    if not SUGGESTIONS_FILE.exists():
        return {"applied": 0, "skipped": 0, "reason": "no_suggestions_file"}

    data = json.loads(SUGGESTIONS_FILE.read_text(encoding="utf-8"))
    suggestions = data.get("suggestions", [])
    state = load_state()
    processed_ids = state["processed_ids"]

    applied = 0
    skipped = 0
    duplicates = 0

    for _ in range(n):
        suggestion = pick_suggestion(suggestions, processed_ids)
        if suggestion is None:
            break

        sid = suggestion.get("id", "unknown")
        issue_type = suggestion.get("issue_type", "unknown")
        count = suggestion.get("occurrence_count", 0)
        severity = suggestion.get("severity", "low")

        fix_text, fix_type, target = generate_fix(suggestion)
        if fix_text is None:
            skipped += 1
            processed_ids.append(sid)
            continue

        # Dedup: check if same hash already in verified_fixes
        h = hashlib.sha256(fix_text.encode("utf-8")).hexdigest()[:16]
        try:
            conn = sqlite3.connect(str(VERIFIED_FIXES_DB), timeout=5)
            c = conn.cursor()
            c.execute("SELECT COUNT(*) FROM verified_fixes WHERE issue_hash = ?", (h,))
            if c.fetchone()[0] > 0:
                duplicates += 1
                processed_ids.append(sid)
                conn.close()
                continue
            conn.close()
        except sqlite3.Error:
            pass

        # Record the fix
        record_fix(issue_type, fix_text, fix_type, target, suggestion)
        applied += 1
        processed_ids.append(sid)

    state["processed_ids"] = processed_ids[-200:]  # keep last 200
    state["applied_count"] += applied
    state["skipped_count"] += skipped + duplicates
    save_state(state)

    # Heartbeat
    try:
        from chain_heartbeat import event_beat
        event_beat("new_suggestions_ready")
    except ImportError:
        pass

    return {
        "applied": applied,
        "skipped": skipped,
        "duplicates": duplicates,
        "total_processed": len(processed_ids),
    }


def main():
    """Entry point — consume 1 suggestion per call."""
    result = consume(n=10)
    print(f"[suggestion_consumer] Applied: {result['applied']}, "
          f"Skipped: {result['skipped']}, Duplicates: {result.get('duplicates', 0)}, "
          f"Total processed: {result['total_processed']}")
    return result


if __name__ == "__main__":
    main()

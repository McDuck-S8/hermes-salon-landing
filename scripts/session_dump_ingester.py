#!/usr/bin/env python3
"""
Session Dump Ingester — imports 107+ session dump JSONs into Knowledge Cube.


> Revisit: when dump ingestion logic, session parsing, or knowledge extraction changes. Last touched: 2026-07-02.
Reads sessions/request_dump_*.json, extracts user+assistant messages,
builds summaries, and stores as KC experiences.

Usage:
    python scripts/session_dump_ingester.py          # ingest all new dumps
    python scripts/session_dump_ingester.py --report  # show stats only
"""
import json
import sys
import hashlib
from pathlib import Path
from datetime import datetime

HERMES_HOME = Path(__file__).resolve().parent.parent
SESSIONS_DIR = HERMES_HOME / "sessions"
INGESTED_FILE = HERMES_HOME / "cache" / "ingested_dumps.json"
KC_DB = HERMES_HOME / "cache" / "knowledge_cube.db"

sys.path.insert(0, str(HERMES_HOME / "scripts"))


def load_ingested() -> set:
    """Load set of already-ingested filenames."""
    if INGESTED_FILE.exists():
        try:
            data = json.loads(INGESTED_FILE.read_text(encoding="utf-8"))
            return set(data.get("files", []))
        except (json.JSONDecodeError, OSError):
            return set()
    return set()


def save_ingested(files: set):
    """Save ingested filenames."""
    INGESTED_FILE.parent.mkdir(parents=True, exist_ok=True)
    INGESTED_FILE.write_text(
        json.dumps({"files": sorted(files), "updated_at": datetime.now().isoformat()},
                    indent=2, ensure_ascii=False),
        encoding="utf-8"
    )


def extract_messages(dump_path: Path) -> dict:
    """Extract user and assistant messages from a session dump."""
    try:
        data = json.loads(dump_path.read_text(encoding="utf-8", errors="replace"))
    except (json.JSONDecodeError, OSError) as e:
        return {"error": str(e)}

    body = data.get("request", {}).get("body", {})
    messages = body.get("messages", [])

    session_id = data.get("session_id", dump_path.stem)
    timestamp = data.get("timestamp", "")

    user_msgs = []
    assistant_msgs = []
    for msg in messages:
        role = msg.get("role", "")
        content = msg.get("content", "")
        if not content or not isinstance(content, str):
            continue
        if role == "user":
            user_msgs.append(content[:500])
        elif role == "assistant":
            assistant_msgs.append(content[:500])

    return {
        "session_id": session_id,
        "timestamp": timestamp,
        "user_msgs": user_msgs,
        "assistant_msgs": assistant_msgs,
        "total_messages": len(messages),
    }


def build_summary(extracted: dict) -> str:
    """Build a human-readable summary of the session."""
    if "error" in extracted:
        return f"Session dump error: {extracted['error']}"

    session_id = extracted.get("session_id", "?")
    ts = extracted.get("timestamp", "?")[:16]
    user_msgs = extracted.get("user_msgs", [])
    assistant_msgs = extracted.get("assistant_msgs", [])

    if not user_msgs:
        return f"Session {session_id} ({ts}): no user messages"

    # First user message as topic
    first_msg = user_msgs[0][:200]
    msg_count = len(user_msgs) + len(assistant_msgs)

    summary = f"Session {session_id} ({ts}): {msg_count} messages. "
    summary += f"Topic: {first_msg}"

    # Add key actions from assistant responses
    if assistant_msgs:
        last_assistant = assistant_msgs[-1][:200]
        summary += f" | Last response: {last_assistant}"

    return summary


def ingest_dumps(dry_run: bool = False) -> dict:
    """Ingest all new session dumps into Knowledge Cube."""
    if not SESSIONS_DIR.exists():
        return {"error": "sessions/ directory not found"}

    dump_files = sorted(SESSIONS_DIR.glob("request_dump_*.json"))
    if not dump_files:
        return {"total": 0, "new": 0, "skipped": 0}

    ingested = load_ingested()
    new_count = 0
    skipped_count = 0
    errors = []

    try:
        from knowledge_cube import add_experience
        has_kc = True
    except ImportError:
        has_kc = False
        errors.append("knowledge_cube module not available")

    for dump_path in dump_files:
        fname = dump_path.name
        if fname in ingested:
            skipped_count += 1
            continue

        extracted = extract_messages(dump_path)
        summary = build_summary(extracted)

        if not dry_run and has_kc:
            try:
                add_experience(
                    text=summary,
                    source="session_dump",
                    dynamic_axes={
                        "session_id": extracted.get("session_id", ""),
                        "message_count": extracted.get("total_messages", 0),
                    }
                )
                new_count += 1
                ingested.add(fname)
            except Exception as e:
                errors.append(f"{fname}: {e}")
        elif dry_run:
            print(f"  [DRY] Would ingest: {fname}")
            print(f"        {summary[:120]}")
            new_count += 1

    if not dry_run:
        save_ingested(ingested)

    return {
        "total": len(dump_files),
        "new": new_count,
        "skipped": skipped_count,
        "errors": errors,
    }


def report():
    """Show ingestion stats."""
    dump_files = list(SESSIONS_DIR.glob("request_dump_*.json")) if SESSIONS_DIR.exists() else []
    ingested = load_ingested()

    print(f"=== Session Dump Ingester ===")
    print(f"Total dumps found: {len(dump_files)}")
    print(f"Already ingested:  {len(ingested)}")
    print(f"Pending:           {len(dump_files) - len(ingested)}")

    # Show KC stats if available
    try:
        import sqlite3
        conn = sqlite3.connect(str(KC_DB))
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM experiences WHERE source='session_dump'")
        count = cur.fetchone()[0]
        conn.close()
        print(f"KC entries from dumps: {count}")
    except Exception:
        pass


if __name__ == "__main__":
    args = sys.argv[1:]

    if "--report" in args:
        report()
    elif "--dry" in args:
        result = ingest_dumps(dry_run=True)
        print(json.dumps(result, indent=2))
    else:
        result = ingest_dumps()
        print(f"Ingested: {result['new']} new, {result['skipped']} skipped")
        if result.get("errors"):
            print(f"Errors: {result['errors']}")

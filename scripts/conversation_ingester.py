#!/usr/bin/env python3
"""
Conversation Ingester — extracts full dialog content from session dumps.


> Revisit: when conversation ingestion logic, knowledge extraction, or session parsing changes. Last touched: 2026-07-02.
Unlike session_dump_ingester.py (which only takes title+count),
this script extracts actual user/assistant messages and creates
rich Knowledge Cube experiences from the conversation content.

Usage:
    python scripts/conversation_ingester.py           # ingest all new dumps
    python scripts/conversation_ingester.py --report   # show stats
    python scripts/conversation_ingester.py --limit 10 # process only 10
"""
import json
import sys
import hashlib
import re
from pathlib import Path
from datetime import datetime

HERMES_HOME = Path(__file__).resolve().parent.parent
SESSIONS_DIR = HERMES_HOME / "sessions"
INGESTED_FILE = HERMES_HOME / "cache" / "ingested_conversations.json"
KC_DB = HERMES_HOME / "cache" / "knowledge_cube.db"

sys.path.insert(0, str(HERMES_HOME / "scripts"))

# Skip patterns — don't ingest these types of messages
SKIP_PATTERNS = [
    r"^\[IMPORTANT: You are running as a scheduled",
    r"^Run .* cron job",
    r"^Execute the following cron",
]


def load_ingested() -> set:
    if INGESTED_FILE.exists():
        try:
            data = json.loads(INGESTED_FILE.read_text(encoding="utf-8"))
            return set(data.get("files", []))
        except (json.JSONDecodeError, OSError):
            return set()
    return set()


def save_ingested(files: set):
    INGESTED_FILE.parent.mkdir(parents=True, exist_ok=True)
    INGESTED_FILE.write_text(
        json.dumps({"files": sorted(files), "updated_at": datetime.now().isoformat()},
                    indent=2, ensure_ascii=False),
        encoding="utf-8"
    )


def extract_dialog(dump_path: Path) -> dict:
    """Extract full dialog from session dump."""
    try:
        data = json.loads(dump_path.read_text(encoding="utf-8-sig", errors="replace"))
    except (json.JSONDecodeError, OSError) as e:
        return {"error": str(e)}

    body = data.get("request", {}).get("body", {})
    messages = body.get("messages", [])
    session_id = data.get("session_id", dump_path.stem)
    timestamp = data.get("timestamp", "")

    dialog = []
    for msg in messages:
        role = msg.get("role", "")
        content = msg.get("content", "")
        if not content or not isinstance(content, str):
            continue
        if role in ("user", "assistant"):
            dialog.append({
                "role": role,
                "content": content[:2000],  # Cap per message
            })

    return {
        "session_id": session_id,
        "timestamp": timestamp,
        "dialog": dialog,
        "message_count": len(dialog),
    }


def should_skip(text: str) -> bool:
    """Check if message is a cron prompt or boilerplate."""
    for pattern in SKIP_PATTERNS:
        if re.match(pattern, text.strip()):
            return True
    return False


def extract_knowledge_from_dialog(dialog: list) -> list[str]:
    """Extract knowledge entries from a dialog.

    Strategy:
    - Find user requests and assistant responses
    - Look for: decisions, fixes, explanations, preferences, corrections
    - Create focused knowledge entries for each significant exchange
    """
    entries = []
    i = 0

    while i < len(dialog):
        msg = dialog[i]
        if msg["role"] != "user":
            i += 1
            continue

        user_text = msg["content"]
        if should_skip(user_text) or len(user_text) < 10:
            i += 1
            continue

        # Find next assistant message
        assistant_text = ""
        if i + 1 < len(dialog) and dialog[i + 1]["role"] == "assistant":
            assistant_text = dialog[i + 1]["content"]
            i += 2
        else:
            i += 1
            continue

        if not assistant_text or len(assistant_text) < 20:
            continue

        # Create knowledge entry
        entry = f"User request: {user_text[:300]}\nAssistant response: {assistant_text[:500]}"

        # Classify the exchange
        entry_lower = (user_text + " " + assistant_text).lower()
        tags = []
        if any(w in entry_lower for w in ["fix", "ошибк", "error", "bug", "исправ"]):
            tags.append("bugfix")
        if any(w in entry_lower for w in ["создай", "create", "новый", "new", "добав"]):
            tags.append("creation")
        if any(w in entry_lower for w in ["объясни", "explain", "почему", "why", "как"]):
            tags.append("explanation")
        if any(w in entry_lower for w in ["настрой", "config", "setup", "установ"]):
            tags.append("configuration")
        if any(w in entry_lower for w in ["запомни", "remember", "не забудь", "важно"]):
            tags.append("preference")

        if tags:
            entry = f"[{','.join(tags)}] {entry}"

        entries.append(entry)

    return entries


def ingest_conversations(limit: int = None, dry_run: bool = False) -> dict:
    """Ingest full conversation content from session dumps."""
    if not SESSIONS_DIR.exists():
        return {"error": "sessions/ directory not found"}

    dump_files = sorted(SESSIONS_DIR.glob("request_dump_*.json"))
    if not dump_files:
        return {"total": 0, "new": 0, "entries": 0}

    ingested = load_ingested()
    new_count = 0
    total_entries = 0
    errors = []

    try:
        from knowledge_cube import add_experience
        has_kc = True
    except ImportError:
        has_kc = False
        errors.append("knowledge_cube module not available")

    processed = 0
    for dump_path in dump_files:
        if limit and processed >= limit:
            break

        fname = dump_path.name
        if fname in ingested:
            continue

        extracted = extract_dialog(dump_path)
        if "error" in extracted:
            errors.append(f"{fname}: {extracted['error']}")
            ingested.add(fname)
            processed += 1
            continue

        entries = extract_knowledge_from_dialog(extracted.get("dialog", []))

        if not dry_run and has_kc and entries:
            for entry in entries:
                try:
                    add_experience(
                        text=entry[:2000],
                        source="conversation_ingester",
                        dynamic_axes={
                            "session_id": extracted.get("session_id", ""),
                            "message_count": extracted.get("message_count", 0),
                        }
                    )
                    total_entries += 1
                except Exception as e:
                    errors.append(f"KC write: {e}")
        elif dry_run and entries:
            print(f"  [DRY] {fname}: {len(entries)} entries")
            for e in entries[:2]:
                print(f"    {e[:120]}...")

        ingested.add(fname)
        new_count += 1
        processed += 1

    if not dry_run:
        save_ingested(ingested)

    return {
        "total": len(dump_files),
        "new": new_count,
        "entries": total_entries,
        "errors": errors[:10],
    }


def report():
    """Show ingestion stats."""
    dump_files = list(SESSIONS_DIR.glob("request_dump_*.json")) if SESSIONS_DIR.exists() else []
    ingested = load_ingested()

    print("=== Conversation Ingester ===")
    print(f"Total dumps:   {len(dump_files)}")
    print(f"Ingested:      {len(ingested)}")
    print(f"Pending:       {len(dump_files) - len(ingested)}")

    try:
        import sqlite3
        conn = sqlite3.connect(str(KC_DB))
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM experiences WHERE source='conversation_ingester'")
        conv_count = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM experiences WHERE source='session_dump'")
        dump_count = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM experiences")
        total = cur.fetchone()[0]
        conn.close()
        print(f"\nKC entries:")
        print(f"  conversation_ingester: {conv_count}")
        print(f"  session_dump:          {dump_count}")
        print(f"  total:                 {total}")
    except Exception:
        pass


if __name__ == "__main__":
    args = sys.argv[1:]

    if "--report" in args:
        report()
    elif "--dry" in args:
        limit = None
        if "--limit" in args:
            idx = args.index("--limit")
            if idx + 1 < len(args):
                limit = int(args[idx + 1])
        result = ingest_conversations(limit=limit, dry_run=True)
        print(json.dumps(result, indent=2))
    else:
        limit = None
        if "--limit" in args:
            idx = args.index("--limit")
            if idx + 1 < len(args):
                limit = int(args[idx + 1])
        result = ingest_conversations(limit=limit)
        print(f"Ingested: {result['new']} dumps -> {result['entries']} knowledge entries")
        if result.get("errors"):
            print(f"Errors: {result['errors'][:5]}")

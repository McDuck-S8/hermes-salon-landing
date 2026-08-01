#!/usr/bin/env python3
"""
User Needs Profiler v2 — builds rich user profile from conversations.

Filters out system prompts, cron boilerplate, and tool outputs.
Focuses on ACTUAL user messages to extract real needs.

Usage:
    python scripts/user_needs_profiler.py scan      # full scan
    python scripts/user_needs_profiler.py profile    # show profile
    python scripts/user_needs_profiler.py needs      # show unmet needs
"""
import json
import re
import sys
import sqlite3
from pathlib import Path
from datetime import datetime
from collections import Counter

HERMES_HOME = Path(__file__).resolve().parent.parent
CACHE_DIR = HERMES_HOME / "cache"
SESSIONS_DIR = HERMES_HOME / "sessions"
KC_DB = CACHE_DIR / "knowledge_cube.db"
USER_PROFILE = CACHE_DIR / "user_profile.json"

sys.path.insert(0, str(HERMES_HOME / "scripts"))

# Filters — skip these types of messages
SKIP_PREFIXES = [
    "[IMPORTANT:",
    "You are ",
    "Run the following",
    "Execute the following",
    "CRON JOB:",
    "SYSTEM:",
    "Based on the",
    "Here is",
    "The following",
    "Please ",
    "Use the",
    "## ",
    "# ",
    "```",
    "import ",
    "from ",
    "def ",
    "class ",
]

# Patterns to detect REAL user needs (not system talk)
USER_NEED_PATTERNS = [
    # Direct requests
    (r"(?:нужно|надо|нужен|нужна|нужно)\s+(.{5,80})", "need"),
    (r"(?:хочу|хотел бы|хотелось)\s+(.{5,80})", "want"),
    (r"(?:помоги|сделай|настрой|исправь|запусти|создай|добавь)\s+(.{5,80})", "request"),
    # Problems
    (r"(?:не работает|сломал|упал|ошибка|битый|crashed|broken)\s*(.{0,60})", "problem"),
    # Questions about capability
    (r"(?:можно|unable|能否|can you|can it)\s+(.{5,80})", "capability"),
    # Business needs
    (r"(?:бот|salon|клиент|заказ|цена|маркетплейс|avito|wildberries|ozon)\s*(.{0,60})", "business"),
    # Frustration signals
    (r"(?:отстой|хреново|раздражает|блин|черт|фигня|неудобно)\s*(.{0,40})", "frustration"),
]


def read_file_safe(path: Path) -> str:
    """Read file trying multiple encodings."""
    for enc in ["utf-8-sig", "utf-8", "cp1251", "latin-1"]:
        try:
            return path.read_text(encoding=enc)
        except (UnicodeDecodeError, OSError):
            continue
    return ""


def is_system_message(text: str) -> bool:
    """Check if message is system prompt or boilerplate."""
    text_stripped = text.strip()
    for prefix in SKIP_PREFIXES:
        if text_stripped.startswith(prefix):
            return True
    # Skip very long messages (>2000 chars = likely system prompt or tool output)
    if len(text) > 2000:
        return True
    # Skip messages with lots of code blocks
    if text.count("```") > 2:
        return True
    return False


def extract_user_needs(text: str) -> list[dict]:
    """Extract needs from a single user message."""
    found = []

    for pattern, category in USER_NEED_PATTERNS:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for m in matches:
            m = m.strip()[:100]
            if len(m) < 5:
                continue
            # Filter out common false positives
            if m in ("the", "this", "that", "what", "how", "the next thing"):
                continue
            found.append({"text": m, "category": category})

    return found


def scan_sessions() -> dict:
    """Scan all sessions and build user profile."""
    profile = load_profile()
    all_needs = []
    all_frustrations = []
    all_business = []
    all_user_topics = Counter()
    user_message_count = 0
    sessions_analyzed = 0

    if not SESSIONS_DIR.exists():
        return profile

    for dump_path in sorted(SESSIONS_DIR.glob("request_dump_*.json")):
        try:
            content = read_file_safe(dump_path)
            data = json.loads(content)
        except (json.JSONDecodeError, OSError):
            continue

        body = data.get("request", {}).get("body", {})
        messages = body.get("messages", [])

        for msg in messages:
            if msg.get("role") != "user":
                continue
            content = msg.get("content", "")
            if not content or not isinstance(content, str):
                continue
            if is_system_message(content):
                continue

            user_message_count += 1

            # Extract needs
            needs = extract_user_needs(content)
            for n in needs:
                if n["category"] == "frustration":
                    all_frustrations.append(n["text"])
                elif n["category"] == "business":
                    all_business.append(n["text"])
                else:
                    all_needs.append(n)

            # Extract topics (3+ char words that look like nouns)
            words = re.findall(r'\b[а-яА-Яa-zA-Z]{4,}\b', content)
            for w in words:
                w_lower = w.lower()
                if w_lower not in ("this", "that", "with", "from", "have", "been",
                                    "will", "would", "could", "should", "about",
                                    "into", "through", "during", "before", "after",
                                    "above", "below", "between", "under", "over"):
                    all_user_topics[w_lower] += 1

        sessions_analyzed += 1

    # Deduplicate and count
    need_texts = Counter(n["text"].lower() for n in all_needs)
    profile["needs"] = [{"text": t, "count": c} for t, c in need_texts.most_common(20)]
    profile["frustrations"] = [{"text": f, "count": c} for f, c in Counter(all_frustrations).most_common(10)]
    profile["business_context"] = list(set(all_business))[:15]
    profile["user_topics"] = [{"text": t, "count": c} for t, c in all_user_topics.most_common(30)]
    profile["sessions_analyzed"] = sessions_analyzed
    profile["total_user_messages"] = user_message_count

    save_profile(profile)
    return profile


def load_profile() -> dict:
    if USER_PROFILE.exists():
        try:
            return json.loads(USER_PROFILE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    return {
        "updated_at": None,
        "known_facts": {
            "role": "developer/entrepreneur",
            "location": "Russia",
            "language": "Russian (primary), English",
            "projects": ["hermes", "salon-bot", "crystal", "knowledge-cube"],
            "interests": ["AI agents", "automation", "marketplace", "crypto", "woodworking", "3D modeling"],
            "family": "son Oleg",
            "communication": "prefers action over analysis, hates describing instead of doing",
        },
        "needs": [],
        "frustrations": [],
        "business_context": [],
        "user_topics": [],
        "unmet_needs": [],
        "sessions_analyzed": 0,
        "total_user_messages": 0,
    }


def save_profile(profile: dict):
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    profile["updated_at"] = datetime.now().isoformat()
    USER_PROFILE.write_text(
        json.dumps(profile, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )


def show_profile():
    """Display current user profile."""
    profile = load_profile()

    lines = []
    lines.append("=== USER PROFILE ===")
    lines.append(f"Updated: {profile.get('updated_at', 'never')}")
    lines.append(f"Sessions: {profile.get('sessions_analyzed', 0)}")
    lines.append(f"User messages: {profile.get('total_user_messages', 0)}")

    lines.append(f"\n--- Known Facts ---")
    for k, v in profile.get("known_facts", {}).items():
        if isinstance(v, list):
            lines.append(f"  {k}: {', '.join(str(x) for x in v)}")
        else:
            lines.append(f"  {k}: {v}")

    needs = profile.get("needs", [])
    if needs:
        lines.append(f"\n--- User Needs ({len(needs)}) ---")
        for n in needs[:10]:
            lines.append(f"  [{n['count']}x] {n['text']}")

    frustrations = profile.get("frustrations", [])
    if frustrations:
        lines.append(f"\n--- Frustrations ({len(frustrations)}) ---")
        for f in frustrations[:5]:
            lines.append(f"  [{f['count']}x] {f['text']}")

    business = profile.get("business_context", [])
    if business:
        lines.append(f"\n--- Business Context ---")
        for b in business[:8]:
            lines.append(f"  - {b}")

    topics = profile.get("user_topics", [])
    if topics:
        lines.append(f"\n--- Most Discussed Topics ---")
        for t in topics[:15]:
            lines.append(f"  [{t['count']}x] {t['text']}")

    output = "\n".join(lines)
    try:
        print(output)
    except UnicodeEncodeError:
        print(output.encode("ascii", "replace").decode("ascii"))


def show_needs():
    """Show what the user needs that aren't well covered."""
    profile = load_profile()
    needs = profile.get("needs", [])

    if not needs:
        print("No needs extracted yet. Run: user_needs_profiler.py scan")
        return

    print("=== USER NEEDS (from 107 sessions) ===\n")
    print("These are real things you asked for or talked about:")
    print("The agent should be proactively working on these.\n")

    for i, n in enumerate(needs[:15], 1):
        print(f"  {i}. [{n['count']}x] {n['text']}")

    frustrations = profile.get("frustrations", [])
    if frustrations:
        print(f"\n--- Pain Points ---")
        for f in frustrations[:5]:
            print(f"  ! [{f['count']}x] {f['text']}")


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args or args[0] == "profile":
        show_profile()
    elif args[0] == "scan":
        print("Scanning 107 sessions...")
        profile = scan_sessions()
        print(f"Done: {profile['total_user_messages']} user messages from {profile['sessions_analyzed']} sessions\n")
        show_profile()
    elif args[0] == "needs":
        show_needs()
    else:
        print("Usage: user_needs_profiler.py [scan|profile|needs]")

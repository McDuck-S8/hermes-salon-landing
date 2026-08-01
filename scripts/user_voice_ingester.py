#!/usr/bin/env python3
"""
user_voice_ingester.py — Extract user signals from session DB → Knowledge Cube.

Scans user messages for frustration, commands, corrections.
Writes to KC with source='user_voice' and 8-angle dynamic_axes.

Crystal sees these via orphan_sources['user_voice'].
"""
import sqlite3
import json
import hashlib
import re
import sys
import os
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE_DB = os.path.join(ROOT, "state.db")
KC_DB = os.path.join(ROOT, "cache", "knowledge_cube.db")

sys.path.insert(0, os.path.join(ROOT, "scripts"))
from kc_axes import build_axes

# ── Signal detection patterns ─────────────────────────────────────

FRUSTRATION_PATTERNS = [
    # Russian frustration
    r"говно|мусор|плохо|сломал|не работает|тормозит|бред|ужас|фигня|дерьмо",
    r"кошмар|отвратительно|катастрофа|провал|раздража",
    r"хватит|остановись|стоп|надоело|задолбал",
    r"ты не понимаешь|это не то|не правильно|не так",
    # English frustration
    r"garbage|trash|broken|terrible|awful|horrible|useless|waste",
    r"stop it|enough|this is wrong|not what i asked",
]

COMMAND_PATTERNS = [
    # Russian commands
    r"сделай|почини|запусти|добавь|убери|покажи|сохрани|начинай",
    r"примени|обнови|измени|перепиши|выполни|запиши|отправь",
    r"установи|настрой|подключи|вызови|прогони|проверь",
    # English commands
    r"fix|build|create|add|remove|show|save|deploy|run|check",
    r"update|modify|rewrite|apply|install|configure|connect",
]

CORRECTION_PATTERNS = [
    # Russian corrections
    r"нет,?\s*(не так|не то|другой|поправь|лучше|иначе)",
    r"поправь|измени на|вместо этого|лучше сделай",
    r"я говорил|я просил|не надо|хватит",
    r"забудь|отмени|верни обратно",
    # English corrections
    r"no,?\s*(not (that|right)|wrong|different|fix|change)",
    r"change to|instead of|rather|better to",
    r"i said|i asked|don't|stop|undo|revert",
]

# Combine into compiled regex
FRUSTRATION_RE = re.compile("|".join(FRUSTRATION_PATTERNS), re.IGNORECASE)
COMMAND_RE = re.compile("|".join(COMMAND_PATTERNS), re.IGNORECASE)
CORRECTION_RE = re.compile("|".join(CORRECTION_PATTERNS), re.IGNORECASE)


def detect_signals(text: str) -> dict:
    """Detect what kind of user signal this is."""
    signals = {
        "is_frustration": bool(FRUSTRATION_RE.search(text)),
        "is_command": bool(COMMAND_RE.search(text)),
        "is_correction": bool(CORRECTION_RE.search(text)),
    }
    signals["has_signal"] = any(signals.values())
    return signals


def classify_severity(text: str, signals: dict) -> str:
    """How strong is this signal?"""
    t = text.lower()
    if signals["is_frustration"]:
        # Strong frustration words
        if any(w in t for w in ["говно", "дерьмо", "ужас", "garbage", "terrible", "broken"]):
            return "critical"
        if any(w in t for w in ["плохо", "сломал", "не работает", "не то", "not right"]):
            return "high"
        return "medium"
    if signals["is_correction"]:
        return "high"
    if signals["is_command"]:
        if any(w in t for w in ["сделай", "почини", "fix", "build", "deploy"]):
            return "high"
        return "medium"
    return "low"


def text_to_axes(text: str, signals: dict, severity: str) -> dict:
    """Build 8-angle axes for a user voice entry."""
    essence = "user_feedback"
    if signals["is_correction"]:
        action = "apply_fix"
    elif signals["is_command"]:
        action = "alert_user"
    else:
        action = "record_only"

    return build_axes(
        essence=essence,
        origin="user_session",
        temporal="during_task",
        confidence="user_confirmed",  # User said it = confirmed
        value=severity,
        applicability="now" if signals["is_command"] else "needs_context",
        action=action,
    )


def ingest_user_voice(
    state_db: str = STATE_DB,
    kc_db: str = KC_DB,
    limit: int = 1000,
    min_length: int = 15,
    since_id: int = 0,
) -> dict:
    """
    Scan user messages, detect signals, write to KC.

    Returns: { ingested: N, skipped: N, frustration: N, commands: N, corrections: N }
    """
    if not os.path.exists(state_db):
        return {"error": f"state.db not found: {state_db}"}

    # Read user messages from state.db
    src = sqlite3.connect(state_db, timeout=10)
    sc = src.cursor()
    sc.execute(
        """SELECT id, content, timestamp FROM messages
           WHERE role='user' AND id > ? AND length(content) > ?
           ORDER BY id ASC LIMIT ?""",
        (since_id, min_length, limit),
    )
    messages = sc.fetchall()
    src.close()

    if not messages:
        return {"ingested": 0, "skipped": 0, "message": "No new messages"}

    # Connect to KC
    from knowledge_cube import get_db
    kc = get_db()

    stats = {"ingested": 0, "skipped": 0, "frustration": 0, "commands": 0, "corrections": 0}

    for msg_id, content, ts in messages:
        signals = detect_signals(content)
        if not signals["has_signal"]:
            stats["skipped"] += 1
            continue

        severity = classify_severity(content, signals)
        axes = text_to_axes(content, signals, severity)

        # Create unique hash
        h = hashlib.sha256(content.encode("utf-8")).hexdigest()[:16]

        # Check if already exists
        exists = kc.execute("SELECT 1 FROM experiences WHERE hash=?", (h,)).fetchone()
        if exists:
            stats["skipped"] += 1
            continue

        # Build content summary
        summary = content[:500].replace("\n", " ").strip()

        try:
            kc.execute(
                """INSERT INTO experiences (ts, content, raw_text, hash, axis_domain,
                   axis_outcome, dynamic_axes, tags, source, is_white_spot)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 0)""",
                (
                    datetime.fromtimestamp(ts).isoformat() if ts else datetime.now().isoformat(),
                    summary,
                    content[:2000],
                    h,
                    "user_voice",
                    "neutral",
                    json.dumps(axes),
                    json.dumps(["user_voice", f"signal:{list(k for k,v in signals.items() if v and k!='has_signal')[0] if signals['has_signal'] else 'none'}"]),
                    "user_voice",
                ),
            )
            stats["ingested"] += 1
            if signals["is_frustration"]:
                stats["frustration"] += 1
            if signals["is_command"]:
                stats["commands"] += 1
            if signals["is_correction"]:
                stats["corrections"] += 1
        except sqlite3.Error:
            stats["skipped"] += 1

    kc.commit()
    return stats


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Ingest user voice into KC")
    parser.add_argument("--limit", type=int, default=500)
    parser.add_argument("--since-id", type=int, default=0)
    args = parser.parse_args()

    result = ingest_user_voice(limit=args.limit, since_id=args.since_id)
    print(json.dumps(result, indent=2))

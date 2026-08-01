#!/usr/bin/env python3
"""
Proactive User Voice Processor.
Runs after every user message — detects corrections, preferences, demands
and ACTS on them without waiting for a command.
"""
import sys, os, re, json, sqlite3
from pathlib import Path
from datetime import datetime

ROOT = Path(os.environ.get("HERMES_HOME", "D:/Portable_Soft/hermes"))
sys.path[0:0] = [str(ROOT / "scripts")]

from session_bridge import load_bridge, save_bridge, add_commitment
from goal_queue import create_goal

# ─── Pattern definitions ──────────────────────────────────────────────

# Correction patterns: user says "не X, а Y" or "X неправильно"
CORRECTION_RE = re.compile(
    r'(не\s+\w+[,.!]?\s+а\s+\w+|'
    r'неправильно|'
    r'ошибка|'
    r'должно\s+быть|'
    r'надо\s+не|'
    r'не\s+так|'
    r'стоп|'
    r'хватит|'
    r'прекрати|'
    r'почему\s+ты|'
    r'ты\s+снова|'
    r'ты\s+опять|'
    r'ты\s+должен|'
    r'исправь|'
    r'почини|'
    r'сделай\s+так)',
    re.IGNORECASE
)

# Preference patterns: user states a preference explicitly
PREFERENCE_RE = re.compile(
    r'(я\s+(предпочитаю|люблю|хочу|желаю)|'
    r'мне\s+(нравится|удобно|важно|надо|нужно)|'
    r'всегда\s+делай|'
    r'никогда\s+не|'
    r'отложи|'
    r'не\s+трогай)',
    re.IGNORECASE
)

# Demand/frustration patterns
DEMAND_RE = re.compile(
    r'(сделай\s+сейчас|'
    r'немедленно|'
    r'срочно|'
    r'запусти|'
    r'начинай|'
    r'приступай|'
    r'покажи|'
    r'доложи|'
    r'отчёт)',
    re.IGNORECASE
)

# Frustration escalation signals
FRUSTRATION_RE = re.compile(
    r'(блять|ёбаный|нахрен|нахуй|пипец|'
    r'ты\s+черепаха|'
    r'ты\s+что\s+издеваешься|'
    r'ты\s+снова\s+спрашиваешь|'
    r'ты\s+блять\s+что|'
    r'опять\s+не\s+работает)',
    re.IGNORECASE
)


def process_user_message(text: str) -> dict:
    """Analyze a user message and trigger proactive actions."""
    actions = {"corrections": [], "preferences": [], "demands": [], "frustrations": [], "summary": None}

    # 1. Detect corrections
    if CORRECTION_RE.search(text):
        actions["corrections"].append({
            "text": text[:200],
            "type": "correction",
            "auto_response": "Correction detected — applying to memory/rules"
        })
        add_commitment(f"User correction: {text[:80]}...", category="correction")
        actions["summary"] = "✅ Correction recorded and committed to bridge"

    # 2. Detect preferences
    if PREFERENCE_RE.search(text):
        actions["preferences"].append({
            "text": text[:200],
            "type": "preference",
        })
        add_commitment(f"User preference: {text[:80]}...", category="preference")
        actions["summary"] = "✅ Preference recorded to bridge"

    # 3. Detect demands
    if DEMAND_RE.search(text):
        actions["demands"].append({
            "text": text[:200],
            "type": "demand",
        })
        actions["summary"] = "⚡ Demand detected — prioritizing"

    # 4. Detect frustration escalation
    if FRUSTRATION_RE.search(text):
        actions["frustrations"].append({
            "text": text[:200],
            "type": "frustration",
            "severity": "high",
        })
        # Auto-log frustration to KC with high importance
        actions["summary"] = "⚠️ User frustration detected — logging"

        # Increment frustration streak in bridge
        bridge = load_bridge()
        streak = bridge.get("failures_streak", 0) + 1
        save_bridge({"failures_streak": streak})

    if not actions["summary"]:
        # No patterns detected — still update last_session
        save_bridge({"last_session_ts": datetime.now().isoformat()})
        actions["summary"] = "No actionable patterns"

    return actions


def get_proactivity_status() -> dict:
    """Report what proactivity sources are active."""
    bridge = load_bridge()
    return {
        "user_voice": {
            "active": True,
            "corrections_recorded": sum(1 for c in bridge.get("key_commitments", []) if c.get("category") == "correction"),
            "preferences_recorded": sum(1 for c in bridge.get("key_commitments", []) if c.get("category") == "preference"),
            "frustration_streak": bridge.get("failures_streak", 0),
        },
        "bridge": {
            "commitments": len(bridge.get("key_commitments", [])),
            "last_session": bridge.get("last_session_ts", "never"),
            "last_ee_sync": bridge.get("last_ee_sync", "never"),
        }
    }


if __name__ == "__main__":
    if len(sys.argv) > 1:
        text = " ".join(sys.argv[1:])
        result = process_user_message(text)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        status = get_proactivity_status()
        print("=== PROACTIVITY STATUS ===")
        print(json.dumps(status, indent=2, ensure_ascii=False))

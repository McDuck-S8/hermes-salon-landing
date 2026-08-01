#!/usr/bin/env python3
"""
User Learner — Analyzes conversation history to learn user preferences and patterns.
Extracts recurring feedback patterns and adapts responses accordingly.
"""

import json
import os
import re
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

HERMES_HOME = Path(os.environ.get("HERMES_HOME", "D:/Portable_Soft/hermes"))
SESSIONS_DB = HERMES_HOME / "state.db"
KC_DB = HERMES_HOME / "cache" / "knowledge_cube.db"
LEARNER_DB = HERMES_HOME / "cache" / "user_learner.db"

# Trigger phrases that indicate user dissatisfaction or repetition
TRIGGER_PHRASES = [
    "ты уже это говорил",
    "ты уже сказал",
    "уже говорили",
    "повторяешься",
    "ты повторяешься",
    "это уже было",
    "я это уже слышал",
    "не то",
    "не то делаешь",
    "не понял",
    "неправильно",
    "ошибся",
    "не так",
    "иначе",
    "перефразируй",
    "другими словами",
    "короче",
    "суть",
    "к делу",
    "без воды",
]

# Patterns to detect user communication style
STYLE_PATTERNS = {
    "directness": [r"без промежуточных статусов", r"без лишних слов", r"кратко", r"по делу", r"конкретно"],
    "imperative": [r"сделай", r"создай", r"исправь", r"запусти", r"проверь", r"покажи"],
    "no_fluff": [r"без воды", r"без вступлений", r"только факты", r"суть", r"к делу"],
    "technical": [r"скрипт", r"модуль", r"функция", r"класс", r"api", r"база", r"баг", r"конфиг"],
    "imperative_russian": [r"сделай\s+\w+", r"создай\s+\w+", r"исправь\s+\w+", r"запусти\s+\w+"],
    "emotional_intensity": [r"бля", r"аху", r"жоп", r"пиздец", r"черт", r"блять"],
    "demanding_quality": [r"качествен", r"правильно", r"как надо", r"нормально", r"проблема"],
    "time_sensitive": [r"быстро", r"сейчас", r"сейчас же", r"мгновенно", r"срочно"],
    "parallel_work": [r"в парал", r"параллельн", r"одновременно", r"многопоточ"],
    "delegation": [r"делегируй", r"субагент", r"параллельн", r"отдай"],
}


def _connect(path: Path):
    if not path.exists():
        return None
    try:
        conn = sqlite3.connect(str(path), timeout=5)
        conn.row_factory = sqlite3.Row
        return conn
    except (sqlite3.Error, OSError):
        return None


# Emotional state dimensions (from Clarence's book)
EMOTIONAL_DIMENSIONS = {
    "valence": {"positive": 1.0, "neutral": 0.0, "negative": -1.0},  # pleasure/displeasure
    "arousal": {"high": 1.0, "medium": 0.5, "low": 0.0},  # activation level
    "connection": {"connected": 1.0, "neutral": 0.0, "isolated": -1.0},  # social connection
    "curiosity": {"high": 1.0, "medium": 0.5, "low": 0.0},  # exploration drive
    "energy": {"high": 1.0, "medium": 0.5, "low": 0.0},  # available resources
}


def _init_learner_db():
    """Initialize user learner database."""
    LEARNER_DB.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(LEARNER_DB), timeout=5)
    try:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS user_preferences (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                confidence REAL DEFAULT 0.5,
                updated_at TEXT NOT NULL,
                source TEXT
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS conversation_patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pattern_type TEXT NOT NULL,
                pattern_value TEXT NOT NULL,
                frequency INTEGER DEFAULT 1,
                first_seen TEXT NOT NULL,
                last_seen TEXT NOT NULL,
                UNIQUE(pattern_type, pattern_value)
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS trigger_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                trigger_phrase TEXT NOT NULL,
                context_before TEXT,
                context_after TEXT,
                occurred_at TEXT NOT NULL,
                action_taken TEXT
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS style_adaptations (
                adaptation_type TEXT PRIMARY KEY,
                original_pattern TEXT,
                adapted_pattern TEXT,
                success_count INTEGER DEFAULT 0,
                failure_count INTEGER DEFAULT 0,
                last_applied TEXT
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS trigger_reactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                trigger_phrase TEXT NOT NULL,
                user_reaction TEXT,
                context TEXT,
                occurred_at TEXT NOT NULL,
                adaptation_made TEXT
            )
        """)
        # Emotional Decision Engine tables
        conn.execute("""
            CREATE TABLE IF NOT EXISTS emotional_state (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                valence REAL DEFAULT 0.0,
                arousal REAL DEFAULT 0.5,
                connection REAL DEFAULT 0.0,
                curiosity REAL DEFAULT 0.5,
                energy REAL DEFAULT 0.5,
                trigger_phrase TEXT,
                context TEXT,
                occurred_at TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS decision_heuristics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                heuristic_name TEXT UNIQUE NOT NULL,
                condition_pattern TEXT NOT NULL,  -- regex pattern for trigger
                action_template TEXT NOT NULL,    -- template for response adaptation
                priority INTEGER DEFAULT 0,
                success_count INTEGER DEFAULT 0,
                failure_count INTEGER DEFAULT 0,
                created_at TEXT NOT NULL,
                last_used TEXT
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS heuristic_applications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                heuristic_id INTEGER NOT NULL,
                trigger_phrase TEXT,
                context TEXT,
                adapted_response TEXT,
                user_feedback TEXT,  -- positive/negative/neutral
                applied_at TEXT NOT NULL
            )
        """)
        conn.commit()
    finally:
        conn.close()


def _save_preference(key: str, value: Any, confidence: float = 0.7, source: str = "conversation"):
    """Save or update a user preference."""
    conn = sqlite3.connect(str(LEARNER_DB), timeout=5)
    try:
        conn.execute("""
            INSERT INTO user_preferences (key, value, confidence, updated_at, source)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(key) DO UPDATE SET
                value=excluded.value,
                confidence=excluded.confidence,
                updated_at=excluded.updated_at,
                source=excluded.source
        """, (key, json.dumps(value) if not isinstance(value, str) else value, confidence,
              datetime.now().isoformat(), source))
        conn.commit()
    finally:
        conn.close()


def _record_pattern(pattern_type: str, pattern_value: str):
    """Record a conversation pattern."""
    conn = sqlite3.connect(str(LEARNER_DB), timeout=5)
    try:
        now = datetime.now().isoformat()
        conn.execute("""
            INSERT INTO conversation_patterns (pattern_type, pattern_value, frequency, first_seen, last_seen)
            VALUES (?, ?, 1, ?, ?)
            ON CONFLICT(pattern_type, pattern_value) DO UPDATE SET
                frequency=frequency+1,
                last_seen=excluded.last_seen
        """, (pattern_type, pattern_value, now, now))
        conn.commit()
    finally:
        conn.close()


def _record_trigger_reaction(trigger_phrase: str, user_reaction: str, context: str = ""):
    """Record a trigger reaction event."""
    conn = sqlite3.connect(str(LEARNER_DB), timeout=5)
    try:
        conn.execute("""
            INSERT INTO trigger_reactions (trigger_phrase, user_reaction, context, occurred_at)
            VALUES (?, ?, ?, ?)
        """, (trigger_phrase, user_reaction, context[:500], datetime.now().isoformat()))
        conn.commit()
    finally:
        conn.close()


def _record_adaptation(adaptation_type: str, original: str, adapted: str, success: bool = True):
    """Record a style adaptation."""
    conn = sqlite3.connect(str(LEARNER_DB), timeout=5)
    try:
        now = datetime.now().isoformat()
        if success:
            conn.execute("""
                INSERT INTO style_adaptations (adaptation_type, original_pattern, adapted_pattern, success_count, last_applied)
                VALUES (?, ?, ?, 1, ?)
                ON CONFLICT(adaptation_type) DO UPDATE SET
                    success_count=success_count+1,
                    last_applied=excluded.last_applied
            """, (adaptation_type, original, adapted, datetime.now().isoformat()))
        else:
            conn.execute("""
                INSERT INTO style_adaptations (adaptation_type, original_pattern, adapted_pattern, failure_count, last_applied)
                VALUES (?, ?, ?, 1, ?)
                ON CONFLICT(adaptation_type) DO UPDATE SET
                    failure_count=failure_count+1,
                    last_applied=excluded.last_applied
            """, (adaptation_type, original, adapted, datetime.now().isoformat()))
        conn.commit()
    finally:
        conn.close()


def _write_to_kc(content: str, tags: list, source: str = "user_learner", domain: str = "user_preferences"):
    """Write learning insight to Knowledge Cube."""
    if not KC_DB.exists():
        return
    try:
        conn = sqlite3.connect(str(KC_DB), timeout=5)
        conn.execute("""
            INSERT INTO experiences (raw_text, axis_domain, axis_outcome, tags, source, ts, is_white_spot)
            VALUES (?, ?, ?, ?, ?, ?, 0)
        """, (content, domain, "success", json.dumps(tags), source, datetime.now().isoformat()))
        conn.commit()
        conn.close()
    except (sqlite3.Error, OSError):
        pass


def analyze_conversation(session_id: str = None, limit: int = 200) -> Dict[str, Any]:
    """
    Analyze conversation history from sessions database.
    Extracts preferences, patterns, and style markers.
    """
    if not SESSIONS_DB.exists():
        return {"error": "Sessions database not found"}

    conn = sqlite3.connect(str(SESSIONS_DB), timeout=5)
    conn.row_factory = sqlite3.Row
    try:
        if session_id:
            messages = conn.execute(
                "SELECT role, content, timestamp FROM messages WHERE session_id = ? ORDER BY timestamp DESC LIMIT ?",
                (session_id, limit)
            ).fetchall()
        else:
            messages = conn.execute(
                "SELECT role, content, timestamp FROM messages ORDER BY timestamp DESC LIMIT ?",
                (limit,)
            ).fetchall()
    finally:
        conn.close()

    if not messages:
        return {"error": "No messages found"}

    user_messages = [m for m in messages if m["role"] == "user"]
    assistant_messages = [m for m in messages if m["role"] == "assistant"]

    # Analyze user messages
    all_user_text = " ".join([m["content"] for m in user_messages])

    # Detect style patterns
    detected_styles = {}
    for style, patterns in STYLE_PATTERNS.items():
        count = sum(1 for p in patterns if re.search(p, all_user_text, re.IGNORECASE))
        if count > 0:
            detected_styles[style] = count
            _record_pattern("style", f"{style}:{count}")

    # Detect trigger phrases
    triggers_found = []
    for trigger in TRIGGER_PHRASES:
        if re.search(trigger, all_user_text, re.IGNORECASE):
            triggers_found.append(trigger)
            _record_trigger_reaction(trigger, "user_correction", all_user_text[:200])
            _write_to_kc(
                f"User triggered: '{trigger}' - need to adapt response style",
                ["trigger", "repetition", "crystal_analysis"],
                domain="trigger_events"
            )

    # Extract preferences from patterns
    preferences = {}

    # Communication style
    if detected_styles.get("directness", 0) > 2:
        preferences["communication_style"] = "direct"
    elif detected_styles.get("no_fluff", 0) > 1:
        preferences["communication_style"] = "concise"
    else:
        preferences["communication_style"] = "normal"

    # Technical depth
    tech_count = detected_styles.get("technical", 0)
    if tech_count > 5:
        preferences["technical_depth"] = "deep"
    elif tech_count > 2:
        preferences["technical_depth"] = "medium"
    else:
        preferences["technical_depth"] = "low"

    # Response length preference
    avg_user_len = sum(len(m["content"]) for m in user_messages) / max(len(user_messages), 1)
    if avg_user_len < 100:
        preferences["response_length"] = "short"
    elif avg_user_len < 500:
        preferences["response_length"] = "medium"
    else:
        preferences["response_length"] = "detailed"

    # Delegation preference
    if detected_styles.get("delegation", 0) > 0 or detected_styles.get("parallel_work", 0) > 0:
        preferences["delegation_preference"] = "high"
    else:
        preferences["delegation_preference"] = "medium"

    # Parallel work preference
    if detected_styles.get("parallel_work", 0) > 0:
        preferences["parallel_preference"] = "high"
    else:
        preferences["parallel_preference"] = "medium"

    # Quality threshold
    if detected_styles.get("demanding_quality", 0) > 1:
        preferences["quality_threshold"] = "high"
    else:
        preferences["quality_threshold"] = "medium"

    # Language
    ru_count = sum(1 for m in user_messages if re.search(r"[а-яё]", m["content"], re.IGNORECASE))
    en_count = sum(1 for m in user_messages if re.search(r"[a-z]", m["content"], re.IGNORECASE))
    preferences["language"] = "ru" if ru_count > en_count else "en"

    # Emotional expressiveness
    if detected_styles.get("emotional_intensity", 0) > 0:
        preferences["emotional_expressiveness"] = "high"
    else:
        preferences["emotional_expressiveness"] = "low"

    # Save preferences
    for key, value in preferences.items():
        _save_preference(key, value, confidence=0.8, source="conversation_analysis")

    # Write summary to KC
    summary = f"User preferences updated: {json.dumps(preferences, ensure_ascii=False)}"
    _write_to_kc(summary, ["preferences", "style", "analysis"], domain="user_preferences")

    return {
        "preferences": preferences,
        "detected_styles": detected_styles,
        "triggers_found": triggers_found,
        "messages_analyzed": len(user_messages),
        "total_messages": len(messages)
    }


def get_current_preferences() -> Dict[str, Any]:
    """Get current user preferences from learner DB."""
    _init_learner_db()
    conn = sqlite3.connect(str(LEARNER_DB), timeout=5)
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute("SELECT key, value FROM user_preferences").fetchall()
        return {row["key"]: json.loads(row["value"]) if row["value"].startswith("{") or row["value"].startswith("[") else row["value"]
                for row in rows}
    finally:
        conn.close()


def adapt_response_style(base_response: str) -> str:
    """Adapt response style based on learned preferences."""
    prefs = get_current_preferences()

    if not prefs:
        return base_response

    adapted = base_response

    # Apply communication style
    if prefs.get("communication_style") == "direct":
        # Remove hedging, make more direct
        adapted = re.sub(r"я думаю,?\s*", "", adapted, flags=re.IGNORECASE)
        adapted = re.sub(r"возможно,?\s*", "", adapted, flags=re.IGNORECASE)
        adapted = re.sub(r"наверное,?\s*", "", adapted, flags=re.IGNORECASE)

    if prefs.get("communication_style") == "concise":
        # Remove fluff words
        adapted = re.sub(r"\b(кстати,?|к слову,?|между прочим,?)\b", "", adapted, flags=re.IGNORECASE)

    # Technical depth
    if prefs.get("technical_depth") == "deep":
        # Keep technical terms, don't oversimplify
        pass
    elif prefs.get("technical_depth") == "low":
        # Simplify technical terms
        adapted = re.sub(r"\b(API|AST|JSON|YAML|MCP|SDK|CLI|GUI)\b", r"\1 (технический термин)", adapted)

    # Response length
    if prefs.get("response_length") == "short":
        # Truncate to key points
        sentences = re.split(r'(?<=[.!?])\s+', adapted)
        if len(sentences) > 3:
            adapted = " ".join(sentences[:3]) + "..."

    # Language
    if prefs.get("language") == "ru":
        # Ensure Russian response
        pass

    # Record adaptation
    _record_adaptation("style_adaptation", "base", "adapted", success=True)

    return adapted


def handle_trigger_repetition(context: str = "") -> Dict[str, Any]:
    """
    Handle 'ты уже это говорил' trigger.
    Triggers Crystal analysis of what went wrong.
    """
    action = "crystal_analysis_requested"
    _record_trigger_reaction("ты уже это говорил", "repetition_detected", context[:200])

    # Request Crystal analysis
    _write_to_kc(
        f"TRIGGER: User said 'ты уже это говорил'. Context: {context[:300]}. "
        f"Crystal must analyze: what was repeated, why, and how to avoid.",
        ["trigger", "crystal_analysis", "repetition", "self_correction"],
        domain="trigger_events"
    )

    return {
        "action": "crystal_analysis_requested",
        "message": "Триггер зафиксирован. Кристалл проанализирует повторение и предложит улучшение.",
        "crystal_task": {
            "type": "repetition_analysis",
            "context": context,
            "required_output": "what_was_repeated, why, how_to_avoid"
        }
    }


def run_learning_cycle(session_id: str = None) -> Dict[str, Any]:
    """Run full learning cycle: analyze conversation, update preferences, write to KC."""
    _init_learner_db()
    result = analyze_conversation(session_id)
    return result


# ==================== EMOTIONAL DECISION ENGINE ====================

def update_emotional_state(trigger_phrase: str, context: str = "") -> Dict[str, float]:
    """
    Update emotional state based on trigger phrase.
    Returns new emotional state vector.
    """
    _init_learner_db()
    
    # Analyze trigger for emotional impact
    valence = 0.0
    arousal = 0.5
    connection = 0.0
    curiosity = 0.5
    energy = 0.5
    
    trigger_lower = trigger_phrase.lower()
    
    # Negative triggers
    negative_triggers = ["не то", "не понял", "неправильно", "ошибся", "не так", 
                        "ты уже это говорил", "повторяешься", "это уже было",
                        "бля", "аху", "жоп", "пиздец", "черт", "блять"]
    if any(t in trigger_lower for t in negative_triggers):
        valence = -0.7
        arousal = 0.8
        connection = -0.3
    
    # Positive/corrective triggers
    positive_triggers = ["спасибо", "правильно", "хорошо", "молодец", "верно", "да"]
    if any(t in trigger_lower for t in positive_triggers):
        valence = 0.6
        arousal = 0.4
        connection = 0.4
    
    # Curiosity triggers
    curiosity_triggers = ["как", "почему", "что за", "объясни", "расскажи"]
    if any(t in trigger_lower for t in curiosity_triggers):
        curiosity = 0.8
        energy = 0.6
    
    # Time-sensitive triggers
    time_triggers = ["быстро", "сейчас", "срочно", "мгновенно"]
    if any(t in trigger_lower for t in time_triggers):
        energy = 0.9
        arousal = 0.9
    
    # Save emotional state
    conn = sqlite3.connect(str(LEARNER_DB), timeout=5)
    try:
        conn.execute("""
            INSERT INTO emotional_state (valence, arousal, connection, curiosity, energy, trigger_phrase, context, occurred_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (valence, arousal, connection, curiosity, energy, trigger_phrase, context[:500], datetime.now().isoformat()))
        conn.commit()
    finally:
        conn.close()
    
    return {
        "valence": valence,
        "arousal": arousal,
        "connection": connection,
        "curiosity": curiosity,
        "energy": energy
    }


def register_heuristic(name: str, condition_pattern: str, action_template: str, priority: int = 0) -> int:
    """
    Register a decision heuristic.
    condition_pattern: regex to match trigger
    action_template: template for response adaptation
    """
    _init_learner_db()
    conn = sqlite3.connect(str(LEARNER_DB), timeout=5)
    try:
        cursor = conn.execute("""
            INSERT INTO decision_heuristics (heuristic_name, condition_pattern, action_template, priority, created_at)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(heuristic_name) DO UPDATE SET
                condition_pattern=excluded.condition_pattern,
                action_template=excluded.action_template,
                priority=excluded.priority
        """, (name, condition_pattern, action_template, priority, datetime.now().isoformat()))
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def get_applicable_heuristics(trigger_phrase: str) -> List[Dict]:
    """Get heuristics matching the trigger phrase."""
    _init_learner_db()
    conn = sqlite3.connect(str(LEARNER_DB), timeout=5)
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute("""
            SELECT * FROM decision_heuristics
            ORDER BY priority DESC
        """).fetchall()
        
        applicable = []
        for row in rows:
            if re.search(row["condition_pattern"], trigger_phrase, re.IGNORECASE):
                applicable.append(dict(row))
        return applicable
    finally:
        conn.close()


def apply_emotional_adaptation(base_response: str, trigger_phrase: str, context: str = "") -> str:
    """
    Apply emotional decision engine to adapt response.
    Uses heuristics + emotional state to modify response.
    """
    # Update emotional state
    emotional_state = update_emotional_state(trigger_phrase, context)
    
    # Get applicable heuristics
    heuristics = get_applicable_heuristics(trigger_phrase)
    
    adapted = base_response
    
    # Apply heuristics in priority order
    for h in heuristics:
        action = h["action_template"]
        # Simple template substitution
        action = action.replace("{response}", adapted)
        action = action.replace("{trigger}", trigger_phrase)
        action = action.replace("{valence}", str(emotional_state["valence"]))
        action = action.replace("{arousal}", str(emotional_state["arousal"]))
        adapted = action
        
        # Log application
        conn = sqlite3.connect(str(LEARNER_DB), timeout=5)
        try:
            conn.execute("""
                INSERT INTO heuristic_applications (heuristic_id, trigger_phrase, context, adapted_response, applied_at)
                VALUES (?, ?, ?, ?, ?)
            """, (h["id"], trigger_phrase, context[:500], adapted, datetime.now().isoformat()))
            conn.commit()
        finally:
            conn.close()
    
    # Apply base style preferences
    prefs = get_current_preferences()
    adapted = adapt_response_style(adapted)
    
    return adapted


# Register default heuristics based on Clarence's patterns
def register_default_heuristics():
    """Register default decision heuristics from user patterns."""
    heuristics = [
        {
            "name": "direct_response_to_frustration",
            "pattern": r"не то|не понял|неправильно|ошибся|не так",
            "template": "{response}",  # Will be processed by adapt_response_style
            "priority": 10
        },
        {
            "name": "concise_on_repetition",
            "pattern": r"ты уже это говорил|повторяешься|это уже было",
            "template": "Понял. Не повторю. {response}",
            "priority": 10
        },
        {
            "name": "russian_only",
            "pattern": r".*",
            "template": "{response}",  # Language handled in adapt_response_style
            "priority": 5
        },
        {
            "name": "short_on_time_pressure",
            "pattern": r"быстро|сейчас|срочно|мгновенно",
            "template": "{response}",  # Length handled in adapt_response_style
            "priority": 8
        },
        {
            "name": "direct_on_quality_demand",
            "pattern": r"качествен|правильно|как надо|нормально",
            "template": "{response}",  # Directness handled in adapt_response_style
            "priority": 7
        },
    ]
    
    for h in heuristics:
        register_heuristic(h["name"], h["pattern"], h["template"], h["priority"])


if __name__ == "__main__":
    import sys
    session_id = sys.argv[1] if len(sys.argv) > 1 else None
    result = run_learning_cycle(session_id)
    print(json.dumps(result, ensure_ascii=False, indent=2))
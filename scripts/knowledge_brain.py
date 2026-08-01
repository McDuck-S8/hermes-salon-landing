#!/usr/bin/env python3
"""
Knowledge Cube — Active Brain (АКТИВНЫЙ МОЗГ)


> Revisit: when knowledge brain logic, decision support, or brain query changes. Last touched: 2026-07-02.

Turns the cube from passive storage into an active decision-maker.
Before acting: consult the cube. After acting: record result.
Three pillars guide every decision.

Usage:
    from knowledge_brain import Brain
    
    brain = Brain()
    
    # Before acting
    advice = brain.before("настроить Telegram прокси")
    print(advice["recommendation"])  # "Используй execute_code, не terminal"
    
    # After acting
    brain.after("настроить прокси", outcome="success", tools=["execute_code", "file"])
"""

import json, os, sqlite3
from pathlib import Path
from datetime import datetime
from typing import Optional

HERMES_HOME = Path(os.environ.get("HERMES_HOME", os.path.expanduser("~/.hermes")))
DB_PATH = HERMES_HOME / "cache" / "knowledge_cube.db"

# Import cube functions
import sys
sys.path.insert(0, str(Path(__file__).parent))
from knowledge_cube import (
    get_db, add_experience, query_cube, get_white_spots,
    get_cube_stats, detect_anomalies, get_three_pillars,
    WHITE_SPOT, NORMAL, RED_ANOMALY, ANOMALY_TYPES,
)


# ═══════════════════════════════════════════════════════════════
# DECISION MATRIX — тип задачи → лучший инструмент
# ═══════════════════════════════════════════════════════════════

TOOL_MATRIX = {
    "network": {
        "best": "execute_code",
        "avoid": ["terminal"],
        "reason": "WSL NAT блокирует terminal → используй execute_code с urllib",
    },
    "file_read": {
        "best": "read_file",
        "avoid": ["terminal"],
        "reason": "read_file быстрее и надёжнее чем cat",
    },
    "file_write": {
        "best": "write_file",
        "avoid": ["terminal"],
        "reason": "write_file создаёт директории автоматически",
    },
    "file_search": {
        "best": "search_files",
        "avoid": ["terminal"],
        "reason": "search_files быстрее grep/find",
    },
    "code_edit": {
        "best": "patch",
        "avoid": ["terminal"],
        "reason": "patch с fuzzy matching надёжнее sed",
    },
    "web_search": {
        "best": "web_search",
        "avoid": ["terminal"],
        "reason": "web_search напрямую, не через curl",
    },
    "web_extract": {
        "best": "web_extract",
        "avoid": ["terminal"],
        "reason": "web_extract парсит markdown автоматически",
    },
    "browser": {
        "best": "mcp_agent_browser_*",
        "avoid": ["terminal"],
        "reason": "MCP browser для JS-рендеринга и интерактива",
    },
    "long_running": {
        "best": "delegate_task",
        "avoid": ["execute_code"],
        "reason": "delegate_task для задач >30 секунд",
    },
    "simple_check": {
        "best": "terminal",
        "avoid": [],
        "reason": "Для простых проверок terminal достаточен",
    },
}


# ═══════════════════════════════════════════════════════════════
# BRAIN CLASS — АКТИВНЫЙ МОЗГ
# ═══════════════════════════════════════════════════════════════

class Brain:
    """Active decision-maker built on top of Knowledge Cube."""
    
    def __init__(self):
        self._current_action = None
        self._current_tools = []
    
    def before(self, action_description: str) -> dict:
        """
        CONSULT THE CUBE before acting.
        Returns: recommendation, warnings, relevant past experiences.
        """
        result = {
            "action": action_description,
            "recommendation": None,
            "warnings": [],
            "past_experiences": [],
            "white_spots": [],
            "anomalies": [],
            "pillar": None,
        }
        
        # 1. Search for similar past experiences
        past = self._find_similar(action_description)
        if past:
            result["past_experiences"] = past
            # Check for failures in similar experiences
            failures = [p for p in past if p.get("axis_outcome") == "failure"]
            if failures:
                result["warnings"].append(
                    f"⚠️ Похожие задачи провалились {len(failures)} раз. "
                    f"Домен: {failures[0].get('axis_domain', '?')}"
                )
        
        # 2. Classify the action into a tool category
        tool_category = self._classify_action(action_description, past)
        if tool_category in TOOL_MATRIX:
            matrix = TOOL_MATRIX[tool_category]
            result["recommendation"] = f"Используй {matrix['best']}. {matrix['reason']}"
            if matrix["avoid"]:
                result["warnings"].append(f"🚫 Избегай: {', '.join(matrix['avoid'])}")
        
        # 3. Check if this is a white spot
        ws = self._check_white_spot(action_description)
        if ws:
            result["white_spots"] = ws
            result["warnings"].append("⬜ Это белое пятно — нет опыта. Действуй осторожно.")
        
        # 4. Check for relevant anomalies
        anomalies = detect_anomalies()
        relevant = [a for a in anomalies if self._anomaly_relevant(a, action_description)]
        if relevant:
            result["anomalies"] = relevant
            for a in relevant:
                result["warnings"].append(f"🔴 Аномалия: {a['description']}")
        
        # 5. Determine pillar
        if ws:
            result["pillar"] = WHITE_SPOT
        elif past and any(p.get("axis_outcome") == "failure" for p in past):
            result["pillar"] = RED_ANOMALY
        else:
            result["pillar"] = NORMAL
        
        self._current_action = action_description
        self._current_tools = []
        
        return result
    
    def after(self, action_description: str = None,
              outcome: str = "unknown",
              tools: list = None,
              notes: str = "") -> dict:
        """
        RECORD THE RESULT after acting.
        Adds experience to cube, updates anomalies.
        """
        desc = action_description or self._current_action or "unknown action"
        tools = tools or self._current_tools
        
        # Add to cube
        result = add_experience(
            text=f"{desc}. {notes}".strip(),
            tools=tools,
            source="brain",
            dynamic_axes={
                "from_brain": True,
                "had_warnings": bool(self._current_action),
            }
        )
        
        # Update pillar classification
        pillars = get_three_pillars()
        
        return {
            "recorded": result,
            "pillars": pillars,
            "message": f"Записано: {desc} → {outcome}",
        }
    
    def status(self) -> dict:
        """Get current brain status — three pillars + anomalies."""
        pillars = get_three_pillars()
        anomalies = detect_anomalies()
        stats = get_cube_stats()
        
        return {
            "pillars": pillars,
            "anomalies": anomalies,
            "stats": stats,
            "health": self._assess_health(pillars, anomalies),
        }
    
    def think(self, topic: str = None) -> dict:
        """
        DEEP THINK — analyze cube state, find patterns, suggest actions.
        If topic given, focus on that domain.
        """
        pillars = get_three_pillars()
        anomalies = detect_anomalies()
        
        suggestions = []
        
        # Suggest filling white spots
        ws = get_white_spots(5)
        if ws:
            suggestions.append({
                "type": "fill_white_spots",
                "priority": "high",
                "description": f"Заполнить {len(ws)} белых пятен",
                "items": [w["raw_text"][:80] for w in ws[:3]],
            })
        
        # Suggest investigating anomalies
        if anomalies:
            suggestions.append({
                "type": "investigate_anomalies",
                "priority": "medium",
                "description": f"Исследовать {len(anomalies)} аномалий",
                "items": [a["description"] for a in anomalies[:3]],
            })
        
        # Suggest building on successes
        with get_db() as conn:
            successes = conn.execute(
                "SELECT raw_text, axis_domain FROM experiences WHERE axis_outcome = 'success' LIMIT 5"
            ).fetchall()
        
        if successes:
            suggestions.append({
                "type": "build_on_success",
                "priority": "low",
                "description": f"Развить {len(successes)} успешных паттернов",
                "items": [s[0][:80] for s in successes[:3]],
            })
        
        return {
            "pillars": pillars,
            "anomalies_count": len(anomalies),
            "suggestions": suggestions,
            "verdict": self._verdict(pillars, anomalies, suggestions),
        }
    
    # ── Internal helpers ──
    
    def _find_similar(self, description: str) -> list:
        """Find similar past experiences using FTS5 full-text search."""
        words = set(description.lower().split())
        stop = {"и", "в", "на", "с", "для", "не", "что", "как", "по", "к", "из", "от"}
        words -= stop
        query = " OR ".join(w for w in words if w) if words else description
        
        db_path = HERMES_HOME / "cache" / "knowledge_cube.db"
        if not db_path.exists():
            return []
        
        import sqlite3 as _sqlite3
        conn = _sqlite3.connect(str(db_path))
        try:
            # Create FTS virtual table if not exists
            conn.execute("""
                CREATE VIRTUAL TABLE IF NOT EXISTS experiences_fts
                USING fts5(raw_text, axis_domain, axis_outcome, tags)
            """)
            
            # Insert into FTS if empty
            count = conn.execute("SELECT count(*) FROM experiences_fts").fetchone()[0]
            if count == 0:
                rows = conn.execute(
                    "SELECT raw_text, axis_domain, axis_outcome, tags FROM experiences"
                ).fetchall()
                if rows:
                    conn.executemany(
                        "INSERT INTO experiences_fts (raw_text, axis_domain, axis_outcome, tags) VALUES (?, ?, ?, ?)",
                        rows,
                    )
            
            # FTS5 MATCH search
            results = []
            try:
                rows = conn.execute(
                    "SELECT raw_text, axis_domain, axis_outcome, tags, rank FROM experiences_fts WHERE experiences_fts MATCH ? ORDER BY rank LIMIT 5",
                    (query,),
                ).fetchall()
                for r in rows:
                    results.append({
                        "raw_text": r[0],
                        "axis_domain": r[1],
                        "axis_outcome": r[2],
                        "tags": json.loads(r[3]) if r[3] else [],
                        "score": abs(r[4]) if r[4] else 0,
                    })
            except Exception:
                pass  # FTS MATCH can fail on malformed queries
            return results
        finally:
            conn.close()
    
    # Domain → tool category mapping for past experience routing
    DOMAIN_TO_TOOL = {
        "communication": "terminal",
        "creative": "long_running",
        "knowledge": "file_search",
        "file_ops": "code_edit",
        "network": "network",
        "file_read": "file_read",
        "file_write": "file_write",
        "file_search": "file_search",
        "code_edit": "code_edit",
        "web_search": "web_search",
        "web_extract": "web_extract",
        "browser": "browser",
        "long_running": "long_running",
    }
    
    def _classify_action(self, description: str, past_experiences: list = None) -> str:
        """Classify action into tool category.
        
        Uses past_experiences from the cube to pick the best tool based on
        the dominant domain. Falls back to keyword matching if no past
        experiences are available.
        """
        # --- 1. Try experience-based classification ---
        if past_experiences:
            # Count domains from past experiences, weighted by score
            domain_scores: dict[str, float] = {}
            for exp in past_experiences:
                domain = exp.get("axis_domain", "")
                if domain and domain in self.DOMAIN_TO_TOOL:
                    score = exp.get("score", 1)
                    domain_scores[domain] = domain_scores.get(domain, 0) + score
            
            if domain_scores:
                best_domain = max(domain_scores, key=domain_scores.get)
                return self.DOMAIN_TO_TOOL[best_domain]
        
        # --- 2. Fallback: keyword matching ---
        desc = description.lower()
        
        if any(w in desc for w in ["curl", "http", "запрос", "api", "сеть", "proxy", "прокси"]):
            return "network"
        if any(w in desc for w in ["прочитать", "cat", "посмотреть файл", "содержимое"]):
            return "file_read"
        if any(w in desc for w in ["записать", "создать файл", "сохранить"]):
            return "file_write"
        if any(w in desc for w in ["найти в файлах", "grep", "поиск по файлам"]):
            return "file_search"
        if any(w in desc for w in ["изменить код", "отредактировать", "patch", "заменить"]):
            return "code_edit"
        if any(w in desc for w in ["найти в интернете", "поиск", "google"]):
            return "web_search"
        if any(w in desc for w in ["скачать страницу", "извлечь", "парсить"]):
            return "web_extract"
        if any(w in desc for w in ["браузер", "открыть сайт", "кликнуть"]):
            return "browser"
        if any(w in desc for w in ["долгая задача", "параллельно", "delegate"]):
            return "long_running"
        
        return "simple_check"
    
    def _check_white_spot(self, description: str) -> list:
        """Check if this area has white spots."""
        words = set(description.lower().split())
        stop = {"и", "в", "на", "с", "для", "не", "что", "как", "по", "к", "из", "от"}
        words -= stop
        
        ws = get_white_spots(50)
        relevant = []
        for w in ws:
            ws_words = set(w["raw_text"].lower().split())
            if len(words & ws_words) >= 2:
                relevant.append(w)
        
        return relevant[:3]
    
    def _anomaly_relevant(self, anomaly: dict, description: str) -> bool:
        """Check if anomaly is relevant to the action."""
        desc_words = set(description.lower().split())
        anom_words = set(anomaly.get("description", "").lower().split())
        return len(desc_words & anom_words) >= 2
    
    def _assess_health(self, pillars: dict, anomalies: list) -> str:
        """Assess overall knowledge health."""
        ws_pct = pillars.get("white_pct", 0)
        red_pct = pillars.get("red_pct", 0)
        
        if ws_pct > 80:
            return "CRITICAL — слишком много белых пятен"
        if red_pct > 30:
            return "WARNING — слишком много аномалий"
        if ws_pct > 60:
            return "GROWING — развиваемся, белых пятен много"
        if red_pct < 10 and ws_pct < 30:
            return "STABLE — стабильная база знаний"
        return "HEALTHY — нормальное развитие"
    
    def _verdict(self, pillars: dict, anomalies: list, suggestions: list) -> str:
        """Generate a verdict based on current state."""
        ws = pillars.get("white_pct", 0)
        red = len(anomalies)
        sug = len(suggestions)
        
        if ws > 70:
            return f"Много белых пятен ({ws}%). Нужно больше опыта. Фокус: заполнение пустот."
        if red > 5:
            return f"Много аномалий ({red}). Нужно разобраться. Фокус: investigación скрытых паттернов."
        if sug > 0:
            return f"Есть {sug} направлений для развития. Выбирай что ближе."
        return "Всё стабильно. Можно исследовать новые горизонты."


# ═══════════════════════════════════════════════════════════════
# QUICK ACCESS — convenience functions
# ═══════════════════════════════════════════════════════════════

_brain = None

def get_brain() -> Brain:
    """Get singleton brain instance."""
    global _brain
    if _brain is None:
        _brain = Brain()
    return _brain

def consult(action: str) -> dict:
    """Quick: consult the brain before acting."""
    return get_brain().before(action)

def record(action: str, outcome: str = "success", tools: list = None) -> dict:
    """Quick: record result after acting."""
    return get_brain().after(action, outcome=outcome, tools=tools)

def think(topic: str = None) -> dict:
    """Quick: deep think about current state."""
    return get_brain().think(topic)

def status() -> dict:
    """Quick: get brain status."""
    return get_brain().status()


# ═══════════════════════════════════════════════════════════════
# CLI MODE — usage:
#   python knowledge_brain.py --record 'action' success 'tool1,tool2'
#   python knowledge_brain.py --status
# ═══════════════════════════════════════════════════════════════

def record_outcome(action: str, outcome: str, tools: list) -> dict:
    """Record an action outcome via the brain."""
    return get_brain().after(action, outcome=outcome, tools=tools)


if __name__ == "__main__":
    import sys
    args = sys.argv[1:]

    if "--record" in args:
        idx = args.index("--record")
        if len(args) < idx + 4:
            print("Usage: --record 'action' outcome 'tool1,tool2'")
            sys.exit(1)
        action = args[idx + 1]
        outcome = args[idx + 2]
        tools = [t.strip() for t in args[idx + 3].split(",") if t.strip()]
        result = record_outcome(action, outcome, tools)
        print(json.dumps(result, indent=2, ensure_ascii=False))

    elif "--status" in args:
        s = status()
        stats = s.get("stats", {})
        pillars = s.get("pillars", {})
        print(f"Total experiences: {stats.get('total_experiences', 0)}")
        print(f"White spots: {stats.get('white_spots', 0)} ({pillars.get('white_pct', 0)}%)")
        print(f"Red anomalies: {stats.get('anomalies', 0)} ({pillars.get('red_pct', 0)}%)")
        print(f"Health: {s.get('health', 'unknown')}")
    else:
        print("Usage:")
        print("  python knowledge_brain.py --record 'action' success 'tool1,tool2'")
        print("  python knowledge_brain.py --status")

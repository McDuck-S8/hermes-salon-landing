"""
Strategic Ranker — ранжирует цели по стратегической ценности.

Не "какой goal проще сделать", а "какой goal важнее для пользователя".
Учитывает: приоритет пользователя, unlock value, cost of delay, зависимости,
время суток и день недели (реальный мир).
"""
import json
from pathlib import Path
from datetime import datetime
from pytz import timezone as tz

HERMES_HOME = Path(__file__).resolve().parent.parent
TZ_MOSCOW = tz("Europe/Moscow")


def _now_moscow() -> datetime:
    return datetime.now(TZ_MOSCOW)


def rank_goals(goals: list, context: dict = None) -> list:
    """
    Ранжирует цели по стратегической ценности.
    Возвращает список (goal, score) отсортированный по убыванию.
    """
    if context is None:
        context = {}

    now = _now_moscow()
    scored = []
    for goal in goals:
        if goal.get("status") != "active":
            continue

        score = (
            _user_priority(goal) * 0.25 +
            _unlock_value(goal) * 0.20 +
            _cost_of_delay(goal) * 0.15 +
            _dependency_readiness(goal) * 0.10 +
            _probability_of_success(goal) * 0.10 +
            _time_of_day_priority(goal, now) * 0.10 +
            _day_of_week_priority(goal, now) * 0.10
        )
        scored.append((goal, round(score, 3), {
            "time_boost": round(_time_of_day_priority(goal, now), 2),
            "day_boost": round(_day_of_week_priority(goal, now), 2),
            "now": now.strftime("%H:%M %A"),
        }))

    return sorted(scored, key=lambda x: x[1], reverse=True)


def _user_priority(goal: dict) -> float:
    """Насколько эта цель важна для пользователя прямо сейчас."""
    priority = goal.get("priority", 5)
    # Map priority 1-10 to 0.0-1.0
    return min(1.0, priority / 10.0)


def _unlock_value(goal: dict) -> float:
    """Сколько других целей разблокируется после выполнения этой."""
    title = goal.get("title", "").lower()
    # Token unlocks: salon bot, auto-posting, content generation
    token_goals = ["salon", "auto-posting", "content", "posting", "deploy"]
    if any(kw in title for kw in token_goals):
        return 0.9  # High unlock value
    # Infrastructure unlocks: monitoring, curiosity
    if any(kw in title for kw in ["monitoring", "curiosity", "workflow"]):
        return 0.7
    # Research: unlocks understanding
    if any(kw in title for kw in ["research", "investigate", "analyze"]):
        return 0.5
    return 0.3


def _cost_of_delay(goal: dict) -> float:
    """Что теряем каждый час откладывания."""
    title = goal.get("title", "").lower()
    # Income goals: delay = lost revenue
    if any(kw in title for kw in ["income", "money", "revenue", "bandwidth"]):
        return 0.9
    # Deployment goals: delay = no clients
    if any(kw in title for kw in ["deploy", "client", "launch"]):
        return 0.8
    # Monitoring: delay = blind spot
    if any(kw in title for kw in ["monitoring", "alert"]):
        return 0.6
    return 0.3


def _dependency_readiness(goal: dict) -> float:
    """Все ли зависимости готовы."""
    title = goal.get("title", "").lower()
    # Check for known blockers
    env_file = HERMES_HOME / ".env"
    has_token = False
    if env_file.exists():
        content = env_file.read_text(encoding="utf-8")
        has_token = "TELEGRAM_BOT_TOKEN" in content and len(content) > 50

    # Goals requiring token
    if any(kw in title for kw in ["salon", "auto-posting", "content", "deploy", "posting"]):
        if not has_token:
            return 0.1  # Blocked - no token
        return 0.9

    # Goals that work locally
    if any(kw in title for kw in ["classify", "analyze", "graph", "knowledge", "research"]):
        return 0.95

    # Goals requiring network
    if any(kw in title for kw in ["curiosity", "monitoring", "youtube"]):
        return 0.2  # Blocked - network issues

    return 0.7


def _probability_of_success(goal: dict) -> float:
    """Байесовская оценка (упрощённая)."""
    progress = goal.get("progress", 0)
    return 0.3 + (progress * 0.7)


# === ВРЕМЕННЫЕ ФАКТОРЫ (реальный мир) ===

_TIME_KEYWORDS = {
    "morning": {  # 07-10: финансы, работа, кредиты
        "high": ["credit", "кредит", "job", "работ", "education", "образов",
                 "finance", "финанс", "ипотек", "loan", "займ", "bank", "банк"],
        "low": ["entertainment", "развлечен", "game", "игр"],
    },
    "afternoon": {  # 12-16: всё среднее
        "high": ["research", "analyze", "plan", "build"],
        "low": [],
    },
    "evening": {  # 18-22: туризм, развлечения, покупки, салоны
        "high": ["travel", "путешеств", "tourism", "туризм", "hotel", "отел",
                 "entertainment", "развлечен", "shop", "покупк",
                 "salon", "салон", "beauty", "красот", "arbitrage", "арбитраж"],
        "low": ["credit", "кредит", "work", "работ"],
    },
    "night": {  # 23-06: аналитика
        "high": ["analyze", "graph", "report", "investigate"],
        "low": [],
    },
}

_DAY_KEYWORDS = {
    "friday": {  # Пятница: выходные
        "high": ["travel", "hotel", "tourism", "entertainment", "salon", "beauty"],
        "low": ["credit", "job"],
    },
    "saturday": {  # Суббота: покупки, услуги
        "high": ["shop", "deliver", "salon", "beauty", "travel"],
        "low": [],
    },
    "sunday": {  # Воскресенье: отдых
        "high": ["entertainment", "travel"],
        "low": ["work", "credit"],
    },
    "monday": {  # Понедельник: финансы, работа
        "high": ["credit", "job", "finance", "education", "bank"],
        "low": ["entertainment"],
    },
}

_DAY_NAMES = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]


def _time_period(hour: int) -> str:
    if 7 <= hour < 10:
        return "morning"
    elif 12 <= hour < 16:
        return "afternoon"
    elif 18 <= hour < 22:
        return "evening"
    return "night"


def _match_kw(text: str, keywords: list) -> bool:
    text_lower = text.lower()
    return any(kw in text_lower for kw in keywords)


def _time_of_day_priority(goal: dict, now: datetime) -> float:
    """Буст/штраф по времени суток."""
    period = _time_period(now.hour)
    kw = _TIME_KEYWORDS.get(period, {"high": [], "low": []})
    text = goal.get("title", "") + " " + goal.get("description", "")

    if _match_kw(text, kw["high"]):
        return 0.9
    elif _match_kw(text, kw["low"]):
        return 0.2
    return 0.5


def _day_of_week_priority(goal: dict, now: datetime) -> float:
    """Буст/штраф по дню недели."""
    day = _DAY_NAMES[now.weekday()]
    kw = _DAY_KEYWORDS.get(day, {"high": [], "low": []})
    text = goal.get("title", "") + " " + goal.get("description", "")

    if _match_kw(text, kw["high"]):
        return 0.9
    elif _match_kw(text, kw["low"]):
        return 0.2
    return 0.5


def suggest_next_action(ranked_goals: list) -> dict:
    """Для верхней цели: какое действие сейчас нужно."""
    if not ranked_goals:
        return {"action": "No goals available", "blocked": False}

    goal, score = ranked_goals[0]
    title = goal.get("title", "").lower()
    progress = goal.get("progress", 0)

    # Check for blockers
    blocker = _detect_blocker(goal)
    if blocker:
        return {
            "action": "Create unblocking goal",
            "blocker": blocker,
            "goal": goal,
            "blocked": True,
        }

    # Suggest decomposed steps
    steps = _decompose_goal(goal)
    current_step = min(int(progress * len(steps)), len(steps) - 1)

    return {
        "action": steps[current_step] if steps else "Execute goal directly",
        "goal": goal,
        "step": current_step + 1,
        "total_steps": len(steps),
        "blocked": False,
        "score": score,
    }


def _detect_blocker(goal: dict) -> str:
    """Определяет что блокирует цель."""
    title = goal.get("title", "").lower()

    # Token blocker
    if any(kw in title for kw in ["salon", "auto-posting", "deploy", "posting"]):
        env_file = HERMES_HOME / ".env"
        if env_file.exists():
            content = env_file.read_text(encoding="utf-8")
            if "TELEGRAM_BOT_TOKEN" not in content or len(content) < 50:
                return "TELEGRAM_BOT_TOKEN not configured"
        else:
            return ".env file missing"

    # Network blocker
    if any(kw in title for kw in ["curiosity", "monitoring", "youtube"]):
        try:
            import urllib.request
            req = urllib.request.Request("https://httpbin.org/get", headers={"User-Agent": "Mozilla/5.0"})
            urllib.request.urlopen(req, timeout=3)
        except Exception:
            return "Network blocked (SSL/timeout)"

    return None


def _decompose_goal(goal: dict) -> list:
    """Разлагает цель на конкретные шаги."""
    title = goal.get("title", "").lower()
    progress = goal.get("progress", 0)

    if "salon" in title:
        if progress < 0.3:
            return ["Configure TELEGRAM_BOT_TOKEN", "Test bot locally", "Deploy to production"]
        elif progress < 0.7:
            return ["Test bot locally", "Deploy to production"]
        else:
            return ["Deploy to production"]

    if "auto-posting" in title:
        return ["Configure channel IDs", "Generate content templates", "Test with preview", "Schedule posts"]

    if "money4band" in title:
        return ["Clone repo", "Run setup wizard", "Register on platforms", "Start Docker containers"]

    if "monitoring" in title:
        return ["Fix network access (proxy)", "Configure curiosity sources", "Verify discoveries"]

    if "knowledge" in title or "classify" in title:
        return ["Identify unclassified entries", "Classify by domain", "Verify classification"]

    if "graph" in title:
        return ["Analyze graph structure", "Identify hubs", "Report findings"]

    return ["Execute goal directly"]


def create_unblocking_goal(blocker: str) -> dict:
    """Создаёт цель для разблокировки."""
    goals_file = HERMES_HOME / "cache" / "goal_queue.json"
    data = json.loads(goals_file.read_text(encoding="utf-8")) if goals_file.exists() else {"goals": []}
    goals = data.get("goals", [])

    # Generate goal ID
    existing_ids = {g.get("id", "") for g in goals}
    i = 1
    while "g-unblock-%d" % i in existing_ids:
        i += 1
    goal_id = "g-unblock-%d" % i

    new_goal = {
        "id": goal_id,
        "title": "Unblock: %s" % blocker,
        "tier": 1,  # SURVIVE priority
        "priority": 9,  # High - blocking other goals
        "created_at": datetime.now().isoformat(),
        "status": "active",
        "progress": 0.0,
        "related_actions": [],
        "deadline": None,
        "description": "Auto-created to unblock: %s" % blocker,
    }

    goals.append(new_goal)
    data["goals"] = goals
    goals_file.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    return new_goal


if __name__ == "__main__":
    # Demo
    now = _now_moscow()
    print("=== STRATEGIC RANKING ===")
    print("Time: %s (%s)" % (now.strftime("%H:%M"), now.strftime("%A")))
    period = _time_period(now.hour)
    day = _DAY_NAMES[now.weekday()]
    print("Period: %s, Day: %s\n" % (period, day))

    goals_file = HERMES_HOME / "cache" / "goal_queue.json"
    data = json.loads(goals_file.read_text(encoding="utf-8"))
    goals = data.get("goals", [])

    ranked = rank_goals(goals)
    for i, (goal, score, meta) in enumerate(ranked[:10], 1):
        blocker = _detect_blocker(goal)
        blocker_str = " [BLOCKED: %s]" % blocker if blocker else ""
        time_str = " (time:%s day:%s)" % (meta["time_boost"], meta["day_boost"])
        print("  %d. %.3f %s%s%s" % (i, score, goal.get("title", "?")[:50], blocker_str, time_str))

    print()
    suggestion = suggest_next_action(ranked)
    print("NEXT ACTION: %s" % suggestion["action"])
    if suggestion.get("blocked"):
        print("BLOCKER: %s" % suggestion.get("blocker", "?"))
        new_goal = create_unblocking_goal(suggestion["blocker"])
        print("CREATED UNBLOCKING GOAL: %s" % new_goal["id"])

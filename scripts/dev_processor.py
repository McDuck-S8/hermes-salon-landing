#!/usr/bin/env python3
"""
Development Processor — event-driven создание целей при заполнении пробелов.
Проверяет новые кирпичи в мастерской,

> Revisit: when goal prioritization, execution logic, or Bayesian integration changes. Last touched: 2026-07-02.
сравнивает с эталонами из SELF_IDENTITY.md,
создаёт цели на тестирование.

Usage:
    python scripts/dev_processor.py           # check & create goals
    python scripts/dev_processor.py --status  # show metrics
"""
import json
import re
from pathlib import Path
from datetime import datetime

HERMES_HOME = Path(__file__).resolve().parent.parent
CACHE_DIR = HERMES_HOME / "cache"
BRICKS_LOG = CACHE_DIR / "bricks_log.jsonl"
GOALS_FILE = CACHE_DIR / "goal_queue.json"
DEV_LOG = CACHE_DIR / "dev_log.jsonl"
LESSONS_FILE = HERMES_HOME / "LESSONS.md"
DECISION_LOG = HERMES_HOME / "DECISION_LOG.md"


# Department → required capabilities mapping
DEPT_GAPS = {
    "Цех": ["PageSpeed", "HTML", "мобильная версия", "дизайн", "Tailwind", "bot", "бот", "сайт", "лендинг"],
    "Продажник": ["UTP", "УТП", "письмо", "email", "cold", "продаж", "конверсия"],
    "Глаза": ["скрапинг", "парсинг", "мониторинг", "поиск", "браузер", "API"],
    "Аналитик": ["анализ", "аудит", "PageSpeed", "конверсия", "метрик", "CPA", "CPI"],
    "R&D": ["арбитраж", "CPA", "оффер", "трафик", "monetiz", "monetis", "revenue", "ROI"],
    "Маска": ["прокси", "antidetect", "fingerprint", "антидетект", "VPN"],
    "Память": ["база знаний", "knowledge", "поиск", "индекс", "vector", "embedding"],
    "Watchdog": ["мониторинг", "алерт", "heartbeat", "uptime", "надёжность"],
    "Бухгалтер": ["налог", "самозанят", "ИП", "доход", "расход", "отчёт"],
    "Юрист": ["договор", "юридическ", "ГК РФ", "самозанят", "регистрац"],
    "Учитель": ["обучение", "урок", "классификация", "паттерн", "ошибк"],
}


def load_goals():
    if GOALS_FILE.exists():
        try:
            data = json.loads(GOALS_FILE.read_text("utf-8"))
            return data.get("goals", [])
        except Exception:
            return []
    return []


def goal_exists_for(title: str) -> bool:
    """Check if a goal already exists for this brick."""
    goals = load_goals()
    title_lower = title.lower()[:40]
    for g in goals:
        if title_lower in g.get("title", "").lower():
            return True
        if title_lower in g.get("description", "").lower():
            return True
    return False


def find_gap_department(brick_title: str) -> list:
    """Find which departments have gaps this brick could fill."""
    title_lower = brick_title.lower()
    matches = []
    for dept, keywords in DEPT_GAPS.items():
        for kw in keywords:
            if kw.lower() in title_lower:
                matches.append(dept)
                break
    return matches


def create_goal(brick: dict, departments: list):
    """Create a goal in goal_queue.json for testing this brick."""
    title = brick.get("title", "Unknown brick")[:60]

    # Bayesian priority scoring
    try:
        from bayesian_scorer import score_goal_priority
        bayesian_priority = score_goal_priority({
            "type": "rd_test",
            "urgency": 7,
            "impact": 7,
            "source": brick.get("source", ""),
        })
    except Exception:
        bayesian_priority = 6.0  # fallback

    goal = {
        "id": f"g-brick-{brick.get('hash', 'x')[:8]}",
        "title": f"Test brick: {title}",
        "tier": 2,
        "priority": bayesian_priority,
        "bayesian_scored": True,
        "created_at": datetime.now().isoformat(),
        "status": "active",
        "progress": 0.0,
        "related_actions": ["rd-test"],
        "deadline": None,
        "description": f"New brick from {brick.get('source','?')}. Departments: {', '.join(departments)}. Needs testing and validation.",
        "done_when": [
            "Brick tested on real data",
            "Math verified (cost < revenue = profit)",
            "ЦА filled for this brick"
        ],
        "updated_at": datetime.now().isoformat()
    }

    if GOALS_FILE.exists():
        try:
            data = json.loads(GOALS_FILE.read_text("utf-8"))
            goals = data.get("goals", [])
        except Exception:
            goals = []
    else:
        goals = []

    goals.append(goal)
    data = {"goals": goals, "updated_at": datetime.now().isoformat()}
    GOALS_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    log_dev("goal_created", title, departments)
    return goal


def log_dev(action: str, title: str, departments: list = None):
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    entry = {
        "ts": datetime.now().isoformat(),
        "action": action,
        "title": title,
        "departments": departments or [],
    }
    with open(DEV_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def check_weekly_lessons():
    """Check if weekly lesson extraction is needed (Monday)."""
    today = datetime.now()
    if today.weekday() != 0:  # Monday
        return

    # Check if we already extracted this week
    week_key = today.strftime("%Y-W%W")
    if DEV_LOG.exists():
        content = DEV_LOG.read_text("utf-8")
        if week_key in content:
            return  # Already extracted this week

    # Extract lessons from DECISION_LOG
    if DECISION_LOG.exists():
        decisions = DECISION_LOG.read_text("utf-8")
        lessons = decisions[-2000:]  # Last 2000 chars

        lesson_entry = f"""
## {today.strftime('%Y-%m-%d')} — Еженедельный урок

**Решения за неделю:**
{lessons[-1500:]}

**Уроки:**
- (извлечь из решений выше)

**Действия:**
- (обновить POLICIES.md если нужно)

---
"""
        if LESSONS_FILE.exists():
            with open(LESSONS_FILE, "a", encoding="utf-8") as f:
                f.write(lesson_entry)
        else:
            LESSONS_FILE.write_text(lesson_entry, encoding="utf-8")

        log_dev("weekly_lessons", f"Weekly lessons {week_key}")
        print(f"Weekly lessons extracted: {week_key}")


def check_metrics():
    """Check daily metrics using Bayesian flow health assessment."""
    try:
        from bayesian_scorer import assess_flow_health
        health = assess_flow_health()

        alert_level = health.get("alert_level", "none")
        p_alive = health.get("p_flow_alive", 0.5)
        daily_rate = health.get("daily_rate", 0)

        if alert_level == "critical":
            print(f"CRITICAL: P(flow_alive)={p_alive:.2f} < 0.4 — signal flow likely dead")
            print(f"  Daily rate: {daily_rate}, Today: {health.get('today', 0)}, Week: {health.get('week_total', 0)}")
            log_dev("alert_critical_flow", f"p={p_alive:.2f} rate={daily_rate}")
        elif alert_level == "warning":
            print(f"WARNING: P(flow_alive)={p_alive:.2f} — signal flow degraded")
            print(f"  Daily rate: {daily_rate}, Today: {health.get('today', 0)}")
            log_dev("alert_warning_flow", f"p={p_alive:.2f} rate={daily_rate}")
        else:
            print(f"Flow OK: P(alive)={p_alive:.2f}, rate={daily_rate}/day")
    except Exception as e:
        # Fallback to simple check
        today = datetime.now().strftime("%Y-%m-%d")
        if BRICKS_LOG.exists():
            lines = BRICKS_LOG.read_text("utf-8").strip().split("\n")
            today_bricks = [l for l in lines if today in l and '"added"' in l]
            if len(today_bricks) == 0:
                print(f"ALERT: R&D 0 bricks today ({today}). Watchdog should create alert.")
                log_dev("alert_no_bricks", today)


def process_new_bricks():
    """Process new bricks and create goals if they fill gaps."""
    if not BRICKS_LOG.exists():
        print("No bricks log.")
        return 0

    lines = BRICKS_LOG.read_text("utf-8").strip().split("\n")
    goals_created = 0

    for line in lines:
        if not line.strip():
            continue
        try:
            brick = json.loads(line)
        except json.JSONDecodeError:
            continue

        if brick.get("action") != "added":
            continue

        title = brick.get("title", "")

        # Check if goal already exists
        if goal_exists_for(title):
            continue

        # Find which departments have gaps
        departments = find_gap_department(title)

        if departments:
            create_goal(brick, departments)
            goals_created += 1
        else:
            log_dev("no_gap_found", title)

    return goals_created


def status():
    """Show dev processor status."""
    if DEV_LOG.exists():
        lines = DEV_LOG.read_text("utf-8").strip().split("\n")
        goals = sum(1 for l in lines if '"goal_created"' in l)
        alerts = sum(1 for l in lines if '"alert' in l)
        weekly = sum(1 for l in lines if '"weekly_lessons"' in l)
        print(f"Goals created: {goals}")
        print(f"Alerts: {alerts}")
        print(f"Weekly extractions: {weekly}")
        print(f"Total actions: {len(lines)}")
        print("\nRecent:")
        for l in lines[-5:]:
            try:
                e = json.loads(l)
                print(f"  [{e.get('action')}] {e.get('title','')[:50]}")
            except Exception:
                pass
    else:
        print("No dev actions yet.")


def main():
    import sys
    if "--status" in sys.argv:
        status()
        return

    # Process new bricks
    goals = process_new_bricks()
    if goals:
        print(f"GOALS CREATED: {goals}")
    else:
        print("No new goals (all exist or no matching gaps).")

    # Check weekly lessons
    check_weekly_lessons()

    # Check daily metrics
    check_metrics()


if __name__ == "__main__":
    main()

"""
Crystal v3 — Конфигурация

Delegates HERMES_HOME resolution to hermes_config (single source of truth).
"""
import os
import sys
from pathlib import Path

# ── Import unified HERMES_HOME ──────────────────────────────────────
_scripts_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _scripts_dir not in sys.path:
    sys.path.insert(0, _scripts_dir)

from hermes_config import HERMES_HOME as _HERMES_HOME, CACHE_DIR as _UNIFIED_CACHE_DIR

# ── Paths ──────────────────────────────────────────────────────────
# Use the unified HERMES_HOME from hermes_config instead of duplicate resolution.
HERMES_HOME = str(_HERMES_HOME)
CRYSTAL_HOME = os.path.join(HERMES_HOME, "crystal")
CACHE_DIR = os.path.join(HERMES_HOME, "cache", "crystal")
SESSIONS_DIR = os.path.join(HERMES_HOME, "sessions")
STATE_DB = os.path.join(HERMES_HOME, "state.db")
SKILLS_DIR = os.path.join(HERMES_HOME, "skills")
CONFIG_PATH = os.path.join(HERMES_HOME, "config.yaml")
ENV_PATH = os.path.join(HERMES_HOME, ".env")

# Скрипты Crystal
SCRIPTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CRYSTAL_SCRIPTS = os.path.join(SCRIPTS_DIR, "crystal")


# ── Данные (JSON-файлы в cache/crystal/) ──────────────────────────────

class Paths:
    """Все пути к JSON-файлам Crystal"""
    signals = os.path.join(CACHE_DIR, "signals.json")
    patterns = os.path.join(CACHE_DIR, "patterns.json")
    needs = os.path.join(CACHE_DIR, "needs.json")
    priority = os.path.join(CACHE_DIR, "priority.json")
    dependencies = os.path.join(CACHE_DIR, "dependencies.json")
    proposals = os.path.join(CACHE_DIR, "proposals.json")
    feedback = os.path.join(CACHE_DIR, "feedback.json")
    staleness = os.path.join(CACHE_DIR, "staleness.json")
    departments = os.path.join(CACHE_DIR, "departments.json")
    energy = os.path.join(CACHE_DIR, "energy.json")
    changelog = os.path.join(CACHE_DIR, "changelog.json")
    synergies = os.path.join(CACHE_DIR, "synergies.json")
    goals = os.path.join(CACHE_DIR, "goals.json")
    intelligence = os.path.join(CACHE_DIR, "intelligence.json")
    snapshots_dir = os.path.join(CACHE_DIR, "snapshots")
    knowledge_base = os.path.join(CACHE_DIR, "knowledge_base.json")
    communication = os.path.join(CACHE_DIR, "communication.json")
    resources = os.path.join(CACHE_DIR, "resources.json")
    evolution = os.path.join(CACHE_DIR, "evolution.json")
    alerts = os.path.join(CACHE_DIR, "alerts.json")


# ── Отделы ────────────────────────────────────────────────────────────

DEPARTMENTS = {
    "youtube": {
        "name": "YouTube",
        "emoji": "📺",
        "skills": ["youtube-transcript", "youtube-content", "video_gen"],
        "keywords": ["youtube", "video", "канал", "контент", "загрузка"],
    },
    "social-media": {
        "name": "Social Media",
        "emoji": "📱",
        "skills": ["social-media", "x_search"],
        "keywords": ["постинг", "соцсети", "twitter", "instagram", "тикток"],
    },
    "websites": {
        "name": "Websites",
        "emoji": "🌐",
        "skills": ["claude-design", "popular-web-designs", "page-agent", "svelte-bits"],
        "keywords": ["сайт", "landing", "дизайн", "фронтенд", "html", "css"],
    },
    "telegram-bots": {
        "name": "Telegram Bots",
        "emoji": "🤖",
        "skills": ["telegram-bot-integration", "telegram-service-bot"],
        "keywords": ["telegram", "бот", "aiogram", "telebot"],
    },
    "monetization": {
        "name": "Monetization",
        "emoji": "💰",
        "skills": ["earning-with-ai"],
        "keywords": ["деньги", "заработок", "монетизация", "продажа", "фриланс"],
    },
    "ai-core": {
        "name": "AI Core",
        "emoji": "🧠",
        "skills": ["hermes-agent", "coding-patterns"],
        "keywords": ["hermes", "модель", "провайдер", "агент", "ai"],
    },
    "devops": {
        "name": "DevOps",
        "emoji": "🛠",
        "skills": ["devops", "surgical-fix", "codebase-update-audit"],
        "keywords": ["деплой", "сервер", "docker", "ci/cd", "инфраструктура"],
    },
    "data": {
        "name": "Data",
        "emoji": "📊",
        "skills": ["data-analyst", "jupyter-live-kernel"],
        "keywords": ["данные", "аналитика", "дашборд", "отчёт", "график"],
    },
}


# ── Конфигурация по умолчанию ─────────────────────────────────────────

DEFAULT_CONFIG = {
    # Наблюдение
    "session_reader": {
        "max_sessions": 50,
        "signal_min_length": 10,
    },
    "pattern_detector": {
        "min_frequency": 2,
        "severity_threshold": 0.3,
    },

    # Анализ
    "need_analyzer": {
        "min_priority": 0.2,
    },
    "priority_engine": {
        "weights": {
            "urgency": 0.4,
            "impact": 0.4,
            "effort": 0.2,
        }
    },
    "risk_assessment": {
        "auto_approve_max": "safe",
    },

    # Действия
    "dev_proposer": {
        "max_proposals_per_run": 5,
    },
    "testing": {
        "default_level": "quick",
        "full_test_threshold": "risky",
    },

    # Обратная связь
    "feedback_loop": {
        "measurement_window_days": 7,
    },
    "rollback": {
        "auto_rollback_threshold": -0.3,
        "max_snapshots": 50,
    },

    # Мониторинг
    "staleness": {
        "check_interval_hours": 24,
        "skill_stale_days": 30,
        "dependency_stale_days": 60,
    },
    "alerts": {
        "max_pending": 10,
    },
    "resources": {
        "budget_warn_percent": 80,
        "budget_critical_percent": 95,
    },

    # Эволюция
    "self_evolution": {
        "min_evolution_score": 0.1,
        "check_interval_hours": 168,
    },

    # Общение
    "communication": {
        "default_length": "short",
        "default_tone": "friendly",
    },
}


# ── Утилиты ───────────────────────────────────────────────────────────

def get_department(text: str) -> str:
    """Определить отдел по тексту"""
    text_lower = text.lower()
    scores = {}
    for dept_id, dept in DEPARTMENTS.items():
        score = sum(1 for kw in dept["keywords"] if kw in text_lower)
        if score > 0:
            scores[dept_id] = score
    if scores:
        return max(scores, key=scores.get)
    return "ai-core"


def ensure_dirs():
    """Создать все необходимые директории"""
    os.makedirs(CACHE_DIR, exist_ok=True)
    os.makedirs(Paths.snapshots_dir, exist_ok=True)

"""
Crystal v3 — Модуль 15: Long-term Goals
Стратегические цели
"""

# Revisit: when goal definitions, tracking logic, or progress criteria change. Last touched: 2026-07-02.

from .models import Goal, Proposal
from .config import Paths
from .models import load_json, save_json


class GoalTracker:
    """Отслеживает прогресс целей"""

    def __init__(self):
        pass

    def update(self, goals: list, proposals: list) -> list:
        """Обновить прогресс на основе proposals"""
        # Если целей нет — создаём базовые
        if not goals:
            goals = self._create_defaults()

        # Обновляем прогресс
        for goal in goals:
            relevant = [p for p in proposals if p.department == goal.department]
            if relevant:
                # Прогресс = доля применённых proposals
                applied = sum(1 for p in relevant if p.applied)
                goal.progress = applied / len(relevant) if relevant else 0

        return goals

    def _create_defaults(self) -> list:
        """Создать дефолтные цели"""
        defaults = [
            Goal(
                title="Стабильная работа AI",
                description="Минимум ошибок, максимум полезности",
                department="ai-core",
                progress=0.0,
            ),
            Goal(
                title="Автоматизация контента",
                description="YouTube + соцсети автоматизированы",
                department="youtube",
                progress=0.0,
            ),
            Goal(
                title="Монетизация",
                description="Стабильный доход от AI навыков",
                department="monetization",
                progress=0.0,
            ),
            Goal(
                title="Надёжная инфраструктура",
                description="Деплой без сбоев",
                department="devops",
                progress=0.0,
            ),
        ]
        return defaults

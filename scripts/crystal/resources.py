"""
Crystal v3 — Модуль 21: Resource Monitor
Бюджет и лимиты
"""

# Revisit: when resource limits, budget tracking, or model selection logic changes. Last touched: 2026-07-02.

import os
from .models import ResourceState
from .config import Paths, HERMES_HOME
from .models import load_json


class ResourceMonitor:
    """Мониторит бюджет и лимиты"""

    def __init__(self):
        pass

    def check(self) -> ResourceState:
        """Проверить текущее состояние ресурсов"""
        # Загружаем сохранённое состояние
        saved = load_json(Paths.resources)
        if saved and isinstance(saved, dict):
            state = ResourceState(**saved)
        else:
            state = ResourceState()

        # Обновляем disk usage
        state.disk_usage_mb = self._get_disk_usage()
        state.last_updated = self._now()

        return state

    def _get_disk_usage(self) -> float:
        """Получить использование диска Hermes в MB (быстро, без os.walk)"""
        try:
            import shutil
            usage = shutil.disk_usage(HERMES_HOME)
            return usage.used / (1024 * 1024)
        except Exception:
            return 0.0

    def _now(self) -> str:
        """Текущее время ISO"""
        from datetime import datetime
        return datetime.now().isoformat()

    def suggest_model(self, state: ResourceState) -> str:
        """Предложить модель на основе бюджета"""
        if state.budget_spent > state.budget_limit * 0.9:
            return "deepseek/deepseek-chat"  # дешёвая
        elif state.budget_spent > state.budget_limit * 0.7:
            return "xiaomi/mimo-v2.5-free"  # средняя
        else:
            return "anthropic/claude-sonnet-4"  # дорогая

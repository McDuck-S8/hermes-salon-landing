"""
Crystal v3 — Модуль 10: Proactive Alerts
Проактивные уведомления
"""

# Revisit: when alert triggers, frustration thresholds, or notification channels change. Last touched: 2026-07-02.

from .models import Signal, Pattern, Alert


class AlertManager:
    """Генерирует проактивные уведомления"""

    def __init__(self, config=None):
        self.config = config or {}
        self.max_pending = self.config.get("max_pending", 10)

    def check(self, signals: list, patterns: list) -> list:
        """Проверить и сгенерировать уведомления"""
        alerts = []

        # 1. Много фрустрации за последние сессии
        recent_frustration = [s for s in signals if s.type == "frustration"]
        if len(recent_frustration) >= 5:
            alerts.append(Alert(
                type="frustration",
                severity="warning",
                title="Высокий уровень фрустрации",
                message=f"{len(recent_frustration)} сигналов фрустрации. Рекомендуется проверить качество.",
                action_required=True,
            ))

        # 2. Много поправок — модель не понимает
        recent_corrections = [s for s in signals if s.type == "correction"]
        if len(recent_corrections) >= 3:
            alerts.append(Alert(
                type="quality",
                severity="warning",
                title="Много поправок",
                message=f"{len(recent_corrections)} поправок. Возможно, нужно улучшить промпты или скиллы.",
                action_required=True,
            ))

        # 3. Нет активности
        if not signals:
            alerts.append(Alert(
                type="idle",
                severity="info",
                title="Нет активности",
                message="Нет новых сессий. Crystal готов к работе.",
                action_required=False,
            ))

        # 4. Критические паттерны
        critical_patterns = [p for p in patterns if p.severity >= 0.8]
        if critical_patterns:
            alerts.append(Alert(
                type="critical_pattern",
                severity="critical",
                title="Критические паттерны",
                message=f"Найдено {len(critical_patterns)} критических паттернов",
                action_required=True,
            ))

        return alerts[:self.max_pending]

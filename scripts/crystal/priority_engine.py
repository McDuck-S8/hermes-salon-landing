"""
Crystal v3 — Модуль 4: Priority Engine
Определяет что делать первым
"""

# Revisit: when priority engine logic, urgency/impact/effort weights, or energy modeling changes. Last touched: 2026-07-02.


from .models import Need, PrioritizedItem, EnergyState, DependencyGraph


class PriorityEngine:
    """Сортирует needs по urgency × impact / effort"""

    DEPARTMENT_WEIGHTS = {
        "ai-core": 1.2,        # ядро — выше приоритет
        "devops": 1.1,
        "telegram-bots": 1.0,
        "websites": 1.0,
        "youtube": 0.9,
        "social-media": 0.9,
        "monetization": 0.8,
        "data": 0.7,
    }

    def __init__(self, config=None):
        self.config = config or {}
        self.weights = self.config.get("weights", {
            "urgency": 0.4,
            "impact": 0.4,
            "effort": 0.2,
        })

    def prioritize(self, needs: list, energy: EnergyState, dependencies: DependencyGraph) -> list:
        """Определяет приоритеты"""
        if not needs:
            return []

        items = []
        for need in needs:
            urgency = self._calculate_urgency(need)
            impact = self._calculate_impact(need)
            effort = self._estimate_effort(need)

            item = PrioritizedItem(
                need_id=need.id,
                urgency=urgency,
                impact=impact,
                effort=effort,
                dependencies=[],
            )
            item.calculate_score()

            # Учитываем энергию пользователя
            if energy.level == "low":
                item.score *= 0.8  # при низкой энергии — менее амбициозные задачи
            elif energy.level == "high":
                item.score *= 1.2  # при высокой — можно больше

            # Учитываем вес отдела
            dept_weight = self.DEPARTMENT_WEIGHTS.get(need.department, 1.0)
            item.score *= dept_weight

            items.append(item)

        # Сортируем по score
        items.sort(key=lambda x: x.score, reverse=True)

        return items

    def _calculate_urgency(self, need: Need) -> float:
        """Вычислить срочность"""
        impact_map = {
            "critical": 1.0,
            "high": 0.8,
            "medium": 0.5,
            "low": 0.3,
        }
        return impact_map.get(need.impact, 0.5)

    def _calculate_impact(self, need: Need) -> float:
        """Вычислить влияние"""
        return need.priority

    def _estimate_effort(self, need: Need) -> float:
        """Оценить усилия (0.0 = легко, 1.0 = сложно)"""
        effort_map = {
            "correction_loop": 0.6,
            "frustration_spike": 0.7,
            "missing_knowledge": 0.4,
            "workflow_success": 0.2,
            "unmet_need": 0.5,
            "department_focus": 0.3,
        }
        return effort_map.get(need.pattern_type, 0.5)

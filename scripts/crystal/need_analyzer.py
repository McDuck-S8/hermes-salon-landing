"""
Crystal v3 — Модуль 3: Need Analyzer
Из паттернов формулирует потребности
"""

# Revisit: when need analysis logic, pattern-to-need mapping, or urgency/impact scoring changes. Last touched: 2026-07-02.


from collections import defaultdict
from .models import Pattern, Need


class NeedAnalyzer:
    """Из паттернов формулирует конкретные потребности"""

    # Маппинг паттерн → потребность
    NEED_MAPPING = {
        "correction_loop": {
            "need": "Улучшить качество выполнения",
            "impact": "high",
            "base_priority": 0.8,
        },
        "frustration_spike": {
            "need": "Уменьшить количество ошибок",
            "impact": "critical",
            "base_priority": 0.9,
        },
        "missing_knowledge": {
            "need": "Добавить недостающие знания",
            "impact": "medium",
            "base_priority": 0.6,
        },
        "workflow_success": {
            "need": "Закрепить успешный паттерн",
            "impact": "low",
            "base_priority": 0.3,
        },
        "unmet_need": {
            "need": "Расширить функциональность",
            "impact": "medium",
            "base_priority": 0.5,
        },
        "department_focus": {
            "need": "Оптимизировать для доменного отдела",
            "impact": "low",
            "base_priority": 0.2,
        },
    }

    def __init__(self, config=None):
        self.config = config or {}
        self.min_priority = self.config.get("min_priority", 0.2)

    def analyze(self, patterns: list) -> list:
        """Из паттернов формулирует needs"""
        if not patterns:
            return []

        needs = []

        # Группируем паттерны по department + type
        grouped = defaultdict(list)
        for p in patterns:
            key = (p.department, p.type)
            grouped[key].append(p)

        for (dept, ptype), group in grouped.items():
            mapping = self.NEED_MAPPING.get(ptype)
            if not mapping:
                continue

            # Агрегируем серьёзность
            total_severity = sum(p.severity for p in group)
            avg_severity = total_severity / len(group)
            max_frequency = max(p.frequency for p in group)

            # Вычисляем приоритет
            priority = mapping["base_priority"]
            priority += min(avg_severity * 0.2, 0.15)  # + за серьёзность
            priority += min(max_frequency * 0.02, 0.1)  # + за частоту
            priority = min(priority, 1.0)

            if priority < self.min_priority:
                continue

            # Формулируем описание
            descriptions = [p.description for p in group[:3]]
            description = f"{mapping['need']} ({dept}): " + "; ".join(descriptions)

            need = Need(
                pattern_type=ptype,
                description=description,
                priority=priority,
                impact=mapping["impact"],
                department=dept,
            )
            needs.append(need)

        # Сортируем по приоритету
        needs.sort(key=lambda n: n.priority, reverse=True)

        return needs

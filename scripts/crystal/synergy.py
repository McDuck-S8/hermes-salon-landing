"""
Crystal v3 — Модуль 14: Cross-department Synergy
Находит связи между отделами
"""

# Revisit: when synergy patterns, cross-department relationships, or connection logic changes. Last touched: 2026-07-02.

from collections import defaultdict
from .models import Proposal, Need, Synergy
from .config import DEPARTMENTS


class SynergyFinder:
    """Находит связи между отделами"""

    # Известные паттерны синергии
    SYNERGY_PATTERNS = [
        {
            "departments": ["youtube", "social-media"],
            "type": "content_pipeline",
            "description": "YouTube контент → посты в соцсети",
            "potential": "high",
        },
        {
            "departments": ["youtube", "monetization"],
            "type": "data_flow",
            "description": "YouTube аналитика → монетизация",
            "potential": "medium",
        },
        {
            "departments": ["ai-core", "devops"],
            "type": "tech_stack",
            "description": "AI ядро → деплой и инфраструктура",
            "potential": "high",
        },
        {
            "departments": ["ai-core", "telegram-bots"],
            "type": "skill_reuse",
            "description": "AI навыки → Telegram боты",
            "potential": "medium",
        },
        {
            "departments": ["websites", "monetization"],
            "type": "content_pipeline",
            "description": "Сайты → лендинги для продаж",
            "potential": "medium",
        },
        {
            "departments": ["data", "ai-core"],
            "type": "data_flow",
            "description": "Данные → обучение AI",
            "potential": "high",
        },
        {
            "departments": ["devops", "websites"],
            "type": "tech_stack",
            "description": "Инфраструктура → хостинг сайтов",
            "potential": "medium",
        },
        {
            "departments": ["telegram-bots", "monetization"],
            "type": "content_pipeline",
            "description": "Боты → автоматизация продаж",
            "potential": "high",
        },
    ]

    def __init__(self):
        pass

    def find(self, proposals: list, needs: list) -> list:
        """Находит связи между отделами"""
        synergies = []

        # Определяем какие отделы активны
        active_depts = set()
        for p in proposals:
            active_depts.add(p.department)
        for n in needs:
            active_depts.add(n.department)

        # Ищем совпадения с известными паттернами
        for pattern in self.SYNERGY_PATTERNS:
            dept_set = set(pattern["departments"])
            if dept_set.issubset(active_depts):
                synergy = Synergy(
                    departments=pattern["departments"],
                    type=pattern["type"],
                    description=pattern["description"],
                    potential=pattern["potential"],
                    action=f"Объединить усилия: {pattern['description']}",
                )
                synergies.append(synergy)

        # Ищем ad-hoc связи по proposals
        dept_proposals = defaultdict(list)
        for p in proposals:
            dept_proposals[p.department].append(p)

        for dept1 in dept_proposals:
            for dept2 in dept_proposals:
                if dept1 < dept2:  # избегаем дублей
                    # Проверяем есть ли общий контекст
                    common = self._find_common_context(
                        dept_proposals[dept1],
                        dept_proposals[dept2]
                    )
                    if common:
                        synergy = Synergy(
                            departments=[dept1, dept2],
                            type="skill_reuse",
                            description=f"Общий контекст: {common}",
                            potential="medium",
                            action=f"Рассмотреть объединение {dept1} + {dept2}",
                        )
                        synergies.append(synergy)

        return synergies

    def _find_common_context(self, props1: list, props2: list) -> str:
        """Найти общий контекст между двумя группами proposals"""
        words1 = set()
        words2 = set()

        for p in props1:
            words1.update(p.description.lower().split())
        for p in props2:
            words2.update(p.description.lower().split())

        common = words1 & words2
        # Убираем стоп-слова
        stop = {"и", "в", "на", "для", "от", "по", "не", "что", "как", "the", "and", "for", "to", "of"}
        common = common - stop

        if len(common) >= 2:
            return ", ".join(list(common)[:3])
        return ""

"""
Crystal v3 — Модуль 8: Development Proposer
Из потребностей генерирует конкретные действия
"""

# Revisit: when proposal generation logic, action types, or knowledge integration changes. Last touched: 2026-07-02.

from .models import Need, Proposal, KnowledgeEntry
from .config import DEPARTMENTS


class DevelopmentProposer:
    """Генерирует конкретные предложения из потребностей"""

    # Что делать при каждом типе need
    ACTIONS = {
        "correction_loop": {
            "action": "patch_skill",
            "template": "Улучшить скилл для {department}: устранить повторяющиеся ошибки",
            "auto": False,
        },
        "frustration_spike": {
            "action": "patch_skill",
            "template": "Критическое улучшение для {department}: снизить количество ошибок",
            "auto": False,
        },
        "missing_knowledge": {
            "action": "create_skill",
            "template": "Создать/дополнить скилл для {department}: добавить недостающие знания",
            "auto": True,
        },
        "workflow_success": {
            "action": "create_skill",
            "template": "Закрепить успешный паттерн для {department} как скилл",
            "auto": True,
        },
        "unmet_need": {
            "action": "patch_skill",
            "template": "Расширить функционал для {department}",
            "auto": False,
        },
        "department_focus": {
            "action": "update_dox",
            "template": "Обновить документацию для интенсивно используемого отдела {department}",
            "auto": True,
        },
    }

    def __init__(self, config=None):
        self.config = config or {}
        self.max_proposals = self.config.get("max_proposals_per_run", 20)

    def propose(self, needs: list, knowledge: list) -> list:
        """Генерирует предложения из потребностей"""
        if not needs:
            return []

        proposals = []
        kb = KnowledgeEntry()  # для поиска похожих решений

        for need in needs[:self.max_proposals]:
            action_config = self.ACTIONS.get(need.pattern_type)
            if not action_config:
                continue

            # Проверяем базу знаний
            known_solution = None
            for k in knowledge:
                if need.department in k.department or need.pattern_type in k.problem:
                    known_solution = k
                    break

            # Формируем описание
            description = action_config["template"].format(department=need.department)

            if known_solution:
                description += f" (уже решалось: {known_solution.solution[:50]})"

            proposal = Proposal(
                action=action_config["action"],
                description=description,
                priority=need.priority,
                department=need.department,
                auto=action_config["auto"],
            )
            proposals.append(proposal)

        return proposals

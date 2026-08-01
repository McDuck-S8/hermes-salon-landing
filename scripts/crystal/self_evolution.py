"""
Crystal v3 — Модуль 22: Self-Evolution
Самоэволюция
"""

# Revisit: when self-evolution strategies, module optimization, or refactoring triggers change. Last touched: 2026-07-02.

from .models import Signal, Pattern, Proposal, EvolutionEntry


class SelfEvolution:
    """Оценивает и улучшает модули"""

    def __init__(self, config=None):
        self.config = config or {}
        self.min_score = self.config.get("min_evolution_score", 0.1)

    def evolve(self, signals: list, patterns: list, proposals: list) -> list:
        """Найти возможности для улучшения"""
        entries = []

        # 1. Модули с низким feedback
        low_feedback = [p for p in proposals if not p.tested and p.auto]
        if low_feedback:
            entries.append(EvolutionEntry(
                module="dev_proposer",
                action="optimize",
                reason=f"{len(low_feedback)} proposals не тестированы",
                before_score=0.5,
                after_score=0.7,
            ))

        # 2. Паттерны не покрыты модулями
        covered_types = {"correction_loop", "frustration_spike", "missing_knowledge",
                        "workflow_success", "unmet_need", "department_focus"}
        uncovered = [p for p in patterns if p.type not in covered_types]
        if uncovered:
            entries.append(EvolutionEntry(
                module="pattern_detector",
                action="new_module",
                reason=f"{len(uncovered)} паттернов не покрыты: {set(p.type for p in uncovered)}",
                before_score=0.6,
                after_score=0.8,
            ))

        # 3. Слишком много паттернов одного типа
        from collections import Counter
        type_counts = Counter(p.type for p in patterns)
        for ptype, count in type_counts.items():
            if count > 50:
                entries.append(EvolutionEntry(
                    module="pattern_detector",
                    action="refactor",
                    reason=f"Слишком много паттернов типа {ptype}: {count}",
                    before_score=0.4,
                    after_score=0.6,
                ))

        return entries

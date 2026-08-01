"""
Crystal v3 — Модуль 19: Knowledge Base
Хранит решённые проблемы, рабочие подходы, провалы
"""

# Revisit: when knowledge base search, confidence thresholds, or department filtering changes. Last touched: 2026-07-02.

from .models import KnowledgeEntry


class KnowledgeBase:
    """База проверенных решений"""

    def __init__(self, entries=None):
        self.entries = entries or []

    def find(self, problem: str) -> KnowledgeEntry:
        """
        Ищет в базе знаний похожую проблему
        Возвращает лучшее совпадение или None
        """
        if not self.entries:
            return None

        problem_words = set(problem.lower().split())
        best_match = None
        best_score = 0

        for entry in self.entries:
            # Простое сравнение по словам
            entry_words = set(entry.problem.lower().split())
            common = problem_words & entry_words
            score = len(common) / max(len(problem_words), 1)

            # Учитываем confidence и times_used
            score *= entry.confidence
            if entry.times_used > 0:
                score *= 1.1

            if score > best_score and score > 0.2:
                best_score = score
                best_match = entry

        if best_match:
            best_match.times_used += 1

        return best_match

    def add(self, problem: str, solution: str, effect: str, department: str = ""):
        """Добавить новое решение"""
        entry = KnowledgeEntry(
            problem=problem,
            solution=solution,
            effect=effect,
            department=department,
        )
        self.entries.append(entry)
        return entry

    def get_by_department(self, department: str) -> list:
        """Получить решения для конкретного отдела"""
        return [e for e in self.entries if e.department == department]

    def get_confident(self, min_confidence: float = 0.7) -> list:
        """Получить только уверенные решения"""
        return [e for e in self.entries if e.confidence >= min_confidence]

    def to_json(self) -> list:
        """Экспорт в JSON"""
        from dataclasses import asdict
        return [asdict(e) for e in self.entries]

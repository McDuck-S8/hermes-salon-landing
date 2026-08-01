"""
Crystal v3 — Петля обратной связи
Предложение → Применение → Оценка → Обучение
"""

# Revisit: when feedback evaluation metrics, execution verification, or assessment criteria change. Last touched: 2026-07-02.

import os
import json
from datetime import datetime
from .config import CACHE_DIR
from .models import Proposal, Assessment, save_json


class FeedbackLoop:
    """Петля: предложение → execute → measure → learn"""

    def __init__(self):
        self.history_file = os.path.join(CACHE_DIR, "feedback_history.json")

    def execute_and_evaluate(self, proposal, executor, engine):
        """Выполнить предложение и оценить результат — полный цикл: execute → verify → save to KB"""
        before = self._snapshot(engine)
        result = executor._execute_one(proposal)
        after = self._snapshot(engine)
        assessment = self._assess(proposal, before, after, result)
        self._save(proposal, result, assessment)

        # ЧЕТВЁРТОЕ ЗВЕНО: сохраняем решение в knowledge_base
        if result.get("success"):
            self._save_to_knowledge_base(proposal, result, assessment)

        return {"proposal": proposal, "result": result, "assessment": assessment}

    def _save_to_knowledge_base(self, proposal, result, assessment):
        """Сохранить решение в knowledge_base — закрыть цепочку проблема→решение→выполнение→проверка"""
        from .models import KnowledgeEntry, save_json
        from .config import Paths

        # Загружаем текущую базу
        kb = []
        if os.path.exists(Paths.knowledge_base):
            try:
                with open(Paths.knowledge_base, "r", encoding="utf-8") as f:
                    kb = json.load(f)
            except Exception:
                kb = []

        # Формируем запись знания
        entry = {
            "problem": proposal.description,
            "solution": result.get("path", "executed"),
            "department": proposal.department,
            "action": proposal.action,
            "success": True,
            "score": assessment.score if hasattr(assessment, "score") else 0.7,
            "timestamp": datetime.now().isoformat(),
            "source": "crystal-execution",
        }

        # Проверяем дубликат по problem
        existing_problems = {e.get("problem") for e in kb}
        if entry["problem"] not in existing_problems:
            kb.append(entry)
            # Ограничиваем размер
            if len(kb) > 500:
                kb = kb[-500:]
            save_json(kb, Paths.knowledge_base)

    def _snapshot(self, engine):
        """Снимок состояния"""
        return {
            "signals": len(engine.signals),
            "patterns": len(engine.patterns),
            "needs": len(engine.needs),
            "proposals": len(engine.proposals),
            "alerts": len(engine.alerts),
        }

    def _assess(self, proposal, before, after, result):
        """Оценить эффект предложение"""
        score = 0.0

        if before["alerts"] > after["alerts"]:
            score += 0.3

        success_flag = result.get("success", False)
        dry_run_flag = result.get("dry_run", False)

        if success_flag:
            score += 0.4
        if dry_run_flag:
            score += 0.2

        score += 0.1

        ok = score >= 0.3

        return Assessment(
            proposal_id=proposal.id,
            metric="combined",
            before=float(before["alerts"]),
            after=float(after["alerts"]),
            delta=float(before["alerts"] - after["alerts"]),
            success=ok,
        )

    def _save(self, proposal, result, assessment):
        """Сохранить историю"""
        history = self._load()
        entry = {
            "timestamp": datetime.now().isoformat(),
            "proposal_id": proposal.id,
            "action": proposal.action,
            "department": proposal.department,
            "success": result.get("success", False),
            "assessment_success": assessment.success,
            "delta": assessment.delta,
        }
        history.append(entry)
        if len(history) > 100:
            history = history[-100:]
        save_json(history, self.history_file)

    def _load(self):
        """Загрузить историю"""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return []

    def get_stats(self):
        """Статистика"""
        history = self._load()
        if not history:
            return {"total": 0, "success_rate": 0, "avg_delta": 0}
        total = len(history)
        successes = sum(1 for h in history if h.get("assessment_success"))
        deltas = [h.get("delta", 0) for h in history]
        return {
            "total": total,
            "successes": successes,
            "success_rate": round(successes / total * 100, 1) if total else 0,
            "avg_delta": round(sum(deltas) / len(deltas), 2) if deltas else 0,
            "recent": history[-5:] if len(history) >= 5 else history,
        }

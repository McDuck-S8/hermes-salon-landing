"""
Crystal v3 — Модуль 7: Risk Assessment
Оценивает безопасность каждого proposal
"""

# Revisit: when risk levels, assessment factors, or auto-apply thresholds change. Last touched: 2026-07-02.

from .models import Proposal, RiskAssessment


class RiskAssessor:
    """Оценивает безопасность каждого proposal"""

    # Риски по типу действия
    ACTION_RISKS = {
        "create_skill": {"level": "safe", "score": 0.1},
        "patch_skill": {"level": "safe", "score": 0.15},
        "update_dox": {"level": "safe", "score": 0.05},
        "update_memory": {"level": "safe", "score": 0.1},
        "new_tool": {"level": "moderate", "score": 0.4},
        "architecture_change": {"level": "risky", "score": 0.7},
        "delete": {"level": "critical", "score": 0.9},
        "config_change": {"level": "moderate", "score": 0.3},
    }

    # Пороги для автоматического одобрения
    AUTO_APPROVE_LEVELS = {"safe"}

    def __init__(self, config=None):
        self.config = config or {}
        self.auto_approve_max = self.config.get("auto_approve_max", "safe")

    def assess(self, proposals: list) -> list:
        """Оценитьриск для каждого proposal"""
        if not proposals:
            return []

        assessments = []
        for proposal in proposals:
            assessment = self._assess_single(proposal)
            proposal.risk_level = assessment.level
            proposal.auto = assessment.auto_approve
            assessments.append(assessment)

        return assessments

    def _assess_single(self, proposal: Proposal) -> RiskAssessment:
        """Оценитьриск одного proposal"""
        # Базовый риск по типу действия
        base = self.ACTION_RISKS.get(proposal.action, {"level": "moderate", "score": 0.5})

        # Модификаторы
        score = base["score"]
        factors = []

        # 1. Если уже тестировано — снижаем риск
        if proposal.tested:
            score *= 0.7
            factors.append("tested")

        # 2. Если auto — повышаем осторожность
        if proposal.auto:
            score *= 1.2
            factors.append("auto_apply")

        # 3. Если.department = ai-core — выше риск (ядро системы)
        if proposal.department == "ai-core":
            score *= 1.1
            factors.append("core_system")

        # 4. Если description длинная — сложнее предсказать эффект
        if len(proposal.description) > 200:
            score *= 1.05
            factors.append("complex")

        # Определяем уровень
        level = self._score_to_level(score)

        # Определяем можно ли автоматически
        auto_approve = level in self.AUTO_APPROVE_LEVELS and not proposal.tested is False

        # Рекомендация
        recommendation = self._get_recommendation(level, factors)

        return RiskAssessment(
            proposal_id=proposal.id,
            level=level,
            score=min(score, 1.0),
            factors=factors,
            recommendation=recommendation,
            auto_approve=auto_approve,
        )

    def _score_to_level(self, score: float) -> str:
        """Перевести score в уровень"""
        if score <= 0.2:
            return "safe"
        elif score <= 0.5:
            return "moderate"
        elif score <= 0.75:
            return "risky"
        else:
            return "critical"

    def _get_recommendation(self, level: str, factors: list) -> str:
        """Рекомендация по уровню риска"""
        recommendations = {
            "safe": "✅ Безопасно — можно применять автоматически",
            "moderate": "⚠️ Умеренный риск — рекомендуется проверка",
            "risky": "🔴 Высокий риск — требуется подтверждение пользователя",
            "critical": "🛑 Критическийриск — запрещено без явного одобрения",
        }
        return recommendations.get(level, "❓ Неизвестный уровень")

"""
Crystal v3 — Модуль 20: Communication Adapter
Стиль общения
"""

# Revisit: when communication style profiles, formatting rules, or tone adaptation changes. Last touched: 2026-07-02.

from .models import CommunicationProfile


class CommunicationAdapter:
    """Адаптирует стиль общения под пользователя"""

    def __init__(self, profile=None):
        self.profile = profile or CommunicationProfile()

    def adapt(self, feedback_text: str) -> CommunicationProfile:
        """Адаптировать профиль по feedback"""
        text_lower = feedback_text.lower()

        # Определяем длину
        if any(w in text_lower for w in ["короче", "кратко", "brief", "short", "tl;dr"]):
            self.profile.length = "short"
        elif any(w in text_lower for w in ["подробнее", "подробнее", "detailed", "long"]):
            self.profile.length = "long"

        # Определяем тон
        if any(w in text_lower for w in ["формально", "formal", "professional"]):
            self.profile.tone = "formal"
        elif any(w in text_lower for w in ["дружески", "friendly", "casual"]):
            self.profile.tone = "friendly"
        elif any(w in text_lower for w in ["технически", "technical", "deep"]):
            self.profile.tone = "technical"

        # Определяем техничность
        if any(w in text_lower for w in ["проще", "простыми словами", "simple"]):
            self.profile.technicality = "low"
        elif any(w in text_lower for w in ["техничнее", "глубже", "technical"]):
            self.profile.technicality = "high"

        # Запоминаем поправку
        self.profile.learned_corrections.append(feedback_text[:100])

        return self.profile

    def format_response(self, text: str) -> str:
        """Отформатировать ответ по профилю"""
        if self.profile.length == "short":
            # Обрезаем до 3 предложений
            sentences = text.split(".")
            if len(sentences) > 3:
                text = ". ".join(sentences[:3]) + "."

        if self.profile.format == "lists":
            # Преобразуем в список если ещё не список
            if "\n-" not in text and "\n*" not in text:
                text = text.replace(". ", ".\n- ")

        return text

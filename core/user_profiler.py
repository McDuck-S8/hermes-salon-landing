"""
User Profiler — понимает пользователя как человека.

Не "юзер" а человек с:
- Обязательствами (семья, кредиты, здоровье)
- Ограничениями (время, юрисдикция, сервисы)
- Допустимым риском (что готов потерять)
- Горизонтом планирования (когда нужны деньги)
- Ценностями (что важно кроме денег)

Загружается в контекст при каждом цикле.
Задаёт вопросы ПО МЕРЕ НЕОБХОДИМОСТИ, а не все сразу.
"""
import json
from pathlib import Path

HERMES_HOME = Path(__file__).resolve().parent.parent
USER_PROFILE_FILE = HERMES_HOME / "cache" / "user_profile_extended.json"


def load_profile() -> dict:
    """Загружает расширенный профиль пользователя."""
    if USER_PROFILE_FILE.exists():
        try:
            return json.loads(USER_PROFILE_FILE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    return _default_profile()


def save_profile(profile: dict):
    """Сохраняет профиль."""
    CACHE_DIR = HERMES_HOME / "cache"
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    USER_PROFILE_FILE.write_text(
        json.dumps(profile, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )


def _default_profile() -> dict:
    return {
        "obligations": {
            "questioned": False,
            "data": {}
        },
        "jurisdiction": {
            "questioned": False,
            "data": {}
        },
        "risk_tolerance": {
            "questioned": False,
            "data": {}
        },
        "time_horizon": {
            "questioned": False,
            "data": {}
        },
        "values": {
            "questioned": False,
            "data": {}
        },
        "last_updated": None,
    }


def get_pending_questions(action_context: dict = None) -> list:
    """
    Определяет какие вопросы нужно задать ПРЯМО СЕЙЧАС.
    Не все сразу — только те которые релевантны текущему действию.
    """
    profile = load_profile()
    questions = []

    # Определяем контекст действия
    context = action_context or {}
    title = context.get("title", "").lower()

    # Финансовые действия → нужны данные о деньгах
    if any(kw in title for kw in ["income", "money", "revenue", "payment", "affiliate", "booking"]):
        if not profile["obligations"]["questioned"]:
            questions.append({
                "topic": "obligations",
                "question": "Есть ли у тебя кредиты или ипотека? Сколько платишь в месяц?",
                "why": "Чтобы понять минимальный доход для покрытия обязательств",
                "priority": "high",
            })
        if not profile["jurisdiction"]["questioned"]:
            questions.append({
                "topic": "jurisdiction",
                "question": "Ты самозанятый, ИП, или просто физлицо? Есть ли банковский счёт в РФ?",
                "why": "Определяет какие платёжные системы доступны и налоги",
                "priority": "high",
            })

    # Юридические действия → нужны данные о рисках
    if any(kw in title for kw in ["deploy", "launch", "client", "contract", "legal"]):
        if not profile["risk_tolerance"]["questioned"]:
            questions.append({
                "topic": "risk_tolerance",
                "question": "Сколько готов потерять денег если что-то пойдёт не так? $10? $100? $1000?",
                "why": "Определяет можно ли использовать реальные деньги в тестах",
                "priority": "medium",
            })

    # Стратегические действия → нужны данные о горизонте
    if any(kw in title for kw in ["scale", "long-term", "strategy", "plan"]):
        if not profile["time_horizon"]["questioned"]:
            questions.append({
                "topic": "time_horizon",
                "question": "Деньги нужны в течение недели, месяца, или года?",
                "why": "Определяет стратегию: быстрый MVP или долгосрочный продукт",
                "priority": "medium",
            })

    # Любы действия → ценности
    if not profile["values"]["questioned"] and any(kw in title for kw in ["build", "create", "launch"]):
        questions.append({
            "topic": "values",
            "question": "Что важнее: стабильный доход или возможность большого заработка? Свобода или предсказуемость?",
            "why": "Определяет тип стратегии:.safe vs risky, passive vs active",
            "priority": "low",
        })

    return questions


def record_answer(topic: str, answer: str):
    """Записывает ответ пользователя."""
    profile = load_profile()
    if topic in profile:
        profile[topic]["questioned"] = True
        profile[topic]["data"]["answer"] = answer
        profile[topic]["data"]["timestamp"] = datetime.now().isoformat()
        save_profile(profile)


def get_profile_for_context() -> str:
    """Возвращает профиль для включения в session context."""
    profile = load_profile()
    lines = ["=== USER PROFILE ==="]

    for topic, data in profile.items():
        if data.get("questioned") and data.get("data", {}).get("answer"):
            lines.append("%s: %s" % (topic, data["data"]["answer"][:100]))

    if len(lines) == 1:
        return "User profile: not yet collected"

    return "\n".join(lines)


if __name__ == "__main__":
    questions = get_pending_questions({"title": "Deploy hotel bot with Travelpayouts"})
    print("=== PENDING QUESTIONS ===")
    for q in questions:
        print("[%s] %s" % (q["priority"], q["question"]))
        print("  Why: %s" % q["why"])
        print()

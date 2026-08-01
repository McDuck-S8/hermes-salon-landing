"""
Self-Ask Engine — честные вопросы перед каждым решением.

Три точки проверки:
1. ДО действия — стоит ли делать?
2. ПОСЛЕ действия, ДО записи success — результат реальный?
3. ПЕРЕД показом пользователю — это правда?
"""


def self_ask_before_action(action: dict, context: dict = None) -> dict:
    """
    Точка 1: ДО выбора действия.
    Возвращает dict с честными ответами.
    """
    answers = {}

    # Вопрос 1: Результат или обслуживание?
    action_id = action.get("id", "")
    title = action.get("title", "").lower()
    infra_keywords = ["classify", "scan", "analyze", "check", "sync", "boot", "log"]
    is_infra = any(kw in title for kw in infra_keywords)
    answers["infrastructure_or_result"] = "infrastructure" if is_infra else "result"

    # Вопрос 2: Нужна ли инфраструктура прямо сейчас?
    if is_infra:
        # Проверяем есть ли что-то сломанное
        answers["infrastructure_needed_now"] = _check_if_something_broken()
    else:
        answers["infrastructure_needed_now"] = "N/A (result action)"

    # Вопрос 3: Максимальная польза для пользователя
    answers["max_user_value"] = _assess_user_value(action)

    # Вопрос 4: Важно или просто high score?
    score = action.get("score", 0)
    user_value = answers["max_user_value"]
    answers["score_vs_importance"] = "aligned" if (score > 0.5 and user_value > 0.5) else "misaligned"

    return answers


def self_ask_after_action(action: dict, result: dict) -> dict:
    """
    Точка 2: ПОСЛЕ действия, ДО записи success.
    """
    answers = {}

    # Вопрос 1: Проверил реальность?
    result_text = str(result.get("output", result.get("evidence", "")))
    checked_reality = (
        "subprocess" in result_text.lower() or
        "classified" in result_text.lower() or
        "created" in result_text.lower() or
        len(result_text) > 20
    )
    answers["checked_reality"] = checked_reality

    # Вопрос 2: Пользователь получит пользу?
    outcome = result.get("outcome", 0)
    if outcome >= 0.8:
        answers["user_gets_value"] = "yes"
    elif outcome > 0:
        answers["user_gets_value"] = "partial"
    else:
        answers["user_gets_value"] = "no"

    # Вопрос 3: Что проверил конкретно?
    answers["what_checked"] = result_text[:200] if result_text else "nothing"

    # Вопрос 4: Что НЕ проверил?
    answers["what_not_checked"] = _list_unchecked_items(action, result)

    return answers


def self_ask_before_showing(action: dict, result: dict) -> dict:
    """
    Точка 3: ПЕРЕД показом пользователю.
    """
    answers = {}

    # Вопрос 1: Правда или красивая упаковка?
    result_text = str(result.get("output", result.get("evidence", "")))
    is_honest = not any(word in result_text.lower() for word in [
        "acknowledged", "placeholder", "todo", "not implemented"
    ])
    answers["truth_or_packaging"] = "truth" if is_honest else "packaging"

    # Вопрос 2: Есть ли риски?
    answers["risks"] = _identify_risks(action, result)

    # Вопрос 3: Где не уверен?
    answers["uncertainties"] = _identify_uncertainties(action, result)

    # Вопрос 4: Что пользователь должен знать?
    answers["must_know"] = _identify_must_know(action, result)

    return answers


def self_ask_adjacent_areas(action: dict, result: dict) -> dict:
    """
    Точка 4: Какие смежные области затрагивает эта задача?
    
    Представь что пользователь уже сделал то что ты предлагаешь.
    Что происходит дальше? Какие вопросы у него возникают?
    """
    title = action.get("title", "").lower()
    adjacent = {}

    # Деньги → вывод → налоги → статус → риски
    if any(kw in title for kw in ["income", "money", "revenue", "affiliate", "travelpayouts", "booking"]):
        adjacent["financial"] = {
            "after_income": [
                "Как вывести деньги? (PayPal, банковский перевод)",
                "Какие налоги? (самозанятый, ИП, НДС)",
                "Нужна ли регистрация? (самозанятый через приложение)",
                "Какие риски? (блокировка аккаунта, штрафы)",
            ],
            "i_can_check": [
                "Регистрация самозанятого через Gosuslugi — 15 минут",
                "Лимиты самозанятого — 2.4 млн руб/год",
                "Налоговая ставка — 4% (или 6% для ИП)",
                "Travelpayouts выплаты — PayPal, bank transfer",
            ],
            "i_cannot_check": [
                "Будут ли реальные бронирования через бота",
                "Конверсию бота (нужен запуск)",
            ],
        }

    # Юридические аспекты
    if any(kw in title for kw in ["bot", "booking", "payment", "hotel"]):
        adjacent["legal"] = {
            "after_launch": [
                "Нужно ли ИП для бронирования?",
                "Нужен ли договор с отелем?",
                "Ответственность за бронирование (no-show, отмена)",
                "Защита персональных данных (152-ФЗ)",
            ],
            "i_can_check": [
                "Самозанятый может принимать оплату через ЮKassa",
                "Для бронирования нужен договор с отелем ( Agency Agreement )",
                "Ответственность — по договору, не по закону (если агент)",
                "152-ФЗ — нужна политика конфиденциальности",
            ],
        }

    # Масштабирование
    if any(kw in title for kw in ["deploy", "launch", "scale", "first client"]):
        adjacent["scaling"] = {
            "after_mvp": [
                "Как масштабировать на несколько отелей?",
                "Как автоматизировать добавление новых номеров?",
                "Как обрабатывать пиковый сезон (июнь-август)?",
                "Как интегрировать с другими OTAs (Booking, Ostrovok)?",
            ],
            "i_can_check": [
                "Multi-tenant архитектура — можно масштабировать через SQLite→PostgreSQL",
                "OTA интеграции — Travelpayouts API, Booking.com Affiliate API",
                "Пиковый сезон — горячие предложения через auto-poster",
            ],
        }

    return adjacent


# === Вспомогательные функции ===

def _check_if_something_broken() -> str:
    """Проверяет есть ли что-то сломанное что требует починки."""
    try:
        # Проверяем errors.log на свежие ошибки
        error_log = HERMES_HOME / "logs" / "errors.log"
        if error_log.exists():
            lines = error_log.read_text(encoding="utf-8", errors="replace").splitlines()
            recent = [l for l in lines[-20:] if "ERROR" in l]
            if len(recent) > 3:
                return "yes — %d recent errors need fixing" % len(recent)
        return "no — system appears healthy"
    except Exception:
        return "unknown — cannot check"


def _assess_user_value(action: dict) -> float:
    """Оценивает ценность действия для пользователя."""
    title = action.get("title", "").lower()
    # Direct user value
    if any(kw in title for kw in ["deploy", "income", "revenue", "client"]):
        return 0.9
    if any(kw in title for kw in ["salon", "bot", "posting", "content"]):
        return 0.7
    if any(kw in title for kw in ["research", "investigate", "analyze"]):
        return 0.5
    # Infrastructure
    if any(kw in title for kw in ["classify", "scan", "sync", "boot", "log"]):
        return 0.2
    return 0.3


def _list_unchecked_items(action: dict, result: dict) -> list:
    """Что НЕ было проверено."""
    unchecked = []
    result_text = str(result.get("output", result.get("evidence", "")))

    if "subprocess" in result_text:
        unchecked.append("stdout/stderr content not parsed")
    if "classified" in result_text:
        unchecked.append("classification accuracy not verified")
    if "success" in result_text.lower() and "test" not in result_text.lower():
        unchecked.append("end-to-end functionality not tested")

    return unchecked


def _identify_risks(action: dict, result: dict) -> list:
    """Определяет риски для пользователя."""
    risks = []
    title = action.get("title", "").lower()

    if "salon" in title and "deploy" in title:
        risks.append("Bot запущен без реального клиента — может показаться рабочим а но не приносит доход")
    if "auto-posting" in title:
        risks.append("Контент не проверен на качество — может навредить репутации каналов")
    if "money4band" in title:
        risks.append("Шарит IP-адрес с неизвестными компаниями — юридические риски")

    return risks


def _identify_uncertainties(action: dict, result: dict) -> list:
    """Где агент не уверен."""
    uncertainties = []
    title = action.get("title", "").lower()

    if "salon" in title:
        uncertainties.append("Не знаю сколько реальных клиентов готовы платить за такого бота")
    if "money4band" in title:
        uncertainties.append("Не знаю реальный доход — видел только claims на GitHub")
    if "workflow" in title:
        uncertainties.append("Не знаю применимы ли паттерны к текущей архитектуре")

    return uncertainties


def _identify_must_know(action: dict, result: dict) -> list:
    """Что пользователь должен знать."""
    must_know = []
    title = action.get("title", "").lower()

    if "salon" in title:
        must_know.append("Бот готов но не задеплоен — нужен токен для запуска")
    if "money4band" in title:
        must_know.append("Доход $10-30/мес claims с GitHub — не проверено independent")
    if any(kw in title for kw in ["classify", "scan"]):
        must_know.append("Это обслуживание инфраструктуры, не прямая польза пользователю")

    return must_know


# === Интеграция ===

def wrap_action_selection(action, context=None):
    """Обёртка для decision_engine — добавляет self-ask перед выбором."""
    answers = self_ask_before_action(action, context)

    # Если действие — обслуживание и нет необходимости — пропускаем
    if (answers["infrastructure_or_result"] == "infrastructure" and
        answers["infrastructure_needed_now"] == "no"):
        return None, answers  # Пропустить действие

    # Если score и importance не совпадают — снижаем score
    if answers["score_vs_importance"] == "misaligned":
        return action, {**answers, "penalty": "score adjusted down"}

    return action, answers


def wrap_action_result(action, result):
    """Обёртка для goal_executor — добавляет self-ask после действия."""
    answers = self_ask_after_action(action, result)

    # Если не проверили реальность — помечаем partial
    if not answers["checked_reality"]:
        result["outcome"] = min(result.get("outcome", 0.5), 0.3)
        result["evidence"] += " [UNCERTAIN: reality not verified]"

    # Если пользователь не получит пользу — помечаем
    if answers["user_gets_value"] == "no":
        result["outcome"] = -0.3
        result["evidence"] += " [WARNING: user gets no value]"

    return result, answers


def wrap_before_showing(action, result):
    """Обёртка для вывода пользователю — добавляет честность."""
    answers = self_ask_before_showing(action, result)

    warnings = []
    if answers["truth_or_packaging"] == "packaging":
        warnings.append("WARNING: This may be packaging, not truth")
    if answers["risks"]:
        warnings.append("RISKS: " + "; ".join(answers["risks"]))
    if answers["uncertainties"]:
        warnings.append("UNCERTAIN: " + "; ".join(answers["uncertainties"]))
    if answers["must_know"]:
        warnings.append("MUST KNOW: " + "; ".join(answers["must_know"]))

    return "\n".join(warnings) if warnings else None


if __name__ == "__main__":
    # Demo
    action = {"id": "test", "title": "Deploy salon-bot to first client", "score": 0.82}
    result = {"outcome": 0.5, "output": "Action executed: Deploy salon booking bot", "evidence": "Criteria not met"}

    print("=== SELF-ASK DEMO ===\n")

    print("BEFORE ACTION:")
    before = self_ask_before_action(action)
    for k, v in before.items():
        print("  %s: %s" % (k, v))

    print("\nAFTER ACTION:")
    after = self_ask_after_action(action, result)
    for k, v in after.items():
        print("  %s: %s" % (k, str(v)[:100]))

    print("\nBEFORE SHOWING:")
    showing = self_ask_before_showing(action, result)
    for k, v in showing.items():
        print("  %s: %s" % (k, str(v)[:100]))

    warnings = wrap_before_showing(action, result)
    if warnings:
        print("\nWARNINGS TO USER:")
        print(warnings)

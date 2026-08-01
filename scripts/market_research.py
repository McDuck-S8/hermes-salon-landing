#!/usr/bin/env python3
"""
market_research.py — Исследование ниш для AI/автоматизации с монетизацией.

Определяет перспективные ниши за пределами салонов красоты,
анализирует платёжные системы для России/CIS, модели монетизации.
Использует DuckDuckGo для поиска и opencode.ai/zen для анализа.
"""

import json
import os
import sys
import time
import datetime
import requests

# ─── Конфиг ───
API_URL = "https://opencode.ai/zen/v1/chat/completions"
API_MODEL = "mimo-v2.5-free"
API_TIMEOUT = 60
DELAY_BETWEEN_CALLS = 4  # секунды

CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "cache")
REPORT_PATH = os.path.join(CACHE_DIR, "market_research.json")

# ─── DuckDuckGo поиск ───
def ddg_search(query: str, max_results: int = 8) -> list[dict]:
    """Поиск через DuckDuckGo Instant Answer API."""
    url = "https://api.duckduckgo.com/"
    params = {"q": query, "format": "json", "no_html": 1, "skip_disambig": 1}
    try:
        r = requests.get(url, params=params, timeout=15)
        data = r.json()
        results = []
        # Абстрактный ответ
        if data.get("Abstract"):
            results.append({"title": "Abstract", "text": data["Abstract"], "url": data.get("AbstractURL", "")})
        # Релевантные темы
        for topic in data.get("RelatedTopics", [])[:max_results]:
            if isinstance(topic, dict) and "Text" in topic:
                results.append({"title": topic.get("Text", "")[:80], "text": topic.get("Text", ""), "url": topic.get("FirstURL", "")})
        return results
    except Exception as e:
        print(f"  [DDG] Ошибка: {e}")
        return []

# ─── LLM-анализ через opencode.ai/zen ───
def llm_analyze(prompt: str, system: str = "Ты — бизнес-аналитик. Отвечай кратко и по существу на русском.") -> str:
    """Вызов LLM для анализа ниши."""
    payload = {
        "model": API_MODEL,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3,
        "max_tokens": 1024
    }
    try:
        r = requests.post(API_URL, json=payload, timeout=API_TIMEOUT)
        data = r.json()
        msg = data.get("choices", [{}])[0].get("message", {})
        return msg.get("content") or msg.get("reasoning") or "Нет ответа"
    except Exception as e:
        print(f"  [LLM] Ошибка: {e}")
        return ""

# ─── Поисковые запросы ───
SEARCH_QUERIES = [
    # Ниши AI-автоматизации
    "AI автоматизация бизнеса ниши 2024 2025 доход",
    "Telegram бот монетизация ниши не красота",
    "AI как сервис бизнес модель доход",
    "автоматизация e-commerce AI бот продажи",
    "AI бот образование онлайн курсы автоматизация",
    "AI автоматизация недвижимость риэлтор бот",
    "AI медицина телемедицина чат-бот Россия",
    "AI логистика автоматизация склад",
    "AI юридические услуги автоматизация консультации",
    "AI HR рекрутинг автоматизация подбор персонала",
    # Платёжные системы
    "ЮKassa Robokassa платежная система Россия альтернатива Stripe",
    "крипто платежи Россия USDT оплата автоматизация",
    # Модели монетизации
    "SaaS модель монетизации цифровые продукты Россия",
]

# ─── Ниши для глубокого анализа ───
NICHES = [
    {
        "id": "ecommerce_ai",
        "name": "AI для e-commerce",
        "description": "Чат-боты для интернет-магазинов: рекомендации товаров, обработка заказов, поддержка клиентов, автоматические рассылки",
        "queries": ["e-commerce AI автоматизация бот продажи", "интернет магазин чатбот автоматизация"]
    },
    {
        "id": "education_ai",
        "name": "AI-образование и курсы",
        "description": "Телементоры, AI-репетиторы, автоматизация курсов, генерация контента для обучения",
        "queries": ["AI образование автоматизация курсы репетитор бот", "онлайн обучение AI"]
    },
    {
        "id": "realestate_ai",
        "name": "AI для недвижимости",
        "description": "Виртуальные агенты для риэлторов, подбор объектов, квалификация лидов, автоподбор недвижимости",
        "queries": ["AI риэлтор автоматизация недвижимость бот", "недвижимость чатбот подбор"]
    },
    {
        "id": "healthcare_ai",
        "name": "AI для медицины и здоровья",
        "description": "Телемедицина боты, запись к врачу, напоминания о лекарствах, первичная диагностика",
        "queries": ["AI медицина телемедицина чатбот Россия", "здоровье бот автоматизация"]
    },
    {
        "id": "logistics_ai",
        "name": "AI для логистики",
        "description": "Отслеживание доставки, оптимизация маршрутов, чат-боты для служб доставки",
        "queries": ["AI логистика автоматизация доставка отслеживание", "логистический бот"]
    },
    {
        "id": "legal_ai",
        "name": "AI-юрист / правовые консультации",
        "description": "Автоматические юридические консультации, составление документов, парсинг законов",
        "queries": ["AI юрист автоматизация консультации документы", "правовой чатбот"]
    },
    {
        "id": "hr_ai",
        "name": "AI для HR и рекрутинга",
        "description": "Автоматический скрининг резюме, чат-боты для собеседований, управление кадрами",
        "queries": ["AI HR рекрутинг подбор персонала автоматизация", "HR чатбот резюме"]
    },
    {
        "id": "saas_platform",
        "name": "SaaS-платформа для AI-ботов",
        "description": "No-code платформа для создания AI-ботов, white-label решения для бизнеса",
        "queries": ["SaaS платформа chatbot white label AI бизнес"]
    },
    {
        "id": "content_ai",
        "name": "AI-генерация контента",
        "description": "Создание текстов, изображений, видео, контента для соцсетей на автомате",
        "queries": ["AI генерация контента автоматизация контент-маркетинг"]
    },
    {
        "id": "finance_ai",
        "name": "AI для финансов и бухгалтерии",
        "description": "Автоматизация отчётов, парсинг данных, аналитика, чат-бот для вопросов по бухгалтерии",
        "queries": ["AI бухгалтерия автоматизация финансы отчёты"]
    },
    {
        "id": "agri_ai",
        "name": "AI для сельского хозяйства",
        "description": "Мониторинг полей, прогнозирование урожая, автоматизация ферм",
        "queries": ["AI агротехнологии сельское хозяйство автоматизация"]
    },
    {
        "id": "marketing_ai",
        "name": "AI-маркетинг и реклама",
        "description": "Автоматизация таргета, A/B тестирование, генерация рекламных креативов, аналитика кампаний",
        "queries": ["AI маркетинг автоматизация таргетированная реклама"]
    },
]

PAYMENT_SYSTEMS = [
    {
        "id": "yukassa",
        "name": "ЮKassa (бывш. Яндекс.Касса)",
        "description": "Основной платёжный агрегатор в РФ, приём карт, SBP, электронных денег"
    },
    {
        "id": "robokassa",
        "name": "Robokassa",
        "description": "Платёжный агрегатор с поддержкой множества способов оплаты, крипто"
    },
    {
        "id": "stripe_ru",
        "name": "Stripe (ограниченно)",
        "description": "Доступен через зарубежные юрлица, не для прямых выплат в РФ"
    },
    {
        "id": "cloudpayments",
        "name": "CloudPayments",
        "description": "Платёжный сервис с подписками и рекуррентными платежами"
    },
    {
        "id": "crypto",
        "name": "Крипто (USDT/TRC20, BTC)",
        "description": "Приём криптовалют через P2P или виджеты, обход санкций"
    },
    {
        "id": "freekassa",
        "name": "FreeKassa",
        "description": "Простой платёжный сервис для цифровых товаров"
    },
    {
        "id": "tranzor",
        "name": "Транзак / ТБанк эквайринг",
        "description": "Эквайринг для ИП и ООО, интеграция с Telegram"
    },
    {
        "id": "sberbank",
        "name": "СберПэй / Сбербанк",
        "description": "Эквайринг и СБП, интеграция через API"
    },
]

MONETIZATION_MODELS = [
    {"id": "subscription", "name": "Подписка (SaaS)", "description": "Ежемесячная/годовая оплата за доступ к AI-сервису"},
    {"id": "per_use", "name": "Pay-per-use", "description": "Оплата за каждое использование API/бота"},
    {"id": "freemium", "name": "Freemium", "description": "Базовый функционал бесплатно, премиум — платно"},
    {"id": "white_label", "name": "White Label", "description": "Продажа готового решения под брендом клиента"},
    {"id": "licensing", "name": "Лицензирование", "description": "Продажа лицензий на AI-модели/боты"},
    {"id": "commission", "name": "Комиссия", "description": "Процент от транзакций, проведённых через сервис"},
    {"id": "consulting", "name": "Консалтинг", "description": "Настройка AI-решений под ключ + обучение"},
    {"id": "marketplace", "name": "Маркетплейс", "description": "Платформа-маркетплейс AI-шаблонов и интеграций"},
]


def main():
    print("=" * 70)
    print("  ИССЛЕДОВАНИЕ РЫНКА: AI-НИШИ ДЛЯ АВТОМАТИЗАЦИИ")
    print("  (множественные ниши, не только салоны красоты)")
    print("=" * 70)

    # Шаг 1: Веб-поиск
    print("\n[1/4] Поиск ниш и тенденций через DuckDuckGo...")
    search_results = {}
    for q in SEARCH_QUERIES:
        print(f"  → {q}")
        results = ddg_search(q)
        search_results[q] = results
        if results:
            print(f"    Найдено: {len(results)} результатов")
        else:
            print(f"    (нет результатов)")
        time.sleep(1)

    # Шаг 2: LLM-анализ ниш
    print(f"\n[2/4] LLM-анализ {len(NICHES)} ниш...")
    niche_analyses = []
    for i, niche in enumerate(NICHES):
        print(f"  [{i+1}/{len(NICHES)}] Анализ: {niche['name']}...")
        prompt = (
            f"Проанализируй нишу: {niche['name']}\n"
            f"Описание: {niche['description']}\n\n"
            f"Оцени по шкале 1-10:\n"
            f"1) Размер рынка (market_size): потенциал дохода\n"
            f"2) Уровень конкуренции (competition): 1=мало, 10=очень много\n"
            f"3) Барьер входа (entry_barrier): 1=низкий, 10=высокий\n"
            f"4) Пригодность AI (ai_fit): насколько AI решает задачу\n"
            f"5) Рекомендуемая модель монетизации (revenue_model)\n"
            f"6) Ожидаемый диапазон дохода в месяц (revenue_range)\n"
            f"7) Срок выхода на рынок (time_to_market)\n\n"
            f"Ответ строго в JSON: {{\"market_size\": N, \"competition\": N, "
            f"\"entry_barrier\": N, \"ai_fit\": N, \"revenue_model\": \"...\", "
            f"\"revenue_range\": \"...\", \"time_to_market\": \"...\", "
            f"\"summary\": \"...\"}}"
        )
        result = llm_analyze(prompt)
        print(f"    Ответ получен ({len(result)} символов)")

        # Парсинг JSON из ответа
        parsed = {"raw": result}
        try:
            # Попытка извлечь JSON
            start = result.find("{")
            end = result.rfind("}") + 1
            if start >= 0 and end > start:
                parsed = json.loads(result[start:end])
        except Exception:
            pass

        parsed["niche_id"] = niche["id"]
        parsed["niche_name"] = niche["name"]
        parsed["niche_description"] = niche["description"]
        niche_analyses.append(parsed)
        time.sleep(DELAY_BETWEEN_CALLS)

    # Шаг 3: Анализ платёжных систем
    print(f"\n[3/4] Анализ платёжных систем для России/CIS...")
    payment_analysis = []
    prompt_payments = (
        "Проанализируй платёжные системы для бизнеса в России/CIS:\n"
        "- ЮKassa, Robokassa, CloudPayments, FreeKassa\n"
        "- Криптовалюта (USDT, BTC)\n"
        "- СБП, СберПэй\n\n"
        "Для каждой оцени: комиссия (%), скорость интеграции, "
        "поддержка подписок, пригодность для AI-ботов.\n"
        "Ответ в JSON: {\"systems\": [{\"name\": \"...\", \"fee\": \"...\", "
        "\"integration_speed\": \"...\", \"subscription_support\": bool, "
        "\"ai_bot_fit\": \"...\"}], \"best_for_bots\": \"...\", "
        "\"crypto_note\": \"...\"}"
    )
    result_payments = llm_analyze(prompt_payments)
    payments_parsed = {"raw": result_payments}
    try:
        start = result_payments.find("{")
        end = result_payments.rfind("}") + 1
        if start >= 0 and end > start:
            payments_parsed = json.loads(result_payments[start:end])
    except Exception:
        pass
    payment_analysis.append(payments_parsed)
    print(f"  Анализ платёжных систем: {len(result_payments)} символов")

    # Шаг 4: Общий анализ и ранжирование
    print(f"\n[4/4] Финальное ранжирование ниш...")
    time.sleep(DELAY_BETWEEN_CALLS)

    ranking_prompt = (
        "Ранжируй ниши по潜在ному доходу и перспективности для индивидуального "
        "разработчика AI-ботов в России. Учитывай:\n"
    )
    for na in niche_analyses:
        name = na.get("niche_name", na.get("niche_id", "?"))
        summary = na.get("summary", na.get("raw", ""))[:200]
        ranking_prompt += f"- {name}: {summary}\n"

    ranking_prompt += (
        "\nОтвет в JSON: {\"rankings\": [{\"rank\": 1, \"niche\": \"...\", "
        "\"reason\": \"...\", \"score\": N}], \"top3_recommendation\": \"...\"}"
    )
    result_ranking = llm_analyze(ranking_prompt)
    ranking_parsed = {"raw": result_ranking}
    try:
        start = result_ranking.find("{")
        end = result_ranking.rfind("}") + 1
        if start >= 0 and end > start:
            ranking_parsed = json.loads(result_ranking[start:end])
    except Exception:
        pass
    print(f"  Ранжирование: готово")

    # ─── Формирование отчёта ───
    report = {
        "generated_at": datetime.datetime.now().isoformat(),
        "niches": niche_analyses,
        "rankings": ranking_parsed,
        "payment_systems": payment_analysis + PAYMENT_SYSTEMS,
        "monetization_models": MONETIZATION_MODELS,
        "search_results_summary": {k: len(v) for k, v in search_results.items()},
    }

    # Сохранение
    os.makedirs(CACHE_DIR, exist_ok=True)
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"\n✅ Отчёт сохранён: {REPORT_PATH}")

    # ─── Печать отчёта на русском ───
    print("\n" + "=" * 70)
    print("  ОТЧЁТ: ИССЛЕДОВАНИЕ AI-НИШ ДЛЯ МОНЕТИЗАЦИИ")
    print("  " + "=" * 66)
    print(f"  Дата: {report['generated_at']}")
    print()

    # Ранжирование
    print("  ╔══════════════════════════════════════════════════════════╗")
    print("  ║              РАНЖИРОВАНИЕ НИШ ПО ПЕРСПЕКТИВНОСТИ       ║")
    print("  ╚══════════════════════════════════════════════════════════╝")
    rankings = ranking_parsed.get("rankings", [])
    if rankings:
        for r in rankings:
            rank = r.get("rank", "?")
            niche = r.get("niche", "?")
            reason = r.get("reason", "")
            score = r.get("score", "?")
            print(f"\n  #{rank} {niche}  (оценка: {score}/10)")
            print(f"     {reason}")
    else:
        # Если ранжирование не в JSON, выводим raw
        print(f"  {ranking_parsed.get('raw', 'Нет данных')[:500]}")

    top3 = ranking_parsed.get("top3_recommendation", "")
    if top3:
        print(f"\n  ★ Топ-3 рекомендация: {top3}")

    # Ниши
    print("\n  ╔══════════════════════════════════════════════════════════╗")
    print("  ║                    ДЕТАЛЬНЫЙ АНАЛИЗ НИШ                ║")
    print("  ╚══════════════════════════════════════════════════════════╝")
    for na in niche_analyses:
        name = na.get("niche_name", "?")
        desc = na.get("niche_description", "")[:100]
        ms = na.get("market_size", "?")
        comp = na.get("competition", "?")
        eb = na.get("entry_barrier", "?")
        af = na.get("ai_fit", "?")
        rev = na.get("revenue_model", "?")
        rev_range = na.get("revenue_range", "?")
        ttm = na.get("time_to_market", "?")
        summary = na.get("summary", "")[:150]
        print(f"\n  ─── {name} ───")
        print(f"  {desc}")
        print(f"  Размер рынка: {ms}/10 | Конкуренция: {comp}/10 | "
              f"Барьер входа: {eb}/10 | AI-подходит: {af}/10")
        print(f"  Модель монетизации: {rev}")
        print(f"  Доход: {rev_range} | Выход на рынок: {ttm}")
        if summary:
            print(f"  Кратко: {summary}")

    # Платёжные системы
    print("\n  ╔══════════════════════════════════════════════════════════╗")
    print("  ║          ПЛАТЁЖНЫЕ СИСТЕМЫ ДЛЯ РОССИИ/CIS             ║")
    print("  ╚══════════════════════════════════════════════════════════╝")
    for ps in PAYMENT_SYSTEMS:
        print(f"\n  • {ps['name']}")
        print(f"    {ps['description']}")

    # Модели монетизации
    print("\n  ╔══════════════════════════════════════════════════════════╗")
    print("  ║              МОДЕЛИ МОНЕТИЗАЦИИ                        ║")
    print("  ╚══════════════════════════════════════════════════════════╝")
    for mm in MONETIZATION_MODELS:
        print(f"  • {mm['name']}: {mm['description']}")

    print("\n" + "=" * 70)
    print("  ИССЛЕДОВАНИЕ ЗАВЕРШЕНО")
    print("  Отчёт: " + REPORT_PATH)
    print("=" * 70)


if __name__ == "__main__":
    main()

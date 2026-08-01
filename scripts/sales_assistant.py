#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
sales_assistant.py — Автономный sales-ассистент.

Возможности:
  1. Классификация интента клиентского сообщения (keyword heuristics):
       sale / question / objection / complaint
  2. Генерация ответа из шаблонов, персонализированных по интенту,
     на русском языке, в деловом стиле.
  3. Логирование каждого обработанного диалога в knowledge_cube.db
     (таблица experiences):
       content  — всегда заполняется (NOT NULL),
       raw_text — исходное сообщение клиента,
       hash     = md5(content + ts)[:16] (UNIQUE),
       source   = 'sales_assistant',
       axis_domain  = 'sales',
       axis_outcome = 'success'.
  4. --demo — имитация 2 диалогов с клиентами (возражение о цене
     и вопрос об услугах) с печатью интента, ответа и статуса записи в БД.

Запуск:
    python scripts/sales_assistant.py --demo
    python scripts/sales_assistant.py --message "Сколько стоит ваша услуга?"
    echo "Это слишком дорого" | python scripts/sales_assistant.py
"""

import argparse
import hashlib
import json
import random
import re
import sqlite3
import sys
from datetime import datetime

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except AttributeError:  # Python < 3.7
    pass

DB_PATH = "D:/Portable_Soft/hermes/cache/knowledge_cube.db"

INTENT_ORDER = ["complaint", "objection", "sale", "question"]

# --- Keyword heuristics -------------------------------------------------------
KEYWORDS = {
    "complaint": [
        "жалоб", "не работает", "не пришл", "не доставил", "верните деньги",
        "возврат", "обман", "кидалов", "ужасн", "отвратительн", "брак",
        "сломал", "некачествен", "не получил", "задержк", "опоздал",
        "плохо", "недовол", "испорчен", "не соответствует", "претензи",
    ],
    "objection": [
        "дорого", "дороговато", "не по карману", "завышен", "у конкурентов дешевле",
        "подумаю", "не сейчас", "потом", "скидку", "скидка", "дешевле",
        "не готов платить", "переплачивать", "не могу позволить", "цена не устроила",
        "слишком дорого", "дорогой", "не вписывается в бюджет",
    ],
    "sale": [
        "хочу купить", "купить", "заказать", "оформить", "приобрести",
        "сколько стоит", "цена", "стоимость", "как оплатить", "сделать заказ",
        "забронировать", "готов купить", "хочу заказать", "заказ", "купить сейчас",
    ],
    "question": [
        "вопрос", "расскажите", "подскажите", "что входит", "какие услуги",
        "как работает", "как проходит", "есть ли", "можно ли", "когда",
        "где", "чем отличает", "подробнее", "уточнить", "интересует",
        "какие сроки", "что нужно для", "как это работает",
    ],
}

# --- Reply templates (business style, Russian) --------------------------------
TEMPLATES = {
    "sale": [
        "Благодарим за интерес к нашей продукции! Для оформления заказа "
        "направьте, пожалуйста, контактные данные и удобное время для звонка — "
        "менеджер свяжется с вами в течение 15 минут.",
        "Рады вашему решению о покупке. Для подтверждения заказа просим "
        "указать удобный способ связи — мы оперативно направим счёт и детали "
        "оплаты и доставки.",
        "Отлично, что вы выбрали наше предложение. Для завершения оформления "
        "подтвердите, пожалуйста, заказ, — мы закрепим за вами лучшие условия.",
    ],
    "question": [
        "Благодарим за обращение! Отвечая на ваш вопрос: в стоимость входят "
        "консультация, выполнение работ и гарантийное сопровождение. "
        "Готовы предоставить подробную презентацию и ответить на уточняющие "
        "вопросы в удобное для вас время.",
        "Спасибо за ваш запрос. Наши специалисты подготовили развёрнутый ответ "
        "и свяжутся с вами в ближайшее время, чтобы обсудить детали и сроки.",
        "Благодарим за интерес к нашим услугам. Мы направили подробную "
        "информацию о составе и стоимости услуг, а также будем рады ответить "
        "на дополнительные вопросы по телефону или в чате.",
    ],
    "objection": [
        "Понимаем ваше сомнение и ценим открытость. Готовы предложить "
        "индивидуальные условия и подробно обосновать стоимость: в неё входят "
        "качество, гарантия и сопровождение. Позвольте нашему менеджеру "
        "связаться с вами и обсудить взаимовыгодный вариант.",
        "Спасибо, что поделились своим мнением. Мы готовы рассмотреть "
        "персональные условия для вас и показать, чем наше предложение "
        "выгоднее. Менеджер свяжется с вами в течение часа, чтобы всё обсудить.",
        "Ценим вашу обратную связь. Предлагаем обсудить детали: мы уверены, "
        "что сможем найти решение, комфортное для вашего бюджета, без потери "
        "качества. Удобно ли вам, если мы позвоним в ближайшее время?",
    ],
    "complaint": [
        "Приносим искренние извинения за доставленные неудобства. Для нас "
        "важно каждое обращение: мы незамедлительно разберём ситуацию и "
        "предложим решение. Пожалуйста, укажите номер заказа или детали — "
        "специалист свяжется с вами в течение 15 минут.",
        "Сожалеем, что столкнулись с проблемой. Мы уже взяли ваше обращение "
        "в работу и оперативно проверим все обстоятельства. Приложим все "
        "усилия, чтобы исправить ситуацию в кратчайшие сроки.",
        "Примите наши извинения. Ваше обращение передано ответственному "
        "сотруднику — в ближайшее время с вами свяжутся и предложат "
        "компенсацию или решение вопроса в соответствии с условиями.",
    ],
}

SIGNATURE = "С уважением, отдел продаж"

NAME_RE = re.compile(
    r"(?:меня зовут|звать)\s+([А-ЯЁ][а-яё]+)|"
    r"(?:я\s+)([А-ЯЁ][а-яё]+)(?:,|\.|\s|$)",
    re.IGNORECASE,
)

INTENT_LABELS_RU = {
    "sale": "продажа",
    "question": "вопрос",
    "objection": "возражение",
    "complaint": "жалоба",
}


def classify_intent(text: str) -> str:
    """Классификация интента сообщения по ключевым словам (эвристики)."""
    lowered = text.lower()
    scores = {intent: 0 for intent in INTENT_ORDER}
    for intent, words in KEYWORDS.items():
        for w in words:
            if w in lowered:
                scores[intent] += 1
    best = max(scores, key=lambda i: (scores[i], -INTENT_ORDER.index(i)))
    return best


def detect_client_name(text: str):
    """Извлечение имени клиента для персонализации (если назвался)."""
    m = NAME_RE.search(text)
    if m:
        return m.group(1) or m.group(2)
    return None


def generate_reply(intent: str, client_text: str, client_name=None) -> str:
    """Генерация ответа из шаблонов, персонализированного по интенту."""
    template = random.choice(TEMPLATES[intent])
    greeting = ""
    if client_name:
        greeting = f"Уважаемый(ая) {client_name},\n\n"
    return f"{greeting}{template}\n\n{SIGNATURE}"


def log_experience(intent: str, client_text: str, reply: str) -> dict:
    """
    Запись диалога в knowledge_cube.db (таблица experiences).

    content всегда заполняется (NOT NULL), hash = md5(content+ts)[:16].
    При коллизии уникального hash (одинаковые ts) — повтор с новым ts.
    """
    result = {"status": "FAILED", "hash": None, "row_id": None, "error": None}
    try:
        conn = sqlite3.connect(DB_PATH, timeout=10)
        conn.execute("PRAGMA busy_timeout = 5000")
        cur = conn.cursor()
        last_err = None
        for _ in range(3):
            ts = datetime.now().isoformat(timespec="seconds")
            content = (
                f"[sales_assistant] intent={intent} | client: {client_text} "
                f"| reply: {reply}"
            )
            digest = hashlib.md5((content + ts).encode("utf-8")).hexdigest()[:16]
            try:
                cur.execute(
                    """
                    INSERT INTO experiences
                        (ts, content, raw_text, hash, axis_domain, axis_outcome,
                         source, tags, is_white_spot)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        ts,
                        content,
                        client_text,
                        digest,
                        "sales",
                        "success",
                        "sales_assistant",
                        json.dumps([f"intent:{intent}"], ensure_ascii=False),
                        0,
                    ),
                )
                conn.commit()
                result.update(status="OK", hash=digest, row_id=cur.lastrowid)
                break
            except sqlite3.IntegrityError as e:  # hash UNIQUE collision -> new ts
                last_err = str(e)
                conn.rollback()
        else:
            result["error"] = f"hash collision: {last_err}"
        conn.close()
    except Exception as e:  # noqa: BLE001 — статус пишем в вывод, не роняем скрипт
        result["error"] = str(e)
    return result


def process_message(client_text: str) -> dict:
    """Полный цикл: интент -> ответ -> запись в БД."""
    client_text = client_text.strip()
    intent = classify_intent(client_text)
    name = detect_client_name(client_text)
    reply = generate_reply(intent, client_text, name)
    log = log_experience(intent, client_text, reply)
    return {
        "client_text": client_text,
        "intent": intent,
        "intent_ru": INTENT_LABELS_RU[intent],
        "client_name": name,
        "reply": reply,
        "db": log,
    }


def run_demo() -> None:
    """--demo: имитация 2 диалогов с клиентами."""
    random.seed(42)  # детерминированный вывод демо
    dialogs = [
        "Здравствуйте! Это слишком дорого, у конкурентов дешевле. "
        "Может, дадите скидку?",
        "Добрый день! Подскажите, пожалуйста, какие у вас услуги и что "
        "входит в стоимость? Меня зовут Иван.",
    ]
    print("=" * 72)
    print("SALES ASSISTANT — ДЕМО (2 диалога с клиентами)")
    print("=" * 72)
    for i, text in enumerate(dialogs, start=1):
        res = process_message(text)
        print(f"\n--- Диалог {i} ---")
        print(f"Клиент: {res['client_text']}")
        print(f"Интент: {res['intent']} ({res['intent_ru']})"
              + (f", имя клиента: {res['client_name']}" if res["client_name"] else ""))
        print(f"Ответ:\n{res['reply']}")
        db = res["db"]
        if db["status"] == "OK":
            print(f"Запись в БД: OK (id={db['row_id']}, hash={db['hash']})")
        else:
            print(f"Запись в БД: FAILED ({db['error']})")
    print("\n" + "=" * 72)
    print("Демо завершено.")
    print("=" * 72)


def main() -> int:
    parser = argparse.ArgumentParser(description="Sales assistant (intent -> reply -> KC log)")
    parser.add_argument("--demo", action="store_true", help="имитация 2 диалогов с клиентами")
    parser.add_argument("--message", "-m", help="обработать одно сообщение клиента")
    args = parser.parse_args()

    if args.demo:
        run_demo()
        return 0

    if args.message:
        res = process_message(args.message)
        print(f"Интент: {res['intent']} ({res['intent_ru']})")
        print(f"Ответ:\n{res['reply']}")
        db = res["db"]
        if db["status"] == "OK":
            print(f"Запись в БД: OK (id={db['row_id']}, hash={db['hash']})")
        else:
            print(f"Запись в БД: FAILED ({db['error']})")
        return 0

    # Интерактивный режим: строки из stdin
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        res = process_message(line)
        print(f"Интент: {res['intent']} ({res['intent_ru']})")
        print(f"Ответ:\n{res['reply']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

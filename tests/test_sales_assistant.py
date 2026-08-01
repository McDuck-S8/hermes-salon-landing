"""Tests for scripts/sales_assistant.py — hermetic (temp DB, no real KC writes)."""

import hashlib
import sqlite3
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import sales_assistant as sa  # noqa: E402


@pytest.fixture
def tmp_db(monkeypatch, tmp_path):
    db = tmp_path / "kc_test.db"
    conn = sqlite3.connect(db)
    conn.execute(
        """
        CREATE TABLE experiences (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts TEXT NOT NULL, content TEXT NOT NULL, raw_text TEXT NOT NULL,
            hash TEXT UNIQUE NOT NULL,
            axis_time_hour INTEGER, axis_time_dow INTEGER,
            axis_domain TEXT, axis_outcome TEXT,
            dynamic_axes TEXT DEFAULT '{}',
            is_white_spot INTEGER DEFAULT 0, white_spot_cluster_id TEXT,
            source TEXT, confidence REAL DEFAULT 1.0, tags TEXT DEFAULT '[]',
            importance REAL DEFAULT 0.5, expiration_date TEXT,
            verification_method TEXT DEFAULT 'manual'
        )
        """
    )
    conn.commit()
    conn.close()
    monkeypatch.setattr(sa, "DB_PATH", str(db))
    return str(db)


# --- intent classification ----------------------------------------------------

@pytest.mark.parametrize(
    "text,expected",
    [
        ("Хочу купить ваш тариф, сколько стоит?", "sale"),
        ("Подскажите, какие у вас услуги?", "question"),
        ("Это слишком дорого, дайте скидку", "objection"),
        ("Заказ не пришёл, верните деньги!", "complaint"),
        ("Менеджер обманул, товар бракованный, ужасно", "complaint"),
        ("Расскажите, что входит в стоимость", "question"),
        ("Готов оформить заказ прямо сейчас", "sale"),
        ("У конкурентов дешевле, подумаю", "objection"),
    ],
)
def test_classify_intent(text, expected):
    assert sa.classify_intent(text) == expected


def test_objection_beats_question_on_price_message():
    # "почему так дорого" — objection, а не question
    assert sa.classify_intent("Почему у вас так дорого?") == "objection"


# --- name detection & replies -------------------------------------------------

def test_detect_client_name():
    assert sa.detect_client_name("Меня зовут Иван, что входит в стоимость?") == "Иван"
    assert sa.detect_client_name("Здравствуйте, я Мария. Сколько стоит?") == "Мария"
    assert sa.detect_client_name("Просто вопрос по услугам") is None


def test_generate_reply_shape():
    reply = sa.generate_reply("question", "текст", None)
    assert "С уважением, отдел продаж" in reply
    assert reply.strip().startswith("Благодарим")


def test_generate_reply_personalized():
    reply = sa.generate_reply("sale", "Меня зовут Пётр", "Пётр")
    assert "Уважаемый(ая) Пётр" in reply


# --- DB logging ---------------------------------------------------------------

def _read_row(db):
    conn = sqlite3.connect(db)
    row = conn.execute(
        "SELECT ts, content, raw_text, hash, axis_domain, axis_outcome, source "
        "FROM experiences ORDER BY id DESC LIMIT 1"
    ).fetchone()
    conn.close()
    return row


def test_log_experience_writes_row(tmp_db):
    res = sa.log_experience("objection", "Слишком дорого", "Ответ менеджера")
    assert res["status"] == "OK"
    assert res["hash"] and len(res["hash"]) == 16

    ts, content, raw_text, digest, domain, outcome, source = _read_row(tmp_db)
    assert content and raw_text  # NOT NULL columns always filled
    assert raw_text == "Слишком дорого"
    assert domain == "sales" and outcome == "success" and source == "sales_assistant"
    assert digest == hashlib.md5((content + ts).encode("utf-8")).hexdigest()[:16]


def test_log_experience_twice_different_hashes(tmp_db):
    r1 = sa.log_experience("sale", "Хочу купить", "Ответ 1")
    r2 = sa.log_experience("question", "Что входит?", "Ответ 2")
    assert r1["status"] == "OK" and r2["status"] == "OK"
    assert r1["hash"] != r2["hash"]  # UNIQUE hash не коллизирует


def test_process_message_end_to_end(tmp_db):
    res = sa.process_message("Здравствуйте! Это слишком дорого, у конкурентов дешевле")
    assert res["intent"] == "objection"
    assert res["reply"]
    assert res["db"]["status"] == "OK"

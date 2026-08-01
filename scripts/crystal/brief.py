"""
Crystal Brief — второй мозг Hermes.

Что делает:

# Revisit: when brief extraction keywords, summary format, or output style changes. Last touched: 2026-07-02.
  1. Читает последние сессии из state.db
  2. Находит что повторяется, что бесит, что не решено
  3. Выдаёт КОРОТКУЮ выжимку для Hermes

Запуск: python -m crystal.brief
Из Hermes: from crystal.brief import crystal_brief
"""

import sqlite3
import os
import json
import sys
from collections import Counter
from datetime import datetime, timedelta


# ── Конфигурация ──────────────────────────────────────────────

HERMES_HOME = os.environ.get("HERMES_HOME", os.path.expanduser("~/.hermes"))
STATE_DB = os.path.join(HERMES_HOME, "state.db")


# ── Ключевые слова ───────────────────────────────────────────

FRUSTRATION = [
    "блин", "чёрт", "ужас", "кошмар", "ненавижу", "задолбал",
    "хуже", "глючит", "сломал", "не работает", "тормозит",
    "хватит", "стоп", "прекрати", "не надо", "достало",
    "damn", "hate", "broken", "sucks", "again", "why",
    "тупик", "бессмысленно", "зря", "одно и то же",
]

CORRECTION = [
    "не так", "неправильно", "ошибка", "исправь", "поправь", "не то",
    "другой", "измени", "перепиши", "не этот", "не так",
    "wrong", "fix", "change", "redo", "not correct", "instead",
]

UNFINISHED = [
    "надо будет", "нужно сделать", "потом", "когда-нибудь",
    "не доделал", "осталось", "незакончено",
    "todo", "todo", "need to", "should do", "later",
]

POSITIVE = [
    "готово", "сделано", "получилось", "работает", "отлично",
    "супер", "класс", "именно так", "вот это", "то что надо",
    "done", "works", "great", "perfect", "exactly",
]


# ── Чтение данных ────────────────────────────────────────────

def _read_sessions(days=7, limit=50):
    """Прочитать последние сессии из state.db"""
    if not os.path.exists(STATE_DB):
        return []

    conn = sqlite3.connect(STATE_DB)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # timestamps в state.db — unix epoch float
    since_epoch = (datetime.now() - timedelta(days=days)).timestamp()
    cur.execute("""
        SELECT id, title, source, model, started_at, message_count
        FROM sessions
        WHERE started_at > ?
        ORDER BY started_at DESC
        LIMIT ?
    """, (since_epoch, limit))
    sessions = cur.fetchall()

    result = []
    for s in sessions:
        # Берём user-сообщения
        cur.execute("""
            SELECT content, timestamp
            FROM messages
            WHERE session_id = ? AND role = 'user'
            ORDER BY timestamp
        """, (s["id"],))
        msgs = cur.fetchall()

        # started_at — unix epoch float
        started_str = ""
        if s["started_at"]:
            try:
                started_str = datetime.fromtimestamp(s["started_at"]).strftime("%Y-%m-%d %H:%M")
            except (ValueError, OSError):
                started_str = str(s["started_at"])

        result.append({
            "id": s["id"],
            "title": s["title"] or "(без названия)",
            "source": s["source"] or "",
            "model": s["model"] or "",
            "started": started_str,
            "message_count": s["message_count"] or 0,
            "user_messages": [m["content"] or "" for m in msgs],
        })

    conn.close()
    return result


# ── Анализ ────────────────────────────────────────────────────

def _find_patterns(sessions):
    """Найти повторяющиеся паттерны в сообщениях пользователя"""
    all_text = []
    frustration_hits = []
    correction_hits = []
    unfinished_hits = []
    positive_hits = []

    for s in sessions:
        for msg in s["user_messages"]:
            if len(msg) < 5:
                continue
            all_text.append(msg.lower())
            words = msg.lower()

            for kw in FRUSTRATION:
                if kw in words:
                    frustration_hits.append(msg[:120])
                    break

            for kw in CORRECTION:
                if kw in words:
                    correction_hits.append(msg[:120])
                    break

            for kw in UNFINISHED:
                if kw in words:
                    unfinished_hits.append(msg[:120])
                    break

            for kw in POSITIVE:
                if kw in words:
                    positive_hits.append(msg[:120])
                    break

    # Частые слова (исключая стоп-слова)
    stop = {"и", "в", "на", "не", "что", "как", "это", "я", "ты", "мы",
            "а", "но", "да", "нет", "вот", "уже", "ещё", "еще", "все",
            "она", "они", "оно", "его", "её", "их", "мне", "мой", "моя",
            "the", "a", "an", "is", "are", "was", "were", "to", "of",
            "and", "or", "but", "in", "on", "at", "for", "with", "i",
            "you", "we", "it", "this", "that", "my", "your", "do", "be"}

    word_counter = Counter()
    for text in all_text:
        for w in text.split():
            w = w.strip(".,!?;:\"'()[]{}")
            if len(w) > 3 and w not in stop:
                word_counter[w] += 1

    return {
        "frustration": frustration_hits[:5],
        "corrections": correction_hits[:5],
        "unfinished": unfinished_hits[:5],
        "positive": positive_hits[:3],
        "top_words": word_counter.most_common(15),
        "total_messages": sum(len(s["user_messages"]) for s in sessions),
        "total_sessions": len(sessions),
    }


def _summarize_sessions(sessions):
    """Краткая сводка по сессиям"""
    summaries = []
    for s in sessions[:10]:
        msg_count = len(s["user_messages"])
        # Берём первое сообщение как контекст
        first_msg = s["user_messages"][0][:100] if s["user_messages"] else ""
        summaries.append({
            "title": s["title"],
            "source": s["source"],
            "started": s["started"][:16] if s["started"] else "",
            "msgs": msg_count,
            "preview": first_msg,
        })
    return summaries


# ── Главная функция ───────────────────────────────────────────

def crystal_brief(days=7, verbose=False):
    """
    Дать мне короткую выжимку: что происходит, что повторяется, что бесит.
    
    Возвращает dict с ключами:
      - sessions: краткие сводки
      - patterns: найденные паттерны
      - summary: текстовая выжимка
    """
    sessions = _read_sessions(days=days)
    if not sessions:
        return {
            "sessions": [],
            "patterns": {},
            "summary": f"Нет данных за последние {days} дней.",
        }

    patterns = _find_patterns(sessions)
    session_summaries = _summarize_sessions(sessions)

    # Формируем текстовую выжимку
    lines = []
    lines.append(f"📊 За {days}д: {patterns['total_sessions']} сессий, {patterns['total_messages']} сообщений")

    if patterns["frustration"]:
        lines.append(f"\n🔴 Фрустрация ({len(patterns['frustration'])} хитов):")
        for h in patterns["frustration"][:3]:
            lines.append(f"  • {h}")

    if patterns["corrections"]:
        lines.append(f"\n🟡 Коррекции ({len(patterns['corrections'])} хитов):")
        for h in patterns["corrections"][:3]:
            lines.append(f"  • {h}")

    if patterns["unfinished"]:
        lines.append(f"\n🟠 Незавершённое ({len(patterns['unfinished'])} хитов):")
        for h in patterns["unfinished"][:3]:
            lines.append(f"  • {h}")

    if patterns["positive"]:
        lines.append(f"\n🟢 Позитив ({len(patterns['positive'])} хитов):")
        for h in patterns["positive"][:3]:
            lines.append(f"  • {h}")

    if patterns["top_words"]:
        words = ", ".join(f"{w}({c})" for w, c in patterns["top_words"][:10])
        lines.append(f"\n🔑 Частые слова: {words}")

    if verbose:
        lines.append(f"\n📋 Сессии:")
        for s in session_summaries[:5]:
            lines.append(f"  [{s['source']}] {s['title']} ({s['msgs']}мсг) — {s['preview'][:60]}")

    summary_text = "\n".join(lines)

    return {
        "sessions": session_summaries,
        "patterns": patterns,
        "summary": summary_text,
    }


# ── CLI ───────────────────────────────────────────────────────

if __name__ == "__main__":
    days = int(sys.argv[1]) if len(sys.argv) > 1 else 7
    verbose = "-v" in sys.argv

    result = crystal_brief(days=days, verbose=verbose)
    print(result["summary"])

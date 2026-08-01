"""
Crystal v3 — Модуль 1: Session Reader
Читает сессии из state.db, извлекает сигналы
"""

# Revisit: when session reading logic, signal classification, or CORRECTION/FRUSTRATION keywords change. Last touched: 2026-07-02.

import sqlite3
import os
import re
from datetime import datetime
from .models import Signal
from .config import STATE_DB, DEPARTMENTS, get_department


class SessionReader:
    """Читает JSONL сессии, извлекает сырые сигналы"""

    # Ключевые слова для определения типа сигнала
    CORRECTION_KEYWORDS = [
        "не так", "неправильно", "ошибка", "исправь", "поправь", "не то",
        "не надо", "стоп", "отмена", "другой", "измени", "перепиши",
        "not correct", "wrong", "fix", "change", "redo", "stop", "cancel",
        "instead", "rather", "actually",
    ]

    FRUSTRATION_KEYWORDS = [
        "блин", "чёрт", "ужас", "кошмар", "ненавижу", "задолбал",
        "хуже", "глючит", "сломал", "не работает", "тормозит",
        "damn", "hate", "broken", "terrible", "awful", "sucks",
        "keeps failing", "again", "why", "how hard",
    ]

    WORKFLOW_KEYWORDS = [
        "готово", "сделано", "получилось", "работает", "отлично",
        "супер", "класс", "именно так", "вот это", "то что надо",
        "done", "works", "great", "perfect", "exactly", "nice",
        "awesome", "well done", "good job",
    ]

    UNMET_KEYWORDS = [
        "а как", "а можно", "а что если", "а если", "а вообще",
        "хочу чтобы", "надо бы", "нужно бы", "хочется",
        "how to", "can you", "is it possible", "what if",
        "i want", "i need", "would be nice",
    ]

    def __init__(self, config=None):
        self.config = config or {}
        self.max_sessions = self.config.get("max_sessions", 50)
        self.min_length = self.config.get("signal_min_length", 10)

    def read(self, session_dir: str = None) -> list:
        """
        Читает сессии из state.db, возвращает список Signal
        """
        db_path = session_dir if session_dir else STATE_DB
        if not os.path.exists(db_path):
            return []

        signals = []
        try:
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            # Берём последние N сессий
            cursor.execute("""
                SELECT id, title, source, model, started_at, ended_at,
                       message_count, tool_call_count
                FROM sessions
                ORDER BY started_at DESC
                LIMIT ?
            """, (self.max_sessions,))
            sessions = cursor.fetchall()

            for session in sessions:
                session_signals = self._extract_signals(cursor, session)
                signals.extend(session_signals)

            conn.close()
        except Exception as e:
            print(f"SessionReader error: {e}")

        return signals

    def _extract_signals(self, cursor, session) -> list:
        """Извлечь сигналы из одной сессии"""
        signals = []
        session_id = session["id"]

        # Берём ВСЕ сообщения одной запросом (user + assistant)
        cursor.execute("""
            SELECT id, role, content, timestamp, tool_name
            FROM messages
            WHERE session_id = ? AND role IN ('user', 'assistant')
            ORDER BY timestamp
        """, (session_id,))
        all_messages = cursor.fetchall()

        # Разделяем по ролям
        messages = [m for m in all_messages if m["role"] == "user"]
        assistant_msgs = [m for m in all_messages if m["role"] == "assistant"]

        # Определяем отдел по сессии
        all_text = " ".join([m["content"] or "" for m in messages])
        department = get_department(all_text)

        # Анализируем каждое сообщение пользователя
        for i, msg in enumerate(messages):
            content = msg["content"] or ""
            if len(content) < self.min_length:
                continue

            signal_type = self._classify_signal(content)
            severity = self._estimate_severity(content, signal_type)

            signal = Signal(
                type=signal_type,
                content=content[:500],  # обрезаем длинные сообщения
                source=session_id,
                severity=severity,
                department=department,
                meta={
                    "message_id": msg["id"],
                    "session_title": session["title"] or "",
                    "model": session["model"] or "",
                }
            )
            signals.append(signal)

        return signals

    def _classify_signal(self, text: str) -> str:
        """Классифицировать тип сигнала"""
        text_lower = text.lower()

        # Проверяем по приоритету
        if any(kw in text_lower for kw in self.CORRECTION_KEYWORDS):
            return "correction"

        if any(kw in text_lower for kw in self.FRUSTRATION_KEYWORDS):
            return "frustration"

        if any(kw in text_lower for kw in self.WORKFLOW_KEYWORDS):
            return "workflow"

        if any(kw in text_lower for kw in self.UNMET_KEYWORDS):
            return "unmet"

        return "request"

    def _estimate_severity(self, text: str, signal_type: str) -> float:
        """Оценить серьёжность сигнала (0.0 - 1.0)"""
        base = {
            "correction": 0.7,
            "frustration": 0.8,
            "workflow": 0.3,
            "unmet": 0.5,
            "request": 0.4,
        }.get(signal_type, 0.5)

        # Увеличиваем для повторений
        text_lower = text.lower()
        if text.count("!") > 2:
            base += 0.1
        if any(caps in text for caps in ["ВСЁ", "СТОП", "НЕ НАДО", "STOP", "NO"]):
            base += 0.15
        if len(text) > 200:
            base += 0.05

        return min(base, 1.0)


def extract_session_titles(session_dir: str = None) -> dict:
    """Быстро извлечь заголовки сессий"""
    db_path = session_dir if session_dir else STATE_DB
    if not os.path.exists(db_path):
        return {}

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, started_at FROM sessions ORDER BY started_at DESC")
    rows = cursor.fetchall()
    conn.close()

    return {row[0]: {"title": row[1], "started_at": row[2]} for row in rows}

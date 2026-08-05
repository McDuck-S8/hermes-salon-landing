#!/usr/bin/env python3
"""Nightly self-analysis — KC health, event stats, anomaly detection.

Runs via cron at 2am (no_agent). Reports what was found.
"""
import json, os, sqlite3
from datetime import datetime, timezone
from pathlib import Path

HERMES = Path(os.environ.get("HERMES_HOME", "D:/Portable_Soft/hermes"))
KC_DB = HERMES / "cache" / "knowledge_cube.db"
EVENTS_DB = HERMES / "cache" / "events.db"

report = []

def r(msg):
    report.append(msg)
    print(msg)

def check_kc():
    conn = sqlite3.connect(str(KC_DB))
    tables = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
    r(f"KC tables: {tables}")
    for tbl in tables:
        cnt = conn.execute(f"SELECT COUNT(*) FROM \"{tbl}\"").fetchone()[0]
        r(f"  {tbl}: {cnt} rows")
    conn.close()

def check_events():
    conn = sqlite3.connect(str(EVENTS_DB))
    total = conn.execute("SELECT COUNT(*) FROM events").fetchone()[0]
    unproc = conn.execute("SELECT COUNT(*) FROM events WHERE processed=0").fetchone()[0]
    r(f"Events DB: {total} total, {unproc} unprocessed")
    types = conn.execute("SELECT event_type, COUNT(*) FROM events GROUP BY event_type ORDER BY COUNT(*) DESC").fetchall()
    for et, cnt in types[:10]:
        r(f"  {et}: {cnt}")
    conn.close()

def check_triggers():
    conn = sqlite3.connect(str(EVENTS_DB))
    trigs = conn.execute("SELECT event_type, action, threshold, accumulated, last_triggered FROM triggers").fetchall()
    r("Triggers:")
    for t in trigs:
        r(f"  {t[0]:25s} {t[1]:25s} th={t[2]} acc={t[3]} last={t[4] or 'never'}")
    conn.close()

r(f"=== Nightly Self-Analysis [{datetime.now().strftime('%Y-%m-%d %H:%M')}] ===")
check_kc()
check_events()
check_triggers()

# ── Рефлексия по свежим сессиям (Этап 3): подсчёт коррекций ──
# 2026-08-05: КОПИРОВАНИЕ УДАЛЕНО. Раньше этот блок записывал
# «[урок из сессии] <сообщение пользователя>» в Куб — сырые копии
# коррекций, которые НИКТО не читал (проверено: единственный читатель —
# сам этот скрипт). 18 из 38 записей source=reflection_history — такие
# копии; грань reflection: 344 записи, потребителей — 0. Это тот же
# паттерн, что preventive_tests.json (53107 копий): запись вместо
# применения. Коррекции фиксируются штатно через
# hermes_hooks.on_user_correction → events.db (user_correction event),
# где у них есть потребитель (event_processor). Здесь — только подсчёт
# для отчёта, без производства мёртвых записей.
try:
    import sqlite3
    STATE_DB = HERMES / "state.db"
    conn = sqlite3.connect(str(STATE_DB))
    since = datetime.now().timestamp() - 86400
    pats = ["не так", "почему", "напоминаю", "не спрашивай", "я же", "опять", "просил", "исправ", "стоп"]
    cond = " OR ".join(["content LIKE ?"] * len(pats))
    n = conn.execute(
        f"SELECT COUNT(DISTINCT content) FROM messages WHERE role='user' AND timestamp > ? AND ({cond})",
        [since] + [f"%{x}%" for x in pats]).fetchone()[0]
    conn.close()
    r(f"Рефлексия: {n} коррекций за сутки (записей в Куб не производится — см. комментарий)")
except Exception as e:
    r(f"Рефлексия: ошибка — {e}")

r("=== Analysis Complete ===")

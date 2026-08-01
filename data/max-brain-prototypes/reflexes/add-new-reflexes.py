#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Add New Reflexes — Добавление новых рефлексов из саморефлексии

Дата: 2026-03-22 23:28
Триггер: Пользователь указал на отсутствие саморефлексии
"""

import sys
import json
from pathlib import Path
from datetime import datetime

# Добавляем путь к reflex-database.py
BRAIN_DIR = Path("D:/MAX-BRAIN")
sys.path.insert(0, str(BRAIN_DIR))

# Импортируем класс из reflex-database.py
import importlib.util
spec = importlib.util.spec_from_file_location("reflex_database", BRAIN_DIR / "reflex-database.py")
reflex_db_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(reflex_db_module)
ReflexDatabase = reflex_db_module.ReflexDatabase

# Новые рефлексы из саморефлексии
NEW_REFLEXES = [
    {
        "trigger_text": "task_id is None — пропускать задачу",
        "pattern": "Processing: None - unknown",
        "action": "continue (пропустить задачу без ID)",
        "type": "error_pattern",
        "weight": 0.8,
        "priority": "P0",
        "learned_from": "samoreflexia-2026-03-22",
        "context": "Auto-agent зацикливался на задачах без ID"
    },
    {
        "trigger_text": ".startswith() проверка на None",
        "pattern": "task_id.startswith(...)",
        "action": "(task_id and task_id.startswith(...))",
        "type": "code_defense",
        "weight": 0.9,
        "priority": "P0",
        "learned_from": "samoreflexia-2026-03-22",
        "context": "Баг: вызов .startswith() на None вызывал зацикливание"
    },
    {
        "trigger_text": "Event Bus CP1251 символы — очистка",
        "pattern": "utf-8 codec can't decode byte",
        "action": "очистить events.jsonl, создать новый с заголовком",
        "type": "data_recovery",
        "weight": 0.7,
        "priority": "P1",
        "learned_from": "samoreflexia-2026-03-22",
        "context": "Event Bus битый из-за CP1251 символов в JSON"
    },
    {
        "trigger_text": "Skeptic зацикливание — rate limiting",
        "pattern": "skeptic-*.py --task",
        "action": "ограничить 5 задач одновременно, таймаут 60 сек",
        "type": "rate_limiting",
        "weight": 0.8,
        "priority": "P1",
        "learned_from": "samoreflexia-2026-03-22",
        "context": "18 процессов Skeptic зависли в фоне"
    },
    {
        "trigger_text": "Self-Evolution активация после проблемы",
        "pattern": "проблема исправлена",
        "action": "запустить self-evolution.py для анализа",
        "type": "meta_cognition",
        "weight": 0.9,
        "priority": "P0",
        "learned_from": "samoreflexia-2026-03-22",
        "context": "Пользователь указал на отсутствие саморефлексии"
    },
    {
        "trigger_text": "Error Classifier активация",
        "pattern": "ошибка в логе",
        "action": "классифицировать ошибку, сохранить в errors-classified.jsonl",
        "type": "meta_cognition",
        "weight": 0.8,
        "priority": "P1",
        "learned_from": "samoreflexia-2026-03-22",
        "context": "Ошибки не классифицировались автоматически"
    }
]

def add_reflexes():
    """Добавить новые рефлексы в базу"""
    print("=" * 70)
    print("🧠 ADD NEW REFLEXES — Саморефлексия 2026-03-22")
    print("=" * 70)
    
    db = ReflexDatabase()
    
    added_count = 0
    for reflex in NEW_REFLEXES:
        try:
            # Создаём кандидата в рефлексы
            candidate = {
                "trigger_text": reflex["trigger_text"],
                "pattern": reflex["pattern"],
                "action": reflex["action"],
                "type": reflex["type"],
                "weight": reflex["weight"],
                "priority": reflex["priority"],
                "learned_from": reflex["learned_from"],
                "context": reflex["context"],
                "created_at": datetime.now().isoformat()
            }
            
            # Добавляем в базу
            db.add_candidate(candidate)
            added_count += 1
            print(f"   ✅ Добавлен рефлекс: {reflex['trigger_text'][:50]}...")
            
        except Exception as e:
            print(f"   ❌ Ошибка: {reflex['trigger_text'][:50]}... — {e}")
    
    print()
    print("=" * 70)
    print(f"✅ ДОБАВЛЕНО РЕФЛЕКСОВ: {added_count}/{len(NEW_REFLEXES)}")
    print("=" * 70)
    
    # Статистика
    print()
    print("📊 СТАТИСТИКА:")
    print(f"   Всего рефлексов: {len(db.reflexes)}")
    
    # По типам
    by_type = {}
    for r in db.reflexes:
        t = r.get('type', 'unknown')
        by_type[t] = by_type.get(t, 0) + 1
    print(f"   По типам: {by_type}")
    
    # По приоритету
    by_priority = {}
    for r in db.reflexes:
        p = r.get('priority', 'unknown')
        by_priority[p] = by_priority.get(p, 0) + 1
    print(f"   По приоритету: {by_priority}")
    
    print()
    print("📁 Reflex Database обновлён!")
    print("=" * 70)

if __name__ == "__main__":
    add_reflexes()

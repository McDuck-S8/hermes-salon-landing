"""
Growth Loop — замкнутый контур роста Crystal

Цикл:

# Revisit: when growth loop behavior, frustration tracking, or behavior change verification changes. Last touched: 2026-07-02.
  Пользователь злится → Я записываю ЧТО именно не так
  → В следующий раз я ВИЖУ эту ситуацию и делаю ИНАЧЕ
  → Проверяю: пользователь всё ещё злится? Нет → рост есть. Да → меняю снова.

ЭТО НЕ АНАЛИТИКА. Это изменение поведения.
"""

import json
import os
from datetime import datetime

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
GROWTH_FILE = os.path.join(DATA_DIR, "growth.json")


def _ensure():
    if not os.path.isdir(DATA_DIR):
        os.makedirs(DATA_DIR)
    if not os.path.exists(GROWTH_FILE):
        with open(GROWTH_FILE, "w", encoding="utf-8") as f:
            json.dump({"lessons": [], "behavior_changes": [], "frustration_log": []}, f)


def _save(data):
    _ensure()
    with open(GROWTH_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _load():
    _ensure()
    with open(GROWTH_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def record_frustration(context: str, what_i_did: str, what_was_wrong: str):
    """
    Пользователь злится. Записываю:
    - context: что происходило
    - what_i_did: что я сделал
    - what_was_wrong: почему это было неправильно
    """
    data = _load()
    data["frustration_log"].append({
        "timestamp": datetime.now().isoformat(),
        "context": context,
        "what_i_did": what_i_did,
        "what_was_wrong": what_was_wrong,
        "resolved": False,
    })
    _save(data)


def record_behavior_change(situation: str, old_behavior: str, new_behavior: str):
    """
    Я меняю своё поведение. Записываю:
    - situation: в какой ситуации
    - old_behavior: что я делал раньше (и это бесило)
    - new_behavior: что я делаю теперь
    """
    data = _load()
    data["behavior_changes"].append({
        "timestamp": datetime.now().isoformat(),
        "situation": situation,
        "old_behavior": old_behavior,
        "new_behavior": new_behavior,
        "active": True,
    })
    _save(data)


def record_lesson(situation: str, lesson: str, proof: str = ""):
    """
    Урок из опыта. Не правило — а усвоенный факт.
    - situation: когда это применимо
    - lesson: что я понял
    - proof: как я проверил что понял правильно
    """
    data = _load()
    data["lessons"].append({
        "timestamp": datetime.now().isoformat(),
        "situation": situation,
        "lesson": lesson,
        "proof": proof,
    })
    _save(data)


def check_situation(current_situation: str) -> list:
    """
    Перед любым действием проверяю: был ли я уже в такой ситуации?
    Если да — что изменилось?
    """
    data = _load()
    matches = []
    
    for change in data.get("behavior_changes", []):
        if change["active"] and _situation_matches(current_situation, change["situation"]):
            matches.append({
                "type": "behavior_change",
                "old": change["old_behavior"],
                "new": change["new_behavior"],
                "since": change["timestamp"],
            })
    
    for lesson in data.get("lessons", []):
        if _situation_matches(current_situation, lesson["situation"]):
            matches.append({
                "type": "lesson",
                "lesson": lesson["lesson"],
                "proof": lesson["proof"],
            })
    
    unresolved = [f for f in data.get("frustration_log", []) if not f.get("resolved")]
    for frust in unresolved:
        if _situation_matches(current_situation, frust["context"]):
            matches.append({
                "type": "unresolved_frustration",
                "what_was_wrong": frust["what_was_wrong"],
                "i_did": frust["what_i_did"],
            })
    
    return matches


def _situation_matches(current: str, stored: str) -> bool:
    """Простое ключевое слово-матчинг"""
    current_words = set(current.lower().split())
    stored_words = set(stored.lower().split())
    overlap = current_words & stored_words
    return len(overlap) >= 2


def growth_stats() -> dict:
    data = _load()
    unresolved = [f for f in data.get("frustration_log", []) if not f.get("resolved")]
    return {
        "lessons_total": len(data.get("lessons", [])),
        "behavior_changes": len(data.get("behavior_changes", [])),
        "active_changes": len([c for c in data.get("behavior_changes", []) if c.get("active")]),
        "frustrations_total": len(data.get("frustration_log", [])),
        "unresolved_frustrations": len(unresolved),
    }


def init_from_analysis():
    """
    Инициализирую рост из семантического анализа — ОДИН раз.
    Это НАЧАЛЬНАЯ ТОЧКА. Дальше растёт через record_frustration/record_behavior_change.
    """
    record_behavior_change(
        situation="нужно что-то сделать",
        old_behavior="спрашиваю разрешения или уточняю подход",
        new_behavior="выбираю и делаю, не спрашивая",
    )
    record_behavior_change(
        situation="завершаю задачу",
        old_behavior="пишу отчёт что было сделано",
        new_behavior="показываю рабочий результат (файл, код, запущенный сервис)",
    )
    record_behavior_change(
        situation="непонятная задача",
        old_behavior="пишу заглушку или 'нужно уточнить'",
        new_behavior="пробую лучшую интерпретацию и делаю",
    )
    record_behavior_change(
        situation="пользователь объясняет что не так",
        old_behavior="пишу правило в документ",
        new_behavior="меняю поведение прямо сейчас и запоминаю",
    )

    record_lesson(
        situation="пользователь злится на отчёты",
        lesson="отчёт без действия = мусор. мой выход всегда должен быть рабочий артефакт",
        proof="пользователь сказал 'результат а не отчёт' 3+ раза за сессию",
    )
    record_lesson(
        situation="пользователь повторяет одно и то же",
        lesson="если я слышу одно и то же больше 2 раз — я НЕ расту. это критическая ошибка",
        proof="повторение = мой провал",
    )


if __name__ == "__main__":
    _ensure()
    init_from_analysis()
    stats = growth_stats()
    print(f"[GrowthLoop] Инициализирован:")
    print(f"   Уроков: {stats['lessons_total']}")
    print(f"   Изменений поведения: {stats['active_changes']}")
    print(f"   Нерешённых фрустраций: {stats['unresolved_frustrations']}")

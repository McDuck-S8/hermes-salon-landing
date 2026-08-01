#!/usr/bin/env python3
"""memory_guard.py — защита от амнезии.

Проверяет что CORE_IDENTITY.md, CORE_PIPELINE.md, MEMORY.md 
не пусты и не повреждены после перезагрузки.

Запускать: при старте сессии, при завершении сессии, каждые 6ч.

Восстановлен из бэкапа 2026-06-21 после краха 2026-07-23.
"""
import os
import sys
import json
from datetime import datetime

HERMES = "D:/Portable_Soft/hermes"
GUARD_LOG = os.path.join(HERMES, "cache", "memory_guard_log.json")

ESSENTIALS = {
    "CORE_IDENTITY.md": {"min_chars": 500, "sections": ["Кто я", "Заповедь", "Ключевое решение"]},
    "CORE_PIPELINE.md": {"min_chars": 100, "sections": []},
    "memories/MEMORY.md": {"min_chars": 50, "sections": ["learnings"]},
    "memories/USER.md": {"min_chars": 100, "sections": []},
}

def check_file(rel_path: str, min_chars: int, required_sections: list) -> dict:
    full = os.path.join(HERMES, rel_path)
    result = {"path": rel_path, "exists": False, "size": 0, "chars": 0, "healthy": False, "missing_sections": []}
    if not os.path.exists(full):
        result["error"] = "FILE_MISSING"
        return result
    result["exists"] = True
    result["size"] = os.path.getsize(full)
    try:
        with open(full, "r", encoding="utf-8") as f:
            content = f.read()
        result["chars"] = len(content)
        if result["chars"] < min_chars:
            result["error"] = f"TOO_SHORT ({result['chars']} < {min_chars})"
            return result
        for sec in required_sections:
            if sec not in content:
                result["missing_sections"].append(sec)
        if not result["missing_sections"]:
            result["healthy"] = True
    except Exception as e:
        result["error"] = f"READ_ERROR: {e}"
    return result


def run_check():
    entry = {
        "timestamp": datetime.now().isoformat(),
        "checks": {},
        "all_healthy": True,
        "alerts": []
    }
    for path, cfg in ESSENTIALS.items():
        res = check_file(path, cfg["min_chars"], cfg["sections"])
        entry["checks"][path] = res
        if not res.get("healthy"):
            entry["all_healthy"] = False
            entry["alerts"].append(f"⚠ {path}: {res.get('error', 'UNHEALTHY')}")
    if entry["all_healthy"]:
        entry["summary"] = "✅ All memory files healthy"
    else:
        entry["summary"] = f"❌ {len(entry['alerts'])} issue(s) found"
    return entry


def save_log(entry: dict):
    os.makedirs(os.path.dirname(GUARD_LOG), exist_ok=True)
    history = []
    if os.path.exists(GUARD_LOG):
        try:
            with open(GUARD_LOG, "r") as f:
                history = json.load(f)
                if not isinstance(history, list):
                    history = []
        except:
            history = []
    history.append(entry)
    if len(history) > 100:
        history = history[-100:]
    with open(GUARD_LOG, "w") as f:
        json.dump(history, f, indent=1, ensure_ascii=False)


def main():
    entry = run_check()
    save_log(entry)
    print(f"[memory_guard] {entry['summary']}")
    if not entry["all_healthy"]:
        for alert in entry["alerts"]:
            print(f"  {alert}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

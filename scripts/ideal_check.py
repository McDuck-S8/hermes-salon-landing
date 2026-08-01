#!/usr/bin/env python3
"""
IDEAL_STANDARD Check — автооценка соответствия эталона Джарвиса
Запускается при каждом авто-буте и по требованию.
"""
import json
import sys
from pathlib import Path
from datetime import datetime

IDEAL_FILE = Path(__file__).parent / "IDEAL_STANDARD.md"

# Метрики из IDEAL_STANDARD.md (ОБНОВЛЕНО 2026-07-28 после внедрения P0)
METRICS = {
    "proactivity": {
        "predicts_needs": 55,      # cron jobs: proactive_doer (15m), auto_boot_scan (15m), heartbeat_fixer (10m)
        "no_wait_commands": 50,    # auto_boot_scan генерирует morning_report кэш каждые 15м
        "reports_fact": 60,        # self_conscience_gate фильтрует упаковку
    },
    "honesty_boundaries": {
        "admits_cant": 70,
        "not_human": 80,           # self_conscience_gate: не выдаёт план за результат
        "respects_limits": 85,     # kill switches, exfiltration guard работают
    },
    "owner_relationship": {
        "respect_no_subservience": 55,  # ещё не убрал вопросы пользователю
        "teaches_owner": 50,          # morning report пока констатирует, не даёт инсайтов
        "grows_with_owner": 55,       # метрики есть, но нет дашборда
    },
    "humor_humanity": {
        "self_irony": 15,            # начал менять тон ответов
        "dry_humor": 10,
    },
    "reliability": {
        "never_down": 75,            # heartbeat_fixer cron */10
        "self_heals": 70,            # proactive_doer чинит locks, json, dead jobs
        "remembers_all": 80,         # KC + Event Evolution + session_bridge
    },
}

CATEGORY_WEIGHTS = {
    "proactivity": 0.30,
    "honesty_boundaries": 0.20,
    "owner_relationship": 0.25,
    "humor_humanity": 0.05,
    "reliability": 0.20,
}

TARGET_THRESHOLD = 80  # % — цель по каждой категории


def calculate_scores():
    """Вычисляет скоры по категориям и общий."""
    category_scores = {}
    for cat, metrics in METRICS.items():
        avg = sum(metrics.values()) / len(metrics)
        category_scores[cat] = round(avg, 1)

    # Взвешенный общий
    weighted = sum(
        category_scores[cat] * CATEGORY_WEIGHTS[cat]
        for cat in category_scores
    )
    overall = round(weighted, 1)

    return category_scores, overall


def get_status(score):
    """Статус по скору."""
    if score >= 80:
        return "✅ TARGET"
    elif score >= 60:
        return "⚠️ NEEDS WORK"
    else:
        return "🔴 CRITICAL"


def main():
    print("=" * 60)
    print("J.A.R.V.I.S. IDEAL STANDARD — AUTO-ASSESSMENT")
    print("=" * 60)
    print(f"Time: {datetime.now().isoformat()}")
    print()

    category_scores, overall = calculate_scores()

    print("CATEGORY BREAKDOWN:")
    print("-" * 60)
    for cat, score in category_scores.items():
        status = get_status(score)
        weight = CATEGORY_WEIGHTS[cat]
        print(f"  {cat:25s} {score:5.1f}%  (weight: {weight:.0%})  {status}")

    print("-" * 60)
    print(f"  {'OVERALL':25s} {overall:5.1f}%  {get_status(overall)}")
    print()

    # Проблемные зоны (< 80%)
    problems = [cat for cat, score in category_scores.items() if score < 80]
    if problems:
        print("PROBLEM AREAS (P0):")
        for cat in problems:
            print(f"  - {cat}: {category_scores[cat]}% (target: 80%+)")
    else:
        print("ALL CATEGORIES AT TARGET. 🎯")

    print()

    # P0 задачи из плана
    print("P0 ACTION ITEMS (from IDEAL_STANDARD.md):")
    p0_items = [
        "auto_boot_scan.py → cron каждые 15 мин, генерирует cache/morning_report.json",
        "proactive_doer.py → включить в cron, убрать notify_on_complete=false",
        "Self-ask Policy 6 check в каждый ответ: 'Что сделал проактивно за 60 мин?'",
        "self_conscience_gate.py — 3 вопроса перед действием",
        "Morning Report: секция 'Что ты мог упустить' (insight engine)",
        "Pre-commit hook: запрет коммита без git add -p + тест",
        "Response gate: если нет артефакта — ответ = 'В процессе. Артефакт: [путь]'",
    ]
    for i, item in enumerate(p0_items, 1):
        print(f"  {i}. {item}")

    print()
    print("=" * 60)

    # Возврат кода выхода: 0 если overall >= 80, иначе 1
    return 0 if overall >= 80 else 1


if __name__ == "__main__":
    sys.exit(main())
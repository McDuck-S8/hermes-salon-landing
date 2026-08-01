#!/usr/bin/env python3
"""
salary_crimea.py — Salary benchmarking for Crimean job market.

Provides salary benchmarks for common roles in Crimea/Simferopol.
Data is approximate and based on publicly available information.

Usage:
  python salary_crimea.py --role "Программист Python"
  python salary_crimea.py --role "Водитель" --city simferopol
  python salary_crimea.py --list-all
  python salary_crimea.py --role "Продавец" --json
"""

import json
import sys
import argparse
from pathlib import Path

DATA_FILE = Path(__file__).parent / "salary_data.json"

# Default salary data for Crimea if data file doesn't exist
DEFAULT_SALARIES = {
    "metadata": {
        "source": "hh.ru, zarplata.ru, gorodrabot.ru (average data for Crimea, 2025-2026)",
        "last_updated": "2026-06",
        "currency": "RUR",
        "note": "Зарплаты указаны в рублях. Данные приблизительные, основаны на публичных источниках.",
    },
    "roles": [
        {"role": "Программист Python", "min": 60000, "max": 180000, "avg": 110000, "city": "symferopol"},
        {"role": "Программист Java", "min": 70000, "max": 200000, "avg": 130000, "city": "symferopol"},
        {"role": "Веб-разработчик (Frontend)", "min": 50000, "max": 150000, "avg": 90000, "city": "symferopol"},
        {"role": "Веб-разработчик (Backend)", "min": 60000, "max": 170000, "avg": 105000, "city": "symferopol"},
        {"role": "Fullstack разработчик", "min": 70000, "max": 200000, "avg": 120000, "city": "symferopol"},
        {"role": "DevOps инженер", "min": 80000, "max": 220000, "avg": 140000, "city": "symferopol"},
        {"role": "Data Scientist", "min": 70000, "max": 200000, "avg": 120000, "city": "symferopol"},
        {"role": "Системный администратор", "min": 35000, "max": 90000, "avg": 55000, "city": "symferopol"},
        {"role": "Тестировщик (QA)", "min": 40000, "max": 120000, "avg": 70000, "city": "symferopol"},
        {"role": "Менеджер проектов (IT)", "min": 60000, "max": 180000, "avg": 100000, "city": "symferopol"},
        {"role": "Product Manager", "min": 80000, "max": 200000, "avg": 130000, "city": "symferopol"},
        {"role": "Аналитик 1С", "min": 50000, "max": 130000, "avg": 80000, "city": "symferopol"},
        {"role": "Бухгалтер", "min": 30000, "max": 80000, "avg": 50000, "city": "symferopol"},
        {"role": "Менеджер по продажам", "min": 25000, "max": 100000, "avg": 50000, "city": "symferopol"},
        {"role": "Продавец-консультант", "min": 20000, "max": 50000, "avg": 35000, "city": "symferopol"},
        {"role": "Кассир", "min": 20000, "max": 40000, "avg": 30000, "city": "symferopol"},
        {"role": "Администратор", "min": 25000, "max": 55000, "avg": 38000, "city": "symferopol"},
        {"role": "Водитель", "min": 30000, "max": 80000, "avg": 50000, "city": "symferopol"},
        {"role": "Курьер", "min": 25000, "max": 70000, "avg": 40000, "city": "symferopol"},
        {"role": "Грузчик", "min": 25000, "max": 55000, "avg": 38000, "city": "symferopol"},
        {"role": "Повар", "min": 25000, "max": 65000, "avg": 40000, "city": "symferopol"},
        {"role": "Официант", "min": 15000, "max": 45000, "avg": 30000, "city": "symferopol"},
        {"role": "Медицинская сестра", "min": 25000, "max": 55000, "avg": 38000, "city": "symferopol"},
        {"role": "Врач", "min": 40000, "max": 120000, "avg": 70000, "city": "symferopol"},
        {"role": "Учитель", "min": 20000, "max": 50000, "avg": 35000, "city": "symferopol"},
        {"role": "Маркетолог", "min": 30000, "max": 100000, "avg": 60000, "city": "symferopol"},
        {"role": "SMM-менеджер", "min": 25000, "max": 80000, "avg": 50000, "city": "symferopol"},
        {"role": "Дизайнер (графический)", "min": 30000, "max": 100000, "avg": 60000, "city": "symferopol"},
        {"role": "UI/UX дизайнер", "min": 40000, "max": 140000, "avg": 80000, "city": "symferopol"},
        {"role": "Юрист", "min": 30000, "max": 100000, "avg": 60000, "city": "symferopol"},
        {"role": "Архитектор", "min": 50000, "max": 150000, "avg": 90000, "city": "symferopol"},
        {"role": "Строитель", "min": 30000, "max": 80000, "avg": 50000, "city": "symferopol"},
        {"role": "Инженер-строитель", "min": 40000, "max": 120000, "avg": 70000, "city": "symferopol"},
        {"role": "Экономист", "min": 30000, "max": 80000, "avg": 50000, "city": "symferopol"},
        {"role": "HR-менеджер", "min": 30000, "max": 80000, "avg": 50000, "city": "symferopol"},
        # Remote / IT roles (higher pay)
        {"role": "Программист Python (удаленно)", "min": 80000, "max": 300000, "avg": 150000, "city": "remote"},
        {"role": "Программист JavaScript (удаленно)", "min": 70000, "max": 280000, "avg": 140000, "city": "remote"},
        {"role": "Аналитик данных (удаленно)", "min": 60000, "max": 250000, "avg": 120000, "city": "remote"},
    ],
}


def load_data():
    """Load salary data, creating default if not exists."""
    if not DATA_FILE.exists():
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_SALARIES, f, ensure_ascii=False, indent=2)
        return dict(DEFAULT_SALARIES)
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def normalize(s: str) -> str:
    """Normalize string for matching."""
    return s.lower().strip().replace("ё", "е")


def match_score(query: str, role: str) -> int:
    """Compute match score between query and role name."""
    q = normalize(query)
    r = normalize(role)

    # Exact match
    if q == r:
        return 100

    # Query is contained in role
    if q in r:
        return 80 + int(len(q) / max(len(r), 1) * 20)

    # Role is contained in query
    if r in q:
        return 80

    # Word overlap
    q_words = set(q.split())
    r_words = set(r.split())
    if not q_words or not r_words:
        return 0
    overlap = q_words & r_words
    if overlap:
        return int(30 + len(overlap) / max(len(q_words), 1) * 50)
    return 0


def main():
    parser = argparse.ArgumentParser(description="Зарплатные ориентиры для Крыма")
    parser.add_argument("--role", "-r", help="Название должности для поиска")
    parser.add_argument("--city", "-c", help="Город (по умолчанию: Симферополь)")
    parser.add_argument("--list-all", "-l", action="store_true", help="Показать все должности")
    parser.add_argument("--json", action="store_true", help="Вывод в JSON")

    args = parser.parse_args()
    data = load_data()
    metadata = data.get("metadata", {})

    if args.list_all:
        if args.json:
            print(json.dumps({"roles": data["roles"], "metadata": metadata},
                             ensure_ascii=False, indent=2))
            return
        print(f"\n  {'Должность':40s} {'Мин':>10s} {'Средняя':>10s} {'Макс':>10s} Город")
        print(f"  {'─'*80}")
        for entry in data["roles"]:
            city = entry.get("city", "")
            city_label = {"symferopol": "Симферополь", "remote": "Удаленно", "crimea": "Крым"}.get(city, city)
            print(f"  {entry['role']:40s} {entry['min']:>8,} ₽ {entry['avg']:>8,} ₽ {entry['max']:>8,} ₽ {city_label}")
        print(f"\n  Источник: {metadata.get('source', '')}")
        return

    if not args.role:
        parser.print_help()
        sys.exit(1)

    # Search for role
    scored = []
    for entry in data["roles"]:
        score = match_score(args.role, entry["role"])
        if score > 0:
            scored.append((score, entry))

    scored.sort(key=lambda x: -x[0])
    min_score = 40
    results = [entry for score, entry in scored if score >= min_score]

    if not results:
        print(f"\n  Ничего не найдено для '{args.role}'")
        print("  Попробуйте другие ключевые слова или --list-all")
        sys.exit(1)

    if args.city:
        city_map = {"simferopol": "symferopol", "симферополь": "symferopol",
                    "remote": "remote", "удаленно": "remote", "удалённо": "remote"}
        target = city_map.get(args.city.lower(), args.city.lower())
        results = [r for r in results if r.get("city") == target]
        if not results:
            print(f"\n  Ничего не найдено для '{args.role}' в {args.city}")
            sys.exit(0)

    if args.json:
        print(json.dumps({"query": args.role, "results": results, "metadata": metadata},
                         ensure_ascii=False, indent=2))
        return

    for entry in results:
        city_label = {"symferopol": "Симферополь", "remote": "Удаленно"}.get(entry.get("city", ""), "")
        print(f"\n  {entry['role']} ({city_label})")
        print(f"  {'─'*40}")
        print(f"  Минимальная:   {entry['min']:>8,} ₽")
        print(f"  Средняя:       {entry['avg']:>8,} ₽")
        print(f"  Максимальная:  {entry['max']:>8,} ₽")

    print(f"\n  Данные: {metadata.get('source', '')}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
crimea_assistant.py — AI Job Search Assistant for Crimea & Simferopol.

A complete workflow: profile setup → job search → evaluation → CV generation.

Inspired by https://github.com/MadsLorentzen/ai-job-search
Adapted for Crimean/Russian job market (hh.ru).

Usage:
  python crimea_assistant.py search -q "python"                         # Quick search
  python crimea_assistant.py search -q "водитель" --full                # Full workflow
  python crimea_assistant.py setup                                       # Create/update profile
  python crimea_assistant.py profile                                     # Show current profile
  python crimea_assistant.py evaluate --vacancy-id 12345678              # Evaluate a vacancy
  python crimea_assistant.py generate-cv                                 # Generate CV from profile
  python crimea_assistant.py generate-letter --vacancy "Python dev" --company "X"  # Cover letter
  python crimea_assistant.py salary --role "Программист"                 # Salary benchmark
  python crimea_assistant.py dashboard                                   # Market overview
"""

import json
import sys
import argparse
import subprocess
from pathlib import Path
from datetime import datetime

PROJECT_DIR = Path(__file__).parent
HH_TOOL = PROJECT_DIR / "hhru_crimea.py"
PROFILE_TOOL = PROJECT_DIR / "setup_profile.py"
SALARY_TOOL = PROJECT_DIR / "salary_crimea.py"
CV_TOOL = PROJECT_DIR / "fill_cv.py"
PROFILE_FILE = PROJECT_DIR / "candidate_profile.json"
CACHE_DIR = PROJECT_DIR / "cache"


def ensure_profile() -> dict:
    """Load profile or exit with error."""
    if not PROFILE_FILE.exists():
        print("  ✗ Профиль не найден. Сначала настройте: python crimea_assistant.py setup")
        sys.exit(1)
    with open(PROFILE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def cmd_setup(args):
    """Run interactive profile setup."""
    cmd = [sys.executable, str(PROFILE_TOOL), "interactive"]
    if args.section:
        cmd.extend(["--section", args.section])
    subprocess.run(cmd)


def cmd_profile(args):
    """Show current profile."""
    cmd = [sys.executable, str(PROFILE_TOOL), "show"]
    subprocess.run(cmd)


def cmd_search(args):
    """Search for jobs on hh.ru in Crimea."""
    cmd = [
        sys.executable, str(HH_TOOL), "search",
        "-q", args.query,
        "-a", args.area or "crimea",
        "--days", str(args.days or 30),
        "--sort", args.sort or "publication_time",
        "--per-page", str(args.per_page or 20),
        "--page", str(args.page or 1),
    ]

    if args.format:
        cmd.extend(["--format", args.format])
    if args.salary:
        cmd.extend(["--salary", args.salary])
    if args.experience:
        cmd.extend(["--experience", args.experience])
    if args.employment:
        cmd.extend(["--employment", args.employment])
    if args.with_salary:
        cmd.append("--with-salary")

    result = subprocess.run(cmd)
    if result.returncode != 0:
        sys.exit(result.returncode)

    # Save search results to cache for later evaluation
    if args.format != "json":
        save_search(args.query, args.area or "crimea")


def save_search(query: str, area: str):
    """Save search metadata for later use."""
    CACHE_DIR.mkdir(exist_ok=True)
    entry = {
        "timestamp": datetime.now().isoformat(),
        "query": query,
        "area": area,
    }
    cache_file = CACHE_DIR / "last_search.json"
    with open(cache_file, "w", encoding="utf-8") as f:
        json.dump(entry, f, ensure_ascii=False, indent=2)


def cmd_evaluate(args):
    """Evaluate a vacancy against your profile."""
    profile = ensure_profile()
    p = profile.get("personal", {})
    prefs = profile.get("preferences", {})
    skills = profile.get("skills", {})

    # Fetch vacancy details
    cmd = [
        sys.executable, str(HH_TOOL), "detail",
        args.vacancy_id, "--format", "json",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"  ✗ Не удалось получить данные вакансии {args.vacancy_id}")
        return

    try:
        vacancy = json.loads(result.stdout)
    except json.JSONDecodeError:
        print(f"  ✗ Ошибка парсинга данных вакансии")
        return

    name = vacancy.get("name", "")
    employer = vacancy.get("employer", {}).get("name", "")
    description = vacancy.get("description", "")
    salary_data = vacancy.get("salary", {})
    key_skills = [s["name"] for s in vacancy.get("key_skills", [])]
    experience = vacancy.get("experience", {}).get("name", "")
    employment = vacancy.get("employment", {}).get("name", "")

    print(f"\n{'='*60}")
    print(f"  ОЦЕНКА ВАКАНСИИ")
    print(f"{'='*60}")
    print(f"\n  [{args.vacancy_id}] {name}")
    print(f"  Компания: {employer}")
    print(f"  Опыт: {experience} | Занятость: {employment}")

    # Salary match
    target_salary = prefs.get("min_salary", 0)
    salary_from = salary_data.get("from") if salary_data else None
    if target_salary and salary_from:
        if salary_from >= target_salary:
            print(f"  ✓ Зарплата: от {salary_from} ₽ (соответствует ожиданиям от {target_salary} ₽)")
        else:
            print(f"  ⚠ Зарплата: от {salary_from} ₽ (ниже ожидаемых {target_salary} ₽)")
    elif salary_data:
        print(f"  Зарплата: {format_salary_eval(salary_data)}")
    else:
        print(f"  ⚠ Зарплата: не указана")

    # Skills match
    my_skills = set()
    for skill_list in skills.values():
        if isinstance(skill_list, list):
            for s in skill_list:
                my_skills.add(s.lower().strip())

    if key_skills:
        matched = []
        missing = []
        for ks in key_skills:
            ksl = ks.lower().strip()
            if any(ms in ksl or ksl in ms for ms in my_skills):
                matched.append(ks)
            else:
                missing.append(ks)

        if matched:
            print(f"\n  ✓ Совпадающие навыки ({len(matched)}):")
            print(f"    {', '.join(matched)}")
        if missing:
            print(f"\n  ✗ Отсутствующие навыки ({len(missing)}):")
            print(f"    {', '.join(missing)}")

    # Role match
    target_roles = prefs.get("target_roles", [])
    if target_roles:
        name_lower = name.lower()
        matches_role = any(r.lower() in name_lower or name_lower in r.lower() for r in target_roles)
        if matches_role:
            print(f"\n  ✓ Вакансия соответствует вашим целевым ролям")
        else:
            print(f"\n  ⚠ Вакансия может не соответствовать вашим ролям: {', '.join(target_roles)}")

    # Overall score
    score = 0
    max_score = 100

    # Salary score
    if target_salary and salary_from:
        if salary_from >= target_salary:
            score += 25
    elif salary_from:
        ratio = salary_from / max(target_salary, 1)
        score += min(25, int(ratio * 25))

    # Skills score
    if key_skills and my_skills:
        skill_score = int((len(matched) / len(key_skills)) * 40) if key_skills else 0
        score += skill_score

    # Role score
    if matches_role:
        score += 20

    # Experience score (subjective)
    score += 5  # base for getting the detail

    # Remote match
    if prefs.get("remote"):
        if "удален" in description.lower() or "remote" in description.lower():
            score += 10

    print(f"\n{'─'*60}")
    print(f"  ОБЩАЯ ОЦЕНКА: {min(score, max_score)}/100")
    if score >= 70:
        print(f"  ▶ Рекомендуется к отклику!")
    elif score >= 40:
        print(f"  ▶ Можно откликнуться, но проверьте детали")
    else:
        print(f"  ▶ Низкое соответствие профилю")

    vacancy_url = vacancy.get("alternate_url", "")
    if vacancy_url:
        print(f"\n  Ссылка: {vacancy_url}")
    print()


def format_salary_eval(salary_data):
    """Format salary for evaluate output."""
    fr = salary_data.get("from")
    to = salary_data.get("to")
    currency = salary_data.get("currency", "RUR")
    if fr and to:
        return f"от {fr:,} до {to:,} ₽".replace(",", " ")
    elif fr:
        return f"от {fr:,} ₽".replace(",", " ")
    elif to:
        return f"до {to:,} ₽".replace(",", " ")
    return "—"


def cmd_generate_cv(args):
    """Generate CV from profile."""
    cmd = [sys.executable, str(CV_TOOL), "--type", "cv"]
    if args.compile:
        cmd.append("--compile")
    if args.output:
        cmd.extend(["--output", args.output])
    subprocess.run(cmd)


def cmd_generate_letter(args):
    """Generate cover letter from profile."""
    cmd = [sys.executable, str(CV_TOOL), "--type", "cover-letter"]
    if args.vacancy:
        cmd.extend(["--vacancy", args.vacancy])
    if args.company:
        cmd.extend(["--company", args.company])
    if args.compile:
        cmd.append("--compile")
    if args.output:
        cmd.extend(["--output", args.output])
    subprocess.run(cmd)


def cmd_salary(args):
    """Look up salary benchmarks."""
    cmd = [sys.executable, str(SALARY_TOOL)]
    if args.role:
        cmd.extend(["--role", args.role])
    if args.list_all:
        cmd.append("--list-all")
    if args.json:
        cmd.append("--json")
    if args.city:
        cmd.extend(["--city", args.city])
    subprocess.run(cmd)


def cmd_dashboard(args):
    """Show a market overview dashboard for Crimea."""
    print(f"\n{'='*60}")
    print(f"  РЫНОК ТРУДА — КРЫМ / СИМФЕРОПОЛЬ")
    print(f"  {datetime.now().strftime('%d.%m.%Y')}")
    print(f"{'='*60}")

    # Quick salary benchmarks for popular roles
    print(f"\n  КРАТКИЙ ОБЗОР ЗАРПЛАТ")
    print(f"  {'─'*40}")
    roles = [
        ("Программист", "110 000 ₽"),
        ("Продавец", "35 000 ₽"),
        ("Водитель", "50 000 ₽"),
        ("Бухгалтер", "50 000 ₽"),
        ("Менеджер по продажам", "50 000 ₽"),
    ]
    for role, salary in roles:
        print(f"  {role:25s} ~ {salary}")

    print(f"\n  БЫСТРЫЙ ПОИСК")
    print(f"  {'─'*40}")
    print(f"  python crimea_assistant.py search -q \"программист\"")
    print(f"  python crimea_assistant.py search -q \"продавец\" --salary 30000-50000")
    print(f"  python crimea_assistant.py salary --role \"Программист\"")
    print(f"  python crimea_assistant.py salary --list-all")

    print(f"\n  ПЛАТФОРМЫ ДЛЯ ПОИСКА")
    print(f"  {'─'*40}")
    print(f"  • hh.ru/simferopol  — https://simferopol.hh.ru")
    print(f"  • zarplata.ru       — https://zarplata.ru")
    print(f"  • superjob.ru       — https://superjob.ru")
    print(f"  • работа в Крыму    — https://crimea.trud.com")
    print(f"  • gorodrabot.ru     — https://gorodrabot.ru")

    print(f"\n  СОВЕТЫ ДЛЯ КРЫМА")
    print(f"  {'─'*40}")
    print(f"  • Учитывайте сезонность — летом много вакансий в туризме")
    print(f"  • Удалённая работа часто платит в 1.5-2x выше местной")
    print(f"  • Ключевые работодатели: IT, торговля, туризм, госсектор")
    print()


def main():
    parser = argparse.ArgumentParser(
        description="AI Job Search Assistant for Crimea & Simferopol",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # setup
    p_setup = sub.add_parser("setup", help="Настроить профиль соискателя")
    p_setup.add_argument("--section", help="Обновить только раздел (personal,skills,etc)")

    # profile
    sub.add_parser("profile", help="Показать текущий профиль")

    # search
    p_search = sub.add_parser("search", help="Поиск вакансий на hh.ru")
    p_search.add_argument("-q", "--query", required=True, help="Поисковый запрос")
    p_search.add_argument("-a", "--area", default="crimea", choices=["crimea", "simferopol", "sevastopol", "yalta", "evpatoriya", "kerch", "feodosiya"], help="Регион")
    p_search.add_argument("--days", type=int, default=30, help="За сколько дней")
    p_search.add_argument("--salary", help="Диапазон (30000-60000)")
    p_search.add_argument("--experience", help="Опыт: noExperience,between1And3,between3And6,moreThan6")
    p_search.add_argument("--employment", help="Тип: full,part,project,probation")
    p_search.add_argument("--with-salary", action="store_true", help="Только с з/п")
    p_search.add_argument("--sort", default="publication_time", help="Сортировка")
    p_search.add_argument("--per-page", type=int, default=20, help="Результатов")
    p_search.add_argument("--page", type=int, default=1, help="Страница")
    p_search.add_argument("--format", choices=["json", "table"], default="table", help="Формат")

    # evaluate
    p_eval = sub.add_parser("evaluate", aliases=["eval"], help="Оценить вакансию по профилю")
    p_eval.add_argument("--vacancy-id", required=True, help="ID вакансии")

    # generate-cv
    p_cv = sub.add_parser("generate-cv", aliases=["cv"], help="Сгенерировать CV из профиля")
    p_cv.add_argument("--compile", action="store_true", help="Скомпилировать в PDF")
    p_cv.add_argument("--output", "-o", help="Путь для .tex")

    # generate-letter
    p_cl = sub.add_parser("generate-letter", aliases=["letter", "cl"], help="Сгенерировать сопроводительное письмо")
    p_cl.add_argument("--vacancy", "-v", help="Название вакансии")
    p_cl.add_argument("--company", "-c", help="Название компании")
    p_cl.add_argument("--compile", action="store_true", help="Скомпилировать в PDF")
    p_cl.add_argument("--output", "-o", help="Путь для .tex")

    # salary
    p_sal = sub.add_parser("salary", help="Зарплатные ориентиры")
    p_sal.add_argument("--role", "-r", help="Название должности")
    p_sal.add_argument("--city", help="Город")
    p_sal.add_argument("--list-all", "-l", action="store_true", help="Все должности")
    p_sal.add_argument("--json", action="store_true", help="JSON вывод")

    # dashboard
    sub.add_parser("dashboard", help="Обзор рынка труда Крыма")

    args = parser.parse_args()

    commands = {
        "setup": cmd_setup,
        "profile": cmd_profile,
        "search": cmd_search,
        "evaluate": cmd_evaluate,
        "eval": cmd_evaluate,
        "generate-cv": cmd_generate_cv,
        "cv": cmd_generate_cv,
        "generate-letter": cmd_generate_letter,
        "letter": cmd_generate_letter,
        "cl": cmd_generate_letter,
        "salary": cmd_salary,
        "dashboard": cmd_dashboard,
    }

    cmd = commands.get(args.command)
    if cmd:
        cmd(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

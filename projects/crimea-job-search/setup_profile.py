#!/usr/bin/env python3
"""
setup_profile.py — Interactive profile setup for Crimean job search.

Creates candidate_profile.json with your personal and professional data
for tailored CV and cover letter generation.

Usage:
  python setup_profile.py                          # Interactive mode
  python setup_profile.py --import-cv cv.pdf       # Extract from existing CV PDF
  python setup_profile.py --show                   # Show current profile
  python setup_profile.py --section skills         # Update only skills section
"""

import json
import sys
import argparse
from pathlib import Path
from datetime import date

PROFILE_FILE = Path(__file__).parent / "candidate_profile.json"

DEFAULT_PROFILE = {
    "version": "2.0",
    "last_updated": "",
    "personal": {
        "name": "",
        "email": "",
        "phone": "",
        "city": "Симферополь",
        "region": "Крым",
        "languages": ["Русский — родной"],
        "employment_status": "",
        "linkedin": "",
        "telegram": "",
        "portfolio": "",
    },
    "education": [],
    "experience": [],
    "skills": {
        "primary": [],
        "secondary": [],
        "domain": [],
        "languages_programming": [],
        "tools": [],
        "certifications": [],
    },
    "preferences": {
        "target_roles": [],
        "target_industries": [],
        "min_salary": 0,
        "employment_types": ["full"],
        "relocation": False,
        "remote": True,
    },
    "behavioral": {
        "strengths": [],
        "growth_areas": [],
        "thrives_in": "",
        "dealbreakers": [],
    },
}


def load_profile() -> dict:
    """Load existing profile or return defaults."""
    if PROFILE_FILE.exists():
        with open(PROFILE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return dict(DEFAULT_PROFILE)


def save_profile(profile: dict):
    """Save profile to JSON file."""
    profile["last_updated"] = date.today().isoformat()
    with open(PROFILE_FILE, "w", encoding="utf-8") as f:
        json.dump(profile, f, ensure_ascii=False, indent=2)
    print(f"\n✓ Профиль сохранён: {PROFILE_FILE}")


def prompt_str(prompt: str, default: str = "") -> str:
    """Prompt for a string value."""
    if default:
        val = input(f"  {prompt} [{default}]: ").strip()
        return val if val else default
    val = input(f"  {prompt}: ").strip()
    return val


def prompt_list(prompt: str) -> list:
    """Prompt for a comma-separated list."""
    val = input(f"  {prompt} (через запятую): ").strip()
    if not val:
        return []
    return [v.strip() for v in val.split(",") if v.strip()]


def prompt_yesno(prompt: str, default: bool = True) -> bool:
    """Prompt for yes/no."""
    hint = "y/n" if default is None else ("Y/n" if default else "y/N")
    val = input(f"  {prompt} ({hint}): ").strip().lower()
    if not val:
        return default
    return val.startswith("y")


def interactive_personal(profile: dict):
    """Gather personal information."""
    print(f"\n{'='*50}")
    print("  ЛИЧНАЯ ИНФОРМАЦИЯ")
    print(f"{'='*50}")
    p = profile["personal"]
    p["name"] = prompt_str("ФИО", p.get("name", ""))
    p["email"] = prompt_str("Email", p.get("email", ""))
    p["phone"] = prompt_str("Телефон", p.get("phone", ""))
    p["city"] = prompt_str("Город", p.get("city", "Симферополь"))
    p["region"] = prompt_str("Регион", p.get("region", "Крым"))
    p["telegram"] = prompt_str("Telegram (username)", p.get("telegram", ""))
    p["portfolio"] = prompt_str("Портфолио / сайт", p.get("portfolio", ""))
    p["languages"] = prompt_list("Языки")

    langs = input("  Языки (через запятую, напр. 'Русский — родной, Английский — B2'): ").strip()
    if langs:
        p["languages"] = [l.strip() for l in langs.split(",")]


def interactive_education(profile: dict):
    """Gather education information."""
    print(f"\n{'='*50}")
    print("  ОБРАЗОВАНИЕ")
    print(f"{'='*50}")
    profile["education"] = []

    while True:
        print()
        inst = prompt_str("Учебное заведение (или Enter = закончить)")
        if not inst:
            break
        degree = prompt_str("Степень / специальность")
        year_start = prompt_str("Год начала")
        year_end = prompt_str("Год окончания (или 'н.в.')")
        profile["education"].append({
            "institution": inst,
            "degree": degree,
            "year_start": year_start,
            "year_end": year_end,
            "description": prompt_str("Описание / достижения"),
        })


def interactive_experience(profile: dict):
    """Gather work experience."""
    print(f"\n{'='*50}")
    print("  ОПЫТ РАБОТЫ")
    print(f"{'='*50}")
    profile["experience"] = []

    while True:
        print()
        title = prompt_str("Должность (или Enter = закончить)")
        if not title:
            break
        company = prompt_str("Компания")
        location = prompt_str("Расположение", "Симферополь")
        period_start = prompt_str("Месяц и год начала (напр. 'Январь 2020')")
        period_end = prompt_str("Месяц и год окончания (или 'по настоящее время')")
        print("  Достижения (каждый с новой строки, Enter = завершить):")
        achievements = []
        while True:
            ach = input("    • ")
            if not ach:
                break
            achievements.append(ach)
        profile["experience"].append({
            "title": title,
            "company": company,
            "location": location,
            "period_start": period_start,
            "period_end": period_end,
            "achievements": achievements,
        })


def interactive_skills(profile: dict):
    """Gather skills information."""
    print(f"\n{'='*50}")
    print("  НАВЫКИ")
    print(f"{'='*50}")
    s = profile["skills"]
    s["primary"] = prompt_list("Основные навыки")
    s["secondary"] = prompt_list("Дополнительные навыки")
    s["domain"] = prompt_list("Отраслевая экспертиза")
    s["languages_programming"] = prompt_list("Языки программирования")
    s["tools"] = prompt_list("Инструменты и софт")
    s["certifications"] = prompt_list("Сертификаты")


def interactive_preferences(profile: dict):
    """Gather job preferences."""
    print(f"\n{'='*50}")
    print("  ПРЕДПОЧТЕНИЯ ПО РАБОТЕ")
    print(f"{'='*50}")
    p = profile["preferences"]
    p["target_roles"] = prompt_list("Желаемые должности")
    p["target_industries"] = prompt_list("Желаемые отрасли")

    salary = prompt_str("Минимальная желаемая зарплата (₽)", str(p.get("min_salary", 0) or 0))
    p["min_salary"] = int(salary) if salary.isdigit() else p.get("min_salary", 0)

    print("  Тип занятости (выберите номера через запятую):")
    emp_options = [
        ("full", "Полная занятость"),
        ("part", "Частичная занятость"),
        ("project", "Проектная работа / фриланс"),
        ("probation", "Стажировка"),
    ]
    for i, (key, label) in enumerate(emp_options, 1):
        print(f"    {i}. {label}")
    emp_choice = input("  Выбор: ").strip()
    if emp_choice:
        indices = [int(x.strip()) for x in emp_choice.split(",") if x.strip().isdigit()]
        p["employment_types"] = [emp_options[i-1][0] for i in indices if 1 <= i <= len(emp_options)]

    p["remote"] = prompt_yesno("Готовы работать удалённо?", p.get("remote", True))
    p["relocation"] = prompt_yesno("Готовы к переезду?", p.get("relocation", False))


def interactive_behavioral(profile: dict):
    """Gather behavioral profile."""
    print(f"\n{'='*50}")
    print("  ЛИЧНЫЕ КАЧЕСТВА")
    print(f"{'='*50}")
    b = profile["behavioral"]
    b["strengths"] = prompt_list("Ваши сильные стороны")
    b["growth_areas"] = prompt_list("Зоны роста (над чем работаете)")
    b["thrives_in"] = prompt_str("В какой среде работаете лучше всего")
    b["dealbreakers"] = prompt_list("Что категорически не подходит")


def cmd_interactive(args):
    """Run the full interactive profile setup."""
    profile = load_profile()

    # Check if we should update only specific sections
    if args.section:
        sections = [s.strip() for s in args.section.split(",")]
        section_map = {
            "personal": interactive_personal,
            "education": interactive_education,
            "experience": interactive_experience,
            "skills": interactive_skills,
            "preferences": interactive_preferences,
            "behavioral": interactive_behavioral,
        }
        for sec in sections:
            if sec in section_map:
                section_map[sec](profile)
        save_profile(profile)
        return

    # Full interactive mode
    print(f"\n  ДОБРО ПОЖАЛОВАТЬ В НАСТРОЙКУ ПРОФИЛЯ")
    print(f"  AI-Job-Search для Крыма и Симферополя")
    print(f"{'='*50}")
    print()

    if any(profile.get("personal", {}).get("name")):
        print(f"  Найден существующий профиль: {profile['personal']['name']}")
        if not prompt_yesno("  Обновить профиль?", True):
            print("  Профиль не изменён.")
            return

    interactive_personal(profile)
    interactive_education(profile)
    interactive_experience(profile)
    interactive_skills(profile)
    interactive_preferences(profile)
    interactive_behavioral(profile)

    save_profile(profile)

    print(f"\n  Что дальше?")
    print(f"  • Ищите вакансии:  python hhru_crimea.py search -q \"ваша должность\"")
    print(f"  • Запустите полный: python crimea_assistant.py search")
    print(f"  • Посмотреть профиль: python setup_profile.py --show")


def cmd_show(args):
    """Display the current profile."""
    profile = load_profile()
    if not profile.get("personal", {}).get("name"):
        print("  Профиль не настроен. Запустите: python setup_profile.py")
        return
    print(json.dumps(profile, ensure_ascii=False, indent=2))


def cmd_import_cv(args):
    """Import profile from an existing CV (PDF)."""
    cv_path = Path(args.path)
    if not cv_path.exists():
        print(f"  Файл не найден: {args.path}")
        sys.exit(1)

    print(f"  Импорт из {cv_path.name}...")
    # Try to extract text from PDF
    try:
        import subprocess
        result = subprocess.run(
            ["pdftotext", str(cv_path), "-"],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0 and result.stdout.strip():
            text = result.stdout
            print(f"  Извлечено {len(text)} символов текста из PDF")
            print(f"\n  Первые 500 символов:")
            print(f"  {text[:500]}")
            print(f"\n  Ручная настройка профиля всё равно потребуется.")
            print(f"  Запустите: python setup_profile.py")
        else:
            print("  Не удалось извлечь текст из PDF. Используйте интерактивный режим.")
    except FileNotFoundError:
        print("  pdftotext не найден. Установите poppler-utils или используйте интерактивный режим.")
    except Exception as e:
        print(f"  Ошибка извлечения: {e}")


def main():
    parser = argparse.ArgumentParser(description="Настройка профиля соискателя для Крыма")
    sub = parser.add_subparsers(dest="command", required=True)

    p_interactive = sub.add_parser("interactive", aliases=["i", "setup"], help="Интерактивная настройка")
    p_interactive.add_argument("--section", help="Обновить только раздел (через запятую): personal,education,experience,skills,preferences,behavioral")

    p_show = sub.add_parser("show", aliases=["view"], help="Показать профиль")
    
    p_import = sub.add_parser("import", aliases=["import-cv"], help="Импорт из PDF CV")
    p_import.add_argument("path", help="Путь к PDF файлу с резюме")

    args = parser.parse_args()

    if args.command in ("interactive", "i", "setup"):
        cmd_interactive(args)
    elif args.command in ("show", "view"):
        cmd_show(args)
    elif args.command in ("import", "import-cv"):
        cmd_import_cv(args)


if __name__ == "__main__":
    main()

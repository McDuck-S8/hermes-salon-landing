#!/usr/bin/env python3
"""
fill_cv.py — Fill LaTeX CV template from candidate_profile.json.

Usage:
  python fill_cv.py                         # Fill CV template
  python fill_cv.py --type cover-letter     # Fill cover letter template
  python fill_cv.py --output my_cv.tex      # Custom output path
  python fill_cv.py --compile               # Also compile to PDF (requires xelatex)
"""

import json
import sys
import re
import subprocess
import argparse
from pathlib import Path

PROJECT_DIR = Path(__file__).parent
PROFILE_FILE = PROJECT_DIR / "candidate_profile.json"
CV_TEMPLATE = PROJECT_DIR / "cv" / "template.tex"
CL_TEMPLATE = PROJECT_DIR / "cover_letters" / "template.tex"
CV_OUTPUT = PROJECT_DIR / "cv" / "output.tex"
CL_OUTPUT = PROJECT_DIR / "cover_letters" / "output.tex"


def load_profile() -> dict:
    """Load candidate profile from JSON."""
    if not PROFILE_FILE.exists():
        print(f"  Профиль не найден: {PROFILE_FILE}")
        print(f"  Сначала выполните: python setup_profile.py")
        sys.exit(1)
    with open(PROFILE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def escape_latex(text: str) -> str:
    """Escape special LaTeX characters."""
    chars = {
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\^{}",
    }
    result = str(text)
    for char, escaped in chars.items():
        result = result.replace(char, escaped)
    return result


def fill_cv(profile: dict, output_path: Path):
    """Fill the CV template with profile data."""
    if not CV_TEMPLATE.exists():
        print(f"  Шаблон CV не найден: {CV_TEMPLATE}")
        sys.exit(1)

    with open(CV_TEMPLATE, "r", encoding="utf-8") as f:
        tex = f.read()

    p = profile.get("personal", {})
    prefs = profile.get("preferences", {})
    skills = profile.get("skills", {})
    experience = profile.get("experience", [])
    education = profile.get("education", [])

    name = escape_latex(p.get("name", "ИМЯ ФАМИЛИЯ"))
    email = escape_latex(p.get("email", "email@example.com"))
    phone = escape_latex(p.get("phone", "+7 (___) ___-__-__"))
    telegram = escape_latex(p.get("telegram", ""))
    portfolio = escape_latex(p.get("portfolio", ""))

    # Target role
    roles = prefs.get("target_roles", [])
    target_role = escape_latex(roles[0] if roles else "Желаемая должность")

    # Replace header fields
    tex = tex.replace("{ИМЯ ФАМИЛИЯ}", name)
    tex = tex.replace("{email@example.com}", email)
    tex = tex.replace("{+7 (___) ___-__-__}", phone)
    tex = tex.replace("{Желаемая должность}", target_role)

    # Optional link
    link = telegram or portfolio or ""
    tex = tex.replace(
        r"\ifx&#5&\else\hspace{1em}\faSymbol{link} #5\fi",
        f"{{{{\\normalsize\\color{{cvgray}} {link}}}}}" if link else ""
    )

    # Skills
    all_skills = []
    if skills.get("primary"):
        all_skills.extend(skills["primary"])
    if skills.get("programming_languages"):
        all_skills.extend(skills["programming_languages"])
    if skills.get("tools"):
        all_skills.extend(skills["tools"])
    skill_text = ", ".join(escape_latex(s) for s in all_skills[:12])
    tex = tex.replace("{Навык 1, Навык 2, Навык 3, Навык 4, Навык 5, Навык 6}", skill_text)

    # About me
    strengths = profile.get("behavioral", {}).get("strengths", [])
    about = f"Специалист из {escape_latex(p.get('city', 'Симферополь'))}, {escape_latex(p.get('region', 'Крым'))}."
    if roles:
        about += f" Ищу работу в качестве {target_role}."
    if strengths:
        about += f" Сильные стороны: {', '.join(escape_latex(s) for s in strengths[:3])}."
    tex = tex.replace(
        "Краткое описание вашего профессионального профиля, ключевых достижений и карьерных целей. 2–3 предложения, которые сразу показывают вашу ценность для работодателя.",
        about
    )

    # Experience section
    if experience:
        exp_entries = []
        for exp in experience:
            title = escape_latex(exp.get("title", "Должность"))
            company = escape_latex(exp.get("company", "Компания"))
            location = escape_latex(exp.get("location", "Симферополь"))
            period = f"{escape_latex(exp.get('period_start', ''))} — {escape_latex(exp.get('period_end', ''))}"
            achievements = exp.get("achievements", [])
            ach_items = "\n".join(
                f"  \\item {escape_latex(a)}" for a in achievements
            ) if achievements else "  \\item Достижение не указано"

            entry = f"""\\begin{{jobentry}}
  {{{title}}}
  {{{company}}}
  {{{location}}}
  {{{period}}}
{ach_items}
\\end{{jobentry}}"""
            exp_entries.append(entry)

        # Replace the sample experience block
        tex = re.sub(
            r"\\begin\{jobentry\}.*?\\end\{jobentry\}\s*\\n*\\begin\{jobentry\}.*?\\end\{jobentry\}",
            "\n".join(exp_entries),
            tex,
            flags=re.DOTALL
        )

    # Education section
    if education:
        edu_entries = []
        for edu in education:
            inst = escape_latex(edu.get("institution", "Название"))
            degree = escape_latex(edu.get("degree", "Степень"))
            year_start = escape_latex(edu.get("year_start", ""))
            year_end = escape_latex(edu.get("year_end", ""))
            entry = f"\\edentry{{{inst}}}{{{degree}}}{{{year_start}}}{{{year_end}}}"
            edu_entries.append(entry)
        tex = re.sub(
            r"\\edentry\{Название.*?\\edentry\{Название.*?\}",
            "\n".join(edu_entries),
            tex,
            flags=re.DOTALL
        )

    # Certifications
    certs = skills.get("certifications", [])
    if certs:
        cert_entries = "\n".join("  \\certentry{" + escape_latex(c) + "}{}" for c in certs)
        tex = re.sub(
            r"\\certentry\{Название сертификата\}.*?\\certentry\{Название курса\}",
            cert_entries,
            tex,
            flags=re.DOTALL
        )

    # Additional info
    extra_items = []
    employment_types = prefs.get("employment_types", [])
    emp_map = {"full": "Полная занятость", "part": "Частичная", "project": "Проектная работа", "probation": "Стажировка"}
    emp_labels = [emp_map.get(e, e) for e in employment_types]
    extra_items.append(f"  \\item Тип занятости: {', '.join(emp_labels)}")

    if prefs.get("remote"):
        extra_items.append(r"  \item Удалённая работа: да")
    if prefs.get("relocation"):
        extra_items.append(r"  \item Готовность к переезду: да")

    languages = p.get("languages", [])
    if languages:
        extra_items.append(f"  \\item Языки: {', '.join(escape_latex(l) for l in languages)}")

    tex = tex.replace(
        "\\item Готовность к командировкам: да / нет\n  \\item Готовность к переезду: да / нет\n  \\item Водительские права: категория B",
        "\n".join(extra_items)
    )

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(tex)
    print(f"  ✓ CV сохранён: {output_path}")


def fill_cover_letter(profile: dict, output_path: Path, vacancy_title: str = "", company: str = ""):
    """Fill the cover letter template with profile data."""
    if not CL_TEMPLATE.exists():
        print(f"  Шаблон письма не найден: {CL_TEMPLATE}")
        sys.exit(1)

    with open(CL_TEMPLATE, "r", encoding="utf-8") as f:
        tex = f.read()

    p = profile.get("personal", {})
    name = escape_latex(p.get("name", "ИМЯ ФАМИЛИЯ"))
    email = escape_latex(p.get("email", "email@example.com"))
    phone = escape_latex(p.get("phone", "+7 (___) ___-__-__"))

    tex = tex.replace("ИМЯ ФАМИЛИЯ", name)
    tex = tex.replace("email@example.com", email)
    tex = tex.replace("{+7 (___) ___-__-__}", phone)

    if vacancy_title:
        tex = tex.replace("[НАЗВАНИЕ ВАКАНСИИ]", escape_latex(vacancy_title))
    if company:
        tex = tex.replace("Название компании", escape_latex(company))
        tex = tex.replace("[НАЗВАНИЕ КОМПАНИИ]", escape_latex(company))

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(tex)
    print(f"  ✓ Сопроводительное письмо сохранено: {output_path}")


def compile_pdf(tex_path: Path):
    """Compile LaTeX to PDF if xelatex is available."""
    try:
        result = subprocess.run(
            ["xelatex", "-interaction=nonstopmode", "-output-directory", str(tex_path.parent), str(tex_path)],
            capture_output=True, text=True, timeout=60
        )
        pdf_path = tex_path.with_suffix(".pdf")
        if pdf_path.exists():
            print(f"  ✓ PDF сгенерирован: {pdf_path}")
            return
        # Check log for errors
        log_path = tex_path.with_suffix(".log")
        if log_path.exists():
            errors = [l for l in result.stdout.split("\n") if "Error" in l][:5]
            if errors:
                print(f"  ✗ Ошибки компиляции LaTeX:")
                for e in errors:
                    print(f"    {e[:100]}")
            else:
                print(f"  ✗ Неизвестная ошибка компиляции. Смотрите {log_path}")
        else:
            print(f"  ✗ xelatex не найден. Установите TeX Live или используйте Overleaf.")
    except FileNotFoundError:
        print(f"  ! xelatex не установлен. Для компиляции установите TeX Live (https://tug.org/texlive/)")
    except subprocess.TimeoutExpired:
        print(f"  ! Компиляция LaTeX превысила 60 сек")
    except Exception as e:
        print(f"  ! Ошибка компиляции: {e}")


def main():
    parser = argparse.ArgumentParser(description="Заполнение шаблонов CV из профиля")
    parser.add_argument("--type", "-t", choices=["cv", "cover-letter"], default="cv",
                        help="Тип документа (по умолчанию: cv)")
    parser.add_argument("--output", "-o", help="Путь для сохранения .tex файла")
    parser.add_argument("--compile", "-c", action="store_true", help="Скомпилировать в PDF")
    parser.add_argument("--vacancy", "-v", help="Название вакансии (для сопроводительного письма)")
    parser.add_argument("--company", help="Название компании (для сопроводительного письма)")

    args = parser.parse_args()
    profile = load_profile()

    if args.type == "cv":
        output = Path(args.output) if args.output else CV_OUTPUT
        fill_cv(profile, output)
        if args.compile:
            compile_pdf(output)
    else:
        output = Path(args.output) if args.output else CL_OUTPUT
        fill_cover_letter(profile, output, args.vacancy or "", args.company or "")
        if args.compile:
            compile_pdf(output)

    print(f"\n  Готово! Посмотреть результат можно в {output}")


if __name__ == "__main__":
    main()

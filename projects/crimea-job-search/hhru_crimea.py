#!/usr/bin/env python3
"""
hhru_crimea.py — CLI for searching job vacancies on hh.ru in Crimea and Simferopol.

Usage:
  python hhru_crimea.py search --query "python" --area simferopol
  python hhru_crimea.py search -q "водитель" -a crimea --days 7 --format table
  python hhru_crimea.py detail 12345678
  python hhru_crimea.py areas
  python hhru_crimea.py search -q "продавец" -a crimea --salary 30000-60000

Uses the public hh.ru API (no auth key required for search within Russia/Crimea).
"""

import json
import sys
import argparse
import urllib.request
import urllib.parse
import urllib.error
import ssl
from datetime import datetime, timezone
from pathlib import Path

API_BASE = "https://api.hh.ru"

# Crimean area IDs from hh.ru directory
AREAS = {
    "crimea": 2114,       # Республика Крым
    "simferopol": 131,    # Симферополь
    "sevastopol": 130,    # Севастополь
    "yalta": 2120,        # Ялта
    "evpatoriya": 2115,   # Евпатория
    "kerch": 2116,        # Керчь
    "feodosiya": 2119,    # Феодосия
}

# Employment types
EMPLOYMENT = {
    "full": "Полная занятость",
    "part": "Частичная занятость",
    "project": "Проектная работа",
    "volunteer": "Волонтёрство",
    "probation": "Стажировка",
}

# Experience mapping
EXPERIENCE = {
    "noExperience": "Нет опыта",
    "between1And3": "От 1 года до 3 лет",
    "between3And6": "От 3 до 6 лет",
    "moreThan6": "Более 6 лет",
}


def api_request(path: str, params: dict = None) -> dict:
    """Make a request to the hh.ru API with proper headers."""
    url = f"{API_BASE}{path}"
    if params:
        url += "?" + urllib.parse.urlencode(params, doseq=True)

    ctx = ssl.create_default_context()
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "HH-User-Agent/1.0 (crimea-job-search; job-search@example.com)",
            "Accept": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=15) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        try:
            err_data = json.loads(body)
            desc = err_data.get("description", err_data.get("errors", [{}])[0].get("value", str(e)))
        except (json.JSONDecodeError, IndexError, KeyError):
            desc = body[:200]
        print(f"API Error {e.code}: {desc}", file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"Network error: {e.reason}", file=sys.stderr)
        print("Note: hh.ru API may be geo-blocked outside Russia.", file=sys.stderr)
        sys.exit(1)


def cmd_search(args):
    """Search for vacancies in Crimea."""
    area_id = AREAS.get(args.area)
    if not area_id:
        print(f"Unknown area '{args.area}'. Available: {', '.join(AREAS.keys())}", file=sys.stderr)
        sys.exit(1)

    params = {
        "area": area_id,
        "per_page": min(args.per_page, 100),
        "page": max(0, args.page - 1),
        "order_by": args.sort or "publication_time",
        "only_with_salary": str(args.with_salary).lower(),
        "period": args.days or 30,
        "clusters": "true",
    }

    if args.query:
        params["text"] = args.query
        params["search_field"] = "name"

    if args.experience:
        params["experience"] = args.experience

    if args.employment:
        params["employment"] = args.employment

    if args.salary:
        salary_parts = args.salary.replace(" ", "").split("-")
        if len(salary_parts) >= 1:
            params["salary_from"] = salary_parts[0]
        if len(salary_parts) >= 2:
            params["salary_to"] = salary_parts[1]

    data = api_request("/vacancies", params)
    items = data.get("items", [])
    found = data.get("found", 0)
    pages = data.get("pages", 1)

    if args.format == "json":
        output = {
            "meta": {"found": found, "page": args.page, "pages": pages},
            "results": items,
        }
        print(json.dumps(output, ensure_ascii=False, indent=2))
        return

    if not items:
        print(f"Ничего не найдено по запросу '{args.query or 'все'}' в {AREA_NAMES.get(args.area, args.area)}")
        return

    # Print vacancy count
    print(f"\n  Найдено вакансий: {found}")
    print(f"  Страница {args.page} из {pages}\n")

    for item in items:
        salary = format_salary(item.get("salary"))
        employer = item.get("employer", {}).get("name", "—")
        city = item.get("area", {}).get("name", "")
        published = item.get("published_at", "")
        if published:
            try:
                dt = datetime.fromisoformat(published)
                published = dt.strftime("%d.%m.%Y")
            except ValueError:
                published = published[:10]

        print(f"  [{item['id']}] {item['name']}")
        print(f"       {employer} | {city} | {salary}")
        print(f"       Опубликовано: {published}")
        url = item.get("alternate_url", "")
        if url:
            print(f"       {url}")
        print()


def cmd_detail(args):
    """Get full details of a specific vacancy."""
    data = api_request(f"/vacancies/{args.vacancy_id}")

    if args.format == "json":
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return

    salary = format_salary(data.get("salary"))
    employer = data.get("employer", {}).get("name", "—")
    area = data.get("area", {}).get("name", "—")
    experience = EXPERIENCE.get(data.get("experience", {}).get("id", ""), data.get("experience", {}).get("name", "—"))
    employment = EMPLOYMENT.get(data.get("employment", {}).get("id", ""), data.get("employment", {}).get("name", "—"))

    print(f"\n{'='*60}")
    print(f"  {data['name']}")
    print(f"{'='*60}")
    print(f"  Компания:    {employer}")
    print(f"  Расположение: {area}")
    print(f"  Зарплата:    {salary}")
    print(f"  Опыт:        {experience}")
    print(f"  Занятость:   {employment}")
    if data.get("schedule"):
        print(f"  График:      {data['schedule'].get('name', '—')}")

    desc = data.get("description", "")
    if desc:
        # Strip HTML tags for plain text view
        import re
        desc = re.sub(r"<[^>]+>", "", desc)
        desc = re.sub(r"\n{3,}", "\n\n", desc).strip()
        print(f"\n{'─'*60}")
        print(f"  ОПИСАНИЕ:")
        print(f"{'─'*60}")
        print(f"  {desc[:3000]}")
        if len(desc) > 3000:
            print(f"\n  ... (описание сокращено, всего {len(desc)} символов)")

    url = data.get("alternate_url", "")
    if url:
        print(f"\n  Ссылка: {url}")

    if data.get("key_skills"):
        skills = [s["name"] for s in data["key_skills"]]
        print(f"\n  Ключевые навыки: {', '.join(skills)}")
    print()


def cmd_areas(args):
    """List all areas within Crimea."""
    data = api_request("/areas/113")  # Russia
    for region in data.get("areas", []):
        if region["id"] == "2114":
            print(f"\n  Регион: {region['name']} (id={region['id']})")
            print(f"  {'─'*40}")
            for city in region.get("areas", []):
                print(f"    {city['name']:30s} id={city['id']}")
            print()
            break


def cmd_suggest(args):
    """Suggest areas matching a query."""
    data = api_request("/suggests/areas", {"text": args.query})
    for item in data.get("items", []):
        print(f"  {item['text']:40s} id={item['id']}")


def format_salary(salary_data):
    """Format salary data for display."""
    if not salary_data:
        return "з/п не указана"
    fr = salary_data.get("from")
    to = salary_data.get("to")
    currency = salary_data.get("currency", "RUR")
    gross = "до вычета" if salary_data.get("gross") else "на руки"

    currency_symbols = {"RUR": "₽", "USD": "$", "EUR": "€"}
    sym = currency_symbols.get(currency, currency)

    if fr and to:
        return f"от {fr:,} до {to:,} {sym} ({gross})".replace(",", " ")
    elif fr:
        return f"от {fr:,} {sym} ({gross})".replace(",", " ")
    elif to:
        return f"до {to:,} {sym} ({gross})".replace(",", " ")
    return "з/п не указана"


AREA_NAMES = {
    2114: "Крым",
    131: "Симферополь",
    130: "Севастополь",
    2120: "Ялта",
    2115: "Евпатория",
    2116: "Керчь",
    2119: "Феодосия",
}


def main():
    parser = argparse.ArgumentParser(
        description="Поиск вакансий на hh.ru в Крыму и Симферополе",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры:
  python hhru_crimea.py search -q "python" -a simferopol
  python hhru_crimea.py search -q "водитель" -a crimea --days 7 --format table
  python hhru_crimea.py search -q "продавец" -a crimea --salary 30000-60000
  python hhru_crimea.py detail 12345678
  python hhru_crimea.py areas
        """,
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # search command
    p_search = sub.add_parser("search", help="Поиск вакансий")
    p_search.add_argument("-q", "--query", help="Ключевые слова для поиска")
    p_search.add_argument(
        "-a", "--area", default="crimea",
        choices=list(AREAS.keys()),
        help="Регион поиска (по умолчанию: crimea — весь Крым)",
    )
    p_search.add_argument("--days", type=int, default=30, help="За сколько дней (по умолчанию: 30)")
    p_search.add_argument("--salary", help="Диапазон зарплаты, например 30000-60000")
    p_search.add_argument("--experience", choices=list(EXPERIENCE.keys()), help="Опыт работы")
    p_search.add_argument("--employment", choices=list(EMPLOYMENT.keys()), help="Тип занятости")
    p_search.add_argument("--with-salary", action="store_true", help="Только с указанной зарплатой")
    p_search.add_argument("--sort", choices=["publication_time", "salary_desc", "salary_asc", "relevance"],
                          default="publication_time", help="Сортировка")
    p_search.add_argument("--page", type=int, default=1, help="Номер страницы")
    p_search.add_argument("--per-page", type=int, default=15, help="Результатов на странице")
    p_search.add_argument("--format", choices=["json", "table"], default="table", help="Формат вывода")

    # detail command
    p_detail = sub.add_parser("detail", help="Детальная информация о вакансии")
    p_detail.add_argument("vacancy_id", help="ID вакансии")
    p_detail.add_argument("--format", choices=["json", "plain"], default="plain", help="Формат вывода")

    # areas command
    p_areas = sub.add_parser("areas", help="Список городов Крыма")
    p_areas.add_argument("--format", choices=["json", "table"], default="table")

    # suggest command
    p_suggest = sub.add_parser("suggest", help="Поиск региона по названию")
    p_suggest.add_argument("query", help="Название региона")

    args = parser.parse_args()

    if args.command == "search":
        cmd_search(args)
    elif args.command == "detail":
        cmd_detail(args)
    elif args.command == "areas":
        cmd_areas(args)
    elif args.command == "suggest":
        cmd_suggest(args)


if __name__ == "__main__":
    main()

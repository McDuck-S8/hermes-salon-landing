#!/usr/bin/env python3
"""
Telegram Daily Report — ежедневный отчёт о работе автономной системы.
Считает запуски за сегодня, ошибки, статистику Knowledge Cube и verified fixes.
Форматирует чистый отчёт на русском языке и выводит в stdout (для cron no_agent=true).
При запуске вручную также может отправить в Telegram через telegram_bridge.

Usage (standalone):
    python telegram_daily_report.py
    python telegram_daily_report.py --send
    python telegram_daily_report.py --send --chat-id 737433175
"""

import argparse
import glob
import json
import os
import sqlite3
import sys
from datetime import datetime, date
from pathlib import Path

HERMES_HOME = Path(os.environ.get("HERMES_HOME", str(Path(__file__).resolve().parent.parent)))
SCRIPTS_DIR = HERMES_HOME / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

CRON_OUTPUT = HERMES_HOME / "cron" / "output"
CRON_JOBS_JSON = HERMES_HOME / "cron" / "jobs.json"
KNOWLEDGE_CUBE_DB = HERMES_HOME / "cache" / "knowledge_cube.db"
VERIFIED_FIXES_DB = HERMES_HOME / "cache" / "verified_fixes.db"


def load_job_names():
    """Читает jobs.json и возвращает dict {job_id: job_name}."""
    if not CRON_JOBS_JSON.exists():
        return {}
    try:
        with open(CRON_JOBS_JSON, "r", encoding="utf-8") as f:
            data = json.load(f)
        return {j["id"]: j.get("name", j["id"][:8]) for j in data.get("jobs", [])}
    except Exception:
        return {}


def get_today_str():
    """Возвращает строку даты сегодня в формате YYYY-MM-DD."""
    return date.today().strftime("%Y-%m-%d")


def scan_cron_output(today_str):
    """
    Сканирует cron/output/ и собирает статистику за сегодня.
    Возвращает dict:
      {
        "total_runs": int,
        "jobs_run": {job_name: run_count},
        "first_run": str,
        "last_run": str,
        "job_ids_today": [job_id, ...],
      }
    """
    if not CRON_OUTPUT.exists():
        return {
            "total_runs": 0,
            "jobs_run": {},
            "first_run": "—",
            "last_run": "—",
            "job_ids_today": [],
        }

    job_names = load_job_names()
    today_prefix = today_str + "_"
    jobs_run = {}
    all_times = []
    job_ids_today = set()

    for job_dir in sorted(CRON_OUTPUT.iterdir()):
        if not job_dir.is_dir():
            continue
        job_id = job_dir.name
        for md_file in job_dir.glob("*.md"):
            fname = md_file.name
            if not fname.startswith(today_prefix):
                continue
            job_ids_today.add(job_id)
            job_name = job_names.get(job_id, job_id[:8])
            jobs_run[job_name] = jobs_run.get(job_name, 0) + 1

            # Extract time from filename: YYYY-MM-DD_HH-MM-SS.md
            time_part = fname.replace(today_prefix, "").replace(".md", "").replace("-", ":", 2)
            all_times.append(time_part)

    all_times.sort()
    total = sum(jobs_run.values())

    return {
        "total_runs": total,
        "jobs_run": dict(sorted(jobs_run.items(), key=lambda x: -x[1])),
        "first_run": all_times[0] if all_times else "—",
        "last_run": all_times[-1] if all_times else "—",
        "job_ids_today": sorted(job_ids_today),
    }


def get_knowledge_cube_stats():
    """Читает статистику из knowledge_cube.db."""
    if not KNOWLEDGE_CUBE_DB.exists():
        return None
    try:
        conn = sqlite3.connect(str(KNOWLEDGE_CUBE_DB))
        cursor = conn.cursor()

        # Total experiences
        cursor.execute("SELECT COUNT(*) FROM experiences")
        total = cursor.fetchone()[0]

        # By domain
        cursor.execute(
            "SELECT axis_domain, COUNT(*) FROM experiences "
            "GROUP BY axis_domain ORDER BY COUNT(*) DESC"
        )
        domains = cursor.fetchall()

        # Recent today
        cursor.execute(
            "SELECT COUNT(*) FROM experiences WHERE date(ts) = date('now', 'localtime')"
        )
        added_today = cursor.fetchone()[0]

        conn.close()
        return {
            "total": total,
            "domains": domains,
            "added_today": added_today,
        }
    except Exception:
        return None


def get_verified_fixes_stats():
    """Читает статистику из verified_fixes.db."""
    if not VERIFIED_FIXES_DB.exists():
        return None
    try:
        conn = sqlite3.connect(str(VERIFIED_FIXES_DB))
        cursor = conn.cursor()

        # Total fixes
        cursor.execute("SELECT COUNT(*) FROM verified_fixes")
        total = cursor.fetchone()[0]

        # By issue type
        cursor.execute(
            "SELECT issue_type, COUNT(*) FROM verified_fixes "
            "GROUP BY issue_type ORDER BY COUNT(*) DESC LIMIT 10"
        )
        types = cursor.fetchall()

        # Recent today
        cursor.execute(
            "SELECT COUNT(*) FROM verified_fixes WHERE date(verified_at) = date('now', 'localtime')"
        )
        fixed_today = cursor.fetchone()[0]

        conn.close()
        return {
            "total": total,
            "types": types,
            "fixed_today": fixed_today,
        }
    except Exception:
        return None


def format_report(today_str, cron_stats, cube_stats, fixes_stats):
    """Форматирует чистый текстовый отчёт на русском языке."""
    lines = []

    # Header
    lines.append(f"Ежедневный отчёт системы Hermes")
    lines.append(f"Дата: {today_str}")
    lines.append(f"Время отчёта: {datetime.now().strftime('%H:%M:%S')}")
    lines.append("")

    # === Cron Jobs Section ===
    lines.append("=== Активность cron-задач ===")
    lines.append(f"Всего запусков сегодня: {cron_stats['total_runs']}")
    lines.append(f"Уникальных задач: {len(cron_stats['jobs_run'])}")

    if cron_stats['first_run'] != "—":
        lines.append(f"Первый запуск: {cron_stats['first_run']}")
        lines.append(f"Последний запуск: {cron_stats['last_run']}")

    if cron_stats['jobs_run']:
        lines.append("")
        lines.append("Задачи (по количеству запусков):")
        for jname, count in list(cron_stats['jobs_run'].items())[:15]:
            bar = "#" * min(count, 30)
            lines.append(f"  {jname}: {count}x {bar}")

    # Count unique jobs that ran
    unique_jobs = len(cron_stats['jobs_run'])
    lines.append(f"\nАктивных задач сегодня: {unique_jobs}")

    # === Knowledge Cube Section ===
    lines.append("")
    lines.append("=== Knowledge Cube ===")
    if cube_stats:
        lines.append(f"Всего записей: {cube_stats['total']}")
        lines.append(f"Добавлено сегодня: {cube_stats['added_today']}")
        if cube_stats['domains']:
            lines.append("")
            lines.append("Домены (топ-10):")
            for domain, count in cube_stats['domains'][:10]:
                lines.append(f"  {domain}: {count}")
    else:
        lines.append("База недоступна")

    # === Verified Fixes Section ===
    lines.append("")
    lines.append("=== Исправления (verified fixes) ===")
    if fixes_stats:
        lines.append(f"Всего исправлений: {fixes_stats['total']}")
        lines.append(f"Исправлено сегодня: {fixes_stats['fixed_today']}")
        if fixes_stats['types']:
            lines.append("")
            lines.append("Типы проблем:")
            for itype, count in fixes_stats['types'][:10]:
                lines.append(f"  {itype}: {count}")
    else:
        lines.append("База недоступна")

    # === Summary ===
    lines.append("")
    lines.append("=== Итого ===")
    lines.append(f"Cron запусков: {cron_stats['total_runs']}")
    cube_total = cube_stats['total'] if cube_stats else "—"
    cube_new = cube_stats['added_today'] if cube_stats else 0
    fixes_total = fixes_stats['total'] if fixes_stats else "—"
    fixes_new = fixes_stats['fixed_today'] if fixes_stats else 0
    lines.append(f"Knowledge Cube: {cube_total} (+{cube_new} сегодня)")
    lines.append(f"Verified Fixes: {fixes_total} (+{fixes_new} сегодня)")

    # Status emoji
    if cron_stats['total_runs'] > 0:
        lines.append(f"\nСтатус: Система работает нормально")
    else:
        lines.append(f"\nСтатус: Нет запусков за сегодня")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Ежедневный отчёт Hermes в Telegram")
    parser.add_argument("--send", action="store_true", help="Отправить отчёт в Telegram")
    parser.add_argument("--chat-id", help="Chat ID для отправки (по умолчанию из channel_directory.json)")
    parser.add_argument("--date", help="Дата для отчёта (YYYY-MM-DD, по умолчанию сегодня)")
    parser.add_argument("--json", action="store_true", help="Вывести статистику в JSON")
    args = parser.parse_args()

    today_str = args.date or get_today_str()

    # Collect data
    cron_stats = scan_cron_output(today_str)
    cube_stats = get_knowledge_cube_stats()
    fixes_stats = get_verified_fixes_stats()

    # Format report
    report = format_report(today_str, cron_stats, cube_stats, fixes_stats)

    if args.json:
        # JSON output for programmatic use
        output = {
            "date": today_str,
            "cron": cron_stats,
            "knowledge_cube": cube_stats,
            "verified_fixes": fixes_stats,
        }
        print(json.dumps(output, ensure_ascii=False, indent=2))
    else:
        # Plain text report (for stdout delivery by cron)
        print(report)

    # Optionally send to Telegram (standalone mode)
    if args.send:
        try:
            from telegram_bridge import send_telegram_message, _load_env_if_missing
            _load_env_if_missing()

            chat_id = args.chat_id
            if not chat_id:
                # Try channel_directory.json
                chan_path = HERMES_HOME / "channel_directory.json"
                if chan_path.exists():
                    with open(chan_path, "r", encoding="utf-8") as f:
                        cd = json.load(f)
                    tg_channels = cd.get("platforms", {}).get("telegram", [])
                    if tg_channels:
                        chat_id = tg_channels[0].get("id")
                if not chat_id:
                    chat_id = os.environ.get("CHAT_ID", "737433175")

            send_telegram_message(text=report, chat_id=chat_id)
            print(f"\n[OK] Отчёт отправлен в чат {chat_id}")
        except Exception as e:
            print(f"\n[ERROR] Не удалось отправить: {e}", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()

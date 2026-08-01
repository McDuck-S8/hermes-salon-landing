#!/usr/bin/env python3
"""
Telegram Delivery Report — собирает результаты cron задач и отправляет в Telegram.
Формирует сводку из последних файлов cron/output/<job_id>/ и вызывает telegram_bridge.py.

Исправлено: CHAT_ID теперь читается из нескольких источников:
  1. --chat-id аргумент CLI
  2. CHAT_ID переменная окружения
  3. config.yaml (telegram.home_chat или telegram раздел)
  4. channel_directory.json (первый telegram канал)
  5. Fallback: @max_brain_chef_official
"""

import argparse
import glob
import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Добавляем scripts в sys.path для импорта telegram_bridge
HERMES_HOME = Path(os.environ.get("HERMES_HOME", str(Path(__file__).resolve().parent.parent)))
SCRIPTS_DIR = os.path.join(HERMES_HOME, "scripts")
sys.path.insert(0, SCRIPTS_DIR)

from telegram_bridge import send_telegram_message, _load_env_if_missing

CRON_OUTPUT = os.path.join(HERMES_HOME, "cron", "output")

# Карта job_id -> имя задачи (из hermes cron list)
JOB_NAMES = {
    "1d9a0647dd29": "unified-system-cycle",
    "5c1bb0103221": "nightly-self-analysis",
    "c26bc0ba908a": "subconscious-loop",
    "772ad3dd931b": "auto-fetch-sessions",
    "2ca6725a4263": "update-runtime-context",
    "74382ce129b9": "dream-memory-consolidation",
    "a0ee2153b147": "morning-report",
    "71398874ad31": "event-trigger",
    "c13c99b28615": "system-watcher",
}


def resolve_chat_id(cli_chat_id=None):
    """
    Определяет chat_id для отправки сообщений.
    Порядок приоритета:
      1. --chat-id аргумент CLI
      2. CHAT_ID переменная окружения
      3. config.yaml → telegram.home_chat
      4. channel_directory.json → первый telegram.chat.id
      5. Fallback: @max_brain_chef_official
    """
    # Сначала загружаем .env чтобы CHAT_ID был доступен
    _load_env_if_missing()

    # 1. CLI аргумент
    if cli_chat_id:
        return cli_chat_id

    # 2. Переменная окружения
    env_chat = os.environ.get("CHAT_ID")
    if env_chat:
        return env_chat

    # 3. config.yaml
    config_path = os.path.join(HERMES_HOME, "config.yaml")
    if os.path.isfile(config_path):
        try:
            import yaml
            with open(config_path, "r", encoding="utf-8") as f:
                cfg = yaml.safe_load(f)
            if cfg:
                # Прямой ключ
                if "telegram" in cfg and isinstance(cfg["telegram"], dict):
                    tg = cfg["telegram"]
                    if "home_chat" in tg and tg["home_chat"]:
                        return str(tg["home_chat"])
                    if "chat_id" in tg and tg["chat_id"]:
                        return str(tg["chat_id"])
                    if "allowed_chats" in tg and tg["allowed_chats"]:
                        return str(tg["allowed_chats"]).split(",")[0].strip()
                # display.platforms.telegram.home_chat
                if "display" in cfg and isinstance(cfg["display"], dict):
                    display = cfg["display"]
                    if "platforms" in display and isinstance(display["platforms"], dict):
                        tg_plat = display["platforms"].get("telegram", {})
                        if isinstance(tg_plat, dict) and "home_chat" in tg_plat and tg_plat["home_chat"]:
                            return str(tg_plat["home_chat"])
        except ImportError:
            pass  # yaml not installed, skip
        except Exception:
            pass

    # 4. channel_directory.json
    chan_dir = os.path.join(HERMES_HOME, "channel_directory.json")
    if os.path.isfile(chan_dir):
        try:
            with open(chan_dir, "r", encoding="utf-8") as f:
                cd = json.load(f)
            platforms = cd.get("platforms", {})
            tg_channels = platforms.get("telegram", [])
            if tg_channels and len(tg_channels) > 0:
                cid = tg_channels[0].get("id")
                if cid:
                    return str(cid)
        except Exception:
            pass

    # 5. Fallback по умолчанию
    return "@max_brain_chef_official"


def resolve_token(cli_token=None):
    """
    Определяет Telegram Bot API токен.
    Порядок приоритета:
      1. --token аргумент CLI
      2. TELEGRAM_BOT_TOKEN переменная окружения
      3. Загрузка из .env (через _load_env_if_missing)
    """
    if cli_token:
        return cli_token

    # Сначала пробуем загрузить .env, если TELEGRAM_BOT_TOKEN не установлен
    _load_env_if_missing()

    env_token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if env_token:
        return env_token

    return None


def get_latest_output(job_id):
    """Читает последний файл .md из cron/output/<job_id>/"""
    job_dir = os.path.join(CRON_OUTPUT, job_id)
    if not os.path.isdir(job_dir):
        return None, None

    md_files = sorted(glob.glob(os.path.join(job_dir, "*.md")), reverse=True)
    if not md_files:
        return None, None

    latest = md_files[0]
    with open(latest, "r", encoding="utf-8", errors="replace") as f:
        content = f.read()
    return latest, content


def extract_summary(content, max_lines=15):
    """Извлекает краткую сводку из содержимого отчёта"""
    lines = content.strip().split("\n")
    # Пропускаем преамбулу с # Title и Job ID
    summary_lines = []
    started = False
    for line in lines:
        stripped = line.strip()
        # Начинаем сбор после разделителя ---
        if stripped == "---":
            started = True
            continue
        if started:
            summary_lines.append(line)
            if len(summary_lines) >= max_lines:
                break

    if not summary_lines:
        # Если разделителя нет — берём первые строки без заголовков
        summary_lines = [l for l in lines if l.strip() and not l.strip().startswith("#")][:max_lines]

    return "\n".join(summary_lines)


def build_report(job_ids=None):
    """Собирает отчёт из последних результатов cron задач"""
    if job_ids is None:
        job_ids = list(JOB_NAMES.keys())

    sections = []
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sections.append(f"📋 *Cron Delivery Report*\n🕐 {timestamp}\n")

    for job_id in job_ids:
        job_name = JOB_NAMES.get(job_id, f"job-{job_id[:8]}")
        latest_path, content = get_latest_output(job_id)

        if content is None:
            sections.append(f"❌ *{job_name}* — нет данных")
            continue

        # Извлекаем время из имени файла или содержимого
        time_str = "неизвестно"
        if latest_path:
            basename = os.path.basename(latest_path).replace(".md", "").replace("_", " ")
            time_str = basename

        summary = extract_summary(content, max_lines=10)
        sections.append(f"━━━━━━━━━━━━━━━━━━━━\n📌 *{job_name}*\n🕐 `{time_str}`\n```\n{summary}\n```\n")

    report = "\n".join(sections)
    return report


def send_report(chat_id=None, message=None, token=None):
    """Отправляет отчёт через send_telegram_message из telegram_bridge.py"""
    resolved_chat = resolve_chat_id(chat_id)
    resolved_token = resolve_token(token)

    if message:
        send_telegram_message(text=message, chat_id=resolved_chat, token=resolved_token)
    return True


def main():
    parser = argparse.ArgumentParser(description="Telegram Delivery Report")
    parser.add_argument("--token", help="Telegram Bot API токен")
    parser.add_argument("--job-id", action="append", help="Job ID для включения в отчёт (можно несколько)")
    parser.add_argument("--chat-id", help="Chat ID для отправки")
    parser.add_argument("--list-jobs", action="store_true", help="Показать доступные job_id и выйти")
    args = parser.parse_args()

    if args.list_jobs:
        print("Доступные cron задачи:")
        for jid, name in sorted(JOB_NAMES.items()):
            print(f"  {jid}  → {name}")
        return

    job_ids = args.job_id or list(JOB_NAMES.keys())
    report = build_report(job_ids)

    print("[telegram-delivery] Собираю отчёт...")

    # Показываем какой chat_id будет использован
    resolved_chat = resolve_chat_id(args.chat_id)
    token_ok = "[OK]" if resolve_token(args.token) else "[MISSING]"
    print(f"[telegram-delivery] Chat ID: {resolved_chat}")
    print(f"[telegram-delivery] Token: {token_ok}")

    try:
        send_report(chat_id=args.chat_id, message=report, token=args.token)
        print(f"[telegram-delivery] Отчёт отправлен успешно в чат {resolved_chat}")
    except ValueError as e:
        print(f"[telegram-delivery] ERROR: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"[telegram-delivery] ERROR: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

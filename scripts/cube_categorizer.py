#!/usr/bin/env python3
"""
Cube Categorizer - auto-assigns domain labels to uncategorized Knowledge Cube entries
using keyword heuristics. Part of BD-003.
"""

import sqlite3
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROJECT_ROOT = HERE.parent
DB_PATH = PROJECT_ROOT / "cache" / "knowledge_cube.db"

# Domain classification rules: (list of keywords, domain_label)
# Order matters — first matching rule wins.
DOMAIN_RULES = [
    # debugging — error/failure keywords
    (["error", "bug", "fix", "crash", "traceback", "exception", "fail", "broken",
      "ошибк", "баг", "сломал", "не работ", "не отвеча", "падени", "глюк",
      "завис", "тормоз", "баган"], "debugging"),
    # devops — infrastructure/deployment
    (["install", "setup", "config", "deploy", "migrat", "docker", "server",
      "port", "установ", "настрой", "разверт", "подключ", "запуст", "деплой",
      "докер", "сервер", "регистр", "разрешен", "бот апи", "апи", "api"], "devops"),
    # coding — writing/creating code
    (["write", "create", "code", "function", "class", "def ", "import ",
      "script", "напиш", "создай", "функци", "код", "программ", "сделай",
      "реализуй", "добавь", "поправь", "исправ"], "coding"),
    # research — searching/finding information
    (["search", "research", "find", "lookup", "поищ", "найди", "исслед",
      "интересн", "узнай", "посмотр", "собери", "вариант", "иде"],
     "research"),
    # terminal — shell/command-line operations
    (["terminal", "bash", "command", "run", "запуст", "команд", "терминал",
      "консол"], "terminal"),
    # browser — web/navigation
    (["browser", "navigate", "click", "page", "url", "link", "браузер",
      "открой", "страниц", "сайт", "ссылк"], "browser"),
    # communication — messaging/sending
    (["telegram", "send", "message", "чат", "сообщен", "отправ", "напиш",
      "тг бот", "телеграм", "бот", "тг", "настроил телеграм"], "communication"),
    # file_ops — file operations
    (["file", "folder", "directory", "copy", "move", "delete",
      "файл", "папк", "скопиру", "сохран"], "file_ops"),
    # system — system/status queries
    (["system", "status", "check", "test", "hi", "hello", "привет",
      "проверк", "готов", "умеешь", "занят", "стоп", "хватит"], "system"),
    # data — data analysis
    (["data", "analyz", "statistic", "report", "данн", "анализ", "отчет",
      "статистик"], "data"),
]


def classify_domain(text: str) -> str:
    """Return a domain label based on keyword heuristics."""
    lower = text.lower()
    for keywords, domain in DOMAIN_RULES:
        for kw in keywords:
            if kw in lower:
                return domain
    return "uncategorized"


def categorize_uncategorized(dry_run: bool = False) -> int:
    """
    Query all uncategorized experiences, classify them, and update the DB.
    Returns the number of entries that were categorized (or would be).
    """
    if not DB_PATH.exists():
        print(f"ERROR: Database not found at {DB_PATH}")
        sys.exit(1)

    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # 1. Fetch all uncategorized entries
    cursor.execute(
        "SELECT id, raw_text FROM experiences WHERE axis_domain = 'uncategorized'"
    )
    rows = cursor.fetchall()
    total = len(rows)
    print(f"Found {total} uncategorized entries.")

    if total == 0:
        conn.close()
        return 0

    # 2. Classify each
    updates: dict[str, list[int]] = {}  # domain -> [ids]
    still_uncategorized: list[int] = []

    for row in rows:
        domain = classify_domain(row["raw_text"])
        if domain == "uncategorized":
            still_uncategorized.append(row["id"])
        else:
            updates.setdefault(domain, []).append(row["id"])

    categorized_count = sum(len(ids) for ids in updates.values())
    print(f"Will categorize: {categorized_count} entries into {len(updates)} domains:")
    for domain, ids in sorted(updates.items()):
        print(f"  {domain}: {len(ids)}")
    if still_uncategorized:
        print(f"  (still uncategorized: {len(still_uncategorized)})")

    # 3. Update DB
    if not dry_run and categorized_count > 0:
        cursor.executemany(
            "UPDATE experiences SET axis_domain = ? WHERE id = ?",
            [(domain, eid) for domain, ids in updates.items() for eid in ids],
        )
        conn.commit()
        print(f"\nUpdated {cursor.rowcount} rows in database.")

    conn.close()
    return categorized_count


def main():
    # Heartbeat: module alive
    try:
        from chain_heartbeat import beat
        beat("cube_categorizer")
    except ImportError:
        pass

    import argparse

    parser = argparse.ArgumentParser(
        description="Auto-categorize uncategorized Knowledge Cube entries"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be categorized without modifying the DB",
    )
    args = parser.parse_args()

    dry_run = args.dry_run
    if dry_run:
        print("=== DRY RUN — no changes will be made ===\n")

    categorized = categorize_uncategorized(dry_run=dry_run)

    if dry_run:
        print(f"\n=== DRY RUN complete. Would categorize {categorized} entries. ===")
    else:
        print(f"\n=== Done. Categorized {categorized} entries. ===")

    return 0


if __name__ == "__main__":
    sys.exit(main())

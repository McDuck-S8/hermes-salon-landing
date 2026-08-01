#!/usr/bin/env python3
"""
Knowledge Cube → Memory мост.

1) Раз в 6 часов проходится по новым записям в knowledge_cube.db (таблица experiences, поле ts).
2) Если опыт содержит ключевые слова (error, bug, crash, fix, solution, learned) — извлекает его.
3) Сохраняет извлечённое знание в .lavra/memory/knowledge.jsonl (JSONL: key, type, content, source, tags, ts, bead).
4) Если .lavra/ не существует — создаёт директорию.

Типы (определяются по ключевым словам):
  - error/fix      → learned
  - pattern/always → pattern
  - decision/choose → decision

Состояние (last_processed_ts) хранится в .lavra/memory/.cube_to_memory_state.json
"""

import json
import sqlite3
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

# ─── Константы ────────────────────────────────────────────────────────────────

HERE = Path(__file__).resolve().parent
WORKSPACE = HERE.parent  # D:\Portable_Soft\hermes

DB_PATH = WORKSPACE / "cache" / "knowledge_cube.db"
MEMORY_DIR = WORKSPACE / ".lavra" / "memory"
OUTPUT_FILE = MEMORY_DIR / "knowledge.jsonl"
STATE_FILE = MEMORY_DIR / ".cube_to_memory_state.json"

KEYWORDS = [
    "error", "bug", "crash", "fix", "solution", "learned",
    "ошибк", "баг", "сломал", "исправ", "почин", "науч",
    "решен", "проблем", "успешн", "готов",
]

# Маппинг ключевых слов на типы знаний
KEYWORD_TYPE_MAP: list[tuple[list[str], str]] = [
    (["error", "fix"], "learned"),
    (["pattern", "always"], "pattern"),
    (["decision", "choose"], "decision"),
]


def load_state() -> str | None:
    """Загружает последний обработанный timestamp из state-файла."""
    if STATE_FILE.exists():
        try:
            with open(STATE_FILE) as f:
                state = json.load(f)
            return state.get("last_processed_ts")
        except (json.JSONDecodeError, KeyError):
            pass
    return None


def save_state(ts: str) -> None:
    """Сохраняет последний обработанный timestamp в state-файл."""
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump({"last_processed_ts": ts, "updated_at": datetime.now(timezone.utc).isoformat()}, f)


def detect_type(content: str) -> str:
    """Определяет тип знания по ключевым словам в тексте."""
    content_lower = content.lower()
    for keywords, knowledge_type in KEYWORD_TYPE_MAP:
        if any(kw in content_lower for kw in keywords):
            return knowledge_type
    return "learned"  # fallback — по умолчанию learned


def make_key(content: str, knowledge_type: str) -> str:
    """Генерирует уникальный ключ для записи знаний."""
    # Используем hash от первых 100 символов содержимого
    import hashlib
    h = hashlib.md5(content.encode("utf-8")).hexdigest()[:12]
    return f"{knowledge_type}-{h}"


def parse_ts(ts_str: str) -> int:
    """Парсит ISO timestamp из БД в unix timestamp (int)."""
    if not ts_str:
        return int(time.time())
    try:
        dt = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
        return int(dt.timestamp())
    except (ValueError, AttributeError):
        pass
    try:
        return int(float(ts_str))
    except (ValueError, TypeError):
        pass
    return int(time.time())


def parse_tags(tags_raw: str | None) -> list[str]:
    """Парсит tags из JSON-строки."""
    if not tags_raw:
        return []
    if isinstance(tags_raw, str):
        tags_raw = tags_raw.strip()
        if not tags_raw:
            return []
        try:
            parsed = json.loads(tags_raw)
            if isinstance(parsed, list):
                return parsed
        except json.JSONDecodeError:
            pass
        # CSV fallback
        return [t.strip() for t in tags_raw.split(",") if t.strip()]
    return []


def process_experiences(last_ts: str | None) -> int:
    """
    Читает новые записи из knowledge_cube.db, фильтрует по ключевым словам
    и дописывает их в .lavra/memory/knowledge.jsonl.
    Возвращает количество обработанных записей.
    """
    if not DB_PATH.exists():
        print(f"[cube_to_memory] БД не найдена: {DB_PATH}", file=sys.stderr)
        return 0

    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Выбираем записи новее last_ts, упорядоченные по ts
    if last_ts:
        cursor.execute(
            """SELECT id, ts, raw_text, axis_domain, tags, source
               FROM experiences
               WHERE ts > ?
               ORDER BY ts ASC""",
            (last_ts,),
        )
    else:
        cursor.execute(
            """SELECT id, ts, raw_text, axis_domain, tags, source
               FROM experiences
               ORDER BY ts ASC""",
        )

    rows = cursor.fetchall()
    conn.close()

    if not rows:
        print(f"[cube_to_memory] Нет новых записей (last_ts={last_ts})")
        return 0

    # Убеждаемся, что директория .lavra/memory/ существует
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)

    processed = 0
    last_processed_ts = last_ts

    with open(OUTPUT_FILE, "a", encoding="utf-8") as out:
        for row in rows:
            content = row["raw_text"]
            if not content:
                continue

            # Проверка на ключевые слова
            content_lower = content.lower()
            if not any(kw in content_lower for kw in KEYWORDS):
                continue

            knowledge_type = detect_type(content)
            key = make_key(content, knowledge_type)
            tags = parse_tags(row["tags"])

            # Добавляем тег домена если есть
            domain = row["axis_domain"]
            if domain and domain != "uncategorized" and domain not in tags:
                tags.append(domain)

            record = {
                "key": key,
                "type": knowledge_type,
                "content": content,
                "source": "knowledge-cube",
                "tags": tags,
                "ts": parse_ts(row["ts"]),
                "bead": "",
            }

            out.write(json.dumps(record, ensure_ascii=False) + "\n")
            last_processed_ts = row["ts"]
            processed += 1

    # Сохраняем состояние
    if last_processed_ts:
        save_state(last_processed_ts)

    print(f"[cube_to_memory] Обработано: {processed} записей (last_ts={last_processed_ts})")
    return processed


def main():
    print(f"[cube_to_memory] Knowledge Cube → Memory мост")
    print(f"  DB:     {DB_PATH}")
    print(f"  Output: {OUTPUT_FILE}")

    last_ts = load_state()
    print(f"  State:  last_ts={last_ts}")

    count = process_experiences(last_ts)
    print(f"[cube_to_memory] Готово. Добавлено: {count}")


if __name__ == "__main__":
    main()

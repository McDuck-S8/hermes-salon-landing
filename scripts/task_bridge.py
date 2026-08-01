#!/usr/bin/env python3
"""Task Bridge — forwards user tasks from McDuck8Bot to Hermes agent system."""
import json, os, time, urllib.request, urllib.parse
from pathlib import Path

HERMES_HOME = Path(os.environ.get("HERMES_HOME", "D:/Portable_Soft/hermes"))
KC_DB = HERMES_HOME / "cache" / "knowledge_cube.db"
TASKS_FILE = HERMES_HOME / "cache" / "pending_tasks.jsonl"

def forward_to_hermes(text: str) -> str:
    """
    Forward user task to Hermes agent system.
    Writes to pending_tasks.jsonl for autonomous_agent.py to pick up.
    Also adds to Knowledge Cube as a task entry.
    """
    task_id = f"task_{int(time.time() * 1000)}"
    task = {
        "id": task_id,
        "text": text,
        "source": "mcduck_bot",
        "chat_id": "737433175",
        "created_at": time.time(),
        "status": "pending"
    }
    
    # Append to pending tasks file
    TASKS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(TASKS_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(task, ensure_ascii=False) + "\n")
    
    # Also add to Knowledge Cube
    try:
        import sqlite3
        conn = sqlite3.connect(str(KC_DB))
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA busy_timeout=5000")
        conn.execute("""
            INSERT INTO knowledge_cube (id, content, tags, source, created_at, updated_at, entry_type, confidence)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            f"task_{task_id}",
            f"User task from @McDuck8Bot: {text}",
            "task,user,mcduck",
            "mcduck_bot",
            time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "task",
            1.0
        ))
        conn.commit()
        conn.close()
    except Exception as e:
        pass  # Don't fail the response
    
    return f"✅ Задача принята: {text[:100]}{'...' if len(text) > 100 else ''}\n\nHermes обработает её в ближайшем цикле. Проверь результат через /status или утренний отчёт."

if __name__ == "__main__":
    # Test
    print(forward_to_hermes("test task from bridge"))
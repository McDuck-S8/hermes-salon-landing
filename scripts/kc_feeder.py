#!/usr/bin/env python3
"""
KC Feeder — автоматически наполняет Knowledge Cube из session history.

Сканирует state.db, извлекает важные моменты и записывает в KC.
Запускается периодически для поддержания актуальности базы знаний.

Использование:
    python kc_feeder.py                  # полный цикл
    python kc_feeder.py --dry-run        # показать что будет добавлено
    python kc_feeder.py --domain web     # только определённый домен
"""

import json
import hashlib
import os
import sqlite3
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict

HERMES_HOME = Path(os.environ.get("HERMES_HOME", str(Path.home() / ".hermes")))
# Also check the portable hermes location for event_bus.json
PORTABLE_HERMES = Path("D:/Portable_Soft/hermes")
if not (HERMES_HOME / "cache" / "event_bus.json").exists() and (PORTABLE_HERMES / "cache" / "event_bus.json").exists():
    HERMES_HOME = PORTABLE_HERMES
STATE_DB = HERMES_HOME / "state.db"
KC_DB = HERMES_HOME / "cache" / "knowledge_cube.db"
OUTPUT = HERMES_HOME / "cache" / "kc_feeder_log.json"


def get_recent_messages(hours: int = 24, limit: int = 100) -> List[Dict]:
    """Получает недавние сообщения из state.db."""
    if not STATE_DB.exists():
        return []
    
    conn = sqlite3.connect(str(STATE_DB))
    cur = conn.cursor()
    
    try:
        since = (datetime.now() - timedelta(hours=hours)).timestamp()
        cur.execute("""
            SELECT id, role, content, timestamp 
            FROM messages 
            WHERE timestamp > ? 
            ORDER BY timestamp DESC 
            LIMIT ?
        """, (since, limit))
        
        messages = []
        for row in cur.fetchall():
            messages.append({
                "id": row[0],
                "role": row[1],
                "content": row[2],
                "timestamp": row[3]
            })
        
        return messages
    except Exception as e:
        print(f"Error reading messages: {e}", file=sys.stderr)
        return []
    finally:
        conn.close()


def extract_insights(messages: List[Dict]) -> List[Dict]:
    """Извлекает инсайты из сообщений."""
    insights = []
    
    for msg in messages:
        content = msg.get("content", "")
        if not content or len(content) < 50:
            continue
        
        # Определяем домен по ключевым словам
        domain = "general"
        if any(w in content.lower() for w in ["web", "browser", "http", "url"]):
            domain = "web"
        elif any(w in content.lower() for w in ["file", "read", "write", "path"]):
            domain = "file"
        elif any(w in content.lower() for w in ["terminal", "command", "shell", "bash"]):
            domain = "terminal"
        elif any(w in content.lower() for w in ["error", "fail", "crash", "bug"]):
            domain = "issues"
        elif any(w in content.lower() for w in ["cron", "schedule", "job"]):
            domain = "infrastructure"
        
        # Определяем исход
        outcome = "neutral"
        if any(w in content.lower() for w in ["success", "worked", "fixed", "resolved"]):
            outcome = "success"
        elif any(w in content.lower() for w in ["error", "fail", "broken"]):
            outcome = "failure"
        
        # Извлекаем ключевую информацию
        if len(content) > 100:
            insight = content[:200]  # Берём начало
        else:
            insight = content
        
        insights.append({
            "content": insight,
            "domain": domain,
            "outcome": outcome,
            "source": "session_history",
            "original_id": msg["id"],
            "timestamp": msg["timestamp"]
        })
    
    return insights


def add_to_kc(insights: List[Dict], dry_run: bool = False) -> int:
    """Добавляет инсайты в Knowledge Cube."""
    if not KC_DB.exists():
        print(f"KC not found: {KC_DB}", file=sys.stderr)
        return 0
    
    if dry_run:
        print(f"Dry run: would add {len(insights)} insights")
        for i, insight in enumerate(insights[:5]):
            print(f"  {i+1}. [{insight['domain']}/{insight['outcome']}] {insight['content'][:80]}...")
        return len(insights)
    
    conn = sqlite3.connect(str(KC_DB))
    cur = conn.cursor()
    
    try:
        added = 0
        
        # Detect schema - check if hash column exists
        cur.execute("PRAGMA table_info(experiences)")
        columns = [row[1] for row in cur.fetchall()]
        has_hash = "hash" in columns
        has_raw_text = "raw_text" in columns
        
        for insight in insights:
            # Проверяем дубликаты
            if has_raw_text:
                cur.execute("""
                    SELECT id FROM experiences 
                    WHERE raw_text = ? AND axis_domain = ?
                """, (insight["content"], insight["domain"]))
            else:
                cur.execute("""
                    SELECT id FROM experiences 
                    WHERE content = ? AND axis_domain = ?
                """, (insight["content"], insight["domain"]))
            
            if cur.fetchone():
                continue  # Пропускаем дубликат
            
            # Добавляем
            if has_hash:
                content_hash = hashlib.md5(f"{insight['content']}_{datetime.now().isoformat()}".encode()).hexdigest()[:16]
                if has_raw_text:
                    cur.execute("""
                        INSERT INTO experiences (raw_text, content, hash, tags, source, ts, axis_domain, axis_outcome)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        insight["content"],
                        insight["content"],
                        content_hash,
                        insight["domain"],
                        insight["source"],
                        datetime.now().isoformat(),
                        insight["domain"],
                        insight["outcome"]
                    ))
                else:
                    cur.execute("""
                        INSERT INTO experiences (content, hash, tags, source, created_at, axis_domain, axis_outcome)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        insight["content"],
                        content_hash,
                        insight["domain"],
                        insight["source"],
                        int(datetime.now().timestamp()),
                        insight["domain"],
                        insight["outcome"]
                    ))
            else:
                if has_raw_text:
                    cur.execute("""
                        INSERT INTO experiences (raw_text, content, tags, source, ts, axis_domain, axis_outcome)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        insight["content"],
                        insight["content"],
                        insight["domain"],
                        insight["source"],
                        datetime.now().isoformat(),
                        insight["domain"],
                        insight["outcome"]
                    ))
                else:
                    cur.execute("""
                        INSERT INTO experiences (content, tags, source, created_at, axis_domain, axis_outcome)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        insight["content"],
                        insight["domain"],
                        insight["source"],
                        int(datetime.now().timestamp()),
                        insight["domain"],
                        insight["outcome"]
                    ))
            added += 1
        
        conn.commit()
        return added
    except Exception as e:
        print(f"Error adding to KC: {e}", file=sys.stderr)
        conn.rollback()
        return 0
    finally:
        conn.close()


def main():
    args = sys.argv[1:]
    dry_run = "--dry-run" in args
    domain_filter = None
    
    for i, arg in enumerate(args):
        if arg == "--domain" and i + 1 < len(args):
            domain_filter = args[i + 1]
    
    print(f"[{datetime.now().isoformat()}] KC Feeder starting...")
    
    # Получаем сообщения
    messages = get_recent_messages(hours=24, limit=200)
    print(f"  Messages: {len(messages)}")
    
    # Извлекаем инсайты
    insights = extract_insights(messages)
    print(f"  Insights: {len(insights)}")
    
    # Фильтруем по домену
    if domain_filter:
        insights = [i for i in insights if i["domain"] == domain_filter]
        print(f"  Filtered to domain '{domain_filter}': {len(insights)}")
    
    # Добавляем в KC
    added = add_to_kc(insights, dry_run=dry_run)
    print(f"  Added: {added}")

    # Emit event if knowledge was added
    if added > 0:
        try:
            from emit_event import emit
            emit("knowledge_added", {
                "domain": domain_filter or "mixed",
                "count": added,
                "source": "kc_feeder",
            })
        except Exception:
            pass
    
    # Сохраняем лог
    log = {
        "timestamp": datetime.now().isoformat(),
        "messages_scanned": len(messages),
        "insights_extracted": len(insights),
        "added_to_kc": added,
        "dry_run": dry_run
    }
    
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT, 'w', encoding='utf-8') as f:
        json.dump(log, f, ensure_ascii=False, indent=2)
    
    print(f"  Log: {OUTPUT}")
    return added


if __name__ == "__main__":
    main()

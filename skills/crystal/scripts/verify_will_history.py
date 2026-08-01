#!/usr/bin/env python3
"""Проверка, что история воли кристалла реально пишется в KC.

Использование: python scripts/verify_will_history.py [--hours N]  (default N=24)
Exit 0 — за последние N часов есть записи crystal_will; exit 1 — истории нет.

Контекст (2026-07-31): _save_will_history() молчаливо падал с
IntegrityError: NOT NULL constraint failed: experiences.content —
INSERT не заполнял колонку content, история воли не накапливалась
с 2026-07-15 (признак: в KC одна-единственная старая запись crystal_will).
"""
import sqlite3
import sys
import os
from datetime import datetime, timedelta

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KC = os.path.join(ROOT, "cache", "knowledge_cube.db")

HOURS = 24
if "--hours" in sys.argv:
    i = sys.argv.index("--hours")
    if i + 1 < len(sys.argv):
        HOURS = int(sys.argv[i + 1])

cutoff = (datetime.now() - timedelta(hours=HOURS)).isoformat()[:19]
conn = sqlite3.connect(KC)
cur = conn.cursor()
cur.execute(
    "SELECT COUNT(*) FROM experiences WHERE source='crystal_will' AND ts > ?",
    (cutoff,),
)
fresh = cur.fetchone()[0]
cur.execute(
    "SELECT ts, substr(raw_text,1,90) FROM experiences "
    "WHERE source='crystal_will' ORDER BY id DESC LIMIT 5"
)
recent = cur.fetchall()
conn.close()

print(f"crystal_will записей за последние {HOURS}ч: {fresh}")
for ts, txt in recent:
    print(f"  {ts} | {txt}")

if fresh == 0:
    print(
        "FAIL: история воли не пишется. Проверь NOT NULL content "
        "в INSERT'ах crystal.py (_save_will_history, record, intent-INSERT)."
    )
    sys.exit(1)
print("OK: история воли пишется")

import sqlite3
from datetime import datetime
KC = 'cache/knowledge_cube.db'

# Test _save_will_history
now = datetime.now()
ts = now.isoformat()[:19]
action_id = "test_extract_fabric"
result_text = "Воля: fabric не содержал новых сущностей (200 записей, 0 кандидатов) — нужен другой подход"

try:
    kc = sqlite3.connect(KC)
    k = kc.cursor()
    k.execute(
        "INSERT INTO experiences (ts, content, raw_text, hash, axis_time_hour, axis_time_dow, axis_domain, axis_outcome, source) VALUES (?,?,?,?,?,?,?,?,?)",
        (ts, result_text, f"[will:{action_id}] {result_text}", str(hash(ts + action_id))[:16], now.hour, now.weekday(), 'crystal_will', 'will_action', 'crystal_will')
    )
    kc.commit()
    kc.close()
    print("SUCCESS: Inserted test entry")
except Exception as e:
    print(f"ERROR: {e}")

# Verify
kc = sqlite3.connect(KC)
k = kc.cursor()
k.execute("SELECT raw_text FROM experiences WHERE source='crystal_will' ORDER BY id DESC LIMIT 5")
for row in k.fetchall():
    print(row[0][:200])
kc.close()
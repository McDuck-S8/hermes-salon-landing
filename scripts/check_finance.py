from scripts.finance_core import FinanceCore, get_finance_summary
import json

fc = FinanceCore()
summary = get_finance_summary()
print(json.dumps(summary, indent=2, ensure_ascii=False))

# Also check baselines
print("\n=== BASELINES ===")
import sqlite3
conn = sqlite3.connect("cache/finance_core.db")
cursor = conn.cursor()
cursor.execute("SELECT * FROM scheme_unit_economics")
rows = cursor.fetchall()
for row in rows:
    print(row)
conn.close()
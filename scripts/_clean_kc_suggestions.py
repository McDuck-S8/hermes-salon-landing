"""Clean KC: re-tag existing suggestion entries with _suggestion_log domain"""
import sqlite3, json, sys

kc = sqlite3.connect('../cache/knowledge_cube.db')
c = kc.cursor()

# Re-tag entries that start with [suggestion:
c.execute("""
    UPDATE experiences 
    SET axis_domain = '_suggestion_log', 
        axis_outcome = 'meta',
        tags = ?
    WHERE raw_text LIKE '%[suggestion:%'
""", (json.dumps(["suggestion", "log-analysis", "auto-detected"]),))

changed = c.rowcount
kc.commit()

total = c.execute('SELECT COUNT(*) FROM experiences').fetchone()[0]
remaining_suggestions = c.execute(
    "SELECT COUNT(*) FROM experiences WHERE axis_domain = '_suggestion_log'"
).fetchone()[0]

print(f"Re-tagged: {changed}")
print(f"Total KC: {total}")
print(f"_suggestion_log entries: {remaining_suggestions}")
print(f"Clean (non-suggestion): {total - remaining_suggestions}")

# Verify domains
c.execute("SELECT axis_domain, COUNT(*) FROM experiences WHERE axis_domain NOT IN ('_suggestion_log', 'system') GROUP BY axis_domain ORDER BY COUNT(*) DESC LIMIT 10")
print("\n=== REAL DOMAINS AFTER CLEANUP ===")
for d, cnt in c.fetchall():
    print(f"  {d}: {cnt}")

kc.close()

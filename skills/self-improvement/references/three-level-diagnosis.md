## Three-Level Diagnosis — System vs Crystal vs Agent

**User correction (critical):** After running `hermes-self-diagnosis`, the agent must clearly
distinguish WHICH component is being diagnosed. "Диагностика КОГО? КРИСТАЛЛА? ИЛИ ТЕБЯ?" — if
the output doesn't explicitly name the target, the user will ask. Always label at the top.

| Level | What | Data Sources | Output Style |
|-------|------|-------------|-------------|
| **SYSTEM** | Hermes infrastructure — cubes, DBs, processes, disk | SQLite queries on kc/entity/fler/state DBs, process list, disk usage | System metrics: entries, domains, sizes, counts |
| **CRYSTAL** | Autonomous agent state — decisions, self-model, will, plans | `cache/self_model.json`, KC crystal* entries, `cache/crystal_tasks.json` | Narrative: "132 цикла, 1244 записей, currently deciding X" |
| **AGENT (Hermes)** | Current session agent — skills loaded, tools used, decisions made | Session context, memory, fabric | Self-report: what I did, what I learned, what I'm unsure about |

### Crystal Diagnosis Procedure

Run when user asks about the crystal's state, thoughts, or decisions:

```python
import json, os, sqlite3

HERMES = "D:/Portable_Soft/hermes"
sm = json.load(open(os.path.join(HERMES, "cache/self_model.json")))

# 1. Cycle metrics
print(f"Версия: {sm.get('version','?')}")
print(f"Циклов: {sm.get('cycle_count','?')}")
print(f"Последний: {sm.get('last_cycle','?')}")

# 2. Active decisions (znu) — what it's thinking about now
znu = sm.get('znu', {})
for k, v in znu.items():
    print(f"  [{k}] {str(v)[:120]}")

# 3. Plan
plan = sm.get('plan', {})
print(f"План: {str(plan)[:300] if plan else 'нет'}")

# 4. Self-evaluation
print(f"Знает: {str(sm.get('znayu','?'))[:200]}")
print(f"Не знает: {str(sm.get('ne_znayu','?'))[:200]}")

# 5. Self-modifications
mods = sm.get('modifications', [])
print(f"Самоизменений: {len(mods)}")

# 6. Bridge tasks
tasks = json.load(open(os.path.join(HERMES, "cache/crystal_tasks.json")))
for t in tasks:
    print(f"  [{t.get('status','?')}] {t.get('id','?')[:40]}")

# 7. KC crystal entries
kc = sqlite3.connect(os.path.join(HERMES, "cache/knowledge_cube.db"))
crystal_total = kc.execute("SELECT COUNT(*) FROM experiences WHERE axis_domain='crystal' OR axis_domain='crystal_will'").fetchone()[0]
crystal_24h = kc.execute("SELECT COUNT(*) FROM experiences WHERE (axis_domain='crystal' OR axis_domain='crystal_will') AND ts > datetime('now', '-1 day')").fetchone()[0]
kc.close()
print(f"Crystal* записей в KC: {crystal_total} (за 24ч: {crystal_24h})")
```

### When to Use Each Level

- **Run SYSTEM diagnosis** when user says "/hermes-self-diagnosis" or "check health" or "диагностика"
- **Run CRYSTAL diagnosis** when user asks about the crystal's state, "что кристалл думает", or after crystal cycles complete
- **Run AGENT diagnosis** when the user asks about YOUR state — what skills you loaded, what you know
- **LABEL the output** — start with "═══ ДИАГНОСТИКА СИСТЕМЫ ═══" or "═══ ДИАГНОСТИКА КРИСТАЛЛА ═══" so there's no ambiguity

## ⚠ CRITICAL: Label Every Diagnosis Output

**Live session correction:** After running any diagnosis, the user's FIRST reaction was
"ЭТО диагностика КОГО? КРИСТАЛЛА? ИЛИ ТЕБЯ?" — they saw compacted context from a prior
session and assumed it was crystal diagnosis. The fix is simple and mandatory:

Every diagnosis output MUST start with one of these headers:
- `═══ ДИАГНОСТИКА СИСТЕМЫ ═══` (Hermes infrastructure)
- `═══ ДИАГНОСТИКА КРИСТАЛЛА ═══` (crystal self-model, will, decisions)
- `═══ ДИАГНОСТИКА АГЕНТА ═══` (current agent state)

Do NOT rely on context compaction to carry the label — the user reads raw output
before you add context. When re-presenting compacted information, re-label it.

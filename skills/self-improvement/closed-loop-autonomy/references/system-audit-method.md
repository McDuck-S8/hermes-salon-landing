# System Audit Method

**When to run:** When user says "анализ системы", when components aren't producing expected outputs, when you need to find dead links in the pipeline.

## Methodology

### 1. Map Every Component

For each major component, answer what it reads and writes:

```python
flow = {
    component_name: {
        "reads": ["data sources"],
        "writes": ["outputs"],
        "produced_ok": "Does it write what consumers need?",
        "consumed_ok": "Does it read what it needs?",
    }
}
```

### 2. Trace Information Flow

``PRODUCER → CHANNEL → CONSUMER``

For each producer:
- Who reads its output? (1 consumer = fragile, 0 = dead)
- Is there a path where data enters but event doesn't fire?

For each consumer:
- Does it have the data it needs before it runs?
- What happens if data is stale/missing?

### 3. Identify Gaps

| Gap Type | Signal | Fix |
|----------|--------|-----|
| Orphan producer | Writes to no consumer | Add consumer or remove |
| Starved consumer | Needs data no one produces | Add producer or merge |
| Dead link | Pipeline broken mid-chain | Find break, restore link |
| Silent signal | Event fires but nothing reacts | Add handler/hook |
| Orphan consumer | Outputs to nowhere | Add reader or prune |

### 4. Gauge Each Component's Information Sufficiency

Check: does every component get enough data to function? Does every component produce what others need?

### 5. Check Frequency — Cron vs Event Inventory

Count total cron jobs. If >20, flag as organizational debt.
Each cron job should pass: "Could this be event-driven instead?"

### 6. Recommend Priority Fixes

Sort by impact: close loops first (producer has no consumer), then fix starved consumers, then clean up redundancy.

## Quick Audit Commands

```bash
# Component count
ls scripts/*.py | wc -l && ls cache/*.db | wc -l

# KC domain distribution
python -c "import sqlite3; c=sqlite3.connect('cache/knowledge_cube.db').cursor(); c.execute('SELECT axis_domain, COUNT(*) FROM experiences GROUP BY axis_domain ORDER BY COUNT(*) DESC'); [print(f'  {d}: {n}') for d,n in c.fetchall()]"

# EE relationships count
python -c "import sqlite3; r=sqlite3.connect('cache/entity_engine.db').cursor().execute('SELECT COUNT(*) FROM relationships').fetchone()[0]; print(f'Relationships: {r}')"

# Semantic memory coverage
python -c "import sqlite3; s=sqlite3.connect('cache/semantic_memory.db').cursor().execute('SELECT COUNT(*) FROM semantic_memories').fetchone()[0]; print(f'Semantic entries: {s}')"

# Heartbeat events
python -c "from scripts.chain_heartbeat import system_status; import json; print(json.dumps(system_status()['summary'], indent=2))"
```

## Applied: 2026-07-23 Audit

Found: 58 cron jobs (organizational debt), EE 3672 entities but 1 relationship (entities without connections), Goal Queue 0 active (goals not consumed), Proactive Voice signal detected but not acted upon (unclosed loop), Semantic Memory 469/8744 entries (5% coverage).

See `reports/system-audit-2026-07-23.md` for the full report.

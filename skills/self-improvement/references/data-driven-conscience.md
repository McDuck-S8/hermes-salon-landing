# Data-Driven Conscience Architecture

## Problem (2026-06-13)

Fixed learning_directions in _conscience() exhaust after a few cycles because:
1. prev_learning accumulates ALL past learning_directions
2. Same strings get generated every cycle → all filtered as duplicates
3. will() returns "всё сделано, жду новых событий"

Root cause: system produces identical output each cycle. Violates core principle:
**"В рекурсии выход должен отличаться от входа данных"**.

## Solution: Data-Driven Learning Directions

Instead of fixed strings like "добавить междоменный анализ", generate
directions from REAL data that changes between cycles:

```python
# In _conscience(): query KC for actual domains/sources
conn = sqlite3.connect(KC)
c = conn.cursor()
c.execute("SELECT axis_domain, COUNT(*) FROM experiences 
           WHERE axis_domain IS NOT NULL 
           GROUP BY axis_domain ORDER BY COUNT(*) DESC LIMIT 20")
domains = c.fetchall()
min_d = min(domains, key=lambda x: x[1])
learning_direction.append(
    f"исследовать слепое пятно: домен '{min_d[0]}' ({min_d[1]} записей)"
)
```

Each cycle gets different strings because KC grows (counts change),
different domains become min/max.

## Pattern: Unique Action IDs from Dynamic Data

Problem: LEARNING_TO_ACTION uses exact string matching → dynamic
strings don't match any key.

Solution: Pattern-based mapping with regex extraction:

```python
# In will() step 3.5 conscience mapping loop
if ld.startswith("исследовать слепое пятно"):
    m = re.search(r"домен '([^']+)'", ld)
    name = m.group(1) if m else 'unknown'
    act = {'action': f'blindspot_{name}', 'target': 'patterns', ...}
```

This creates UNIQUE action_ids (conscience_blindspot_music-audio,
conscience_blindspot_research) that don't collide in historical_ids.

## Specialized Handlers

Catch-all else is too generic. Add specific handlers:

```python
elif action_type.startswith('blindspot_'):
    domain = action_type.replace('blindspot_', '')
    conn = sqlite3.connect(KC)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM experiences WHERE axis_domain=?", (domain,))
    count = c.fetchone()[0]
    return f"Слепое пятно '{domain}': {count} записей"
```

## Tie-Breaking for Equal-Weight Candidates

When all candidates have same weight (impact/effort), stable sort
always picks first. Add randomization + bonus for data-driven:

```python
def weight(c):
    import random
    base = impact/effort
    if source == 'conscience': base *= 1.5
    if action_id has domain-specific prefix: base *= 1.1
    base += random.uniform(0, 0.3)  # tie-breaking
    return base
```

## Pitfall: prev_learning Exhaustion

If prev_learning checks ALL assessments, all directions get filtered
after a few cycles. Fix: limit to last N assessments OR skip
filtering for data-driven directions (they're unique by nature).

## Key Insight

Fixed learning_directions are a closed set → guaranteed exhaustion.
Data-driven directions are an open set → grows with data → system
can run indefinitely without repeating.

The crystal currently has 3 data-driven types:
- blindspot_{domain} — smallest domain, blind spot
- deepen_{domain} — largest domain, go deeper
- audit_{source} — least-used source, check coverage

# Data-Driven Conscience — Debugging Guide

## Problem: candidates=0 after all_learning=10

**Root cause:** LEARNING_TO_ACTION mapping keys don't match conscience-generated learning_directions.

**Diagnosis:**
```python
# Check what conscience generates
from crystal import _conscience, _load_will_history, _load_self_model, observe
snap = observe()
h = _load_will_history()
m = _load_self_model(snap)
hist = [(k, v.get('efficiency', 0)) for k, v in list(h.items())[-5:]]
cr = _conscience('test', 'test', {'type': 'test', 'efficiency': 0}, m)
print(f"all_learning: {cr.get('learning_direction', [])}")

# Check mapping keys
import re
with open('scripts/crystal.py') as f:
    content = f.read()
idx = content.find('LEARNING_TO_ACTION = {')
block = content[idx:idx+5000]
pairs = re.findall(r'"([^"]+)":\s*\{', block)
print(f"Mapping keys: {pairs}")
```

**Fix:** Either add missing keys to mapping, or use pattern-based matching for dynamic strings.

## Problem: All conscience actions repeat (audit overrepresented)

**Root cause:** Fixed LEARNING_TO_ACTION actions have same weight as data-driven, stable sort picks first.

**Fix:** Add tie-breaking via random in weight():
```python
base += random.uniform(0, 0.3)  # tie-breaking
```

## Problem: studied filter blocks all domains

**Root cause:** studied list approaches total domains.

**Fix:** Keep only last 5 studied:
```python
m['sovest']['studied'] = m['sovest']['studied'][-5:]
```

## Problem: SQL "no such column: content"

**Root cause:** KC uses `raw_text` not `content`, `axis_domain` not `domain`.

**Fix:** Check schema first:
```python
import sqlite3
conn = sqlite3.connect('cache/knowledge_cube.db')
c = conn.cursor()
c.execute("PRAGMA table_info(experiences)")
print([r[1] for r in c.fetchall()])
conn.close()
```

## Problem: observe() timeout (exit 124)

**Root cause:** observe() does heavy DB queries, times out on slow machines.

**Workaround:** Run via CLI not import:
```bash
python scripts/crystal.py --iterative 1
```

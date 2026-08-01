# Integration — Connect Everything to Real Data

## The Problem

I created isolated demos with their own databases.
They didn't connect to Knowledge Cube, Lavra, or sessions.
They were "cool code" that did nothing useful.

## The Solution

Every new system MUST connect to existing data sources.

## Real Data Sources

### Knowledge Cube
- Path: `cache/knowledge_cube.db`
- Table: `experiences` (619 records)
- Columns: raw_text, tags, axis_domain, axis_outcome
- Search: `WHERE raw_text LIKE '%query%' OR tags LIKE '%query%'`

### Lavra Knowledge
- Path: `data/lavra_knowledge.jsonl`
- Format: JSON lines (each line is a JSON string)
- Fields: type, content, domain
- Types: DECISION, LEARNED, FACT, PATTERN

### Session Database
- Path: `state.db`
- Tables: sessions, messages
- Full history of all conversations

## Integration Pattern

```python
from pathlib import Path
import sqlite3
import json

HERMES_HOME = Path("D:/Portable_Soft/hermes")
KNOWLEDGE_CUBE = HERMES_HOME / "cache" / "knowledge_cube.db"
LAVRA_KNOWLEDGE = HERMES_HOME / "data" / "lavra_knowledge.jsonl"

class RealSystem:
    def __init__(self):
        # Connect to REAL data
        self.kc = sqlite3.connect(str(KNOWLEDGE_CUBE))
        self.kc.row_factory = sqlite3.Row
        
        # Load REAL Lavra
        self.lavra = []
        with open(LAVRA_KNOWLEDGE, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    self.lavra.append(json.loads(line.strip().strip('"')))
                except:
                    pass
    
    def search(self, query):
        results = []
        
        # Search Knowledge Cube
        rows = self.kc.execute(
            "SELECT * FROM experiences WHERE raw_text LIKE ?",
            (f'%{query}%',)
        ).fetchall()
        for row in rows:
            results.append({'source': 'kc', 'content': row['raw_text'][:200]})
        
        # Search Lavra
        for entry in self.lavra:
            if query.lower() in entry.get('content', '').lower():
                results.append({'source': 'lavra', 'content': entry['content'][:200]})
        
        return results
```

## Verification

After creating any system, verify it connects to real data:

```bash
python -c "
import sqlite3
conn = sqlite3.connect('cache/knowledge_cube.db')
count = conn.execute('SELECT COUNT(*) FROM experiences').fetchone()[0]
print(f'Knowledge Cube: {count} records')
assert count > 0, 'NOT CONNECTED TO REAL DATA'
print('✓ Connected to real data')
"
```

## Anti-Patterns

### BAD: Isolated Demo
```python
class DemoSystem:
    def __init__(self):
        self.db = sqlite3.connect('demo.db')  # WRONG: isolated database
        self.db.execute('CREATE TABLE ...')    # WRONG: creating new tables
```

### GOOD: Integrated System
```python
class RealSystem:
    def __init__(self):
        self.kc = sqlite3.connect('cache/knowledge_cube.db')  # RIGHT: existing data
        self.lavra = load('data/lavra_knowledge.jsonl')        # RIGHT: existing data
```

## Key Insight

If your new system has its own database that nothing else reads → it's a demo.
If your new system reads from existing databases → it's integrated.

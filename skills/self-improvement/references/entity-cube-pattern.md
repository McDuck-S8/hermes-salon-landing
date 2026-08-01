# Entity Cube — Pattern for Building Knowledge Cubes

## Когда применять
Когда нужно создать новый куб данных в системе Hermes (четвёртый куб, специализированный куб для отслеживания чего-либо).

## Трёхслойная архитектура куба

### Слой 1: Schema (SQLite)
```sql
-- 1. Taxonomy table — defines types/categories
CREATE TABLE IF NOT EXISTS entity_types (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    color TEXT,
    description TEXT
);

-- 2. Core data table — the main entities
CREATE TABLE IF NOT EXISTS entities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    type_id TEXT NOT NULL,
    first_seen_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_seen_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    mention_count INTEGER DEFAULT 1,
    cumulative_tone REAL DEFAULT 0.0,
    FOREIGN KEY (type_id) REFERENCES entity_types(id)
);

-- 3. Relations table — links between entities
CREATE TABLE IF NOT EXISTS relationships (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_entity_id INTEGER NOT NULL,
    target_entity_id INTEGER NOT NULL,
    relation_type TEXT NOT NULL,
    strength REAL DEFAULT 0.3,
    occurrence_count INTEGER DEFAULT 1,
    FOREIGN KEY (source_entity_id) REFERENCES entities(id),
    FOREIGN KEY (target_entity_id) REFERENCES entities(id),
    UNIQUE(source_entity_id, target_entity_id, relation_type)
);

-- 4. Mentions table — links to source data (sessions, files, etc.)
CREATE TABLE IF NOT EXISTS entity_mentions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_id INTEGER NOT NULL,
    session_id TEXT,
    context TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (entity_id) REFERENCES entities(id)
);
```

### Слой 2: Extraction + Storage
```python
# 1. Define entity/pattern dictionaries
TOOL_PATTERNS = [r'\b(?:python|docker|git)\b']
ENTITY_TYPES = {"tool": {}, "person": {}, "project": {}}

# 2. Extract entities from text
def extract_entities_from_message(text: str) -> list[dict]:
    entities = []
    # Pattern-based extraction
    for pattern in TOOL_PATTERNS:
        for match in re.finditer(pattern, text):
            entities.append({
                "name": match.group(0),
                "type": classify(match.group(0)),
                "confidence": 0.8
            })
    # Deduplicate by name+type
    # Return unique entities

# 3. Detect relationships (co-occurrence)
def detect_relationships(entities: list[dict]) -> list[dict]:
    # All pairs in same message/session
    relationships = infer_relation_type(e1, e2, text)
    return relationships

# 4. Save to DB
def save_session(session_id: str, result: dict):
    conn = init_db()
    for entity in result["entities"]:
        # Upsert entity
        # Insert mention
        # Upsert session profile
    # Save relationships with strength aggregation
    conn.commit()
```

### Слой 3: CLI + Batch
```python
# CLI commands:
if cmd == "demo":     # Run on sample data
elif cmd == "analyze": # Run on a file
elif cmd == "stats":   # Cube statistics
elif cmd == "graph":   # Relationship graph JSON

# Batch script:
# 1. Connect to state.db
# 2. Get all sessions
# 3. For each session: get messages → analyze → save
# 4. Report summary
```

## Пример: Entity Cube (`projects/entity-engine/entity_engine.py`)

- 10 entity types (person, tool, project, concept, domain, technology, platform, language, location, organization)
- 5 relation types (uses, works_with, belongs_to, related_to, co_occurs_with)
- 547 entities, 11,706 relationships (seed data from session analysis)
- CLI: demo | analyze FILE | stats | graph

## Pitfalls

1. **DB_PATH resolution** — Use `os.environ.get("HERMES_HOME", os.path.expanduser("~/.hermes"))` not hardcoded paths
2. **Deduplication** — Entities need `name.lower()` dedup to avoid duplicates from case variations
3. **Relation strength** — Base on co-occurrence count with cap at 1.0: `strength = min(1.0, count * 0.2)`
4. **Session-based batch** — `state.db` can reach 346MB+ → batch scripts need limits (cap at N sessions) or timeout handling
5. **Pattern ordering** — More specific patterns first, generic patterns last to avoid misclassification

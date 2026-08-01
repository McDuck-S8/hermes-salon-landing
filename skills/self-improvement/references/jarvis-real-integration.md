# JARVIS Real — Integration Guide

## Connected Systems

### Knowledge Cube (619 experiences)
- Location: `cache/knowledge_cube.db`
- Table: `experiences` (id, ts, raw_text, hash, axis_domain, axis_outcome, tags)
- Search: `WHERE raw_text LIKE ? OR tags LIKE ?`
- Note: column is `raw_text`, not `content`

### Lavra Knowledge (217 entries)
- Location: `data/lavra_knowledge.jsonl`
- Format: escaped JSON strings (each line is `"json_string"`)
- Parse: `json.loads(json.loads(line))` — two layers of parsing
- Fields: key, type, content, source, tags, ts, bead

### Session Database
- Location: `state.db`
- Tables: sessions, messages, FTS5 index

## Usage Example

```python
from scripts.jarvis_real import JARVISReal

jarvis = JARVISReal()

# Recall from real data
results = jarvis.recall("salon", top_n=5)

# Each result has:
# - source: 'knowledge_cube' or 'lavra'
# - content: raw_text (truncated to 500 chars)
# - domain: axis_domain (for knowledge_cube)
# - outcome: axis_outcome (for knowledge_cube)
# - tags: JSON string (for knowledge_cube)
# - when: timestamp
```

## Common Queries

### Find salon bot work
```python
jarvis.recall("salon")  # finds salon-related experiences
jarvis.recall("hairdresser")  # finds salon work in Russian
```

### Find deployment issues
```python
jarvis.recall("deploy")  # finds deployment records
jarvis.recall("ошибка")  # finds error records in Russian
```

### Find Lavra decisions
```python
jarvis.recall("agent")  # finds agent-related Lavra entries
jarvis.recall("architecture")  # finds architecture decisions
```

## Pitfalls

1. **Lavra JSON is double-escaped**: Each line is `"escaped_json"`, 
   not `{"key": "value"}`. Must parse twice.

2. **Knowledge Cube columns differ**: Use `raw_text`, not `content`.
   Use `ts`, not `created_at`.

3. **Tags are JSON strings**: In Knowledge Cube, tags is a JSON string,
   not a list. Search with `LIKE`, not array operations.

4. **Recent sessions may be 0**: Sessions DB may not have recent data
   depending on when it was last updated.

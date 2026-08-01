# Lavra Memory System

Persistent knowledge base for Hermes Agent. Stores learned facts, decisions,
patterns, and investigations as searchable JSONL entries with optional SQLite
FTS5 indexing for fast full-text search.

## Location

All files live in `D:\Portable_Soft\hermes\data\lavra-memory\`:

| File | Purpose |
|------|---------|
| `knowledge.jsonl` | Main knowledge base (JSONL format, 1 entry per line) |
| `recall.sh` | Search/query script |
| `knowledge-db.sh` | SQLite FTS5 library (sourced by recall.sh) |
| `lavra.json` | Lavra workflow config |

## Usage

### Search by keyword
```bash
bash D:/Portable_Soft/hermes/data/lavra-memory/recall.sh "keyword"
```

### Search with type filter
```bash
bash D:/Portable_Soft/hermes/data/lavra-memory/recall.sh "keyword" --type learned
bash D:/Portable_Soft/hermes/data/lavra-memory/recall.sh "keyword" --type decision
bash D:/Portable_Soft/hermes/data/lavra-memory/recall.sh "keyword" --type fact
bash D:/Portable_Soft/hermes/data/lavra-memory/recall.sh "keyword" --type pattern
```

### Show recent entries
```bash
bash D:/Portable_Soft/hermes/data/lavra-memory/recall.sh --recent 10
```

### Knowledge base stats
```bash
bash D:/Portable_Soft/hermes/data/lavra-memory/recall.sh --stats
```

### Filter by topic (requires bd CLI)
```bash
bash D:/Portable_Soft/hermes/data/lavra-memory/recall.sh --topic BD-005
```

## Knowledge Entry Format

Each line in `knowledge.jsonl` is a JSON object:
```json
{
  "key": "unique-key",
  "type": "learned|decision|fact|pattern|investigation",
  "content": "The actual knowledge text",
  "source": "source identifier",
  "tags": ["tag1", "tag2"],
  "ts": 1234567890,
  "bead": "bead-id"
}
```

### Entry Types
- **learned** - Things learned during development
- **decision** - Architectural or design decisions made
- **fact** - Verified facts about the system
- **pattern** - Recurring patterns observed
- **investigation** - Research findings

## Adding Knowledge

Append a new JSONL line to `knowledge.jsonl`:
```bash
echo '{"key":"my-fact-001","type":"fact","content":"Hermes uses bash on Windows","source":"hermes","tags":["setup","windows"],"ts":'$(date +%s)'}' >> D:/Portable_Soft/hermes/data/lavra-memory/knowledge.jsonl
```

## SQLite FTS5 Index (Optional)

For faster searches on large knowledge bases, recall.sh will automatically
use SQLite FTS5 if `sqlite3` is available and `knowledge.db` exists.

To create/sync the index:
```bash
source D:/Portable_Soft/hermes/data/lavra-memory/knowledge-db.sh
kb_sync "D:/Portable_Soft/hermes/data/lavra-memory/knowledge.db" "D:/Portable_Soft/hermes/data/lavra-memory"
```

## Path Configuration

The scripts use `CLAUDE_PROJECT_DIR` env var if set, otherwise default to
the script's own directory. No path adjustments needed for Hermes usage.

## Dependencies

- bash
- jq (for JSON parsing)
- sqlite3 (optional, for FTS5 index)

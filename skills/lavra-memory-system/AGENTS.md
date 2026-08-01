# AGENTS.md — lavra-memory-system

## Purpose
Persistent knowledge base for Hermes Agent. Stores learned facts, decisions, patterns, and investigations as searchable JSONL entries with optional SQLite FTS5 indexing for fast full-text search. Provides CLI tools (recall.sh, knowledge-db.sh) for querying and managing the knowledge base.

## Ownership
Owner: Hermes Agent (Lavra workflow system)
Category: self-improvement / knowledge-management
Location: D:\Portable_Soft\hermes\data\lavra-memory\
Status: Active production system

## Local Contracts
### Triggers (from SKILL.md)
- Need to search knowledge base by keyword
- Need to filter by entry type (learned, decision, fact, pattern, investigation)
- Need to show recent entries
- Need knowledge base statistics
- Need to add new knowledge entries
- Need to sync SQLite FTS5 index for performance

### Required Tools
- bash (shell execution)
- jq (JSON parsing)
- sqlite3 (optional, for FTS5 indexing)
- File I/O for knowledge.jsonl

### Config References
- D:\Portable_Soft\hermes\data\lavra-memory\knowledge.jsonl — main knowledge base
- D:\Portable_Soft\hermes\data\lavra-memory\recall.sh — search/query script
- D:\Portable_Soft\hermes\data\lavra-memory\knowledge-db.sh — SQLite FTS5 library
- D:\Portable_Soft\hermes\data\lavra-memory\lavra.json — Lavra workflow config
- CLAUDE_PROJECT_DIR env var (optional path override)

## Work Guidance
### When to Use
- Storing learned facts, architectural decisions, verified facts, recurring patterns, research findings
- Searching existing knowledge before starting new investigations
- Building institutional memory across sessions
- Fast full-text search over large knowledge bases (via SQLite FTS5)

### Common Patterns (from SKILL.md)
1. **Search by keyword**: `bash recall.sh "keyword"`
2. **Search with type filter**: `bash recall.sh "keyword" --type learned|decision|fact|pattern|investigation`
3. **Show recent entries**: `bash recall.sh --recent 10`
4. **Knowledge base stats**: `bash recall.sh --stats`
5. **Filter by topic**: `bash recall.sh --topic BD-005` (requires bd CLI)
6. **Add knowledge**: Append JSONL line to knowledge.jsonl
7. **Sync FTS5 index**: `source knowledge-db.sh && kb_sync "knowledge.db" "."`

### Entry Format (JSONL)
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

## Verification
### Test Strategy
- Check for test scripts in skill directory: `ls scripts/ tests/ evals/` → none exist in skill dir (scripts in data/lavra-memory/)
- Verify system works by:
  1. Running `bash recall.sh --stats` — should show entry count
  2. Running `bash recall.sh "test"` — should search without error
  3. Running `bash recall.sh --recent 5` — should show recent entries
  4. Adding entry and verifying it appears in search
  5. Syncing FTS5 index and verifying faster search

### Validation Commands
```bash
# Test basic functionality
bash D:/Portable_Soft/hermes/data/lavra-memory/recall.sh --stats

# Test search
bash D:/Portable_Soft/hermes/data/lavra-memory/recall.sh "Hermes"

# Test type filter
bash D:/Portable_Soft/hermes/data/lavra-memory/recall.sh "decision" --type decision

# Test recent
bash D:/Portable_Soft/hermes/data/lavra-memory/recall.sh --recent 5

# Sync FTS5 index (if sqlite3 available)
source D:/Portable_Soft/hermes/data/lavra-memory/knowledge-db.sh
kb_sync "D:/Portable_Soft/hermes/data/lavra-memory/knowledge.db" "D:/Portable_Soft/hermes/data/lavra-memory"
```

## Child DOX Index
### References
- (none in skill directory — references are in data/lavra-memory/)

### Templates
- (none in skill directory)

### Scripts
- (none in skill directory — scripts are in data/lavra-memory/):
  - recall.sh — search/query CLI
  - knowledge-db.sh — SQLite FTS5 library

### Related Skills
- lavra-knowledge (capture solved problems as knowledge entries)
- persistent-memory (file-based cross-session memory)
- three-layer-memory (FTS5 keyword search for Knowledge Cube)
- crystal-self-learning (Crystal system learning modules)
- self-improvement (self-improvement protocols)
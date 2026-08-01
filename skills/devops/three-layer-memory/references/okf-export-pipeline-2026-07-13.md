# OKF Export Pipeline — Implementation Notes (2026-07-13)

## Overview

Full OKF SPEC v0.1 export pipeline built on top of OKF-Lite (3 SQL columns: confidence, expiration_date, verification_method). The Knowledge Cube now exports to a disk-based markdown bundle at `knowledge/okf/` with every mutation synced live.

## Architecture

```
kc_rag.upsert(content, ...)
    │
    ├─► SQLite: kc_entries (fast query)
    │
    └─► OKF bundle: knowledge/okf/knowledge/{category}/{hash}.md
         ├─ YAML frontmatter (type, tags, confidence, expiration_date, verification_method)
         ├─ Body (markdown)
         │
         └─ log.md append: "| {timestamp} | UPSERT | {id} | {source}/{category} |"

migrate_kc_to_okf.py --export
    │
    ├─► Reads all kc_entries + experiences tables
    ├─► Groups by category/axis_domain → subdirectories
    ├─► Writes one .md file per concept
    ├─► Generates index.md per directory
    ├─► Generates root index.md with section overview
    └─► Generates log.md with export event
```

## Bundle Structure

```
knowledge/okf/
├── index.md                           # Root index — links to all sections
├── log.md                             # Change log (OKF SPEC §7)
├── knowledge/                         # kc_entries concepts
│   ├── {category}/
│   │   ├── index.md                   # Directory index with concept links
│   │   └── {hash}.md                  # One concept file
│   │   └── ...
│   └── ...
└── experiences/                       # experiences concepts (from Knowledge Cube)
    ├── {axis_domain}/
    │   ├── index.md
    │   ├── {hash}.md
    │   └── ...
    └── ...
```

## Commands

```
# Full export (one-shot, rebuilds entire bundle)
python scripts/migrate_kc_to_okf.py --export

# Validate bundle against OKF SPEC v0.1
python scripts/migrate_kc_to_okf.py --validate

# Both
python scripts/migrate_kc_to_okf.py --export --validate
```

## Live Sync

`kc_rag.upsert()` automatically writes/updates the corresponding `.md` file after every DB write. The sync is wrapped in try/except so DB writes succeed even if the filesystem write fails.

```python
from kc_rag import upsert

# This writes to both SQLite AND the OKF bundle
eid = upsert(
    content="Knowledge entry text",
    tags="example,test",
    source="system",
    category="architecture",
    importance=7,
    confidence=0.95,
    verification_method="automated",
    expiration_date="2026-12-31T23:59:59"
)
```

## Frontmatter Format

```yaml
---
type: architecture
title: "Knowledge entry title (first 80 chars)"
timestamp: 2026-07-13T12:00:00
confidence: 0.950
expiration_date: 2026-12-31T23:59:59
verification_method: automated
source_table: kc_entries
importance: 7
tags:
  - example
  - test
resource: system
---
```

## Tag Parsing

The `yaml_list()` function handles three tag formats from the DB:
1. Comma-separated: `"okf, google, knowledge-format"`
2. JSON list: `'["tool:web_search", "tool:terminal"]'`
3. Mixed: `'["complexity:low"], auto_tagged, auto_tagged'`

Filters out `auto_tagged`, `auto_tag`, duplicates, and strings > 80 chars.

## Changes to Scripts

### `scripts/migrate_kc_to_okf.py`
- Added: `OKF_BUNDLE_ROOT`, `OKF_SPEC_VERSION` constants
- Added: `yaml_list()` — tag parsing with JSON/comma/mixed support
- Added: `concept_to_md(row, source_table)` — converts DB row to OKF .md
- Added: `fetch_all_entries(conn)` — reads both kc_entries + experiences
- Added: `determine_subdir(entry)` — maps category/domain to directory
- Added: `okf_log_entry(path, action, concept_id, detail)` — log.md writer
- Added: `export_to_okf(conn, bundle_root)` — main export loop
- Added: `generate_index_md(dir_path, files, title)` — index.md generator
- Added: `validate_bundle(bundle_root)` — OKF SPEC v0.1 validation
- Added: CLI flags: `--export`, `--export-dir`, `--validate`
- Existing: `--status`, `--test` unchanged

### `scripts/kc_rag.py`
- Added: `OKF_BUNDLE_ROOT`, `OKF_LOG_PATH` constants
- Added: `okf_make_frontmatter()` — YAML frontmatter generator
- Added: `okf_determine_subdir(category)` — maps category to subdirectory
- Added: `okf_write_single(...)` — writes one concept .md file
- Added: `okf_delete_single(entry_id)` — removes concept from bundle
- Added: `okf_log_entry(action, concept_id, detail)` — live log.md append
- Modified: `upsert()` calls `okf_write_single()` after DB write

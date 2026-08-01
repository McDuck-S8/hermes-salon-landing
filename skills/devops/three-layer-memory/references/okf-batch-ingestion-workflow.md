# OKF Batch Ingestion Workflow

Domain research → OKF entries — the pattern for bulk-importing findings from web/GitHub research into the Knowledge Cube.

## Steps

1. **Define target domain** — pick the OKF domain (e.g. `referral-automation`)
2. **Batch-search** — `web_search` + `web_extract` for repos/pages, `site:github.com` targeted queries
3. **Extract per-finding** — id, title, tags, description with reference link + applicability assessment
4. **Bulk-create via `execute_code`** — call `kc_rag.upsert()` for each finding in one script

## kc_rag.upsert() API

```python
kc_rag.upsert(
    content="markdown body",          # Required. Full description + applicability
    tags="tag1, tag2, tag3",          # CRITICAL: must be a STRING (comma-sep), NOT a list
    source="github-research",          # Identifies the source batch
    category="",                       # Auto-detected from YAML tags
    importance=5, confidence=0.5,
    verification_method="manual"
)
```

## Pitfalls

- **tags parameter**: `upsert()` uses SQLite parameter binding — must be a string, not a Python list. `["tag1", "tag2"]` → `Error binding parameter 3: type 'list' is not supported`
- **okf_determine_subdir bug (fixed 2026-07-13)**: function returned `knowledge/{cat}` instead of `experiences/{cat}`. Verify with:
  ```python
  kc_rag.okf_determine_subdir('referral-automation')
  # Expected: 'experiences/referral-automation'
  ```
- **Events**: Each `upsert()` emits `knowledge_added` → auto-triggers `cube-categorizer`, `knowledge-gap-filler`, `okf-navigator` cron jobs — they run automatically, no manual action needed
- **Batch size**: 25-50 entries per `execute_code` script is fine; each upsert is fast (<100ms)

## Example Batch Structure

```python
records = [
    {"id": "ref-auto-example", "title": "Example finding", 
     "tags": "domain, relevant-tags", "body": "Description..."},
    # ... more records
]
for rec in records:
    kc_rag.upsert(content=rec["body"], tags=rec["tags"], source="github-research")
```

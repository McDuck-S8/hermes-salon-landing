# Knowledge Cube Domain Analysis

## Purpose

Analyze Knowledge Cube domain hierarchy — detect subdomains, noise domains (misclassified single-entry garbage), tag-to-domain anchors, and propose restructuring.

## DB Schema

**File:** `cache/knowledge_cube.db`
**Table:** `experiences` (not `knowledge_cube`)
**Key columns:**

| Column | Description | Example |
|--------|-------------|---------|
| `axis_domain` | Domain classification | `bugfix`, `coding`, `system` |
| `axis_outcome` | Outcome | `unknown`, `failure`, `success`, `indexed` |
| `source` | Origin script/system | `state_db`, `improvement_suggestions`, `skill-indexer` |
| `tags` | JSON array or string | `'["complexity:low", "tool:code"]'` |
| `dynamic_axes` | JSON with extra metadata | `{"feeder_source": "improvement_suggestions"}` |

## Analysis Methodology

### Phase 1: Domain distribution

```sql
SELECT axis_domain as domain, COUNT(*) as total,
  SUM(CASE WHEN axis_outcome='unknown' THEN 1 ELSE 0 END) as unknown,
  SUM(CASE WHEN axis_outcome='failure' THEN 1 ELSE 0 END) as failure,
  SUM(CASE WHEN axis_outcome='success' THEN 1 ELSE 0 END) as success,
  SUM(CASE WHEN axis_outcome='indexed' THEN 1 ELSE 0 END) as indexed
FROM experiences
WHERE axis_domain IS NOT NULL AND axis_domain != ""
GROUP BY axis_domain
ORDER BY total DESC
```

This reveals the real shape: ~96 domains, but 78 of them have only 1 entry — those are noise (misclassified single words treated as domains).

### Phase 2: Source distribution

Each domain has a characteristic `source` mix. Sources hint at the nature of entries:

- `state_db` = raw user conversations
- `improvement_suggestions` = auto-generated proposals (NOT errors)
- `skill-indexer` = indexing logs (low value, overwritten)
- `cube_analysis` = analysis results
- `lavra_decision` = Lavra framework decisions

### Phase 3: Tag → domain matrix

Extract tags from the `tags` column (JSON or comma-separated). Compute tag frequency per domain:

```python
from collections import Counter, defaultdict
domain_tag_counter = defaultdict(Counter)

for domain, tags_str in cursor:
    tags = json.loads(tags_str)  # or comma-split fallback
    for t in tags:
        domain_tag_counter[domain][t] += 1
```

Tags appearing in >15% of a domain's entries are **subdomain anchors** (e.g. `tool:code` → coding has sub-segments, `issue:log_unknown` → bugfix has automation-log subdomain).

### Phase 4: Noise detection

Domains with 1 entry are always noise — single words like `"your"`, `"backup"`, `"hermes"`, `"agent"` that got classified as domain names instead of content. **78 such domains** found in the 2148-entry cube.

Filter: `HAVING cnt = 1` — these need cleanup or reassignment.

### Phase 5: Small domain mergers

Domains with 2-29 entries may be legitimate subdomains that were separated incorrectly. Check their tags and sources against larger parent domains:

- `user-preference(11)` → belongs under `communication`
- `skill(24)` → belongs under `learning` as `learning-skills`
- `design(2)` → belongs under `creative`

### Phase 6: Hierarchy proposal

Group current flat domains into 6 top-level buckets with subdomains:

```
system-dev      coding + architecture + debugging
system-ops      devops + system + terminal
data-knowledge  research + data + learning + skill
communication   communication + file_ops + creative + user-preference
quality         bugfix (largest: 504 entries, needs 5+ subdomains)
automation      browser + tools
```

Each bucket gets ~30 subdomains total. The bugfix bucket alone should split into `bugfix-python`, `bugfix-js`, `bugfix-config`, `bugfix-network`, `bugfix-dependency`.

## Reusable Script

`scripts/_domain_analysis.py` — standalone Python script that runs all 6 phases. Reads from `cache/knowledge_cube.db`, outputs to stdout. Pipe to `reports/` for persistence:

```bash
cd /d/Portable_Soft/hermes
python scripts/_domain_analysis.py 2>&1 | tee reports/domain_hierarchy_analysis.txt
```

## Common Findings (June 2026)

| Finding | Count | Action |
|---------|-------|--------|
| Flat domains | 96 | Restructure to 6 groups |
| Noise domains (1 entry) | 78 | Clean or reassign |
| bugfix single largest | 504 (23.5%) | Split into 5 subdomains |
| file_ops mixed ops | 346 (16.1%) | Separate read/write/search |
| improvement_suggestions as "failure" | 329 | Reclassify to `proposal_rejected` |
| dynamic_axes filled | 2148 (100%) but 776 empty `{}` | Auto-fill on event write |

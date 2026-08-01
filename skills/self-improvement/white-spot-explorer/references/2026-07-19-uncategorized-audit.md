# White Spot Explorer — 2026-07-19 Uncategorized Audit Findings

## Discovery: Actual uncategorized count much lower than estimated

Estimated ~255. Actual: **41** in `experiences` + **26** in `kc_entries` = **67 total**.
Previous runs (auto_tagger, earlier white-spot-explorer) had already classified most.

## Critical Pattern: Tag/axis_domain Mismatch

**25 entries** in `experiences` had `tags = ["domain:coding", ...]` but `axis_domain IS NULL`.
This means `auto_tagger` and/or the ingestion pipeline sets the tag but doesn't sync `axis_domain`.
Fix SQL:
```sql
UPDATE experiences 
SET axis_domain = 'coding' 
WHERE (axis_domain IS NULL OR axis_domain = '' OR axis_domain = 'uncategorized')
  AND tags LIKE '%domain:coding%'
  AND tags NOT LIKE '%rejected-by-user%';
```

## Discovery: kc_entries table has its own uncategorized bucket

`kc_entries` is a separate table with `category` column (not `axis_domain`).
26 entries had `category IS NULL OR category = ''`.
Types found: Telegram bots, CPA landing pages, Docker bandwidth stacks, AI content factories.

## Discovery: Incomplete white_spot_clusters

16 clusters in `ws_*` format had `status='pending'` and `proposed_dimension IS NULL`.
These are from incomplete previous runs — registered but never classified.

## Cluster breakdown (experiences)

| Cluster | Count | Recommendation |
|---------|-------|---------------|
| coding-development | 18 | → `coding` (has domain:coding tag) |
| cpa-arbitrage | 11 | → `cpa-arbitrage` or `research` |
| testing | 3 | → `test` or delete (low value) |
| automation | 4 | → `devops` or `system` |
| ai-ml | 2 | → `research` |
| content-writing | 1 | → `ai-content-factory` |
| system | 1 | → `system` |

## Cluster breakdown (kc_entries)

| Cluster | Count | Recommendation |
|---------|-------|---------------|
| social-media | 7 | Telegram bots → `social-media` |
| cpa-arbitrage | 7 | CPA landing pages, Amazon Affiliate |
| devops | 4 | Docker stacks, URL shorteners |
| ai-content-factory | 3 | AI content generation |
| needs review | 4 | MLM, passive income lists, URL shorteners |

## Key Insight: No new domains needed

All 67 entries fit into existing ~40 domains. The problem was sync (tag→axis_domain), not missing categories.

---
name: knowledge-cube-gap-patch
description: Clean knowledge_cube.db — classify white spots, tag/confidence-bulk-update records, create deferred tasks. Run after scheme rejections or before major strategy shifts.
version: "1.0"
tags: [knowledge-cube, gap-patch, cleanup, classification, cpa]
---

# Knowledge Cube Gap-Patch

## When to Use

- User rejects categories of records (e.g., all CPA schemes)
- White spots pile up and need classification
- Before a major strategy shift — clean the knowledge base first
- Average confidence drifts and needs recalibration

## Process

### 0. Source Distribution Audit (перед любыми изменениями)

Первый шаг — понять ЧЕМ забит experiences.

```sql
-- Источники
SELECT source, COUNT(*) FROM experiences GROUP BY source ORDER BY COUNT(*) DESC;
```

**Красный флаг:** если `improvement_suggestions` > 50% — куб забит авто-логами, не фактами.

```sql
-- Процент мусора
SELECT ROUND(100.0 * SUM(CASE WHEN source = 'improvement_suggestions' THEN 1 ELSE 0 END) / COUNT(*), 1) 
FROM experiences;
```

**Если мусора > 50%: создать clean_facts view**
```sql
CREATE VIEW IF NOT EXISTS clean_facts AS
SELECT * FROM experiences WHERE source IN (
  'rss_partnerkin', 'rss_affiliatefix', 'rss_reddit_affiliatemarketing',
  'rss_hackernews', 'youtube_easy_traff', 'youtube_partnerkin',
  'ripple_engine', 'agent_decisions', 'user_voice',
  'email', 'cube_analysis', 'gap_filler'
);
```

**Проверить kc_entries (проверенный куб):**
```sql
SELECT source, COUNT(*) FROM kc_entries GROUP BY source ORDER BY COUNT(*) DESC;
```

**Поиск по нишам — считает реальные упоминания:**
```sql
SELECT 'трафик', COUNT(*) FROM experiences WHERE content LIKE '%трафик%' OR content LIKE '%traf%'
UNION ALL
SELECT 'cpa/офферы', COUNT(*) FROM experiences WHERE content LIKE '%cpa%' OR content LIKE '%CPA%' OR content LIKE '%оффер%'
UNION ALL
SELECT 'креативы', COUNT(*) FROM experiences WHERE content LIKE '%креатив%' OR content LIKE '%creativ%';
```
Если упоминания ниши < 5% от всех записей — wheel будет показывать шум.

### 1. Understand the Scope

Query the DB at `cache/knowledge_cube.db`:

```sql
-- Total records
SELECT COUNT(*) FROM experiences;

-- White spots
SELECT COUNT(*) FROM experiences WHERE is_white_spot = 1;

-- White spots by cluster
SELECT white_spot_cluster_id, COUNT(*), ROUND(AVG(confidence), 4) 
FROM experiences WHERE is_white_spot = 1 
GROUP BY white_spot_cluster_id ORDER BY COUNT(*) DESC;

-- Target records (e.g., CPA)
SELECT COUNT(*) FROM experiences 
WHERE (content LIKE '%CPAGrip%' OR content LIKE '%ogads%' OR ...)
  AND tags NOT LIKE '%rejected-by-user%';
```

### 2. Check Tags Format

Tags column may contain raw strings (not JSON arrays). Verify:

```sql
SELECT id, tags FROM experiences LIMIT 5;
```

**If tags are raw strings** (e.g., `has_source, verified`):
- Cannot use `json_set()` — will get "malformed JSON"
- Use string concatenation instead: `CASE WHEN tags IS NULL OR tags = '' THEN 'new-tag' ELSE tags || ', new-tag' END`

**If tags contain trailing garbage** (e.g., `[], auto_tagged, auto_tagged`):
- Strip first: `UPDATE experiences SET tags = substr(tags, 1, instr(tags, '],') + 1) WHERE tags LIKE '%], auto_tagged%';`

### 3. Bulk-Update Rejected Records

```sql
UPDATE experiences 
SET 
  confidence = 0.3,
  importance = 0.3,
  tags = CASE 
    WHEN tags IS NULL OR tags = '' THEN 'rejected-by-user' 
    ELSE tags || ', rejected-by-user' 
  END
WHERE <condition matching rejected schemes>
  AND is_white_spot = 0
  AND tags NOT LIKE '%rejected-by-user%';
```

### 4. Classify White Spots

Group by `white_spot_cluster_id`:

| Pattern | Status | Action |
|---------|--------|--------|
| `auto-seeded` / `ws_abe1d41c` | Garbage (auto-generated placeholders, conf~0.5) | Delete after user confirmation |
| `knowledge_domains` | Genuine content areas | Ask user if relevant |
| `skill_domain_mappings` / `ws_bc87e17d` | Trivially correct facts (skill→domain) | Raise to conf 1.0 |
| `session_dumps` / conventions | Technical metadata | Leave as-is |
| `human_domain_analysis` | Analysis records | Ask user |

### 5. Verify Results

```sql
-- Summary
SELECT 'total_rejected', COUNT(*) FROM experiences WHERE tags LIKE '%rejected-by-user%';
SELECT 'white_spots', COUNT(*) FROM experiences WHERE is_white_spot = 1;
SELECT 'avg_confidence', ROUND(AVG(confidence), 4) FROM experiences;
SELECT 'avg_confidence_clean', ROUND(AVG(confidence), 4) FROM experiences WHERE tags NOT LIKE '%rejected-by-user%';
```

### 6. Create Deferred Tasks

For records requiring external access (VPN, paid tools, etc.), create a task file:

```
knowledge/okf/deferred-tasks/<task-name>.md
```

Format:
```markdown
# Deferred Tasks — Requires <resource>

## [N] <Task name>
**Tags:** #requires-vpn #gap-patch #<domain>

**What needs to be done:**
...
```

Also add to DB as a white spot with the tag.

## Pitfalls

- **DO check source distribution first** — если improvement_suggestions > 50%, любые изменения бесполезны пока не создан clean_facts
- **DO NOT trust wheel output without clean data** — fractal-wheel читает experiences (12k+), где 71% могут быть авто-логами. Результат будет шумом.
- **DO NOT delete "not yet checked" records without user confirmation** — sort into categories first
- **DO NOT use json_set() on tags** — they're raw strings, not JSON arrays
- **DO trust the safety guard** on destructive actions — ask before DELETE
- **DO run pytest** after SQL changes on non-SQL files to confirm nothing broke
- **DO verify all URLs** before presenting data to user (trust was damaged by fincpa.com incident)
- **DO save as skill** after first successful gap-patch run

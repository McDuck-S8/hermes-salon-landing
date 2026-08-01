---
name: human-domain-gap-analysis
description: Detect missing human-centric domains in Knowledge Cube, add them to domain_definitions.yaml, reclassify entries, register as white spots
category: self-improvement
---

# Human Domain Gap Analysis

Use when: Knowledge Cube has only technical domains, human-centric info is being lost.

## Trigger
- User asks about missing categories/domains in cube
- Analysis shows entries with tags for domains that don't exist as axis_domain
- New info arrives that doesn't fit existing technical domains

## Key Principle
Новая инфа без категории = white spot = надо создать ящик и наполнить.

## Steps

### 1. Detect gaps
```sql
-- Check what domain:XXX values exist in tags but NOT as axis_domain
SELECT DISTINCT axis_domain FROM experiences;
-- Compare against tags containing 'domain:' or 'category:'
```

### 2. Add missing domains to domain_definitions.yaml
- Add new domain block with:
  - description (Russian + English)
  - keywords (Russian + English)
  - exclude_keywords (if needed to avoid false positives with technical domains)
- Include both Russian and English keywords for better coverage

### 3. Reclassify existing entries
```bash
python scripts/auto_tagger.py --force
```

### 4. Register as white spots
Insert into `white_spot_clusters` table:
- cluster_id: `human-domain-{name}`
- proposed_dimension: `{name}`
- status: 'developing' if entries exist, 'pending' if empty

### 5. Seed empty domains
If a domain has 0 entries:
- Record `on_task_complete` with tags for that domain
- Use skills that belong to that domain (e.g. earning-with-ai → business-marketing)
- Delegate agent to explore and fill knowledge

### 6. DO NOT write scripts by hand
- Use `delegate_task` for any script creation
- Create skill first if workflow is new
- Everything through skills pipeline

## Files
- `config/domain_definitions.yaml` → `domain_definitions` — domain keywords
- `cache/knowledge_cube.db` → `white_spot_clusters` table
- `scripts/auto_tagger.py` — reclassification
- `scripts/knowledge_cube.py` — query/seed functions

## Pitfalls
- Don't just analyze — DO. Create the box, fill it.
- Include BOTH language keywords (ru + en) for human domains
- business-marketing needs explicit seeding — keywords alone won't match existing entries
- auto_tagger only uses keyword matching — if keywords are too generic, it over-classifies
- **Never ask "do you want me to run this?"** — POLICY 20: autonomous execution. Run auto_tagger --force, seed, register white spots. Report after.

## Working recipe (validated 2026-07-04)

### 1. Detect missing human domains
```python
# Compare axis_domain vs tags domain:XXX vs skill categories vs domain_definitions.yaml
# Human domains to ensure exist: social-media, finance, health-fitness, entertainment,
# smart-home, business-marketing, music-audio, video-content, education, lifestyle, productivity
```

### 2. Ensure domains exist in domain_definitions.yaml
```yaml
# All 11 human domains must be present with ru+en keywords
# If missing → add to YAML, then run step 3
```

### 3. Reclassify existing entries
```bash
python scripts/auto_tagger.py --force
# Result: 1371/1522 reclassified in 2s
```

### 4. Seed empty domains from skills
```python
# Map skill → domain, insert seed experiences
skill_to_domain = {
    'stocks': 'finance', 'excel-author': 'finance', 'pptx-author': 'finance',
    'earning-with-ai': 'business-marketing', 'polymarket': 'finance',
    'fitness-nutrition': 'health-fitness', 'pokemon-player': 'entertainment',
    'openhue': 'smart-home', 'spotify': 'music-audio', 'heartmula': 'music-audio',
    'songsee': 'music-audio', 'youtube-content': 'video-content', 'ascii-video': 'video-content',
    'arxiv': 'education', 'llm-wiki': 'education', 'obsidian': 'lifestyle',
    'notion': 'productivity', 'linear': 'productivity', 'airtable': 'productivity',
    'google-workspace': 'productivity', 'project-planner': 'productivity',
    'telegram-bot-integration': 'social-media', 'telegram-service-bot': 'social-media',
    'agent-browser': 'social-media',
}
# Insert into experiences table with axis_domain, tags=['skill', 'domain:X', 'seeded']
```

### 5. Register white spot clusters
```sql
INSERT OR IGNORE INTO white_spot_clusters
(cluster_id, formed_at, size, representative_text, proposed_dimension, status)
VALUES ('human-domain-{name}', now(), {cnt}, 'Seeded human domain: {name}', '{name}', 
        CASE WHEN {cnt}>0 THEN 'developing' ELSE 'pending' END);
```

### 6. Verify
```bash
python -c "
import sqlite3
db = sqlite3.connect('cache/knowledge_cube.db')
c = db.cursor()
c.execute('SELECT axis_domain, COUNT(*) FROM experiences GROUP BY axis_domain ORDER BY COUNT(*) DESC')
for r in c.fetchall(): print(f'{r[0]:<25} {r[1]}')
"
```

Expected: all 11 human domains appear with counts >0.

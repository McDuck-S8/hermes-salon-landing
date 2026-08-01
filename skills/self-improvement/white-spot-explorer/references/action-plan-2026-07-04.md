# Action Plan: Reclassify & Register White Spots

## Pending (run in next session)

### 1. Run auto_tagger to populate domains
```bash
python D:/Portable_Soft/hermes/scripts/auto_tagger.py --force
```

### 2. Verify reclassification
```bash
python -c "
import sqlite3
db = sqlite3.connect('cache/knowledge_cube.db')
c = db.cursor()
c.execute('SELECT axis_domain, COUNT(*) FROM experiences GROUP BY axis_domain ORDER BY COUNT(*) DESC')
for r in c.fetchall():
    print(f'{r[0]:<30} {r[1]}')
"
```

### 3. Register white spots for empty domains
```python
import sqlite3, uuid
from datetime import datetime

db = sqlite3.connect('cache/knowledge_cube.db')
c = db.cursor()

empty_domains = [
    'social-media', 'finance', 'health-fitness', 'entertainment',
    'smart-home', 'business-marketing', 'music-audio', 'video-content',
    'education', 'lifestyle', 'productivity',
    'architecture', 'bugfix', 'learning', 'coding', 'debugging',
    'devops', 'research', 'data', 'terminal', 'uncategorized'
]

for dom in empty_domains:
    c.execute('''
        INSERT OR IGNORE INTO white_spot_clusters
        (cluster_id, formed_at, size, representative_text, proposed_dimension, status)
        VALUES (?, datetime('now'), 0, ?, ?, ?)
    ''', (f'human-domain-{dom}', f'empty domain {dom}', dom, 'pending'))

db.commit()
print(f'Registered {len(empty_domains)} white spots')
```

### 4. Seed priority domains from skills/conversations
Priority order (highest ROI for arbitrage):
1. **finance** — stocks, excel-author, earning-with-ai, polymarket skills exist
2. **social-media** — telegram-bot-integration, agent-browser skills
3. **productivity** — notion, linear, airtable, google-workspace skills
4. **business-marketing** — earning-with-ai skill
5. **video-content** — youtube-content, ascii-video skills
6. **education** — arxiv, llm-wiki skills

### 5. Trigger white-spot-explorer on top 3
```python
# For each priority domain, run exploration via opencode.ai/zen/v1
# Record findings in KC with tags: domain:finance, white-spot, exploration
```

## Expected Outcome After Auto-tagger
- communication: ~1000 (telegram, discord, slack, email, webhook, api)
- creative: ~400 (design, visualization, video, animation)
- file_ops: ~20 (read, write, open, save, directory, path)
- social-media: ~50+ (from telegram, channel, post, tg, chat keywords)
- finance: ~30+ (from money, payment, revenue, crypto, stock, earning)
- devops: ~20+ (deploy, server, docker, cron, service, daemon)
- coding: ~15+ (function, class, implement, refactor, algorithm)
- ...others emerging from keyword matches

## Notes
- auto_tagger uses keyword matching from domain_definitions.yaml
- Russian + English keywords both needed for human domains
- After reclassification, white_spot_explorer can explore high-value domains
- Finance + social-media + productivity = core arbitrage knowledge
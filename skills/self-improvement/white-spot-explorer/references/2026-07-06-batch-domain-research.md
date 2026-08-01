# 2026-07-06 Batch Domain Research — 7 Domains in One Session

## Overview
Executed complete white-spot-explorer workflow for 7 new human domains in a single session. Total cost: ~$0.004, time: ~3 minutes.

## Domains Researched

| Domain | Key Focus | Arbitrage Application |
|--------|-----------|----------------------|
| advanced-analytics | Bayesian A/B testing, sequential testing, hierarchical models, power analysis | Rigorous test design for arbitrage schemes |
| behavioral-psychology | Cognitive biases, neuromarketing, Cialdini/Fogg/Hook, ethical persuasion | Conversion optimization, funnel psychology |
| organic-traffic | SEO clusters, YouTube/Pinterest SEO, AI content, 1→10+ repurposing | Free traffic for CPA funnels |
| crypto-web3 | DeFi primitives, staking/restaking, MEV, cross-chain, stablecoin yields | DeFi yield, MEV arb, funding rate arb |
| ai-content-factory | Local SD/Flux/video, ComfyUI, quantization, automation, business models | Content generation for Content-Locking-CPA, Shorts |
| b2b-sales | Cold email, SPIN/MEDDIC, demo, pricing, LAER objections, closing | Direct bot/template sales, partnership outreach |
| referral-automation | Travelpayouts, SaaS affiliates, crypto exchanges, turnkey packaging, K-factor | Recurring commissions without own product |

## Technical Pattern (Reusable)

### 1. Domain Definitions
Added all 7 domains to `config/domain_definitions.yaml` with EN+RU keywords.

### 2. White Spot Cluster Registration
```sql
INSERT OR IGNORE INTO white_spot_clusters 
(cluster_id, formed_at, size, representative_text, proposed_dimension, status)
VALUES 
('white-spot-advanced-analytics', now(), 0, '...', 'advanced-analytics', 'developing'),
-- ... etc for all 7
```

### 3. DeepSeek Research Loop (execute_code + urllib)
```python
def ask_deepseek(prompt, max_tokens=2500):
    url = "http://localhost:9655/v1/chat/completions"
    payload = {"model": "deepseek-chat", "messages": [{"role": "user", "content": prompt}], "max_tokens": max_tokens, "temperature": 0.3}
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read().decode())["choices"][0]["message"]["content"]

# For each domain: prompt with 8 structured subtopics → ask_deepseek → time.sleep(3)
```

### 4. Schema-Compliant Insert
```python
c.execute("""
    INSERT INTO experiences (content, raw_text, source, confidence, ts, hash, 
                             dynamic_axes, axis_domain, tags, is_white_spot, importance)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
""", (content, content, "white-spot-explorer", 0.95, datetime.now().isoformat(), content_hash,
      json.dumps({"topic": domain, "research": True, "white_spot": True}),
      domain,
      json.dumps([domain, "white-spot", "research", *subtags]),
      1, 0.9))
```

### 5. Cluster Update
```sql
UPDATE white_spot_clusters 
SET size = (SELECT COUNT(*) FROM experiences WHERE axis_domain = proposed_dimension),
    status = 'researched'
WHERE cluster_id = 'white-spot-{domain}';
```

### 6. Auto-Tagger Reclassification
```bash
python scripts/auto_tagger.py --force
# 442 entries reclassified using new domain keywords
```

## Results
- 7 new domains with 1+ research entries each
- crypto-web3 got 3 entries (had 2 pre-existing from tags)
- Total Knowledge Cube: 2142 entries across 29 domains
- All 7 clusters status: `researched`

## Cost & Performance
- ~17,500 tokens total
- ~$0.004 (DeepSeek-V4-Flash @ $0.14/$0.28 per 1M)
- ~3 minutes wall time
- No rate limit issues with 3s sleep between requests
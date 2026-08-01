# Latent Domain Detection — "Суслик" Pattern

## What It Is
Automatic discovery of **implicit knowledge gaps** in the Knowledge Cube by analyzing
co-occurrence patterns, logical clusters, and bridge terms in existing entries.
The "суслик" (gopher) approach — finding what the system doesn't know it knows.

## Pipeline Position
```
Cube entries (флер/ambient knowledge)
  → Latent Domain Detector (co-occurrence + cluster analysis)
    → White spot seeds (automatic)
      → knowledge_gap_filler.py (every 2h) researches each gap
        → New domain entries populated
```

## How It Works

### Step 1: Cross-Domain Term Analysis
- Extract all unique terms from Cube entries
- Group by existing domains
- Find high-frequency terms that appear across many domains
- Filter out terms that already belong to a formal domain
- **Top candidates** become potential new domain names

### Step 2: Co-occurrence (Bridge) Analysis
- Find term pairs that co-occur in entries from DIFFERENT domains
- High co-frequency → missing intermediate domain
- Example: `skill ↔ terminal` co-occur 214 times, missing "installation" domain

### Step 3: Logical Gap Detection
- Cluster related terms (e.g., "telegram bot", "bot", "tgb", "salon-bot")
- For each cluster, check if essential supporting domains exist
- Missing essential domain → logical gap
- Example: 170 mentions of Telegram bots but NO payment/hosting/deployment domain

### Step 4: Seed Generation
- For each missing domain, create white-spot entries in Cube
- Each seed links back to the source cluster (traceability)
- Seeds are tagged `latent-detect:auto`

## Scoring

### Candidate Score
```
candidate_score = frequency × domain_spread
  where:
    frequency = total occurrences in Cube
    domain_spread = number of different domains this term appears in
```

### Gap Detection Score
```
gap_score = cluster_size × (expected_domains - existing_domains)
  where:
    cluster_size = total mentions of related terms
    expected_domains = minimal viable domains for this topic
    existing_domains = count of domains already covering this area
```

### Bridge Detection Score
```
bridge_score = co_frequency / (domain_a_entries × domain_b_entries) × total_entries
  High score → missing intermediate domain likely
```

## First Run Results (June 2026)

**3 Logical Gaps from 1891 Cube entries:**

| Cluster | Mentions | Missing Domains |
|---------|----------|-----------------|
| Telegram bots | 170 | payment, hosting, deployment, monetization, analytics |
| Content/channels | 91 | marketing, analytics, seo, audience |
| Dev/infra | 411 | cicd, monitoring, backup |

**48 seeds generated** and written to Cube as white spots.

**194 cross-domain candidates** and **44 bridge candidates** identified.

## When to Run

- After `cube_feeder.py` or significant Cube growth (100+ new entries)
- After adding new major domains
- Before `knowledge_gap_filler.py` run (to give it fresh targets)
- At most once per day (gives gap filler time to research seeds)

## Running

```bash
# Preview only — shows gaps without writing
python scripts/latent_domain_detector.py --dry-run

# Active mode — seeds white spots into Cube
python scripts/latent_domain_detector.py --seed
```

## Pitfalls

1. **Common word noise** — "output", "description", "recent" are high-frequency
   but not domain-worthy. Use domain_spread threshold (appears in 3+ domains min).
2. **Don't re-seed too often** — seeds need 2h+ (gap filler cycle) to be researched
   before generating new ones. 24h+ gap between seeding runs recommended.
3. **Complementary to white-spot-explorer** — this DETECTS gaps from existing data;
   white-spot-explorer RESEARCHES already-known gaps via external APIs.
   Different phases of the same pipeline — run detector first, then explorer.
4. **Code-based, no user input needed** — never ask "should I run this?" Just run it
   when conditions are met. User requires autonomous operation.
5. **Re-run idempotent** — duplicates are skipped via content hash. Safe to run
   multiple times, just wasteful before gap filler processed previous seeds.

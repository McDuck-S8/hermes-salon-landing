---
name: latent-domain-detector
description: "Find implicit knowledge gaps in Knowledge Cube — latent domains, bridge domains, and logical gaps"
version: 1.0.0
author: Hermes Agent
license: MIT
tags: [knowledge-cube, gaps, domains, white-spots, discovery]
---

# Latent Domain Detector

Analyses Knowledge Cube entries to find implicit knowledge domains that logically should exist but aren't populated. Uses term frequency, co-occurrence analysis, and logical gap detection (the "fler" approach).

## When to Use

- When you suspect the Knowledge Cube has blind spots
- Before running skill auto-evolution to guide what domains to create
- Periodically (daily) to discover emerging knowledge gaps
- After adding many new entries from sessions

## Procedure

### Analysis Only (Report)

```bash
cd /d/Portable_Soft/hermes
python scripts/_deprecated/latent_domain_detector.py --dry-run
```

### Analysis + Seed Gaps into Cube

```bash
python scripts/_deprecated/latent_domain_detector.py --seed
```

### Dry Run (Preview Only)

```bash
python scripts/_deprecated/latent_domain_detector.py --dry-run
```

> **Note**: The working script is `scripts/_deprecated/latent_domain_detector.py` (archived but functional). It requires `CUBE_PATH` override since it's in `_deprecated/`. Use the wrapper `run_latent.py` at repo root or set `latent_domain_detector.CUBE_PATH = 'D:/Portable_Soft/hermes/cache/knowledge_cube.db'` before importing.

## What It Detects

### 1. Cross-Domain Term Candidates
Terms that appear frequently across multiple existing domains but aren't a domain themselves. High spread score = strong candidate.

### 2. Bridge Domain Candidates
Terms that co-occur between two or more existing domains, suggesting a missing linking domain. E.g. "booking" appearing in both "salon" and "calendar" entries suggests a missing "booking" domain.

### 3. Logical Gaps
Semantic clusters that imply missing domains:

| Cluster | Implied Missing Domains |
|---------|------------------------|
| Telegram bots → | payment, hosting, deployment, monetization, analytics |
| Business/monetization → | payment, marketing, legal, crm, pricing |
| Salon business → | booking, client_management, loyalty, schedule |
| Content/channels → | marketing, analytics, seo, audience |
| Dev/infrastructure → | cicd, monitoring, backup |

### 4. Seed Generation
With `--seed`, inserts "white spot" entries into Knowledge Cube that the `knowledge_gap_filler` and `white-spot-explorer` systems will automatically pick up for investigation.

## Output

Structured report with:
- All existing domains in Cube
- Logical gaps found (clusters with missing sub-domains)
- Top 20 candidate terms for new domains (with frequency and coverage)
- Bridge domain candidates (with co-occurrence frequencies)

## Requirements

- Python 3.8+
- Knowledge Cube database (`cache/knowledge_cube.db`) populated with entries
- Stop-word list built-in (technical + common Russian/English words filtered)

## Pitfalls

- First run may find many "gaps" — this is normal, the system learns over time
- `--seed` creates entries with `is_white_spot=1` — they won't trigger again
- Bridge detection requires at least 3 domains with related entries
- The semantic clusters are hardcoded — update the script if your domain changes

---
name: nocturnal_cognition
description: "Crystal's nightly memory consolidation — runs Three-Layer Memory compression, generates insights from compressed patterns, and produces 'dreams' (cross-domain synthesis). Runs as cron job at 02:00."
trigger: "Cron (02:00 daily), on Crystal cycle start, on 'consolidate_daily' command"
usage: nocturnal_cognition
---

# Nocturnal Cognition — Crystal's Nightly Consolidation

Implements Clarence's "Nocturnal Cognition" — nightly dream cycles for agents. Runs Three-Layer Memory compression, extracts insights, generates cross-domain "dreams".

## Architecture

```
NocturnalCognition.consolidate_daily()
    ├─ ThreeLayerMemory.run_full_compression()     # Raw → Thematic → Compressed
    ├─ _generate_insights()                        # Warnings, recommendations, patterns
    ├─ _generate_dreams()                          # Cross-domain synthesis
    └─ _log_consolidation()                        # Audit trail
```

## Database (crystal.db)

| Table | Purpose |
|---|---|
| `crystal_consolidation` | Nightly run log with metrics |
| `crystal_insights` | Actionable insights (warning/pattern/recommendation) |
| `crystal_dreams` | Cross-domain synthesis predictions |

## Outputs

### Insights (crystal_insights)
| Type | Source | Action |
|---|---|---|
| `warning` | Anti-pattern with high evidence | Risk Assessment → Proposal |
| `recommendation` | Rule/heuristic pattern | Dev Proposer → Guard |
| `pattern` | Cross-domain principle | Priority Engine → Need |

### Dreams (crystal_dreams)
Cross-domain synthesis: "Theme X connects N domains. Unified mechanism?"

Example: "Theme 'failure' connects 11 domains: devops, design, data, coding, research, debugging, creative, browser, communication, file_ops, system. Possible unified mechanism?"

## Usage

```python
from crystal.nocturnal_cognition import NocturnalCognition, run_nocturnal_cognition

# Run full consolidation
nc = NocturnalCognition()
result = nc.consolidate_daily()

# Or use cron entry point
run_nocturnal_cognition()
```

## Cron Job

```json
{
  "name": "nocturnal-cognition",
  "script": "crystal/nocturnal_cognition.py",
  "schedule": "0 2 * * *",
  "enabled_toolsets": ["file", "terminal"]
}
```

## Verification

```bash
python -c "from crystal.nocturnal_cognition import NocturnalCognition; nc=NocturnalCognition(); r=nc.consolidate_daily(); print(r['insights_generated'], r['dreams_generated'])"
```

---

**Created:** 2026-07-30
**Version:** 1.0
**Author:** Hermes Agent
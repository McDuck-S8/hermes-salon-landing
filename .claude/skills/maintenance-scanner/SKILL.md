---
name: maintenance-scanner
description: "Weekly anti-rot scanner. Scans all 5 layers + substrate against blueprint, reports drift, expiry, and drift. Runs as cron (Sunday 03:00)."
trigger: "On schedule (0 3 * * 0), or when maintenance_reports show drift > threshold"
usage: maintenance-scanner
---

# Maintenance Scanner — Weekly Anti-Rot Scanner

Scans all 5 layers + substrate against blueprint, reports drift, expiry, and drift.

## Architecture

```
maintenance-scanner/
├── SKILL.md                    # This file
├── scripts/
│   └── maintenance_scanner.py  # Main scanner logic
├── reference/
│   └── REVISIT_CONVENTION.md   # Revisit field convention
└── templates/
    └── MAINTENANCE_REPORT.md   # Report template
```

## Quick Start

```bash
# Run scan manually
python scripts/maintenance_scanner.py

# Run with verbose output
python scripts/maintenance_scanner.py --verbose

# Output to custom directory
python scripts/maintenance_scanner.py --output /path/to/reports
```

## Cron Integration

```json
{
  "name": "maintenance-scanner",
  "script": "maintenance_scanner.py",
  "schedule": "0 3 * * 0",  // Sunday 03:00
  "enabled": true
}
```

## Layer Definitions

| Layer | Paths | Rot Rate | Revisit |
|-------|-------|----------|---------|
| Identity | `CLAUDE.md`, `IDENTITY.md` | Months | 6 months |
| Rules | `.claude/rules/always.md`, `never.md` | Weeks | 3 months |
| Skills | `.claude/skills/` | Days-Weeks | 1 month |
| Agents | `.claude/agents/` | Days | 2 weeks |
| Tools | `.claude/tools/` | Hours | 1 week |
| Substrate | `.wiki/` | Grows | Never |

## Report Output

Generates two files per run:
- `maintenance_YYYYMMDD_HHMMSS.json` — machine-readable
- `maintenance_YYYYMMDD_HHMMSS.md` — human-readable

## Integration Points

| System | Hook |
|--------|------|
| Cron | Runs weekly via scheduler |
| Crystal | Consumes drift reports for self-improvement |
| User Learner | Feeds trigger patterns |
| Graphify | Exports drift graph |
| Token Tracker | Logs scan token cost |

## Cron Integration

```json
{
  "name": "maintenance-scanner",
  "script": "maintenance_scanner.py",
  "schedule": "0 3 * * 0",  // Sunday 03:00
  "enabled": true
}
```

## Topic Index

| Section | Description |
|---------|-------------|
| Architecture | Component structure and layer definitions |
| Quick Start | Manual scan commands |
| Cron Integration | Automated weekly scheduling |
| Layer Definitions | Paths, rot rates, revisit intervals |
| Report Output | JSON + Markdown formats |
| Integration Points | Cron, Crystal, User Learner, Graphify, Token Tracker |
| Anti-Rot Cadence | On-contact, weekly, monthly, on-demand |
| Verification Rule | Adversarial verification requirement |

## Anti-Rot Cadence

| Frequency | Action |
|-----------|--------|
| On Contact | Fix edge cases in skills when spotted |
| Weekly | Maintenance workflow scans all 5 layers + wiki, reports drift |
| Monthly | Revisit scheduler walks expiry register, interviews to refresh |
| On Demand | Token-budgeted workflows for build/maintenance |

## Verification Rule

Every generated file gets a SECOND agent that adversarially verifies it against the blueprint before it survives.

## Core Mental Models

1. **Inside-Out Growth** — Start at the core (Identity), only add outer layers when earned by real usage. The deeper the layer, the slower it changes.
2. **Rot at Different Rates** — Different layers rot at different speeds. The foundation holds for years; the fridge is gone by the weekend. Maintain on appropriate cadences.
3. **Verification Before Survival** — Every generated file gets a SECOND agent that adversarially verifies it against the blueprint before it survives.

## Key Frameworks & Decision Rules

| Framework | Purpose | When to Apply |
|-----------|---------|---------------|
| **Anti-Rot Cadence** | Maintain system health at appropriate frequencies | On contact / Weekly / Monthly / On demand |
| **Revisit Convention** | Track expiry via `Revisit: YYYY-MM-DD` frontmatter | Every file in tracked layers |
| **Drift Detection** | Hash-track files, detect missing Revisit, expired, changed | Every scan cycle |
| **Blueprint Compliance** | Verify actual structure matches `os-blueprint.md` | Every scan cycle |

## Topic & Chapter Index

- [Architecture](#architecture)
- [Quick Start](#quick-start)
- [Cron Integration](#cron-integration)
- [Layer Definitions](#layer-definitions)
- [Report Output](#report-output)
- [Integration Points](#integration-points)
- [Anti-Rot Cadence](#anti-rot-cadence)
- [Verification Rule](#verification-rule)

## Anti-Patterns & Common Pitfalls

| Anti-Pattern | Symptom | Fix |
|--------------|---------|-----|
| **Uniform Maintenance** | Treating all layers with same frequency | Apply per-layer cadence |
| **No Revisit Tracking** | Files expire silently | Enforce `Revisit:` frontmatter |
| **Skipping Verification** | First-draft files survive | Mandate second-agent verification |
| **Full-Disk Scans** | Token waste, slow | Prefer slice scans |

---

**Version**: 1.0  
**Created**: 2026-07-31  
**Author**: Hermes Agent
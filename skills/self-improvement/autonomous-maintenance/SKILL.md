---
name: autonomous-maintenance
description: "Class-level skill for autonomous maintenance system: skill usage analysis, suggestion auto-application, compliance verification, anti-rot scanning, adversarial file verification. Implements Zero Trust, Passive Income, Iterative Attack autonomy rules."
trigger: "On schedule (maintenance_scanner weekly, compliance_checker daily, suggestion_applier 30min), or when new_suggestions_ready event fires"
usage: autonomous-maintenance
---

# Autonomous Maintenance — Class-Level Skill

Covers the complete autonomous maintenance pipeline: **skill usage analysis → suggestion queue → auto-application → compliance verification → anti-rot scanning → adversarial verification**.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    AUTONOMOUS MAINTENANCE LOOP                  │
├─────────────────────────────────────────────────────────────────┤
│  skill_usage_analyzer.py     │  Analyzes skill usage from       │
│  (14-day threshold)          │  feedback_store/logs, routes     │
│                              │  to action systems                │
├─────────────────────────────────────────────────────────────────┤
│  suggestion_applier.py       │  Auto-applies queued suggestions │
│  (30-min cron + event)       │  - Register skills in CLAUDE.md  │
│                              │  - Add Revisit frontmatter       │
│                              │  - Fix files via subagent_verifier│
├─────────────────────────────────────────────────────────────────┤
│  compliance_checker.py       │  Daily verifies 3 core rules:    │
│  (daily cron)                │  Zero Trust, Passive Income,     │
│                              │  Iterative Attack; auto-corrects │
├─────────────────────────────────────────────────────────────────┤
│  maintenance_scanner.py      │  Weekly scans 5 layers + substrate│
│  (weekly cron Sun 03:00)     │  Reports drift, expiry, missing  │
│                              │  Revisit; rotation recommendations│
├─────────────────────────────────────────────────────────────────┤
│  subagent_verifier.py        │  Adversarial verification of all │
│  (on file create)            │  generated files before survival │
├─────────────────────────────────────────────────────────────────┤
│  token_tracker.py            │  Logs token usage/cost per model │
│  (per operation)             │  operation, daily/model breakdown│
└─────────────────────────────────────────────────────────────────┘
```

## Component Scripts

| Script | Purpose | Trigger |
|--------|---------|---------|
| `skill_usage_analyzer.py` | Collects usage from feedback_store/logs, identifies unused skills (>14d), routes to Suggestion Applier / Crystal / Knowledge Cube / Proactive Doer | Daily or on demand |
| `suggestion_applier.py` | Processes `cache/suggestion_queue.json`, applies fixes: registers skills, adds Revisit, fixes files | Event `new_suggestions_ready` + cron `*/30 * * * *` |
| `compliance_checker.py` | Verifies Zero Trust (subagent_verifier logs), Passive Income (cron runs), Iterative Attack (proactive_doer tasks); auto-corrects | Daily cron `0 4 * * *` |
| `maintenance_scanner.py` | Scans 6 layers (Identity, Rules, Skills, Agents, Tools, Substrate) for drift/expiry/missing Revisit | Weekly cron `0 3 * * 0` |
| `subagent_verifier.py` | Adversarial checks: not_empty, reasonable_size, no_placeholders, no_fabricated_output, frontmatter_complete, skill_sections, no_hallucinated_commands | On file create / manual |
| `token_tracker.py` | SQLite logging of token usage/cost per model/operation; daily/model breakdowns | Per LLM operation |
| `read_only_auditor.py` | Generates blueprint draft from existing files (no writes) | Manual / on demand |

## Routing Logic (skill_usage_analyzer)

| Root Cause | Days Unused | Severity | Routed To | Action |
|------------|-------------|----------|-----------|--------|
| Broken dependencies | Any | Critical | Proactive Doer | Fix deps / restart cron |
| No triggers defined | >14 | High | Suggestion Applier | Add event triggers / cron |
| Not in CLAUDE.md/AGENTS.md | >14 | High | Suggestion Applier | Register in config files |
| Duplicates another skill | >14 | Medium | Crystal | Merge / consolidate |
| No usage examples | >14 | Medium | Suggestion Applier | Add examples / tests |
| Task model shifted | >14 | Low | Knowledge Cube | Reassess relevance signal |

## Three Core Autonomy Rules (Enforced by compliance_checker)

| Rule | Verification | Auto-Correction |
|------|--------------|-----------------|
| **Zero Trust** | All changes pass subagent_verifier (24h logs) | Queue subagent_verifier task for recent changes |
| **Passive Income** | Cron runs in 48h, maintenance_scanner active | Restart failed crons via Proactive Doer |
| **Iterative Attack** | ≥1 proactive_doer task/day | Generate task from suggestions/gaps |

## Cron Integration

| Job | Schedule | Script | No-Agent |
|-----|----------|--------|----------|
| suggestion-applier | `*/30 * * * *` | suggestion_applier.py | true |
| maintenance-scanner | `0 3 * * 0` | maintenance_scanner.py | true |
| compliance-checker | `0 4 * * *` | compliance_checker.py | true |
| skill-usage-analyzer | `0 5 * * *` | skill_usage_analyzer.py --execute | true |

## Key Files

```
scripts/
├── skill_usage_analyzer.py      # Core analyzer + router
├── suggestion_applier.py        # Queue processor (fixed nested payload)
├── compliance_checker.py        # 3-rule verifier + auto-correct
├── maintenance_scanner.py       # 6-layer anti-rot scanner
├── subagent_verifier.py         # Adversarial file verification
├── token_tracker.py             # Token/cost tracking (SQLite)
├── read_only_auditor.py         # Blueprint generator
└── maintenance_reports/         # Weekly JSON+MD outputs
```

## Pitfalls & Fixes (Learned)

| Issue | Fix |
|-------|-----|
| **Nested payload in suggestion queue** | `suggestion_applier.py` now extracts `inner = payload.get("payload", {})` before checking `action` |
| **999 days logic** | `skill_usage_analyzer.py`: `days_unused = 0` if used <14d, `999` only if NO feedback_store record |
| **Applied log corruption** | `suggestion_applier.load_applied()` handles both list and `{"failed": [...]}` formats |
| **Path resolution in suggestion_applier** | Uses `HERMES_HOME / target_file` not relative paths |
| **Compliance checker glob** | Convert `Path.glob()` to `list()` before slicing |
| **KC write NOT NULL** | Include `hash` column with SHA256 prefix in INSERT |

## Verification Commands

```bash
# Syntax check all
python -m py_compile scripts/skill_usage_analyzer.py scripts/suggestion_applier.py scripts/compliance_checker.py scripts/maintenance_scanner.py scripts/subagent_verifier.py scripts/token_tracker.py

# Run full compliance check
python scripts/compliance_checker.py --check --json

# Run skill analysis + execute
python scripts/skill_usage_analyzer.py --analyze --execute --threshold 14 --json

# Process suggestion queue
python scripts/suggestion_applier.py --once --json

# Run maintenance scan
python scripts/maintenance_scanner.py

# Verify files
python scripts/subagent_verifier.py CLAUDE.md .claude/rules/always.md .claude/rules/never.md --strict

# Check token usage
python scripts/token_tracker.py --models 7
```

## Integration Points

| System | Hook |
|--------|------|
| **chain_heartbeat** | Fires `maintenance_scan_complete`, `compliance_check_complete` |
| **feedback_store** | Logs all verifications, applications, compliance results |
| **knowledge_cube** | Receives "skill unused → context shift" signals |
| **proactive_doer** | Receives fix-deps, restart-cron, execute-generated-task tasks |
| **crystal** | Receives merge/consolidate tasks for duplicate skills |
| **suggestion_consumer** | Produces suggestions consumed by suggestion_applier |
| **subagent_orchestrator** | Receives marketplace search tasks via delegation protocol; provides context injection, retries, monitoring |

## Related Skills

- `self-improvement/suggestion_applier` — Queue consumer (this skill enhances it)
- `self-improvement/skill-evolution` — Skill auto-evolution from KC
- `self-improvement/three_layer_memory` — KC compression for context shift signals
- `self-improvement/white_spot_explorer` — Finds gaps that become Iterative Attack tasks
- `devops/chain-heartbeat` — Event-driven monitoring
- `devops/cron-maintenance` — Cron management
- `automation/web-automation` — Browser/HTTP automation for marketplace scraping
- `automation/subagent-orchestration` — Subagent delegation with context injection, proxy, retries

## Version
1.1 — Updated 2026-08-01 with subagent-orchestration integration and browser launch workaround for geo-restricted regions
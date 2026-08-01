# Architecture Model — Module & Connection Reference

Source: `scripts/architecture_model.py`
Storage: `data/architecture_model.json` + Knowledge Cube (entry_type=architecture, tags=["architecture","crystal","model"])

## Module Layers

| Layer | Modules | Purpose |
|-------|---------|---------|
| engine | core, event_system | Core loop, event bus, hooks |
| knowledge | knowledge, knowledge_pipeline, skills | KC, recall, pipeline, filter |
| io | llm, tools, telegram, plugins_websrch | External integrations |
| automation | cron_tools | Scheduled jobs |
| action | posting | Content delivery |
| self-improvement | health, crystal_base, plugins_selfev, plugins_icarus, plugins_lcm | Self-healing, suggestions, lifecycle |
| infra | config, deprecated | Config, archive |

## Connection Types

- `data` — data flow (A produces data consumed by B)
- `trigger` — A triggers action in B (cron, event)
- `config` — configuration consumed by B
- `event` — event/message passing
- `reference` — B reads from A's store

## Health States

- **HEALTHY** — all tracked files exist
- **DEGRADED** — some files missing
- **DEAD** — no tracked files found

## Connection States

- **ACTIVE** — both endpoint modules are HEALTHY
- **BROKEN** — one or both endpoint modules are not HEALTHY

## Diff Detection

Model compares current modules_state with previous snapshot (stored in data/architecture_model.json). Detects:
- NEW → HEALTHY (module appeared)
- HEALTHY → DEGRADED (file deleted)
- HEALTHY → DEAD (module wiped)
- DEGRADED → HEALTHY (file restored)
- BROKEN → ACTIVE (module healed)

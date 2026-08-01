# IBOS (Infinite Brain OS) Mapping to Hermes

This document maps the key concepts from [starmynd-org/infinite-brain-os](https://github.com/starmynd-org/infinite-brain-os) to Hermes implementations.

## Source Repository
- **Repo**: https://github.com/starmynd-org/infinite-brain-os
- **Philosophy**: Git-backed OS for business on AI agents. Plain Markdown/YAML, readable by any file-reading agent, owned by you. No DB, no server, no vendor lock-in.

---

## 11 Entity Types — IBOS vs Hermes

| IBOS Entity | Canonical Location | Hermes Implementation |
|-------------|-------------------|----------------------|
| **Command** | `entities/commands/` | `scripts/*.py` + `.claude/commands/` (future) |
| **Agent** | `entities/agents/` | `scripts/autonomous_agent.py`, `scripts/crystal/*.py` |
| **Skill** | `entities/skills/` | `skills/` (100+), `scripts/ibos_entity_sensor.py` |
| **Rule** | `entities/rules/` | `AGENTS.md`, `PROCEDURAL_SKILLS.md`, `scripts/procedural_executor.py` |
| **Workflow** | `workflows/` (agentic), `automations/n8n/` (deterministic) | `scripts/crystal/` (agentic), `scripts/procedural_executor.py` (deterministic) |
| **Tool** | `tools/` (pointer nodes) | `scripts/*.py` as bounded capabilities |
| **Knowledge** | `knowledge//` (namespace-first) | `knowledge_cube/`, `ARBITRAGE_WORKSHOP.md`, `cache/` |
| **Data** | `data/` (pointers only) | `cache/` (pointers), `config/` |
| **Memory** | `memory/` (reviewed learnings) | `MEMORY.md`, `fabric`, `memory_guard.py` |
| **Output** | `outputs/` (artifacts with lineage) | `ARBITRAGE_WORKSHOP.md`, `reports/`, `plans/` |
| **Project** | `projects/{name}/PLAN.md` | `ARBITRAGE_WORKSHOP.md`, `scripts/goal_queue.py` |

**Departments** (`departments/`) = assemblies over entities → Hermes: implicit via `AGENTS.md` + project structure

---

## Namespace Architecture

| IBOS Concept | Hermes Equivalent |
|--------------|-------------------|
| `knowledge//` (namespace-first) | `knowledge_cube/` domains + `ARBITRAGE_WORKSHOP.md` sections |
| Base folders: `INDEX.md`, `canon/`, `playbooks/`, `support/`, `synthesis/` | Partial: `canon` → `ARBITRAGE_WORKSHOP.md` tables, `support` → `cache/`, `synthesis` → `crystal/` |
| 8 profiles (`_system/namespace-profiles.md`) | Not yet implemented |
| **Promotion path**: raw → support → synthesis → canon-candidate → **canon (operator approval)** | **MISSING** — critical gap: no governance, `canon` is implicit |

**Starter namespaces in IBOS:**
- `knowledge/ai-architecture/` → Hermes: `knowledge_cube/ai-architecture/`
- `knowledge/personal-operator/` → Hermes: `memories/USER.md`, `memories/MEMORY.md`
- `knowledge/emberline-studio/` (worked example) → Hermes: `ARBITRAGE_WORKSHOP.md` as worked example
- `knowledge/_examples/` → Hermes: `skills/*/references/`

---

## Contract Layer (`_ (`_ (`_system/`)

| IBOS File | Hermes Equivalent |
|-----------|-------------------|
| `validate.sh` (frontmatter, refs, schemas) | `scripts/ibos_entity_sensor.py` + `_system/schemas/frontmatter.schema.yaml` |
| `retrieval-routing-map.md` | `scripts/session_recall.py` (BM25), `scripts/kc_rag.py` |
| `namespace-profiles.md` | **MISSING** |
| `session-ledger-rules.md` | **MISSING** (Hermes has `hermes_start.py` boot + session_context) |
| `core-doctrine.md` | `AGENTS.md` + `SOUL.md` + `PROCEDURAL_SKILLS.md` |

---

## Session Discipline

| IBOS | Hermes |
|------|--------|
| `sessions/active/` — register session | `hermes_start.py` boot → `session_context` |
| `sessions/logs/` — transcript | `sessions/` dumps (ingested at boot) |
| `sessions/reviews/` — closeout review | `crystal/` self-learning loop produces reviews |
| `sessions/closed/` — archived | `sessions/` dumps archived |
| Dual-write for swarms: `sessions/` + `swarms/Sprints/` | **MISSING** (no swarm concept) |

---

## Sync Adapters

| IBOS | Hermes |
|------|--------|
| `entities/` (canonical) → `.claude/`, `.codex/` via `sync-adapters.sh` | `scripts/` + `skills/` → runtime adapters via `hermes_bootstrap.py` |
| **Never edit shims directly** | **Enforced**: bootstrap is entry point |

---

## What Hermes Does BETTER (IBOS Lacks)

| Capability | IBOS | Hermes |
|------------|------|--------|
| **Event-Driven Loop** | Declarative workflows only | Full: sensors → bus → classification → chains → actions |
| **Autonomous Agent** | File-reading executor only | 29-candidate Bayesian decision matrix + `crystal` self-learning |
| **Procedural Reflexes** | ❌ | `procedural_executor.py` (deterministic, no LLM) |
| **Bayesian Scoring** | ❌ | `bayesian_scorer.py` for all decision points |
| **Signal Daemon** | ❌ | Adaptive backoff HN/GitHub trending |
| **Sub-agents (Maker-Checker)** | ❌ | `delegate_task` with orchestrator/leaf roles |
| **Memory Guard** | ❌ | `memory_guard.py` (amnesia protection, auto-restore) |
| **Skill Evolution** | Manual | Auto from Knowledge Cube |
| **Self-Improvement Loop** | ❌ | `crystal/` 23 modules (observe→diagnose→will→execute→learn) |

---

## Hybrid Architecture (Implemented)

```
┌─────────────────────────────────────────────────────────────────┐
│                    HERMES RUNTIME (Executive)                   │
│  autonomous_agent • crystal • event_bus • procedural            │
│  delegate_task • signal_daemon • goal_queue • memory_guard      │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│              INFINITE BRAIN OS (Knowledge Layer)                │
│  _system/validate.sh • namespaces/ • entities/                 │
│  knowledge// • projects/PLAN.md • sessions/ • outputs/         │
│  frontmatter contract • lifecycle states • canon governance    │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    EXTERNAL RUNTIMES (Adapters)                 │
│  .claude/commands/ • .codex/commands/ • Obsidian vault         │
│  sync-adapters.sh • MCP servers • Web UI                       │
└─────────────────────────────────────────────────────────────────┘
```

---

## Integration Plan (4 Weeks)

| Week | Deliverable | Hermes Files |
|------|-------------|--------------|
| 1 | Frontmatter Contract + Validator | `_system/schemas/`, `scripts/ibos_entity_sensor.py` |
| 2 | Namespace Registry + Promotion Path | `knowledge/`, `_system/namespace-registry.yaml` |
| 3 | Session Ledger + Sync Adapters | `sessions/`, `sync-adapters.sh`, `.hermes/` adapters |
| 4 | Canon Governance + Obsidian Compat | `canon-approval.yaml`, `.obsidian/`, dashboard |

---

## Key Takeaway

**IBOS = Knowledge/Governance Layer** (what Hermes was missing)
**Hermes = Executive Runtime** (what IBOS was missing)

Together = **Full Stack Agent OS**: Governed knowledge + Autonomous execution + Procedural self-healing
# Understory + OKF Integration Plan for Hermes Agent

**Created:** 2026-07-13
**Sources:** Understory (thecodacus/understory), OKF v0.1 Spec (Google), Video "Every Local AI I Run Now Shares ONE Memory"

---

## Table of Contents
1. [Executive Summary](#1-executive-summary)
2. [What We Researched](#2-what-we-researched)
3. [Hermes Current State](#3-hermes-current-state)
4. [Gap Analysis](#4-gap-analysis)
5. [Architecture Decision: Run vs Import](#5-architecture-decision-run-vs-import)
6. [Roadmap: 3 Phases](#6-roadmap-3-phases)
7. [Phase 1: Quick Wins (1-2 Days)](#7-phase-1-quick-wins)
8. [Phase 2: Knowledge Layer Unification (1 Week)](#8-phase-2-knowledge-layer-unification)
9. [Phase 3: Living Knowledge (2-3 Weeks)](#9-phase-3-living-knowledge)
10. [Detailed Implementation Steps](#10-detailed-implementation-steps)
11. [Appendix: Understory Source Map](#11-appendix-understory-source-map)

---

## 1. Executive Summary

Hermes Agent already has a RICH memory/knowledge infrastructure that in many ways **surpasses** Understory:
- FTS5 keyword search + LanceDB vector embeddings + salience scoring (three-layer memory)
- SQLite Knowledge Cube with OKF-Lite metadata (confidence, expiration, verification)
- File-based persistent memory (MEMORY.md, learnings.md, goals.md)
- Native MCP client that can consume Understory as a server

However, Hermes lacks three transformative capabilities that Understory/OKF bring:
1. **OKF-compliant file-based knowledge** — portable, diffable, human-readable markdown with cross-linking (not locked in SQLite)
2. **Knowledge graph visualization** — seeing the memory as a living graph changes how you interact with it
3. **Auto-maintenance** — orphans/broken links detection + session seeding

**Recommendation: Hybrid approach** — Run Understory as a sidecar Docker container for its Web UI, graph, and MCP tools, while in parallel importing OKF concepts into Hermes' native memory layer. This gives us the best of both worlds without rewriting either system.

---

## 2. What We Researched

### 2.1 Understory
- **Repo:** https://github.com/thecodacus/understory
- **Stack:** TypeScript, pnpm monorepo, Vercel AI SDK, Express, React+Vite+Tailwind, d3-force
- **MCP Tools:** memory_query, memory_add, memory_update, memory_status, memory_maintain
- **Architecture:**
  - `packages/core/src/okf/` — Bundle file ops (sandboxed), frontmatter parser, search (naive scan), validate (conformance), lint (orphans+borken links), graph builder, indexer, logger
  - `packages/core/src/agent/` — runQuery, runMutation, system prompt builder, read/write tools, trace recorder
  - `packages/core/src/providers/` — anthropic, openrouter, llamacpp, local
  - `packages/server/` — Express: MCP streamable-HTTP at `/mcp`, stdio bin, REST browse at `/api/*`, streaming chat at `/api/chat`, serves web build
  - `packages/web/` — React bundle browser + force-directed graph + agent chat (useChat)
- **Key Design Rule:** "Conformance is enforced in code, not prompts" — deterministic bundle layer validates frontmatter (type required), regenerates index.md, appends log.md, sandboxes paths
- **Session Seed:** MCP `instructions` field + `memory_query` tool description — compact overview injected at every session start
- **Maintenance:** memory_maintain lint (orphans + broken links) + memory_status
- **Traces:** Every agent run records its traversal as compact notation under `/.traces/`
- **Providers:** env-selectable, swappable per chat (Anthropic, OpenRouter, llamacpp, local)
- **Deployment:** Single Docker container (image on GHCR)

### 2.2 OKF Spec v0.1 (Google)
- **Bundle:** Directory of markdown files with YAML frontmatter
- **Concept:** One markdown file = one unit of knowledge
- **Required field:** `type` (non-empty, any string)
- **Recommended:** `title`, `description`, `resource`, `tags`, `timestamp`
- **Reserved filenames:** `index.md` (directory listing), `log.md` (change history)
- **Cross-linking:** Standard markdown links `[text](/path/to/concept.md)`
- **Citations:** `# Citations` section in body
- **Versioning:** Bundle can declare `okf_version: "0.1"` in root index.md
- **Consumer contract:** Must tolerate missing optional fields, unknown types, broken links, missing indexes
- **Producer-consumer asymmetry:** Producers aim to be precise, consumers aim to be forgiving

### 2.3 Video Key Insights
- "Memory is NOT a vector DB" — RAG and memory are different things
- Architecture pattern: **librarian** (agent manages its own memory) not library (fixed corpus)
- Three MCP tools: search, add, update
- Challenges identified: cold start (forgets to remember → session seed), junk drawer (linking → write-time linking), maintenance (orphans, contradictions → memory_maintain)
- Local-first: runs on llama.cpp, every memory is a diffable markdown file

---

## 3. Hermes Current State

### 3.1 What Hermes Already Has

| Capability | Status | Details |
|---|---|---|
| **Knowledge Cube** | ✅ | SQLite + FTS5, concepts with tags, experiences |
| **Three-Layer Memory** | ✅ | FTS5 + LanceDB vectors + Salience scoring |
| **OKF-Lite** | ✅ | confidence, expiration_date, verification_method fields |
| **Native MCP Client** | ✅ | Connects to any MCP server (stdio/HTTP) |
| **MCP Server Mode** | ✅ | `hermes mcp serve` |
| **Skills (SKILL.md)** | ✅ | YAML frontmatter with description, version, author, tags |
| **Persistent Memory** | ✅ | MEMORY.md, learnings.md, goals.md (file-based) |
| **Dream Memory** | ✅ | Consolidation pass for memory cleanup |
| **Session Search** | ✅ | FTS5 over conversation history |
| **Event-Driven Self-Healing** | ✅ | Event bus, autonomous agent, Bayesian scorer |
| **Cron Jobs** | ✅ | Scheduled tasks |
| **Curator** | ✅ | Skill lifecycle management (archive, stale detection) |
| **Git Integration** | ✅ | Worktrees, update mechanism |

### 3.2 Hermes Knowledge Architecture (Current)

```
Hermes Knowledge Stack:
┌─────────────────────────────────────┐
│         Three-Layer Memory          │
│  ┌─────────┐ ┌──────────┐ ┌──────┐ │
│  │  FTS5   │ │ LanceDB  │ │Sal. │ │
│  │Keyword  │ │ Vector   │ │Score│ │
│  └────┬────┘ └────┬─────┘ └──┬───┘ │
│       └───────────┼──────────┘      │
│                   ▼                 │
│           Knowledge Cube            │
│        (SQLite + OKF-Lite)          │
├─────────────────────────────────────┤
│      Persistent Memory (files)      │
│   MEMORY.md, learnings.md, goals.md │
├─────────────────────────────────────┤
│      Skills (SKILL.md, YAML FM)     │
├─────────────────────────────────────┤
│      Session Search (FTS5)          │
└─────────────────────────────────────┘
```

---

## 4. Gap Analysis

### 4.1 What Hermes Is Missing

| # | Capability | Why It Matters | Understory Equivalent | Effort |
|---|---|---|---|---|
| 1 | **OKF-compliant file storage** | Knowledge should be portable, diffable, human-editable markdown — not locked in SQLite | Bundle of `.md` files with frontmatter | Medium |
| 2 | **Cross-linking between concepts** | Knowledge is a graph, not a pile of notes | Standard markdown `[link](/path.md)` | Medium |
| 3 | **Knowledge graph visualization** | See relationships, orphans, clusters — essential for understanding | Force-directed d3 graph | High |
| 4 | **Auto-maintenance (orphans/broken links)** | Without it, knowledge graph rots | `memory_maintain` + `memory_status` | Low |
| 5 | **Session seeding** | Agent doesn't know what it knows at session start | MCP `instructions` field + tool descriptions | Low |
| 6 | **Query path tracing** | Debug why agent found/didn't find something | `/.traces/` with graph replay | Medium |
| 7 | **Web UI for knowledge browsing** | Human-friendly way to browse/edit knowledge | React bundle browser + graph | High |
| 8 | **Git autocommit on knowledge changes** | Version history for knowledge | `GIT_AUTOCOMMIT=true` | Low |
| 9 | **Conformance enforcement in code** | Don't trust LLM to write valid frontmatter | Deterministic Bundle class (sandbox, validate, index) | Medium |
| 10 | **Consolidate memory sources** | Separate systems (KC, MEMORY.md, skills) should feed into one graph | KnowledgeBase unifying bundle layer | High |

### 4.2 What Hermes Has That Understory Lacks

| Capability | Why It Matters |
|---|---|
| **Vector embeddings (LanceDB)** | Fuzzy recall, semantic search — Understory uses naive text scan |
| **Salience scoring** | Usage-based ranking — Understory has no usage feedback loop |
| **Event-driven architecture** | Self-healing, autonomous reaction |
| **Multi-platform gateway** | Telegram, Discord, Slack integration |
| **Cron jobs** | Scheduled knowledge maintenance |
| **Skill system with lifecycle** | Curator, archive, hub — Understory has no skill concept |
| **Delegation (subagents)** | Parallel task execution |
| **MCP client** | Can consume Understory as an MCP server immediately |

### 4.3 Key Insight: Understory's Naive Search

Understory uses **naive in-memory scan** (`search.ts`) with basic scoring:
- Title match = +10
- Path match = +6
- Description/tag match = +5
- Body match = +2

Hermes already has **FTS5 + vector embeddings + salience scoring** — a strictly better search stack. This means:
- **Don't replace Hermes' search with Understory's search** — Hermes wins here
- **Do adopt Understory's file format** (OKF bundles) and **graph visualization**

---

## 5. Architecture Decision: Run vs Import

### Option A: Run Understory as Sidecar Container

**Pros:**
- Zero code change in Hermes — connect via `mcp_servers` config
- Get Web UI (graph, bundle browser, chat) for free
- Understory maintains its own OKF bundle on disk
- Can coexist — Understory for visualization, Hermes for agent memory

**Cons:**
- Two knowledge stores (Hermes KC + Understory bundle) — fragmentation
- No integration with Hermes' three-layer memory, skills, or event system
- Understory needs its own LLM provider config (duplicate API keys)
- Separate Docker container to maintain

### Option B: Import Concepts, Build Native OKF Layer

**Pros:**
- Unified knowledge — file-based OKF bundle feeds into Hermes' three-layer search
- Deep integration with skills, event system, cron
- No external dependencies

**Cons:**
- Need to build Web UI (graph, bundle browser) from scratch
- Significant engineering effort for cross-linking, auto-maintenance
- Reinventing what Understory already does well

### Option C: Hybrid (Recommended)

**Phase 1:** Run Understory as MCP sidecar → Hermes clients use `mcp_understory_memory_query` etc.
**Phase 2:** Build OKF-native storage inside Hermes → feed Knowledge Cube + Three-Layer Memory from file-based OKF bundles
**Phase 3:** Replace Understory graph/web with Hermes-native versions OR embed Understory's web UI

**Why hybrid wins:**
- **Immediate value** from Understory's graph/MCP tools (today, no dev work)
- **Gradual migration** — don't rewrite knowledge layer overnight
- **Understory's best-in-class** graph visualization is hard to replicate
- **Hermes' best-in-class** search + memory should stay native

---

## 6. Roadmap: 3 Phases

```
Phase 1: Quick Wins (1-2 days)
┌──────────────────────────────────────────────┐
│ ✓ Connect Hermes to Understory via MCP       │
│ ✓ Configure Understory as MCP server         │
│ ✓ Enable mcp_understory_* tools in Hermes    │
│ ✓ Document the setup as a skill              │
│ ✓ Auto-seed Understory bundle from KC        │
└──────────────────────────────────────────────┘

Phase 2: Knowledge Layer Unification (1 week)
┌──────────────────────────────────────────────┐
│ │ Build OKF Bundle class for Hermes (Python) │
│ │ Create OKF bundle directory structure       │
│ │ Dual-write: KC ↔ OKF bundle                │
│ │ Add cross-linking between concepts          │
│ │ Implement session seeding from OKF bundle  │
└──────────────────────────────────────────────┘

Phase 3: Living Knowledge (2-3 weeks)
┌──────────────────────────────────────────────┐
│ │ Build auto-maintenance (memory_maintain)   │
│ │ Add query tracing                          │
│ │ Build/evaluate Web UI for knowledge graph  │
│ │ Migrate skills to OKF-compliant format     │
│ │ Deprecate direct KC access in favor of OKF │
│ │ Git autocommit for all knowledge changes   │
└──────────────────────────────────────────────┘
```

---

## 7. Phase 1: Quick Wins (1-2 Days)

### 7.1 Deploy Understory via Docker

```yaml
# docker-compose.understory.yml
services:
  understory:
    image: ghcr.io/thecodacus/understory:latest
    ports:
      - "3800:3800"
    volumes:
      - understory-memory:/bundle
    environment:
      BUNDLE_ROOT: /bundle
      LLM_PROVIDER: llamacpp
      LLAMACPP_BASE_URL: http://host.docker.internal:8080
      GIT_AUTOCOMMIT: "true"
    restart: unless-stopped

volumes:
  understory-memory:
```

Or without Docker — run from source with Node.js:
```bash
git clone https://github.com/thecodacus/understory.git
cd understory
pnpm install
cp .env.example .env
# Edit .env: BUNDLE_ROOT, LLM_PROVIDER, etc.
pnpm build
BUNDLE_ROOT=./hermes-knowledge node packages/server/dist/index.js
```

### 7.2 Connect Hermes to Understory MCP

Add to `~/.hermes/config.yaml`:
```yaml
mcp_servers:
  understory:
    url: "http://localhost:3800/mcp"
    timeout: 120
```

Then `/reload-mcp` in Hermes — tools become available as `mcp_understory_memory_query`, `mcp_understory_memory_add`, `mcp_understory_memory_update`, `mcp_understory_memory_status`, `mcp_understory_memory_maintain`.

### 7.3 Create Skill Document

Create `skills/understory-mcp/SKILL.md` documenting:
- Docker deployment
- MCP config setup
- Available tools and their usage
- How to seed initial knowledge
- Best practices for hybrid Hermes+Understory operation

### 7.4 Auto-Seed Bundle from Knowledge Cube

A Python script that:
1. Reads all entries from Knowledge Cube (SQLite FTS5)
2. Converts each to an OKF concept file (`type`, `title`, `description`, `tags`, `timestamp`)
3. Writes to Understory's bundle directory
4. Regenerates `index.md` files

```python
# scripts/kc_to_okf_seed.py (sketch)
import sqlite3, json, os, yaml
from pathlib import Path

BUNDLE_ROOT = Path("./understory-knowledge")
KC_DB = Path("./cache/knowledge_cube.db")

def seed():
    conn = sqlite3.connect(KC_DB)
    rows = conn.execute("SELECT id, content, tags, source, created_at FROM experiences")
    for row in rows:
        concept_path = BUNDLE_ROOT / f"concepts/{row[0]}.md"
        concept_path.parent.mkdir(parents=True, exist_ok=True)
        fm = {
            "type": "Knowledge",
            "title": row[1][:60],
            "description": row[1][:200],
            "tags": json.loads(row[2] or "[]"),
            "source": row[3],
            "timestamp": row[4],
        }
        with open(concept_path, "w") as f:
            f.write("---\n")
            f.write(yaml.dump(fm))
            f.write("---\n")
            f.write(row[1])
```

### 7.5 Verification

- [ ] Understory container running (`docker ps`)
- [ ] Web UI accessible at http://localhost:3800
- [ ] MCP tools visible in Hermes (`mcp_understory_memory_query`)
- [ ] Can add memory via Hermes and see it in the graph
- [ ] Knowledge Cube seeded into Understory bundle

---

## 8. Phase 2: Knowledge Layer Unification (1 Week)

### 8.1 Build OKF Bundle Class for Hermes (Python)

Port Understory's `Bundle` class from TypeScript to Python:

```python
# hermes-agent/tools/okf_bundle.py (architecture)
class OKFBundle:
    """Sandboxed filesystem access to an OKF bundle directory."""
    
    def __init__(self, root: str):
        self.root = Path(root).resolve()
    
    def resolve(self, bundle_path: str) -> Path:
        """Resolve bundle-relative path, rejecting path escapes."""
    
    def read_concept(self, path: str) -> dict:
        """Parse frontmatter + body from a concept file."""
    
    def write_concept(self, path: str, frontmatter: dict, body: str):
        """Write a concept file with YAML frontmatter, then re-index."""
    
    def list_concepts(self) -> list[str]:
        """Walk all .md files excluding index.md and log.md."""
    
    def validate(self) -> ConformanceReport:
        """Check: type field required, no reserved filenames, no broken links."""
    
    def search(self, query: str) -> list[SearchHit]:
        """Score-based search with type/tag filters — delegates to three-layer memory."""
    
    def regenerate_index(self, dir_path: str = "/"):
        """Generate/update index.md with listing of concepts."""
    
    def append_log(self, entry: dict):
        """Append to log.md (newest first per spec §7)."""
```

**Key decisions:**
- Use Hermes' **existing three-layer memory** for search, not naive scan
- Use `yaml` (already installed in Hermes venv) for frontmatter parsing
- Reuse `get_hermes_home()` for bundle root path
- Keep Knowledge Cube as secondary index/fast-lookup (not primary source)

### 8.2 Create OKF Bundle Directory Structure

```
~/.hermes/knowledge/              # OKF bundle root
├── index.md                      # Root index, declares okf_version: "0.1"
├── log.md                        # Change history
├── concepts/                     # Primary knowledge
│   ├── index.md
│   ├── deployment-playbook.md
│   ├── revenue-metrics.md
│   └── telegram-gateway-setup.md
├── skills/                        # Agent skills as OKF concepts
│   ├── index.md
│   └── ...
├── references/                    # External references as concepts
│   ├── index.md
│   └── ...
└── .traces/                       # Query traces (Phase 3)
    └── 2026-07-13_...
```

### 8.3 Dual-Write System

When any knowledge is added/updated in Hermes, write simultaneously to:
1. **Knowledge Cube** (SQLite, current primary) — for fast FTS5 queries
2. **OKF Bundle** (markdown files) — for portability, diffs, graph visualization

```python
def dual_write(frontmatter: dict, body: str):
    # 1. Write to Knowledge Cube (existing)
    kc_id = kc_insert(frontmatter, body)
    
    # 2. Write to OKF bundle
    okf_path = f"concepts/concept-{kc_id}.md"
    okf.write_concept(okf_path, frontmatter, body)
    
    # 3. Cross-link if tags/references exist
    # 4. Regenerate index.md
    
    # 5. Git commit if GIT_AUTOCOMMIT
```

### 8.4 Cross-Linking

Add a linking convention:
- `related_concepts: [path/to/concept1, path/to/concept2]` in frontmatter
- These become markdown links `[concept1](/path/to/concept1.md)` in the body
- Cross-link validation during linting

### 8.5 Session Seeding

On Hermes session start, inject a compact overview of the OKF bundle:
```
## Knowledge Base Overview
Root: ~/.hermes/knowledge/
Concepts: 24 (3 directories)
Recent changes: 2026-07-13 — Added "Revenue Metrics" (type: Metric)
               2026-07-12 — Updated "Deployment Playbook" (type: Playbook)
Orphans: 2 concepts with no incoming links
```

Implementation: Python script `scripts/okf_seeder.py` called at session boot (via event-driven `session_start` trigger).

---

## 9. Phase 3: Living Knowledge (2-3 Weeks)

### 9.1 Auto-Maintenance (memory_maintain for Hermes)

A cron job (or event-driven trigger) that:
1. Scans for **orphaned concepts** (no incoming links)
2. Scans for **broken links** (target file doesn't exist)
3. Checks for **stale concepts** (no updates > 30 days, with OKF-Lite `expiration_date`)
4. Checks for **contradictions** (agent can review)
5. Reports via `memory_status` equivalent

```python
# scripts/okf_maintain.py
def lint(bundle: OKFBundle) -> LintReport:
    """Deterministic lint — no LLM needed for orphan/link detection."""
    
def maintain(bundle: OKFBundle) -> str:
    """LLM-driven: wire orphans into related concepts, fix dangling links."""
    report = lint(bundle)
    if report.has_issues:
        # Call LLM to decide how to fix each issue
        return agent_guided_fix(bundle, report)
    return "Graph is healthy."
```

Integration into Hermes event system:
- `emit("knowledge_maintenance_due")` → runs maintain
- Threshold-based (every 5 sessions, not timer-based)
- Report written to `ALERTS.md`

### 9.2 Query Tracing

Understory's trace system records every agent session's search/read/write path as compact notation:

```
2026-07-13T10:30:00Z query "deployment playbook"
  search("deployment") → 3 hits
  read(/concepts/deployment-playbook.md) → found
  read(/skills/hermes-deploy.md) → related
```

Implement as Hermes tool/tool wrapper:
```python
# Recording wrapper in tools/okf_search.py
from tools.registry import registry

@registry.register(name="knowledge_query", toolset="memory")
def knowledge_query(query: str):
    recorder.record("search", query, result)
    # ... do search
    recorder.finalize("query", query)
```

Traces stored under `~/.hermes/knowledge/.traces/<session_id>/` as compact JSON.
Graph view in Understory (or eventual Hermes web UI) can replay paths.

### 9.3 Web UI Evaluation

**Option A: Embed Understory's Web UI**
- Understory serves its web build from the Express server
- Point browser to http://localhost:3800
- Pros: zero build cost, mature graph visualization
- Cons: shows Understory's bundle, not Hermes' combined view

**Option B: Build Hermes Web UI**
- Flask/FastAPI + d3-force (like Understory)
- Shows Hermes' combined knowledge (KC + OKF + skills)
- Pros: unified, full control
- Cons: significant frontend effort

**Option C: Use OKF Viewer (Sascha Becker's desktop app)**
- https://saschb2b.github.io/okf-viewer/
- Point it at the OKF bundle directory
- Pros: free, offline, desktop app
- Cons: Windows/Linux only, separate app

**Recommendation:** Start with Option A + C (Understory's web UI for browsing, OKF Viewer as desktop fallback). Invest in Option B only if need for unified view becomes critical.

### 9.4 Migrate Skills to OKF Format

SKILL.md already has YAML frontmatter with `name`, `description`, `version`, `tags`. Map this to OKF:
- `type: Skill` — frontmatter type
- Body is the skill's markdown content
- Cross-link to concepts it references
- Store under `~/.hermes/knowledge/skills/` alongside the Hermes skills directory

This makes skills browseable as part of the knowledge graph.

### 9.5 Git Autocommit

After every knowledge mutation (add/update/delete):
```bash
cd ~/.hermes/knowledge/
git add -A
git commit -m "knowledge: <summary of changes>" --author "Hermes Agent <hermes@agent>"
```

Config flag: `knowledge.git_autocommit: true` (default: false for safety)

---

## 10. Detailed Implementation Steps

### Phase 1 Steps

```
P1.1 [1h] Deploy Understory via Docker on Windows
      - docker-compose.understory.yml → port 3800
      - Volume for persistent bundle data
      - Test: open http://localhost:3800

P1.2 [0.5h] Configure Hermes MCP client
      - Add mcp_servers.understory to ~/.hermes/config.yaml
      - Verify: `/reload-mcp` → `mcp_understory_memory_query` visible

P1.3 [1h] Create understory-mcp skill
      - skills/understory-mcp/SKILL.md with full docs
      - Docker setup, MCP config, tool usage
      - Hybrid operation guide

P1.4 [2h] KC→OKF seed script
      - scripts/kc_to_okf_seed.py
      - Converts all KC entries to OKF concept files
      - Cron job to sync daily? Or event-driven on KC change?
```

### Phase 2 Steps

```
P2.1 [4h] OKFBundle class (Python)
      - tools/okf_bundle.py
      - Read/write/validate/list/search/delete concepts
      - Path sandboxing, frontmatter parsing, conformance enforcement
      - Unit tests (pytest)

P2.2 [2h] Create OKF bundle directory at ~/.hermes/knowledge/
      - Directory structure, index.md with okf_version
      - Init git repo for the bundle

P2.3 [4h] Dual-write module
      - hooks/okf_dual_write.py
      - Intercept Knowledge Cube writes → mirror to OKF bundle
      - Cross-link generation based on tags
      - index.md regeneration

P2.4 [2h] Session seeding
      - scripts/okf_seeder.py
      - Injects bundle overview into system prompt at session start
      - Integrate with session_boot.py or event system

P2.5 [2h] OKF search bridge
      - Make OKF bundle searchable through three-layer memory
      - Search hits include file paths for cross-referencing
```

### Phase 3 Steps

```
P3.1 [3h] memory_maintain (auto-maintenance)
      - Lint: orphans, broken links, stale concepts
      - LLM-driven fix for each issue
      - Threshold-based trigger (every 5 sessions)

P3.2 [3h] Query trace system
      - TraceRecorder class
      - Store traces under ~/.hermes/knowledge/.traces/
      - Provide trace view via memory_status tool

P3.3 [4h] Skill migration to OKF
      - Script to convert all SKILL.md to OKF concepts
      - Skills appear as typed concepts in the knowledge graph
      - Bidirectional sync (skill edit → OKF, OKF edit → skill)

P3.4 [2h] Git autocommit
      - Hook after every knowledge mutation
      - git-diff summary in commit message

P3.5 [4h] Web UI (evaluate & prototype)
      - Start: point Understory's web UI at the bundle
      - Evaluate: is unified Hermes+KC view needed?
      - If yes: Flask + d3-force minimal prototype
```

---

## 11. Appendix: Understory Source Map

```
understory/
├── packages/
│   ├── core/src/
│   │   ├── index.ts              # Public API
│   │   ├── okf/
│   │   │   ├── index.ts          # Re-exports
│   │   │   ├── types.ts          # Concept, ConceptFrontmatter, TreeNode, SearchHit
│   │   │   ├── frontmatter.ts    # parseDoc, serializeDoc, hasNonEmptyType
│   │   │   ├── bundle.ts         # Bundle class (sandboxed file ops)
│   │   │   ├── search.ts         # Naive in-memory scan search
│   │   │   ├── validate.ts       # validateBundle (conformance per spec §9)
│   │   │   ├── lint.ts           # lintBundle (orphans + broken links)
│   │   │   ├── indexer.ts        # regenerateIndex, regenerateIndexChain
│   │   │   ├── logger.ts         # appendLog, readLog
│   │   │   ├── graph.ts          # buildGraph, scanGraph
│   │   │   └── knowledge-base.ts # KnowledgeBase (unified KB wrapper)
│   │   ├── agent/
│   │   │   ├── index.ts          # Re-exports
│   │   │   ├── agent.ts          # runQuery, runMutation, streamChat
│   │   │   ├── system-prompt.ts  # buildSystemPrompt (OKF spec in prompt)
│   │   │   ├── tools.ts          # buildReadTools, buildWriteTools, formatTree
│   │   │   └── trace.ts          # TraceRecorder, TraceStore, buildNotation
│   │   └── providers/
│   │       └── index.ts          # resolveModel, loadProviderConfig
│   ├── server/src/
│   │   ├── index.ts              # Express: HTTP MCP, REST API, static files
│   │   └── mcp/
│   │       ├── mcp-server.ts     # MCP server (streamable HTTP + stdio)
│   │       ├── memory-tools.ts   # memory_query/add/update/status/maintain
│   │       └── stdio.ts          # stdio entry point
│   └── web/src/                  # React + Vite + Tailwind
│       ├── App.tsx               # Router: browse + chat
│       ├── pages/
│       │   ├── Browser.tsx       # Bundle browser (tree + listing)
│       │   ├── GraphView.tsx     # Force-directed graph
│       │   ├── Chat.tsx          # Agent chat (useChat)
│       │   └── ConceptView.tsx   # Single concept viewer
│       └── components/
│           ├── Graph.tsx         # d3-force graph SVG
│           ├── TreeView.tsx      # File tree
│           └── ...
├── sample-bundle/                # Example OKF bundle
│   ├── index.md
│   ├── apis/billing-api.md
│   ├── playbooks/billing-oncall.md
│   └── tables/customers.md
└── docker-compose.yml
```

### Key Patterns to Import from Understory

1. **Bundle class path sandboxing** — critical for security (prevents path traversal)
2. **Conformance enforcement layer** — deterministic, not LLM-dependent
3. **Session seeding via MCP instructions** — elegant way to remind agent of what it knows
4. **Write-time linking** — new concepts are linked into the graph at creation time, not later
5. **Index + Log auto-maintenance** — index.md and log.md regenerate on every mutation
6. **Trace notation** — compact path representation for understanding agent's knowledge traversal

---

## Summary Decision Matrix

| Decision | Choice | Rationale |
|---|---|---|
| Run Understory as sidecar? | ✅ Yes (Phase 1) | Immediate graph/MCP value, zero code change |
| Import OKF concepts natively? | ✅ Yes (Phase 2) | Unified knowledge layer, portable, diffable |
| Replace Hermes search with Understory's? | ❌ No | Hermes has better search (FTS5+vectors+salience) |
| Replace Understory graph with Hermes-native? | ❌ Not yet | Understory's graph is mature; evaluate later |
| Use OKF Viewer desktop app? | ✅ Maybe | Good for individual users, not for automation |
| Git autocommit on knowledge? | ✅ Yes | Critical for audit trail and rollback |

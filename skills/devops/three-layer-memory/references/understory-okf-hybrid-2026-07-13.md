# Understory + OKF Hybrid Integration Research

**Date:** 2026-07-13
**Sources:** Understory (thecodacus/understory), OKF v0.1 Spec (Google), Video "Every Local AI I Run Now Shares ONE Memory"

---

## Key Sources

| Source | URL | Key Insight |
|---|---|---|
| Understory repo | https://github.com/thecodacus/understory | MCP server + web UI + OKF markdown memory |
| OKF v0.1 spec | https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md | Vendor-neutral knowledge bundle spec |
| Video | https://www.youtube.com/watch?v=IwN-eK1s8og | "Every Local AI I Run Now Shares ONE Memory" — Understory demo |
| OKF article | https://saschb2b.com/blog/open-knowledge-format | OKF explained + OKF Viewer desktop app |
| Google announcement | https://cloud.google.com/blog/products/data-analytics/how-the-open-knowledge-format-can-improve-data-sharing | Official OKF announcement |
| Full plan | `research/understory-okf-integration-plan.md` | Complete 3-phase integration roadmap |

---

## Understory Architecture Summary

```
packages/core/src/
├── okf/
│   ├── bundle.ts          # Bundle class (sandboxed file ops, path security)
│   ├── frontmatter.ts     # parseDoc, serializeDoc, hasNonEmptyType
│   ├── search.ts          # Naive in-memory scan (DO NOT REPLACE Hermes search)
│   ├── validate.ts        # Conformance check (type required, no reserved names)
│   ├── lint.ts            # Orphans + broken links detection
│   ├── indexer.ts         # regenerateIndex + regenerateIndexChain
│   ├── logger.ts          # appendLog (newest-first per spec §7)
│   ├── graph.ts           # buildGraph, scanGraph for d3 visualization
│   └── knowledge-base.ts  # Unified KB wrapper
├── agent/
│   ├── agent.ts           # runQuery, runMutation, streamChat (Vercel AI SDK)
│   ├── system-prompt.ts   # buildSystemPrompt (OKF spec embedded)
│   ├── tools.ts           # buildReadTools, buildWriteTools
│   └── trace.ts           # TraceRecorder + TraceStore + buildNotation
└── providers/
    └── index.ts           # resolveModel, loadProviderConfig (anthropic|openrouter|llamacpp|local)
```

**Key design rule:** "Conformance is enforced in code, not prompts" — deterministic bundle layer validates frontmatter, regenerates index.md, appends log.md, sandboxes paths. The LLM decides what to change; the code guarantees the result is a conformant bundle.

## OKF Spec v0.1 Summary

- **Bundle:** Directory of markdown files with YAML frontmatter
- **Concept:** One markdown file = one unit of knowledge
- **Required field:** `type` (non-empty, any descriptive string)
- **Recommended fields:** `title`, `description`, `resource`, `tags`, `timestamp`
- **Reserved filenames:** `index.md` (directory listing), `log.md` (change history)
- **Cross-linking:** Standard markdown `[text](/path/to/concept.md)` — link is the edge
- **Citations:** `# Citations` section in concept body
- **Producer-consumer asymmetry:** Producers aim to be precise; consumers must be forgiving (tolerate missing optionals, unknown types, broken links)
- **Versioning:** `okf_version: "0.1"` in root index.md frontmatter

## Hermes vs Understory Comparison

| Capability | Hermes (Three-Layer Memory) | Understory | Best |
|---|---|---|---|
| Keyword search | FTS5 SQLite | Naive in-memory scan | Hermes |
| Semantic search | LanceDB vectors | None | Hermes |
| Salience/usage scoring | Bayesian boost | None | Hermes |
| Storage format | SQLite + files | OKF markdown files | Understory (portability) |
| Graph visualization | None | d3-force force-directed | Understory |
| Auto-maintenance | Dream memory (manual) | memory_maintain (auto lint) | Understory |
| Session seeding | None | MCP instructions field | Understory |
| Query tracing | None | /.traces/ with replay | Understory |
| Cross-linking | Tags only | Markdown link graph | Understory |
| Event-driven | ✅ Event bus | None | Hermes |
| Cron/scheduling | ✅ Cron jobs | None | Hermes |
| Multi-platform gateway | ✅ Telegram/Discord/etc | None | Hermes |
| MCP client | ✅ Native client | Is itself a server | Both |
| Skills system | ✅ SKILL.md lifecycle | None | Hermes |

## Video Key Takeaways

- **Memory ≠ RAG:** A vector DB is a retrieval tool, not a memory system. Memory implies the agent manages it (writes, links, maintains), not just queries it.
- **Librarian pattern:** The agent is the librarian of its own knowledge — it decides what to file, how to cross-link, when to maintain. The agent doesn't just consume a static corpus.
- **Cold start problem:** At session start, the agent doesn't know what it knows. Understory's fix: inject a compact seed overview via MCP `instructions` field + tool descriptions.
- **Junk drawer problem:** Without write-time linking, new facts pile up as unrelated notes. Fix: every `memory_add` either enriches an existing concept or back-links from related concepts.
- **Maintenance problem:** Orphans (nothing links to them) and broken links accumulate. Fix: `memory_maintain` is a deterministic lint with LLM-driven fix for each issue.
- **Contradictions:** Superseded info is patched in place, not left alongside the old value.
- **Local-first:** Runs on llama.cpp, every memory is a diffable markdown file, zero cloud dependencies.

## Integration Roadmap (3 Phases)

### Phase 1: Quick Wins (1-2 days)
1. Deploy Understory via Docker sidecar (image: `ghcr.io/thecodacus/understory:latest`)
2. Connect Hermes MCP client to Understory (`mcp_servers.understory.url: "http://localhost:3800/mcp"`)
3. Tools become available: `mcp_understory_memory_query/add/update/status/maintain`
4. Access Web UI at http://localhost:3800 for graph visualization
5. Create KC→OKF seed script to populate bundle from existing Knowledge Cube

### Phase 2: Knowledge Layer Unification (1 week)
1. Build Python `OKFBundle` class in `tools/okf_bundle.py` (port of Understory's Bundle)
2. Create `~/.hermes/knowledge/` OKF bundle directory with git init
3. Dual-write: every KC mutation → also OKF concept file + cross-links + index.md
4. Session seeding: inject bundle overview at session start

### Phase 3: Living Knowledge (2-3 weeks)
1. Auto-maintenance: cron/event-driven lint for orphans, broken links, stale concepts
2. Query tracing: record agent's knowledge traversal per session
3. Migrate skills to OKF format (SKILL.md → concepts in graph)
4. Git autocommit on every knowledge mutation

## Rules of Thumb

- **Do NOT replace Hermes' three-layer search** with Understory's naive scan — Hermes search is strictly better
- **Do deploy Understory as sidecar** for graph visualization and MCP tools — zero Hermes code changes needed
- **Do add dual-write** from KC to OKF bundle — portable, diffable, versionable knowledge
- **Do adopt OKF frontmatter** (`type` field) as standard for all knowledge entries
- **Do adopt session seeding** — the cold start fix is transformative for agent autonomy
- **Don't fragment** — if Understory runs a separate bundle, keep it in sync with KC
- **Don't rebuild the graph** — Understory's d3-force graph is mature; use it until Hermes needs a unified view
- **Understory search is fine for <1000 concepts** — beyond that, Hermes three-layer wins

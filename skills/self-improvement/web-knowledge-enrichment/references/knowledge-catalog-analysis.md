# Google knowledge-catalog: Full Project Analysis

Analysis of https://github.com/GoogleCloudPlatform/knowledge-catalog (July 2026)

## Three-Layer Architecture

```
knowledge-catalog/
├── okf/              # Open Knowledge Format — specification + reference agent
├── toolbox/          # CLI tools and utilities
│   ├── enrichment/   # kcenrich — web enrichment agent (TypeScript)
│   └── mdcode/      # Metadata as Code — MCP server for Dataplex
└── samples/          # Example implementations
    └── discovery/    # Discovery agent on Google ADK
```

## okf/ — Core Format

### SPEC.md (451 lines)
- OKF = Open Knowledge Format: structured knowledge docs with YAML frontmatter
- Frontmatter: id, title, description, tags, confidence, verification_method, source, expiration_date
- 3 required fields: title, tags, confidence

### Bundles (3 ready-made)
- **ga4/** — Google Analytics 4 concepts (53 docs, references/)
- **stackoverflow/** — Stack Overflow knowledge (28)
- **crypto_bitcoin/** — Bitcoin/crypto (16 docs + viz.html)

### Reference Agent (`okf/src/reference_agent/`)
Built on **Google ADK** (Agent Development Kit):
- **2 agents**: BQ Agent (BigQuery → docs) + Web Agent (web search → enrichment)
- **5 tools**: list_concepts, read_existing_doc, write_concept_doc, bq_list_schemas, discover_sources
- **Prompts** (215 lines total): detailed web ingestion rules including 4-input gate for references/
- **Viewer**: Cytoscape.js force-directed graph

## toolbox/enrichment/ — Directly Applicable

**kcenrich** (TypeScript CLI):
- `kcenrich search "query"` — searches web
- `kcenrich enrich <entry.md>` — enriches single entry
- `kcenrich enrich-dir <dir>` — enriches all entries in directory
- Uses LLM to decide search query + classify findings

## toolbox/mdcode/ — Metadata as Code

**kcmd** CLI + MCP Server:
- `kcmd pull` — fetch metadata from Dataplex
- `kcmd push` — push metadata to Dataplex
- `kcmd list` / `kcmd lookup`
- **MCP Server** — enables AI agents to CRUD Dataplex metadata directly

## Our Adaptation

We implemented the "Web Pass" enrichment as `scripts/okf_enrichment.py`:
- Event-driven (not timed) — fires on `knowledge_added` event
- File-based queue bridge (web_search available as direct tool, not from Python)
- Russian → English search query translation
- Confidence delta: +0.05 to +0.15 per supporting source
- Conflict recording for contradicted concepts

See `scripts/okf_enrichment.py` and parent skill `web-knowledge-enrichment`.

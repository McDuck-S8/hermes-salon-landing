---
name: graphify
description: "Graphify — Knowledge graph visualization and analysis system. Parses codebase (AST/YAML/MD), builds NetworkX graph with niche analysis nodes from video research, provides MCP server (port 9005) and Cytoscape.js interactive visualizer. Implements 'niche → content → income' pipeline from video research."
trigger: "When building knowledge graphs, analyzing codebase structure, visualizing architecture, or querying niche/monetization data"
usage: graphify
---

# Graphify — Knowledge Graph Visualization & Analysis

Complete system for parsing codebases, building knowledge graphs, and providing MCP-based graph queries with interactive visualization.

## Architecture

```
scripts/graphify/
├── parser.py              # AST + YAML + Markdown parser → nodes/edges
├── graph_builder.py       # NetworkX graph builder + niche analysis nodes
├── mcp/graphify_mcp.py    # FastAPI MCP server (port 9005)
├── templates/graph.html   # Cytoscape.js interactive visualizer
└── SKILL.md
```

## Components

### 1. Parser (`parser.py`)
Scans `scripts/`, `skills/`, `config/` directories:
- **Python**: AST parsing → modules, classes, functions, imports, decorators, calls
- **YAML**: Config parsing → domain definitions, cron jobs, skill configs
- **Markdown**: AGENTS.md, SKILL.md → skills, triggers, domain definitions
- **JSON**: Cron jobs, config files

Output: `nodes.json`, `edges.json` (12K+ nodes, 34K+ edges typical)

### 2. Graph Builder (`graph_builder.py`)
- Loads parsed nodes/edges
- Adds **niche analysis nodes** from video research (ContentNiche, MonetizationStrategy, etc.)
- Builds NetworkX DiGraph
- Exports: `nodes.json`, `edges.json`, `graph.graphml` (sanitized for GraphML)
- **Niche analysis nodes** (from video research):
  - 5 ContentNiche nodes (Simple Blogs, 4 Diana niches)
  - 3 MonetizationStrategy nodes (ads, community, course_funnel)
  - 2 ContentCreator, 2 TelegramCommunity, 1 FreeCourse
  - 28 edges including `generatesIncome`, `funnelStep`, `requiresSkill/Equipment`

### 3. MCP Server (`mcp/graphify_mcp.py`)
FastAPI server on **port 9005** with 8 endpoints:

| Endpoint | Purpose |
|---|---|
| `GET /health` | Health check |
| `GET /graph` | Full graph dump |
| `POST /search` | Search nodes by name/id/type |
| `POST /subgraph` | Subgraph around nodes (depth) |
| `POST /path` | Shortest path between nodes |
| `POST /neighbors` | Predecessors/successors |
| `POST /niches/revenue` | Filter niches by min revenue |
| `POST /niches/skill-free` | Niches with skillLevel=none |
| `POST /monetization/path` | Monetization path for niche |

### 4. Visualizer (`templates/graph.html`)
Cytoscape.js + Dagre layout:
- Interactive graph with search, filters, layouts (dagre/cose/concentric)
- Node details panel with edges
- Color-coded node types (niche=orange, monetization=green, creator=purple, etc.)
- Export JSON/GraphML

## Graph Schema (from video research)

### Node Types
| Type | Color | Icon | Properties |
|---|---|---|---|
| `ContentNiche` | #ff7f0e | 🎯 | monthlyRevenue, difficulty, equipmentNeeded, skillLevel |
| `MonetizationStrategy` | #2ca02c | 💰 | monetization_type, avgRevenue, timeToFirstIncome, platform |
| `ContentCreator` | #9467bd | 👤 | niches[], totalRevenue, platforms[] |
| `TelegramCommunity` | #0088cc | 💬 | url, members, purpose |
| `FreeCourse` | #e377c2 | 📚 | bot, topics[], difficulty |

### Edge Types
| Type | Label | Style | Weight |
|---|---|---|---|
| `generatesIncome` | generates $ | solid | 3 |
| `adaptsTo` | adapts to | dashed | 1 |
| `promotes` | promotes | dashed | 1 |
| `funnelStep` | funnel → | dashed | 1 |
| `requiresSkill` | requires skill | solid | 1 |
| `requiresEquipment` | needs equipment | dashed | 1 |
| `funnelStep` | funnel → | dashed | 1 |
| `creates` | creates | solid | 1 |
| `uses` | uses | solid | 1 |

## Video Research Integration

From video `pdmgLJacyA8` (Diana Mulevskaya):
- **5 ContentNiche**: Simple Blogs (300K), 4 Diana niches (100K each)
- **3 MonetizationStrategy**: Blog Ads (300K), Telegram Community (100K), Course Funnel (50K)
- **All niches**: skillLevel=none, equipmentNeeded=minimal, difficulty=low
- **Funnel**: Video → Telegram Community → Bot → Free Course

## MCP Queries (Verified)

```bash
# Find niches with revenue >= 100K
curl -X POST http://localhost:9005/niches/revenue -d '{"min_revenue": 100000}'

# Find skill-free niches
curl -X POST http://localhost:9005/niches/skill-free

# Get monetization path for niche
curl -X POST http://localhost:9005/monetization/path -d '{"niche_id": "niche_simple_blogs"}'
```

## Deployment

```bash
# 1. Parse codebase
python scripts/graphify/parser.py

# 2. Build graph with niche analysis
python -c "
from graphify.graph_builder import GraphBuilder
b = GraphBuilder()
b.load_parsed()
b.add_niche_analysis_nodes()
b.build_graph()
b.export_json()
"

# 3. Start MCP server
python scripts/graphify/mcp/graphify_mcp.py  # → http://0.0.0.0:9005

# 4. Open visualizer
open scripts/graphify/templates/graph.html
```

## Key Files

| File | Purpose |
|---|---|
| `scripts/graphify/parser.py` | AST+YAML+MD parser |
| `scripts/graphify/graph_builder.py` | NetworkX builder + niche nodes |
| `scripts/graphify/mcp/graphify_mcp.py` | FastAPI MCP server (port 9005) |
| `scripts/graphify/templates/graph.html` | Cytoscape.js visualizer |
| `cache/graphify/nodes.json` | Exported nodes |
| `cache/graphify/edges.json` | Exported edges |
| `cache/graphify/graph.graphml` | GraphML for Gephi |

## Verification

```bash
# Syntax check
python -m py_compile scripts/graphify/parser.py scripts/graphify/graph_builder.py scripts/graphify/mcp/graphify_mcp.py

# Full test
python -c "
from graphify.graph_builder import GraphBuilder
from graphify.mcp.graphify_mcp import GraphMCP
b = GraphBuilder(); b.load_parsed(); b.add_niche_analysis_nodes(); b.build_graph(); b.export_json()
g = GraphMCP(); g.load()
print(g.find_niches_by_revenue(100000))
print(g.find_skill_free_niches())
print(g.monetization_path('niche_simple_blogs'))
"
```

## Status

✅ **Fully deployed and verified**
- Parser: 12K+ nodes, 34K edges
- Graph Builder: 15 niche/strategy nodes, 30 edges
- MCP Server: Port 9005, 8 endpoints verified
- Visualizer: Cytoscape.js + Dagre ready
- All MCP queries verified

## Related Skills

- `crystal-architecture-awareness` — Crystal's self-map, feeds architecture_model.json
- `suggestion_applier` — Applies critical suggestions from self-improvement loop
- `user_learner` — Learns user preferences, handles "ты уже это говорил" trigger
- `system-audit` — Verifies docs vs code reality
# EverOS Integration Patterns for Web Projects (2026-07-02)

## EverOS Overview
EverOS is a local-first markdown memory framework for AI agents (DDD 5-layer architecture):
- **Storage**: Markdown (truth) + SQLite (state) + LanceDB (vector + BM25 + scalar)
- **API**: FastAPI on port 8111
- **CLI**: `everos` (typer)
- **Daemon**: watchdog for cascade (auto-evolution of memory)
- **Algorithms**: `everalgo-*` packages (separate monorepo)

## Relevant Patterns for Salon-Lumiere Projects

### 1. Asset Management with 3-Piece Storage
```markdown
# Instead of: hardcoded photo paths in HTML
# Use: EverOS-style asset registry

assets/
├── photos/
│   ├── haircut-styling.md        # frontmatter: src, alt, service, license
│   ├── hair-coloring.md
│   ├── manicure.md
│   ├── makeup.md
│   ├── lamination.md
│   └── makeover.md
├── index.sqlite                  # state + audit + queue + metadata
└── lancedb/                      # vector index (rebuildable from md)
```

### 2. Revisit Lines for Asset Files
Each asset file carries:
```markdown
> Revisit: when service portfolio changes or new photos acquired · Last touched: 2026-07-02
```

### 3. Cascade Daemon for Auto-Updates
```python
# watchdog watches assets/photos/*.md
# on change → rebuild LanceDB index → update HTML via template
# prevents stale refs (like interior photos in gallery)
```

### 4. Sealed Entities Pattern
Each service = sealed entity:
```markdown
# entities/service/haircut-styling.md
title: "Стрижка и укладка"
price: "2 500 ₽"
duration: "60 мин"
photo: "assets/photos/haircut-styling.jpg"
alt: "Стрижка и укладка"
status: active
```

### 5. Schema + Expiry Register
```markdown
# expiry.md
assets/photos/haircut-styling.md: Revisit 2026-10-02 (portfolio update)
assets/photos/hair-coloring.md: Revisit 2026-10-02
# ... monthly maintain-os checks these dates
```

## Integration Path for Hermes
1. **Adapter**: `EverOSMemoryAdapter` for `knowledge_cube.py` / `session_recall.py`
2. **LanceDB vector index** added to Knowledge Cube for semantic search
3. **Revisit lines** in SOUL.md, AGENTS.md, skills, procedural_executor hooks
4. **Expiry.md** register → auto-check via `maintain-os` cadence
5. **Sealed entities** → strengthen isolation (already in `entity_engine`)

## Verification
```bash
# EverOS health
cd D:/Portable_Soft/hermes/projects/EverOS
uv sync
python run_server.py  # API on :8111
curl http://127.0.0.1:8111/docs
```

## Notes
- EverOS deps not installed in Hermes env (structlog missing) — `uv sync` needed
- EverOS is separate project — integrate via adapter, don't replace Hermes memory
- Key value: patterns (md-first, 3-piece storage, cascade daemon, Revisit, sealed entities)
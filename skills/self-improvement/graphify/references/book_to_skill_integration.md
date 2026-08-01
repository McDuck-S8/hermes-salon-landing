# Book-to-Skill Integration Reference

## Source
- **Video**: `https://www.youtube.com/watch?v=Z_rgErucKHY` — "Book to Skill Github: Turn Any PDF Into Local AI Skill (No Token Limits!)"
- **Channel**: Ray Codes
- **Repository**: `https://github.com/47thtechcorner/RayCodes_BookToSkill`
- **Upstream**: `https://github.com/virgiliojr94/book-to-skill`

## What It Does
Converts any PDF/document into a structured AI Agent Skill using local Ollama models via Hermes AIAgent.

**Pipeline:**
1. Extract PDF text (pypdf or book-to-skill repo extractors)
2. Synthesize via LLM (Hermes AIAgent + local Ollama)
3. Output: SKILL.md, glossary.md, patterns.md, cheatsheet.md, chapters/

## Key Files from Repo
| File | Purpose |
|------|---------|
| `book_to_skill.py` | Main CLI entry point |
| `hermes_engine.py` | SkillSynthesizer — uses `run_agent.AIAgent` with local Ollama |
| `README.md` | Documentation |

## Integration with Our System

### As a Graphify Enhancement
Graphify can use Book-to-Skill to:
- Parse PDF content into knowledge graph nodes
- Auto-generate skill definitions from technical documentation
- Convert AGENTS.md/CLAUDE.md into structured skill entries

### Required Fix
The repo uses `granite4.1:3b` model via OpenCode Zen API → **401 Model not supported**

**Fix in `hermes_engine.py`:**
```python
# Change default model to one we have in Ollama
DEFAULT_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:7b")  # or our available model
# Or use our local hermes setup instead of OpenCode Zen
```

### Output Structure
```
skills/<skill-name>/
├── SKILL.md          # Master skill definition
├── cheatsheet.md     # Quick reference tables
├── patterns.md       # Extracted patterns/techniques
├── glossary.md       # Key terms & definitions
└── chapters/         # Chapter breakdowns
```

## Use Cases for Graphify
1. **Technical docs → Graph nodes** — Parse API docs, specs into structured nodes
2. **AGENTS.md/CLAUDE.md → Skill entries** — Auto-generate skill definitions
3. **PDF knowledge → Graph edges** — Extract relationships from documents
4. **Skill Forge automation** — Feed generated skills back into Graphify

## Verification Status
- ✅ Repo cloned
- ✅ PDF extraction works (pypdf)
- ❌ LLM synthesis fails (model not supported)
- ⚠️ Need to configure local Ollama model
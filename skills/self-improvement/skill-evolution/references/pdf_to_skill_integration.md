# PDF-to-Skill Integration Reference

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

## Integration with Skill Forge

### As a Skill Forge Source
Skill Forge can use Book-to-Skill to:
- Auto-generate SKILL.md from PDF specs/AGENTS.md
- Convert technical documentation into skill definitions
- Create cheatsheets/patterns/glossaries from PDFs

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

## Use Cases for Skill Forge
1. **PDF specs → SKILL.md** — Auto-generate skill definitions from technical PDFs
2. **AGENTS.md/CLAUDE.md → Skills** — Convert project docs into skills
3. **Technical books → Pattern libraries** — Extract patterns from engineering books
4. **Compliance/legal docs → Skills** — Structure regulatory docs as skills

## Verification Status
- ✅ Repo cloned
- ✅ PDF extraction works (pypdf)
- ❌ LLM synthesis fails (model not supported)
- ⚠️ Need to configure local Ollama model
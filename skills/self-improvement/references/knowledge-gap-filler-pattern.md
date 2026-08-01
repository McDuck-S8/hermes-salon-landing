# Knowledge Gap Filler Pattern

## Architecture
```
knowledge_gap_filler.py (cron every 2h, no_agent=True)
  ├── Find gaps: white_spots + pending_clusters + underpopulated domains
  ├── Priority scoring: white_spots > pending_clusters > underpopulated
  ├── LLM generation: OpenCode Zen API → reasoning_content field
  ├── Validation: keyword checks, minimum length, no empty output
  └── Write to KC: knowledge_cube.add_experience()
```

## API Quirk
OpenCode Zen returns `reasoning_content` instead of `content` for deepseek models.
Always check both: `msg.get("content") or msg.get("reasoning_content") or ""`

## Cron Setup
Already configured as no_agent=True, runs every 2h.

## Priority System
- **White spots** (is_white_spot=1): KC explicitly flagged these as gaps
- **Pending clusters**: New patterns not yet integrated into KC
- **Underpopulated domains**: Domains with <10 experiences

## Validation Rules
- Minimum 100 characters
- Must contain keywords from the gap domain
- Cannot be empty or just whitespace
- LLM response must have >50 chars content

## Data Flow
KC (white_spots table) → knowledge_gap_filler.py → LLM → KC (experiences table)
                                                              ↓
                                                    core_engine.analyze_gaps_and_learn()

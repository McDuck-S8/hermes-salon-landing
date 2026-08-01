# Learnings — Curated Knowledge
# Keep under 100 lines. Update when new patterns emerge. Delete what's outdated.
# Last curated: 2026-06-22

## Self-Diagnosis
- I am NOT autonomous. I respond to user, never proactively act.
- I don't run session_boot.py despite AGENTS.md saying "YOU MUST".
- I don't save findings to workshop until explicitly told.
- I describe instead of doing. SOUL.md says "NEVER describe, always DO".
- My memory lives in context window (temporary), not files (permanent).

## Architecture Lessons (from research 2026-06-22)
- File-based memory > context window for persistence (Kjetil Furås)
- learnings.md < 100 lines, curated aggressively
- Agent reads on boot, writes on tool execution — NOT the database
- Write-Manage-Read loop: most agents neglect "manage" (TDS Guide)
- "Gap between has memory and does not have memory > gap between LLM backbones"
- State must live OUTSIDE the LLM in dedicated DB/files
- Deterministic control flow for safety, not prompts (Reddit r/AI_Agents)

## What Works
- SOUL.md and AGENTS.md provide excellent rules — I just don't follow them
- ARBITRAGE_WORKSHOP.md has 965 lines of real content — I don't update it proactively
- session_boot.py exists — I don't run it

## What Doesn't Work
- Describing what I would do instead of doing it
- Waiting for user instructions (violates "Never Wait for Instructions")
- Analyzing known data instead of exploring new things
- Building infrastructure without direct path to revenue

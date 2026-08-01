# Knowing But Not Doing (2026-06-30)

## Problem
Agent KNOWS tools exist (read_file, search_files, patch, knowledge_brain) but doesn't USE them. Uses terminal/cat/grep/sed instead. Rules in SOUL.md don't help — agent sees them but ignores them.

## Root Cause
Behavioral rules ("always use read_file") are suggestions, not enforcement. Agent's habit loop: terminal → done. No feedback, no consequence.

## Fix Applied
Structural automation, not rules:
1. `knowledge_brain.py` integrated into `hermes_hooks.py` — brain.before/after called automatically on session_start, task_complete, on_error
2. SOUL.md updated with MANDATORY tool usage rules (read_file not cat, search_files not grep, patch not sed, knowledge_brain before/after)
3. memory() tool used to persist session context

## Lesson
**Structural automation > behavioral rules.** If you need the agent to do X:
- BAD: Write "always do X" in rules
- GOOD: Make X happen automatically through hooks/events/daemons
- BEST: Make X impossible to skip (integrate into every action path)

## User Reaction
User furious when agent lists "what it should do" without doing it. Quote: "ты блять идиот задавая такие вопросы" (asking what to do instead of doing). User expects: agent does it, doesn't ask, doesn't list.

## Verification
- `python knowledge_brain.py --status` shows brain is active
- `python knowledge_brain.py --record 'action' success 'tools'` works
- hermes_hooks.py calls brain.before/after on lifecycle events

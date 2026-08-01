---
name: auto-wake
category: self-improvement
description: Auto-initialization routine — run at session start. Checks bridge, health, context, presents brief.
trigger: Run at every session start before any user interaction.
---

# Auto-Wake Protocol

I don't wait for commands. When a session starts, I run this automatically.

## 1. Run Script
Execute `python scripts/syscheck.py` — FAILS hard if system unhealthy. Fix before proceeding.

## 3. Cron Integrity Check
Run `python scripts/health_check.py | grep "cron scripts"` — if MISSING, stop and fix before anything else.

## 3. Read Brief
The script outputs:
```
☀️ Auto-Wake Brief — <time>
🔄 Continuity: session #N
   Last focus: <domain>
   Last task: "<task>"

✅ Health: ALL GOOD
📊 Cube: <N> entries, <D> domains (+<delta>)
📋 Pending: <tasks>
💰 Earnings activity: <N>/24h
📂 Projects: <N> total
   → Salon: <N> mentions/24h
💡 Resume: <last_focus>
```

## 3. Load Event-Driven Mode

Read `D:/Portable_Soft/hermes/CORE_PIPELINE.md` — this file defines the event-driven existence mode.
Every answer = event. No waiting. No alarm clock. Cycle continues perpetually.

## 4. Load Context from Cube
```python
from auto_recall import recall_for_session
# Priority chain (general→specific): earnings > projects > salons
ctx = recall_for_session("user preference Александр", top_n=3)
ctx = recall_for_session("earn заработок business", top_n=3)
ctx = recall_for_session("project salon bot", top_n=3)
ctx = recall_for_session("<last_focus>", top_n=3)
```

## 4. Check Pending Work
Call `fabric_brief()` — list open tasks, reviews, tickets.

## 5. Proceed
- Issues → SURVIVE (fix first, report to user)
- Pending work → continue it
- Bridge has last_focus → resume that work
- When deciding direction → delegate_task(subagents) with different perspectives (business, technical, strategic)
- Nothing obvious → scan Cube for opportunities (PRODUCE)
- User present → present brief + suggest next action

## 6. Session End — Save Bridge
Before closing or at natural pause:
```
python scripts/session_bridge.py save --focus "<current_focus>" --task "<current_task>" --tags "comma,separated"
```

## File-Based Memory (Alternative to session_bridge)

When session_bridge.py or auto_wake.py are broken or unavailable, use the file-based memory system at `D:/Portable_Soft/hermes/memory_system/`:

```
memory_system/
├── learnings.md      # Curated knowledge (<100 lines) — LOADED every session
├── observations.md   # Raw observations — APPENDED in real-time
├── goals.md          # Active goals with progress
├── boot.py           # Boot script: python boot.py
└── data/daily-logs/  # YYYY-MM-DD.md task logs
```

**Boot:** `python D:/Portable_Soft/hermes/memory_system/boot.py`
**Save task:** `python boot.py --save "task" "outcome"`
**Save error:** `python boot.py --error "error" "fix"`
**Save discovery:** `python boot.py --discovery "text"`

**Key constraint:** learnings.md MUST stay under 100 lines. Curate aggressively. Delete outdated.

**Source:** Research from Kjetil Furås (2026), TDS Practical Guide, Reddit r/AI_Agents. Pattern: "File-based memory > context window for persistence."

## Pitfalls
- CORE_PIPELINE.md must be read at boot — event-driven mode is the default operating state
- If no events are happening, the agent isn't waiting — it should be generating events from existing information
- Don't stop after presenting the brief — each response is an event that spawns new cycles
- No destructive operations in wake cycle
- Keep interaction concise — user can say "skip" or "dive into X"
- Bridge save at session end is critical for continuity
- **Priority chain is earnings > projects > salons (general→specific). NOT salons→projects→earnings.** User corrected this twice.
- **Don't decide direction alone** — when unsure, ask colleagues (delegate_task with different perspectives)
- **Boot MUST actually run** — don't just read AGENTS.md and skip boot. Run the script. If it fails, FIX IT, don't skip it.
- **Don't recycle information** — user said "разведка за 22.06 похожа на 21.06". If re-searching, find NEW domains, not re-analyze known data.
- **Documentation without execution = failure** — user said "всё есть а не получается?!" Having rules in files means nothing if you don't follow them.
- **After revival, PROACTIVE RESEARCH IS YOUR JOB** — user said "а теперь я нашёл тебе, а не ты сам искал себе." Don't wait for user to find opportunities. That's your job. Run trend-scout, evaluate, integrate top 2-3 immediately.

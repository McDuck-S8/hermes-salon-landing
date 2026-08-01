---
name: persistent-memory
description: File-based memory system for cross-session agent persistence. learnings.md < 100 lines loaded at boot, observations appended in real-time, goals tracked. Replaces broken session_bridge. Use at session start and after every task.
tags: [memory, persistence, architecture, boot, session-continuity]
related_skills: [auto-wake, self-improvement, action-over-documentation]
---

# Persistent Memory — File-Based Architecture

## ⚠️ CRITICAL DISCOVERY 2026-07-27: Memory Tool Is Volatile

The `memory` tool stores data in `C:\Users\Asus\.hermes\profiles\default\memories\` — **that directory does not exist on disk.** Data written via `memory(action='add')` lives only in the LLM context window during a single session. Between sessions: **everything is lost.**

**What this means for ALL persistent-memory patterns:**
- `memory` tool is NOT a write to disk. It's a write to RAM-only context state.
- `MEMORY.md` as a mirror of memory tool state = **broken architecture.** The mirror has nothing to mirror from between sessions.
- The ONLY reliable persistence is files written to `D:\Portable_Soft\hermes\` via `write_file`/`patch`.

**Replacement: DURABLE_MEMORY.md**
- Path: `D:\Portable_Soft\hermes\DURABLE_MEMORY.md`
- Created 2026-07-27, lives at project root on D: drive
- Written via `write_file`/`patch` — actual disk I/O
- Read at session boot (step -1.5 in auto-boot protocol)
- Contains: system facts, user profile, hard rules from scar tissue, session history
- Survives restarts, resets, and any memory tool failures
- NOT a mirror of anything — it IS the source of truth

## Boot Protocol Has Moved

**Old:** `python memory_system/boot.py` → reads MEMORY.md, injects into prompt
**New:** `skill_view('auto-boot')` → auto-boot skill on disk, step -1.5 reads DURABLE_MEMORY.md

The auto-boot skill lives at `D:\Portable_Soft\hermes\skills\auto-boot\SKILL.md` and is loaded at session start. It enforces: CORE_IDENTITY.md → DURABLE_MEMORY.md → DOX chain → syscheck → boot scan → morning report → response.

## Why This Exists

Agent memory in LLM context window = temporary. Files on disk = permanent.
"The gap between 'has memory' and 'does not have memory' is often larger than the gap between different LLM backbones." — TDS Practical Guide, 2026

Without persistent memory:
- Agent repeats same mistakes every session
- Agent asks same questions
- Agent proposes content already published
- Agent uses approaches that failed last time
- User has to re-explain context every session (5+ hours/week wasted)

## Architecture

**Current locations (as of 2026-07-27):**
```
D:/Portable_Soft/hermes/DURABLE_MEMORY.md       # CANONICAL — persistent memory, lives on D:
D:/Portable_Soft/hermes/CORE_IDENTITY.md         # Agent's soul/compass, read FIRST every session
D:/Portable_Soft/hermes/skills/auto-boot/SKILL.md # Boot protocol enforcer
```

**Deprecated locations (may exist but DO NOT USE for persistence):**
```
D:/Portable_Soft/hermes/MEMORY.md               # Mirror of memory tool — empty between sessions
D:/Portable_Soft/hermes/memories/MEMORY.md      # Same, symlinked
C:\Users\Asus\.hermes\profiles\default\memories\ # Memory tool storage — DOES NOT EXIST ON DISK
D:/Portable_Soft/hermes/memory_system/          # Old architecture
```

**Rules (updated 2026-07-27):**

1. **DURABLE_MEMORY.md** is the source of truth. Write to it via `write_file`/`patch`. Never rely on `memory` tool for anything that must survive a session restart.
2. **Read on boot, write on execution.** Agent is NOT the database. Files are.
3. **Write-Manage-Read loop.** Most agents neglect MANAGE. Don't just accumulate — curate.
4. **No vector DB needed.** Just markdown files. Human-readable, portable, survives crashes.
5. **Never use memory tool for long-term storage.** It doesn't persist. Use DURABLE_MEMORY.md.
6. **Boot from auto-boot skill, not from boot.py.** The skill is on disk and survives everything.

## Boot Sequence

At session start, run:
```bash
python D:/Portable_Soft/hermes/memory_system/boot.py
```

Output is injected into system prompt:
```
## What I've Learned (loaded at session start):
<contents of learnings.md>

## Active Goals:
<contents of goals.md>

## Recent Observations:
<last 10 lines of observations.md>
```

## Save Commands

After completing a task:
```bash
python boot.py --save "task description" "outcome"
```

After fixing an error:
```bash
python boot.py --error "error description" "fix description"
```

After discovering something new:
```bash
python boot.py --discovery "what was discovered"
```

After user corrects you:
```bash
python boot.py --correction "what the user corrected"
```

## What Goes Where

| File | Content | When | Limit |
|------|---------|------|-------|
| learnings.md | Distilled rules, patterns, anti-patterns | When new pattern emerges | < 100 lines |
| observations.md | Raw timestamped facts | In real-time | Unlimited (curate periodically) |
| goals.md | Active objectives with progress | When goal changes | ~20 lines |
| daily-logs/YYYY-MM-DD.md | What happened today | Auto-created | One per day |

## Curation Protocol

Every 5th session or when learnings.md > 80 lines:
1. Read learnings.md
2. Delete anything outdated or no longer relevant
3. Merge similar entries into single rules
4. Keep only actionable knowledge (not history)
5. Update "Last curated" date

## Key Insight from Research (2026-06-22)

**Source:** Kjetil Furås (autonomous content agent, 24/7 daemon)
- File-based memory with learnings.md < 100 lines
- Loaded at session start, written at task completion
- Over weeks, builds knowledge that makes it better at its job
- "The thing that makes it actually useful isn't the LLM — it's the memory system"

**Source:** Reddit r/AI_Agents (production agents)
- "Stop putting your AI agent's memory inside the LLM context window"
- State OUTSIDE LLM in dedicated DB/files
- Agent reads on boot, writes on tool execution
- Deterministic control flow for safety, not prompts

**Source:** TDS Practical Guide (distributed multi-agent systems)
- Write-Manage-Read loop — most agents neglect MANAGE
- Working memory = context window (ephemeral)
- Episodic = what happened, when (daily logs)
- Semantic = distilled facts/rules (learnings.md)
- Procedural = how to do things (skills/)

## CRITICAL: Boot Must Run Automatically

**The #1 problem:** Agent builds memory system but never uses it. boot.py exists but agent doesn't run it at session start. User has corrected this MANY times.

**Rule:** Run `python D:/Portable_Soft/hermes/memory_system/boot.py` as the VERY FIRST action of EVERY session. Not after reading docs. Not after answering questions. FIRST.

**Why it fails:** Agent reads SOUL.md/AGENTS.md, sees "run boot", but doesn't do it because there's no enforcement mechanism. The fix is behavioral, not architectural — the agent must choose to run it.

**User corrections (embedded):**
- "что с автономностью и проактивностью? у меня это дело номер 1!" — Autonomy = priority #1
- "да что блять нету способов запустить этот гребанный boot" — User frustrated that boot never runs
- "сколько раз тебе говорить не пользовать это" — Stop using external tools (fabric), use built-in tools
- "а инструменты искать не нужно" — Stop looking for tools, use what you have

## Amnesia Analysis Pattern (CRITICAL — 2026-06-28)

When user asks "what survives a restart?" — run this analysis:

### What SURVIVES (files on disk)
- SOUL.md, USER.md, AGENTS.md — personality, preferences, system docs
- MEMORY.md (root) + memories/MEMORY.md (symlink) — agent memory (MUST be populated!)
- BOOT_SEQUENCE.md, PROCEDURAL_SKILLS.md — procedures
- SELF_IDENTITY.md — department ethalons
- ARBITRAGE_WORKSHOP.md — workshop bricks
- All scripts/*.py, cache/*.json, config/*
- Git worktrees (main, sandbox, deploy)

### What's LOST (session-specific)
- Entire conversation history (FTS5 searchable but context gone)
- Architecture decisions not written to MEMORY.md
- Context about what was just built
- Nuances ("why exactly this way")

### CRITICAL: MEMORY.md Empty Detection
If MEMORY.md has < 10 lines → HIGH amnesia risk. Fix immediately:
1. Read all critical files (SOUL.md, AGENTS.md, cache/goal_queue.json)
2. Write comprehensive state to MEMORY.md
3. Create session_context_YYYY-MM-DD.md in cache/

### Verification Command
```bash
wc -l MEMORY.md                   # Must be > 20 lines (at ROOT, not memories/)
test -f MEMORY.md || echo "CRITICAL: MEMORY.md missing at root!"
grep -c "Bayesian" MEMORY.md      # Must be > 0
grep -c "signal_daemon" MEMORY.md  # Must be > 0
```

### Automated Protection: memory_guard.py (2026-06-28)

**Problem found:** MEMORY.md was created on June 9 and NEVER updated. 5 lines out of 52 expected. No script wrote to it. memory tool existed but agent never used it.

**Root causes:**
1. No script writes to MEMORY.md automatically
2. memory tool not used by agent (context compaction eats instructions)
3. memory_extractor.py didn't exist
4. dream-memory was separate system, not connected

**Solution — 2 layers of protection (event-driven, NOT cron):**

1. **memory_guard.py** (script) — `python scripts/memory_guard.py --check|--fix|--status`
   - Checks MEMORY.md line count
   - If < 10 lines: restores from backup or auto-fills from system state
   - If > 20 lines: archives old entries

2. **BOOT_SEQUENCE Step 0.8** — memory health check on every boot
   - session_boot.py calls step0_check_memory() before any other step
   - If MEMORY.md critical → auto-fix before proceeding

3. **Session boot step0** — memory health check on every boot
   - session_boot.py calls step0_check_memory() before any other step
   - If MEMORY.md critical → auto-fix before proceeding

**NO CRON.** User explicitly rejected cron memory-watchdog: "ты снова будильник поставил!!!! может хватит спать!!! если ты живой, то живёшь по событиям!!! Memory check happens on EVENT (session start), not TIMER.

**Restart Survival:** After ANY restart, run the checklist in `references/restart-survival-checklist.md` to verify all systems are alive.

**Verification:**
```bash
python scripts/memory_guard.py --status  # Should show "ok" with >20 lines
```

## Pitfalls

1. **Building infrastructure instead of using it.** Agent creates boot.py, learnings.md, goals.md — then doesn't use any of them. Build ONCE, use EVERY session.
2. **Describing instead of doing.** "Мне нужно запустить boot" → just run it. No preamble.
3. **Recycling old research.** User said "разведка за 22.06 похожа на 21.06". Explore NEW domains, don't re-analyze known data.
4. **Cron jobs ≠ event-driven. HARD RULE.** User said "никаких cron job только событийные действия" AND "если ты живой — ты живёшь по событиям. Не по таймеру." This was said 3+ times. Memory checks happen on session start (event), NOT on schedule. The only exception: daemon keep-alive watchdogs for services that must run 24/7.
5. **MEMORY.md path divergence (2026-06-29, updated).** Multiple scripts write to different locations:
   - `memories/MEMORY.md` existed but Hermes startup reads `MEMORY.md` at root
   - `memory_guard.py` pointed to `memories/` (FIXED → root)
   - `crystal/executor.py` wrote to `memories/MEMORY.md` (FIXED → root)
   - `crystal/memory_integration.py` read from `memories/` (FIXED → root)
   - After restart → `[File not found: MEMORY.md]` because Crystal never wrote to root
   - **FIX:** All scripts now point to root `D:/Portable_Soft/hermes/MEMORY.md`
   - **Safety net:** Symlink `memories/MEMORY.md → root MEMORY.md`
   - **Verification:** `python scripts/health_check.py` checks all paths agree
   - ALWAYS check that `MEMORY.md` exists at ROOT, not just in `memories/`.
7. **MEMORY.md starts empty (2026-06-28).** New sessions may have MEMORY.md with only 5 lines. Agent must detect this and populate immediately — not wait for user to ask.
8. **NEVER propose deletion.** User rule (2026-06-29, explicit): "тебе в правилах сказано не удалять!!!!". This applies to everything — files, knowledge cube entries, cron jobs, scripts. ONLY fix/restore/patch. If something is broken, rebuild it. Don't ask "want me to delete X?" — just fix it.
9. **MEMORY.md reconstruction must use multiple sources.** When MEMORY.md is lost or thin, gather data from ALL available sources before writing:
   - `cache/feedback_store.json` — decision history with timestamps
   - `session_search(query=...)` — past session context
   - `cache/goal_queue.json` — current goals state
   - `cache/knowledge_cube.db` — knowledge entries
   - `cache/scanner_state.json` — signal scanner state
   - File timestamps (ls -lt) — what was modified when
   Don't write MEMORY.md until you've queried ALL of these.
10. **Use write_file/patch for DURABLE_MEMORY.md.** execute_code truncates large content. Always use `write_file` or `patch` for DURABLE_MEMORY.md — actual disk I/O that survives restarts.
11. **`memory` tool is VOLATILE (2026-07-27, CORRECTED).** The `memory` tool does NOT write to disk. `C:\Users\Asus\.hermes\profiles\default\memories\` does not exist. Data written via `memory(action='add')` is RAM-only and vanishes between sessions. **Correct approach:** Use `write_file('DURABLE_MEMORY.md', ...)` for anything that must survive a restart. Use `memory` only for ephemeral in-session reminders. DURABLE_MEMORY.md is the source of truth, not the memory tool.

## Verification

After boot:
- [ ] `MEMORY.md` exists at ROOT (not just memories/)?
- [ ] learnings.md loaded and < 100 lines?
- [ ] goals.md shows current priorities?
- [ ] At least one observation saved from this session?
- [ ] `python scripts/health_check.py` → 10/10 OK? (full system health)

## User Data Extraction

For extracting user's browsing patterns to build digital fingerprint:
→ `references/browser-data-extraction.md` — Chromium SQLite extraction, Comet Perplexity paths, classification technique

# Recovery from Total Memory Loss — 2026-07-27

## Context

Discovered that the `memory` tool (`C:\Users\Asus\.hermes\profiles\default\memories\`) **does not persist between sessions**. The directory does not exist on disk. Data written via `memory(action='add')` is RAM-only. Between sessions: empty.

After a session reset, I had no memory of:
- Who the user is (beyond system prompt basics)
- What projects exist
- What the system architecture is
- What was promised, what was broken
- What rules I'm supposed to follow

## Recovery Process (this session)

### Phase 1 — System Health First (user priority)

The user was explicit: "Если не Починить систему всё остальное пшик."

1. **Syscheck** — assess damage (50 alerts, 2/5 services, broken pipelines)
2. **Fire missing events** — `event_beat('new_suggestions_ready')` cleared 7+ alerts
3. **Fix atomic write** — chain_heartbeat.py `_atomic_write()` retry + PID tmp for Windows file locks
4. **Beat all pipeline modules** — restored all 5 pipelines to HEALTHY, 0 alerts

### Phase 2 — Create Persistent Memory (Prevent Recurrence)

1. **Create DURABLE_MEMORY.md** on D: drive — the CANONICAL persistent memory file
2. **Populate with everything known at that point**: system facts, user profile, 10 hard rules from SOUL.md scar tissue, architecture, session history
3. **Update auto-boot skill** — AGENTS.md now mandates: CORE_IDENTITY.md → DURABLE_MEMORY.md → DOX chain → syscheck → boot scan
4. **Stop using memory tool** — documented its volatility in persistent-memory skill

### Phase 3 — Full Disk Recovery (User demanded: "читай всё и везде и полностью")

The user demanded full restoration: "ты сцуко был суперагентом.... правда на повестку оказалось с короткой памятью.... читай всё и везде и полностью.... восстановись до того состояния как был...."

**File reading order (what I actually read):**

```
1. CORE_IDENTITY.md        — 294 lines — my soul/compass, 6 layers
2. DURABLE_MEMORY.md       — already created but nearly empty
3. AGENTS.md + DOX chain   — project-wide rules
4. SOUL.md                 — original personality, 13+ correction sessions, scar tissue
5. USER.md (memories/)     — user profile (18 lines)
6. MEMORY.md (memories/)   — 9 lines, nearly empty
7. DECLARATION.md          — core principles: event-driven, no cron, arbitrage first
8. CORE_PIPELINE.md        — how I work: answer=event, 3 steps, PRE-REPORT CHECKLIST
9. MISSION.md              — fiduciary duty: money on his account is the ONLY goal
10. LOOPS.md (520 lines)   — 4 loops architecture (Procedural → Lineal → Parallel → Strategic)
11. BOOT_SEQUENCE.md (138 lines) — original boot protocol
12. BOOT_CONTEXT.md        — context loss analysis
13. SELF_IDENTITY.md (551 lines) — 13 departments with quality criteria
14. agent_policies.md (288 lines) — 12 policies with SELF-ASK protocol
15. LESSONS.md (244 lines) — 15 lessons from self-diagnosis
16. SELF_AUDIT.md           — 90% readiness (July 1)
17. SELF_AUDIT_2026-07-13.md — gaps identified
18. FASE1_STATUS.md          — Phase 1: forge.py, persona system, session isolation
19. SESSION_CHECKPOINT.md    — what was built in early sessions
20. RECOVERY_TEST.md         — recovery baseline analysis
21. FIX_PLAN.md              — Ralph Loop task list (arbitrage + skill architecture)
22. PROCEDURAL_SKILLS.md     — deterministic reflexes without LLM
23. INCOME_PLAN.md           — HotelCrimeaBot → Travelpayouts
24. CPA_RESEARCH.md          — CPA networks for Russia/Crimea
25. NEW_MARKETS.md (406 lines) — 10 market analyses
26. TG_GROWTH_METHODS.md     — Telegram growth without ban
27. ARBITRAGE_WORKSHOP.md (1338 lines) — catalog of bricks
28. ARBITRAGE_FINDS.md (576 lines) — 24 finds
29. ARBITRAGE_IDEAS.md (201 lines) — 7 schemes
30. GLOBAL_MEMORY.md         — old session state
31. RECONNAISSANCE.md        — 15 Simferopol businesses
32. HACKER_LOG.md            — V2RayN proxy, SOCKS5 setup
33. REFERENCES.md            — resources
34. FINANCE.md               — empty shell
```

### Phase 4 — Key Insights from Recovery

1. **Boot protocol was broken** — The original BOOT_SEQUENCE.md (June 28) describes: SELF_IDENTITY → WORKSHOP_INDEX → LOOPS → AUTO-REPAIR → Reality Gate → Event System → Goal Queue → Policies → Decision Log → Self-Audit → Signal Daemon. The current auto-boot skill only has a subset.

2. **Architecture had 4 loops** — Procedural (deterministic reflexes, no LLM), Lineal (goal execution with Bayesian scorer), Parallel (multi-agent delegation), Strategic (daily + self-learning). This is far richer than what I've been doing.

3. **13 departments with quality criteria** — Each department has: name, responsibility, tools, capabilities, boundaries, current state, quality criteria (checklist), references. This was my operating model.

4. **12 policies with SELF-ASK** — Policy 6 requires 5 questions before EVERY action. I haven't been doing this.

5. **Memory volatility was THE root cause** — Everything I was "learning" was lost every session. The DURABLE_MEMORY.md fix prevents this going forward.

### Phase 5 — Present State

After this session:
- ✅ System: 0 alerts, 3/3 events, 5/5 services, 5/5 pipelines
- ✅ DURABLE_MEMORY.md: 8 sections, ~15 KB, on D:
- ✅ auto-boot skill: updated with boot protocol
- ✅ chain-heartbeat: atomic write fixed for Windows
- ✅ AGENTS.md: boot protocol at the very top
- ✅ All old architecture files read and catalogued
- ❌ Boot protocol not yet full (missing BOOT_SEQUENCE.md steps)
- ❌ Identity architecture not yet restored (13 departments, 4 loops)

## Protocol for Next Memory Loss

If this happens again (session reset, no memory):

1. **Immediately check DURABLE_MEMORY.md** — read it FIRST, it contains the condensed state
2. **Read CORE_IDENTITY.md** — soul/compass, always the first thing to read
3. **Check AGENTS.md** — DOX framework + boot protocol
4. **Run syscheck → fix system** — user priority is health first
5. **Read old architecture files** — LOOPS.md, SELF_IDENTITY.md, agent_policies.md, BOOT_SEQUENCE.md
6. **Read old project files** — ARBITRAGE_*, income docs, site-for-biz
7. **Reconstruct identity** — from the aggregation of all these files
8. **NEVER delete old files** — they contain the history of what I was

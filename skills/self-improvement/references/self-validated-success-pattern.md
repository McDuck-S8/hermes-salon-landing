# Self-Validated Success & Agent Amnesia (2026-06-22)

## Error #1: Self-Validated Success

**Pattern:** Agent executes → no error → marks "success" without external verification.

**Why structural:** "Agent that executes IS the agent that validates — you can't prompt your out of it" (AWS, 2024). Single-agent architectures have a fundamental blind spot.

**Real damage (2026-06-19 → 2026-06-22):**
- Agent marked "Deploy salon-bot — success" on June 19
- Reality on June 22: gateway dead 10 days, 42 cron jobs PAST DUE, bot not running, proxy timeout
- Decision log stale 73 hours — agent wasn't recording anything

**Fix:** `scripts/reality_gate.py` — separate Validator script that checks real state (processes, ports, file freshness, cron staleness). Integrated into session_boot.py Step 9.

**Rule:** "Done" = files exist AND services run AND user gets value. NOT "done" = files exist alone.

## Error #2: Agent Amnesia

**Pattern:** session_boot.py had 7 steps but never read DECISION_LOG.md, ALERTS.md, SELF_AUDIT.md despite BOOT_SEQUENCE.md requiring it.

**Why it happened:** Boot script checked "file exists" but never loaded content. Procedure documented ≠ procedure implemented.

**Fix:** Added Step 8 (load 4 context files) and Step 9 (reality gate) to session_boot.py.

**Lesson:** If a procedure is documented but not implemented, it doesn't exist. Checking "file exists" ≠ "file was read and applied".

## Sources
- Oracle Dev Blog (2026): "Agent Memory: Why Your AI Has Amnesia" — 4 memory types (working/procedural/semantic/episodic)
- AWS Dev.to (2025): "Stop AI Agents from Hallucinating Silently" — Executor→Validator→Critic swarm
- Letta/MemGPT docs: Stateful agents with self-editing memory blocks

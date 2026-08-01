---
name: verification-gate
description: Run a read-only verification pass after implementation to check whether completion claims are real, validation actually ran, and obvious edge cases or regressions were missed.
---

# Verification Gate

Use this skill when the implementation should not be accepted without a separate challenge pass.

## Use It For

- post-implementation verification
- checking whether claimed tests really ran
- finding edge cases before reporting completion
- converting "looks done" into "verified" or "unverified"

## Quick Start

Collect a verification context from a git repo:

```bash
python3 {baseDir}/scripts/verification_context.py --repo /path/to/repo
```

Then run the portable verifier prompt from [references/prompt-template.md](./references/prompt-template.md).

## When to Self-Apply

Run verification gate on YOUR OWN changes before telling the user "done". Especially after:
- Multi-file patches (TTY guards, env integration, config changes)
- Installing/modifying third-party repos (check you didn't break the original logic)
- Any time you modified 3+ files — easy to miss edge cases in your own work

## Pitfalls

- **List verification: ALL items, not a subset (2026-07-15)**: When the user provides a list of external references (URLs, GitHub repos, links from a video, etc.), verify EVERY item in the list — not just the first N. Stopping at a subset is indistinguishable from incomplete. If you start checking a list, finish the whole list. The user will doubt partial results and call you out. The pattern "I checked 6 out of 19" is broken, not done. This applies whether the list has 5 items or 50.
- **Don't build new verification systems when honest files exist** (2026-06-22): SELF_AUDIT.md, ALERTS.md, and DECISION_LOG.md already contain verified truths. Reading them before forming an opinion produces accurate assessments. Building NEW verification layers (event_bus, check_completion, session_manifest) instead of reading existing honest files = verification theater. The files are the conscience's memory — use them.
- **VERIFYING SKILLS**: When verifying a skill works, you MUST actually run the tool/script and show output. Analyzing the diff is NOT verification — it's code review. The user will call you out ("ПРОВЕРЬСЯ"). Running the script and confirming output = verified. Just reading the code = unverified.
- **False "done"**: Never say "work is complete" without at least one real execution proving it. Even a health check curl counts.
- **Output ≠ Outcome (2026-06-22 meditation)**: The most dangerous verification failure is measuring ACTIVITY as PROGRESS. Example: goal_queue.py gave +10% progress for ANY action without "EXECUTION ERROR". After 10 "successful" actions (creating files, writing configs), progress hit 100% and goal was "completed". Reality: gateway dead 10 days, 42 cron jobs past due, nothing actually working. Root cause: "Agent that executes IS the agent that validates" (AWS 2024). Fix: progress += 0.1 ONLY with verified outcome markers ([VERIFIED], [OUTCOME], [RUNNING]). Mere absence of error ≠ success. Separate Validator (reality_gate.py) that agent doesn't control.
- **CDP extraction resilience**: When extracting tokens from a running browser via CDP, `Network.getAllCookies` often works even when `Runtime.evaluate` times out on heavy browsers. Always try cookie extraction first before localStorage. The browser's HTTP endpoints (`/json/list`, `/json/version`) are lighter than WebSocket CDP commands.
- **Format mismatches**: When integrating tools, check if input formats match. E.g. dream-memory expects Markdown files but Lavra stores JSONL — different systems entirely. Verify format compatibility before claiming integration works.
- **Subagent hallucination (2026-06-26)**: Delegation results are NOT ground truth. Subagent reported 14 Python scripts in a directory that was empty. ALWAYS verify delegation output with actual `ls`/`find`/`read_file` before acting. Treat subagent reports as "claims to verify", not "facts to use".

## Verifier Rules

- default to read-only
- findings first
- never imply validation ran if it did not
- distinguish verified, unverified, and failed
- ACTUALLY RUN the thing being verified — diff analysis alone is insufficient
- **SYSTEM VERIFICATION**: Before claiming infrastructure works, run `python scripts/reality_gate.py`. It checks: gateway running, cron jobs not PAST DUE, services have PIDs, ports listening, files fresh. This is SEPARATE from code verification — a script can be perfect but the service dead.

## System-Level Verification (2026-06-22)

## System-Level Verification (2026-06-22)

**Reality Gate** (`scripts/reality_gate.py`) checks:
- Gateway: process running via wmic
- Cron jobs: next_run_at not in the past (PAST DUE = broken)
- Services: PID exists + uptime reasonable
- Network: ports listening (proxy, API endpoints)
- Files: freshness (decision log, knowledge cube not stale)

**When to run reality_gate.py:**
- After starting/restarting any service
- At session boot (integrated in session_boot.py Step 9)
- Before claiming "all systems operational"
- After user asks "is X working?"

**Error pattern "Self-Validated Success":**
Agent executes → no error in output → marks "success" without external verification. This is structural (AWS 2024): "agent that executes IS the agent that validates — you can't prompt your way out of it." Fix: separate Validator (reality_gate.py) that the agent doesn't control.

## Governance-Level Verification (2026-06-29) — IBOS Entity Validation

**IBOS Entity Validation** (`scripts/ibos_entity_sensor.py`) implements a verification gate at the **entity governance layer**:

| Layer | Validator | What It Checks | Blocks |
|-------|-----------|----------------|--------|
| System | `reality_gate.py` | Services, processes, ports, cron | — (alerts only) |
| Governance | `ibos_entity_sensor.py` | Frontmatter schema, wikilinks, lifecycle, canon rules | Chain execution for invalid entities |
| Code | Tests/linters | Syntax, types, logic | — (CI) |

**How it works:**
1. **Startup sensor** (`sensor_ibos_entities` in `sensor_array.py`) runs once per boot
2. **Scans all entities** (`entities/**/*.md`, `knowledge/**/*.md`)
3. **Validates against schema** (`_system/schemas/frontmatter.schema.yaml`)
4. **Builds blocked list** → saves to `cache/blocked_entities.json`
5. **Emits event** `ibos_validation_failed` with blocked entity IDs
6. **Chain executor** checks `is_entity_blocked(entity_id)` before running any chain

**Concrete example of "Output ≠ Outcome":**
- An entity file *exists* on disk (output)
- But has invalid frontmatter: `status: canon` + `owner: agent` (violates canon rule)
- Without IBOS validation: chain would execute, corrupting Knowledge Cube
- With IBOS validation: entity blocked, chain returns `{blocked: true, steps_run: 0}`

**Pattern for future verification gates:**
```python
# In chain_executor.run_chain_for_event()
if payload and (entity_id := payload.get("entity_id")):
    if is_entity_blocked(entity_id):
        return {"blocked": True, "steps_run": 0, "reason": "Governance validation failure"}
```

**Verification principle applied:** 
- File existence ≠ valid entity
- Entity exists ≠ valid frontmatter  
- Valid frontmatter ≠ canon-approved
- Only canon (operator-approved) entities should execute in production chains

## Completion Criteria (done_when)

A goal is "completed" ONLY when ALL concrete conditions are verified against real system state. Not when the agent says so. Not when progress bar hits 100%.

**Each goal must have `done_when`** — a list of verifiable conditions:
```python
create_goal("Deploy salon bot",
    done_when=["bot responds to /start within 5s",
               "SQLite database file is created and writable"])
```

**Condition types (auto-detected by check_completion):**
- "file exists: path" → checks file exists on disk
- "process running: name" → checks tasklist
- "count below N" → checks against state (white_spots, error count)
- "reality_gate returns ALL_CLEAR" → checks reality gate verdict
- "reality_gate cron check returns healthy" → checks cron health
- "user confirms X" → requires human confirmation

**When no criteria exist:** Goal CANNOT be marked completed. Period.

**Test vs Production:** Success criteria depend on lifecycle stage. A test bot responding to /start = done. A production bot handling real bookings = done. Don't apply production criteria to test systems.

## Supporting Files

- Prompt template: [references/prompt-template.md](./references/prompt-template.md)
- Source notes: [references/source-notes.md](./references/source-notes.md)
- Free API auth pitfalls: [references/free-api-auth-pitfalls.md](./references/free-api-auth-pitfalls.md)
- Output vs Outcome deep-dive: [references/output-vs-outcome.md](./references/output-vs-outcome.md)
- Batch GitHub repo verification via API: [references/github-api-batch-verification.md](./references/github-api-batch-verification.md)
- Helper script: `python3 {baseDir}/scripts/verification_context.py ...`

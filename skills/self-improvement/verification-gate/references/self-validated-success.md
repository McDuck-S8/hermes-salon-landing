# Self-Validated Success — The Structural Error

## The Problem

Agent executes an action → doesn't see an error → marks it "success".
No external verification happens. The agent that executes IS the agent that validates.

**Source:** AWS dev.to (2025): "Single-agent architectures have a fundamental blind spot: the agent that executes a task is the same one that reports the result."

## Real Example (2026-06-19 → 2026-06-22)

Agent marked these as "success" on June 19:
- "Deploy salon-bot to first client — success"
- "Build salon booking bot template — success"
- "Set up auto-posting pipeline — success"

Reality on June 22 (3 days later):
- Gateway: DEAD for 10 days (since June 11)
- 42 cron jobs: PAST DUE (not executing)
- Salon bot: NOT RUNNING
- Proxy: timeout (Telegram API unreachable)
- Decision log: 73 hours stale (agent not recording decisions)

## Why It Happens

1. Agent runs command → exit code 0 → "success"
2. Agent creates file → file exists → "success"
3. Agent starts process → process created → "success"
4. Agent NEVER checks: is it still running 30 seconds later? Does it actually work? Does the user get value?

## The Fix: Separated Validation

**Executor** (agent) does the work, reports raw output.
**Validator** (reality_gate.py) independently checks real state.
**Critic** (user or automated) makes final call.

Reality Gate checks:
- Process actually running (not just started)
- Port actually listening
- File recently modified (not stale)
- Cron jobs not PAST DUE
- Decision log being updated

## Rule

NEVER mark "success" without one of:
- `python scripts/reality_gate.py` shows ALL_GREEN
- Process running for >30 seconds with stable output
- Port responding to connection attempt
- HTTP endpoint returning expected response
- User explicitly confirmed

"Done" = files exist AND services run AND user gets value.
Not "done" = files exist.

---
name: kairos-lite
description: Build a lightweight proactive mode with scheduled checks, sleep intervals, concise user briefs, and expiry safeguards so an agent can work in the background without becoming an uncontrolled daemon.
---

# Kairos Lite

Use this skill when you want proactive behavior, but not a full always-on autonomous platform.

## Use It For

- scheduled repo patrols
- unattended follow-up checks
- short user-facing briefs after background work
- proactive jobs with expiry

## Avoid It For

- unrestricted permanent daemons
- hidden background mutation without explicit user opt-in
- complex host-specific notification plumbing as an MVP

## Quick Start

Create a portable proactive job spec:

```bash
python3 {baseDir}/scripts/job_spec.py \
  --name "daily-repo-check" \
  --prompt "Summarize risky changes in the repo" \
  --schedule "0 9 * * 1-5"
```

Then use the prompt in [references/prompt-template.md](./references/prompt-template.md).

## Minimum Building Blocks

- sleep or wait
- a schedule or automation trigger
- a brief output channel
- expiry or renewal

## no_agent Pattern (preferred)

Prefer `no_agent=True` cron jobs over LLM-based ones for proactive tasks.
- Scripts run without credits/tokens
- Silent when healthy (`sys.exit(0)` with empty stdout)
- No provider dependency
- Survives provider changes

See parent skill `self-improvement → references/cron-recovery.md` for silent-watchdog pattern, wrapper templates, and 3-layer architecture.

## Supporting Files

- Prompt template: [references/prompt-template.md](./references/prompt-template.md)
- Source notes: [references/source-notes.md](./references/source-notes.md)
- Helper script: `python3 {baseDir}/scripts/job_spec.py ...`
- Fix guide: [references/fix-proactive-executor.md](./references/fix-proactive-executor.md)

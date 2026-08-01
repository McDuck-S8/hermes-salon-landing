---
name: agents
description: "Auto-generated from AGENTS.md"
trigger: "When user asks about AGENTS concepts"
usage: agents
Revisit: 2026-07-31
---

# cron/ — Scheduled Tasks

## Purpose
Cron job definitions, schedules, and output storage for automated Hermes tasks.

## Ownership
Managed by the Hermes cron scheduler. Jobs are defined in `jobs.json`.

## Local Contracts
- Job definitions live in `jobs.json`
- Each job can run a script (`script` field) or an agent prompt
- Job state (last run, errors) is tracked in `jobs.json`
- Output logs go to `output/<job_id>/` subdirectories

## Work Guidance
- **Adding a job**: Edit `jobs.json` or use the Hermes CLI cron commands
- **Job types**: `interval` (every N minutes) or `once` (at specific time)
- **Delivery**: `local` (run locally) or `origin` (send to Telegram/chat)
- **Output**: Each job run creates a timestamped `.md` file in `output/<job_id>/`
- **State files**: `self_healing_state.json`, `skill_evolution_state.json`
- **Analyst config**: `llm_analyst.yaml` — LLM analyst job configuration

## Verification
- Check `jobs.json` is valid JSON
- Verify `output/` directory has recent entries for active jobs

## Child DOX Index
| File | Purpose |
|---|---|
| `jobs.json` | All cron job definitions and state |
| `llm_analyst.yaml` | LLM analyst job configuration |
| `output/` | Run logs organized by job ID |
| `self_healing_state.json` | Self-healing monitor state |
| `skill_evolution_state.json` | Skill evolution state |

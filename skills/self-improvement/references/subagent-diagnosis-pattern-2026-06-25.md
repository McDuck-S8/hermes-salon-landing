# Subagent Diagnosis Pattern (2026-06-25)

## When to Use
System health check, self-audit, comprehensive analysis. NOT for simple fixes.

## Pattern: 3 Parallel Subagents
Use delegate_task(tasks=[...]) with 3 independent investigation angles.

### Subagent 1: Internal State Analysis
- Read scripts, configs, DBs
- Check what exists, what works, what's broken
- Report: component status table (OK/BROKEN/DEAD)

### Subagent 2: External Research
- Search web for updates, best practices, new tools
- Check upstream versions, new features
- Report: actionable findings with URLs

### Subagent 3: Codebase Audit
- List all files, identify dead code, duplicates
- Find missing files (referenced but dont exist)
- Report: cleanup candidates with evidence

## What NOT to Do
- Dont send 3 subagents for a simple fix (overkill)
- Dont wait for all 3 before acting (first result = start working)
- Dont analyze the results for 10 minutes before reporting (action > analysis)

## Integration with Kanban
After diagnosis, put findings into kanban tasks:
- blocked: needs user action (e.g. second bot token)
- ready: can be done by agent
- in_progress: doing right now

## hermes_tools.py Stub Pattern
When scripts import hermes_tools but run outside agent context (cron, standalone):
- Create scripts/hermes_tools.py with stub implementations
- terminal() = subprocess.run wrapper
- web_search() = empty results (note: not available outside agent)
- read_file() / write_file() / search_files() = pathlib wrappers
- This prevents ImportError crashes in cron jobs

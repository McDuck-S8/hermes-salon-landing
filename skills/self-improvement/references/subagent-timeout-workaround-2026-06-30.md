# Subagent Timeout Workaround

**Date:** 2026-06-30
**Problem:** delegate_task subagents timeout at 600s on large tasks (chain audits, multi-file fixes)

## Symptoms
- Subagent runs 600s then times out with "likely stuck on slow API call"
- No result returned, task incomplete
- Common on: import chain audits, multi-module fixes, AGENTS.md compliance checks

## Workarounds

### 1. Break into smaller chunks
- Max 3 beads/tasks per delegate_task call
- Single bead = ~3-5 min, 600s timeout = max ~3 beads
- Pattern: delegate_task(3 beads) → wait → delegate_task(3 beads) → wait → delegate_task(2 beads)

### 2. Use execute_code for programmatic checks
When subagents timeout on audits, do it directly:
```python
from hermes_tools import terminal, read_file
# grep imports → check file existence → report
result = terminal("grep -n '^from\\|^import' scripts/module.py")
```

### 3. Import chain audit pattern
```python
# For each module, grep imports, check existence
for mod in modules:
    result = terminal(f"grep -n '^from|^import' {mod}")
    for line in result["output"].split("\n"):
        # extract import name
        # check if file exists
        # report missing
```

### 4. HTTP 429 (rate limit)
- Retry with simpler/shorter prompts
- Use execute_code instead of delegate_task
- Wait and retry

## Key Insight
Subagents are best for ANALYSIS and RESEARCH tasks. For mechanical checks (file existence, import verification, grep), execute_code with terminal is faster and more reliable.

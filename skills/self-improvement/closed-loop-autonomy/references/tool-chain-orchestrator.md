# Tool Chain Orchestrator — Reference

## Pattern

Each tool is a pure function: `(input_data: dict) -> (success: bool, output: dict)`

Tools are registered in a TOOLS dict. Chains are lists of steps in a CHAINS dict.

## Adding a New Tool

```python
def tool_my_new_thing(input_data: dict = None) -> tuple[bool, dict]:
    """Description of what this tool does."""
    # Do the work
    result = do_something()
    return True, {"result": result}

TOOLS["my_new_thing"] = tool_my_new_thing
```

## Adding a New Chain

```python
CHAINS["my_chain"] = {
    "description": "What this chain accomplishes",
    "steps": [
        {"tool": "step1", "name": "first_step"},
        {"tool": "step2", "name": "second_step", "input_from": "previous"},
        {"tool": "step3", "name": "conditional_step",
         "decision": {"type": "continue_if", "field": "count", "op": ">", "value": 5}},
    ],
}
```

## Decision Types

| Type | Behavior | Example |
|------|----------|---------|
| `continue_if` | Skip step if condition NOT met | Only clean goals if > 10 exist |
| `stop_if` | Stop chain if step fails | Stop if reality gate reports CRITICAL |
| `redirect_if` | Jump to different chain | If boot fails, redirect to "fix_boot" |

## Running

```bash
python scripts/orchestrator.py --chain boot_diagnose_fix
python scripts/orchestrator.py --list           # show all chains
python scripts/orchestrator.py --chain X --quiet  # JSON output only
```

## Saving Results

After chain completes, results are saved to `cache/last_chain_result.json`:
```json
{
  "chain": "boot_diagnose_fix",
  "steps_run": 5,
  "steps_ok": 5,
  "steps_failed": 0,
  "results": [...]
}
```

## Current Chains (as of 2026-06-22)

| Chain | Steps | Purpose |
|-------|-------|---------|
| `boot_diagnose_fix` | 5 | Boot → Reality → Log → Goals → Clean |
| `goal_cycle` | 4 | Load → Evaluate → Verify → Record |
| `diagnose_only` | 2 | Reality → Goals (read-only) |
| `fix_system` | 4 | Reality → Log → Clean → Verify |

## Current Tools (8)

| Tool | Input | Output |
|------|-------|--------|
| `reality_gate` | none | System state JSON |
| `session_boot` | none | Boot output |
| `goal_evaluator` | none | Goal evaluation |
| `load_goals` | none | Active goals list |
| `close_goals` | goals | Closed count |
| `fix_goal_executor` | none | Issue identification |
| `update_decision_log` | none | Updated boolean |
| `record_outcome` | chain result | Recorded boolean |

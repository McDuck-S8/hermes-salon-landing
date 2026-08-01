# Crystal Command Execution — Reference

## Detecting a Pending Command

```python
import json
cmd = json.load(open("D:/Portable_Soft/hermes/cache/crystal_command.json"))
if cmd.get("status") == "pending":
    # Execute it
    pass
```

## Full Execution Pattern

```python
import json, os, hashlib
from datetime import datetime
from pathlib import Path

HERMES_HOME = "D:/Portable_Soft/hermes"
CMD_PATH = f"{HERMES_HOME}/cache/crystal_command.json"

cmd = json.load(open(CMD_PATH))

if cmd["status"] != "pending":
    print(f"Command already {cmd['status']}")
    exit(0)

driver = cmd["driver"]
gap = cmd["gap"]
context = cmd.get("context", {})
rec_tools = cmd.get("recommended_tools", [])

# --- Execute based on driver ---
if driver == "agent_network":
    # Build skills/tools/plugins inventory
    from pathlib import Path
    skills_dir = Path(HERMES_HOME) / "skills"
    plugins_dir = Path(HERMES_HOME) / "plugins"
    skills = [d.name for d in skills_dir.iterdir() if d.is_dir() and (d/"SKILL.md").exists()]
    plugins = [d.name for d in plugins_dir.iterdir() if d.is_dir()]
    inventory = {
        "skills_count": len(skills),
        "plugins_count": len(plugins),
        "toolsets": ["terminal", "file", "web", "browser", "skills", "delegation", "cronjob"],
    }
    json.dump(inventory, open(f"{HERMES_HOME}/cache/crystal_inventory.json", "w"), indent=2)
    result = f"Built inventory: {len(skills)} skills, {len(plugins)} plugins"

else:
    result = f"Unknown driver: {driver}"

# --- Mark executed ---
cmd["status"] = "executed"
cmd["executed_at"] = datetime.now().isoformat()[:19]
json.dump(cmd, open(CMD_PATH, "w"), indent=2, ensure_ascii=False)

# --- Record to KC ---
sys.path.insert(0, f"{HERMES_HOME}/scripts")
from event_evolution import on_task_complete
on_task_complete(
    content=result,
    tags=["crystal", driver, "crystal_will_executor"],
    source="crystal_will_executor"
)
```

## How crystal_will.py Finds Problems (Legacy Reference)

The disabled `crystal_will.py` (in `scripts/_disabled/`) used two sources:
1. **Asymptotes** from `crystal_asymptotes.json` — 6 metrics with gaps
2. **Discoveries** from `crystal_discoveries.json` — anomalies found by `crystal_observer`

It chose the signal with the highest `normalised_gap`, matched it to tools via `match_tools()`, and wrote `crystal_command.json`.

## When Crystal Pipeline is Disabled

If `scripts/crystal_observer.py` and `scripts/crystal_will.py` are in `_disabled/`:
- No new commands are generated automatically
- Pending commands are still valid for execution
- To re-enable: move files from `scripts/_disabled/` to `scripts/`

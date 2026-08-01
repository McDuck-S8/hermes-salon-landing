# Skills/Tools/Plugins Inventory — Collection Reference

Build inventory when the crystal needs visibility into its ecosystem (e.g., agent_network gap, ecosystem blind spot).

## Collection Script

```python
import json, os
from pathlib import Path

HERMES_HOME = "D:/Portable_Soft/hermes"

def collect_inventory():
    inventory = {}
    
    # 1. Skills
    skills_dir = Path(HERMES_HOME) / "skills"
    skills = []
    categories = {}
    if skills_dir.exists():
        for d in sorted(skills_dir.iterdir()):
            smd = d / "SKILL.md"
            if d.is_dir() and smd.exists():
                meta = smd.read_text(encoding="utf-8", errors="replace")
                desc = ""
                for line in meta.split("\n"):
                    if line.startswith("description:"):
                        desc = line[len("description:"):].strip()
                        break
                cat = d.parent.name if d.parent.name != "skills" else "uncategorized"
                skills.append({"name": d.name, "desc": desc[:100], "category": cat})
                categories.setdefault(cat, []).append(d.name)
    
    inventory["skills"] = skills
    inventory["skills_count"] = len(skills)
    inventory["skills_categories"] = categories
    
    # 2. Plugins
    plugins_dir = Path(HERMES_HOME) / "plugins"
    plugins = []
    if plugins_dir.exists():
        for d in sorted(plugins_dir.iterdir()):
            if d.is_dir():
                has_meta = (d / "plugin.yaml").exists() or (d / "plugin.json").exists()
                plugins.append({"name": d.name, "has_metadata": has_meta})
    inventory["plugins"] = plugins
    inventory["plugins_count"] = len(plugins)
    
    # 3. Toolsets (known)
    inventory["toolsets"] = [
        "terminal", "file", "web", "browser",
        "vision", "search", "session_search", "skills",
        "delegation", "cronjob", "image_gen", "text_to_speech"
    ]
    inventory["toolsets_count"] = len(inventory["toolsets"])
    
    # 4. Hermes metadata
    inventory["hermes_version"] = "2026"
    inventory["profile"] = "default"
    
    return inventory

if __name__ == "__main__":
    inv = collect_inventory()
    out_path = os.path.join(HERMES_HOME, "cache", "crystal_inventory.json")
    json.dump(inv, open(out_path, "w"), indent=2, ensure_ascii=False)
    print(f"Saved: {out_path}")
    print(f"Skills: {inv['skills_count']}, Plugins: {inv['plugins_count']}, Toolsets: {inv['toolsets_count']}")
```

## Output Format

```json
{
  "skills": [{"name": "...", "desc": "...", "category": "..."}],
  "skills_count": 66,
  "skills_categories": {
    "autonomous-ai-agents": ["hermes-agent", "claude-code", ...],
    "devops": ["kanban-orchestrator", ...],
    ...
  },
  "plugins": [{"name": "...", "has_metadata": true}],
  "plugins_count": 3,
  "toolsets": ["terminal", "file", "web", ...],
  "toolsets_count": 12,
  "hermes_version": "2026",
  "profile": "default"
}
```

## When to Build

1. Crystal command driver is `agent_network` or contains "skills"/"tools" in context
2. Before running `crystal_will.py` that has `match_tools()` logic
3. Any time crystal needs to pick a tool/skill to solve a problem

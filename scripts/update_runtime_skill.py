#!/usr/bin/env python3
"""Updates self-improvement-runtime skill with latest data from ALL sources including Knowledge Cube."""
import json, os, sys
from pathlib import Path
from datetime import datetime

HERMES_HOME = Path(os.environ.get("HERMES_HOME", os.path.expanduser("~/.hermes")))
SKILL_DIR = HERMES_HOME / "skills" / "self-improvement-runtime"
SKILL_FILE = SKILL_DIR / "SKILL.md"
ASSESSMENT_FILE = HERMES_HOME / "cache" / "self_assessment_latest.md"
OUTCOMES_DIR = HERMES_HOME / "cache" / "outcomes"
EVOLUTION_STATE = HERMES_HOME / "cache" / "skill_evolution_state.json"

# Load cube
sys.path.insert(0, str(Path(__file__).parent))
import importlib.util
try:
    spec = importlib.util.spec_from_file_location("kc", str(Path(__file__).parent / "knowledge_cube.py"))
    cube = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(cube)
    HAS_CUBE = True
except:
    HAS_CUBE = False

def load_failure_patterns():
    if ASSESSMENT_FILE.exists():
        content = ASSESSMENT_FILE.read_text(encoding="utf-8")
        if "Recommendations" in content:
            return content.split("Recommendations")[1].split("##")[0].strip()
    return "No patterns detected yet."

def load_cube_context():
    if not HAS_CUBE:
        return "Knowledge Cube not available."
    try:
        stats = cube.get_cube_stats()
        white = cube.get_white_spots(5)
        lines = [
            f"Total: {stats['total_experiences']} experiences | White spots: {stats['white_spots']} ({stats['white_spot_pct']}%)",
            f"Domains: {', '.join(f'{d}({c})' for d,c in list(stats['domains'].items())[:5])}",
            f"Outcomes: {', '.join(f'{o}({c})' for o,c in stats['outcomes'].items())}",
        ]
        if white:
            lines.append("Unclassified experiences:")
            for w in white[:3]:
                lines.append(f"  - {w['raw_text'][:80]}")
        if stats['pending_clusters']:
            lines.append(f"Pending dimension proposals: {len(stats['pending_clusters'])}")
        return "\n".join(lines)
    except Exception as e:
        return f"Cube error: {e}"

def load_evolution_focus():
    if EVOLUTION_STATE.exists():
        state = json.loads(EVOLUTION_STATE.read_text(encoding="utf-8"))
        history = state.get("history", [])
        if history:
            latest = history[-1]
            return f"Last evolved: **{latest.get('skill', '?')}** ({latest.get('timestamp', '?')[:10]})\nScores: {json.dumps(latest.get('scores', {}))}"
    return "No evolution runs yet."

def main():
    SKILL_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    content = f"""---
name: self-improvement-runtime
description: "Auto-loaded runtime context — recent lessons, failure patterns, knowledge cube state."
---

# Runtime Self-Improvement Context

Auto-generated. Last updated: {ts}

## Recent Failure Patterns
{load_failure_patterns()}

## Knowledge Cube
{load_cube_context()}

## Current Evolution Focus
{load_evolution_focus()}

## How To Use This
- Before answering: check if your approach matches a failure pattern
- After completing tasks: record outcome for cube tracking
- White spots = unclassified experiences → new dimensions emerging
- Query cube from any angle: time x domain x outcome
"""
    SKILL_FILE.write_text(content, encoding="utf-8")
    print(f"Updated: {SKILL_FILE} ({len(content)} chars)")

if __name__ == "__main__":
    main()

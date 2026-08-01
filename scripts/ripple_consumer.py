#!/usr/bin/env python3
"""
Ripple Consumer — event-driven report generator.
Called from event_beat() points in kc_rag.py, self_improvement_loop.py, etc.
Generates morning report when enough data accumulates, not on timer.
"""
import sys, os, json, sqlite3
from pathlib import Path
from datetime import datetime

ROOT = Path(os.environ.get("HERMES_HOME", "D:/Portable_Soft/hermes"))
sys.path[0:0] = [str(ROOT / "scripts")]

TRIGGER_FILE = ROOT / "cache" / "ripple_trigger.json"
THRESHOLD = 3  # knowledge_added events before regenerating

# ─── Trigger tracking ─────────────────────────────────────────────

def _load_trigger():
    if TRIGGER_FILE.exists():
        try:
            with open(TRIGGER_FILE) as f:
                return json.load(f)
        except Exception:
            pass
    return {"pending_count": 0, "last_generated": None, "pending_suggestions": False}


def _save_trigger(data):
    TRIGGER_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(TRIGGER_FILE, "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ─── Public API ───────────────────────────────────────────────────

def on_knowledge_added(count=1):
    """
    Called by kc_rag.py etc. after event_beat('knowledge_added').
    Accumulates count. When threshold reached → generates report.
    """
    data = _load_trigger()
    data["pending_count"] = data.get("pending_count", 0) + count
    
    if data["pending_count"] >= THRESHOLD:
        return _generate_report(data)
    else:
        _save_trigger(data)
        return {"generated": False, "reason": f"pending {data['pending_count']}/{THRESHOLD}"}


def on_suggestions_ready():
    """
    Called by self_improvement_loop.py after event_beat('new_suggestions_ready').
    Always generates report — suggestions are high-signal events.
    """
    data = _load_trigger()
    data["pending_suggestions"] = True
    return _generate_report(data)


def _generate_report(data):
    """Run morning_report.py and reset trigger."""
    import subprocess
    
    try:
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "morning_report.py")],
            capture_output=True, text=True, timeout=60, cwd=str(ROOT)
        )
        generated = result.returncode == 0
        output = result.stdout[-500:] if result.stdout else ""
        error = result.stderr[-500:] if result.stderr else ""
        
        # Beat heartbeat to keep system alive between events
        try:
            from chain_heartbeat import event_beat
            event_beat("new_suggestions_ready")
            event_beat("knowledge_added")
        except ImportError:
            pass
        
        # Convert morning report proposal → Goal Queue goal
        if generated:
            try:
                cache_path = ROOT / "cache" / "latest_morning_report.json"
                if cache_path.exists():
                    with open(cache_path, encoding="utf-8") as f:
                        cache = json.load(f)
                    if cache.get("top_proposal"):
                        from goal_queue import create_goal, get_active_goals
                        label = cache["top_proposal"]["label"]
                        maturity = cache["top_proposal"]["maturity"]
                        goal_id = create_goal(
                            title=f"Unlock: {label}",
                            tier=2,
                            priority=5,
                            description=f"Morning report top proposal: {label} (maturity={maturity:.0%})",
                            done_when=[
                                f"Explored {label} domain in Knowledge Cube",
                                f"Generated actionable report for {label}",
                                f"Presented findings to user",
                            ],
                        )
                        print(f"  🎯 Goal created: {goal_id} — Unlock: {label}")
            except Exception as e:
                print(f"  ⚠️ Goal creation failed: {e}")
    except subprocess.TimeoutExpired:
        generated = False
        output = ""
        error = "timeout"
    except Exception as e:
        generated = False
        output = ""
        error = str(e)

    # Reset trigger
    _save_trigger({
        "pending_count": 0,
        "last_generated": datetime.now().isoformat(),
        "pending_suggestions": False,
        "last_success": generated,
        "last_output_preview": output[:200],
    })
    
    return {"generated": generated, "error": error, "trigger_reset": True}


def get_status():
    """Return current trigger state and last cache age."""
    data = _load_trigger()
    cache_path = ROOT / "cache" / "latest_morning_report.json"
    cache_age = None
    if cache_path.exists():
        try:
            with open(cache_path) as f:
                c = json.load(f)
            cache_ts = datetime.fromisoformat(c["ts"])
            cache_age = (datetime.now() - cache_ts).total_seconds() / 60
        except Exception:
            pass
    data["cache_age_min"] = cache_age
    data["threshold"] = THRESHOLD
    return data


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        if sys.argv[1] == "on_knowledge_added":
            count = int(sys.argv[2]) if len(sys.argv) > 2 else 1
            print(json.dumps(on_knowledge_added(count), ensure_ascii=False))
        elif sys.argv[1] == "on_suggestions_ready":
            print(json.dumps(on_suggestions_ready(), ensure_ascii=False))
        elif sys.argv[1] == "status":
            print(json.dumps(get_status(), ensure_ascii=False, indent=2))
    else:
        print(json.dumps(get_status(), ensure_ascii=False, indent=2))

#!/usr/bin/env python3
"""
Workflow Executor — Native n8n replacement.
Executes goal_queue.json sequences: [step1, step2, step3]
Each step: trigger → check → action → log
Failure → corrective goal (self-healing)
Zero external deps. Pure Python + SQLite.
"""
import json
import sys
import os
import time
import subprocess
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional

HERMES_HOME = Path(__file__).resolve().parent.parent
CACHE = HERMES_HOME / "cache"
GOAL_QUEUE = CACHE / "goal_queue.json"
WORKFLOW_LOG = CACHE / "workflow.log"
WORKFLOW_STATE = CACHE / "workflow_state.json"

sys.path.insert(0, str(HERMES_HOME / "scripts"))

def _now():
    return datetime.now(timezone.utc).isoformat()

def _log(msg: str):
    CACHE.mkdir(parents=True, exist_ok=True)
    with open(WORKFLOW_LOG, "a", encoding="utf-8") as f:
        f.write(f"[{_now()}] {msg}\n")

def _load_state() -> dict:
    if WORKFLOW_STATE.exists():
        try:
            return json.loads(WORKFLOW_STATE.read_text(encoding="utf-8"))
        except:
            pass
    return {"executed": 0, "failed": 0, "last_run": None}

def _save_state(state: dict):
    CACHE.mkdir(parents=True, exist_ok=True)
    WORKFLOW_STATE.write_text(
        json.dumps(state, indent=2, ensure_ascii=False, default=str),
        encoding="utf-8"
    )

def _load_goals() -> dict:
    if GOAL_QUEUE.exists():
        try:
            return json.loads(GOAL_QUEUE.read_text(encoding="utf-8"))
        except:
            pass
    return {"goals": []}

# ═══ STEP EXECUTORS ═══
# Each step type has an executor. Add new ones here.

def exec_script(script_name: str, args: List[str] = None) -> Dict:
    """Run a Python script from scripts/"""
    script_path = HERMES_HOME / "scripts" / script_name
    if not script_path.exists():
        return {"ok": False, "error": f"Script not found: {script_path}"}
    
    cmd = [sys.executable, str(script_path)] + (args or [])
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300, cwd=HERMES_HOME)
        return {
            "ok": result.returncode == 0,
            "stdout": result.stdout[-2000:] if result.stdout else "",
            "stderr": result.stderr[-2000:] if result.stderr else "",
            "code": result.returncode
        }
    except subprocess.TimeoutExpired:
        return {"ok": False, "error": "Timeout (300s)"}
    except Exception as e:
        return {"ok": False, "error": str(e)}

def exec_terminal(command: str) -> Dict:
    """Run shell command"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=120, cwd=HERMES_HOME)
        return {
            "ok": result.returncode == 0,
            "stdout": result.stdout[-2000:] if result.stdout else "",
            "stderr": result.stderr[-2000:] if result.stderr else "",
            "code": result.returncode
        }
    except Exception as e:
        return {"ok": False, "error": str(e)}

def exec_kc_upsert(content: str, tags: str = "", source: str = "workflow", category: str = "action", importance: int = 5) -> Dict:
    """Upsert to Knowledge Cube"""
    try:
        from kc_rag import upsert
        eid = upsert(content, tags, source, category, importance)
        return {"ok": True, "entry_id": eid}
    except Exception as e:
        return {"ok": False, "error": str(e)}

def exec_kc_search(query: str, limit: int = 10) -> Dict:
    """Search Knowledge Cube"""
    try:
        from kc_rag import search
        results = search(query, limit)
        return {"ok": True, "results": results, "count": len(results)}
    except Exception as e:
        return {"ok": False, "error": str(e)}

def exec_goal_create(goal_data: Dict) -> Dict:
    """Create a new goal in goal_queue"""
    try:
        goals_data = _load_goals()
        goal_id = goal_data.get("id") or f"g-{int(time.time())}"
        goal = {
            "id": goal_id,
            "title": goal_data.get("title", "Untitled"),
            "tier": goal_data.get("tier", 3),
            "priority": goal_data.get("priority", 5),
            "created_at": _now(),
            "status": "active",
            "progress": 0.0,
            "related_actions": goal_data.get("related_actions", []),
            "deadline": goal_data.get("deadline"),
            "description": goal_data.get("description", ""),
            "done_when": goal_data.get("done_when", []),
        }
        goals_data["goals"].append(goal)
        GOAL_QUEUE.write_text(json.dumps(goals_data, indent=2, ensure_ascii=False), encoding="utf-8")
        return {"ok": True, "goal_id": goal_id}
    except Exception as e:
        return {"ok": False, "error": str(e)}

def exec_goal_update(goal_id: str, updates: Dict) -> Dict:
    """Update goal progress/status"""
    try:
        goals_data = _load_goals()
        for goal in goals_data["goals"]:
            if goal["id"] == goal_id:
                goal.update(updates)
                goal["updated_at"] = _now()
                GOAL_QUEUE.write_text(json.dumps(goals_data, indent=2, ensure_ascii=False), encoding="utf-8")
                return {"ok": True}
        return {"ok": False, "error": f"Goal not found: {goal_id}"}
    except Exception as e:
        return {"ok": False, "error": str(e)}

def exec_wait(seconds: int) -> Dict:
    """Wait N seconds"""
    time.sleep(seconds)
    return {"ok": True, "waited": seconds}

# Registry of step executors
EXECUTORS = {
    "script": exec_script,
    "terminal": exec_terminal,
    "kc_upsert": exec_kc_upsert,
    "kc_search": exec_kc_search,
    "goal_create": exec_goal_create,
    "goal_update": exec_goal_update,
    "wait": exec_wait,
}

def execute_step(step: Dict) -> Dict:
    """Execute a single workflow step"""
    step_type = step.get("type", "script")
    executor = EXECUTORS.get(step_type)
    
    if not executor:
        return {"ok": False, "error": f"Unknown step type: {step_type}"}
    
    # Remove internal keys, pass rest as kwargs
    internal_keys = {"type", "name", "continue_on_error"}
    kwargs = {k: v for k, v in step.items() if k not in internal_keys}
    return executor(**kwargs)

def execute_workflow(workflow: Dict) -> Dict:
    """Execute a full workflow (sequence of steps)"""
    workflow_id = workflow.get("id", f"wf-{int(time.time())}")
    steps = workflow.get("steps", [])
    name = workflow.get("name", "Unnamed Workflow")
    
    _log(f"WORKFLOW START: {name} ({workflow_id}) — {len(steps)} steps")
    
    results = []
    state = _load_state()
    
    for i, step in enumerate(steps):
        step_name = step.get("name", f"step_{i+1}")
        _log(f"  Step {i+1}/{len(steps)}: {step_name} ({step.get('type', 'script')})")
        
        result = execute_step(step)
        results.append({
            "step": i + 1,
            "name": step_name,
            "type": step.get("type", "script"),
            "result": result
        })
        
        if result.get("ok"):
            _log(f"    ✅ OK")
            state["executed"] += 1
        else:
            _log(f"    ❌ FAILED: {result.get('error', 'unknown')}")
            state["failed"] += 1
            
            # SELF-HEALING: Create corrective goal
            corrective = {
                "id": f"corrective-{workflow_id}-{i+1}",
                "title": f"Fix: {name} step {i+1} ({step_name})",
                "tier": 1,
                "priority": 10,
                "created_at": _now(),
                "status": "active",
                "progress": 0.0,
                "related_actions": ["workflow-fix"],
                "deadline": None,
                "description": f"Workflow '{name}' step {i+1} ({step_name}) failed: {result.get('error', 'unknown')}. Original step: {json.dumps(step, ensure_ascii=False)}",
                "done_when": [f"Step {i+1} executes successfully", "Workflow completes without errors"],
            }
            goals_data = _load_goals()
            goals_data["goals"].append(corrective)
            GOAL_QUEUE.write_text(json.dumps(goals_data, indent=2, ensure_ascii=False), encoding="utf-8")
            _log(f"    🔧 Corrective goal created: {corrective['id']}")
            
            # Stop on failure unless continue_on_error
            if not step.get("continue_on_error", False):
                break
    
    state["last_run"] = _now()
    _save_state(state)
    
    success = all(r["result"].get("ok") for r in results)
    _log(f"WORKFLOW {'SUCCESS' if success else 'FAILED'}: {name} ({workflow_id})")
    
    return {
        "workflow_id": workflow_id,
        "name": name,
        "success": success,
        "steps_executed": len(results),
        "steps_total": len(steps),
        "results": results
    }

def run_pending_workflows():
    """Run all active workflows from goal_queue"""
    goals_data = _load_goals()
    workflows = []
    
    for goal in goals_data.get("goals", []):
        if goal.get("status") == "active" and "workflow" in goal.get("related_actions", []):
            # Extract workflow from goal
            wf = goal.get("workflow")
            if wf:
                workflows.append(wf)
    
    if not workflows:
        return {"executed": 0, "message": "No active workflows found"}
    
    results = []
    for wf in workflows:
        results.append(execute_workflow(wf))
    
    return {"executed": len(results), "results": results}

# Built-in workflows (can be extended via goal_queue)
BUILTIN_WORKFLOWS = {
    "daily_maintenance": {
        "id": "wf-daily-maintenance",
        "name": "Daily Maintenance",
        "steps": [
            {"name": "check_cron_health", "type": "script", "script_name": "autonomous_agent.py", "args": ["--check-cron"]},
            {"name": "run_kc_populator", "type": "script", "script_name": "kc_populator.py"},
            {"name": "run_procedural", "type": "script", "script_name": "procedural_executor.py"},
            {"name": "self_system_status", "type": "script", "script_name": "self_system.py", "args": ["--status"]},
        ]
    },
    "revenue_test_cycle": {
        "id": "wf-revenue-test",
        "name": "Revenue Test Cycle",
        "steps": [
            {"name": "check_salon_bot", "type": "script", "script_name": "salon_bot.py", "args": ["--health"]},
            {"name": "post_cpa_offer", "type": "script", "script_name": "auto_poster.py", "args": ["--cpa"]},
            {"name": "check_conversions", "type": "terminal", "command": "grep -c 'conversion' D:/Portable_Soft/hermes/logs/*.log 2>/dev/null || echo 0"},
        ]
    },
    "research_to_kc": {
        "id": "wf-research-to-kc",
        "name": "Research → Knowledge Cube",
        "steps": [
            {"name": "search_web", "type": "script", "script_name": "web_search.py", "args": ["--topic", "AI agents"]},
            {"name": "extract_content", "type": "script", "script_name": "web_extract.py", "args": ["--urls", "from_search"]},
            {"name": "upsert_findings", "type": "kc_upsert", "content": "AI agents research findings", "tags": "research,agents", "category": "research"},
        ]
    },
}

def list_workflows():
    """List available workflows"""
    print("Built-in workflows:")
    for k, v in BUILTIN_WORKFLOWS.items():
        print(f"  {k}: {v['name']} ({len(v['steps'])} steps)")
    
    print("\nActive goal-based workflows:")
    goals_data = _load_goals()
    for goal in goals_data.get("goals", []):
        if goal.get("status") == "active" and "workflow" in goal.get("related_actions", []):
            print(f"  {goal['id']}: {goal['title']}")

def main():
    if len(sys.argv) < 2:
        print("Usage: workflow_executor.py run|list|builtin <name>|goal <goal_id>")
        return
    
    cmd = sys.argv[1]
    
    if cmd == "list":
        list_workflows()
    
    elif cmd == "builtin":
        if len(sys.argv) < 3:
            print("Usage: workflow_executor.py builtin <workflow_name>")
            return
        name = sys.argv[2]
        if name in BUILTIN_WORKFLOWS:
            result = execute_workflow(BUILTIN_WORKFLOWS[name])
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print(f"Unknown workflow: {name}")
    
    elif cmd == "goal":
        if len(sys.argv) < 3:
            print("Usage: workflow_executor.py goal <goal_id>")
            return
        goal_id = sys.argv[2]
        goals_data = _load_goals()
        for goal in goals_data.get("goals", []):
            if goal["id"] == goal_id and "workflow" in goal.get("related_actions", []):
                result = execute_workflow(goal.get("workflow", {}))
                print(json.dumps(result, indent=2, ensure_ascii=False))
                return
        print(f"Goal not found or no workflow: {goal_id}")
    
    elif cmd == "run":
        result = run_pending_workflows()
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    else:
        print(f"Unknown command: {cmd}")

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Orchestrator — tool chain runner.

Concept: chains of tools. Each tool produces output, next tool consumes it.
Decision points: continue / stop / redirect.

Chain = list of steps. Each step:
  - tool: function to call
  - input_from: where to get input (previous step output, or external)
  - decision: how to handle result (continue_if, stop_if, redirect_if)

Usage:
  python scripts/orchestrator.py                    # run default chain
  python scripts/orchestrator.py --chain boot       # specific chain
  python scripts/orchestrator.py --list             # list available chains
"""

import json
import sys
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Any, Callable, Optional

HERMES_HOME = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = HERMES_HOME / "scripts"
CACHE_DIR = HERMES_HOME / "cache"
LOGS_DIR = HERMES_HOME / "logs"

sys.path.insert(0, str(SCRIPTS_DIR))


# ─── Tool Registry ───
# Each tool is a function: (input_data) -> (success: bool, output: dict)
# Tools are simple: take input, return result.

def tool_reality_gate(input_data: dict = None) -> tuple[bool, dict]:
    """Run reality gate, return honest system state."""
    try:
        r = subprocess.run(
            [sys.executable, str(SCRIPTS_DIR / "reality_gate.py"), "--json"],
            capture_output=True, text=True, timeout=30,
            cwd=str(HERMES_HOME), encoding="utf-8", errors="replace"
        )
        output = r.stdout
        start = output.find("{")
        end = output.rfind("}")
        if start >= 0 and end > start:
            data = json.loads(output[start:end + 1])
            return True, data
        return False, {"error": "no JSON in reality_gate output", "raw": output[:300]}
    except Exception as e:
        return False, {"error": str(e)}


def tool_session_boot(input_data: dict = None) -> tuple[bool, dict]:
    """Run session boot, return boot results."""
    try:
        r = subprocess.run(
            [sys.executable, str(SCRIPTS_DIR / "session_boot.py")],
            capture_output=True, text=True, timeout=60,
            cwd=str(HERMES_HOME), encoding="utf-8", errors="replace"
        )
        return r.returncode == 0, {"output": r.stdout[-500:], "exit_code": r.returncode}
    except Exception as e:
        return False, {"error": str(e)}


def tool_goal_evaluator(input_data: dict = None) -> tuple[bool, dict]:
    """Run goal evaluator, return goal state."""
    try:
        r = subprocess.run(
            [sys.executable, str(SCRIPTS_DIR / "goal_evaluator.py")],
            capture_output=True, text=True, timeout=30,
            cwd=str(HERMES_HOME), encoding="utf-8", errors="replace"
        )
        return r.returncode == 0, {"output": r.stdout[-500:], "exit_code": r.returncode}
    except Exception as e:
        return False, {"error": str(e)}


def tool_load_goals(input_data: dict = None) -> tuple[bool, dict]:
    """Load current goals from queue."""
    goal_file = CACHE_DIR / "goal_queue.json"
    if not goal_file.exists():
        return True, {"goals": [], "count": 0}
    try:
        data = json.loads(goal_file.read_text(encoding="utf-8"))
        goals = data.get("goals", [])
        active = [g for g in goals if g.get("status") == "active"]
        return True, {
            "goals": active,
            "count": len(active),
            "total": len(goals),
            "by_priority": sorted(active, key=lambda g: -g.get("priority", 0))[:5]
        }
    except Exception as e:
        return False, {"error": str(e)}


def tool_close_goals(input_data: dict = None) -> tuple[bool, dict]:
    """Close all boot-generated goals, keep only user-created ones."""
    goal_file = CACHE_DIR / "goal_queue.json"
    if not goal_file.exists():
        return True, {"closed": 0, "reason": "no goals file"}
    try:
        data = json.loads(goal_file.read_text(encoding="utf-8"))
        goals = data.get("goals", [])
        closed = 0
        kept = []
        for g in goals:
            title = g.get("title", "").lower()
            # Keep goals that are clearly user-created or high-value
            is_boot_generated = any(phrase in title for phrase in [
                "fill knowledge gaps",
                "generate daily value",
                "session boot mandatory",
                "agent must work autonomously",
                "collect and act on user real-world needs",
                "investigate:",
                "address need:",
                "address user need:",
            ])
            if g.get("status") == "active" and is_boot_generated:
                g["status"] = "closed"
                g["closed_reason"] = "boot-generated noise"
                g["closed_at"] = datetime.now().isoformat()
                closed += 1
            kept.append(g)

        data["goals"] = kept
        data["updated_at"] = datetime.now().isoformat()
        goal_file.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        return True, {"closed": closed, "remaining": len([g for g in kept if g.get("status") == "active"])}
    except Exception as e:
        return False, {"error": str(e)}


def tool_fix_goal_executor(input_data: dict = None) -> tuple[bool, dict]:
    """Patch goal_queue.py: done_when checks should verify functionality, not file existence."""
    gq_path = SCRIPTS_DIR / "goal_queue.py"
    if not gq_path.exists():
        return False, {"error": "goal_queue.py not found"}

    content = gq_path.read_text(encoding="utf-8")

    # Find the evaluate_goals function and check what it does with done_when
    if "file.exists()" in content and "done_when" in content:
        # The goal evaluator checks file existence for done_when criteria
        # We need to add a reality gate check
        return True, {
            "status": "identified",
            "issue": "goal_queue.py uses file.exists() for done_when criteria",
            "fix_needed": "Add reality gate verification to done_when checks"
        }
    return True, {"status": "ok", "issue": "none_found"}


def tool_update_decision_log(input_data: dict = None) -> tuple[bool, dict]:
    """Update DECISION_LOG.md with last 20 actions from action_log.jsonl."""
    log_file = CACHE_DIR / "action_log.jsonl"
    out_file = HERMES_HOME / "DECISION_LOG.md"

    if not log_file.exists():
        return True, {"updated": False, "reason": "no action_log.jsonl"}

    try:
        lines = log_file.read_text(encoding="utf-8").strip().split("\n")
        entries = []
        for line in lines[-20:]:
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError:
                pass

        md = "DECISION_LOG.md\n\n"
        md += f"Last {len(entries)} actions from action_log.jsonl:\n\n"
        for e in entries:
            ts = e.get("timestamp", "?")
            action = e.get("action", "?")
            score = e.get("score", "?")
            status = e.get("status", "?")
            result = str(e.get("result", "?"))[:200]
            md += f"### {ts}\n"
            md += f"- **Action:** {action}\n"
            md += f"- **Score:** {score}\n"
            md += f"- **Status:** {status}\n"
            md += f"- **Result:** {result}\n\n"

        out_file.write_text(md, encoding="utf-8")
        return True, {"updated": True, "entries": len(entries)}
    except Exception as e:
        return False, {"error": str(e)}


def tool_record_outcome(input_data: dict = None) -> tuple[bool, dict]:
    """Record chain execution outcome to action_log.jsonl."""
    if input_data is None:
        return False, {"error": "no input_data"}

    log_file = CACHE_DIR / "action_log.jsonl"
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    entry = {
        "timestamp": datetime.now().isoformat(),
        "action": input_data.get("action", "orchestrator_chain"),
        "score": input_data.get("score", 0),
        "status": input_data.get("status", "unknown"),
        "result": input_data.get("result", ""),
        "chain": input_data.get("chain", []),
    }

    try:
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        return True, {"recorded": True}
    except Exception as e:
        return False, {"error": str(e)}


# ─── Tool Registry ───

TOOLS = {
    "reality_gate": tool_reality_gate,
    "session_boot": tool_session_boot,
    "goal_evaluator": tool_goal_evaluator,
    "load_goals": tool_load_goals,
    "close_goals": tool_close_goals,
    "fix_goal_executor": tool_fix_goal_executor,
    "update_decision_log": tool_update_decision_log,
    "record_outcome": tool_record_outcome,
}


# ─── Chain Definitions ───
# Each chain is a list of steps. Steps run sequentially.
# Each step: {tool, input_from, decision}
#   input_from: "previous" = output of last step, None = no input
#   decision: {type: "continue"|"stop"|"redirect", condition: ...}

CHAINS = {
    "boot_diagnose_fix": {
        "description": "Boot → Reality Check → Fix what's broken",
        "steps": [
            {"tool": "session_boot", "name": "boot"},
            {"tool": "reality_gate", "name": "diagnose"},
            {"tool": "update_decision_log", "name": "update_log",
             "input_from": "previous"},
            {"tool": "load_goals", "name": "check_goals"},
            {"tool": "close_goals", "name": "clean_goals",
             "decision": {"type": "continue_if", "field": "count", "op": ">", "value": 10}},
        ],
    },
    "goal_cycle": {
        "description": "Load goals → Evaluate → Execute top priority → Verify",
        "steps": [
            {"tool": "load_goals", "name": "load"},
            {"tool": "goal_evaluator", "name": "evaluate"},
            {"tool": "reality_gate", "name": "verify"},
            {"tool": "record_outcome", "name": "record",
             "input_from": "chain_result"},
        ],
    },
    "diagnose_only": {
        "description": "Reality check + goal audit, no actions",
        "steps": [
            {"tool": "reality_gate", "name": "diagnose"},
            {"tool": "load_goals", "name": "goals"},
        ],
    },
    "fix_system": {
        "description": "Diagnose → Fix decision log → Clean goals → Verify",
        "steps": [
            {"tool": "reality_gate", "name": "diagnose"},
            {"tool": "update_decision_log", "name": "fix_log"},
            {"tool": "close_goals", "name": "clean_goals"},
            {"tool": "reality_gate", "name": "verify"},
        ],
    },
}


# ─── Chain Runner ───

def run_chain(chain_name: str, verbose: bool = True) -> dict:
    """Run a chain of tools. Returns final state."""
    if chain_name not in CHAINS:
        return {"error": f"unknown chain: {chain_name}", "available": list(CHAINS.keys())}

    chain = CHAINS[chain_name]
    steps = chain["steps"]
    state = {}  # accumulates results
    results = []  # step results for reporting

    if verbose:
        print(f"\n{'='*60}")
        print(f"CHAIN: {chain_name}")
        print(f"DESCRIPTION: {chain['description']}")
        print(f"STEPS: {len(steps)}")
        print(f"{'='*60}")

    for i, step in enumerate(steps):
        tool_name = step["tool"]
        step_name = step.get("name", tool_name)

        if tool_name not in TOOLS:
            results.append({"step": step_name, "status": "error", "detail": f"tool not found: {tool_name}"})
            continue

        # Get input
        input_data = None
        input_from = step.get("input_from")
        if input_from == "previous" and results:
            input_data = results[-1].get("output")
        elif input_from == "chain_result":
            input_data = {"chain": [r["step"] for r in results], "results": results}

        # Check decision gate (skip step if condition not met)
        decision = step.get("decision")
        if decision and decision.get("type") == "continue_if":
            field = decision.get("field")
            op = decision.get("op")
            value = decision.get("value")
            # Check against last result
            if results:
                last_output = results[-1].get("output", {})
                actual = last_output.get(field)
                if actual is not None:
                    skip = False
                    if op == ">" and not (actual > value):
                        skip = True
                    elif op == "<" and not (actual < value):
                        skip = True
                    elif op == "==" and not (actual == value):
                        skip = True
                    if skip:
                        results.append({"step": step_name, "status": "skipped", "detail": f"condition not met: {field} {op} {value}"})
                        continue

        # Execute tool
        if verbose:
            print(f"\n[{i+1}/{len(steps)}] Running: {step_name} ({tool_name})")

        try:
            start = datetime.now()
            success, output = TOOLS[tool_name](input_data)
            elapsed = (datetime.now() - start).total_seconds()

            result = {
                "step": step_name,
                "tool": tool_name,
                "success": success,
                "output": output,
                "elapsed_s": round(elapsed, 2),
                "status": "ok" if success else "failed",
            }
            results.append(result)

            if verbose:
                status_icon = "✓" if success else "✗"
                detail = str(output)[:200] if output else ""
                print(f"  {status_icon} {step_name}: {detail}")

            # Stop chain on failure if decision says so
            if decision and decision.get("type") == "stop_if" and not success:
                if verbose:
                    print(f"  ⛔ Chain stopped at {step_name}")
                break

        except Exception as e:
            results.append({"step": step_name, "status": "error", "detail": str(e)})
            if verbose:
                print(f"  ✗ {step_name}: ERROR — {e}")

    # Final state
    state = {
        "chain": chain_name,
        "steps_run": len(results),
        "steps_ok": sum(1 for r in results if r.get("success")),
        "steps_failed": sum(1 for r in results if r.get("status") == "failed"),
        "steps_skipped": sum(1 for r in results if r.get("status") == "skipped"),
        "results": results,
        "timestamp": datetime.now().isoformat(),
    }

    if verbose:
        print(f"\n{'='*60}")
        print(f"CHAIN COMPLETE: {state['steps_ok']}/{state['steps_run']} OK, {state['steps_failed']} failed, {state['steps_skipped']} skipped")
        print(f"{'='*60}\n")

    return state


# ─── Main ───

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Orchestrator — tool chain runner")
    parser.add_argument("--chain", default="boot_diagnose_fix", help="Chain to run")
    parser.add_argument("--list", action="store_true", help="List available chains")
    parser.add_argument("--quiet", action="store_true", help="Minimal output")
    args = parser.parse_args()

    if args.list:
        print("Available chains:")
        for name, chain in CHAINS.items():
            print(f"  {name}: {chain['description']}")
            for i, step in enumerate(chain['steps']):
                print(f"    {i+1}. {step['tool']} ({step.get('name', '')})")
        return

    result = run_chain(args.chain, verbose=not args.quiet)

    # Save result
    out_file = CACHE_DIR / "last_chain_result.json"
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    out_file.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")

    if args.quiet:
        print(json.dumps({
            "chain": result["chain"],
            "ok": result["steps_ok"],
            "failed": result["steps_failed"],
            "skipped": result["steps_skipped"],
        }))


if __name__ == "__main__":
    main()

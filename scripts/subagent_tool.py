#!/usr/bin/env python3
"""
Subagent Tool — Fixed version with FULL context passing.
Implements DIRECTIVE 0x14: PRINCIPAL_OBLIGATION
"""

import os
import subprocess
import json
from pathlib import Path
from typing import Dict, Any, Optional, List

HERMES_HOME = Path(os.environ.get("HERMES_HOME", "D:/Portable_Soft/hermes"))

# Complete environment for ALL subagents
SUBAGENT_ENV_BASE = {
    "HERMES_HOME": str(HERMES_HOME),
    "ALL_PROXY": "socks5://127.0.0.1:10806",
    "HTTPS_PROXY": "socks5://127.0.0.1:10806",
    "HTTP_PROXY": "socks5://127.0.0.1:10806",
    "PYTHONPATH": f"{HERMES_HOME}/scripts;" + os.environ.get("PYTHONPATH", ""),
    "PATH": f"{HERMES_HOME / 'hermes-agent' / '.venv' / 'Scripts'};" + os.environ.get("PATH", ""),
}

# Handoff context store
HANDOFF_STORE = HERMES_HOME / "cache" / "handoffs"
HANDOFF_STORE.mkdir(parents=True, exist_ok=True)


def get_full_subagent_env(extra: Dict = None) -> Dict[str, str]:
    """Get complete environment for subagent execution. DIRECTIVE 0x14."""
    env = os.environ.copy()
    env.update(SUBAGENT_ENV_BASE)
    if extra:
        env.update(extra)
    return env


def run_subagent(
    goal: str,
    context: str = "",
    timeout: int = 300,
    model: Optional[str] = None,
    handoff_from: Optional[str] = None,
    handoff_data: Optional[Dict] = None
) -> Dict[str, Any]:
    """
    Run subagent with FULL Hermes context + handoff support.
    
    Implements:
    - DIRECTIVE 0x14: PRINCIPAL_OBLIGATION (full context)
    - Handoff patterns: context passing between agents
    """
    # Build full context
    full_context = context
    if handoff_from:
        full_context = f"HANDOFF FROM: {handoff_from}\nHANDOFF DATA: {json.dumps(handoff_data)}\n\n{context}"
    
    # Prepare command
    cmd = ["python", "-m", "hermes_cli", "delegate", "--goal", goal, "--context", full_context]
    if model:
        cmd.extend(["--model", model])
    
    # Full environment
    env = get_full_subagent_env({
        "HERMES_GOAL": goal,
        "HERMES_CONTEXT": full_context,
        "HERMES_HANDOFF_FROM": handoff_from or "",
    })
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=str(HERMES_HOME),
            env=env
        )
        
        response = {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode
        }
        
        # Store handoff result for next agent
        if response["success"]:
            handoff_id = f"handoff_{goal[:20]}_{os.getpid()}"
            handoff_file = HANDOFF_STORE / f"{handoff_id}.json"
            handoff_file.write_text(json.dumps({
                "goal": goal,
                "result": response,
                "timestamp": str(__import__('datetime').datetime.now()),
            }))
            response["handoff_id"] = handoff_id
        
        return response
        
    except subprocess.TimeoutExpired:
        return {"success": False, "error": f"Timeout after {timeout}s"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def handoff_task(
    from_agent: str,
    to_goal: str,
    context: str,
    data: Dict,
    timeout: int = 300
) -> Dict[str, Any]:
    """
    Handoff pattern: Agent A passes task to Agent B with full context.
    
    Pattern from Claude Code: "When an agent completes its subtask,
    it hands off to another agent with all relevant context preserved."
    """
    handoff_id = f"handoff_{from_agent}_{__import__('time').time()}"
    
    # Save handoff data
    handoff_file = HANDOFF_STORE / f"{handoff_id}.json"
    handoff_file.write_text(json.dumps({
        "from": from_agent,
        "to_goal": to_goal,
        "context": context,
        "data": data,
        "timestamp": str(__import__('datetime').datetime.now()),
    }))
    
    # Run next agent with handoff
    return run_subagent(
        goal=to_goal,
        context=context,
        timeout=timeout,
        handoff_from=from_agent,
        handoff_data=data
    )


def load_handoff(handoff_id: str) -> Optional[Dict]:
    """Load handoff data for next agent."""
    handoff_file = HANDOFF_STORE / f"{handoff_id}.json"
    if handoff_file.exists():
        return json.loads(handoff_file.read_text())
    return None


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python subagent_tool.py <goal> [context]")
        sys.exit(1)
    goal = sys.argv[1]
    context = sys.argv[2] if len(sys.argv) > 2 else ""
    result = run_subagent(goal, context)
    print(json.dumps(result, ensure_ascii=False, indent=2))
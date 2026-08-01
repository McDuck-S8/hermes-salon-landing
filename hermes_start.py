#!/usr/bin/env python3
"""Hermes bootstrap — runs at session start via terminal tool."""
import sys
import os

HERMES_HOME = r"D:\Portable_Soft\hermes"
sys.path.insert(0, os.path.join(HERMES_HOME, "scripts"))

def boot():
    results = []
    
    # 1. Session boot
    try:
        from session_boot import boot as session_boot
        r = session_boot()
        results.append(f"session_boot: OK ({len(r.get('dumps', []))} dumps, {len(r.get('errors', []))} errors)")
    except Exception as e:
        results.append(f"session_boot: FAILED — {e}")
    
    # 2. Load context
    try:
        from session_context import build_context
        ctx = build_context()
        if isinstance(ctx, dict):
            results.append(f"session_context: OK (keys: {list(ctx.keys())[:5]})")
        else:
            results.append(f"session_context: OK ({len(ctx)} chars, type=str)")
    except Exception as e:
        results.append(f"session_context: FAILED — {e}")
    
    # 3. Check goals
    try:
        from goal_queue import get_active_goals
        goals = get_active_goals()
        results.append(f"goals: {len(goals)} active")
    except Exception as e:
        results.append(f"goals: FAILED — {e}")
    
    # 4. Check tool catalog
    tool_catalog = os.path.join(HERMES_HOME, "skills", "tool-catalog", "SKILL.md")
    if os.path.exists(tool_catalog):
        results.append("tool_catalog: EXISTS")
    else:
        results.append("tool_catalog: MISSING")

    # 5. Autonomous First Action
    try:
        from goal_queue import get_active_goals, create_goal
        active = get_active_goals()
        if active:
            goal = active[0]  # highest priority, sorted desc
            if goal.get('status') == 'active':
                # Try to execute via goal_executor
                try:
                    from goal_executor import execute_goal
                    result = execute_goal(goal)
                    if isinstance(result, bool):
                        status = "SUCCESS" if result else "FAILED"
                    elif isinstance(result, dict):
                        status = result.get('status', str(result)[:80])
                    else:
                        status = str(result)[:80]
                    results.append(f"autonomous_action: EXECUTED goal {goal.get('id')} — {status}")
                except ImportError:
                    results.append(f"autonomous_action: EXECUTOR_MISSING goal {goal.get('id')} — {goal.get('title', '')[:60]}")
                except Exception as e:
                    results.append(f"autonomous_action: FAILED goal {goal.get('id')} — {e}")
            else:
                results.append(f"autonomous_action: SKIP — top goal {goal.get('id')} status={goal.get('status')}")
        else:
            # No active goals — create corrective goal
            new_id = create_goal("system_health_check", tier=1, priority=10,
                                 description="Auto-created corrective goal: no active goals found at boot")
            results.append(f"autonomous_action: CREATED corrective goal {new_id}")
    except Exception as e:
        results.append(f"autonomous_action: FAILED — {e}")

    return results

if __name__ == "__main__":
    print("=== HERMES BOOT ===")
    for line in boot():
        print(f"  {line}")
    print("=== BOOT DONE ===")

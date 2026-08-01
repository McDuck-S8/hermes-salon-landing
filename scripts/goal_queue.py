#!/usr/bin/env python3
"""
Goal Queue — autonomous goal management for the agent.


> Revisit: when goal queue structure, status transitions, or priority logic changes. Last touched: 2026-07-03.
The agent creates goals based on system state, tracks progress,
and converts goals into action candidates for autonomous_agent.

Usage:
    from goal_queue import get_active_goals, goal_to_action, evaluate_goals
    goals = get_active_goals()
    candidates = [goal_to_action(g) for g in goals]
"""
import json
import sys
from pathlib import Path
from datetime import datetime

HERMES_HOME = Path(__file__).resolve().parent.parent
CACHE_DIR = HERMES_HOME / "cache"
GOAL_QUEUE_FILE = CACHE_DIR / "goal_queue.json"
GOAL_ARCHIVE_FILE = CACHE_DIR / "goal_archive.json"

# Goal tiers (same as autonomous_agent)
TIER_SURVIVE = 1
TIER_LEARN = 2
TIER_PRODUCE = 3

# Event bus integration
sys.path.insert(0, str(HERMES_HOME / "scripts"))
try:
    from event_bus import emit
    _EVENT_BUS_ENABLED = True
except ImportError:
    _EVENT_BUS_ENABLED = False
    def emit(event_type: str, payload: dict = None):
        pass


def _load_goals() -> list:
    if GOAL_QUEUE_FILE.exists():
        try:
            data = json.loads(GOAL_QUEUE_FILE.read_text(encoding="utf-8"))
            return data.get("goals", [])
        except (json.JSONDecodeError, OSError):
            return []
    return []


def _save_goals(goals: list):
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    GOAL_QUEUE_FILE.write_text(
        json.dumps({"goals": goals, "updated_at": datetime.now().isoformat()},
                    indent=2, ensure_ascii=False),
        encoding="utf-8"
    )


def _next_goal_id(goals: list) -> str:
    existing_ids = {g.get("id", "") for g in goals}
    i = 1
    while f"g-{i:03d}" in existing_ids:
        i += 1
    return f"g-{i:03d}"


def create_goal(title: str, tier: int, priority: int,
                related_actions: list[str] = None,
                description: str = "",
                deadline: str = None,
                done_when: list[str] = None) -> str:
    """Create a new goal. Returns goal_id.
    
    done_when: list of concrete, verifiable conditions.
    Goal is "completed" ONLY when ALL conditions in done_when are True.
    Example: done_when=["bot responds to /start", "database file exists"]
    """
    goals = _load_goals()

    # Deduplicate: don't create if similar goal exists
    for g in goals:
        if g.get("status") == "active" and g.get("title", "").lower() == title.lower():
            return g.get("id", "")

    goal_id = _next_goal_id(goals)
    goal = {
        "id": goal_id,
        "title": title,
        "tier": tier,
        "priority": priority,
        "created_at": datetime.now().isoformat(),
        "status": "active",
        "progress": 0.0,
        "related_actions": related_actions or [],
        "deadline": deadline,
        "description": description,
        "done_when": done_when or [],
    }
    goals.append(goal)
    _save_goals(goals)
    
    # Emit goal_created event for event-driven execution
    emit("goal_created", {"goal_id": goal_id, "title": title, "tier": tier, "priority": priority})
    
    return goal_id


def update_goal(goal_id: str, progress: float = None, status: str = None):
    """Update goal progress or status."""
    goals = _load_goals()
    for g in goals:
        if g.get("id") == goal_id:
            if progress is not None:
                g["progress"] = min(1.0, max(0.0, progress))
            if status is not None:
                g["status"] = status
            g["updated_at"] = datetime.now().isoformat()
            break
    _save_goals(goals)


def update_goal_progress(action_id: str, result: str):
    """Auto-update related goals based on action result.
    
    CRITICAL RULE (2026-06-22): Progress += 0.1 ONLY if action has
    a VERIFIABLE outcome marker in the result string. Mere absence
    of "EXECUTION ERROR" is NOT progress — that's activity, not outcome.
    
    Verified outcome markers: [VERIFIED], [OUTCOME], [REAL], [PERSISTED]
    """
    goals = _load_goals()
    updated = False
    
    # Check for verified outcome markers (not just absence of error)
    has_outcome = any(marker in result for marker in [
        "[VERIFIED]", "[OUTCOME]", "[REAL]", "[PERSISTED]", 
        "[CONFIRMED]", "[LIVE]", "[RUNNING]", "[HEALTHY]"
    ])
    
    for g in goals:
        if g.get("status") != "active":
            continue
        related = g.get("related_actions", [])
        if action_id in related:
            if has_outcome:
                # Verified outcome: real progress
                g["progress"] = min(1.0, g.get("progress", 0) + 0.1)
                g["updated_at"] = datetime.now().isoformat()
                g.setdefault("history", []).append({
                    "ts": datetime.now().isoformat(),
                    "action": action_id,
                    "result": result[:200],
                    "verified": True,
                    "progress": g["progress"]
                })
                updated = True
                # Auto-complete only if progress reaches 1.0 AND verified
                if g["progress"] >= 1.0:
                    g["status"] = "completed"
                    g["completed_at"] = datetime.now().isoformat()
                    g["completed_reason"] = "All outcomes verified"
            else:
                # Activity only: record it but don't bump progress
                g.setdefault("history", []).append({
                    "ts": datetime.now().isoformat(),
                    "action": action_id,
                    "result": result[:200],
                    "verified": False,
                    "note": "No outcome marker — progress NOT bumped"
                })
                updated = True
    if updated:
        _save_goals(goals)


def check_completion(goal_id: str, state: dict = None) -> dict:
    """Check if a goal's done_when conditions are met.
    
    Returns: {"met": bool, "conditions": [{"text": str, "met": bool}, ...]}
    
    Condition types (auto-detected from text):
    - "file exists: path" → checks file exists
    - "process running: name" → checks process
    - "count below N" → checks against state
    - "bot responds to X" → checks bot is running
    - Other → logged as "needs manual verification"
    """
    goals = _load_goals()
    goal = next((g for g in goals if g.get("id") == goal_id), None)
    if not goal:
        return {"met": False, "conditions": [], "error": "Goal not found"}
    
    done_when = goal.get("done_when", [])
    if not done_when:
        return {"met": False, "conditions": [], "error": "No done_when criteria defined"}
    
    results = []
    for condition in done_when:
        cond = {"text": condition, "met": False, "type": "unknown"}
        cond_lower = condition.lower()
        
        # Auto-detect condition type and evaluate
        if "file exists" in cond_lower:
            import re
            match = re.search(r"file exists[:\s]+(\S+)", cond_lower)
            if match:
                fpath = Path(match.group(1))
                cond["met"] = fpath.exists()
                cond["type"] = "file_check"
        
        elif "process running" in cond_lower:
            import subprocess
            try:
                result = subprocess.run(
                    ["tasklist"], capture_output=True, text=True, timeout=5
                )
                # Simple check — would need more sophisticated detection
                cond["type"] = "process_check"
                cond["met"] = False  # Needs specific process name
                cond["note"] = "Needs manual process name"
            except:
                pass
        
        elif "white_spots" in cond_lower or "white spots" in cond_lower:
            import re
            match = re.search(r"below\s+(\d+)", cond_lower)
            if match and state:
                current = state.get("knowledge_cube", {}).get("white_spots", 999)
                threshold = int(match.group(1))
                cond["met"] = current < threshold
                cond["type"] = "threshold"
                cond["current"] = current
                cond["threshold"] = threshold
        
        elif "reality_gate" in cond_lower and "all_clear" in cond_lower:
            if state and "reality_gate" in state:
                verdict = state["reality_gate"].get("verdict", "")
                cond["met"] = verdict == "ALL_CLEAR"
                cond["type"] = "reality_gate"
                cond["verdict"] = verdict
        
        elif "reality_gate" in cond_lower and "healthy" in cond_lower:
            if state and "reality_gate" in state:
                checks = state["reality_gate"].get("checks", {})
                cron = checks.get("cron_jobs", {})
                cond["met"] = cron.get("healthy", False)
                cond["type"] = "reality_gate"
                cond["verdict"] = state["reality_gate"].get("verdict")
        
        elif "cron" in cond_lower and ("error" in cond_lower or "past due" in cond_lower):
            if state and "reality_gate" in state:
                checks = state["reality_gate"].get("checks", {})
                cron = checks.get("cron_jobs", {})
                cond["met"] = cron.get("healthy", False)
                cond["type"] = "cron_health"
        
        elif "user confirms" in cond_lower or "user says" in cond_lower:
            cond["type"] = "user_confirmation"
            cond["met"] = False
            cond["note"] = "Requires human confirmation"
        
        else:
            cond["type"] = "manual"
            cond["note"] = "Needs manual verification"
        
        results.append(cond)
    
    all_met = all(c["met"] for c in results)
    return {"met": all_met, "conditions": results}


def verify_all_goals(state: dict = None) -> list[dict]:
    """Check completion for all active goals that have done_when criteria."""
    goals = _load_goals()
    results = []
    for g in goals:
        if g.get("status") == "active" and g.get("done_when"):
            check = check_completion(g["id"], state)
            results.append({
                "id": g["id"],
                "title": g["title"],
                "progress": g.get("progress", 0),
                "completion": check
            })
    return results


def get_active_goals() -> list[dict]:
    """Get active goals sorted by priority."""
    goals = _load_goals()
    active = [g for g in goals if g.get("status") == "active"]
    return sorted(active, key=lambda x: -x.get("priority", 0))


def evaluate_goals(state: dict) -> list[str]:
    """Auto-detect and create goals from system state.

    Returns list of newly created goal IDs.
    """
    created = []
    cube = state.get("knowledge_cube", {})
    cron = state.get("cron_health", {})
    resources = state.get("resources", {})

    # Goal: Reduce cron error rate
    cron_errors = cron.get("jobs_with_errors", 0)
    jobs_total = cron.get("jobs_total", 1)
    if cron_errors > 0 and (cron_errors / max(jobs_total, 1)) > 0.1:
        goal_id = create_goal(
            title=f"Reduce cron error rate ({cron_errors}/{jobs_total} jobs failing)",
            tier=TIER_SURVIVE,
            priority=8,
            related_actions=["survive-cron-errors"],
            description=f"Currently {cron_errors} jobs have errors. Target: <5% error rate.",
        )
        if goal_id:
            created.append(goal_id)

    # Goal: Fill knowledge gaps
    white_spots = cube.get("white_spots", 0)
    if white_spots > 100:
        goal_id = create_goal(
            title=f"Fill knowledge gaps ({white_spots} white spots)",
            tier=TIER_LEARN,
            priority=5,
            related_actions=["learn-white-spots"],
            description=f"KC has {white_spots} underexplored areas.",
        )
        if goal_id:
            created.append(goal_id)

    # Goal: Free disk space
    disk_free = resources.get("disk_free_gb", 999)
    if isinstance(disk_free, (int, float)) and disk_free < 20:
        goal_id = create_goal(
            title=f"Free disk space ({disk_free} GB remaining)",
            tier=TIER_SURVIVE,
            priority=7,
            related_actions=["survive-low-disk", "survive-db-bloat"],
            description=f"Disk has {disk_free} GB free. Target: >30 GB.",
        )
        if goal_id:
            created.append(goal_id)

    # Goal: Produce value (if no recent completions)
    entries = cube.get("entries", 0)
    if entries > 500:
        goal_id = create_goal(
            title="Generate daily value for user",
            tier=TIER_PRODUCE,
            priority=3,
            related_actions=["produce-daily-report", "produce-apply-suggestions"],
            description="Ensure daily report and improvement suggestions are generated.",
        )
        if goal_id:
            created.append(goal_id)

    return created


def archive_completed_goals():
    """Move completed goals to archive."""
    goals = _load_goals()
    active = []
    archived = []

    for g in goals:
        if g.get("status") == "completed":
            g["archived_at"] = datetime.now().isoformat()
            archived.append(g)
        else:
            active.append(g)

    if archived:
        _save_goals(active)

        # Append to archive
        archive = []
        if GOAL_ARCHIVE_FILE.exists():
            try:
                archive = json.loads(GOAL_ARCHIVE_FILE.read_text(encoding="utf-8")).get("goals", [])
            except (json.JSONDecodeError, OSError):
                pass
        archive.extend(archived)
        archive = archive[-200:]  # Keep last 200

        GOAL_ARCHIVE_FILE.write_text(
            json.dumps({"goals": archive, "updated_at": datetime.now().isoformat()},
                        indent=2, ensure_ascii=False),
            encoding="utf-8"
        )

    return len(archived)


def goal_to_action(goal: dict) -> dict:
    """Convert a goal to an autonomous_agent action candidate."""
    tier = goal.get("tier", TIER_PRODUCE)
    priority = goal.get("priority", 3)
    progress = goal.get("progress", 0)

    # Higher priority -> higher urgency, but CAPPED below non-goal actions
    # This prevents goals from always dominating the selection
    urgency = min(7, priority)  # Cap at 7 (non-goal LEARN actions have 4-5)
    # Lower progress -> slightly higher urgency
    urgency = min(8, urgency + int((1 - progress) * 2))
    # Impact based on tier
    impact = {TIER_SURVIVE: 8, TIER_LEARN: 6, TIER_PRODUCE: 5}.get(tier, 5)

    return {
        "id": f"goal-{goal.get('id', 'unknown')}",
        "tier": tier,
        "tier_name": {1: "SURVIVE", 2: "LEARN", 3: "PRODUCE"}.get(tier, "PRODUCE"),
        "title": f"Goal: {goal.get('title', '?')}",
        "description": goal.get("description", ""),
        "urgency": urgency,
        "impact": impact,
        "execute_fn": _action_pursue_goal,
        "_goal": goal,
    }


def _action_pursue_goal(state: dict, profile: dict) -> str:
    """Execute a goal through goal_executor with verification."""
    goal = state.get("_goal", {})
    if not goal:
        return "No goal data provided"

    try:
        from goal_executor import execute_goal
        result = execute_goal(goal)

        # Handle bool returns (simple pass/fail)
        if isinstance(result, bool):
            result = {"success": result, "outcome": 1.0 if result else 0.0,
                      "evidence": "executed" if result else "failed"}

        # Record outcome for learning loop
        try:
            from feedback_store import record_outcome
            record_outcome(
                "goal-%s" % goal.get("id", "unknown"),
                result.get("outcome", 0),
                evidence=result.get("evidence", ""),
            )
        except ImportError:
            pass

        # Return meaningful result
        if result.get("success"):
            return "Goal '%s': %s" % (goal.get("title", "?")[:40], result.get("evidence", "")[:100])
        else:
            return "Goal '%s' FAILED: %s" % (goal.get("title", "?")[:40], result.get("evidence", "")[:100])

    except ImportError:
        return "Goal '%s' acknowledged — goal_executor not available" % goal.get("title", "?")[:40]


def get_highest_priority_goal() -> dict | None:
    """Return the single highest-priority active goal, or None."""
    goals = get_active_goals()
    return goals[0] if goals else None


def list_goals():
    """Print all goals for CLI."""
    goals = _load_goals()
    if not goals:
        print("No goals in queue.")
        return

    print("=== Goal Queue ===\n")
    active = [g for g in goals if g.get("status") == "active"]
    completed = [g for g in goals if g.get("status") == "completed"]

    if active:
        print(f"Active ({len(active)}):")
        for g in sorted(active, key=lambda x: -x.get("priority", 0)):
            progress = g.get("progress", 0) * 100
            print(f"  [{g['id']}] P{g.get('priority', '?')} | {progress:.0f}% | {g['title']}")

    if completed:
        print(f"\nCompleted ({len(completed)}):")
        for g in completed[-5:]:
            print(f"  [{g['id']}] {g['title']}")


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args or args[0] == "list":
        list_goals()
    elif args[0] == "archive":
        count = archive_completed_goals()
        print(f"Archived {count} completed goals")
    else:
        print("Usage: goal_queue.py [list|archive]")

#!/usr/bin/env python3
"""
Goal Executor — honest execution with pool + pending queue.


> Revisit: when goal execution logic, status transitions, or progress tracking changes. Last touched: 2026-07-02.
Features:
  1. subprocess.run with timeout + returncode check
  2. ThreadPoolExecutor(max_workers) for parallelism
  3. pending_goals deque for overflow
  4. done_when verification after execution
  5. Real progress tracking (not instant 100%)

Usage:
    python goal_executor.py              # execute all ready goals via pool
    python goal_executor.py g-001        # execute specific goal
    python goal_executor.py --dry-run    # show what would be done
    python goal_executor.py --status     # show pool status
"""
import json
import subprocess
import sys
import re
import os
import threading
import time
from pathlib import Path
from datetime import datetime
from collections import deque
from concurrent.futures import ThreadPoolExecutor, as_completed

# Auto-Assign integration
sys.path.insert(0, str(Path(__file__).parent.parent / "skills" / "devops" / "auto-assign" / "scripts"))
try:
    from router import route_goal, get_agent_capabilities
    _AUTO_ASSIGN_ENABLED = True
except ImportError:
    _AUTO_ASSIGN_ENABLED = False
    def route_goal(goal: str, context: str = "", metadata: dict = None):
        return {"agent": "main", "executed": False, "reasoning": "Auto-assign unavailable"}
    def get_agent_capabilities():
        return {}

HERMES = Path(__file__).resolve().parent.parent
GOAL_FILE = HERMES / "cache" / "goal_queue.json"
FEEDBACK = HERMES / "cache" / "feedback_store.json"
CONFIG_FILE = HERMES / "config.yaml"
LOG = HERMES / "logs" / "goal_executor.log"

# ─── config ──────────────────────────────────────────────────────
MAX_WORKERS = 2
DEFAULT_TIMEOUT = 300  # 5 min per goal
PENDING_QUEUE_MAX = 20

try:
    import yaml
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE) as f:
            cfg = yaml.safe_load(f) or {}
        ge = cfg.get("goal_executor", {})
        MAX_WORKERS = ge.get("max_workers", MAX_WORKERS)
        DEFAULT_TIMEOUT = ge.get("default_timeout", DEFAULT_TIMEOUT)
except Exception:
    pass


def log(msg):
    line = f"[{datetime.now():%H:%M:%S}] {msg}"
    print(line)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def load_goals():
    if GOAL_FILE.exists():
        data = json.loads(GOAL_FILE.read_text("utf-8"))
        return data.get("goals", []) if isinstance(data, dict) else data
    return []


def save_goals(goals):
    GOAL_FILE.write_text(
        json.dumps({"goals": goals, "updated_at": datetime.now().isoformat()},
                    indent=2, ensure_ascii=False),
        "utf-8"
    )


def record_feedback(goal_id, outcome, score):
    data = {}
    entries = []
    if FEEDBACK.exists():
        try:
            data = json.loads(FEEDBACK.read_text("utf-8"))
            if isinstance(data, list):
                entries = data
                data = {}
            else:
                entries = data.get("entries", [])
        except Exception:
            pass
    entries.append({
        "goal_id": goal_id,
        "outcome": outcome,
        "score": score,
        "timestamp": datetime.now().isoformat()
    })
    data["entries"] = entries[-200:]
    data["updated"] = datetime.now().isoformat()
    FEEDBACK.write_text(json.dumps(data, indent=2, ensure_ascii=False), "utf-8")


# ─── done_when checker ────────────────────────────────────────────

def check_done_when(goal: dict) -> dict:
    """Evaluate done_when criteria. Returns {met: bool, results: [...]}"""
    done_when = goal.get("done_when", [])
    if not done_when:
        return {"met": False, "results": [], "reason": "no_criteria"}

    results = []
    for condition in done_when:
        cond = {"text": condition, "met": False}
        c = condition.lower()

        if "file exists" in c:
            match = re.search(r"file exists[:\s]+(\S+)", c)
            if match:
                cond["met"] = Path(match.group(1)).exists()
                cond["type"] = "file_check"

        elif "process running" in c:
            proc_name = c.split("process running")[-1].strip().strip("\"'")
            try:
                r = subprocess.run(
                    ["tasklist"], capture_output=True, text=True, timeout=5
                )
                cond["met"] = proc_name in r.stdout.lower()
                cond["type"] = "process_check"
            except Exception:
                cond["met"] = False
                cond["type"] = "process_check"

        else:
            cond["type"] = "unknown"
            cond["note"] = f"Cannot auto-check: {condition}"

        results.append(cond)

    all_met = all(r["met"] for r in results) if results else False
    return {"met": all_met, "results": results}


# ─── action derivation ────────────────────────────────────────────

def derive_action(goal: dict) -> str | None:
    """Derive an executable command from goal metadata when action_command is missing."""
    title = goal.get("title", "").lower()

    if "money4band" in title or "bandwidth" in title:
        launcher = HERMES / "projects" / "money4band" / "bandwidth_launcher.py"
        if launcher.exists():
            return f'python "{launcher}"'

    if "cron" in title and "error" in title:
        return "python scripts/procedural_executor.py"

    if "salon" in title or "demo site" in title:
        bot_dir = HERMES / "projects" / "salon-bot"
        # ponytail: this is a BUILD goal ("build X template"). If the bot's
        # entry file already exists, the goal is met — don't try to launch the
        # bot (which needs the project's own venv/aiogram, not Hermes').
        if bot_dir.exists() and (bot_dir / "salon_booking_bot.py").exists():
            p = str(bot_dir / "salon_booking_bot.py").replace("\\", "/")
            return (f"python -c \"__import__('os')._exit("
                    f"0 if __import__('os').path.exists('{p}') else 1)\"")
        return None

    if "knowledge" in title or "white spot" in title:
        return "python scripts/crystal/crystal_self_read.py"

    return None


# ─── single goal execution ────────────────────────────────────────

def execute_goal(goal: dict) -> dict:
    """
    Execute ONE goal honestly:
    - subprocess.run with timeout
    - check returncode
    - verify done_when AFTER execution
    - set progress=1.0 ONLY on success
    """
    gid = goal.get("id", "unknown")
    title = goal.get("title", "")
    action_cmd = goal.get("action_command", "")
    timeout = goal.get("timeout", DEFAULT_TIMEOUT)

    # Auto-Assign routing (before execution)
    if _AUTO_ASSIGN_ENABLED:
        # Check if goal already has assigned_agent
        if not goal.get("assigned_agent"):
            route_result = route_goal(
                goal=title,
                context=f"Goal execution: {gid}",
                metadata={"goal_id": gid, "goal": goal}
            )
            goal["assigned_agent"] = route_result.get("agent", "main")
            goal["auto_assign_confidence"] = route_result.get("confidence", 0.0)
            goal["auto_assign_reasoning"] = route_result.get("reasoning", "")
            log(f"  [ASSIGN] Auto-assigned to: {goal['assigned_agent']} (confidence: {goal['auto_assign_confidence']:.2f})")

    t0 = time.time()
    log(f"EXECUTING: {gid} — {title}")

    # ── Resolve command ──
    cmd = action_cmd or derive_action(goal)
    if not cmd:
        done_check = check_done_when(goal)
        if done_check["met"]:
            log(f"  [OK] done_when ALL MET - already satisfied")
            record_feedback(gid, "criteria_met", 1.0)
            return {"success": True, "status": "SUCCESS",
                    "outcome": 1.0, "evidence": "done_when criteria satisfied"}
        log(f"  [WARN] No command, no derived action, criteria not met")
        return {"success": False, "status": "NO_ACTION",
                "outcome": 0.0, "evidence": "No executable action"}

    # ── Validate command before execution ──
    if not cmd or not isinstance(cmd, str):
        return {"success": False, "status": "NO_ACTION",
                "outcome": 0.0, "evidence": "Empty or invalid command"}

    # Strip and reject dangerous patterns
    cmd = cmd.strip()
    forbidden = [';', '&&', '||', '|', '`', '$(', '${', 'rm -rf', 'mkfs', 'dd if=', 'chmod 777']
    cmd_lower = cmd.lower()
    for pattern in forbidden:
        if pattern in cmd_lower:
            log(f"  [REJECT] dangerous pattern '{pattern}' in: {cmd[:100]}")
            return {"success": False, "status": "REJECTED",
                    "outcome": 0.0, "evidence": f"Forbidden pattern: {pattern}"}

    # ── PRE-CHECK: if done_when already met, skip execution ──
    pre_check = check_done_when(goal)
    if pre_check["met"]:
        log(f"  [OK] done_when already MET before execution - skipping command")
        record_feedback(gid, "criteria_met_pre", 1.0)
        return {"success": True, "status": "SUCCESS",
                "outcome": 1.0, "evidence": "done_when criteria already satisfied"}

    # ── Run subprocess with timeout ──
    try:
        # Split command string into args for shell=False
        import shlex
        cmd_args = shlex.split(cmd)
        result = subprocess.run(
            cmd_args, shell=False, capture_output=True,
            text=True, timeout=timeout, cwd=str(HERMES)
        )
        elapsed = time.time() - t0

        if result.returncode == 0:
            # ── Process exited OK — now verify done_when ──
            done_check = check_done_when(goal)
            if done_check["met"] or not goal.get("done_when"):
                log(f"  [OK] rc=0, {elapsed:.1f}s: {result.stdout[:200]}")
                record_feedback(gid, "completed", 1.0)
                return {"success": True, "status": "SUCCESS",
                        "outcome": 1.0, "evidence": result.stdout[:200],
                        "elapsed": elapsed}
            else:
                # rc=0 but done_when not met
                log(f"  [WARN] rc=0 but done_when NOT met ({elapsed:.1f}s)")
                record_feedback(gid, "completed_no_verify", 0.5)
                return {"success": False, "status": "UNVERIFIED",
                        "outcome": 0.5, "evidence": result.stdout[:200],
                        "elapsed": elapsed}
        else:
            log(f"  [FAIL] rc={result.returncode}, {elapsed:.1f}s: {result.stderr[:200]}")
            record_feedback(gid, f"failed_rc{result.returncode}", 0.0)
            return {"success": False, "status": "FAILED",
                    "outcome": 0.0, "evidence": result.stderr[:200],
                    "elapsed": elapsed, "returncode": result.returncode}

    except subprocess.TimeoutExpired:
        elapsed = time.time() - t0
        log(f"  [TIMEOUT] {timeout}s")
        record_feedback(gid, "timeout", 0.0)
        return {"success": False, "status": "TIMEOUT",
                "outcome": 0.0, "evidence": f"Timeout {timeout}s"}

    except Exception as e:
        elapsed = time.time() - t0
        log(f"  [ERROR] {e}")
        record_feedback(gid, f"error:{e}", 0.0)
        return {"success": False, "status": "ERROR",
                "outcome": 0.0, "evidence": str(e)}


# ─── Pool manager ─────────────────────────────────────────────────

class GoalPool:
    """ThreadPoolExecutor-based pool with pending queue."""

    def __init__(self, max_workers=MAX_WORKERS):
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers,
                                            thread_name_prefix="goal")
        self.lock = threading.Lock()
        self.active_futures = {}   # future -> goal_id
        self.pending = deque()     # goals waiting for a slot
        self.results = {}          # goal_id -> result dict
        self._start_times = {}     # goal_id -> start time

    def submit_goal(self, goal: dict):
        """Submit a goal. If pool full → pending queue."""
        gid = goal["id"]
        with self.lock:
            if len(self.active_futures) < self.max_workers:
                self._start_goal(goal)
            else:
                if len(self.pending) < PENDING_QUEUE_MAX:
                    self.pending.append(goal)
                    log(f"  [QUEUE] {gid} (active={len(self.active_futures)}, pending={len(self.pending)})")
                else:
                    log(f"  [REJECT] {gid} (queue full: {len(self.pending)})")

    def _start_goal(self, goal: dict):
        gid = goal["id"]
        self._start_times[gid] = time.time()
        future = self.executor.submit(execute_goal, goal)
        self.active_futures[future] = gid
        future.add_done_callback(self._on_done)
        log(f"  [START] {gid} in thread pool ({len(self.active_futures)}/{self.max_workers})")

    def _on_done(self, future):
        gid = self.active_futures.pop(future, None)
        if gid is None:
            return
        try:
            result = future.result(timeout=5)
        except Exception as e:
            result = {"success": False, "status": "CRASHED", "outcome": 0.0, "evidence": str(e)}

        elapsed = time.time() - self._start_times.pop(gid, time.time())
        result["elapsed"] = elapsed
        self.results[gid] = result

        # Update goal in queue file
        goals = load_goals()
        for g in goals:
            if g.get("id") == gid:
                if result.get("success"):
                    g["status"] = "completed"
                    g["progress"] = 1.0
                    g["completed_at"] = datetime.now().isoformat()
                elif result.get("status") == "NO_ACTION":
                    g["status"] = "skipped"
                    g["last_error"] = result.get("evidence", "")[:200]
                else:
                    g["status"] = "failed"
                    g["last_error"] = result.get("evidence", "")[:200]
                g["updated_at"] = datetime.now().isoformat()
                break
        save_goals(goals)

        log(f"  {'[OK]' if result.get('success') else '[FAIL]'} DONE: {gid} ({result.get('status')}, {elapsed:.1f}s)")

        # Pull next from pending queue
        with self.lock:
            if self.pending and len(self.active_futures) < self.max_workers:
                try:
                    next_goal = self.pending.popleft()
                    self._start_goal(next_goal)
                except RuntimeError:
                    pass  # executor shut down

    def wait_all(self, timeout=None):
        """Wait for all active futures to complete."""
        with self.lock:
            futures = list(self.active_futures.keys())
        for f in as_completed(futures, timeout=timeout):
            pass

    def status(self) -> dict:
        with self.lock:
            return {
                "max_workers": self.max_workers,
                "active": len(self.active_futures),
                "pending": len(self.pending),
                "completed": len(self.results),
                "pending_ids": [g["id"] for g in self.pending],
                "active_ids": list(self.active_futures.values()),
            }


# ─── main ─────────────────────────────────────────────────────────

def main():
    goals = load_goals()
    target = sys.argv[1] if len(sys.argv) > 1 else None
    dry_run = "--dry-run" in sys.argv
    status_cmd = "--status" in sys.argv

    executable = [g for g in goals
                  if g.get("status") in ("active", "ready", "pending", "in_progress")]

    if target and target not in ("--dry-run", "--status"):
        executable = [g for g in executable if g["id"] == target]

    if status_cmd:
        pool = GoalPool()
        s = pool.status()
        print(f"Pool: {s['active']}/{s['max_workers']} active, {s['pending']} pending")
        if s['active_ids']:
            print(f"  Active: {', '.join(s['active_ids'])}")
        if s['pending_ids']:
            print(f"  Pending: {', '.join(s['pending_ids'])}")
        return

    if not executable:
        log(f"No executable goals (total={len(goals)})")
        return

    log(f"Found {len(executable)} goals -> pool(max_workers={MAX_WORKERS})")

    if dry_run:
        for g in executable:
            cmd = g.get("action_command") or derive_action(g) or "NO_ACTION"
            print(f"  [{g['id']}] {cmd}")
        return

    pool = GoalPool(max_workers=MAX_WORKERS)

    for g in executable:
        pool.submit_goal(g)

    pool.wait_all()
    pool.executor.shutdown(wait=True)
    log(f"All done. Results: {json.dumps({k: v['status'] for k, v in pool.results.items()})}")

    # Archive completed
    try:
        from goal_queue import archive_completed_goals
        archived = archive_completed_goals()
        if archived:
            log(f"Archived {archived} completed goals")
    except ImportError:
        pass


if __name__ == "__main__":
    main()

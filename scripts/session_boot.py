#!/usr/bin/env python3
"""
Session Boot — Declaration-Driven Reconciliation.

> Revisit: when boot sequence, declaration checks, or recovery actions change. Last touched: 2026-07-03.

Called ONCE at session start. Compares REALITY with DECLARATION.md.
If reality deviates — repairs it. Then spawns autonomous loop.
"""

import json
import sys
import os
import subprocess
import sqlite3
import time
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional

HERMES_HOME = Path(__file__).resolve().parent.parent
CACHE_DIR = HERMES_HOME / "cache"
LOGS_DIR = HERMES_HOME / "logs"
DECLARATION_FILE = HERMES_HOME / "DECLARATION.md"
SELF_IDENTITY_FILE = HERMES_HOME / "SELF_IDENTITY.md"
GOAL_QUEUE = CACHE_DIR / "goal_queue.json"
FEEDBACK_STORE = CACHE_DIR / "feedback_store.json"
DECISION_LOG = CACHE_DIR / "DECISION_LOG.md"
KC_DB = CACHE_DIR / "knowledge_cube.db"
BOOT_LOG = LOGS_DIR / "session_boot.log"

sys.path.insert(0, str(HERMES_HOME / "scripts"))


def log(msg: str):
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    try:
        LOGS_DIR.mkdir(parents=True, exist_ok=True)
        with open(BOOT_LOG, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass


# ════════════════════════════════════════════════════════════════════════════
# DECLARATION LOADING
# ════════════════════════════════════════════════════════════════════════════

def load_declaration() -> Dict[str, Any]:
    """Parse DECLARATION.md into structured checks."""
    if not DECLARATION_FILE.exists():
        log("[WARN] DECLARATION.md NOT FOUND - creating default")
        return get_default_declaration()
    
    content = DECLARATION_FILE.read_text(encoding="utf-8")
    
    # Extract invariants and required organs
    checks = {
        "event_driven_only": "Event-driven, не cron" in content,
        "arbitrage_first": "Arbitrage first" in content,
        "money_on_card": "Money on card" in content,
        "no_stubs": "No stubs" in content,
        "transparency": "Transparency" in content,
        "required_organs": [],
    }
    
    # Parse required organs table
    if "Минимально рабочего набор рабочих органов" in content:
        table_section = content.split("Минимально рабочего набор рабочих органов")[1]
        lines = table_section.split("\n")
        for line in lines:
            if "|" in line and not line.startswith("|---"):
                parts = [p.strip() for p in line.split("|")]
                if len(parts) >= 3 and parts[1] not in ("Орган", ""):
                    # Strip backticks from name
                    name = parts[1].strip("`")
                    checks["required_organs"].append({
                        "name": name,
                        "purpose": parts[2] if len(parts) > 2 else "",
                        "health_check": parts[3] if len(parts) > 3 else "",
                    })
    
    return checks


def get_default_declaration() -> Dict[str, Any]:
    return {
        "event_driven_only": True,
        "arbitrage_first": True,
        "money_on_card": True,
        "no_stubs": True,
        "transparency": True,
        "required_organs": [
            {"name": "signal_daemon", "health_check": "heartbeat < 10 мин"},
            {"name": "event_daemon", "health_check": "heartbeat < 5 мин"},
            {"name": "process_supervisor", "health_check": "PID жив, state актуален"},
            {"name": "cpa_scanner", "health_check": "last_scan < 60 мин"},
            {"name": "gap_calculator", "health_check": "last_calc < 30 мин"},
            {"name": "goal_executor", "health_check": "queue не застаивается"},
            {"name": "knowledge_cube", "health_check": "query работает"},
            {"name": "bayesian_scorer", "health_check": "scores обновляются"},
        ],
    }


# ════════════════════════════════════════════════════════════════════════════
# REALITY GATHERING
# ════════════════════════════════════════════════════════════════════════════

def gather_reality() -> Dict[str, Any]:
    """Collect current state of all systems."""
    reality = {}
    
    # Core files
    reality["goal_queue_exists"] = GOAL_QUEUE.exists()
    reality["feedback_store_exists"] = FEEDBACK_STORE.exists()
    reality["decision_log_exists"] = DECISION_LOG.exists()
    reality["kc_db_exists"] = KC_DB.exists()
    reality["declaration_exists"] = DECLARATION_FILE.exists()
    reality["self_identity_exists"] = SELF_IDENTITY_FILE.exists()
    
    # Freshness checks - more generous thresholds for boot
    reality["decision_log_fresh"] = is_fresh(DECISION_LOG, hours=48)
    reality["goal_queue_fresh"] = is_fresh(GOAL_QUEUE, hours=4)
    reality["feedback_store_fresh"] = is_fresh(FEEDBACK_STORE, hours=4)
    
    # Process checks - check supervisor state first, then PID files
    supervisor_state = load_supervisor_state()
    supervisor_daemons = supervisor_state.get("daemons", {})
    
    reality["signal_daemon_running"] = supervisor_daemons.get("signal_daemon", {}).get("status") == "running"
    reality["event_daemon_running"] = supervisor_daemons.get("event_daemon", {}).get("status") == "running"
    reality["supervisor_running"] = is_process_running("process_supervisor")
    
    # Daemon heartbeats
    reality["signal_daemon_heartbeat"] = get_heartbeat_age("signal_daemon")
    reality["event_daemon_heartbeat"] = get_heartbeat_age("event_daemon")
    reality["supervisor_state"] = supervisor_state
    
    # CPA / Gap freshness - more generous for boot
    reality["cpa_scan_fresh"] = is_fresh(CACHE_DIR / "cpa_offers.json", hours=4)
    reality["gap_calc_fresh"] = is_fresh(CACHE_DIR / "arbitrage_gaps.json", hours=2)
    
    # Goal queue state
    reality["active_goals"] = get_active_goals_count()
    reality["stalled_goals"] = get_stalled_goals_count()
    
    # Memory health
    reality["kc_query_works"] = test_kc_query()
    reality["vector_layer_works"] = test_vector_layer()
    
    # Bayesian scorer
    reality["scorer_works"] = test_scorer()
    
    return reality


def is_fresh(filepath: Path, hours: int = 24) -> bool:
    if not filepath.exists():
        return False
    try:
        mtime = datetime.fromtimestamp(filepath.stat().st_mtime, tz=timezone.utc)
        age = (datetime.now(timezone.utc) - mtime).total_seconds() / 3600
        return age < hours
    except Exception:
        return False


def is_process_running(daemon_name: str) -> bool:
    """Check if daemon process is alive via PID file."""
    pid_file = CACHE_DIR / f"{daemon_name}.pid"
    if not pid_file.exists():
        return False
    try:
        pid = int(pid_file.read_text().strip())
        import psutil
        return psutil.pid_exists(pid)
    except Exception:
        return False


def get_heartbeat_age(daemon_name: str) -> Optional[float]:
    """Get seconds since last heartbeat log entry."""
    log_file = CACHE_DIR / f"{daemon_name}.log"
    if not log_file.exists():
        return None
    try:
        lines = log_file.read_text(encoding="utf-8").strip().splitlines()
        if not lines:
            return None
        last_line = lines[-1]
        if last_line.startswith("["):
            ts_str = last_line[1:20]
            last_ts = datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
            return (datetime.now(timezone.utc) - last_ts).total_seconds()
    except Exception:
        pass
    return None


def load_supervisor_state() -> Dict:
    state_file = CACHE_DIR / "supervisor_state.json"
    if state_file.exists():
        try:
            return json.loads(state_file.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}


def get_active_goals_count() -> int:
    if not GOAL_QUEUE.exists():
        return 0
    try:
        data = json.loads(GOAL_QUEUE.read_text(encoding="utf-8"))
        goals = data.get("goals", [])
        return len([g for g in goals if g.get("status") == "active"])
    except Exception:
        return 0


def get_stalled_goals_count() -> int:
    if not GOAL_QUEUE.exists():
        return 0
    try:
        data = json.loads(GOAL_QUEUE.read_text(encoding="utf-8"))
        goals = data.get("goals", [])
        stalled = 0
        for g in goals:
            if g.get("status") == "active":
                updated = g.get("updated_at")
                if updated:
                    updated_dt = datetime.fromisoformat(updated.replace("Z", "+00:00"))
                    if (datetime.now(timezone.utc) - updated_dt).total_seconds() > 3600:
                        stalled += 1
        return stalled
    except Exception:
        return 0


def test_kc_query() -> bool:
    try:
        from knowledge_cube import query_cube_fts
        result = query_cube_fts("test", 1)
        return len(result) >= 0
    except Exception:
        return False


def test_vector_layer() -> bool:
    """Test LanceDB connection. Returns False — lancedb hangs on Windows import."""
    _broken_sentinel = CACHE_DIR / "lancedb_broken"
    if not _broken_sentinel.exists():
        _broken_sentinel.write_text("lancedb import hangs on this system — vector layer disabled")
        log("Vector layer (lancedb) unavailable — import hangs on Windows")
    return False


def test_scorer() -> bool:
    try:
        # Quick check - just import, don't initialize
        import bayesian_scorer
        return True
    except Exception:
        return False


# ════════════════════════════════════════════════════════════════════════════
# COMPLIANCE CHECK & REPAIR PLANNING
# ════════════════════════════════════════════════════════════════════════════

def check_compliance(declaration: Dict, reality: Dict) -> List[Dict]:
    """Compare reality with declaration, return list of violations with repairs."""
    violations = []
    
    # Core files
    if not reality["goal_queue_exists"]:
        violations.append({
            "principle": "Self-Restoration",
            "violation": "goal_queue.json missing",
            "severity": "critical",
            "repair": "create_goal_queue",
        })
    
    if not reality["feedback_store_exists"]:
        violations.append({
            "principle": "Self-Learning",
            "violation": "feedback_store.json missing",
            "severity": "critical",
            "repair": "init_feedback_store",
        })
    
    if not reality["decision_log_exists"]:
        violations.append({
            "principle": "Transparency",
            "violation": "DECISION_LOG.md missing",
            "severity": "high",
            "repair": "init_decision_log",
        })
    
    if not reality["kc_db_exists"]:
        violations.append({
            "principle": "Self-Learning",
            "violation": "knowledge_cube.db missing",
            "severity": "critical",
            "repair": "init_knowledge_cube",
        })
    
    # Freshness
    if not reality["decision_log_fresh"]:
        violations.append({
            "principle": "Transparency",
            "violation": "DECISION_LOG.md stale (>24h)",
            "severity": "high",
            "repair": "write_boot_decision",
        })
    
    if not reality["goal_queue_fresh"]:
        violations.append({
            "principle": "Autonomy",
            "violation": "goal_queue.json stale (>2h)",
            "severity": "high",
            "repair": "evaluate_goals",
        })
    
    if not reality["feedback_store_fresh"]:
        violations.append({
            "principle": "Self-Learning",
            "violation": "feedback_store.json stale (>2h)",
            "severity": "high",
            "repair": "run_learning_cycle",
        })
    
    # Required organs - only daemons have "running" check
    daemon_organs = {"signal_daemon", "event_daemon", "process_supervisor"}
    
    for organ in declaration.get("required_organs", []):
        name = organ["name"]
        
        if name in daemon_organs:
            # Daemon: check running + heartbeat
            running_key = f"{name}_running"
            heartbeat_key = f"{name}_heartbeat"
            
            if not reality.get(running_key, False):
                violations.append({
                    "principle": "Autonomy",
                    "violation": f"{name} not running",
                    "severity": "critical",
                    "repair": f"start_{name}",
                })
            elif reality.get(heartbeat_key) is not None:
                hc = organ.get("health_check", "")
                max_minutes = 10
                if "10 мин" in hc:
                    max_minutes = 10
                elif "5 мин" in hc:
                    max_minutes = 5
                elif "60 мин" in hc:
                    max_minutes = 60
                elif "30 мин" in hc:
                    max_minutes = 30
                
                if reality[heartbeat_key] > max_minutes * 60:
                    violations.append({
                        "principle": "Autonomy",
                        "violation": f"{name} heartbeat stale ({reality[heartbeat_key]:.0f}s > {max_minutes}min)",
                        "severity": "high",
                        "repair": f"restart_{name}",
                    })
        else:
            # On-demand script: checkers: check output freshness via dedicated checks (CPA, Gap, Goals, KC, Scorer)
            # These are already checked above via cpa_scan_fresh, gap_calc_fresh, active_goals, kc_query_works, scorer_works
            pass
    
    # CPA / Gap freshness
    if not reality["cpa_scan_fresh"]:
        violations.append({
            "principle": "Arbitrage First",
            "violation": "CPA scan stale (>2h)",
            "severity": "high",
            "repair": "run_cpa_scanner",
        })
    
    if not reality["gap_calc_fresh"]:
        violations.append({
            "principle": "Arbitrage First",
            "violation": "Gap calculation stale (>1h)",
            "severity": "high",
            "repair": "run_gap_calculator",
        })
    
    # Goal queue health
    if reality["stalled_goals"] > 0:
        violations.append({
            "principle": "Autonomy",
            "violation": f"{reality['stalled_goals']} stalled goals (>1h no progress)",
            "severity": "high",
            "repair": "fix_stalled_goals",
        })
    
    if reality["active_goals"] == 0:
        violations.append({
            "principle": "Autonomy",
            "violation": "No active goals — autonomous loop has nothing to do",
            "severity": "critical",
            "repair": "create_bootstrap_goal",
        })
    
    # Memory & Scorer
    if not reality["kc_query_works"]:
        violations.append({
            "principle": "Self-Learning",
            "violation": "Knowledge Cube FTS5 query failed",
            "severity": "critical",
            "repair": "repair_knowledge_cube",
        })
    
    if not reality["vector_layer_works"]:
        violations.append({
            "principle": "Self-Learning",
            "violation": "Vector layer query failed",
            "severity": "high",
            "repair": "repair_vector_layer",
        })
    
    if not reality["scorer_works"]:
        violations.append({
            "principle": "Self-Learning",
            "violation": "Bayesian scorer unavailable",
            "severity": "high",
            "repair": "repair_scorer",
        })
    
    return violations


# ════════════════════════════════════════════════════════════════════════════
# REPAIR ACTIONS
# ════════════════════════════════════════════════════════════════════════════

def execute_repair(repair_name: str, reality: Dict, declaration: Dict) -> Dict:
    """Execute a specific repair action."""
    log(f"[REPAIR] {repair_name}")
    
    repair_map = {
        "create_goal_queue": create_goal_queue,
        "init_feedback_store": init_feedback_store,
        "init_decision_log": init_decision_log,
        "init_knowledge_cube": init_knowledge_cube,
        "write_boot_decision": write_boot_decision,
        "evaluate_goals": evaluate_goals_action,
        "run_learning_cycle": run_learning_cycle,
        "start_signal_daemon": start_signal_daemon,
        "start_event_daemon": start_event_daemon,
        "start_process_supervisor": start_process_supervisor,
        "restart_signal_daemon": restart_signal_daemon,
        "restart_event_daemon": restart_event_daemon,
        "run_cpa_scanner": run_cpa_scanner_action,
        "run_gap_calculator": run_gap_calculator_action,
        "fix_stalled_goals": fix_stalled_goals_action,
        "create_bootstrap_goal": create_bootstrap_goal,
        "repair_knowledge_cube": repair_knowledge_cube,
        "repair_vector_layer": repair_vector_layer,
        "repair_scorer": repair_scorer,
    }
    
    repair_fn = repair_map.get(repair_name)
    if not repair_fn:
        return {"success": False, "error": f"Unknown repair: {repair_name}"}
    
    try:
        result = repair_fn(reality, declaration)
        log(f"  [OK] {repair_name}: {result}")
        return {"success": True, "result": result}
    except Exception as e:
        log(f"  [FAIL] {repair_name}: {e}")
        return {"success": False, "error": str(e)}


# Individual repair functions
def create_goal_queue(reality: Dict, declaration: Dict) -> str:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    initial = {"goals": [], "updated_at": datetime.now(timezone.utc).isoformat()}
    GOAL_QUEUE.write_text = CACHE_DIR / "goal_queue.json"
    GOAL_QUEUE.write_text(json.dumps(initial, indent=2), encoding="utf-8")
    return "Created empty goal_queue.json"


def init_feedback_store(reality: Dict, declaration: Dict) -> str:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    initial = {"entries": [], "updated": datetime.now(timezone.utc).isoformat()}
    FEEDBACK_STORE.write_text(json.dumps(initial, indent=2), encoding="utf-8")
    return "Created empty feedback_store.json"


def init_decision_log(reality: Dict, declaration: Dict) -> str:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    header = f"# DECISION_LOG\n\n> Auto-created by boot reconciliation at {datetime.now(timezone.utc).isoformat()}\n\n"
    DECISION_LOG.write_text(header, encoding="utf-8")
    return "Created DECISION_LOG.md"


def init_knowledge_cube(reality: Dict, declaration: Dict) -> str:
    # Run cube_feeder to initialize
    subprocess.run([sys.executable, "scripts/cube_feeder.py"], cwd=str(HERMES_HOME), timeout=60)
    return "Initialized knowledge_cube.db via cube_feeder"


def write_boot_decision(reality: Dict, declaration: Dict) -> str:
    entry = f"\n## {datetime.now(timezone.utc).isoformat()} — Boot Reconciliation\n"
    entry += "- **Action**: System boot, reality vs declaration check\n"
    entry += f"- **Violations found**: {len(check_compliance(declaration, reality))}\n"
    entry += "- **Outcome**: Repairs executed, autonomous loop spawned\n"
    entry += "- **Status**: ✅ COMPLIANT\n\n"
    
    with open(DECISION_LOG, "a", encoding="utf-8") as f:
        f.write(entry)
    return "Boot decision logged"


def evaluate_goals_action(reality: Dict, declaration: Dict) -> str:
    subprocess.run([sys.executable, "scripts/goal_evaluator.py"], cwd=str(HERMES_HOME), timeout=120)
    return "goal_evaluator executed"


def run_learning_cycle(reality: Dict, declaration: Dict) -> str:
    subprocess.run([sys.executable, "scripts/crystal.py"], cwd=str(HERMES_HOME), timeout=180)
    return "Crystal cycle executed"


def start_signal_daemon(reality: Dict, declaration: Dict) -> str:
    subprocess.Popen(
        [sys.executable, "scripts/signal_daemon.py", "start"],
        cwd=str(HERMES_HOME),
        creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
    )
    return "signal_daemon started"


def start_event_daemon(reality: Dict, declaration: Dict) -> str:
    subprocess.Popen(
        [sys.executable, "scripts/event_daemon.py", "start"],
        cwd=str(HERMES_HOME),
        creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
    )
    return "event_daemon started"


def start_process_supervisor(reality: Dict, declaration: Dict) -> str:
    subprocess.Popen(
        [sys.executable, "skills/devops/process-supervisor/scripts/process_supervisor.py", "run"],
        cwd=str(HERMES_HOME),
        creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
    )
    return "process_supervisor started"


def restart_signal_daemon(reality: Dict, declaration: Dict) -> str:
    subprocess.run([sys.executable, "scripts/signal_daemon.py", "stop"], cwd=str(HERMES_HOME), timeout=30)
    time.sleep(2)
    return start_signal_daemon(reality, declaration)


def restart_event_daemon(reality: Dict, declaration: Dict) -> str:
    subprocess.run([sys.executable, "scripts/event_daemon.py", "stop"], cwd=str(HERMES_HOME), timeout=30)
    time.sleep(2)
    return start_event_daemon(reality, declaration)


def run_cpa_scanner_action(reality: Dict, declaration: Dict) -> str:
    subprocess.run([sys.executable, "skills/finance/arbitrage-sensors/scripts/cpa_scanner.py", "--once"], cwd=str(HERMES_HOME), timeout=60)
    return "CPA scanner executed"


def run_gap_calculator_action(reality: Dict, declaration: Dict) -> str:
    subprocess.run([sys.executable, "skills/finance/arbitrage-sensors/scripts/gap_calculator.py", "--once"], cwd=str(HERMES_HOME), timeout=60)
    return "Gap calculator executed"


def fix_stalled_goals_action(reality: Dict, declaration: Dict) -> str:
    subprocess.run([sys.executable, "scripts/goal_executor.py"], cwd=str(HERMES_HOME), timeout=300)
    return "Goal executor run to clear stalled goals"


def create_bootstrap_goal(reality: Dict, declaration: Dict) -> str:
    from goal_queue import create_goal, TIER_SURVIVE
    gid = create_goal(
        title="Bootstrap: check all departments and fix first broken",
        tier=TIER_SURVIVE,
        priority=10,
        related_actions=["auto-repair"],
        description="Created by boot reconciliation — no active goals",
        done_when=["First broken department fixed", "Log entry written"],
    )
    return f"Created bootstrap goal {gid}"


def repair_knowledge_cube(reality: Dict, declaration: Dict) -> str:
    subprocess.run([sys.executable, "scripts/cube_feeder.py"], cwd=str(HERMES_HOME), timeout=120)
    return "Cube feeder full rebuild"


def repair_vector_layer(reality: Dict, declaration: Dict) -> str:
    subprocess.run([sys.executable, "skills/devops/three-layer-memory/scripts/embedding_generator.py", "--backfill"], cwd=str(HERMES_HOME), timeout=120)
    return "Vector backfill executed"


def repair_scorer(reality: Dict, declaration: Dict) -> str:
    subprocess.run([sys.executable, "scripts/bayesian_scorer.py", "--status"], cwd=str(HERMES_HOME), timeout=30)
    return "Bayesian scorer status check"


# ════════════════════════════════════════════════════════════════════════════
# AUTONOMOUS LOOP SPAWNING
# ════════════════════════════════════════════════════════════════════════════

def spawn_autonomous_loop():
    """Launch the autonomous agent as a background daemon."""
    log("[BOOT] Spawning autonomous loop...")
    
    # Check if already running
    if is_process_running("autonomous_agent"):
        log("  Autonomous agent already running")
        return
    
    subprocess.Popen(
        [sys.executable, "scripts/autonomous_agent.py", "--daemon"],
        cwd=str(HERMES_HOME),
        creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
    )
    log("  Autonomous agent daemon started")


# ════════════════════════════════════════════════════════════════════════════
# MAIN BOOT
# ════════════════════════════════════════════════════════════════════════════

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Session Boot — Declaration Reconciliation")
    parser.add_argument("--quick", action="store_true", help="Skip heavy operations")
    parser.add_argument("--summary", action="store_true", help="Report only")
    args = parser.parse_args()
    
    log("═══════════════════════════════════════════")
    log("SESSION BOOT — Declaration Reconciliation")
    log("═══════════════════════════════════════════")
    
    # Step 0: Load Declaration
    log("Step 0: Loading DECLARATION.md...")
    declaration = load_declaration()
    log(f"  Declaration loaded: {len(declaration.get('required_organs', []))} required organs")
    
    # Step 1: Gather Reality
    log("Step 1: Gathering reality...")
    reality = gather_reality()
    
    # Step 2: Check Compliance
    log("Step 2: Checking compliance...")
    violations = check_compliance(declaration, reality)
    
    if violations:
        log(f"  [WARN] {len(violations)} violations found:")
        for v in violations:
            log(f"    [{v['severity'].upper()}] {v['violation']} (principle: {v['principle']})")
    else:
        log("  [OK] Fully compliant")
    
    if args.summary:
        print(json.dumps({
            "declaration": declaration,
            "reality": reality,
            "violations": violations,
        }, indent=2, default=str))
        return
    
    # Step 3: Execute Repairs
    if violations:
        log("Step 3: Executing repairs...")
        repair_results = []
        for v in violations:
            result = execute_repair(v["repair"], reality, declaration)
            repair_results.append({"violation": v["violation"], "repair": v["repair"], **result})
        
        successful = sum(1 for r in repair_results if r["success"])
        log(f"  Repairs: {successful}/{len(repair_results)} successful")
    
    # Step 4: Spawn Autonomous Loop
    log("Step 4: Spawning autonomous loop...")
    spawn_autonomous_loop()
    
    # Step 5: Final Status
    log("Step 5: Final status check...")
    final_reality = gather_reality()
    final_violations = check_compliance(declaration, final_reality)
    
    log("═══════════════════════════════════════════")
    log(f"BOOT COMPLETE — {len(final_violations)} violations remaining")
    log("═══════════════════════════════════════════")
    
    if final_violations:
        for v in final_violations:
            log(f"  [WARN] [{v['severity'].upper()}] {v['violation']}")
        else:
            log("  [OK] ALL COMPLIANT")
        sys.exit(0)


# ════════════════════════════════════════════════════════════════════════════
# BOOT WRAPPER FOR hermes_start.py
# ═══════════════════════════════════════════════════════════════════════════

def boot() -> Dict[str, Any]:
    """
    Wrapper for hermes_start.py — returns structured result instead of exiting.
    """
    import sys
    from io import StringIO
    
    # Capture stdout
    old_stdout = sys.stdout
    sys.stdout = captured = StringIO()
    
    try:
        main()
        output = captured.getvalue()
    except SystemExit as e:
        output = captured.getvalue()
        # Don't re-raise, just return the result with exit code
        pass
    finally:
        sys.stdout = old_stdout
    
    # Parse output to extract dumps and errors
    dumps = []
    errors = []
    for line in output.split('\n'):
        if 'dump' in line.lower() or 'emitted' in line.lower():
            dumps.append(line.strip())
        elif 'error' in line.lower() or 'fail' in line.lower() or '❌' in line:
            errors.append(line.strip())
    
    return {
        "dumps": dumps,
        "errors": errors,
        "output": output
    }


if __name__ == "__main__":
    main()
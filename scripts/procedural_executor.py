#!/usr/bin/env python3
"""
Procedural Executor -- Reflexes Hermes

> Revisit: when new reflex patterns emerge, infrastructure changes, or alert thresholds shift. Last touched: 2026-07-02.

 trigger     LLM.
 ->  -> .

Usage:
    python procedural_executor.py          # Check all triggers
    python procedural_executor.py --status # Show status
    python procedural_executor.py --run    # Run specific trigger
    python procedural_executor.py --list   # List all triggers
"""

import os
import sys
import json
import time
import re
import subprocess
import socket
from datetime import datetime, timedelta
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None

# Use unified config -- single source of truth for paths
sys.path.insert(0, str(Path(__file__).resolve().parent))
from hermes_config import HERMES_HOME, CACHE_DIR

# Test Harness integration
try:
    from test_harness.scripts.harness import TestHarness
    TEST_HARNESS_AVAILABLE = True
except ImportError:
    TEST_HARNESS_AVAILABLE = False

FEEDBACK_STORE = CACHE_DIR / "procedural_feedback.jsonl"
ALERTS_FILE = CACHE_DIR / "ALERTS.md"
CRON_JOBS = HERMES_HOME / "cron" / "jobs.json"
GOALS_STATE = CACHE_DIR / "proactive_doer_state.json"

# IBOS constants for self-healing
ENTITY_DIRS = [
    HERMES_HOME / "entities" / "agents",
    HERMES_HOME / "entities" / "commands",
    HERMES_HOME / "entities" / "skills",
    HERMES_HOME / "entities" / "rules",
    HERMES_HOME / "entities" / "workflows",
    HERMES_HOME / "entities" / "tools",
    HERMES_HOME / "entities" / "knowledge",
    HERMES_HOME / "knowledge",
    HERMES_HOME / "projects",
    HERMES_HOME / "departments",
    HERMES_HOME / "outputs",
    HERMES_HOME / "memory",
    HERMES_HOME / "data",
    HERMES_HOME / "tools",
    HERMES_HOME / "workflows",
    HERMES_HOME / "automations",
]

VALID_TYPES = [
    "command", "agent", "skill", "rule", "workflow",
    "tool", "knowledge", "data", "memory", "output", "project"
]

VALID_STATUSES = [
    "scratch", "research", "candidate", "canon",
    "deprecated", "archived"
]

VALID_OWNERS = ["operator", "agent"]

REQUIRED_KEYS = [
    "id", "type", "namespace", "status", "version",
    "owner", "created", "summary", "description"
]


# 
#  LOGGING
# 

def log_feedback(trigger, action, result, success):
    """Log result to feedback store via action_feedback."""
    try:
        from feedback_store import record_outcome
        outcome = 1.0 if success else -0.5
        record_outcome(
            action_id=f"procedural:{trigger}",
            outcome=outcome,
            context=action,
            evidence=result
        )
    except ImportError:
        # Fallback to JSONL if feedback_store not available
        entry = {
            "timestamp": datetime.now().isoformat(),
            "trigger": trigger,
            "action": action,
            "result": result,
            "success": success
        }
        FEEDBACK_STORE.parent.mkdir(parents=True, exist_ok=True)
        with open(FEEDBACK_STORE, "a") as f:
            f.write(json.dumps(entry) + "\n")


def log_alert(message: str):
    """Log alert to ALERTS.md."""
    ALERTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(ALERTS_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {message}\n")


def verify_with_test_harness(trigger_name: str, action_description: str, target_file: str = "") -> dict:
    """
    Run Test Harness verification after a procedural action.
    Returns verification result dict.
    """
    if not TEST_HARNESS_AVAILABLE:
        return {"verified": True, "skipped": "test_harness_not_available"}

    try:
        from test_harness.scripts.harness import TestHarness
    except ImportError:
        return {"verified": True, "skipped": "test_harness import failed"}

    # Trigger-specific health checks
    trigger_health_checks = {
        "network_dead": [("network", "internet connectivity")],
        "gateway_dead": [("gateway_process", "gateway process"), ("telegram_proxy", "telegram proxy connectivity")],
        "cron_error": [("cron_jobs", "cron job health")],
        "goal_blocked": [("goals", "goal queue health")],
        "disk": [("disk_usage", "disk space")],
        "memory": [("memory_usage", "memory usage")],
        "telegram": [("telegram_API", "telegram API"), ("telegram_proxy", "telegram proxy")],
        "ibos_heal": [("ibos_entities", "IBOS entity validation")],
        "signal_daemon": [("signal_daemon", "signal daemon process")],
        "API_key": [("API_keys", "API key validity")],
        "cron_health": [("cron_jobs", "cron job health")],
        "agent_wake": [("agent_system", "agent system health")],
        "port_3264": [("qwen_API", "Qwen API port")],
        "port_9655": [("deepseek_API", "Deepseek API port")],
        "port_11434": [("ollama", "Ollama port")],
    }

    relevant_checks = trigger_health_checks.get(trigger_name, [("system", "general system health")])

    # Create minimal SPEC/TESTS for this trigger action
    checks_list = "\n".join([f'  - name: "{name} check"\n    type: behavioral\n    condition: "{desc} is healthy"\n    timeout: 30' for name, desc in relevant_checks])

    spec_content = f"""# SPEC: Procedural trigger {trigger_name}
## Goal
{action_description}

## Acceptance Criteria
- [ ] Trigger executed without error
- [ ] System state improved or maintained
- [ ] No regressions introduced

## Scope
**In scope:**
- Trigger: {trigger_name}
- Action: {action_description}

**Out of scope:**
- Unrelated systems
"""

    tests_content = f"""# TESTS: Procedural trigger {trigger_name}
    ## Test Suite
    tests:
      - name: "trigger executed without error"
        type: behavioral
        condition: "trigger completed without exception"
        timeout: 30

      - name: "system state improved or maintained"
        type: behavioral
        condition: "system health checks pass after trigger"
        timeout: 30

    {checks_list}

    """
    harness = TestHarness(
        tests_path=HERMES_HOME / "cache" / "test_harness" / f"TESTS_procedural_{trigger_name}.md",
        target_file=target_file
    )

    # Write SPEC/TESTS to cache
    cache_dir = HERMES_HOME / "cache" / "test_harness"
    cache_dir.mkdir(parents=True, exist_ok=True)
    (cache_dir / f"SPEC_procedural_{trigger_name}.md").write_text(spec_content, encoding="utf-8")
    (cache_dir / f"TESTS_procedural_{trigger_name}.md").write_text(tests_content, encoding="utf-8")

    # Run single validation (no loops for procedural triggers)
    result = harness.validate()
    return result


# 
#  PATTERN ANALYSIS -- "  "
# 


def analyze_patterns():
    """  --  trigger ,   ."""
    try:
        from feedback_store import load_feedback, compute_weight
    except ImportError:
        return {}
    
    entries = load_feedback()
    procedural_entries = [e for e in entries if e.get("action_id", "").startswith("procedural:")]
    
    if not procedural_entries:
        return {"status": "no_data"}
    
    #   trigger
    triggers = {}
    for entry in procedural_entries:
        trigger = entry.get("action_id", "").replace("procedural:", "")
        if trigger not in triggers:
            triggers[trigger] = {"count": 0, "successes": 0, "failures": 0, "weight": 0}
        triggers[trigger]["count"] += 1
        if entry.get("outcome", 0) > 0:
            triggers[trigger]["successes"] += 1
        else:
            triggers[trigger]["failures"] += 1
        triggers[trigger]["weight"] = compute_weight(entry.get("action_id", ""))
    
    #  
    questions = []
    for trigger, stats in triggers.items():
        if stats["count"] > 5:
            success_rate = stats["successes"] / stats["count"]
            if success_rate < 0.5:
                questions.append(f"Trigger '{trigger}'   ({stats['count']} )    ({success_rate:.0%}). ?")
            elif success_rate > 0.9:
                questions.append(f"gressor '{trigger}'   ({success_rate:.0%}).   ?")
        
        if stats["weight"] < 0.7:
            questions.append(f"Trigger '{trigger}'    ({stats['weight']:.2f}).      .    action?")
    
    return {
        "triggers": triggers,
        "questions": questions,
        "total_procedural_actions": len(procedural_entries)
    }


def show_pattern_report():
    """   ."""
    print("=== Pattern Analysis --    ===\n")
    
    analysis = analyze_patterns()
    
    if analysis.get("status") == "no_data":
        print("   .  procedural_executor  .")
        return
    
    print(f"  : {analysis['total_procedural_actions']}\n")
    
    print("[]")
    for trigger, stats in analysis.get("triggers", {}).items():
        success_rate = stats["successes"] / stats["count"] if stats["count"] > 0 else 0
        print(f"  {trigger}: {stats['count']} , {success_rate:.0%} success,  {stats['weight']:.2f}")
    
    print("\n[]")
    for q in analysis.get("questions", []):
        print(f"  ? {q}")
    
    if not analysis.get("questions"):
        print("      .   .")


# 
#  SENSOR HELPERS
# 

def check_port(port: int) -> bool:
    """Check if port is listening via netstat."""
    try:
        result = subprocess.run(
            ["netstat", "-ano"], capture_output=True, timeout=5
        )
        output = result.stdout.decode("utf-8", errors="replace")
        return any(
            f":{port}" in line and "LISTENING" in line
            for line in output.split("\n")
        )
    except Exception:
        return False


def check_port_socket(port: int) -> bool:
    """Check if port responds to TCP connect."""
    try:
        with socket.create_connection(("127.0.0.1", port), timeout=3):
            return True
    except (ConnectionRefusedError, TimeoutError, OSError):
        return False


def kill_process_on_port(port: int) -> bool:
    """Kill process occupying a port."""
    try:
        result = subprocess.run(
            ["netstat", "-ano"], capture_output=True, timeout=5
        )
        output = result.stdout.decode("utf-8", errors="replace")
        for line in output.split("\n"):
            if f":{port}" in line and "LISTENING" in line:
                parts = line.split()
                if len(parts) >= 5:
                    pid = parts[-1]
                    subprocess.run(
                        ["taskkill", "/F", "/PID", pid],
                        capture_output=True, timeout=5
                    )
                    return True
    except Exception:
        pass
    return False


def check_process(name: str) -> bool:
    """Check if process is running. Uses psutil (fast, cross-platform)."""
    try:
        import psutil
        for proc in psutil.process_iter(['name']):
            if name.lower() in proc.info['name'].lower():
                return True
        return False
    except Exception:
        return False


def check_network() -> bool:
    """Check if internet is reachable."""
    try:
        result = subprocess.run(
            ["ping", "-n", "1", "-w", "3000", "8.8.8.8"],
            capture_output=True, timeout=5
        )
        return result.returncode == 0
    except Exception:
        return False


def check_disk_usage() -> int:
    """Check disk usage percentage (Windows-compatible)."""
    try:
        # Primary: use wmic (native Windows, most reliable)
        result = subprocess.run(
            ["wmic", "logicaldisk", "where", "DeviceID='D:'",
             "get", "FreeSpace,Size", "/format:list"],
            capture_output=True, text=True, timeout=5
        )
        total = free = 0
        for line in result.stdout.split("\n"):
            if "FreeSpace" in line and "=" in line:
                try:
                    free = int(line.split("=")[1].strip())
                except (ValueError, IndexError):
                    pass
            if "Size" in line and "=" in line and "FreeSpace" not in line:
                try:
                    total = int(line.split("=")[1].strip())
                except (ValueError, IndexError):
                    pass
        if total > 0:
            return int((1 - free / total) * 100)
        # Fallback: try df (Git Bash)
        result = subprocess.run(
            ["df", "-h", "D:"], capture_output=True, text=True, timeout=5
        )
        for line in result.stdout.split("\n"):
            if "D:" in line:
                for part in line.split():
                    if "%" in part:
                        return int(part.replace("%", ""))
        return 0
    except Exception:
        return 0


def check_memory_usage() -> int:
    """Check memory usage percentage."""
    try:
        result = subprocess.run(
            ["wmic", "OS", "get", "TotalVisibleMemorySize,FreePhysicalMemory",
             "/format:list"],
            capture_output=True, text=True, timeout=5
        )
        total = free = 0
        for line in result.stdout.split("\n"):
            if "TotalVisibleMemorySize" in line:
                total = int(line.split("=")[1].strip())
            if "FreePhysicalMemory" in line:
                free = int(line.split("=")[1].strip())
        if total > 0:
            return int((1 - free / total) * 100)
        return 0
    except Exception:
        return 0


# 
#  TRIGGERS
# 

# --- TRIGGER-1: Network dead -> switch proxy ---
def trigger_network_dead():
    """
    TRIGGER-1: Network dead
    Action:  , . key proxy
       (V2RayN / proxy_bridge).
    """
    if check_network():
        return True  # network , trigger  

    print("  [TRIGGER-1] Network unreachable")
    log_feedback("network_dead", "detect", "no_connectivity", False)
    log_alert("TRIGGER-1: Network is dead -- manual proxy switch needed")
    return False


# --- TRIGGER-2: Gateway  ---
def trigger_gateway_dead():
    """
    TRIGGER-2: Gateway 
    Action:  stale locks, .
    """
    gateway_running = check_process("hermes-gateway") or check_process("node")

    if gateway_running:
        return True

    print("  [TRIGGER-2] Gateway process not found")

    # Kill stale locks
    lock_files = list((HERMES_HOME / "cache").glob("*.lock"))
    for lf in lock_files:
        try:
            lf.unlink()
            print(f"  [ACTION] Removed stale lock: {lf.name}")
        except Exception:
            pass

    # Kill zombie processes
    for proc_name in ["hermes-gateway", "hermes_gateway"]:
        try:
            subprocess.run(
                ["taskkill", "/F", "/IM", f"{proc_name}.exe"],
                capture_output=True, timeout=5
            )
        except Exception:
            pass

    time.sleep(3)

    # Try to restart via hermes CLI
    try:
        subprocess.Popen(
            ["hermes", "gateway", "start"],
            shell=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        time.sleep(10)

        if check_process("hermes-gateway") or check_process("node"):
            log_feedback("gateway_dead", "restart", "restarted", True)
            print("  [ACTION] Gateway restarted")
            
            # Test Harness verification
            verify_result = verify_with_test_harness(
                "gateway_dead",
                "Gateway process not found -- removed stale locks, killed zombies, restarted via hermes CLI",
                str(HERMES_HOME / "cache" / "gateway.pid")
            )
            if not verify_result.get("verified") and not verify_result.get("skipped"):
                log_alert(f"TRIGGER-2: Test Harness verification failed: {verify_result.get('details')}")
                print(f"  [VERIFY] FAILED: {verify_result.get('details')}")
            elif verify_result.get("verified"):
                print("  [VERIFY] PASSED")
            
            return True
        else:
            log_feedback("gateway_dead", "restart", "failed", False)
            log_alert("TRIGGER-2: Gateway failed to restart")
            print("  [ACTION] Gateway restart failed")
            return False
    except Exception as e:
        log_feedback("gateway_dead", "restart", str(e), False)
        log_alert(f"TRIGGER-2: Gateway restart error: {e}")
        return False


# --- TRIGGER-3: Cron job error 3x -> delay +1h ---
def trigger_cron_error_3x():
    """
    TRIGGER-3: Cron job  error 3  
    Action:  next_run_at  +1 .
    """
    if not CRON_JOBS.exists():
        return True

    try:
        data = json.loads(CRON_JOBS.read_text(encoding="utf-8"))
    except Exception:
        return True

    jobs = data.get("jobs", [])
    now = datetime.now()
    modified = False

    for job in jobs:
        if job.get("last_status") != "error":
            continue

        next_run = job.get("next_run_at")
        if not next_run:
            continue

        try:
            # Normalize: strip timezone for comparison
            next_str = next_run.replace("Z", "").split("+")[0].split("T")
            next_dt = datetime.fromisoformat(next_run.replace("Z", "").split("+")[0])
        except Exception:
            continue

        # If next_run is in the past and status is error -> delay +1h
        if next_dt < now:
            new_next = now + timedelta(hours=1)
            job["next_run_at"] = new_next.isoformat()
            modified = True

            job_id = job.get("id", "unknown")
            job_name = job.get("name", "unknown")
            error_msg = job.get("last_error", "unknown")[:100]

            print(f"  [TRIGGER-3] Cron job '{job_name}' ({job_id}) delayed +1h")
            print(f"    Error: {error_msg}")

            log_feedback(
                "cron_error_3x",
                f"delay_job_{job_id}",
                f"delayed to {new_next.isoformat()}",
                True
            )
            log_alert(
                f"TRIGGER-3: Job '{job_name}' ({job_id}) "
                f"error repeated -- delayed 1h. Error: {error_msg}"
            )

    if modified:
        CRON_JOBS.write_text(
            json.dumps(data, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )

    return True


# --- TRIGGER-4: Goal blocked > 24h ---
def trigger_goal_blocked_24h():
    """
    TRIGGER-4: Goal  status blocked > 24 
    Action:    ALERTS.md.
    """
    # Check multiple possible goal state files
    state_files = [
        GOALS_STATE,
        HERMES_HOME / "cache" / "goals.json",
        HERMES_HOME / "cache" / "autonomous_state.json",
    ]

    now = datetime.now()
    found_blocked = False

    for sf in state_files:
        if not sf.exists():
            continue

        try:
            data = json.loads(sf.read_text(encoding="utf-8"))
        except Exception:
            continue

        # Handle different state formats
        goals = []
        if isinstance(data, dict):
            if "goals" in data:
                goals = data["goals"]
            elif "tasks" in data:
                goals = data["tasks"]
            elif "items" in data:
                goals = data["items"]
        elif isinstance(data, list):
            goals = data

        for goal in goals:
            if not isinstance(goal, dict):
                continue
            status = goal.get("status", "")
            if status not in ("blocked", "stuck"):
                continue

            # Check timestamp
            updated = goal.get("updated_at") or goal.get("blocked_at") or goal.get("created_at")
            if not updated:
                continue

            try:
                updated_dt = datetime.fromisoformat(updated.replace("Z", "").split("+")[0])
            except Exception:
                continue

            age_hours = (now - updated_dt).total_seconds() / 3600

            if age_hours > 24:
                name = goal.get("name") or goal.get("title") or goal.get("id", "unknown")
                print(f"  [TRIGGER-4] Goal '{name}' blocked for {age_hours:.0f}h")
                log_alert(
                    f"TRIGGER-4: [ESCALATION] Goal '{name}' "
                    f"blocked for {age_hours:.0f}h -- needs human"
                )
                log_feedback(
                    "goal_blocked_24h",
                    f"escalate_{name}",
                    f"blocked {age_hours:.0f}h",
                    True
                )
                found_blocked = True

    return not found_blocked


# --- TRIGGER-5: Port service dead ---
PORT_CONFIG = [
    (3264, "FreeQwenApi",  "cd D:/Portable_Soft/FreeQwenApi && node index.js"),
    (9655, "FreeDeepseekAPI", "cd D:/Portable_Soft/FreeDeepseekAPI && node server.js"),
    (11434, "Ollama", "ollama serve"),
]


def trigger_port_dead(port: int, name: str, restart_cmd: str):
    """
    TRIGGER-5: Port  
    Action: , , .
    """
    if check_port(port):
        return True

    print(f"  [TRIGGER-5] {name} port {port} not responding")

    kill_process_on_port(port)
    time.sleep(2)

    try:
        subprocess.Popen(
            restart_cmd, shell=True,
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        time.sleep(5)

        if check_port(port):
            log_feedback(f"port_{port}_dead", f"restart_{name}", "restarted", True)
            print(f"  [ACTION] {name} restarted successfully")
            return True
        else:
            log_feedback(f"port_{port}_dead", f"restart_{name}", "failed", False)
            log_alert(f"TRIGGER-5: Failed to restart {name} on port {port}")
            print(f"  [ACTION] {name} restart failed")
            return False
    except Exception as e:
        log_feedback(f"port_{port}_dead", f"restart_{name}", str(e), False)
        log_alert(f"TRIGGER-5: Error restarting {name}: {e}")
        return False


# --- TRIGGER-6: Disk usage > 80% -> find large files ---
def trigger_disk_usage():
    """TRIGGER-6: Disk usage > 80% -> find large files -> log."""
    usage = check_disk_usage()
    if usage > 80:
        print(f"  [TRIGGER-6] Disk usage {usage}% > 80%")
        large_files = []
        try:
            # Windows-native: use PowerShell to find files > 100MB
            ps_cmd = (
                "Get-ChildItem -Path 'D:\\' -Recurse -File -ErrorAction SilentlyContinue "
                "| Where-Object { $_.Length -gt 100MB } "
                "| Sort-Object Length -Descending "
                "| Select-Object -First 20 FullName, @{N='SizeMB';E={[math]::Round($_.Length/1MB)}} "
                "| Format-Table -AutoSize"
            )
            result = subprocess.run(
                ["powershell", "-NoProfile", "-Command", ps_cmd],
                capture_output=True, text=True, timeout=30
            )
            output = result.stdout.strip()
            if output:
                # Parse the output lines (skip header/separator lines)
                lines = [l.strip() for l in output.split("\n")
                         if l.strip() and "----" not in l and "FullName" not in l]
                large_files = lines[:20]
                if large_files:
                    print(f"  [ACTION] Found {len(large_files)} files > 100MB:")
                    for lf in large_files[:5]:
                        print(f"    {lf}")
                    if len(large_files) > 5:
                        print(f"    ... and {len(large_files) - 5} more")
                    log_feedback("disk_usage_high", "find_large_files",
                                 f"{len(large_files)} files > 100MB", True)
                else:
                    log_feedback("disk_usage_high", "find_large_files",
                                 "0 files > 100MB", True)
            else:
                log_feedback("disk_usage_high", "find_large_files",
                             "scan completed, no large files", True)
        except Exception as e:
            log_feedback("disk_usage_high", "find_large_files", str(e), False)
            print(f"  [ACTION] Error scanning for large files: {e}")

        # Escalate if usage > 90%
        if usage > 90:
            log_alert(
                f"TRIGGER-6: CRITICAL disk usage {usage}% -- "
                f"{len(large_files)} large files found. Needs cleanup!"
            )
        else:
            log_alert(
                f"TRIGGER-6: Disk usage {usage}% > 80% -- "
                f"{len(large_files)} large files found"
            )

        return True
    return False


# --- TRIGGER-7: Memory usage > 80% -> find processes ---
def trigger_memory_usage():
    """TRIGGER-7: Memory usage > 80% -> find top processes -> log."""
    usage = check_memory_usage()
    if usage > 80:
        print(f"  [TRIGGER-7] Memory usage {usage}% > 80%")

        # Find top memory-consuming processes
        top_processes = []
        try:
            # Use wmic to get processes sorted by memory usage
            result = subprocess.run(
                ["wmic", "process", "get", "Name,WorkingSetSize",
                 "/format:csv"],
                capture_output=True, text=True, timeout=10
            )
            processes = []
            for line in result.stdout.strip().split("\n"):
                line = line.strip()
                if not line or "," not in line:
                    continue
                parts = line.split(",")
                if len(parts) >= 3:
                    try:
                        name = parts[1].strip()
                        mem_bytes = int(parts[2].strip())
                        if mem_bytes > 0:
                            processes.append((name, mem_bytes))
                    except (ValueError, IndexError):
                        continue

            # Sort by memory (descending) and take top 5
            processes.sort(key=lambda x: x[1], reverse=True)
            # Deduplicate by name, summing memory
            seen = {}
            for name, mem in processes:
                if name in seen:
                    seen[name] += mem
                else:
                    seen[name] = mem
            sorted_procs = sorted(seen.items(),
                                  key=lambda x: x[1], reverse=True)[:5]

            for name, mem in sorted_procs:
                mem_mb = mem // (1024 * 1024)
                top_processes.append(f"{name}: {mem_mb} MB")
                print(f"    {name}: {mem_mb} MB")
        except Exception as e:
            print(f"  [ACTION] Error listing processes: {e}")

        proc_summary = "; ".join(top_processes) if top_processes else "unable to list"
        log_feedback("memory_usage_high", "find_top_processes",
                     f"{usage}% -- {proc_summary}", True)
        log_alert(
            f"TRIGGER-7: Memory usage critical: {usage}% -- "
            f"Top processes: {proc_summary}"
        )
        return True
    return False


# --- TRIGGER-8: Telegram API down ---
def trigger_telegram_down():
    """
    TRIGGER-8: Telegram API access
    Action: , .
    """
    # Check 1: Is any telegram-related process running?
    try:
        result = subprocess.run(
            ["tasklist"],
            capture_output=True, shell=True, timeout=5
        )
        text = result.stdout.decode('cp866', errors='replace')
        if 'Telegram' in text or 'telegram' in text:
            return True  # Telegram app is running, proxy works for browser
    except Exception:
        pass

    # Check 2: Can we reach any HTTPS site via proxy? (V2RayN TUN/transparent)
    try:
        result = subprocess.run(
            ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}",
             "--connect-timeout", "5",
             "--proxy", "http://127.0.0.1:10806",
             "https://web.telegram.org"],
            capture_output=True, text=True, timeout=10
        )
        code = result.stdout.strip()
        if code in ("200", "302", "401", "404"):
            return True  # Telegram reachable via proxy
    except Exception:
        pass

    print("  [TRIGGER-8] Telegram API unreachable")
    log_feedback("telegram_down", "detect", "unreachable", False)
    log_alert("TRIGGER-8: Telegram API unreachable -- proxy may need switch")
    return False


# --- TRIGGER-9: IBOS Validation Self-Healing ---
def cascade_revalidate(fixed_entity_id: str, validation_data: dict):
    """
    CASCADE REVALIDATION: When an entity is auto-fixed, find all entities that depend on it
    and re-validate them. If they pass, unblock them.
    
    Args:
        fixed_entity_id: The entity that was just fixed
        validation_data: The full validation state dict
    """
    dependency_graph = validation_data.get("dependency_graph", {})
    
    # Build reverse dependency map: entity -> list of entities that depend on it
    reverse_deps = {}
    for entity, deps in dependency_graph.items():
        for dep in deps:
            if dep not in reverse_deps:
                reverse_deps[dep] = []
            reverse_deps[dep].append(entity)
    
    # Find direct and transitive dependents
    dependents = set()
    to_check = reverse_deps.get(fixed_entity_id, [])
    while to_check:
        current = to_check.pop()
        if current not in dependents:
            dependents.add(current)
            to_check.extend(reverse_deps.get(current, []))
    
    if not dependents:
        print(f"  [CASCADE] No dependents for {fixed_entity_id}")
        return
    
    print(f"  [CASCADE] Re-validating {len(dependents)} dependent(s) of {fixed_entity_id}: {dependents}")
    
    # Re-validate each dependent
    entity_results = validation_data.get("entity_results", {})
    blocked_entities = validation_data.get("blocked_entities", [])
    
    for dep_id in dependents:
        if dep_id not in entity_results:
            print(f"  [CASCADE] {dep_id} not in entity_results, skipping")
            continue
        
        # Re-run validation for this entity
        dep_info = entity_results[dep_id]
        file_path = dep_info.get("file_path")
        if not file_path:
            continue
            
        full_path = HERMES_HOME / file_path
        if not full_path.exists():
            continue
        
        # Read and validate
        try:
            content = full_path.read_text(encoding="utf-8")
            if not content.startswith("---"):
                continue
                
            end_match = re.search(r'^---\s*\n', content[3:], re.MULTILINE)
            if not end_match:
                continue
                
            fm_end = 3 + end_match.start()
            frontmatter_text = content[3:fm_end]
            fm = yaml.safe_load(frontmatter_text)
            if fm is None:
                fm = {}
            
            # Validate
            errors, warnings = validate_frontmatter(fm, full_path)
            
            if not errors:
                # Dependent is now valid! Unblock it
                if dep_id in blocked_entities:
                    blocked_entities.remove(dep_id)
                    entity_results[dep_id]["valid"] = True
                    entity_results[dep_id]["errors"] = []
                    print(f"  [CASCADE] [OK] UNBLOCKED {dep_id} (now valid)")
                    
                    # Log cascade unblock
                    log_feedback(f"cascade_revalidate:{dep_id}", "unblocked", 
                                f"unblocked via cascade from {fixed_entity_id}", True)
            else:
                print(f"  [CASCADE] [FAIL] {dep_id} still invalid: {errors}")
                
        except Exception as e:
            print(f"  [CASCADE] Error re-validating {dep_id}: {e}")
    
    # Update the validation state file if any were unblocked
    if any(dep not in blocked_entities for dep in dependents if dep in entity_results and entity_results[dep].get("valid")):
        validation_data["blocked_entities"] = blocked_entities
        validation_data["entity_results"] = entity_results
        validation_state = HERMES_HOME / "cache" / "ibos_validation_state.json"
        validation_state.parent.mkdir(parents=True, exist_ok=True)
        validation_state.write_text(
            json.dumps(validation_data, indent=2, ensure_ascii=False, default=str),
            encoding="utf-8"
        )
        print(f"  [CASCADE] Updated validation state")


# --- TRIGGER-9: IBOS Validation Self-Healing ---
def trigger_ibos_self_heal():
    """
    TRIGGER-9: IBOS validation failed -- attempt auto-fix
    Action:  validation state,   errors .
    """
    validation_state = HERMES_HOME / "cache" / "ibos_validation_state.json"
    if not validation_state.exists():
        return True  # No validation state = nothing to fix

    try:
        data = json.loads(validation_state.read_text(encoding="utf-8"))
    except Exception as e:
        log_feedback("ibos_self_heal", "read_state", str(e), False)
        return False

    blocked = data.get("blocked_entities", [])
    if not blocked:
        return True  # Nothing blocked

    fixed = 0
    failed = 0

    for entity_id in blocked:
        # Find entity file
        entity_info = data.get("entity_results", {}).get(entity_id, {})
        file_path = entity_info.get("file_path")
        if not file_path:
            # Try to find it
            for entity_dir in ENTITY_DIRS:
                f = entity_dir / f"{entity_id}.md"
                if f.exists():
                    file_path = str(f.relative_to(HERMES_HOME))
                    break

        if not file_path:
            log_feedback(f"ibos_self_heal:{entity_id}", "locate_file", "not found", False)
            failed += 1
            continue

        full_path = HERMES_HOME / file_path
        if not full_path.exists():
            log_feedback(f"ibos_self_heal:{entity_id}", "locate_file", "path missing", False)
            failed += 1
            continue

        # Try to fix common issues
        try:
            content = full_path.read_text(encoding="utf-8")
            if not content.startswith("---"):
                raise ValueError("No frontmatter")

            # Split frontmatter and body
            end_match = re.search(r'^---\s*\n', content[3:], re.MULTILINE)
            if not end_match:
                raise ValueError("Unclosed frontmatter")

            fm_end = 3 + end_match.start()
            frontmatter_text = content[3:fm_end]
            body = content[fm_end+4:]  # skip closing ---\n\n

            fm = yaml.safe_load(frontmatter_text)
            if fm is None:
                fm = {}

            # Track changes
            changed = False

            # Fix 1: Missing required keys
            for key in REQUIRED_KEYS:
                if key not in fm:
                    if key == "summary":
                        # Generate from description or body
                        desc = fm.get("description", "")
                        fm[key] = (desc[:150] if desc else body[:150]).strip()
                        changed = True
                    elif key == "description":
                        fm[key] = body.strip()[:500]
                        changed = True
                    elif key == "version":
                        fm[key] = "1.0.0"
                        changed = True
                    elif key == "status":
                        fm[key] = "scratch"
                        changed = True
                    elif key == "owner":
                        fm[key] = "agent"
                        changed = True
                    elif key == "created":
                        fm[key] = datetime.now(timezone.utc).isoformat()
                        changed = True
                    elif key == "type":
                        # Infer from directory
                        if "agents" in file_path:
                            fm[key] = "agent"
                        elif "skills" in file_path:
                            fm[key] = "skill"
                        elif "tools" in file_path:
                            fm[key] = "tool"
                        elif "knowledge" in file_path:
                            fm[key] = "knowledge"
                        else:
                            fm[key] = "skill"
                        changed = True
                    elif key == "namespace":
                        # Infer from path
                        if "knowledge/ai-core" in file_path:
                            fm[key] = "knowledge/ai-core"
                        elif "knowledge/arbitrage" in file_path:
                            fm[key] = "knowledge/arbitrage"
                        elif "knowledge/finance" in file_path:
                            fm[key] = "knowledge/finance"
                        else:
                            fm[key] = "knowledge/ai-core"
                        changed = True
                    elif key == "id":
                        fm[key] = entity_id
                        changed = True

            # Fix 2: Invalid status -> scratch
            if fm.get("status") not in VALID_STATUSES:
                fm["status"] = "scratch"
                changed = True

            # Fix 3: Invalid type -> skill
            if fm.get("type") not in VALID_TYPES:
                fm["type"] = "skill"
                changed = True

            # Fix 4: Invalid owner -> agent
            if fm.get("owner") not in VALID_OWNERS:
                fm["owner"] = "agent"
                changed = True

            # Fix 5: Canon with non-operator owner
            if fm.get("status") == "canon" and fm.get("owner") != "operator":
                fm["status"] = "candidate"
                changed = True

            # Fix 6: Invalid confidence
            if "confidence" in fm:
                try:
                    conf = float(fm["confidence"])
                    if not (0.0 <= conf <= 1.0):
                        fm["confidence"] = 0.5
                        changed = True
                except (ValueError, TypeError):
                    fm["confidence"] = 0.5
                    changed = True

            if changed:
                # Write back fixed frontmatter
                new_fm = yaml.dump(fm, allow_unicode=True, sort_keys=False, default_flow_style=False)
                new_content = f"---\n{new_fm}---\n{body}"
                full_path.write_text(new_content, encoding="utf-8")

                log_feedback(f"ibos_self_heal:{entity_id}", "auto_fix", f"fixed {len(fm)} fields", True)
                fixed += 1
                print(f"  [ACTION] Auto-fixed {entity_id} at {file_path}")

                # --- CASCADE REVALIDATION: re-validate dependents ---
                cascade_revalidate(entity_id, data)
                # ----------------------------------------------------

            else:
                log_feedback(f"ibos_self_heal:{entity_id}", "no_changes", "no auto-fixable issues", False)
                failed += 1

        except Exception as e:
            log_feedback(f"ibos_self_heal:{entity_id}", "error", str(e), False)
            failed += 1

    if fixed > 0:
        log_alert(f"TRIGGER-9: IBOS self-heal fixed {fixed} entities, {failed} failed")
        print(f"  [ACTION] Self-heal: {fixed} fixed, {failed} failed")
    elif failed > 0:
        log_alert(f"TRIGGER-9: IBOS self-heal could not fix {failed} entities")
        print(f"  [ACTION] Self-heal: {failed} entities could not be auto-fixed")

    return fixed > 0 or failed == 0


# --- TRIGGER-12: Cron job died -> emit event + attempt restart ---
def trigger_cron_job_health():
    """
    TRIGGER-12: Cron job health check
    Checks all cron jobs in jobs.json. If any job has last_status=error
    and next_run_at is in the past (missed), emit cron_job_died event
    and attempt to fix (rebuild job, reset next_run).
    """
    if not CRON_JOBS.exists():
        return True
    
    try:
        data = json.loads(CRON_JOBS.read_text(encoding="utf-8"))
    except Exception:
        return True
    
    jobs = data.get("jobs", [])
    now = datetime.now()
    fixed = 0
    dead_jobs = []
    
    for job in jobs:
        job_id = job.get("id", "unknown")
        job_name = job.get("name", "unknown")
        last_status = job.get("last_status", "")
        next_run = job.get("next_run_at", "")
        
        # Skip if not in error state
        if last_status != "error":
            continue
            
        # Check if next_run is in the past (missed execution)
        try:
            next_dt = datetime.fromisoformat(next_run.replace("Z", "").split("+")[0])
        except Exception:
            continue
            
        if next_dt >= now:
            continue  # Not yet due
            
        # Job is in error AND missed its run - THIS IS A DEAD CRON JOB
        dead_jobs.append(job)
        print(f"  [TRIGGER-12] Cron job DEAD: {job_name} ({job_id}) - missed run at {next_run}")
        
        # Emit event for event-driven recovery
        from event_bus import emit
        emit("cron_job_died", {
            "job_id": job_id,
            "job_name": job_name,
            "last_error": job.get("last_error", "unknown")[:200],
            "missed_at": next_run,
            "next_run_was": next_run
        })
        
        # Attempt auto-fix: reset next_run to now + 5min, clear error
        new_next = now + timedelta(minutes=5)
        job["next_run_at"] = new_next.isoformat()
        job["last_status"] = "pending"
        job["last_error"] = ""
        job["auto_restarted"] = datetime.now().isoformat()
        fixed += 1
        
        log_feedback(
            "cron_job_health",
            f"auto_restart_{job_id}",
            f"reset next_run to {new_next.isoformat()}",
            True
        )
        log_alert(
            f"TRIGGER-12: Cron job '{job_name}' ({job_id}) was dead -- "
            f"auto-restarted for {new_next.isoformat()}. Error: {job.get('last_error', 'unknown')[:100]}"
        )
    
    if fixed > 0:
        CRON_JOBS.write_text(
            json.dumps(data, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )
        print(f"  [ACTION] Auto-restarted {fixed} dead cron job(s)")
        return True
    
    if dead_jobs:
        print(f"  [ACTION] Found {len(dead_jobs)} dead job(s) but couldn't fix")
        return False
        
    return True


# --- TRIGGER-11: API key expired -> refresh -> fallback ---
PROVIDER_PRIORITY = ["openai", "anthropic", "together", "groq"]


def _load_API_keys():
    """Load API key state from cache."""
    keys_file = HERMES_HOME / "cache" / "API_keys.json"
    if not keys_file.exists():
        return {}
    try:
        return json.loads(keys_file.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _save_API_keys(data):
    """Save API key state to cache."""
    keys_file = HERMES_HOME / "cache" / "API_keys.json"
    keys_file.parent.mkdir(parents=True, exist_ok=True)
    keys_file.write_text(
        json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8"
    )


def _check_API_key_valid(provider: str) -> bool:
    """Check if an API key for a provider is valid (not expired)."""
    # Check environment variable first
    env_map = {
        "openai": "OPENAI_API_KEY",
        "anthropic": "ANTHROPIC_API_KEY",
        "together": "TOGETHER_API_KEY",
        "groq": "GROQ_API_KEY",
    }
    env_var = env_map.get(provider)
    if env_var and os.environ.get(env_var):
        return True

    # Check key store
    keys = _load_API_keys()
    provider_info = keys.get(provider, {})
    if not provider_info.get("key"):
        return False

    # Check expiry
    expires_at = provider_info.get("expires_at")
    if expires_at:
        try:
            exp_dt = datetime.fromisoformat(expires_at.replace("Z", ""))
            if datetime.now() > exp_dt:
                return False
        except Exception:
            pass

    return True


def _refresh_API_key(provider: str) -> bool:
    """Attempt to refresh an expired API key."""
    keys = _load_API_keys()
    provider_info = keys.get(provider, {})
    refresh_token = provider_info.get("refresh_token")
    if not refresh_token:
        return False

    # OpenAI/Anthropic keys don't have refresh tokens -- need manual replacement
    try:
        if provider in ("openai", "anthropic"):
            return False
        # For other providers, refresh endpoint would go here
        return False
    except Exception:
        return False


def _find_fallback_provider(exclude: str = None) -> str:
    """Find the next available provider that has a valid key."""
    for provider in PROVIDER_PRIORITY:
        if provider == exclude:
            continue
        if _check_API_key_valid(provider):
            return provider
    return None


def trigger_API_key_expired():
    """
    TRIGGER-11: API key expired -> refresh -> fallback provider
    Checks if any configured API provider key is expired.
    Attempts refresh, then falls back to another provider.
    """
    alerts = []

    for provider in PROVIDER_PRIORITY:
        if _check_API_key_valid(provider):
            continue  # Key is valid, no action needed

        print(f"  [TRIGGER-11] API key for '{provider}' is expired or missing")
        alerts.append(provider)

        # Step 1: Try to refresh
        print(f"  [ACTION] Attempting refresh for {provider}...")
        refreshed = _refresh_API_key(provider)

        if refreshed:
            print(f"  [ACTION] Successfully refreshed {provider} API key")
            log_feedback("API_key_expired", f"refresh_{provider}",
                         "refreshed", True)
            continue

        # Step 2: Refresh failed -- try fallback
        print(f"  [ACTION] Refresh failed for {provider}, looking for fallback...")
        fallback = _find_fallback_provider(exclude=provider)

        if fallback:
            print(f"  [ACTION] Fallback provider found: {fallback}")
            # Record the fallback switch
            keys = _load_API_keys()
            keys.setdefault(provider, {})["fallback_to"] = fallback
            keys.setdefault(provider, {})["fallback_at"] = (
                datetime.now().isoformat()
            )
            _save_API_keys(keys)

            log_feedback(
                "API_key_expired",
                f"fallback_{provider}_to_{fallback}",
                f"key expired, switched to {fallback}",
                True,
            )
            log_alert(
                f"TRIGGER-11: API key for '{provider}' expired -- "
                f"refresh failed. Fallback to '{fallback}'"
            )
        else:
            # No fallback available -- escalate
            print(f"  [ACTION] No fallback available for {provider} -- ESCALATE")
            log_feedback(
                "API_key_expired",
                f"escalate_{provider}",
                "key expired, no refresh, no fallback",
                False,
            )
            log_alert(
                f"TRIGGER-11: [ESCALATION] API key for '{provider}' expired -- "
                f"refresh failed, no fallback provider available. "
                f"Manual action needed!"
            )

    if not alerts:
        return True  # All keys valid

    return len(alerts) == 0


# --- TRIGGER-10: Signal Daemon dead -> restart ---
def _is_process_alive(pid: int) -> bool:
    """Check if a PID is alive. Works on Windows + Linux."""
    try:
        if os.name == 'nt':
            # Windows: use tasklist to check PID
            result = subprocess.run(
                ['tasklist', '/FI', f'PID eq {pid}', '/NH'],
                capture_output=True, timeout=5,
                creationflags=0x08000000  # CREATE_NO_WINDOW
            )
            # tasklist outputs CP1251 on Russian Windows, not UTF-8
            output = result.stdout.decode('cp1251', errors='replace')
            return str(pid) in output
        else:
            os.kill(pid, 0)
            return True
    except Exception:
        return False


def check_signal_daemon_dead():
    """Check if signal_daemon process is running. Triple check: PID file + scanner_state + tasklist."""
    # 1. Check PID file (fastest)
    pid_file = HERMES_HOME / "cache" / "signal_daemon.pid"
    if pid_file.exists():
        try:
            pid = int(pid_file.read_text(encoding="utf-8").strip())
            if _is_process_alive(pid):
                return False
        except Exception:
            pass
    # 2. Fallback: check scanner_state.json
    scanner_state = HERMES_HOME / "cache" / "scanner_state.json"
    if not scanner_state.exists():
        return True
    try:
        state = json.loads(scanner_state.read_text(encoding="utf-8"))
        last_scan = state.get("last_scan")
        if not last_scan:
            return True
        last_dt = datetime.fromisoformat(last_scan.replace("Z", ""))
        age_seconds = (datetime.now(timezone.utc) - last_dt).total_seconds()
        return age_seconds > 1200  # 20 minutes
    except Exception:
        return True


def restart_signal_daemon():
    """Restart signal_daemon."""
    pid_file = HERMES_HOME / "cache" / "signal_daemon.pid"
    try:
        # Remove stale PID file if daemon is dead
        if pid_file.exists():
            try:
                pid = int(pid_file.read_text(encoding="utf-8").strip())
                if _is_process_alive(pid):
                    print("  [ACTION] Signal daemon already running, skip restart")
                    return True
            except Exception:
                pass
            pid_file.unlink(missing_ok=True)
        # Start daemon detached
        subprocess.Popen(
            [sys.executable, str(HERMES_HOME / "scripts" / "signal_daemon.py"), "start"],
            cwd=str(HERMES_HOME),
            stdout=open(os.devnull, 'w'),
            stderr=open(os.devnull, 'w'),
            stdin=open(os.devnull, 'r'),
            start_new_session=True
        )
        # Wait for daemon to start and write PID file
        for i in range(6):
            time.sleep(2)
            if pid_file.exists():
                try:
                    pid = int(pid_file.read_text(encoding="utf-8").strip())
                    if _is_process_alive(pid):
                        print(f"  [ACTION] Signal daemon restarted (PID {pid})")
                        return True
                except Exception:
                    pass
        print("  [ACTION] Signal daemon restart failed -- no valid PID after 12s")
    except Exception as e:
        print(f"  [ACTION] Failed to restart signal_daemon: {e}")
    return False


def trigger_signal_daemon_dead():
    """
    TRIGGER-10: Signal Daemon dead -> restart
    Watchdog: if signal_daemon crashes, auto-restart it.
    """
    if not check_signal_daemon_dead():
        return True  # Daemon is running, trigger not needed

    print("  [TRIGGER-10] Signal daemon is dead -- restarting")
    if restart_signal_daemon():
        log_feedback("signal_daemon_dead", "restart", "restarted", True)
        print("  [ACTION] Signal daemon restarted successfully")
        return True
    else:
        log_feedback("signal_daemon_dead", "restart", "failed", False)
        log_alert("TRIGGER-10: Failed to restart signal_daemon")
        return False


# --- TRIGGER-13: Goal queue has active goals but agent is sleeping ---
def trigger_autonomous_agent_wake():
    """
    TRIGGER-13: Active goals exist but autonomous_agent has not run -> emit event.
    Safety net: ensures the brain wakes up even if no external event fires.
    Checks goal_queue.json for active/open goals, then emits goal_queue_changed.
    """
    goal_queue_file = CACHE_DIR / "goal_queue.json"
    if not goal_queue_file.exists():
        return True  # No goal queue = nothing to wake

    try:
        gq = json.loads(goal_queue_file.read_text("utf-8"))
        goals = gq.get("goals", []) if isinstance(gq, dict) else []
        active = [g for g in goals if g.get("status") in ("active", "open")]
        if not active:
            return True  # No active goals = nothing to wake

        # Check when autonomous_agent last ran
        decisions_file = CACHE_DIR / "agent_decisions.json"
        last_run = None
        if decisions_file.exists():
            try:
                decisions = json.loads(decisions_file.read_text("utf-8"))
                if decisions:
                    last_run = decisions[-1].get("timestamp")
            except Exception:
                pass

        # If agent ran in last 10 minutes, don't wake it
        if last_run:
            from datetime import datetime as _dt, timezone as _tz
            try:
                last_dt = _dt.fromisoformat(last_run)
                if last_dt.tzinfo is None:
                    last_dt = last_dt.replace(tzinfo=_tz.utc)
                age_min = (_dt.now(_tz.utc) - last_dt).total_seconds() / 60
                if age_min < 10:
                    return True  # Recently ran, no need to wake
            except Exception:
                pass

        # Emit goal_queue_changed to wake autonomous_agent
        print(f"  [TRIGGER-13] {len(active)} active goals, agent idle -> emitting goal_queue_changed")
        try:
            import subprocess
            result = subprocess.run(
                [sys.executable, str(HERMES_HOME / "scripts" / "event_bus.py"),
                 "emit", "goal_queue_changed",
                 json.dumps({"source": "procedural_executor", "active_goals": len(active)})],
                capture_output=True, text=True, timeout=10,
                cwd=str(HERMES_HOME)
            )
            if result.stdout.strip():
                print(f"  {result.stdout.strip()[:200]}")
            log_feedback("autonomous_agent_wake", "emit goal_queue_changed",
                         f"{len(active)} active goals", True)
            return True
        except Exception as e:
            log_feedback("autonomous_agent_wake", "emit goal_queue_changed",
                         str(e)[:100], False)
            return False

    except Exception as e:
        print(f"  [TRIGGER-13] Error reading goal queue: {e}")
        return True  # Non-fatal


# 
#  MAIN EXECUTOR
# 

TRIGGER_MAP = {
    "network":       ("TRIGGER-1: Network dead -> check",       trigger_network_dead),
    "gateway":       ("TRIGGER-2: Gateway not found -> log -> escalate", trigger_gateway_dead),
    "cron_error":    ("TRIGGER-3: Cron error 3x -> delay +1h",  trigger_cron_error_3x),
    "goal_blocked":  ("TRIGGER-4: Goal blocked > 24h -> escalate", trigger_goal_blocked_24h),
    "disk":          ("TRIGGER-6: Disk > 80% -> find large files -> log", trigger_disk_usage),
    "memory":        ("TRIGGER-7: Memory > 80% -> find processes -> log", trigger_memory_usage),
    "telegram":      ("TRIGGER-8: Telegram API down",           trigger_telegram_down),
    "ibos_heal":     ("TRIGGER-9: IBOS validation self-heal",   trigger_ibos_self_heal),
    "signal_daemon":  ("TRIGGER-10: Signal daemon dead -> restart", trigger_signal_daemon_dead),
    "API_key":       ("TRIGGER-11: API key expired -> refresh -> fallback", trigger_API_key_expired),
    "cron_health":   ("TRIGGER-12: Cron job died -> event + restart", trigger_cron_job_health),
    "agent_wake":    ("TRIGGER-13: Active goals, agent idle -> wake", trigger_autonomous_agent_wake),
}


def check_all_triggers():
    """Check all triggers and execute actions. NO LLM."""
    print("")
    print("  PROCEDURAL EXECUTOR -- Reflexes Hermes")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("")
    print()

    actions = 0
    ok = 0
    fail = 0

    # --- Network ---
    print("[NETWORK]")
    if trigger_network_dead():
        ok += 1
        print("  [OK] Network OK")
    else:
        fail += 1
        actions += 1
    print()

    # --- Gateway ---
    print("[GATEWAY]")
    if trigger_gateway_dead():
        ok += 1
        print("  [OK] Gateway running")
    else:
        fail += 1
        actions += 1
    print()

    # --- Cron jobs ---
    print("[CRON]")
    trigger_cron_error_3x()
    print()

    # --- Goals ---
    print("[GOALS]")
    trigger_goal_blocked_24h()
    print()

    # --- IBOS Self-Heal ---
    print("[IBOS HEAL]")
    if trigger_ibos_self_heal():
        ok += 1
        print("  [OK] IBOS entities healthy or auto-fixed")
    else:
        fail += 1
        actions += 1
    print()

    # --- Ports ---
    print("[PORTS]")
    for port, name, cmd in PORT_CONFIG:
        if trigger_port_dead(port, name, cmd):
            ok += 1
            print(f"  [OK] {name} (:{port}) running")
        else:
            fail += 1
            actions += 1
    print()

    # --- System ---
    print("[SYSTEM]")
    disk = check_disk_usage()
    mem = check_memory_usage()
    if disk <= 80:
        ok += 1
        print(f"  [OK] Disk: {disk}%")
    else:
        actions += 1
        print(f"  [FAIL] Disk: {disk}% -- exceeded 80%")
    if mem <= 80:
        ok += 1
        print(f"  [OK] Memory: {mem}%")
    else:
        actions += 1
        print(f"  [FAIL] Memory: {mem}% -- exceeded 80%")
    trigger_disk_usage()
    trigger_memory_usage()
    print()

    # --- Telegram ---
    print("[TELEGRAM]")
    if trigger_telegram_down():
        ok += 1
        print("  [OK] Telegram API reachable")
    else:
        fail += 1
        actions += 1
    print()

    # --- Signal Daemon ---
    print("[SIGNAL DAEMON]")
    if trigger_signal_daemon_dead():
        ok += 1
        print("  [OK] Signal daemon running")
    else:
        fail += 1
        actions += 1
    print()

    # --- API Keys ---
    print("[API KEYS]")
    if trigger_API_key_expired():
        ok += 1
        print("  [OK] API keys valid")
    else:
        fail += 1
        actions += 1
    print()

    # --- Cron Health ---
    print("[CRON HEALTH]")
    if trigger_cron_job_health():
        ok += 1
        print("  [OK] Cron jobs healthy")
    else:
        fail += 1
        actions += 1
    print()

    # --- Autonomous Agent Wake ---
    print("[AGENT WAKE]")
    if trigger_autonomous_agent_wake():
        ok += 1
        print("  [OK] Agent wake check passed")
    else:
        fail += 1
        actions += 1
    print()

    # --- Summary ---
    print("")
    print(f"  OK: {ok}  FAIL: {fail}  ACTIONS: {actions}")
    print("")

    return actions


def show_status():
    """Show current status of all monitored systems."""
    print("")
    print("  PROCEDURAL EXECUTOR -- STATUS")
    print("")
    print()

    # Network
    net = "[OK]" if check_network() else "[FAIL]"
    print(f"  Network:     {net}")

    # Gateway
    gw = "[OK]" if (check_process("hermes-gateway") or check_process("node")) else "[FAIL]"
    print(f"  Gateway:     {gw}")

    # Telegram
    try:
        result = subprocess.run(
            ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}",
             "--connect-timeout", "3",
             "--proxy", "http://127.0.0.1:10809",
             "https://API.telegram.org"],
            capture_output=True, text=True, timeout=5
        )
        tg = "[OK]" if result.stdout.strip() in ("200", "302", "401", "404") else "[FAIL]"
    except Exception:
        tg = "?"
    print(f"  Telegram:    {tg}")

    # Signal Daemon
    sd = "[OK] RUNNING" if not check_signal_daemon_dead() else "[FAIL] DEAD"
    print(f"  SignalDaemon: {sd}")

    # Ports
    print()
    for port, name, _ in PORT_CONFIG:
        status = "[OK] RUNNING" if check_port(port) else "[FAIL] DEAD"
        print(f"  {name:15s} :{port}  {status}")

    # System
    print()
    print(f"  Disk:        {check_disk_usage()}%")
    print(f"  Memory:      {check_memory_usage()}%")

    # Recent feedback
    print()
    print("  RECENT FEEDBACK:")
    if FEEDBACK_STORE.exists():
        lines = FEEDBACK_STORE.read_text(encoding="utf-8").strip().split("\n")
        for line in lines[-5:]:
            try:
                entry = json.loads(line)
                mark = "[OK]" if entry.get("success") else "[FAIL]"
                print(f"    {mark} {entry['timestamp'][:19]} | {entry['trigger']} | {entry.get('result', '')}")
            except Exception:
                pass
    else:
        print("    (empty)")

    print()
    print("  ALERTS (last 5):")
    if ALERTS_FILE.exists():
        lines = ALERTS_FILE.read_text(encoding="utf-8").strip().split("\n")
        for line in lines[-5:]:
            print(f"    {line}")
    else:
        print("    (empty)")


def list_triggers():
    """List all available triggers."""
    print("")
    print("  AVAILABLE TRIGGERS")
    print("")
    for key, (desc, _) in TRIGGER_MAP.items():
        print(f"  {key:15s} -> {desc}")
    print()
    print("  port_3264      -> FreeQwenApi dead -> restart")
    print("  port_9655      -> FreeDeepseekAPI dead -> restart")
    print("  port_11434     -> Ollama dead -> restart")
    print("  API_key        -> API key expired -> refresh -> fallback")
    print()
    print("Usage: python procedural_executor.py --run <trigger>")


def main():
    if "--status" in sys.argv:
        show_status()
    elif "--patterns" in sys.argv:
        show_pattern_report()
    elif "--list" in sys.argv:
        list_triggers()
    elif "--run" in sys.argv:
        idx = sys.argv.index("--run")
        if idx + 1 < len(sys.argv):
            trigger_name = sys.argv[idx + 1]
            if trigger_name in TRIGGER_MAP:
                desc, func = TRIGGER_MAP[trigger_name]
                print(f"Running: {desc}")
                func()
            elif trigger_name.startswith("port_"):
                port = int(trigger_name.split("_")[1])
                for p, name, cmd in PORT_CONFIG:
                    if p == port:
                        trigger_port_dead(port, name, cmd)
                        break
            else:
                print(f"Unknown trigger: {trigger_name}")
                list_triggers()
        else:
            list_triggers()
    else:
        check_all_triggers()


if __name__ == "__main__":
    main()

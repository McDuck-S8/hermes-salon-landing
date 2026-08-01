#!/usr/bin/env python3
"""Qwen API Auto-Restarter - Monitors port 3264 and restarts Qwen on failure.

Windows-compatible replacement for systemd monitoring.

> Revisit: when qwen auto-restart logic, proxy recovery, or health checks change. Last touched: 2026-07-02.
Checks if Qwen API is responding on port 3264, restarts if crashed.
Can run as a cron job or continuous monitor.

Usage:
    python qwen_auto_restarter.py          # Single check
    python qwen_auto_restarter.py --loop   # Continuous monitoring
"""
import json
import logging
import os
import socket
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

HERMES_HOME = Path(os.environ.get("HERMES_HOME", "D:/Portable_Soft/hermes"))
LOG_FILE = HERMES_HOME / "logs" / "qwen_auto_restarter.log"
STATE_FILE = HERMES_HOME / "cache" / "qwen_restarter_state.json"

# Qwen API configuration
QWEN_HOST = "127.0.0.1"
QWEN_PORT = 3264
HEALTH_ENDPOINT = f"http://{QWEN_HOST}:{QWEN_PORT}/health"

# Thresholds
CONSECUTIVE_FAILURES_BEFORE_ALERT = 3
RESTART_DELAY_SECONDS = 5
CHECK_INTERVAL_SECONDS = 30

LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler(str(LOG_FILE), encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger("qwen-restarter")


def load_state() -> dict:
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return {}
    return {}


def save_state(state: dict) -> None:
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")


def check_port_open(host: str, port: int, timeout: float = 5.0) -> bool:
    """Check if a TCP port is open."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(timeout)
            result = sock.connect_ex((host, port))
            return result == 0
    except (socket.error, OSError):
        return False


def check_qwen_health() -> tuple[bool, str]:
    """Check if Qwen API is healthy by connecting to port 3264."""
    if not check_port_open(QWEN_HOST, QWEN_PORT, timeout=5.0):
        return False, "port 3264 not responding"
    return True, "port 3264 open"


def find_qwen_process() -> int | None:
    """Find Qwen-related process PID (node.exe on port 3264)."""
    try:
        result = subprocess.run(
            ["netstat", "-ano"],
            capture_output=True, text=True, timeout=10
        )
        for line in result.stdout.split("\n"):
            if f":{QWEN_PORT}" in line and "LISTENING" in line:
                parts = line.split()
                if parts:
                    pid = int(parts[-1])
                    if pid > 0:
                        return pid
    except (subprocess.TimeoutExpired, ValueError, OSError) as e:
        log.error("Failed to find Qwen process: %s", e)
    return None


def kill_process(pid: int) -> bool:
    """Kill a process by PID."""
    try:
        subprocess.run(
            ["taskkill", "/F", "/PID", str(pid)],
            capture_output=True, text=True, timeout=10
        )
        log.info("Killed process PID %d", pid)
        return True
    except (subprocess.TimeoutExpired, OSError) as e:
        log.error("Failed to kill PID %d: %s", pid, e)
        return False


def start_qwen() -> bool:
    """Start the Qwen API service."""
    # Look for common Qwen startup scripts
    possible_commands = [
        ["node", "server.js"],  # If there's a server.js
        ["python", "-m", "uvicorn", "main:app", "--host", QWEN_HOST, "--port", str(QWEN_PORT)],
        ["python", "main.py"],
    ]
    
    # Check if there's a qwen-specific directory or config
    qwen_dirs = list(HERMES_HOME.glob("**/qwen*server*"))
    qwen_configs = list(HERMES_HOME.glob("**/qwen*config*"))
    
    log.info("Starting Qwen API on port %d...", QWEN_PORT)
    
    # Try to start based on what we find
    for cmd in possible_commands:
        try:
            subprocess.Popen(
                cmd,
                cwd=str(HERMES_HOME),
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            log.info("Started Qwen with command: %s", " ".join(cmd))
            time.sleep(RESTART_DELAY_SECONDS)
            return True
        except (OSError, FileNotFoundError):
            continue
    
    log.warning("Could not auto-start Qwen - no startup command found")
    return False


def attempt_restart(state: dict) -> bool:
    """Attempt to restart the Qwen API."""
    pid = find_qwen_process()
    if pid:
        log.info("Found Qwen process PID %d, attempting restart...", pid)
        kill_process(pid)
        time.sleep(2)
    
    started = start_qwen()
    if started:
        # Verify it started
        time.sleep(3)
        healthy, _ = check_qwen_health()
        if healthy:
            log.info("Qwen API restarted successfully")
            state["consecutive_failures"] = 0
            state["last_restart"] = datetime.now(timezone.utc).isoformat()
            state["restart_count"] = state.get("restart_count", 0) + 1
            return True
        else:
            log.error("Qwen API failed to start after restart attempt")
            state["consecutive_failures"] = state.get("consecutive_failures", 0) + 1
            return False
    else:
        state["consecutive_failures"] = state.get("consecutive_failures", 0) + 1
        return False


def main():
    state = load_state()
    state["total_checks"] = state.get("total_checks", 0) + 1
    
    healthy, message = check_qwen_health()
    
    if healthy:
        state["consecutive_failures"] = 0
        state["last_ok"] = datetime.now(timezone.utc).isoformat()
        save_state(state)
        log.info("Qwen API healthy: %s (total checks: %d)", message, state["total_checks"])
        return
    
    # Qwen is down
    state["consecutive_failures"] = state.get("consecutive_failures", 0) + 1
    state["total_failures"] = state.get("total_failures", 0) + 1
    
    log.warning("Qwen API down: %s (failure #%d)", message, state["consecutive_failures"])
    
    # Attempt restart
    restart_ok = attempt_restart(state)
    save_state(state)
    
    # Alert after multiple consecutive failures
    if state["consecutive_failures"] >= CONSECUTIVE_FAILURES_BEFORE_ALERT:
        alert = (
            f"⚠️ Qwen API DOWN! {state['consecutive_failures']} consecutive failures.\n"
            f"Error: {message}\n"
            f"Last OK: {state.get('last_ok', 'never')}\n"
            f"Total restarts: {state.get('restart_count', 0)}\n"
            f"Restart {'succeeded' if restart_ok else 'FAILED'}"
        )
        print(alert)
        log.error(alert)


def monitor_loop():
    """Run continuous monitoring loop."""
    log.info("Starting Qwen API monitor loop (interval: %ds)", CHECK_INTERVAL_SECONDS)
    while True:
        try:
            main()
            time.sleep(CHECK_INTERVAL_SECONDS)
        except KeyboardInterrupt:
            log.info("Monitor loop interrupted by user")
            break
        except Exception as e:
            log.error("Unexpected error in monitor loop: %s", e)
            time.sleep(CHECK_INTERVAL_SECONDS)


if __name__ == "__main__":
    if "--loop" in sys.argv:
        monitor_loop()
    else:
        main()

#!/usr/bin/env python3
"""
Auto-Recovery System for Hermes Daemons.
Monitors all daemons, restarts on failure, enforces health, alerts on degradation.
"""

import os
import sys
import json
import time
import signal
import subprocess
import threading
import psutil
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field

HERMES_HOME = Path(os.environ.get("HERMES_HOME", "D:/Portable_Soft/hermes"))
CACHE_DIR = HERMES_HOME / "cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

PYTHON_EXE = sys.executable

# ─── Daemon Definitions ────────────────────────────────────────────────

@dataclass
class DaemonConfig:
    name: str
    script: str
    args: List[str]
    restart_policy: str = "always"  # always, on_failure, never
    health_check_interval: int = 30  # seconds
    max_restarts_per_hour: int = 10
    backoff: List[int] = field(default_factory=lambda: [5, 10, 30, 60, 300])
    health_check: Optional[Callable] = None
    pre_start_hook: Optional[Callable] = None
    post_crash_hook: Optional[Callable] = None


# ─── Built-in Health Checks ────────────────────────────────────────────

def check_signal_daemon_health() -> Dict[str, Any]:
    """Check signal_daemon: process alive + heartbeat fresh + scanner state."""
    pid_file = CACHE_DIR / "signal_daemon.pid"
    log_file = CACHE_DIR / "signal_daemon.log"
    state_file = CACHE_DIR / "scanner_state.json"
    
    result = {"alive": False, "heartbeat_age": None, "state_ok": False, "details": []}
    
    if pid_file.exists():
        try:
            pid = int(pid_file.read_text().strip())
            if psutil.pid_exists(pid):
                result["alive"] = True
                result["details"].append(f"PID {pid} alive")
            else:
                result["details"].append(f"PID {pid} dead")
        except Exception as e:
            result["details"].append(f"PID check failed: {e}")
    else:
        result["details"].append("No PID file")
    
    if log_file.exists():
        try:
            lines = log_file.read_text(encoding="utf-8").strip().splitlines()
            if lines:
                last = lines[-1]
                if last.startswith("["):
                    ts_str = last[1:20]
                    last_ts = datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
                    age = (datetime.now(timezone.utc) - last_ts).total_seconds()
                    result["heartbeat_age"] = age
                    result["details"].append(f"Heartbeat age: {age:.0f}s")
        except Exception as e:
            result["details"].append(f"Heartbeat parse failed: {e}")
    
    if state_file.exists():
        try:
            state = json.loads(state_file.read_text())
            if "backoff_interval" in state and "last_scan" in state:
                result["state_ok"] = True
                result["details"].append("Scanner state valid")
        except Exception as e:
            result["details"].append(f"Scanner state invalid: {e}")
    
    return result


def check_event_daemon_health() -> Dict[str, Any]:
    """Check event_daemon: process alive + heartbeat fresh."""
    pid_file = CACHE_DIR / "event_daemon.pid"
    log_file = CACHE_DIR / "event_daemon.log"
    
    result = {"alive": False, "heartbeat_age": None, "details": []}
    
    if pid_file.exists():
        try:
            pid = int(pid_file.read_text().strip())
            if psutil.pid_exists(pid):
                result["alive"] = True
                result["details"].append(f"PID {pid} alive")
            else:
                result["details"].append(f"PID {pid} dead")
        except Exception as e:
            result["details"].append(f"PID check failed: {e}")
    else:
        result["details"].append("No PID file")
    
    if log_file.exists():
        try:
            lines = log_file.read_text(encoding="utf-8").strip().splitlines()
            if lines:
                last = lines[-1]
                if last.startswith("["):
                    ts_str = last[1:20]
                    last_ts = datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
                    age = (datetime.now(timezone.utc) - last_ts).total_seconds()
                    result["heartbeat_age"] = age
                    result["details"].append(f"Heartbeat age: {age:.0f}s")
        except Exception as e:
            result["details"].append(f"Heartbeat parse failed: {e}")
    
    return result


def check_process_supervisor_health() -> Dict[str, Any]:
    """Check process_supervisor: process alive + state file fresh + daemons managed."""
    pid_file = CACHE_DIR / "process_supervisor.pid"
    state_file = CACHE_DIR / "supervisor_state.json"
    
    result = {"alive": False, "state_fresh": False, "managed_daemons": 0, "details": []}
    
    if pid_file.exists():
        try:
            pid = int(pid_file.read_text().strip())
            if psutil.pid_exists(pid):
                result["alive"] = True
                result["details"].append(f"Supervisor PID {pid} alive")
            else:
                result["details"].append(f"Supervisor PID {pid} dead")
        except Exception as e:
            result["details"].append(f"PID check failed: {e}")
    else:
        result["details"].append("No supervisor PID file")
    
    if state_file.exists():
        try:
            state = json.loads(state_file.read_text())
            daemons = state.get("daemons", {})
            result["managed_daemons"] = len(daemons)
            result["details"].append(f"Managing {len(daemons)} daemons")
            
            started = state.get("started_at")
            if started:
                start_ts = datetime.fromisoformat(started.replace("Z", "+00:00"))
                age = (datetime.now(timezone.utc) - start_ts).total_seconds()
                if age < 86400:  # 24h
                    result["state_fresh"] = True
        except Exception as e:
            result["details"].append(f"State parse failed: {e}")
    
    return result


# ─── Recovery Actions ──────────────────────────────────────────────────

def recover_signal_daemon() -> Dict[str, Any]:
    """Full recovery: stop, clear state, restart."""
    result = {"success": False, "actions": [], "error": None}
    
    try:
        pid_file = CACHE_DIR / "signal_daemon.pid"
        if pid_file.exists():
            pid = int(pid_file.read_text().strip())
            try:
                p = psutil.Process(pid)
                p.terminate()
                p.wait(timeout=5)
                result["actions"].append(f"Terminated PID {pid}")
            except:
                pass
        
        if pid_file.exists():
            pid_file.unlink()
            result["actions"].append("Cleared PID file")
        
        # Reset scanner state (preserve total_signals)
        state_file = CACHE_DIR / "scanner_state.json"
        if state_file.exists():
            state = json.loads(state_file.read_text())
            preserved = {"total_signals": state.get("total_signals", 0)}
            state = {**preserved, "backoff_interval": 60, "last_scan": None}
            state_file.write_text(json.dumps(state, indent=2))
            result["actions"].append("Reset scanner state (preserved total_signals)")
        
        # Start fresh with same approach as process_supervisor
        cmd = [PYTHON_EXE, str(HERMES_HOME / "scripts/signal_daemon.py"), "run"]
        subprocess.Popen(
            cmd, 
            cwd=str(HERMES_HOME), 
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        result["actions"].append("Started new signal_daemon process")
        result["success"] = True
        
    except Exception as e:
        result["error"] = str(e)
    
    return result


def recover_event_daemon() -> Dict[str, Any]:
    """Full recovery for event_daemon."""
    result = {"success": False, "actions": [], "error": None}
    
    try:
        pid_file = CACHE_DIR / "event_daemon.pid"
        if pid_file.exists():
            pid = int(pid_file.read_text().strip())
            try:
                p = psutil.Process(pid)
                p.terminate()
                p.wait(timeout=5)
                result["actions"].append(f"Terminated PID {pid}")
            except:
                pass
        
        if pid_file.exists():
            pid_file.unlink()
            result["actions"].append("Cleared PID file")
        
        cmd = [PYTHON_EXE, str(HERMES_HOME / "scripts/event_daemon.py"), "run"]
        subprocess.Popen(
            cmd, 
            cwd=str(HERMES_HOME), 
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        result["actions"].append("Started new event_daemon process")
        result["success"] = True
        
    except Exception as e:
        result["error"] = str(e)
    
    return result


def recover_process_supervisor() -> Dict[str, Any]:
    """Restart the entire supervisor (which restarts all daemons)."""
    result = {"success": False, "actions": [], "error": None}
    
    try:
        pid_file = CACHE_DIR / "process_supervisor.pid"
        if pid_file.exists():
            pid = int(pid_file.read_text().strip())
            try:
                p = psutil.Process(pid)
                p.terminate()
                p.wait(timeout=10)
                result["actions"].append(f"Terminated supervisor PID {pid}")
            except:
                pass
        
        if pid_file.exists():
            pid_file.unlink()
            result["actions"].append("Cleared supervisor PID file")
        
        cmd = [PYTHON_EXE, str(HERMES_HOME / "skills/devops/process-supervisor/scripts/process_supervisor.py"), "run"]
        proc = subprocess.Popen(
            cmd, 
            cwd=str(HERMES_HOME), 
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        # Write PID file for new supervisor
        pid_file.write_text(str(proc.pid))
        result["actions"].append(f"Started new process_supervisor (PID {proc.pid})")
        result["success"] = True
        
    except Exception as e:
        result["error"] = str(e)
    
    return result


# ─── Daemon Registry ───────────────────────────────────────────────────

DAEMON_REGISTRY: Dict[str, DaemonConfig] = {
    "signal_daemon": DaemonConfig(
        name="signal_daemon",
        script="scripts/signal_daemon.py",
        args=["run"],
        health_check_interval=30,
        health_check=check_signal_daemon_health,
        post_crash_hook=recover_signal_daemon,
    ),
    "event_daemon": DaemonConfig(
        name="event_daemon",
        script="scripts/event_daemon.py",
        args=["run"],
        health_check_interval=30,
        health_check=check_event_daemon_health,
        post_crash_hook=recover_event_daemon,
    ),
    "process_supervisor": DaemonConfig(
        name="process_supervisor",
        script="skills/devops/process-supervisor/scripts/process_supervisor.py",
        args=["run"],
        health_check_interval=60,
        health_check=check_process_supervisor_health,
        post_crash_hook=recover_process_supervisor,
    ),
}


# ─── Auto-Recovery Engine ──────────────────────────────────────────────

@dataclass
class DaemonStatus:
    name: str
    alive: bool
    healthy: bool
    last_check: datetime
    consecutive_failures: int = 0
    last_restart: Optional[datetime] = None
    restart_count_last_hour: int = 0
    last_restart_times: List[float] = field(default_factory=list)
    health_details: Dict[str, Any] = field(default_factory=dict)


class AutoRecoveryEngine:
    """
    Continuous monitoring and auto-recovery for all Hermes daemons.
    Runs as a background thread, integrates with process_supervisor.
    """
    
    def __init__(self, check_interval: int = 10):
        self.check_interval = check_interval
        self.daemon_status: Dict[str, DaemonStatus] = {}
        self.running = False
        self._monitor_thread: Optional[threading.Thread] = None
        self._alert_callbacks: List[Callable] = []
        
        # Initialize status
        for name in DAEMON_REGISTRY:
            self.daemon_status[name] = DaemonStatus(
                name=name,
                alive=False,
                healthy=False,
                last_check=datetime.now(timezone.utc),
            )
    
    def add_alert_callback(self, callback: Callable):
        """Add callback for alerts: callback(daemon_name, status, details)."""
        self._alert_callbacks.append(callback)
    
    def _alert(self, daemon_name: str, level: str, message: str, details: Dict):
        """Fire alerts."""
        for cb in self._alert_callbacks:
            try:
                cb(daemon_name, level, message, details)
            except Exception:
                pass
    
    def check_daemon(self, name: str) -> DaemonStatus:
        """Check a single daemon's health."""
        config = DAEMON_REGISTRY[name]
        status = self.daemon_status[name]
        
        # Run health check
        health = config.health_check()
        
        alive = health.get("alive", False)
        heartbeat_age = health.get("heartbeat_age")
        
        # Determine healthy
        healthy = alive
        if heartbeat_age is not None:
            # For signal_daemon, use adaptive threshold based on backoff_interval
            if name == "signal_daemon":
                # Get expected interval from scanner state
                try:
                    state_file = CACHE_DIR / "scanner_state.json"
                    if state_file.exists():
                        state = json.loads(state_file.read_text())
                        expected_interval = state.get("backoff_interval", config.health_check_interval)
                        max_age = expected_interval * 3  # 3x the expected interval
                    else:
                        max_age = config.health_check_interval * 3
                except Exception:
                    max_age = config.health_check_interval * 3
            else:
                max_age = config.health_check_interval * 3  # 3x tolerance
            
            if heartbeat_age > max_age:
                healthy = False
        
        # Also check state_ok for signal_daemon
        if name == "signal_daemon" and not health.get("state_ok", True):
            healthy = False
        
        # Update status
        now = datetime.now(timezone.utc)
        was_healthy = status.healthy
        was_alive = status.alive
        
        status.alive = alive
        status.healthy = healthy
        status.last_check = now
        status.health_details = health
        
        if not healthy:
            status.consecutive_failures += 1
            if was_healthy:
                self._alert(name, "WARNING", f"Daemon became unhealthy: {health.get('details', [])}", health)
        else:
            status.consecutive_failures = 0
            if was_alive and not alive:
                self._alert(name, "CRITICAL", f"Daemon process died", health)
            elif not was_alive and alive:
                self._alert(name, "RECOVERY", f"Daemon process restarted", health)
        
        return status
    
    def should_restart(self, name: str) -> bool:
        """Determine if daemon should be restarted."""
        config = DAEMON_REGISTRY[name]
        status = self.daemon_status[name]
        
        if config.restart_policy == "never":
            return False
        if config.restart_policy == "on_failure" and status.healthy:
            return False
        
        # Check restart rate limit
        now = time.time()
        hour_ago = now - 3600
        status.last_restart_times = [ts for ts in status.last_restart_times if ts > hour_ago]
        
        if len(status.last_restart_times) >= config.max_restarts_per_hour:
            return False
        
        # Restart if dead or unhealthy for too long
        if not status.alive:
            return True
        if not status.healthy and status.consecutive_failures >= 3:
            return True
        
        return False
    
    def restart_daemon(self, name: str) -> bool:
        """Execute recovery for a daemon."""
        config = DAEMON_REGISTRY[name]
        status = self.daemon_status[name]
        
        self._alert(name, "RECOVERY", f"Starting recovery for {name}", status.health_details)
        
        if config.post_crash_hook:
            result = config.post_crash_hook()
            if result.get("success"):
                status.last_restart = datetime.now(timezone.utc)
                status.last_restart_times.append(time.time())
                status.restart_count_last_hour += 1
                status.consecutive_failures = 0
                self._alert(name, "RECOVERY", f"Recovery successful: {result.get('actions', [])}", result)
                return True
            else:
                self._alert(name, "CRITICAL", f"Recovery failed: {result.get('error')}", result)
                return False
        
        return False
    
    def _monitor_loop(self):
        """Main monitoring loop."""
        while self.running:
            try:
                for name in DAEMON_REGISTRY:
                    self.check_daemon(name)
                    
                    if self.should_restart(name):
                        self.restart_daemon(name)
                
            except Exception as e:
                print(f"[AUTO-RECOVERY] Monitor loop error: {e}")
            
            time.sleep(self.check_interval)
    
    def start(self):
        """Start the auto-recovery engine."""
        if self.running:
            return
        
        self.running = True
        self._monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._monitor_thread.start()
        print(f"[AUTO-RECOVERY] Started monitoring {len(DAEMON_REGISTRY)} daemons")
    
    def stop(self):
        """Stop the auto-recovery engine."""
        self.running = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=5)
        print("[AUTO-RECOVERY] Stopped")
    
    def status(self) -> Dict:
        """Get current status of all daemons."""
        result = {}
        for name, status in self.daemon_status.items():
            result[name] = {
                "alive": status.alive,
                "healthy": status.healthy,
                "last_check": status.last_check.isoformat(),
                "consecutive_failures": status.consecutive_failures,
                "last_restart": status.last_restart.isoformat() if status.last_restart else None,
                "restart_count_last_hour": status.restart_count_last_hour,
                "health_details": status.health_details,
            }
        return result
    
    def force_restart(self, name: str) -> bool:
        """Force restart a specific daemon."""
        if name not in DAEMON_REGISTRY:
            return False
        return self.restart_daemon(name)


# ─── CLI ───────────────────────────────────────────────────────────────

def run_daemon():
    """Run auto-recovery as a background daemon."""
    import signal
    
    engine = AutoRecoveryEngine(check_interval=10)
    
    # Add console alert callback
    def console_alert(name, level, message, details):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] [AUTO-RECOVERY] {level}: {name} - {message}")
        if details.get("details"):
            for d in details["details"]:
                print(f"  {d}")
    
    engine.add_alert_callback(console_alert)
    
    def signal_handler(signum, frame):
        print(f"[AUTO-RECOVERY] Received signal {signum}, shutting down...")
        engine.stop()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    engine.start()
    
    try:
        while engine.running:
            time.sleep(1)
    except KeyboardInterrupt:
        engine.stop()


def status_command():
    """Show current status."""
    engine = AutoRecoveryEngine()
    # Run one check cycle
    for name in DAEMON_REGISTRY:
        engine.check_daemon(name)
    
    st = engine.status()
    print(json.dumps(st, indent=2, default=str))


def check_once():
    """Run one check cycle and exit."""
    engine = AutoRecoveryEngine()
    for name in DAEMON_REGISTRY:
        engine.check_daemon(name)
    
    st = engine.status()
    print(json.dumps(st, indent=2, default=str))
    return st


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Hermes Auto-Recovery Engine")
    parser.add_argument("action", choices=["run", "status", "check", "restart"], help="Action to perform")
    parser.add_argument("--daemon", help="Daemon name for restart action")
    args = parser.parse_args()
    
    if args.action == "run":
        run_daemon()
    elif args.action == "status":
        status_command()
    elif args.action == "check":
        check_once()
    elif args.action == "restart":
        if not args.daemon:
            print("Error: --daemon required for restart")
            sys.exit(1)
        engine = AutoRecoveryEngine()
        if engine.force_restart(args.daemon):
            print(f"Restarted {args.daemon}")
        else:
            print(f"Failed to restart {args.daemon}")
            sys.exit(1)


if __name__ == "__main__":
    main()
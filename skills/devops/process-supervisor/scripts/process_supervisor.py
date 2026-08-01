#!/usr/bin/env python3
"""
Process Supervisor — Immortal Daemon Manager for Hermes.
Survives session kills, crashes, reboots. Runs as Windows Service or foreground.
"""

import os
import sys
import json
import time
import signal
import subprocess
import threading
import atexit
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any

# ─── Config ──────────────────────────────────────────────────────────────
HERMES_HOME = Path(os.environ.get("HERMES_HOME", "D:/Portable_Soft/hermes"))
CACHE_DIR = HERMES_HOME / "cache"
STATE_FILE = CACHE_DIR / "supervisor_state.json"
PYTHON_EXE = sys.executable

DAEMONS = [
    {
        "name": "signal_daemon",
        "script": "scripts/signal_daemon.py",
        "args": ["run"],
        "restart_policy": "always",
        "health_check_interval": 30,
    },
    {
        "name": "event_daemon",
        "script": "scripts/event_daemon.py",
        "args": ["run"],
        "restart_policy": "always",
        "health_check_interval": 30,
    },
]

BACKOFF = [5, 10, 30, 60, 300]  # seconds
MAX_RESTARTS_PER_HOUR = 10

# ─── State ───────────────────────────────────────────────────────────────
state_lock = threading.Lock()
supervisor_state = {
    "daemons": {},
    "supervisor_pid": os.getpid(),
    "started_at": datetime.now(timezone.utc).isoformat(),
}

# ─── Utils ───────────────────────────────────────────────────────────────
def log(msg: str):
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] [SUPERVISOR] {msg}")

def load_state():
    global supervisor_state
    if STATE_FILE.exists():
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                supervisor_state = json.load(f)
        except Exception:
            pass

def save_state():
    with state_lock:
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(supervisor_state, f, indent=2, ensure_ascii=False)

def is_process_alive(pid: int) -> bool:
    """Check if process is alive (Windows compatible)."""
    try:
        import psutil
        return psutil.pid_exists(pid)
    except ImportError:
        pass
    # Windows: tasklist /FI with locale-safe cp1251 check
    if sys.platform == "win32":
        try:
            r = subprocess.run(["tasklist", "/FI", f"PID eq {pid}"],
                               capture_output=True, timeout=5)
            out = r.stdout.decode("cp1251", errors="replace")
            return str(pid) in out and "отсутствуют" not in out and "No tasks" not in out
        except:
            return False
    # POSIX fallback: signal 0
    try:
        os.kill(pid, 0)
        return True
    except ProcessLookupError:
        return False

def get_heartbeat_age(daemon_name: str) -> Optional[float]:
    """Get seconds since last heartbeat from daemon's log."""
    log_file = CACHE_DIR / f"{daemon_name}.log"
    if not log_file.exists():
        return None
    try:
        lines = log_file.read_text(encoding="utf-8").strip().splitlines()
        if not lines:
            return None
        last_line = lines[-1]
        # Parse timestamp from log line: [2026-07-03 10:05:00] message
        if last_line.startswith("["):
            ts_str = last_line[1:20]
            last_ts = datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
            return (datetime.now(timezone.utc) - last_ts).total_seconds()
    except Exception:
        pass
    return None

# ─── Daemon Management ──────────────────────────────────────────────────
class DaemonManager:
    def __init__(self, config: Dict):
        self.config = config
        self.name = config["name"]
        self.process: Optional[subprocess.Popen] = None
        self.backoff_index = 0
        self.restart_count = 0
        self.restart_timestamps: List[float] = []
        self._stop_event = threading.Event()

    def start(self) -> bool:
        script_path = HERMES_HOME / self.config["script"]
        if not script_path.exists():
            log(f"Script not found: {script_path}")
            return False

        cmd = [PYTHON_EXE, str(script_path)] + self.config["args"]
        
        try:
            # Start detached process
            creationflags = subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == "win32" else 0
            self.process = subprocess.Popen(
                cmd,
                cwd=str(HERMES_HOME),
                creationflags=creationflags,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            
            pid = self.process.pid
            self.backoff_index = 0
            self.restart_timestamps.append(time.time())
            
            # Update state
            with state_lock:
                supervisor_state["daemons"][self.name] = {
                    "pid": pid,
                    "status": "running",
                    "restart_count": self.restart_count,
                    "last_start": datetime.now(timezone.utc).isoformat(),
                    "last_health_check": datetime.now(timezone.utc).isoformat(),
                    "backoff_index": 0,
                }
            save_state()
            
            log(f"Started {self.name} (PID: {pid})")
            return True
        except Exception as e:
            log(f"Failed to start {self.name}: {e}")
            return False

    def stop(self, timeout: int = 10):
        if self.process and self.process.poll() is None:
            log(f"Stopping {self.name} (PID: {self.process.pid})...")
            try:
                if sys.platform == "win32":
                    self.process.send_signal(signal.CTRL_BREAK_EVENT)
                else:
                    self.process.terminate()
                self.process.wait(timeout=timeout)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait()
            log(f"{self.name} stopped")

    def is_healthy(self) -> bool:
        """Check if daemon process is alive and heartbeat is recent."""
        with state_lock:
            daemon_state = supervisor_state["daemons"].get(self.name, {})
        
        pid = daemon_state.get("pid")
        if not pid:
            return False
        
        if not is_process_alive(pid):
            return False
        
        # Check heartbeat age
        heartbeat_age = get_heartbeat_age(self.name)
        if heartbeat_age is not None:
            max_age = self.config["health_check_interval"] * 3  # 3x interval tolerance
            if heartbeat_age > max_age:
                log(f"{self.name} heartbeat stale: {heartbeat_age:.0f}s > {max_age}s")
                return False
        
        return True

    def restart(self):
        self.stop()
        wait_time = BACKOFF[min(self.backoff_index, len(BACKOFF) - 1)]
        log(f"Restarting {self.name} in {wait_time}s (backoff index {self.backoff_index})")
        time.sleep(wait_time)
        self.backoff_index = min(self.backoff_index + 1, len(BACKOFF) - 1)
        self.restart_count += 1
        self.start()

    def check_restart_rate(self) -> bool:
        """Return True if restart rate is acceptable."""
        now = time.time()
        hour_ago = now - 3600
        self.restart_timestamps = [ts for ts in self.restart_timestamps if ts > hour_ago]
        return len(self.restart_timestamps) < MAX_RESTARTS_PER_HOUR

# ─── Supervisor ──────────────────────────────────────────────────────────
class Supervisor:
    def __init__(self):
        self.daemons: Dict[str, DaemonManager] = {}
        self.running = False
        self._monitor_thread: Optional[threading.Thread] = None

    def initialize(self):
        load_state()
        for config in DAEMONS:
            self.daemons[config["name"]] = DaemonManager(config)

    def start_all(self):
        log("Starting all daemons...")
        for daemon in self.daemons.values():
            daemon.start()
        self.running = True
        self._monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._monitor_thread.start()

    def stop_all(self):
        log("Stopping all daemons...")
        self.running = False
        for daemon in self.daemons.values():
            daemon.stop()
        if self._monitor_thread:
            self._monitor_thread.join(timeout=5)

    def _monitor_loop(self):
        while self.running:
            time.sleep(10)  # Check every 10s
            for name, daemon in self.daemons.items():
                if not daemon.is_healthy():
                    log(f"{name} unhealthy, restarting...")
                    if daemon.check_restart_rate():
                        daemon.restart()
                    else:
                        log(f"{name} restart rate exceeded, pausing...")

    def status(self) -> Dict:
        result = {"supervisor_pid": os.getpid(), "daemons": {}}
        for name, daemon in self.daemons.items():
            with state_lock:
                ds = supervisor_state["daemons"].get(name, {})
            result["daemons"][name] = {
                "pid": ds.get("pid"),
                "status": ds.get("status"),
                "healthy": daemon.is_healthy(),
                "restart_count": ds.get("restart_count", 0),
                "last_start": ds.get("last_start"),
            }
        return result

# ─── Windows Service ─────────────────────────────────────────────────────
try:
    import win32serviceutil
    import win32service
    import win32event
    import servicemanager
    
    class HermesSupervisorService(win32serviceutil.ServiceFramework):
        _svc_name_ = "HermesSupervisor"
        _svc_display_name_ = "Hermes Agent Supervisor"
        _svc_description_ = "Manages Hermes AI agent daemons (signal_daemon, event_daemon)"

        def __init__(self, args):
            win32serviceutil.ServiceFramework.__init__(self, args)
            self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
            self.supervisor = Supervisor()

        def SvcStop(self):
            self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
            win32event.SetEvent(self.hWaitStop)
            self.supervisor.stop_all()

        def SvcDoRun(self):
            self.supervisor.initialize()
            self.supervisor.start_all()
            win32event.WaitForSingleObject(self.hWaitStop, win32event.INFINITE)

except ImportError:
    HermesSupervisorService = None

# ─── CLI ─────────────────────────────────────────────────────────────────
def run_foreground():
    """Run supervisor in foreground (for testing)."""
    supervisor = Supervisor()
    supervisor.initialize()
    supervisor.start_all()
    
    def signal_handler(signum, frame):
        log(f"Received signal {signum}, shutting down...")
        supervisor.stop_all()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        supervisor.stop_all()

def install_service():
    if not HermesSupervisorService:
        log("pywin32 not installed. Run: pip install pywin32")
        return
    win32serviceutil.InstallService(
        HermesSupervisorService.__module__ + "." + HermesSupervisorService.__name__,
        HermesSupervisorService._svc_name_,
        HermesSupervisorService._svc_display_name_,
    )
    log("Service installed")

def start_service():
    if not HermesSupervisorService:
        return
    win32serviceutil.StartService(HermesSupervisorService._svc_name_)
    log("Service started")

def stop_service():
    if not HermesSupervisorService:
        return
    win32serviceutil.StopService(HermesSupervisorService._svc_name_)
    log("Service stopped")

def status():
    supervisor = Supervisor()
    supervisor.initialize()
    st = supervisor.status()
    print(json.dumps(st, indent=2))

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Hermes Process Supervisor")
    parser.add_argument("action", choices=["run", "install", "start", "stop", "status"])
    args = parser.parse_args()

    if args.action == "run":
        run_foreground()
    elif args.action == "install":
        install_service()
    elif args.action == "start":
        start_service()
    elif args.action == "stop":
        stop_service()
    elif args.action == "status":
        status()

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Autonomous Agent Daemon — runs the agent continuously in background.

Unlike cron (which runs every 30 min), this daemon:
- Runs the agent every 5 minutes
- Logs every action to cache/action_log.jsonl
- Auto-restarts on crash with backoff
- Tracks uptime and total runs

Usage:
    python scripts/agent_daemon.py          # run in foreground
    python scripts/agent_daemon.py --status  # check if running
    python scripts/agent_daemon.py --stop    # stop daemon
    python scripts/agent_daemon.py --log     # show last 10 actions
"""
import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

HERMES_HOME = Path(__file__).resolve().parent.parent
AGENT_SCRIPT = HERMES_HOME / "scripts" / "autonomous_agent.py"
PID_FILE = HERMES_HOME / "cache" / "agent_daemon.pid"
LOG_FILE = HERMES_HOME / "cache" / "action_log.jsonl"
DAEMON_LOG = HERMES_HOME / "logs" / "agent_daemon.log"

INTERVAL = 300  # 5 minutes between runs
MAX_BACKOFF = 600  # 10 minutes max backoff
INITIAL_BACKOFF = 30


def log(msg: str):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = "[%s] %s" % (ts, msg)
    try:
        print(line)
    except UnicodeEncodeError:
        print(line.encode("ascii", "replace").decode("ascii"))
    try:
        DAEMON_LOG.parent.mkdir(parents=True, exist_ok=True)
        with open(DAEMON_LOG, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass


def is_running() -> bool:
    if not PID_FILE.exists():
        return False
    try:
        pid = int(PID_FILE.read_text().strip())
        # Windows: use tasklist to check if process exists
        result = subprocess.run(
            ["tasklist", "/FI", "PID eq %d" % pid],
            capture_output=True, timeout=5,
        )
        return str(pid) in result.stdout.decode("utf-8", errors="replace")
    except Exception:
        return False


def save_pid():
    PID_FILE.parent.mkdir(parents=True, exist_ok=True)
    PID_FILE.write_text(str(os.getpid()))


def cleanup_pid():
    try:
        PID_FILE.unlink(missing_ok=True)
    except Exception:
        pass


def run_agent() -> dict:
    """Run one cycle of the autonomous agent."""
    start = time.time()
    try:
        result = subprocess.run(
            [sys.executable, str(AGENT_SCRIPT)],
            capture_output=True, timeout=120,
            cwd=str(HERMES_HOME),
        )
        elapsed = time.time() - start
        stdout = result.stdout.decode("utf-8", errors="replace")
        stderr = result.stderr.decode("utf-8", errors="replace")
        output = stdout + stderr

        # Parse result
        action = "unknown"
        status = "success"
        for line in output.split("\n"):
            if "SELECTED:" in line:
                action = line.split("SELECTED:")[-1].strip()
            if "EXECUTION ERROR" in line:
                status = "error"
            if "TIMEOUT" in line:
                status = "timeout"

        return {
            "timestamp": datetime.now().isoformat(),
            "action": action[:100],
            "status": status,
            "elapsed": round(elapsed, 1),
            "returncode": result.returncode,
        }
    except subprocess.TimeoutExpired:
        return {
            "timestamp": datetime.now().isoformat(),
            "action": "TIMEOUT (agent script)",
            "status": "timeout",
            "elapsed": 120,
            "returncode": -1,
        }
    except Exception as e:
        return {
            "timestamp": datetime.now().isoformat(),
            "action": "ERROR: %s" % str(e)[:80],
            "status": "error",
            "elapsed": 0,
            "returncode": -1,
        }


def show_status():
    if is_running():
        pid = int(PID_FILE.read_text().strip())
        print("Agent daemon: RUNNING (PID %d)" % pid)
    else:
        print("Agent daemon: NOT RUNNING")

    if LOG_FILE.exists():
        lines = LOG_FILE.read_text(encoding="utf-8").strip().split("\n")
        print("Total actions logged: %d" % len(lines))
        if lines:
            last = json.loads(lines[-1])
            print("Last action: [%s] %s (status=%s)" % (
                last.get("timestamp", "?")[:16],
                last.get("title", "?")[:50],
                last.get("status", "?"),
            ))
    else:
        print("No actions logged yet")


def show_log(n: int = 10):
    if not LOG_FILE.exists():
        print("No actions logged yet.")
        return

    lines = LOG_FILE.read_text(encoding="utf-8").strip().split("\n")
    print("Last %d actions:" % min(n, len(lines)))
    for line in lines[-n:]:
        try:
            e = json.loads(line)
            ts = e.get("timestamp", "?")[:16]
            action = e.get("title", "?")[:50]
            status = e.get("status", "?")
            score = e.get("score", "?")
            print("  [%s] %s (score=%s, status=%s)" % (ts, action, score, status))
        except json.JSONDecodeError:
            pass


def stop_daemon():
    if not PID_FILE.exists():
        print("No daemon PID file found.")
        return
    try:
        pid = int(PID_FILE.read_text().strip())
        subprocess.run(
            ["taskkill", "/F", "/PID", str(pid)],
            capture_output=True, timeout=5,
        )
        print("Killed PID %d" % pid)
        time.sleep(2)
        cleanup_pid()
    except (ValueError, ProcessLookupError, PermissionError) as e:
        print("Could not stop daemon: %s" % e)
        cleanup_pid()


def main():
    args = sys.argv[1:]

    if "--status" in args:
        show_status()
        return

    if "--log" in args:
        n = 10
        if "--limit" in args:
            idx = args.index("--limit")
            if idx + 1 < len(args):
                n = int(args[idx + 1])
        show_log(n)
        return

    if "--stop" in args:
        stop_daemon()
        return

    # Run daemon
    if is_running():
        print("Daemon already running.")
        return

    save_pid()
    log("Agent daemon started (event-driven mode)")

    backoff = INITIAL_BACKOFF
    run_count = 0
    
    # Set up file watcher for event-driven mode
    watch_dirs = [
        str(HERMES_HOME / "cache"),
        str(HERMES_HOME / "config"),
        str(HERMES_HOME / "scripts"),
    ]
    file_events = []
    
    has_observer = False
    last_event_run = 0.0
    
    try:
        from watchdog.observers import Observer
        from watchdog.events import FileSystemEventHandler
        
        class ChangeHandler(FileSystemEventHandler):
            def on_modified(self, event):
                if not event.is_directory:
                    nonlocal file_events
                    file_events.append(time.time())
            def on_created(self, event):
                if not event.is_directory:
                    nonlocal file_events
                    file_events.append(time.time())
        
        observer = Observer()
        for d in watch_dirs:
            if Path(d).exists():
                observer.schedule(ChangeHandler(), d, recursive=False)
                log("  Watching: %s" % d)
        observer.start()
        has_observer = True
        log("File watcher active — event-driven mode (debounced 30s)")
    except ImportError:
        log("watchdog not installed — polling mode")
    
    try:
        while True:
            now = time.time()
            
            # Event-driven: debounced file changes trigger agent
            if file_events:
                # Drain all accumulated events, use latest timestamp
                while file_events:
                    last_ts = file_events.pop(0)
                if now - last_ts < 30:
                    time.sleep(2)
                    continue
                log("Events detected — running agent")
                result = run_agent()
                log("  Result: [%s] %s" % (result["status"], result["action"][:60]))
                last_event_run = now
                backoff = INITIAL_BACKOFF
            
            # Polling fallback: run every 30 min if no events
            run_count += 1
            if run_count % 360 == 0 and now - last_event_run > 300:
                log("Polling fallback — running agent...")
                result = run_agent()
                log("  Result: [%s] %s" % (result["status"], result["action"][:60]))
            
            time.sleep(5)

    except KeyboardInterrupt:
        log("Daemon stopped by user")
    finally:
        if has_observer:
            observer.stop()
            observer.join()
        cleanup_pid()
        log("Daemon exited")


if __name__ == "__main__":
    main()

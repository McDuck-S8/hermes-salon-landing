#!/usr/bin/env python3
"""
Signal Daemon — event-driven внешний мониторинг.
Запускается как фоновый процесс.

> Revisit: when signal sources, adaptive backoff, or event routing changes. Last touched: 2026-07-02.
Следит за HN + GitHub trending.
При новом сигнале → event_bus.emit("new_external_signal") → rd_processor + dev_processor.

Usage:
    python scripts/signal_daemon.py start   # start as background daemon
    python scripts/signal_daemon.py stop    # stop daemon
    python scripts/signal_daemon.py status  # check status
    python scripts/signal_daemon.py run     # foreground (for testing)
"""
import sys
import os
import json
import time
import signal as sig
from pathlib import Path
from datetime import datetime, timezone

HERMES_HOME = Path(__file__).resolve().parent.parent
CACHE_DIR = HERMES_HOME / "cache"
DAEMON_PID = CACHE_DIR / "signal_daemon.pid"
DAEMON_LOG = CACHE_DIR / "signal_daemon.log"
SCANNER_STATE = CACHE_DIR / "scanner_state.json"


def _log(msg: str):
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    with open(DAEMON_LOG, "a", encoding="utf-8") as f:
        f.write(f"[{ts}] {msg}\n")


def _write_pid():
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    DAEMON_PID.write_text(str(os.getpid()), "utf-8")


def _read_pid() -> int:
    if DAEMON_PID.exists():
        try:
            return int(DAEMON_PID.read_text("utf-8").strip())
        except:
            pass
    return 0


def _is_running() -> bool:
    pid = _read_pid()
    if pid == 0:
        return False
    if sys.platform == "win32":
        import subprocess
        try:
            r = subprocess.run(["tasklist", "/FI", f"PID eq {pid}"], capture_output=True, timeout=5)
            out = r.stdout.decode("cp1251", errors="replace")
            # PID in output = process found; "отсутствуют" / "No tasks" = not found
            return str(pid) in out and "отсутствуют" not in out and "No tasks" not in out
        except:
            return False
    try:
        os.kill(pid, 0)
        return True
    except ProcessLookupError:
        return False


def _handle_signal(signum, frame):
    _log("Daemon stopped by signal")
    if DAEMON_PID.exists():
        DAEMON_PID.unlink()
    sys.exit(0)


def run_daemon():
    """Main daemon loop."""
    if _is_running():
        print(f"Already running (PID {_read_pid()})")
        return

    _write_pid()
    sig.signal(sig.SIGTERM, _handle_signal)
    sig.signal(sig.SIGINT, _handle_signal)

    _log(f"Signal daemon started (PID {os.getpid()})")
    print(f"Signal daemon started (PID {os.getpid()})")

    sys.path.insert(0, str(HERMES_HOME / "scripts"))
    from signal_scanner import run_once, load_state, save_state

    state = load_state()
    interval = state.get("backoff_interval", 60)

    while True:
        try:
            scan_start = time.time()
            new = run_once()
            scan_duration = time.time() - scan_start

            state = load_state()
            state["last_scan"] = datetime.now(timezone.utc).isoformat()
            state["total_signals"] = state.get("total_signals", 0) + new

            if new > 0:
                interval = 60  # reset backoff
                _log(f"+{new} signals ({scan_duration:.1f}s) -> backoff reset")
                print(f"[{datetime.now().strftime('%H:%M:%S')}] +{new} signals -> backoff reset to {interval}s")
            else:
                interval = min(interval * 2, 600)  # max 10 min
                _log(f"nothing new ({scan_duration:.1f}s) -> backoff {interval}s")
                print(f"[{datetime.now().strftime('%H:%M:%S')}] nothing new -> backoff to {interval}s")

            state["backoff_interval"] = interval
            save_state(state)

            time.sleep(interval)

        except KeyboardInterrupt:
            _log("Daemon stopped by user")
            break
        except Exception as e:
            _log(f"Error: {e}")
            print(f"Error: {e}")
            interval = min(interval * 3, 600)
            time.sleep(interval)

    if DAEMON_PID.exists():
        DAEMON_PID.unlink()


def stop_daemon():
    """Stop the daemon (Windows-compatible)."""
    pid = _read_pid()
    if pid == 0:
        print("Not running.")
        return
    try:
        if sys.platform == "win32":
            import subprocess
            subprocess.run(["taskkill", "/F", "/PID", str(pid)], capture_output=True, timeout=5)
            print(f"Force-killed PID {pid}")
        else:
            os.kill(pid, sig.SIGTERM)
            print(f"Sent SIGTERM to PID {pid}")
        time.sleep(1)
        if not _is_running():
            print("Daemon stopped.")
        else:
            print("Daemon still running, trying force kill...")
            if sys.platform == "win32":
                import subprocess
                subprocess.run(["taskkill", "/F", "/PID", str(pid)], capture_output=True, timeout=5)
            else:
                os.kill(pid, sig.SIGKILL)
    except ProcessLookupError:
        print("Process not found.")
        if DAEMON_PID.exists():
            DAEMON_PID.unlink()


def status():
    """Show daemon status."""
    if _is_running():
        pid = _read_pid()
        print(f"Signal daemon: RUNNING (PID {pid})")
    else:
        print("Signal daemon: STOPPED")

    if SCANNER_STATE.exists():
        state = json.loads(SCANNER_STATE.read_text("utf-8"))
        print(f"  Total signals: {state.get('total_signals', 0)}")
        print(f"  Last scan: {state.get('last_scan', 'never')}")
        print(f"  Backoff: {state.get('backoff_interval', 60)}s")

    if DAEMON_LOG.exists():
        lines = DAEMON_LOG.read_text("utf-8").strip().split("\n")
        print(f"  Log entries: {len(lines)}")
        print(f"  Last 5:")
        for l in lines[-5:]:
            print(f"    {l}")


def main():
    if len(sys.argv) < 2:
        print("Usage: signal_daemon.py start|stop|status|run")
        return

    cmd = sys.argv[1]
    if cmd == "start":
        run_daemon()
    elif cmd == "stop":
        stop_daemon()
    elif cmd == "status":
        status()
    elif cmd == "run":
        run_daemon()
    else:
        print(f"Unknown: {cmd}")


if __name__ == "__main__":
    main()

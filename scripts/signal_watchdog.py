#!/usr/bin/env python3
"""Watchdog for signal_daemon — start if not running."""
import subprocess, sys, os
HERMES = "D:/Portable_Soft/hermes"
python = sys.executable

# Check if running
r = subprocess.run([python, f"{HERMES}/scripts/signal_daemon.py", "status"], capture_output=True, text=True, timeout=10)
if "RUNNING" in r.stdout:
    print("Signal daemon: RUNNING")
    sys.exit(0)

# Not running — start it
print("Signal daemon: STOPPED — starting...")
subprocess.Popen(
    [python, f"{HERMES}/scripts/signal_daemon.py", "start"],
    cwd=HERMES,
    creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0,
)
print("Signal daemon: STARTED")

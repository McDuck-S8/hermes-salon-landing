#!/usr/bin/env python3
"""Wrapper: runs jarvis_security_monitor.py without args (stub) — for cron."""
import subprocess, sys
from pathlib import Path

HERMES = Path("D:/Portable_Soft/hermes")
script = HERMES / "scripts" / "jarvis_security_monitor.py"

if not script.exists():
    print(f"[jarvis_wrapper] Script not found: {script}")
    sys.exit(1)

r = subprocess.run(
    [sys.executable, str(script)],
    capture_output=True, text=True, timeout=60,
    cwd=str(HERMES),
)
if r.stdout:
    print(r.stdout)
if r.stderr:
    print(r.stderr, file=sys.stderr)
sys.exit(r.returncode)

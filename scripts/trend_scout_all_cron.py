#!/usr/bin/env python3
"""Wrapper: runs trend_scout.py with --category all for cron."""
import subprocess, sys
from pathlib import Path

HERMES = Path("D:/Portable_Soft/hermes")
script = HERMES / "scripts" / "trend_scout.py"

if not script.exists():
    print(f"[trend_scout_all] Script not found: {script}")
    sys.exit(1)

r = subprocess.run(
    [sys.executable, str(script), "--category", "all"],
    capture_output=True, text=True, timeout=120,
    cwd=str(HERMES),
)
if r.stdout:
    print(r.stdout)
if r.stderr:
    print(r.stderr, file=sys.stderr)
sys.exit(r.returncode)

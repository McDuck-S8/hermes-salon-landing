#!/usr/bin/env python3
"""Wrapper: run auto-fetch sessions (cron: every 60m).

Originally pointed to memory_tree/scripts/run_auto_fetch.py (broken path).
Now delegates to session_dump_ingester.py for session dump ingestion.
"""
import subprocess, sys, os
from pathlib import Path

HERMES_HOME = Path(__file__).resolve().parent.parent

# Primary: session dump ingester
script = HERMES_HOME / "scripts" / "session_dump_ingester.py"

# Fallback: memory_tree auto_fetch (if it exists)
fallback = os.path.expanduser("~/.hermes/memory_tree/scripts/run_auto_fetch.py")
if not script.is_file():
    if os.path.isfile(fallback):
        script = Path(fallback)
    else:
        print(f"[auto-fetch] ERROR: no ingest script found")
        print(f"  Tried: {script}")
        print(f"  Tried: {fallback}")
        sys.exit(1)

result = subprocess.run(
    [sys.executable, str(script)],
    capture_output=True, text=True, timeout=120,
    cwd=str(HERMES_HOME),
)
print(result.stdout)
if result.stderr:
    print(f"STDERR: {result.stderr}", file=sys.stderr)
if result.returncode != 0:
    print(f"[auto-fetch] exit code: {result.returncode}", file=sys.stderr)
    sys.exit(result.returncode)

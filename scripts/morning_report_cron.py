#!/usr/bin/env python3
"""Morning report: read branches.yaml and breadcrumbs.log (cron: daily at 8am).

Outputs a brief summary of active branches and recent breadcrumbs.
Runs as no_agent=True — output is delivered verbatim.
Silent when no branches/breadcrumbs found.
"""
import sys, os, yaml
from pathlib import Path

branches_file = os.path.expanduser("~/.hermes/branches.yaml")
breadcrumbs_file = os.path.expanduser("~/.hermes/breadcrumbs.log")

print(f"# Morning Report — {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M')}")
print()

# 1. Branches
if os.path.isfile(branches_file):
    try:
        with open(branches_file) as f:
            branches = yaml.safe_load(f) or {}
        active = [b for b in (branches.get("branches") or []) if b.get("status") != "completed"]
        if active:
            print(f"## Active Branches ({len(active)})")
            for b in active:
                print(f"  - {b.get('name', '?')}: {b.get('status', '?')} ({b.get('goal', '')[:80]})")
        else:
            print("## No active branches")
    except Exception as e:
        print(f"## Branches error: {e}")
else:
    print("## No branches.yaml found")

print()

# 2. Breadcrumbs (last 7 days)
if os.path.isfile(breadcrumbs_file):
    try:
        with open(breadcrumbs_file) as f:
            lines = f.readlines()
        recent = [l.strip() for l in lines if l.strip()][-15:]
        if recent:
            print(f"## Recent Breadcrumbs ({len(recent)} of {len(lines)} total)")
            for l in recent:
                print(f"  {l[:120]}")
        else:
            print("## No breadcrumbs")
    except Exception as e:
        print(f"## Breadcrumbs error: {e}")
else:
    print("## No breadcrumbs.log found")

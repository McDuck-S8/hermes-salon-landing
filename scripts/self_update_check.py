#!/usr/bin/env python3
"""
Hermes Self-Update Check — daily check for upstream updates.
Reports commits behind and critical changes.

> Revisit: when self-update check logic, version comparison, or upgrade triggers change. Last touched: 2026-07-02.
Does NOT auto-update (user must approve).
"""
import subprocess
import json
import os
from datetime import datetime
from pathlib import Path

HERMES_ROOT = Path(os.environ.get("HERMES_HOME", "D:/Portable_Soft/hermes"))
HERMES_AGENT = HERMES_ROOT / "hermes-agent"
LOG_FILE = HERMES_ROOT / "logs" / "self_update_check.log"

def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}\n"
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(line)
    print(line.strip())

def run_git(args):
    r = subprocess.run(
        ["git"] + args,
        cwd=str(HERMES_AGENT),
        capture_output=True, text=True, timeout=30
    )
    return r.stdout.strip(), r.returncode

def main():
    log("=== Daily self-update check ===")
    
    # Fetch latest
    out, rc = run_git(["fetch", "--all", "--quiet"])
    if rc != 0:
        log(f"ERROR: git fetch failed: {out}")
        print(f"[FAIL] Git fetch failed: {out}")
        return
    
    # Count commits behind
    behind, _ = run_git(["rev-list", "--count", "HEAD..origin/main"])
    ahead, _ = run_git(["rev-list", "--count", "origin/main..HEAD"])
    
    # Current version
    version, _ = run_git(["describe", "--tags", "--always"])
    branch, _ = run_git(["branch", "--show-current"])
    commit_date, _ = run_git(["log", "-1", "--format=%ci"])
    
    log(f"Branch: {branch}, Version: {version}, Behind: {behind}, Ahead: {ahead}")
    
    # Get recent important changes
    recent, _ = run_git(["log", f"HEAD..origin/main", "--oneline", "-10"])
    
    # Check for critical files changed
    critical_files = []
    files_changed, _ = run_git(["diff", "--name-only", f"HEAD..origin/main"])
    for f in files_changed.split("\n"):
        if f and any(x in f for x in ["AGENTS.md", "config.yaml", "requirements", "pyproject.toml"]):
            critical_files.append(f)
    
    report = []
    report.append(f"📦 Hermes Self-Update Check")
    report.append(f"Branch: {branch} | Version: {version}")
    report.append(f"Behind: {behind} commits | Ahead: {ahead}")
    report.append(f"Local commit: {commit_date}")
    
    if int(behind or 0) > 0:
        report.append(f"\n📥 Recent upstream changes:")
        report.append(recent)
        
        if critical_files:
            report.append(f"\n⚠️ Critical files changed:")
            for f in critical_files:
                report.append(f"  - {f}")
        
        report.append(f"\n💡 To update: cd hermes-agent && git pull origin main")
        report.append(f"Then restart gateway.")
    else:
        report.append(f"\n✅ Up to date!")
    
    print("\n".join(report))

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Hermes Self-Improvement Cycle — runs every 15 min.
Meditates on errors, limitations, insights.

> Revisit: when self-improvement cycle logic, analysis phases, or cycle orchestration changes. Last touched: 2026-07-02.
Checks network, gateway health, tries to improve.
"""
import subprocess
import json
import os
import sys
import httpx
import time
from datetime import datetime
from pathlib import Path

HERMES_ROOT = Path(os.environ.get("HERMES_HOME", "D:/Portable_Soft/hermes"))
LOG_FILE = HERMES_ROOT / "logs" / "self_improvement_cycle.log"
INSIGHTS_FILE = HERMES_ROOT / "cache" / "meditation_insights.json"

def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")
    print(line)

def run_cmd(cmd, timeout=15):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, shell=True)
        return r.stdout.strip(), r.returncode
    except subprocess.TimeoutExpired:
        return "TIMEOUT", 1
    except Exception as e:
        return str(e), 1

def check_network():
    """Quick Telegram API check."""
    try:
        from telegram_helper import check_telegram_api
        ok, code = check_telegram_api()
        return ok, code, 0
    except:
        return False, 0, 0

def check_gateway():
    """Check gateway log for recent health."""
    log_path = HERMES_ROOT / "logs" / "gateway.log"
    if not log_path.exists():
        return "NO_LOG"
    lines = log_path.read_text(encoding="utf-8", errors="ignore").split("\n")
    last_10 = [l for l in lines[-10:] if l.strip()]
    
    connected = any("Connected to Telegram" in l for l in last_10)
    errors = sum(1 for l in last_10 if "ERROR" in l)
    warnings = sum(1 for l in last_10 if "WARNING" in l)
    
    return {
        "connected": connected,
        "errors": errors,
        "warnings": warnings,
        "last_line": last_10[-1] if last_10 else "EMPTY"
    }

def check_errors():
    """Review recent errors for patterns."""
    err_path = HERMES_ROOT / "logs" / "errors.log"
    if not err_path.exists():
        return []
    lines = err_path.read_text(encoding="utf-8", errors="ignore").split("\n")
    recent = [l for l in lines[-50:] if l.strip()]
    
    # Find patterns
    patterns = {}
    for l in recent:
        for keyword in ["ConnectError", "TimeoutError", "NetworkError", "FileNotFoundError", "PermissionError"]:
            if keyword in l:
                patterns[keyword] = patterns.get(keyword, 0) + 1
    return patterns

def load_insights():
    defaults = {"cycles": 0, "insights": [], "errors_seen": {}, "network_checks": 0, "network_fails": 0}
    try:
        data = json.loads(INSIGHTS_FILE.read_text())
        defaults.update(data)
        return defaults
    except:
        return defaults

def save_insights(data):
    INSIGHTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    INSIGHTS_FILE.write_text(json.dumps(data, indent=2, default=str))

def main():
    now = datetime.now()
    insights = load_insights()
    insights["cycles"] += 1
    
    log(f"=== Self-improvement cycle #{insights['cycles']} ===")
    
    # 1. Network check
    net_ok, net_code, net_time = check_network()
    insights["network_checks"] += 1
    if not net_ok:
        insights["network_fails"] += 1
    log(f"Network: {'OK ' + str(net_code) if net_ok else 'FAIL'} ({net_time:.1f}s)")
    
    # 2. Gateway health
    gw = check_gateway()
    if isinstance(gw, dict):
        log(f"Gateway: connected={gw['connected']} errors={gw['errors']} warnings={gw['warnings']}")
        if not gw['connected']:
            insights["insights"].append(f"[{now.strftime('%H:%M')}] Gateway disconnected from Telegram")
    else:
        log(f"Gateway: {gw}")
    
    # 3. Error pattern analysis
    errors = check_errors()
    for err_type, count in errors.items():
        insights["errors_seen"][err_type] = insights["errors_seen"].get(err_type, 0) + count
    if errors:
        log(f"Error patterns: {errors}")
    
    # 4. Insights — meditate on what could be improved
    cycle_num = insights["cycles"]
    
    if cycle_num % 4 == 0:  # Every hour (4 cycles)
        # Check for stale files
        out, rc = run_cmd(f'find "{HERMES_ROOT}/scripts" -name "*.py" -mtime +7 | head -5')
        if out and out != "TIMEOUT":
            insights["insights"].append(f"[{now.strftime('%H:%M')}] Stale scripts: {out}")
            log(f"Stale scripts found: {out}")
    
    if cycle_num % 8 == 0:  # Every 2 hours
        # Check disk space
        out, rc = run_cmd('df -h 2>/dev/null | tail -1' if __import__('os').name != 'nt' else 'echo N/A')
        if out and out != "TIMEOUT":
            log(f"Disk: {out}")
        
        # Check memory system
        mem_path = HERMES_ROOT / "memory_system" / "learnings.md"
        if mem_path.exists():
            lines = len(mem_path.read_text().split("\n"))
            log(f"Learnings file: {lines} lines")
            if lines > 100:
                insights["insights"].append(f"[{now.strftime('%H:%M')}] Learnings file growing: {lines} lines — needs pruning")
    
    if not net_ok and insights["network_fails"] % 5 == 0:
        insights["insights"].append(f"[{now.strftime('%H:%M')}] Network instability — {insights['network_fails']}/{insights['network_checks']} fails")
    
    # Keep insights bounded
    if len(insights["insights"]) > 50:
        insights["insights"] = insights["insights"][-50:]
    
    save_insights(insights)
    log(f"Cycle #{cycle_num} complete. Insights: {len(insights['insights'])}")

if __name__ == "__main__":
    main()

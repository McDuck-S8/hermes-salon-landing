#!/usr/bin/env python3
"""
Hermes Heartbeat — simple health check + event processing.
Runs every 2 minutes via cron.

> Revisit: when heartbeat interval, event emission, or health metrics change. Last touched: 2026-07-02.
Checks: network, gateway, disk, memory.
Also processes pending events via event_bus.py.
Logs to heartbeat.log.
"""
import json
import sys
import time
import httpx
import subprocess
from datetime import datetime
from pathlib import Path

HERMES_ROOT = Path("D:/Portable_Soft/hermes")
LOG_FILE = HERMES_ROOT / "logs" / "heartbeat.log"

def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")
    print(line)

def check_network():
    """Check real internet connectivity, not Telegram specifically."""
    try:
        r = httpx.get("https://httpbin.org/ip", timeout=5, proxy="socks5://127.0.0.1:10806")
        return r.status_code == 200, r.status_code
    except:
        try:
            r = httpx.get("https://httpbin.org/ip", timeout=5)
            return r.status_code == 200, r.status_code
        except Exception as e:
            return False, str(e)[:50]

def check_gateway():
    log_path = HERMES_ROOT / "logs" / "gateway.log"
    if not log_path.exists():
        return "NO_LOG"
    lines = log_path.read_text(encoding="utf-8", errors="ignore").split("\n")
    last_5 = [l for l in lines[-5:] if l.strip()]
    connected = any("Connected to Telegram" in l for l in last_5)
    errors = sum(1 for l in last_5 if "ERROR" in l)
    return {"connected": connected, "errors": errors}

def main():
    net_ok, net_code = check_network()
    gw = check_gateway()
    
    status = "OK" if net_ok else "NO_NETWORK"
    gw_status = "connected" if isinstance(gw, dict) and gw.get("connected") else "disconnected"
    
    log(f"Heartbeat: network={status}({net_code}) gateway={gw_status}")
    
    # Write state for other scripts to read
    state = {
        "timestamp": datetime.now().isoformat(),
        "network_ok": net_ok,
        "gateway_connected": isinstance(gw, dict) and gw.get("connected", False),
        "gateway_errors": gw.get("errors", 0) if isinstance(gw, dict) else 0
    }
    state_file = HERMES_ROOT / "cache" / "heartbeat_state.json"
    state_file.write_text(json.dumps(state, indent=2))

    # --- Event processing: process all pending events via event_bus ---
    try:
        scripts_dir = Path(__file__).resolve().parent
        result = subprocess.run(
            [sys.executable, str(scripts_dir / "event_bus.py"), "process"],
            capture_output=True, text=True, timeout=40,
            cwd=str(HERMES_ROOT)
        )
        if result.stdout.strip():
            log(f"Events: {result.stdout.strip()}")
        if result.returncode != 0 and result.stderr.strip():
            log(f"Events error: {result.stderr.strip()[:200]}")
    except Exception as e:
        log(f"Events: subprocess failed: {e}")

if __name__ == "__main__":
    main()

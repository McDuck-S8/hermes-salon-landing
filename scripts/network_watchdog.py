#!/usr/bin/env python3
"""
Telegram Network Watchdog — checks api.telegram.org connectivity.
Returns status for cron delivery.

> Revisit: when network watchdog logic, connectivity checks, or recovery actions change. Last touched: 2026-07-02.
"""
import httpx
import json
import time
import os
from datetime import datetime
from pathlib import Path

LOG_FILE = Path(os.environ.get("HERMES_HOME", "D:/Portable_Soft/hermes")) / "logs" / "network_watchdog.log"
STATE_FILE = Path(os.environ.get("HERMES_HOME", "D:/Portable_Soft/hermes")) / "cache" / "watchdog_state.json"

def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}\n"
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(line)
    print(line.strip())

def load_state():
    try:
        return json.loads(STATE_FILE.read_text())
    except:
        return {"consecutive_fails": 0, "last_ok": None, "total_checks": 0, "total_fails": 0}

def save_state(state):
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2))

def check_telegram():
    """Check Telegram API via HTTP proxy."""
    try:
        from telegram_helper import check_telegram_api
        start = time.time()
        ok, code = check_telegram_api()
        elapsed = time.time() - start
        return ok, code, elapsed
    except Exception as e:
        return False, str(e), 0

def check_via_proxy():
    """Check Telegram API via socks5 proxy (fallback)."""
    for port in [10806, 10808]:
        try:
            start = time.time()
            r = httpx.get("https://api.telegram.org", proxy=f"socks5://127.0.0.1:{port}", timeout=8)
            elapsed = time.time() - start
            return True, r.status_code, elapsed, port
        except:
            pass
    return False, "all proxies failed", 0, 0

def main():
    state = load_state()
    state["total_checks"] += 1
    
    # Direct check
    ok, code, elapsed = check_telegram()
    
    if ok:
        state["consecutive_fails"] = 0
        state["last_ok"] = datetime.now().isoformat()
        state["total_checks"] += 1
        save_state(state)
        log(f"OK direct: {code} in {elapsed:.2f}s (fails={state['consecutive_fails']})")
        # Silent on success — no notification needed
        return
    
    state["consecutive_fails"] += 1
    state["total_fails"] += 1
    save_state(state)
    
    # Try proxy fallback
    proxy_ok, proxy_code, proxy_elapsed, port = check_via_proxy()
    
    log(f"FAIL direct: {code} | proxy={'OK:'+str(proxy_code)+' port:'+str(port) if proxy_ok else 'FAIL'} | consecutive_fails={state['consecutive_fails']}")
    
    # Report only on consecutive failures >= 3
    if state["consecutive_fails"] >= 3:
        print(f"[WARN] Telegram API unreachable! {state['consecutive_fails']} consecutive failures.")
        print(f"Direct: {code}")
        print(f"Proxy: {'OK via port ' + str(port) if proxy_ok else 'All proxies failed'}")
        print(f"Last OK: {state['last_ok'] or 'never'}")
        print(f"Total checks: {state['total_checks']}, Total fails: {state['total_fails']}")
    else:
        # First failures are normal network noise — silent
        pass

if __name__ == "__main__":
    main()

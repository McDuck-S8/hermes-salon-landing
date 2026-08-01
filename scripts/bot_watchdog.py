#!/usr/bin/env python3
"""Background bot watchdog — restart cpa_bot if dead."""
import subprocess, sys, os, time, logging
from pathlib import Path

HERMES = Path("D:/Portable_Soft/hermes")
LOG = HERMES / "logs" / "bot_watchdog.log"
PID_FILE = HERMES / "cache" / "cpa_bot.pid"

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s %(message)s",
    handlers=[logging.FileHandler(str(LOG), encoding="utf-8")],
)

def is_running(pid):
    if not pid: return False
    try:
        import subprocess
        r = subprocess.run(["tasklist", "/FI", f"PID eq {pid}"], capture_output=True, timeout=5, text=True)
        return str(pid) in r.stdout and "отсутствуют" not in r.stdout and "No tasks" not in r.stdout
    except:
        return False

if __name__ == "__main__":
    logging.info("Checking CPA bot...")
    pid = None
    if PID_FILE.exists():
        pid = int(PID_FILE.read_text().strip())

    if pid and is_running(pid):
        logging.info(f"CPA bot alive (PID {pid})")
        sys.exit(0)

    # Not running — restart
    logging.warning("CPA bot dead — restarting...")
    proc = subprocess.Popen(
        [sys.executable, str(HERMES / "scripts" / "cpa_telegram_bot.py")],
        cwd=str(HERMES),
        creationflags=subprocess.CREATE_NO_WINDOW,
    )
    PID_FILE.write_text(str(proc.pid))
    logging.info(f"CPA bot started (PID {proc.pid})")

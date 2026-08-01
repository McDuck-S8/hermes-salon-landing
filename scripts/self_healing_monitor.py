"""Self-Healing Monitor for Hermes cron jobs.

Checks all cron jobs via `hermes cron list`, parses the text output.
If a job has an error status or didn't run within 2x its interval,

> Revisit: when self-healing logic, error detection, or auto-fix routines change. Last touched: 2026-07-02.
attempts a restart via `hermes cron run {job_id}`.
Logs consecutive failures; after 3, prints an alert to stdout
(which the telegram-delivery cron will pick up).

Runs as no_agent cron job (every 15 min).
"""

import json
import logging
import os
import re
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

HERMES_HOME = Path(os.environ.get("HERMES_HOME", "D:/Portable_Soft/hermes"))
STATE_FILE = HERMES_HOME / "cron" / "self_healing_state.json"
LOG_FILE = HERMES_HOME / "logs" / "self_healing.log"
SELF_JOB_IDS = set()  # will be populated

LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[logging.FileHandler(str(LOG_FILE), encoding="utf-8"),
              logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger("self-healing")


def load_state() -> dict:
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return {}
    return {}


def save_state(state: dict) -> None:
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")


def run_hermes_cmd(*args: str) -> str:
    """Run `hermes <args>` and return stdout."""
    try:
        result = subprocess.run(
            ["hermes", *args],
            capture_output=True, text=True, timeout=30,
            cwd=str(HERMES_HOME)
        )
        return result.stdout + result.stderr
    except subprocess.TimeoutExpired:
        log.error("Timeout running hermes %s", " ".join(args))
        return ""
    except FileNotFoundError:
        log.error("hermes command not found in PATH")
        return ""
    except OSError as e:
        log.error("Error running hermes %s: %s", " ".join(args), e)
        return ""


def parse_cron_list(output: str) -> list:
    """Parse `hermes cron list` text output into job dicts.

    Output format (per job):
        abc123456789 [active]
            Name:      job-name
            Schedule:  every 15m
            Repeat:    infinity
            Next run:  2026-06-07T...
            Deliver:   local
            Script:    script.py
            Mode:      no-agent (...)
            Last run:  datetime  ok|error|(n/a)
    """
    jobs = []
    blocks = re.split(r'\n\s*\n', output)
    for block in blocks:
        block = block.strip()
        if not block:
            continue
        # First line: ID [status]
        m = re.match(r'^(\S+)\s+\[(\w+)\]', block)
        if not m:
            continue
        job_id = m.group(1)
        status = m.group(2)

        # Extract fields
        name = ""
        schedule = ""
        last_run_time = ""
        last_status = ""
        last_run_line = ""

        for line in block.split('\n'):
            line = line.strip()
            if line.startswith('Name:'):
                name = line.split('Name:', 1)[1].strip()
            elif line.startswith('Schedule:'):
                schedule = line.split('Schedule:', 1)[1].strip()
            elif line.startswith('Last run:'):
                last_run_line = line.split('Last run:', 1)[1].strip()

        # Parse last_run_line: "datetime  ok" or "datetime  error" or "(n/a)"
        if last_run_line and last_run_line != '(n/a)':
            parts = last_run_line.rsplit(' ', 1)
            last_run_time = parts[0].strip()
            if len(parts) > 1:
                last_status = parts[1].strip()

        jobs.append({
            "id": job_id,
            "name": name,
            "status": status,
            "schedule": schedule,
            "last_run_time": last_run_time,
            "last_status": last_status,
        })
    return jobs


def get_schedule_interval_minutes(schedule_str: str):
    """Estimate interval in minutes from schedule string like 'every 15m' or '0 2 * * *'."""
    if not schedule_str:
        return None
    m = re.match(r'every\s+(\d+)\s*m', schedule_str)
    if m:
        return int(m.group(1))
    m = re.match(r'every\s+(\d+)\s*h', schedule_str)
    if m:
        return int(m.group(1)) * 60
    # Cron pattern - common ones
    if re.match(r'\d+ \d+ \* \* \*', schedule_str):  # daily at X:Y
        return 1440
    if re.match(r'\d+ \* \* \* \*', schedule_str):  # hourly at :MM
        return 60
    if re.match(r'\*/\d+', schedule_str):  # */N
        h = re.match(r'\*/(\d+)', schedule_str)
        if h:
            return int(h.group(1)) * 60
    return None


def parse_datetime(dt_str: str):
    """Parse a datetime string, handling multiple formats."""
    if not dt_str:
        return None
    # Strip trailing timezone info like +0300 or +00:00 if present
    clean = dt_str.strip()
    try:
        dt = datetime.fromisoformat(clean)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except (ValueError, TypeError):
        pass
    # Try without timezone suffix
    clean_no_tz = re.sub(r'[+-]\d{2}:?\d{2}$', '', clean)
    try:
        dt = datetime.fromisoformat(clean_no_tz)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except (ValueError, TypeError):
        return None


def main():
    # Heartbeat: module alive
    try:
        from chain_heartbeat import beat
        beat("self_healing_monitor")
    except ImportError:
        pass

    state = load_state()
    now = datetime.now(timezone.utc)

    output = run_hermes_cmd("cron", "list")
    jobs = parse_cron_list(output)

    if not jobs:
        log.warning("No cron jobs found or failed to parse output")
        print("[ALERT] Self-healing: no cron jobs parsed -- possible scheduler issue")
        return

    # Track self-healing-monitor job ID to skip
    global SELF_JOB_IDS
    SELF_JOB_IDS = {j["id"] for j in jobs if "self-healing" in j["name"]}

    alerts = []
    for job in jobs:
        jid = job["id"]
        jname = job["name"]

        # Skip self
        if jid in SELF_JOB_IDS:
            continue

        if job["status"] != "active":
            log.warning("Job %s (%s) status is '%s' -- not active", jid, jname, job["status"])
            continue  # Don't restart paused jobs

        if job["last_status"] == "error" or "exit code" in job.get("last_status", "").lower():
            # Job errored -- needs restart
            conde = state.get(jid, 0) + 1
            state[jid] = conde
            if conde >= 3:
                alert = f"[ALERT] Job {jname} ({jid}) failed {conde}x consecutively!"
                log.error(alert)
                alerts.append(alert)
                state[jid] = 0  # Reset after alert
            else:
                log.warning("Job %s (%s) errored (failure #%d). Restarting...",
                            jid, jname, conde)

            # Restart
            try:
                result = subprocess.run(
                    ["hermes", "cron", "run", jid],
                    capture_output=True, text=True, timeout=15,
                    cwd=str(HERMES_HOME)
                )
                log.info("Restart triggered for %s: %s", jid, result.stdout.strip()[:200])
            except subprocess.TimeoutExpired:
                log.error("Timeout restarting %s", jid)
                state[jid] = state.get(jid, 0) + 1
            except (FileNotFoundError, OSError) as e:
                log.error("Error restarting %s: %s", jid, e)
                state[jid] = state.get(jid, 0) + 1

        elif job["last_run_time"]:
            # Check if stale (2x interval since last run)
            last_dt = parse_datetime(job["last_run_time"])
            interval = get_schedule_interval_minutes(job["schedule"])
            if last_dt and interval and interval > 0:
                stale_threshold = interval * 2
                age_min = (now - last_dt).total_seconds() / 60.0
                if age_min > stale_threshold and age_min > 30:  # >30 min grace
                    log.warning(
                        "Job %s (%s) stale: last run %.0f min ago (threshold: %.0f)",
                        jid, jname, age_min, stale_threshold
                    )
            # Reset consecutive failure counter on successful run
            if job["last_status"] == "ok" and jid in state:
                state[jid] = 0

    # Clean up stale state entries
    active_ids = {j["id"] for j in jobs}
    for jid in list(state.keys()):
        if jid not in active_ids:
            del state[jid]

    save_state(state)
    log.info("Self-healing check complete. %d jobs, %d alerts", len(jobs), len(alerts))

    if alerts:
        print("\n".join(alerts))


if __name__ == "__main__":
    main()

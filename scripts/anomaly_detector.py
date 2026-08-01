#!/usr/bin/env python3
"""
Red Light Anomaly Detector — one-shot: scan system for anomalies,
generate alerts, write to cache/red_alerts.json.

Catches:
  - Cron jobs with consecutive errors
  - Knowledge Cube domains with >30% failure rate
  - Sudden drops in activity
  - Stale scripts (not updated in 30+ days)
  - Memory gaps (no new knowledge in 24h)
  - Disk pressure
"""

import json
import os
import sys
import time
from pathlib import Path
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any

# ── Paths ────────────────────────────────────────────────────────────────────

SCRIPT_DIR = Path(__file__).resolve().parent
HERMES_HOME = SCRIPT_DIR.parent
CACHE_DIR = HERMES_HOME / "cache"
CRON_DIR = HERMES_HOME / "cron"
DB_PATH = CACHE_DIR / "knowledge_cube.db"
ALERTS_FILE = CACHE_DIR / "red_alerts.json"
CRON_JOBS_FILE = CRON_DIR / "jobs.json"

import sqlite3


# ── Helpers ──────────────────────────────────────────────────────────────────

def _load_json(path: Path, default=None):
    if not path.exists():
        return default if default is not None else {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default if default is not None else {}


def _db_query(db_path: Path, sql: str, params=()) -> List[Dict]:
    if not db_path.exists():
        return []
    try:
        conn = sqlite3.connect(str(db_path), timeout=5)
        conn.execute("PRAGMA journal_mode=WAL")
        conn.row_factory = sqlite3.Row
        rows = [dict(r) for r in conn.execute(sql, params).fetchall()]
        conn.close()
        return rows
    except Exception:
        return []


# ── Detectors ────────────────────────────────────────────────────────────────

def detect_cron_anomalies() -> List[Dict]:
    """Find cron jobs with consecutive errors or stale runs."""
    alerts = []
    jobs_data = _load_json(CRON_JOBS_FILE, {"jobs": []})
    jobs = jobs_data.get("jobs", [])
    now = datetime.now(timezone.utc)

    for j in jobs:
        name = j.get("name", "unknown")
        enabled = j.get("enabled", True)

        if not enabled:
            continue

        # Check for errors
        last_error = j.get("last_error", "")
        last_status = j.get("last_status", "")
        error_count = j.get("error_count", 0)

        if error_count >= 3:
            alerts.append({
                "type": "cron_consecutive_errors",
                "severity": "critical",
                "source": f"cron/{name}",
                "message": f"Cron job '{name}' has {error_count} consecutive errors",
                "detail": last_error[:200] if last_error else "unknown error",
                "detected_at": now.isoformat(),
            })

        # Check for stale jobs (no run in 72h for enabled jobs)
        last_run = j.get("last_run_at")
        if last_run:
            try:
                lr = datetime.fromisoformat(last_run.replace("Z", "+00:00"))
                hours_ago = (now - lr).total_seconds() / 3600
                schedule = j.get("schedule", {})
                if isinstance(schedule, dict):
                    kind = schedule.get("kind", "")
                    if kind == "interval" and hours_ago > 72:
                        alerts.append({
                            "type": "cron_stale",
                            "severity": "warning",
                            "source": f"cron/{name}",
                            "message": f"Cron job '{name}' last ran {hours_ago:.0f}h ago (expected every few hours)",
                            "detected_at": now.isoformat(),
                        })
            except Exception:
                pass

    return alerts


def detect_knowledge_anomalies() -> List[Dict]:
    """Find domains with high failure rates or sudden drops."""
    alerts = []

    # Domain failure rates
    rows = _db_query(DB_PATH,
        "SELECT axis_domain, axis_outcome, COUNT(*) as cnt "
        "FROM experiences GROUP BY axis_domain, axis_outcome"
    )
    if not rows:
        return alerts

    # Group by domain
    domains: Dict[str, Dict[str, int]] = {}
    for r in rows:
        d = r.get("axis_domain", "unknown") or "unknown"
        o = r.get("axis_outcome", "unknown") or "unknown"
        if d not in domains:
            domains[d] = {}
        domains[d][o] = r["cnt"]

    for domain, outcomes in domains.items():
        total = sum(outcomes.values())
        failures = outcomes.get("failure", 0)
        if total < 5:
            continue
        fail_rate = failures / total
        if fail_rate > 0.3:
            alerts.append({
                "type": "high_failure_rate",
                "severity": "critical",
                "source": f"kc/domain/{domain}",
                "message": f"Domain '{domain}' has {fail_rate:.0%} failure rate ({failures}/{total})",
                "detected_at": datetime.now(timezone.utc).isoformat(),
            })

    # Check if knowledge is growing (compare last 24h vs previous 24h)
    now = datetime.now(timezone.utc)
    yesterday = (now - timedelta(hours=24)).isoformat()
    two_days = (now - timedelta(hours=48)).isoformat()

    recent = _db_query(DB_PATH,
        "SELECT COUNT(*) as cnt FROM experiences WHERE ts > ?", (yesterday,))
    older = _db_query(DB_PATH,
        "SELECT COUNT(*) as cnt FROM experiences WHERE ts > ? AND ts <= ?", (two_days, yesterday))

    recent_count = recent[0]["cnt"] if recent else 0
    older_count = older[0]["cnt"] if older else 0

    if recent_count == 0 and older_count > 0:
        alerts.append({
            "type": "knowledge_stagnation",
            "severity": "warning",
            "source": "kc/growth",
            "message": f"No new knowledge entries in last 24h (previous 24h had {older_count})",
            "detected_at": now.isoformat(),
        })

    return alerts


def detect_disk_anomaly() -> List[Dict]:
    """Check disk space pressure."""
    alerts = []
    import shutil
    try:
        usage = shutil.disk_usage("D:/")
        free_pct = usage.free / usage.total
        if free_pct < 0.05:
            alerts.append({
                "type": "disk_critical",
                "severity": "critical",
                "source": "system/disk",
                "message": f"Disk D: only {free_pct:.1%} free ({usage.free // (1024**3)}GB)",
                "detected_at": datetime.now(timezone.utc).isoformat(),
            })
        elif free_pct < 0.10:
            alerts.append({
                "type": "disk_warning",
                "severity": "warning",
                "source": "system/disk",
                "message": f"Disk D: {free_pct:.1%} free ({usage.free // (1024**3)}GB)",
                "detected_at": datetime.now(timezone.utc).isoformat(),
            })
    except Exception:
        pass
    return alerts


def detect_script_anomalies() -> List[Dict]:
    """Find scripts that haven't been updated in 30+ days but are referenced by cron."""
    alerts = []
    scripts_dir = HERMES_HOME / "scripts"
    now = datetime.now(timezone.utc)

    jobs_data = _load_json(CRON_JOBS_FILE, {"jobs": []})
    referenced_scripts = set()
    for j in jobs_data.get("jobs", []):
        s = j.get("script", "")
        if s:
            referenced_scripts.add(s.split("/")[-1].split("\\")[-1])

    if not scripts_dir.exists():
        return alerts

    for script in scripts_dir.glob("*.py"):
        if script.name not in referenced_scripts:
            continue
        try:
            mtime = datetime.fromtimestamp(script.stat().st_mtime, tz=timezone.utc)
            days_old = (now - mtime).days
            if days_old > 30:
                alerts.append({
                    "type": "script_stale",
                    "severity": "info",
                    "source": f"scripts/{script.name}",
                    "message": f"Script '{script.name}' last modified {days_old} days ago",
                    "detected_at": now.isoformat(),
                })
        except Exception:
            pass

    return alerts


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    # Heartbeat: module alive
    try:
        from chain_heartbeat import beat
        beat("anomaly_detector")
    except ImportError:
        pass

    print(f"[RedAlert] {datetime.now().isoformat()} — scanning")

    all_alerts = []
    all_alerts.extend(detect_cron_anomalies())
    all_alerts.extend(detect_knowledge_anomalies())
    all_alerts.extend(detect_disk_anomaly())
    all_alerts.extend(detect_script_anomalies())

    # Sort by severity
    severity_order = {"critical": 0, "warning": 1, "info": 2}
    all_alerts.sort(key=lambda a: severity_order.get(a.get("severity", "info"), 9))

    # Filter: only critical and warning for output
    actionable = [a for a in all_alerts if a.get("severity") in ("critical", "warning")]

    print(f"[RedAlert] Found {len(all_alerts)} alerts ({len(actionable)} actionable)")

    for alert in all_alerts:
        sev = alert["severity"].upper()
        print(f"  [{sev}] {alert['message']}")

    # Save
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "total_alerts": len(all_alerts),
        "actionable": len(actionable),
        "alerts": all_alerts,
    }

    existing = _load_json(ALERTS_FILE, [])
    if not isinstance(existing, list):
        existing = []
    existing.append(entry)
    if len(existing) > 100:
        existing = existing[-100:]

    with open(ALERTS_FILE, "w", encoding="utf-8") as f:
        json.dump(existing, f, ensure_ascii=False, indent=2)

    print(f"[RedAlert] Saved to {ALERTS_FILE}")

    # Exit code: 1 if critical alerts, 0 otherwise
    has_critical = any(a["severity"] == "critical" for a in all_alerts)
    sys.exit(1 if has_critical else 0)


if __name__ == "__main__":
    main()

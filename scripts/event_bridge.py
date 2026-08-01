#!/usr/bin/env python3
"""
Event Bridge — the missing link between sensors and actions.


> Revisit: when event bridge logic, external integrations, or event routing changes. Last touched: 2026-07-02.
Sensors detect → event_bridge writes to queue → cron picks up on_event jobs.

This is what makes the system EVENT-DRIVEN instead of time-based.
"""
import json
import os
import sys
import time
from pathlib import Path
from datetime import datetime, timezone

HERMES = Path(__file__).resolve().parent.parent
CACHE = HERMES / "cache"
EVENT_QUEUE = CACHE / "event_queue.jsonl"
CRON_JOBS = HERMES / "cron" / "jobs.json"

# Map sensor events to cron event triggers
EVENT_MAP = {
    "error": "error_logged",
    "error_spike": "error_logged",
    "new_session": "session_completed",
    "session_end": "session_completed",
    "file_changed": "file_changed",
    "file_modified": "file_changed",
    "user_message": "user_message",
    "goal_completed": "goal_updated",
    "goal_changed": "goal_updated",
    "knowledge_added": "knowledge_added",
    "knowledge_new": "knowledge_added",
    "action_done": "action_completed",
    "action_completed": "action_completed",
    "result_ready": "result_available",
}


def push_event(event_type: str, detail: str = "", data: dict = None):
    """Push an event to the queue. Called by sensors, daemons, any code."""
    CACHE.mkdir(parents=True, exist_ok=True)
    entry = {
        "event_type": event_type,
        "trigger": EVENT_MAP.get(event_type, event_type),
        "detail": detail,
        "data": data or {},
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    with open(EVENT_QUEUE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return entry


def drain_queue() -> list[dict]:
    """Read all pending events and find matching cron jobs."""
    if not EVENT_QUEUE.exists():
        return []

    events = []
    with open(EVENT_QUEUE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                events.append(json.loads(line))
            except json.JSONDecodeError:
                pass

    if not events:
        return []

    # Find matching on_event jobs
    if not CRON_JOBS.exists():
        return events

    with open(CRON_JOBS, "r", encoding="utf-8") as f:
        jobs_data = json.load(f)

    matched = []
    for event in events:
        trigger = event.get("trigger", "")
        for job in jobs_data.get("jobs", []):
            if not job.get("enabled", False):
                continue
            schedule = job.get("schedule", {})
            if isinstance(schedule, dict) and schedule.get("kind") == "event":
                job_trigger = schedule.get("trigger", "").split("→")[0].strip()
                if job_trigger == trigger:
                    matched.append({
                        "event": event,
                        "job": job.get("name", job.get("id", "?")),
                        "job_id": job.get("id", job.get("job_id", "?")),
                    })

    return matched


def fire_jobs(matched: list[dict]) -> list[dict]:
    """Actually fire matched cron jobs via hermes CLI."""
    import subprocess

    results = []
    for m in matched:
        job_id = m["job_id"]
        try:
            r = subprocess.run(
                ["hermes", "cron", "run", str(job_id)],
                capture_output=True, text=True, timeout=30,
                cwd=str(HERMES),
            )
            results.append({
                "job": m["job"],
                "event": m["event"]["event_type"],
                "success": r.returncode == 0,
                "output": r.stdout[:200] if r.stdout else r.stderr[:200],
            })
        except Exception as e:
            results.append({
                "job": m["job"],
                "event": m["event"]["event_type"],
                "success": False,
                "error": str(e)[:200],
            })

    return results


def process():
    """One cycle: drain queue → match → fire."""
    matched = drain_queue()
    if not matched:
        return {"processed": 0, "events": 0}

    results = fire_jobs(matched)

    # Clear processed events (truncate file)
    if EVENT_QUEUE.exists():
        EVENT_QUEUE.write_text("", encoding="utf-8")

    return {
        "processed": len(results),
        "events": len(matched),
        "results": results,
    }


def watch(interval: int = 10):
    """Continuous watch mode — the EVENT HEARTBEAT."""
    print(f"Event Bridge — watching every {interval}s")
    while True:
        try:
            result = process()
            if result["processed"] > 0:
                for r in result.get("results", []):
                    status = "✅" if r.get("success") else "❌"
                    print(f"  {status} {r['job']} <- {r['event']}")
        except KeyboardInterrupt:
            print("\nBridge stopped.")
            break
        except Exception as e:
            print(f"Bridge error: {e}")
        time.sleep(interval)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "push":
        event_type = sys.argv[2] if len(sys.argv) > 2 else "manual"
        detail = sys.argv[3] if len(sys.argv) > 3 else ""
        result = push_event(event_type, detail)
        print(json.dumps(result, indent=2))
    elif len(sys.argv) > 1 and sys.argv[1] == "watch":
        interval = int(sys.argv[2]) if len(sys.argv) > 2 else 10
        watch(interval)
    else:
        result = process()
        print(json.dumps(result, indent=2))

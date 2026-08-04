#!/usr/bin/env python3
"""
Event Processor — central event-driven dispatcher.

Reads events from chain_heartbeat (level 1) and dispatches to handlers.
Runs as a daemon: watches for new events, processes them, acknowledges.
No cron — event-driven via polling with exponential backoff.
"""
import json
import os
import sys
import time
import subprocess
import sqlite3
from pathlib import Path
from datetime import datetime

HERMES_HOME = Path(__file__).resolve().parent.parent
CACHE_DIR = HERMES_HOME / "cache"
STATE_FILE = CACHE_DIR / "chain_heartbeat.json"
PROCESSED_FILE = CACHE_DIR / "event_processor_state.json"

sys.path.insert(0, str(HERMES_HOME / "scripts"))
from chain_heartbeat import EVENTS, _load

# Register heartbeat
try:
    from chain_heartbeat import beat
    beat("event_processor")
except Exception:
    pass

# Event → handler mapping (DIRECTIVE: every event must have a subscriber)
HANDLERS = {
    "research_queued": {
        "cmd": ["python", "scripts/researcher_agent.py", "--batch", "--limit", "5"],
        "description": "Process pending research tasks"
    },
    "new_suggestions_ready": {
            "cmd": ["python", "scripts/autonomous_agent.py"],
            "description": "Apply improvement suggestions (real patcher: autonomous_agent._action_apply_suggestions)"
        },
    "knowledge_added": {
        "cmd": ["python", "-c", """
import sys
sys.path.insert(0, 'scripts')
from event_evolution import process_pending_events
result = process_pending_events()
print(f'Processed: {result}')
"""],
        "description": "Process pending KC events for Crystal"
    },
    "architecture_scan_complete": {
        "cmd": ["python", "scripts/architecture_model.py"],
        "description": "Update architecture model",
        "timeout": 120
    },
}

# Events that are alert-only (no handler needed, but must be documented)
ALERT_ONLY = {"cron_job_died", "external_service_down", "user_correction"}

# Verify every expected event has a handler
EXPECTED_EVENTS = {e for e, c in EVENTS.items() if c.get("expected_interval_s") is not None}
UNHANDLED = EXPECTED_EVENTS - set(HANDLERS.keys()) - ALERT_ONLY
if UNHANDLED:
    print(f"WARNING: Events without handlers: {UNHANDLED}")
    # Constitutional violation - log but continue


def load_processed():
    if PROCESSED_FILE.exists():
        try:
            return json.loads(PROCESSED_FILE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return {"last_event_counts": {}, "last_check": 0}
    return {"last_event_counts": {}, "last_check": 0}


def save_processed(state):
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_FILE.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")


def get_event_counts(state):
    """Extract event beat counts from heartbeat state."""
    beats = state.get("beats", {})
    return {name: beats.get(name, {}).get("count", 0) for name in HANDLERS.keys()}


def dispatch_event(event_name: str, handler_info: dict) -> bool:
    """Run handler for event. Returns True if successful."""
    print(f"[{datetime.now().isoformat()}] Dispatching {event_name}: {handler_info['description']}")
    try:
        timeout = handler_info.get("timeout", 300)
        result = subprocess.run(
            handler_info["cmd"],
            cwd=HERMES_HOME,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        if result.returncode == 0:
            print(f"  ✅ {event_name} done")
            if result.stdout.strip():
                print(f"  stdout: {result.stdout.strip()[:200]}")
        else:
            print(f"  ❌ {event_name} failed (exit {result.returncode})")
            if result.stderr.strip():
                print(f"  stderr: {result.stderr.strip()[:300]}")
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print(f"  ⏱️ {event_name} timeout")
        return False
    except Exception as e:
        print(f"  💥 {event_name} error: {e}")
        return False


def main():
    print(f"=== EVENT PROCESSOR STARTED ===")
    print(f"Watching events: {list(HANDLERS.keys())}")
    print(f"Alert-only (no handler): {ALERT_ONLY}")
    if UNHANDLED:
        print(f"⚠️ CONSTITUTIONAL VIOLATION: Unhandled events: {UNHANDLED}")

    processed = load_processed()
    last_counts = processed.get("last_event_counts", {})

    # Exponential backoff for polling
    base_interval = 5  # seconds
    max_interval = 60
    interval = base_interval

    while True:
        try:
            # Load current heartbeat state
            hb_state = _load()
            current_counts = get_event_counts(hb_state)

            # Check for new events (count increased)
            for event_name, handler in HANDLERS.items():
                current = current_counts.get(event_name, 0)
                last = last_counts.get(event_name, 0)
                if current > last:
                    print(f"\n🔔 New event: {event_name} (count {last} → {current})")
                    # Run handler ONCE per event type per cycle (not N times for N deltas)
                    # Handler is idempotent - running once processes all pending
                    dispatch_event(event_name, handler)
                    last_counts[event_name] = current
                    interval = base_interval  # reset backoff on activity
                elif current < last:
                    # Counter reset (shouldn't happen with our atomic writes)
                    print(f"⚠️ Counter reset detected for {event_name}: {last} → {current}")
                    last_counts[event_name] = current

            # Batch trigger: force researcher_agent if ≥5 pending tasks (DIRECTIVE 0x52)
            # Check queue directly, independent of research_queued event
            try:
                rq_file = CACHE_DIR / "research_queue.json"
                if rq_file.exists():
                    rq = json.loads(rq_file.read_text(encoding="utf-8"))
                    pending_count = len([t for t in rq.get("tasks", []) if t.get("status") == "pending"])
                    if pending_count >= 5:
                        last_batch = processed.get("last_batch_trigger", 0)
                        if time.time() - last_batch > 60:  # min 60s between batch triggers
                            print(f"\n⚡ BATCH TRIGGER: {pending_count} pending research tasks")
                            dispatch_event("research_queued", HANDLERS["research_queued"])
                            # Sync state so delta detection works
                            hb_state = _load()
                            current = hb_state.get("beats", {}).get("research_queued", {}).get("count", 0)
                            last_counts["research_queued"] = current
                            processed["last_batch_trigger"] = time.time()
            except Exception:
                pass

            # Save state
            processed["last_event_counts"] = last_counts
            processed["last_check"] = time.time()
            save_processed(processed)

        except Exception as e:
            print(f"[ERROR] Event processor loop: {e}")

        # Sleep with backoff
        time.sleep(interval)
        interval = min(interval * 1.5, max_interval)


if __name__ == "__main__":
    # Single-shot mode for testing: --once
    if "--once" in sys.argv:
        hb_state = _load()
        current_counts = get_event_counts(hb_state)
        processed = load_processed()
        last_counts = processed.get("last_event_counts", {})

        for event_name, handler in HANDLERS.items():
            current = current_counts.get(event_name, 0)
            last = last_counts.get(event_name, 0)
            if current > last:
                # Run handler ONCE per event type (idempotent)
                dispatch_event(event_name, handler)
                last_counts[event_name] = current

        processed["last_event_counts"] = last_counts
        processed["last_check"] = time.time()
        save_processed(processed)
        print("=== EVENT PROCESSOR --once DONE ===")
    else:
        main()
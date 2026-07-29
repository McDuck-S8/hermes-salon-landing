#!/usr/bin/env python3
"""
Event Trigger System — replaces time-based polling with event-driven execution.

Problem: 44 cron jobs run on timers. If gateway dies, ALL die simultaneously.
Even when running: most jobs poll for something that rarely changes.
90% of executions return "nothing to do" — wasted tokens.

Solution: Jobs run WHEN something happens, not WHEN a timer fires.

Events:
  error_logged       → self-healing-monitor, anomaly-detector
  knowledge_added    → cube-categorizer, knowledge-gap-filler
  session_completed  → cube-session-ingester, memory-consolidation
  goal_updated       → proactive-executor, proactive-doer
  file_changed       → system-watcher
  boot_completed     → proactive-doer, reality-gate
  user_message       → event-trigger
  heartbeat          → hermes-heartbeat (only this stays timer-based)

Usage:
  # Trigger an event:
  python scripts/event_bus.py emit error_logged '{"script": "foo.py", "error": "timeout"}'
  
  # Check pending events:
  python scripts/event_bus.py pending
  
  # Process all pending events (called by heartbeat):
  python scripts/event_bus.py process
"""

import json
import sys
import os
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Unified config — single source of truth
# ---------------------------------------------------------------------------
sys.path.insert(0, str(Path(__file__).resolve().parent))
from hermes_config import HERMES_HOME, CACHE_DIR

EVENTS_FILE = CACHE_DIR / "event_bus.json"
JOBS_FILE = HERMES_HOME / "cron" / "jobs.json"

# Event -> Job mapping
# Each event triggers specific jobs instead of running ALL jobs on a timer
EVENT_JOB_MAP = {
    "error_logged": [
        "self-healing-monitor",
        "anomaly-detector"
    ],
    "knowledge_added": [
        "cube-categorizer",
        "knowledge-gap-filler"
    ],
    "session_completed": [
        "cube-session-ingester",
        "memory-consolidation",
        "dream-memory-consolidation"
    ],
    "goal_updated": [
        "proactive-executor",
        "proactive-doer"
    ],
    "file_changed": [
        "system-watcher"
    ],
    "boot_completed": [
        "proactive-doer",
        "self-assessment"
    ],
    "user_message": [
        "event-trigger"
    ],
    "action_completed": [
        "result-producer",
        "autonomous-agent"
    ],
    # These STAY timer-based (need periodic execution regardless of events):
    # heartbeat, morning-report, daily-report, trend-scout, etc.
}


def load_events() -> dict:
    if EVENTS_FILE.exists():
        try:
            return json.loads(EVENTS_FILE.read_text(encoding="utf-8"))
        except:
            pass
    return {"pending": [], "processed": [], "stats": {}}


def save_events(data: dict):
    EVENTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    EVENTS_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def emit(event_type: str, payload: dict = None):
    """Emit an event. Jobs mapped to this event will be triggered."""
    data = load_events()
    event = {
        "id": f"evt-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}",
        "type": event_type,
        "ts": datetime.now(timezone.utc).isoformat(),
        "payload": payload or {},
        "triggered_jobs": EVENT_JOB_MAP.get(event_type, [])
    }
    data["pending"].append(event)
    
    # Update stats
    data["stats"][event_type] = data["stats"].get(event_type, 0) + 1
    
    save_events(data)
    print(f"Emitted: {event_type}")
    print(f"  Triggers: {len(event['triggered_jobs'])} jobs")
    for job in event["triggered_jobs"]:
        print(f"    → {job}")
    return event


def process_events():
    """Process all pending events, run chains via chain_executor."""
    data = load_events()
    pending = data.get("pending", [])

    if not pending:
        print("No pending events.")
        return []

    # --- Session recall: обогащение событий историческим контекстом ---
    try:
        from session_recall import semantic_search
        for event in pending:
            event_type = event.get("type", "unknown")
            payload = event.get("payload", {})
            query = payload.get("text", event_type)
            if query and len(query) > 3:
                results = semantic_search(query, limit=2)
                if results:
                    event["historical_context"] = [
                        {"content": r["content"][:200], "score": r["score"]}
                        for r in results
                    ]
    except Exception:
        pass  # fallback если session_recall недоступен

    # --- Chain execution: classify + execute for each event ---
    try:
        from chain_executor import AdaptiveClassifier, execute_chain
        classifier = AdaptiveClassifier()
        chains_ran = 0
        for event in pending:
            event_type = event.get("type", "unknown")
            payload = event.get("payload", {})
            # Build input text from event type + payload
            input_text = payload.get("text", event_type)
            result = classifier.classify(input_text)
            chain_result = execute_chain(
                result["event_type"], result["severity"],
                result["chain"], result["confidence"], input_text,
            )
            chains_ran += 1
            print(f"  Chain [{event_type}]: {result['event_type']} "
                  f"[{result['severity']}] → "
                  f"{chain_result['steps_succeeded']}/{chain_result['steps_run']} steps")
        print(f"Chains executed: {chains_ran}")
    except Exception as e:
        print(f"Chain execution skipped: {e}")

    # --- Legacy: collect cron jobs to run ---
    jobs_to_run = set()
    for event in pending:
        for job_name in event.get("triggered_jobs", []):
            jobs_to_run.add(job_name)

    # Move pending to processed
    data["processed"].extend(pending)
    data["pending"] = []
    data["processed"] = data["processed"][-100:]

    save_events(data)

    print(f"Processed {len(pending)} events → {len(jobs_to_run)} cron jobs queued")
    return list(jobs_to_run)


def show_pending():
    """Show pending events."""
    data = load_events()
    pending = data.get("pending", [])
    stats = data.get("stats", {})
    
    print(f"Pending events: {len(pending)}")
    for evt in pending[-10:]:
        print(f"  [{evt['type']}] {evt['ts'][:19]} → {len(evt.get('triggered_jobs', []))} jobs")
    
    print(f"\nEvent stats (all time):")
    for etype, count in sorted(stats.items(), key=lambda x: -x[1]):
        print(f"  {etype}: {count}")


if __name__ == "__main__":
    args = sys.argv[1:]
    
    if not args:
        print("Usage:")
        print("  event_bus.py emit <event_type> [json_payload]")
        print("  event_bus.py pending")
        print("  event_bus.py process")
        print(f"\nKnown events: {', '.join(sorted(EVENT_JOB_MAP.keys()))}")
        sys.exit(0)
    
    cmd = args[0]
    
    if cmd == "emit":
        if len(args) < 2:
            print("Usage: event_bus.py emit <event_type> [json_payload]")
            sys.exit(1)
        event_type = args[1]
        payload = json.loads(args[2]) if len(args) > 2 else {}
        emit(event_type, payload)
    
    elif cmd == "pending":
        show_pending()
    
    elif cmd == "process":
        process_events()
    
    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)

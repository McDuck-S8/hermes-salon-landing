#!/usr/bin/env python3
"""Wrapper to run event_bus.py process for cron - lightweight version without session_recall."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from event_bus import load_events, save_events, DIRECT_EVENT_HANDLERS, EVENT_JOB_MAP

def process_events_lightweight():
    """Process all pending events without session_recall enrichment."""
    data = load_events()
    pending = data.get("pending", [])

    if not pending:
        print("No pending events.")
        return []

    # Run DIRECT handlers first (synchronously, no queue)
    for event in pending:
        event_type = event.get("type")
        if event_type in DIRECT_EVENT_HANDLERS:
            try:
                DIRECT_EVENT_HANDLERS[event_type](event)
            except Exception as e:
                print(f"  [WARN] DIRECT handler for {event_type} failed: {e}")

    # Clear pending
    data["pending"] = []
    save_events(data)

    return []

if __name__ == "__main__":
    process_events_lightweight()
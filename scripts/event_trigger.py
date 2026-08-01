#!/usr/bin/env python3
"""
Event Trigger — processes new events as they appear.
Lightweight: checks for unprocessed events in the event log.
"""
import json
from datetime import datetime
from pathlib import Path

HERMES = Path(__file__).resolve().parent.parent
LOG = HERMES / "cache" / "event_log.jsonl"

def main():
    try:
        from chain_heartbeat import beat
        beat("event_trigger")
    except ImportError:
        pass
    
    if not LOG.exists():
        return
    
    count = 0
    with open(LOG) as f:
        for line in f:
            try:
                ev = json.loads(line.strip())
                if not ev.get("processed", False):
                    count += 1
            except:
                pass
    
    if count > 0:
        print(json.dumps({
            "status": "events_pending",
            "count": count,
            "timestamp": datetime.now().isoformat()
        }))
        # Also process pending events from events.db
        _process_db_events()
    else:
        pass  # Silent — no output when nothing to do


def _process_db_events():
    """Process unprocessed evolution events."""
    try:
        import sys
        sys.path.insert(0, str(HERMES / "scripts"))
        from event_evolution import process_pending_events
        result = process_pending_events()
        if result.get("processed", 0) > 0:
            print(json.dumps({
                "status": "processed",
                "count": result["processed"],
                "errors": result.get("errors", 0),
                "timestamp": datetime.now().isoformat()
            }))
    except Exception as e:
        print(json.dumps({
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }))

if __name__ == "__main__":
    main()

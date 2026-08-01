#!/usr/bin/env python3
"""
emit_event — вызывается из любого скрипта для отправки события в event_bus.


> Revisit: when event emission, event types, or event-driven architecture changes. Last touched: 2026-07-02.
Использование:
    from emit_event import emit
    emit("error_logged", {"script": "foo.py", "error": str(e)})
    emit("session_completed", {"session_id": "abc", "messages": 42})
    emit("knowledge_added", {"domain": "coding", "count": 5})
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timezone

HERMES_HOME = Path(__file__).resolve().parent.parent
EVENTS_FILE = HERMES_HOME / "cache" / "event_bus.json"


def emit(event_type: str, payload: dict = None):
    """Отправляет событие. Вызывается из любого скрипта."""
    data = {"pending": [], "processed": [], "stats": {}}

    if EVENTS_FILE.exists():
        try:
            data = json.loads(EVENTS_FILE.read_text(encoding="utf-8"))
        except:
            pass

    event = {
        "id": f"evt-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S.%f')}",
        "type": event_type,
        "ts": datetime.now(timezone.utc).isoformat(),
        "payload": payload or {},
    }

    data["pending"].append(event)
    data["stats"][event_type] = data["stats"].get(event_type, 0) + 1

    # Храним последние 200 processed + все pending
    data["processed"] = data.get("processed", [])[-200:]

    EVENTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    EVENTS_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: emit_event.py <event_type> [json_payload]")
        sys.exit(1)

    event_type = sys.argv[1]
    payload = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}
    emit(event_type, payload)
    print(f"Emitted: {event_type}")

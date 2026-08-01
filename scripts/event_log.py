#!/usr/bin/env python3
"""
Lightweight event logger — fast, no heavy dependencies.


> Revisit: when event logging format, log storage, or event retrieval changes. Last touched: 2026-07-02.
Unlike hermes_hooks.py (which imports CoreEngine, MCP, LLM clients),
this writes directly to JSONL files. Use in cron scripts and quick tasks.

Usage:
    from event_log import log_task, log_error, log_correction
    
    log_task("Classified KC entries", "10 entries classified", ["classification"])
    log_error("API balance depleted", "Switched to free provider", "deepseek")
"""
import json
from pathlib import Path
from datetime import datetime

HERMES_HOME = Path(__file__).resolve().parent.parent
EVENT_LOG = HERMES_HOME / "cache" / "event_log.jsonl"


def _log(event_type: str, data: dict):
    """Append event to JSONL log."""
    CACHE_DIR = HERMES_HOME / "cache"
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    
    entry = {
        "timestamp": datetime.now().isoformat(),
        "type": event_type,
        **data,
    }
    
    with open(EVENT_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def log_task(description: str, result: str, tags: list[str] = None):
    """Log task completion."""
    _log("task_complete", {
        "description": description,
        "result": result,
        "tags": tags or [],
    })


def log_error(error: str, fix: str = "", context: str = ""):
    """Log error and fix."""
    _log("error", {
        "error": error,
        "fix": fix,
        "context": context,
    })


def log_correction(correction: str, context: str = ""):
    """Log user correction."""
    _log("correction", {
        "correction": correction,
        "context": context,
    })


def log_goal_progress(goal_id: str, progress: float, title: str = ""):
    """Log goal progress update."""
    _log("goal_progress", {
        "goal_id": goal_id,
        "progress": progress,
        "title": title,
    })


def log_classification(count: int, domains: dict = None):
    """Log KC classification results."""
    _log("classification", {
        "entries_classified": count,
        "domains": domains or {},
    })


def recent_events(limit: int = 10) -> list:
    """Read recent events."""
    if not EVENT_LOG.exists():
        return []
    
    events = []
    with open(EVENT_LOG, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    events.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    
    return events[-limit:]


if __name__ == "__main__":
    events = recent_events(20)
    print(f"Recent events: {len(events)}")
    for e in events:
        ts = e.get("timestamp", "?")[:16]
        etype = e.get("type", "?")
        desc = e.get("description", e.get("error", e.get("correction", "?")))[:60]
        print(f"  [{ts}] {etype}: {desc}")

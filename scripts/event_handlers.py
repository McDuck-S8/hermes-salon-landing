"""
Custom event handlers for the event-driven system (Ring of Rules).
Auto-loaded by EvolutionEngine.__init__() at boot.

Register handlers for event-driven actions instead of cron jobs.
Each handler receives (action_name: str, event: Event).
"""

import json
from datetime import datetime
from pathlib import Path


def register_handlers(engine):
    """Register all custom handlers with the engine."""

    engine.register_handler("fix_skill_findings", on_skill_issues)
    engine.register_handler("research_urls", on_research_urls)
    engine.register_handler("recover_service", on_service_down)
    engine.register_handler("income_pipeline", on_income_pipeline)

    print(f"  [event_handlers] 4 custom handlers registered: fix_skill_findings, research_urls, recover_service, income_pipeline")


def on_skill_issues(action: str, event):
    """Respond to skill security findings by flagging for remediation."""
    data = event.data or {}
    skill = data.get("skill_name", "unknown")
    count = data.get("findings_count", 0)
    print(f"  ⚡ EVENT: skill_issues_detected — {skill} ({count} findings)")
    # Record to a trigger queue (processed by next interactive session)
    _log_event("skill_issues", {"skill": skill, "count": count, "time": datetime.now().isoformat()})


def on_research_urls(action: str, event):
    """Respond to new research URLs by logging them for processing."""
    urls = event.data.get("urls", [])
    source = event.data.get("source", "unknown")
    print(f"  ⚡ EVENT: research_urls_provided — {len(urls)} URLs from {source}")
    for url in urls:
        _log_event("research_url", {"url": url, "source": source})


def on_service_down(action: str, event):
    """Respond to a service being detected as down."""
    service = event.data.get("service", "unknown")
    module = event.data.get("module", "unknown")
    print(f"  ⚡ EVENT: service_down — {service} (module: {module})")
    _log_event("service_down", {"service": service, "module": module, "time": datetime.now().isoformat()})


def on_income_pipeline(action: str, event):
    """Income pipeline — triggered by knowledge_added, processes YouTube → content."""
    data = event.data or {}
    kind = data.get("kind", "")
    source = data.get("source", "")

    # Only process YouTube knowledge events
    if "youtube" not in source and kind != "youtube_learning":
        return

    print(f"  ⚡ EVENT: income_pipeline — processing YouTube knowledge")
    # Log for the next interactive session to pick up
    _log_event("income_ready", {
        "source": source,
        "time": datetime.now().isoformat(),
        "action": "check_transcripts_and_generate",
    })


# ── internal helpers ──

HERMES = Path(__file__).resolve().parent.parent
EVENT_LOG = HERMES / "cache" / "event_queue.jsonl"
EVENT_LOG.parent.mkdir(exist_ok=True)


def _log_event(kind: str, data: dict):
    """Append to event queue (processed by interactive session)."""
    entry = {"kind": kind, "data": data, "ts": datetime.now().isoformat()}
    try:
        with open(EVENT_LOG, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except OSError:
        pass  # Silently skip if queue is locked/writable

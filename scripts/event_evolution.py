"""Event-driven self-evolution system.

Monitors events and triggers learning/optimization automatically.
No fixed schedule — reacts to what happens in the system.

Events:
  - task_complete: after successful task
  - error_occurred: after error/fix
  - skill_used: after skill usage
  - session_end: after session ends
  - knowledge_threshold: when knowledge grows
  - user_correction: when user corrects something
"""

import json
import os
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional
from dataclasses import dataclass, field


HERMES_HOME = Path(os.environ.get("HERMES_HOME", str(Path(__file__).resolve().parent.parent)))
EVENTS_DB = HERMES_HOME / "cache" / "events.db"
KNOWLEDGE_CUBE = HERMES_HOME / "cache" / "knowledge_cube.db"
LAVRA_KNOWLEDGE = HERMES_HOME / "data" / "lavra_knowledge.jsonl"
EVOLUTION_DIR = HERMES_HOME / "plugins" / "self-evolution"


@dataclass
class Event:
    """Represents a system event."""
    event_type: str
    timestamp: datetime
    data: dict = field(default_factory=dict)
    source: str = "system"
    priority: int = 5  # 1-10, higher = more important


class EventMonitor:
    """Monitors and records events."""
    
    def __init__(self):
        self._init_db()
    
    def _init_db(self):
        """Initialize events database."""
        EVENTS_DB.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(str(EVENTS_DB))
        conn.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_type TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                data TEXT,
                source TEXT DEFAULT 'system',
                priority INTEGER DEFAULT 5,
                processed INTEGER DEFAULT 0
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS triggers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_type TEXT NOT NULL,
                action TEXT NOT NULL,
                cooldown_hours INTEGER DEFAULT 24,
                last_triggered TEXT,
                enabled INTEGER DEFAULT 1
            )
        """)
        conn.commit()
        conn.close()
    
    def record(self, event: Event):
        """Record an event."""
        conn = sqlite3.connect(str(EVENTS_DB))
        conn.execute(
            "INSERT INTO events (event_type, timestamp, data, source, priority) VALUES (?, ?, ?, ?, ?)",
            (event.event_type, event.timestamp.isoformat(), json.dumps(event.data), event.source, event.priority)
        )
        conn.commit()
        conn.close()
    
    def get_unprocessed(self, event_type: Optional[str] = None) -> list[dict]:
        """Get unprocessed events."""
        conn = sqlite3.connect(str(EVENTS_DB))
        conn.row_factory = sqlite3.Row
        
        if event_type:
            rows = conn.execute(
                "SELECT * FROM events WHERE processed = 0 AND event_type = ? ORDER BY timestamp",
                (event_type,)
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM events WHERE processed = 0 ORDER BY priority DESC, timestamp"
            ).fetchall()
        
        conn.close()
        return [dict(r) for r in rows]
    
    def mark_processed(self, event_id: int):
        """Mark event as processed."""
        conn = sqlite3.connect(str(EVENTS_DB))
        conn.execute("UPDATE events SET processed = 1 WHERE id = ?", (event_id,))
        conn.commit()
        conn.close()


class EvolutionTrigger:
    """Decides when to trigger self-evolution based on events."""
    
    def __init__(self):
        self.monitor = EventMonitor()
        self._init_triggers()
    
    def _init_triggers(self):
        """Initialize default triggers."""
        conn = sqlite3.connect(str(EVENTS_DB))
        
        default_triggers = [
            ("task_complete", "capture_knowledge", 4),
            ("error_occurred", "capture_investigation", 2),
            ("skill_used", "evaluate_skill", 24),
            ("session_end", "session_summary", 4),
            ("knowledge_threshold", "optimize_knowledge", 48),
            ("user_correction", "capture_pattern", 12),
        ]
        
        for event_type, action, cooldown in default_triggers:
            exists = conn.execute(
                "SELECT id FROM triggers WHERE event_type = ? AND action = ?",
                (event_type, action)
            ).fetchone()
            
            if not exists:
                conn.execute(
                    "INSERT INTO triggers (event_type, action, cooldown_hours) VALUES (?, ?, ?)",
                    (event_type, action, cooldown)
                )
        
        conn.commit()
        conn.close()
    
    def should_trigger(self, event_type: str) -> list[str]:
        """Check if any actions should be triggered for this event type."""
        conn = sqlite3.connect(str(EVENTS_DB))
        conn.row_factory = sqlite3.Row
        
        triggers = conn.execute(
            "SELECT * FROM triggers WHERE event_type = ? AND enabled = 1",
            (event_type,)
        ).fetchall()
        
        conn.close()
        
        actions_to_trigger = []
        now = datetime.now()
        
        for trigger in triggers:
            trigger = dict(trigger)
            last_triggered = trigger.get("last_triggered")
            cooldown_hours = trigger.get("cooldown_hours", 24)
            
            if last_triggered:
                last_dt = datetime.fromisoformat(last_triggered)
                if now - last_dt < timedelta(hours=cooldown_hours):
                    continue
            
            actions_to_trigger.append(trigger["action"])
        
        return actions_to_trigger
    
    def record_trigger(self, event_type: str, action: str):
        """Record that a trigger was fired."""
        conn = sqlite3.connect(str(EVENTS_DB))
        conn.execute(
            "UPDATE triggers SET last_triggered = ? WHERE event_type = ? AND action = ?",
            (datetime.now().isoformat(), event_type, action)
        )
        conn.commit()
        conn.close()


class EvolutionEngine:
    """Executes evolution actions based on triggers."""
    
    def __init__(self):
        self.monitor = EventMonitor()
        self.trigger = EvolutionTrigger()
    
    def process_event(self, event: Event):
        """Process an event and trigger appropriate actions."""
        # Record the event
        self.monitor.record(event)
        
        # Get the event ID from the record
        conn = sqlite3.connect(str(EVENTS_DB))
        conn.row_factory = sqlite3.Row
        row = conn.execute(
            "SELECT id FROM events WHERE event_type = ? AND processed = 0 ORDER BY id DESC LIMIT 1",
            (event.event_type,)
        ).fetchone()
        conn.close()
        
        if not row:
            return
        
        event_id = row["id"]
        
        # Check what actions to trigger
        actions = self.trigger.should_trigger(event.event_type)
        
        for action in actions:
            self._execute_action(action, event)
            self.trigger.record_trigger(event.event_type, action)
        
        # Mark event as processed
        self.monitor.mark_processed(event_id)
    
    def _execute_action(self, action: str, event: Event):
        """Execute an evolution action."""
        handlers = {
            "capture_knowledge": self._capture_knowledge,
            "capture_investigation": self._capture_investigation,
            "evaluate_skill": self._evaluate_skill,
            "session_summary": self._session_summary,
            "optimize_knowledge": self._optimize_knowledge,
            "capture_pattern": self._capture_pattern,
        }
        
        handler = handlers.get(action)
        if handler:
            try:
                handler(event)
            except Exception as e:
                print(f"Error executing {action}: {e}")
    
    def _capture_knowledge(self, event: Event):
        """Capture knowledge from successful task completion."""
        import sys
        sys.path.insert(0, str(HERMES_HOME / "plugins" / "self-evolution"))
        try:
            from evolution.core.knowledge import capture_knowledge
        except ImportError:
            print(f"  [WARN] self-evolution plugin not available, skipping knowledge capture")
            return
        content = event.data.get("content", "")
        tags = event.data.get("tags", [])
        area = ", ".join(tags) if tags else ""
        if content:
            capture_knowledge(
                prefix="LEARNED",
                content=content,
                area=area,
            )
            print(f"  Captured knowledge from task")

    def _capture_investigation(self, event: Event):
        """Capture investigation from error/fix events."""
        import sys
        sys.path.insert(0, str(HERMES_HOME / "plugins" / "self-evolution"))
        try:
            from evolution.core.knowledge import capture_knowledge
        except ImportError:
            print(f"  [WARN] self-evolution plugin not available, skipping investigation")
            return
        error = event.data.get("error", "")
        fix = event.data.get("fix", "")
        tags = event.data.get("tags", [])
        area = ", ".join(tags) if tags else ""
        if error:
            capture_knowledge(
                prefix="ERROR",
                content=f"Error: {error}",
                area=area,
                symptom=error,
                solution=fix,
            )
            print(f"  Captured investigation from error")

    def _evaluate_skill(self, event: Event):
        """Evaluate skill usage from skill_used events."""
        skill_name = event.data.get("skill_name", "unknown")
        success = event.data.get("success", True)
        print(f"  Skill '{skill_name}' used, success={success}")

    def _session_summary(self, event: Event):
        """Summarize session end."""
        session_id = event.data.get("session_id", "unknown")
        summary = event.data.get("summary", "")
        print(f"  Session {session_id} ended: {summary[:100]}")

    def _optimize_knowledge(self, event: Event):
        """Trigger knowledge optimization when threshold crossed."""
        print(f"  Knowledge threshold triggered — optimization needed")

    def _capture_pattern(self, event: Event):
        """Capture user correction pattern."""
        correction = event.data.get("correction", "")
        context = event.data.get("context", "")
        print(f"  User correction: {correction[:100]} (context: {context[:50]})")

# Global instance
_engine = None

def get_engine() -> EvolutionEngine:
    """Get or create the evolution engine."""
    global _engine
    if _engine is None:
        _engine = EvolutionEngine()
    return _engine


def emit_event(event_type: str, data: dict = None, source: str = "system", priority: int = 5):
    """Emit an event to the evolution system."""
    engine = get_engine()
    event = Event(
        event_type=event_type,
        timestamp=datetime.now(),
        data=data or {},
        source=source,
        priority=priority,
    )
    engine.process_event(event)


# Convenience functions for common events

def on_task_complete(content: str, tags: list[str] = None, source: str = "agent", verified: bool = False, evidence: str = ""):
    """Call after successful task completion."""
    emit_event("task_complete", {
        "content": content, 
        "tags": tags or [], 
        "source": source,
        "verified": verified,
        "evidence": evidence
    })

def on_error(error: str, fix: str = "", tags: list[str] = None, source: str = "agent"):
    """Call after error and fix."""
    emit_event("error_occurred", {"error": error, "fix": fix, "tags": tags or [], "source": source})

def on_skill_used(skill_name: str, skill_path: str = "", success: bool = True):
    """Call after skill usage."""
    emit_event("skill_used", {"skill_name": skill_name, "skill_path": skill_path, "success": success})

def on_session_end(session_id: str, summary: str = ""):
    """Call at session end."""
    emit_event("session_end", {"session_id": session_id, "summary": summary})

def on_user_correction(correction: str, context: str = ""):
    """Call when user corrects something."""
    emit_event("user_correction", {"correction": correction, "context": context})


def process_pending_events() -> dict:
    """Process all unprocessed events from events.db.
    
    Gets events with processed=0, runs their triggers, marks processed=1.
    Returns summary dict with counts.
    """
    engine = get_engine()
    unprocessed = engine.monitor.get_unprocessed()
    
    processed_count = 0
    error_count = 0
    errors = []
    
    for evt_row in unprocessed:
        event_id = evt_row["id"]
        event_type = evt_row["event_type"]
        data_raw = evt_row.get("data", "{}")
        try:
            data = json.loads(data_raw) if data_raw else {}
        except (json.JSONDecodeError, TypeError):
            data = {}
        
        event = Event(
            event_type=event_type,
            timestamp=datetime.fromisoformat(evt_row["timestamp"]),
            data=data,
            source=evt_row.get("source", "system"),
            priority=evt_row.get("priority", 5),
        )
        
        try:
            # Check what actions to trigger
            actions = engine.trigger.should_trigger(event_type)
            
            for action in actions:
                engine._execute_action(action, event)
                engine.trigger.record_trigger(event_type, action)
            
            engine.monitor.mark_processed(event_id)
            processed_count += 1
            print(f"  [OK] event #{event_id} ({event_type}) -> {actions or 'no trigger'}")
        except Exception as e:
            error_count += 1
            errors.append({"event_id": event_id, "error": str(e)})
            print(f"  [ERR] event #{event_id} ({event_type}): {e}")
    
    summary = {
        "total": len(unprocessed),
        "processed": processed_count,
        "errors": error_count,
        "error_details": errors,
    }
    print(f"\nProcessed: {processed_count}/{len(unprocessed)}, errors: {error_count}")
    return summary


if __name__ == "__main__":
    # Demo: emit some events
    print("Event-driven self-evolution system initialized")
    print(f"Events DB: {EVENTS_DB}")
    print(f"Knowledge Cube: {KNOWLEDGE_CUBE}")
    
    # Example usage
    on_task_complete(
        "Successfully deployed salon bot with aiogram3",
        tags=["salon-bot", "deployment", "aiogram3"],
        source="agent"
    )
    
    on_error(
        error="FTS5 index corrupted in state.db",
        fix="Recreated database from scratch with fresh FTS5 index",
        tags=["database", "fts5", "fix"],
        source="agent"
    )
    
    print("\nEvents recorded. Check events.db for details.")
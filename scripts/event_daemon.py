#!/usr/bin/env python3
"""
event_daemon.py — Единый цикл событий.

Заменяет все cron jobs. Без таймеров, без расписаний.
Просто: жди событие → обработай → жди дальше.

Архитектура:
```
  events.db ──> poll (5s) ──┐
  time:tick ──> gen (60s) ──┤→ Queue ──> Handler ──> emit_event/action
  signal ─────> handler ────┘
```

Правила:
- Никакого cron. Никаких расписаний.
- Время — это событие: time:tick каждые 60с, из него handler решает что делать.
- Внешние события — из events.db (emit_event пишет туда).
- Молчит когда здоров. Пишет в stdout только когда делает что-то.

Managed by process_supervisor (auto-restart на падение).
"""

import json
import os
import signal
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Optional
from collections import defaultdict

# ── paths ─────────────────────────────────────────────────────────────
HERMES_HOME = Path(__file__).resolve().parent.parent
SCRIPTS = HERMES_HOME / "scripts"
CACHE = HERMES_HOME / "cache"
sys.path.insert(0, str(SCRIPTS))

HEARTBEAT_FILE = CACHE / "event_daemon.heartbeat"
PID_FILE = CACHE / "event_daemon.pid"

POLL_INTERVAL = 5        # сек — частота проверки events.db
TICK_INTERVAL = 60       # сек — time:tick
HEARTBEAT_INTERVAL = 30  # сек — запись heartbeat


# ── Event Loop ────────────────────────────────────────────────────────

class EventLoop:
    """Один цикл, чтобы править всеми cron jobs."""

    def __init__(self):
        self.running = False
        self.handlers: dict[str, list[Callable]] = defaultdict(list)
        self.queue: list[tuple[str, dict]] = []
        self._last_tick = 0.0
        self._last_heartbeat = 0.0
        self._last_event_id = 0

    # ── handler registration ──

    def on(self, event_type: str):
        """Decorator: register handler for event type."""
        def decorator(fn):
            self.handlers[event_type].append(fn)
            return fn
        return decorator

    def register(self, event_type: str, fn: Callable):
        """Register handler for event type."""
        self.handlers[event_type].append(fn)

    def register_handler(self, action: str, handler: Callable):
        """Compatibility: register directly with EvolutionEngine."""
        try:
            from event_evolution import get_engine
            eng = get_engine()
            if hasattr(eng, 'register_handler'):
                eng.register_handler(action, handler)
        except Exception:
            pass

    # ── emit (to self, not to events.db — that's for external callers) ──

    def emit(self, event_type: str, data: dict = None):
        self.queue.append((event_type, data or {}))

    # ── sources ──

    def _poll_events_db(self):
        """Check events.db for new unprocessed events."""
        try:
            from event_evolution import get_engine
            engine = get_engine()
            unprocessed = engine.monitor.get_unprocessed()
            for row in unprocessed:
                eid = row["id"]
                if eid <= self._last_event_id:
                    continue
                self._last_event_id = eid
                data = {}
                try:
                    data = json.loads(row.get("data", "{}"))
                except (json.JSONDecodeError, TypeError):
                    pass
                self.queue.append((row["event_type"], {
                    **data,
                    "_event_id": eid,
                    "_source": row.get("source", "events_db"),
                }))
        except Exception as exc:
            # Молчим — events.db может быть заблокирован
            pass

    def _generate_tick(self):
        """Generate time:tick every TICK_INTERVAL."""
        now = time.time()
        if now - self._last_tick >= TICK_INTERVAL:
            self._last_tick = now
            dt = datetime.now()
            self.queue.append(("time:tick", {
                "hour": dt.hour,
                "minute": dt.minute,
                "second": dt.second,
                "weekday": dt.weekday(),
                "day": dt.day,
                "month": dt.month,
                "unix": int(now),
            }))

    def _heartbeat(self):
        """Write heartbeat for supervisor."""
        now = time.time()
        if now - self._last_heartbeat >= HEARTBEAT_INTERVAL:
            self._last_heartbeat = now
            hb = {
                "pid": os.getpid(),
                "ts": datetime.now(timezone.utc).isoformat(),
                "status": "alive",
                "queue_depth": len(self.queue),
                "handler_count": len(self.handlers),
            }
            CACHE.mkdir(parents=True, exist_ok=True)
            HEARTBEAT_FILE.write_text(json.dumps(hb, ensure_ascii=False))
            PID_FILE.write_text(str(os.getpid()))

    # ── processing ──

    def _process(self, event_type: str, data: dict):
        """Run all handlers for event_type."""
        hh = self.handlers.get(event_type, [])
        if not hh:
            hh = self.handlers.get("*", [])  # wildcard handler

        if not hh:
            return  # no handlers registered — silent drop

        source = data.get("_source", "internal")
        for handler in hh:
            try:
                handler(event_type, data)
            except Exception as e:
                print(json.dumps({
                    "ts": datetime.now(timezone.utc).isoformat(),
                    "level": "ERROR",
                    "event": event_type,
                    "handler": handler.__name__,
                    "error": str(e),
                    "source": source,
                }))

    # ── main loop ──

    def start(self):
        self.running = True
        self._last_tick = time.time()
        self._last_heartbeat = time.time()

        # Signals
        signal.signal(signal.SIGTERM, lambda *_: setattr(self, 'running', False))
        signal.signal(signal.SIGINT, lambda *_: setattr(self, 'running', False))
        if hasattr(signal, 'SIGBREAK'):
            signal.signal(signal.SIGBREAK, lambda *_: setattr(self, 'running', False))

        # Register built-in handlers
        self._register_core()

        # Load custom handlers from event_handlers.py
        self._load_event_handlers()

        # Bootstrap: emit time:tick immediately
        self.emit("time:tick", {"source": "boot"})

        print(json.dumps({
            "ts": datetime.now(timezone.utc).isoformat(),
            "level": "INFO",
            "event": "loop_started",
            "pid": os.getpid(),
            "handlers": list(self.handlers.keys()),
        }))
        self._loop()

    def _loop(self):
        """Main: poll → tick → process → sleep."""
        while self.running:
            # 1. Poll events.db for external events
            self._poll_events_db()

            # 2. Generate time:tick
            self._generate_tick()

            # 3. Process queue
            while self.queue and self.running:
                event_type, data = self.queue.pop(0)
                self._process(event_type, data)

            # 4. Heartbeat
            self._heartbeat()

            # 5. Sleep — короткий, чтобы реагировать быстро
            time.sleep(POLL_INTERVAL)

    def stop(self):
        self.running = False

    # ── boot ──

    def _register_core(self):
        """Register built-in handlers (replace cron jobs)."""

        @self.on("time:tick")
        def _on_tick(event_type, data):
            """Process time events — replaces ALL time-based cron jobs."""
            h = data.get("hour", -1)
            m = data.get("minute", -1)
            wd = data.get("weekday", -1)

            # Each tick: process pending events through evolution engine
            try:
                from event_evolution import process_pending_events
                result = process_pending_events()
                if result.get("processed", 0) > 0:
                    print(json.dumps({
                        "ts": datetime.now(timezone.utc).isoformat(),
                        "level": "INFO",
                        "event": "events_processed",
                        "count": result["processed"],
                    }))
            except Exception:
                pass

            # Nightly (02:00-03:00): consolidate memory
            if h == 2 and m < 5:
                try:
                    from dream_memory_cron import consolidate
                    result = consolidate()
                    print(json.dumps({
                        "ts": datetime.now(timezone.utc).isoformat(),
                        "level": "INFO",
                        "event": "memory_consolidated",
                        "detail": str(result)[:200],
                    }))
                except Exception:
                    pass

        @self.on("*")
        def _on_any(event_type, data):
            """Wildcard: only for events NOT handled by EvolutionEngine."""
            if event_type in ("time:tick",):
                return
            # Log unknown events (debug)
            pass

    def _load_event_handlers(self):
        """Load custom event handlers from event_handlers.py."""
        hp = SCRIPTS / "event_handlers.py"
        if not hp.exists():
            return
        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location("event_handlers_reg", hp)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            if hasattr(mod, "register_handlers"):
                mod.register_handlers(self)
        except Exception as e:
            print(json.dumps({
                "ts": datetime.now(timezone.utc).isoformat(),
                "level": "WARN",
                "event": "handler_load_failed",
                "error": str(e),
            }))


# ── CLI ───────────────────────────────────────────────────────────────

loop: Optional[EventLoop] = None


def main():
    global loop
    loop = EventLoop()

    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == "--status":
            if HEARTBEAT_FILE.exists():
                hb = json.loads(HEARTBEAT_FILE.read_text())
                age = int(time.time() - datetime.fromisoformat(hb["ts"]).timestamp())
                print(f"{'ALIVE' if age < 120 else 'DEAD'} — PID {hb['pid']}, {age}s since heartbeat")
                print(f"Handler count: {hb.get('handler_count', 0)}")
            else:
                print("DEAD — no heartbeat file")
            return
        if cmd == "--stop":
            if PID_FILE.exists():
                pid = int(PID_FILE.read_text())
                try:
                    os.kill(pid, signal.SIGTERM)
                    print(f"Sent SIGTERM to PID {pid}")
                except ProcessLookupError:
                    print(f"PID {pid} not found (already dead)")
                    PID_FILE.unlink(missing_ok=True)
            else:
                print("No PID file")
            return

    loop.start()


if __name__ == "__main__":
    main()

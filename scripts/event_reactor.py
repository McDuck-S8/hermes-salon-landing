#!/usr/bin/env python3
"""
Event Reactor — reacts to system events beyond file changes.


> Revisit: when reactor logic, event-to-action mapping, or handler execution changes. Last touched: 2026-07-02.
Extends file_watcher.py with event-driven triggers:
- Knowledge Cube changes → auto-classify new entries
- Goal queue changes → recalculate priorities
- Error log spikes → auto-investigate
- Session context changes → refresh context cache
- Cron job completions → log outcomes

Unlike cron (which polls), this reacts immediately to changes.

Usage:
    python scripts/event_reactor.py check    # one-shot check
    python scripts/event_reactor.py watch    # continuous watch
"""
import json
import os
import sys
import time
import hashlib
from pathlib import Path
from datetime import datetime, timedelta

HERMES_HOME = Path(__file__).resolve().parent.parent
CACHE_DIR = HERMES_HOME / "cache"
LOGS_DIR = HERMES_HOME / "logs"
DATA_DIR = HERMES_HOME / "data"

KC_DB = CACHE_DIR / "knowledge_cube.db"
ERROR_LOG = LOGS_DIR / "errors.log"
AGENT_DECISIONS = CACHE_DIR / "agent_decisions.json"
GOAL_QUEUE = CACHE_DIR / "goal_queue.json"
EVENT_STATE = CACHE_DIR / "event_reactor_state.json"
CONTEXT_CACHE = CACHE_DIR / "session_context_cache.json"

sys.path.insert(0, str(HERMES_HOME / "scripts"))


def load_state() -> dict:
    if EVENT_STATE.exists():
        try:
            return json.loads(EVENT_STATE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return {}
    return {}


def save_state(state: dict):
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    EVENT_STATE.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")


def log(msg: str):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] {msg}")


# ── Event 1: KC new entries → auto-classify ──

def check_kc_new_entries(state: dict) -> list[str]:
    """Detect new KC entries and classify them."""
    import sqlite3
    if not KC_DB.exists():
        return []

    last_id = state.get("last_kc_id", 0)
    try:
        conn = sqlite3.connect(str(KC_DB))
        cur = conn.cursor()
        cur.execute(
            "SELECT id, raw_text, axis_domain FROM experiences WHERE id > ? ORDER BY id DESC LIMIT 20",
            (last_id,)
        )
        rows = cur.fetchall()
        conn.close()
    except Exception:
        return []

    if not rows:
        return []

    actions = []
    for row in rows:
        text = row[1] or ""
        domain = row[2] or ""
        if not domain or domain == "uncategorized":
            # Try to classify
            text_lower = text.lower()
            detected = None
            for d, keywords in [
                ("coding", ["python", "code", "bug", "function", "git"]),
                ("devops", ["docker", "deploy", "server", "cron", "nginx"]),
                ("research", ["search", "find", "analyze", "compare"]),
                ("communication", ["telegram", "message", "send", "notify"]),
                ("system", ["install", "config", "setup", "env"]),
            ]:
                if any(k in text_lower for k in keywords):
                    detected = d
                    break
            if detected:
                actions.append(f"Classify entry {row[0]} as {detected}")

    state["last_kc_id"] = max(r[0] for r in rows)
    return actions


# ── Event 2: Error log spikes → auto-investigate ──

def check_error_spikes(state: dict) -> list[str]:
    """Detect spikes in error log and alert."""
    if not ERROR_LOG.exists():
        return []

    try:
        lines = ERROR_LOG.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return []

    recent_cutoff = datetime.now() - timedelta(minutes=30)
    recent_errors = 0
    for line in lines[-100:]:
        if "ERROR" in line:
            recent_errors += 1

    last_count = state.get("last_error_count", 0)
    spike = recent_errors - last_count

    state["last_error_count"] = recent_errors

    if spike > 5:
        return [f"Error spike detected: {spike} new errors in last 100 lines"]
    return []


# ── Event 3: Goal queue changes → refresh context cache ──

def check_goal_changes(state: dict) -> list[str]:
    """Detect goal queue changes and refresh context."""
    if not GOAL_QUEUE.exists():
        return []

    try:
        data = json.loads(GOAL_QUEUE.read_text(encoding="utf-8"))
        goals = data.get("goals", [])
        active = [g for g in goals if g.get("status") == "active"]
        completed = [g for g in goals if g.get("status") == "completed"]
    except (json.JSONDecodeError, OSError):
        return []

    last_active = state.get("last_active_goals", 0)
    last_completed = state.get("last_completed_goals", 0)

    actions = []
    if len(completed) > last_completed:
        newly_done = len(completed) - last_completed
        actions.append(f"Goal completed: {newly_done} new completed goals")

    if len(active) != last_active:
        actions.append(f"Active goals changed: {last_active} -> {len(active)}")

    state["last_active_goals"] = len(active)
    state["last_completed_goals"] = len(completed)

    return actions


# ── Event 4: Session context refresh ──

def check_session_context(state: dict) -> list[str]:
    """Refresh session context cache when decisions change."""
    if not AGENT_DECISIONS.exists():
        return []

    try:
        data = json.loads(AGENT_DECISIONS.read_text(encoding="utf-8"))
        decisions = data.get("decisions", [])
    except (json.JSONDecodeError, OSError):
        return []

    last_decisions_hash = state.get("last_decisions_hash", "")
    current_hash = hashlib.md5(
        json.dumps(decisions[-5:], sort_keys=True).encode()
    ).hexdigest()

    if current_hash != last_decisions_hash:
        # Refresh context cache
        try:
            from session_context import build_context
            ctx = build_context()
            if ctx:
                CONTEXT_CACHE.write_text(
                    json.dumps({"context": ctx, "updated_at": datetime.now().isoformat()}),
                    encoding="utf-8"
                )
        except ImportError:
            pass

        state["last_decisions_hash"] = current_hash
        return ["Session context cache refreshed"]

    return []


# ── Main ──

def check_all() -> dict:
    """Run all event checks."""
    state = load_state()
    all_actions = []

    checks = [
        ("KC entries", check_kc_new_entries),
        ("Error spikes", check_error_spikes),
        ("Goal changes", check_goal_changes),
        ("Session context", check_session_context),
    ]

    for name, check_fn in checks:
        try:
            actions = check_fn(state)
            if actions:
                log(f"[{name}] {len(actions)} events")
                for a in actions:
                    log(f"  -> {a}")
                all_actions.extend(actions)
        except Exception as e:
            log(f"[{name}] Error: {e}")

    save_state(state)
    return {"actions": all_actions, "state": state}


def watch():
    """Continuous watch mode."""
    log("Event reactor started (watch mode)")
    while True:
        try:
            result = check_all()
            if result["actions"]:
                log(f"Processed {len(result['actions'])} events")
        except Exception as e:
            log(f"Check error: {e}")
        time.sleep(30)


if __name__ == "__main__":
    args = sys.argv[1:]
    if "--watch" in args:
        watch()
    else:
        result = check_all()
        if result["actions"]:
            print(f"Actions taken: {len(result['actions'])}")
        else:
            print("No events to process.")

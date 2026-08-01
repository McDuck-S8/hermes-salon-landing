#!/usr/bin/env python3
"""
Event Sense — THE LIVING NERVOUS SYSTEM.


> Revisit: when event sensing logic, sensor types, or detection thresholds change. Last touched: 2026-07-02.
Пуля попадает → мишень чувствует → реагирует.

  event_registry  — ЧТО это (18 типов событий, 4 уровня)
  event_sense     — КОГДА это (detect из环境)
  chain_executor  — КАК это (цепочки действий)

Flow: sense detects → registry classifies → chain executes → outcome

Это НЕ сканер. Это НЕ таймер.
ЭTO ОРГАН ЧУВСТВ: что-то случилось → тут же реагирую.
"""
import json
import sys
import time
import socket
import subprocess
from pathlib import Path
from datetime import datetime, timezone, timedelta
from typing import Optional

REPO_ROOT = Path(__file__).resolve().parent.parent
CACHE = REPO_ROOT / "cache"
BUS_FILE = CACHE / "event_bus.json"
STATE_FILE = CACHE / "sense_state.json"

# Import the registry
sys.path.insert(0, str(REPO_ROOT / "scripts"))
from event_registry import detect_event


# ═══════════════════════════════════════════════
# CORE: Detect → Classify → React
# ═══════════════════════════════════════════════

def _now():
    return datetime.now(timezone.utc)


def fire(event_text: str, context: dict = None) -> dict:
    """
    THE ONE ENTRY POINT.
    Something happened? Call fire().
    It detects, reacts, logs.
    """
    # 1. Detect what happened (from config)
    event = detect_event(event_text, context)

    # 2. Log to bus
    _log_to_bus(event)

    # 2b. Record to knowledge cube via event_evolution
    try:
        from event_evolution import on_task_complete
        on_task_complete(
            content=f"Event: {event['event_type']} (L{event['level']}) — {event['description']}",
            tags=[event["event_type"], f"L{event['level']}", "event_system"],
            source="event_sense"
        )
    except:
        pass

    # 3. Spawn agents for L0/L1
    _spawn_agents(event, {})

    # 4. EXECUTE ACTIONS — the hands move
    action_results = []
    actions = event.get("actions", [])
    if actions:
        try:
            from action_executor import execute_actions
            action_results = execute_actions(event["event_type"], actions, event)
        except:
            pass

    # If L0 — alert immediately
    if event["level"] == 0:
        try:
            from event_log import log_error
            log_error(f"CRITICAL: {event['event_type']}", f"L0 event: {event['description']}", ["L0", "critical"])
        except:
            pass

    return {
        "event": event["event_type"],
        "level": event["level"],
        "level_name": _level_name(event["level"]),
        "description": event["description"],
        "confidence": event["confidence"],
        "agents": event.get("agents", []),
        "actions": actions,
        "action_results": [{"action": r["action"], "success": r["success"]} for r in action_results],
        "timestamp": _now().isoformat(),
    }


def _level_name(level: int) -> str:
    return {
        0: "МГНОВЕННО",
        1: "БЫСТРО",
        2: "В ФОНЕ",
        3: "ПЕРИОДИЧЕСКИ"
    }.get(level, "НЕИЗВЕСТНО")


def _log_to_bus(event: dict):
    """Write event to a dedicated sense log (separate from event_bus.json).
    
    NOTE: We do NOT write to event_bus.json here — that would race with
    event_bus.process_events(). Sensor events are emitted through 
    event_bus.emit() in event_daemon.py which properly queues them.
    This function only records history for the sense subsystem.
    """
    sense_log = CACHE / "sense_history.json"
    bus = {"entries": []}
    if sense_log.exists():
        try:
            bus = json.loads(sense_log.read_text(encoding="utf-8"))
        except:
            pass

    entry = {
        "event_type": event["event_type"],
        "level": event["level"],
        "severity": ["critical", "high", "medium", "low"][min(event["level"], 3)],
        "confidence": event["confidence"],
        "timestamp": _now().isoformat(),
        "agents": event.get("agents", []),
    }
    bus["entries"].append(entry)
    bus["entries"] = bus["entries"][-200:]  # Keep last 200

    CACHE.mkdir(parents=True, exist_ok=True)
    sense_log.write_text(json.dumps(bus, indent=2, ensure_ascii=False, default=str), encoding="utf-8")


def _spawn_agents(event: dict, reaction: dict):
    """
    Multi-agent: spawn subagents for L0 and L1 events.
    L2-L3 run in background (cron handles those).
    """
    level = event["level"]
    if level > 1:
        return

    agents = event.get("agents", reaction.get("agents", []))
    event_type = event["event_type"]

    for agent_name in agents:
        prompt = (
            f"Событие: {event_type} (L{level})\n"
            f"Описание: {event['description']}\n"
            f"Действия: {', '.join(event.get('actions', []))}\n"
            f"Выполни необходимые действия."
        )
        agent_log = CACHE / "agent_spawns.jsonl"
        CACHE.mkdir(parents=True, exist_ok=True)
        with open(agent_log, "a", encoding="utf-8") as f:
            f.write(json.dumps({
                "agent": agent_name,
                "event": event_type,
                "level": level,
                "prompt": prompt[:500],
                "timestamp": _now().isoformat(),
                "status": "queued",
            }, ensure_ascii=False) + "\n")


# ═══════════════════════════════════════════════
# ENVIRONMENT SENSORS — what's happening around me
# ═══════════════════════════════════════════════

def check_gateway() -> dict:
    """Is the gateway alive?"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2)
        result = s.connect_ex(('127.0.0.1', 9003))
        s.close()
        if result != 0:
            return fire("gateway упал порт 9003 не отвечает")
    except:
        return fire("gateway connection failed")
    return {"event": None}


def check_proxy() -> dict:
    """Is the SOCKS5 proxy alive?"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2)
        result = s.connect_ex(('127.0.0.1', 10806))
        s.close()
        if result != 0:
            return fire("socks5 прокси не работает порт 10806")
    except:
        return fire("proxy connection failed")
    return {"event": None}


def check_salon_bot() -> dict:
    """Is the salon bot running?"""
    try:
        r = subprocess.run(
            ["tasklist", "/FI", "IMAGENAME eq python.exe", "/FO", "CSV"],
            capture_output=True, text=True, timeout=5,
            encoding="utf-8", errors="replace"
        )
        # Check if salon bot process exists
        if "main.py" not in r.stdout and "python" in r.stdout.lower():
            pass  # python running, likely bot
        return {"event": None}
    except:
        return {"event": None}


def check_cron() -> dict:
    """Are cron jobs healthy?"""
    jobs_file = REPO_ROOT / "cron" / "jobs.json"
    if not jobs_file.exists():
        return {"event": None}
    try:
        data = json.loads(jobs_file.read_text(encoding="utf-8"))
        now = _now()
        stale = 0
        for j in data.get("jobs", []):
            if not j.get("enabled") or j.get("event_driven"):
                continue
            nrt = j.get("next_run_at")
            if nrt:
                try:
                    if datetime.fromisoformat(nrt) < now:
                        stale += 1
                except:
                    pass
        if stale > 3:
            return fire(f"крон деградировал {stale} задач просрочено")
    except:
        pass
    return {"event": None}


def check_knowledge_cube() -> dict:
    """Is the knowledge cube being updated?"""
    kc_db = REPO_ROOT / "cache" / "knowledge_cube.db"
    if kc_db.exists():
        age_hours = (time.time() - kc_db.stat().st_mtime) / 3600
        if age_hours > 48:
            return fire(f"knowledge cube не обновлялся {age_hours:.0f} часов")
    return {"event": None}


def check_user_silence() -> dict:
    """Has the user been silent too long?"""
    state = _load_state()
    last_msg = state.get("last_user_message")
    if last_msg:
        try:
            last_dt = datetime.fromisoformat(last_msg)
            silent_min = (_now() - last_dt).total_seconds() / 60
            if silent_min >= 10 and not state.get("notified_away"):
                state["notified_away"] = True
                _save_state(state)
                return fire(f"пользователь молчит {silent_min:.0f} минут")
            elif silent_min < 10:
                state["notified_away"] = False
                _save_state(state)
        except:
            pass
    return {"event": None}


# ═══════════════════════════════════════════════
# FULL SWEEP — check everything, fire what fires
# ═══════════════════════════════════════════════

def sweep() -> dict:
    """
    Run ALL sensors via sensor_array. Fire events for whatever fires.
    This is the "moment of feeling" — complete environment scan.
    """
    # Import sensor_array
    try:
        from sensor_array import sweep_all
        sensor_result = sweep_all()
    except ImportError:
        # Fallback to old sweep
        return _sweep_legacy()

    # Fire events for each detected sensor event
    fired = []
    for evt in sensor_result.get("events", []):
        event_text = f"{evt['type']} {evt.get('detail', '')}"
        result = fire(event_text, {"sensor_event": True})
        fired.append(result)

    return {
        "timestamp": _now().isoformat(),
        "sensors_active": sensor_result.get("sensors_active", 0),
        "sensors_triggered": sensor_result.get("sensors_triggered", 0),
        "events_fired": len(fired),
        "fired": fired,
        "sensor_detail": sensor_result.get("sensor_detail", []),
    }


def _sweep_legacy() -> dict:
    """Fallback sweep if sensor_array not available."""
    results = []
    sensors = [
        ("gateway", check_gateway),
        ("proxy", check_proxy),
        ("cron", check_cron),
        ("knowledge_cube", check_knowledge_cube),
        ("user_silence", check_user_silence),
    ]
    for name, sensor in sensors:
        try:
            r = sensor()
            if r.get("event"):
                results.append({"sensor": name, "event": r["event"]})
        except Exception as e:
            results.append({"sensor": name, "event": "error", "detail": str(e)[:200]})
    return {"timestamp": _now().isoformat(), "sensors_checked": len(sensors), "events_fired": len(results), "results": results}


# ═══════════════════════════════════════════════
# USER MESSAGE — classify and react
# ═══════════════════════════════════════════════

def on_user_message(text: str) -> dict:
    """User sent something. Classify + react."""
    # Reset silence timer
    state = _load_state()
    state["last_user_message"] = _now().isoformat()
    state["notified_away"] = False
    _save_state(state)

    return fire(text, {"is_user_message": True})


# ═══════════════════════════════════════════════
# STATE
# ═══════════════════════════════════════════════

def _load_state() -> dict:
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text(encoding="utf-8"))
        except:
            pass
    return {"last_user_message": None, "notified_away": False, "last_check": None}

def _save_state(state: dict):
    CACHE.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2, ensure_ascii=False, default=str), encoding="utf-8")


# ═══════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════

def main():
    if len(sys.argv) < 2:
        print("Event Sense — Living Nervous System")
        print("")
        print("  fire 'текст'       — detect + classify + react")
        print("  sweep              — scan all sensors, fire what fires")
        print("  message 'текст'    — user message (reset silence + fire)")
        print("  list               — all event types by level")
        return

    cmd = sys.argv[1]

    if cmd == "fire":
        text = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else ""
        r = fire(text)
        print(json.dumps(r, indent=2, ensure_ascii=False))

    elif cmd == "sweep":
        r = sweep()
        print(json.dumps(r, indent=2, ensure_ascii=False))

    elif cmd == "message":
        text = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else ""
        r = on_user_message(text)
        print(json.dumps(r, indent=2, ensure_ascii=False))

    elif cmd == "list":
        for level in range(4):
            name = _level_name(level)
            events = [e for e, d in EVENTS.items() if d["level"] == level]
            print(f"\n  L{level} ({name}):")
            for e in events:
                desc = EVENTS[e]["description"]
                agents = ", ".join(EVENTS[e]["reaction"]["agents"])
                print(f"    {e}: {desc}")
                print(f"      -> agents: {agents}")

    else:
        print(f"Unknown: {cmd}")


if __name__ == "__main__":
    main()

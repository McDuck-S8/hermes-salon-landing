#!/usr/bin/env python3
"""
SENSOR ARRAY — Датчики на ВСЁ что всегда происходит.


> Revisit: when sensor array logic, event sense logic, or trigger conditions change. Last touched: 2026-07-02.
Мир не стоит на месте. Всегда:
  - Время идёт (утро → день → вечер → ночь)
  - Погода меняется
  - Тренды движутся
  - Контент выходит
  - Ресурсы тают
  - Система работает/глохнет
  - Пользователи активны
  - Знания растут

Если sweep() говорит "ALL QUIET" — датчики мёртвые.
"""
import json
import os
import time
import socket
import subprocess
import sys
from pathlib import Path
from datetime import datetime, timezone, timedelta

REPO_ROOT = Path(__file__).resolve().parent.parent
CACHE = REPO_ROOT / "cache"
SENSORS_STATE = CACHE / "sensors_state.json"


def _now():
    return datetime.now(timezone.utc)


def _load_state() -> dict:
    if SENSORS_STATE.exists():
        try:
            return json.loads(SENSORS_STATE.read_text(encoding="utf-8"))
        except:
            pass
    return {}


def _save_state(state: dict):
    CACHE.mkdir(parents=True, exist_ok=True)
    SENSORS_STATE.write_text(
        json.dumps(state, indent=2, ensure_ascii=False, default=str),
        encoding="utf-8"
    )


# ═══════════════════════════════════════════════
# SENSOR: TIME — Время всегда идёт
# ═══════════════════════════════════════════════

def sensor_time() -> list:
    """
    Время — единственное что ГАРАНТИРОВАННО происходит.
    Утро/день/вечер/ночь — каждое время = свои действия.
    """
    events = []
    now = _now()
    hour = now.hour

    state = _load_state()
    last_phase = state.get("time_phase")

    # Определяем фазу дня
    if 6 <= hour < 9:
        phase = "morning"
    elif 9 <= hour < 12:
        phase = "forenoon"
    elif 12 <= hour < 17:
        phase = "afternoon"
    elif 17 <= hour < 21:
        phase = "evening"
    elif 21 <= hour or hour < 1:
        phase = "night"
    else:
        phase = "deep_night"

    # Фаза изменилась — это СОБЫТИЕ
    if phase != last_phase:
        state["time_phase"] = phase
        state["phase_changed_at"] = now.isoformat()
        _save_state(state)

        phase_events = {
            "morning": {
                "type": "day_started",
                "level": 2,
                "detail": f"Начался день ({now.strftime('%H:%M')})",
                "actions": ["system_health_check", "overnight_report", "day_planning"],
            },
            "forenoon": {
                "type": "work_mode",
                "level": 2,
                "detail": f"Рабочее время ({now.strftime('%H:%M')})",
                "actions": ["check_goals", "prioritize_tasks"],
            },
            "afternoon": {
                "type": "midday",
                "level": 2,
                "detail": f"Середина дня ({now.strftime('%H:%M')})",
                "actions": ["progress_check", "energy_assessment"],
            },
            "evening": {
                "type": "day_ending",
                "level": 2,
                "detail": f"День заканчивается ({now.strftime('%H:%M')})",
                "actions": ["daily_summary", "plan_tomorrow"],
            },
            "night": {
                "type": "night_started",
                "level": 2,
                "detail": f"Наступила ночь ({now.strftime('%H:%M')})",
                "actions": ["cleanup", "backup", "analytics"],
            },
            "deep_night": {
                "type": "deep_night",
                "level": 3,
                "detail": f"Глубокая ночь ({now.strftime('%H:%M')})",
                "actions": ["maintenance", "knowledge_compaction"],
            },
        }

        if phase in phase_events:
            events.append(phase_events[phase])

    return events


# ═══════════════════════════════════════════════
# SENSOR: SYSTEM — Ресурсы всегда тают
# ═══════════════════════════════════════════════

def sensor_system() -> list:
    """
    Диск, RAM, CPU — всегда что-то меняется.
    """
    events = []

    try:
        # Disk space
        r = subprocess.run(
            ["df", "-h", "/"], capture_output=True, text=True, timeout=5,
            encoding="utf-8", errors="replace"
        )
        lines = r.stdout.strip().split("\n")
        if len(lines) > 1:
            parts = lines[1].split()
            usage_pct = parts[4].replace("%", "")
            try:
                pct = int(usage_pct)
                if pct > 90:
                    events.append({
                        "type": "disk_critical",
                        "level": 0,
                        "detail": f"Диск {pct}% заполнен — КРИТИЧЕСКИ",
                        "actions": ["emergency_cleanup", "alert_user"],
                    })
                elif pct > 75:
                    events.append({
                        "type": "disk_warning",
                        "level": 1,
                        "detail": f"Диск {pct}% заполнен",
                        "actions": ["suggest_cleanup"],
                    })
            except:
                pass
    except:
        pass

    try:
        # Memory
        r = subprocess.run(
            ["free", "-m"], capture_output=True, text=True, timeout=5,
            encoding="utf-8", errors="replace"
        )
        lines = r.stdout.strip().split("\n")
        if len(lines) > 1:
            parts = lines[1].split()
            total = int(parts[1])
            used = int(parts[2])
            pct = (used / total * 100) if total > 0 else 0
            if pct > 90:
                events.append({
                    "type": "memory_critical",
                    "level": 0,
                    "detail": f"RAM {pct:.0f}% ({used}/{total} MB) — КРИТИЧЕСКИ",
                    "actions": ["kill_processes", "alert_user"],
                })
            elif pct > 75:
                events.append({
                    "type": "memory_warning",
                    "level": 1,
                    "detail": f"RAM {pct:.0f}% ({used}/{total} MB)",
                    "actions": ["monitor"],
                })
    except:
        pass

    return events


# ═══════════════════════════════════════════════
# SENSOR: PROCESSES — Сервисы всегда работают/падают
# ═══════════════════════════════════════════════

def sensor_processes() -> list:
    """Check critical processes."""
    events = []

    # Gateway (port 9003)
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2)
        result = s.connect_ex(('127.0.0.1', 9003))
        s.close()
        if result != 0:
            events.append({
                "type": "breakdown",
                "level": 0,
                "detail": "Gateway port 9003 не отвечает",
                "actions": ["restart_gateway", "verify_fix"],
            })
    except:
        events.append({
            "type": "breakdown",
            "level": 0,
            "detail": "Gateway check failed",
            "actions": ["restart_gateway"],
        })

    # SOCKS5 proxy (port 10806)
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2)
        result = s.connect_ex(('127.0.0.1', 10806))
        s.close()
        if result != 0:
            events.append({
                "type": "breakdown",
                "level": 1,
                "detail": "SOCKS5 proxy port 10806 не отвечает",
                "actions": ["restart_proxy", "alert_user"],
            })
    except:
        pass

    return events


# ═══════════════════════════════════════════════
# SENSOR: FILES — Файлы всегда меняются
# ═══════════════════════════════════════════════

def sensor_files() -> list:
    """Check if critical files changed."""
    events = []
    state = _load_state()

    critical_files = {
        "scripts/event_registry.py": "registry",
        "scripts/event_sense.py": "sense",
        "scripts/chain_executor.py": "chain_executor",
        "scripts/reality_gate.py": "reality_gate",
        "cron/jobs.json": "cron_config",
    }

    for rel_path, name in critical_files.items():
        fpath = REPO_ROOT / rel_path
        if fpath.exists():
            mtime = fpath.stat().st_mtime
            last = state.get(f"file_{name}_mtime")
            if last and mtime > last:
                events.append({
                    "type": "file_changed",
                    "level": 2,
                    "detail": f"Изменился {rel_path}",
                    "actions": ["verify_syntax", "check_impact"],
                })
            state[f"file_{name}_mtime"] = mtime

    _save_state(state)
    return events


# ═══════════════════════════════════════════════
# SENSOR: CRON — Задачи всегда выполняются/просрочиваются
# ═══════════════════════════════════════════════

def sensor_cron() -> list:
    """Check cron job health."""
    events = []
    jobs_file = REPO_ROOT / "cron" / "jobs.json"
    if not jobs_file.exists():
        return events

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
            events.append({
                "type": "cron_degraded",
                "level": 1,
                "detail": f"{stale} cron jobs просрочено",
                "actions": ["reschedule_cron"],
            })
    except:
        pass

    return events


# ═══════════════════════════════════════════════
# SENSOR: KNOWLEDGE — Знания всегда растут/устаревают
# ═══════════════════════════════════════════════

def sensor_knowledge() -> list:
    """Check knowledge freshness."""
    events = []

    kc_db = REPO_ROOT / "cache" / "knowledge_cube.db"
    if kc_db.exists():
        age_hours = (time.time() - kc_db.stat().st_mtime) / 3600
        if age_hours > 24:
            events.append({
                "type": "knowledge_gap",
                "level": 2,
                "detail": f"KC не обновлялся {age_hours:.0f}ч",
                "actions": ["explore_and_learn"],
            })

    # Check if goals exist
    goals_file = CACHE / "goal_queue.json"
    if goals_file.exists():
        try:
            data = json.loads(goals_file.read_text(encoding="utf-8"))
            active = [g for g in data.get("goals", []) if g.get("status") == "active"]
            if not active:
                events.append({
                    "type": "no_goals",
                    "level": 2,
                    "detail": "Нет активных целей — система простаивает",
                    "actions": ["create_goals", "explore_opportunities"],
                })
        except:
            pass

    return events


# ═══════════════════════════════════════════════
# SENSOR: USER — Пользователь существует
# ═══════════════════════════════════════════════

def sensor_user() -> list:
    """Check user interaction state."""
    events = []
    state = _load_state()
    last_msg = state.get("last_user_message")

    if last_msg:
        try:
            last_dt = datetime.fromisoformat(last_msg)
            silent_min = (_now() - last_dt).total_seconds() / 60
            if silent_min >= 5 and not state.get("user_away_notified"):
                state["user_away_notified"] = True
                _save_state(state)
                events.append({
                    "type": "user_silent",
                    "level": 2,
                    "detail": f"Пользователь молчит {silent_min:.0f} мин",
                    "actions": ["start_background_work"],
                })
        except:
            pass
    else:
        # Never received a message
        events.append({
            "type": "no_user_interaction",
            "level": 3,
            "detail": "Пользователь ещё не писал в этой сессии",
            "actions": ["wait_for_user"],
        })

    return events


# ═══════════════════════════════════════════════
# SENSOR: IBOS ENTITIES — Валидация сущностей IBOS
# ═══════════════════════════════════════════════

def sensor_ibos_entities() -> list:
    """Validate IBOS entities on startup and emit events for violations."""
    events = []
    state = _load_state()
    
    # Only run once per boot (check if we already validated this session)
    if state.get("ibos_validated_this_session"):
        return events
    
    state["ibos_validated_this_session"] = True
    _save_state(state)
    
    # Import and run IBOS validator
    try:
        import sys
        sys.path.insert(0, str(REPO_ROOT / "scripts"))
        from ibos_entity_sensor import run_startup_validation
        
        validation_state = run_startup_validation()
        
        if validation_state.invalid_entities > 0:
            events.append({
                "type": "ibos_validation_failed",
                "level": 0,  # Critical
                "detail": f"IBOS validation failed: {validation_state.invalid_entities} entities invalid, {len(validation_state.blocked_entities)} blocked",
                "actions": ["fix_entity_frontmatter", "check_dependency_graph"],
                "payload": {
                    "total": validation_state.total_entities,
                    "valid": validation_state.valid_entities,
                    "invalid": validation_state.invalid_entities,
                    "blocked": validation_state.blocked_entities
                }
            })
        else:
            events.append({
                "type": "ibos_validation_passed",
                "level": 2,
                "detail": f"IBOS validation passed: {validation_state.valid_entities} entities valid",
                "actions": ["proceed_with_chains"],
            })
    except ImportError:
        events.append({
            "type": "ibos_sensor_unavailable",
            "level": 1,
            "detail": "ibos_entity_sensor module not found",
            "actions": ["install_dependencies"],
        })
    except Exception as e:
        events.append({
            "type": "ibos_validation_error",
            "level": 0,
            "detail": f"IBOS validation error: {str(e)[:200]}",
            "actions": ["check_logs", "restart_validation"],
        })
    
    return events


# ══════════════════════════════════════════════
# FULL SWEEP — ВСЕ датчики, ВСЕ события
# ═══════════════════════════════════════════════

def sweep_all() -> dict:
    """
    Запускает ВСЕ датчики. Каждый датчик проверяет СВОЮ область мира.
    Если датчик говорит "ALL QUIET" — он мёртвый.
    """
    now = _now()
    all_events = []

    sensors = [
        ("time", sensor_time),
        ("system", sensor_system),
        ("processes", sensor_processes),
        ("files", sensor_files),
        ("cron", sensor_cron),
        ("knowledge", sensor_knowledge),
        ("user", sensor_user),
        ("ibos_entities", sensor_ibos_entities),
    ]

    sensor_results = []
    for name, func in sensors:
        try:
            events = func()
            sensor_results.append({
                "name": name,
                "events": len(events),
                "status": "active" if events else "quiet",
            })
            all_events.extend(events)
        except Exception as e:
            sensor_results.append({
                "name": name,
                "events": 0,
                "status": f"error: {str(e)[:100]}",
            })

    # Sort by level (L0 first)
    all_events.sort(key=lambda e: e.get("level", 99))

    return {
        "timestamp": now.isoformat(),
        "sensors_active": len(sensors),
        "sensors_triggered": sum(1 for s in sensor_results if s["events"] > 0),
        "events_total": len(all_events),
        "events": all_events,
        "sensor_detail": sensor_results,
    }


# ═══════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════

def main():
    if len(sys.argv) < 2:
        print("Sensor Array — датчики на ВСЁ")
        print("")
        print("  sweep     — все датчики, все события")
        print("  time      — только время")
        print("  system    — только ресурсы")
        print("  procs     — только процессы")
        print("  files     — только файлы")
        print("  cron      — только крон")
        print("  knowledge — только знания")
        print("  user      — только пользователь")
        return

    cmd = sys.argv[1]

    if cmd == "sweep":
        r = sweep_all()
        print(json.dumps(r, indent=2, ensure_ascii=False))
    elif cmd == "time":
        print(json.dumps(sensor_time(), indent=2, ensure_ascii=False))
    elif cmd == "system":
        print(json.dumps(sensor_system(), indent=2, ensure_ascii=False))
    elif cmd == "procs":
        print(json.dumps(sensor_processes(), indent=2, ensure_ascii=False))
    elif cmd == "files":
        print(json.dumps(sensor_files(), indent=2, ensure_ascii=False))
    elif cmd == "cron":
        print(json.dumps(sensor_cron(), indent=2, ensure_ascii=False))
    elif cmd == "knowledge":
        print(json.dumps(sensor_knowledge(), indent=2, ensure_ascii=False))
    elif cmd == "user":
        print(json.dumps(sensor_user(), indent=2, ensure_ascii=False))
    elif cmd == "ibos":
        print(json.dumps(sensor_ibos_entities(), indent=2, ensure_ascii=False))
    else:
        print(f"Unknown: {cmd}")


if __name__ == "__main__":
    main()

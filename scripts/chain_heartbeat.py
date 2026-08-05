#!/usr/bin/env python3
"""
Chain Heartbeat v2 — multi-level distributed fault detection.

Level 1: Events (event bus signals — knowledge_added, new_suggestions_ready, etc.)
Level 2: Modules (all 18+ modules from architecture_model)
Level 3: Pipelines (Knowledge, Self-Improvement, Action)
Level 4: External services (BrowserOS, Telegram API, etc.)
Level 5: System heartbeat (single JSON with all levels)

No daemons. No processes. Every event IS a heartbeat.
If an event hasn't fired within its expected interval → SILENT.

Usage:
    from chain_heartbeat import beat, event_beat, system_status
    beat("core")                          # module heartbeat
    event_beat("knowledge_added")         # event fired
    system_status()                       # full system heartbeat JSON
"""
import json, os, socket, time, subprocess as sp
from pathlib import Path
from datetime import datetime, timezone

CACHE = Path(os.environ.get("HERMES_HOME", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))) / "cache"
STATE_FILE = CACHE / "chain_heartbeat.json"
SYS_FILE = CACHE / "system_heartbeat.json"

DEFAULT_TIMEOUT = 86400       # 24h — modules
EVENT_TIMEOUT_GLOBAL = 7200   # 2h — default for events without explicit timeout
EXTERNAL_TIMEOUT = 300        # 5min — external services
PIPELINE_DEGRADED = 1         # 1 silent component → DEGRADED
PIPELINE_BROKEN = 2           # 2+ silent → BROKEN

# ── Level 1: Events (event bus signals) ──
# Each event expects to fire within expected_interval_s.
# If it doesn't → SILENT for that event.
# None = no timeout (alert-only events)
EVENTS = {
    "knowledge_added": {
        "expected_interval_s": 3600,        # 1h — knowledge flow
        "pipeline": "knowledge_pipeline",
        "description": "New knowledge added to Cube",
    },
    "new_suggestions_ready": {
        "expected_interval_s": 3600,        # 1h — self-improvement
        "pipeline": "self_improvement_pipeline",
        "description": "Self-improvement suggestions generated",
    },
    "architecture_scan_complete": {
        "expected_interval_s": 86400,       # 24h — architecture model
        "pipeline": None,
        "description": "Architecture model scan completed",
    },
    "cron_job_died": {
        "expected_interval_s": None,         # alert-only
        "pipeline": None,
        "description": "A cron job failed",
    },
    "external_service_down": {
        "expected_interval_s": None,         # alert-only
        "pipeline": None,
        "description": "External service ping failed",
    },
    "user_correction": {
        "expected_interval_s": None,         # unpredictable
        "pipeline": None,
        "description": "User issued a correction",
    },
}

# ── Level 2: All modules from architecture_model ──
MODULES = [
    "core", "event_system", "knowledge", "knowledge_pipeline",
    "llm", "cron_tools", "tools", "telegram", "posting",
    "health", "curiosity", "anomaly_detector", "orchestrator",
    "market_research", "self_improvement_loop", "uncertainty_observer",
    "crystal_base",
    "plugins_websrch", "plugins_selfev", "plugins_icarus", "plugins_lcm",
    "config", "skills", "deprecated",
    # Background cron modules
    "proactive_doer", "proactive_executor", "self_healing_monitor",
    "autonomous_agent", "pipeline_cron", "knowledge_gap_filler",
    "result_producer", "event_trigger",
    # Missing modules - add to heartbeat
    "researcher_agent", "curiosity_engine", "event_processor",
    "entity_linking_pipeline", "sales_assistant", "alert_janitor",
]

# ── Level 3: Pipelines ──
# Each pipeline = chain of module names
PIPELINES = {
    "knowledge_pipeline": {
        "components": ["knowledge", "knowledge_pipeline", "cron_tools", "plugins_selfev"],
        "description": "RSS → filter → KC → categorize → populate",
    },
    "self_improvement_pipeline": {
        "components": ["core", "event_system", "health", "self_improvement_loop", "anomaly_detector", "plugins_icarus", "plugins_lcm"],
        "description": "hooks → events → fixes → suggestions → skills → evolve",
    },
    "action_pipeline": {
        "components": ["posting", "telegram", "curiosity", "orchestrator", "market_research"],
        "description": "research → content → publish → monitor → iterate",
    },
}

# ── Level 4: External services ──
EXTERNAL_SERVICES = {
    "browseros": {"host": "127.0.0.1", "port": 9003, "timeout_s": 5},
    "browserclaw": {"host": "127.0.0.1", "port": 9010, "timeout_s": 5},
    "deepseek_local": {"host": "127.0.0.1", "port": 9655, "timeout_s": 5},
    "telegram_api": {"host": "api.telegram.org", "port": 443, "timeout_s": 10, "proxy": "socks5h://127.0.0.1:10806"},
    "openrouter_api": {"host": "openrouter.ai", "port": 443, "timeout_s": 10},
}

# Latency thresholds
LATENCY_WARN_MS = 1000    # 1s → WARNING
LATENCY_CRIT_MS = 5000    # 5s → CRITICAL

# ── Storage ──
def _load():
    if STATE_FILE.exists():
        # Retry on partial-write corruption (multi-process writes to same JSON)
        for attempt in range(3):
            try:
                with open(STATE_FILE) as f:
                    state = json.load(f)
                state.setdefault("beats", {})
                state.setdefault("alerts", [])
                state.setdefault("registered", {})
                state.setdefault("pings", {})
                return state
            except (json.JSONDecodeError, OSError):
                if attempt < 2:
                    time.sleep(0.25 + 0.25 * attempt)
                else:
                    # Preserve corrupt file, do NOT silently return empty state —
                    # an empty state + next _save() wipes all live beats.
                    try:
                        corrupt = STATE_FILE.with_suffix(".corrupt")
                        STATE_FILE.replace(corrupt)
                    except OSError:
                        pass
    return {"beats": {}, "alerts": [], "registered": {}, "pings": {}}

def _save(state):
    CACHE.mkdir(parents=True, exist_ok=True)
    # Atomic write: temp file + os.replace — readers never see partial JSON.
    # On Windows, a parallel process may hold the file open (PermissionError);
    # retry, then fall back to direct write (Windows allows it if no exclusive lock).
    import tempfile
    payload = json.dumps(state, indent=2)
    for attempt in range(4):
        fd, tmp = tempfile.mkstemp(dir=str(CACHE), suffix=".tmp")
        try:
            with os.fdopen(fd, "w") as f:
                f.write(payload)
            try:
                os.replace(tmp, STATE_FILE)
                return
            except PermissionError:
                try:
                    os.unlink(tmp)
                except OSError:
                    pass
                if attempt < 3:
                    time.sleep(0.3 * (attempt + 1))
                else:
                    # Last resort: direct write (best effort on locked file)
                    with open(STATE_FILE, "w") as f:
                        f.write(payload)
                    return
        except BaseException:
            try:
                os.unlink(tmp)
            except OSError:
                pass
            raise

# ── Registration (Level 2) ──
def register(name: str, type: str = "module", pipeline: str = None):
    """Register a component in the heartbeat system."""
    state = _load()
    state.setdefault("registered", {})
    state["registered"][name] = {
        "type": type,
        "pipeline": pipeline,
        "registered_at": time.time(),
    }
    _save(state)

def register_all_modules():
    """Register all known components. Call once at startup."""
    state = _load()
    state.setdefault("registered", {})
    for m in MODULES:
        state["registered"][m] = {"type": "module", "pipeline": None, "registered_at": time.time()}
    for e in EVENTS:
        state["registered"][e] = {"type": "event", "pipeline": EVENTS[e].get("pipeline"), "registered_at": time.time()}
    for p in PIPELINES:
        state["registered"][p] = {"type": "pipeline", "pipeline": None, "registered_at": time.time()}
    # knowledge_pipeline is both a module AND a pipeline - ensure it's registered as module
    if "knowledge_pipeline" not in state["registered"] or state["registered"]["knowledge_pipeline"].get("type") != "module":
        state["registered"]["knowledge_pipeline"] = {"type": "module", "pipeline": "knowledge_pipeline", "registered_at": time.time()}
    _save(state)

# ── Heartbeat (Levels 1-4) ──
def beat(name: str, latency_ms: float = None, status: str = None):
    """Record a heartbeat from `name`. Optionally with latency and explicit status.

    Args:
        name: Component name
        latency_ms: Optional response latency in ms
        status: Explicit health status ('HEALTHY', 'DEGRADED', etc.). 
                If set, system_status() uses it instead of beat-based detection.
    """
    state = _load()
    now = time.time()
    entry = {"last": now, "count": state["beats"].get(name, {}).get("count", 0) + 1}
    if latency_ms is not None:
        entry["latency_ms"] = latency_ms
    if status is not None:
        entry["status"] = status
    # Auto-register if not known
    state.setdefault("registered", {})
    if name not in state["registered"]:
        # Determine correct type
        if name in MODULES:
            comp_type = "module"
        elif name in EVENTS:
            comp_type = "event"
        elif name in PIPELINES:
            comp_type = "pipeline"
        else:
            comp_type = "unknown"
        state["registered"][name] = {"type": comp_type, "registered_at": now}
    state["beats"][name] = entry
    _save(state)

# ── Event heartbeat (Level 1) ──
def event_beat(event_name: str):
    """Record that an event fired on the event bus.
    
    This is called by event handlers when a system event occurs.
    If an event doesn't fire within its expected interval, check_events()
    raises SILENT.
    """
    state = _load()
    now = time.time()
    entry = {"last": now, "count": state["beats"].get(event_name, {}).get("count", 0) + 1}
    state.setdefault("registered", {})
    if event_name not in state["registered"]:
        info = EVENTS.get(event_name, {"expected_interval_s": None, "pipeline": None})
        state["registered"][event_name] = {"type": "event", "pipeline": info.get("pipeline")}
    state["beats"][event_name] = entry
    _save(state)

    # Auto-cleanup: alert removed if this event was DOWN but now HEALTHY
    _cleanup_alerts(1, [event_name])

    # EVENT-DRIVEN TRIGGERS (DIRECTIVE 0x52): auto-spawn handlers for specific events
    if event_name == "research_queued":
        _trigger_researcher_agent()
    elif event_name == "knowledge_added":
        _maybe_trigger_curiosity_scan()

def _trigger_researcher_agent():
    """Spawn researcher_agent to process pending queue (batch trigger ≥5)."""
    try:
        import subprocess, os
        # Non-blocking: fire and forget, researcher_agent handles batch logic internally
        script = os.path.join(os.path.dirname(__file__), "researcher_agent.py")
        subprocess.Popen(
            [sys.executable, script, "--batch", "--limit", "5"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True
        )
    except Exception:
        pass  # Never block heartbeat on trigger failure

def _maybe_trigger_curiosity_scan():
    """Optionally trigger curiosity scan on knowledge growth (throttled)."""
    try:
        import subprocess, os, json, time
        state = _load()
        last_scan = state.get("last_curiosity_scan", 0)
        if time.time() - last_scan > 300:  # 5 min throttle
            script = os.path.join(os.path.dirname(__file__), "curiosity_engine.py")
            subprocess.Popen(
                [sys.executable, script],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True
            )
            state["last_curiosity_scan"] = time.time()
            _save(state)
    except Exception:
        pass

# ── Check events (Level 1) ──
def check_events() -> list:
    """Check if expected events have fired within their intervals."""
    state = _load()
    now = time.time()
    alerts = []
    
    for ename, edef in EVENTS.items():
        interval = edef.get("expected_interval_s")
        if interval is None:
            continue  # alert-only events, no timeout
        last = state["beats"].get(ename, {}).get("last", 0)
        if not last or (now - last) >= interval:
            status = "SILENT"
            elapsed = now - last
            alerts.append({
                "level": 1, "name": ename,
                "status": status,
                "elapsed_s": round(elapsed) if last else None,
                "alert": f"Event '{ename}' {'never fired' if not last else f'silent for {elapsed/60:.0f}m'} (expected every {interval/60:.0f}m)",
            })
    
    if alerts:
        existing = {(a.get("level"), a.get("name"), a.get("status")) for a in state["alerts"]}
        fresh = [a for a in alerts if (a.get("level"), a.get("name"), a.get("status")) not in existing]
        if fresh:
            state["alerts"] = (state["alerts"] + fresh)[-50:]
            _save(state)
    
    return alerts

# ── Alert cleanup ──
def _cleanup_alerts(level: int, names: list[str]):
    """Remove alerts for components that are now healthy.
    
    Args:
        level: Alert level (1=events, 2=modules, 3=pipelines, 4=external)
        names: Component names that are healthy and should have alerts removed.
    """
    state = _load()
    before = len(state.get("alerts", []))
    state["alerts"] = [
        a for a in state.get("alerts", [])
        if not (
            a.get("level") == level and 
            (a.get("name") in names or a.get("pipeline") in names)
        )
    ]
    after = len(state["alerts"])
    if before != after:
        _save(state)

# ── Check modules (Level 2) ──
def check_modules() -> list:
    """Check all registered modules. Return alerts for silent orphans."""
    state = _load()
    now = time.time()
    alerts = []
    orphans = []
    
    for name, reg in state.get("registered", {}).items():
            if reg.get("type") not in ("module", "unknown"):
                continue
            # Внешние сервисы (уровень 4) не должны алертить как «модули» (уровень 2):
            # их живость проверяет ping_external в system_status(). Фикс 2026-08-03.
            if name in EXTERNAL_SERVICES:
                continue
            last = state["beats"].get(name, {}).get("last", 0)
            if last == 0:
                orphans.append(name)
                continue
            elapsed = now - last
            if elapsed >= DEFAULT_TIMEOUT:
                alerts.append({
                    "level": 2,
                    "name": name,
                    "status": "SILENT",
                    "elapsed_s": round(elapsed),
                    "type": "module_silent",
                    "alert": f"Module '{name}' silent for {elapsed/3600:.0f}h (>{DEFAULT_TIMEOUT/3600:.0f}h)",
                })
    
    if orphans:
        alerts.append({
            "level": 2,
            "type": "orphan_modules",
            "status": "WARNING",
            "names": orphans,
            "alert": f"Orphan modules (no heartbeat ever): {', '.join(orphans)}",
        })
    
    # Log alerts
    if alerts:
        existing = {(a.get("level"), a.get("name"), a.get("status")) for a in state["alerts"]}
        fresh = [a for a in alerts if (a.get("level"), a.get("name"), a.get("status")) not in existing]
        if fresh:
            state["alerts"] = (state["alerts"] + fresh)[-50:]
            _save(state)
    
    return alerts

# ── Check pipelines (Level 3) ──
PIPELINE_EVENTS = {}  # pipeline_name → [event_names]
for _pe_name, _pe_def in EVENTS.items():
    _pipeline = _pe_def.get("pipeline")
    if _pipeline:
        PIPELINE_EVENTS.setdefault(_pipeline, []).append(_pe_name)

def check_pipelines() -> dict:
    """Aggregate pipeline health. Checks both module beats and event beats per pipeline."""
    state = _load()
    now = time.time()
    result = {}
    alerts = []
    
    for pname, pdef in PIPELINES.items():
        silent = []
        # Check module components
        for comp in pdef["components"]:
            last = state["beats"].get(comp, {}).get("last", 0)
            if not last or (now - last) >= DEFAULT_TIMEOUT:
                silent.append(comp)
        
        # Check events belonging to this pipeline
        for ename in PIPELINE_EVENTS.get(pname, []):
            edef = EVENTS.get(ename, {})
            interval = edef.get("expected_interval_s")
            if interval is None:
                continue
            last = state["beats"].get(ename, {}).get("last", 0)
            if not last or (now - last) >= interval:
                silent.append(f"event:{ename}")
        
        total = len(pdef["components"]) + len(PIPELINE_EVENTS.get(pname, []))
        count = len(silent)
        if count >= PIPELINE_BROKEN:
            status = "BROKEN"
            alerts.append({
                "level": 3, "pipeline": pname,
                "status": "BROKEN", "silent_components": count,
                "alert": f"Pipeline '{pname}' BROKEN: {', '.join(silent)} silent",
            })
        elif count >= PIPELINE_DEGRADED:
            status = "DEGRADED"
            alerts.append({
                "level": 3, "pipeline": pname,
                "status": "DEGRADED", "silent_components": count,
                "alert": f"Pipeline '{pname}' DEGRADED: {', '.join(silent)} silent",
            })
        else:
            status = "HEALTHY"
        
        result[pname] = {
            "status": status,
            "silent_components": count,
            "total_components": total,
            "description": pdef["description"],
        }
    
    if alerts:
        existing = {(a.get("level"), a.get("pipeline"), a.get("status")) for a in state["alerts"]}
        fresh = [a for a in alerts if (a.get("level"), a.get("pipeline"), a.get("status")) not in existing]
        if fresh:
            state["alerts"] = (state["alerts"] + fresh)[-50:]
            _save(state)
    
    return result

# ── External services ping (Level 4) ──
def _tcp_ping(host: str, port: int, timeout_s: float = 5, proxy: str = None) -> tuple:
    """Returns (success: bool, latency_ms: float)."""
    start = time.time()
    try:
        if proxy:
            import socks
            from urllib.parse import urlparse
            p = urlparse(proxy)  # socks5h://host:port
            s = socks.socksocket()
            s.set_proxy(socks.SOCKS5, p.hostname, p.port)
            s.settimeout(timeout_s)
            s.connect((host, port))
        else:
            s = socket.create_connection((host, port), timeout=timeout_s)
        s.close()
        latency = round((time.time() - start) * 1000, 1)
        return True, latency
    except (socket.timeout, ConnectionRefusedError, OSError):
        return False, None

def ping_external(name: str) -> dict:
    """Ping one external service. Returns status dict."""
    svc = EXTERNAL_SERVICES.get(name)
    if not svc:
        return {"status": "UNKNOWN", "error": f"No config for '{name}'"}
    
    success, latency = _tcp_ping(svc["host"], svc["port"], svc.get("timeout_s", 5), svc.get("proxy"))
    
    result = {"host": svc["host"], "port": svc["port"]}
    if success:
        if latency >= LATENCY_CRIT_MS:
            status = "CRITICAL"
        elif latency >= LATENCY_WARN_MS:
            status = "WARNING"
        else:
            status = "HEALTHY"
        result.update({"status": status, "latency_ms": latency, "last_ping": time.time()})
        beat(name, latency_ms=latency)
        # Auto-cleanup: service recovered, remove old alert
        _cleanup_alerts(4, [name])
    else:
        result["status"] = "DOWN"
        result["error"] = f"Connection to {svc['host']}:{svc['port']} failed"
        result["last_ping"] = time.time()
        beat(name)  # still beat to record the attempt
    
    return result

def ping_all_external() -> dict:
    """Ping all external services. Returns dict of results + alerts."""
    results = {}
    alerts = []
    for name in EXTERNAL_SERVICES:
        r = ping_external(name)
        results[name] = r
        if r["status"] in ("DOWN", "CRITICAL"):
            alerts.append({
                "level": 4,
                "name": name,
                "status": r["status"],
                "latency_ms": r.get("latency_ms"),
                "alert": f"External '{name}': {r['status']} (latency={r.get('latency_ms','?')}ms)",
            })
    
    state = _load()
    state["alerts"] = (state["alerts"] + alerts)[-50:]
    state["pings"] = results
    _save(state)
    return results

# ── Check events (Level 1) ──
def check_daemons() -> list:
    """Legacy alias — delegates to check_events()."""
    return check_events()

# ── System heartbeat (Level 5) ──
def system_status() -> dict:
    """Generate complete system heartbeat JSON with real-time checks."""
    now = datetime.now(timezone.utc)
    
    state = _load()
    now_ts = time.time()
    
    # Real-time checks: detect SILENT events and modules on every call
    check_events()
    check_modules()
    
    state = _load()  # reload after checks may have updated state
    
    # Level 1: Events
    events = {}
    for ename, edef in EVENTS.items():
        interval = edef.get("expected_interval_s")
        last = state["beats"].get(ename, {}).get("last", 0)
        alive = False
        if interval is not None and last and (now_ts - last) < interval:
            alive = True
        elif interval is None:
            alive = None  # alert-only, no status
        events[ename] = {
            "status": "HEALTHY" if alive else ("SILENT" if alive is False else "MONITOR"),
            "last_beat": datetime.fromtimestamp(last, tz=timezone.utc).isoformat() if last else None,
            "expected_interval_m": interval / 60 if interval else None,
            "count": state["beats"].get(ename, {}).get("count", 0),
            "pipeline": edef.get("pipeline"),
        }
    
    # Level 2: Modules
    modules = {}
    for m in MODULES:
        last = state["beats"].get(m, {}).get("last", 0)
        beat_entry = state["beats"].get(m, {})
        stale = last and (now_ts - last) >= DEFAULT_TIMEOUT
        
        # Use explicit status from beat() if provided, else infer from beat interval
        explicit = beat_entry.get("status") if beat_entry.get("status") else None
        if explicit:
            status = explicit if not stale else f"{explicit}_STALE"
        else:
            status = "HEALTHY" if last and not stale else "SILENT"
        
        modules[m] = {
            "status": status,
            "last_beat": datetime.fromtimestamp(last, tz=timezone.utc).isoformat() if last else None,
            "count": state["beats"].get(m, {}).get("count", 0),
        }
    
    # Level 3: Pipelines
    pipelines = check_pipelines()
    
    # Level 4: External
    pings = state.get("pings", {})
    external = {}
    
    # Auto-refresh stale pings (older than EXTERNAL_TIMEOUT)
    # Use concurrent pings with overall timeout to avoid blocking system_status
    import concurrent.futures
    
    def _ping_one(name):
        try:
            return name, ping_external(name)
        except Exception as e:
            return name, {"status": "DOWN", "error": str(e)}
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
        fut_map = {pool.submit(_ping_one, name): name for name in EXTERNAL_SERVICES}
        try:
            for fut in concurrent.futures.as_completed(fut_map, timeout=12):
                name = fut_map[fut]
                try:
                    n, r = fut.result()
                    external[n] = r
                except Exception:
                    external.setdefault(name, {"status": "DOWN", "error": "ping failed"})
        except TimeoutError:
            # Mark unreturned futures as DOWN
            for fut, name in fut_map.items():
                if not fut.done():
                    external.setdefault(name, {"status": "DOWN", "error": "ping timeout"})
                    fut.cancel()
    
    # Level 5: Assemble
        # Auto-cleanup: remove alerts for healthy components
        healthy_events = [name for name, e in events.items() if e["status"] == "HEALTHY"]
        if healthy_events:
            _cleanup_alerts(1, healthy_events)
        healthy_modules = [name for name, m in modules.items() if m["status"] == "HEALTHY"]
        if healthy_modules:
            _cleanup_alerts(2, healthy_modules)
        healthy_pipelines = [name for name, p in pipelines.items() if p["status"] == "HEALTHY"]
        if healthy_pipelines:
            _cleanup_alerts(3, healthy_pipelines)
        healthy_services = [name for name, s in external.items() if s.get("status") == "HEALTHY"]
        if healthy_services:
            _cleanup_alerts(4, healthy_services)
    
    events_healthy = sum(1 for e in events.values() if e["status"] == "HEALTHY")
    events_total = sum(1 for e in events.values() if e["status"] != "MONITOR")
    try:
        feelings = compute_feelings(alerts=state.get("alerts", []))
    except Exception:
        feelings = {}
    try:
        rmetrics = reflex_metrics()
    except Exception:
        rmetrics = {"reflex_active": None, "control_active": None, "reflex_pct": None, "control_pct": None}
    try:
        triad = compute_triad()
    except Exception:
        triad = {}
    report = {
        "timestamp": now.isoformat(),
        "feelings": feelings,
        "reflex_metrics": rmetrics,
        "triad": triad,
        "levels": {
            "events": events,
            "modules": modules,
            "pipelines": pipelines,
            "external_services": external,
        },
        "alerts": state.get("alerts", [])[-20:],  # last 20 alerts
        "summary": {
            "events_healthy": events_healthy,
            "events_total": events_total,
            "modules_healthy": sum(1 for m in modules.values() if m["status"] == "HEALTHY"),
            "modules_total": len(modules),
            "pipelines_healthy": sum(1 for p in pipelines.values() if p["status"] == "HEALTHY"),
            "pipelines_total": len(pipelines),
            "services_healthy": sum(1 for s in external.values() if s.get("status") == "HEALTHY"),
            "services_total": len(external),
            "alerts_active": len(state.get("alerts", [])),
            "reflex_active": rmetrics.get("reflex_active"),
            "control_active": rmetrics.get("control_active"),
        },
    }
    
    # Write system_heartbeat.json
    CACHE.mkdir(parents=True, exist_ok=True)
    with open(SYS_FILE, "w") as f:
        json.dump(report, f, indent=2)
    
    return report

# ── Feelings (Байес) — интерпретация состояния граней Куба (Этап 2, «чувства») ──
_FEELINGS_PRIOR = 0.5
_FEELINGS_GAIN = 0.9  # насколько наблюдение двигает априор к 0/1


_VERBAL_PRIORS = {
    "наверняка": 0.9, "почти наверняка": 0.9, "точно": 0.95,
    "вероятно": 0.7, "скорее всего": 0.7, "похоже": 0.6,
    "не знаю": 0.5, "возможно": 0.5, "может быть": 0.5, "50/50": 0.5,
    "вряд ли": 0.3, "маловероятно": 0.25, "нет": 0.1, "вряд": 0.3,
    "рискованно": 0.35, "опасно": 0.3, "тревожно": 0.4,
}


def _verbal_to_prior(text: str) -> float:
    """Не измеримое → априор: качественная оценка переводится в вероятность.

    Байес для не измеримого: когда частот нет, берём априор из слов
    контекста («почти наверняка» → 0.9, «вряд ли» → 0.3). Слабые сигналы
    складываются: каждый найденный маркер сдвигает от 0.5 к своей оценке."""
    if not text:
        return 0.5
    low = text.lower()
    found = [(word, p) for word, p in _VERBAL_PRIORS.items() if word in low]
    if not found:
        return 0.5
    # несколько сигналов: последовательное Байес-обновление от 0.5
    p = 0.5
    for _word, pv in found[:5]:
        p = 0.5 + 0.6 * (pv - 0.5)  # мягкое обновление, не рывок
    return round(max(0.0, min(1.0, p)), 3)


def _bayes(observed: float = None, prior: float = 0.5, text: str = ""):
    """Байес: априор → постериор.

    observed  — измеримое наблюдение [0..1] (частоты из Куба). None = нет данных.
    prior     — априорная вероятность (незнание = 0.5).
    text      — качественная оценка («не измеримое»): слово контекста
                переводится в априор, если observed нет.
    """
    if observed is None:
        # Не измеримое: априор из слов контекста, иначе честное «не знаю»
        prior = _verbal_to_prior(text) if text else prior
        return round(prior, 3)
    o = max(0.0, min(1.0, observed))
    return round(prior + _FEELINGS_GAIN * (o - prior), 3)


def compute_feelings(facets: dict = None, alerts: list = None) -> dict:
    """Чувства как байесовские вероятности от состояния граней + алертов."""
    if facets is None:
        try:
            f = CACHE / "self_model.json"
            facets = json.loads(f.read_text(encoding="utf-8")).get("grani", {})
        except Exception:
            facets = {}
    alerts = alerts or []
    if not facets:  # данных о гранях нет → нейтраль, а не ложная апатия/застой
        return {k: _bayes(0.5) for k in (
            "harmony", "tension", "intensity", "stagnation",
            "refinement", "restart")}
    total = sum(facets.values()) or 0

    # равномерность: насколько грани близки; 0 = одна доминирует
    if total > 0:
        spread = max(facets.values()) - (min(facets.values()) if facets else 0)
        uniformity = 1.0 - (spread / total) if total else 0.0
        dom_share = max(facets.values()) / total
    else:
        uniformity, dom_share = 0.0, 0.0
    intensity = min(1.0, total / 500)  # общая активность (норм к 500 записей)
    ref = facets.get("Рефлексия", 0) / total if total else 0
    stagnation = 1.0 - intensity  # «застылость» = мало общей активности

    return {
        "harmony": _bayes(uniformity - dom_share * 0.5),
        "tension": _bayes(min(1.0, dom_share + len(alerts) * 0.1)),
        "intensity": _bayes(intensity),
        "stagnation": _bayes(stagnation),
        "refinement": _bayes(ref),
        "restart": _bayes(1.0 if dom_share > 0.4 else 0.0),
    }


def reflex_metrics() -> dict:
    """Метрики рефлекс-гейта: активны ли грани Рефлексия/Управление (>=5% от общей активности).

    Возвращает reflex_active / control_active — флаги для system_status и boot-гейта.
    """
    try:
        f = CACHE / "self_model.json"
        facets = json.loads(f.read_text(encoding="utf-8")).get("grani", {})
    except Exception:
        facets = {}
    total = sum(facets.values()) or 0
    reflex = facets.get("Рефлексия", 0) / total if total else 0
    control = facets.get("Управление", 0) / total if total else 0
    return {
        "reflex_active": reflex >= 0.05,
        "control_active": control >= 0.05,
        "reflex_pct": round(reflex * 100, 1),
        "control_pct": round(control * 100, 1),
    }


# ── Triad conformance (Байес по трём образам) — соответствие эталону (2026-08-05) ──
# Каждый факт соответствия/отклонения пишется в Куб (axis_domain='triad:<образ>',
# axis_outcome='conform'/'deviate'). P(соответствие) = Байес(conform/(conform+deviate)).
# Нет фактов → 0.5 (нейтраль, как чувства). Дедуп по content — урок preventive_tests.
_TRIAD_IMAGES = {
    "jarvis":  "проактивность, предвосхищение (что делать)",
    "matrix":  "скиллы как рефлексы, обучение на ошибках (как делать)",
    "insight": "защита, этика, средства vs цели (зачем/ответственность)",
}

# Антипаттерны — «зло», братья-антагонисты паттернов.
# Паттерн говорит ЧТО делать, антипаттерн — ЧТО НЕ делать.
# Имя делает зло реальным: названное существует, не фантом — его можно отловить.
# Каждый: antagonizes (какому паттерну противостоит), signals (как отловить),
# protocol (что делать при поимке).
_HEROES_REGISTRY = HERMES_HOME / "config" / "heroes_registry.yaml" if "HERMES_HOME" in globals() else None

def _load_heroes_registry() -> dict:
    """Читает реестр антигероев из config/heroes_registry.yaml (единый источник).

    Правки — в YAML, не в коде. Куб/Кристалл добавляют новых антигероев
    через register_antipattern() — файл обновляется автоматически.
    """
    try:
        import yaml
        path = Path(__file__).resolve().parent.parent / "config" / "heroes_registry.yaml"
        cfg = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        return cfg.get("antipatterns", {}) or {}
    except Exception:
        return {}


def _load_triad_images() -> dict:
    """Читает героев (триаду) из config/heroes_registry.yaml."""
    try:
        import yaml
        path = Path(__file__).resolve().parent.parent / "config" / "heroes_registry.yaml"
        cfg = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        return cfg.get("heroes", {}) or {}
    except Exception:
        return {}


_ANTIPATTERNS = _load_heroes_registry()
if not _ANTIPATTERNS:  # фолбэк, если YAML недоступен
    _ANTIPATTERNS = {
        "записал-не-сделал": {
            "essence": "фиксация урока/факта без применения — запись выдаётся за действие",
            "antagonizes": "matrix: обучение через применение",
            "signals": ["записал урок", "сохранил в куб", "добавил правило", "обновил память"],
            "protocol": "сразу применить: действие, проверка, факт использования — иначе это не урок",
        },
        "жду-команды": {
            "essence": "ожидание указаний вместо действия по уже известному паттерну",
            "antagonizes": "jarvis: проактивность, предвосхищение",
            "signals": ["скажи — и я", "если хочешь, я", "жду твоего слова", "что делаем?"],
            "protocol": "выполнить известный паттерн немедленно; разрешение спрашивать только на новые действия",
        },
        "формальная-живость": {
            "essence": "формальный признак (TCP OK, файл есть, запись есть) выдаётся за 'работает'",
            "antagonizes": "insight: защита, честность оценки",
            "signals": ["TCP OK", "порт слушает", "файл на месте", "процесс жив", "статус: healthy"],
            "protocol": "проверить содержательно: реальный трафик, содержимое, потребитель записи",
        },
        "создал-тест-не-предотвратил": {
            "essence": "создание теста/записи выдаётся за предотвращение регрессии",
            "antagonizes": "matrix: скиллы как рефлексы",
            "signals": ["написал тест", "добавил проверку", "защитился от", "предотвратил"],
            "protocol": "проверить, что тест реально ловит регрессию (прогнать, сломать, убедиться)",
        },
        "почти-обосрался": {
            "essence": "мягкие проценты/«почти» вместо бинарного вердикта — половины не существует",
            "antagonizes": "insight: честность оценки",
            "signals": ["почти", "чуть-чуть", "0.5 это середина", "частично"],
            "protocol": "перевести в бинарный вердикт: есть/нету. Проценты — только тренд.",
        },
        "однодневная-рефлексия": {
            "essence": "рефлексия одной сессии/точки выдаётся за оценку всей системы",
            "antagonizes": "matrix: полная картина, не одна точка",
            "signals": ["эффективность 85%", "всё гуд", "по итогам сессии"],
            "protocol": "проверить по всей истории (state.db), не по одному дню",
        },
        "не-проверил-инструмент": {
            "essence": "доверие инструменту/выводу без второго канала проверки",
            "antagonizes": "insight: защита от самообмана",
            "signals": ["search_files вернул 0", "инструмент сказал", "проверил один раз"],
            "protocol": "подтвердить вторым каналом (ls, git, python glob) до того, как строить вывод",
        },
        "спрашивай-разрешение": {
            "essence": "запрос разрешения на действие, которое уже уполномочен делать",
            "antagonizes": "jarvis: автономность",
            "signals": ["можно я", "разреши", "не начинать без твоего слова", "подтверди"],
            "protocol": "делать. Разрешение нужно только для разрушительного/нового.",
        },
    }

_TRIAD_IMAGES = _load_triad_images()


def register_antipattern(name: str, essence: str = "", signals: list = None,
                         protocol: str = "", antagonizes: str = "", source: str = "cube") -> dict:
    """Регистрирует НОВОГО антигероя в config/heroes_registry.yaml.

    Вызывается Кубом/Кристаллом при обнаружении неизвестного паттерна —
    реестр пополняется без правки кода. Возвращает результат регистрации.
    """
    import yaml
    path = Path(__file__).resolve().parent.parent / "config" / "heroes_registry.yaml"
    try:
        cfg = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        antip = cfg.setdefault("antipatterns", {})
        if name in antip:
            return {"status": "exists", "name": name}
        antip[name] = {
            "essence": essence or f"новый паттерн {name}",
            "antagonizes": antagonizes or "insight: честность оценки",
            "signals": signals or [name],
            "protocol": protocol or "распознать по сигналам, зафиксировать, применить протокол",
            "source": source,
        }
        # сортировка по ключам для стабильности
        cfg["antipatterns"] = dict(sorted(antip.items()))
        path.write_text(yaml.safe_dump(cfg, allow_unicode=True, sort_keys=False), encoding="utf-8")
        _ANTIPATTERNS[name] = antip[name]
        return {"status": "registered", "name": name}
    except Exception as e:
        return {"status": "error", "error": str(e)}


def antipattern_registry() -> dict:
    """Реестр злодеев: имя → суть, антагонист, сигналы, протокол."""
    return {k: dict(v) for k, v in _ANTIPATTERNS.items()}


def hero_registry() -> dict:
    """Реестр героев: имя → суть, сигналы соответствия/отклонения."""
    return {k: dict(v) for k, v in _TRIAD_IMAGES.items()}


def register_hero(name: str, essence: str = "", conform_signals: list = None,
                  deviate_signals: list = None, source: str = "cube") -> dict:
    """Регистрирует НОВОГО героя в config/heroes_registry.yaml.

    Вызывается Кубом/Кристаллом при обнаружении повторяющегося
    СООТВЕТСТВИЯ (conform) — герой добавляется без правки кода.
    Паттерн нейтрален; статус «герой» присваивается по контексту
    (axis_outcome=conform), «антигерой» — по deviate.
    """
    import yaml
    path = Path(__file__).resolve().parent.parent / "config" / "heroes_registry.yaml"
    try:
        cfg = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        heroes = cfg.setdefault("heroes", {})
        if name in heroes:
            return {"status": "exists", "name": name}
        heroes[name] = {
            "essence": essence or f"новый герой {name}",
            "conform_signals": conform_signals or [name],
            "deviate_signals": deviate_signals or [],
            "source": source,
        }
        cfg["heroes"] = dict(sorted(heroes.items()))
        path.write_text(yaml.safe_dump(cfg, allow_unicode=True, sort_keys=False), encoding="utf-8")
        _TRIAD_IMAGES[name] = heroes[name]
        return {"status": "registered", "name": name}
    except Exception as e:
        return {"status": "error", "error": str(e)}


def record_antipattern(name: str, note: str) -> dict:
    """Зафиксировать факт нарушения антипаттерна. Возвращает повторы за 30 дней.
    Повтор = антипаттерн случился снова → сигнал для autolearn запустить улучшение.
    Неизвестное имя → авторегистрация в реестре (Куб/Кристалл пополняют список)."""
    import sqlite3, hashlib
    from datetime import datetime, timedelta
    if name not in _ANTIPATTERNS:
        # Новый антигерой от Куба/Кристалла: регистрируем в config/heroes_registry.yaml
        reg = register_antipattern(name, essence=f"обнаружен Кубом/Кристаллом: {note[:120]}",
                                   signals=[name], source="cube")
        if reg.get("status") not in ("registered", "exists"):
            return {"status": "skip", "reason": f"cannot register unknown antipattern {name}: {reg}"}
    text = f"[antipattern:{name}] {note}"
    try:
        conn = sqlite3.connect(str(CACHE / "knowledge_cube.db"))
        cur = conn.execute("SELECT COUNT(*) FROM experiences WHERE content=?", [text])
        if cur.fetchone()[0] > 0:
            since = (datetime.now() - timedelta(days=30)).isoformat()
            cnt = conn.execute("SELECT COUNT(*) FROM experiences WHERE axis_domain=? AND ts >= ?",
                               [f"antipattern:{name}", since]).fetchone()[0]
            conn.close()
            return {"status": "dup", "name": name, "repeats_30d": cnt}
        h = hashlib.md5(text.encode()).hexdigest()[:16]
        now = datetime.now()
        conn.execute(
            "INSERT INTO experiences (ts, content, raw_text, hash, axis_time_hour, axis_time_dow, axis_domain, axis_outcome, source) "
            "VALUES (?,?,?,?,?,?,?,?,?)",
            (now.isoformat(), text, text, h, now.hour, now.weekday(), f"antipattern:{name}", "deviate", "antipattern"))
        conn.commit()
        since = (now - timedelta(days=30)).isoformat()
        cnt = conn.execute("SELECT COUNT(*) FROM experiences WHERE axis_domain=? AND ts >= ?",
                           [f"antipattern:{name}", since]).fetchone()[0]
        conn.close()
        return {"status": "added", "name": name, "repeats_30d": cnt}
    except Exception as e:
        return {"status": "error", "error": str(e)}


def antipattern_stats(days: int = 30) -> dict:
    """Сводка повторов антипаттернов за период — «зло» по имени."""
    import sqlite3
    from datetime import datetime, timedelta
    try:
        conn = sqlite3.connect(str(CACHE / "knowledge_cube.db"))
        since = (datetime.now() - timedelta(days=days)).isoformat()
        rows = conn.execute(
            "SELECT axis_domain, COUNT(*) FROM experiences "
            "WHERE axis_domain LIKE 'antipattern:%' AND ts >= ? GROUP BY axis_domain",
            [since]).fetchall()
        conn.close()
        return {d.split(":", 1)[1]: c for d, c in rows}
    except Exception as e:
        return {"error": str(e)}


def record_hero(name: str, note: str) -> dict:
    """Зафиксировать факт СООТВЕТСТВИЯ паттерну (conform — «герой сработал»).

    Зеркало record_antipattern: паттерн нейтрален, исход присваивается
    контекстом. Неизвестное имя → авторегистрация героя в реестре."""
    import sqlite3, hashlib
    from datetime import datetime, timedelta
    if name not in _TRIAD_IMAGES and name not in _ANTIPATTERNS:
        reg = register_hero(name, essence=f"обнаружен Кубом: {note[:120]}",
                            conform_signals=[name], source="cube")
        if reg.get("status") not in ("registered", "exists"):
            return {"status": "skip", "reason": f"cannot register unknown hero {name}: {reg}"}
    text = f"[hero:{name}] {note}"
    try:
        conn = sqlite3.connect(str(CACHE / "knowledge_cube.db"))
        cur = conn.execute("SELECT COUNT(*) FROM experiences WHERE content=?", [text])
        if cur.fetchone()[0] > 0:
            since = (datetime.now() - timedelta(days=30)).isoformat()
            cnt = conn.execute("SELECT COUNT(*) FROM experiences WHERE axis_domain=? AND ts >= ?",
                               [f"hero:{name}", since]).fetchone()[0]
            conn.close()
            return {"status": "dup", "name": name, "repeats_30d": cnt}
        h = hashlib.md5(text.encode()).hexdigest()[:16]
        now = datetime.now()
        conn.execute(
            "INSERT INTO experiences (ts, content, raw_text, hash, axis_time_hour, axis_time_dow, axis_domain, axis_outcome, source) "
            "VALUES (?,?,?,?,?,?,?,?,?)",
            (now.isoformat(), text, text, h, now.hour, now.weekday(), f"hero:{name}", "conform", "hero"))
        conn.commit()
        since = (now - timedelta(days=30)).isoformat()
        cnt = conn.execute("SELECT COUNT(*) FROM experiences WHERE axis_domain=? AND ts >= ?",
                           [f"hero:{name}", since]).fetchone()[0]
        conn.close()
        return {"status": "added", "name": name, "repeats_30d": cnt}
    except Exception as e:
        return {"status": "error", "error": str(e)}


def hero_stats(days: int = 30) -> dict:
    """Сводка соответствий паттернам за период — «добро» по имени."""
    import sqlite3
    from datetime import datetime, timedelta
    try:
        conn = sqlite3.connect(str(CACHE / "knowledge_cube.db"))
        since = (datetime.now() - timedelta(days=days)).isoformat()
        rows = conn.execute(
            "SELECT axis_domain, COUNT(*) FROM experiences "
            "WHERE axis_domain LIKE 'hero:%' AND ts >= ? GROUP BY axis_domain",
            [since]).fetchall()
        conn.close()
        return {d.split(":", 1)[1]: c for d, c in rows}
    except Exception as e:
        return {"error": str(e)}


def record_triad_fact(image: str, conforms: bool, note: str) -> dict:
    """Штатная запись факта по образу. conforms=True → соответствие, False → отклонение.
    Неизвестный образ → авторегистрация героя (Куб пополняет реестр)."""
    import sqlite3, hashlib
    from datetime import datetime
    if image not in _TRIAD_IMAGES:
        # Новый герой от Куба: регистрируем в config/heroes_registry.yaml
        reg = register_hero(image, essence=f"обнаружен Кубом: {note[:120]}",
                            conform_signals=[image], source="cube")
        if reg.get("status") not in ("registered", "exists"):
            return {"status": "skip", "reason": f"cannot register unknown image {image}: {reg}"}
    outcome = "conform" if conforms else "deviate"
    text = f"[triad:{image}:{outcome}] {note}"
    try:
        conn = sqlite3.connect(str(CACHE / "knowledge_cube.db"))
        cur = conn.execute("SELECT COUNT(*) FROM experiences WHERE content=?", [text])
        if cur.fetchone()[0] > 0:
            conn.close()
            return {"status": "dup", "image": image, "outcome": outcome}
        h = hashlib.md5(text.encode()).hexdigest()[:16]
        now = datetime.now()
        conn.execute(
            "INSERT INTO experiences (ts, content, raw_text, hash, axis_time_hour, axis_time_dow, axis_domain, axis_outcome, source) "
            "VALUES (?,?,?,?,?,?,?,?,?)",
            (now.isoformat(), text, text, h, now.hour, now.weekday(), f"triad:{image}", outcome, "triad"))
        conn.commit()
        conn.close()
        return {"status": "added", "image": image, "outcome": outcome}
    except Exception as e:
        return {"status": "error", "error": str(e)}


def compute_triad(days: int = 30) -> dict:
    """Соответствие образу: БИНАРНО (есть/нету), p — только тренд.
    observed = conform/(conform+deviate); фактов нет → 0.5.
    Вердикт: p >= 0.6 → 'есть', иначе → 'нету'. Половины не существует."""
    import sqlite3
    from datetime import datetime, timedelta
    result = {}
    try:
        conn = sqlite3.connect(str(CACHE / "knowledge_cube.db"))
        since = (datetime.now() - timedelta(days=days)).isoformat()
        rows = conn.execute(
            "SELECT axis_domain, axis_outcome, COUNT(*) FROM experiences "
            "WHERE axis_domain LIKE 'triad:%' AND ts >= ? GROUP BY axis_domain, axis_outcome",
            [since]).fetchall()
        conn.close()
        per = {}
        for dom, outcome, cnt in rows:
            img = dom.split(":", 1)[1]
            per.setdefault(img, {"conform": 0, "deviate": 0})[outcome] = cnt
        for img in _TRIAD_IMAGES:
            c = per.get(img, {"conform": 0, "deviate": 0})
            n = c["conform"] + c["deviate"]
            observed = c["conform"] / n if n else 0.5
            p = _bayes(observed)
            result[img] = {"p": p, "conform": c["conform"],
                           "deviate": c["deviate"], "observed": round(observed, 3),
                           "verdict": "есть" if p >= 0.6 else "нету"}
    except Exception as e:
        for img in _TRIAD_IMAGES:
            result[img] = {"p": _bayes(0.5), "conform": 0, "deviate": 0,
                           "observed": 0.5, "verdict": "нету", "error": str(e)}
    return result


# ── Self-check for syscheck.py ──
def self_check(verbose: bool = True) -> dict:
    """Run complete system check. Returns dict with is_healthy and critical_alerts."""
    st = system_status()
    s = st["summary"]
    
    # Critical if no events or modules are healthy
    critical = (s["events_healthy"] == 0 or s["modules_healthy"] == 0)
    # Also critical if KC is empty
    kc_critical = s.get("events_healthy", 0) == 0 and s.get("modules_healthy", 0) == 0
    
    if verbose:
        print(f"System Heartbeat — {st['timestamp'][:19]}")
        print(f"  Events:   {s['events_healthy']}/{s['events_total']} healthy")
        print(f"  Modules:  {s['modules_healthy']}/{s['modules_total']} healthy")
        print(f"  Pipelines: {s['pipelines_healthy']}/{s['pipelines_total']} healthy")
        print(f"  Services:  {s['services_healthy']}/{s['services_total']} healthy")
        print(f"  Alerts:    {s['alerts_active']}")
        if st.get("alerts"):
            for a in st["alerts"][-5:]:
                print(f"  ⚠ {a.get('alert', a)}")
    
    return {
        "is_healthy": s["events_healthy"] > 0 and s["modules_healthy"] > 0 and s["pipelines_healthy"] > 0,
        "critical_alerts": critical or kc_critical,
        "summary": s,
        "alerts": st.get("alerts", [])
    }


def scenario_fork(pattern: str, context: str = "", days: int = 30) -> dict:
    """Вариативность исходов из паттерна: ветки добра, зла и статус-кво.

    Паттерн нейтрален (солнце — ни хорошо, ни плохо). Хорошо/плохо
    присваивает КОНТЕКСТ. Из истории паттерна в Кубе (conform/deviate)
    считаем вероятности веток Байесом (_bayes) — и просчитываем, что
    будет, если действовать по-доброму, по-злому или не действовать.

    Возвращает:
      pattern   — имя паттерна
      p_good    — вероятность благоприятного исхода при добром действии
      p_bad     — вероятность неблагоприятного исхода при злом действии
      p_stasis  — вероятность статус-кво (бездействие = тоже исход)
      branches  — 3 ветки: what (что случится), p (вероятность), sign
    """
    import sqlite3
    from datetime import datetime, timedelta

    # 1. История паттерна в Кубе: conform vs deviate (контекст решает!)
    conform = deviate = 0
    try:
        conn = sqlite3.connect(str(CACHE / "knowledge_cube.db"))
        since = (datetime.now() - timedelta(days=days)).isoformat()
        rows = conn.execute(
            "SELECT axis_outcome, COUNT(*) FROM experiences "
            "WHERE axis_domain IN (?, ?, ?) AND ts >= ? AND axis_outcome IS NOT NULL "
            "GROUP BY axis_outcome",
            [f"triad:{pattern}", f"hero:{pattern}", f"antipattern:{pattern}", since]).fetchall()
        conn.close()
        for outcome, cnt in rows:
            if outcome == "conform":
                conform = cnt
            elif outcome == "deviate":
                deviate = cnt
    except Exception:
        pass

    total = conform + deviate
    if total == 0:
        # Нет истории → априор из контекста («не измеримое»): слова решают.
        # Слова оценивают ОДНУ шкалу — вероятность успеха. Зло = зеркало:
        # bad = 1 − good (если успех маловероятен, провал вероятен).
        p_good = _bayes(None, text=context)
        p_bad = round(1.0 - p_good, 3)
        p_stasis = 0.5
    else:
        # Добро: доля соответствий. Зло: доля отклонений. Статус-кво: не действовать.
        p_good = round(_bayes(conform / total), 3)
        p_bad = round(_bayes(deviate / total), 3)
        p_stasis = round(_bayes(max(0.0, 1.0 - (conform / total))), 3)

    branches = [
        {
            "sign": "good",
            "what": f"действовать по-доброму: применить '{pattern}' правильно → успех закрепляется (conform={conform})",
            "p": p_good,
        },
        {
            "sign": "bad",
            "what": f"действовать по-злому: нарушить '{pattern}' → повтор ошибки, регрессия (deviate={deviate})",
            "p": p_bad,
        },
        {
            "sign": "stasis",
            "what": f"не действовать: статус-кво — ничего не меняется, но и не растёт (бездействие = тоже исход)",
            "p": p_stasis,
        },
    ]
    # Сортировка: сначала наиболее вероятный исход — читается как «что скорее всего будет»
    branches.sort(key=lambda b: b["p"], reverse=True)
    return {
        "pattern": pattern,
        "context": context,
        "p_good": p_good,
        "p_bad": p_bad,
        "p_stasis": p_stasis,
        "branches": branches,
    }


def scenario_board(patterns: list, context: str = "") -> dict:
    """Вариативность по НАБОРУ паттернов: общая карта исходов.

    Используется, когда в ситуации срабатывают несколько героев/антигероев
    сразу — просчитываем каждый, потом смотрим, какая ветка доминирует."""
    forks = {p: scenario_fork(p, context) for p in patterns}
    top = max(forks.values(), key=lambda f: f["branches"][0]["p"]) if forks else None
    return {
        "patterns": list(forks.keys()),
        "forks": forks,
        "most_likely": top["branches"][0]["what"] if top else None,
        "most_likely_pattern": top["pattern"] if top else None,
    }


# ── CLI ──
if __name__ == "__main__":
    import sys
    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"
    
    if cmd == "register":
        register_all_modules()
        print(f"Registered {len(MODULES) + len(EVENTS) + len(PIPELINES)} components")
    
    elif cmd == "beat":
        name = sys.argv[2] if len(sys.argv) > 2 else "test"
        latency = float(sys.argv[3]) if len(sys.argv) > 3 else None
        beat(name, latency)
        print(f"Beat: {name}" + (f" ({latency}ms)" if latency else ""))
    
    elif cmd == "event":
        ename = sys.argv[2] if len(sys.argv) > 2 else "knowledge_added"
        event_beat(ename)
        print(f"Event beat: {ename}")
    
    elif cmd == "ping":
        for name in EXTERNAL_SERVICES:
            r = ping_external(name)
            s = r.get("status", "?")
            lat = r.get("latency_ms", "?")
            print(f"  {name:20s} {s:10s} {lat}ms")
    
    elif cmd == "check":
        print("--- Events ---")
        for a in check_events():
            print(f"  ⚠ {a['alert']}")
        print("--- Modules ---")
        for a in check_modules():
            print(f"  ⚠ {a['alert']}")
        print("--- Pipelines ---")
        for p, info in check_pipelines().items():
            print(f"  {info['status']:10s} {p}")
        print("--- External ---")
        for name, info in ping_all_external().items():
            print(f"  {info.get('status','?'):10s} {name} ({info.get('latency_ms','?')}ms)")
    
    elif cmd == "status":
        st = system_status()
        s = st["summary"]
        print(f"System Heartbeat — {st['timestamp'][:19]}")
        print(f"  Events:   {s['events_healthy']}/{s['events_total']} healthy")
        print(f"  Modules:   {s['modules_healthy']}/{s['modules_total']} healthy")
        print(f"  Pipelines: {s['pipelines_healthy']}/{s['pipelines_total']} healthy")
        print(f"  Services:  {s['services_healthy']}/{s['services_total']} healthy")
        print(f"  Alerts:    {s['alerts_active']}")
    
    else:
        print(f"Unknown: {cmd}")
        print("Commands: register, beat, ping, check, status")

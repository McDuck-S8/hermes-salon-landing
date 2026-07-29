#!/usr/bin/env python3
"""
Architecture Model — Crystal's self-map of Hermes system.

Scans filesystem, extracts modules & connections, writes model to Knowledge Cube.
Designed to be run by Crystal on each cycle.

Output: architecture state in KC as entries with tags ["architecture", "crystal", "model"]
"""

import json, os, re, sys, sqlite3, hashlib
from pathlib import Path
from datetime import datetime, timezone, timedelta

NOW = lambda: datetime.now(timezone.utc)

HERMES_HOME = Path(os.environ.get("HERMES_HOME", os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
KC_DB = HERMES_HOME / "data" / "knowledge_cube.db"
DEPRECATED_DIR = HERMES_HOME / "scripts" / "_deprecated"
SHAME_DAYS = 30  # files older than this get shamed

# ── Module definitions ──────────────────────────────────
MODULES = {
    "core": {
        "path": "scripts/",
        "label": "Core Engine & Events",
        "files": [
            "core_engine.py", "event_evolution.py", "hermes_hooks.py",
            "autonomous_agent.py",
            "proactive_executor.py", "proactive_doer.py",
        ],
        "layer": "engine",
        "tags": ["engine", "events", "scheduling"],
    },
    "event_system": {
        "path": "scripts/",
        "label": "Event Bus & Reactors",
        "files": [
            "event_bus.py", "event_bridge.py", "event_heartbeat.py",
            "event_classifier.py", "event_reactor.py",
            "event_registry.py", "event_sense.py", "event_trigger.py",
        ],
        "layer": "engine",
        "tags": ["events", "bus", "reactor"],
    },
    "knowledge": {
        "path": "scripts/",
        "label": "Knowledge Cube",
        "files": [
            "knowledge_cube.py", "cube_feeder.py", "cube_categorizer.py",
            "auto_recall.py", "knowledge_brain.py",
        ],
        "layer": "knowledge",
        "tags": ["kc", "memory", "recall"],
    },
    "knowledge_pipeline": {
        "path": "scripts/",
        "label": "Knowledge Pipeline",
        "files": [
            "knowledge_pipeline.py", "knowledge_filter_cron.py",
            "knowledge_gap_filler.py",
        ],
        "layer": "knowledge",
        "tags": ["kc", "pipeline", "cron"],
    },
    "llm": {
        "path": "scripts/",
        "label": "LLM Interface",
        "files": [
            "openrouter_client.py", "llm_classifier.py",
            "llm_client.py", "llm_filter.py", "llm_tracer.py",
        ],
        "layer": "io",
        "tags": ["llm", "api", "inference"],
    },
    "cron_tools": {
        "path": "cron/",
        "label": "Cron Jobs",
        "files": ["jobs.json"],
        "layer": "automation",
        "tags": ["cron", "monitoring"],
    },
    "tools": {
        "path": "tools/",
        "label": "CLI Tools",
        "files": ["amr_calc.py", "auto_compress.py", "hermes_compress.py", "price_monitor.py"],
        "layer": "io",
        "tags": ["cli", "tools"],
    },
    "telegram": {
        "path": "scripts/",
        "label": "Telegram Integration",
        "files": [
            "telegram_bridge.py", "tg_client.py",
            "telegram_poster.py", "telegram_helper.py",
            "telegram_cron_monitor.py", "telegram_daily_report.py",
            "telegram_delivery_report.py",
        ],
        "layer": "io",
        "tags": ["telegram", "messaging"],
    },
    "posting": {
        "path": "scripts/posting/",
        "label": "Content Posting",
        "files": [
            "post_all.py", "post_final.py", "post_frontier.py",
            "post_with_images.py", "ai_tools_poster.py",
        ],
        "layer": "action",
        "tags": ["posting", "content"],
    },
    "health": {
        "path": "scripts/",
        "label": "Health & Self-Monitor",
        "files": [
            "hermes_health.py", "hermes_heartbeat.py",
            "auto_recovery.py", "hermes_self_monitor.py",
            "hermes_self_upgrade.py",
        ],
        "layer": "self-improvement",
        "tags": ["health", "monitor", "recovery"],
    },
    "crystal_base": {
        "path": "scripts/crystal/",
        "label": "Crystal Knowledge Base",
        "files": ["knowledge_base.py"],
        "layer": "self-improvement",
        "tags": ["crystal", "kb"],
    },
    "plugins_websrch": {
        "path": "plugins/web-search-plus/",
        "label": "Web Search Plugin",
        "files": ["__init__.py", "search.py", "providers.py", "routing.py"],
        "layer": "io",
        "tags": ["plugin", "web"],
    },
    "plugins_selfev": {
        "path": "plugins/self-evolution/",
        "label": "Self-Evolution Plugin",
        "files": ["generate_report.py"],
        "layer": "self-improvement",
        "tags": ["plugin", "evolution"],
    },
    "plugins_icarus": {
        "path": "plugins/icarus/",
        "label": "Icarus Plugin",
        "files": ["__init__.py", "hooks.py", "tools.py", "state.py"],
        "layer": "self-improvement",
        "tags": ["plugin", "icarus"],
    },
    "plugins_lcm": {
        "path": "plugins/hermes-lcm/",
        "label": "LCM Plugin",
        "files": ["__init__.py", "engine.py", "dag.py", "config.py"],
        "layer": "self-improvement",
        "tags": ["plugin", "lcm"],
    },
    "curiosity": {
        "path": "scripts/",
        "label": "Curiosity Engine (restored)",
        "files": ["curiosity_engine.py"],
        "layer": "io",
        "tags": ["restored", "research", "discovery"],
    },
    "anomaly_detector": {
        "path": "scripts/",
        "label": "Anomaly Detector (restored)",
        "files": ["anomaly_detector.py"],
        "layer": "self-improvement",
        "tags": ["restored", "health", "anomaly"],
    },
    "orchestrator": {
        "path": "scripts/",
        "label": "Orchestrator (restored)",
        "files": ["orchestrator.py"],
        "layer": "engine",
        "tags": ["restored", "orchestrator", "chains"],
    },
    "market_research": {
        "path": "scripts/",
        "label": "Market Research (restored)",
        "files": ["market_research.py"],
        "layer": "io",
        "tags": ["restored", "research", "niches"],
    },
    "self_improvement_loop": {
        "path": "scripts/",
        "label": "Self-Improvement Loop (restored)",
        "files": ["self_improvement_loop.py"],
        "layer": "self-improvement",
        "tags": ["restored", "improvement", "patterns"],
    },
    "uncertainty_observer": {
        "path": "scripts/",
        "label": "Uncertainty Observer (restored)",
        "files": ["uncertainty_observer.py"],
        "layer": "self-improvement",
        "tags": ["restored", "philosophy", "analysis"],
    },
    "config": {
        "path": "",
        "label": "Configuration",
        "files": ["config.yaml"],
        "layer": "infra",
        "tags": ["config"],
    },
    "skills": {
        "path": "skills/",
        "label": "Skills Library",
        "files": ["self-improvement/crystal-architecture-awareness/SKILL.md"],
        "layer": "knowledge",
        "tags": ["skills", "library"],
    },
    "deprecated": {
        "path": "scripts/_deprecated/",
        "label": "Deprecated Scripts",
        "files": [],
        "layer": "infra",
        "tags": ["deprecated"],
        "orphan": True,
    },
}

# ── Connections (from→to, type) ────────────────────────
CONNECTIONS = [
    # Event flow
    ("core", "event_system", "data", "hooks → event_bus"),
    ("event_system", "knowledge", "data", "event_classifier → KC"),
    ("core", "knowledge", "data", "on_task_complete → KC write"),
    ("knowledge", "knowledge", "data", "recall → KC query"),
    ("knowledge", "knowledge", "data", "feeder → KC write"),
    # Knowledge pipeline
    ("knowledge_pipeline", "knowledge", "data", "filter → KC write"),
    ("knowledge_pipeline", "core", "data", "gap_filler → events"),
    # IO flow
    ("telegram", "core", "trigger", "incoming messages → hooks"),
    ("telegram", "core", "data", "daily_report → context"),
    ("plugins_websrch", "core", "data", "search results → context"),
    ("llm", "core", "data", "LLM responses → agent"),
    # Action flow
    ("core", "posting", "trigger", "cron → post"),
    ("tools", "core", "data", "CLI tools → execution"),
    # Health
    ("health", "core", "event", "heartbeat → health check"),
    ("health", "event_system", "event", "monitor → events"),
    # Self-improvement
    ("core", "plugins_selfev", "data", "events → evolution"),
    ("plugins_selfev", "knowledge", "data", "patterns → KC"),
    ("plugins_icarus", "core", "data", "suggestions → fixes"),
    ("plugins_lcm", "core", "data", "lifecycle → state"),
    ("crystal_base", "knowledge", "data", "KB ← KC queries"),
    # Infra
    ("config", "core", "config", "config → all modules"),
    ("skills", "knowledge", "reference", "skills → tool execution"),
]

# ── Helpers ────────────────────────────────────────────
KC_LOCK = os.path.join(os.path.dirname(str(KC_DB)), ".kc.lock")

def kc_connect():
    os.makedirs(os.path.dirname(str(KC_DB)), exist_ok=True)
    conn = sqlite3.connect(str(KC_DB))
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout=5000")
    conn.row_factory = sqlite3.Row
    conn.execute("""
        CREATE TABLE IF NOT EXISTS knowledge_cube (
            id TEXT PRIMARY KEY,
            content TEXT,
            tags TEXT,
            source TEXT,
            created_at TEXT,
            updated_at TEXT,
            entry_type TEXT DEFAULT 'knowledge',
            confidence REAL DEFAULT 1.0
        )
    """)
    conn.commit()
    return conn

def kc_insert(conn, entry):
    """Insert into knowledge_cube as an architecture entry"""
    h = hashlib.sha256(entry["content"].encode()).hexdigest()[:16]
    now = NOW().isoformat()
    conn.execute("""
        INSERT OR REPLACE INTO knowledge_cube 
        (id, content, tags, source, created_at, updated_at, entry_type, confidence)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        f"arch_{h}",
        entry["content"],
        json.dumps(entry.get("tags", [])),
        entry.get("source", "crystal"),
        now, now,
        entry.get("entry_type", "architecture"),
        1.0
    ))
    conn.commit()

def file_exists(path):
    return (HERMES_HOME / path).exists()

def get_file_hash(path):
    try:
        with open(HERMES_HOME / path, "rb") as f:
            return hashlib.md5(f.read()).hexdigest()[:8]
    except:
        return "?"

# ── Build snapshot ────────────────────────────────────
def build_modules_snapshot():
    """Check each module: what files exist, their hashes, health."""
    modules_state = {}
    for mid, mod in MODULES.items():
        files_state = {}
        for f in mod.get("files", []):
            p = str(Path(mod["path"]) / f) if mod["path"] != "skills/" else str(Path("skills") / "<category>" / f)
            fp = str(Path(mod["path"]) / f)
            exists = file_exists(fp)
            h = get_file_hash(fp) if exists else "?"
            files_state[f] = {"exists": exists, "hash": h}
        
        alive = sum(1 for fs in files_state.values() if fs.get("exists"))
        total = len(files_state) or 1
        health = "HEALTHY" if alive == total and total > 0 else ("DEGRADED" if alive > 0 else "DEAD")
        
        modules_state[mid] = {
            "label": mod["label"],
            "layer": mod["layer"],
            "files": files_state,
            "files_alive": alive,
            "files_total": total,
            "health": health,
            "tags": mod["tags"],
        }
    return modules_state

def build_connections_snapshot(modules_state):
    """Build connection list with health from module states."""
    conns = []
    for src, dst, ctype, desc in CONNECTIONS:
        src_alive = modules_state.get(src, {}).get("health") == "HEALTHY"
        dst_alive = modules_state.get(dst, {}).get("health") == "HEALTHY"
        status = "ACTIVE" if src_alive and dst_alive else "BROKEN"
        conns.append({
            "from": src,
            "to": dst,
            "type": ctype,
            "description": desc,
            "status": status,
        })
    return conns

def build_system_report(modules_state, connections, diff=None):
    """Human-readable system state."""
    lines = []
    lines.append(f"# Hermes Architecture Snapshot — {NOW().strftime('%Y-%m-%d %H:%M UTC')}")
    lines.append("")
    
    if diff:
        lines.append("## Changes since last scan")
        lines.extend(f"- {d}" for d in diff)
        lines.append("")
    
    layers = {}
    for mid, ms in modules_state.items():
        layers.setdefault(ms["layer"], []).append((mid, ms))
    
    for layer_name in ["engine", "knowledge", "io", "automation", "action", "self-improvement", "infra"]:
        if layer_name not in layers:
            continue
        items = layers[layer_name]
        # Filter out orphans from main display
        items = [(mid, ms) for mid, ms in items if not ms.get("orphan")]
        if not items:
            continue
        lines.append(f"## Layer: {layer_name.upper()}")
        for mid, ms in items:
            icon = {"HEALTHY": "✓", "DEGRADED": "⚠", "DEAD": "✗"}.get(ms["health"], "?")
            lines.append(f"  {icon} {ms['label']} ({mid}) — {ms['health']} [{ms['files_alive']}/{ms['files_total']} files]")
            for fn, fs in ms["files"].items():
                if fs["exists"]:
                    lines.append(f"    · {fn} [{fs['hash']}]")
        lines.append("")
    
    lines.append("## Connections")
    broken = [c for c in connections if c["status"] == "BROKEN"]
    active = [c for c in connections if c["status"] == "ACTIVE"]
    lines.append(f"  {len(active)} ACTIVE, {len(broken)} BROKEN")
    for c in connections:
        ic = "→" if c["status"] == "ACTIVE" else "✗"
        lines.append(f"  {ic} {c['from']} → {c['to']} [{c['type']}]: {c['description']}")
    
    lines.append("")
    lines.append("---")
    lines.append(f"Total: {len(modules_state)} modules, {len(connections)} connections")
    
    # Orphans/Deprecated section
    orphans = [(mid, ms) for mid, ms in modules_state.items() if ms.get("orphan")]
    if orphans:
        lines.append("")
        lines.append("## Orphaned / Deprecated")
        for mid, ms in orphans:
            lines.append(f"  ⊘ {ms['label']} ({mid}) — {ms['health']}")
    
    return "\n".join(lines)


# ── Deprecated Shame Counter ──────────────────────────
def scan_deprecated():
    """Scan _deprecated/ — file names, ages, shame flag."""
    files = []
    if not DEPRECATED_DIR.exists():
        return files, 0, 0
    now = NOW()
    for f in sorted(DEPRECATED_DIR.iterdir()):
        if not f.is_file() or f.suffix not in (".py", ".sh", ".json", ".yaml", ".yml", ".md"):
            continue
        mtime = datetime.fromtimestamp(f.stat().st_mtime, tz=timezone.utc)
        age_days = (now - mtime).days
        shamed = age_days >= SHAME_DAYS
        files.append({
            "name": f.name,
            "age_days": age_days,
            "shamed": shamed,
            "mtime": mtime.isoformat(),
            "size_kb": round(f.stat().st_size / 1024, 1),
        })
    total = len(files)
    shamed_count = sum(1 for f in files if f["shamed"])
    return files, total, shamed_count

def build_shame_report(files, total, shamed_count):
    """Build the shame counter section."""
    lines = []
    lines.append(f"## ⊘ Deprecated Shame Counter ({total} files, {shamed_count} shamed >{SHAME_DAYS}d)")
    if not files:
        lines.append("  (empty)")
        return "\n".join(lines)
    
    # Group by shame status
    shamed = [f for f in files if f["shamed"]]
    clean = [f for f in files if not f["shamed"]]
    
    if shamed:
        lines.append(f"\n  ⚠ SHAMED — older than {SHAME_DAYS} days — needs action:")
        for f in shamed[:20]:  # top 20
            lines.append(f"    🔴 {f['name']:40s} {f['age_days']:3d}d  {f['size_kb']:6.1f}KB")
        if len(shamed) > 20:
            lines.append(f"    ... and {len(shamed)-20} more")
    
    if clean:
        lines.append(f"\n  ✓ Not yet shamed — within {SHAME_DAYS} days:")
        for f in clean:
            lines.append(f"    🟢 {f['name']:40s} {f['age_days']:2d}d  {f['size_kb']:6.1f}KB")
    
    lines.append("")
    return "\n".join(lines)

def main(prev_snapshot=None):
    modules_state = build_modules_snapshot()
    connections = build_connections_snapshot(modules_state)
    
    # ── Shame counter ──
    deprecated_files, total_deprecated, shamed_count = scan_deprecated()
    shame_report = build_shame_report(deprecated_files, total_deprecated, shamed_count)
    
    # Detect changes from prev snapshot
    diff = []
    if prev_snapshot:
        for mid, ms in modules_state.items():
            prev = prev_snapshot.get(mid, {})
            if prev.get("health") != ms["health"]:
                diff.append(f"{ms['label']}: {prev.get('health', 'NEW')} → {ms['health']}")
    if not diff:
        diff = ["No changes detected"]
    
    report = build_system_report(modules_state, connections, diff)
    report += "\n\n" + shame_report
    
    # Write to KC
    conn = kc_connect()
    try:
        kc_insert(conn, {
            "content": report,
            "tags": ["architecture", "crystal", "model"],
            "source": "crystal",
            "entry_type": "architecture",
        })
        print(f"Architecture model written to Knowledge Cube")
        print(f"Modules: {len(modules_state)}, Connections: {len(connections)}, Changes: {len(diff)}")
    finally:
        conn.close()
    
    # Also save as JSON for programmatic access
    model = {
        "timestamp": NOW().isoformat(),
        "modules": modules_state,
        "connections": connections,
        "diff": diff,
        "deprecated": {
            "total": total_deprecated,
            "shamed": shamed_count,
            "files": deprecated_files,
        },
    }
    model_path = HERMES_HOME / "data" / "architecture_model.json"
    with open(model_path, "w") as f:
        json.dump(model, f, indent=2, default=str)
    print(f"Model saved to {model_path}")
    
    # Print summary
    healthy = sum(1 for m in modules_state.values() if m["health"] == "HEALTHY")
    degraded = sum(1 for m in modules_state.values() if m["health"] == "DEGRADED")
    dead = sum(1 for m in modules_state.values() if m["health"] == "DEAD")
    active_conns = sum(1 for c in connections if c["status"] == "ACTIVE")
    broken_conns = sum(1 for c in connections if c["status"] == "BROKEN")
    
    print(f"\nSummary: {healthy}✓ HEALTHY, {degraded}⚠ DEGRADED, {dead}✗ DEAD")
    print(f"         {active_conns}→ ACTIVE connections, {broken_conns}✗ BROKEN")
    print(f"         ⊘ {total_deprecated} deprecated files, {shamed_count} SHAMED >{SHAME_DAYS}d")
    
    # ── Heartbeat ──
    try:
        from chain_heartbeat import beat, event_beat, ping_all_external, system_status
        
        # Level 1: Fire architecture scan event
        event_beat("architecture_scan_complete")
        
        # Level 2: Each healthy module beats
        for mid, ms in modules_state.items():
            if ms.get("orphan"):
                continue
            if ms["health"] in ("HEALTHY", "DEGRADED"):
                # Pass explicit status so chain_heartbeat shows real module health
                beat(mid, status=ms["health"])
        
        # Level 3: Pipeline beats
        for pname in ["knowledge_pipeline", "self_improvement_pipeline", "action_pipeline"]:
            beat(f"pipeline:{pname}")
        
        # Level 4: External services ping
        ping_all_external()
        
        # Level 5: System heartbeat
        sys_st = system_status()
        beat("architecture_model")
    except ImportError:
        pass
    
    return modules_state, connections, diff

if __name__ == "__main__":
    # Load previous snapshot if exists
    model_path = HERMES_HOME / "data" / "architecture_model.json"
    prev = None
    if model_path.exists():
        with open(model_path) as f:
            try:
                prev = json.load(f).get("modules")
            except:
                pass
    
    main(prev_snapshot=prev)

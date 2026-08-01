#!/usr/bin/env python3
"""
Hermes Bootstrap — Autonomous startup sequence.
Loads state bundle, verifies integrity, applies pending fixes, starts crons, signals ready.
"""

import json
import os
import subprocess
import sys
import tarfile
import time
from datetime import datetime
from pathlib import Path

HERMES_HOME = Path(os.environ.get("HERMES_HOME", "D:/Portable_Soft/hermes"))
BUNDLE = HERMES_HOME / "system_state_backup.tar.gz"
STATE_FILE = HERMES_HOME / "cache" / "bootstrap_state.json"


def log(msg: str):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] [BOOTSTRAP] {msg}")


def load_state() -> dict:
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    return {"last_bundle_load": None, "fixes_applied": 0, "crons_started": 0}


def save_state(state: dict):
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")


def verify_bundle() -> bool:
    """Check bundle exists and is valid."""
    if not BUNDLE.exists():
        log(f"❌ Bundle not found: {BUNDLE}")
        return False
    try:
        with tarfile.open(BUNDLE, "r:gz") as tf:
            members = tf.getmembers()
            log(f"✅ Bundle valid: {len(members)} files, {BUNDLE.stat().st_size / 1024 / 1024:.1f} MB")
            return True
    except tarfile.TarError as e:
        log(f"❌ Bundle corrupt: {e}")
        return False


def verify_modules() -> tuple[bool, list[str]]:
    """Check critical modules exist and import."""
    critical = [
        "scripts.chain_heartbeat",
        "scripts.action_executor",
        "scripts.self_improvement_loop",
        "scripts.proactive_doer",
        "scripts.proactive_executor",
        "scripts.autonomous_agent",
        "scripts.suggestion_applier",
    ]
    missing = []
    for mod in critical:
        try:
            __import__(mod)
        except ImportError as e:
            missing.append(f"{mod}: {e}")
    if missing:
        log(f"❌ Missing modules: {missing}")
    else:
        log("✅ All critical modules import OK")
    return len(missing) == 0, missing


def restore_bundle():
    """Extract bundle to restore configs, scripts, skills."""
    log("Restoring bundle...")
    try:
        with tarfile.open(BUNDLE, "r:gz") as tf:
            tf.extractall(HERMES_HOME)
        log("✅ Bundle restored")
        return True
    except Exception as e:
        log(f"❌ Restore failed: {e}")
        return False


def apply_pending_fixes() -> int:
    """Apply pending fixes from improvement_suggestions.json via suggestion_applier."""
    suggestions_file = HERMES_HOME / "cache" / "improvement_suggestions.json"
    if not suggestions_file.exists():
        log("No suggestions file found")
        return 0
    try:
        # Run suggestion_applier directly
        result = subprocess.run(
            [sys.executable, "skills/self-improvement/suggestion_applier/scripts/suggestion_applier.py"],
            cwd=str(HERMES_HOME),
            capture_output=True,
            text=True,
            timeout=300,
        )
        if result.returncode == 0:
            applied = 0
            for line in result.stdout.split("\n"):
                if "Applied:" in line and "Failed:" in line:
                    parts = line.split()
                    for p in parts:
                        if p.isdigit():
                            applied = int(p)
                            break
            log(f"✅ Suggestion applier: {applied} applied")
            return applied
        else:
            log(f"❌ Suggestion applier failed: {result.stderr[:200]}")
            return 0
    except subprocess.TimeoutExpired:
        log("❌ Suggestion applier timeout")
        return 0
    except Exception as e:
        log(f"❌ Suggestion applier error: {e}")
        return 0


def start_crons() -> int:
    """Start cron scheduler and all enabled jobs."""
    log("Starting cron scheduler...")
    try:
        # Check if cron is already running
        result = subprocess.run(
            ["hermes", "cron", "status"],
            cwd=str(HERMES_HOME),
            capture_output=True,
            text=True,
            timeout=30,
        )
        if "running" in result.stdout.lower() or "active" in result.stdout.lower():
            log("✅ Cron already running")
            return 1
    except:
        pass
    try:
        # Start cron daemon
        subprocess.Popen(
            ["hermes", "cron", "start"],
            cwd=str(HERMES_HOME),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        time.sleep(2)
        log("✅ Cron started")
        return 1
    except Exception as e:
        log(f"❌ Cron start failed: {e}")
        return 0


def emit_heartbeat():
    """Emit system_ready event."""
    try:
        sys.path.insert(0, str(HERMES_HOME / "scripts"))
        from chain_heartbeat import event_beat
        event_beat("system_ready")
        log("✅ Event 'system_ready' emitted")
    except Exception as e:
        log(f"❌ Heartbeat emit failed: {e}")


def main():
    log("=" * 50)
    log("HERMES BOOTSTRAP STARTING")
    log("=" * 50)

    state = load_state()

    # 1. Verify bundle
    if not verify_bundle():
        log("Bundle verification failed — attempting restore from embedded configs")
        # Continue anyway with embedded configs

    # 2. Verify modules
    ok, missing = verify_modules()
    if not ok:
        log("Critical modules missing — restoring bundle")
        if not restore_bundle():
            log("❌ Cannot recover — aborting")
            sys.exit(1)

    # 3. Apply pending fixes
    applied = apply_pending_fixes()
    state["fixes_applied"] = state.get("fixes_applied", 0) + applied

    # 4. Start crons
    started = start_crons()
    state["crons_started"] = state.get("crons_started", 0) + started

    # 5. Emit ready heartbeat
    emit_heartbeat()

    # Save state
    state["last_bundle_load"] = datetime.now().isoformat()
    state["last_boot"] = datetime.now().isoformat()
    save_state(state)

    log("=" * 50)
    log("✅ BOOTSTRAP COMPLETE — SYSTEM READY")
    log(f"   Fixes applied: {applied}")
    log(f"   Crons started: {started}")
    log(f"   Bundle: {BUNDLE.stat().st_size / 1024 / 1024:.1f} MB")
    log("=" * 50)


if __name__ == "__main__":
    main()
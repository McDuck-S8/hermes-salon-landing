#!/usr/bin/env python3
"""
Kill Switches — Core switch management for Hermes.

Six hot-reloadable boolean gates for every dangerous boundary.
"""

import os
import sys
import time
import threading
from pathlib import Path
from typing import Dict, Any, Optional, Callable
from functools import wraps

# ─── config ─────────────────────────────────────────────────────────
HERMES_HOME = Path(os.environ.get("HERMES_HOME", "D:/Portable_Soft/hermes"))
ENV_FILE = HERMES_HOME / ".env"

# The six kill switches
KILL_SWITCHES = {
    "HERMES_LLM_ENABLED": {
        "description": "All LLM API calls (text, voice, agent chat, scheduler)",
        "default": True,
        "category": "llm"
    },
    "HERMES_CRON_ENABLED": {
        "description": "All scheduled task execution",
        "default": True,
        "category": "cron"
    },
    "HERMES_BRIDGE_ENABLED": {
        "description": "Telegram/Slack/Discord message delivery",
        "default": True,
        "category": "bridge"
    },
    "HERMES_KC_WRITE_ENABLED": {
        "description": "All Knowledge Cube writes",
        "default": True,
        "category": "knowledge"
    },
    "HERMES_SELF_MODIFY_ENABLED": {
        "description": "Self-modifying code (patches, skill updates)",
        "default": True,
        "category": "self_modify"
    },
    "HERMES_WARROOM_ENABLED": {
        "description": "War Room /standup and /discuss commands",
        "default": True,
        "category": "warroom"
    },
}

# Master switch
MASTER_SWITCH = "HERMES_KILL_SWITCHES_ENABLED"

# Cache
_switch_cache: Dict[str, bool] = {}
_cache_timestamp = 0
_cache_lock = threading.Lock()
_watcher_thread = None
_watcher_running = False


def _parse_env_file() -> Dict[str, str]:
    """Parse .env file into dict."""
    env_vars = {}
    if ENV_FILE.exists():
        try:
            content = ENV_FILE.read_text(encoding="utf-8")
            for line in content.splitlines():
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    env_vars[key.strip()] = value.strip()
        except Exception as e:
            print(f"[KILL_SWITCHES] Failed to parse .env: {e}")
    return env_vars


def _load_switches() -> Dict[str, bool]:
    """Load all switches from .env."""
    env_vars = _parse_env_file()
    switches = {}

    # Master switch
    master_enabled = env_vars.get(MASTER_SWITCH, "true").lower() == "true"

    for switch_name, config in KILL_SWITCHES.items():
        if not master_enabled:
            switches[switch_name] = False
        else:
            value = env_vars.get(switch_name, str(config["default"])).lower()
            switches[switch_name] = value in ("true", "1", "yes", "on")

    return switches


def refresh_cache() -> Dict[str, bool]:
    """Force refresh of switch cache."""
    global _switch_cache, _cache_timestamp
    with _cache_lock:
        _switch_cache = _load_switches()
        _cache_timestamp = time.time()
    return _switch_cache


def get_switches() -> Dict[str, bool]:
    """Get current switch states (cached, refreshed every 2 seconds)."""
    global _switch_cache, _cache_timestamp
    with _cache_lock:
        if time.time() - _cache_timestamp > 2.0:  # 2 second cache TTL
            _switch_cache = _load_switches()
            _cache_timestamp = time.time()
        return _switch_cache.copy()


def is_enabled(switch_name: str) -> bool:
    """Check if a kill switch is enabled."""
    if switch_name not in KILL_SWITCHES:
        raise ValueError(f"Unknown kill switch: {switch_name}. Valid: {list(KILL_SWITCHES.keys())}")
    return get_switches().get(switch_name, KILL_SWITCHES[switch_name]["default"])


def require_switch(switch_name: str) -> Callable:
    """Decorator: require kill switch to be enabled."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not is_enabled(switch_name):
                raise RuntimeError(
                    f"Kill switch '{switch_name}' is OFF. "
                    f"{KILL_SWITCHES[switch_name]['description']}. "
                    f"Set {switch_name}=true in .env to re-enable."
                )
            return func(*args, **kwargs)
        return wrapper
    return decorator


def check_switch(switch_name: str) -> bool:
    """Context manager: check switch, return False if disabled."""
    return is_enabled(switch_name)


class SwitchContext:
    """Context manager for kill switch checking."""

    def __init__(self, switch_name: str):
        self.switch_name = switch_name
        self.enabled = False

    def __enter__(self):
        self.enabled = is_enabled(self.switch_name)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def __bool__(self):
        return self.enabled


def audit_switch_flip(switch_name: str, old_value: bool, new_value: bool, reason: str = "") -> None:
    """Log switch flip to audit log."""
    try:
        audit_file = HERMES_HOME / "logs" / "kill_switch_audit.log"
        audit_file.parent.mkdir(parents=True, exist_ok=True)
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        with open(audit_file, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] KILL_SWITCH: {switch_name} {old_value} -> {new_value}")
            if reason:
                f.write(f" (reason: {reason})")
            f.write("\n")
    except Exception:
        pass  # Don't fail on audit logging


def set_switch(switch_name: str, value: bool, reason: str = "") -> bool:
    """Set a kill switch value in .env."""
    if switch_name not in KILL_SWITCHES:
        raise ValueError(f"Unknown kill switch: {switch_name}")

    try:
        # Read current .env
        lines = []
        if ENV_FILE.exists():
            lines = ENV_FILE.read_text(encoding="utf-8").splitlines()

        # Update or add the switch
        found = False
        new_lines = []
        for line in lines:
            if line.strip().startswith(f"{switch_name}="):
                new_lines.append(f"{switch_name}={str(value).lower()}")
                found = True
            else:
                new_lines.append(line)

        if not found:
            new_lines.append(f"{switch_name}={str(value).lower()}")

        # Write back
        ENV_FILE.write_text("\n".join(new_lines) + "\n", encoding="utf-8")

        # Audit log
        old_value = not value  # approximate
        audit_switch_flip(switch_name, old_value, value, reason)

        # Refresh cache
        refresh_cache()

        return True

    except Exception as e:
        print(f"[KILL_SWITCHES] Failed to set {switch_name}: {e}")
        return False


def start_hot_reload_watcher():
    """Start file watcher for .env changes."""
    global _watcher_thread, _watcher_running

    if _watcher_running:
        return

    _watcher_running = True

    def watcher():
        last_mtime = 0
        while _watcher_running:
            try:
                if ENV_FILE.exists():
                    mtime = ENV_FILE.stat().st_mtime
                    if mtime != last_mtime:
                        last_mtime = mtime
                        print("[KILL_SWITCHES] .env changed, refreshing switches...")
                        refresh_cache()
            except Exception:
                pass
            time.sleep(1)  # Check every second

    _watcher_thread = threading.Thread(target=watcher, daemon=True)
    _watcher_thread.start()
    print("[KILL_SWITCHES] Hot reload watcher started")


def stop_hot_reload_watcher():
    """Stop file watcher."""
    global _watcher_running, _watcher_thread
    _watcher_running = False
    if _watcher_thread:
        _watcher_thread.join(timeout=2)
    print("[KILL_SWITCHES] Hot reload watcher stopped")


def status() -> Dict[str, Any]:
    """Get status of all kill switches."""
    switches = get_switches()
    master = os.environ.get(MASTER_SWITCH, "true").lower() == "true"

    return {
        "master_enabled": master,
        "switches": {
            name: {
                "enabled": switches.get(name, config["default"]),
                "description": config["description"],
                "category": config["category"]
            }
            for name, config in KILL_SWITCHES.items()
        },
        "cache_age_seconds": time.time() - _cache_timestamp
    }


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Kill Switches Management")
    parser.add_argument("command", choices=["status", "enable", "disable", "watch", "test"],
                       help="Command to run")
    parser.add_argument("switch", nargs="?", help="Switch name (for enable/disable)")
    parser.add_argument("--reason", help="Reason for switch change")

    args = parser.parse_args()

    if args.command == "status":
        s = status()
        print(f"Master ({MASTER_SWITCH}): {'ON' if s['master_enabled'] else 'OFF'}")
        print()
        for name, info in s["switches"].items():
            status_str = "ON" if info["enabled"] else "OFF"
            print(f"  {name}: {status_str} — {info['description']}")
        print(f"\nCache age: {s['cache_age_seconds']:.1f}s")

    elif args.command == "enable":
        if not args.switch:
            print("Error: switch name required")
            sys.exit(1)
        if set_switch(args.switch, True, args.reason or "manual enable"):
            print(f"Enabled: {args.switch}")
        else:
            print(f"Failed to enable: {args.switch}")
            sys.exit(1)

    elif args.command == "disable":
        if not args.switch:
            print("Error: switch name required")
            sys.exit(1)
        if set_switch(args.switch, False, args.reason or "manual disable"):
            print(f"Disabled: {args.switch}")
        else:
            print(f"Failed to disable: {args.switch}")
            sys.exit(1)

    elif args.command == "watch":
        print("Starting hot reload watcher (Ctrl+C to stop)...")
        start_hot_reload_watcher()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            stop_hot_reload_watcher()
            print("Stopped.")

    elif args.command == "test":
        # Test all switches
        print("Testing kill switches...")
        for name in KILL_SWITCHES:
            print(f"  {name}: {'ON' if is_enabled(name) else 'OFF'}")
        print("Done.")


if __name__ == "__main__":
    main()
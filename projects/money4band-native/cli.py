"""
Money4Band Native — CLI Interface
══════════════════════════════════
Command-line interface for managing the M4B stack.
Usage:
  python cli.py status          — Show all apps status
  python cli.py start [app]     — Start all or specific app
  python cli.py stop [app]      — Stop all or specific app
  python cli.py setup           — Interactive setup wizard
  python cli.py dashboard       — Start web dashboard
"""

import sys
import json
import asyncio
from pathlib import Path

from manager import M4BManager
from apps import RUNNERS


def cmd_status(manager: M4BManager):
    """Show status of all apps."""
    status = manager.get_all_status()
    if not status:
        print("\n  No apps configured. Run: python cli.py setup\n")
        return
    
    print("\n" + "=" * 60)
    print("  MONEY4BAND NATIVE — Status")
    print("=" * 60)
    
    for s in status:
        icon = "🟢" if s["running"] else ("⚪" if s["config_ok"] else "🔴")
        print(f"\n  {icon} {s['name'].upper()}")
        print(f"     Running: {s['running']}  |  PID: {s['pid'] or '-'}")
        print(f"     Uptime:  {s['uptime']}  |  Earnings: {s['earnings']}")
        print(f"     Config:  {'OK' if s['config_ok'] else 'INCOMPLETE'}")
        if s["error"]:
            print(f"     ⚠️  Error: {s['error']}")
    
    print("\n" + "=" * 60 + "\n")


def cmd_start(manager: M4BManager, app_name: str = None):
    """Start all apps or a specific one."""
    if app_name:
        if app_name not in manager.runners:
            print(f"App '{app_name}' not found. Available: {list(manager.runners.keys())}")
            return
        runner = manager.runners[app_name]
        success = runner.start()
        print(f"{'✅' if success else '❌'} {app_name}: {'started' if success else runner.status.error}")
    else:
        results = manager.start_all()
        for name, ok in results.items():
            print(f"{'✅' if ok else '❌'} {name}")


def cmd_stop(manager: M4BManager, app_name: str = None):
    """Stop all apps or a specific one."""
    if app_name:
        if app_name not in manager.runners:
            print(f"App '{app_name}' not found")
            return
        manager.runners[app_name].stop()
        print(f"⏹️  {app_name}: stopped")
    else:
        manager.stop_all()
        print("⏹️  All apps stopped")


def cmd_setup(manager: M4BManager):
    """Interactive setup wizard."""
    print("\n🔧 Money4Band Native — Setup Wizard\n")
    print("Available apps:")
    for i, name in enumerate(RUNNERS.keys(), 1):
        print(f"  {i}. {name}")
    
    print(f"\n  0. Exit\n")
    
    choice = input("Select app to configure (number): ").strip()
    if not choice or choice == "0":
        return
    
    try:
        idx = int(choice) - 1
        app_names = list(RUNNERS.keys())
        if idx < 0 or idx >= len(app_names):
            print("Invalid choice")
            return
    except ValueError:
        print("Invalid choice")
        return
    
    app_name = app_names[idx]
    print(f"\n--- Configure {app_name} ---\n")
    
    # Get fields from user
    runner_cls = RUNNERS[app_name]
    # Create dummy instance to check what config fields are needed
    dummy = runner_cls({"enabled": True}, Path("./data"))
    
    print("Enter your credentials (leave blank to skip):")
    fields = {
        "honeygain": ["email", "password", "device_token"],
        "earnapp": ["redeem_code", "email"],
        "packetstream": ["psk"],
        "pawns": ["email", "password", "invite_code"],
        "traffmonetizer": ["token"],
        "peer2profit": ["token"],
        "bitping": ["node_key", "email", "password"],
    }
    
    config = {"enabled": True}
    for field in fields.get(app_name, []):
        val = input(f"  {field}: ").strip()
        if val:
            config[field] = val
    
    # Update config.yaml
    import yaml
    with open(manager.config_path, "r", encoding="utf-8") as f:
        full_config = yaml.safe_load(f) or {}
    
    if "apps" not in full_config:
        full_config["apps"] = {}
    full_config["apps"][app_name] = config
    
    with open(manager.config_path, "w", encoding="utf-8") as f:
        yaml.dump(full_config, f, default_flow_style=False, allow_unicode=True)
    
    print(f"\n✅ {app_name} configured! Restart M4B to apply.\n")


def cmd_dashboard(manager: M4BManager):
    """Start the web dashboard."""
    try:
        from dashboard import run_dashboard
        port = manager.config.get("global", {}).get("dashboard_port", 8080)
        run_dashboard(manager, port)
    except ImportError:
        print("Dashboard module not found. Install: pip install aiohttp")
    except Exception as e:
        print(f"Dashboard error: {e}")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    
    cmd = sys.argv[1]
    manager = M4BManager("config.yaml")
    manager.init_runners()
    
    if cmd == "status":
        cmd_status(manager)
    elif cmd == "start":
        app = sys.argv[2] if len(sys.argv) > 2 else None
        cmd_start(manager, app)
    elif cmd == "stop":
        app = sys.argv[2] if len(sys.argv) > 2 else None
        cmd_stop(manager, app)
    elif cmd == "setup":
        cmd_setup(manager)
    elif cmd == "dashboard":
        cmd_dashboard(manager)
    else:
        print(f"Unknown command: {cmd}")
        print(__doc__)


if __name__ == "__main__":
    main()

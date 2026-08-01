#!/usr/bin/env python3
"""
Salon Bot Deploy - запуск бота с отдельным токеном.


> Revisit: when deploy salon logic, deployment steps, or salon bot deployment changes. Last touched: 2026-07-02.
Usage:
  python scripts/deploy_salon.py YOUR_BOT_TOKEN
  python scripts/deploy_salon.py --test YOUR_BOT_TOKEN  (getMe only)
"""
import sys
import os
import subprocess
from pathlib import Path

HERMES_HOME = Path(__file__).resolve().parent.parent
SALON_BOT = HERMES_HOME / "scripts" / "salon_bot.py"


def deploy(token: str, test_only: bool = False):
    if not token or len(token) < 30:
        print(f"Invalid token: {token[:10]}...")
        return False

    # Verify bot with getMe
    print(f"Testing token {token[:8]}...{token[-4:]}")
    import json
    import urllib.request
    try:
        req = urllib.request.Request(
            f"https://api.telegram.org/bot{token}/getMe",
            headers={"User-Agent": "Hermes/1.0"}
        )
        resp = urllib.request.urlopen(req, timeout=10)
        data = json.loads(resp.read())
        if data.get("ok"):
            bot = data["result"]
            print(f"OK: @{bot.get('username')} ({bot.get('first_name')})")
            if test_only:
                return True
        else:
            print(f"FAILED: {data}")
            return False
    except Exception as e:
        print(f"Network error: {e}")
        return False

    # Start salon bot
    print(f"Starting salon_bot.py...")
    env = os.environ.copy()
    env["TELEGRAM_BOT_TOKEN"] = token

    proc = subprocess.Popen(
        [sys.executable, str(SALON_BOT)],
        cwd=str(HERMES_HOME / "scripts"),
        env=env,
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0)
    )
    print(f"Started PID {proc.pid}")

    # Save PID
    pid_file = HERMES_HOME / "cache" / "salon_bot.pid"
    pid_file.write_text(str(proc.pid))
    print(f"PID saved to {pid_file}")
    return True


def main():
    args = sys.argv[1:]
    test_only = "--test" in args
    if test_only:
        args.remove("--test")

    if not args:
        print("Usage: deploy_salon.py [--test] BOT_TOKEN")
        return

    deploy(args[0], test_only)


if __name__ == "__main__":
    main()

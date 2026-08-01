#!/usr/bin/env python3
"""
Signal Pipeline — event-driven оркестратор.
Цепочка: Signal Scanner → R&D Processor → Dev Processor.

> Revisit: when signal pipeline stages, brick extraction, or workshop integration changes. Last touched: 2026-07-02.

Запускается Watchdog каждые 5 минут.
Usage:
    python scripts/signal_pipeline.py           # full pipeline
    python scripts/signal_pipeline.py --quick   # scan only (no dev)
    python scripts/signal_pipeline.py --status  # all metrics
"""
import subprocess
import sys
from pathlib import Path
from datetime import datetime

HERMES_HOME = Path(__file__).resolve().parent.parent
SCRIPTS = HERMES_HOME / "scripts"
CACHE_DIR = HERMES_HOME / "cache"
ALERTS_FILE = CACHE_DIR / "ALERTS.md"


def run_script(name: str, args: list = None) -> tuple:
    """Run a script and return (exit_code, stdout)."""
    cmd = [sys.executable, str(SCRIPTS / name)] + (args or [])
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60,
            cwd=str(HERMES_HOME)
        )
        return result.returncode, result.stdout.strip()
    except subprocess.TimeoutExpired:
        return 1, "TIMEOUT"
    except Exception as e:
        return 1, str(e)


def add_alert(severity: str, description: str):
    """Add alert to ALERTS.md."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    alert = f"\n## [{severity}] {datetime.now().strftime('%Y-%m-%d %H:%M')} — {description}\n"
    if ALERTS_FILE.exists():
        with open(ALERTS_FILE, "a", encoding="utf-8") as f:
            f.write(alert)
    else:
        ALERTS_FILE.write_text(f"# ALERTS\n{alert}", encoding="utf-8")


def pipeline(quick=False):
    """Run the full signal pipeline."""
    print(f"=== Signal Pipeline {datetime.now().strftime('%Y-%m-%d %H:%M')} ===")

    # Step 1: Scan for new signals
    print("\n[1/3] Scanning for signals...")
    code, out = run_script("signal_scanner.py")
    print(f"  Scanner: {out}")

    # Step 2: Process through R&D
    if not quick:
        print("\n[2/3] R&D processing...")
        code, out = run_script("rd_processor.py")
        print(f"  R&D: {out}")

        # Step 3: Dev processor — create goals for gaps
        print("\n[3/3] Dev processing...")
        code, out = run_script("dev_processor.py")
        print(f"  Dev: {out}")
    else:
        print("\n[Quick mode — skipping R&D and Dev]")

    # Check metrics and alert
    check_daily_metrics()
    print("\n=== Pipeline complete ===")


def check_daily_metrics():
    """Check daily metrics, create alerts if needed."""
    today = datetime.now().strftime("%Y-%m-%d")

    # R&D: ≥1 brick per day
    bricks_log = CACHE_DIR / "bricks_log.jsonl"
    if bricks_log.exists():
        lines = bricks_log.read_text("utf-8").strip().split("\n")
        today_bricks = [l for l in lines if today in l and '"added"' in l]
        if len(today_bricks) == 0:
            # Check if this is first run of day
            today_alerts = [l for l in lines if today in l and '"alert_no_bricks"' in l]
            if len(today_alerts) == 0:
                add_alert("WARNING", f"R&D: 0 новых кирпичей за {today}")
                print(f"  ALERT: R&D 0 bricks today")

    # Dev: ≥1 lesson per day
    lessons_file = HERMES_HOME / "LESSONS.md"
    if lessons_file.exists():
        content = lessons_file.read_text("utf-8")
        if today not in content:
            add_alert("WARNING", f"Отдел развития: 0 уроков за {today}")
            print(f"  ALERT: Development 0 lessons today")


def status():
    """Show all metrics."""
    print("=== Signal Pipeline Status ===\n")

    # Scanner
    signals_file = CACHE_DIR / "signals.jsonl"
    if signals_file.exists():
        lines = signals_file.read_text("utf-8").strip().split("\n")
        print(f"Signals total: {len(lines)}")
    else:
        print("Signals: 0")

    # R&D
    bricks_log = CACHE_DIR / "bricks_log.jsonl"
    if bricks_log.exists():
        lines = bricks_log.read_text("utf-8").strip().split("\n")
        added = sum(1 for l in lines if '"added"' in l)
        skipped = sum(1 for l in lines if '"skip_exists"' in l)
        print(f"Bricks added: {added}")
        print(f"Bricks skipped: {skipped}")
    else:
        print("Bricks: 0")

    # Dev
    dev_log = CACHE_DIR / "dev_log.jsonl"
    if dev_log.exists():
        lines = dev_log.read_text("utf-8").strip().split("\n")
        goals = sum(1 for l in lines if '"goal_created"' in l)
        print(f"Goals created: {goals}")
    else:
        print("Goals: 0")

    # Goals
    goals_file = CACHE_DIR / "goal_queue.json"
    if goals_file.exists():
        try:
            data = json.loads(goals_file.read_text("utf-8"))
            goals = data.get("goals", [])
            active = sum(1 for g in goals if g.get("status") == "active")
            print(f"Active goals: {active}")
        except Exception:
            pass

    # Alerts
    alerts_file = CACHE_DIR / "ALERTS.md"
    if alerts_file.exists():
        content = alerts_file.read_text("utf-8")
        alert_count = content.count("## [")
        print(f"Total alerts: {alert_count}")


def main():
    import json
    if "--status" in sys.argv:
        status()
        return

    if "--quick" in sys.argv:
        pipeline(quick=True)
    else:
        pipeline()


if __name__ == "__main__":
    main()

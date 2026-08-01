#!/usr/bin/env python3
"""Соединяет anomaly-detector → proactive-doer.
Когда детектор находит красные лампочки — doer получает алерт и чинит."""

import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime

HERMES = Path("D:/Portable_Soft/hermes")
ALERTS_FILE = HERMES / "cache" / "red_alerts.json"
BRIDGE_FILE = HERMES / "cache" / "alert_bridge.json"

def load_alerts():
    if not ALERTS_FILE.exists():
        return None
    return json.loads(ALERTS_FILE.read_text())

def escalate_to_doer(alerts):
    """Формирует задачу для proactive-doer и сохраняет в мост."""
    tasks = []
    for alert in alerts.get("actionable", []):
        task = {
            "source": "anomaly-detector",
            "target": "proactive-doer",
            "type": alert.get("type", "unknown"),
            "domain": alert.get("domain", ""),
            "message": alert.get("message", ""),
            "severity": alert.get("severity", "info"),
            "created_at": datetime.now().isoformat(),
            "status": "pending"
        }
        tasks.append(task)
    
    bridge = {
        "updated_at": datetime.now().isoformat(),
        "tasks": tasks,
        "summary": {
            "total": len(tasks),
            "critical": sum(1 for t in tasks if t["severity"] == "critical"),
            "warning": sum(1 for t in tasks if t["severity"] == "warning")
        }
    }
    
    BRIDGE_FILE.parent.mkdir(parents=True, exist_ok=True)
    BRIDGE_FILE.write_text(json.dumps(bridge, indent=2, ensure_ascii=False))
    return bridge["summary"]

def main():
    alerts = load_alerts()
    if not alerts:
        print("[Bridge] Нет алертов — нечего передавать")
        return

    actionable = alerts.get("actionable", [])
    if not actionable:
        print("[Bridge] Есть алерты, но нет actionable — ждём")
        return

    summary = escalate_to_doer(alerts)
    print(f"[Bridge] Передано {summary['total']} задач doer'у")
    print(f"  Критических: {summary['critical']}")
    print(f"  Предупреждений: {summary['warning']}")
    print(f"  Мост: {BRIDGE_FILE}")

if __name__ == "__main__":
    main()

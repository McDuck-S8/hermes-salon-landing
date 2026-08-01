#!/usr/bin/env python3
"""
Infrastructure Alert System — для subagent'ов и любых процессов.
Пишет алерт → фиксер читает и чинит.

Использование из subagent:
    from scripts.alert_system import alert
    alert("proxy_down", "SOCKS5 127.0.0.1:10806 не отвечает", severity="critical")

Или из командной строки:
    python scripts/alert_system.py proxy_down "SOCKS5 proxy timeout"
"""
import json, os, sys, time, subprocess
from pathlib import Path
from datetime import datetime

ALERTS_DIR = Path(__file__).resolve().parent.parent / "cache" / "alerts"
ALERTS_DIR.mkdir(parents=True, exist_ok=True)

FIX_ACTIONS = {
    "proxy_down": [
        ("Проверить v2rayN", "tasklist //FI 'IMAGENAME eq v2rayN.exe' 2>nul | findstr v2rayN", "process check"),
        ("Перезапустить v2rayN", 'start "" "C:\\Users\\Asus\\AppData\\Local\\v2rayN\\v2rayN.exe"', "restart"),
    ],
    "network_blocked": [
        ("Проверить DNS", "nslookup google.com 2>&1 | findstr 'Address'", "dns check"),
        ("Проверить gateway", "curl -s --connect-timeout 3 https://api.telegram.org 2>&1", "gateway check"),
    ],
    "youtube_blocked": [
        ("Проверить прокси", "curl -s --socks5 127.0.0.1:10806 --connect-timeout 5 https://www.youtube.com 2>&1", "proxy check"),
        ("Проверить yt-dlp", "yt-dlp --proxy socks5://127.0.0.1:10806 --print title 'https://www.youtube.com/watch?v=dQw4w9WgXcQ' --timeout 5 2>&1", "yt-dlp check"),
    ],
}

def alert(alert_type: str, message: str, severity: str = "error", source: str = "system"):
    """Записать алерт. Вызывается откуда угодно — из subagent, скрипта, демона."""
    aid = f"alert_{int(time.time())}_{os.urandom(2).hex()}"
    entry = {
        "id": aid,
        "type": alert_type,
        "severity": severity,
        "source": source,
        "message": message,
        "timestamp": datetime.now().isoformat(),
        "unix_ts": time.time(),
        "resolved": False,
        "fix_attempts": 0,
    }
    (ALERTS_DIR / f"{aid}.json").write_text(json.dumps(entry, indent=2, ensure_ascii=False))
    print(f"⚠ ALERT {aid}: [{alert_type}] {message}")
    return aid

def list_unresolved() -> list[dict]:
    """Вернуть все нерешённые алерты."""
    result = []
    for f in sorted(ALERTS_DIR.glob("*.json")):
        try:
            data = json.loads(f.read_text())
            if not data.get("resolved", False):
                result.append(data)
        except Exception:
            pass
    return result

def try_fix(alert_data: dict) -> bool:
    """Попытаться исправить проблему. Вернуть True если получилось."""
    alert_type = alert_data.get("type", "")
    actions = FIX_ACTIONS.get(alert_type, [])
    
    if not actions:
        print(f"  ⚠ Нет fix actions для типа '{alert_type}'")
        return False
    
    for label, cmd, category in actions:
        print(f"  → {label}: {cmd[:60]}...")
        try:
            r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
            if r.returncode == 0 and r.stdout.strip():
                print(f"    ✅ {label} OK")
            else:
                print(f"    ❌ {label} не сработал")
        except subprocess.TimeoutExpired:
            print(f"    ⏱ {label} timeout")
    
    return False  # Даже если что-то получилось — алерт остаётся до проверки

def fix_all():
    """Попытаться исправить все нерешённые алерты."""
    alerts = list_unresolved()
    if not alerts:
        print("✅ Нет нерешённых алертов")
        return {"fixed": 0, "remaining": 0}
    
    print(f"\n⚠ Найдено {len(alerts)} нерешённых алертов:\n")
    fixed = 0
    for a in alerts:
        print(f"  [{a['type']}] {a['message']} ({a['timestamp']})")
        ok = try_fix(a)
        if ok:
            a["resolved"] = True
            a["fixed_at"] = datetime.now().isoformat()
            (ALERTS_DIR / f"{a['id']}.json").write_text(json.dumps(a, indent=2))
            fixed += 1
    
    return {"fixed": fixed, "remaining": len(alerts) - fixed}

if __name__ == "__main__":
    if len(sys.argv) >= 3:
        alert(sys.argv[1], sys.argv[2])
    elif len(sys.argv) == 2 and sys.argv[1] == "--fix":
        result = fix_all()
        print(f"\n✅ Исправлено: {result['fixed']}, осталось: {result['remaining']}")
        sys.exit(0 if result['remaining'] == 0 else 1)
    elif len(sys.argv) == 2 and sys.argv[1] == "--list":
        alerts = list_unresolved()
        for a in alerts:
            print(f"  [{a['severity']}] {a['type']}: {a['message']} ({a['timestamp']})")
        if not alerts:
            print("✅ Нет нерешённых алертов")
    else:
        print("Использование:")
        print("  python scripts/alert_system.py <type> <message>")
        print("  python scripts/alert_system.py --fix")
        print("  python scripts/alert_system.py --list")

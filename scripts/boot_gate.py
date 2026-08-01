#!/usr/bin/env python3
"""Boot gate — запускается ПЕРЕД началом работы.
Принудительно выполняет boot protocol, если он ещё не выполнен в этой сессии.

Использование: python scripts/boot_gate.py [session_id]
"""
import json, os, sys, time
from pathlib import Path

GATE_FILE = Path(__file__).parent.parent / 'cache' / 'boot_gate.json'

def has_booted(session_id: str | None = None) -> bool:
    if not GATE_FILE.exists():
        return False
    try:
        data = json.loads(GATE_FILE.read_text())
        if session_id:
            return data.get('session_id') == session_id
        return data.get('completed', False)
    except:
        return False

def mark_booted(session_id: str = 'unknown'):
    GATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    GATE_FILE.write_text(json.dumps({
        'session_id': session_id,
        'completed': True,
        'time': time.time(),
        'iso': time.strftime('%Y-%m-%dT%H:%M:%S')
    }, indent=2, ensure_ascii=False))

def should_boot(session_id: str | None = None) -> bool:
    """Возвращает True если boot необходим"""
    if not has_booted(session_id):
        return True
    # Если прошло больше 12 часов — перезагрузить
    try:
        data = json.loads(GATE_FILE.read_text())
        elapsed = time.time() - data.get('time', 0)
        if elapsed > 12 * 3600:
            return True
    except:
        return True
    return False

if __name__ == '__main__':
    sid = sys.argv[1] if len(sys.argv) > 1 else os.environ.get('HERMES_SESSION_ID', 'cli')
    
    if should_boot(sid):
        print(f'⚠ Boot required for session {sid}. Run boot protocol first.')
        print('  → python -c "from scripts.boot_gate import mark_booted; mark_booted()"')
        sys.exit(1)
    else:
        print(f'✓ Boot already completed for session {sid}')
        sys.exit(0)

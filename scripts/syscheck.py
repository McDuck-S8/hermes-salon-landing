#!/usr/bin/env python3
"""
Syscheck — System Health Reflex.
Запускается на старте КАЖДОЙ сессии агента.
Не спрашивает разрешения. Не ждёт команды. Просто проверяет.

Usage:
    python scripts/syscheck.py          # verbose check
    python scripts/syscheck.py --quiet   # silent, exit code only

Exit codes:
    0 — system healthy
    1 — system unhealthy (check output for details)
    -1 — critical (KC empty / heartbeat dead)
"""

import sys, os

HERMES_HOME = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(HERMES_HOME, "scripts"))

verbose = "--quiet" not in sys.argv

try:
    from chain_heartbeat import self_check, STATE_FILE
except ImportError as e:
    if verbose:
        print(f"❌ Syscheck FAILED: cannot import chain_heartbeat — {e}")
    sys.exit(1)

result = self_check(verbose=verbose)

if result["is_healthy"]:
    sys.exit(0)
else:
    if result["critical_alerts"]:
        sys.exit(-1)
    sys.exit(1)

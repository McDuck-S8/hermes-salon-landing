"""Hermes health check — JSON health snapshot."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from reality_gate import gate

result = gate()
try:
    from chain_heartbeat import in_view_guard
    for w in in_view_guard(days=7):
        result.setdefault("failed", []).append("in_view")
        result.setdefault("checks", {})["in_view"] = {"status": "WARN", "entries": [w]}
except Exception:
    pass
if "--json" in sys.argv:
    print(json.dumps(result, indent=2, ensure_ascii=False))
else:
    verdict = result.get("verdict", "UNKNOWN")
    failed = result.get("failed", [])
    print(f"Hermes Health: {verdict}")
    for name, check in result.get("checks", {}).items():
        status = check.get("status", "?")
        detail = check.get("entries") or check.get("error") or check.get("listening") or ""
        print(f"  {name:20s} {status:5s} {detail}")
    if failed:
        print(f"\nFailed checks: {', '.join(failed)}")

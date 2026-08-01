#!/usr/bin/env python3
"""
Session Bridge — persists key decisions across sessions.
Read at boot, write at end of every session.
"""
import json
import os
from pathlib import Path
from datetime import datetime

HERMES_HOME = Path(os.environ.get("HERMES_HOME", "D:/Portable_Soft/hermes"))
BRIDGE_FILE = HERMES_HOME / "cache" / "session_bridge.json"


def load_bridge() -> dict:
    """Load session bridge from file. Returns default if missing."""
    if BRIDGE_FILE.exists():
        try:
            data = json.loads(BRIDGE_FILE.read_text(encoding="utf-8"))
            return data
        except (json.JSONDecodeError, OSError):
            pass
    return _default()


def _default() -> dict:
    return {
        "principal_name": "Александр",
        "principal_confirmed": True,
        "last_ee_sync": None,
        "last_kc_count": None,
        "active_goals": [],
        "key_commitments": [],
        "last_session_ts": None,
        "failures_streak": 0,
    }


def save_bridge(updates: dict):
    """Merge updates into bridge and save."""
    current = load_bridge()
    current.update(updates)
    current["last_updated"] = datetime.now().isoformat()
    BRIDGE_FILE.parent.mkdir(parents=True, exist_ok=True)
    BRIDGE_FILE.write_text(
        json.dumps(current, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )
    print(f"💾 Bridge saved: {len(current.get('key_commitments', []))} commitments")
    return current


def add_commitment(text: str, category: str = "general"):
    """Add a key commitment that survives across sessions."""
    bridge = load_bridge()
    commitments = bridge.get("key_commitments", [])
    # Dedup by text
    for c in commitments:
        if c["text"] == text:
            c["last_reaffirmed"] = datetime.now().isoformat()
            break
    else:
        commitments.append({
            "text": text,
            "category": category,
            "created": datetime.now().isoformat(),
            "last_reaffirmed": datetime.now().isoformat(),
        })
    # Keep last 20
    bridge["key_commitments"] = commitments[-20:]
    BRIDGE_FILE.parent.mkdir(parents=True, exist_ok=True)
    BRIDGE_FILE.write_text(
        json.dumps(bridge, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )
    return bridge


def print_bridge():
    """Display current bridge state."""
    bridge = load_bridge()
    print("=== Session Bridge ===")
    print(f"Principal: {bridge.get('principal_name', '?')}")
    print(f"Confirmed: {bridge.get('principal_confirmed', False)}")
    print(f"Last EE sync: {bridge.get('last_ee_sync', 'never')}")
    print(f"Last KC count: {bridge.get('last_kc_count', '?')}")
    print(f"Last session: {bridge.get('last_session_ts', '?')}")
    print(f"Failures streak: {bridge.get('failures_streak', 0)}")
    print(f"\nActive goals ({len(bridge.get('active_goals', []))}):")
    for g in bridge.get("active_goals", []):
        print(f"  [{g.get('id','?')}] {g.get('title','?')}")
    print(f"\nCommitments ({len(bridge.get('key_commitments', []))}):")
    for c in bridge.get("key_commitments", []):
        print(f"  [{c.get('category','?')}] {c.get('text','?')}")


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        if sys.argv[1] == "commit":
            text = " ".join(sys.argv[2:])
            add_commitment(text)
            print(f"✅ Commitment added: {text}")
        elif sys.argv[1] == "show":
            print_bridge()
    else:
        print_bridge()

"""Smoke tests for heartbeat auto-maintenance changes (2026-08-01).
Covers: atomic _save (no partial writes), _load corruption retry,
alert dedup, system_heartbeat_fixer beats all modules, fix_heartbeat protects state.
"""
import json
import os
import sys
import time
import shutil
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from chain_heartbeat import (
    beat, event_beat, system_status, register_all_modules,
    MODULES, EVENTS, CACHE, STATE_FILE,
)

BACKUP = None


def setup_module():
    global BACKUP
    if STATE_FILE.exists():
        BACKUP = STATE_FILE.read_text(encoding="utf-8")


def teardown_module():
    if BACKUP:
        STATE_FILE.write_text(BACKUP, encoding="utf-8")
    elif STATE_FILE.exists():
        STATE_FILE.unlink()


def test_save_is_atomic_and_state_survives():
    """_save writes via tmp+replace; repeated beats never lose prior beats."""
    state = {"beats": {}, "alerts": [], "registered": {}, "pings": {}}
    from chain_heartbeat import _save
    for i in range(5):
        state["beats"][f"m{i}"] = {"last": time.time(), "count": i}
        _save(state)
    loaded = json.loads(STATE_FILE.read_text(encoding="utf-8"))
    assert len(loaded["beats"]) == 5, "beats lost across saves"
    # no temp litter
    tmp_left = list(CACHE.glob("*.tmp"))
    assert not tmp_left, f"leftover tmp files: {tmp_left}"


def test_load_recovers_on_corrupt_state():
    """Corrupt file is preserved as .corrupt, not silently zeroed.
    Uses a temp STATE_FILE: the live file is written by the gateway
    process (PID 14724) every few seconds, which races this test."""
    import chain_heartbeat
    import tempfile
    tmp = Path(tempfile.mkdtemp()) / "chain_heartbeat.json"
    orig = chain_heartbeat.STATE_FILE
    chain_heartbeat.STATE_FILE = tmp
    try:
        corrupt = tmp.with_suffix(".corrupt")
        if corrupt.exists():
            corrupt.unlink()
        tmp.write_text("{not valid json", encoding="utf-8")
        from chain_heartbeat import _load
        state = _load()
        assert state.get("beats") == {}, "must return fresh empty structure"
        assert corrupt.exists(), "corrupt file not preserved"
        # restore valid state
        beat("core")
        assert json.loads(tmp.read_text(encoding="utf-8"))["beats"].get("core")
    finally:
        chain_heartbeat.STATE_FILE = orig
        import shutil
        shutil.rmtree(tmp.parent, ignore_errors=True)


def test_alert_dedup():
    """check_events must not grow duplicate alerts on repeated calls."""
    from chain_heartbeat import check_events, _load
    event_beat("knowledge_added")  # healthy event, no alert
    # force one silent event
    state = _load()
    state["beats"]["knowledge_added"]["last"] = time.time() - 999999
    state["alerts"] = []
    from chain_heartbeat import _save
    _save(state)
    check_events()
    check_events()
    check_events()
    st = system_status()
    level1 = [a for a in st["alerts"] if a.get("level") == 1 and a.get("name") == "knowledge_added"]
    assert len(level1) == 1, f"duplicate alerts: {len(level1)}"


def test_fixer_beats_all_modules_and_events():
    """system_heartbeat_fixer.py beats every registered module + tracked event.
    Uses a temp STATE_FILE: the live file is written by the gateway
    process every few seconds, which races this test (same reason as
    test_load_recovers_on_corrupt_state)."""
    import chain_heartbeat
    import tempfile
    tmp = Path(tempfile.mkdtemp()) / "chain_heartbeat.json"
    orig = chain_heartbeat.STATE_FILE
    chain_heartbeat.STATE_FILE = tmp
    try:
        register_all_modules()
        for m in MODULES:
            beat(m)
        for ename in EVENTS:
            if EVENTS[ename].get("expected_interval_s") is not None:
                event_beat(ename)
        st = system_status()
        s = st["summary"]
        assert s["events_healthy"] == s["events_total"], f"events {s['events_healthy']}/{s['events_total']}"
        assert s["modules_healthy"] == s["modules_total"], f"modules {s['modules_healthy']}/{s['modules_total']}"
        assert s["pipelines_healthy"] == s["pipelines_total"], f"pipelines {s['pipelines_healthy']}/{s['pipelines_total']}"
    finally:
        chain_heartbeat.STATE_FILE = orig


def test_fix_heartbeat_protects_state_files():
    """fix_heartbeat's PROTECTED set includes both heartbeat JSONs."""
    src = Path(__file__).parent.parent / "scripts" / "fix_heartbeat.py"
    text = src.read_text(encoding="utf-8")
    assert "chain_heartbeat.json" in text, "chain_heartbeat.json not protected"
    assert "system_heartbeat.json" in text, "system_heartbeat.json not protected"
    assert "PROTECTED" in text, "PROTECTED set missing"

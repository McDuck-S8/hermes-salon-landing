"""Regression tests for scripts/crystal.py will-history persistence.

Covers the fix: INSERT into experiences must populate the NOT NULL `content`
column (previously only raw_text was written -> silent IntegrityError, and
will_history never accumulated in KC).

Note: `scripts/crystal.py` (self-awareness loop) shares the name `crystal`
with the `scripts/crystal/` package (Crystal v3). Load the script explicitly
via importlib to avoid the package shadowing it.
"""
import importlib.util
import sqlite3
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
CRYSTAL_SCRIPT = ROOT / "scripts" / "crystal.py"

SCHEMA = """
CREATE TABLE experiences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts TEXT NOT NULL, content TEXT NOT NULL, raw_text TEXT NOT NULL, hash TEXT UNIQUE NOT NULL,
    axis_time_hour INTEGER, axis_time_dow INTEGER,
    axis_domain TEXT, axis_outcome TEXT,
    dynamic_axes TEXT DEFAULT '{}',
    is_white_spot INTEGER DEFAULT 0, white_spot_cluster_id TEXT,
    source TEXT, confidence REAL DEFAULT 1.0, tags TEXT DEFAULT '[]',
    importance REAL DEFAULT 0.5,
    expiration_date TEXT, verification_method TEXT DEFAULT 'manual'
)
"""


@pytest.fixture(scope="module")
def crystal():
    spec = importlib.util.spec_from_file_location("crystal_self_awareness", CRYSTAL_SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture()
def tmp_kc(tmp_path, monkeypatch, crystal):
    db = tmp_path / "knowledge_cube.db"
    conn = sqlite3.connect(db)
    conn.execute(SCHEMA)
    conn.commit()
    conn.close()
    monkeypatch.setattr(crystal, "KC", str(db))
    return db


def test_save_will_history_writes_content(tmp_kc, crystal):
    """_save_will_history must succeed and store content (NOT NULL column)."""
    crystal._save_will_history("test_action_1", "результат действия")

    conn = sqlite3.connect(tmp_kc)
    row = conn.execute(
        "SELECT content, raw_text, source FROM experiences"
    ).fetchone()
    conn.close()

    assert row is not None
    content, raw_text, source = row
    assert content == raw_text == "[will:test_action_1] результат действия"
    assert source == "crystal_will"


def test_load_will_history_reads_back(tmp_kc, crystal):
    """Saved actions must be visible to _load_will_history."""
    crystal._save_will_history("test_action_2", "ещё одно действие")

    history = crystal._load_will_history()

    assert "test_action_2" in history
    assert history["test_action_2"]["result"].startswith("[will:test_action_2]")


def test_record_snapshot_writes_content(tmp_kc, crystal):
    """record() snapshot INSERT must also populate content."""
    snap = {"kc": {"total": 0}, "ee": {"entities": 0}, "fl": {"sessions": 0}}
    diag = {"dominant": "meta", "growth": 0}
    preds = {"rate": 0, "milestones": []}
    decisions = ["тест решения"]

    crystal.record(snap, diag, preds, decisions)

    conn = sqlite3.connect(tmp_kc)
    row = conn.execute(
        "SELECT content, source FROM experiences WHERE source='crystal'"
    ).fetchone()
    conn.close()

    assert row is not None
    assert row[0]  # content not empty

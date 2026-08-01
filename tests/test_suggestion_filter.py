"""Regression tests for suggestion_filter (DIRECTIVE 0x50, 2026-08-01).

Uses a temp DB with the experiences schema — never touches the live cube.
"""
import sqlite3
from pathlib import Path

import pytest

sys_path = None  # placeholder to avoid unused import lint noise


@pytest.fixture()
def db(tmp_path: Path):
    conn = sqlite3.connect(tmp_path / "test_cube.db")
    c = conn.cursor()
    c.execute(
        """CREATE TABLE experiences (
            id INTEGER PRIMARY KEY, ts TEXT, content TEXT, raw_text TEXT,
            hash TEXT, axis_domain TEXT, axis_outcome TEXT, tags TEXT,
            source TEXT, is_white_spot INTEGER)"""
    )
    samples = [
        # garbage: log echo
        ("[suggestion:log_unknown] Log pattern 'unknown' seen 22 times: httpx. Error type 'unknown' appeared 22 times in recent logs.",
         "improvement_suggestions"),
        # garbage: Log pattern + N/A fix
        ("Log pattern 'tool_error' appeared 7 times. Latest fix: N/A. Common tags: N/A.",
         "self_improvement_loop"),
        # structural: domain failure analysis
        ("[suggestion:domain_failure_pattern] High failure rate in domain 'creative' (57%). Domain 'creative' has a 57.0% failure rate.",
         "improvement_suggestions"),
        # structural: recurring fix with real fix
        ("Self-improvement pattern: 'log_unknown' appeared 8 times. Latest fix: Added guard clause. Common tags: network.",
         "self_improvement_loop"),
    ]
    for i, (text, source) in enumerate(samples, 1):
        c.execute(
            "INSERT INTO experiences (ts, content, raw_text, hash, axis_domain, axis_outcome, tags, source, is_white_spot) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0)",
            ("2026-08-01T00:00:00", text, text, f"h{i}", "test", "meta", "[]", source),
        )
    conn.commit()
    return conn


def _load_filter(monkeypatch, tmp_path, db_path):
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "suggestion_filter", "scripts/suggestion_filter.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    monkeypatch.setattr(mod, "CUBE_DB", db_path)
    return mod


def test_classify_split(db):
    from scripts.suggestion_filter import is_log_copy

    rows = db.execute("SELECT raw_text FROM experiences").fetchall()
    classified = [is_log_copy(r[0]) for r in rows]
    assert classified == [True, True, False, False]


def test_archive_moves_garbage_only(db, monkeypatch, tmp_path):
    mod = _load_filter(monkeypatch, tmp_path, tmp_path / "test_cube.db")
    mod.CUBE_DB = tmp_path / "test_cube.db"
    # exec_module binds CUBE_DB at import; override after load
    st = mod.classify(db)
    assert len(st["garbage"]) == 2
    moved = mod.archive(db, st["garbage"], dry=False)
    assert moved == 2
    left = db.execute("SELECT COUNT(*) FROM experiences").fetchone()[0]
    assert left == 2  # structural kept
    arch = db.execute("SELECT COUNT(*) FROM experiences_log_archive").fetchone()[0]
    assert arch == 2
    # archive is reversible: rows still have original ids
    ids = db.execute("SELECT id FROM experiences_log_archive ORDER BY id").fetchall()
    assert [i[0] for i in ids] == [1, 2]


def test_dry_run_writes_nothing(db, monkeypatch, tmp_path):
    mod = _load_filter(monkeypatch, tmp_path, tmp_path / "test_cube.db")
    st = mod.classify(db)
    moved = mod.archive(db, st["garbage"], dry=True)
    assert moved == 2
    assert db.execute("SELECT COUNT(*) FROM experiences").fetchone()[0] == 4
    tables = [r[0] for r in db.execute(
        "SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
    assert "experiences_log_archive" not in tables


def test_self_improvement_loop_no_log_clusters_write():
    """The log_clusters INSERT block must be gone from self_improvement_loop."""
    src = Path("scripts/self_improvement_loop.py").read_text(encoding="utf-8")
    assert "Write knowledge from strong log patterns" not in src
    assert "[suggestion:{cluster['error_type']}]" not in src
    assert "reads improvement_suggestions.json" in src

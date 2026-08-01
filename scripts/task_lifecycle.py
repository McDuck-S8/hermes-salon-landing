#!/usr/bin/env python3
"""
Task Lifecycle -- lifecycle of tasks in Knowledge Cube.


> Revisit: when task lifecycle logic, task states, or task transitions change. Last touched: 2026-07-02.
IDEA -> START -> DONE / FAIL / STALL

Three pillars:
  IDEA  = white (void)
  START = normal (known)
  DONE  = normal (known)
  FAIL  = red (anomaly)
  STALL = red (anomaly)
"""

import json, os, sqlite3
from pathlib import Path
from datetime import datetime, timedelta

HERMES_HOME = Path(os.environ.get("HERMES_HOME", os.path.expanduser("~/.hermes")))
DB_PATH = HERMES_HOME / "cache" / "knowledge_cube.db"


def _get_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT DEFAULT "",
            status TEXT DEFAULT "idea",
            pillar TEXT DEFAULT "white",
            created_at TEXT NOT NULL,
            started_at TEXT,
            completed_at TEXT,
            outcome TEXT,
            notes TEXT DEFAULT "",
            tags TEXT DEFAULT "[]"
        );
        CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
        CREATE INDEX IF NOT EXISTS idx_tasks_pillar ON tasks(pillar);
    """)
    return conn


class TaskTracker:

    def idea(self, title, description="", tags=None):
        with _get_db() as conn:
            existing = conn.execute(
                "SELECT id, status FROM tasks WHERE title = ?", (title,)
            ).fetchone()
            if existing:
                return {"status": "exists", "id": existing[0],
                        "current_status": existing[1],
                        "message": "Already exists: {}".format(existing[1])}
            now = datetime.now().isoformat()
            cur = conn.execute(
                'INSERT INTO tasks (title,description,status,pillar,created_at,tags) VALUES (?,"","idea","white",?,?)',
                (title, now, json.dumps(tags or [])))
            return {"status": "created", "id": cur.lastrowid, "pillar": "white",
                    "message": "IDEA: {}".format(title)}

    def start(self, title):
        with _get_db() as conn:
            task = conn.execute("SELECT id, status FROM tasks WHERE title = ?", (title,)).fetchone()
            if not task:
                self.idea(title)
                task = conn.execute("SELECT id, status FROM tasks WHERE title = ?", (title,)).fetchone()
            now = datetime.now().isoformat()
            conn.execute('UPDATE tasks SET status="started", pillar="normal", started_at=? WHERE id=?',
                         (now, task[0]))
            return {"status": "started", "id": task[0], "pillar": "normal",
                    "message": "STARTED: {}".format(title)}

    def done(self, title, notes=""):
        with _get_db() as conn:
            task = conn.execute("SELECT id FROM tasks WHERE title = ?", (title,)).fetchone()
            if not task:
                return {"status": "not_found"}
            now = datetime.now().isoformat()
            conn.execute(
                'UPDATE tasks SET status="done", pillar="normal", completed_at=?, outcome="success", notes=? WHERE id=?',
                (now, notes, task[0]))
            return {"status": "completed", "id": task[0], "pillar": "normal",
                    "message": "DONE: {}".format(title)}

    def fail(self, title, reason=""):
        with _get_db() as conn:
            task = conn.execute("SELECT id FROM tasks WHERE title = ?", (title,)).fetchone()
            if not task:
                return {"status": "not_found"}
            now = datetime.now().isoformat()
            conn.execute(
                'UPDATE tasks SET status="failed", pillar="red", completed_at=?, outcome="failure", notes=? WHERE id=?',
                (now, reason, task[0]))
            return {"status": "failed", "id": task[0], "pillar": "red",
                    "message": "FAIL: {} -- {}".format(title, reason)}

    def stall(self, title, reason="stalled"):
        with _get_db() as conn:
            task = conn.execute("SELECT id FROM tasks WHERE title = ?", (title,)).fetchone()
            if not task:
                return {"status": "not_found"}
            conn.execute('UPDATE tasks SET status="stalled", pillar="red", notes=? WHERE id=?',
                         (reason, task[0]))
            return {"status": "stalled", "id": task[0], "pillar": "red",
                    "message": "STALL: {} -- {}".format(title, reason)}

    def open_tasks(self):
        with _get_db() as conn:
            rows = conn.execute(
                'SELECT id, title, description, status, pillar, created_at, started_at, notes '
                'FROM tasks WHERE status IN ("idea","started") '
                'ORDER BY CASE status WHEN "started" THEN 0 WHEN "idea" THEN 1 END, created_at DESC'
            ).fetchall()
        return [{"id": r[0], "title": r[1], "description": r[2], "status": r[3],
                 "pillar": r[4], "created_at": r[5], "started_at": r[6], "notes": r[7]} for r in rows]

    def stalled_tasks(self, days=3):
        cutoff = (datetime.now() - timedelta(days=days)).isoformat()
        with _get_db() as conn:
            rows = conn.execute(
                'SELECT id, title, status, pillar, started_at, notes '
                'FROM tasks WHERE status="started" AND started_at < ? ORDER BY started_at ASC',
                (cutoff,)).fetchall()
        return [{"id": r[0], "title": r[1], "status": r[2], "pillar": r[3],
                 "started_at": r[4], "notes": r[5]} for r in rows]

    def stats(self):
        with _get_db() as conn:
            total = conn.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]
            by_status = conn.execute("SELECT status, COUNT(*) FROM tasks GROUP BY status").fetchall()
            by_pillar = conn.execute("SELECT pillar, COUNT(*) FROM tasks GROUP BY pillar").fetchall()
        return {"total": total,
                "by_status": {r[0]: r[1] for r in by_status},
                "by_pillar": {r[0]: r[1] for r in by_pillar}}

    def import_from_cube(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location("kc", str(Path(__file__).parent / "knowledge_cube.py"))
        kc = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(kc)
        ws = kc.get_white_spots(100)
        imported = 0
        for w in ws:
            result = self.idea(w["raw_text"][:100])
            if result["status"] == "created":
                imported += 1
        return {"imported": imported, "total": len(ws),
                "message": "Imported {} white spots as ideas".format(imported)}

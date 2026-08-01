"""SQLite registry — schema management and CRUD operations for skills."""

import sqlite3
import time
from pathlib import Path
from typing import Any


SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS skills (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    category TEXT,
    version TEXT,
    description TEXT DEFAULT '',
    path TEXT NOT NULL,
    body TEXT DEFAULT '',
    installed_at TEXT,
    updated_at TEXT,
    status TEXT DEFAULT 'active'
);

CREATE TABLE IF NOT EXISTS quality_checks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    skill_id INTEGER NOT NULL,
    check_name TEXT NOT NULL,
    passed INTEGER NOT NULL DEFAULT 0,
    details TEXT DEFAULT '',
    checked_at TEXT NOT NULL,
    FOREIGN KEY (skill_id) REFERENCES skills(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS versions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    skill_id INTEGER NOT NULL,
    version TEXT NOT NULL,
    changelog TEXT DEFAULT '',
    published_at TEXT NOT NULL,
    FOREIGN KEY (skill_id) REFERENCES skills(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS dependencies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    skill_id INTEGER NOT NULL,
    depends_on_name TEXT NOT NULL,
    type TEXT DEFAULT 'reference',
    FOREIGN KEY (skill_id) REFERENCES skills(id) ON DELETE CASCADE
);

CREATE VIRTUAL TABLE IF NOT EXISTS skills_fts USING fts5(
    name,
    category,
    description,
    body,
    content='skills',
    content_rowid='id'
);

-- Triggers to keep FTS in sync
CREATE TRIGGER IF NOT EXISTS skills_ai AFTER INSERT ON skills BEGIN
    INSERT INTO skills_fts(rowid, name, category, description, body)
    VALUES (new.id, new.name, new.category, new.description, new.body);
END;

CREATE TRIGGER IF NOT EXISTS skills_ad AFTER DELETE ON skills BEGIN
    INSERT INTO skills_fts(skills_fts, rowid, name, category, description, body)
    VALUES ('delete', old.id, old.name, old.category, old.description, old.body);
END;

CREATE TRIGGER IF NOT EXISTS skills_au AFTER UPDATE ON skills BEGIN
    INSERT INTO skills_fts(skills_fts, rowid, name, category, description, body)
    VALUES ('delete', old.id, old.name, old.category, old.description, old.body);
    INSERT INTO skills_fts(rowid, name, category, description, body)
    VALUES (new.id, new.name, new.category, new.description, new.body);
END;

CREATE INDEX IF NOT EXISTS idx_quality_checks_skill
    ON quality_checks(skill_id, check_name);

CREATE INDEX IF NOT EXISTS idx_versions_skill
    ON versions(skill_id);

CREATE INDEX IF NOT EXISTS idx_dependencies_skill
    ON dependencies(skill_id);
"""


class Registry:
    """SQLite-backed skill registry with FTS5 search."""

    def __init__(self, db_path: str | Path):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self):
        """Create schema if not exists. Enables WAL for concurrent access."""
        with self._conn() as conn:
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA foreign_keys=ON")
            conn.executescript(SCHEMA_SQL)

    def _conn(self) -> sqlite3.Connection:
        """Get a new connection with foreign keys and WAL enforced."""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def _now(self) -> str:
        return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    # ── Skills CRUD ────────────────────────────────────────────

    def add_skill(
        self,
        name: str,
        category: str | None,
        version: str | None,
        path: str,
        body: str = "",
        description: str = "",
    ) -> int:
        """Add a skill. Returns skill_id. Raises on duplicate name."""
        now = self._now()
        with self._conn() as conn:
            cur = conn.execute(
                """INSERT INTO skills (name, category, version, description, path, body, installed_at, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (name, category, version, description, path, body, now, now),
            )
            skill_id = cur.lastrowid
            # Record initial version
            if version:
                conn.execute(
                    "INSERT INTO versions (skill_id, version, published_at) VALUES (?, ?, ?)",
                    (skill_id, version, now),
                )
            return skill_id

    def upsert_skill(
        self,
        name: str,
        category: str | None,
        version: str | None,
        path: str,
        body: str = "",
        description: str = "",
    ) -> int:
        """Add or update a skill by name. Returns skill_id."""
        now = self._now()
        with self._conn() as conn:
            existing = conn.execute(
                "SELECT id, version FROM skills WHERE name = ?", (name,)
            ).fetchone()
            if existing:
                conn.execute(
                    """UPDATE skills SET category=?, version=?, description=?, path=?, body=?, updated_at=?
                       WHERE id=?""",
                    (category, version, description, path, body, now, existing["id"]),
                )
                # Record version if changed
                if version and version != existing["version"]:
                    conn.execute(
                        "INSERT INTO versions (skill_id, version, published_at) VALUES (?, ?, ?)",
                        (existing["id"], version, now),
                    )
                return existing["id"]
            else:
                return self.add_skill(name, category, version, path, body, description)

    def get_skill(self, name: str) -> dict | None:
        """Get skill by name."""
        with self._conn() as conn:
            row = conn.execute("SELECT * FROM skills WHERE name = ?", (name,)).fetchone()
            return dict(row) if row else None

    def get_skill_by_id(self, skill_id: int) -> dict | None:
        """Get skill by ID."""
        with self._conn() as conn:
            row = conn.execute(
                "SELECT * FROM skills WHERE id = ?", (skill_id,)
            ).fetchone()
            return dict(row) if row else None

    def list_skills(
        self, category: str | None = None, status: str | None = None
    ) -> list[dict[str, Any]]:
        """List skills, optionally filtered."""
        query = "SELECT * FROM skills WHERE 1=1"
        params: list[Any] = []
        if category:
            query += " AND category = ?"
            params.append(category)
        if status:
            query += " AND status = ?"
            params.append(status)
        query += " ORDER BY name"
        with self._conn() as conn:
            rows = conn.execute(query, params).fetchall()
            return [dict(r) for r in rows]

    def update_skill_status(self, name: str, status: str) -> bool:
        """Update skill status (active/deprecated/broken)."""
        with self._conn() as conn:
            cur = conn.execute(
                "UPDATE skills SET status = ?, updated_at = ? WHERE name = ?",
                (status, self._now(), name),
            )
            return cur.rowcount > 0

    def delete_skill(self, name: str) -> bool:
        """Delete a skill (cascades to checks, versions, deps, FTS)."""
        with self._conn() as conn:
            cur = conn.execute("DELETE FROM skills WHERE name = ?", (name,))
            return cur.rowcount > 0

    def skill_count(self) -> int:
        """Total number of registered skills."""
        with self._conn() as conn:
            return conn.execute("SELECT COUNT(*) FROM skills").fetchone()[0]

    def prune_stale(self) -> int:
        """Remove skills whose files no longer exist on disk.

        Returns count of pruned skills.
        """
        with self._conn() as conn:
            rows = conn.execute("SELECT id, name, path FROM skills").fetchall()
            pruned = 0
            for row in rows:
                if not Path(row["path"]).exists():
                    conn.execute("DELETE FROM skills WHERE id = ?", (row["id"],))
                    pruned += 1
            return pruned

    def export_json(self) -> str:
        """Export entire registry as JSON string."""
        import json
        with self._conn() as conn:
            skills = [dict(r) for r in conn.execute(
                "SELECT * FROM skills ORDER BY name"
            ).fetchall()]
            for s in skills:
                s["quality_checks"] = [
                    dict(r) for r in conn.execute(
                        "SELECT * FROM quality_checks WHERE skill_id = ? ORDER BY check_name, checked_at DESC",
                        (s["id"],)
                    ).fetchall()
                ]
        return json.dumps(skills, indent=2, default=str)

    # ── Quality Checks ─────────────────────────────────────────

    def record_quality_check(
        self, skill_id: int, check_name: str, passed: bool, details: str = ""
    ) -> int:
        """Record a quality gate result."""
        now = self._now()
        with self._conn() as conn:
            cur = conn.execute(
                """INSERT INTO quality_checks (skill_id, check_name, passed, details, checked_at)
                   VALUES (?, ?, ?, ?, ?)""",
                (skill_id, check_name, int(passed), details, now),
            )
            return cur.lastrowid

    def get_latest_checks(self, skill_id: int) -> list[dict[str, Any]]:
        """Get most recent quality check for each check_name."""
        with self._conn() as conn:
            rows = conn.execute(
                """SELECT qc.* FROM quality_checks qc
                   WHERE qc.skill_id = ?
                     AND qc.id = (
                       SELECT MAX(id) FROM quality_checks
                       WHERE skill_id = qc.skill_id AND check_name = qc.check_name
                     )
                   ORDER BY qc.check_name""",
                (skill_id,),
            ).fetchall()
            return [dict(r) for r in rows]

    def get_failed_checks(self) -> list[dict[str, Any]]:
        """Get all skills that have failing quality checks."""
        with self._conn() as conn:
            rows = conn.execute(
                """SELECT DISTINCT s.name, qc.check_name, qc.details
                   FROM quality_checks qc
                   JOIN skills s ON s.id = qc.skill_id
                   WHERE qc.passed = 0
                     AND qc.id = (
                       SELECT MAX(id) FROM quality_checks
                       WHERE skill_id = qc.skill_id AND check_name = qc.check_name
                     )
                   ORDER BY s.name, qc.check_name"""
            ).fetchall()
            return [dict(r) for r in rows]

    # ── FTS5 Search ────────────────────────────────────────────

    def search(self, query: str, limit: int = 20) -> list[dict[str, Any]]:
        """Full-text search across skills."""
        with self._conn() as conn:
            try:
                rows = conn.execute(
                    """SELECT s.* FROM skills s
                       JOIN skills_fts fts ON s.id = fts.rowid
                       WHERE skills_fts MATCH ?
                       ORDER BY rank
                       LIMIT ?""",
                    (query, limit),
                ).fetchall()
            except sqlite3.OperationalError:
                # Invalid FTS query — fall back to LIKE search
                like = f"%{query}%"
                rows = conn.execute(
                    """SELECT * FROM skills
                       WHERE name LIKE ? OR description LIKE ? OR body LIKE ?
                       ORDER BY name LIMIT ?""",
                    (like, like, like, limit),
                ).fetchall()
            return [dict(r) for r in rows]

    # ── Health / Stats ─────────────────────────────────────────

    def get_stats(self) -> dict[str, Any]:
        """Registry health overview."""
        with self._conn() as conn:
            total = conn.execute("SELECT COUNT(*) FROM skills").fetchone()[0]
            by_status = {}
            for row in conn.execute(
                "SELECT status, COUNT(*) as cnt FROM skills GROUP BY status"
            ).fetchall():
                by_status[row["status"]] = row["cnt"]
            by_category = {}
            for row in conn.execute(
                "SELECT category, COUNT(*) as cnt FROM skills GROUP BY category ORDER BY cnt DESC"
            ).fetchall():
                cat = row["category"] or "(uncategorized)"
                by_category[cat] = row["cnt"]
            total_checks = conn.execute(
                "SELECT COUNT(*) FROM quality_checks"
            ).fetchone()[0]
            failed = len(self.get_failed_checks())

        return {
            "total_skills": total,
            "by_status": by_status,
            "by_category": by_category,
            "total_quality_checks": total_checks,
            "skills_with_failures": failed,
            "db_path": str(self.db_path),
        }

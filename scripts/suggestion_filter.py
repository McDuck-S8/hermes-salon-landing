#!/usr/bin/env python3
"""suggestion_filter — gate between improvement_suggestions and Knowledge Cube.

Classifies experiences rows as LOG_COPY (garbage: raw log-pattern echoes)
vs STRUCTURAL (value: domain failure analysis, knowledge gaps, commands).

LOG_COPY heuristic (source='improvement_suggestions'/'self_improvement_loop'):
  - raw_text starts with '[suggestion:log_'
  - OR contains 'Log pattern' AND 'Latest fix: N/A' (echo without a fix)
Everything else with those sources is structural.

Existing rows are NOT deleted — moved to `experiences_log_archive` table
(reversible). Future writes are blocked at the source (self_improvement_loop).

Usage:
  python scripts/suggestion_filter.py          # classify + archive, print stats
  python scripts/suggestion_filter.py --dry    # stats only, no write
"""
import json
import sqlite3
import sys
from pathlib import Path

CUBE_DB = Path(__file__).resolve().parent.parent / "cache" / "knowledge_cube.db"
ARCHIVE_TABLE = "experiences_log_archive"
SOURCES = ("improvement_suggestions", "self_improvement_loop")


def is_log_copy(raw_text: str) -> bool:
    if not raw_text:
        return False
    t = raw_text.strip()
    if t.startswith("[suggestion:log_"):
        return True
    if "Log pattern" in t and "Latest fix: N/A" in t:
        return True
    return False


def classify(conn) -> dict:
    c = conn.cursor()
    q = "SELECT id, raw_text FROM experiences WHERE source IN (?, ?)"
    c.execute(q, SOURCES)
    rows = c.fetchall()
    garbage, keep = [], []
    for rid, raw in rows:
        (garbage if is_log_copy(raw) else keep).append(rid)
    return {"total": len(rows), "garbage": garbage, "keep": keep}


def archive(conn, garbage_ids, dry: bool) -> int:
    if not garbage_ids:
        return 0
    if dry:
        return len(garbage_ids)
    c = conn.cursor()
    c.execute(
        f"CREATE TABLE IF NOT EXISTS {ARCHIVE_TABLE} AS SELECT * FROM experiences WHERE 0"
    )
    placeholders = ",".join("?" * len(garbage_ids))
    c.execute(
        f"INSERT INTO {ARCHIVE_TABLE} SELECT * FROM experiences WHERE id IN ({placeholders})",
        garbage_ids,
    )
    c.execute(
        f"DELETE FROM experiences WHERE id IN ({placeholders})", garbage_ids
    )
    conn.commit()
    return len(garbage_ids)


def main():
    dry = "--dry" in sys.argv
    conn = sqlite3.connect(CUBE_DB)
    try:
        st = classify(conn)
        moved = archive(conn, st["garbage"], dry)
        # post-state
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM experiences")
        total = c.fetchone()[0]
        c.execute(
            "SELECT COUNT(*) FROM experiences WHERE source IN (?, ?)", SOURCES
        )
        remaining = c.fetchone()[0]
        c.execute(
            "SELECT COUNT(*) FROM experiences WHERE source IN (?, ?) AND axis_domain NOT IN ('_suggestion_log')",
            SOURCES,
        )
        structural = c.fetchone()[0]
    finally:
        conn.close()

    mode = "DRY-RUN" if dry else "APPLIED"
    print(f"[{mode}] suggestion_filter on knowledge_cube.db")
    print(f"  total rows in scope:        {st['total']}")
    print(f"  LOG_COPY (garbage):         {len(st['garbage'])}")
    print(f"  STRUCTURAL (kept):          {len(st['keep'])}")
    print(f"  archived to {ARCHIVE_TABLE}: {moved}")
    print(f"  Cube total after:           {total}")
    print(f"  remaining from sources:     {remaining}")
    print(f"  structural remaining:       {structural}")


if __name__ == "__main__":
    main()

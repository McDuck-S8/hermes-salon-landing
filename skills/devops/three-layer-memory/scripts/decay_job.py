#!/usr/bin/env python3
"""
Decay Job — Periodic decay of old, unused memories.

Runs daily via cron. Archives or deletes memories below salience threshold.
"""

import os
import sys
import sqlite3
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any

# ─── config ─────────────────────────────────────────────────────────
HERMES_HOME = Path(os.environ.get("HERMES_HOME", "D:/Portable_Soft/hermes"))
KC_DB = HERMES_HOME / "cache" / "knowledge_cube.db"

# Decay config
SALIENCE_HALFLIFE_DAYS = 30
SALIENCE_MIN_THRESHOLD = 0.05
ARCHIVE_BEFORE_DELETE = True  # Archive to JSON before deleting
ARCHIVE_DIR = HERMES_HOME / "cache" / "memory_archive"


class DecayJob:
    """Periodic memory decay and archival."""

    def __init__(self):
        ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
        self._ensure_archive_table()

    def _ensure_archive_table(self):
        """Create archive table for soft-deleted memories."""
        try:
            conn = sqlite3.connect(KC_DB)
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS memory_archive (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    original_id INTEGER NOT NULL,
                    text TEXT NOT NULL,
                    domain TEXT,
                    created_at TEXT,
                    archived_at TEXT DEFAULT (datetime('now')),
                    final_salience REAL,
                    retrieval_count INTEGER,
                    importance REAL,
                    archive_reason TEXT
                )
            """)
            conn.commit()
            conn.close()
            print("[DECAY] memory_archive table ready")
        except Exception as e:
            print(f"[DECAY] Archive table creation failed: {e}")

    def compute_effective_salience(self, memory_id: int) -> float:
        """Compute effective salience with recency decay."""
        try:
            conn = sqlite3.connect(KC_DB)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute("""
                SELECT ms.salience, ms.retrieval_count, ms.importance, ms.last_used_at,
                       kc.created_at
                FROM memory_salience ms
                JOIN knowledge_cube kc ON ms.memory_id = kc.id
                WHERE ms.memory_id = ?
            """, [memory_id])

            row = cursor.fetchone()
            conn.close()

            if not row:
                return 0.0

            salience = row["salience"] or 0.0
            retrieval_count = row["retrieval_count"] or 0
            importance = row["importance"] or 0.5
            last_used_at = row["last_used_at"]

            # Recency boost
            recency_boost = 1.0
            if last_used_at:
                try:
                    last_used = datetime.fromisoformat(last_used_at.replace("Z", "").split("+")[0])
                    days_old = (datetime.now() - last_used).days
                    recency_boost = 0.5 ** (days_old / SALIENCE_HALFLIFE_DAYS)
                except:
                    pass

            effective = (salience + retrieval_count * 0.1 + importance * 0.5) * recency_boost
            return max(SALIENCE_MIN_THRESHOLD, effective)

        except Exception as e:
            print(f"[DECAY] Salience compute failed for {memory_id}: {e}")
            return 0.0

    def find_candidates_for_decay(self, limit: int = 1000) -> List[Dict[str, Any]]:
        """Find memories below salience threshold."""
        try:
            conn = sqlite3.connect(KC_DB)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute("""
                SELECT ms.memory_id, ms.salience, ms.retrieval_count, ms.last_used_at, ms.importance,
                       kc.text, kc.domain, kc.created_at
                FROM memory_salience ms
                JOIN knowledge_cube kc ON ms.memory_id = kc.id
                WHERE ms.retrieval_count = 0
                ORDER BY ms.salience ASC
                LIMIT ?
            """, [limit])

            rows = cursor.fetchall()
            conn.close()

            candidates = []
            for row in rows:
                effective = self.compute_effective_salience(row["memory_id"])
                if effective < SALIENCE_MIN_THRESHOLD:
                    candidates.append({
                        "memory_id": row["memory_id"],
                        "text": row["text"],
                        "domain": row["domain"],
                        "created_at": row["created_at"],
                        "base_salience": row["salience"],
                        "retrieval_count": row["retrieval_count"],
                        "importance": row["importance"],
                        "effective_salience": effective,
                    })

            return candidates

        except Exception as e:
            print(f"[DECAY] Find candidates failed: {e}")
            return []

    def archive_memory(self, memory: Dict[str, Any], reason: str = "decay") -> bool:
        """Archive memory to archive table and JSON file."""
        try:
            # 1. Insert into archive table
            conn = sqlite3.connect(KC_DB)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO memory_archive
                (original_id, text, domain, created_at, final_salience, retrieval_count, importance, archive_reason)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, [
                memory["memory_id"],
                memory["text"],
                memory["domain"],
                memory["created_at"],
                memory["effective_salience"],
                memory["retrieval_count"],
                memory["importance"],
                reason
            ])
            conn.commit()
            conn.close()

            # 2. Write JSON archive file
            archive_file = ARCHIVE_DIR / f"memory_{memory['memory_id']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            archive_file.write_text(json.dumps(memory, indent=2, default=str), encoding="utf-8")

            return True

        except Exception as e:
            print(f"[DECAY] Archive failed for {memory['memory_id']}: {e}")
            return False

    def delete_memory(self, memory_id: int) -> bool:
        """Hard delete from knowledge_cube and memory_salience."""
        try:
            conn = sqlite3.connect(KC_DB)
            cursor = conn.cursor()

            # Delete from FTS5 (requires rebuild or delete from base table)
            cursor.execute("DELETE FROM knowledge_cube WHERE id = ?", [memory_id])
            cursor.execute("DELETE FROM memory_salience WHERE memory_id = ?", [memory_id])

            conn.commit()
            conn.close()

            print(f"[DECAY] Deleted memory_id={memory_id}")
            return True

        except Exception as e:
            print(f"[DECAY] Delete failed for {memory_id}: {e}")
            return False

    def run_decay(self, dry_run: bool = False, max_delete: int = 100) -> Dict[str, Any]:
        """Run decay job."""
        print(f"[DECAY] Starting decay job (dry_run={dry_run})...")

        candidates = self.find_candidates_for_decay()
        print(f"[DECAY] Found {len(candidates)} candidates below threshold")

        results = {
            "candidates_found": len(candidates),
            "archived": 0,
            "deleted": 0,
            "errors": 0,
            "dry_run": dry_run
        }

        for i, memory in enumerate(candidates[:max_delete]):
            if dry_run:
                print(f"[DECAY] DRY RUN: Would archive memory_id={memory['memory_id']} (salience={memory['effective_salience']:.4f})")
                results["archived"] += 1
                continue

            # Archive first
            if ARCHIVE_BEFORE_DELETE:
                if self.archive_memory(memory):
                    results["archived"] += 1
                else:
                    results["errors"] += 1
                    continue

            # Then delete
            if self.delete_memory(memory["memory_id"]):
                results["deleted"] += 1
            else:
                results["errors"] += 1

            if i % 10 == 0:
                print(f"[DECAY] Progress: {i+1}/{min(len(candidates), max_delete)}")

        print(f"[DECAY] Complete: {results}")
        return results

    def rebuild_fts5(self) -> bool:
        """Rebuild FTS5 index after deletions."""
        try:
            conn = sqlite3.connect(KC_DB)
            cursor = conn.cursor()
            # FTS5 contentless table - rebuild by reinserting
            cursor.execute("INSERT INTO knowledge_cube_fts(knowledge_cube_fts) VALUES('rebuild')")
            conn.commit()
            conn.close()
            print("[DECAY] FTS5 rebuilt")
            return True
        except Exception as e:
            print(f"[DECAY] FTS5 rebuild failed: {e}")
            return False


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Memory Decay Job")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done without doing it")
    parser.add_argument("--max-delete", type=int, default=100, help="Max memories to process per run")
    parser.add_argument("--rebuild-fts", action="store_true", help="Rebuild FTS5 index after decay")

    args = parser.parse_args()

    job = DecayJob()
    results = job.run_decay(dry_run=args.dry_run, max_delete=args.max_delete)

    if args.rebuild_fts and not args.dry_run:
        job.rebuild_fts5()

    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
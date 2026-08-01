#!/usr/bin/env python3
"""
Salience Scorer — Computes and updates salience scores for memories.

Salience = base_importance + retrieval_boost + recency_boost
Updated on every retrieval and via relevance feedback.
"""

import os
import sys
import sqlite3
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

# ─── config ─────────────────────────────────────────────────────────
HERMES_HOME = Path(os.environ.get("HERMES_HOME", "D:/Portable_Soft/hermes"))
KC_DB = HERMES_HOME / "cache" / "knowledge_cube.db"

# Salience config
SALIENCE_HALFLIFE_DAYS = 30
RETRIEVAL_BOOST = 0.1
IMPORTANCE_WEIGHT = 0.5
MIN_SALIENCE = 0.0
MAX_SALIENCE = 10.0

# Kill switch
KC_SALIENCE_ENABLED = os.environ.get("KC_SALIENCE_ENABLED", "true").lower() == "true"


class SalienceScorer:
    """Manages salience scores for Knowledge Cube memories."""

    def __init__(self):
        if not KC_SALIENCE_ENABLED:
            return
        self._ensure_salience_table()

    def _ensure_salience_table(self):
        """Create memory_salience table if not exists."""
        try:
            conn = sqlite3.connect(KC_DB)
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS memory_salience (
                    memory_id INTEGER PRIMARY KEY,
                    salience REAL DEFAULT 0.0,
                    retrieval_count INTEGER DEFAULT 0,
                    importance REAL DEFAULT 0.5,
                    last_used_at TEXT,
                    created_at TEXT DEFAULT (datetime('now')),
                    updated_at TEXT DEFAULT (datetime('now')),
                    FOREIGN KEY (memory_id) REFERENCES knowledge_cube(id) ON DELETE CASCADE
                )
            """)
            # Index for decay job
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_memory_salience_salience
                ON memory_salience(salience)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_memory_salience_retrieval
                ON memory_salience(retrieval_count)
            """)
            conn.commit()
            conn.close()
            print("[SALIENCE] memory_salience table ready")
        except Exception as e:
            print(f"[SALIENCE] Table creation failed: {e}")

    def get_salience(self, memory_id: int) -> Dict[str, Any]:
        """Get current salience data for a memory."""
        try:
            conn = sqlite3.connect(KC_DB)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM memory_salience WHERE memory_id = ?
            """, [memory_id])
            row = cursor.fetchone()
            conn.close()

            if row:
                return dict(row)
            return {"memory_id": memory_id, "salience": 0.0, "retrieval_count": 0,
                    "importance": 0.5, "last_used_at": None}
        except Exception as e:
            print(f"[SALIENCE] Get failed for {memory_id}: {e}")
            return {"memory_id": memory_id, "salience": 0.0, "retrieval_count": 0,
                    "importance": 0.5, "last_used_at": None}

    def initialize_memory_id: int, was_used: bool) -> None:
        """Update salience when a memory is retrieved (used or not used)."""
        if not KC_SALIENCE_ENABLED:
            return

        try:
            conn = sqlite3.connect(KC_DB)
            cursor = conn.cursor()

            # Get current state
            cursor.execute("""
                SELECT salience, retrieval_count, importance
                FROM memory_salience WHERE memory_id = ?
            """, [memory_id])
            row = cursor.fetchone()

            now = datetime.now().isoformat()

            if row:
                salience, retrieval_count, importance = row
                salience = salience or 0.0
                retrieval_count = retrieval_count or 0
                importance = importance or 0.5

                if was_used:
                    retrieval_count += 1
                    salience = min(MAX_SALIENCE, salience + RETRIEVAL_BOOST)

                # Update last_used_at if used
                if was_used:
                    cursor.execute("""
                        UPDATE memory_salience
                        SET salience = ?, retrieval_count = ?, last_used_at = ?, updated_at = ?
                        WHERE memory_id = ?
                    """, [salience, retrieval_count, now, now, memory_id])
                else:
                    # Small decay for unused retrieval
                    salience = max(MIN_SALIENCE, salience - 0.01)
                    cursor.execute("""
                        UPDATE memory_salience
                        SET salience = ?, updated_at = ?
                        WHERE memory_id = ?
                    """, [salience, now, memory_id])
            else:
                # First retrieval
                retrieval_count = 1 if was_used else 0
                salience = RETRIEVAL_BOOST if was_used else 0.0
                cursor.execute("""
                    INSERT INTO memory_salience
                    (memory_id, salience, retrieval_count, importance, last_used_at, created_at, updated_at)
                    VALUES (?, ?, ?, 0.5, ?, datetime('now'), datetime('now'))
                """, [memory_id, salience, retrieval_count, now if was_used else None])

            conn.commit()
            conn.close()

        except Exception as e:
            print(f"[SALIENCE] Update on retrieval failed for {memory_id}: {e}")

    def update_importance(self, memory_id: int, importance: float) -> None:
        """Manually set importance (user pinning)."""
        if not KC_SALIENCE_ENABLED:
            return

        try:
            importance = max(0.0, min(1.0, importance))
            conn = sqlite3.connect(KC_DB)
            cursor = conn.cursor()
            now = datetime.now().isoformat()

            cursor.execute("""
                INSERT INTO memory_salience (memory_id, importance, updated_at)
                VALUES (?, ?, ?)
                ON CONFLICT(memory_id) DO UPDATE SET
                    importance = excluded.importance,
                    updated_at = excluded.updated_at
            """, [memory_id, importance, now])

            conn.commit()
            conn.close()
            print(f"[SALIENCE] Importance set for {memory_id}: {importance}")

        except Exception as e:
            print(f"[SALIENCE] Importance update failed for {memory_id}: {e}")

    def apply_feedback(self, memory_id: int, was_used: bool) -> None:
        """Apply relevance feedback (stronger signal than retrieval)."""
        if not KC_SALIENCE_ENABLED:
            return

        try:
            conn = sqlite3.connect(KC_DB)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT salience, retrieval_count, importance
                FROM memory_salience WHERE memory_id = ?
            """, [memory_id])
            row = cursor.fetchone()

            if row:
                salience, retrieval_count, importance = row
                salience = salience or 0.0
                importance = importance or 0.5

                if was_used:
                    # Strong positive signal
                    salience = min(MAX_SALIENCE, salience + 1.0)
                else:
                    # Negative signal (retrieved but not used)
                    salience = max(MIN_SALIENCE, salience - 0.2)

                now = datetime.now().isoformat()
                cursor.execute("""
                    UPDATE memory_salience
                    SET salience = ?, updated_at = ?
                    WHERE memory_id = ?
                """, [salience, now, memory_id])
            else:
                # First feedback
                salience = 1.0 if was_used else 0.0
                now = datetime.now().isoformat()
                cursor.execute("""
                    INSERT INTO memory_salience
                    (memory_id, salience, retrieval_count, importance, updated_at)
                    VALUES (?, ?, 0, 0.5, ?)
                """, [memory_id, salience, now])

            conn.commit()
            conn.close()
            print(f"[SALIENCE] Feedback applied for {memory_id}: {'used' if was_used else 'unused'} -> {salience:.2f}")

        except Exception as e:
            print(f"[SALIENCE] Feedback failed for {memory_id}: {e}")

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

            effective = (salience + retrieval_count * RETRIEVAL_BOOST + importance * IMPORTANCE_WEIGHT) * recency_boost
            return max(MIN_SALIENCE, min(MAX_SALIENCE, effective))

        except Exception as e:
            print(f"[SALIENCE] Effective salience compute failed for {memory_id}: {e}")
            return 0.0

    def get_all_salience(self, limit: int = 1000) -> list:
        """Get all salience records for analysis."""
        try:
            conn = sqlite3.connect(KC_DB)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT ms.*, kc.text, kc.domain
                FROM memory_salience ms
                LEFT JOIN knowledge_cube kc ON ms.memory_id = kc.id
                ORDER BY ms.salience DESC
                LIMIT ?
            """, [limit])
            rows = cursor.fetchall()
            conn.close()
            return [dict(row) for row in rows]
        except Exception as e:
            print(f"[SALIENCE] Get all failed: {e}")
            return []


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Salience Scorer for Knowledge Cube")
    parser.add_argument("--memory-id", type=int, help="Memory ID to query/update")
    parser.add_argument("--importance", type=float, help="Set importance (0-1)")
    parser.add_argument("--feedback", choices=["used", "unused"], help="Apply feedback")
    parser.add_argument("--retrieval", choices=["used", "unused"], help="Update on retrieval")
    parser.add_argument("--list", action="store_true", help="List top salience entries")
    parser.add_argument("--limit", type=int, default=20, help="List limit")

    args = parser.parse_args()

    if not KC_SALIENCE_ENABLED:
        print("Salience disabled: KC_SALIENCE_ENABLED=false")
        sys.exit(1)

    scorer = SalienceScorer()

    if args.memory_id:
        if args.importance is not None:
            scorer.update_importance(args.memory_id, args.importance)
        elif args.feedback:
            scorer.apply_feedback(args.memory_id, args.feedback == "used")
        elif args.retrieval:
            scorer.update_on_retrieval(args.memory_id, args.retrieval == "used")
        else:
            # Query
            data = scorer.get_salience(args.memory_id)
            effective = scorer.compute_effective_salience(args.memory_id)
            print(json.dumps({"base": data, "effective_salience": effective}, indent=2))

    elif args.list:
        all_salience = scorer.get_all_salience(args.limit)
        for s in all_salience:
            eff = scorer.compute_effective_salience(s["memory_id"])
            text_preview = s.get("text", "")[:60] if s.get("text") else "N/A"
            print(f"  {s['memory_id']:6d} | salience={s['salience']:.2f} eff={eff:.2f} | ret={s['retrieval_count']} imp={s['importance']:.1f} | {text_preview}...")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
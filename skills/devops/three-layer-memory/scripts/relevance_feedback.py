#!/usr/bin/env python3
"""
Relevance Feedback — Post-response learning loop.

After agent responds, asks LLM which memories were actually used.
Updates salience scores accordingly.
"""

import os
import sys
import json
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional

# ─── config ─────────────────────────────────────────────────────────
HERMES_HOME = Path(os.environ.get("HERMES_HOME", "D:/Portable_Soft/hermes"))
KC_DB = HERMES_HOME / "cache" / "knowledge_cube.db"

# Kill switch
KC_FEEDBACK_ENABLED = os.environ.get("KC_FEEDBACK_ENABLED", "true").lower() == "true"

# Feedback config
FEEDBACK_MODEL = os.environ.get("KC_FEEDBACK_MODEL", "gemini-flash")  # cheap model
USED_BOOST = 0.5
UNUSED_PENALTY = 0.1


class RelevanceFeedback:
    """Handles post-response relevance feedback loop."""

    def __init__(self):
        self._ensure_feedback_table()

    def _ensure_feedback_table(self):
        """Create feedback log table."""
        try:
            conn = sqlite3.connect(KC_DB)
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS memory_feedback (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    memory_id INTEGER NOT NULL,
                    session_id TEXT NOT NULL,
                    query_text TEXT NOT NULL,
                    agent_response TEXT NOT NULL,
                    was_used BOOLEAN NOT NULL,
                    confidence REAL,
                    feedback_model TEXT,
                    created_at TEXT DEFAULT (datetime('now')),
                    FOREIGN KEY (memory_id) REFERENCES knowledge_cube(id)
                )
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_feedback_memory
                ON memory_feedback(memory_id)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_feedback_session
                ON memory_feedback(session_id)
            """)
            conn.commit()
            conn.close()
            print("[FEEDBACK] memory_feedback table ready")
        except Exception as e:
            print(f"[FEEDBACK] Table creation failed: {e}")

    def analyze_response(self, session_id: str, query: str, agent_response: str,
                         retrieved_memories: List[Dict[str, Any]]) -> Dict[str, bool]:
        """
        Ask LLM which retrieved memories were actually used in the response.
        Returns dict: {memory_id: was_used}
        """
        if not KC_FEEDBACK_ENABLED:
            return {m["memory_id"]: True for m in retrieved_memories}

        if not retrieved_memories:
            return {}

        # Build prompt for LLM
        memories_text = "\n".join([
            f"[{m['memory_id']}] {m['text'][:200]}..."
            for m in retrieved_memories
        ])

        prompt = f"""The user asked: "{query}"

The agent responded:
{agent_response[:1000]}

The following memories were retrieved and injected into the agent's context:
{memories_text}

Which of these memories did the agent ACTUALLY USE in its response?
Respond with ONLY a JSON array of memory_ids that were used.
Example: [123, 456]

If none were used, respond: []"""

        try:
            # Use cheap model for classification
            # For now, return heuristic - in production, call LLM API
            used_ids = self._heuristic_analysis(agent_response, retrieved_memories)
            return {m["memory_id"]: m["memory_id"] in used_ids for m in retrieved_memories}

        except Exception as e:
            print(f"[FEEDBACK] Analysis failed: {e}")
            # Default: assume all used
            return {m["memory_id"]: True for m in retrieved_memories}

    def _heuristic_analysis(self, response: str, memories: List[Dict[str, Any]]) -> List[int]:
        """Heuristic: check if response contains key terms from memories."""
        used = []
        response_lower = response.lower()

        for m in memories:
            # Extract key terms from memory text
            text = m.get("text", "").lower()
            # Simple heuristic: if any 3+ word phrase from memory appears in response
            words = text.split()
            if len(words) >= 3:
                # Check 3-grams
                for i in range(len(words) - 2):
                    phrase = " ".join(words[i:i+3])
                    if len(phrase) > 10 and phrase in response_lower:
                        used.append(m["memory_id"])
                        break

        return used

    def record_feedback(self, session_id: str, query: str, agent_response: str,
                        retrieved_memories: List[Dict[str, Any]],
                        used_results: Dict[str, bool]) -> None:
        """Record feedback to database."""
        try:
            conn = sqlite3.connect(KC_DB)
            cursor = conn.cursor()

            for m in retrieved_memories:
                mid = m["memory_id"]
                used = used_results.get(mid, True)
                cursor.execute("""
                    INSERT INTO memory_feedback
                    (memory_id, session_id, query_text, agent_response, was_used, confidence, feedback_model)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, [mid, session_id, query, agent_response[:500], used, 0.8, FEEDBACK_MODEL])

            conn.commit()
            conn.close()
            print(f"[FEEDBACK] Recorded feedback for {len(retrieved_memories)} memories")

        except Exception as e:
            print(f"[FEEDBACK] Record failed: {e}")

    def apply_salience_updates(self, used_results: Dict[str, bool]) -> None:
        """Apply salience updates based on feedback."""
        try:
            from salience_scorer import SalienceScorer
            scorer = SalienceScorer()

            for memory_id, was_used in used_results.items():
                scorer.update_on_retrieval(int(memory_id), was_used)

            print(f"[FEEDBACK] Applied salience updates for {len(used_results)} memories")

        except Exception as e:
            print(f"[FEEDBACK] Salience update failed: {e}")

    def process_turn(self, session_id: str, query: str, agent_response: str,
                     retrieved_memories: List[Dict[str, Any]]) -> Dict[str, bool]:
        """Full feedback loop for one conversation turn."""
        # 1. Analyze which memories were used
        used_results = self.analyze_response(session_id, query, agent_response, retrieved_memories)

        # 2. Record feedback
        self.record_feedback(session_id, query, agent_response, retrieved_memories, used_results)

        # 3. Update salience
        self.apply_salience_updates(used_results)

        return used_results

    def get_feedback_stats(self, days: int = 30) -> Dict[str, Any]:
        """Get feedback statistics."""
        try:
            conn = sqlite3.connect(KC_DB)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            since = (datetime.now() - timedelta(days=days)).isoformat()

            cursor.execute("""
                SELECT
                    COUNT(*) as total_feedback,
                    SUM(CASE WHEN was_used = 1 THEN 1 ELSE 0 END) as used_count,
                    AVG(confidence) as avg_confidence
                FROM memory_feedback
                WHERE created_at > ?
            """, [since])

            row = cursor.fetchone()
            conn.close()

            if row and row["total_feedback"] > 0:
                return {
                    "total_feedback": row["total_feedback"],
                    "used_count": row["used_count"],
                    "unused_count": row["total_feedback"] - row["used_count"],
                    "usage_rate": row["used_count"] / row["total_feedback"],
                    "avg_confidence": row["avg_confidence"],
                    "period_days": days
                }
            return {"total_feedback": 0}

        except Exception as e:
            print(f"[FEEDBACK] Stats failed: {e}")
            return {}


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Relevance Feedback for Knowledge Cube")
    parser.add_argument("--session-id", help="Session ID")
    parser.add_argument("--query", help="User query")
    parser.add_argument("--response", help="Agent response")
    parser.add_argument("--memories", help="JSON file with retrieved memories")
    parser.add_argument("--stats", action="store_true", help="Show feedback stats")
    parser.add_argument("--days", type=int, default=30, help="Stats period in days")

    args = parser.parse_args()

    if not KC_FEEDBACK_ENABLED:
        print("Feedback disabled: KC_FEEDBACK_ENABLED=false")
        sys.exit(1)

    fb = RelevanceFeedback()

    if args.stats:
        stats = fb.get_feedback_stats(args.days)
        print(json.dumps(stats, indent=2))
        return

    if not args.session_id or not args.query or not args.response:
        print("Error: --session-id, --query, --response required")
        sys.exit(1)

    memories = []
    if args.memories:
        with open(args.memories, "r") as f:
            memories = json.load(f)

    used = fb.process_turn(args.session_id, args.query, args.response, memories)
    print(f"Feedback processed. Used: {sum(1 for v in used.values() if v)}/{len(used)}")


if __name__ == "__main__":
    main()
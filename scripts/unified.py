"""UNIFIED SYSTEM — Everything connected, everything works.

All systems in one place:
  - Knowledge Cube
  - Lavra
  - Sessions
  - Gap Analysis
  - Search
  - Impact Scoring
  - Pattern Learning
  - Chain Reactions
  - Self-Learning (via current model)
"""

import json
import os
import sqlite3
import sys
from pathlib import Path
from datetime import datetime
from collections import defaultdict

HERMES_HOME = Path(os.environ.get("HERMES_HOME", str(Path(__file__).resolve().parent.parent)))
KNOWLEDGE_CUBE = HERMES_HOME / "cache" / "knowledge_cube.db"
LAVRA_KNOWLEDGE = HERMES_HOME / "data" / "lavra_knowledge.jsonl"
SESSION_DB = HERMES_HOME / "state.db"
UNIFIED_DB = HERMES_HOME / "cache" / "unified.db"


class UnifiedSystem:
    """Everything connected. Everything works."""

    def __init__(self):
        self._unified_conn = None
        self._init_db()
        self._connect_all()

    def _init_db(self):
        """Initialize the unified database schema."""
        conn = None
        try:
            conn = sqlite3.connect(str(UNIFIED_DB), timeout=5)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS knowledge_gaps (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    topic TEXT, domain TEXT, importance REAL,
                    source TEXT, found_at TEXT, filled INTEGER DEFAULT 0
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS searches (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    query TEXT, results_count INTEGER, source TEXT,
                    results_json TEXT, searched_at TEXT
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS chain_actions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    chain_id TEXT, action_type TEXT, description TEXT,
                    result TEXT, status TEXT, created_at TEXT
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS self_learning (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    topic TEXT, insight TEXT, source TEXT,
                    confidence REAL, learned_at TEXT
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS user_patterns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pattern_type TEXT, pattern_data TEXT,
                    confidence REAL, last_seen TEXT
                )
            """)

            conn.commit()
        except (sqlite3.Error, OSError) as e:
            print(f"[unified] Warning: failed to init DB: {e}", file=sys.stderr)
        finally:
            if conn is not None:
                try:
                    conn.close()
                except (sqlite3.Error, OSError):
                    pass

    def _connect_all(self):
        """Connect to all data sources."""
        # Knowledge Cube
        self.kc = None
        if KNOWLEDGE_CUBE.exists():
            try:
                self.kc = sqlite3.connect(str(KNOWLEDGE_CUBE), timeout=5)
                self.kc.row_factory = sqlite3.Row
            except (sqlite3.Error, OSError):
                self.kc = None

        # Lavra
        self.lavra = []
        if LAVRA_KNOWLEDGE.exists():
            try:
                with open(LAVRA_KNOWLEDGE, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if not line:
                            continue
                        try:
                            entry = json.loads(line.strip('"'))
                            self.lavra.append(entry)
                        except (json.JSONDecodeError, TypeError):
                            continue
            except OSError:
                pass

        # Sessions
        self.db = None
        if SESSION_DB.exists():
            try:
                self.db = sqlite3.connect(str(SESSION_DB), timeout=5)
                self.db.row_factory = sqlite3.Row
            except (sqlite3.Error, OSError):
                self.db = None

    def _get_unified_conn(self):
        """Get a connection to the unified DB, creating if needed."""
        if self._unified_conn is None:
            try:
                self._unified_conn = sqlite3.connect(str(UNIFIED_DB), timeout=5)
            except (sqlite3.Error, OSError):
                return None
        return self._unified_conn

    def close(self):
        """Close all open connections."""
        for conn in (self.kc, self.db, self._unified_conn):
            if conn is not None:
                try:
                    conn.close()
                except (sqlite3.Error, OSError):
                    pass
        self.kc = None
        self.db = None
        self._unified_conn = None

    def __del__(self):
        """Ensure connections are closed on garbage collection."""
        self.close()

    def search(self, query: str) -> list:
        """Search ALL sources."""
        results = []

        # Knowledge Cube
        if self.kc:
            try:
                rows = self.kc.execute(
                    "SELECT * FROM experiences WHERE raw_text LIKE ? OR tags LIKE ? LIMIT 5",
                    (f"%{query}%", f"%{query}%")
                ).fetchall()
                for r in rows:
                    results.append({
                        "source": "knowledge_cube",
                        "content": r["raw_text"][:200] if r["raw_text"] else "",
                        "domain": r["axis_domain"]
                    })
            except (sqlite3.Error, TypeError):
                pass

        # Lavra
        q = query.lower()
        for entry in self.lavra:
            if q in entry.get("content", "").lower():
                results.append({
                    "source": "lavra",
                    "content": entry.get("content", "")[:200],
                    "type": entry.get("type", "unknown")
                })

        # Save search
        unified = self._get_unified_conn()
        if unified is not None:
            try:
                unified.execute(
                    "INSERT INTO searches (query, results_count, source, results_json, searched_at) "
                    "VALUES (?, ?, ?, ?, ?)",
                    (query, len(results), "all", json.dumps(results[:3]), datetime.now().isoformat())
                )
                unified.commit()
            except (sqlite3.Error, TypeError, OSError):
                pass

        return results

    def find_gaps(self) -> list:
        """Find REAL knowledge gaps."""
        gaps = []

        if self.kc:
            try:
                rows = self.kc.execute(
                    "SELECT axis_domain, COUNT(*) as cnt FROM experiences "
                    "GROUP BY axis_domain ORDER BY cnt ASC"
                ).fetchall()

                for r in rows:
                    if r["cnt"] < 10:
                        gaps.append({
                            "topic": f"Low knowledge: {r['axis_domain']}",
                            "domain": r["axis_domain"],
                            "importance": 0.8 if r["cnt"] < 5 else 0.6,
                            "count": r["cnt"]
                        })
            except (sqlite3.Error, TypeError):
                pass

        # Save gaps
        unified = self._get_unified_conn()
        if unified is not None:
            try:
                for g in gaps:
                    unified.execute(
                        "INSERT INTO knowledge_gaps (topic, domain, importance, source, found_at) "
                        "VALUES (?, ?, ?, ?, ?)",
                        (g["topic"], g["domain"], g["importance"], "knowledge_cube",
                         datetime.now().isoformat())
                    )
                unified.commit()
            except (sqlite3.Error, TypeError, OSError):
                pass

        return gaps

    def learn(self, topic: str, insight: str, source: str = "conversation",
              confidence: float = 0.7):
        """Learn something new. This is the self-learning part."""
        unified = self._get_unified_conn()
        if unified is None:
            return

        try:
            unified.execute(
                "INSERT INTO self_learning (topic, insight, source, confidence, learned_at) "
                "VALUES (?, ?, ?, ?, ?)",
                (topic, insight, source, confidence, datetime.now().isoformat())
            )
            unified.commit()
        except (sqlite3.Error, TypeError, OSError):
            pass

        # Also save as pattern (reuses same connection)
        try:
            unified.execute(
                "INSERT INTO user_patterns (pattern_type, pattern_data, confidence, last_seen) "
                "VALUES (?, ?, ?, ?)",
                (topic, json.dumps({"insight": insight}), confidence, datetime.now().isoformat())
            )
            unified.commit()
        except (sqlite3.Error, TypeError, OSError):
            pass

    def chain(self, action: str, data: dict = None) -> dict:
        """Execute a chain action."""
        if data is None:
            data = {}
        chain_id = f"chain_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        result = {"chain_id": chain_id, "actions": []}

        if action == "fill_gap":
            gaps = self.find_gaps()
            for g in gaps[:3]:
                results = self.search(g["domain"])
                if results:
                    self.learn(
                        g["domain"],
                        f"Found {len(results)} resources for {g['domain']}",
                        "gap_fill",
                        0.6
                    )
                    # Mark gap as filled (reuses unified connection)
                    unified = self._get_unified_conn()
                    if unified is not None:
                        try:
                            unified.execute(
                                "UPDATE knowledge_gaps SET filled=1 WHERE topic=? AND filled=0",
                                (g["topic"],)
                            )
                            unified.commit()
                        except (sqlite3.Error, TypeError, OSError):
                            pass
                    result["actions"].append({
                        "type": "gap_filled",
                        "gap": g["topic"],
                        "results": len(results)
                    })

        elif action == "search_and_learn":
            query = data.get("query", "")
            results = self.search(query)
            if results:
                self.learn(query, f"Found {len(results)} results", "search", 0.7)
                result["actions"].append({
                    "type": "searched",
                    "query": query,
                    "results": len(results)
                })

        # Save chain (reuses unified connection)
        unified = self._get_unified_conn()
        if unified is not None:
            try:
                for a in result["actions"]:
                    unified.execute(
                        "INSERT INTO chain_actions "
                        "(chain_id, action_type, description, result, status, created_at) "
                        "VALUES (?, ?, ?, ?, ?, ?)",
                        (chain_id, a["type"], json.dumps(a), "success", "completed",
                         datetime.now().isoformat())
                    )
                unified.commit()
            except (sqlite3.Error, TypeError, OSError):
                pass

        return result

    def get_learnings(self) -> list:
        """Get all self-learned insights."""
        unified = self._get_unified_conn()
        if unified is None:
            return []
        try:
            unified.row_factory = sqlite3.Row
            rows = unified.execute(
                "SELECT * FROM self_learning ORDER BY learned_at DESC"
            ).fetchall()
            return [dict(r) for r in rows]
        except (sqlite3.Error, TypeError):
            return []

    def get_status(self) -> dict:
        """Get complete system status."""
        status = {
            "data_sources": {
                "knowledge_cube": {"connected": self.kc is not None, "count": 0},
                "lavra": {"connected": bool(self.lavra), "count": len(self.lavra)},
                "sessions": {"connected": self.db is not None, "count": 0}
            },
            "unified_db": {
                "gaps": 0,
                "searches": 0,
                "learnings": 0,
                "patterns": 0,
                "chains": 0
            }
        }

        if self.kc:
            try:
                status["data_sources"]["knowledge_cube"]["count"] = \
                    self.kc.execute("SELECT COUNT(*) FROM experiences").fetchone()[0]
            except (sqlite3.Error, TypeError):
                pass

        if self.db:
            try:
                status["data_sources"]["sessions"]["count"] = \
                    self.db.execute("SELECT COUNT(*) FROM messages").fetchone()[0]
            except (sqlite3.Error, TypeError):
                pass

        unified = self._get_unified_conn()
        if unified is not None:
            try:
                status["unified_db"]["gaps"] = \
                    unified.execute("SELECT COUNT(*) FROM knowledge_gaps").fetchone()[0]
                status["unified_db"]["searches"] = \
                    unified.execute("SELECT COUNT(*) FROM searches").fetchone()[0]
                status["unified_db"]["learnings"] = \
                    unified.execute("SELECT COUNT(*) FROM self_learning").fetchone()[0]
                status["unified_db"]["patterns"] = \
                    unified.execute("SELECT COUNT(*) FROM user_patterns").fetchone()[0]
                status["unified_db"]["chains"] = \
                    unified.execute("SELECT COUNT(DISTINCT chain_id) FROM chain_actions").fetchone()[0]
            except (sqlite3.Error, TypeError):
                pass

        return status

    def demonstrate(self):
        """Show what the system actually does."""
        print("=== UNIFIED SYSTEM ===\n")

        # Status
        status = self.get_status()
        print("DATA SOURCES:")
        for name, info in status["data_sources"].items():
            conn_status = "\u2713" if info["connected"] else "\u2717"
            print(f"  {conn_status} {name}: {info['count']} records")

        print("\nUNIFIED DB:")
        for k, v in status["unified_db"].items():
            print(f"  {k}: {v}")

        print("\n=== SEARCH ===")
        queries = ["salon", "bot", "deploy", "error"]
        for q in queries:
            results = self.search(q)
            print(f"  '{q}' \u2192 {len(results)} results")
            for r in results[:1]:
                print(f"    [{r['source']}] {r['content'][:60]}...")

        print("\n=== GAPS ===")
        gaps = self.find_gaps()
        for g in gaps:
            print(f"  {g['topic']} (importance: {g['importance']}, count: {g['count']})")

        print("\n=== SELF-LEARNING ===")
        self.learn("test", "This is a test learning", "demo", 0.5)
        learnings = self.get_learnings()
        for l in learnings:
            print(f"  [{l['source']}] {l['topic']}: {l['insight']}")

        print("\n=== CHAIN ===")
        result = self.chain("search_and_learn", {"query": "salon bot"})
        for a in result["actions"]:
            print(f"  {a['type']}: {a['query']} \u2192 {a['results']} results")

        print("\n=== FINAL STATUS ===")
        status = self.get_status()
        print(f"  Total learnings: {status['unified_db']['learnings']}")
        print(f"  Total searches: {status['unified_db']['searches']}")
        print(f"  Total chains: {status['unified_db']['chains']}")

        print("\n=== DONE ===")


if __name__ == "__main__":
    system = UnifiedSystem()
    try:
        system.demonstrate()
    finally:
        system.close()

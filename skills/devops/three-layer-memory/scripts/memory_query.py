#!/usr/bin/env python3
"""
Memory Query — Unified query across all three memory layers.

Combines: FTS5 (keyword) + LanceDB (semantic) + Salience (usage-based)
Returns ranked, deduplicated results.
"""

import os
import sys
import sqlite3
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

# ─── config ─────────────────────────────────────────────────────────
HERMES_HOME = Path(os.environ.get("HERMES_HOME", "D:/Portable_Soft/hermes"))
KC_DB = HERMES_HOME / "cache" / "knowledge_cube.db"

# Kill switches
KC_TIER3_ENABLED = os.environ.get("KC_TIER3_ENABLED", "true").lower() == "true"
KC_LANCE_ENABLED = os.environ.get("KC_LANCE_ENABLED", "true").lower() == "true"
KC_SALIENCE_ENABLED = os.environ.get("KC_SALIENCE_ENABLED", "true").lower() == "true"

# Query weights
WEIGHT_FTS5 = 0.4
WEIGHT_VECTOR = 0.4
WEIGHT_SALIENCE = 0.2

# Salience config
SALIENCE_HALFLIFE_DAYS = 30
SALIENCE_MIN_THRESHOLD = 0.05


class MemoryQuery:
    """Unified query across FTS5, Vector, and Salience layers."""

    def __init__(self):
        self.embedding_gen = None
        if KC_TIER3_ENABLED and KC_LANCE_ENABLED:
            try:
                sys.path.insert(0, str(HERMES_HOME / "skills" / "devops" / "three-layer-memory" / "scripts"))
                from embedding_generator import EmbeddingGenerator
                self.embedding_gen = EmbeddingGenerator()
            except Exception as e:
                print(f"[MEMORY_QUERY] Embedding generator unavailable: {e}")

    def query_fts5(self, query: str, limit: int = 20, domain: str = None) -> List[Dict[str, Any]]:
            """Layer 1: FTS5 keyword search (joined with experiences table)."""
            try:
                conn = sqlite3.connect(KC_DB)
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()

                # Build FTS5 query
                fts_query = " ".join([f'"{term}"' for term in query.split() if len(term) > 2])
                if not fts_query:
                    fts_query = query

                sql = """
                    SELECT e.id, e.content as text, e.axis_domain as domain, e.ts as created_at, e.importance,
                           bm25(knowledge_cube_fts) as rank
                    FROM knowledge_cube_fts
                    JOIN experiences e ON knowledge_cube_fts.rowid = e.id
                    WHERE knowledge_cube_fts MATCH ?
                """
                params = [fts_query]

                if domain:
                    sql += " AND e.axis_domain = ?"
                    params.append(domain)

                sql += " ORDER BY rank LIMIT ?"
                params.append(limit)

                cursor.execute(sql, params)
                rows = cursor.fetchall()
                conn.close()

                results = []
                for row in rows:
                    # Normalize BM25 score (lower is better) to 0-1 similarity
                    # BM25 typically 0-10+, so we invert and cap
                    bm25_score = row["rank"] if row["rank"] else 10.0
                    similarity = max(0.0, 1.0 - (bm25_score / 10.0))

                    results.append({
                        "memory_id": row["id"],
                        "text": row["text"],
                        "domain": row["domain"],
                        "created_at": row["created_at"],
                        "importance": row["importance"] or 0.5,
                        "layer": "fts5",
                        "score": similarity,
                    })

                return results

            except Exception as e:
                print(f"[MEMORY_QUERY] FTS5 query failed: {e}")
                return []

    def query_vector(self, query: str, limit: int = 20, domain: str = None) -> List[Dict[str, Any]]:
        """Layer 2: Vector similarity search via LanceDB."""
        if not self.embedding_gen:
            return []

        try:
            results = self.embedding_gen.search_similar(query, limit, domain)
            # Convert cosine distance to similarity (1 - distance)
            for r in results:
                r["similarity"] = max(0.0, 1.0 - r["score"])
                r["score"] = r["similarity"]
                r["layer"] = "vector"
            return results
        except Exception as e:
            print(f"[MEMORY_QUERY] Vector query failed: {e}")
            return []

    def get_salience_boost(self, memory_ids: List[int]) -> Dict[int, float]:
        """Layer 3: Get salience boost for memory IDs."""
        if not KC_SALIENCE_ENABLED:
            return {mid: 1.0 for mid in memory_ids}

        try:
            conn = sqlite3.connect(KC_DB)
            cursor = conn.cursor()

            # Check if salience table exists
            cursor.execute("""
                SELECT name FROM sqlite_master
                WHERE type='table' AND name='memory_salience'
            """)
            if not cursor.fetchone():
                conn.close()
                return {mid: 1.0 for mid in memory_ids}

            # Get salience data
            placeholders = ",".join(["?"] * len(memory_ids))
            cursor.execute(f"""
                SELECT memory_id, salience, retrieval_count, last_used_at, importance
                FROM memory_salience
                WHERE memory_id IN ({placeholders})
            """, memory_ids)

            rows = cursor.fetchall()
            conn.close()

            boosts = {}
            now = datetime.now()

            for row in rows:
                mid, salience, retrieval_count, last_used_at, importance = row
                base_salience = salience or 0.0
                importance = importance or 0.5

                # Recency boost
                recency_boost = 1.0
                if last_used_at:
                    try:
                        last_used = datetime.fromisoformat(last_used_at.replace("Z", ""))
                        days_old = (now - last_used).days
                        recency_boost = 0.5 ** (days_old / SALIENCE_HALFLIFE_DAYS)
                    except:
                        pass

                # Combined boost: base + usage + importance + recency
                boost = (
                    base_salience +
                    (retrieval_count or 0) * 0.1 +
                    importance * 0.5
                ) * recency_boost

                boosts[mid] = max(0.1, min(3.0, boost))  # clamp 0.1-3.0

            # Default for missing entries
            for mid in memory_ids:
                if mid not in boosts:
                    boosts[mid] = 1.0

            return boosts

        except Exception as e:
            print(f"[MEMORY_QUERY] Salience query failed: {e}")
            return {mid: 1.0 for mid in memory_ids}

    def merge_results(self, fts5_results: List[Dict], vector_results: List[Dict],
                      salience_boosts: Dict[int, float], limit: int = 10) -> List[Dict]:
        """Merge and rank results from all three layers."""

        # Combine by memory_id
        combined = {}

        # Add FTS5 results
        for r in fts5_results:
            mid = r["memory_id"]
            combined[mid] = {
                "memory_id": mid,
                "text": r["text"],
                "domain": r["domain"],
                "created_at": r["created_at"],
                "importance": r["importance"],
                "fts5_score": r["score"],
                "vector_score": 0.0,
            }

        # Add/merge vector results
        for r in vector_results:
            mid = r["memory_id"]
            if mid in combined:
                combined[mid]["vector_score"] = r["score"]
            else:
                combined[mid] = {
                    "memory_id": mid,
                    "text": r["text"],
                    "domain": r["domain"],
                    "created_at": r["created_at"],
                    "importance": r.get("importance", 0.5),
                    "fts5_score": 0.0,
                    "vector_score": r["score"],
                }

        # Apply salience boost and compute final score
        final_results = []
        for mid, data in combined.items():
            salience_boost = salience_boosts.get(mid, 1.0)

            weighted_score = (
                WEIGHT_FTS5 * data["fts5_score"] +
                WEIGHT_VECTOR * data["vector_score"] +
                WEIGHT_SALIENCE * min(1.0, salience_boost / 3.0)  # normalize boost
            )

            data["salience_boost"] = salience_boost
            data["final_score"] = weighted_score
            final_results.append(data)

        # Sort by final score descending
        final_results.sort(key=lambda x: x["final_score"], reverse=True)

        return final_results[:limit]

    def query(self, query: str, limit: int = 10, domain: str = None) -> Dict[str, Any]:
        """Main query method - runs all three layers and merges."""

        print(f"[MEMORY_QUERY] Query: '{query}' (limit={limit}, domain={domain})")

        # Run all three layers in parallel (sequential for now)
        fts5_results = self.query_fts5(query, limit * 2, domain)
        print(f"[MEMORY_QUERY] FTS5: {len(fts5_results)} results")

        vector_results = self.query_vector(query, limit * 2, domain)
        print(f"[MEMORY_QUERY] Vector: {len(vector_results)} results")

        # Get all unique memory_ids for salience lookup
        all_ids = set()
        for r in fts5_results:
            all_ids.add(r["memory_id"])
        for r in vector_results:
            all_ids.add(r["memory_id"])

        salience_boosts = self.get_salience_boost(list(all_ids))

        # Merge and rank
        merged = self.merge_results(fts5_results, vector_results, salience_boosts, limit)
        print(f"[MEMORY_QUERY] Merged: {len(merged)} final results")

        return {
            "query": query,
            "limit": limit,
            "domain": domain,
            "results": merged,
            "layer_counts": {
                "fts5": len(fts5_results),
                "vector": len(vector_results),
                "merged": len(merged)
            }
        }


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Three-Layer Memory Query")
    parser.add_argument("query", help="Search query")
    parser.add_argument("--limit", type=int, default=10, help="Result limit")
    parser.add_argument("--domain", help="Domain filter")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    if not KC_TIER3_ENABLED:
        print("Tier 3 memory disabled: KC_TIER3_ENABLED=false")
        # Fallback to FTS5 only
        import sqlite3
        conn = sqlite3.connect(KC_DB)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        fts_query = " ".join([f'"{term}"' for term in args.query.split() if len(term) > 2])
        cursor.execute("""
            SELECT id, text, domain, created_at, importance
            FROM knowledge_cube_fts
            WHERE knowledge_cube_fts MATCH ?
            ORDER BY bm25(knowledge_cube_fts) LIMIT ?
        """, [fts_query, args.limit])
        rows = cursor.fetchall()
        conn.close()

        results = [{"memory_id": r["id"], "text": r["text"], "domain": r["domain"],
                   "created_at": r["created_at"], "score": 1.0} for r in rows]

        if args.json:
            print(json.dumps({"results": results}, indent=2))
        else:
            for r in results:
                print(f"  [{r['memory_id']}] {r['domain']}: {r['text'][:80]}...")
        return

    mq = MemoryQuery()
    result = mq.query(args.query, args.limit, args.domain)

    if args.json:
        print(json.dumps(result, indent=2, default=str))
    else:
        print(f"\nQuery: {result['query']}")
        print(f"Layers: FTS5={result['layer_counts']['fts5']}, Vector={result['layer_counts']['vector']}, Merged={result['layer_counts']['merged']}\n")
        for i, r in enumerate(result["results"]):
            print(f"  {i+1}. [{r['final_score']:.3f}] (FTS5:{r['fts5_score']:.3f} Vec:{r['vector_score']:.3f} Sal:{r['salience_boost']:.2f})")
            print(f"     memory_id={r['memory_id']} domain={r['domain']}")
            print(f"     {r['text'][:120]}...")
            print()


if __name__ == "__main__":
    main()
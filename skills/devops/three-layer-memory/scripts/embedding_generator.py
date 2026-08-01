#!/usr/bin/env python3
"""
Embedding Generator — Generates vector embeddings for Knowledge Cube entries.

Uses sentence-transformers (local, free, fast) for Tier 3 memory.
"""

import os
import sys
import json
import time
from pathlib import Path
from typing import List, Dict, Any, Optional

# ─── config ─────────────────────────────────────────────────────────
HERMES_HOME = Path(os.environ.get("HERMES_HOME", "D:/Portable_Soft/hermes"))
KC_DB = HERMES_HOME / "cache" / "knowledge_cube.db"
LANCE_DB_DIR = HERMES_HOME / "cache" / "lancedb"

# Model config
MODEL_NAME = os.environ.get("KC_TIER3_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
EMBEDDING_DIM = 384  # all-MiniLM-L6-v2 dimension
CHUNK_SIZE = 512
CHUNK_OVERLAP = 50

# Kill switches
KC_TIER3_ENABLED = os.environ.get("KC_TIER3_ENABLED", "true").lower() == "true"
KC_LANCE_ENABLED = os.environ.get("KC_LANCE_ENABLED", "true").lower() == "true"


class EmbeddingGenerator:
    """Generates and stores embeddings for KC entries."""

    def __init__(self):
        self.model = None
        self.lance_table = None
        self._init_model()
        self._init_lance()

    def _init_model(self):
        """Initialize sentence-transformers model."""
        if not KC_TIER3_ENABLED:
            return
        try:
            from sentence_transformers import SentenceTransformer
            print(f"[EMBEDDING] Loading model: {MODEL_NAME}")
            self.model = SentenceTransformer(MODEL_NAME)
            print(f"[EMBEDDING] Model loaded, dim={self.model.get_embedding_dimension()}")
        except ImportError:
            print("[EMBEDDING] sentence-transformers not installed. Run: pip install sentence-transformers")
        except Exception as e:
            print(f"[EMBEDDING] Model load failed: {e}")

    def _init_lance(self):
        """Initialize LanceDB connection."""
        if not KC_LANCE_ENABLED:
            return
        try:
            import lancedb
            LANCE_DB_DIR.mkdir(parents=True, exist_ok=True)
            db = lancedb.connect(str(LANCE_DB_DIR))
            
            # Create or open table
            if "kc_embeddings" in db.table_names():
                self.lance_table = db.open_table("kc_embeddings")
                print(f"[EMBEDDING] Opened existing LanceDB table: {self.lance_table.count_rows()} rows")
            else:
                # Create with schema
                import pyarrow as pa
                schema = pa.schema([
                    pa.field("memory_id", pa.int64()),
                    pa.field("text", pa.string()),
                    pa.field("embedding", pa.list_(pa.float32(), EMBEDDING_DIM)),
                    pa.field("domain", pa.string()),
                    pa.field("created_at", pa.string()),
                ])
                self.lance_table = db.create_table("kc_embeddings", schema=schema)
                print("[EMBEDDING] Created new LanceDB table: kc_embeddings")
        except ImportError:
            print("[EMBEDDING] lancedb not installed. Run: pip install lancedb pyarrow")
        except Exception as e:
            print(f"[EMBEDDING] LanceDB init failed: {e}")

    def chunk_text(self, text: str) -> List[str]:
        """Split text into overlapping chunks."""
        words = text.split()
        chunks = []
        for i in range(0, len(words), CHUNK_SIZE - CHUNK_OVERLAP):
            chunk = " ".join(words[i:i + CHUNK_SIZE])
            if chunk.strip():
                chunks.append(chunk)
        return chunks if chunks else [text[:CHUNK_SIZE]]

    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for a single text."""
        if not self.model:
            return [0.0] * EMBEDDING_DIM
        try:
            embedding = self.model.encode(text, convert_to_numpy=True, normalize_embeddings=True)
            return embedding.tolist()
        except Exception as e:
            print(f"[EMBEDDING] Generation failed: {e}")
            return [0.0] * EMBEDDING_DIM

    def generate_for_entry(self, memory_id: int, text: str, domain: str, created_at: str) -> bool:
        """Generate and store embeddings for a KC entry (chunked)."""
        if not self.model or not self.lance_table:
            return False

        try:
            chunks = self.chunk_text(text)
            print(f"[EMBEDDING] Generating {len(chunks)} chunks for memory_id={memory_id}")

            for i, chunk in enumerate(chunks):
                embedding = self.generate_embedding(chunk)
                if not embedding or all(v == 0.0 for v in embedding):
                    continue

                # Insert into LanceDB
                import pyarrow as pa
                data = pa.table({
                    "memory_id": [memory_id],
                    "text": [chunk],
                    "embedding": [embedding],
                    "domain": [domain],
                    "created_at": [created_at],
                })
                self.lance_table.add(data)

            return True
        except Exception as e:
            print(f"[EMBEDDING] Store failed for memory_id={memory_id}: {e}")
            return False

    def search_similar(self, query: str, limit: int = 10, domain: str = None) -> List[Dict[str, Any]]:
        """Search for similar entries using vector similarity."""
        if not self.model or not self.lance_table:
            return []

        try:
            query_embedding = self.generate_embedding(query)
            if all(v == 0.0 for v in query_embedding):
                return []

            # Search LanceDB
            results = self.lance_table.search(query_embedding).limit(limit * 2).to_pandas()

            # Filter by domain if specified
            if domain:
                results = results[results["domain"] == domain]

            # Format results
            formatted = []
            for _, row in results.head(limit).iterrows():
                formatted.append({
                    "memory_id": int(row["memory_id"]),
                    "text": row["text"],
                    "domain": row["domain"],
                    "created_at": row["created_at"],
                    "score": float(row["_distance"]),  # cosine distance (lower = more similar)
                })

            return formatted
        except Exception as e:
            print(f"[EMBEDDING] Search failed: {e}")
            return []


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Embedding Generator for Knowledge Cube")
    parser.add_argument("--text", help="Text to embed (for testing)")
    parser.add_argument("--search", help="Search query")
    parser.add_argument("--limit", type=int, default=10, help="Search limit")
    parser.add_argument("--domain", help="Domain filter")
    parser.add_argument("--backfill", action="store_true", help="Backfill embeddings for existing KC entries")

    args = parser.parse_args()

    if not KC_TIER3_ENABLED:
        print("Tier 3 memory disabled: KC_TIER3_ENABLED=false")
        sys.exit(1)

    gen = EmbeddingGenerator()

    if args.text:
        embedding = gen.generate_embedding(args.text)
        print(f"Embedding (first 10): {embedding[:10]}")
        print(f"Dim: {len(embedding)}")

    if args.search:
        results = gen.search_similar(args.search, args.limit, args.domain)
        print(f"Found {len(results)} similar entries:")
        for r in results:
            print(f"  [{r['score']:.4f}] memory_id={r['memory_id']} domain={r['domain']}: {r['text'][:80]}...")

    if args.backfill:
        print("[EMBEDDING] Starting backfill...")
        import sqlite3
        conn = sqlite3.connect(KC_DB)
        cursor = conn.cursor()
        cursor.execute("SELECT id, content as text, axis_domain as domain, ts as created_at FROM experiences WHERE content IS NOT NULL AND content != ''")
        rows = cursor.fetchall()
        print(f"[EMBEDDING] Found {len(rows)} entries to process")

        for i, (mid, text, domain, created_at) in enumerate(rows):
            if i % 100 == 0:
                print(f"[EMBEDDING] Progress: {i}/{len(rows)}")
            gen.generate_for_entry(mid, text, domain or "unknown", created_at or "")

        conn.close()
        print("[EMBEDDING] Backfill complete")


if __name__ == "__main__":
    main()
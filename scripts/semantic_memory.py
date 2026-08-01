#!/usr/bin/env python3
"""
Semantic Memory Module for Hermes
Uses FastEmbed (local, no API keys) + SQLite for vector storage
Provides semantic search alongside KC FTS5 keyword search
"""
import os
import sys
import json
import sqlite3
import numpy as np
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

# FastEmbed for local embeddings (no API key)
try:
    from fastembed import TextEmbedding
    FASTEMBED_AVAILABLE = True
except ImportError:
    FASTEMBED_AVAILABLE = False

# Export availability flag
SEMANTIC_AVAILABLE = FASTEMBED_AVAILABLE

# Local DB paths
SEMANTIC_DB_PATH = os.path.join(os.path.dirname(__file__), "..", "cache", "semantic_memory.db")

# Global embedding model (lazy loaded)
_embedding_model = None

def get_embedding_model():
    """Lazy-load the FastEmbed model (singleton)."""
    global _embedding_model
    if _embedding_model is None:
        try:
            # BAAI/bge-small-en-v1.5 - good quality, small, fast
            _embedding_model = TextEmbedding(model_name="BAAI/bge-small-en-v1.5")
        except Exception as e:
            print(f"Failed to load embedding model: {e}", file=sys.stderr)
            return None
    return _embedding_model

def get_db():
    """Get or create the semantic memory database."""
    os.makedirs(os.path.dirname(SEMANTIC_DB_PATH), exist_ok=True)
    conn = sqlite3.connect(SEMANTIC_DB_PATH)
    conn.row_factory = sqlite3.Row
    
    # Semantic memories table
    conn.execute("""CREATE TABLE IF NOT EXISTS semantic_memories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        content TEXT NOT NULL,
        embedding BLOB NOT NULL,  -- serialized numpy array
        user_id TEXT NOT NULL,
        source TEXT DEFAULT '',
        category TEXT DEFAULT '',
        tags TEXT DEFAULT '',
        importance INTEGER DEFAULT 5,
        confidence REAL DEFAULT 0.5,
        metadata TEXT DEFAULT '{}',
        created_at TEXT,
        updated_at TEXT,
        access_count INTEGER DEFAULT 0
    )""")
    
    # Index for faster lookups
    conn.execute("CREATE INDEX IF NOT EXISTS idx_user_id ON semantic_memories(user_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_category ON semantic_memories(category)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_source ON semantic_memories(source)")
    
    conn.commit()
    return conn


# ============================================================
# Embedding Functions
# ============================================================

_embedding_model = None

def get_embedding_model_instance():
    """Lazy-load the FastEmbed model (singleton)."""
    global _embedding_model
    if _embedding_model is None:
        try:
            from fastembed import TextEmbedding
            # BAAI/bge-small-en-v1.5 - 384 dims, good quality/speed
            _embedding_model = TextEmbedding(model_name="BAAI/bge-small-en-v1.5")
        except Exception as e:
            print(f"Failed to load embedding model: {e}", file=sys.stderr)
            return None
    return _embedding_model

def embed_text(text: str) -> Optional[np.ndarray]:
    """Generate embedding for a single text."""
    model = get_embedding_model()
    if model is None:
        return None
    try:
        embeddings = list(model.embed([text]))
        return embeddings[0] if embeddings else None
    except Exception as e:
        print(f"Embedding failed: {e}", file=sys.stderr)
        return None

def embed_batch(texts: List[str]) -> List[np.ndarray]:
    """Generate embeddings for multiple texts."""
    model = get_embedding_model()
    if model is None:
        return []
    try:
        embeddings = list(model.embed(texts))
        return embeddings
    except Exception as e:
        print(f"Batch embedding failed: {e}", file=sys.stderr)
        return []

def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """Compute cosine similarity between two vectors."""
    if a is None or b is None:
        return 0.0
    dot = np.dot(a, b)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(dot / (norm_a * norm_b))


# ============================================================
# Memory CRUD Operations
# ============================================================

def add_memory(content: str, 
               user_id: str = "alexander",
               source: str = "",
               category: str = "",
               tags: str = "",
               importance: int = 5,
               confidence: float = 0.5,
               metadata: Optional[Dict] = None) -> Optional[int]:
    """Add a memory with automatic embedding."""
    if not FASTEMBED_AVAILABLE:
        print("FastEmbed not available", file=sys.stderr)
        return None
    
    # Generate embedding
    embedding = embed_text(content)
    if embedding is None:
        print(f"Failed to embed: {content[:50]}...", file=sys.stderr)
        return None
    
    # Serialize embedding to bytes
    embedding_bytes = embedding.astype(np.float32).tobytes()
    
    conn = get_db()
    now = datetime.now().isoformat()
    metadata_json = json.dumps(metadata or {})
    
    cursor = conn.execute("""INSERT INTO semantic_memories
        (content, embedding, user_id, source, category, tags, 
         importance, confidence, metadata, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (content, embedding.tobytes(), user_id, source, category, tags,
         importance, confidence, json.dumps({}), datetime.now().isoformat(), 
         datetime.now().isoformat()))
    
    memory_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return memory_id


def search_memories(query: str, 
                    user_id: str = "alexander", 
                    limit: int = 10,
                    min_score: float = 0.0) -> List[Dict[str, Any]]:
    """Semantic search using cosine similarity."""
    if not FASTEMBED_AVAILABLE:
        return []
    
    query_embedding = embed_text(query)
    if query_embedding is None:
        return []
    
    conn = get_db()
    rows = conn.execute("""SELECT id, content, embedding, user_id, source, 
                                  category, tags, importance, confidence,
                                  created_at, access_count
                           FROM semantic_memories 
                           WHERE user_id = ?""", (user_id,)).fetchall()
    conn.close()
    
    if not rows:
        return []
    
    query_vec = embed_text(query) if isinstance(query, str) else query
    if query_vec is None:
        return []
    
    # Compute similarities
    results = []
    for row in rows:
        # Deserialize embedding
        stored_emb = np.frombuffer(row["embedding"], dtype=np.float32)
        if len(stored_emb) != len(query_vec):
            continue
        
        score = cosine_similarity(query_vec, stored_emb)
        if score >= min_score:
            results.append({
                "id": row["id"],
                "content": row["content"],
                "score": score,
                "source": row["source"],
                "category": row["category"],
                "tags": row["tags"],
                "importance": row["importance"],
                "confidence": row["confidence"],
                "created_at": row["created_at"],
            })
    
    # Sort by score descending
    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:limit]


def hybrid_search(query: str, 
                  user_id: str = "alexander",
                  kc_limit: int = 5,
                  sem_limit: int = 5,
                  sem_weight: float = 0.7,
                  kc_weight: float = 0.3) -> Dict[str, Any]:
    """
    Hybrid search: combines KC FTS5 (keyword) + Semantic (vector).
    Returns merged, deduplicated, re-ranked results.
    """
    # Import KC search
    try:
        from .kc_rag import search as kc_search
    except ImportError:
        kc_results = []
    else:
        kc_results = kc_search(query, limit=kc_limit)
    
    # Semantic search
    sem_results = search_memories(query, user_id=user_id, limit=sem_limit)
    
    # Merge and re-rank
    # Normalize scores to 0-1
    max_kc_score = max([r.get("score", 0) for r in kc_results]) if kc_results else 1
    max_sem_score = max([r.get("score", 0) for r in sem_results]) if sem_results else 1
    
    merged = {}
    
    # Add KC results
    for r in kc_results:
        norm_score = r.get("score", 0) / max_kc_score if max_kc_score > 0 else 0
        key = r.get("id", r.get("content", "")[:50])
        merged[key] = {
            "id": r.get("id"),
            "content": r.get("content", ""),
            "source": "kc",
            "kc_score": r.get("score", 0),
            "sem_score": 0.0,
            "combined_score": kc_weight * norm_score,
            "metadata": {
                "source": r.get("source", ""),
                "category": r.get("category", ""),
                "tags": r.get("tags", ""),
                "importance": r.get("importance", 5),
            }
        }
    
    # Add Semantic results
    for r in sem_results:
        norm_score = r.get("score", 0) / max_sem_score if max_sem_score > 0 else 0
        key = r.get("id", r.get("content", "")[:50])
        if key in merged:
            merged[key]["sem_score"] = r.get("score", 0)
            merged[key]["combined_score"] += sem_weight * norm_score
            merged[key]["metadata"].update({
                "category": r.get("category", ""),
                "source": r.get("source", ""),
            })
        else:
            merged[key] = {
                "id": r.get("id"),
                "content": r.get("content", ""),
                "source": "semantic",
                "kc_score": 0.0,
                "sem_score": r.get("score", 0),
                "combined_score": sem_weight * norm_score,
                "metadata": {
                    "source": r.get("source", ""),
                    "category": r.get("category", ""),
                    "tags": r.get("tags", ""),
                    "importance": r.get("importance", 5),
                }
            }
    
    # Sort by combined score
    sorted_results = sorted(merged.values(), key=lambda x: x["combined_score"], reverse=True)
    
    return {
        "query": query,
        "results": sorted_results,
        "kc_count": len(kc_results),
        "semantic_count": len(sem_results),
        "total": len(sorted_results)
    }


def get_all_memories(user_id: str = "alexander", limit: int = 100) -> List[Dict]:
    """Get all memories for a user (for debugging/export)."""
    conn = get_db()
    rows = conn.execute("""
        SELECT * FROM semantic_memories 
        WHERE user_id = ? 
        ORDER BY created_at DESC 
        LIMIT ?
    """, (user_id, limit)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def stats() -> Dict[str, Any]:
    """Get semantic memory statistics."""
    conn = get_db()
    total = conn.execute("SELECT COUNT(*) FROM semantic_memories").fetchone()[0]
    by_category = conn.execute("""
        SELECT category, COUNT(*) as cnt 
        FROM semantic_memories 
        GROUP BY category 
        ORDER BY cnt DESC
    """).fetchall()
    by_user = conn.execute("""
        SELECT user_id, COUNT(*) as cnt 
        FROM semantic_memories 
        GROUP BY user_id
    """).fetchall()
    conn.close()
    
    return {
        "total": total,
        "by_category": dict(by_category),
        "by_user": dict(by_user),
    }


def sync_kc_to_semantic(user_id: str = "alexander") -> int:
    """Sync all KC entries to semantic memory for semantic search."""
    from .kc_rag import get_db as kc_get_db
    
    kc_conn = kc_get_db()
    rows = kc_conn.execute("""
        SELECT id, content, source, category, tags, importance, confidence
        FROM kc_entries
    """).fetchall()
    kc_conn.close()
    
    synced = 0
    for row in rows:
        # Check if already synced
        # (could add a sync_id column, for now just add)
        try:
            add_memory(
                content=row["content"],
                user_id=user_id,
                source=row["source"],
                category=row["category"],
                tags=row["tags"],
                importance=row["importance"],
                confidence=row["confidence"],
                metadata={"kc_id": row["id"]}
            )
            synced += 1
        except Exception as e:
            print(f"Sync failed for {row['id']}: {e}")
    
    return synced


if __name__ == "__main__":
    # Test
    if not FASTEMBED_AVAILABLE:
        print("FastEmbed not available. Install: pip install fastembed")
        sys.exit(1)
    
    print("Testing semantic memory...")
    
    # Add test memories
    test_memories = [
        ("User Alexander runs autonomous CPA/arbitrage on Windows 11 with Hermes agent", "cpa", "research"),
        ("User prefers Telegram for CPA traffic and P2P USDT offramps via Bybit", "cpa", "config"),
        ("DeepTutor: 2-layer plugin model (Tools/Capabilities), 3-layer memory (L1/L2/L3), MCP integration", "deeptutor", "research"),
        ("Mem0: structured facts to vector DB, preferred agent memory 2026", "memory", "research"),
        ("LangGraph: production-grade multi-agent orchestrator, stateful workflows", "langgraph", "research"),
        ("LightRAG: HKUDS fast RAG with GraphRAG support, used in DeepTutor", "lightrag", "research"),
    ]
    
    print("Adding memories...")
    for content, cat, src in test_memories:
        mid = add_memory(content, category=cat, source=src, importance=7)
        print(f"  Added {mid}: {content[:50]}...")
    
    print("\nSearching...")
    queries = [
        "CPA traffic Telegram",
        "DeepTutor memory architecture",
        "Mem0 vector database",
        "P2P USDT offramp",
        "agent orchestration LangGraph",
    ]
    
    for q in queries:
        print(f"\nQuery: '{q}'")
        results = search_memories(q, limit=3)
        for r in results:
            print(f"  [{r['score']:.3f}] {r['content'][:70]}...")
    
    print("\nHybrid search test:")
    hybrid = hybrid_search("CPA traffic Telegram")
    print(f"KC: {hybrid['kc_count']}, Semantic: {hybrid['semantic_count']}")
    for r in hybrid["results"][:3]:
        print(f"  [{r['combined_score']:.3f}] {r['source']} - {r['content'][:60]}...")
    
    print(f"\nStats: {stats()}")
    print("\nSemantic Memory: OK")
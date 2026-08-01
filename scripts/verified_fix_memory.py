#!/usr/bin/env python3
"""
Simple Verified Fix Memory — stores and retrieves verified fixes from Knowledge Cube.
No Docker, no heavy deps — just SQLite + optional sentence-transformers.
"""

import json
import os
import sys
import sqlite3
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any

HERMES_HOME = Path(os.environ.get("HERMES_HOME", str(Path(__file__).resolve().parent.parent)))
DB_PATH = HERMES_HOME / "cache" / "verified_fixes.db"

# Try to use embeddings if available
try:
    from sentence_transformers import SentenceTransformer
    EMBED_MODEL = SentenceTransformer('all-MiniLM-L6-v2')
    HAS_EMBEDDINGS = True
except ImportError:
    HAS_EMBEDDINGS = False
    EMBED_MODEL = None


def init_db():
    """Initialize the verified fixes database."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("""
        CREATE TABLE IF NOT EXISTS verified_fixes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            issue_hash TEXT UNIQUE NOT NULL,
            issue_type TEXT NOT NULL,
            issue_description TEXT NOT NULL,
            fix_type TEXT NOT NULL,
            fix_description TEXT NOT NULL,
            fix_content TEXT,
            target_file TEXT,
            evidence TEXT,
            tags TEXT,  -- JSON array
            embedding BLOB,  -- serialized numpy array
            created_at TEXT NOT NULL,
            verified_at TEXT NOT NULL
        )
    """)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_verified_fixes_issue_hash ON verified_fixes(issue_hash)
    """)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_verified_fixes_type ON verified_fixes(issue_type)
    """)
    conn.commit()
    conn.close()


def _hash_issue(issue_type: str, description: str) -> str:
    """Create a hash for deduplication."""
    return hashlib.sha256(f"{issue_type}:{description}".encode()).hexdigest()[:16]


def _get_embedding(text: str) -> Optional[bytes]:
    """Get embedding for text if available."""
    if not HAS_EMBEDDINGS or not EMBED_MODEL:
        return None
    try:
        emb = EMBED_MODEL.encode(text)
        return emb.tobytes()
    except Exception:
        return None


def _cosine_similarity(a: bytes, b: bytes) -> float:
    """Compute cosine similarity between two embeddings."""
    import numpy as np
    try:
        vec_a = np.frombuffer(a, dtype=np.float32)
        vec_b = np.frombuffer(b, dtype=np.float32)
        if vec_a.size == 0 or vec_b.size == 0:
            return 0.0
        return float(np.dot(vec_a, vec_b) / (np.linalg.norm(vec_a) * np.linalg.norm(vec_b)))
    except Exception:
        return 0.0


def store_verified_fix(
    issue_type: str,
    issue_description: str,
    fix_type: str,
    fix_description: str,
    fix_content: str = "",
    target_file: str = "",
    evidence: str = "",
    tags: List[str] = None
) -> bool:
    """
    Store a verified fix in the memory.
    Returns True if stored (new), False if duplicate.
    """
    init_db()
    issue_hash = _hash_issue(issue_type, issue_description)
    embedding = _get_embedding(f"{issue_type}: {issue_description} | Fix: {fix_description}")
    tags_json = json.dumps(tags or [])
    
    conn = sqlite3.connect(str(DB_PATH))
    try:
        conn.execute("""
            INSERT INTO verified_fixes 
            (issue_hash, issue_type, issue_description, fix_type, fix_description, 
             fix_content, target_file, evidence, tags, embedding, created_at, verified_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            issue_hash, issue_type, issue_description, fix_type, fix_description,
            fix_content, target_file, evidence, tags_json, embedding,
            datetime.now().isoformat(), datetime.now().isoformat()
        ))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        # Duplicate - update verification timestamp
        conn.execute("""
            UPDATE verified_fixes 
            SET verified_at = ?, evidence = ?
            WHERE issue_hash = ?
        """, (datetime.now().isoformat(), evidence, issue_hash))
        conn.commit()
        return False
    finally:
        conn.close()


def query_similar_fixes(query_text: str, limit: int = 5, min_similarity: float = 0.3) -> List[Dict]:
    """
    Query for similar verified fixes using embeddings.
    Falls back to keyword search if no embeddings.
    """
    init_db()
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    
    if HAS_EMBEDDINGS and EMBED_MODEL:
        query_emb = _get_embedding(query_text)
        if query_emb:
            cursor = conn.execute("SELECT * FROM verified_fixes WHERE embedding IS NOT NULL")
            results = []
            for row in cursor.fetchall():
                sim = _cosine_similarity(query_emb, row["embedding"])
                if sim >= min_similarity:
                    results.append((sim, dict(row)))
            results.sort(key=lambda x: x[0], reverse=True)
            conn.close()
            return [r[1] for r in results[:limit]]
    
    # Fallback: simple keyword search
    keywords = query_text.lower().split()
    placeholders = " OR ".join(["issue_description LIKE ? OR fix_description LIKE ?"] * len(keywords))
    params = []
    for kw in keywords:
        params.extend([f"%{kw}%", f"%{kw}%"])
    
    cursor = conn.execute(f"""
        SELECT * FROM verified_fixes 
        WHERE {placeholders}
        ORDER BY verified_at DESC
        LIMIT ?
    """, params + [limit])
    results = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return results


def get_fix_by_hash(issue_hash: str) -> Optional[Dict]:
    """Get a specific fix by its hash."""
    init_db()
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    cursor = conn.execute("SELECT * FROM verified_fixes WHERE issue_hash = ?", (issue_hash,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def get_stats() -> Dict:
    """Get memory statistics."""
    init_db()
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.execute("SELECT COUNT(*) as total, COUNT(DISTINCT issue_type) as types FROM verified_fixes")
    row = cursor.fetchone()
    conn.close()
    return {"total_fixes": row[0], "issue_types": row[1]}


# Convenience function for hermes_hooks integration
def on_verified_fix(
    issue_id: str,
    issue_type: str,
    issue_description: str,
    fix_result: Dict[str, Any]
) -> bool:
    """
    Called from hermes_hooks.on_task_complete when verified=True.
    Expects fix_result with: fix_type, fix_description, fix_content, target_file, evidence, tags
    """
    return store_verified_fix(
        issue_type=issue_type,
        issue_description=issue_description,
        fix_type=fix_result.get("fix_type", "unknown"),
        fix_description=fix_result.get("fix_description", ""),
        fix_content=fix_result.get("fix_content", ""),
        target_file=fix_result.get("target_file", ""),
        evidence=fix_result.get("evidence", ""),
        tags=fix_result.get("tags", []) + ["verified", "proactive", issue_id]
    )


if __name__ == "__main__":
    # Test
    init_db()
    print("DB initialized at:", DB_PATH)
    
    # Store a test fix
    stored = store_verified_fix(
        issue_type="indentation_error",
        issue_description="IndentationError in proactive_executor.py line 1024",
        fix_type="patch",
        fix_description="Fixed missing indentation after if statement",
        fix_content="--- a/scripts/proactive_executor.py\n+++ b/scripts/proactive_executor.py\n@@ -1021,7 +1021,7 @@\n                 )\n \n-    if not errors:\n+    if not errors:\n         report(\"  No cron jobs with errors detected — all green\")",
        target_file="scripts/proactive_executor.py",
        evidence="python -m py_compile scripts/proactive_executor.py PASSED",
        tags=["indentation", "proactive", "auto-fix"]
    )
    print(f"Stored: {stored}")
    
    # Query similar
    results = query_similar_fixes("IndentationError proactive_executor")
    print(f"Found {len(results)} similar fixes")
    for r in results:
        print(f"  - {r['issue_type']}: {r['fix_description'][:60]}")
    
    print("Stats:", get_stats())
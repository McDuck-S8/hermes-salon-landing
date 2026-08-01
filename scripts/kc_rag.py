import sqlite3
import json
import os
import sys
import hashlib
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path

# Import semantic memory module
try:
    from scripts.semantic_memory import (
        add_memory as sem_add_memory,
        search_memories as sem_search,
        get_db as sem_get_db,
        SEMANTIC_AVAILABLE
    )
    SEMANTIC_AVAILABLE = True
except ImportError as e:
    SEMANTIC_AVAILABLE = False
    print(f"Semantic memory not available: {e}", file=sys.stderr)

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "cache", "knowledge_cube.db")
LOG_PATH = os.path.join(os.path.dirname(__file__), "..", "logs", "kc_rag.log")
OKF_BUNDLE_ROOT = os.path.join(os.path.dirname(__file__), "..", "knowledge", "okf")
OKF_LOG_PATH = os.path.join(OKF_BUNDLE_ROOT, "log.md")

def log(msg):
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    with open(LOG_PATH, "a") as f:
        f.write(f"[{datetime.now().isoformat()}] {msg}\n")

def get_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    # Core table
    conn.execute("""CREATE TABLE IF NOT EXISTS kc_entries (
        id TEXT PRIMARY KEY,
        content TEXT NOT NULL,
        tags TEXT DEFAULT '',
        source TEXT DEFAULT '',
        category TEXT DEFAULT '',
        importance INTEGER DEFAULT 5,
        created_at TEXT,
        updated_at TEXT,
        access_count INTEGER DEFAULT 0
    )""")
    # FTS5 index (content table for external content mode)
    conn.execute("""CREATE VIRTUAL TABLE IF NOT EXISTS kc_fts USING fts5(
        id, content, tags, source, category
    )""")
    # Trigger table for events
    conn.execute("""CREATE TABLE IF NOT EXISTS kc_events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        event_type TEXT,
        payload TEXT,
        processed INTEGER DEFAULT 0,
        created_at TEXT
    )""")
    conn.commit()
    return conn

def content_hash(text):
    return hashlib.md5(text.encode()).hexdigest()[:12]


# ═══════════════════════════════════════════════════════════════
# OKF Live Sync — writes concept .md files on every upsert
# ═══════════════════════════════════════════════════════════════


def sanitize_yaml_field(s):
    """Replace YAML-dangerous characters to prevent injection via crafted input.

    Escapes backslash, newline, and colon characters that could break YAML
    structure or allow injection of new YAML keys/values.
    """
    if not s:
        return s
    s = s.replace("\\", "\\\\")   # backslash (YAML escape char in quoted strings)
    s = s.replace("\n", "\\n")    # newlines (would break YAML lines)
    s = s.replace(":", "\\:")     # colons (YAML key separator in bare scalars)
    return s


def okf_make_frontmatter(content, tags="", source="", category="",
                         importance=5, confidence=0.5,
                         verification_method="manual", expiration_date=None,
                         entry_id=None, is_update=False):
    """Build OKF-conformant YAML frontmatter for a kc_entries concept."""
    now = datetime.now().isoformat()
    concept_type = sanitize_yaml_field(category or "Knowledge")
    title = (content or "")[:80]
    ts = now

    fm = "---\n"
    fm += f"type: {concept_type}\n"
    if title:
        safe_title = title.replace('"', "'")
        safe_title = sanitize_yaml_field(safe_title)
        fm += f'title: "{safe_title}"\n'
    fm += f"timestamp: {ts}\n"
    fm += f"confidence: {float(confidence):.3f}\n"
    if expiration_date:
        fm += f"expiration_date: {sanitize_yaml_field(expiration_date)}\n"
    fm += f"verification_method: {sanitize_yaml_field(verification_method)}\n"
    fm += f"source_table: kc_entries\n"
    fm += f"importance: {int(importance)}\n"

    # Format tags properly
    if tags:
        tag_list = [t.strip() for t in tags.replace(",", " ").split() if t.strip()]
        if tag_list:
            unique_tags = []
            seen = set()
            for t in tag_list:
                t = t.strip('"').strip("'")
                if t and t not in seen and t not in ("auto_tagged",):
                    seen.add(t)
                    unique_tags.append(t)
            if unique_tags:
                fm += "tags:\n"
                for t in unique_tags[:10]:
                    fm += f"  - {sanitize_yaml_field(t)}\n"

    if source:
        fm += f"resource: {sanitize_yaml_field(source)}\n"
    fm += "---\n\n"
    fm += (content or "").rstrip() + "\n"
    return fm


def okf_determine_subdir(category="", entry_id=""):
    """Determine subdirectory path for a kc_entries concept."""
    cat = (category or "uncategorized").lower().replace(" ", "_").replace("/", "_")[:40]
    return f"experiences/{cat}"


def okf_write_single(content, tags="", source="", category="",
                     importance=5, confidence=0.5,
                     verification_method="manual", expiration_date=None,
                     entry_id=None):
    """Write a single concept .md file to the OKF bundle."""
    bundle_root = OKF_BUNDLE_ROOT
    subdir = okf_determine_subdir(category, entry_id)
    target_dir = os.path.join(bundle_root, subdir)
    os.makedirs(target_dir, exist_ok=True)

    if not entry_id:
        entry_id = content_hash(content)
    filename = f"{entry_id}.md"
    filepath = os.path.join(target_dir, filename)

    md_content = okf_make_frontmatter(
        content, tags, source, category,
        importance, confidence, verification_method, expiration_date, entry_id
    )

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(md_content)

    # Append to log.md
    okf_log_entry("UPSERT", entry_id, f"[{source}/{category}] conf={confidence:.2f}")

    return filepath


def okf_delete_single(entry_id):
    """Remove a concept .md file from the OKF bundle."""
    # Search for the file across all subdirectories
    bundle_root = OKF_BUNDLE_ROOT
    if not os.path.exists(bundle_root):
        return False

    for root, dirs, files in os.walk(bundle_root):
        for fname in files:
            if fname == f"{entry_id}.md":
                fpath = os.path.join(root, fname)
                os.remove(fpath)
                okf_log_entry("DELETE", entry_id, "removed from bundle")
                return True
    return False


def okf_log_entry(action, concept_id, detail=""):
    """Append to log.md per OKF SPEC §7."""
    log_path = OKF_LOG_PATH
    if not os.path.exists(os.path.dirname(log_path)):
        return
    now = datetime.now().isoformat()
    line = f"| {now} | {action} | {concept_id} | {detail} |\n"
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(line)


def upsert(content, tags="", source="", category="", importance=5,
           confidence=0.5, verification_method="manual", expiration_date=None):
    """Add/update knowledge entry with OKF-Lite fields."""
    conn = get_db()
    entry_id = content_hash(content)
    now = datetime.now().isoformat()

    # Check if exists
    existing = conn.execute("SELECT id FROM kc_entries WHERE id=?", (entry_id,)).fetchone()
    if existing:
        conn.execute("""UPDATE kc_entries SET content=?, tags=?, source=?, category=?,
            importance=?, confidence=?, verification_method=?, expiration_date=?,
            updated_at=? WHERE id=?""",
            (content, tags, source, category, importance, confidence,
             verification_method, expiration_date, now, entry_id))
        log(f"UPDATE: {entry_id} [{source}] conf={confidence:.2f} verify={verification_method}")
    else:
        conn.execute("""INSERT INTO kc_entries
            (id, content, tags, source, category, importance, confidence,
             verification_method, expiration_date, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (entry_id, content, tags, source, category, importance, confidence,
             verification_method, expiration_date, now, now))
        # Update FTS
        conn.execute("INSERT INTO kc_fts (id, content, tags, source, category) VALUES (?, ?, ?, ?, ?)",
            (entry_id, content, tags, source, category))
        log(f"INSERT: {entry_id} [{source}] conf={confidence:.2f} verify={verification_method}")

    conn.commit()
    conn.close()

    # OKF live sync: write/update concept .md file in bundle
    try:
        okf_write_single(
            content=content, tags=tags, source=source, category=category,
            importance=importance, confidence=confidence,
            verification_method=verification_method,
            expiration_date=expiration_date, entry_id=entry_id
        )
    except Exception as e:
        log(f"OKF-SYNC ERROR: {e}")

    # OKF event: emit knowledge_added for real-time domain monitoring
    try:
        _scripts_dir = os.path.join(os.path.dirname(__file__))
        if _scripts_dir not in sys.path:
            sys.path.insert(0, _scripts_dir)
        from event_bus import emit as eb_emit
        eb_emit("knowledge_added", {
            "content": content[:200],
            "domain": category,
            "category": category,
            "tags": tags,
            "source": source,
            "confidence": confidence,
            "verification_method": verification_method,
            "expiration_date": expiration_date,
            "entry_id": entry_id,
        })
        # Chain heartbeat: knowledge added to KC
        try:
            from chain_heartbeat import event_beat
            event_beat("knowledge_added")
        except ImportError:
            pass
        # Event-driven ripple: new knowledge may trigger report
        try:
            from ripple_consumer import on_knowledge_added
            on_knowledge_added()
        except ImportError:
            pass
    except ImportError:
        # Fallback: queue event without direct dispatch
        try:
            from emit_event import emit as ee_emit
            ee_emit("knowledge_added", {
                "content": content[:200],
                "domain": category,
                "category": category,
                "tags": tags,
                "source": source,
                "confidence": confidence,
                "entry_id": entry_id,
            })
        except Exception:
            pass  # event is non-critical, don't break upsert
    except Exception as e:
        log(f"EVENT-EMIT ERROR: {e}")

    # Semantic memory: embed new knowledge for semantic search
    try:
        from semantic_memory import add_memory
        add_memory(
            content=content[:500],
            source=source or "kc_rag",
            category=category or "",
            tags=tags or "",
            importance=importance,
            confidence=confidence,
            metadata={"entry_id": entry_id, "method": verification_method}
        )
    except Exception:
        pass  # embedding is non-critical

    return entry_id


def _sanitize_fts5_query(query):
    """Sanitize a user query for safe use with FTS5 MATCH.

    Strips FTS5 special characters and operators, then wraps in double
    quotes to force literal phrase matching. Enforces 500-char limit.
    """
    if not isinstance(query, str):
        query = str(query)
    # Strip double quotes (would break out of quoted phrase)
    query = query.replace('"', '')
    # Strip FTS5 special characters that have syntactic meaning
    import re
    query = re.sub(r'[()*+]', '', query)
    # Strip FTS5 boolean/keyword operators (case-insensitive whole words)
    query = re.sub(
        r'\b(NEAR|AND|OR|NOT)\b',
        '',
        query,
        flags=re.IGNORECASE
    )
    # Collapse whitespace from removals
    query = re.sub(r'\s+', ' ', query).strip()
    # Enforce 500-char limit
    query = query[:500]
    # Wrap in double quotes for literal phrase matching
    return f'"{query}"'


def search(query, limit=10, min_importance=0, min_confidence=0.0):
    """Search knowledge with confidence-weighted ranking.

    Results are ranked by: confidence * 0.3 + fts_rank * 0.7
    Higher confidence entries appear first.
    """
    conn = get_db()
    # FTS5 search with confidence weighting
    safe_query = _sanitize_fts5_query(query)
    try:
        rows = conn.execute("""
            SELECT e.*, fts.rank,
                   (COALESCE(e.confidence, 0.5) * 0.3 + (1.0 / (1.0 + ABS(fts.rank))) * 0.7) as score
            FROM kc_fts fts
            JOIN kc_entries e ON e.id = fts.id
            WHERE kc_fts MATCH ?
            AND e.importance >= ?
            AND COALESCE(e.confidence, 0.5) >= ?
            ORDER BY score DESC
            LIMIT ?
        """, (safe_query, min_importance, min_confidence, limit)).fetchall()
    except Exception:
        # Fallback to LIKE search
        rows = conn.execute("""
            SELECT *, 0 as rank,
                   COALESCE(confidence, 0.5) as score
            FROM kc_entries
            WHERE (content LIKE ? OR tags LIKE ?)
            AND importance >= ?
            AND COALESCE(confidence, 0.5) >= ?
            ORDER BY score DESC
            LIMIT ?
        """, (f"%{query}%", f"%{query}%", min_importance, min_confidence, limit)).fetchall()

    # Update access counts
    for row in rows:
        conn.execute("UPDATE kc_entries SET access_count = access_count + 1 WHERE id=?", (row["id"],))
    conn.commit()
    conn.close()

    return [dict(r) for r in rows]


def hybrid_search(query, limit=10, semantic_weight=0.5, kc_weight=0.5):
    """Hybrid search: combine KC FTS5 keyword search with Semantic vector search.
    
    Args:
        query: search query
        limit: max results
        semantic_weight: weight for semantic search (0-1)
        kc_weight: weight for KC FTS5 search (0-1)
    
    Returns merged, ranked results.
    """
    results = []
    
    # 1. KC FTS5 search
    kc_results = search(query, limit=limit*2)
    for r in kc_results:
        r["source_type"] = "kc"
        r["hybrid_score"] = r.get("score", 0) * kc_weight
        results.append(r)
    
    # 2. Semantic search (if available)
    if SEMANTIC_AVAILABLE:
        try:
            sem_results = sem_search(query, user_id="alexander", limit=limit*2)
            for r in sem_results:
                r["source_type"] = "semantic"
                r["hybrid_score"] = r.get("score", 0) * semantic_weight
                # Ensure content field exists
                r["content"] = r.get("content", "")
                r["id"] = r.get("id", f"sem_{r.get('id', 0)}")
                results.append(r)
        except Exception as e:
            print(f"Semantic search error: {e}", file=sys.stderr)
    
    # Deduplicate by content similarity (simple)
    seen = set()
    deduped = []
    for r in results:
        content_key = r["content"][:100]  # First 100 chars as key
        if content_key not in seen:
            seen.add(content_key)
            deduped.append(r)
    
    # Sort by hybrid score
    deduped.sort(key=lambda x: x.get("hybrid_score", 0), reverse=True)
    
    return deduped[:limit]


def find_expired_knowledge(limit=100):
    """Find knowledge entries where expiration_date < now.

    These are stale facts that need re-verification or removal.
    Returns list of expired entries sorted by confidence (lowest first).
    """
    conn = get_db()
    now = datetime.now().isoformat()
    rows = conn.execute("""
        SELECT id, content, tags, source, category, confidence,
               expiration_date, verification_method, updated_at
        FROM kc_entries
        WHERE expiration_date IS NOT NULL
        AND expiration_date != ''
        AND expiration_date < ?
        ORDER BY confidence ASC
        LIMIT ?
    """, (now, limit)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def find_expiring_soon(days=30, limit=50):
    """Find entries expiring within N days."""
    conn = get_db()
    now = datetime.now()
    cutoff = (now + timedelta(days=days)).isoformat()
    rows = conn.execute("""
        SELECT id, content, tags, source, confidence, expiration_date
        FROM kc_entries
        WHERE expiration_date IS NOT NULL
        AND expiration_date != ''
        AND expiration_date > ?
        AND expiration_date < ?
        ORDER BY expiration_date ASC
        LIMIT ?
    """, (now.isoformat(), cutoff, limit)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_by_tags(tags, limit=20):
    conn = get_db()
    tag_conditions = " OR ".join(["tags LIKE ?"] * len(tags))
    params = [f"%{t}%" for t in tags]
    params.append(limit)
    rows = conn.execute(f"""
        SELECT * FROM kc_entries WHERE {tag_conditions} ORDER BY importance DESC LIMIT ?
    """, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def stats():
    conn = get_db()
    total = conn.execute("SELECT COUNT(*) as n FROM kc_entries").fetchone()["n"]
    by_source = conn.execute("SELECT source, COUNT(*) as n FROM kc_entries GROUP BY source ORDER BY n DESC").fetchall()
    by_category = conn.execute("SELECT category, COUNT(*) as n FROM kc_entries GROUP BY category ORDER BY n DESC").fetchall()
    most_accessed = conn.execute("SELECT id, content, access_count, tags FROM kc_entries ORDER BY access_count DESC LIMIT 5").fetchall()
    conn.close()
    return {
        "total": total,
        "by_source": {r["source"]: r["n"] for r in by_source},
        "by_category": {r["category"]: r["n"] for r in by_category},
        "most_accessed": [dict(r) for r in most_accessed]
    }

def event(event_type, payload=""):
    conn = get_db()
    conn.execute("INSERT INTO kc_events (event_type, payload, created_at) VALUES (?, ?, ?)",
        (event_type, json.dumps(payload, ensure_ascii=False), datetime.now().isoformat()))
    conn.commit()
    conn.close()

def pending_events(limit=50):
    conn = get_db()
    rows = conn.execute("SELECT * FROM kc_events WHERE processed=0 ORDER BY created_at LIMIT ?", (limit,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def mark_event_processed(event_id):
    conn = get_db()
    conn.execute("UPDATE kc_events SET processed=1 WHERE id=?", (event_id,))
    conn.commit()
    conn.close()

if __name__ == "__main__":
    # Test
    db = get_db()
    e1 = upsert("RAG Pipeline built with SQLite FTS5. Zero new deps.", "rag,knowledge", "system", "architecture", 8)
    e2 = upsert("Salon bot needs separate token for polling mode", "salon,bot,token", "system", "blocker", 9)
    e3 = upsert("Network unstable from Crimea. Gateway auto-reconnect works.", "network,crimea,gateway", "system", "infrastructure", 7)
    print(f"Inserted 3 entries: {e1}, {e2}, {e3}")
    
    results = search("salon bot")
    print(f"Search 'salon bot': {len(results)} results")
    for r in results:
        print(f"  [{r['source']}] {r['content'][:80]}... (imp={r['importance']})")
    
    s = stats()
    print(f"Total: {s['total']}, by_source: {s['by_source']}")
    
    event("task_complete", {"task": "RAG pipeline built", "result": "working"})
    evts = pending_events()
    print(f"Pending events: {len(evts)}")
    
    db.close()
    print("RAG Pipeline: OK")

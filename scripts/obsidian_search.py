#!/usr/bin/env python3
"""
Obsidian Vault Search for Hermes.
Uses FTS5 index for fast full-text search across all .md notes.
Re-index daily or on-demand.

Usage:
  python scripts/obsidian_search.py --query "search term"    # Search vault
  python scripts/obsidian_search.py --reindex                 # Rebuild index
  python scripts/obsidian_search.py --tags                    # Show tag cloud
  python scripts/obsidian_search.py --stats                   # Index stats
"""

import os, sys, sqlite3, hashlib, re, time, json, argparse
from pathlib import Path

VAULT_PATH = r"D:\Users\Asus\Документы\Obsidian Vault"
DB_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
DB_PATH = os.path.join(DB_DIR, "obsidian_search.db")

def get_db():
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL")
    return conn

def ensure_index():
    """Create tables if they don't exist."""
    conn = get_db()
    conn.execute("CREATE VIRTUAL TABLE IF NOT EXISTS notes_fts USING fts5(title, path, content, tags, tokenize='porter unicode61')")
    conn.execute("CREATE TABLE IF NOT EXISTS notes_meta (path TEXT PRIMARY KEY, file_hash TEXT, mtime REAL, indexed_at REAL)")
    conn.close()

def reindex():
    """Rebuild the FTS index from all .md files."""
    ensure_index()
    conn = get_db()
    
    existing = {}
    for row in conn.execute("SELECT path, file_hash, mtime FROM notes_meta"):
        existing[row[0]] = (row[1], row[2])
    
    new_count = changed_count = skipped_count = 0
    
    for root, dirs, files in os.walk(VAULT_PATH):
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        for fname in files:
            if not fname.endswith('.md'):
                continue
            fpath = os.path.join(root, fname)
            rel_path = os.path.relpath(fpath, VAULT_PATH)
            
            try:
                with open(fpath, 'r', encoding='utf-8', errors='replace') as f:
                    content = f.read()
            except:
                continue
            
            file_hash = hashlib.md5(content.encode()).hexdigest()
            old = existing.get(rel_path)
            if old and old[0] == file_hash:
                skipped_count += 1
                continue
            
            title_match = re.search(r'^# (.+)$', content, re.MULTILINE)
            title = title_match.group(1).strip() if title_match else fname[:-3]
            tags_list = re.findall(r'#([\w-]+)', content)
            tags_str = ' '.join(tags_list[:30])
            
            clean_content = content
            if content.startswith('---'):
                end = content.find('---', 3)
                if end > 0:
                    clean_content = content[end+3:]
            
            if old:
                conn.execute("DELETE FROM notes_fts WHERE path = ?", (rel_path,))
                changed_count += 1
            else:
                new_count += 1
            
            conn.execute("INSERT INTO notes_fts(title, path, content, tags) VALUES (?, ?, ?, ?)",
                        (title, rel_path, clean_content[:100000], tags_str))
            conn.execute("INSERT OR REPLACE INTO notes_meta(path, file_hash, mtime, indexed_at) VALUES (?, ?, ?, ?)",
                        (rel_path, file_hash, mtime, time.time()))
    
    conn.commit()
    total = conn.execute("SELECT COUNT(*) FROM notes_fts").fetchone()[0]
    conn.close()
    
    return {"total": total, "new": new_count, "changed": changed_count, "skipped": skipped_count}

def search(query, limit=10, include_content=False):
    """Search notes by content."""
    ensure_index()
    conn = get_db()
    
    # Try FTS5 first
    results = []
    try:
        fts_query = ' OR '.join(f'"{w}"' for w in query.split() if len(w) > 1) or f'"{query}"'
        rows = conn.execute(
            "SELECT path, title, snippet(notes_fts, 2, '...', '...', 20, 3) FROM notes_fts WHERE notes_fts MATCH ? LIMIT ?",
            (fts_query, limit)
        ).fetchall()
        results = [{"path": r[0], "title": r[1], "snippet": r[2], "method": "fts5"} for r in rows]
    except:
        pass
    
    # Fallback to LIKE search
    if not results:
        like_q = f'%{query}%'
        rows = conn.execute(
            "SELECT path, title, length(content) FROM notes_fts WHERE content LIKE ? OR title LIKE ? LIMIT ?",
            (like_q, like_q, limit)
        ).fetchall()
        results = [{"path": r[0], "title": r[1], "snippet": f"({r[2]} chars)", "method": "like"} for r in rows]
    
    conn.close()
    return results

def get_tags(min_count=1, limit=20):
    """Get tag cloud from indexed notes."""
    ensure_index()
    conn = get_db()
    rows = conn.execute("""
        SELECT value, COUNT(*) as cnt FROM (
            SELECT DISTINCT notes_fts.path, substr(value, 1, 40) as value 
            FROM notes_fts, json_each('["' || replace(tags, ' ', '","') || '"]')
            WHERE tags != '' AND length(value) > 1
        ) GROUP BY value HAVING cnt >= ? ORDER BY cnt DESC LIMIT ?
    """, (min_count, limit)).fetchall()
    conn.close()
    return rows

def get_stats():
    """Get index statistics."""
    ensure_index()
    conn = get_db()
    total = conn.execute("SELECT COUNT(*) FROM notes_fts").fetchone()[0]
    tags_count = conn.execute("SELECT COUNT(*) FROM notes_meta").fetchone()[0]
    last_index = conn.execute("SELECT MAX(indexed_at) FROM notes_meta").fetchone()[0]
    
    # Size of index
    index_size = os.path.getsize(DB_PATH) if os.path.exists(DB_PATH) else 0
    conn.close()
    
    return {
        "total_notes": total,
        "indexed_notes": tags_count,
        "last_indexed": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(last_index)) if last_index else 'Never',
        "db_size_bytes": index_size,
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Obsidian Vault Search")
    parser.add_argument("--query", "-q", help="Search query")
    parser.add_argument("--reindex", action="store_true", help="Rebuild index")
    parser.add_argument("--tags", action="store_true", help="Show tag cloud")
    parser.add_argument("--stats", action="store_true", help="Show stats")
    parser.add_argument("--limit", type=int, default=10, help="Max results")
    parser.add_argument("--json", action="store_true", help="JSON output")
    
    args = parser.parse_args()
    
    if args.reindex:
        result = reindex()
        if args.json:
            print(json.dumps(result))
        else:
            print(f"Indexed: {result['total']} notes (new={result['new']}, changed={result['changed']}, skipped={result['skipped']})")
    
    elif args.tags:
        tags = get_tags(limit=args.limit)
        if args.json:
            print(json.dumps(dict(tags)))
        else:
            for tag, count in tags:
                print(f"  #{tag}: {count}")
    
    elif args.stats:
        stats = get_stats()
        if args.json:
            print(json.dumps(stats))
        else:
            for k, v in stats.items():
                print(f"  {k}: {v}")
    
    elif args.query:
        results = search(args.query, limit=args.limit)
        if args.json:
            print(json.dumps(results))
        else:
            if results:
                print(f"Found {len(results)} results for '{args.query}':")
                for r in results:
                    print(f"\n  📄 {r['path']}")
                    print(f"     {r['title']}")
                    print(f"     {r['snippet']}")
            else:
                print(f"No results for '{args.query}'")
    
    else:
        parser.print_help()

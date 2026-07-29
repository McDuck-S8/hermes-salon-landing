#!/usr/bin/env python3
"""
Auto-Recall for Knowledge Cube — Lavra pattern.
Searches experiences by keywords and returns top relevant ones.
"""

import json, os, sqlite3, re
import sys
from pathlib import Path
from collections import Counter

# ---------------------------------------------------------------------------
# Unified config — single source of truth
# ---------------------------------------------------------------------------
sys.path.insert(0, str(Path(__file__).resolve().parent))
from hermes_config import HERMES_HOME, CACHE_DIR
from hermes_config import get_db as _config_get_db

DB_PATH = CACHE_DIR / "knowledge_cube.db"
LAVRA_KNOWLEDGE = HERMES_HOME / "data" / "lavra_knowledge.jsonl"

# Common stopwords to ignore during keyword extraction
STOPWORDS = {
    "the","a","an","is","was","were","are","be","been","have","has","had",
    "do","does","did","will","would","could","should","may","might","shall",
    "can","to","of","in","for","on","with","at","by","from","as","into",
    "through","during","before","after","above","below","between","out",
    "off","over","under","again","further","then","once","and","but","or",
    "nor","not","so","very","just","than","too","also","it","its","this",
    "that","i","me","my","we","our","you","your","he","him","his","she",
    "her","they","them","what","which","who","when","where","why","how",
    "all","each","every","both","few","more","most","other","some","such",
    "no","only","own","same","if","because","about","up","down","been",
    "being","into","need","make","please","help","want","try","use","set",
    "get","let","run","way","well","also","like","know","think","see",
    "come","take","make","go","say","tell","give","put","keep","let",
}

# Domain keywords for boosting relevant matches
DOMAIN_KEYWORDS = {
    "coding": ["code","python","javascript","bug","function","class","import","debug","refactor","git"],
    "research": ["search","find","analyze","compare","review","paper","study"],
    "devops": ["docker","deploy","server","nginx","config","cron","ci","cd","pipeline"],
    "data": ["data","csv","json","database","sql","pandas","analysis","chart"],
    "communication": ["email","telegram","message","send","notify","slack"],
    "file_ops": ["file","read","write","directory","path","copy","move"],
    "browser": ["browser","web","page","url","click","navigate","scrape"],
    "creative": ["image","generate","design","write","story","creative"],
    "system": ["install","config","setup","env","path","permission","process"],
}


def get_db():
    """Get database connection, create FTS if not exists."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = _config_get_db(DB_PATH)
    if conn is None:
        # Fallback: create directly if hermes_config.get_db returned None
        # (e.g., DB didn't exist yet)
        conn = sqlite3.connect(str(DB_PATH))
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")

    # Create FTS5 virtual table if not exists for full-text search
    try:
        conn.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS experiences_fts USING fts5(
                raw_text, axis_domain, axis_outcome, tags,
                content='experiences',
                content_rowid='id'
            )
        """)
        # Populate FTS if empty
        count = conn.execute("SELECT COUNT(*) FROM experiences_fts").fetchone()[0]
        if count == 0:
            conn.execute("""
                INSERT INTO experiences_fts(rowid, raw_text, axis_domain, axis_outcome, tags)
                SELECT id, raw_text, axis_domain, axis_outcome, tags FROM experiences
            """)
            conn.commit()
    except Exception:
        pass  # FTS not available, fall back to LIKE search

    return conn


def extract_keywords(text):
    """Extract meaningful keywords from query text."""
    # Normalize
    text_lower = text.lower()
    # Extract words (3+ chars, not stopwords)
    words = re.findall(r'\b[a-zA-Zа-яА-ЯёЁ]{3,}\b', text_lower)
    keywords = [w for w in words if w not in STOPWORDS]
    # Deduplicate while preserving order
    seen = set()
    unique = []
    for w in keywords:
        if w not in seen:
            seen.add(w)
            unique.append(w)
    return unique


def detect_domain(keywords):
    """Detect likely domain from keywords for boosting."""
    combined = " ".join(keywords)
    scores = {}
    for domain, dkw in DOMAIN_KEYWORDS.items():
        scores[domain] = sum(1 for kw in dkw if kw in combined)
    best = max(scores, key=scores.get) if scores else None
    return best if scores.get(best, 0) > 0 else None


def search_fts(conn, query_text, limit=20):
    """Search using FTS5 full-text search."""
    try:
        # Build FTS query: OR-join keywords
        keywords = extract_keywords(query_text)
        if not keywords:
            return []
        fts_query = " OR ".join(keywords)
        rows = conn.execute("""
            SELECT e.*, rank
            FROM experiences_fts fts
            JOIN experiences e ON e.id = fts.rowid
            WHERE experiences_fts MATCH ?
            ORDER BY rank
            LIMIT ?
        """, (fts_query, limit)).fetchall()
        return [dict(r) for r in rows]
    except Exception:
        return []


def search_like(conn, keywords, domain=None, limit=20):
    """Fallback search using LIKE when FTS is unavailable."""
    if not keywords:
        return []

    # Build LIKE conditions
    conditions = []
    params = []
    for kw in keywords[:10]:  # Limit to 10 keywords
        conditions.append("raw_text LIKE ?")
        params.append(f"%{kw}%")

    where = " OR ".join(conditions)
    if domain:
        where = f"({where}) AND axis_domain = ?"
        params.append(domain)

    rows = conn.execute(f"""
        SELECT * FROM experiences
        WHERE {where}
        ORDER BY ts DESC
        LIMIT ?
    """, params + [limit]).fetchall()
    return [dict(r) for r in rows]


def score_experience(exp, keywords, domain=None):
    """Score an experience for relevance to the query keywords."""
    score = 0.0
    text_lower = exp.get("raw_text", "").lower()
    tags = exp.get("tags", "[]")
    if isinstance(tags, str):
        try:
            tags = json.loads(tags)
        except:
            tags = []

    # Keyword match score
    for i, kw in enumerate(keywords):
        if kw in text_lower:
            # Earlier keywords = higher weight
            score += 10.0 / (i + 1)
        for tag in tags:
            if kw in tag.lower():
                score += 2.0

    # Domain match bonus
    if domain and exp.get("axis_domain") == domain:
        score += 5.0

    # Recency bonus (more recent = slightly higher)
    ts = exp.get("ts", "")
    if ts:
        try:
            from datetime import datetime
            exp_time = datetime.fromisoformat(ts)
            days_ago = (datetime.now() - exp_time).days
            score += max(0, 3.0 - days_ago * 0.05)
        except:
            pass

    # Outcome bonus
    if exp.get("axis_outcome") == "success":
        score += 3.0
    elif exp.get("axis_outcome") == "failure":
        score += 1.0  # Still useful to know about failures

    # Complexity bonus (more detailed = more useful)
    word_count = len(text_lower.split())
    if word_count > 100:
        score += 2.0

    return score


def format_experience(exp, rank=None):
    """Format an experience for context injection."""
    prefix = f"#{rank}" if rank else ""
    domain = exp.get("axis_domain", "?")
    outcome = exp.get("axis_outcome", "?")
    ts = exp.get("ts", "?")[:16]
    text = exp.get("raw_text", "")
    # Truncate long texts
    if len(text) > 500:
        text = text[:500] + "..."

    tags = exp.get("tags", "[]")
    if isinstance(tags, str):
        try:
            tags = json.loads(tags)
        except:
            tags = []
    tag_str = ", ".join(tags[:5]) if tags else ""

    return (
        f"{prefix} [{ts}] domain={domain} outcome={outcome}\n"
        f"   {text}\n"
        f"   tags: {tag_str}"
    )


def auto_recall(query, top_n=5, domain=None):
    """
    Main entry point: search Knowledge Cube and return top relevant experiences.

    Args:
        query: Search query or task description (string)
        top_n: Number of results to return (default 5)
        domain: Optional domain to filter/boost

    Returns:
        dict with 'results' (list of formatted experiences), 'keywords', 'domain'
    """
    conn = get_db()
    keywords = extract_keywords(query)
    detected_domain = domain or detect_domain(keywords)

    # Try FTS first, fallback to LIKE
    results = search_fts(conn, query, limit=top_n * 4)
    if not results:
        results = search_like(conn, keywords, detected_domain, limit=top_n * 4)

    conn.close()

    # Score and rank
    scored = [(score_experience(r, keywords, detected_domain), r) for r in results]
    scored.sort(key=lambda x: x[0], reverse=True)

    # Take top N
    top_results = []
    for i, (score, exp) in enumerate(scored[:top_n]):
        if score > 0:
            top_results.append({
                "formatted": format_experience(exp, i + 1),
                "raw": exp,
                "score": round(score, 2),
            })

    return {
        "results": top_results,
        "keywords": keywords[:10],
        "domain": detected_domain,
        "total_found": len(scored),
    }


def search_lavra_knowledge(query: str, top_n: int = 5) -> list[dict]:
    """Search Lavra knowledge.jsonl by keywords.
    
    Returns list of matching entries with scores.
    """
    if not LAVRA_KNOWLEDGE.exists():
        return []
    
    keywords = extract_keywords(query)
    if not keywords:
        return []
    
    results = []
    
    with open(LAVRA_KNOWLEDGE, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            
            try:
                # Handle double-escaped JSON
                if line.startswith('"') and line.endswith('"'):
                    line = json.loads(line)
                if isinstance(line, str):
                    entry = json.loads(line)
                else:
                    entry = line
            except (json.JSONDecodeError, TypeError):
                continue
            
            content = entry.get("content", "").lower()
            tags = [t.lower() for t in entry.get("tags", [])]
            entry_type = entry.get("type", "unknown")
            
            # Score by keyword overlap
            score = 0
            for kw in keywords:
                if kw in content:
                    score += 2
                if kw in tags:
                    score += 3
                if kw in entry_type:
                    score += 1
            
            if score > 0:
                results.append({
                    "content": entry.get("content", ""),
                    "type": entry_type,
                    "tags": tags,
                    "bead": entry.get("bead", ""),
                    "score": score,
                })
    
    # Sort by score
    results.sort(key=lambda x: x["score"], reverse=True)
    
    return results[:top_n]


def auto_recall_with_lavra(query: str, top_n: int = 5) -> dict:
    """Auto-recall from both Knowledge Cube and Lavra knowledge."""
    # Search Knowledge Cube
    cube_results = auto_recall(query, top_n=top_n)
    
    # Search Lavra knowledge
    lavra_results = search_lavra_knowledge(query, top_n=top_n)
    
    # Merge results
    all_results = []
    
    # Add cube results
    for r in cube_results.get("results", []):
        all_results.append({
            "source": "knowledge_cube",
            "formatted": r["formatted"],
            "score": r["score"],
        })
    
    # Add lavra results
    for r in lavra_results:
        formatted = f"[{r['type'].upper()}] {r['content']}"
        if r['bead']:
            formatted += f"\n  bead: {r['bead']}"
        all_results.append({
            "source": "lavra",
            "formatted": formatted,
            "score": r["score"],
        })
    
    # Sort by score
    all_results.sort(key=lambda x: x["score"], reverse=True)
    
    return {
        "results": all_results[:top_n],
        "keywords": cube_results.get("keywords", []),
        "domain": cube_results.get("domain", "unknown"),
        "cube_found": cube_results.get("total_found", 0),
        "lavra_found": len(lavra_results),
    }


def recall_for_session(query: str, top_n: int = 5) -> dict:
    """Recall relevant context from Knowledge Cube + Lavra for a session.
    
    This is the main entry point for agent integration. Takes a query string
    and returns top-N relevant entries from both sources, merged by score.
    
    Args:
        query: Search query or task description (string)
        top_n: Number of results to return (default 5)
    
    Returns:
        dict with 'results' (list), 'keywords', 'domain', 'total'
    """
    # Use the combined auto_recall_with_lavra function
    combined = auto_recall_with_lavra(query, top_n=top_n)
    
    # Also get scored results from Knowledge Cube directly
    cube = auto_recall(query, top_n=top_n)
    
    # Merge: combine results from both sources, re-sort by score
    all_results = []
    
    # Add cube results with source tag
    for r in cube.get("results", []):
        all_results.append({
            "source": "knowledge_cube",
            "formatted": r["formatted"],
            "score": r["score"],
        })
    
    # Add lavra results from combined search
    for r in combined.get("results", []):
        if r.get("source") == "lavra":
            all_results.append(r)
    
    # Sort by score descending, take top_n
    all_results.sort(key=lambda x: x.get("score", 0), reverse=True)
    
    return {
        "results": all_results[:top_n],
        "keywords": cube.get("keywords", []),
        "domain": cube.get("domain", "unknown"),
        "total": len(all_results),
        "cube_found": cube.get("total_found", 0),
        "lavra_found": combined.get("lavra_found", 0),
    }


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: auto_recall.py <query> [top_n]")
        sys.exit(1)

    query = " ".join(sys.argv[1:-1]) if len(sys.argv) > 2 else sys.argv[1]
    top_n = int(sys.argv[-1]) if len(sys.argv) > 2 and sys.argv[-1].isdigit() else 5

    result = auto_recall(query, top_n=top_n)
    print(f"Keywords: {result['keywords']}")
    print(f"Domain: {result['domain']}")
    print(f"Found: {result['total_found']} experiences, showing top {len(result['results'])}")
    print("---")
    for r in result["results"]:
        print(r["formatted"])
        print(f"   score: {r['score']}")
        print()

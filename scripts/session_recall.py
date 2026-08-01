#!/usr/bin/env python3
"""
Session Recall — Semantic-like search through session history.


> Revisit: when search/indexing algorithm, BM25 scoring, or FTS5 schema changes. Last touched: 2026-07-02.
Pure Python, no external dependencies. Uses TF-IDF + BM25 scoring
with multilingual tokenization.

Usage:
    python session_recall.py "telegram bot error"
    python session_recall.py "knowledge cube growth" --limit 10
    python session_recall.py --context "почини cron"
    python session_recall.py --fts5 "telegram"   # use FTS5 index
"""

import sqlite3
import sys
import json
import os
import re
import math
import signal
from collections import Counter
from pathlib import Path
from typing import List, Dict, Optional, Tuple

# Use unified config — single source of truth for paths
sys.path.insert(0, str(Path(__file__).resolve().parent))
from hermes_config import HERMES_HOME, STATE_DB

# ── Timeout mechanism ──────────────────────────────────────────────────
class SearchTimeout(Exception):
    """Raised when a search exceeds its time budget."""
    pass

def _timeout_handler(signum, frame):
    raise SearchTimeout("Search timed out")

def set_timeout(seconds: int = 10):
    """Set a watchdog timer. Only works on Unix; on Windows falls back to no-op."""
    if os.name != 'nt':
        signal.signal(signal.SIGALRM, _timeout_handler)
        signal.alarm(seconds)

def clear_timeout():
    """Cancel the watchdog timer."""
    if os.name != 'nt':
        signal.alarm(0)


def tokenize(text: str) -> List[str]:
    """Multilingual tokenizer: splits on non-alphanumeric, lowercases."""
    if not text:
        return []
    # Split on non-alphanumeric (preserves cyrillic, latin, digits)
    tokens = re.findall(r'[a-zA-Zа-яА-ЯёЁ0-9]{2,}', text.lower())
    return tokens


class BM25:
    """Okapi BM25 — better than raw TF-IDF for short texts."""

    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.doc_freqs = {}
        self.doc_lens = []
        self.avg_dl = 0
        self.docs = []
        self.n_docs = 0
        # Precomputed per-doc term frequencies (avoids Counter in search loop)
        self._tf_counters: List[Counter] = []

    def fit(self, documents: List[str]):
        """Build index from documents. Precomputes TF counters for fast search."""
        self.docs = documents
        self.n_docs = len(documents)

        # Tokenize all documents (cached for search)
        self.tokenized_docs = [tokenize(doc) for doc in documents]

        # Document lengths
        self.doc_lens = [len(t) for t in self.tokenized_docs]
        self.avg_dl = sum(self.doc_lens) / max(self.n_docs, 1)

        # Document frequency for each term + precomputed TF counters
        self.doc_freqs = {}
        self._tf_counters = []
        for tokens in self.tokenized_docs:
            unique_tokens = set(tokens)
            for token in unique_tokens:
                self.doc_freqs[token] = self.doc_freqs.get(token, 0) + 1
            # Precompute TF counter once — avoids O(n) Counter creation per search
            self._tf_counters.append(Counter(tokens))

    def search(self, query: str, top_k: int = 10) -> List[Tuple[int, float]]:
        """Search and return (doc_index, score) pairs. Uses precomputed TF counters."""
        query_tokens = tokenize(query)
        if not query_tokens:
            return []

        scores = []
        avg_dl = max(self.avg_dl, 1)

        for i in range(self.n_docs):
            score = 0.0
            tf_counter = self._tf_counters[i]
            doc_len = self.doc_lens[i]

            for qt in query_tokens:
                if qt not in self.doc_freqs:
                    continue

                # TF component
                tf = tf_counter.get(qt, 0)
                tf_norm = (tf * (self.k1 + 1)) / (tf + self.k1 * (1 - self.b + self.b * doc_len / avg_dl))

                # IDF component
                df = self.doc_freqs[qt]
                idf = math.log((self.n_docs - df + 0.5) / (df + 0.5) + 1)

                score += tf_norm * idf

            if score > 0:
                scores.append((i, score))

        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:top_k]


# Global BM25 index
_bm25 = None
_messages_cache = None
_index_built_at = 0  # track when index was last built

# ── Tuning knobs ───────────────────────────────────────────────────────
MAX_MESSAGES = 3000       # default row limit (was 5000)
SEARCH_TIMEOUT_SEC = 10   # hard timeout for the full search pipeline


def get_messages(limit: int = MAX_MESSAGES) -> List[tuple]:
    """Get messages from state.db. Uses a shorter query with timeout."""
    conn = sqlite3.connect(str(STATE_DB), timeout=5)
    cur = conn.cursor()
    cur.execute("""
        SELECT id, content, role, timestamp
        FROM messages
        WHERE content IS NOT NULL AND length(content) > 10
        ORDER BY timestamp DESC
        LIMIT ?
    """, (limit,))
    messages = cur.fetchall()
    conn.close()
    return messages


def build_index(messages: List[tuple]) -> BM25:
    """Build BM25 index from messages."""
    bm25 = BM25()
    bm25.fit([m[1] for m in messages])
    return bm25


def semantic_search(query: str, limit: int = 5, timeout_sec: int = SEARCH_TIMEOUT_SEC) -> List[Dict]:
    """Search using BM25 scoring (semantic-like, no external deps).
    
    Includes:
    - Timeout protection (SIGALRM on Unix, no-op on Windows)
    - Precomputed TF counters (avoids per-query Counter rebuild)
    - Reduced default message limit (3000 vs 5000)
    """
    global _bm25, _messages_cache, _index_built_at

    set_timeout(timeout_sec)

    try:
        # Load messages (only if cache is empty)
        if _messages_cache is None:
            _messages_cache = get_messages(limit=MAX_MESSAGES)
            if not _messages_cache:
                return []
            print(f"Indexed {len(_messages_cache)} messages", file=sys.stderr)

        # Build index (only if not yet built)
        if _bm25 is None:
            _bm25 = build_index(_messages_cache)
            _index_built_at = len(_messages_cache)

        # Search
        raw_results = _bm25.search(query, top_k=limit * 3)

        if not raw_results:
            return []

        # Normalize scores
        max_score = raw_results[0][1] if raw_results else 1.0

        results = []
        seen = set()

        for idx, score in raw_results:
            msg = _messages_cache[idx]
            content = msg[1]

            # Deduplicate similar content
            fingerprint = content[:80]
            if fingerprint in seen:
                continue
            seen.add(fingerprint)

            results.append({
                "id": msg[0],
                "content": content[:500],
                "role": msg[2],
                "timestamp": msg[3],
                "score": round(score / max_score, 3)  # normalize to 0-1
            })

            if len(results) >= limit:
                break

        return results

    except SearchTimeout:
        print("[WARN] Search timed out - returning partial results", file=sys.stderr)
        return []
    finally:
        clear_timeout()


def search_fts5(query: str, limit: int = 5) -> List[Dict]:
    """FTS5 keyword search."""
    conn = sqlite3.connect(str(STATE_DB), timeout=5)
    cur = conn.cursor()

    try:
        # Escape special FTS5 characters
        safe_query = re.sub(r'[\"\(\)\*\+]', ' ', query).strip()
        if not safe_query:
            return []

        cur.execute("""
            SELECT m.id, m.content, m.role, m.timestamp
            FROM messages m
            JOIN messages_fts f ON m.id = f.rowid
            WHERE messages_fts MATCH ?
            ORDER BY rank
            LIMIT ?
        """, (safe_query, limit))

        results = []
        for row in cur.fetchall():
            results.append({
                "id": row[0],
                "content": (row[1] or "")[:500],
                "role": row[2],
                "timestamp": row[3],
                "score": 1.0
            })
        return results
    except Exception as e:
        print(f"FTS5 error: {e}", file=sys.stderr)
        return []
    finally:
        conn.close()


def format_context(results: List[Dict], query: str) -> str:
    """Format as context block for agent injection."""
    if not results:
        return f"[No relevant sessions found for: {query}]"

    lines = [f"[Session Recall: \"{query}\"]", ""]

    for i, r in enumerate(results, 1):
        role = "User" if r["role"] == "user" else "Assistant"
        ts = r.get("timestamp", "")
        if ts:
            from datetime import datetime
            try:
                ts = datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M")
            except:
                pass

        # Truncate content for context
        content = r["content"][:300]
        if len(r["content"]) > 300:
            content += "..."

        lines.append(f"--- {i}. [{r['score']:.2f}] {role} ({ts}) ---")
        lines.append(content)
        lines.append("")

    return "\n".join(lines)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Session Recall — semantic search")
    parser.add_argument("query", nargs="?", help="Search query")
    parser.add_argument("--limit", "-n", type=int, default=5, help="Results count")
    parser.add_argument("--context", "-c", action="store_true", help="Context block format")
    parser.add_argument("--json", "-j", action="store_true", help="JSON output")
    parser.add_argument("--fts5", action="store_true", help="Use FTS5 index (faster, keyword only)")
    parser.add_argument("--timeout", "-t", type=int, default=SEARCH_TIMEOUT_SEC,
                        help=f"Search timeout in seconds (default: {SEARCH_TIMEOUT_SEC})")
    args = parser.parse_args()

    if not args.query:
        parser.print_help()
        sys.exit(1)

    # Search
    if args.fts5:
        results = search_fts5(args.query, args.limit)
    else:
        results = semantic_search(args.query, args.limit, timeout_sec=args.timeout)

    # Output
    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    elif args.context:
        print(format_context(results, args.query))
    else:
        for i, r in enumerate(results, 1):
            ts = ""
            if r.get("timestamp"):
                from datetime import datetime
                try:
                    ts = datetime.fromtimestamp(r["timestamp"]).strftime("%m-%d %H:%M")
                except:
                    pass
            preview = r["content"][:120].replace("\n", " ")
            print(f"  {i}. [{r['score']:.2f}] ({ts}) {r['role']}: {preview}")


if __name__ == "__main__":
    main()

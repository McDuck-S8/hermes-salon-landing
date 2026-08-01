"""
OKF Enrichment Worker — web-based knowledge enrichment for OKF Navigator.

Brings the Google knowledge-catalog "Web Pass" pattern to our OKF system:
  1. Fetch all concepts in a domain
  2. For each: web_search based on tags + translated keywords
  3. Classify results as supporting/contradicting
  4. Update confidence: confirmed → +delta, not found → -delta
  5. Record contradictions as conflict entries
  6. Generate enrichment report

Architecture:
  - Web search is DONE VIA DIRECT TOOL CALLS (not hermes_tools which has SSL issues)
  - This module is called with pre-collected search results
  - Or run in terminal mode via 'python okf_enrichment.py <domain>'

Usage:
    # From Python (after collecting search results):
    from okf_enrichment import enrich_domain_with_data, get_domain_concepts
    
    concepts = get_domain_concepts("referral-automation")
    for c in concepts:
        # call web_search externally, pass results to enrich_concept()
        pass
"""

import sys
import json
import re
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Any

SCRIPTS_DIR = Path("D:/Portable_Soft/hermes/scripts")
sys.path.insert(0, str(SCRIPTS_DIR))

import okf_navigator as nav

# ── RUSSIAN → ENGLISH TRANSLATION MAP ──────────────────────────────────────

RU_EN_KEYWORDS: dict[str, str] = {
    "реферальные программы": "referral programs",
    "заработок без вложений": "earn money free no investment",
    "партнёрские программы": "affiliate programs",
    "реферальные ссылки": "referral links",
    "хостинги": "web hosting referral",
    "домены": "domain registrar referral",
    "кешбэк": "cashback",
    "промокоды": "promo codes",
    "доход пассивный": "passive income",
    "пассивный": "passive income",
    "воронки": "sales funnel",
    "цепочки": "multi-level referral",
    "бесплатного продукта": "free product lead magnet",
    "упаковка": "link branding",
    "маркетплейсов": "marketplace affiliate",
    "комиссии": "commission rates",
    "ai-инструментов": "AI tools affiliate",
    "recurring": "recurring commission",
    "рефоводство": "referral marketing",
    "бинанс": "Binance referral",
    "bybit": "Bybit referral",
    "okx": "OKX referral commission",
}

NOISE_TAGS = {"level-1", "level-2", "level-3", "bez-vlozhenij", 
              "arbitrage-traffic", "white-spot", "research"}

# ── HELPERS ─────────────────────────────────────────────────────────────────

def log(msg: str) -> None:
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"  [ENRICH] {ts} {msg}")

def extract_title(content: str) -> str:
    """Extract ## Title from OKF markdown content."""
    for line in content.splitlines():
        s = line.strip()
        if s.startswith("## "):
            return s[3:].strip()
    return content[:60].strip()

# ── DOMAIN CONCEPTS ─────────────────────────────────────────────────────────

def get_domain_concepts(domain: str) -> list[dict[str, Any]]:
    """Get all concepts from kc_entries for a domain."""
    db = nav.get_db()
    rows = db.execute(
        "SELECT id, content, tags, confidence, source, verification_method, category "
        "FROM kc_entries WHERE category = ?",
        (domain,)
    ).fetchall()
    db.close()
    
    concepts = []
    for r in rows:
        content = r["content"] or ""
        title = extract_title(content)
        
        # Parse tags: could be JSON array or comma-separated
        tags_str = r["tags"] or ""
        tags: list[str] = []
        if tags_str.startswith("["):
            try:
                tags = json.loads(tags_str.replace("'", '"'))
            except json.JSONDecodeError:
                pass
        if not tags:
            tags = [t.strip().strip("'\"").strip() 
                    for t in tags_str.replace("[","").replace("]","").split(",") if t.strip()]
        
        concepts.append({
            "id": r["id"],
            "title": title,
            "content": content,
            "tags": tags,
            "source": r["source"] or "",
            "confidence": float(r["confidence"] or 0.5),
            "verification_method": r["verification_method"] or "manual",
            "category": r["category"] or domain,
        })
    
    return concepts

def get_experience_concepts(domain: str) -> list[dict[str, Any]]:
    """Get concepts from experiences table for a domain."""
    db = nav.get_db()
    rows = db.execute(
        "SELECT id, content, tags, confidence, source, verification_method, axis_domain "
        "FROM experiences WHERE axis_domain = ?",
        (domain,)
    ).fetchall()
    db.close()
    
    concepts = []
    for r in rows:
        content = r["content"] or ""
        title = extract_title(content)
        
        tags_str = r["tags"] or ""
        tags: list[str] = []
        try:
            if isinstance(tags_str, str):
                tags = json.loads(tags_str)
        except (json.JSONDecodeError, TypeError):
            tags = []
        
        concepts.append({
            "id": f"exp:{r['id']}",
            "title": title,
            "content": content,
            "tags": tags,
            "source": r["source"] or "",
            "confidence": float(r["confidence"] or 1.0),
            "verification_method": r["verification_method"] or "manual",
            "category": r["axis_domain"] or domain,
        })
    
    return concepts

# ── SEARCH QUERY BUILDER ───────────────────────────────────────────────────

def build_en_query(concept: dict) -> str:
    """Build English search query from a concept (title may be Russian)."""
    title = concept["title"]
    title_lower = title.lower()
    tags = concept["tags"]
    
    en_parts: set[str] = set()
    
    # Check title for Russian keywords
    for ru_phrase, en_phrase in RU_EN_KEYWORDS.items():
        if ru_phrase in title_lower:
            en_parts.add(en_phrase)
    
    # Add English tags (filter out noise and Cyrillic)
    for t in tags:
        t_clean = t.strip()
        if t_clean.lower() in NOISE_TAGS:
            continue
        has_cyrillic = any('\u0400' <= c <= '\u04FF' for c in t_clean)
        if not has_cyrillic and t_clean:
            en_parts.add(t_clean)
    
    # Add year for recency
    en_parts.add("2026")
    
    # Fallback if nothing mapped
    if not en_parts or (len(en_parts) == 1 and "2026" in en_parts):
        domain = concept.get("category", "")
        fallback_map = {
            "referral-automation": "referral program affiliate marketing best",
            "social-media": "social media monetization affiliate marketing",
            "crypto": "cryptocurrency affiliate program",
        }
        en_parts.add(fallback_map.get(domain, f"{domain.replace('-', ' ')} guide 2026"))
    
    return " ".join(en_parts)

# ── ENRICHMENT CLASSIFICATION ──────────────────────────────────────────────

def classify_search_results(web_results: list[dict]) -> dict:
    """
    Classify web search results as supporting, contradicting, or neutral.
    Returns dict with:
      - sources: all sources
      - supporting: confirmed evidence
      - contradicting: evidence against
    """
    sources = []
    supporting = []
    contradicting = []
    
    for r in web_results:
        url = r.get("url", "")
        title_s = r.get("title", "")
        snippet = r.get("description", "")
        
        source = {"url": url, "title": title_s, "snippet": snippet}
        sources.append(source)
        
        text_lower = (snippet + " " + title_s).lower()
        
        contradicting_signals = [
            "scam", "shut down", "closed", "not working",
            "no longer", "terminated", "fraud", "fake",
            "dead", "discontinued", "avoid", "illegal"
        ]
        supporting_signals = [
            "works", "legit", "review", "how to", "guide",
            "earn", "commission", "affiliate program", "payout",
            "benchmark", "rates", "platform", "top", "best",
            "recurring", "sign up", "join", "program"
        ]
        
        is_contradicting = any(s in text_lower for s in contradicting_signals)
        is_supporting = any(s in text_lower for s in supporting_signals)
        
        # Check URL domain quality
        good_domains = [".com", ".io", ".org", ".net", ".global", ".xyz"]
        has_good_domain = any(d in url for d in good_domains)
        
        if is_contradicting and not is_supporting:
            contradicting.append(source)
        elif is_supporting and not is_contradicting:
            supporting.append(source)
    
    return {
        "found": len(sources) > 0,
        "sources": sources,
        "supporting": supporting,
        "contradicting": contradicting,
        "total_web_results": len(web_results),
    }

# ── CONFIDENCE UPDATE ──────────────────────────────────────────────────────

TABLE_UPDATE_SQL = {
    "kc_entries": "UPDATE kc_entries SET confidence = ?, verification_method = 'web-enriched', updated_at = ? WHERE id = ?",
    "experiences": "UPDATE experiences SET confidence = ?, verification_method = 'web-enriched' WHERE id = ?",
}

def update_confidence(concept_id: str, delta: float, reason: str, dry_run: bool = False) -> float | None:
    """Update confidence for a concept. Returns new confidence or None."""
    table = "experiences" if concept_id.startswith("exp:") else "kc_entries"
    real_id = concept_id[4:] if concept_id.startswith("exp:") else concept_id
    
    db = nav.get_db()
    
    if table == "kc_entries":
        row = db.execute("SELECT confidence FROM kc_entries WHERE id = ?", (real_id,)).fetchone()
    else:
        row = db.execute("SELECT confidence FROM experiences WHERE id = ?", (int(real_id),)).fetchone()
    
    if not row:
        db.close()
        return None
    
    current = float(row["confidence"] or 0.5)
    new_conf = max(0.0, min(1.0, current + delta))
    
    if not dry_run:
        now = datetime.now(timezone.utc).isoformat()
        if table == "kc_entries":
            db.execute(TABLE_UPDATE_SQL["kc_entries"], (new_conf, now, real_id))
        else:
            db.execute(TABLE_UPDATE_SQL["experiences"], (new_conf, real_id))
        db.commit()
    
    db.close()
    
    direction = "+" if delta >= 0 else ""
    log(f"  confidence {concept_id[:16]}: {current:.2f} → {new_conf:.2f} ({direction}{delta:.2f}) | {reason[:50]}")
    return new_conf

# ── CONFLICT RECORDING ─────────────────────────────────────────────────────

def record_conflict(concept_id: str, title: str, domain: str,
                    existing_confidence: float, new_confidence: float,
                    contradicting_sources: list[dict], dry_run: bool = False) -> str | None:
    """Record a contradiction as a knowledge entry."""
    if dry_run:
        log(f"  DRY-RUN: would create conflict for {title}")
        return None
    
    sources_text = "\n".join(
        f"- [{s['title']}]({s['url']})" for s in contradicting_sources[:5]
    )
    
    conflict_content = f"""---
type: Conflict
title: "CONFLICT: {title}"
description: Contradictory or unconfirmed information found for domain {domain} entry
tags: [conflict, {domain}]
timestamp: {datetime.now(timezone.utc).isoformat()}
source: web-enrichment
---

## CONFLICT DETECTED: {title}

**Domain:** {domain}
**Original concept:** {concept_id}
**Original confidence:** {existing_confidence:.2f}
**New confidence:** {new_confidence:.2f}
**Delta:** {new_confidence - existing_confidence:+.2f}
**Detected:** {datetime.now(timezone.utc).isoformat()}

### Sources

{sources_text}

### Suggested Action

This concept may be outdated or inaccurate. Web search found contradictory or no supporting information.
Review and either:
1. Update the concept with current data
2. Remove if program no longer exists
3. Mark as verified if sources are erroneous
4. Refine search query for better results
"""
    
    conflicts_dir = Path("D:/Portable_Soft/hermes/knowledge/okf/conflicts")
    conflicts_dir.mkdir(parents=True, exist_ok=True)
    
    slug = re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')[:50] or "unnamed"
    timestamp = datetime.now().strftime("%Y%m%d")
    path = conflicts_dir / f"{timestamp}_{slug}.md"
    
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(conflict_content)
        log(f"  conflict written: {path}")
        return str(path)
    except Exception as e:
        log(f"  conflict failed: {e}")
        return None

# ── SINGLE CONCEPT ENRICHMENT ──────────────────────────────────────────────

def enrich_concept(concept: dict, web_data: dict, dry_run: bool = False) -> dict:
    """
    Enrich a single concept with pre-collected web search data.
    
    Args:
        concept: concept dict from get_domain_concepts()
        web_data: dict with 'web' key containing list of search results
        dry_run: if True, don't write to DB
    
    Returns:
        dict with enrichment result
    """
    result = {
        "id": concept["id"],
        "title": concept["title"],
        "old_confidence": concept["confidence"],
        "new_confidence": concept["confidence"],
        "delta": 0.0,
        "conflict": False,
        "sources_found": 0,
        "status": "skipped",
    }
    
    web_results = web_data.get("web", []) if isinstance(web_data, dict) else []
    
    if not web_results:
        return result
    
    classification = classify_search_results(web_results)
    result["sources_found"] = len(classification["sources"])
    
    # Calculate net delta
    delta = 0.0
    
    if classification["supporting"]:
        delta += min(0.15, len(classification["supporting"]) * 0.05)
    
    if classification["contradicting"]:
        delta -= min(0.2, len(classification["contradicting"]) * 0.07)
    
    # Apply update
    if delta != 0:
        new_conf = update_confidence(concept["id"], delta, 
                                     f"web {'confirmed' if delta > 0 else 'questioned'} "
                                     f"(s={len(classification['supporting'])}, "
                                     f"c={len(classification['contradicting'])})",
                                     dry_run=dry_run)
        if new_conf is not None:
            result["new_confidence"] = new_conf
            result["delta"] = delta
            result["status"] = "updated"
    
    # Record conflicts
    if classification["contradicting"] and delta < 0:
        record_conflict(
            concept["id"], concept["title"], concept["category"],
            concept["confidence"], concept["confidence"] + delta,
            classification["contradicting"],
            dry_run=dry_run
        )
        result["conflict"] = True
    
    # Show sources
    for s in classification["sources"][:2]:
        log(f"    source: {s['title'][:60]}")
    
    return result


# ── ENRICHMENT QUEUE (event-driven, async via file) ────────────────────────

PENDING_FILE = SCRIPTS_DIR.parent / "cache" / "pending_enrichment.json"


def write_enrichment_tasks(domain: str, concepts: list[dict]) -> int:
    """
    Write enrichment tasks to pending queue (called by on_knowledge_added).
    Lightweight — only stores concept metadata + search query.
    Consumer (process_pending_enrichments) handles the actual web_search.
    """
    tasks = []
    for c in concepts:
        query = build_en_query(c)
        tasks.append({
            "id": c["id"],
            "domain": domain,
            "title": c["title"][:100],
            "confidence": c["confidence"],
            "tags": c["tags"][:5] if c.get("tags") else [],
            "query": query,
            "created": datetime.now(timezone.utc).isoformat(),
            "status": "pending",
        })
    
    # Load existing queue, append new, dedupe by id
    PENDING_FILE.parent.mkdir(parents=True, exist_ok=True)
    existing = []
    if PENDING_FILE.exists():
        try:
            existing = json.loads(PENDING_FILE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, Exception):
            existing = []
    
    existing_ids = {t["id"] for t in existing if t.get("status") in ("pending", "in_progress")}
    for t in tasks:
        if t["id"] not in existing_ids:
            existing.append(t)
            existing_ids.add(t["id"])
    
    PENDING_FILE.write_text(json.dumps(existing, indent=2, ensure_ascii=False), encoding="utf-8")
    return len(tasks)


def get_pending_enrichments(domain: str = None, limit: int = 20) -> list[dict]:
    """Read pending enrichments from queue. Optionally filter by domain."""
    if not PENDING_FILE.exists():
        return []
    try:
        tasks = json.loads(PENDING_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, Exception):
        return []
    
    pending = [t for t in tasks if t.get("status") in ("pending", "in_progress")]
    if domain:
        pending = [t for t in pending if t.get("domain") == domain]
    return pending[:limit]


def mark_enrichment_done(task_id: str, delta: float):
    """Mark a pending enrichment as completed with delta."""
    if not PENDING_FILE.exists():
        return
    try:
        tasks = json.loads(PENDING_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, Exception):
        return
    
    for t in tasks:
        if t["id"] == task_id:
            t["status"] = "done"
            t["delta"] = delta
            t["completed"] = datetime.now(timezone.utc).isoformat()
            break
    
    PENDING_FILE.write_text(json.dumps(tasks, indent=2, ensure_ascii=False), encoding="utf-8")


def enrich_next_pending(web_data: dict) -> dict | None:
    """
    Consume the next pending enrichment using provided search results.
    Called by the agent with direct web_search tool results.
    
    Args:
        web_data: dict with 'web' key containing list of search results
    
    Returns:
        dict with enrichment result, or None if queue empty
    """
    pending = get_pending_enrichments(limit=1)
    if not pending:
        return None
    
    task = pending[0]
    
    # Mark in_progress
    tasks = json.loads(PENDING_FILE.read_text(encoding="utf-8"))
    for t in tasks:
        if t["id"] == task["id"]:
            t["status"] = "in_progress"
            break
    PENDING_FILE.write_text(json.dumps(tasks, indent=2, ensure_ascii=False), encoding="utf-8")
    
    # Build concept dict for enrich_concept
    concept = {
        "id": task["id"],
        "title": task["title"],
        "tags": task.get("tags", []),
        "category": task["domain"],
        "confidence": task["confidence"],
        "source": "kc_entries",
    }
    
    # Run enrichment
    result = enrich_concept(concept, web_data)
    
    # Mark done
    mark_enrichment_done(task["id"], result["delta"])
    
    return result


# ── REPORT ──────────────────────────────────────────────────────────────────

def print_summary(results: list[dict], domain: str, duration_sec: float):
    """Print a formatted summary of enrichment results."""
    
    updated = [r for r in results if r["status"] == "updated"]
    conflicts = [r for r in results if r["conflict"]]
    skipped = [r for r in results if r["status"] == "skipped"]
    
    total_delta = sum(r["delta"] for r in results)
    avg_old = sum(r["old_confidence"] for r in results) / len(results) if results else 0
    avg_new = sum(r["new_confidence"] for r in results) / len(results) if results else 0
    
    print(f"""
╔══════════════════════════════════════════════╗
║  OKF Enrichment Report: {domain:<20s} ║
╚══════════════════════════════════════════════╝
  Concepts:     {len(results)}
  Updated:      {len(updated)}
  Conflicts:    {len(conflicts)}
  Skipped:      {len(skipped)}
  Duration:     {duration_sec:.1f}s

  Avg confidence: {avg_old:.3f} → {avg_new:.3f} ({total_delta:+.3f})
""")
    
    if updated:
        print("  ── Updated ──")
        for r in updated:
            icon = "⚠️" if r["conflict"] else "✅"
            print(f"    {icon} {r['title'][:55]:55s} {r['old_confidence']:.2f} → {r['new_confidence']:.2f}")
    
    if conflicts:
        print("\n  ── Conflicts written to knowledge/okf/conflicts/ ──")
        for r in conflicts:
            print(f"    ⚠️  {r['title'][:55]}")


# ── CLI ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="OKF Enrichment Worker")
    parser.add_argument("domain", nargs="?", default="referral-automation",
                       help="Domain/category to enrich")
    parser.add_argument("--dry-run", action="store_true",
                       help="Don't write changes, just preview")
    parser.add_argument("--sources", type=str, default=None,
                       help="JSON file with pre-collected search results")
    
    args = parser.parse_args()
    
    if args.dry_run:
        log(f"DRY RUN — no changes will be written")
    
    concepts = get_domain_concepts(args.domain)
    log(f"Found {len(concepts)} concepts in domain '{args.domain}'")
    
    for i, c in enumerate(concepts):
        log(f"[{i+1}/{len(concepts)}] {c['title'][:50]}...")
        query = build_en_query(c)
        log(f"  would search: {query}")
        if args.dry_run:
            print(f"    → {c['confidence']:.2f} (dry, no change)")
    
    log(f"Dry run complete. Use direct web_search tool to collect results, then run without --dry-run")

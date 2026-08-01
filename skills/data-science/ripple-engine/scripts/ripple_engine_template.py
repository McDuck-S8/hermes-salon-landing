#!/usr/bin/env python
"""
Ripple Engine Analysis Script — reusable template.
Run: python cache/run_ripple_N.py
Output: cache/ripple_keys_N.json
"""
import sqlite3, json, os, sys
from datetime import datetime
from collections import Counter

CONSTRAINTS = [
    "Crimea — geographic/regulatory restrictions",
    "No KYC — cannot use identity-verified platforms",
    "stdlib-first — prefer standard library, minimal deps",
    "no budget — zero-capital strategies only"
]

# --- Customize these per run ---
SOURCES = ('arbitrage-research', 'github-research', 'agent')
DB_PATH = 'cache/knowledge_cube.db'
OUTPUT_PATH = 'D:/Portable_Soft/hermes/cache/ripple_keys_N.json'
HIGH_PRIORITY_ONLY = True  # Only include critical/high suggestions


def analyze_entry(content, source, tags="", importance=0, confidence_db=0):
    """Ripple Engine analysis for one entry. See SKILL.md for full methodology."""
    text = (content or "").lower()
    tag_text = (tags or "").lower()
    full_text = f"{text} {tag_text}"

    # Phase 1: Aspect extraction
    aspects = []
    aspect_map = {
        "automation": "automation", "auto": "automation", "bot": "bot-development",
        "telegram": "telegram-ecosystem", "api": "api-integration",
        "scrape": "web-scraping", "parser": "data-parsing",
        "content": "content-generation", "seo": "seo-optimization",
        "deploy": "deployment", "docker": "containerization",
        "monitor": "monitoring", "cron": "scheduled-automation",
        "llm": "llm-integration", "gpt": "llm-integration", "claude": "llm-integration",
        "crypto": "crypto-finance", "usdt": "crypto-finance",
        "arbitrage": "arbitrage", "cpa": "cpa-affiliate", "affiliate": "cpa-affiliate",
        "traffic": "traffic-acquisition", "landing": "landing-page",
        "free": "zero-cost-strategy", "browser": "browser-automation",
        "github": "open-source-tooling", "python": "python-development",
        "react": "frontend-development", "static": "static-site-generation",
        "git": "version-control", "webhook": "event-driven-architecture",
        "self-heal": "resilience-patterns", "knowledge": "knowledge-management",
        "agent": "agent-architecture", "skill": "skill-system",
        "error": "error-handling", "fail": "error-handling",
        "security": "security", "sqlite": "database",
        "rss": "feed-monitoring", "youtube": "video-content",
        "poster": "social-posting", "social": "social-media",
        "fitness": "fitness", "mcp": "mcp-protocol",
    }
    for kw, tag in aspect_map.items():
        if kw in full_text:
            aspects.append(tag)
    aspects = list(dict.fromkeys(aspects))
    if not aspects:
        aspects = ["general-knowledge"]

    # Phase 2: Constraint conflicts
    conflicts = []
    conflict_checks = {
        "kyc": "No KYC constraint", "identity verif": "No KYC constraint",
        "passport": "No KYC constraint", "credit card": "No budget constraint",
        "subscription": "No budget constraint", "premium tier": "No budget constraint",
        "aws lambda": "stdlib-first: AWS dependency",
        "sanction": "Crimea: sanctions compliance",
        "restricted region": "Crimea: geographic restriction",
    }
    for indicator, conflict in conflict_checks.items():
        if indicator in full_text:
            conflicts.append(conflict)
    if any(w in full_text for w in ["crimea", "simferopol"]):
        conflicts.append("Direct Crimea reference")

    # Phase 3: Gap analysis
    gaps = []
    if not any(w in full_text for w in ["step", "tutorial", "how to", "guide", "example"]):
        gaps.append("Missing actionable steps")
    if not any(w in full_text for w in ["test", "verify", "check", "validate"]):
        gaps.append("No verification methodology")
    if not any(w in full_text for w in ["error", "fail", "pitfall", "debug"]):
        gaps.append("No error handling documented")
    if not any(w in full_text for w in ["cost", "budget", "free", "price"]):
        gaps.append("No cost analysis")
    if not any(w in full_text for w in ["metric", "kpi", "roi", "measure"]):
        gaps.append("No measurable outcomes")
    if len(content or "") < 100:
        gaps.append("Very short content")

    # Phase 4: New keys
    new_keys = []
    key_checks = {
        "open-source-tool-discovery": ["github", "open source"],
        "zero-budget-automation": ["free", "auto"],
        "content-pipeline": ["content", "pipeline"],
        "telegram-monetization": ["telegram", "monetiz"],
        "arbitrage-discovery": ["arbitrage", "gap"],
        "cpa-funnel-building": ["cpa", "affiliate"],
        "llm-integration-patterns": ["llm", "gpt", "claude"],
    }
    for key, kws in key_checks.items():
        if sum(1 for k in kws if k in full_text) >= 2:
            new_keys.append(key)
    if not new_keys:
        new_keys = ["domain-specific-knowledge"]

    # Phase 5: Scoring
    content_len = len(content or "")
    aspect_score = min(40, len(aspects) * 8)
    length_score = min(30, content_len // 20)
    source_bonus = 15 if source in ('arbitrage-research', 'github-research') else 10 if source == 'agent' else 5
    conflict_penalty = min(30, len(conflicts) * 15)
    key_strength = min(100, max(5, aspect_score + length_score + source_bonus - conflict_penalty))

    db_conf = confidence_db if confidence_db else 50
    content_conf = min(25, content_len // 30)
    gap_penalty = min(20, len(gaps) * 5)
    confidence = min(100, max(10, int(db_conf * 0.4 + content_conf - gap_penalty + 20)))

    actionable = len(conflicts) == 0 and len(gaps) < 4

    if any(w in full_text for w in ["arbitrage", "cpa", "monetiz", "revenue", "earn"]):
        roi = "Medium-High: revenue-generating"
    elif any(w in full_text for w in ["automation", "bot", "pipeline"]):
        roi = "Medium: time savings"
    elif any(w in full_text for w in ["knowledge", "memory", "agent"]):
        roi = "Low-Medium: capability building"
    else:
        roi = "Low-Medium: information value"

    summary = (content[:500].strip() if content else "No content") + ("..." if content and len(content) > 500 else "")

    return {
        "title": summary[:120].replace('\n', ' ').strip(),
        "source": source,
        "url": "",
        "content_summary": summary,
        "aspects": aspects,
        "conflicts": conflicts,
        "gaps": gaps,
        "new_keys_generated": new_keys,
        "key_strength": key_strength,
        "roi_estimate": roi,
        "confidence": confidence,
        "actionable": actionable,
        "reason": f"{len(aspects)} aspects, {len(conflicts)} conflicts, {len(gaps)} gaps"
                  + (f" | BLOCKS: {'; '.join(conflicts[:2])}" if conflicts else " | ACTIONABLE"),
    }


def main():
    results = []
    print(f"[1] Reading KC entries from {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    placeholders = ','.join('?' * len(SOURCES))
    cur.execute(f"""
        SELECT id, content, tags, source, category, importance, confidence
        FROM kc_entries WHERE source IN ({placeholders})
    """, SOURCES)
    rows = cur.fetchall()
    print(f"  Found {len(rows)} entries")
    for row in rows:
        entry_id, content, tags, source, category, importance, confidence_db = row
        result = analyze_entry(content, source, tags or "", importance or 0, confidence_db or 0)
        result['kc_id'] = entry_id
        results.append(result)
    conn.close()

    # Improvement suggestions
    sug_path = "cache/improvement_suggestions.json"
    if os.path.exists(sug_path):
        print(f"\n[2] Reading suggestions from {sug_path}")
        with open(sug_path, 'r', encoding='utf-8') as f:
            suggestions = json.load(f).get('suggestions', [])
        if HIGH_PRIORITY_ONLY:
            suggestions = [s for s in suggestions if (s.get('priority', '') or '').lower() in ('critical', 'high')]
        print(f"  Processing {len(suggestions)} suggestions")
        for s in suggestions:
            parts = [s.get(k, '') for k in ['description', 'content', 'text', 'details'] if s.get(k)]
            content = " | ".join(parts) if parts else json.dumps(s)[:1000]
            result = analyze_entry(content, 'improvement-suggestion', s.get('tags', ''))
            result['priority'] = s.get('priority', '')
            results.append(result)

    # Aggregate
    all_aspects = []
    all_conflicts = []
    all_new_keys = []
    for r in results:
        all_aspects.extend(r.get('aspects', []))
        all_conflicts.extend(r.get('conflicts', []))
        all_new_keys.extend(r.get('new_keys_generated', []))

    output = {
        "generated_at": datetime.now().isoformat(),
        "total_entries": len(results),
        "kc_entries_count": len(rows),
        "suggestion_entries_count": len(suggestions) if os.path.exists(sug_path) else 0,
        "actionable_count": sum(1 for r in results if r.get('actionable')),
        "avg_key_strength": round(sum(r['key_strength'] for r in results) / max(len(results), 1), 1),
        "avg_confidence": round(sum(r['confidence'] for r in results) / max(len(results), 1), 1),
        "constraints_checked": CONSTRAINTS,
        "aspect_distribution": dict(Counter(all_aspects).most_common(20)),
        "unique_conflicts": list(set(all_conflicts)),
        "unique_new_keys": sorted(set(all_new_keys)),
        "keys": results,
    }

    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    print(f"\n[SAVED] {OUTPUT_PATH}: {len(results)} entries")


if __name__ == '__main__':
    main()

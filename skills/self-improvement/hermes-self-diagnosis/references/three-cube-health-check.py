#!/usr/bin/env python3
"""
Three-Cube Health Check — Hermes diagnostic.

Queries all three cubes + fabric + session index simultaneously.
Run first in any diagnostic cycle before deeper investigation.

Usage:
    python three-cube-health-check.py
"""

import sys
import os
import sqlite3
import json
from pathlib import Path
from collections import Counter

HERMES_ROOT = Path("D:/Portable_Soft/hermes")
HERMES_HOME = Path.home() / ".hermes"

sep = "=" * 72


def check_entity_cube():
    """Entity Cube: entities, types, relationships."""
    print(sep)
    print("  ENTITY CUBE")
    print(sep)

    sys.path.insert(0, str(HERMES_ROOT / "projects" / "entity-engine"))
    try:
        from entity_engine import get_stats
        s = get_stats()
        print(f"  Entities:       {s['total_entities']}")
        print(f"  Relationships:  {s['total_relationships']}")
        print(f"  Mentions:       {s['total_mentions']}")
        print(f"\n  Type distribution:")
        for t, c in sorted(s["type_distribution"].items(), key=lambda x: -x[1]):
            pct = c / s['total_entities'] * 100
            bar = "■" * (int(pct / 5)) + "□" * (20 - int(pct / 5))
            print(f"    {t:15s}: {c:4d} ({pct:5.1f}%) {bar}")
        print(f"\n  Top entities:")
        for e in s["top_entities"][:5]:
            print(f"    {e['name']:25s} ×{e['mentions']}")
        print(f"\n  Top edges:")
        for edge in s["top_edges"][:5]:
            print(f"    {edge['source']:20s} → {edge['target']:20s} [{edge['type']}]")

        # Health verdict
        type_counts = s["type_distribution"]
        total = s['total_entities']
        dominant = max(type_counts.values()) / total if total else 0
        has_people = type_counts.get("person", 0) > 0
        has_locations = type_counts.get("location", 0) > 0

        verdict = "🟢 HEALTHY" if (dominant < 0.5 and has_people) else \
                  "🟡 IMBALANCED" if dominant < 0.8 else \
                  "🔴 IMBALANCED"
        print(f"\n  Verdict: {verdict}")
        if dominant > 0.5:
            print(f"    Warning: {max(type_counts, key=type_counts.get)} dominates ({dominant:.0%})")
        if not has_people:
            print(f"    Warning: 0 person entities")
        if not has_locations:
            print(f"    Warning: 0 location entities")

        return {"status": verdict, "entities": total, "relationships": s['total_relationships']}
    except Exception as e:
        print(f"  ERROR: {e}")
        return {"status": "🔴 ERROR", "error": str(e)}


def check_fler_cube():
    """Fler Cube: session analysis state."""
    print(sep)
    print("  FLER CUBE")
    print(sep)

    fler_db = HERMES_HOME / "cache" / "fler_engine.db"
    if not fler_db.exists():
        print("  DB NOT FOUND → 0 bytes (never populated)")
        return {"status": "🔴 EMPTY", "error": "DB not found"}
    
    size = fler_db.stat().st_size
    if size == 0:
        print("  DB exists but 0 bytes → never populated")
        print("  Fix: run_fler_analysis.py")
        return {"status": "🔴 EMPTY", "size": 0}

    conn = sqlite3.connect(str(fler_db))
    c = conn.cursor()
    c.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [r[0] for r in c.fetchall()]

    result = {"tables": tables}
    for t in tables:
        c.execute(f"SELECT COUNT(*) FROM {t}")
        cnt = c.fetchone()[0]
        result[f"{t}_count"] = cnt
        print(f"  {t}: {cnt} rows")

    if "sessions" in tables:
        c.execute("SELECT COUNT(*) FROM sessions")
        sc = c.fetchone()[0]
        print(f"\n  Sessions analyzed: {sc}")
        if sc == 0:
            print("  Verdict: 🔴 EMPTY (table exists, 0 data)")
        else:
            c.execute("SELECT * FROM sessions LIMIT 1")
            cols = [desc[0] for desc in c.description]
            numeric_cols = [col for col in cols if col not in ("id", "session_id", "analyzed_at")]
            if numeric_cols:
                avgs = {}
                for col in numeric_cols:
                    try:
                        c.execute(f"SELECT AVG({col}) FROM sessions")
                        avgs[col] = round(c.fetchone()[0], 3)
                    except:
                        pass
                result["avg_metrics"] = avgs
                print(f"  Avgs: {avgs}")
            print("  Verdict: 🟢 POPULATED" if sc > 0 else "  Verdict: 🔴 EMPTY")

    conn.close()
    return result


def check_knowledge_cube():
    """Knowledge Cube: experiences, domains, outcomes."""
    print(sep)
    print("  KNOWLEDGE CUBE")
    print(sep)

    kc_db = HERMES_ROOT / "cache" / "knowledge_cube.db"
    if not kc_db.exists():
        print("  DB NOT FOUND")
        return {"status": "🔴 ERROR"}

    conn = sqlite3.connect(str(kc_db))
    c = conn.cursor()

    # Total
    c.execute("SELECT COUNT(*) FROM experiences")
    total = c.fetchone()[0]
    print(f"  Total entries: {total}")

    # Domains
    c.execute("SELECT axis_domain, COUNT(*) FROM experiences GROUP BY 1 ORDER BY 2 DESC")
    domains = dict(c.fetchall())
    orphan_domains = sum(1 for v in domains.values() if v == 1)
    top_domains = sorted(domains.items(), key=lambda x: -x[1])[:10]
    print(f"  Domains: {len(domains)} ({orphan_domains} with 1 entry)")
    for d, cnt in top_domains:
        pct = cnt / total * 100
        bar = "■" * (int(pct / 2)) + "□" * (20 - int(pct / 2))
        print(f"    {d:20s}: {cnt:4d} ({pct:5.1f}%) {bar}")

    # Outcomes
    c.execute("SELECT axis_outcome, COUNT(*) FROM experiences GROUP BY 1 ORDER BY 2 DESC")
    outcomes = dict(c.fetchall())
    print(f"\n  Outcomes:")
    unknown_pct = outcomes.get("unknown", 0) / total * 100
    failure_pct = outcomes.get("failure", 0) / total * 100
    success_pct = outcomes.get("success", 0) / total * 100
    for o, cnt in sorted(outcomes.items(), key=lambda x: -x[1]):
        print(f"    {o or 'NULL':15s}: {cnt} ({cnt/total*100:.1f}%)")
    print(f"\n    Unknown rate: {unknown_pct:.1f}%  {'🔴 HIGH' if unknown_pct > 30 else '🟡 OK' if unknown_pct > 15 else '🟢 LOW'}")
    print(f"    Failure rate: {failure_pct:.1f}%  {'🔴 HIGH' if failure_pct > 30 else '🟡 OK' if failure_pct > 15 else '🟢 LOW'}")
    print(f"    Success rate: {success_pct:.1f}%  {'🟢 GOOD' if success_pct > 20 else '🟡 OK' if success_pct > 10 else '🔴 LOW'}")

    # White spots
    c.execute("SELECT COUNT(*) FROM experiences WHERE is_white_spot = 1")
    ws = c.fetchone()[0]
    print(f"\n  White spots: {ws}")

    # Sources
    c.execute("SELECT source, COUNT(*) FROM experiences GROUP BY 1 ORDER BY 2 DESC LIMIT 5")
    sources = c.fetchall()
    print(f"  Top sources: {[s[0] for s in sources]}")

    conn.close()

    verdict = "🟢 HEALTHY" if (unknown_pct < 20 and success_pct > 15) else \
              "🟡 DEGRADED" if (unknown_pct < 40) else \
              "🔴 UNHEALTHY"
    print(f"\n  Verdict: {verdict}")
    return {"status": verdict, "total": total, "domains": len(domains),
            "unknown_pct": unknown_pct, "success_pct": success_pct}


def main():
    print(sep)
    print("  HERMES THREE-CUBE HEALTH CHECK")
    print("  " + str(Path.cwd()))
    print(sep)

    ec = check_entity_cube()
    fc = check_fler_cube()
    kc = check_knowledge_cube()

    print(sep)
    print("  SUMMARY")
    print(sep)
    print(f"  Entity Cube:    {ec.get('status', 'ERROR')}")
    print(f"  Fler Cube:      {fc.get('status', 'ERROR')}")
    print(f"  Knowledge Cube: {kc.get('status', 'ERROR')}")
    print(sep)
    print("  Note: fabric_report() and session_search() must be called separately")
    print("  as they are tool-gated.")
    print(sep)


if __name__ == "__main__":
    main()

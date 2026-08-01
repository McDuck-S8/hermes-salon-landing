#!/usr/bin/env python3
"""
System Metrics Collector — tracks Knowledge Cube, verified fixes, and cron health.
Outputs metrics to cache/system_metrics.json and prints a health score.
If score drops >10 points from last check, prints a warning.
"""

import json
import os
import re
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

HERMES = Path(os.environ.get("HERMES_HOME", str(Path(__file__).resolve().parent.parent)))

# Database paths
KB_DB = HERMES / "cache" / "knowledge_cube.db"
FIX_DB = HERMES / "cache" / "verified_fixes.db"
METRICS_FILE = HERMES / "cache" / "system_metrics.json"
CRON_OUTPUT = HERMES / "cron" / "output"


def count_knowledge_cube():
    """Count entries and domains in knowledge_cube.db"""
    if not KB_DB.exists():
        return {"entries": 0, "domains": 0, "domain_list": []}
    
    conn = sqlite3.connect(str(KB_DB))
    c = conn.cursor()
    
    # Total entries
    c.execute("SELECT COUNT(*) FROM experiences")
    entries = c.fetchone()[0]
    
    # Unique domains
    c.execute("SELECT DISTINCT axis_domain FROM experiences WHERE axis_domain IS NOT NULL AND axis_domain != ''")
    domains = [r[0] for r in c.fetchall()]
    
    conn.close()
    return {"entries": entries, "domains": len(domains), "domain_list": domains}


def count_verified_fixes():
    """Count verified fixes and calculate success rate"""
    if not FIX_DB.exists():
        return {"total_fixes": 0, "fix_types": {}, "success_rate": 0.0}
    
    conn = sqlite3.connect(str(FIX_DB))
    c = conn.cursor()
    
    # Total fixes
    c.execute("SELECT COUNT(*) FROM verified_fixes")
    total = c.fetchone()[0]
    
    # By fix type
    c.execute("SELECT fix_type, COUNT(*) FROM verified_fixes GROUP BY fix_type")
    fix_types = {r[0]: r[1] for r in c.fetchall()}
    
    # Success rate (simplified: any fix that exists is "verified")
    # We count entries where verified_at is not null as successful
    c.execute("SELECT COUNT(*) FROM verified_fixes WHERE verified_at IS NOT NULL AND verified_at != ''")
    verified = c.fetchone()[0]
    success_rate = (verified / total * 100) if total > 0 else 0.0
    
    conn.close()
    return {"total_fixes": total, "fix_types": fix_types, "success_rate": round(success_rate, 1)}


def count_cron_runs():
    """Count cron job runs by parsing cron/output/*.md files"""
    if not CRON_OUTPUT.exists():
        return {"total_runs": 0, "success": 0, "failed": 0, "silent": 0, "success_rate": 0.0}
    
    total = 0
    success = 0
    failed = 0
    silent = 0
    
    # Regex to match timestamped md files
    file_pattern = re.compile(r"\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}\.md$")
    status_pattern = re.compile(r"\*\*Status:\*\*\s*(.+)")
    
    for job_dir in CRON_OUTPUT.iterdir():
        if not job_dir.is_dir():
            continue
        for md_file in job_dir.glob("*.md"):
            if not file_pattern.search(md_file.name):
                continue
            
            total += 1
            
            # Read the file to check status
            try:
                content = md_file.read_text(encoding="utf-8", errors="replace")
                # Check first 20 lines for status
                head = "\n".join(content.splitlines()[:20])
                status_match = status_pattern.search(head)
                
                if status_match:
                    status_text = status_match.group(1).strip().lower()
                    if "script failed" in status_text or "error" in status_text:
                        failed += 1
                    elif "silent" in status_text or "empty output" in status_text:
                        silent += 1
                    else:
                        success += 1
                else:
                    # No status line = successful run
                    success += 1
            except Exception:
                failed += 1
    
    success_rate = (success / total * 100) if total > 0 else 0.0
    return {
        "total_runs": total,
        "success": success,
        "failed": failed,
        "silent": silent,
        "success_rate": round(success_rate, 1),
    }


def calculate_health_score(kb, fixes, cron):
    """
    Calculate system health score (0-100).
    
    Components:
    - Knowledge Cube richness (0-30): more entries + domains = better
    - Verified fixes (0-30): more verified fixes = better
    - Cron reliability (0-40): higher success rate = better
    """
    score = 0.0
    
    # Knowledge Cube: 0-30
    # 100+ entries and 10+ domains = full score
    kb_entries_score = min(kb["entries"] / 100, 1.0) * 15
    kb_domains_score = min(kb["domains"] / 10, 1.0) * 15
    score += kb_entries_score + kb_domains_score
    
    # Verified Fixes: 0-30
    # 50+ fixes = full score for count, success_rate contributes
    fix_count_score = min(fixes["total_fixes"] / 50, 1.0) * 15
    fix_rate_score = (fixes["success_rate"] / 100) * 15
    score += fix_count_score + fix_rate_score
    
    # Cron reliability: 0-40
    # Success rate directly maps
    score += (cron["success_rate"] / 100) * 40
    
    return round(min(score, 100), 1)


def load_previous_score():
    """Load previous health score from metrics file"""
    if not METRICS_FILE.exists():
        return None
    
    try:
        with open(METRICS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list) and len(data) > 0:
            return data[-1].get("health_score")
    except Exception:
        pass
    return None


def save_metrics(metrics):
    """Append metrics to the JSON array file"""
    METRICS_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    # Load existing
    existing = []
    if METRICS_FILE.exists():
        try:
            with open(METRICS_FILE, "r", encoding="utf-8") as f:
                existing = json.load(f)
        except Exception:
            existing = []
    
    existing.append(metrics)
    
    # Keep last 500 entries max to prevent file bloat
    if len(existing) > 500:
        existing = existing[-500:]
    
    with open(METRICS_FILE, "w", encoding="utf-8") as f:
        json.dump(existing, f, indent=2, ensure_ascii=False)


def main():
    now = datetime.now(timezone.utc).isoformat()
    
    # Collect metrics
    kb = count_knowledge_cube()
    fixes = count_verified_fixes()
    cron = count_cron_runs()
    health_score = calculate_health_score(kb, fixes, cron)
    
    # Build metrics record
    metrics = {
        "timestamp": now,
        "health_score": health_score,
        "knowledge_cube": kb,
        "verified_fixes": fixes,
        "cron_runs": cron,
    }
    
    # Check for score drop
    prev_score = load_previous_score()
    if prev_score is not None:
        drop = prev_score - health_score
        if drop > 10:
            print(f"[WARNING] Health score dropped {drop:.1f} points! {prev_score} -> {health_score}")
    
    # Save
    save_metrics(metrics)
    
    # Print summary
    print(f"=== System Health Report ===")
    print(f"Time:               {now}")
    print(f"Health Score:       {health_score}/100")
    print()
    print(f"Knowledge Cube:")
    print(f"  Entries:          {kb['entries']}")
    print(f"  Domains:          {kb['domains']}")
    if kb["domain_list"]:
        print(f"  Domain list:      {', '.join(kb['domain_list'][:10])}")
    print()
    print(f"Verified Fixes:")
    print(f"  Total:            {fixes['total_fixes']}")
    print(f"  Success Rate:     {fixes['success_rate']}%")
    if fixes["fix_types"]:
        print(f"  By Type:          {fixes['fix_types']}")
    print()
    print(f"Cron Jobs:")
    print(f"  Total Runs:       {cron['total_runs']}")
    print(f"  Success:          {cron['success']}")
    print(f"  Failed:           {cron['failed']}")
    print(f"  Silent:           {cron['silent']}")
    print(f"  Success Rate:     {cron['success_rate']}%")
    
    if prev_score is not None:
        diff = health_score - prev_score
        if diff > 0:
            print(f"\nScore trend: +{diff:.1f} from last check")
        elif diff < 0:
            print(f"\nScore trend: {diff:.1f} from last check")
        else:
            print(f"\nScore trend: unchanged")


if __name__ == "__main__":
    main()

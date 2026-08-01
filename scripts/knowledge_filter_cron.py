#!/usr/bin/env python3
"""
Knowledge Filter Cron Job — runs knowledge filter on latest RSS/YouTube cache.
"""

import json
import sys
from pathlib import Path

# Add scripts path
sys.path.insert(0, "D:/Portable_Soft/hermes/scripts")

from skills.automation.knowledge_filter.scripts.filter import KnowledgeFilter

CACHE_DIR = Path("D:/Portable_Soft/hermes/cache")

def main():
    # Heartbeat: module alive
    try:
        from chain_heartbeat import beat
        beat("knowledge_filter_cron")
    except ImportError:
        pass

    print("=== Knowledge Filter Cron Job ===")
    
    filter = KnowledgeFilter()
    total_passed = 0
    total_rejected = 0
    
    # ─── Process RSS cache ───
    rss_cache = CACHE_DIR / "rss_monitor" / "latest.json"
    if rss_cache.exists():
        print(f"\n📰 Processing RSS cache...")
        with open(rss_cache) as f:
            data = json.load(f)
        
        articles = []
        for feed_id, entries in data.get("feeds", {}).items():
            for e in entries:
                articles.append({
                    "title": e.get("title", ""),
                    "url": e.get("url", ""),
                    "source": f"rss_{feed_id}",
                    "content": e.get("summary", "")[:2000],
                    "extra": {"tags": e.get("tags", []), "topic": e.get("topic", "")}
                })
        
        print(f"  Found {len(articles)} articles")
        results = filter.filter_batch(articles)
        passed = sum(1 for r in results if r.passed)
        rejected = len(results) - passed
        total_passed += passed
        total_rejected += rejected
        print(f"  RSS: {passed} passed, {rejected} rejected")
    else:
        print("RSS cache not found")
    
    # ─── Process YouTube cache ───
    yt_cache = CACHE_DIR / "youtube_watch" / "latest.json"
    if yt_cache.exists():
        print(f"\n📺 Processing YouTube cache...")
        with open(yt_cache) as f:
            data = json.load(f)
        
        articles = []
        for ch_id, ch_data in data.get("channels", {}).items():
            for v in ch_data.get("videos", []):
                articles.append({
                    "title": v.get("title", ""),
                    "url": v.get("url", ""),
                    "source": f"youtube_{ch_id}",
                    "content": f"Title: {v.get('title', '')}\nDuration: {v.get('duration', '')}\nChannel: {ch_id}",
                    "extra": {"channel": ch_id, "topic": ch_data.get("topic", "")}
                })
        
        print(f"  Found {len(articles)} videos")
        results = filter.filter_batch(articles)
        passed = sum(1 for r in results if r.passed)
        rejected = len(results) - passed
        total_passed += passed
        total_rejected += rejected
        print(f"  YouTube: {passed} passed, {rejected} rejected")
    else:
        print("YouTube cache not found")
    
    print(f"\n=== TOTAL ===")
    print(f"Passed: {total_passed} | Rejected: {total_rejected}")
    
    # Report KC stats
    try:
        import sqlite3
        conn = sqlite3.connect("D:/Portable_Soft/hermes/cache/knowledge_cube.db")
        c = conn.cursor()
        c.execute('SELECT source, COUNT(*) FROM kc_entries GROUP BY source ORDER BY COUNT(*) DESC')
        print("\n=== KC Sources ===")
        for row in c.fetchall():
            print(f"  {row[0]}: {row[1]}")
        conn.close()
    except Exception as e:
        print(f"Stats error: {e}")

if __name__ == "__main__":
    main()
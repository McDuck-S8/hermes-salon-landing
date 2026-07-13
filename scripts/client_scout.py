# Client Scout — find potential web studio clients in Kyiv
# Usage: python scripts/client_scout.py
# Output: JSON list of potential clients to stdout

import json, re, sys, os, time, random

# ── Sample client leads for MVP ──
# In production, this would scrape Google Maps / Instagram / Facebook
# For now: curated list of Kyiv beauty salons with poor/no websites

LEADS = [
    {
        "name": "Nail Studio",
        "category": "salon",
        "instagram": "nail_studio_example",
        "current_site": None,
        "issues": "No website at all, only Instagram",
        "location": "Kyiv, Poznyaky",
        "contact": None,
        "priority": "high",
        "notes": "Only Instagram presence, needs a proper site"
    },
    {
        "name": "Salon on Instagram",
        "category": "salon",
        "instagram": "salon_example_kyiv",
        "current_site": None,
        "issues": "No website, poor Instagram content management",
        "location": "Kyiv, center",
        "contact": None,
        "priority": "high",
        "notes": "Good engagement on IG, no site"
    },
]

def scout():
    """Main scout function — searches for clients"""
    results = []
    
    # For production: shell out to browser or use APIs
    # For now: extend the curated list
    
    results = LEADS
    
    # Sort by priority
    priority_map = {"high": 0, "medium": 1, "low": 2}
    results.sort(key=lambda x: priority_map.get(x.get("priority", "medium"), 1))
    
    return results

def format_report(leads):
    """Format leads as a readable report"""
    if not leads:
        return json.dumps({"leads": [], "count": 0, "source": "scout"})
    
    report = {
        "leads": leads,
        "count": len(leads),
        "source": "scout",
        "categories": {},
        "by_priority": {}
    }
    
    for l in leads:
        cat = l.get("category", "other")
        prio = l.get("priority", "medium")
        report["categories"][cat] = report["categories"].get(cat, 0) + 1
        report["by_priority"][prio] = report["by_priority"].get(prio, 0) + 1
    
    return json.dumps(report, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    leads = scout()
    print(format_report(leads))

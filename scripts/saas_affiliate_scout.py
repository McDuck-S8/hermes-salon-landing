#!/usr/bin/env python3
"""
SaaS Affiliate Scout — Finds SaaS companies with best referral programs.
Criteria: recurring commission %, cookie duration, minimum payout.
"""

import json
import urllib.request
import urllib.parse
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

HERMES_HOME = Path(__file__).resolve().parent.parent.parent.parent
DATA_DIR = HERMES_HOME / "skills" / "arbitrage-execution" / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Curated list of known SaaS affiliate programs (since we can't scrape dynamically)
SAAS_PROGRAMS = [
    {
        "name": "ConvertKit",
        "url": "https://convertkit.com/affiliates",
        "category": "Email Marketing",
        "commission_rate": 30,
        "commission_type": "recurring",
        "cookie_days": 30,
        "min_payout": 50,
        "payment_frequency": "monthly",
        "tier": "premium"
    },
    {
        "name": "ActiveCampaign",
        "url": "https://www.activecampaign.com/affiliate",
        "category": "Email Marketing/CRM",
        "commission_rate": 20,
        "commission_type": "recurring",
        "cookie_days": 90,
        "min_payout": 50,
        "payment_frequency": "monthly",
        "tier": "premium"
    },
    {
        "name": "ClickFunnels",
        "url": "https://clickfunnels.com/affiliates",
        "category": "Sales Funnels",
        "commission_rate": 40,
        "commission_type": "recurring",
        "cookie_days": 45,
        "min_payout": 100,
        "payment_frequency": "monthly",
        "tier": "premium"
    },
    {
        "name": "Kajabi",
        "url": "https://kajabi.com/affiliates",
        "category": "Course Platform",
        "commission_rate": 30,
        "commission_type": "recurring",
        "cookie_days": 30,
        "min_payout": 50,
        "payment_frequency": "monthly",
        "tier": "premium"
    },
    {
        "name": "Teachable",
        "url": "https://teachable.com/affiliates",
        "category": "Course Platform",
        "commission_rate": 30,
        "commission_type": "recurring",
        "cookie_days": 90,
        "min_payout": 50,
        "payment_frequency": "monthly",
        "tier": "premium"
    },
    {
        "name": "Thinkific",
        "url": "https://www.thinkific.com/affiliates",
        "category": "Course Platform",
        "commission_rate": 20,
        "commission_type": "recurring",
        "cookie_days": 90,
        "min_payout": 50,
        "payment_frequency": "monthly",
        "tier": "standard"
    },
    {
        "name": "Shopify",
        "url": "https://www.shopify.com/affiliates",
        "category": "E-commerce",
        "commission_rate": 20,
        "commission_type": "recurring",
        "cookie_days": 30,
        "min_payout": 10,
        "payment_frequency": "monthly",
        "tier": "standard"
    },
    {
        "name": "BigCommerce",
        "url": "https://www.bigcommerce.com/affiliates",
        "category": "E-commerce",
        "commission_rate": 200,
        "commission_type": "one-time",
        "cookie_days": 90,
        "min_payout": 50,
        "payment_frequency": "monthly",
        "tier": "standard"
    },
    {
        "name": "SEMrush",
        "url": "https://www.semrush.com/affiliate/",
        "category": "SEO Tools",
        "commission_rate": 40,
        "commission_type": "recurring",
        "cookie_days": 120,
        "min_payout": 50,
        "payment_frequency": "monthly",
        "tier": "premium"
    },
    {
        "name": "Ahrefs",
        "url": "https://ahrefs.com/affiliate",
        "category": "SEO Tools",
        "commission_rate": 20,
        "commission_type": "recurring",
        "cookie_days": 30,
        "min_payout": 50,
        "payment_frequency": "monthly",
        "tier": "standard"
    },
    {
        "name": "Mangools",
        "url": "https://mangools.com/affiliate",
        "category": "SEO Tools",
        "commission_rate": 30,
        "commission_type": "recurring",
        "cookie_days": 30,
        "min_payout": 50,
        "payment_frequency": "monthly",
        "tier": "standard"
    },
    {
        "name": "Hotjar",
        "url": "https://www.hotjar.com/affiliates",
        "category": "Analytics",
        "commission_rate": 20,
        "commission_type": "recurring",
        "cookie_days": 90,
        "min_payout": 50,
        "payment_frequency": "monthly",
        "tier": "standard"
    },
    {
        "name": "Mixpanel",
        "url": "https://mixpanel.com/partners/affiliate",
        "category": "Analytics",
        "commission_rate": 25,
        "commission_type": "recurring",
        "cookie_days": 90,
        "min_payout": 50,
        "payment_frequency": "monthly",
        "tier": "standard"
    },
    {
        "name": "Intercom",
        "url": "https://www.intercom.com/affiliates",
        "category": "Customer Support",
        "commission_rate": 15,
        "commission_type": "recurring",
        "cookie_days": 90,
        "min_payout": 50,
        "payment_frequency": "monthly",
        "tier": "standard"
    },
    {
        "name": "Freshworks",
        "url": "https://www.freshworks.com/affiliates",
        "category": "Customer Support/CRM",
        "commission_rate": 20,
        "commission_type": "recurring",
        "cookie_days": 90,
        "min_payout": 50,
        "payment_frequency": "monthly",
        "tier": "standard"
    },
    {
        "name": "PipeDrive",
        "url": "https://www.pipedrive.com/en/affiliate",
        "category": "CRM",
        "commission_rate": 20,
        "commission_type": "recurring",
        "cookie_days": 90,
        "min_payout": 50,
        "payment_frequency": "monthly",
        "tier": "standard"
    },
    {
        "name": "HubSpot",
        "url": "https://www.hubspot.com/affiliates",
        "category": "CRM/Marketing",
        "commission_rate": 30,
        "commission_type": "recurring",
        "cookie_days": 90,
        "min_payout": 50,
        "payment_frequency": "monthly",
        "tier": "premium"
    },
    {
        "name": "Monday.com",
        "url": "https://monday.com/affiliate",
        "category": "Project Management",
        "commission_rate": 20,
        "commission_type": "recurring",
        "cookie_days": 90,
        "min_payout": 50,
        "payment_frequency": "monthly",
        "tier": "standard"
    },
    {
        "name": "Notion",
        "url": "https://www.notion.so/affiliates",
        "category": "Productivity",
        "commission_rate": 50,
        "commission_type": "one-time",
        "cookie_days": 30,
        "min_payout": 10,
        "payment_frequency": "monthly",
        "tier": "standard"
    },
    {
        "name": "Airtable",
        "url": "https://airtable.com/affiliates",
        "category": "Productivity/Database",
        "commission_rate": 10,
        "commission_type": "recurring",
        "cookie_days": 30,
        "min_payout": 50,
        "payment_frequency": "monthly",
        "tier": "standard"
    }
]

def score_program(program: Dict) -> float:
    """Score a program based on our criteria."""
    score = 0
    
    # Recurring commission bonus
    if program["commission_type"] == "recurring":
        score += program["commission_rate"] * 2
    else:
        score += program["commission_rate"] * 0.5
    
    # Cookie duration bonus
    score += min(program["cookie_days"], 120) * 0.5
    
    # Low min payout bonus
    if program["min_payout"] <= 10:
        score += 20
    elif program["min_payout"] <= 50:
        score += 10
    elif program["min_payout"] <= 100:
        score += 5
    
    # Premium tier bonus
    if program["tier"] == "premium":
        score += 15
    
    return round(score, 1)

def filter_programs(programs: List[Dict], min_recurring: float = 20, min_cookie: int = 30, max_min_payout: int = 50) -> List[Dict]:
    """Filter programs by criteria."""
    filtered = []
    for p in programs:
        if p["commission_type"] == "recurring" and p["commission_rate"] >= min_recurring:
            if p["cookie_days"] >= min_cookie:
                if p["min_payout"] <= max_min_payout:
                    filtered.append(p)
    return filtered

def main():
    print("[SAAS_SCOUT] Starting SaaS affiliate program reconnaissance...")
    
    # Filter by criteria
    filtered = filter_programs(SAAS_PROGRAMS)
    print(f"[SAAS_SCOUT] Found {len(filtered)} programs meeting criteria (recurring>20%, cookie>30d, min_payout<$50)")
    
    # Score all programs
    for p in SAAS_PROGRAMS:
        p["score"] = score_program(p)
    
    # Sort by score
    SAAS_PROGRAMS.sort(key=lambda x: x["score"], reverse=True)
    filtered.sort(key=lambda x: x["score"], reverse=True)
    
    # Top 10 overall
    top_10 = SAAS_PROGRAMS[:10]
    
    # Prepare results
    results = {
        "scanned_at": datetime.now().isoformat(),
        "total_programs": len(SAAS_PROGRAMS),
        "filtered_count": len(filtered),
        "criteria": {
            "min_recurring_commission": 20,
            "min_cookie_days": 30,
            "max_min_payout": 50
        },
        "top_10_overall": top_10,
        "top_10_filtered": filtered[:10],
        "by_category": {}
    }
    
    # Group by category
    for p in SAAS_PROGRAMS:
        cat = p["category"]
        if cat not in results["by_category"]:
            results["by_category"][cat] = []
        results["by_category"][cat].append(p)
    
    # Save
    output_file = DATA_DIR / "saas_affiliates.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    # Also save filtered only
    filtered_file = DATA_DIR / "saas_affiliates_filtered.json"
    with open(filtered_file, "w", encoding="utf-8") as f:
        json.dump(filtered, f, indent=2, ensure_ascii=False)
    
    print(f"[SAAS_SCOUT] Results saved to {output_file}")
    print(f"[SAAS_SCOUT] Top 10 programs:")
    for i, p in enumerate(top_10, 1):
        print(f"  {i}. {p['name']} ({p['category']}) - {p['commission_rate']}% {p['commission_type']}, {p['cookie_days']}d cookie, ${p['min_payout']} min, Score: {p['score']}")
    
    return {
        "success": True,
        "data": results,
        "message": f"Found {len(SAAS_PROGRAMS)} programs, {len(filtered)} meet criteria"
    }

if __name__ == "__main__":
    result = main()
    print(json.dumps(result, ensure_ascii=False, indent=2))
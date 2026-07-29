"""client_scout.py — Find potential web studio clients in Kyiv
Outputs JSON array of leads with name, category, instagram, site, issues, location, contact.
"""

import json, sys
from pathlib import Path

LEADS_FILE = Path(__file__).resolve().parent.parent / "kyiv_potential_clients.json"

def scout():
    """Return list of leads from the curated leads file."""
    if LEADS_FILE.exists():
        with open(LEADS_FILE, encoding="utf-8") as f:
            return json.load(f)
    return []

def hot_leads():
    """Return leads sorted by urgency (no site / broken site first)."""
    all_leads = scout()
    def urgency(l):
        score = 0
        if not l.get("current_site"): score += 3
        elif "сломан" in (l.get("issues") or "").lower(): score += 4
        elif "только" in (l.get("current_site") or ""): score += 2
        if l.get("instagram") and "direct" in (l.get("contact") or "").lower(): score += 1
        return -score
    return sorted(all_leads, key=urgency)

def summary():
    leads = scout()
    if not leads:
        return "No leads found."
    lines = [f"Found {len(leads)} leads:"]
    for l in hot_leads():
        site = l.get("current_site") or "❌ No site"
        lines.append(f"  [{l['category']}] {l['name']} — {l.get('instagram','-')} — {l['location']} — {site[:50]}")
    return "\n".join(lines)

if __name__ == "__main__":
    if "--hot" in sys.argv:
        print(json.dumps(hot_leads(), ensure_ascii=False, indent=2))
    elif "--summary" in sys.argv:
        print(summary())
    else:
        print(json.dumps(scout(), ensure_ascii=False, indent=2))

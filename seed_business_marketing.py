#!/usr/bin/env python3
"""
Seed 3 initial Knowledge Cube entries for 'business-marketing' domain.
"""
import sqlite3, json, hashlib, time
from datetime import datetime

DB = "cache/knowledge_cube.db"

# The 3 most relevant business/marketing skills identified from skill_index:
# 1. earning-with-ai    - earning/monetization with AI
# 2. telegram-service-bot - service business bots (tag: service-business)
# 3. trend-scout         - business trend scouting

entries = [
    {
        "skill_name": "earning-with-ai",
        "raw_text": "Skill: earning-with-ai — Comprehensive guide to earning money with AI skills. Covers freelance platforms, local business opportunities, crypto payments, and region-specific strategies (Russia/Crimea). Category: finance. This skill teaches how to monetize AI capabilities across multiple channels.",
        "tags": json.dumps(["business-marketing", "seed", "earning-with-ai", "monetization", "finance"]),
    },
    {
        "skill_name": "telegram-service-bot",
        "raw_text": "Skill: telegram-service-bot — Build Telegram booking bots for service businesses (salons, clinics, studios). Multi-role architecture (client/master/admin), calendar with time slots, SQLite backend. Tagged with 'service-business', 'booking', 'salon'. Category: web-development. This skill enables automated client booking for service-based businesses, a key marketing and customer acquisition tool.",
        "tags": json.dumps(["business-marketing", "seed", "telegram-service-bot", "service-business", "audience"]),
    },
    {
        "skill_name": "trend-scout",
        "raw_text": "Skill: trend-scout — Search web for emerging trends in AI, automation, and beauty salon tech. Analyze relevance for Telegram channels and business. Category: trend-scout. This skill supports business marketing by identifying emerging trends to inform content strategy, service offerings, and competitive positioning.",
        "tags": json.dumps(["business-marketing", "seed", "trend-scout", "audience", "marketing"]),
    },
]

def main():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    # Check existing count
    cur.execute("SELECT COUNT(*) FROM experiences WHERE axis_domain=?", ('business-marketing',))
    before = cur.fetchone()[0]
    print(f"Existing business-marketing entries before: {before}")

    now = datetime.utcnow().isoformat() + "Z"
    inserted = 0
    for e in entries:
        raw = e["raw_text"]
        h = hashlib.sha256(raw.encode()).hexdigest()[:16]
        cur.execute("""
            INSERT INTO experiences 
                (ts, raw_text, hash, axis_domain, axis_outcome, source, confidence, tags)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            now,
            raw,
            h,
            'business-marketing',
            'indexed',
            'agent-seed',
            0.8,
            e["tags"]
        ))
        inserted += 1
        print(f"  Inserted entry for '{e['skill_name']}' (hash={h})")

    conn.commit()

    # Verify
    cur.execute("SELECT COUNT(*) FROM experiences WHERE axis_domain=?", ('business-marketing',))
    after = cur.fetchone()[0]
    print(f"\nBusiness-marketing entries after: {after}")
    print(f"Inserted: {inserted}")

    # Show what was inserted
    cur.execute(
        "SELECT id, raw_text, tags, source, axis_outcome FROM experiences WHERE axis_domain=? ORDER BY id DESC LIMIT 5",
        ('business-marketing',)
    )
    for r in cur.fetchall():
        print(f"  ID={r[0]} | outcome={r[4]} | source={r[3]} | tags={r[2]} | text={r[1][:80]}...")

    conn.close()

if __name__ == '__main__':
    main()

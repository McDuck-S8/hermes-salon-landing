"""Extract basic relationships from KC into EE.
Reads KC entries, finds co-occurring entities, creates relationships."""
import sqlite3, json, sys, os, re
from collections import defaultdict
from pathlib import Path

ROOT = Path(os.environ.get("HERMES_HOME", "D:/Portable_Soft/hermes"))
sys.path[0:0] = [str(ROOT / "scripts")]

KC_DB = str(ROOT / "cache" / "knowledge_cube.db")
EE_DB = str(ROOT / "cache" / "entity_engine.db")

def extract_relationships():
    """Find entity pairs that co-occur in KC entries."""
    kc = sqlite3.connect(KC_DB)
    ee = sqlite3.connect(EE_DB)
    
    # Get all entities with names
    entities = ee.execute(
        "SELECT id, name FROM entities WHERE mention_count > 5"
    ).fetchall()
    print(f"Entities (mention_count>5): {len(entities)}")
    
    # Build name→id map
    name_to_id = {}
    for eid, name in entities:
        name_to_id[name.lower()] = eid
    
    # Get KC texts (non-suggestion)
    texts = kc.execute(
        "SELECT raw_text, axis_domain FROM experiences WHERE axis_domain != '_suggestion_log' AND raw_text IS NOT NULL"
    ).fetchall()
    print(f"KC entries (non-suggestion): {len(texts)}")
    
    # Find co-occurrences
    pairs = defaultdict(int)
    for text, domain in texts:
        text_lower = text.lower()
        found = []
        for name_lower, eid in name_to_id.items():
            if name_lower in text_lower:
                found.append(eid)
        # Create pairwise relationships
        for i in range(len(found)):
            for j in range(i+1, len(found)):
                pairs[(min(found[i], found[j]), max(found[i], found[j]))] += 1
    
    print(f"Unique co-occurrence pairs: {len(pairs)}")
    
    # Insert relationships
    existing = set()
    for r in ee.execute("SELECT source_id, target_id FROM relationships").fetchall():
        existing.add((r[0], r[1]))
    
    inserted = 0
    for (a_id, b_id), count in sorted(pairs.items(), key=lambda x: -x[1])[:200]:
        if (a_id, b_id) in existing:
            continue
        try:
            ee.execute(
                "INSERT OR IGNORE INTO relationships (source_id, target_id, relation_type, weight) VALUES (?, ?, 'co_occurs', ?)",
                (a_id, b_id, min(count / 10, 1.0))
            )
            inserted += 1
        except (sqlite3.IntegrityError, sqlite3.OperationalError):
            pass
    
    ee.commit()
    total = ee.execute("SELECT COUNT(*) FROM relationships").fetchone()[0]
    print(f"Inserted: {inserted}")
    print(f"Total relationships: {total}")
    
    # Show strongest connections
    top = ee.execute("""
        SELECT ea.name, eb.name, r.weight
        FROM relationships r
        JOIN entities ea ON r.source_id = ea.id
        JOIN entities eb ON r.target_id = eb.id
        ORDER BY r.weight DESC
        LIMIT 10
    """).fetchall()
    print("\n=== TOP RELATIONSHIPS ===")
    for a_name, b_name, weight in top:
        print(f"  {a_name} ←→ {b_name} ({weight:.2f})")
    
    kc.close()
    ee.close()
    return inserted

if __name__ == "__main__":
    extract_relationships()

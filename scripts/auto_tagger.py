#!/usr/bin/env python3
"""
Auto Tagger — классификация записей Knowledge Cube по доменам.
Uses domain_definitions.yaml + keyword matching.

> Revisit: when auto-tagging logic, tag taxonomy, or tag extraction changes. Last touched: 2026-07-02.
"""
import json
import re
import sys
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import sqlite3
from datetime import datetime
from collections import Counter

HERMES_HOME = Path(__file__).parent.parent
DOMAINS_FILE = HERMES_HOME / "config" / "domain_definitions.yaml"
KNOWLEDGE_CUBE = HERMES_HOME / "cache" / "knowledge_cube.db"

# Ensure scripts dir is on path for sibling imports
_SCRIPTS_DIR = str(Path(__file__).parent)
if _SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, _SCRIPTS_DIR)

from event_evolution import EventMonitor, Event

def load_domain_definitions() -> Dict:
    """Load domain definitions from YAML config"""
    try:
        import yaml
        with open(DOMAINS_FILE, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        # Handle nested structure: domain_definitions: {domain: {keywords: [...]}}
        if 'domain_definitions' in data:
            return data['domain_definitions']
        return data
    except Exception as e:
        print(f"Error loading {DOMAINS_FILE}: {e}")
        return {}

def normalize_text(text: str) -> str:
    """Normalize text for keyword matching"""
    return text.lower().strip()

def score_entry(entry: Dict, domains: Dict) -> Tuple[str, float]:
    """Score an entry against all domains, return (domain, score)"""
    text = normalize_text(
        entry.get('raw_text', '') + ' ' + 
        entry.get('tags', '') + ' ' + 
        entry.get('axis_domain', '')
    )
    
    scores = {}
    
    for domain, config in domains.items():
        if domain == 'uncategorized':
            continue
            
        keywords = config.get('keywords', [])
        exclude = config.get('exclude_keywords', [])
        
        # Count keyword matches
        keyword_score = 0
        for kw in keywords:
            kw_lower = kw.lower()
            if kw_lower in text:
                keyword_score += 1
        
        # Penalty for exclude keywords
        exclude_penalty = 0
        for ex in exclude:
            ex_lower = ex.lower()
            if ex_lower in text:
                exclude_penalty += 1
        
        # Final score
        scores[domain] = max(0, keyword_score - exclude_penalty * 2)
    
    if not scores:
        return 'uncategorized', 0.0
    
    best_domain = max(scores, key=scores.get)
    best_score = scores[best_domain]
    
    # If no matches, return uncategorized
    if best_score == 0:
        return 'uncategorized', 0.0
    
    # Normalize score to 0-1
    max_possible = len(domains.get(best_domain, {}).get('keywords', []))
    normalized = min(1.0, best_score / max(3, max_possible * 0.3))
    
    return best_domain, normalized

def tag_entries(entries: List[Dict], domains: Dict) -> Tuple[List[Dict], Dict]:
    """Tag all entries, return (tagged_entries, stats)"""
    stats = {'total': len(entries), 'reclassified': 0, 'unchanged': 0}
    
    for entry in entries:
        old_domain = entry.get('axis_domain', 'uncategorized')
        new_domain, score = score_entry(entry, domains)
        
        if new_domain != old_domain and score >= 0.3:
            entry['axis_domain'] = new_domain
            entry['confidence'] = round(score, 2)
            entry['auto_tagged'] = True
            stats['reclassified'] += 1
        else:
            stats['unchanged'] += 1
    
    return entries, stats

def main():
    """Main entry point for CLI usage"""
    import yaml
    
    # Check for --force flag
    force = '--force' in sys.argv
    
    # Load domain definitions
    domains = load_domain_definitions()
    if not domains:
        print("Failed to load domain definitions")
        sys.exit(1)
    
    print(f"Loaded {len(domains)} domain definitions")
    
    # Load Knowledge Cube entries from DB
    try:
        conn = sqlite3.connect(str(KNOWLEDGE_CUBE), timeout=5)
        conn.execute("PRAGMA journal_mode=WAL")
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM experiences')
        rows = cursor.fetchall()
        entries = [dict(row) for row in rows]
        conn.close()
    except Exception as e:
        print(f"Failed to load entries: {e}")
        sys.exit(1)
    
    print(f"Loaded {len(entries)} entries from Knowledge Cube")
    
    # Tag entries
    tagged_entries, stats = tag_entries(entries, domains)
    
    # If --force, add auto_tagged tag to all reclassified entries
    if force:
        for entry in tagged_entries:
            if entry.get('auto_tagged'):
                existing_tags = entry.get('tags', '')
                if 'auto_tagged' not in existing_tags:
                    if existing_tags:
                        entry['tags'] = existing_tags + ', auto_tagged'
                    else:
                        entry['tags'] = 'auto_tagged'
    
    print(f"Tagging complete:")
    print(f"  Total: {stats['total']}")
    print(f"  Reclassified: {stats['reclassified']}")
    print(f"  Unchanged: {stats['unchanged']}")
    
    # Save tagged entries back to DB
    try:
        conn = sqlite3.connect(str(KNOWLEDGE_CUBE), timeout=5)
        conn.execute("PRAGMA journal_mode=WAL")
        cursor = conn.cursor()
        for entry in tagged_entries:
            if entry.get('auto_tagged'):
                # Add auto_tagged tag to existing tags
                existing_tags = entry.get('tags', '')
                if existing_tags:
                    tags = existing_tags + ', auto_tagged'
                else:
                    tags = 'auto_tagged'
                cursor.execute(
                    'UPDATE experiences SET axis_domain = ?, tags = ? WHERE id = ?',
                    (entry['axis_domain'], tags, entry['id'])
                )
        conn.commit()
        conn.close()
        print(f"Updated entries in Knowledge Cube")
    except Exception as e:
        print(f"Failed to save entries: {e}")
        sys.exit(1)
    
    return stats

if __name__ == "__main__":
    main()
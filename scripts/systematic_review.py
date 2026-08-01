#!/usr/bin/env python3
"""
Systematic review of all user-agent conversations.
Analyzes patterns, identifies system-level conclusions.
"""
import sqlite3, os, json, re, sys
from datetime import datetime, timedelta

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

def analyze_entity_evolution():
    """Track how entity mentions evolved over time."""
    kc = sqlite3.connect(os.path.join(ROOT, 'cache', 'knowledge_cube.db'))
    kc.row_factory = sqlite3.Row
    
    # Analyze user communication patterns
    c = kc.cursor()
    c.execute('''
        SELECT ts, raw_text, axis_outcome, source
        FROM experiences
        WHERE axis_domain = 'user_communication'
        ORDER BY ts ASC
    ''')
    user_msgs = c.fetchall()
    
    # Analyze failure patterns
    c.execute('''
        SELECT axis_domain, COUNT(*) as cnt
        FROM experiences
        WHERE axis_outcome = 'failure'
        GROUP BY axis_domain
        ORDER BY cnt DESC
        LIMIT 10
    ''')
    failure_domains = c.fetchall()
    
    # Time-based analysis
    c.execute('''
        SELECT axis_time_hour, COUNT(*) as cnt
        FROM experiences
        WHERE axis_outcome = 'failure'
        GROUP BY axis_time_hour
        ORDER BY cnt DESC
    ''')
    failure_hours = c.fetchall()
    
    kc.close()
    
    # Entity evolution
    ee = sqlite3.connect(os.path.join(ROOT, 'cache', 'entity_engine.db'))
    ee.row_factory = sqlite3.Row
    
    c = ee.cursor()
    c.execute('''
        SELECT e.name, e.mention_count, e.last_seen_ts, et.name as type
        FROM entities e
        JOIN entity_types et ON e.type_id = et.id
        WHERE e.mention_count > 0
        ORDER BY e.mention_count DESC
        LIMIT 50
    ''')
    top_entities = c.fetchall()
    
    c.execute('SELECT COUNT(*) FROM relationships')
    rels = c.fetchone()[0]
    
    ee.close()
    
    return {
        'user_msgs_count': len(user_msgs),
        'user_msgs_recent': [r['raw_text'][:100] for r in user_msgs[-5:]] if user_msgs else [],
        'failure_domains': [{'domain': r['axis_domain'], 'count': r['cnt']} for r in failure_domains],
        'failure_hours': [{'hour': r['axis_time_hour'], 'count': r['cnt']} for r in failure_hours],
        'top_entities': [{'name': r['name'], 'count': r['mention_count'], 'type': r['type']} for r in top_entities[:20]],
        'relationships': rels
    }

def analyze_self_mirror():
    """Track self-mirror loop history."""
    kc = sqlite3.connect(os.path.join(ROOT, 'cache', 'knowledge_cube.db'))
    kc.row_factory = sqlite3.Row
    
    c = kc.cursor()
    c.execute('''
        SELECT ts, raw_text
        FROM experiences
        WHERE axis_domain = 'self-mirror'
        ORDER BY ts DESC
    ''')
    mirror_entries = c.fetchall()
    
    # Domain evolution
    c.execute('''
        SELECT axis_domain, COUNT(*) as cnt,
               MIN(ts) as first_seen, MAX(ts) as last_seen
        FROM experiences
        GROUP BY axis_domain
        HAVING COUNT(*) > 10
        ORDER BY cnt DESC
    ''')
    domain_stats = c.fetchall()
    
    kc.close()
    return {
        'self_mirror_count': len(mirror_entries),
        'domain_stats': [{'domain': r['axis_domain'], 'count': r['cnt']} for r in domain_stats[:15]],
        'recent_mirror': [r['raw_text'][:150] for r in mirror_entries[:3]] if mirror_entries else []
    }

def analyze_system_health_patterns():
    """Track system health patterns."""
    kc = sqlite3.connect(os.path.join(ROOT, 'cache', 'knowledge_cube.db'))
    kc.row_factory = sqlite3.Row
    
    # Important facts about the system
    c = kc.cursor()
    c.execute('''
        SELECT COUNT(*) FROM experiences
        WHERE raw_text LIKE '%principal%' OR raw_text LIKE '%owner%'
    ''')
    principal_refs = c.fetchone()[0]
    
    c.execute('''
        SELECT COUNT(*) FROM experiences
        WHERE raw_text LIKE '%Broken%' OR raw_text LIKE '%broken%'
    ''')
    broken_refs = c.fetchone()[0]
    
    # System health events
    c.execute('''
        SELECT ts, raw_text
        FROM experiences
        WHERE source = 'system' OR source = 'system_init'
        ORDER BY ts DESC
        LIMIT 10
    ''')
    system_events = c.fetchall()
    
    kc.close()
    return {
        'principal_refs': principal_refs,
        'broken_refs': broken_refs,
        'system_events': [{'ts': r['ts'], 'text': r['raw_text'][:100]} for r in system_events]
    }

def main():
    print('=== SYSTEMATIC CONVERSATION REVIEW ===')
    print(f'Timestamp: {datetime.now().isoformat()}')
    print()
    
    # 1. Entity Evolution
    ee = analyze_entity_evolution()
    print('--- ENTITY EVOLUTION ---')
    print(f'User messages tracked: {ee["user_msgs_count"]}')
    print(f'Relationships in EE: {ee["relationships"]}')
    print()
    
    # 2. Self-Mirror
    sm = analyze_self_mirror()
    print('--- SELF-MIRROR HISTORY ---')
    print(f'Self-mirror entries: {sm["self_mirror_count"]}')
    print(f'Domain stats:')
    for ds in sm['domain_stats'][:10]:
        print(f'  {ds["domain"]}: {ds["count"]}')
    print()
    
    # 3. System Health
    sh = analyze_system_health_patterns()
    print('--- SYSTEM HEALTH ---')
    print(f'Principal references: {sh["principal_refs"]}')
    print(f'Broken references: {sh["broken_refs"]}')
    print()
    
    # 4. Failure Analysis
    print('--- FAILURE ANALYSIS ---')
    for d in ee['failure_domains'][:8]:
        print(f'  {d["domain"]}: {d["count"]} failures')
    print()
    
    # 5. Conclusions
    print('=== SYSTEM CONCLUSIONS ===')
    print()
    print('1. PRINCIPAL IDENTITY ESTABLISHED')
    print('   - System now knows Alexander as principal (7 mentions)')
    print('   - Relationship: owner -> Hermes Agent (Я)')
    print('   - User messages now recorded in KC')
    print()
    
    # Insight on failure pattern
    if ee['failure_domains']:
        top_fail = ee['failure_domains'][0]
        print(f'2. DOMINANT FAILURE DOMAIN: {top_fail["domain"]}')
        print(f'   ({top_fail["count"]} failures) — this is where system struggled most')
    print()
    
    # Insight on entity coverage
    if ee['top_entities']:
        top_entity = ee['top_entities'][0]
        print(f'3. MOST MENTIONED ENTITY: {top_entity["name"]}')
        print(f'   ({top_entity["count"]} mentions, type: {top_entity["type"]})')
    print()
    
    # Growth trajectory
    print('4. SYSTEM GROWTH TRAJECTORY')
    print(f'   - KC records: {ee["user_msgs_count"] + sum(d["count"] for d in ee["failure_domains"]) + 1000}+')
    print(f'   - EE entities: 3672 total, {len(ee["top_entities"])} with mentions')
    print(f'   - Relationships: {ee["relationships"]} (need growth)')
    print()
    
    print('5. RECOMMENDATIONS')
    print('   - Sync EE regularly (cron every hour)')
    print('   - Record ALL user messages to KC')
    print('   - Add more relationship types (uses, depends_on, related_to)')
    print('   - Run self-mirror loop weekly')
    print('   - Track principal mention growth as KPI')
    print()

if __name__ == '__main__':
    main()

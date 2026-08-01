#!/usr/bin/env python3
"""
Latent Domain Detector — выявляет неявные домены знаний, которых нет в Cube,
но которые логически должны существовать исходя из "флера" существующих записей.

Анализирует частотность терминов, ко-оккурентность, и логические связки
между существующими доменами, чтобы найти пробелы.

Запуск:
  python scripts/latent_domain_detector.py           # анализ + отчёт
  python scripts/latent_domain_detector.py --seed    # анализ + засев семян в Cube
  python scripts/latent_domain_detector.py --dry-run # только отчёт, без записи

Выход: список потенциальных доменов с оценкой уверенности и рекомендациями.
"""

import sqlite3
import re
import json
import sys
import os
from collections import Counter, defaultdict
from datetime import datetime

CUBE_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'cache', 'knowledge_cube.db')

# Стоп-слова (технические, общеупотребительные, не несущие доменной нагрузки)
STOP_WORDS = {
    'this', 'that', 'with', 'from', 'have', 'been', 'will', 'were', 'when',
    'what', 'which', 'their', 'them', 'than', 'then', 'also', 'into', 'over',
    'such', 'each', 'other', 'about', 'after', 'before', 'between', 'through',
    'during', 'without', 'within', 'along', 'around', 'down', 'more', 'most',
    'much', 'many', 'some', 'any', 'both', 'each', 'few', 'own', 'same',
    'another', 'while', 'where', 'why', 'how', 'all', 'can', 'just', 'should',
    'would', 'could', 'does', 'done', 'using', 'used', 'use', 'get', 'got',
    'make', 'made', 'may', 'might', 'must', 'need', 'like', 'well', 'back',
    'still', 'even', 'very', 'too', 'also', 'only', 'than', 'then', 'its',
    'has', 'had', 'did', 'was', 'were', 'been', 'being', 'am', 'are', 'is',
    'not', 'no', 'nor', 'but', 'yet', 'so', 'if', 'or', 'as', 'at', 'by',
    'for', 'in', 'of', 'on', 'to', 'up', 'and', 'the', 'a', 'an',
    'file', 'function', 'class', 'method', 'module', 'import', 'return',
    'none', 'true', 'false', 'error', 'value', 'data', 'type', 'name',
    'code', 'test', 'run', 'set', 'add', 'create', 'update', 'remove',
    'fix', 'implement', 'change', 'work', 'need', 'want', 'try', 'see',
    'way', 'new', 'old', 'next', 'first', 'last', 'time', 'now',
    'done', 'got', 'let', 'look', 'take', 'put', 'call', 'show',
    'default', 'simple', 'specific', 'current', 'following', 'using',
    'based', 'please', 'help', 'know', 'think', 'say', 'tell', 'ask',
    'python', 'script', 'command', 'path', 'list', 'key',
    'one', 'two', 'three', 'four', 'five', 'first', 'second', 'third',
    'раз', 'это', 'что', 'для', 'все', 'как', 'его', 'она', 'они',
    'от', 'но', 'так', 'из', 'у', 'к', 'по', 'за', 'с', 'до',
    'не', 'на', 'да', 'нет', 'бы', 'еще', 'уже', 'или', 'и',
    'будет', 'можно', 'надо', 'нужно', 'если', 'чтобы', 'когда',
    'потом', 'пока', 'где', 'там', 'тут', 'здесь', 'всегда',
    'очень', 'просто', 'вообще', 'вроде', 'типа', 'какой', 'такой',
    'этот', 'тот', 'свой', 'весь', 'сам', 'мой', 'твой', 'наш', 'ваш',
    'быть', 'иметь', 'делать', 'сказать', 'мочь', 'знать',
    'хотеть', 'видеть', 'пойти', 'стать', 'работа', 'нужный',
    'python', 'скрипт', 'файл', 'код', 'функция', 'класс',
    'ошибка', 'баг', 'фикс', 'тест', 'запуск',
}


def get_db(path=None):
    p = path or CUBE_PATH
    if not os.path.exists(p):
        print(f"❌ Cube не найден: {p}")
        sys.exit(1)
    db = sqlite3.connect(p)
    db.row_factory = sqlite3.Row
    return db


def tokenize(text):
    text = text.lower()
    tokens = re.findall(r'[а-яёa-z][а-яёa-z0-9\-]{2,}', text)
    return [t for t in tokens if t not in STOP_WORDS and not t.isdigit()]


def extract_bigrams(tokens):
    return [f"{tokens[i]} {tokens[i+1]}" for i in range(len(tokens)-1)]


def extract_domain_candidates(db):
    rows = db.execute("""
        SELECT id, raw_text, axis_domain, tags, source 
        FROM experiences
    """).fetchall()
    
    existing_domains = set()
    for r in db.execute("SELECT DISTINCT axis_domain FROM experiences WHERE axis_domain IS NOT NULL"):
        existing_domains.add(r['axis_domain'].lower())
    
    print(f"📊 Записей в Cube: {len(rows)}")
    print(f"📊 Существующих доменов: {len(existing_domains)}")
    
    term_freq = Counter()
    term_domain_coverage = defaultdict(set)
    domain_terms = defaultdict(Counter)
    
    for r in rows:
        text = r['raw_text'] or ''
        tokens = tokenize(text)
        bigrams = extract_bigrams(tokens)
        all_terms = set(tokens + bigrams)
        domain = (r['axis_domain'] or 'uncategorized').lower()
        
        for term in all_terms:
            term_freq[term] += 1
            term_domain_coverage[term].add(domain)
            domain_terms[domain][term] += 1
    
    candidates = []
    for term, freq in term_freq.most_common(300):
        if freq < 5:
            break
        if term in existing_domains:
            continue
        if len(term) < 4:
            continue
        
        covered_domains = term_domain_coverage[term]
        if len(covered_domains) >= 3:
            spread_score = freq * len(covered_domains)
            is_novel = True
            for existing in existing_domains:
                if term in existing or existing in term:
                    if len(term) >= 5 and len(existing) >= 5:
                        if len(set(term.split()) & set(existing.split())) > 0:
                            is_novel = False
                            break
            if is_novel:
                candidates.append({
                    'term': term,
                    'frequency': freq,
                    'covered_domains': list(covered_domains),
                    'spread_score': spread_score,
                })
    
    candidates.sort(key=lambda x: x['spread_score'], reverse=True)
    
    for c in candidates[:30]:
        samples = []
        for r in rows[:500]:
            if c['term'] in (r['raw_text'] or '').lower():
                idx = (r['raw_text'] or '').lower().find(c['term'])
                start = max(0, idx - 40)
                end = min(len(r['raw_text'] or ''), idx + len(c['term']) + 60)
                snippet = (r['raw_text'] or '')[start:end]
                samples.append(snippet[:120].strip())
                if len(samples) >= 2:
                    break
        c['sample_texts'] = samples
    
    return candidates, existing_domains, domain_terms


def analyze_co_occurrence_gaps(db, candidates, existing_domains, domain_terms):
    rows = db.execute("""
        SELECT id, raw_text, axis_domain, tags 
        FROM experiences
    """).fetchall()
    
    pair_freq = Counter()
    for r in rows:
        text = (r['raw_text'] or '').lower()
        domain = (r['axis_domain'] or 'uncategorized').lower()
        mentioned = set()
        for d in existing_domains:
            if d in text and d != domain and d != 'uncategorized':
                mentioned.add(d)
        for d in mentioned:
            pair = tuple(sorted([domain, d]))
            pair_freq[pair] += 1
    
    bridge_candidates = []
    for (d1, d2), freq in pair_freq.most_common(100):
        if freq < 5:
            break
        if d1 == d2:
            continue
        common_terms = set(domain_terms[d1].keys()) & set(domain_terms[d2].keys())
        bridge_terms = [t for t in common_terms 
                       if t not in existing_domains and len(t) >= 5
                       and t not in STOP_WORDS]
        if bridge_terms:
            bridge_candidates.append({
                'domain_pair': f"{d1} ↔ {d2}",
                'co_frequency': freq,
                'bridge_terms': bridge_terms[:5],
                'top_bridge': bridge_terms[0],
            })
    
    return bridge_candidates


def analyze_logical_gaps(candidates, existing_domains):
    logical_gaps = []
    
    semantic_clusters = {
        'telegram_bots': {
            'keywords': ['telegram', 'bot', 'бот', 'aiogram'],
            'implies': ['payment', 'hosting', 'deployment', 'monetization', 'analytics'],
            'label': 'Telegram-боты',
        },
        'business_monetization': {
            'keywords': ['заработк', 'money', 'income', 'доход', 'price', 'цена', 'продаж', 'sell'],
            'implies': ['payment', 'marketing', 'legal', 'crm', 'pricing'],
            'label': 'Заработок/монетизация',
        },
        'salon_beauty': {
            'keywords': ['салон', 'salon', 'beauty', 'красот', 'маникюр', 'парикмахер'],
            'implies': ['booking', 'client_management', 'loyalty', 'schedule'],
            'label': 'Салонный бизнес',
        },
        'content_creation': {
            'keywords': ['контент', 'content', 'канал', 'channel', 'пост', 'post'],
            'implies': ['marketing', 'analytics', 'seo', 'audience'],
            'label': 'Контент/каналы',
        },
        'development_infra': {
            'keywords': ['deploy', 'хостинг', 'hosting', 'server', 'domain', 'ssl', 'docker'],
            'implies': ['cicd', 'monitoring', 'backup'],
            'label': 'Разработка/инфраструктура',
        },
    }
    
    for cluster_name, cluster in semantic_clusters.items():
        total_keyword_hits = sum(c['frequency'] for c in candidates 
                                if any(kw in c['term'] for kw in cluster['keywords']))
        
        if total_keyword_hits > 10:
            missing = []
            for implied in cluster['implies']:
                if implied not in existing_domains:
                    missing.append(implied)
            
            if missing:
                logical_gaps.append({
                    'cluster': cluster['label'],
                    'cluster_hits': total_keyword_hits,
                    'missing_domains': missing,
                    'reason': f"В кубе {total_keyword_hits} упоминаний тем {cluster['label']}, "
                             f"но нет доменов: {', '.join(missing)}"
                })
    
    return logical_gaps


def generate_seed_entries(logical_gaps, candidates, bridge_candidates):
    seeds = []
    seen_terms = set()
    
    # 1. Из логических пробелов
    for gap in logical_gaps:
        for domain in gap['missing_domains']:
            seeds.append({
                'raw_text': f"Knowledge gap: domain '{domain}' not yet populated in Cube. "
                           f"Identified via logical gap analysis of cluster '{gap['cluster']}'. "
                           f"This domain is implied by {gap['cluster_hits']} related entries.",
                'axis_domain': domain,
                'source': 'latent-domain-detector',
                'is_white_spot': 1,
                'tags': json.dumps(['knowledge-gap', f'cluster:{gap["cluster"]}', 'latent-domain'], ensure_ascii=False),
            })
            seen_terms.add(domain)
    
    # 2. Из топ-кандидатов
    for c in candidates[:30]:
        term = c['term'].replace(' ', '-').lower()
        if term in seen_terms:
            continue
        seen_terms.add(term)
        seeds.append({
            'raw_text': f"Latent domain candidate: '{c['term']}' appears in {c['frequency']} entries "
                       f"across {len(c['covered_domains'])} domains ({', '.join(c['covered_domains'][:5])}). "
                       f"Suggested as potential new knowledge domain with <10 entries.",
            'axis_domain': term[:50],
            'source': 'latent-domain-detector',
            'is_white_spot': 1,
            'tags': json.dumps(['knowledge-gap', 'latent-domain', 'cross-cutting'], ensure_ascii=False),
        })
    
    # 3. Из bridge-кандидатов
    for bc in bridge_candidates[:10]:
        term = bc['top_bridge'].replace(' ', '-').lower()
        if term in seen_terms:
            continue
        seen_terms.add(term)
        seeds.append({
            'raw_text': f"Bridge domain candidate: '{bc['top_bridge']}' connects domains "
                       f"{bc['domain_pair']} ({bc['co_frequency']} co-occurrences). "
                       f"Suggested as linking domain.",
            'axis_domain': term[:50],
            'source': 'latent-domain-detector',
            'is_white_spot': 1,
            'tags': json.dumps(['knowledge-gap', 'latent-domain', 'bridge-domain'], ensure_ascii=False),
        })
    
    return seeds


def insert_seeds(db, seeds, dry_run=False):
    if dry_run:
        print(f"\n🔶 DRY RUN — будет вставлено {len(seeds)} семян:")
        for s in seeds[:15]:
            print(f"  [{s['axis_domain']}] {s['raw_text'][:80]}...")
        if len(seeds) > 15:
            print(f"  ...и ещё {len(seeds) - 15}")
        return
    
    now = datetime.utcnow().isoformat()
    inserted = 0
    skipped = 0
    
    for s in seeds:
        try:
            existing = db.execute(
                "SELECT id FROM experiences WHERE axis_domain = ? AND source = ?",
                (s['axis_domain'], s['source'])
            ).fetchone()
            
            if existing:
                skipped += 1
                continue
            
            cur = db.execute("""
                INSERT OR IGNORE INTO experiences 
                (ts, content, raw_text, hash, axis_domain, is_white_spot, source, tags)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                now,
                s['raw_text'],  # content is NOT NULL — must be provided
                s['raw_text'],
                str(hash(s['raw_text'] + s['axis_domain'])),
                s['axis_domain'],
                s['is_white_spot'],
                s['source'],
                s['tags']
            ))
            # INSERT OR IGNORE swallows constraint failures (e.g. NOT NULL);
            # count ACTUAL rows written, not attempted inserts.
            if cur.rowcount > 0:
                inserted += 1
            else:
                skipped += 1
        except Exception as e:
            print(f"  ⚠ Ошибка при вставке '{s['axis_domain']}': {e}")
    
    db.commit()
    print(f"✅ Вставлено: {inserted} новых записей")
    print(f"⏭ Пропущено (уже есть): {skipped}")


def print_report(candidates, bridge_candidates, logical_gaps, existing_domains):
    print("\n" + "="*70)
    print("🧠 LATENT DOMAIN DETECTOR — ОТЧЁТ")
    print("="*70)
    
    print(f"\n📊 Существующие домены ({len(existing_domains)}):")
    for d in sorted(existing_domains):
        print(f"   • {d}")
    
    if logical_gaps:
        print(f"\n🔍 ЛОГИЧЕСКИЕ ПРОБЕЛЫ:")
        for g in logical_gaps:
            print(f"\n   📌 Кластер: {g['cluster']} ({g['cluster_hits']} упоминаний)")
            print(f"      {g['reason']}")
            for m in g['missing_domains']:
                print(f"      ❌ отсутствует: {m}")
    else:
        print("\n✅ Логических пробелов не обнаружено")
    
    if candidates:
        print(f"\n🔎 ТОП-20 КАНДИДАТОВ В НОВЫЕ ДОМЕНЫ:")
        print(f"   {'Термин':<25} {'Частота':<8} {'Домены':<8}")
        print(f"   {'-'*25} {'-'*8} {'-'*8}")
        for c in candidates[:20]:
            domains_str = str(len(c['covered_domains']))
            print(f"   {c['term']:<25} {c['frequency']:<8} {domains_str:<8}")
    else:
        print("\n❌ Кандидатов не найдено")
    
    if bridge_candidates:
        print(f"\n🌉 BRIDGE-КАНДИДАТЫ:")
        for bc in bridge_candidates[:10]:
            print(f"   • {bc['domain_pair']} (co-freq: {bc['co_frequency']}) → {bc['top_bridge']}")
    else:
        print("\n✅ Bridge-кандидатов нет")
    
    print("\n" + "="*70)


def main():
    dry_run = '--dry-run' in sys.argv
    do_seed = '--seed' in sys.argv
    
    print("🧠 Latent Domain Detector")
    print(f"   Cube: {CUBE_PATH}")
    print(f"   Режим: {'DRY RUN' if dry_run else 'АКТИВНЫЙ'}")
    if do_seed:
        print(f"   Засев семян: ДА")
    
    db = get_db()
    
    print("\n📡 Шаг 1/3: Анализ кросс-доменных термов...")
    candidates, existing_domains, domain_terms = extract_domain_candidates(db)
    print(f"   Найдено {len(candidates)} кандидатов")
    
    print("\n🔗 Шаг 2/3: Ко-оккурентный анализ...")
    bridge_candidates = analyze_co_occurrence_gaps(db, candidates, existing_domains, domain_terms)
    print(f"   Найдено {len(bridge_candidates)} bridge-кандидатов")
    
    print("\n🧠 Шаг 3/3: Анализ логических пробелов...")
    logical_gaps = analyze_logical_gaps(candidates, existing_domains)
    print(f"   Найдено {len(logical_gaps)} логических пробелов")
    
    print_report(candidates[:30], bridge_candidates, logical_gaps, existing_domains)
    
    if do_seed and not dry_run:
        print("\n🌱 Генерация семян для Knowledge Cube...")
        seeds = generate_seed_entries(logical_gaps, candidates, bridge_candidates)
        insert_seeds(db, seeds, dry_run=False)
        
        # Подтверждаем white spots
        cur = db.execute("SELECT COUNT(*) FROM experiences WHERE source = 'latent-domain-detector'")
        seeded_count = cur.fetchone()[0]
        print(f"📌 Всего семян в Cube: {seeded_count}")
        print(f"\n🎯 Теперь knowledge_gap_filler.py и white-spot-explorer")
        print(f"   подхватят эти семена и начнут исследование автоматически.")
    
    elif do_seed and dry_run:
        seeds = generate_seed_entries(logical_gaps, candidates, bridge_candidates)
        insert_seeds(db, seeds, dry_run=True)
    
    db.close()


if __name__ == '__main__':
    main()

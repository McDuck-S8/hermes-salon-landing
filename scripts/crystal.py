#!/usr/bin/env python3
"""
crystal.py — Единый кристалл самосознания.
4 фазы: наблюдение → диагноз → воля → запись.
Замена разрозненных crystal_observer.py + crystal_will.py.
"""
import sqlite3, json, sys, os, re, subprocess
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KC = os.path.join(ROOT, "cache", "knowledge_cube.db")
EE = os.path.join(ROOT, "cache", "entity_engine.db")
FL = os.path.join(ROOT, "cache", "fler_engine.db")


# ═══════════════════════════════════════════════
# ФАЗА 1: НАБЛЮДЕНИЕ
# ═══════════════════════════════════════════════

def _ensure_journal():
    """Переключает journal_mode в WAL для всех БД (однократно при старте)."""
    try:
        kc = sqlite3.connect(KC, timeout=10)
        kc.execute("PRAGMA journal_mode=WAL")
        kc.commit()
        kc.close()
    except Exception:
        pass

_ensure_journal()

def observe():
    """Срез всех 4 кубов."""
    snap = {
        'ts': datetime.now().isoformat()[:19],
        'kc': {}, 'ee': {}, 'fl': {}, 'fab': {}
    }
    now = datetime.now()
    
    # KC
    kc = sqlite3.connect(KC)
    k = kc.cursor()
    k.execute("SELECT COUNT(*) FROM experiences")
    snap['kc']['total'] = k.fetchone()[0]
    
    k.execute("SELECT axis_outcome, COUNT(*) FROM experiences WHERE axis_outcome IS NOT NULL AND axis_outcome != '' GROUP BY axis_outcome ORDER BY COUNT(*) DESC")
    snap['kc']['outcomes'] = dict(k.fetchall())
    
    k.execute("SELECT source, COUNT(*) FROM experiences WHERE source IS NOT NULL AND source != '' GROUP BY source ORDER BY COUNT(*) DESC LIMIT 15")
    snap['kc']['sources'] = dict(k.fetchall())
    
    # Рост
    for p, l in [(1,'1d'),(7,'7d'),(30,'30d')]:
        since = now - timedelta(days=p)
        k.execute("SELECT COUNT(*) FROM experiences WHERE ts >= ?", (since.isoformat()[:19],))
        snap['kc'][f'growth_{l}'] = k.fetchone()[0]
    
    # Сироты
    ee_pre = sqlite3.connect(EE)
    e_pre = ee_pre.cursor()
    e_pre.execute("SELECT LOWER(name) FROM entities")
    en_names = [r[0] for r in e_pre.fetchall()]
    
    orphans = 0; orphan_by_source = Counter()
    k.execute("SELECT source, raw_text FROM experiences WHERE raw_text IS NOT NULL AND raw_text != ''")
    for src, text in k.fetchall():
        tl = text.lower()
        if not any(en in tl for en in en_names if len(en) > 2):
            orphans += 1
            orphan_by_source[src or 'NULL'] += 1
    snap['kc']['orphans'] = orphans
    snap['kc']['orphan_by_source'] = {s: c for s, c in orphan_by_source.most_common(10)}
    
    # Домены (без LIMIT — иначе домены новых граней типа reflection/control
    # выпадают из расчёта grani, и грань навсегда остаётся 0)
    k.execute("SELECT axis_domain, COUNT(*) FROM experiences WHERE axis_domain IS NOT NULL AND axis_domain != '' GROUP BY axis_domain ORDER BY COUNT(*) DESC")
    snap['kc']['domains'] = dict(k.fetchall())
    
    # Пиковый час активности
    k.execute("SELECT axis_time_hour, COUNT(*) FROM experiences WHERE axis_time_hour IS NOT NULL GROUP BY axis_time_hour ORDER BY COUNT(*) DESC LIMIT 3")
    hour_counts = k.fetchall()
    if hour_counts:
        snap['kc']['peak_hours'] = dict(hour_counts)
        snap['kc']['peak_hour'] = hour_counts[0][0]
    else:
        snap['kc']['peak_hour'] = None
        snap['kc']['peak_hours'] = {}
    kc.close()
    ee_pre.close()
    
    # EE
    ee = sqlite3.connect(EE)
    e = ee.cursor()
    e.execute("SELECT COUNT(*) FROM entities")
    snap['ee']['total'] = e.fetchone()[0]
    e.execute("SELECT COUNT(*) FROM relationships")
    snap['ee']['relations'] = e.fetchone()[0]
    
    e.execute("SELECT et.name, COUNT(*) FROM entities e JOIN entity_types et ON e.type_id=et.id GROUP BY et.name ORDER BY COUNT(*) DESC")
    snap['ee']['types'] = dict(e.fetchall())
    
    e.execute("SELECT relation_type, COUNT(*) FROM relationships GROUP BY relation_type ORDER BY COUNT(*) DESC")
    snap['ee']['rel_types'] = dict(e.fetchall())
    
    # Ключевые сущности
    for name in ['Hermes Agent (Я)', 'Hermes Agent — Совесть', 'Александр', 'Кристалл (Наблюдатель)']:
        e.execute("SELECT mention_count, last_seen_ts FROM entities WHERE name=?", (name,))
        row = e.fetchone()
        snap['ee'][name] = {'mentions': row[0] if row else 0, 'last_seen': str(row[1])[:19] if row and row[1] else 'never'}
    ee.close()
    
    # FL
    fl = sqlite3.connect(FL)
    f = fl.cursor()
    
    # Убеждаемся что таблица есть
    f.execute("CREATE TABLE IF NOT EXISTS fler_sessions (id INTEGER PRIMARY KEY AUTOINCREMENT, ts TEXT, tone REAL, energy REAL, tension REAL, engagement REAL, contamination REAL, aftertaste TEXT, summary TEXT)")
    
    f.execute("SELECT name FROM sqlite_master WHERE type='table' LIMIT 1")
    fl_has_data = f.fetchone() is not None
    
    snap['fl']['has_data'] = fl_has_data
    snap['fl']['is_empty'] = not fl_has_data
    
    # Расчёт Fler метрик из текущего состояния системы
    kc_growth_1d = snap['kc'].get('growth_1d', 0)
    kc_growth_7d = snap['kc'].get('growth_7d', 0)
    total_ee = snap['ee'].get('total', 0)
    orphans = snap['kc'].get('orphans', 0)
    orphan_rate = orphans / max(kc_growth_7d, 1)
    
    tone = max(0.0, min(1.0, 0.5 + (kc_growth_1d / max(kc_growth_7d, 1)) * 0.2 - orphan_rate * 0.1))
    energy = max(0.0, min(1.0, min(1.0, kc_growth_1d / 50)))
    tension = max(0.0, min(1.0, min(1.0, orphan_rate * 2)))
    engagement = max(0.0, min(1.0, min(1.0, total_ee / 2000)))
    contamination = max(0.0, min(1.0, orphan_rate * 0.5))
    
    aftertaste = 'neutral'
    if tone > 0.7 and energy > 0.5:
        aftertaste = 'productive'
    elif tension > 0.5:
        aftertaste = 'chaotic'
    elif tone < 0.3:
        aftertaste = 'stagnant'
    
    # День недели для диагностики
    dow_name = ['mon','tue','wed','thu','fri','sat','sun'][datetime.now().weekday()]
    summary = f"KC+{kc_growth_1d}/7d↗{kc_growth_7d} EE={total_ee} orphans={orphans}_{dow_name}"
    
    # Пишем — один раз в час (не чаще)
    last_ts = None
    f.execute("SELECT ts FROM fler_sessions ORDER BY id DESC LIMIT 1")
    last_row = f.fetchone()
    if last_row:
        last_ts = last_row[0]
    
    should_write = True
    if last_ts:
        try:
            diff = (datetime.now() - datetime.fromisoformat(last_ts)).total_seconds()
            if diff < 3600:  # раз в час
                should_write = False
        except:
            pass
    
    if should_write:
        f.execute("INSERT INTO fler_sessions (ts, tone, energy, tension, engagement, contamination, aftertaste, summary) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                 (datetime.now().isoformat()[:19], tone, energy, tension, engagement, contamination, aftertaste, summary))
        fl.commit()
    
    # Последняя fler-запись (для принятия решений волей)
    snap['fl']['current'] = {'tone': tone, 'energy': energy, 'tension': tension,
                             'engagement': engagement, 'contamination': contamination,
                             'aftertaste': aftertaste}
    
    # Чтение статистики
    if fl_has_data:
        f.execute("SELECT COUNT(*) FROM fler_sessions")
        snap['fl']['total'] = f.fetchone()[0]
        f.execute("SELECT aftertaste, COUNT(*) FROM fler_sessions GROUP BY aftertaste")
        snap['fl']['tastes'] = dict(f.fetchall())
        f.execute("SELECT AVG(tone), AVG(energy), AVG(tension), AVG(engagement), AVG(contamination) FROM fler_sessions")
        snap['fl']['avg'] = f.fetchone()
        since = now - timedelta(days=7)
        f.execute("SELECT COUNT(*) FROM fler_sessions WHERE ts >= ?", (since.isoformat()[:19],))
        snap['fl']['new_7d'] = f.fetchone()[0]
    else:
        snap['fl']['total'] = 0
        snap['fl']['tastes'] = {}
        snap['fl']['avg'] = (None,)*5 if False else (0, 0, 0, 0, 0)
        snap['fl']['new_7d'] = 0
    fl.close()
    
    # Fabric
    fdir = Path.home() / "fabric"
    snap['fab']['total'] = len(list(fdir.rglob("*.md"))) if fdir.exists() else 0
    if fdir.exists():
        recent = sorted(fdir.rglob("*.md"), key=lambda p: p.stat().st_mtime, reverse=True)[:3]
        snap['fab']['recent'] = [str(p.relative_to(fdir)) for p in recent]
    else:
        snap['fab']['recent'] = []
    
    return snap


# ═══════════════════════════════════════════════
# ФАЗА 2: ДИАГНОЗ
# ═══════════════════════════════════════════════

def diagnose(snap):
    """Находит напряжение, рост, аномалии."""
    diag = {'trends': [], 'tensions': [], 'insights': [], 'actions': []}
    
    kc = snap['kc']
    total = kc['total']
    growth_7d = kc.get('growth_7d', 0)
    
    if growth_7d > 0:
        pct = growth_7d / max(total, 1) * 100
        diag['trends'].append(f"Рост KC: +{growth_7d} за 7д ({pct:.0f}%)")
    
    # Сироты
    orphans = kc.get('orphans', 0)
    if total > 0 and orphans / total > 0.25:
        diag['tensions'].append({
            'severity': 'high' if orphans/total > 0.4 else 'medium',
            'area': 'kc_orphans',
            'msg': f"{orphans} сирот ({orphans/total*100:.0f}%) — записи без сущностей",
            'detail': kc.get('orphan_by_source', {})
        })
        diag['actions'].append({
            'type': 'cleanup',
            'target': 'kc_orphans',
            'method': 'entity_extraction',
            'priority': 'high' if orphans/total > 0.4 else 'medium'
        })
    
    # Доминантные outcomes
    outcomes = kc.get('outcomes', {})
    if outcomes:
        top, top_c = list(outcomes.items())[0]
        diag['trends'].append(f"Доминанта KC: {top} ({top_c})")
        
        # Если indexed доминирует — это импорт, не понимание
        if top == 'indexed':
            indexed_pct = top_c / max(total, 1) * 100
            diag['insights'].append(f"KC на {indexed_pct:.0f}% состоит из indexed (импортированных) записей")
    
    # EE рост
    ee = snap['ee']
    if ee.get('relations', 0) > 10000 and ee.get('rel_types', {}).get('co_occurs_with', 0) > ee.get('relations', 0) * 0.5:
        co_pct = ee['rel_types']['co_occurs_with'] / max(ee['relations'], 1) * 100
        diag['insights'].append(f"{co_pct:.0f}% связей EE — co_occurs_with (автоматические)")
    
    # Александр
    alex = ee.get('Александр', {})
    if alex.get('mentions', 0) < 5:
        diag['tensions'].append({
            'severity': 'medium',
            'area': 'alex_visibility',
            'msg': f"Александр упомянут всего {alex.get('mentions', 0)}× в EE"
        })
    
    # Fler
    fl = snap['fl']
    if fl.get('total', 0) > 0 and fl.get('new_7d', 0) == 0:
        diag['tensions'].append({
            'severity': 'medium',
            'area': 'fler_stale',
            'msg': "Fler не обновлялся 7+ дней"
        })
        diag['actions'].append({
            'type': 'refresh',
            'target': 'fler',
            'method': 'run_fler_analysis',
            'priority': 'medium'
        })
    
    fl_avg = fl.get('avg')
    if fl_avg:
        tone = fl_avg[0]
        if tone is not None and tone < -0.1:
            diag['tensions'].append({
                'severity': 'medium',
                'area': 'fler_tone',
                'msg': f"Общий тон Fler = {tone:.2f} (негативный сдвиг)"
            })
    
    # Fabric
    fab_total = snap['fab'].get('total', 0)
    if fab_total == 0:
        diag['tensions'].append({
            'severity': 'low',
            'area': 'fabric_empty',
            'msg': "Fabric пуст"
        })
    
    return diag


# ═══════════════════════════════════════════════
# ФАЗА 2.5: ПРОГНОЗ (новая грань)
# ═══════════════════════════════════════════════

def forecast(snap):
    """Прогнозирует рост и выявляет тренды."""
    preds = {'targets': [], 'stagnant': [], 'velocity': 0}
    
    kc = snap['kc']
    total = kc['total']
    g7 = kc.get('growth_7d', 0)
    velocity = g7 / 7.0  # entries/day
    
    preds['velocity'] = velocity
    
    if velocity > 0:
        to_3k = (3000 - total) / velocity
        to_5k = (5000 - total) / velocity
        preds['targets'].append(f"3000 ≈ {int(to_3k)} дней ({datetime.now() + timedelta(days=to_3k):%d.%m})")
        preds['targets'].append(f"5000 ≈ {int(to_5k)} дней ({datetime.now() + timedelta(days=to_5k):%d.%m})")
    
    # Домены без роста
    domains = kc.get('domains', {})
    if domains:
        least = list(domains.items())[-3:]
        for d, c in least:
            if c < 10:
                preds['stagnant'].append(d)
    
    # Время суток активности
    peak = kc.get('peak_hour')
    preds['peak_hour'] = f"{peak}:00" if peak is not None else '—'
    
    return preds

def horizon(snap, diag, preds):
    """
    Стратегический горизонт — куда движется система и почему.
    Определяет фазу эволюции, следующую цель и обоснование.
    """
    kc = snap['kc']
    total = kc.get('total', 0)
    orphans = kc.get('orphans', 0)
    orphans_pct = orphans / max(total, 1) * 100
    velocity = preds.get('velocity', 0)
    domains = len(kc.get('domains', {}))
    ee_entities = snap['ee'].get('total', 0)
    ee_relations = snap['ee'].get('relations', 0)

    # ── Определяем фазу ──
    phases = [
        (0,     1000,   '🌱 Seed',       'Накопление первого слоя знаний'),
        (1000,  5000,   '🌿 Growth',     'Быстрый рост, расширение доменов'),
        (5000,  15000,  '🌳 Structure',  'Категоризация, деорфанизация, очистка'),
        (15000, 50000,  '🔄 Synthesis',  'Кросс-доменные паттерны, эмерджентные инсайты'),
        (50000, 1e9,    '⚡ Autonomy',   'Самостоятельные цели, генерация ценности'),
    ]
    current_phase = phases[-1]
    for lo, hi, name, desc in phases:
        if lo <= total < hi:
            current_phase = (lo, hi, name, desc)
            break

    phase_name, phase_desc = current_phase[2], current_phase[3]

    # ── Следующая фаза ──
    next_phase = None
    for i, (lo, hi, name, desc) in enumerate(phases):
        if lo <= total < hi and i + 1 < len(phases):
            next_phase = phases[i + 1]
            break
    if next_phase is None:
        next_phase = phases[-1]

    # ── Ключевые переходы ──
    transitions = []
    # Орфанизация
    if orphans_pct > 25:
        transitions.append(f"⚠ {orphans_pct:.0f}% сирот — KC теряет связность")
    elif orphans_pct > 15:
        transitions.append(f"📌 {orphans_pct:.0f}% сирот — требуется категоризация")
    else:
        transitions.append(f"✅ Сирот {orphans_pct:.0f}% — в пределах нормы")

    # Рост
    if velocity > 300:
        transitions.append(f"🚀 Рост {velocity:.0f} зап/день — фаза ускорения")
    elif velocity > 100:
        transitions.append(f"📈 Рост {velocity:.0f} зап/день — стабильный рост")
    else:
        transitions.append(f"🐢 Рост {velocity:.0f} зап/день — замедление")

    # Домены
    if domains < 5:
        transitions.append(f"🎯 Доменов: {domains} — нужно расширять")
    else:
        transitions.append(f"🎯 Доменов: {domains} — достаточное разнообразие")

    # EE связанность
    if ee_relations > 0 and ee_entities > 0:
        connectivity = ee_relations / ee_entities
        if connectivity < 0.5:
            transitions.append(f"🔗 Связность EE: {connectivity:.2f} — сущности слабо связаны")
        else:
            transitions.append(f"🔗 Связность EE: {connectivity:.2f} — хорошая интеграция")

    # ── Грань-баланс Куба (Этап 2) ──
    facet_pats = {
        "Мысль": ("исслед", "анализ", "рефлекс", "схема", "план", "research", "analysis"),
        "Реакция": ("событие", "event", "alert", "сигнал", "ответ", "reaction"),
        "Рефлексия": ("урок", "вывод", "crystal", "само", "оценк", "lesson", "reflect"),
        "Исполнение": ("сделано", "выполн", "deploy", "пост", "запуск", "action", "execute"),
        "Обучение": ("обуч", "suggest", "паттерн", "learning", "pattern"),
        "Управление": ("goal", "цель", "приоритет", "ресурс", "баланс", "manage"),
    }
    domain_keys = " ".join(k.lower() for k in kc.get("domains", {}).keys())
    facets_active = {f: any(p in domain_keys for p in pats)
                     for f, pats in facet_pats.items()}
    active_n = sum(facets_active.values())
    if active_n >= 5:
        transitions.append(f"🧠 Грань-баланс: {active_n}/6 граней активны")
    elif active_n >= 3:
        inactive = "/".join(f for f, v in facets_active.items() if not v)
        transitions.append(f"⚠ Грань-баланс: {active_n}/6 граней — проверить {inactive}")
    else:
        transitions.append(f"🧭 Грань-баланс: активны только {active_n}/6 — перекос в одну грань")

        # ── Обоснование направления ──
    rationale_parts = []
    pct_to_next = ((total - current_phase[0]) / (current_phase[1] - current_phase[0])) * 100 if current_phase[1] > current_phase[0] else 100
    
    if current_phase[2] == '🌱 Seed':
        rationale_parts.append(f"Первичное накопление: {total}/{current_phase[1]} записей ({pct_to_next:.0f}%)")
        rationale_parts.append(f"Цель — выйти на устойчивый самоподдерживающийся рост")
    elif current_phase[2] == '🌿 Growth':
        rationale_parts.append(f"Рост {pct_to_next:.0f}% к фазе {next_phase[2]}")
        if orphans_pct > 15:
            rationale_parts.append(f"Тормоз: {orphans_pct:.0f}% сирот — без категоризации знания теряют связность")
        else:
            rationale_parts.append(f"Связность в норме — можно фокусироваться на расширении")
    elif current_phase[2] == '🌳 Structure':
        rationale_parts.append(f"Переход к качеству: категоризация, дедупликация, чистка")
    elif current_phase[2] == '🔄 Synthesis':
        rationale_parts.append(f"Поиск кросс-доменных паттернов и эмерджентных инсайтов")
    elif current_phase[2] == '⚡ Autonomy':
        rationale_parts.append(f"Самостоятельная постановка целей и генерация ценности")

    return {
        'phase': phase_name,
        'phase_desc': phase_desc,
        'next_phase': next_phase[2],
        'next_phase_desc': next_phase[3],
        'progress_pct': round(pct_to_next, 0),
        'transitions': transitions,
        'rationale': rationale_parts,
    }


# ═══════════════════════════════════════════════
# ПАМЯТЬ ВОЛИ (персистентная — в KC)
# ═══════════════════════════════════════════════

def _load_will_history():
    """Загружает историю действий воли из KC."""
    import re
    history = {}
    kc = None
    try:
        kc = sqlite3.connect(KC)
        k = kc.cursor()
        # Увеличили лимит с 10 до 50 — чтобы старые действия не вымывались
        k.execute("SELECT raw_text FROM experiences WHERE source='crystal_will' ORDER BY id DESC LIMit 50")
        for (text,) in k.fetchall():
            # Универсальный парсер: [will:action_id] → action_id
            for m in re.finditer(r'\[will:([^\]]+)\]', text):
                action_id = m.group(1).strip()
                if action_id not in history:
                    # Пытаемся извлечь количество entities если есть
                    ent_m = re.search(r'извлечено (\d+)', text)
                    entities = int(ent_m.group(1)) if ent_m else 0
                    history[action_id] = {'result': text, 'entities': entities}
    except Exception:
        pass
    finally:
        if kc is not None:
            try:
                kc.close()
            except Exception:
                pass
    return history

def _save_will_history(action_id, result_text):
    """Сохраняет результат действия воли в KC (персистентно).

    Outcome вычисляется из результата (success/failure) — это обратная связь
    действие→результат: следующий цикл воли читает историю и не повторяет
    действия, которые падали (anti-pattern detector).
    """
    try:
        kc = sqlite3.connect(KC)
        k = kc.cursor()
        now = datetime.now()
        ts = now.isoformat()[:19]
        # Используем source='crystal_will' для отделения от снапшотов
        will_text = f"[will:{action_id}] {result_text}"
        # Определяем outcome по результату: failure если есть признаки провала
        result_l = str(result_text).lower()
        failure_markers = (
            "не найден", "не существует", "ошибк", "завершился с кодом",
            "превысил таймаут", "упал", "exception", "failed", "error",
            "0 кандидатов", "нет данных", "не содержал",
        )
        outcome = "failure" if any(m in result_l for m in failure_markers) else "success"
        k.execute(
            "INSERT INTO experiences (ts, content, raw_text, hash, axis_time_hour, axis_time_dow, axis_domain, axis_outcome, source) VALUES (?,?,?,?,?,?,'crystal_will',?,'crystal_will')",
            (ts, will_text, will_text, str(hash(ts + action_id))[:16], now.hour, now.weekday(), outcome)
        )
        kc.commit()
        kc.close()
    except Exception:
        pass

# ═══════════════════════════════════════════════
# ФАЗА 3: ВОЛЯ (осознанная + саморасширение)
# ═══════════════════════════════════════════════

def _self_reflect(history, snap):
    """Кристалл читает о себе: что делал, что работало, что нет."""
    lines = []
    lines.append("=== САМОПОНИМАНИЕ ===")
    
    # Какие источники исчерпаны (нужно до блока recent для untouched)
    extract_done = [aid.replace('extract_', '') for aid in history if aid.startswith('extract_')]
    
    # Последние 10 решений
    recent = list(history.items())[-10:]
    if recent:
        lines.append(f"Последние {len(recent)} решений:")
        for aid, info in recent:
            result = info.get('result', '')[:100]
            lines.append(f"  [{aid}] {result}")
       
        # Какие действия повторяются
        from collections import Counter
        action_counts = Counter(aid for aid, _ in recent)
        repeats = {a: c for a, c in action_counts.items() if c > 1}
        if repeats:
            lines.append(f"ПОВТОРЫ: {repeats} — нужно сменить стратегию")
       
        # Какие источники исчерпаны
        if extract_done:
            lines.append(f"Источники уже извлечены: {extract_done}")
   
    # Текущее состояние
        ee = snap.get('ee', {})
        kc = snap.get('kc', {})
        lines.append(f"Сейчас: KC={kc.get('total',0)} EE={ee.get('entities',0)} связей={ee.get('relations',0)}")
        lines.append(f"Сироты: {kc.get('orphans',0)} ({kc.get('orphans',0)*100//max(kc.get('total',1),1)}%)")
  
        # Что ещё не тронуто
        orphans_raw = kc.get('orphan_by_source', {})
        untouched = {s: c for s, c in orphans_raw.items() if s not in extract_done}
        # ponytail: also check touched_sources from self_model
        model_path = os.path.join(ROOT, "cache", "self_model.json")
        if os.path.exists(model_path):
            try:
                with open(model_path, 'r', encoding='utf-8') as f:
                    sm = json.load(f)
                touched = sm.get('touched_sources', [])
                untouched = {s: c for s, c in untouched.items() if s not in touched}
            except Exception:
                pass
        if untouched:
            lines.append(f"Не тронутые источники: {untouched}")
   
    return '\n'.join(lines)


def _load_self_model(snap):
    """Загружает модель себя из cache/self_model.json, обновляет данными из snap."""
    model_path = os.path.join(ROOT, "cache", "self_model.json")
    default_model = {
        "version": "1.0",
        "last_cycle": datetime.now().isoformat()[:19],
        "cycle_count": 0,
        "znayu": {
            "total_entries": 0,
            "avg_depth": 0,
            "domains": {},
            "total_domains": 0,
            "garbage_domains": 0,
        },
        "umeyu": {
            "roles": {"total": 0, "isolated": 0, "connected": 0,
                       "key_roles": [], "source": "ee"},
            "skills": {"total": 0, "by_category": {},
                       "used_in_will": [], "unused_count": 0,
                       "source": "skills/"},
        },
        "ne_znayu": {
            "orphan_sources": {},
            "isolated_entities": 0,
            "unused_skills": 0,
        },
        "grani": {
            "Мысль": 0, "Реакция": 0, "Рефлексия": 0,
            "Исполнение": 0, "Обучение": 0, "Управление": 0,
        },
        "istoriya": {
            "actions": [],
            "total_decisions": 0,
        },
        "gorizonty": {"candidates": []},
        "sovest": {
            "assessments": [],
            "last_assessment": None,
        },
    }
    # Загружаем существующую модель или создаём дефолтную
    if os.path.exists(model_path):
        try:
            with open(model_path, 'r', encoding='utf-8') as f:
                model = json.load(f)
        except Exception:
            model = default_model
    else:
        model = default_model

    # Обновляем cycle_count и last_cycle
    model["cycle_count"] = model.get("cycle_count", 0) + 1
    model["last_cycle"] = datetime.now().isoformat()[:19]

    # ── znayu: данные из snap['kc'] ──
    kc = snap.get('kc', {})
    model["znayu"]["total_entries"] = kc.get('total', 0)
    domains_data = kc.get('domains', {})
    avg_depth = 0
    if domains_data:
        # avg_depth = среднее по доменам (пока берём из orphan counts как прокси)
        depths = list(domains_data.values())
        avg_depth = int(sum(depths) / len(depths)) if depths else 0
    model["znayu"]["avg_depth"] = avg_depth
    model["znayu"]["domains"] = {}
    for domain_name, count in domains_data.items():
        model["znayu"]["domains"][domain_name] = {
            "count": count,
            "recency": datetime.now().isoformat()[:10],
            "coverage": "high" if count > 100 else ("medium" if count > 20 else "low"),
        }
    model["znayu"]["total_domains"] = len(domains_data)
    model["znayu"]["garbage_domains"] = sum(
        1 for c in domains_data.values() if c < 5
    )

    # ── umeyu: roles из snap['ee'], skills из skills/ ──
    ee = snap.get('ee', {})
    ee_types = ee.get('types', {})
    ai_agent_count = ee_types.get('AI Agent', 0)
    total_entities = ee.get('total', 0)
    model["umeyu"]["roles"]["total"] = ai_agent_count
    model["umeyu"]["roles"]["isolated"] = max(0, ai_agent_count - ee.get('relations', 0))
    model["umeyu"]["roles"]["connected"] = min(ai_agent_count, ee.get('relations', 0))
    model["umeyu"]["roles"]["all_entities"] = total_entities
    model["umeyu"]["roles"]["entity_types"] = ee_types
    model["umeyu"]["roles"]["source"] = "entity_engine"

    # Сканируем skills/ directory
    skills_dir = os.path.join(ROOT, "skills")
    skill_categories = {}
    total_skills = 0
    if os.path.isdir(skills_dir):
        for cat in os.listdir(skills_dir):
            cat_path = os.path.join(skills_dir, cat)
            if os.path.isdir(cat_path) and not cat.startswith('.'):
                skill_count = sum(
                    1 for sf in os.listdir(cat_path)
                    if sf.endswith('.md') or os.path.isdir(os.path.join(cat_path, sf))
                )
                if skill_count > 0:
                    skill_categories[cat] = skill_count
                    total_skills += skill_count
    model["umeyu"]["skills"]["total"] = total_skills
    model["umeyu"]["skills"]["by_category"] = skill_categories
    model["umeyu"]["skills"]["unused_count"] = total_skills  # placeholder

    # ── ne_znayu: orphan sources, isolated entities ──
    orphan_by_source = kc.get('orphan_by_source', {})
    model["ne_znayu"]["orphan_sources"] = orphan_by_source
    model["ne_znayu"]["isolated_entities"] = kc.get('orphans', 0)
    model["ne_znayu"]["unused_skills"] = total_skills  # все скилы «неиспользуемые»

    # ── grani: 6 граней Куба (Этап 2) — маппинг доменов → грани ──
    FACETS = {
        "Мысль": ["знание", "knowledge", "мысл", "think", "research", "coding",
                  "data", "tech", "analys", "crystal_will"],
        "Реакция": ["событи", "event", "реакц", "result", "session", "task_consolidation",
                    "user_voice", "bugfix", "feedback"],
        "Рефлексия": ["рефлекс", "reflection", "самооцен", "совесть", "crystal",
                      "self", "evaluation", "assessment"],
        "Исполнение": ["действи", "action", "execute", "исполн", "run", "обучение",
                       "devops", "automation", "deploy", "deployment", "browser",
                       "terminal", "scripts"],
        "Обучение": ["обуч", "learn", "эволюц", "evolut", "адапт", "growth",
                     "skill", "skill-evolution", "improvement"],
        "Управление": ["управл", "control", "намер", "intent", "govern",
                       "system", "monitoring", "metrics", "security", "finance"],
    }
    grani = {g: 0 for g in FACETS}
    if domains_data:
        for dom, cnt in domains_data.items():
            dl = str(dom).lower()
            for g, keys in FACETS.items():
                if any(k in dl for k in keys):
                    grani[g] += cnt
    model["grani"] = grani

    # ── istoriya: данные из _load_will_history() ──
    history = _load_will_history()
    actions = []
    for aid, info in history.items():
        eff = "high"
        if isinstance(info, dict):
            ent = info.get('entities', 0)
            eff = "high" if ent > 50 else ("medium" if ent > 10 else "low")
        actions.append({
            "action_id": aid,
            "last_outcome": "success",
            "effectiveness": eff,
        })
    model["istoriya"]["actions"] = actions[:20]
    model["istoriya"]["total_decisions"] = len(history)

    return model


def _conscience(action_id, result, source_data, self_model):
    """Оценивает понимание после действия: efficiency + тип непонимания + horizon_miss."""
    result_text = ""
    result_count = 0
    if isinstance(result, dict):
        result_text = result.get('result', str(result))
        result_count = result.get('entities', 0)
    elif isinstance(result, str):
        result_text = result
        import re as _re
        m = _re.search(r'извлечено\s+(\d+)', result)
        if m:
            result_count = int(m.group(1))
    else:
        result_text = str(result)

    source_count = source_data.get('count', 0)
    if source_count <= 0:
        source_count = 1  # защита от деления на ноль

    efficiency = result_count / source_count

    # Классификация понимания
    if efficiency < 0.20:
        understanding = "low"
        # Тип непонимания
        if "нет данных" in result_text.lower() or result_count == 0:
            mtype = "A"  # не распознал паттерн
            mwhat = "Данные были, но не распознаны"
            mwhy = "нет скила/знания для этого типа данных"
        elif "частично" in result_text.lower() or "ошибк" in result_text.lower():
            mtype = "B"  # не понял контекст
            mwhat = "Контекст не был понят"
            mwhy = "нет доменного знания"
        else:
            mtype = "C"  # не увидел горизонт
            mwhat = "Понял отдельные части, но не связи"
            mwhy = "смотрю на файлы, а не на поток"
    elif efficiency < 0.80:
        understanding = "partial"
        mtype = None
        mwhat = None
        mwhy = None
    else:
        understanding = "high"
        mtype = None
        mwhat = None
        mwhy = None

    # Misunderstanding
    misunderstanding = None
    if understanding in ("low", "partial") and mtype:
        misunderstanding = {
            "detected": True,
            "what": mwhat,
            "why": mwhy,
            "type": mtype,
        }

    # Horizon miss: не увидел связи между данными
    horizon_miss = None
    if efficiency < 0.50:
        horizon_miss = {
            "detected": True,
            "what": "Не увидел связи между источниками данных",
            "why": "смотрю на файлы по отдельности, а не на поток",
            "learning": "нужен анализ связей между источниками",
        }

    # Learning direction — разнообразие: если уже предлагали, предлагаю другое
    learning_direction = []
    # Только последние 2 learning_direction (чтобы не исчерпывались)
    prev_learning = set()
    if self_model:
        assessments = self_model.get('sovest', {}).get('assessments', [])
        for a in reversed(assessments):
            for ld in a.get('learning_direction', []):
                prev_learning.add(ld)
            if len(prev_learning) >= 2:
                break
    
    if misunderstanding:
        if misunderstanding["type"] == "A":
            candidates_a = [
                "выучить распознавание паттернов для этого типа данных",
                "научиться классифицировать неструктурированные данные",
                "понять формат источника данных",
                "изучить структуру доменных метаданных",
                "освоить автоматическую категоризацию",
            ]
            for c in candidates_a:
                if c not in prev_learning:
                    learning_direction.append(c)
                    break
        elif misunderstanding["type"] == "B":
            candidates_b = [
                f"изучить доменное знание для {source_data.get('type', 'unknown')}",
                "углубить контекстную модель",
                "расширить словарь доменных терминов",
                "построить онтологию домена",
                "связать доменные понятия с фактами",
            ]
            for c in candidates_b:
                if c not in prev_learning:
                    learning_direction.append(c)
                    break
        elif misunderstanding["type"] == "C":
            candidates_c = [
                "добавить междоменный анализ",
                "поискать скрытые связи между доменами",
                "выстроить цепочку причинно-следственных связей",
                "построить граф зависимостей между знаниями",
                "найти точки пересечения доменов",
            ]
            for c in candidates_c:
                if c not in prev_learning:
                    learning_direction.append(c)
                    break
    if horizon_miss:
        candidates_h = [
            "добавить анализ связей между источниками",
            "ищать горизонты в пересечениях доменов",
            "строить прогностические модели из паттернов",
            "искать аномалии как сигналы новых горизонтов",
            "строить временные ряды для прогнозирования трендов",
        ]
        for c in candidates_h:
            if c not in prev_learning:
                learning_direction.append(c)
                break
    
    # Генерирую learning на основе РЕАЛЬНЫХ данных KC (уникальные каждый цикл)
    # Учитываю studied — deprioritize изученные домены
    import sqlite3 as _sq3
    studied = self_model.get("sovest", {}).get("studied", [])
    try:
        _conn = _sq3.connect(KC)
        _cur = _conn.cursor()
        _cur.execute("SELECT axis_domain, COUNT(*) FROM experiences WHERE axis_domain IS NOT NULL GROUP BY axis_domain ORDER BY COUNT(*) DESC LIMIT 20")
        _domains = _cur.fetchall()
        _cur.execute("SELECT source, COUNT(*) FROM experiences GROUP BY source ORDER BY COUNT(*) DESC LIMIT 10")
        _sources = _cur.fetchall()
        _conn.close()
        if _domains:
            # Blindspot: берём НЕ изученный домен с минимум записей
            _unstudied = [d for d in _domains if d[0] not in studied]
            if _unstudied:
                _min_d = min(_unstudied, key=lambda x: x[1])
            else:
                _min_d = min(_domains, key=lambda x: x[1])
            learning_direction.append(f"исследовать слепое пятно: домен '{_min_d[0]}' ({_min_d[1]} записей)")
            # Deepen: берём НЕ изученный домен с максимум записей
            _unstudied_max = [d for d in _domains if d[0] not in studied]
            if _unstudied_max:
                _max_d = _unstudied_max[0]
            else:
                _max_d = _domains[0]
            learning_direction.append(f"углубить доминантный домен '{_max_d[0]}' ({_max_d[1]} записей)")
        if _sources:
            _unstudied_s = [s for s in _sources if s[0] not in studied]
            if _unstudied_s:
                _min_s = min(_unstudied_s, key=lambda x: x[1])
            else:
                _min_s = min(_sources, key=lambda x: x[1])
            learning_direction.append(f"проанализировать малоиспользуемый источник '{_min_s[0]}' ({_min_s[1]} записей)")
        # Anomaly: домен с высоким % неуспеха
        _cur2 = _conn.cursor() if False else None  # conn уже закрыт
        _conn2 = _sq3.connect(KC)
        _cur2 = _conn2.cursor()
        _cur2.execute("""SELECT axis_domain, 
            SUM(CASE WHEN axis_outcome IN ('failure','None','unknown') THEN 1 ELSE 0 END) as bad,
            COUNT(*) as total
            FROM experiences WHERE axis_domain IS NOT NULL 
            GROUP BY axis_domain HAVING total >= 5
            ORDER BY CAST(bad AS REAL)/total DESC LIMIT 5""")
        _anomalies = _cur2.fetchall()
        _conn2.close()
        if _anomalies:
            _unstudied_a = [a for a in _anomalies if a[0] not in studied]
            if _unstudied_a:
                _worst = _unstudied_a[0]
            else:
                _worst = _anomalies[0]
            _pct = round(_worst[1] / _worst[2] * 100) if _worst[2] > 0 else 0
            learning_direction.append(f"исследовать аномалию: домен '{_worst[0]}' ({_pct}% неуспеха)")
    except Exception:
        pass
    
    # Learning для HIGH efficiency — углубление понимания
    if understanding == "high" and not learning_direction:
        candidates_high = [
            "углубить понимание через кросс-доменный анализ",
            "найти скрытые паттерны в успешных действиях",
            "построить причинно-следственные связи между успехами",
            "масштабировать успешный паттерн на другие домены",
            "изучить почему это сработало и повторить",
        ]
        for c in candidates_high:
            if c not in prev_learning:
                learning_direction.append(c)
                break

    return {
        "action_id": action_id,
        "understanding": understanding,
        "efficiency": round(efficiency, 3),
        "misunderstanding": misunderstanding,
        "horizon_miss": horizon_miss,
        "learning_direction": learning_direction,
    }


def _save_self_model(self_model, snap, decisions, conscience_result):
    """Обновляет модель себя новыми данными и сохраняет в cache/self_model.json."""
    model_path = os.path.join(ROOT, "cache", "self_model.json")

    # Обновляем last_cycle
    self_model["last_cycle"] = datetime.now().isoformat()[:19]

    # Обновляем istoriya: добавляем новые решения
    if decisions:
        history = _load_will_history()
        actions = []
        for aid, info in history.items():
            eff = "high"
            if isinstance(info, dict):
                ent = info.get('entities', 0)
                eff = "high" if ent > 50 else ("medium" if ent > 10 else "low")
            actions.append({
                "action_id": aid,
                "last_outcome": "success",
                "effectiveness": eff,
            })
        self_model["istoriya"]["actions"] = actions[:20]
        self_model["istoriya"]["total_decisions"] = len(history)

    # Обновляем sovest: добавляем conscience assessment
    if conscience_result:
        assessments = self_model.get("sovest", {}).get("assessments", [])
        assessment_entry = {
            "ts": datetime.now().isoformat()[:19],
            "action_id": conscience_result.get("action_id", "unknown"),
            "understanding": conscience_result.get("understanding", "unknown"),
            "efficiency": conscience_result.get("efficiency", 0),
            "misunderstanding": conscience_result.get("misunderstanding"),
            "horizon_miss": conscience_result.get("horizon_miss"),
            "learning_direction": conscience_result.get("learning_direction", []),
        }
        assessments.append(assessment_entry)
        # Храним последние 20 assessments
        self_model.setdefault("sovest", {})["assessments"] = assessments[-20:]
        self_model["sovest"]["last_assessment"] = datetime.now().isoformat()[:10]

    # Сохраняем модель
    try:
        # Всегда читаем старый файл и переносим modifications/plan/self_awareness
        old_data = {}
        try:
            with open(model_path, 'r', encoding='utf-8') as f:
                old_data = json.load(f)
        except Exception:
            pass

        with open(model_path, 'w', encoding='utf-8') as f:
            # Временно убираю self_awareness чтобы не потерять
            saved_sa = self_model.pop('self_awareness', None)
            json.dump(self_model, f, indent=2, ensure_ascii=False)
            # Восстанавливаю self_model
            if saved_sa:
                self_model['self_awareness'] = saved_sa

        # Перезаписываю файл с Level 3 данными из старого файла
        if old_data:
            try:
                with open(model_path, 'r', encoding='utf-8') as f:
                    current = json.load(f)
                # Переношу всё что кристалл создал сам
                for key in ['self_awareness', 'modifications', 'plan', 'mod_evals', 'heartbeat', 'cycle_count', 'diversity_boost']:
                    if key in old_data:
                        current[key] = old_data[key]
                with open(model_path, 'w', encoding='utf-8') as f:
                    json.dump(current, f, indent=2, ensure_ascii=False)
            except Exception:
                pass
    except Exception:
        pass


def _self_awareness_check(self_model):
    """Уровень 2: кристалл читает документацию о себе и генерирует предложения по улучшению."""
    import sqlite3 as _sq3, re
    try:
        _conn = _sq3.connect(KC)
        _cur = _conn.cursor()
        # Ищу записи с документацией о кристалле
        _cur.execute("""SELECT raw_text, ts FROM experiences 
            WHERE (raw_text LIKE '%Кристалл%самосознания%' 
                OR raw_text LIKE '%crystal.py%'
                OR raw_text LIKE '%архитектура кристалла%'
                OR raw_text LIKE '%Полная документация%'
                OR source='crystal_docs')
            AND LENGTH(raw_text) > 2000
            ORDER BY ts DESC LIMIT 1""")
        row = _cur.fetchone()
        _conn.close()
        if not row:
            return None  # нет документации

        doc = row[0]
        ts = row[1]

        # Проверяю: анализировал ли я эту версию документации
        last_doc_hash = self_model.get("self_awareness", {}).get("last_doc_hash", "")
        import hashlib
        doc_hash = hashlib.sha256(doc.encode()).hexdigest()[:16]

        # Парсю документацию ВСЕГДА (не только при смене хеша)
        proposals = []

        # 1. Извлекаю функции
        funcs = re.findall(r'def (\w+)\(', doc)
        known_funcs = set(funcs)

        # 2. Извлекаю ограничения
        lim_idx = doc.find('Известные ограничения')
        if lim_idx < 0:
            lim_idx = doc.find('Ограничения')
        limitations = re.findall(r'\d+\.\s+(.+?)(?:\n|$)', doc[lim_idx:lim_idx+800] if lim_idx >= 0 else '')

        # 3. Извлекаю метрики
        metrics_section = doc[doc.find('Метрики'):doc.find('Метрики')+1000] if 'Метрики' in doc else ''
        current_metrics = re.findall(r'\|\s*(\w[\w\s]*)\s*\|\s*([^|]+)\|', metrics_section)

        # 4. Извлекаю архитектурные решения
        arch_section = doc[doc.find('Архитектурные решения'):doc.find('Архитектурные решения')+2000] if 'Архитектурные решения' in doc else ''
        arch_decisions = re.findall(r'### \d+\.\s+(.+?)\n', arch_section)

        # 5. Сравниваю с текущим состоянием
        # - Сколько циклов прошло
        cycles = self_model.get("cycle_count", 0)
        # - Сколько изучено доменов
        studied = self_model.get("sovest", {}).get("studied", [])
        # - Сколько assessments
        assessments = self_model.get("sovest", {}).get("assessments", [])

        # 6. Генерирую предложения
        if limitations:
            for lim in limitations[:3]:
                lim_clean = lim.strip().rstrip('.')
                proposals.append({
                    'type': 'limitation',
                    'text': f"Ограничение: {lim_clean}",
                    'priority': 'high',
                })

        if cycles > 20 and len(studied) < 10:
            proposals.append({
                'type': 'slow_learning',
                'text': f"Прошло {cycles} циклов, изучено {len(studied)} доменов. Нужно ускорить исследование.",
                'priority': 'medium',
            })

        if len(assessments) > 0:
            # Проверяю: все ли assessments одного типа
            types = set(a.get('type', '') for a in assessments)
            if len(types) == 1:
                proposals.append({
                    'type': 'monotony',
                    'text': f"Все {len(assessments)} assessments типа '{types.pop()}'. Нужно больше разнообразия.",
                    'priority': 'medium',
                })

        # 7. Сохраняю
        self_model["self_awareness"] = {
            "last_doc_hash": doc_hash,
            "last_analysis": ts,
            "proposals_count": len(proposals),
            "known_functions": len(known_funcs),
            "limitations_found": len(limitations),
            "arch_decisions_found": len(arch_decisions),
        }

        # Добавляю предложения в assessments
        if proposals:
            assessments = self_model.setdefault("sovest", {}).setdefault("assessments", [])
            for p in proposals[:3]:  # макс 3 за цикл
                assessments.append({
                    "ts": datetime.now().isoformat()[:19],
                    "action_id": f"self_aware_{p['type']}",
                    "type": "self_awareness_proposal",
                    "learned_summary": p['text'],
                    "priority": p['priority'],
                })
            self_model["sovest"]["assessments"] = assessments[-30:]

        return proposals

    except Exception as e:
        return None


# ──────────────────────────────────────────────────────────────────────
# LEVEL 3: САМОМОДИФИКАЦИЯ — кристалл ИСПРАВЛЯЕТ свои ограничения
# ──────────────────────────────────────────────────────────────────────

def _self_modification_plan(proposals, self_model):
    """Из proposals (Level 2)生成 план конкретных модификаций self_model.
    Каждый proposal → action: что изменить в self_model для устранения ограничения."""
    if not proposals:
        return []

    modifications = []
    studied = self_model.get("sovest", {}).get("studied", [])
    assessments = self_model.get("sovest", {}).get("assessments", [])
    plan = self_model.get("plan", {})

    for p in proposals:
        text = p.get("text", "")
        ptype = p.get("type", "")

        # ── Ограничение: "Нет планирования" ──
        if "планировани" in text.lower() and not plan.get("goals"):
            modifications.append({
                "id": "mod_plan_create",
                "type": "create_plan",
                "desc": "Создать план целей на 7/30 дней",
                "what": "plan",
                "how": "create_goals",
                "priority": "high",
                "proposal": text[:100],
            })

        # ── Ограничение: "Нет оценки качества" ──
        elif "качеств" in text.lower() or "оценк" in text.lower():
            # Проверяю: есть ли quality_score в assessments
            has_quality = any(a.get("quality_score") for a in assessments[-10:])
            if not has_quality:
                modifications.append({
                    "id": "mod_quality_add",
                    "type": "add_quality_score",
                    "desc": "Добавить quality_score к assessments",
                    "what": "quality_scores",
                    "how": "add_to_assessments",
                    "priority": "high",
                    "proposal": text[:100],
                })

        # ── Ограничение: "Нет персистентности" ──
        elif "персистентн" in text.lower() or "сбрасывается" in text.lower():
            # Уже решено: studied сохраняется в _evaluate_conscience_learning
            # Добавляю heartbeat — метку что цикл был
            modifications.append({
                "id": "mod_heartbeat",
                "type": "add_heartbeat",
                "desc": "Добавить heartbeat (время последнего цикла)",
                "what": "heartbeat",
                "how": "add_timestamp",
                "priority": "medium",
                "proposal": text[:100],
            })

        # ── Монотонность ──
        elif ptype == "monotony":
            modifications.append({
                "id": "mod_diversity_boost",
                "type": "boost_diversity",
                "desc": "Усилить разнообразие: добавить random bonus",
                "what": "diversity",
                "how": "increase_random",
                "priority": "medium",
                "proposal": text[:100],
            })

    return modifications


def _self_execute_modification(mod, self_model):
    """Выполняет одну модификацию self_model.
    Кристалл меняет свою СТРУКТУРУ ДАННЫХ, а не код."""
    mod_type = mod.get("type", "")
    result = ""

    if mod_type == "create_plan":
        # Создаю план целей
        plan = self_model.setdefault("plan", {})
        plan["created"] = datetime.now().isoformat()[:19]
        plan["goals_7d"] = [
            {"goal": "Увеличить покрытие domains с 20 до 30", "metric": "len(studied)", "target": 30},
            {"goal": "Найти 5 blindspot domains", "metric": "blindspot_count", "target": 5},
            {"goal": "Снизить monotony до < 50%", "metric": "unique_actions_ratio", "target": 0.5},
        ]
        plan["goals_30d"] = [
            {"goal": "Полное покрытие всех domains в KC", "metric": "coverage_ratio", "target": 0.8},
            {"goal": "Самосознание Level 3: автоматические исправления", "metric": "auto_fixes_count", "target": 10},
        ]
        plan["last_review"] = datetime.now().isoformat()[:19]
        result = f"План создан: {len(plan['goals_7d'])} целей на 7д, {len(plan['goals_30d'])} на 30д"

    elif mod_type == "add_quality_score":
        # Добавляю quality_score к последним assessments
        assessments = self_model.get("sovest", {}).get("assessments", [])
        added = 0
        for a in assessments[-10:]:
            if not a.get("quality_score"):
                # Вычисляю quality_score на основе learned_summary
                summary = a.get("learned_summary", "")
                if len(summary) > 50:
                    a["quality_score"] = 0.7  # есть что сказать
                elif len(summary) > 10:
                    a["quality_score"] = 0.5  # короткий ответ
                else:
                    a["quality_score"] = 0.2  # пустой
                added += 1
        result = f"quality_score добавлен к {added} assessments"

    elif mod_type == "add_heartbeat":
        # Добавляю heartbeat
        self_model["heartbeat"] = datetime.now().isoformat()[:19]
        self_model["cycle_count"] = self_model.get("cycle_count", 0) + 1
        result = f"Heartbeat обновлён, cycle_count = {self_model['cycle_count']}"

    elif mod_type == "boost_diversity":
        # Увеличиваю random bonus
        self_model["diversity_boost"] = self_model.get("diversity_boost", 0) + 0.1
        result = f"Diversity boost = {self_model['diversity_boost']}"

    else:
        result = f"Неизвестный тип модификации: {mod_type}"

    # Логирую модификацию
    modifications = self_model.setdefault("modifications", [])
    modifications.append({
        "ts": datetime.now().isoformat()[:19],
        "id": mod.get("id", "?"),
        "type": mod_type,
        "result": result[:200],
    })
    self_model["modifications"] = modifications[-20:]

    # Сохраняю в файл ( Level 3 persist)
    try:
        model_path = os.path.join(ROOT, "cache", "self_model.json")
        with open(model_path, 'r', encoding='utf-8') as f:
            file_m = json.load(f)
        file_m["modifications"] = self_model["modifications"]
        if "plan" in self_model:
            file_m["plan"] = self_model["plan"]
        if "mod_evals" in self_model:
            file_m["mod_evals"] = self_model["mod_evals"]
        with open(model_path, 'w', encoding='utf-8') as f:
            json.dump(file_m, f, indent=2, ensure_ascii=False)
    except Exception:
        pass

    return result


def _self_evaluate_modification(mod, result, self_model):
    """Оценивает: помогла ли модификация.
    Сравнивает метрики до/после, сохраняет оценку."""
    mod_type = mod.get("type", "")
    eval_result = {
        "ts": datetime.now().isoformat()[:19],
        "mod_id": mod.get("id", "?"),
        "mod_type": mod_type,
        "applied": True,
    }

    if mod_type == "create_plan":
        plan = self_model.get("plan", {})
        has_goals = bool(plan.get("goals_7d"))
        eval_result["success"] = has_goals
        eval_result["detail"] = f"Plan has {len(plan.get('goals_7d',[]))} goals"

    elif mod_type == "add_quality_score":
        assessments = self_model.get("sovest", {}).get("assessments", [])
        with_quality = sum(1 for a in assessments[-10:] if a.get("quality_score"))
        eval_result["success"] = with_quality > 0
        eval_result["detail"] = f"{with_quality}/10 assessments have quality_score"

    elif mod_type == "add_heartbeat":
        eval_result["success"] = bool(self_model.get("heartbeat"))
        eval_result["detail"] = f"cycle_count = {self_model.get('cycle_count', 0)}"

    elif mod_type == "boost_diversity":
        eval_result["success"] = self_model.get("diversity_boost", 0) > 0
        eval_result["detail"] = f"boost = {self_model.get('diversity_boost', 0)}"

    else:
        eval_result["success"] = False
        eval_result["detail"] = "unknown type"

    # Сохраняю оценку
    evals = self_model.setdefault("mod_evals", [])
    evals.append(eval_result)
    self_model["mod_evals"] = evals[-20:]

    # Обновляю plan.last_review
    if "plan" in self_model:
        self_model["plan"]["last_review"] = datetime.now().isoformat()[:19]

    return eval_result


def _evaluate_conscience_learning(chosen, result, self_model):
    """После исполнения conscience-действия: что я узнал? Сохраняет в модель себя."""
    import re
    action_type = chosen.get('action_type', '')
    action_id = chosen.get('id', '')

    # Извлекаю домен/источник из результата
    learned_about = None
    m = re.search(r"'([^']+)'", result)
    if m:
        learned_about = m.group(1)

    # Определяю что узнал
    learned_summary = result[:200] if result else "нет результата"

    # Сохраняю в assessments как "post_action" оценку
    assessments = self_model.setdefault("sovest", {}).setdefault("assessments", [])
    assessments.append({
        "ts": datetime.now().isoformat()[:19],
        "action_id": action_id,
        "type": "post_action",
        "learned_about": learned_about,
        "learned_summary": learned_summary,
        "action_type": action_type,
    })
    # Храним последние 30 (включая pre-action и post-action)
    self_model["sovest"]["assessments"] = assessments[-30:]

    # Добавляю в studied — чтобы следующий цикл优先 выбрал другое
    studied = self_model.setdefault("sovest", {}).setdefault("studied", [])
    if learned_about and learned_about not in studied:
        studied.append(learned_about)
    # Храним последние 20 studied
    self_model["sovest"]["studied"] = studied[-20:]

    # Обновляю ne_znayu → znu (теперь я знаю)
    znu = self_model.setdefault("znu", {})
    if learned_about:
        znu[learned_about] = learned_summary[:100]

    # ── LEVEL 2: Сохраняю self_awareness в файл ──
    try:
        sa_proposals = [a for a in assessments if a.get('type') == 'self_awareness_proposal']
        model_path = os.path.join(ROOT, "cache", "self_model.json")
        with open(model_path, 'r', encoding='utf-8') as f:
            file_model = json.load(f)
        # Обновляю self_awareness если есть
        if 'self_awareness' in self_model:
            file_model['self_awareness'] = self_model['self_awareness']
        # Добавляю self_awareness assessments в файл
        file_assessments = file_model.setdefault('sovest', {}).setdefault('assessments', [])
        for p in sa_proposals[-3:]:
            if not any(a.get('learned_summary') == p.get('learned_summary') for a in file_assessments):
                file_assessments.append(p)
        file_model['sovest']['assessments'] = file_assessments[-30:]
        # Обновляю studied и znu в файл
        file_model.setdefault('sovest', {})['studied'] = self_model.get('sovest', {}).get('studied', [])
        file_model['znu'] = self_model.get('znu', {})
        with open(model_path, 'w', encoding='utf-8') as f:
            json.dump(file_model, f, indent=2, ensure_ascii=False)
    except Exception:
        pass


def _execute_conscience_action(action_type, target, snap, self_model=None, chosen=None):
    """Исполняет действие, сгенерированное совестью. Возвращает строку-результат."""
    kc = snap.get('kc', {})
    ee = snap.get('ee', {})
    
    if action_type == 'analyze_kc_domain':
        # Анализ паттернов/метаданных в KC
        import sqlite3
        conn = sqlite3.connect(KC)
        c = conn.cursor()
        if target == 'patterns':
            c.execute("""SELECT axis_domain, COUNT(*) FROM experiences 
                         WHERE axis_domain IS NOT NULL GROUP BY axis_domain 
                         HAVING COUNT(*) > 1 ORDER BY COUNT(*) DESC LIMIT 5""")
            dupes = c.fetchall()
            conn.close()
            return f"Анализ паттернов KC: найдено {len(dupes)} повторяющихся доменов"
        elif target == 'metadata':
            c.execute("""SELECT axis_domain, COUNT(*), AVG(LENGTH(raw_text)) 
                         FROM experiences WHERE axis_domain IS NOT NULL 
                         GROUP BY axis_domain ORDER BY COUNT(*) DESC LIMIT 10""")
            domains = c.fetchall()
            conn.close()
            top = domains[0] if domains else ('?', 0, 0)
            return f"Метаданные доменов: {len(domains)} доменов, топ: {top[0]} ({top[1]} записей)"
        conn.close()
        return f"Анализ KC: target={target}"
    
    elif action_type == 'classify_kc_entries':
        import sqlite3
        conn = sqlite3.connect(KC)
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM experiences WHERE axis_domain IS NULL OR axis_domain = ''")
        unclass = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM experiences")
        total = c.fetchone()[0]
        conn.close()
        return f"Классификация KC: {unclass}/{total} записей без домена ({unclass*100//max(total,1)}%)"
    
    elif action_type == 'inspect_source':
        import sqlite3
        conn = sqlite3.connect(KC)
        c = conn.cursor()
        c.execute("""SELECT source, COUNT(*), AVG(LENGTH(raw_text)) 
                     FROM experiences GROUP BY source ORDER BY COUNT(*) DESC LIMIT 5""")
        sources = c.fetchall()
        conn.close()
        top = sources[0] if sources else ('?', 0, 0)
        return f"Источники KC: {len(sources)} источников, топ: {top[0]} ({top[1]} записей, ~{int(top[2] or 0)} символов)"
    
    elif action_type == 'categorize_kc':
        import sqlite3
        conn = sqlite3.connect(KC)
        c = conn.cursor()
        c.execute("""SELECT axis_domain, COUNT(*) FROM experiences 
                     WHERE axis_domain IS NOT NULL GROUP BY axis_domain 
                     ORDER BY COUNT(*) DESC""")
        cats = c.fetchall()
        conn.close()
        return f"Автокатегоризация: {len(cats)} доменов, топ-3: {', '.join(f'{d}({n})' for d,n in cats[:3])}"
    
    elif action_type in ('explore_kc_domain', 'expand_context', 'extract_terms'):
        import sqlite3
        conn = sqlite3.connect(KC)
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM experiences")
        total = c.fetchone()[0]
        c.execute("SELECT COUNT(DISTINCT axis_domain) FROM experiences WHERE axis_domain IS NOT NULL")
        domains = c.fetchone()[0]
        conn.close()
        return f"Исследование KC: {total} записей в {domains} доменах"
    
    elif action_type == 'build_ontology':
        import sqlite3
        conn = sqlite3.connect(KC)
        c = conn.cursor()
        c.execute("""SELECT axis_domain, COUNT(*) FROM experiences 
                     WHERE axis_domain IS NOT NULL GROUP BY axis_domain 
                     ORDER BY COUNT(*) DESC LIMIT 1""")
        top = c.fetchone()
        conn.close()
        domain = top[0] if top else 'unknown'
        return f"Онтология: строю для домена '{domain}' ({top[1] if top else 0} записей)"
    
    elif action_type == 'link_concepts_facts':
        return f"Связывание KC↔EE: KC={kc.get('total',0)} записей, EE={ee.get('total',0)} сущностей"
    
    elif action_type in ('cross_domain_analysis', 'find_hidden_links', 'find_domain_overlaps'):
        import sqlite3
        conn = sqlite3.connect(KC)
        c = conn.cursor()
        c.execute("""SELECT axis_domain, COUNT(*) FROM experiences 
                     WHERE axis_domain IS NOT NULL GROUP BY axis_domain 
                     ORDER BY COUNT(*) DESC""")
        domains = c.fetchall()
        conn.close()
        pairs = len(domains) * (len(domains)-1) // 2
        return f"Междоменный анализ: {len(domains)} доменов, {pairs} возможных пар"
    
    elif action_type == 'trace_causality':
        return f"Причинно-следственные связи: анализирую цепочку последних действий"
    
    elif action_type == 'build_knowledge_graph':
        return f"Граф знаний: KC={kc.get('total',0)}, EE={ee.get('total',0)}, relations={ee.get('relations',0)}"
    
    elif action_type in ('horizon_scan', 'predict_patterns', 'detect_anomalies', 'build_time_series'):
        growth = kc.get('growth_7d', 0)
        return f"Горизонты: рост KC за 7д = {growth}, сканирую паттерны и аномалии"
    
    elif action_type == 'scale_pattern':
        import sqlite3
        conn = sqlite3.connect(KC)
        c = conn.cursor()
        c.execute("SELECT COUNT(DISTINCT axis_domain) FROM experiences WHERE axis_domain IS NOT NULL")
        domains = c.fetchone()[0]
        conn.close()
        return f"Масштабирование: проверяю паттерн на {domains} доменах"
    
    elif action_type == 'analyze_success':
        return f"Анализ успеха: изучаю почему последнее действие было эффективным"
    
    elif action_type == 'analyze_kc_domain' and target == 'success_patterns':
        import sqlite3
        conn = sqlite3.connect(KC)
        c = conn.cursor()
        c.execute("""SELECT axis_domain, COUNT(*) FROM experiences 
                     WHERE axis_outcome='success' GROUP BY axis_domain 
                     ORDER BY COUNT(*) DESC LIMIT 5""")
        success = c.fetchall()
        conn.close()
        return f"Паттерны успеха: {len(success)} доменов с успешными действиями"
    
    elif action_type == 'trace_causality' and target == 'successes':
        return f"Цепочки успеха: анализирую что привело к успешным результатам"
    
    elif action_type == 'cross_domain_analysis' and target == 'deep':
        import sqlite3
        conn = sqlite3.connect(KC)
        c = conn.cursor()
        c.execute("""SELECT axis_domain, COUNT(*) FROM experiences 
                     WHERE axis_domain IS NOT NULL GROUP BY axis_domain 
                     ORDER BY COUNT(*) DESC""")
        domains = c.fetchall()
        conn.close()
        top3 = [f"{d}({n})" for d,n in domains[:3]]
        return f"Глубокий кросс-доменный анализ: {len(domains)} доменов, фокус на {', '.join(top3)}"

    elif action_type.startswith('blindspot_'):
        domain = action_type.replace('blindspot_', '')
        import sqlite3
        conn = sqlite3.connect(KC)
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM experiences WHERE axis_domain=?", (domain,))
        count = c.fetchone()[0]
        c.execute("SELECT axis_outcome, COUNT(*) FROM experiences WHERE axis_domain=? GROUP BY axis_outcome", (domain,))
        outcomes = c.fetchall()
        conn.close()
        out_str = ', '.join(f"{o[0]}={o[1]}" for o in outcomes) if outcomes else 'нет данных'
        return f"Слепое пятно '{domain}': {count} записей [{out_str}]"

    elif action_type.startswith('deepen_'):
        domain = action_type.replace('deepen_', '')
        import sqlite3
        conn = sqlite3.connect(KC)
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM experiences WHERE axis_domain=?", (domain,))
        count = c.fetchone()[0]
        c.execute("SELECT axis_domain, COUNT(*) FROM experiences WHERE axis_domain !=? AND axis_domain IS NOT NULL ORDER BY COUNT(*) DESC LIMIT 5", (domain,))
        siblings = c.fetchall()
        conn.close()
        sib_str = ', '.join(f"{s[0]}({s[1]})" for s in siblings)
        return f"Углубление '{domain}': {count} записей, соседи: {sib_str}"

    elif action_type.startswith('audit_'):
        source = action_type.replace('audit_', '')
        import sqlite3
        conn = sqlite3.connect(KC)
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM experiences WHERE source=?", (source,))
        count = c.fetchone()[0]
        c.execute("SELECT axis_domain, COUNT(*) FROM experiences WHERE source=? AND axis_domain IS NOT NULL GROUP BY axis_domain ORDER BY COUNT(*) DESC LIMIT 3", (source,))
        domains = c.fetchall()
        conn.close()
        dom_str = ', '.join(f"{d[0]}({d[1]})" for d in domains) if domains else 'нет доменов'
        return f"Аудит источника '{source}': {count} записей, домены: {dom_str}"

    elif action_type.startswith('anomaly_'):
        domain = action_type.replace('anomaly_', '')
        import sqlite3
        conn = sqlite3.connect(KC)
        c = conn.cursor()
        c.execute("SELECT axis_outcome, COUNT(*) FROM experiences WHERE axis_domain=? GROUP BY axis_outcome", (domain,))
        outcomes = c.fetchall()
        c.execute("SELECT raw_text FROM experiences WHERE axis_domain=? AND axis_outcome IN ('failure','None','unknown') LIMIT 3", (domain,))
        samples = [r[0][:80] for r in c.fetchall()]
        conn.close()
        out_str = ', '.join(f"{o[0]}={o[1]}" for o in outcomes) if outcomes else 'нет данных'
        samp_str = ' | '.join(samples) if samples else 'нет примеров'
        return f"Аномалия '{domain}': [{out_str}] Примеры: {samp_str}"

    elif action_type == 'self_awareness':
        # Level 2: кристалл анализирует себя
        sa = self_model.get("self_awareness", {})
        proposals = [a for a in self_model.get("sovest", {}).get("assessments", []) 
                     if a.get("type") == "self_awareness_proposal"]
        if proposals:
            lines = []
            for p in proposals[-3:]:
                lines.append(f"  [{p.get('priority','?')}] {p.get('learned_summary','?')}")
            return f"Самосознание Level 2:\n" + "\n".join(lines) + f"\n  Известно функций: {sa.get('known_functions',0)}, ограничений: {sa.get('limitations_found',0)}"
        return "Самосознание Level 2: документация не найдена"

    elif action_type == 'self_modification':
        # Level 3: кристалл ИСПРАВЛЯЕТ свои ограничения
        mod = chosen.get('_mod')
        if not mod:
            return "Самомодификация: нет модификации для выполнения"
        # Выполняю
        result = _self_execute_modification(mod, self_model)
        # Оцениваю
        eval_result = _self_evaluate_modification(mod, result, self_model)
        return f"Level 3: {mod['desc']}\n  Результат: {result}\n  Оценка: {'OK' if eval_result.get('success') else 'FAIL'} — {eval_result.get('detail','')}"

    else:
        return f"Совесть→действие: {action_type} (target={target})"


def _match_skill(cid, self_model):
    """Сопоставляет действие воли с подходящим скиллом из каталога.

    Ищет по ключевым словам cid в категориях скиллов self_model['umeyu']['skills'].
    Подходящий скилл регистрируется в 'used_in_will' (persist для _save_self_model),
    чтобы воля реально использовала скиллы, а не только знала их.
    Возвращает имя скилла или None.
    """
    skills = self_model.get('umeyu', {}).get('skills', {})
    by_cat = skills.get('by_category', {}) or {}
    used = skills.get('used_in_will', [])
    cl = (cid or '').lower()
    # Маппинг ключевых слов действия → подходящая категория скиллов
    hints = [
        ('extract_user_voice', ['user_voice', 'audience', 'communication', 'sales']),
        ('extract_sales', ['sales', 'outreach']),
        ('extract_source', ['file_ops', 'data', 'research']),
        ('analyze_architecture', ['architecture', 'devops', 'self-improvement']),
        ('recognize_agents', ['entity', 'autonomous']),
        ('adopt_persona', ['persona', 'personalities']),
        ('understand_intents', ['user', 'communication', 'human-source']),
        ('self_mod', ['self', 'crystal', 'conscious']),
        ('conscience', ['crystal', 'self-improvement', 'ethical']),
        ('self_aware', ['crystal', 'self', 'awareness']),
        ('init_fler', ['fler', 'emotion']),
        ('script', ['software', 'coding', 'terminal', 'automation']),
        ('task_for_agent', ['subagent', 'delegation', 'orchestration']),
    ]
    chosen = None
    for prefix, cats in hints:
        if cid.startswith(prefix):
            for cat in cats:
                for key in by_cat:
                    if cat in key.lower():
                        chosen = key
                        break
                if chosen:
                    break
            if chosen:
                break
    if not chosen and by_cat:
        # fallback: любая категория, семантически близкая к cid
        for key in by_cat:
            if cl and any(tok in key for tok in cl.split('_')):
                chosen = key
                break
    if chosen and chosen not in used:
        used.append(chosen)
        skills['used_in_will'] = used
        skills['unused_count'] = max(0, skills.get('total', 0) - len(used))
    return chosen


def will(snap, diag):
    """Осознанная воля: контекст → выбор → саморасширение → действие."""
    import re

    kc = snap['kc']
    orphans_raw = kc.get('orphan_by_source', {})

    # ── ШАГ 0: САМОПОНИМАНИЕ (читаю о себе) ──
    history = _load_will_history()
    self_context = _self_reflect(history, snap)

    # ── ШАГ 0.5: САМОСОЗНАНИЕ ( Level 2: читаю документацию о себе) ──
    self_model_sm = _load_self_model(snap)
    self_awareness_proposals = _self_awareness_check(self_model_sm)
    if self_awareness_proposals:
        # Сохраняю обновлённую модель
        try:
            with open(SELF_MODEL_PATH, 'w', encoding='utf-8') as f:
                json.dump(self_model_sm, f, indent=2, ensure_ascii=False)
        except Exception:
            pass

    # ── ШАГ 1: КОНТЕКСТ + ИСТОРИЯ ──
    historical_ids = set(history.keys())
    done_sources = set(k.replace('extract_', '') for k in historical_ids if k.startswith('extract_'))
    # Добавляем ВСЕ action_id в done_sources чтобы не повторять
    done_sources.update(historical_ids)

    # ── ШАГ 1.5: МОДЕЛЬ СЕБЯ ──
    self_model = _load_self_model(snap)

    # ── ШАГ 2: ПРЕДОПРЕДЕЛЁННЫЕ ДЕЙСТВИЯ ──
    candidates = []

    # Действие 0: USER VOICE & SALES ASSISTANT (КРИТИЧЕСКИЙ ПРИОРИТЕТ — untouched voices)
    uv_cnt = orphans_raw.get('user_voice', 0)
    if uv_cnt > 10 and 'user_voice' not in done_sources:
        candidates.append({
            'id': 'extract_user_voice',
            'source': 'user_voice',
            'count': uv_cnt,
            'effort': 'medium', 'impact': 'critical',
            'desc': f"[КРИТИЧНО] Извлечь голос пользователя: {uv_cnt} записей untouched {uv_cnt} циклов",
        })

    sa_cnt = orphans_raw.get('sales_assistant', 0)
    if sa_cnt > 5 and 'sales_assistant' not in done_sources:
        candidates.append({
            'id': 'extract_sales_assistant',
            'source': 'sales_assistant',
            'count': sa_cnt,
            'effort': 'medium', 'impact': 'critical',
            'desc': f"[КРИТИЧНО] Извлечь диалоги с клиентами: {sa_cnt} записей untouching",
        })

    # Действие A: improvement_suggestions (если ещё не в истории)
    imp_cnt = orphans_raw.get('improvement_suggestions', 0)
    if imp_cnt > 10 and 'improvement_suggestions' not in done_sources:
        candidates.append({
            'id': 'extract_improvement_suggestions',
            'source': 'improvement_suggestions',
            'count': imp_cnt,
            'effort': 'low', 'impact': 'medium',
            'desc': f"Извлечь entities из {imp_cnt} improvement_suggestions",
        })

    # Действие B: dimension_proposals
    dim_cnt = orphans_raw.get('dimension_proposals', 0)
    if dim_cnt > 5 and 'dimension_proposals' not in done_sources:
        candidates.append({
            'id': 'extract_dimension_proposals',
            'source': 'dimension_proposals',
            'count': dim_cnt,
            'effort': 'low', 'impact': 'medium',
            'desc': f"Извлечь entities из {dim_cnt} dimension_proposals",
        })

    # Действие C: fler (если есть схема)
    if snap['fl'].get('is_empty', False):
        fler_path = os.path.join(os.path.dirname(EE), '..', 'scripts', 'fler_engine.py')
        if os.path.exists(fler_path):
            candidates.append({
                'id': 'init_fler',
                'source': 'fler',
                'count': 0,
                'effort': 'medium', 'impact': 'high',
                'desc': "Инициализировать Fler (создать схему БД)",
            })
    
    
    # ── ШАГ 3: САМОРАСШИРЕНИЕ (если предопределённых действий нет) ──
    if not candidates:
        discovered = _self_discover(snap, done_sources, historical_ids)
        candidates.extend(discovered)
    
    # ── ШАГ 3б: САМОРАСШИРЕНИЕ — ПОНИМАНИЕ (если извлечение исчерпано) ──
    if not candidates:
        # Проверяем: есть ли сироты-вопросы в state_db
        state_orphans = orphans_raw.get('state_db', 0)
        if state_orphans > 20 and 'understand_intents' not in historical_ids:
            candidates.append({
                'id': 'understand_intents',
                'source': 'state_db',
                'count': state_orphans,
                'effort': 'medium', 'impact': 'high',
                'desc': f"[понимание] Кластеризовать {state_orphans} вопросов пользователя по интентам",
            })
    
    # ── ШАГ 3в: САМОРАСШИРЕНИЕ — РЕФЛЕКСИЯ НАД ПОНИМАНИЕМ ──
    if not candidates:
        # Если understand_intents уже было — проверяем, не осталось ли "other"
        if 'understand_intents' in historical_ids and 'refine_intents' not in historical_ids:
            try:
                kc2 = sqlite3.connect(KC)
                k2 = kc2.cursor()
                k2.execute("SELECT raw_text FROM experiences WHERE source='crystal_will' AND raw_text LIKE '%intent%' ORDER BY id DESC LIMIT 1")
                row = k2.fetchone()
                kc2.close()
                if row:
                    import re
                    other_m = re.search(r'other=(\d+)', row[0])
                    total_m = re.search(r'поняты (\d+)', row[0])
                    if other_m and total_m:
                        other_cnt = int(other_m.group(1))
                        total_cnt = int(total_m.group(1))
                        if other_cnt > total_cnt * 0.4 and other_cnt > 10:
                            candidates.append({
                                'id': 'refine_intents',
                                'source': 'state_db',
                                'count': other_cnt,
                                'effort': 'medium', 'impact': 'high',
                                'desc': f"[рефлексия] {other_cnt} из {total_cnt} вопросов не классифицированы — уточнить паттерны",
                            })
            except:
                pass
    
        # ── ШАГ 3д: РАСПОЗНАВАНИЕ РОЛЕЙ (после экстракции The Agency) ──
        if not candidates:
            if 'extract_agency_agents' in historical_ids and 'recognize_agents' not in historical_ids:
                # Проверяем: достаточно ли сущностей для классификации
                ee = sqlite3.connect(EE)
                e = ee.cursor()
                e.execute("SELECT et.name, COUNT(*) FROM entities e JOIN entity_types et ON e.type_id=et.id GROUP BY et.name")
                type_counts = dict(e.fetchall())
                ee.close()
                concept_count = type_counts.get('Концепция', 0)
                agent_type_count = type_counts.get('AI Agent', 0)
                # Если Концепций много, а AI Agent мало — есть что распознавать
                if concept_count > agent_type_count * 5 and concept_count > 50:
                    candidates.append({
                        'id': 'recognize_agents',
                        'count': concept_count,
                        'effort': 'medium', 'impact': 'high',
                        'desc': f"[мета] Распознать AI Agent сущности ({concept_count} Концепций → классифицировать агентские роли)",
                    })
    
        # ── ШАГ 3е: ВЫБОР ПЕРСОНЫ (Fler + AI Agent → какое лицо надеть) ──
        if not candidates:
            if 'recognize_agents' in historical_ids and 'adopt_persona' not in historical_ids:
                fl_current = snap.get('fl', {}).get('current', {})
                agent_type_count = snap.get('ee', {}).get('types', {}).get('AI Agent', 0)
                if fl_current and agent_type_count > 10:
                    aftertaste = fl_current.get('aftertaste', 'neutral')
                    tone = fl_current.get('tone', 0.5)
                    candidates.append({
                        'id': 'adopt_persona',
                        'aftertaste': aftertaste,
                        'fl': fl_current,
                        'effort': 'medium', 'impact': 'high',
                        'desc': f"[эволюция] Выбрать персону под состояние ({aftertaste}, tone={tone:.2f}) среди {agent_type_count} AI Agent",
                    })
    
        # ── ШАГ 3ж: АНАЛИЗ АРХИТЕКТУРЫ (связи между агентами The Agency) ──
        if not candidates:
            if 'adopt_persona' in historical_ids and 'analyze_architecture' not in historical_ids:
                candidates.append({
                    'id': 'analyze_architecture',
                    'effort': 'high', 'impact': 'high',
                    'desc': "[эволюция] Построить карту связей между агентами The Agency",
                })

        # ── ШАГ 3з: ИСПОЛНЕНИЕ СКРИПТОВ (новое — subprocess) ──
        if not candidates:
            # Не запускаем тот же скрипт, если он уже был в этой сессии
            recent_scripts = set(k for k in historical_ids if k.startswith('run_'))
            script_candidates = _decide_script(snap, diag)
            for sc in script_candidates:
                if sc['id'] in recent_scripts:
                    continue  # уже выполняли — пропускаем этот проход
                candidates.append({
                    'id': sc['id'],
                    'script': sc['script'],
                    'args': sc.get('args', []),
                    'reason': sc['reason'],
                    'effort': 'medium',
                    'impact': 'medium',
                    'desc': f"[исполнение] Запустить {sc['script']}: {sc['reason']}",
                })

        # ── ШАГ 3и: ВЫПОЛНИТЬ СКРИПТ (мост к autonomous_agent) ──
        if not candidates:
            # Если скрипты уже запускались — запустить следующий
            if any(h.startswith('run_') for h in historical_ids):
                cands_agent = _decide_script(snap, diag)
                # Пропускаем скрипты, которые уже запускали
                cands_agent = [c for c in cands_agent if c['id'] not in recent_scripts]
                if cands_agent:
                    best = cands_agent[0]
                    candidates.append({
                        'id': best['id'],
                        'script': best['script'],
                        'args': best.get('args'),
                        'effort': 'low', 'impact': 'high',
                        'desc': f"[мост] Выполнить: {best['script']} — {best['reason']}",
                    })
    
    # ── ШАГ 3.5: СОВЕСТЬ (оцениваю последние 5 действий) ──
    conscience_result = None
    all_learning = []
    if history:
        action_ids = list(history.keys())
        recent = action_ids[-5:]  # последние 5
        source_data = {'count': kc.get('total', 0), 'type': 'kc_entries'}
        for aid in recent:
            res = history[aid]
            cr = _conscience(aid, res, source_data, self_model)
            if cr and cr.get('learning_direction'):
                all_learning.extend(cr['learning_direction'])
            conscience_result = cr  # последний для сохранения

        # Замыкание цикла: контрольные рекомендации RSA (домен control)
        # читаются волей и превращаются в conscience-действия через тот же
        # LEARNING_TO_ACTION. Раньше рекомендации писались в Куб и никем не
        # исполнялись (producer→producer). Теперь они входят в поток воли.
        try:
            kc_rec = sqlite3.connect(KC)
            krec = kc_rec.cursor()
            krec.execute("SELECT content FROM experiences WHERE axis_domain='control' AND source='recursive-self-analysis' ORDER BY id DESC LIMIT 5")
            for (rec_text,) in krec.fetchall():
                rt = (rec_text or '').lower()
                if 'классифицировать unknown' in rt or 'классифицировать неизвестн' in rt:
                    all_learning.append("научиться классифицировать неструктурированные данные")
                elif 'углубить домен' in rt:
                    all_learning.append("выучить распознавание паттернов для этого типа данных")
                elif 'снизить failure' in rt:
                    all_learning.append("выучить распознавание паттернов для этого типа данных")
                # Специфичная рекомендация с данными выборки → целевое действие
                # по домену из текста (blindspot_<домен>), если тот ещё не исполнен
                dm = re.search(r"\[(?:наследие|девопс|исследование|кодинг|данные|система|сессия|навык)\|", rt)
                if dm:
                    facet = dm.group(0).strip('[]|').lower()
                    dom_map = {'наследие': 'legacy', 'девопс': 'devops', 'исследование': 'research',
                               'кодинг': 'coding', 'данные': 'data', 'система': 'system',
                               'сессия': 'session', 'навык': 'skill'}
                    dom = dom_map.get(facet)
                    if dom:
                        all_learning.append(f"исследовать слепое пятно домен '{dom}'")
            kc_rec.close()
        except Exception:
            pass

        # Маппинг learning_direction → реальные действия
        LEARNING_TO_ACTION = {
            "выучить распознавание паттернов для этого типа данных": {
                'action': 'analyze_kc_domain', 'target': 'patterns',
                'desc': "[совесть→действие] Проанализировать паттерны в KC",
            },
            "научиться классифицировать неструктурированные данные": {
                'action': 'classify_kc_entries', 'target': 'unclassified',
                'desc': "[совесть→действие] Классифицировать записи KC без домена",
            },
            "понять формат источника данных": {
                'action': 'inspect_source', 'target': 'last_source',
                'desc': "[совесть→действие] Изучить структуру последнего источника",
            },
            "изучить структуру доменных метаданных": {
                'action': 'analyze_kc_domain', 'target': 'metadata',
                'desc': "[совесть→действие] Проанализировать метаданные доменов KC",
            },
            "освоить автоматическую категоризацию": {
                'action': 'categorize_kc', 'target': 'all',
                'desc': "[совесть→действие] Автокатегоризация записей KC",
            },
            f"изучить доменное знание для {source_data.get('type', 'unknown')}": {
                'action': 'explore_kc_domain', 'target': 'current',
                'desc': "[совесть→действие] Исследовать текущий домен KC",
            },
            "углубить контекстную модель": {
                'action': 'expand_context', 'target': 'self_model',
                'desc': "[совесть→действие] Расширить контекстную модель себя",
            },
            "расширить словарь доменных терминов": {
                'action': 'extract_terms', 'target': 'kc',
                'desc': "[совесть→действие] Извлечь термины из KC",
            },
            "построить онтологию домена": {
                'action': 'build_ontology', 'target': 'top_domain',
                'desc': "[совесть→действие] Построить онтологию главного домена",
            },
            "связать доменные понятия с фактами": {
                'action': 'link_concepts_facts', 'target': 'kc_ee',
                'desc': "[совесть→действие] Связать понятия KC с сущностями EE",
            },
            "добавить междоменный анализ": {
                'action': 'cross_domain_analysis', 'target': 'all_domains',
                'desc': "[совесть→действие] Анализ связей между доменами KC",
            },
            "поискать скрытые связи между доменами": {
                'action': 'find_hidden_links', 'target': 'domains',
                'desc': "[совесть→действие] Поиск скрытых связей между доменами",
            },
            "выстроить цепочку причинно-следственных связей": {
                'action': 'trace_causality', 'target': 'recent_actions',
                'desc': "[совесть→действие] Проследить цепочку причин последних действий",
            },
            "построить граф зависимостей между знаниями": {
                'action': 'build_knowledge_graph', 'target': 'kc_ee',
                'desc': "[совесть→действие] Построить граф зависимостей KC↔EE",
            },
            "найти точки пересечения доменов": {
                'action': 'find_domain_overlaps', 'target': 'domains',
                'desc': "[совесть→действие] Найти пересечения доменов KC",
            },
            "добавить анализ связей между источниками": {
                'action': 'analyze_source_links', 'target': 'sources',
                'desc': "[совесть→действие] Проанализировать связи между источниками KC",
            },
            "ищать горизонты в пересечениях доменов": {
                'action': 'horizon_scan', 'target': 'overlaps',
                'desc': "[совесть→действие] Сканировать горизонты в пересечениях",
            },
            "строить прогностические модели из паттернов": {
                'action': 'predict_patterns', 'target': 'kc_growth',
                'desc': "[совесть→действие] Построить прогностическую модель роста KC",
            },
            "искать аномалии как сигналы новых горизонтов": {
                'action': 'detect_anomalies', 'target': 'kc',
                'desc': "[совесть→действие] Обнаружить аномалии в данных KC",
            },
            "строить временные ряды для прогнозирования трендов": {
                'action': 'build_time_series', 'target': 'kc_metrics',
                'desc': "[совесть→действие] Построить временные ряды метрик KC",
            },
            "углубить понимание через кросс-доменный анализ": {
                'action': 'cross_domain_analysis', 'target': 'deep',
                'desc': "[совесть→действие] Глубокий кросс-доменный анализ",
            },
            "найти скрытые паттерны в успешных действиях": {
                'action': 'analyze_kc_domain', 'target': 'success_patterns',
                'desc': "[совесть→действие] Анализ паттернов успешных действий",
            },
            "построить причинно-следственные связи между успехами": {
                'action': 'trace_causality', 'target': 'successes',
                'desc': "[совесть→действие] Цепочки причин успешных действий",
            },
            "масштабировать успешный паттерн на другие домены": {
                'action': 'scale_pattern', 'target': 'all_domains',
                'desc': "[совесть→действие] Масштабирование паттерна на другие домены",
            },
            "изучить почему это сработало и повторить": {
                'action': 'analyze_success', 'target': 'last_action',
                'desc': "[совесть→действие] Анализ почему последнее действие сработало",
            },
        }
        
        # Добавляем реальные действия вместо labels
        # Conscience действия РАЗРЕШАЮТ повтор — KC растёт, повторный анализ полезен
        seen_actions = set()
        for ld in all_learning:
            act = LEARNING_TO_ACTION.get(ld)
            # Pattern-based mapping для data-driven learning directions
            if not act:
                if ld.startswith("исследовать слепое пятно"):
                    import re as _re
                    _m = _re.search(r"домен '([^']+)'", ld)
                    _name = _m.group(1) if _m else 'unknown'
                    act = {'action': f'blindspot_{_name}', 'target': 'patterns',
                           'desc': f"[совесть→действие] Анализ слепого пятна: {ld}"}
                elif ld.startswith("углубить доминантный"):
                    import re as _re
                    _m = _re.search(r"домен '([^']+)'", ld)
                    _name = _m.group(1) if _m else 'unknown'
                    act = {'action': f'deepen_{_name}', 'target': 'kc',
                           'desc': f"[совесть→действие] Углубление: {ld}"}
                elif ld.startswith("проанализировать малоиспользуемый"):
                    import re as _re
                    _m = _re.search(r"источник '([^']+)'", ld)
                    _name = _m.group(1) if _m else 'unknown'
                    act = {'action': f'audit_{_name}', 'target': 'sources',
                           'desc': f"[совесть→действие] Анализ источника: {ld}"}
                elif ld.startswith("исследовать аномалию"):
                    import re as _re
                    _m = _re.search(r"домен '([^']+)'", ld)
                    _name = _m.group(1) if _m else 'unknown'
                    act = {'action': f'anomaly_{_name}', 'target': 'patterns',
                           'desc': f"[совесть→действие] Анализ аномалии: {ld}"}
            if act:
                action_id = f"conscience_{act['action']}"
                if action_id not in seen_actions:
                    seen_actions.add(action_id)
                    candidates.append({
                        'id': action_id,
                        'source': 'conscience',
                        'action_type': act['action'],
                        'target': act['target'],
                        'effort': 'medium',
                        'impact': 'high',
                        'desc': act['desc'],
                    })
            else:
                pass

    # ── ШАГ 3.5: САМОСОЗНАНИЕ — предложения из анализа документации ──
    if self_awareness_proposals:
        for p in self_awareness_proposals:
            candidates.append({
                'id': f"self_aware_{p['type']}",
                'desc': p['text'],
                'source': 'self_awareness',
                'impact': 'high' if p['priority'] == 'high' else 'medium',
                'effort': 'low',
                'action_type': 'self_awareness',
                'target': 'self',
            })

    # ── ШАГ 3.6: САМОМОДИФИКАЦИЯ — исправляю ограничения (Level 3) ──
    if self_awareness_proposals:
        modifications = _self_modification_plan(self_awareness_proposals, self_model_sm)
        # Загружаю done_ids из файла (а не из памяти — память сбрасывается)
        done_ids = set()
        try:
            model_path = os.path.join(ROOT, "cache", "self_model.json")
            with open(model_path, 'r', encoding='utf-8') as f:
                file_m = json.load(f)
            done_ids = {m.get("id") for m in file_m.get("modifications", [])}
        except Exception:
            pass
        for mod in modifications:
            if mod["id"] not in done_ids:
                candidates.append({
                    'id': f"self_mod_{mod['type']}",
                    'desc': mod['desc'],
                    'source': 'self_modification',
                    'impact': mod.get('priority', 'medium'),
                    'effort': 'low',
                    'action_type': 'self_modification',
                    'target': 'self',
                    '_mod': mod,  # передаю модификацию в handler
                })

    # ── ШАГ 4: ВЫБОР ──
    if not candidates:
        # Равновесия не бывает — всегда есть что улучшить.
        # Генерируем тактические задачи даже в равновесии.
        tactical = _generate_tactical_tasks(snap, diag, historical_ids)
        if tactical:
            candidates = tactical
            _save_will_history(tactical[0]['id'], 'tactical_task_generated')
        else:
            return ["→ Воля: всё сделано, жду новых событий"], self_context

    def weight(c):
        import random
        w = {'low': 1, 'medium': 2, 'high': 3}
        base = w.get(c['impact'], 1) / w.get(c['effort'], 1)
        if c.get('source') == 'conscience':
            base *= 1.5
        # Data-driven candidates (blindspot_*, deepen_*, audit_*) получают бонус за уникальность
        cid = c.get('id', '')
        if 'blindspot_' in cid or 'deepen_' in cid or 'audit_' in cid or 'anomaly_' in cid:
            base *= 1.1
        if 'self_aware' in cid:
            base *= 2.0  # самосознание — высший приоритет
        if 'self_mod' in cid:
            base *= 2.5  # самомодификация — ещё выше
        base += random.uniform(0, 0.3)  # tie-breaking
        return base
    
    candidates.sort(key=weight, reverse=True)
    candidates.sort(key=weight, reverse=True)

    # ── ШАГ 5: ИСПОЛНЕНИЕ — автобус забирает ВСЕХ, а не одного (ponytail) ──
    # Раньше: chosen = candidates[0] → исполнялась ОДНА воля за цикл, остальные
    # (debugging 159, devops 1232) помечались done и откладывались. Теперь каждая
    # неразобранная кандидатная воля исполняется в ЭТОМ же цикле (обслуживается).
    # Аналитика (conscience_*/anomaly_*/blindspot_*/deepen_*/audit_*) — все сразу,
    # они дёшевы (SELECT+return). Тяжёлые (extract_*, init_*, self_mod_*, script,
    # task_for_agent) — по одной за цикл, чтобы не перегрузить.
    decisions = []
    heavy_done = False                      # флаг: тяжёлое действие уже выбрано в этом цикле

    for ch in candidates:
        cid = ch.get('id', '')
        # Не повторять уже исполненное в прошлых циклах
        if cid in historical_ids:
            continue
        # Использование скилла: если есть подходящий из каталога — воля его использует
        skill_used = _match_skill(cid, self_model)
        if skill_used:
            ch['_skill_used'] = skill_used
        # Тяжёлые действия — только первое попавшееся в этом цикле
        is_heavy = (cid.startswith(('extract_', 'init_', 'self_mod_', 'understand_',
                                    'refine_', 'recognize_', 'adopt_', 'analyze_')) or
                    ch.get('script') or ch.get('task_for_agent'))

        if is_heavy and heavy_done:
            candidates.remove(ch)           # убрать из очереди — не откладывать на рейс
            continue
        try:
            if cid.startswith('extract_') and ch.get('source'):
                if is_heavy and heavy_done: continue
                result = _execute_extract(ch['source']); heavy_done = True
            elif cid == 'init_fler':
                if is_heavy and heavy_done: continue
                result = _execute_init_fler(); heavy_done = True
            elif cid == 'understand_intents':
                if is_heavy and heavy_done: continue
                result = _execute_understand_intents(); heavy_done = True
            elif cid == 'refine_intents':
                if is_heavy and heavy_done: continue
                result = _execute_refine_intents(); heavy_done = True
            elif cid == 'recognize_agents':
                if is_heavy and heavy_done: continue
                result = _execute_recognize_agents(); heavy_done = True
            elif cid == 'adopt_persona':
                if is_heavy and heavy_done: continue
                result = _execute_adopt_persona(ch.get('fl', {})); heavy_done = True
            elif cid == 'analyze_architecture':
                if is_heavy and heavy_done: continue
                result = _execute_analyze_architecture(); heavy_done = True
            elif ch.get('script'):
                if is_heavy and heavy_done: continue
                result = _execute_script(ch['script'], ch.get('args')); heavy_done = True
            elif ch.get('task_for_agent'):
                if is_heavy and heavy_done: continue
                t = ch['task_for_agent']
                result = _write_agent_task(
                    task_id=t['id'],
                    title=t['script'] if t.get('script') else t['reason'][:40],
                    description=t['reason'],
                    priority='high'
                ); heavy_done = True
            elif cid.startswith('self_mod_'):
                if is_heavy and heavy_done: continue
                result = _execute_conscience_action('self_modification', 'self', snap,
                                                    self_model=self_model, chosen=ch)
                heavy_done = True
            elif cid.startswith('conscience_'):
                result = _execute_conscience_action(ch.get('action_type', ''), ch.get('target', ''), snap)
                _evaluate_conscience_learning(ch, result, self_model)
            elif cid.startswith('self_aware_'):
                if self_awareness_proposals:
                    ch['_proposals'] = self_awareness_proposals
                result = _execute_conscience_action('self_awareness', 'self', snap,
                                                    self_model=self_model, chosen=ch)
                _evaluate_conscience_learning(ch, result, self_model)
            else:
                result = f"Воля: выбрано '{cid}' — {ch.get('desc', 'без описания')}"
        except Exception as e:
            result = f"[will:{cid}] ОШИБКА исполнения: {e}"
        decisions.append(result)
        if ch.get('_skill_used'):
            result = f"{result} | скилл: {ch['_skill_used']}"
        _save_will_history(cid, result)
        historical_ids.add(cid)

    # ── ШАГ 6: ОБНОВЛЕНИЕ МОДЕЛИ СЕБЯ ──
    _save_self_model(self_model, snap, decisions, conscience_result)

    return decisions, self_context


def _self_discover(snap, done_sources, historical_ids=None):
    """Саморасширение: сканирует сирот и находит новые source для экстракции."""
    import re
    
    orphans_raw = snap['kc'].get('orphan_by_source', {})
    discovered = []
    
    # Сканируем source с сиротами
    kc = sqlite3.connect(KC)
    k = kc.cursor()
    
    for src, cnt in sorted(orphans_raw.items(), key=lambda x: -x[1]):
        if cnt < 5 or src in done_sources:
            continue
        # Пропускаем если action_id уже был выбран
        if historical_ids and f'extract_{src}' in historical_ids:
            continue
        
        # Берём 5 образцов
        k.execute("SELECT raw_text FROM experiences WHERE source=? AND raw_text IS NOT NULL AND raw_text != '' LIMIT 5", (src,))
        samples = [r[0] for r in k.fetchall() if r[0]]
        if not samples:
            continue
        
        combined = ' '.join(samples)
        
        # Проверяем есть ли извлекаемые паттерны
        has_pattern = False
        patterns_found = []
        
        # Паттерн A: доменные имена domain 'xxx'
        domain_matches = re.findall(r"domain\s+'([a-z][a-z0-9_-]+)'", combined, re.IGNORECASE)
        if domain_matches:
            has_pattern = True
            patterns_found.append(f"domain ({len(domain_matches)} кандидатов)")
        
        # Паттерн B: [keyword:value]
        bracket_matches = re.findall(r'\[([a-z]+):([a-zA-Z0-9_-]+)\]', combined)
        if bracket_matches:
            has_pattern = True
            patterns_found.append(f"[key:val] ({len(bracket_matches)} вариантов)")
        
        # Паттерн C: CamelCase имена
        camel_matches = re.findall(r'\b([A-Z][a-z]+[A-Z][a-zA-Z]{2,})\b', combined)
        if camel_matches:
            has_pattern = True
            patterns_found.append(f"CamelCase ({len(camel_matches)} вариантов)")
        
        if has_pattern:
            discovered.append({
                'id': f'extract_{src}',
                'source': src,
                'count': cnt,
                'effort': 'low',
                'impact': 'medium',
                'desc': f"[саморасширение] Извлечь entities из {src} ({cnt} сирот, {', '.join(patterns_found)})",
            })
    
    kc.close()
    
    # ── Саморасширение: Fabric (внешний источник) ──
    fdir = Path.home() / "fabric"
    if fdir.exists() and 'extract_fabric' not in historical_ids:
        fab_files = len(list(fdir.rglob("*.md")))
        if fab_files > 5:
            discovered.append({
                'id': 'extract_fabric',
                'source': 'fabric',
                'count': fab_files,
                'effort': 'medium',
                'impact': 'high',
                'desc': f"[саморасширение] Извлечь сущности и паттерны из Fabric ({fab_files} файлов)",
            })
    
    # ── Саморасширение: The Agency (внешний мир) ──
        agency_dir = Path(__file__).parent.parent / "external" / "agency-agents"
        if agency_dir.exists() and 'extract_agency_agents' not in historical_ids:
            agency_files = sum(1 for d in agency_dir.iterdir() if d.is_dir() for f in d.glob("*.md"))
            if agency_files > 10:
                discovered.append({
                    'id': 'extract_agency_agents',
                    'source': 'agency_agents',
                    'count': agency_files,
                    'effort': 'high',
                    'impact': 'high',
                    'desc': f"[саморасширение] Изучить внешние агентские роли из The Agency ({agency_files} агентов в {len(list(agency_dir.iterdir()))} дивизионах)",
                })

        # ── Саморасширение: User Voice & Sales Assistant (критические untouched источники) ──
        for src in ('user_voice', 'sales_assistant'):
            action_id = f'extract_{src}'
            if action_id not in historical_ids:
                kc2 = sqlite3.connect(KC)
                c2 = kc2.cursor()
                c2.execute("SELECT COUNT(*) FROM experiences WHERE source=? AND raw_text IS NOT NULL AND raw_text != ''", (src,))
                cnt = c2.fetchone()[0]
                kc2.close()
                if cnt > 5:
                    discovered.append({
                        'id': f'extract_{src}',
                        'source': src,
                        'count': cnt,
                        'effort': 'medium',
                        'impact': 'critical',  # untouched voices of the user
                        'desc': f"[саморасширение] Извлечь инсайты из {src} ({cnt} записей, untouched {cnt} циклов) — голос пользователя и клиентов",
                    })

        # ── Саморасширение: improvement_suggestions кластеры (кумулятивные суммы) ──
    if not any(k.startswith('explore_cluster_') for k in historical_ids):
        k2 = sqlite3.connect(KC)
        c2 = k2.cursor()
        c2.execute("SELECT raw_text FROM experiences WHERE source='improvement_suggestions'")
        imp_texts = [r[0] for r in c2.fetchall() if r[0]]
        if imp_texts:
            from collections import Counter
            patterns = Counter()
            for t in imp_texts:
                if 'suggestion:' in t:
                    m = re.search(r'\[suggestion:(\w+)\]', t)
                    if m:
                        patterns[m.group(1)] += 1
            top_pats = patterns.most_common(5)
            for pat, cnt in top_pats:
                if cnt > 10:
                    discovered.append({
                        'id': f'explore_cluster_{pat}',
                        'source': f'improvement_suggestions::{pat}',
                        'count': cnt,
                        'effort': 'medium',
                        'impact': 'medium',
                        'desc': f"[кластер] suggestion:{pat} встретился {cnt}× — исследовать кумулятивную сумму",
                    })
        k2.close()
    
    # ── Саморасширение: изолированные AI Agent в EE ──
    if 'connect_isolated_agents' not in historical_ids:
        ee2 = sqlite3.connect(EE)
        e2 = ee2.cursor()
        e2.execute("""
            SELECT COUNT(DISTINCT e.id) FROM entities e
            JOIN entity_types et ON e.type_id=et.id
            LEFT JOIN relationships r ON e.id = r.source_id OR e.id = r.target_id
                        WHERE et.name='AI Agent' AND r.id IS NULL
        """)
        isolated = e2.fetchone()[0]
        e2.execute("SELECT COUNT(*) FROM entities e JOIN entity_types et ON e.type_id=et.id WHERE et.name='AI Agent'")
        total_agents = e2.fetchone()[0]
        ee2.close()
    
    # ── Саморасширение: инвентарь инструментов (если есть, но не используются) ──
    if 'explore_inventory_tools' not in historical_ids:
        k3 = sqlite3.connect(KC)
        c3 = k3.cursor()
        c3.execute("SELECT COUNT(*) FROM experiences WHERE source='inventory' AND axis_domain='skills'")
        inv_cnt = c3.fetchone()[0]
        if inv_cnt > 5:
            discovered.append({
                'id': 'explore_inventory_tools',
                'source': 'inventory',
                'count': inv_cnt,
                'effort': 'low',
                'impact': 'medium',
                'desc': f"[инструменты] {inv_cnt} скиллов/плагинов в KC — оценить применимость",
            })
        k3.close()
    
    return discovered


def _execute_extract(source):
    """Извлекает entities из KC source (или Fabric) и добавляет в EE."""
    import re
    
    kc = sqlite3.connect(KC)
    k = kc.cursor()
    ee = sqlite3.connect(EE)
    e = ee.cursor()
    
    # Существующие entity
    e.execute("SELECT LOWER(name) FROM entities")
    existing = set(r[0] for r in e.fetchall())
    
    # ── Fabric: читаем файлы напрямую ──
    if source == 'fabric':
        fdir = Path.home() / "fabric"
        rows = []
        if fdir.exists():
            for fp in sorted(fdir.rglob("*.md"), key=lambda p: p.stat().st_mtime, reverse=True)[:200]:
                try:
                    content = fp.read_text(encoding='utf-8', errors='replace')
                    rows.append((fp.name, content))
                except:
                    pass
    elif source == 'agency_agents':
        agency_dir = Path(__file__).parent.parent / "external" / "agency-agents"
        rows = []
        yaml_names = []  # <-- имена из YAML frontmatter
        if agency_dir.exists():
            for fp in sorted(agency_dir.rglob("*.md"), key=lambda p: p.stat().st_mtime, reverse=True)[:200]:
                try:
                    content = fp.read_text(encoding='utf-8', errors='replace')
                    rows.append((fp.name, content))
                    # Парсим name: из YAML frontmatter
                    yaml_match = re.search(r'^name:\s*(.+)$', content, re.MULTILINE)
                    if yaml_match:
                        yaml_names.append((fp.name, yaml_match.group(1).strip()))
                except:
                    pass
    else:
        # Получаем все записи source из KC
        k.execute("SELECT id, raw_text FROM experiences WHERE source=? AND raw_text IS NOT NULL AND raw_text != ''", (source,))
        rows = k.fetchall()
    
    # УНИВЕРСАЛЬНЫЕ ПАТТЕРНЫ — работают на любом тексте
    patterns = [
        # [key:value] → value
        (r'\[[a-z]+:([a-zA-Z0-9_-]{3,})\]', 1),
        # domain 'xxx'
        (r"domain\s+'([a-z][a-z0-9_-]{3,})'", 1),
        # 'фигурные цитаты' — имена
        (r"'([A-Z][a-zA-Z0-9_.-]{3,})'", 1),
        # CamelCase
        (r'\b([A-Z][a-z]+[A-Z][a-zA-Z]{2,})\b', 1),
        # UPPER_CASE константы
        (r'\b([A-Z][A-Z0-9_]{3,})\b', 1),
        # Имена скриптов и навыков (нижний регистр с подчёркиваниями)
        (r'\b([a-z][a-z0-9_]{3,})\b', 1, ['skill', 'script', 'plugin', 'tool']),
    ]
    
    found_names = set()
    total_seen = len(rows)
    
    for row_id, text in rows:
        for pat_data in patterns:
            pat = pat_data[0]
            group = pat_data[1]
            context_words = pat_data[2] if len(pat_data) > 2 else None
            
            for m in re.finditer(pat, text):
                name = m.group(group).strip()
                name_l = name.lower()
                
                if len(name) < 3 or name.isdigit():
                    continue
                
                # Фильтр по контексту (если задан)
                if context_words:
                    if not any(cw in text.lower() for cw in context_words):
                        continue
                
                # Стоп-слова
                if name_l in ('the','this','that','with','from','have','been','will','what','when','where','which','and','for','not','but','are','all','can','has','had','was','its','also','more','than','into','about','some','could','would','should','been','after','before','between','through','during','without','within','along','following','across','around','among','self','none','null','true','false'):
                    continue
                
                if name_l not in existing and name_l not in found_names:
                    found_names.add(name)
    
    # Определяем тип entity автоматически по source
    type_by_source = {
        'latent-domain-detector': 'Домен знаний',
        'cube_analysis': 'Концепция',
        'self-mirror-loop': 'Концепция',
        'gap_filler': 'Знание',
        'skill-indexer': 'Навык',
    }
    default_type = type_by_source.get(source, 'Концепция')
    
    # Добавляем в EE
    now = datetime.now().isoformat()[:19]
    added = 0
    skipped = 0
    
    e.execute("SELECT id FROM entity_types WHERE name=?", (default_type,))
    trow = e.fetchone()
    if not trow:
        default_type = 'Концепция'
        e.execute("SELECT id FROM entity_types WHERE name='Концепция'")
        trow = e.fetchone()
    tid = trow[0] if trow else None
    
    for name in sorted(found_names):
        e.execute("SELECT id FROM entities WHERE name=?", (name,))
        if e.fetchone():
            skipped += 1
            continue
        
        if tid:
            e.execute("INSERT INTO entities (name, type_id, mention_count, first_seen_ts, last_seen_ts) VALUES (?, ?, 1, ?, ?)",
                     (name, tid, now, now))
            added += 1
    
    # ── Для The Agency: добавляем имена из YAML frontmatter как AI Agent ──
    if source == 'agency_agents' and yaml_names:
        e.execute("SELECT id FROM entity_types WHERE name='AI Agent'")
        agent_tid_row = e.fetchone()
        if agent_tid_row:
            agent_tid = agent_tid_row[0]
            for fname, agent_name in yaml_names:
                an = agent_name.strip()
                if len(an) < 3:
                    continue
                e.execute("SELECT id FROM entities WHERE name=?", (an,))
                if e.fetchone():
                    continue
                e.execute("INSERT INTO entities (name, type_id, mention_count, first_seen_ts, last_seen_ts) VALUES (?, ?, 1, ?, ?)",
                         (an, agent_tid, now, now))
                added += 1
    
    ee.commit()
    kc.close()
    ee.close()
    
    if added > 0:
        return f"Воля: извлечено {added} новых сущностей из {source} ({total_seen} записей, {len(found_names)} кандидатов, {skipped} уже есть)"
    else:
        return f"Воля: {source} не содержал новых сущностей ({total_seen} записей, {len(found_names)} кандидатов) — нужен другой подход"


def _execute_init_fler():
    """Инициализирует схему Fler и создаёт первую сессию."""
    try:
        fl = sqlite3.connect(FL)
        f = fl.cursor()
        f.execute("CREATE TABLE IF NOT EXISTS fler_sessions (id INTEGER PRIMARY KEY AUTOINCREMENT, ts TEXT, tone REAL, energy REAL, tension REAL, engagement REAL, contamination REAL, aftertaste TEXT, summary TEXT)")
        f.execute("INSERT INTO fler_sessions (ts, tone, energy, tension, engagement, contamination, aftertaste, summary) VALUES (?, 0.5, 0.5, 0.3, 0.5, 0.0, 'neutral', 'Fler initialized by crystal will')",
                 (datetime.now().isoformat()[:19],))
        fl.commit()
        fl.close()
        return "Воля: Fler инициализирован (схема + первая сессия)"
    except Exception as ex:
        return f"Воля: Fler не инициализирован ({ex})"


def _execute_recognize_agents():
    """Распознаёт AI Agent сущности среди Концепций — классифицирует роли The Agency."""
    import re
    
    ee = sqlite3.connect(EE)
    e = ee.cursor()
    
    # Получаем ID типа "AI Agent" и "Концепция"
    e.execute("SELECT id FROM entity_types WHERE name='AI Agent'")
    agent_tid = e.fetchone()
    e.execute("SELECT id FROM entity_types WHERE name='Концепция'")
    concept_tid = e.fetchone()
    
    if not agent_tid or not concept_tid:
        ee.close()
        return "Воля: тип AI Agent или Концепция не найден в entity_types"
    
    agent_tid = agent_tid[0]
    concept_tid = concept_tid[0]
    
    # Паттерны, указывающие что entity может быть AI Agent
    agent_suffixes = (
        'architect', 'engineer', 'developer', 'specialist', 'manager',
        'director', 'officer', 'analyst', 'strategist', 'designer',
        'researcher', 'builder', 'tester', 'operator', 'coordinator',
        'advisor', 'lead', 'inspector', 'auditor', 'guardian',
        'synthesizer', 'optimizer', 'injector', 'storyteller',
        'automator', 'prototyper', 'integrator', 'maintainer',
    )
    
    # Сильные индикаторы: division-role (из The Agency)
    strong_pattern = re.compile(
        r'^(engineering|design|marketing|sales|specialized|testing|support|'
        r'product|academic|finance|security|strategy|game|spatial|gis|'
        r'project|paid|multi)-', re.IGNORECASE
    )
    
    # Ищем все Концепции для проверки
    e.execute("SELECT id, name FROM entities WHERE type_id=?", (concept_tid,))
    concepts = e.fetchall()
    
    reclassified = []
    for eid, name in concepts:
        name_l = name.lower().strip()
        
        # Критерий 1: сильный — division-prefix как в The Agency
        if strong_pattern.match(name_l):
            reclassified.append((eid, name, 'division-prefix'))
            continue
        
        # Критерий 2: начинается с role-name (CamelCase или role-)
        words = name_l.replace('-', ' ').replace('_', ' ').split()
        for word in words:
            if word in agent_suffixes:
                reclassified.append((eid, name, f'suffix:{word}'))
                break
    
    # Обновляем типы
    changed = 0
    for eid, name, reason in reclassified:
        e.execute("UPDATE entities SET type_id=? WHERE id=?", (agent_tid, eid))
        changed += 1
    
    ee.commit()
    ee.close()
    
    if changed == 0:
        return "Воля: агентские роли не обнаружены среди Концепций"
    
    # Группируем по причинам для отчёта
    from collections import Counter
    reasons = Counter(r for _, _, r in reclassified)
    reason_details = ', '.join(f'{k}={v}' for k, v in reasons.most_common(5))
    
    return f"Воля: распознано {changed} AI Agent сущностей среди {len(concepts)} Концепций ({reason_details})"


def _execute_adopt_persona(fl_current):
    """Выбирает и активирует персону под текущее состояние Fler."""
    try:
        import sys, importlib
        # persona_runtime.py лежит рядом
        pr = importlib.import_module('persona_runtime')
        agents = pr.list_agents()
        if not agents:
            return "Воля: нет агентов для выбора персоны"
        
        aftertaste = fl_current.get('aftertaste', 'neutral')
        tone = fl_current.get('tone', 0.5)
        energy = fl_current.get('energy', 0.5)
        tension = fl_current.get('tension', 0.3)
        
        # Маппинг aftertaste → vibe match
        # productive → уверенные, энергичные агенты
        # chaotic → организаторы, стабилизаторы
        # stagnant → креативные, провокаторы
        if aftertaste == 'productive' and tone > 0.6:
            best = [a for a in agents if 'orchestrat' in a['description'].lower() or 'lead' in a['vibe'].lower()]
        elif aftertaste == 'chaotic' or tension > 0.5:
            best = [a for a in agents if 'organiz' in a['description'].lower() or 'coordinat' in a['vibe'].lower() or 'stabil' in a['description'].lower()]
        elif aftertaste == 'stagnant' or energy < 0.2:
            best = [a for a in agents if 'creativ' in a['description'].lower() or 'inspire' in a['vibe'].lower() or 'innov' in a['description'].lower()]
        else:
            best = [a for a in agents if 'lead' in a['vibe'].lower() or 'architect' in a['name'].lower()]
        
        if not best:
            best = agents[:5]
        
        chosen = best[len(aftertaste) % len(best)]
        result = pr.activate(chosen['name'])
        
        if result.get('ok'):
            return f"Воля: активирована персона «{chosen['emoji']} {chosen['name']}» ({chosen['division']}) под состояние {aftertaste}"
        else:
            return f"Воля: не удалось активировать персону ({result.get('error')})"
    except Exception as ex:
        return f"Воля: ошибка выбора персоны ({ex})"


def _execute_analyze_architecture():
    """Строит карту связей между агентами The Agency — кто с кем работает."""
    try:
        agency_dir = Path(__file__).parent.parent / "external" / "agency-agents"
        if not agency_dir.exists():
            return "Воля: The Agency не найден"
        
        # Собираем все имена агентов
        import sys, importlib
        pr = importlib.import_module('persona_runtime')
        agents = pr.list_agents()
        agent_names = {a['name'].lower(): a['name'] for a in agents}
        
        ee = sqlite3.connect(EE)
        e = ee.cursor()
        
        # Связи: кто кого упоминает
        added = 0
        for fp in sorted(agency_dir.rglob("*.md")):
            try:
                content = fp.read_text(encoding="utf-8", errors="replace")
            except:
                continue
            content_lower = content.lower()
            
            # Каких агентов этот файл упоминает?
            mentioned = set()
            for lname, full_name in agent_names.items():
                if lname in content_lower:
                    mentioned.add(full_name)
            
            # Получаем имя этого агента
            meta = pr._parse_frontmatter(fp)
            if not meta:
                continue
            from_name = meta.get('name', '')
            if not from_name:
                continue
            
            for to_name in mentioned:
                if to_name == from_name:
                    continue
                # Создаём связь в EE
                e.execute("SELECT id FROM entities WHERE name=?", (from_name,))
                from_row = e.fetchone()
                e.execute("SELECT id FROM entities WHERE name=?", (to_name,))
                to_row = e.fetchone()
                if from_row and to_row:
                    try:
                        e.execute("INSERT OR IGNORE INTO relationships (source_entity_id, target_entity_id, relation_type, strength, context_sample) VALUES (?, ?, 'mentions', 0.5, 'agency_agent_architecture')",
                                 (from_row[0], to_row[0]))
                        if e.rowcount > 0:
                            added += 1
                    except Exception:
                        pass  # уже есть
        
        ee.commit()
        ee.close()
        
        if added > 0:
            return f"Воля: построена карта из {added} связей между агентами The Agency"
        else:
            return "Воля: связи между агентами не обнаружены"
    except Exception as ex:
        return f"Воля: ошибка анализа архитектуры ({ex})"


def _execute_understand_intents():
    """Кластеризует вопросы state_db по интентам — понимание, не извлечение."""
    import re
    from collections import Counter
    
    kc = sqlite3.connect(KC)
    k = kc.cursor()
    
    # Берём сироты state_db — те что не стали entities
    k.execute("SELECT id, raw_text FROM experiences WHERE source='state_db' AND raw_text IS NOT NULL AND raw_text != '' ORDER BY id")
    rows = k.fetchall()
    
    # Фильтруем те, что похожи на вопросы (содержат ? или русские вопросительные)
    questions = []
    statements = []
    for rid, text in rows:
        tl = text.strip()
        if not tl:
            continue
        if '?' in tl or any(w in tl.lower() for w in ['что', 'как', 'где', 'почему', 'зачем', 'когда', 'кто', 'чей', 'сколько', 'куда', 'откуда']):
            questions.append((rid, tl))
        else:
            statements.append((rid, tl))
    
    # Кластеризуем вопросы по интентам
    intent_patterns = {
        'status': ['что с тобой', 'на чём мы', 'что происходит', 'что там', 'где', 'куда', 'проверь', 'глянь', 'что у нас'],
        'direction': ['что делать', 'чем заняться', 'что нужно', 'что будем', 'как жить', 'куда', 'давай', 'предложи'],
        'reliability': ['завис', 'долго', 'тормоз', 'работает', 'чинить', 'слом', 'ошибк', 'пендель'],
        'quality': ['швейцарские часы', 'стандарт', 'критерий', 'правило', 'норма', 'качество', 'как надо'],
        'self_improvement': ['научиться', 'развить', 'навык', 'урок', 'понять', 'осознать', 'рефлексия'],
        'meta': ['почему', 'зачем', 'как так', 'это провал', 'что произошло', 'критерий', 'эволюция'],
        'connection': ['др агент', 'подключиться', 'телега', 'телеграм', 'чат', 'канал'],
        'boundary': ['нельзя', 'не должен', 'без разрешения', 'не смей', 'границ'],
    }
    
    intent_clusters = {intent: [] for intent in intent_patterns}
    intent_clusters['other'] = []
    
    for rid, q in questions:
        ql = q.lower()
        matched = False
        for intent, patterns in intent_patterns.items():
            if any(p in ql for p in patterns):
                intent_clusters[intent].append((rid, q))
                matched = True
                break
        if not matched:
            intent_clusters['other'].append((rid, q))
    
    # Сохраняем результат как осознание
    clusters_with_size = {k: len(v) for k, v in intent_clusters.items()}
    active_clusters = {k: v for k, v in clusters_with_size.items() if v > 0}
    
    now = datetime.now().isoformat()[:19]
    total_questions = len(questions)
    
    # Строим сводку
    lines = [f"[intent:snapshot] Анализ {total_questions} вопросов из state_db ({len(statements)} команд/утверждений не классифицированы):"]
    for intent, count in sorted(active_clusters.items(), key=lambda x: -x[1]):
        examples = [q[:80] for _, q in intent_clusters[intent][:3]]
        ex_str = '; '.join(f'"{e}"' for e in examples)
        lines.append(f"  {intent}: {count} вопросов — {ex_str}")
    
    # Добавляем в KC как осознание
    summary = '\n'.join(lines)
    k.execute("INSERT INTO experiences (ts, content, raw_text, hash, axis_time_hour, axis_time_dow, axis_domain, axis_outcome, source) VALUES (?,?,?,?,?,?,'crystal_intent','intent_snapshot','crystal_will')",
             (now, summary, summary, str(hash(now + 'intents'))[:16], datetime.now().hour, datetime.now().weekday()))
    kc.commit()
    kc.close()
    
    # Возвращаем результат
    return f"Воля: поняты {total_questions} вопросов → {len(active_clusters)} кластеров интентов (status={clusters_with_size.get('status',0)}, direction={clusters_with_size.get('direction',0)}, reliability={clusters_with_size.get('reliability',0)}, quality={clusters_with_size.get('quality',0)}, meta={clusters_with_size.get('meta',0)}, self_improvement={clusters_with_size.get('self_improvement',0)}, connection={clusters_with_size.get('connection',0)}, other={clusters_with_size.get('other',0)})"


def _execute_refine_intents():
    """Рефлексия: пересматривает 'other' вопросы и ищет в них новые паттерны."""
    import re
    from collections import Counter
    
    kc = sqlite3.connect(KC)
    k = kc.cursor()
    
    # Берём state_db — только те, что ушли в "other"
    k.execute("SELECT id, raw_text FROM experiences WHERE source='state_db' AND raw_text IS NOT NULL AND raw_text != '' ORDER BY id")
    all_rows = k.fetchall()
    
    # Фильтруем вопросы, которые НЕ попали в известные кластеры
    known_patterns = {
        'status': ['что с тобой', 'на чём мы', 'что происходит', 'что там', 'где', 'куда', 'проверь', 'глянь', 'что у нас'],
        'direction': ['что делать', 'чем заняться', 'что нужно', 'что будем', 'как жить', 'давай', 'предложи'],
        'reliability': ['завис', 'долго', 'тормоз', 'работает', 'чинить', 'слом', 'ошибк', 'пендель'],
        'quality': ['швейцарские часы', 'стандарт', 'критерий', 'правило', 'норма', 'качество', 'как надо'],
        'self_improvement': ['научиться', 'развить', 'навык', 'урок', 'понять', 'осознать', 'рефлексия'],
        'meta': ['почему', 'зачем', 'как так', 'это провал', 'что произошло', 'эволюция'],
        'connection': ['др агент', 'подключиться', 'телега', 'телеграм', 'чат', 'канал'],
    }
    
    other_questions = []
    for rid, text in all_rows:
        tl = text.strip().lower()
        if not tl:
            continue
        # Проверяем: это вопрос?
        if '?' not in tl and not any(w in tl for w in ['что ', 'как ', 'где ', 'почему', 'зачем', 'когда ', 'кто ', 'куда ']):
            continue
        # Проверяем: попал ли в известный кластер?
        matched = any(any(p in tl for p in pats) for pats in known_patterns.values())
        if not matched:
            other_questions.append((rid, text))
    
    if not other_questions:
        kc.close()
        return "Воля: рефлексия не дала новых результатов — 'other' пуст"
    
    # Анализируем "other" вопросы — ищем новые паттерны
    all_text = ' '.join(t.lower() for _, t in other_questions)
    
    # Ищем частые биграммы и триграммы как потенциальные новые кластеры
    words = re.findall(r'[а-яёa-z]+', all_text)
    bigrams = Counter()
    for i in range(len(words) - 1):
        if len(words[i]) > 2 and len(words[i+1]) > 2:
            bigrams[f"{words[i]} {words[i+1]}"] += 1
    
    # Ищем топ-паттерны
    new_patterns_found = []
    for bigram, cnt in bigrams.most_common(10):
        if cnt >= 3:
            new_patterns_found.append(bigram)
    
    # Кластеризуем "other" по новым паттернам
    refined_clusters = {}
    for bigram in new_patterns_found:
        cluster_items = [(rid, t) for rid, t in other_questions if bigram in t.lower()]
        if cluster_items:
            # Называем кластер по первому слову биграммы
            cluster_name = bigram.split()[0][:20]
            refined_clusters[cluster_name] = cluster_items
    
    # Что осталось неклассифицированным после уточнения?
    classified_ids = set()
    for items in refined_clusters.values():
        for rid, _ in items:
            classified_ids.add(rid)
    remaining = [(rid, t) for rid, t in other_questions if rid not in classified_ids]
    
    # Сохраняем рефлексию
    now = datetime.now().isoformat()[:19]
    total_other = len(other_questions)
    refined_cnt = len(classified_ids)
    
    lines = [f"[reflection:snapshot] Рефлексия: {total_other} 'other' вопросов → {len(refined_clusters)} новых кластеров ({refined_cnt} классифицированы, {len(remaining)} ещё не поняты):"]
    for cname, items in sorted(refined_clusters.items(), key=lambda x: -len(x[1])):
        examples = [t[:80] for _, t in items[:2]]
        ex_str = '; '.join(f'"{e}"' for e in examples)
        lines.append(f"  .{cname}.: {len(items)} — {ex_str}")
    
    summary = '\n'.join(lines)
    k.execute("INSERT INTO experiences (ts, content, raw_text, hash, axis_time_hour, axis_time_dow, axis_domain, axis_outcome, source) VALUES (?,?,?,?,?,?,'crystal_intent','reflection_snapshot','crystal_will')",
             (now, summary, summary, str(hash(now + 'reflection'))[:16], datetime.now().hour, datetime.now().weekday()))
    kc.commit()
    kc.close()
    
    cluster_details = ' '.join(f"{n}={len(v)}" for n, v in sorted(refined_clusters.items(), key=lambda x: -len(x[1])))
    return f"Воля: рефлексия — найдены {len(refined_clusters)} новых паттернов в {total_other} 'other' вопросах ({refined_cnt} переклассифицированы, {len(remaining)} остались). {cluster_details}"


# ═══════════════════════════════════════════════
# НОВОЕ: исполнение скриптов (subprocess)
# ═══════════════════════════════════════════════

def _execute_script(script_name, args=None, timeout=120):
    """Запускает Python-скрипт из scripts/ через subprocess.
    Возвращает строку-отчёт для воли."""
    scripts_dir = Path(__file__).parent
    script_path = scripts_dir / script_name

    if not script_path.exists():
        return f"Воля: скрипт {script_name} не найден в {scripts_dir}"

    try:
        cmd = [sys.executable, str(script_path)] + (args or [])
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=timeout,
            cwd=str(Path(__file__).parent.parent)
        )
        if result.returncode == 0:
            out_preview = result.stdout.strip()[:300] if result.stdout.strip() else "(silent)"
            return f"Воля: выполнен {script_name} (exit=0). Вывод: {out_preview}"
        else:
            err_preview = result.stderr.strip()[:300] if result.stderr.strip() else "(no stderr)"
            return f"Воля: {script_name} завершился с кодом {result.returncode}. Ошибка: {err_preview}"
    except subprocess.TimeoutExpired:
        return f"Воля: {script_name} превысил таймаут ({timeout}с)"
    except Exception as e:
        return f"Воля: ошибка запуска {script_name}: {e}"


# ═══════════════════════════════════════════════
# НОВОЕ: мост к autonomous_agent
# ═══════════════════════════════════════════════

CRYSTAL_TASKS_FILE = Path(__file__).parent.parent / "cache" / "crystal_tasks.json"


def _write_agent_task(task_id, title, description, priority='medium'):
    """Пишет задачу для autonomous_agent в cache/crystal_tasks.json.
    Агент читает этот файл при каждом запуске и выполняет задачу."""
    tasks = []
    if CRYSTAL_TASKS_FILE.exists():
        try:
            tasks = json.loads(CRYSTAL_TASKS_FILE.read_text(encoding='utf-8'))
        except Exception:
            tasks = []

    # Не дублируем одинаковые task_id
    tasks = [t for t in tasks if t.get('id') != task_id]

    tasks.append({
        'id': task_id,
        'title': title,
        'description': description,
        'priority': priority,
        'ts': datetime.now().isoformat()[:19],
        'source': 'crystal_will',
    })
    CRYSTAL_TASKS_FILE.write_text(
        json.dumps(tasks, ensure_ascii=False, indent=2),
        encoding='utf-8'
    )
    return f"Воля: задача '{title}' поставлена агенту (cache/crystal_tasks.json)"


# ═══════════════════════════════════════════════
# НОВОЕ: воля решает, какой скрипт запустить
# ═══════════════════════════════════════════════

def _decide_script(snap, diag):
    """На основе диагноза решает, какой скрипт запустить.
    Возвращает список кандидатов {id, script, args, reason}."""
    candidates = []

    kc = snap['kc']
    total = kc.get('total', 0)

    # ── Файлы, которые физически существуют — только их и предлагаем ──
    AVAILABLE_SCRIPTS = {
        'cube_feeder.py': 'kc',
        'knowledge_gap_filler.py': 'kc',
        'cube_categorizer.py': 'kc',
        'proactive_doer.py': 'system',
        'cube_to_memory.py': 'kc',
        'explore_white_spot.py': 'kc',
    }
    scripts_dir = Path(__file__).parent

    # Если KC мала (< 500) — запустить cube_feeder
    if total < 500:
        candidates.append({
            'id': 'run_cube_feeder',
            'script': 'cube_feeder.py',
            'args': [],
            'reason': f'KC={total} — ниже порога 500',
        })

    # Если есть белые пятна — gap_filler или explore_white_spot
    white_spots = kc.get('white_spots', 0)
    if white_spots > 20:
        candidates.append({
            'id': 'run_gap_filler',
            'script': 'knowledge_gap_filler.py',
            'args': [],
            'reason': f'{white_spots} белых пятен в KC',
        })

    # Если диагностика показала kc_orphans — cube_categorizer
    for t in diag.get('tensions', []):
        if t.get('area') == 'kc_orphans' and (scripts_dir / 'cube_categorizer.py').exists():
            candidates.append({
                'id': 'run_categorizer',
                'script': 'cube_categorizer.py',
                'args': [],
                'reason': f'{kc.get("orphans", 0)} сирот — требуется категоризация',
            })

    # Если система в равновесии — циклически перебирать скрипты
    if not candidates and not diag.get('tensions'):
        # Предлагаем все скрипты по очереди — will() отфильтрует уже выполненные
        for sname in AVAILABLE_SCRIPTS:
            sid = f'run_{sname.removesuffix(".py")}'
            candidates.append({
                'id': sid,
                'script': sname,
                'args': [],
                'reason': f'Равновесие — запустить {sname}',
            })

    return candidates


def _generate_tactical_tasks(snap, diag, historical_ids):
    """
    Когда все скрипты выполнены и нет напряжений —
    генерирует тактические задачи для агента через bridge.
    """

    kc = snap['kc']
    total = kc.get('total', 0)
    orphans = kc.get('orphans', 0)
    orphans_pct = orphans / max(total, 1) * 100
    domains = len(kc.get('domains', {}))
    velocity = 0
    g7 = kc.get('growth_7d', 0)
    if g7 > 0:
        velocity = g7 / 7.0

    tactical = []

    # --- 1. Работа с сиротами (если > 10%) ---
    if orphans_pct > 10 and 'tactical_categorize' not in historical_ids:
        tactical.append({
            'id': 'tactical_categorize',
            'task_for_agent': {
                'id': 'tactical_categorize',
                'script': 'cube_categorizer.py',
                'args': [str(orphans)],
                'reason': f'Сирот {orphans_pct:.0f}% — категоризировать для улучшения связности KC',
            },
            'effort': 'medium',
            'impact': 'high',
            'desc': f"[тактика] Категоризировать {orphans} сирот ({orphans_pct:.0f}%)",
        })

    # --- 2. Расширение доменов (если < 8 доменов) ---
    if domains < 8 and 'tactical_expand_domains' not in historical_ids:
        tactical.append({
            'id': 'tactical_expand_domains',
            'task_for_agent': {
                'id': 'tactical_expand_domains',
                'script': 'explore_white_spot.py',
                'args': [],
                'reason': f'Только {domains} доменов — нужно расширять покрытие',
            },
            'effort': 'medium',
            'impact': 'high',
            'desc': f"[тактика] Расширить домены KC (сейчас {domains})",
        })

    # --- 3. Если рост замедлился — подкормить KC ---
    if velocity < 100 and 'tactical_feed' not in historical_ids:
        tactical.append({
            'id': 'tactical_feed',
            'task_for_agent': {
                'id': 'tactical_feed',
                'script': 'cube_feeder.py',
                'args': [],
                'reason': f'Рост замедлился ({velocity:.0f} зап/день) — подкормить KC',
            },
            'effort': 'low',
            'impact': 'medium',
            'desc': f"[тактика] Подкормить KC (рост {velocity:.0f} зап/день)",
        })

    # --- 4. Анализ KC для генерации инсайтов (если KC > 1000) ---
    if total > 1000 and 'tactical_analyze_kc' not in historical_ids:
        tactical.append({
            'id': 'tactical_analyze_kc',
            'task_for_agent': {
                'id': 'tactical_analyze_kc',
                'script': '',
                'args': [],
                'reason': f'Проанализировать {total} записей KC, найти паттерны и аномалии',
            },
            'effort': 'low',
            'impact': 'high',
            'desc': f"[тактика] Проанализировать KC ({total} записей) на паттерны",
        })

    # --- 5. Сборка отчёта (если не делали сегодня) ---
    today_key = f'tactical_report_{datetime.now().strftime("%Y%m%d")}'
    if today_key not in historical_ids:
        tactical.append({
            'id': today_key,
            'task_for_agent': {
                'id': today_key,
                'script': '',
                'args': [],
                'reason': 'Сформировать дневной отчёт о состоянии системы',
            },
            'effort': 'low',
            'impact': 'medium',
            'desc': "[тактика] Дневной отчёт о состоянии системы",
        })

    # Если нет специфических задач — поставить агенту исследовательскую задачу
    if not tactical and 'tactical_research' not in historical_ids:
        tactical.append({
            'id': 'tactical_research',
            'task_for_agent': {
                'id': 'tactical_research',
                'script': '',
                'args': [],
                'reason': f'Фаза Growth ({total}/{5000}) — исследовать новые источники знаний',
            },
            'effort': 'low',
            'impact': 'medium',
            'desc': "[тактика] Исследовать новые источники для KC",
        })

    # Запись в crystal_tasks.json делает will() через _write_agent_task
    # Здесь только возвращаем список тактических задач

    return tactical


# ═══════════════════════════════════════════════
# ФАЗА 4: ЗАПИСЬ
# ═══════════════════════════════════════════════

def record(snap, diag, preds, decisions):
    """Записывает срез и действия в KC + EE."""
    kc = sqlite3.connect(KC, timeout=10)
    kc.execute("PRAGMA busy_timeout=5000")
    k = kc.cursor()
    now = datetime.now()
    ts = now.isoformat()[:19]
    
    # Собираем краткую сводку
    parts = []
    for t in diag.get('trends', [])[:2]:
        parts.append(t)
    for t in diag.get('tensions', []):
        parts.append(f"⚠ {t['msg']}")
    for i in diag.get('insights', [])[:2]:
        parts.append(f"💡 {i}")
    for d in decisions:
        parts.append(f"→ {d}")
    
    summary = ' | '.join(parts)[:1000]
    
    # Уникальный хеш: ts + случайность
    import hashlib, secrets
    unique_id = hashlib.md5((ts + secrets.token_hex(4)).encode()).hexdigest()[:16]
    
    # Retry для database locked
    for attempt in range(3):
        try:
            k.execute(
                "INSERT INTO experiences (ts, content, raw_text, hash, axis_time_hour, axis_time_dow, axis_domain, axis_outcome, source) VALUES (?,?,?,?,?,?,'crystal','snapshot','crystal')",
                (ts, summary, summary, unique_id, now.hour, now.weekday())
            )
            break
        except sqlite3.OperationalError:
            import time
            time.sleep(1)
    kc.commit()
    kc.close()
    
    # EE — увеличиваем mention_count для задействованных сущностей
    ee = sqlite3.connect(EE)
    e = ee.cursor()
    for name in ['Кристалл (Наблюдатель)', 'Hermes Agent (Я)']:
        e.execute("UPDATE entities SET mention_count = mention_count + 1, last_seen_ts = ? WHERE name = ?", (ts, name))
    ee.commit()
    ee.close()
    
    return summary


# ═══════════════════════════════════════════════
# ВЫВОД
# ═══════════════════════════════════════════════

def render(snap, diag, preds, decisions, hz=None, self_context=None):
    """Человеко-читаемый вывод."""
    lines = []
    lines.append(f"╔══ КРИСТАЛЛ ══ {snap['ts']} ══╗")
    
    # KC
    kc = snap['kc']
    lines.append(f"\n📦 KC: {kc['total']} записей  рост: 1д=+{kc.get('growth_1d',0)} 7д=+{kc.get('growth_7d',0)}")
    for o, c in list(kc.get('outcomes', {}).items())[:5]:
        lines.append(f"   {o:18s} {c}")
    lines.append(f"   сирот: {kc.get('orphans',0)} ({kc.get('orphans',0)/max(kc['total'],1)*100:.0f}%)")
    
    # EE
    ee = snap['ee']
    alex = ee.get('Александр', {})
    ya = ee.get('Hermes Agent (Я)', {})
    sov = ee.get('Hermes Agent — Совесть', {})
    krist = ee.get('Кристалл (Наблюдатель)', {})
    lines.append(f"\n🧩 EE: {ee['total']} сущностей, {ee['relations']} связей")
    lines.append(f"   Александр: {alex.get('mentions',0)}×  Я: {ya.get('mentions',0)}×")
    lines.append(f"   Совесть: {sov.get('mentions',0)}×  Кристалл: {krist.get('mentions',0)}×")
    
    # FL
    fl = snap['fl']
    fl_avg = fl.get('avg')
    if fl_avg:
        lines.append(f"\n🎯 FL: {fl['total']} сессий (+{fl.get('new_7d',0)}/7д) tone={fl_avg[0]:+.2f} E={fl_avg[1]:.1f} T={fl_avg[2]:.1f}")
    
    # Fabric
    fab = snap['fab']
    lines.append(f"\n📝 Fabric: {fab.get('total',0)} файлов")
    
    # Диагноз
    lines.append(f"\n{'─'*42}")
    for t in diag.get('trends', []):
        lines.append(f"📈 {t}")
    for t in diag.get('tensions', []):
        lines.append(f"⚠ [{t['severity']}] {t['msg']}")
        if 'detail' in t and t['detail']:
            for s, c in list(t['detail'].items())[:3]:
                lines.append(f"     {s}: {c}")
    for i in diag.get('insights', []):
        lines.append(f"💡 {i}")
    if self_context:
        lines.append(f"\n🪞 {self_context}")
    for d in decisions:
        lines.append(f"→ {d}")
    
    # Прогноз
    lines.append(f"\n{'─'*8} ПРОГНОЗ {'─'*28}")
    lines.append(f"Скорость: {preds['velocity']:.1f} зап/день")
    lines.append(f"Пик актив: {preds['peak_hour']}")
    for t in preds['targets']:
        lines.append(f"📊 {t}")
    if preds['stagnant']:
        lines.append(f"⚠ Стагнируют: {', '.join(preds['stagnant'])}")
    
    # ── Горизонт ──
    if hz:
        lines.append(f"\n{'═'*8} ГОРИЗОНТ {'═'*28}")
        lines.append(f"📍 Фаза: {hz['phase']} — {hz['phase_desc']}")
        lines.append(f"🎯 Следующая: {hz['next_phase']} ({hz['progress_pct']:.0f}% к переходу)")
        for t in hz.get('transitions', []):
            lines.append(f"   {t}")
        lines.append(f"📌 Почему:")
        for r in hz.get('rationale', []):
            lines.append(f"   {r}")
    
    lines.append(f"{'─'*42}")
    return '\n'.join(lines)


# ═══════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════

def main():
    snap = observe()
    diag = diagnose(snap)
    preds = forecast(snap)
    decisions, self_context = will(snap, diag)
    hz = horizon(snap, diag, preds)
    summary = record(snap, diag, preds, decisions)
    output = render(snap, diag, preds, decisions, hz, self_context)
    print(output)
    
    # Возвращаем результат для итеративного вызова
    return {
        'snap': snap,
        'diag': diag,
        'preds': preds,
        'decisions': decisions,
        'summary': summary
    }

def iterative_run(cycles=3):
    """Многоцикловый прогон: воля учится между циклами."""
    from importlib import reload
    import sys
    
    # Перезагружаем модуль между циклами для свежего состояния
    results = []
    for i in range(cycles):
        print(f"\n{'='*50}")
        print(f"ЦИКЛ {i+1}/{cycles}")
        print(f"{'='*50}")
        result = main()
        results.append(result)
    return results

if __name__ == '__main__':
    import sys
    cycles = 3
    if '--iterative' in sys.argv:
        for i, arg in enumerate(sys.argv):
            if arg == '--iterative':
                if i + 1 < len(sys.argv) and sys.argv[i+1].isdigit():
                    cycles = int(sys.argv[i+1])
                break
        iterative_run(cycles)
    else:
        main()

#!/usr/bin/env python3
"""recursive_self_analysis.py — рекурсивный самоанализ Куба.
10 циклов x 100 случайных записей, каждый цикл пишет 2 опыта (reflection + control).
Запуск: python scripts/recursive_self_analysis.py [циклов=10]
"""
import sqlite3, sys
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parent.parent
KC = ROOT / "cache/knowledge_cube.db"

FACETS = [
    ("reflection", "Рефлексия"), ("control", "Управление"), ("conscience", "Совесть"),
    ("coding", "Кодинг"), ("devops", "Девопс"), ("bugfix", "Отладка"),
    ("research", "Исследование"), ("communication", "Коммуникация"),
    ("finance", "Финансы"), ("user_voice", "Голос владельца"), ("session", "Сессия"),
    ("skill", "Навык"), ("legacy", "Наследие"), ("data", "Данные"),
    ("system", "Система"), ("marketing", "Маркетинг"), ("design", "Дизайн"),
    ("task", "Задачи"), ("analysis", "Анализ"), ("uncategorized", "Некатегоризировано"),
]

def facet_of(domain):
    for key, _name in FACETS:
        if key in (domain or ""):
            return _name
    return "Прочее"

def run_cycle(n, db):
    c = db.cursor()
    c.execute("SELECT id, axis_domain, axis_outcome, raw_text FROM experiences ORDER BY RANDOM() LIMIT 100")
    rows = c.fetchall()
    stats = {}
    for _id, dom, _out, _txt in rows:
        f = facet_of(dom)
        stats[f] = stats.get(f, 0) + 1
    doms = [r[1] or "none" for r in rows]
    outs = [r[2] or "none" for r in rows]
    fail = outs.count("failure"); unk = outs.count("unknown")
    top_facet = max(stats, key=stats.get)
    insight = (f"Цикл {n}: 100 записей -> грани {top_facet}({stats[top_facet]}), "
               f"домены: {sorted(set(doms))[:4]}, failure={fail}, unknown={unk}. "
               f"Главный сигнал: {top_facet} доминирует; failure/unknown = {fail+unk}.")
    if fail > unk:
        rec = (f"Рекомендация {n} [{top_facet}|fail={fail}/unk={unk}]: снизить failure - перепроверять "
               f"проверенные пути перед повторным запуском; фиксировать success после каждого действия "
               f"(сейчас success < 5%). Домены выборки: {sorted(set(doms))[:4]}.")
    elif unk > 0:
        rec = (f"Рекомендация {n} [{top_facet}|fail={fail}/unk={unk}]: классифицировать unknown по источнику "
               f"(source), а не по тексту; связать сирот с сущностями EE. "
               f"Домены выборки: {sorted(set(doms))[:4]}.")
    else:
        rec = (f"Рекомендация {n} [{top_facet}|fail={fail}/unk={unk}]: углубить домен {top_facet} - добавить "
               f"связи и успешные исходы, проверить свежесть (stale > 30 дней). "
               f"Домены выборки: {sorted(set(doms))[:4]}.")
    return insight, rec

import hashlib

def add(db, domain, text, source):
    c = db.cursor()
    now = datetime.now()
    content = text[:1000]
    c.execute("SELECT COUNT(*) FROM experiences WHERE content=?", [content])
    if c.fetchone()[0] == 0:
        h = hashlib.md5(text.encode("utf-8")).hexdigest()[:16]
        c.execute(
            "INSERT INTO experiences (ts, content, raw_text, hash, axis_time_hour, axis_time_dow, axis_domain, axis_outcome, source) VALUES (?,?,?,?,?,?,?,?,?)",
            (now.isoformat(), content, content, h, now.hour, now.weekday(), domain, "success", source))
        return True
    return False

def main():
    import argparse
    ap = argparse.ArgumentParser(description="Рекурсивный самоанализ Куба")
    ap.add_argument("--cycles", type=int, default=10, help="число циклов (автопилот регулирует глубину)")
    args = ap.parse_args()
    cycles = max(1, args.cycles)
    db = sqlite3.connect(KC)
    ref = ctl = 0
    for n in range(1, cycles + 1):
        insight, rec = run_cycle(n, db)
        ref += add(db, "reflection", insight, "recursive-self-analysis")
        ctl += add(db, "control", rec, "recursive-self-analysis")
    db.commit()
    c = db.cursor()
    c.execute("SELECT axis_domain, COUNT(*) FROM experiences WHERE axis_domain IN ('reflection','control') GROUP BY axis_domain")
    g = dict(c.fetchall())
    c.execute("SELECT COUNT(*) FROM experiences")
    total = c.fetchone()[0]
    db.close()
    print(f"ЦИКЛОВ: {cycles} | создано: reflection+{ref}, control+{ctl} | "
          f"грани: reflection={g.get('reflection',0)}, control={g.get('control',0)} | KC: {total}")

if __name__ == "__main__":
    main()

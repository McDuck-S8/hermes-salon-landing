#!/usr/bin/env python3
"""Daily digest — HTML отчёт со всех мониторов.

Генерирует reports/digest.html + dashboard_data/digest.html + digest.html (корень репо).
URL preview: projects/ai-ofm-tribute/content/sessions/*/preview.html (от корня репо).

Вызов: python scripts/daily_digest.py
       python scripts/daily_digest.py --text
"""

import os, sys, json, re, shutil, urllib.request
from pathlib import Path
from datetime import datetime, timezone

H = Path(__file__).resolve().parent.parent
CACHE = H / "cache"

# ── Preview база — путь от корня сайта/репозитория ──
PREVIEW_PATH = "projects/ai-ofm-tribute/content/sessions/{name}/preview.html"

def jload(p):
    if not p.exists(): return None
    try: return json.loads(p.read_text())
    except: return None

def strip(text):
    if not text: return ""
    c = re.sub(r'<[^>]+>', '', text)
    for e in [('&amp;','&'),('&lt;','<'),('&gt;','>'),('&quot;','"'),('&#39;',"'"),('&#039;',"'"),('&#x27;',"'"),('&#47;','/'),('&#x2F;','/')]:
        c = c.replace(*e)
    return re.sub(r'\s+', ' ', c).strip()[:300]

# ── Фильтры ──
# AI: только инструменты + заработок
AI_BLOCK = re.compile(
    r'(teacher|Bernanke|Trust|reflect|buddy|reflection|government|'
    r'national security|LGBTQ|pride|Deutsche Telekom|rewiring|telecommunications|'
    r'Getting started|partner for your|ambitious work|'
    r'How .* teams use|hard questions)', re.I)
AI_KEEP = re.compile(
    r'(GPT|Claude Sonnet|model|API|SDK|tool|code|agent|'
    r'autonomous|deploy|launch|release|upgrade|'
    r'earn|profit|invest|business|enterprise|'
    r'pricing|benchmark|performance|speed|'
    r'Fable \d|jailbreak|bug bounty|cyber safeguard)', re.I)
def ai_keep(t, d):
    s = f"{t} {d}"
    if AI_BLOCK.search(s): return False
    return bool(AI_KEEP.search(s))

# Tech: только полезное (без развлечений)
TECH_BLOCK = re.compile(
    r'(Jurassic Park|Super Mario|LeMario|Vancouver PD|Quick Escape|'
    r'Probably check on your smart|book review|retro gaming)', re.I)

# ── CPA — без фильтра дат ──
def is_recent(e):
    return True  # CPA entries: keep regardless of date

# ── Collectors ──
def get_yt():
    d = jload(CACHE / "youtube_watch" / "latest.json")
    if not d: return []
    out = []
    for ch in d.get("results", []):
        ci = ch.get("channel_id", "?")
        for e in ch.get("entries", []):
            out.append({"c": "📺 YouTube", "s": ci[:20], "t": e.get("title", "?"),
                        "u": e.get("url", ""), "d": strip(e.get("description", ""))})
    return out

def get_rss():
    d = jload(CACHE / "rss_monitor" / "latest.json")
    if not d: return []
    cm = {"cpa-news": "💰 CPA / Арбитраж", "ai": "🤖 AI", "tech": "🖥 Tech"}
    out = []
    for fid, fd in d.get("feeds", {}).items():
        # rss_monitor.py saves feeds as list of entries directly, not as dict with 'topic'/'entries'
        # Find the topic from the original FEEDS config
        topic_map = {
            "partnerkin": "cpa-news",
            "affiliatefix": "cpa-news",
            "openai_blog": "ai",
            "anthropic_rsshub": "ai",
            "hackernews": "tech",
        }
        topic = topic_map.get(fid, "?")
        cat = cm.get(topic, f"📄 {topic}")
        is_cpa = cat == "💰 CPA / Арбитраж"
        for e in fd if isinstance(fd, list) else fd.get("entries", []):
            if not is_recent(e): continue
            desc = strip(e.get("summary", "") or e.get("description", "") or "")
            # Для CPA показываем всё, для остальных нужны описания
            if not is_cpa and not desc: continue
            if cat == "🤖 AI" and not ai_keep(e.get("title",""), desc): continue
            if cat == "🖥 Tech" and TECH_BLOCK.search(f"{e.get('title','')} {desc}"): continue
            out.append({"c": cat, "s": fid, "t": e.get("title","Untitled"),
                        "u": e.get("url",""), "d": desc, "p": e.get("published","")})
    return out

def get_ofm():
    od = H / "projects" / "ai-ofm-tribute" / "content" / "sessions"
    if not od.exists(): return {"s": 0, "i": 0, "sessions": []}
    sessions = []
    for d in sorted(od.iterdir()):
        if not d.is_dir(): continue
        mf = d / "manifest.json"
        if not mf.exists():
            jpgs = list(d.glob("*.jpg")) + list(d.glob("*.png"))
            if jpgs:
                sessions.append({"id": d.name, "style": "?", "cnt": len(jpgs),
                                 "model": "?", "pv": None, "note": "нет манифеста"})
            continue
        try:
            m = json.loads(mf.read_text())
            cnt = m.get("success_count")
            if cnt is None: cnt = len(m.get("images", []))
            if not cnt: continue
            pf = d / "preview.html"
            pv = PREVIEW_PATH.format(name=d.name) if pf.exists() else None
            sessions.append({"id": d.name, "style": m.get("style","?"), "cnt": cnt,
                             "model": m.get("model","flux"), "pv": pv, "note": ""})
        except: pass
    return {"s": len(sessions), "i": sum(s["cnt"] for s in sessions), "sessions": sessions}

# ── HTML ──
SI = {"fantasy": "🧝", "anime": "🌸", "realistic": "📸"}

HTML = """<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Дайджест — {date}</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:-apple-system,'Segoe UI',system-ui,sans-serif;background:#0d1117;color:#e6edf3;padding:20px;max-width:960px;margin:0 auto}}
h1{{color:#ff6b9d;font-size:24px;margin-bottom:4px}}
.subtitle{{color:#8b949e;font-size:14px;margin-bottom:24px}}
.category{{background:#161b22;border:1px solid #30363d;border-radius:8px;padding:16px 20px;margin-bottom:16px}}
.category h2{{color:#f0f6fc;font-size:18px;margin-bottom:12px;display:flex;align-items:center;gap:8px}}
.count{{color:#8b949e;font-size:13px;font-weight:400;background:#21262d;padding:2px 8px;border-radius:10px}}
.item{{padding:8px 0;border-bottom:1px solid #21262d}}
.item:last-child{{border-bottom:none}}
.item a{{color:#58a6ff;text-decoration:none;font-size:15px;font-weight:500}}
.item a:hover{{color:#79c0ff;text-decoration:underline}}
.item .desc{{color:#8b949e;font-size:13px;margin-top:2px;line-height:1.4}}
.tag{{display:inline-block;background:#1f2937;color:#8b949e;font-size:11px;padding:1px 6px;border-radius:4px;margin-right:6px;vertical-align:middle}}
.pub{{color:#484f58;font-size:11px;margin-right:8px}}
.ofm-table{{width:100%;border-collapse:collapse;font-size:14px}}
.ofm-table th{{text-align:left;color:#8b949e;font-weight:500;padding:6px 8px;border-bottom:1px solid #30363d}}
.ofm-table td{{padding:5px 8px;border-bottom:1px solid #21262d}}
.ofm-table a{{color:#58a6ff;text-decoration:none}}
.ofm-table .note{{color:#da3633;font-size:11px}}
.stats{{display:flex;gap:12px;flex-wrap:wrap;margin-bottom:20px}}
.stat-card{{background:#161b22;border:1px solid #30363d;border-radius:8px;padding:12px 16px;flex:1;min-width:120px}}
.stat-card .num{{color:#f0f6fc;font-size:22px;font-weight:600}}
.stat-card .label{{color:#8b949e;font-size:12px;margin-top:2px}}
.footer{{color:#484f58;font-size:11px;text-align:center;margin-top:24px;padding-top:12px;border-top:1px solid #21262d}}
</style>
</head>
<body>
<h1>Ежедневный дайджест</h1>
<p class="subtitle">{date}</p>
<div class="stats">
<div class="stat-card"><div class="num">{n}</div><div class="label">записей</div></div>
<div class="stat-card"><div class="num">{oi}</div><div class="label">изображений</div></div>
<div class="stat-card"><div class="num">{os}</div><div class="label">сессий OFM</div></div>
</div>
{cats}
{ofm}
<div class="footer">Сгенерировано {date} · YouTube, Partnerkin, AffiliateFix, OpenAI, Anthropic, HN</div>
</body>
</html>"""

OFM_T = '<div class="category"><h2>🎨 AI OFM <span class="count">{s} сессий · {i} изображений</span></h2><table class="ofm-table"><tr><th>#</th><th>Стиль</th><th>Кол-во</th><th>Модель</th><th>Preview</th></tr>{r}</table></div>'

def fi(item):
    u = item.get("u",""); t = item.get("t","Untitled")[:120]; d = item.get("d","")
    sb = item.get("s",""); pb = item.get("p","")
    pt = f'<span class="pub">{pb[:16]}</span>' if pb else ""
    st = f'<span class="tag">{sb}</span>' if sb else ""
    lk = f'<a href="{u}" target="_blank">{t}</a>' if u else f"<strong>{t}</strong>"
    dh = f'<p class="desc">{d}</p>' if d else ""
    return f'<div class="item">{st}{pt}{lk}{dh}</div>'

def gen(yt, rss, ofm):
    dt = datetime.now().strftime("%Y-%m-%d %H:%M")
    cats = {}
    ordr = ["💰 CPA / Арбитраж", "🤖 AI", "🖥 Tech", "📺 YouTube"]
    for i in yt+rss:
        cats.setdefault(i["c"], []).append(i)
    cb = ""
    for c in ordr:
        its = cats.get(c, [])
        if not its: continue
        cb += f'<div class="category"><h2>{c} <span class="count">{len(its)}</span></h2>{"".join(fi(i) for i in its)}</div>'
    ob = ""
    if ofm["sessions"]:
        rs = ""
        for s in ofm["sessions"]:
            si = SI.get(s["style"], "🎨")
            pv = f'<a href="{s["pv"]}" target="_blank">👁</a>' if s.get("pv") else "—"
            nt = f' <span class="note">{s["note"]}</span>' if s.get("note") else ""
            rs += f"<tr><td>{s['id']}{nt}</td><td>{si} {s['style']}</td><td>{s['cnt']}</td><td>{s['model']}</td><td>{pv}</td></tr>\n"
        ob = OFM_T.format(s=ofm["s"], i=ofm["i"], r=rs)
    n = len(yt)+len(rss)
    return HTML.format(date=dt, n=n, oi=ofm["i"], os=ofm["s"], cats=cb, ofm=ob)

def save(h):
    # Сохраняем в корень репо — чтобы preview-ссылки работали
    (H / "digest.html").write_text(h, "utf-8")
    print(f"File: {H / 'digest.html'}")
    # Копия для HTTP-сервера (порт 8766)
    (H / "dashboard_data").mkdir(parents=True, exist_ok=True)
    (H / "dashboard_data" / "digest.html").write_text(h, "utf-8")
    print(f"HTTP: http://localhost:8766/digest.html")

def main():
    import argparse
    ap = argparse.ArgumentParser(); ap.add_argument("--text", action="store_true")
    a = ap.parse_args()
    yt = get_yt(); rss = get_rss(); of = get_ofm()
    if a.text:
        print(f"Дайджест {datetime.now():%Y-%m-%d %H:%M}")
        print(f"  YouTube: {len(yt)} · RSS: {len(rss)} · OFM: {of['i']} img / {of['s']} sess")
        print(f"  File: {H / 'digest.html'}  HTTP: http://localhost:8766/digest.html")
    else:
        save(gen(yt, rss, of))
        cats = {}
        for i in yt+rss:
            cats.setdefault(i["c"], []).append(i)
        print(f"  {len(yt)+len(rss)} записей: " + " · ".join(f"{c} {len(v)}" for c,v in cats.items()))
        print(f"  OFM: {of['i']} img / {of['s']} сессий")

if __name__ == "__main__":
    main()

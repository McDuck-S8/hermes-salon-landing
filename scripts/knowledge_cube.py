#!/usr/bin/env python3
"""
Knowledge Cube — multidimensional experience indexing.
3 base axes + dynamic dimension discovery + white spots.
"""

import json, os, sqlite3, hashlib
from pathlib import Path
from datetime import datetime
from collections import Counter

HERMES_HOME = Path(os.environ.get("HERMES_HOME", os.path.expanduser("~/.hermes")))
DB_PATH = HERMES_HOME / "cache" / "knowledge_cube.db"

def get_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS experiences (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts TEXT NOT NULL, raw_text TEXT NOT NULL, hash TEXT UNIQUE NOT NULL,
            axis_time_hour INTEGER, axis_time_dow INTEGER,
            axis_domain TEXT, axis_outcome TEXT,
            dynamic_axes TEXT DEFAULT '{}',
            is_white_spot INTEGER DEFAULT 0, white_spot_cluster_id TEXT,
            source TEXT, confidence REAL DEFAULT 1.0, tags TEXT DEFAULT '[]'
        );
        CREATE TABLE IF NOT EXISTS dimensions (
            name TEXT PRIMARY KEY, discovered_at TEXT NOT NULL,
            source TEXT, dim_values TEXT DEFAULT '[]', description TEXT
        );
        CREATE TABLE IF NOT EXISTS white_spot_clusters (
            cluster_id TEXT PRIMARY KEY, formed_at TEXT NOT NULL,
            size INTEGER, representative_text TEXT,
            proposed_dimension TEXT, status TEXT DEFAULT 'pending'
        );
        CREATE INDEX IF NOT EXISTS idx_exp_domain ON experiences(axis_domain);
        CREATE INDEX IF NOT EXISTS idx_exp_outcome ON experiences(axis_outcome);
        CREATE INDEX IF NOT EXISTS idx_exp_white ON experiences(is_white_spot);
        CREATE INDEX IF NOT EXISTS idx_exp_ts ON experiences(ts);
    """)
    base_dims = [
        ("time_hour", "base", "[]", "Hour of day (0-23)"),
        ("time_dow", "base", "[]", "Day of week (0=Mon, 6=Sun)"),
        ("domain", "base", "[]", "Task domain / skill area"),
        ("outcome", "base", "['success','failure','partial']", "Task outcome"),
    ]
    for name, src, vals, desc in base_dims:
        conn.execute("INSERT OR IGNORE INTO dimensions (name, discovered_at, source, dim_values, description) VALUES (?,?,?,?,?)",
                     (name, datetime.now().isoformat(), src, vals, desc))
    conn.commit()
    return conn

def compute_hash(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]

def classify_domain(text, tools=None):
    t = (text + " " + " ".join(tools or [])).lower()
    domains = {
        "coding": ["code","python","javascript","bug","function","class","import","debug","refactor","git"],
        "research": ["search","web_search","find","analyze","compare","review","paper","study"],
        "devops": ["docker","deploy","server","nginx","config","cron","ci","cd","pipeline"],
        "data": ["data","csv","json","database","sql","pandas","analysis","chart"],
        "communication": ["email","telegram","message","send","notify","slack"],
        "file_ops": ["file","read","write","directory","path","copy","move"],
        "browser": ["browser","web","page","url","click","navigate","scrape"],
        "design": ["design","ui","ux","layout","typography","color","glassmorphism","modern","trend","css","html","frontend"],
        "creative": ["image","generate","write","story","creative"],
        "system": ["install","config","setup","env","path","permission","process"],
    }
    scores = {d: sum(1 for kw in kws if kw in t) for d, kws in domains.items()}
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else "uncategorized"

def classify_outcome(text):
    t = text.lower()
    if any(w in t for w in ["success","done","completed","fixed","resolved","working","ok","pass"]):
        return "success"
    elif any(w in t for w in ["fail","error","broken","wrong","issue","problem","crash"]):
        return "failure"
    elif any(w in t for w in ["partial","progress","started","attempt"]):
        return "partial"
    return "unknown"

def auto_tag(text, tools=None):
    tags = set()
    combined = (text + " " + " ".join(tools or [])).lower()
    for tool in ["terminal","browser","web_search","file","code","delegate_task","execute_code"]:
        if tool in combined:
            tags.add(f"tool:{tool}")
    wc = len(text.split())
    tags.add("complexity:high" if wc > 500 else "complexity:medium" if wc > 100 else "complexity:low")
    if any(w in combined for w in ["again","recurring","repeated"]):
        tags.add("pattern:recurring")
    if any(w in combined for w in ["new","first","novel","initial"]):
        tags.add("pattern:novel")
    return list(tags)

def detect_white_spot(text, domain, outcome, dynamic_axes):
    reasons = []
    if domain == "uncategorized": reasons.append("unknown_domain")
    if outcome == "unknown": reasons.append("unknown_outcome")
    for dim, val in (dynamic_axes or {}).items():
        if val in ("?","unknown","unclassified"): reasons.append(f"unknown_{dim}")
    return len(reasons) > 0, reasons

def add_experience(text, tools=None, source="session", dynamic_axes=None):
    conn = get_db()
    h = compute_hash(text)
    if conn.execute("SELECT id FROM experiences WHERE hash=?", (h,)).fetchone():
        conn.close(); return {"status": "duplicate"}
    now = datetime.now()
    domain = classify_domain(text, tools)
    outcome = classify_outcome(text)
    tags = auto_tag(text, tools)
    dynamic = dynamic_axes or {}
    is_white, white_reasons = detect_white_spot(text, domain, outcome, dynamic)
    conn.execute("""INSERT INTO experiences (ts,raw_text,hash,axis_time_hour,axis_time_dow,
        axis_domain,axis_outcome,dynamic_axes,is_white_spot,source,tags) VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
        (now.isoformat(), text, h, now.hour, now.weekday(), domain, outcome,
         json.dumps(dynamic), 1 if is_white else 0, source, json.dumps(tags)))
    conn.commit(); conn.close()
    return {"status":"added","domain":domain,"outcome":outcome,"tags":tags,
            "is_white_spot":is_white,"white_reasons":white_reasons}

def query_cube(domain=None, outcome=None, hour_range=None, dow=None, is_white_spot=None, limit=50):
    conn = get_db()
    conds, params = [], []
    if domain: conds.append("axis_domain=?"); params.append(domain)
    if outcome: conds.append("axis_outcome=?"); params.append(outcome)
    if hour_range: conds.append("axis_time_hour BETWEEN ? AND ?"); params.extend(hour_range)
    if dow is not None: conds.append("axis_time_dow=?"); params.append(dow)
    if is_white_spot is not None: conds.append("is_white_spot=?"); params.append(1 if is_white_spot else 0)
    where = " AND ".join(conds) if conds else "1=1"
    rows = conn.execute(f"SELECT * FROM experiences WHERE {where} ORDER BY ts DESC LIMIT ?", params+[limit]).fetchall()
    conn.close(); return [dict(r) for r in rows]

def get_white_spots(limit=100):
    return query_cube(is_white_spot=True, limit=limit)

def cluster_white_spots():
    spots = get_white_spots(500)
    if not spots: return []
    stopwords = {"the","a","an","is","was","were","are","be","been","have","has","had","do","does","did",
        "will","would","could","should","may","might","shall","can","to","of","in","for","on","with",
        "at","by","from","as","into","through","during","before","after","above","below","between",
        "out","off","over","under","again","further","then","once","and","but","or","nor","not","so",
        "very","just","than","too","also","it","its","this","that","i","me","my","we","our","you",
        "your","he","him","his","she","her","they","them","what","which","who","when","where","why",
        "how","all","each","every","both","few","more","most","other","some","such","no","only","own",
        "same","if","because","about","up","down","been","being","into"}
    spot_kw = [(s["id"], set(s["raw_text"].lower().split()) - stopwords) for s in spots]
    clusters, used = [], set()
    for i,(id1,kw1) in enumerate(spot_kw):
        if id1 in used: continue
        cluster, cluster_kw = [id1], set(kw1)
        for j,(id2,kw2) in enumerate(spot_kw):
            if i==j or id2 in used: continue
            if len(kw1 & kw2) >= 3:
                cluster.append(id2); cluster_kw &= kw2; used.add(id2)
        if len(cluster) >= 3:
            used.add(id1)
            rep = next(s for s in spots if s["id"]==cluster[0])["raw_text"][:200]
            cid = f"ws_{hashlib.md5(str(cluster).encode()).hexdigest()[:8]}"
            clusters.append({"cluster_id":cid,"size":len(cluster),"shared_keywords":list(cluster_kw)[:10],"representative_text":rep,"ids":cluster})
    conn = get_db()
    for c in clusters:
        conn.execute("INSERT OR REPLACE INTO white_spot_clusters (cluster_id,formed_at,size,representative_text,status) VALUES (?,?,?,?,?)",
            (c["cluster_id"], datetime.now().isoformat(), c["size"], c["representative_text"], "pending"))
        for sid in c["ids"]:
            conn.execute("UPDATE experiences SET white_spot_cluster_id=? WHERE id=?", (c["cluster_id"], sid))
    conn.commit(); conn.close()
    return clusters

def get_cube_stats():
    conn = get_db()
    total = conn.execute("SELECT COUNT(*) as c FROM experiences").fetchone()["c"]
    white = conn.execute("SELECT COUNT(*) as c FROM experiences WHERE is_white_spot=1").fetchone()["c"]
    domains = conn.execute("SELECT axis_domain, COUNT(*) as c FROM experiences GROUP BY axis_domain ORDER BY c DESC").fetchall()
    outcomes = conn.execute("SELECT axis_outcome, COUNT(*) as c FROM experiences GROUP BY axis_outcome ORDER BY c DESC").fetchall()
    dims = conn.execute("SELECT * FROM dimensions").fetchall()
    clusters = conn.execute("SELECT * FROM white_spot_clusters WHERE status='pending'").fetchall()
    conn.close()
    return {"total_experiences":total,"white_spots":white,
            "white_spot_pct": round(white/total*100,1) if total else 0,
            "domains":{r["axis_domain"]:r["c"] for r in domains},
            "outcomes":{r["axis_outcome"]:r["c"] for r in outcomes},
            "dimensions":[dict(d) for d in dims],
            "pending_clusters":[dict(c) for c in clusters]}

def ingest_from_outcomes():
    outcomes_dir = HERMES_HOME / "cache" / "outcomes"
    if not outcomes_dir.exists(): return 0
    imported = 0
    for f in sorted(outcomes_dir.glob("outcomes_*.jsonl")):
        for line in f.read_text(encoding="utf-8").strip().split("\n"):
            if not line.strip(): continue
            try:
                o = json.loads(line)
                text = o.get("task_prompt","") + " -> " + o.get("final_result","")[:500]
                r = add_experience(text=text, tools=o.get("tools_used",[]), source="outcome_tracker",
                    dynamic_axes={"task_type":o.get("task_type","unknown"),
                                  "duration":str(o.get("duration_seconds","?")),
                                  "tool_count":str(o.get("tool_count","?"))})
                if r["status"]=="added": imported += 1
            except: pass
    return imported

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: knowledge_cube.py <add|query|white-spots|cluster|stats|ingest-outcomes> [args]")
        sys.exit(1)
    cmd = sys.argv[1]
    if cmd == "add":
        r = add_experience(" ".join(sys.argv[2:])); print(json.dumps(r, indent=2))
    elif cmd == "query":
        kwargs = {}
        for arg in sys.argv[2:]:
            if "=" in arg:
                k,v = arg.split("=",1)
                if k=="hour_range": kwargs[k]=(int(v.split("-")[0]),int(v.split("-")[1]))
                elif k=="dow": kwargs[k]=int(v)
                else: kwargs[k]=v
        for r in query_cube(**kwargs):
            print(f"[{r['ts'][:16]}] {r['axis_domain']}/{r['axis_outcome']} {'W' if r['is_white_spot'] else 'O'} {r['raw_text'][:100]}")
    elif cmd == "white-spots":
        for s in get_white_spots(): print(f"  [{s['ts'][:16]}] {s['raw_text'][:120]}")
    elif cmd == "cluster":
        for c in cluster_white_spots(): print(f"  {c['cluster_id']}: {c['size']} spots, kw={c['shared_keywords'][:5]}")
    elif cmd == "stats":
        import json; print(json.dumps(get_cube_stats(), indent=2))
    elif cmd == "ingest-outcomes":
        print(f"Imported {ingest_from_outcomes()} experiences")

# ═══════════════════════════════════════════════════════════════
# THREE PILLARS OF KNOWLEDGE BEING (ТРОИЦА)
# ═══════════════════════════════════════════════════════════════

WHITE_SPOT = "white"      # Void — I know I don't know
NORMAL = "normal"          # Known — I know I know
RED_ANOMALY = "red"        # Anomaly — I don't know I don't know

ANOMALY_TYPES = {
    "hidden_advantage":     "Что выглядит как проблема, но на самом деле преимущество",
    "expectation_mismatch": "Несовпадение ожиданий — проблема не там где кажется",
    "missing_structure":    "Отсутствие системы — не случайность, а структурный пробел",
    "root_cause_disguise":  "Одна причина маскируется под много проблем",
    "role_ambiguity":       "Роли не определены — и это источник напряжения",
    "memory_paradox":       "Знания есть, но не влияют на решения",
    "growth_indicator":     "Рост белых пятен — не баг, а признак развития",
}


def classify_experience(exp: dict) -> str:
    """Classify experience into one of three pillars."""
    if exp.get("is_white_spot"):
        return WHITE_SPOT
    if exp.get("axis_outcome", exp.get("axis_outcome", exp.get("outcome"))) == "failure":
        return RED_ANOMALY
    return NORMAL


def get_three_pillars() -> dict:
    """Get the three-pillar distribution: white/normal/red."""
    with get_db() as conn:
        ws = conn.execute("SELECT COUNT(*) FROM experiences WHERE is_white_spot = 1").fetchone()[0]
        red = conn.execute("SELECT COUNT(*) FROM experiences WHERE axis_outcome = 'failure'").fetchone()[0]
        total = conn.execute("SELECT COUNT(*) FROM experiences").fetchone()[0]
        normal = total - ws - red

    return {
        "white": ws, "normal": normal, "red": red, "total": total,
        "white_pct": round(ws / total * 100, 1) if total else 0,
        "normal_pct": round(normal / total * 100, 1) if total else 0,
        "red_pct": round(red / total * 100, 1) if total else 0,
    }


def get_red_anomalies(limit: int = 20) -> list:
    """Get experiences classified as red anomalies."""
    with get_db() as conn:
        rows = conn.execute("""
            SELECT id, raw_text, domain, outcome, tools_used, created_at, dynamic_axes
            FROM experiences
            WHERE axis_outcome = 'failure'
            ORDER BY created_at DESC
            LIMIT ?
        """, (limit,)).fetchall()

    return [
        {"id": r[0], "raw_text": r[1], "domain": r[2], "outcome": r[3],
         "tools_used": json.loads(r[4]) if r[4] else [],
         "created_at": r[5], "dynamic_axes": json.loads(r[6]) if r[6] else {}}
        for r in rows
    ]


def detect_anomalies() -> list:
    """Detect hidden patterns — red anomalies from experience data."""
    with get_db() as conn:
        rows = conn.execute(
            "SELECT raw_text, axis_domain, axis_outcome, tags, is_white_spot, dynamic_axes FROM experiences"
        ).fetchall()

    experiences = [
        {"raw_text": r[0], "axis_domain": r[1], "axis_outcome": r[2],
         "tags": json.loads(r[3]) if r[3] else [], "is_white_spot": r[4],
         "dynamic_axes": r[5] if len(r) > 5 else "{}"}
        for r in rows
    ]

    anomalies = []

    # 1. Repeating failure patterns (3+ failures in same domain)
    failure_domains = {}
    for exp in experiences:
        if exp.get("axis_outcome") == "failure":
            d = exp.get("axis_domain", "unknown")
            failure_domains.setdefault(d, []).append(exp)

    for domain, fails in failure_domains.items():
        if len(fails) >= 3:
            anomalies.append({
                "type": "root_cause_disguise",
                "domain": domain,
                "count": len(fails),
                "description": f"{len(fails)} провалов в домене \'{domain}\' — возможна одна корневая причина",
            })

    # 2. White spot growth
    ws = sum(1 for e in experiences if e.get("is_white_spot"))
    total = len(experiences)
    if total > 10 and ws / total > 0.6:
        anomalies.append({
            "type": "growth_indicator",
            "white_pct": round(ws / total * 100),
            "description": f"{round(ws/total*100)}% белых пятен — растём быстрее чем понимаем",
        })

    # 3. Tool switching (4+ tools in tags, but skip if decision_matrix exists)
    for exp in experiences:
        tool_tags = [t for t in exp.get("tags", []) if t.startswith("tool:")]
        if len(tool_tags) >= 4:
            # Check if decision matrix already recorded
            dynamic = exp.get("dynamic_axes", "{}")
            if isinstance(dynamic, str):
                try:
                    import json as _json
                    dynamic = _json.loads(dynamic)
                except:
                    dynamic = {}
            if isinstance(dynamic, dict) and "decision_matrix" in dynamic:
                continue  # Already has matrix, skip
            anomalies.append({
                "type": "missing_structure",
                "tools": tool_tags,
                "description": f"Для задачи использовано {len(tool_tags)} инструментов — нет матрицы решений",
            })

    # 4. Contradictions (success + failure in same domain)
    domain_outcomes = {}
    for exp in experiences:
        d = exp.get("axis_domain", "unknown")
        domain_outcomes.setdefault(d, set()).add(exp.get("axis_outcome"))

    for domain, outcomes in domain_outcomes.items():
        if "success" in outcomes and "failure" in outcomes:
            anomalies.append({
                "type": "hidden_advantage",
                "domain": domain,
                "outcomes": list(outcomes),
                "description": f"Домен \'{domain}\' имеет и успехи и провалы — скрытая структура",
            })

    return anomalies

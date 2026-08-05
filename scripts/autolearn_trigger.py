#!/usr/bin/env python3
"""autolearn_trigger.py — Автопилот самоанализа (ТЗ 2026-08-04).

Проверяет состояние граней/чувств и запускает recursive_self_analysis.py,
когда система «застаивается». Вызывается из system_heartbeat_fixer.py.

Триггеры (пороги из self_model.json autolearn_params):
  reflex < 5%            -> 10 циклов
  control < 3%           -> 8 циклов
  reflex+control < 10%   -> 15 циклов
  stagnation > 0.5       -> 20 циклов
  не запускались > 7дн   -> 10 циклов
Cooldown 6ч (12ч после неудачного запуска); 3 неудачи подряд — стоп + уведомление.
"""
import json, os, sqlite3, subprocess, sys
from datetime import datetime, timedelta
from pathlib import Path

HERMES_HOME = Path(__file__).resolve().parent.parent
SELF_MODEL = HERMES_HOME / "cache" / "self_model.json"
KC = HERMES_HOME / "cache" / "knowledge_cube.db"
SCRIPT = HERMES_HOME / "scripts" / "recursive_self_analysis.py"

DEFAULT_PARAMS = {
    "reflex_threshold": 5.0,
    "control_threshold": 3.0,
    "sum_threshold": 10.0,
    "stagnation_threshold": 0.5,
    "max_cycles": 20,
    "cooldown_hours": 6,
    "cooldown_fail_hours": 12,
    "max_fail_streak": 3,
    "idle_days": 7,
}


def load_params() -> dict:
    """autolearn_params из self_model.json (кристалл может править) + дефолты."""
    p = dict(DEFAULT_PARAMS)
    try:
        data = json.loads(SELF_MODEL.read_text(encoding="utf-8"))
        p.update(data.get("autolearn_params", {}))
    except Exception:
        pass
    return p


def _grani(db=None) -> dict:
    """Канонические грани из self_model.json grani (как reflex_metrics в chain_heartbeat)."""
    try:
        facets = json.loads(SELF_MODEL.read_text(encoding="utf-8")).get("grani", {})
        total = sum(facets.values()) or 1
        return {
            "reflex_pct": round(facets.get("Рефлексия", 0) * 100.0 / total, 1),
            "control_pct": round(facets.get("Управление", 0) * 100.0 / total, 1),
        }
    except Exception:
        return {"reflex_pct": 0.0, "control_pct": 0.0}


def stagnation_score(db) -> float:
    """0..1: доля «пустых» суток за последние 7 дней (нет записей в Кубе)."""
    try:
        rows = db.execute("SELECT ts FROM experiences WHERE ts >= ?",
                          [(datetime.now() - timedelta(days=7)).isoformat()]).fetchall()
        days = {r[0][:10] for r in rows}
        return round(1.0 - len(days) / 7.0, 2)
    except Exception:
        return 0.0


def should_learn(metrics: dict, params: dict) -> tuple[bool, str]:
    """Решение о запуске. metrics: reflex_pct, control_pct, stagnation, triad."""
    r = metrics.get("reflex_pct", 0.0)
    c = metrics.get("control_pct", 0.0)
    stag = metrics.get("stagnation", 0.0)
    if r < params["reflex_threshold"]:
        return True, f"reflex {r}% < {params['reflex_threshold']}%"
    if c < params["control_threshold"]:
        return True, f"control {c}% < {params['control_threshold']}%"
    if r + c < params["sum_threshold"]:
        return True, f"reflex+control {r + c}% < {params['sum_threshold']}%"
    if stag > params["stagnation_threshold"]:
        return True, f"stagnation {stag} > {params['stagnation_threshold']}"
    # Триада образов (2026-08-05): устойчивое отклонение по образу = p < порога
    # И Байес уже учитывает повторяемость: 1 deviate при 5 conform даст p~0.56,
    # а 3 deviate при 1 conform — p~0.36 < 0.4. Порог — из autolearn_params.
    for img, t in (metrics.get("triad") or {}).items():
        if isinstance(t, dict) and t.get("deviate", 0) > 0 and t.get("p", 0.5) < params.get("triad_threshold", 0.4):
            return True, f"triad {img} p={t['p']} < {params.get('triad_threshold', 0.4)} (deviate={t['deviate']})"
    return False, "в норме"


def calculate_cycles(metrics: dict, params: dict) -> int:
    """Selftuning: чем ниже грани — тем глубже прогон. clamp [3, max_cycles]."""
    r = metrics.get("reflex_pct", 0.0)
    c = metrics.get("control_pct", 0.0)
    cycles = round((params["reflex_threshold"] - r) * 3 + (params["control_threshold"] - c) * 2)
    return max(3, min(params["max_cycles"], cycles))


def log_event(db, tag: str, note: str):
    """Запись запуска/результата в Куб (домен self_learning), дедуп по content."""
    try:
        now = datetime.now()
        text = f"[self_learning] {tag}: {note}"
        cur = db.execute("SELECT COUNT(*) FROM experiences WHERE content=?", [text])
        if cur.fetchone()[0] > 0:
            return
        h = __import__("hashlib").md5(text.encode("utf-8")).hexdigest()[:16]
        db.execute(
            "INSERT INTO experiences (ts, content, raw_text, hash, axis_time_hour, axis_time_dow, axis_domain, axis_outcome, source) "
            "VALUES (?,?,?,?,?,?,?,?,?)",
            (now.isoformat(), text, text, h, now.hour, now.weekday(), "self_learning", "success", "autolearn"))
        db.commit()
    except Exception as e:
        print(f"[autolearn] не записал событие {tag}: {e}")


def check_and_trigger(metrics: dict | None = None) -> dict:
    """Основная логика: проверить -> решить -> запустить -> записать результат."""
    params = load_params()
    db = sqlite3.connect(KC)
    gm = _grani(db)
    try:
        sys.path.insert(0, str(HERMES_HOME / "scripts"))
        from chain_heartbeat import compute_triad
        triad = compute_triad()
    except Exception:
        triad = {}
    if metrics is None:
        metrics = {**gm, "stagnation": stagnation_score(db), "triad": triad}
    else:
        metrics = {**gm, **metrics}
        metrics.setdefault("triad", triad)

    # cooldown: не чаще чем раз в N часов (любая последняя запись; FAIL удваивает)
    try:
        row = db.execute(
            "SELECT raw_text, ts FROM experiences WHERE source='autolearn' ORDER BY id DESC LIMIT 1").fetchone()
        if row:
            last_ts = datetime.fromisoformat(row[1])
            cooldown = params["cooldown_fail_hours"] if "FAIL" in (row[0] or "") else params["cooldown_hours"]
            if datetime.now() - last_ts < timedelta(hours=cooldown):
                db.close()
                return {"triggered": False, "reason": f"cooldown {cooldown}ч", "metrics": metrics}
    except Exception:
        pass

    ok, reason = should_learn(metrics, params)
    if not ok:
        db.close()
        return {"triggered": False, "reason": reason, "metrics": metrics}

    # 3 неудачи подряд — стоп
    try:
        fails = db.execute(
            "SELECT COUNT(*) FROM experiences WHERE source='autolearn' AND raw_text LIKE '%FAIL%' AND ts >= ?",
            [(datetime.now() - timedelta(days=2)).isoformat()]).fetchone()[0]
        if fails >= params["max_fail_streak"]:
            db.close()
            return {"triggered": False, "reason": f"{fails} неудач подряд — стоп", "metrics": metrics}
    except Exception:
        pass

    cycles = calculate_cycles(metrics, params)
    log_event(db, "START", f"cycles={cycles} | {reason} | reflex={metrics['reflex_pct']}% control={metrics['control_pct']}%")
    db.close()

    try:
        r = subprocess.run([sys.executable, str(SCRIPT), "--cycles", str(cycles)],
                           capture_output=True, text=True, timeout=600, cwd=str(HERMES_HOME))
        out = r.stdout.strip()[-200:]
        db = sqlite3.connect(KC)
        if r.returncode == 0:
            log_event(db, "DONE", f"cycles={cycles} OK | {out}")
            db.close()
            return {"triggered": True, "cycles": cycles, "ok": True, "output": out, "metrics": metrics}
        log_event(db, "FAIL", f"cycles={cycles} exit={r.returncode} | {r.stderr.strip()[-150:]}")
        db.close()
        return {"triggered": True, "cycles": cycles, "ok": False, "error": r.stderr[-200:], "metrics": metrics}
    except Exception as e:
        db = sqlite3.connect(KC)
        log_event(db, "FAIL", f"cycles={cycles} exc={str(e)[:120]}")
        db.close()
        return {"triggered": True, "cycles": cycles, "ok": False, "error": str(e), "metrics": metrics}


if __name__ == "__main__":
    res = check_and_trigger()
    print(json.dumps(res, ensure_ascii=False, default=str)[:500])

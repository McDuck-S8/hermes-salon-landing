#!/usr/bin/env python3
"""
Morning Report — активирует все 3 источника проактивности.
Запускается ежедневно утром через cron.

Источник 1: User Voice — анализ твоих реакций из KC
Источник 2: Chain Heartbeat — syscheck как обязательный рефлекс
Источник 3: Ripple Engine — зрелые ключи → предложение действий
"""
import sys, os, json, sqlite3, re
from datetime import datetime, timedelta
from pathlib import Path
from collections import Counter

ROOT = Path(os.environ.get("HERMES_HOME", "D:/Portable_Soft/hermes"))
sys.path[0:0] = [str(ROOT / "scripts"), str(ROOT / "skills")]

from session_bridge import load_bridge, save_bridge

KC_DB = str(ROOT / "cache" / "knowledge_cube.db")
EE_DB = str(ROOT / "cache" / "entity_engine.db")


# ─── SOURCE 1: User Voice Analysis ──────────────────────────────

def analyze_user_voice() -> dict:
    """Read user voice entries from KC, detect sentiment patterns."""
    result = {
        "total_messages": 0,
        "sentiment": {"positive": 0, "negative": 0, "neutral": 0, "demand": 0, "correction": 0},
        "recent_signals": [],
        "signal": None,  # overall signal for today
    }

    if not os.path.exists(KC_DB):
        return result

    conn = sqlite3.connect(KC_DB)
    c = conn.cursor()

    # All user_voice entries from last 24h
    yesterday = (datetime.now() - timedelta(hours=24)).isoformat()
    c.execute("""
        SELECT raw_text, ts, axis_outcome FROM experiences
        WHERE (axis_domain = 'user_communication' OR raw_text LIKE '%user_chat%' OR content LIKE '%[user:%')
        AND ts > ?
        ORDER BY ts DESC
    """, (yesterday,))
    rows = c.fetchall()

    result["total_messages"] = len(rows)

    for text, ts, outcome in rows:
        text_lower = text.lower()

        # Sentiment keywords
        pos = bool(re.search(r'(огонь|круто|отлично|молодец|👍|✅|да|хорошо|работает|понял|принят)', text_lower))
        neg = bool(re.search(r'(говно|херня|пиздец|сраный|не работает|сломалось|ужас|плохо|опять)', text_lower))
        demand = bool(re.search(r'(сделай|запусти|начинай|приступай|реализуй|покажи|срочно|немедленно)', text_lower))
        correction = bool(re.search(r'(неправильно|ошибка|надо не|должно быть|исправь|не так)', text_lower))

        signals = []
        if pos: signals.append("positive"); result["sentiment"]["positive"] += 1
        if neg: signals.append("negative"); result["sentiment"]["negative"] += 1
        if demand: signals.append("demand"); result["sentiment"]["demand"] += 1
        if correction: signals.append("correction"); result["sentiment"]["correction"] += 1
        if not signals: signals.append("neutral"); result["sentiment"]["neutral"] += 1

        result["recent_signals"].append({
            "time": ts[:19],
            "text": text[:120],
            "signals": signals,
        })

    conn.close()

    # Determine overall signal
    s = result["sentiment"]
    if s["correction"] > 0:
        result["signal"] = "correction"
    elif s["negative"] > s["positive"] and s["negative"] > 0:
        result["signal"] = "frustration"
    elif s["demand"] > 0:
        result["signal"] = "demand"
    elif s["positive"] > s["negative"]:
        result["signal"] = "positive"
    else:
        result["signal"] = "neutral"

    # Persist to bridge
    save_bridge({"last_user_voice_analysis": {
        "ts": datetime.now().isoformat(),
        "signal": result["signal"],
        "messages_24h": result["total_messages"],
    }})

    return result


# ─── SOURCE 2: System Health Reflex ──────────────────────────────

def check_system_health() -> dict:
    """Run syscheck as mandatory reflex."""
    result = {"healthy": False, "events": "?", "alerts": "?", "details": []}

    try:
        sys.path.insert(0, str(ROOT / "scripts"))
        from chain_heartbeat import system_status, self_check
        sc = self_check(verbose=False)
        st = system_status()

        result["healthy"] = sc.get("is_healthy", False)
        s = st.get("summary", {})
        result["events"] = f"{s.get('events_healthy',0)}/{s.get('events_total',0)}"
        result["alerts"] = str(s.get("alerts_active", 0))
        result["details"] = [
            f"Events: {result['events']} healthy",
            f"Modules: {s.get('modules_healthy',0)}/{s.get('modules_total',0)}",
            f"Alerts: {s.get('alerts_active',0)}",
        ]
    except Exception as e:
        result["details"] = [f"Health check failed: {e}"]

    return result


# ─── SOURCE 3: Ripple Engine — Mature Keys ───────────────────────

def find_mature_keys() -> list:
    """Find patterns in KC that are ready to become proposals.
    Excludes auto-generated suggestions to avoid noise inflation.
    """
    keys = []

    if not os.path.exists(KC_DB):
        return keys

    conn = sqlite3.connect(KC_DB)
    c = conn.cursor()

    # Find frequently-occurring domain patterns (exclude suggestions)
    c.execute("""
        SELECT axis_domain, COUNT(*) as cnt, 
               COUNT(DISTINCT axis_outcome) as outcomes,
               SUM(CASE WHEN axis_outcome = 'success' THEN 1 ELSE 0 END) as success_count
        FROM experiences
        WHERE axis_domain IS NOT NULL AND axis_domain != ''
          AND raw_text NOT LIKE '%[suggestion:%'
        GROUP BY axis_domain
        HAVING cnt > 3
        ORDER BY cnt DESC
        LIMIT 10
    """)
    for row in c.fetchall():
        domain, cnt, outcomes, success_count = row
        keys.append({
            "type": "domain_cluster",
            "domain": domain,
            "count": cnt,
            "outcome_variety": outcomes,
            "success_count": success_count,
            "maturity": min(cnt / 5, 1.0),
        })

    # Find entities that grew recently
    if os.path.exists(EE_DB):
        ee = sqlite3.connect(EE_DB)
        ec = ee.cursor()
        yesterday = (datetime.now() - timedelta(hours=24)).isoformat()
        ec.execute("""
            SELECT name, mention_count, last_seen_ts FROM entities
            WHERE mention_count > 0 AND last_seen_ts > ?
            ORDER BY mention_count DESC
            LIMIT 5
        """, (yesterday,))
        for name, count, last_seen in ec.fetchall():
            keys.append({
                "type": "entity_growth",
                "entity": name,
                "mention_count": count,
                "last_seen": last_seen[:19] if last_seen else "?",
                "maturity": min(count / 10, 1.0),
            })
        ee.close()

    conn.close()

    # Sort by maturity
    keys.sort(key=lambda k: k["maturity"], reverse=True)
    return keys


# ─── REPORT ──────────────────────────────────────────────────────

def generate_report(user_voice: dict, health: dict, keys: list) -> str:
    """Generate the morning report text."""
    lines = []
    lines.append(f"╔══ УТРЕННИЙ ДОКЛАД ══ {datetime.now().strftime('%Y-%m-%d %H:%M')} ══╗")
    lines.append("")

    # Source 2 first (health is mandatory)
    if health["healthy"]:
        lines.append(f"✅ Система: {health['events']} events, {health['alerts']} alerts — ЗДОРОВА")
    else:
        lines.append(f"❌ Система: {health['events']} events, {health['alerts']} alerts — ПРОБЛЕМЫ")
    lines.append("")

    # Source 1: User Voice
    uv = user_voice
    signal_emoji = {
        "positive": "😊", "frustration": "😠", "correction": "🔧",
        "demand": "⚡", "neutral": "😐"
    }.get(uv["signal"], "❓")

    lines.append(f"{signal_emoji} User Voice ({uv['total_messages']} сообщ./24ч): "
                 f"👍{uv['sentiment']['positive']} "
                 f"👎{uv['sentiment']['negative']} "
                 f"🔧{uv['sentiment']['correction']} "
                 f"⚡{uv['sentiment']['demand']}")

    # If there were corrections/demands, show the latest
    recent = uv.get("recent_signals", [])
    corrections = [r for r in recent if "correction" in r.get("signals", [])]
    demands = [r for r in recent if "demand" in r.get("signals", [])]

    if corrections:
        lines.append(f"   🔧 Последняя коррекция: {corrections[0]['text'][:80]}")
    if demands:
        lines.append(f"   ⚡ Последний запрос: {demands[0]['text'][:80]}")
    lines.append("")

    # Source 3: Ripple Engine — Mature Keys
    if keys:
        lines.append(f"💎 {len(keys)} зрелых ключей:")
        for k in keys[:3]:
            if k["type"] == "domain_cluster":
                lines.append(f"   📊 {k['domain']} — {k['count']} записей, maturity={k['maturity']:.0%}")
            elif k["type"] == "entity_growth":
                lines.append(f"   🧩 {k['entity']} — {k['mention_count']} mentions (последнее: {k['last_seen']})")
        if len(keys) > 3:
            lines.append(f"   ... и ещё {len(keys)-3} ключей")
    else:
        lines.append("💎 Зрелых ключей пока нет")
    lines.append("")

    # Summary
    lines.append("─" * 44)

    if uv["signal"] == "correction":
        lines.append(f"🔧 Вывод: Принципал вносит коррективы. Проверяю направление.")
        lines.append(f"🔧 Действие: Применить коррекцию к правилам работы.")
    elif uv["signal"] == "frustration":
        lines.append(f"😠 Вывод: Принципал недоволен. Анализирую причины.")
        lines.append(f"😠 Действие: Проверить качество. Ускорить ответы. Не спрашивать.")
    elif uv["signal"] == "demand":
        lines.append(f"⚡ Вывод: Принципал в режиме команд. Повышаю приоритет.")
        lines.append(f"⚡ Действие: Выполнить последнюю команду без вопросов.")
    elif uv["signal"] == "positive":
        lines.append(f"😊 Вывод: Принципал доволен. Продолжаю в том же духе.")
        lines.append(f"😊 Действие: Усилить автономность. Меньше спрашивать.")
    else:
        lines.append(f"😐 Вывод: Принципал нейтрален. Стандартный режим.")
        lines.append(f"😐 Действие: Продолжить фоновые задачи.")

    lines.append("")
    lines.append("╚" + "═" * 44 + "╝")

    return "\n".join(lines)


def main():
    # Source 2: mandatory health check first
    health = check_system_health()
    if not health["healthy"]:
        print("❌ Система нездорова. Утренний доклад прерван.")
        print("\n".join(health["details"]))
        sys.exit(1)

    # Source 1: User Voice
    user_voice = analyze_user_voice()

    # Source 3: Ripple Engine — mature keys
    keys = find_mature_keys()
    try:
        kc = sqlite3.connect(KC_DB)
        total_raw = kc.execute("SELECT COUNT(*) FROM experiences").fetchone()[0]
        non_suggestion = kc.execute("SELECT COUNT(*) FROM experiences WHERE raw_text NOT LIKE '%[suggestion:%'").fetchone()[0]
        kc.close()
        print(f"\n📊 KC: {total_raw} total, {non_suggestion} non-suggestion ({non_suggestion/total_raw*100:.0f}% чистых)")
    except Exception as e:
        print(f"⚠️ KC stats error: {e}")
    if keys:
        report = generate_report(user_voice, health, keys)

    # Save report
    report_dir = ROOT / "reports" / "morning"
    report_dir.mkdir(parents=True, exist_ok=True)
    report_path = report_dir / f"{datetime.now().strftime('%Y-%m-%d')}.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)

    print(report)
    print(f"\n💾 Report saved: {report_path}")

    # Save JSON cache (read by auto_boot_scan at session start)
    cache = {
        "ts": datetime.now().isoformat(),
        "health": health,
        "user_voice": {
            "total_messages": user_voice["total_messages"],
            "sentiment": user_voice["sentiment"],
            "signal": user_voice["signal"],
            "recent_corrections": [r["text"] for r in user_voice.get("recent_signals", []) if "correction" in r.get("signals", [])][:2],
            "recent_demands": [r["text"] for r in user_voice.get("recent_signals", []) if "demand" in r.get("signals", [])][:2],
        },
        "mature_keys": [{
            "type": k["type"],
            "label": k.get("domain") or k.get("entity", "?"),
            "count": k.get("count") or k.get("mention_count", 0),
            "maturity": k["maturity"],
        } for k in keys[:5]],
        "top_proposal": {
            "label": keys[0]["domain"] if keys and keys[0]["type"] == "domain_cluster" else (keys[0]["entity"] if keys else None),
            "maturity": keys[0]["maturity"] if keys else 0,
        } if keys else None,
    }
    cache_path = ROOT / "cache" / "latest_morning_report.json"
    with open(cache_path, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)
    print(f"💾 Cache saved: {cache_path}")

    # Also add top proposal to bridge
    if keys:
        top = keys[0]
        save_bridge({"morning_proposal": {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "top_key": top["domain"] if top["type"] == "domain_cluster" else top["entity"],
            "maturity": top["maturity"],
            "proposal": f"Разблокировать '{top['domain'] if top['type'] == 'domain_cluster' else top['entity']}' сегодня",
        }})


if __name__ == "__main__":
    main()

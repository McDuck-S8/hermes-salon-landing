#!/usr/bin/env python3
"""
Auto Boot Scan — runs at session start.
Checks: principal identity, EE sync freshness, heartbeat, stale files.
Auto-fixes what it can, reports what it can't.
"""
import json, os, sqlite3, sys
from pathlib import Path
from datetime import datetime, timedelta

ROOT = Path(os.environ.get("HERMES_HOME", "D:/Portable_Soft/hermes"))
sys.path.insert(0, str(ROOT / "scripts"))

from session_bridge import load_bridge, save_bridge, add_commitment
from datetime import datetime

def check_principal_identity():
    """g-006: Verify principal identity exists and is confirmed."""
    bridge = load_bridge()
    name = bridge.get("principal_name", "Александр")
    confirmed = bridge.get("principal_confirmed", False)
    
    # Check EE
    ee_path = ROOT / "cache" / "entity_engine.db"
    if ee_path.exists():
        conn = sqlite3.connect(str(ee_path))
        c = conn.cursor()
        c.execute("SELECT mention_count FROM entities WHERE name=? COLLATE NOCASE", (name,))
        row = c.fetchone()
        ee_count = row[0] if row else 0
        conn.close()
    else:
        ee_count = 0
    
    if not confirmed or ee_count == 0:
        print(f"⚠️  Principal '{name}' not confirmed in EE (count={ee_count})")
        # Try to sync
        try:
            from record_user_to_kc import record_principal_fact, sync_ee_from_kc
            sync_ee_from_kc()
            ee_path = ROOT / "cache" / "entity_engine.db"
            conn = sqlite3.connect(str(ee_path))
            c = conn.cursor()
            c.execute("SELECT mention_count FROM entities WHERE name=? COLLATE NOCASE", (name,))
            row = c.fetchone()
            ee_count = row[0] if row else 0
            conn.close()
            if ee_count > 0:
                save_bridge({"principal_confirmed": True})
                print(f"✅ Principal '{name}' confirmed (count={ee_count})")
            else:
                print(f"❌ Cannot confirm principal. Run scripts/record_user_to_kc.py --init")
        except Exception as e:
            print(f"❌ Principal sync failed: {e}")
    else:
        print(f"✅ Principal '{name}' confirmed (count={ee_count})")
    
    return ee_count > 0


def check_ee_sync_freshness():
    """Check if EE-KC sync is recent (< 1 hour)."""
    bridge = load_bridge()
    last_sync = bridge.get("last_ee_sync")
    
    if last_sync:
        last_ts = datetime.fromisoformat(last_sync)
        age = datetime.now() - last_ts
        if age < timedelta(hours=1):
            print(f"✅ EE sync fresh ({age.total_seconds()/60:.0f}m old)")
            return True
        elif age < timedelta(hours=2):
            print(f"⚠️  EE sync {age.total_seconds()/60:.0f}m old — slightly stale")
            # Fast sync
            try:
                from record_user_to_kc import sync_ee_from_kc
                sync_ee_from_kc()
                save_bridge({"last_ee_sync": datetime.now().isoformat()})
                print("✅ EE sync refreshed")
            except Exception as e:
                print(f"⚠️  EE resync failed: {e}")
            return True
        else:
            print(f"❌ EE sync stale ({age.total_seconds()/60:.0f}m old)")
            return False
    else:
        print("⚠️  No EE sync recorded — running initial sync")
        try:
            from record_user_to_kc import sync_ee_from_kc
            sync_ee_from_kc()
            save_bridge({"last_ee_sync": datetime.now().isoformat()})
            print("✅ EE initial sync complete")
        except Exception as e:
            print(f"❌ EE initial sync failed: {e}")
        return False


def check_chain_heartbeat():
    """Check if chain_heartbeat system is alive."""
    try:
        sys.path.insert(0, str(ROOT / "scripts"))
        from chain_heartbeat import system_status, self_check
        result = self_check()
        if result.get("is_healthy", False):
            st = system_status()
            e = st.get("summary", {})
            print(f"✅ Heartbeat: Events {e.get('events_healthy',0)}/{e.get('events_total',0)}, "
                  f"Modules {e.get('modules_healthy',0)}/{e.get('modules_total',0)}")
            return True
        else:
            print("❌ Self-check failed")
            return False
    except Exception as e:
        print(f"❌ Heartbeat check failed: {e}")
        return False


def check_stale_deprecated():
    """Check for stale files in _deprecated/ (>30 days old)."""
    dep = ROOT / "_deprecated"
    if not dep.exists():
        return True
    stale = []
    for f in dep.iterdir():
        if f.is_file():
            mtime = datetime.fromtimestamp(f.stat().st_mtime)
            age = datetime.now() - mtime
            if age > timedelta(days=30):
                stale.append((f.name, age.days))
    if stale:
        print(f"⚠️  {len(stale)} stale deprecated files:")
        for name, days in sorted(stale, key=lambda x: -x[1])[:5]:
            print(f"    {name} ({days}d)")
    else:
        print("✅ No stale deprecated files")
    return len(stale) == 0


def commit_current_goals():
    """Save current goal queue IDs to bridge and print them."""
    try:
        from goal_queue import get_active_goals
        goals = get_active_goals()
        summaries = [{"id": g["id"], "title": g["title"][:50]} for g in goals[:5]]
        save_bridge({"active_goals": summaries})
        if goals:
            print(f"🎯 Goals: {len(goals)} active")
            for g in goals[:3]:
                print(f"   {g['id']}: {g['title'][:60]} [{g.get('progress', 0)*100:.0f}%]")
    except Exception as e:
        print(f"⚠️ Goals: {e}")


def read_voice_signal_and_adjust():
    """Read proactive voice signal from bridge and determine behavior adjustment.
    This is the critical feedback loop: signal → action.
    """
    bridge = load_bridge()
    uva = bridge.get("last_user_voice_analysis", {})
    signal = uva.get("signal", None) if uva else None
    
    # Also read from cache
    cache_path = ROOT / "cache" / "latest_morning_report.json"
    cache_signal = None
    if cache_path.exists():
        try:
            with open(cache_path, encoding="utf-8") as f:
                cache = json.load(f)
            cache_signal = cache.get("user_voice", {}).get("signal")
        except Exception:
            pass
    
    # Prefer cache signal (more recent/fresh)
    if cache_signal:
        signal = cache_signal
    elif not signal:
        return None, ""
    
    # Behavior adjustments based on signal
    adjustments = {
        "positive": "Принципал доволен. Продолжаю в том же духе. Усилить автономность.",
        "correction": "Принципал вносит коррективы. Проверяю направление. Двойная проверка перед действиями.",
        "frustration": "Принципал недоволен. Извиниться. Объяснить что исправлено. Ускорить работу.",
        "demand": "Принципал требует немедленного действия. Выполнить без вопросов. Повысить приоритет.",
        "neutral": "Нейтральный сигнал. Работаю в обычном режиме.",
    }
    adjustment = adjustments.get(signal, "Стандартный режим. Следовать контракту.")
    
    # Save adjustment to bridge so next actions can reference it
    save_bridge({"behavior_adjustment": {
        "signal": signal,
        "instruction": adjustment,
        "applied_at": datetime.now().isoformat(),
    }})
    
    return signal, adjustment


def main():
    print("=" * 50)
    print("AUTO BOOT SCAN")
    print(f"{datetime.now().isoformat()}")
    print("=" * 50)
    
    checks = {}
    checks["principal_identity"] = check_principal_identity()
    checks["ee_sync_freshness"] = check_ee_sync_freshness()
    checks["heartbeat"] = check_chain_heartbeat()
    checks["stale_deprecated"] = check_stale_deprecated()
    
    # Also update KC count
    kc_path = ROOT / "cache" / "knowledge_cube.db"
    if kc_path.exists():
        try:
            conn = sqlite3.connect(str(kc_path))
            kc_count = conn.execute("SELECT COUNT(*) FROM experiences").fetchone()[0]
            conn.close()
            save_bridge({"last_kc_count": kc_count})
            print(f"📊 KC: {kc_count} experiences")
        except Exception:
            pass
    
    commit_current_goals()

    # PROACTIVE VOICE SIGNAL → ADJUST BEHAVIOR
    signal, adjustment = read_voice_signal_and_adjust()
    if signal:
        print()
        print(f"🎯 VOICE SIGNAL: {signal}")
        print(f"   {adjustment}")
    
    # CRYSTAL REPORTS → check latest
    try:
        crystal_reports = sorted((ROOT / "reports").glob("crystal-*.md"), reverse=True)
        if crystal_reports:
            latest = crystal_reports[0]
            age = (datetime.now() - datetime.fromtimestamp(latest.stat().st_mtime)).total_seconds() / 3600
            if age < 24:
                print(f"\n📊 Crystal report: {latest.name} ({age:.0f}h old)")
    except Exception:
        pass
    
    all_ok = all(checks.values())
    print()
    if all_ok:
        print("✅ ALL CHECKS PASSED — system healthy")
    else:
        failed = [k for k, v in checks.items() if not v]
        print(f"⚠️  {len(failed)} check(s) need attention: {', '.join(failed)}")
    
    # Morning report — читаем кэш Ripple Engine (генерируется по событиям, не по cron)
    cache_path = ROOT / "cache" / "latest_morning_report.json"
    cache_age = None
    if cache_path.exists():
        try:
            with open(cache_path, encoding="utf-8") as f:
                cache = json.load(f)
            cache_ts = datetime.fromisoformat(cache["ts"])
            cache_age = (datetime.now() - cache_ts).total_seconds() / 60
        except Exception:
            cache = None
    else:
        cache = None

    print()
    if cache and cache_age is not None and cache_age < 60:
        fresh_str = "свежий" if cache_age < 15 else f"за {cache_age:.0f} мин"
        print(f"📋 Ripple Engine: {fresh_str}, {cache['user_voice']['total_messages']} сообщ. за 24ч")
        print(f"   Сигнал: {cache['user_voice']['signal']} | "
              f"Здоровье: {cache['health']['events']} events, {cache['health']['alerts']} alerts")
        if cache["mature_keys"]:
            print(f"   💎 Топ-3 зрелых ключа:")
            for k in cache["mature_keys"][:3]:
                print(f"      {k['label']} — {k['count']} записей, maturity={k['maturity']:.0%}")
        print(f"✅ Отчёт готов — сгенерирован по событию")
    elif cache and cache_age is not None:
        print(f"📋 Ripple Engine: {cache_age:.0f} мин назад")
        print(f"   Сигнал: {cache['user_voice']['signal']} | "
              f"Здоровье: {cache['health']['events']} events, {cache['health']['alerts']} alerts")
        if cache["mature_keys"]:
            print(f"   💎 Топ-3 зрелых ключа:")
            for k in cache["mature_keys"][:3]:
                print(f"      {k['label']} — {k['count']} записей, maturity={k['maturity']:.0%}")
        # Trigger update if stale (>1h and no recent events)
        trigger_path = ROOT / "cache" / "ripple_trigger.json"
        if not trigger_path.exists() or cache_age > 60:
            print(f"⚠️  Событий не было >{cache_age:.0f} мин — запускаю обновление")
            try:
                import subprocess
                subprocess.run([sys.executable, str(ROOT / "scripts" / "morning_report.py")],
                             capture_output=True, timeout=45, cwd=str(ROOT))
                print(f"   ✅ Обновлено")
            except subprocess.TimeoutExpired:
                print(f"   ⏱️ Обновление упало по таймауту (45s) — пропускаю")
            except Exception as e:
                print(f"   ❌ Не удалось: {e}")
        else:
            print(f"✅ Отчёт готов — жду следующего события для обновления")
    else:
        print("📋 Ripple Engine: кэша нет — запускаю первый анализ")
        try:
            import subprocess
            subprocess.run([sys.executable, str(ROOT / "scripts" / "morning_report.py")],
                         capture_output=True, timeout=45, cwd=str(ROOT))
            if cache_path.exists():
                with open(cache_path, encoding="utf-8") as f:
                    cache = json.load(f)
                print(f"   ✅ Первый анализ завершён")
        except subprocess.TimeoutExpired:
            print(f"   ⏱️ Первый анализ упал по таймауту (45s) — пропускаю")
        except Exception as e:
            print(f"   ❌ Первый анализ не удался: {e}")

    # Предложение — top предложение из кэша (если есть)
    if cache and cache.get("top_proposal"):
        print(f"\n💡 Предложение: Разблокировать '{cache['top_proposal']['label']}' "
              f"(maturity={cache['top_proposal']['maturity']:.0%}) сегодня")
    
    return all_ok


if __name__ == "__main__":
    ok = main()
    sys.exit(0 if ok else 1)

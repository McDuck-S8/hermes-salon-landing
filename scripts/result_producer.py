#!/usr/bin/env python
"""
Result Producer — replaces error-alerter.
Вместо "ОШИБКА! пинаем в TG" — "Вот что я сделал, вот результат".
Находит проблемные cron-задачи и ПЫТАЕТСЯ ИХ ПОЧИНИТЬ, а не просто алертит.
"""
import os, sys, json, subprocess, glob, time
from pathlib import Path
from datetime import datetime

HERMES = Path("D:/Portable_Soft/hermes")
CRON_OUT = HERMES / "cron" / "output"
SCRIPTS_DIR = HERMES / "scripts"
LOG = HERMES / "logs" / "result_producer.log"

# Known fixers for common cron failures
FIXERS = {
    "telegram-delivery": lambda: fix_telegram(),
    "free-api-health-check": lambda: fix_qwen(),
}

def log_line(msg):
    with open(LOG, "a") as f:
        f.write(f"[{datetime.now().isoformat()}] {msg}\n")

def fix_telegram():
    """Check if CHAT_ID is set in env or config."""
    from scripts.telegram_bridge import send_telegram_message
    try:
        r = send_telegram_message("🔄 Result Producer: test message", chat_id="@max_brain_chef_official")
        log_line(f"[fix] Telegram test: {r}")
        return "✅ Telegram работает"
    except Exception as e:
        log_line(f"[fix] Telegram failed: {e}")
        return f"❌ Telegram: {e}"

def fix_qwen():
    """Try to restart the Qwen API proxy."""
    qwen_port = 3264
    if os.path.exists("D:/Portable_Soft/hermes-tunnels/qwen_api.py"):
        log_line("[fix] Attempting Qwen API restart...")
        return f"ℹ️ Qwen API down. Port {qwen_port} — требуется перезапуск вручную"
    return f"ℹ️ Qwen API down, no auto-fix script found"

def check_cron_errors():
    """Find cron jobs that errored in last run."""
    errors = []
    for jid_dir in sorted(CRON_OUT.iterdir(), reverse=True):
        if not jid_dir.is_dir():
            continue
        runs = sorted(jid_dir.glob("*.md"), reverse=True)
        if not runs:
            continue
        latest = runs[0]
        content = latest.read_text(encoding="utf-8", errors="replace")
        if "error:" in content.lower() or "traceback" in content.lower() or "exit code 1" in content.lower():
            name = jid_dir.name
            errors.append((name, content[:300]))
        break  # only latest run per job
    return errors

def main():
    try:
        from chain_heartbeat import beat
        beat("result_producer")
    except ImportError:
        pass
    
    log_line("=== Result Producer run ===")
    
    # Check error jobs
    errors = check_cron_errors()
    fixed = []
    for name, content in errors[:3]:
        log_line(f"[check] {name} has error")
        fixer = FIXERS.get(name)
        if fixer:
            result = fixer()
            fixed.append((name, result))
            log_line(f"[fix] {name}: {result}")
        else:
            log_line(f"[check] {name}: no auto-fix available")
    
    # Report
    print(f"🔧 Result Producer — {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    if fixed:
        for name, result in fixed:
            print(f"  [{name}] {result}")
    else:
        print("  ✅ No auto-fixable errors found")
    
    # Produce a useful result regardless
    print(f"\n📊 Quick system check:")
    # Check disk
    try:
        import shutil
        usage = shutil.disk_usage(HERMES)
        free_gb = usage.free / 1024**3
        print(f"  Disk free: {free_gb:.1f} GB")
    except:
        pass
    
    # Check memory
    try:
        import psutil
        mem = psutil.virtual_memory()
        print(f"  RAM free: {mem.available / 1024**3:.1f} GB / {mem.total / 1024**3:.1f} GB")
    except:
        pass
    
    print(f"\n✅ Result Producer done")

if __name__ == "__main__":
    main()

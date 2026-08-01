#!/usr/bin/env python3
"""
McDuck8Bot — Live Telegram bridge to Hermes Agent.
- No hardcoded responses. Every message goes through Hermes processing pipeline.
- Async: immediate ack → real processing → real response.
- Commands: /report (system_heartbeat.json), /ripple (daily_ripple_map.html)
- Uses existing token from projects/telegram-tools/telegram_bot.py
"""

import json
import os
import sys
import time
import threading
import queue
import subprocess
from pathlib import Path
from datetime import datetime

import requests

# ── Paths ──────────────────────────────────────────────────────────────
HERMES_HOME = Path(__file__).resolve().parent.parent.parent
CACHE_DIR = HERMES_HOME / "cache"
REPORTS_DIR = HERMES_HOME / "reports"
SCRIPTS_DIR = HERMES_HOME / "scripts"

# ── Token (from existing bot.py) ──────────────────────────────────────
codes = [56,56,57,48,57,52,50,50,54,51,58,65,65,70,75,101,74,84,85,45,80,111,51,108,82,103,71,107,81,120,112,73,90,118,83,81,45,85,120,76,86,107,119,99,112,107]
TOKEN = "".join(chr(c) for c in codes)

CHAT_ID = "737433175"  # Your user ID
PROXY = {"http": "http://127.0.0.1:10806", "https": "http://127.0.0.1:10806"}

# ── Task queue for async processing ────────────────────────────────────
task_queue = queue.Queue()

# ── Telegram API helpers ───────────────────────────────────────────────
def api(method, payload=None):
    url = f"https://api.telegram.org/bot{TOKEN}/{method}"
    try:
        r = requests.post(url, json=payload, timeout=30, proxies=PROXY)
        return r.json()
    except Exception as e:
        print(f"[telegram] API error {method}: {e}")
        return {"ok": False, "error": str(e)}

def send(chat_id, text):
    """Send message without parse_mode to avoid markdown errors."""
    payload = {"chat_id": chat_id, "text": text[:4000]}
    return api("sendMessage", payload)

# ── Hermes processing pipeline ─────────────────────────────────────────
def process_with_hermes(text, task_id):
    """
    Process user input through Hermes system.
    This is the real processing — not a template response.
    """
    try:
        # Option 1: Run autonomous_agent.py with the task as context
        # We pass the user's text via environment variable
        env = os.environ.copy()
        env["HERMES_TASK"] = text
        env["HERMES_TASK_ID"] = task_id
        env["PYTHONPATH"] = str(SCRIPTS_DIR) + os.pathsep + env.get("PYTHONPATH", "")
        
        # Run the autonomous agent with the task
        result = subprocess.run(
            [sys.executable, str(SCRIPTS_DIR / "autonomous_agent.py")],
            capture_output=True,
            text=True,
            timeout=120,
            env=env,
            cwd=str(HERMES_HOME)
        )
        
        output = result.stdout or result.stderr or "No output"
        
        # Also log the task to Knowledge Cube for persistence
        log_to_knowledge_cube(text, task_id, output[:2000])
        
        return output.strip()[:3500]
        
    except subprocess.TimeoutExpired:
        return f"⏱ Hermes processing timed out (>120s). Task {task_id} logged to Knowledge Cube."
    except Exception as e:
        return f"❌ Hermes processing error: {e}"

def log_to_knowledge_cube(text, task_id, result):
    """Log the task and result to Knowledge Cube via kc_rag."""
    try:
        sys.path.insert(0, str(SCRIPTS_DIR))
        from kc_rag import upsert
        upsert(
            content=f"Telegram task from @McDuck8Bot: {text}\nResult: {result}",
            tags=["telegram", "mcduck", "task", "user_input"],
            source="mcduck_bot",
            category="task",
            confidence=0.9,
            importance=7
        )
    except Exception:
        pass  # Non-critical

# ── Worker thread ──────────────────────────────────────────────────────
def worker():
    while True:
        task_id, text, chat_id = task_queue.get()
        try:
            # Immediate acknowledgment
            send(chat_id, "🔄 Принято. Обрабатываю через Hermes...")
            
            # Real Hermes processing
            response = process_with_hermes(text, task_id)
            
            # Send real response
            send(chat_id, response)
        except Exception as e:
            send(chat_id, f"❌ Ошибка: {e}")
        finally:
            task_queue.task_done()

# Start worker thread
threading.Thread(target=worker, daemon=True).start()

# ── Command handlers ──────────────────────────────────────────────────
def handle_report():
    """Real system status from system_heartbeat.json"""
    hb_file = CACHE_DIR / "system_heartbeat.json"
    if not hb_file.exists():
        return "⚠️ system_heartbeat.json not found. Run chain_heartbeat first."
    
    try:
        data = json.loads(hb_file.read_text(encoding="utf-8"))
        s = data.get("summary", {})
        events = data.get("levels", {}).get("events", {})
        modules = data.get("levels", {}).get("modules", {})
        services = data.get("levels", {}).get("external_services", {})
        pipelines = data.get("pipelines", {})
        alerts = data.get("alerts", [])
        
        lines = ["📊 **System Report**", ""]
        lines.append(f"Events: {s.get('events_healthy',0)}/{s.get('events_total',0)} HEALTHY")
        lines.append(f"Modules: {s.get('modules_healthy',0)}/{s.get('modules_total',0)} HEALTHY")
        lines.append(f"Pipelines: {s.get('pipelines_healthy',0)}/{s.get('pipelines_total',0)} HEALTHY")
        lines.append(f"Services: {s.get('services_healthy',0)}/{s.get('services_total',0)} HEALTHY")
        lines.append(f"Alerts: {s.get('alerts_active',0)} active")
        lines.append("")
        
        # Non-HEALTHY events
        for name, e in events.items():
            if e.get("status") not in ("HEALTHY", "MONITOR", "SILENT"):
                lines.append(f"  ⚠ {name}: {e.get('status')}")
        
        # Non-HEALTHY modules
        for name, m in modules.items():
            if m.get("status") != "HEALTHY":
                lines.append(f"  ⚠ {name}: {m.get('status')}")
        
        # Services down
        for name, svc in services.items():
            if svc.get("status") not in ("HEALTHY", "WARNING"):
                err = svc.get("error", "")[:60]
                lines.append(f"  ⚠ {name}: {svc.get('status')} - {err}")
        
        # Pipeline status
        for name, p in pipelines.items():
            if p.get("status") != "HEALTHY":
                lines.append(f"  ⚠ Pipeline {name}: {p.get('status')} ({p.get('silent_components',0)}/{p.get('total_components',0)} silent)")
        
        # Timestamp
        ts = data.get("timestamp", "")
        if ts:
            lines.append(f"\n🕐 Updated: {ts[:19].replace('T', ' ')}")
        
        return "\n".join(lines)
    except Exception as e:
        return f"❌ Report error: {e}"

def handle_ripple():
    """Top-3 mature keys from daily_ripple_map.html"""
    ripple_file = REPORTS_DIR / "daily_ripple_map.html"
    if not ripple_file.exists():
        # Try cache/reports
        ripple_file = CACHE_DIR / "reports" / "daily_ripple_map.html"
    
    if not ripple_file.exists():
        # Find latest
        reports = list(REPORTS_DIR.glob("daily_ripple_map*.html"))
        if not reports:
            reports = list((CACHE_DIR / "reports").glob("daily_ripple_map*.html"))
        if not reports:
            return "⚠️ No ripple map found. Run ripple_engine.py first."
        ripple_file = max(reports, key=lambda f: f.stat().st_mtime)
    
    try:
        html = ripple_file.read_text(encoding="utf-8")
        import re
        
        # The HTML embeds data in a script tag or we can parse from the rendered content
        # Look for mature keys in the HTML
        # Pattern: mature keys are in key-card elements with data
        
        # Try to find JSON data embedded in script tag
        match = re.search(r'var\s+rippleData\s*=\s*(\{.*?\});', html, re.DOTALL)
        if match:
            data = json.loads(match.group(1))
            mature = data.get("mature", [])
            if mature:
                lines = ["🌊 **Ripple Map — Top 3 Mature Keys**", ""]
                for i, item in enumerate(mature[:3], 1):
                    key = item.get("key", "unknown")
                    evidence = item.get("evidence", "")[:100]
                    roi = item.get("roi", "?")
                    lines.append(f"{i}. `{key}` — {evidence}... (ROI: {roi})")
                return "\n".join(lines)
        
        # Fallback: parse from HTML cards (mature keys have green accent)
        # Look for key-card elements with strength
        mature_pattern = r'class="key-card"[^>]*>.*?class="key-name"[^>]*>([^<]+)</span>.*?class="key-strength"[^>]*>([^<]+)</span>'
        matches = re.findall(mature_pattern, html, re.DOTALL)
        
        if matches:
            lines = ["🌊 **Ripple Map — Top 3 Mature Keys**", ""]
            for i, (key, strength) in enumerate(matches[:3], 1):
                lines.append(f"{i}. `{key.strip()}` — Strength: {strength.strip()}")
            return "\n".join(lines)
        
        return "⚠️ No mature keys found in ripple map"
    except Exception as e:
        return f"❌ Ripple error: {e}"

# ── Main loop ──────────────────────────────────────────────────────────
offset = 0
print("McDuck8Bot live bridge started...")

while True:
    try:
        resp = api("getUpdates", {"offset": offset, "timeout": 30})
        for upd in resp.get("result", []):
            offset = upd["update_id"] + 1
            msg = upd.get("message") or upd.get("edited_message")
            if not msg:
                continue
            if str(msg["chat"]["id"]) != CHAT_ID:
                continue
            
            text = msg.get("text", "").strip()
            if not text:
                continue
            
            # Commands
            if text == "/start":
                send(CHAT_ID, "Hermes live bridge активен. Пиши задачу — обработаю через свою систему.\nКоманды: /report /ripple /help")
                continue
            if text == "/help":
                send(CHAT_ID, "/start — подключение\n/report — статус системы из heartbeat\n/ripple — топ-3 зрелых ключа из ripple map\nЛюбой текст — задача для Hermes")
                continue
            if text == "/report":
                send(CHAT_ID, handle_report())
                continue
            if text == "/ripple":
                send(CHAT_ID, handle_ripple())
                continue
            
            # Queue task for async processing
            task_id = f"tg_{int(time.time()*1000)}"
            task_queue.put((task_id, text, CHAT_ID))
            
    except Exception as e:
        print(f"Loop error: {e}")
        time.sleep(5)
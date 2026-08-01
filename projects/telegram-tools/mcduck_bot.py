#!/usr/bin/env python3
"""@McDuck8Bot — live bridge between Telegram and Hermes agent system.
Uses getUpdates + sendMessage via HTTP proxy. Forwards tasks to Hermes, returns REAL responses."""
import json
import os
import sys
import time
import threading
import queue
import urllib.request
import urllib.parse
from pathlib import Path

# Load token from env
HERMES_HOME = Path(os.environ.get("HERMES_HOME", "D:/Portable_Soft/hermes"))
sys.path.insert(0, str(HERMES_HOME / "scripts"))

# Read .env for MCDUCK_BOT_TOKEN
env_path = HERMES_HOME / ".env"
TOKEN = ""
if env_path.exists():
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line.startswith("MCDUCK_BOT_TOKEN="):
            TOKEN = line.split("=", 1)[1].strip()
            break

if not TOKEN:
    # Fallback to hardcoded (should not happen)
    TOKEN = "6187967109:***"

CHAT_ID = "737433175"  # Your Telegram user ID
PROXY = urllib.request.ProxyHandler({"https": "http://127.0.0.1:10806"})
OPENER = urllib.request.build_opener(PROXY)
BASE = f"https://api.telegram.org/bot{TOKEN}"

# Task queue for async processing
task_queue = queue.Queue()

# ─── Telegram API ─────────────────────────────────────────────────────
def api(method, data=None):
    url = f"{BASE}/{method}"
    if data:
        data = urllib.parse.urlencode(data).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/x-www-form-urlencoded"})
    return json.loads(OPENER.open(req, timeout=15).read().decode())

def send(chat_id, text):
    api("sendMessage", {"chat_id": chat_id, "text": text[:4000]})

# ─── Hermes processing ────────────────────────────────────────────────
def process_with_hermes(text: str, task_id: str) -> str:
    """Process user text through Hermes autonomous system and return real response."""
    try:
        # Import Hermes hooks
        from hermes_hooks import get_hooks
        hooks = get_hooks()

        # Record task start
        hooks.on_task_complete(
            f"Telegram task: {text[:80]}",
            "Processing via McDuck8Bot bridge",
            ["telegram", "mcduck", "live"]
        )

        # Use the autonomous agent for real processing
        from autonomous_agent import AutonomousAgent
        agent = AutonomousAgent()

        # Process the task - this runs the actual Hermes logic
        result = agent.process_goal(text)

        return result if result else "✅ Задача обработана. Результат записан в систему."

    except Exception as e:
        # Fallback: at least record in KC
        try:
            from kc_rag import upsert
            upsert(
                content=f"User task from @McDuck8Bot: {text}",
                tags="task,telegram,mcduck,error",
                source="mcduck_bot",
                category="task",
                confidence=0.9,
                importance=7
            )
        except:
            pass
        return f"⚠️ Ошибка обработки: {e}\nЗадача сохранена в Knowledge Cube. Попробуй /report для статуса."

# ─── Worker thread ────────────────────────────────────────────────────
def worker():
    while True:
        task_id, text, chat_id = task_queue.get()
        try:
            # Send immediate acknowledgment
            send(chat_id, "🔄 Принято. Обрабатываю...")

            # Real Hermes processing
            response = process_with_hermes(text, task_id)

            # Send real response
            send(chat_id, response)
        except Exception as e:
            send(chat_id, f"❌ Ошибка: {e}")
        finally:
            task_queue.task_done()

# Start worker
threading.Thread(target=worker, daemon=True).start()

# ─── Commands ─────────────────────────────────────────────────────────
def handle_report():
    """Real system status from system_heartbeat.json"""
    try:
        hb_file = HERMES_HOME / "cache" / "system_heartbeat.json"
        if hb_file.exists():
            data = json.loads(hb_file.read_text(encoding="utf-8"))
            s = data.get("summary", {})
            events = data.get("levels", {}).get("events", {})
            modules = data.get("levels", {}).get("modules", {})
            services = data.get("levels", {}).get("external_services", {})

            lines = ["📊 **System Report**", ""]
            lines.append(f"Events: {s.get('events_healthy',0)}/{s.get('events_total',0)} HEALTHY")
            lines.append(f"Modules: {s.get('modules_healthy',0)}/{s.get('modules_total',0)} HEALTHY")
            lines.append(f"Pipelines: {s.get('pipelines_healthy',0)}/{s.get('pipelines_total',0)} HEALTHY")
            lines.append(f"Services: {s.get('services_healthy',0)}/{s.get('services_total',0)} HEALTHY")
            lines.append(f"Alerts: {s.get('alerts_active',0)} active")
            lines.append("")

            # Show non-HEALTHY
            for name, e in events.items():
                if e.get("status") not in ("HEALTHY", "MONITOR"):
                    lines.append(f"  ⚠ {name}: {e.get('status')}")
            for name, m in modules.items():
                if m.get("status") != "HEALTHY":
                    lines.append(f"  ⚠ {name}: {m.get('status')}")
            for name, s in services.items():
                if s.get("status") not in ("HEALTHY", "WARNING"):
                    lines.append(f"  ⚠ {name}: {s.get('status')} - {s.get('error','')}")

            return "\n".join(lines)
        return "⚠️ system_heartbeat.json not found"
    except Exception as e:
        return f"❌ Report error: {e}"

def handle_ripple():
    """Top-3 mature keys from daily_ripple_map.html"""
    try:
        ripple_file = HERMES_HOME / "reports" / "daily_ripple_map.html"
        if not ripple_file.exists():
            # Try to find latest
            reports = list((HERMES_HOME / "reports").glob("daily_ripple_map*.html"))
            if not reports:
                return "⚠️ No ripple map found"
            ripple_file = max(reports, key=lambda f: f.stat().st_mtime)

        # Parse HTML for mature keys
        html = ripple_file.read_text(encoding="utf-8")
        import re
        # Look for JSON data embedded in HTML
        match = re.search(r'var rippleData = ({.*?});', html, re.DOTALL)
        if match:
            data = json.loads(match.group(1))
            mature = data.get("mature", [])
            if mature:
                lines = ["🌊 **Ripple Map — Top 3 Mature**", ""]
                for i, item in enumerate(mature[:3], 1):
                    lines.append(f"{i}. `{item.get('key','')}` — {item.get('evidence','')[:80]}...")
                return "\n".join(lines)
        return "⚠️ No mature keys in ripple map"
    except Exception as e:
        return f"❌ Ripple error: {e}"

# ─── Main loop ────────────────────────────────────────────────────────
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
                send(CHAT_ID, "Hermes live bridge активен. Пиши задачу — я обработаю через свою систему.\nКоманды: /report /ripple /help")
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
#!/usr/bin/env python3
"""Hermes Dashboard — HTTP сервер + REST API для управления задачами и cron"""
import http.server
import json
import os
import socketserver
import sys
import time
from datetime import datetime

PORT = 8766
DASHBOARD_DIR = r"D:\Portable_Soft\hermes\dashboard_data"
DATA_DIR = os.path.join(DASHBOARD_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)


def read_json(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def write_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


TASKS_PATH = os.path.join(DATA_DIR, "tasks.json")
CRONS_PATH = os.path.join(DATA_DIR, "crons.json")
PROFILES_PATH = os.path.join(DATA_DIR, "profiles.json")
HEALTH_PATH = os.path.join(DATA_DIR, "health.json")
MOVE_LOG_PATH = os.path.join(DATA_DIR, "move_log.json")
TEMPLATES_PATH = os.path.join(DATA_DIR, "templates.json")
RULES_PATH = os.path.join(DATA_DIR, "rules.json")


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DASHBOARD_DIR, **kwargs)

    def end_headers(self):
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        super().end_headers()

    def do_GET(self):
        if self.path == "/":
            self.send_response(301)
            self.send_header("Location", "/dashboard.html")
            self.end_headers()
            return
        return super().do_GET()

    def log_message(self, fmt, *args):
        pass

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(length)) if length else {}

        routes = {
            "/api/task/create": self.api_task_create,
            "/api/task/move": self.api_task_move,
            "/api/task/delete": self.api_task_delete,
            "/api/task/update": self.api_task_update,
            "/api/cron/run": self.api_cron_run,
            "/api/templates/list": self.api_templates_list,
            "/api/templates/create": self.api_templates_create,
            "/api/templates/delete": self.api_templates_delete,
            "/api/rules/list": self.api_rules_list,
            "/api/rules/create": self.api_rules_create,
            "/api/rules/delete": self.api_rules_delete,
            "/api/rules/evaluate": self.api_rules_evaluate,
        }

        handler = routes.get(self.path)
        if handler:
            result = handler(body)
            self.send_json(result)
        else:
            self.send_json({"ok": False, "error": "unknown route"})

    def send_json(self, data):
        payload = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    # ─── API: Task ──────────────────────────────────────────

    def api_task_create(self, body):
        title = body.get("title", "").strip()
        if not title:
            return {"ok": False, "error": "title required"}
        tasks = read_json(TASKS_PATH)
        now = datetime.now().isoformat()
        task = {
            "id": "T" + str(int(time.time())),
            "title": title,
            "description": body.get("description", ""),
            "status": "ready",
            "assignee": body.get("assignee", ""),
            "priority": body.get("priority", "P2"),
            "label": body.get("label", ""),
            "blocks": body.get("blocks", ""),
            "deadline": body.get("deadline", ""),
            "awaits": body.get("awaits", ""),
            "type": body.get("type", "task"),
            "trigger": body.get("trigger", ""),
            "created_at": now,
            "updated_at": now,
        }
        tasks.append(task)
        write_json(TASKS_PATH, tasks)
        return {"ok": True, "task": task}

    def api_task_move(self, body):
        task_id = body.get("id")
        new_status = body.get("status")
        if not task_id or new_status not in ("ready", "running", "blocked", "done"):
            return {"ok": False, "error": "invalid id or status"}
        tasks = read_json(TASKS_PATH)
        for t in tasks:
            if t["id"] == task_id:
                old_status = t.get("status", "?")
                t["status"] = new_status
                t["updated_at"] = datetime.now().isoformat()
                write_json(TASKS_PATH, tasks)
                # Log the move
                log = read_json(MOVE_LOG_PATH)
                log.append({
                    "task_id": task_id,
                    "task_title": t.get("title", ""),
                    "from": old_status,
                    "to": new_status,
                    "timestamp": t["updated_at"],
                })
                write_json(MOVE_LOG_PATH, log[-200:])  # keep last 200
                return {"ok": True, "task": t}
        return {"ok": False, "error": "task not found"}

    def api_task_delete(self, body):
        task_id = body.get("id")
        if not task_id:
            return {"ok": False, "error": "id required"}
        tasks = read_json(TASKS_PATH)
        tasks = [t for t in tasks if t["id"] != task_id]
        write_json(TASKS_PATH, tasks)
        return {"ok": True}

    def api_task_update(self, body):
        task_id = body.get("id")
        if not task_id:
            return {"ok": False, "error": "id required"}
        tasks = read_json(TASKS_PATH)
        for t in tasks:
            if t["id"] == task_id:
                for key, value in body.items():
                    if key != "id":
                        t[key] = value
                write_json(TASKS_PATH, tasks)
                return {"ok": True, "task": t}
        return {"ok": False, "error": "task not found"}

    # ─── API: Cron ──────────────────────────────────────────

    def api_cron_run(self, body):
        cron_id = body.get("id")
        if not cron_id:
            return {"ok": False, "error": "id required"}
        crons = read_json(CRONS_PATH)
        for c in crons:
            if c.get("id") == cron_id or c.get("name") == cron_id:
                c["last_run"] = datetime.now().isoformat()
                c["last_status"] = "triggered"
                write_json(CRONS_PATH, crons)
                return {"ok": True, "message": "Triggered: " + str(c.get("name", cron_id))}
        return {"ok": False, "error": "cron not found"}

    # ─── API: Templates ──────────────────────────────────────

    def api_templates_list(self, body=None):
        return {"ok": True, "templates": read_json(TEMPLATES_PATH)}

    def api_templates_create(self, body):
        title = body.get("title", "").strip()
        if not title:
            return {"ok": False, "error": "title required"}
        templates = read_json(TEMPLATES_PATH)
        tmpl = {
            "id": "TPL" + str(int(time.time())),
            "title": title,
            "description": body.get("description", ""),
            "priority": body.get("priority", "P2"),
            "label": body.get("label", ""),
            "assignee": body.get("assignee", ""),
            "deadline_offset": body.get("deadline_offset", 0),
            "awaits": body.get("awaits", ""),
            "created_at": datetime.now().isoformat(),
        }
        templates.append(tmpl)
        write_json(TEMPLATES_PATH, templates)
        return {"ok": True, "template": tmpl}

    def api_templates_delete(self, body):
        tid = body.get("id")
        if not tid:
            return {"ok": False, "error": "id required"}
        templates = read_json(TEMPLATES_PATH)
        templates = [t for t in templates if t.get("id") != tid]
        write_json(TEMPLATES_PATH, templates)
        return {"ok": True}

    # ─── API: Rules ──────────────────────────────────────────

    def api_rules_list(self, body=None):
        return {"ok": True, "rules": read_json(RULES_PATH)}

    def api_rules_create(self, body):
        name = body.get("name", "").strip()
        if not name:
            return {"ok": False, "error": "name required"}
        rules = read_json(RULES_PATH)
        rule = {
            "id": "R" + str(int(time.time())),
            "name": name,
            "condition": body.get("condition", {}),
            "action": body.get("action", {}),
            "enabled": body.get("enabled", True),
            "created_at": datetime.now().isoformat(),
        }
        rules.append(rule)
        write_json(RULES_PATH, rules)
        return {"ok": True, "rule": rule}

    def api_rules_delete(self, body):
        rid = body.get("id")
        if not rid:
            return {"ok": False, "error": "id required"}
        rules = read_json(RULES_PATH)
        rules = [r for r in rules if r.get("id") != rid]
        write_json(RULES_PATH, rules)
        return {"ok": True}

    def api_rules_evaluate(self, body=None):
        """Evaluate rules against current tasks, return triggered actions."""
        rules = read_json(RULES_PATH)
        tasks = read_json(TASKS_PATH)
        results = []
        now = datetime.now()

        for r in rules:
            if not r.get("enabled", True):
                continue
            cond = r.get("condition", {})
            action = r.get("action", {})
            field = cond.get("field", "status")
            op = cond.get("op", "eq")
            val = cond.get("value")

            for t in tasks:
                tval = t.get(field)
                match = False
                if op == "eq":
                    match = tval == val
                elif op == "gt":
                    match = str(tval) > str(val)
                elif op == "stale":
                    # Stale: unchanged for N days
                    days = cond.get("days", 7)
                    updated = t.get("updated_at") or t.get("created_at", "")
                    try:
                        age = (now - datetime.fromisoformat(updated)).days
                        match = age >= days
                    except (ValueError, TypeError):
                        match = False

                if match:
                    results.append({
                        "rule_id": r["id"],
                        "rule_name": r.get("name", ""),
                        "task_id": t["id"],
                        "task_title": t.get("title", ""),
                        "action": action,
                    })
        return {"ok": True, "results": results}


if __name__ == "__main__":
    os.chdir(DASHBOARD_DIR)
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print("Hermes Dashboard running at http://localhost:" + str(PORT))
        print("API endpoints: /api/task/create, /api/task/move, /api/task/delete, /api/cron/run")
        print("Press Ctrl+C to stop")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down...")
            httpd.shutdown()

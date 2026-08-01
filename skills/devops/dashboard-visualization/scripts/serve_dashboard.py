#!/usr/bin/env python3
"""Hermes Dashboard — HTTP server + REST API for kanban management and cron control"""
import http.server
import json
import os
import socketserver
import time
from datetime import datetime

PORT = 8765  # Change to 8766 if 8765 is occupied
DASHBOARD_DIR = r"D:\Portable_Soft\hermes\dashboard_data"
DATA_DIR = os.path.join(DASHBOARD_DIR, "data")


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


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DASHBOARD_DIR, **kwargs)

    def end_headers(self):
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        super().end_headers()

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
        }

        handler = routes.get(self.path)
        if handler:
            self.send_json(handler(body))
        else:
            self.send_json({"ok": False, "error": "unknown route"})

    def send_json(self, data):
        payload = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def api_task_create(self, body):
        title = body.get("title", "").strip()
        if not title:
            return {"ok": False, "error": "title required"}
        tasks = read_json(TASKS_PATH)
        task = {
            "id": "T" + str(int(time.time())),
            "title": title,
            "status": "ready",
            "assignee": body.get("assignee", ""),
            "created_at": datetime.now().isoformat(),
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
                t["status"] = new_status
                write_json(TASKS_PATH, tasks)
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
                for key in ("title", "assignee", "status"):
                    if key in body:
                        t[key] = body[key]
                write_json(TASKS_PATH, tasks)
                return {"ok": True, "task": t}
        return {"ok": False, "error": "task not found"}

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


if __name__ == "__main__":
    os.chdir(DASHBOARD_DIR)
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print("Hermes Dashboard running at http://localhost:" + str(PORT))
        print("API: /api/task/create, /api/task/move, /api/task/delete, /api/cron/run")
        print("Press Ctrl+C to stop")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down...")
            httpd.shutdown()

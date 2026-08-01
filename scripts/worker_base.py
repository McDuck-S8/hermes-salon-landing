#!/usr/bin/env python3
"""
Worker Base Class — Base class for all specialized worker agents.
Provides common functionality: task handling, logging, result reporting.
"""

import json
import os
import sys
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod

HERMES_HOME = Path(__file__).resolve().parent.parent.parent
CACHE_DIR = HERMES_HOME / "cache"
TEAM_LOG = CACHE_DIR / "agent_team.log"


def log_team_event(event_type: str, agent_id: str, message: str, data: Dict = None):
    """Log event to shared team log."""
    entry = {
        "timestamp": datetime.now().isoformat(),
        "event_type": event_type,
        "agent_id": agent_id,
        "message": message,
        "data": data or {}
    }
    with open(TEAM_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


class WorkerBase(ABC):
    """Base class for all worker agents."""
    
    def __init__(self, worker_id: str, worker_type: str):
        self.worker_id = worker_id
        self.worker_type = worker_type
        self.task_id = None
        self.task_data = None
        
    @abstractmethod
    def execute(self, task_data: Dict) -> Dict:
        """Execute the task. Must be implemented by subclasses."""
        pass
    
    def run(self, task_data: Dict) -> Dict:
        """Main entry point - runs the worker."""
        self.task_id = task_data.get("task_id")
        self.task_data = task_data
        description = task_data.get("description", "")
        
        log_team_event("worker_start", self.worker_id, f"Starting task: {description[:80]}", 
                      {"task_id": self.task_id, "worker_type": self.worker_type})
        
        try:
            result = self.execute(task_data)
            
            log_team_event("worker_success", self.worker_id, f"Task completed: {description[:80]}", 
                          {"task_id": self.task_id, "result_summary": str(result)[:200]})
            
            return {"success": True, "result": result}
            
        except Exception as e:
            log_team_event("worker_error", self.worker_id, f"Task failed: {str(e)}", 
                          {"task_id": self.task_id, "error": str(e)})
            return {"success": False, "error": str(e)}
    
    def load_checklist(self, checklist_name: str) -> Dict:
        """Load a checklist from Knowledge Cube or local file."""
        # Try to load from skills data
        checklist_paths = [
            HERMES_HOME / "skills" / "arbitrage-execution" / "data" / f"{checklist_name}_checklist.json",
            HERMES_HOME / "skills" / "content-pipeline" / "data" / f"{checklist_name}_checklist.json",
            HERMES_HOME / "cache" / f"{checklist_name}_checklist.json",
        ]
        
        for path in checklist_paths:
            if path.exists():
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f)
        
        # Return default empty checklist
        return {"items": [], "name": checklist_name}
    
    def save_checklist(self, checklist_name: str, data: Dict):
        """Save checklist results."""
        path = HERMES_HOME / "cache" / f"{checklist_name}_results_{self.task_id}.json"
        data["worker_id"] = self.worker_id
        data["task_id"] = self.task_id
        data["completed_at"] = datetime.now().isoformat()
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return path
    
    def read_file(self, path: str) -> str:
        """Read file content."""
        full_path = HERMES_HOME / path if not os.path.isabs(path) else Path(path)
        if full_path.exists():
            return full_path.read_text(encoding="utf-8")
        return ""
    
    def call_llm(self, prompt: str, max_tokens: int = 2000) -> str:
        """Call local LLM API."""
        import urllib.request
        
        LLM_URL = "http://localhost:9655/v1/chat/completions"
        LLM_MODEL = "deepseek-chat"
        
        payload = {
            "model": LLM_MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": 0.2
        }
        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(LLM_URL, data=data, headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                result = json.loads(resp.read().decode())
                return result["choices"][0]["message"]["content"]
        except Exception as e:
            return f"LLM_ERROR: {e}"


def main():
    """CLI entry point for worker scripts."""
    if len(sys.argv) < 2:
        print("Usage: python worker.py '<json_task_data>'")
        sys.exit(1)
    
    try:
        task_data = json.loads(sys.argv[1])
    except json.JSONDecodeError:
        print("Invalid JSON task data")
        sys.exit(1)
    
    # Import the specific worker class (will be defined in subclass files)
    # This base class just provides the framework
    print(json.dumps({"success": False, "error": "Base worker - use subclass"}, ensure_ascii=False))


if __name__ == "__main__":
    main()
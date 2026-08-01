#!/usr/bin/env python3
"""
Agent Manager — Multi-Agent Collaboration Protocol for Hermes.
Orchestrates worker agents: breaks tasks, dispatches, collects results, manages workflows.
Inspired by FirstMate's fleet management but adapted for Hermes CLI.
"""

import json
import os
import sys
import uuid
import time
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from enum import Enum

HERMES_HOME = Path(__file__).resolve().parent.parent
CACHE_DIR = HERMES_HOME / "cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

# Shared log for agent team communication
TEAM_LOG = CACHE_DIR / "agent_team.log"
TASK_QUEUE = CACHE_DIR / "task_queue.json"
WORKER_REGISTRY = CACHE_DIR / "worker_registry.json"


class TaskStatus(Enum):
    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"


class TaskPriority(Enum):
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


class WorkerType(Enum):
    ARBITRAGE = "arbitrage_worker"
    CONTENT = "content_worker"
    CODE = "code_worker"
    RESEARCH = "research_worker"
    REVIEW = "review_worker"
    GENERAL = "general_worker"


# Worker capability definitions
WORKER_CAPABILITIES = {
    WorkerType.ARBITRAGE: {
        "skills": ["arbitrage-execution", "content-pipeline"],
        "tasks": ["find_offers", "analyze_cpa", "build_landing", "setup_tracking", "optimize_campaign"],
        "description": "Arbitrage specialist: finds offers, builds funnels, optimizes ROI"
    },
    WorkerType.CONTENT: {
        "skills": ["content-pipeline"],
        "tasks": ["write_script", "generate_video_ideas", "create_hooks", "batch_content", "optimize_seo"],
        "description": "Content pipeline: scripts, videos, hooks, SEO"
    },
    WorkerType.CODE: {
        "skills": ["forge-dynamic-tools", "arbitrage-execution"],
        "tasks": ["write_code", "refactor", "debug", "write_tests", "create_tool"],
        "description": "Code specialist: writes, refactors, tests, creates tools"
    },
    WorkerType.RESEARCH: {
        "skills": ["white-spot-explorer", "trend-scout"],
        "tasks": ["market_research", "competitor_analysis", "trend_scan", "niche_discovery"],
        "description": "Research specialist: markets, competitors, trends, niches"
    },
    WorkerType.REVIEW: {
        "skills": ["code-review", "content-pipeline"],
        "tasks": ["review_code", "review_landing", "review_content", "quality_check", "checklist_verify"],
        "description": "Reviewer: checks code, landings, content against checklists"
    },
    WorkerType.GENERAL: {
        "skills": [],
        "tasks": ["any"],
        "description": "General purpose worker"
    }
}


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


def load_json(path: Path, default=None):
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return default or {}


def save_json(path: Path, data: Dict):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


class AgentManager:
    """Main orchestrator - the 'First Mate' that manages the crew."""
    
    def __init__(self, manager_id: str = None):
        self.manager_id = manager_id or f"manager_{uuid.uuid4().hex[:8]}"
        self.task_queue = load_json(TASK_QUEUE, {"tasks": []})
        self.workers = load_json(WORKER_REGISTRY, {"workers": {}})
        self.active_tasks = {}
        self.completed_tasks = []
        
        log_team_event("manager_start", self.manager_id, f"Agent Manager started: {self.manager_id}")
    
    def register_worker(self, worker_type: WorkerType, worker_id: str, capabilities: List[str] = None) -> Dict:
        """Register a worker agent."""
        worker_info = {
            "worker_id": worker_id,
            "worker_type": worker_type.value,
            "capabilities": capabilities or WORKER_CAPABILITIES[worker_type]["tasks"],
            "status": "idle",
            "registered_at": datetime.now().isoformat(),
            "current_task": None,
            "completed_tasks": 0,
            "failed_tasks": 0
        }
        self.workers["workers"][worker_id] = worker_info
        save_json(WORKER_REGISTRY, self.workers)
        
        log_team_event("worker_register", self.manager_id, f"Worker registered: {worker_id} ({worker_type.value})", worker_info)
        return worker_info
    
    def create_task(self, description: str, required_worker_type: WorkerType = None, 
                    priority: TaskPriority = TaskPriority.NORMAL, 
                    dependencies: List[str] = None,
                    context: Dict = None) -> str:
        """Create a new task and add to queue."""
        task_id = f"task_{uuid.uuid4().hex[:8]}"
        task = {
            "task_id": task_id,
            "description": description,
            "required_worker_type": required_worker_type.value if required_worker_type else None,
            "priority": priority.value,
            "status": TaskStatus.PENDING.value,
            "dependencies": dependencies or [],
            "context": context or {},
            "created_at": datetime.now().isoformat(),
            "assigned_to": None,
            "started_at": None,
            "completed_at": None,
            "result": None,
            "error": None
        }
        self.task_queue["tasks"].append(task)
        save_json(TASK_QUEUE, self.task_queue)
        
        log_team_event("task_create", self.manager_id, f"Task created: {task_id} - {description[:80]}", task)
        return task_id
    
    def find_available_worker(self, worker_type: WorkerType = None) -> Optional[str]:
        """Find an idle worker matching the required type."""
        for worker_id, info in self.workers["workers"].items():
            if info["status"] == "idle":
                if worker_type is None or info["worker_type"] == worker_type.value:
                    return worker_id
        return None
    
    def dispatch_task(self, task_id: str, worker_id: str = None) -> bool:
        """Dispatch task to worker."""
        task = next((t for t in self.task_queue["tasks"] if t["task_id"] == task_id), None)
        if not task:
            return False
        
        if task["status"] != TaskStatus.PENDING.value:
            return False
        
        # Check dependencies
        for dep_id in task["dependencies"]:
            dep_task = next((t for t in self.task_queue["tasks"] if t["task_id"] == dep_id), None)
            if dep_task and dep_task["status"] != TaskStatus.COMPLETED.value:
                log_team_event("task_blocked", self.manager_id, f"Task {task_id} blocked by dependency {dep_id}")
                return False
        
        # Find worker if not specified
        if not worker_id:
            required_type = WorkerType(task["required_worker_type"]) if task["required_worker_type"] else None
            worker_id = self.find_available_worker(required_type)
            if not worker_id:
                log_team_event("no_worker", self.manager_id, f"No available worker for task {task_id}")
                return False
        
        # Assign task
        worker = self.workers["workers"].get(worker_id)
        if not worker or worker["status"] != "idle":
            return False
        
        task["status"] = TaskStatus.ASSIGNED.value
        task["assigned_to"] = worker_id
        task["started_at"] = datetime.now().isoformat()
        
        worker["status"] = "busy"
        worker["current_task"] = task_id
        
        save_json(TASK_QUEUE, self.task_queue)
        save_json(WORKER_REGISTRY, self.workers)
        
        log_team_event("task_dispatch", self.manager_id, f"Task {task_id} dispatched to {worker_id}", {"task": task, "worker": worker})
        
        # Actually execute the worker (in real implementation, this would spawn a subprocess)
        self._execute_worker(worker_id, task)
        
        return True
    
    def _execute_worker(self, worker_id: str, task: Dict):
        """Execute worker task via subprocess."""
        worker_type = WorkerType(self.workers["workers"][worker_id]["worker_type"])
        
        # Map worker types to their scripts
        worker_scripts = {
            WorkerType.REVIEW: "scripts/workers/review_worker.py",
            WorkerType.ARBITRAGE: "scripts/workers/arbitrage_worker.py",
            WorkerType.CONTENT: "scripts/workers/content_worker.py",
            WorkerType.CODE: "scripts/workers/code_worker.py",
            WorkerType.RESEARCH: "scripts/workers/research_worker.py",
        }
        
        script_path = HERMES_HOME / worker_scripts.get(worker_type, "scripts/workers/general_worker.py")
        
        if not script_path.exists():
            self._complete_task(task["task_id"], False, f"Worker script not found: {script_path}")
            return
        
        # Prepare task data for worker
        task_data = {
            "task_id": task["task_id"],
            "description": task["description"],
            "context": task["context"],
            "worker_id": worker_id
        }
        
        # Run worker as subprocess
        try:
            env = os.environ.copy()
            env["PYTHONPATH"] = str(HERMES_HOME)
            
            result = subprocess.run(
                [sys.executable, str(script_path), json.dumps(task_data)],
                capture_output=True,
                text=True,
                timeout=300,
                cwd=str(HERMES_HOME),
                env=env
            )
            
            if result.returncode == 0:
                try:
                    worker_result = json.loads(result.stdout.strip().split('\n')[-1])
                    self._complete_task(task["task_id"], True, worker_result)
                except:
                    self._complete_task(task["task_id"], True, {"output": result.stdout})
            else:
                self._complete_task(task["task_id"], False, f"Worker failed: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            self._complete_task(task["task_id"], False, "Worker timeout after 300s")
        except Exception as e:
            self._complete_task(task["task_id"], False, f"Worker execution error: {str(e)}")
    
    def _complete_task(self, task_id: str, success: bool, result: Any):
        """Mark task as completed/failed and free worker."""
        task = next((t for t in self.task_queue["tasks"] if t["task_id"] == task_id), None)
        if not task:
            return
        
        worker_id = task["assigned_to"]
        worker = self.workers["workers"].get(worker_id) if worker_id else None
        
        if success:
            task["status"] = TaskStatus.COMPLETED.value
            task["result"] = result
            if worker:
                worker["completed_tasks"] += 1
        else:
            task["status"] = TaskStatus.FAILED.value
            task["error"] = str(result)
            if worker:
                worker["failed_tasks"] += 1
        
        task["completed_at"] = datetime.now().isoformat()
        
        if worker:
            worker["status"] = "idle"
            worker["current_task"] = None
        
        save_json(TASK_QUEUE, self.task_queue)
        save_json(WORKER_REGISTRY, self.workers)
        
        log_team_event("task_complete", self.manager_id, f"Task {task_id} {'completed' if success else 'failed'}", {"task_id": task_id, "success": success})
        
        # Check for dependent tasks that can now be dispatched
        self._check_dependent_tasks()
    
    def _check_dependent_tasks(self):
        """Check if any pending tasks can now be dispatched."""
        for task in self.task_queue["tasks"]:
            if task["status"] == TaskStatus.PENDING.value:
                self.dispatch_task(task["task_id"])
    
    def run_workflow(self, workflow_name: str, steps: List[Dict]) -> Dict:
        """Run a multi-step workflow."""
        workflow_id = f"wf_{uuid.uuid4().hex[:8]}"
        task_ids = []
        previous_task_id = None
        
        log_team_event("workflow_start", self.manager_id, f"Workflow started: {workflow_id} ({workflow_name})", {"steps": len(steps)})
        
        for i, step in enumerate(steps):
            # Pass context from previous step if needed
            context = step.get("context", {}).copy()
            if previous_task_id:
                # Add previous task ID to context for dependent steps
                context["previous_task_id"] = previous_task_id
            
            task_id = self.create_task(
                description=step["description"],
                required_worker_type=WorkerType(step.get("worker_type", "general_worker")),
                priority=TaskPriority(step.get("priority", 2)),
                dependencies=[previous_task_id] if previous_task_id else None,
                context=context
            )
            task_ids.append(task_id)
            previous_task_id = task_id
        
        # Dispatch first task (or all if no dependencies)
        for task_id in task_ids:
            task = next((t for t in self.task_queue["tasks"] if t["task_id"] == task_id), None)
            if task and not task["dependencies"]:
                self.dispatch_task(task_id)
        
        # Wait for completion (in real implementation, this would be async)
        return {
            "workflow_id": workflow_id,
            "task_ids": task_ids,
            "status": "started"
        }
    
    def get_status(self) -> Dict:
        """Get current fleet status."""
        return {
            "manager_id": self.manager_id,
            "workers": {k: {"worker_id": v["worker_id"], "type": v["worker_type"], "status": v["status"], "current_task": v["current_task"], "completed": v["completed_tasks"]} 
                       for k, v in self.workers["workers"].items()},
            "tasks": {
                "pending": len([t for t in self.task_queue["tasks"] if t["status"] == TaskStatus.PENDING.value]),
                "in_progress": len([t for t in self.task_queue["tasks"] if t["status"] in [TaskStatus.ASSIGNED.value, TaskStatus.IN_PROGRESS.value]]),
                "completed": len([t for t in self.task_queue["tasks"] if t["status"] == TaskStatus.COMPLETED.value]),
                "failed": len([t for t in self.task_queue["tasks"] if t["status"] == TaskStatus.FAILED.value])
            },
            "recent_tasks": [{"task_id": t["task_id"], "status": t["status"], "description": t["description"][:60]} 
                           for t in sorted(self.task_queue["tasks"], key=lambda x: x["created_at"], reverse=True)[:10]]
        }
    
    def wait_for_completion(self, task_ids: List[str], timeout: int = 600) -> Dict:
        """Wait for tasks to complete."""
        start_time = time.time()
        while time.time() - start_time < timeout:
            all_done = True
            for task_id in task_ids:
                task = next((t for t in self.task_queue["tasks"] if t["task_id"] == task_id), None)
                if task and task["status"] not in [TaskStatus.COMPLETED.value, TaskStatus.FAILED.value]:
                    all_done = False
                    break
            if all_done:
                break
            time.sleep(2)
        
        results = {}
        for task_id in task_ids:
            task = next((t for t in self.task_queue["tasks"] if t["task_id"] == task_id), None)
            if task:
                results[task_id] = {"status": task["status"], "result": task.get("result"), "error": task.get("error")}
        
        return results


def main():
    """CLI interface for Agent Manager."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Agent Manager - Multi-Agent Orchestrator")
    parser.add_argument("--create-task", help="Create a new task")
    parser.add_argument("--worker-type", help="Required worker type", default="general_worker")
    parser.add_argument("--priority", type=int, default=2, help="Task priority (1-4)")
    parser.add_argument("--workflow", help="Run a predefined workflow")
    parser.add_argument("--status", action="store_true", help="Show fleet status")
    parser.add_argument("--register-worker", help="Register a worker")
    parser.add_argument("--list-workers", action="store_true", help="List registered workers")
    
    args = parser.parse_args()
    
    manager = AgentManager()
    
    if args.status:
        status = manager.get_status()
        print(json.dumps(status, indent=2, ensure_ascii=False))
        return
    
    if args.list_workers:
        workers = manager.workers["workers"]
        for w in workers.values():
            print(f"  {w['worker_id']}: {w['worker_type']} - {w['status']} (completed: {w['completed_tasks']})")
        return
    
    if args.register_worker:
        worker_type = WorkerType(args.worker_type) if args.worker_type in [w.value for w in WorkerType] else WorkerType.GENERAL
        worker_id = manager.register_worker(worker_type, args.register_worker)
        print(f"Registered worker: {worker_id['worker_id']}")
        return
    
    if args.workflow:
        workflows = {
            "landing_review": [
                {"description": "Create landing page for beauty salon", "worker_type": "code_worker", "priority": 3},
                {"description": "Review landing page quality", "worker_type": "review_worker", "priority": 3, "context": {"checklist": "landing"}}
            ],
            "arbitrage_pipeline": [
                {"description": "Find CPA offers for nutra vertical", "worker_type": "arbitrage_worker", "priority": 3},
                {"description": "Analyze offer ROI potential", "worker_type": "research_worker", "priority": 2},
                {"description": "Create content for top offer", "worker_type": "content_worker", "priority": 2}
            ]
        }
        if args.workflow in workflows:
            result = manager.run_workflow(args.workflow, workflows[args.workflow])
            print(f"Workflow started: {result['workflow_id']}")
            print(f"Tasks: {result['task_ids']}")
            
            # Wait for completion
            final = manager.wait_for_completion(result["task_ids"])
            print(f"Results: {json.dumps(final, indent=2)}")
        else:
            print(f"Unknown workflow: {args.workflow}")
            print(f"Available: {list(workflows.keys())}")
        return
    
    if args.create_task:
        worker_type = WorkerType(args.worker_type) if args.worker_type in [w.value for w in WorkerType] else WorkerType.GENERAL
        task_id = manager.create_task(args.create_task, worker_type, TaskPriority(args.priority))
        print(f"Created task: {task_id}")
        
        # Dispatch immediately
        if manager.dispatch_task(task_id):
            print(f"Dispatched task: {task_id}")
            # Wait for completion
            result = manager.wait_for_completion([task_id])
            print(f"Result: {json.dumps(result, indent=2)}")
        else:
            print(f"Could not dispatch - no available worker")
        return
    
    # Default: show status
    status = manager.get_status()
    print(json.dumps(status, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
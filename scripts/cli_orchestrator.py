#!/usr/bin/env python3
"""
CLI Orchestrator — Multi-Agent Terminal Control
Implements: CLI Orchestration from Claude Code (parallel agent execution, result aggregation)

Runs multiple composed agents in parallel, aggregates results, handles dependencies.
"""

import os
import json
import subprocess
import threading
import time
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

HERMES_HOME = Path(os.environ.get("HERMES_HOME", "D:/Portable_Soft/hermes"))


@dataclass
class AgentTask:
    """Single agent execution task"""
    task_id: str
    agent_name: str
    prompt: str
    dependencies: List[str]  # Task IDs that must complete first
    timeout: int = 300
    priority: int = 0


@dataclass
class AgentResult:
    """Result from agent execution"""
    task_id: str
    agent_name: str
    success: bool
    output: str
    error: str = ""
    elapsed: float = 0.0
    artifacts: List[Dict] = None


class CLIOrchestrator:
    """Orchestrates multiple agents in parallel with dependency management"""
    
    def __init__(self, max_workers: int = 3):
        self.max_workers = max_workers
        self.tasks: Dict[str, AgentTask] = {}
        self.results: Dict[str, AgentResult] = {}
        self.executor_fn: Optional[Callable] = None
    
    def set_executor(self, fn: Callable[[str], Dict]):
        """Set the function to execute agent prompts (e.g., subagent runner)"""
        self.executor_fn = fn
    
    def add_task(
        self,
        task_id: str,
        agent_name: str,
        prompt: str,
        dependencies: List[str] = None,
        timeout: int = 300,
        priority: int = 0
    ):
        """Add a task to the orchestration plan"""
        self.tasks[task_id] = AgentTask(
            task_id=task_id,
            agent_name=agent_name,
            prompt=prompt,
            dependencies=dependencies or [],
            timeout=timeout,
            priority=priority
        )
    
    def add_chain(self, base_id: str, steps: List[Dict]):
        """Add a chain of dependent tasks"""
        prev_id = None
        for i, step in enumerate(steps):
            task_id = f"{base_id}_{i}"
            deps = [prev_id] if prev_id else []
            self.add_task(task_id, step["agent"], step["prompt"], deps)
            prev_id = task_id
    
    def add_parallel(self, base_id: str, steps: List[Dict]):
        """Add parallel tasks (all start together)"""
        for i, step in enumerate(steps):
            task_id = f"{base_id}_p{i}"
            self.add_task(task_id, step["agent"], step["prompt"], [])
    
    def execute(self, executor_fn: Callable[[str], Dict] = None) -> Dict[str, AgentResult]:
        """Execute all tasks respecting dependencies"""
        if executor_fn:
            self.executor_fn = executor_fn
        
        if not self.executor_fn:
            raise ValueError("No executor function set. Use set_executor() or pass to execute().")
        
        completed = set()
        running = {}
        lock = threading.Lock()
        
        def run_task(task: AgentTask) -> AgentResult:
            """Execute single task"""
            start = time.time()
            try:
                result = self.executor_fn(task.prompt)
                elapsed = time.time() - start
                return AgentResult(
                    task_id=task.task_id,
                    agent_name=task.agent_name,
                    success=result.get("success", True),
                    output=result.get("output", ""),
                    error=result.get("error", ""),
                    elapsed=elapsed,
                    artifacts=result.get("artifacts")
                )
            except Exception as e:
                elapsed = time.time() - start
                return AgentResult(
                    task_id=task.task_id,
                    agent_name=task.agent_name,
                    success=False,
                    output="",
                    error=str(e),
                    elapsed=elapsed
                )
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit ready tasks
            future_to_task = {}
            
            while True:
                with lock:
                    # Find ready tasks (dependencies met, not running, not completed)
                    ready = []
                    for task_id, task in self.tasks.items():
                        if task_id in completed or task_id in running:
                            continue
                        if all(dep in completed for dep in task.dependencies):
                            ready.append(task)
                    
                    # Sort by priority
                    ready.sort(key=lambda t: -t.priority)
                    
                    # Submit up to max_workers
                    for task in ready:
                        if len(running) >= self.max_workers:
                            break
                        future = executor.submit(run_task, task)
                        future_to_task[future] = task.task_id
                        running[task.task_id] = task
                
                if not ready and not running:
                    break  # All done
                
                # Wait for at least one completion
                if running:
                    done, _ = as_completed(future_to_task.keys(), timeout=1).__iter__()
                    future = done
                    task_id = future_to_task[future]
                    result = future.result()
                    
                    with lock:
                        self.results[task_id] = result
                        completed.add(task_id)
                        del running[task_id]
                        del future_to_task[future]
                        
                        print(f"  ✓ {task_id} ({result.agent_name}) - {'OK' if result.success else 'FAIL'} ({result.elapsed:.1f}s)")
                        if result.error:
                            print(f"    Error: {result.error[:100]}")
                
                time.sleep(0.1)
        
        return self.results
    
    def get_summary(self) -> Dict:
        """Get execution summary"""
        total = len(self.results)
        successful = sum(1 for r in self.results.values() if r.success)
        failed = total - successful
        total_time = sum(r.elapsed for r in self.results.values())
        
        return {
            "total_tasks": total,
            "successful": successful,
            "failed": failed,
            "total_time": total_time,
            "results": {k: asdict(v) for k, v in self.results.items()}
        }
    
    def save_results(self, output_file: Path = None):
        """Save results to file"""
        if output_file is None:
            output_file = HERMES_HOME / "cache" / "orchestration_results.json"
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        data = {
            "timestamp": datetime.now().isoformat(),
            "summary": self.get_summary(),
            "tasks": {k: asdict(v) for k, v in self.tasks.items()},
            "results": {k: asdict(v) for k, v in self.results.items()}
        }
        output_file.write_text(json.dumps(data, indent=2, ensure_ascii=False))
        return output_file


def default_subagent_executor(prompt: str) -> Dict:
    """Default executor using python -m hermes_cli delegate"""
    try:
        result = subprocess.run(
            ["python", "-m", "hermes_cli", "delegate", "--goal", prompt],
            capture_output=True, text=True, timeout=300,
            cwd=str(HERMES_HOME),
            env={**os.environ, "HERMES_HOME": str(HERMES_HOME)}
        )
        return {
            "success": result.returncode == 0,
            "output": result.stdout,
            "error": result.stderr
        }
    except subprocess.TimeoutExpired:
        return {"success": False, "output": "", "error": "Timeout"}
    except Exception as e:
        return {"success": False, "output": "", "error": str(e)}


# CLI
def main():
    import sys
    if len(sys.argv) < 2:
        print("Usage: python cli_orchestrator.py <plan_file.json>")
        print("Or use programmatically: orchestrator = CLIOrchestrator(); orchestrator.add_task(...); orchestrator.execute()")
        sys.exit(1)
    
    plan_file = Path(sys.argv[1])
    if not plan_file.exists():
        print(f"Plan file not found: {plan_file}")
        sys.exit(1)
    
    plan = json.loads(plan_file.read_text())
    
    orchestrator = CLIOrchestrator(max_workers=plan.get("max_workers", 3))
    
    for task in plan.get("tasks", []):
        orchestrator.add_task(
            task["id"],
            task["agent"],
            task["prompt"],
            task.get("dependencies", []),
            task.get("timeout", 300),
            task.get("priority", 0)
        )
    
    orchestrator.set_executor(default_subagent_executor)
    results = orchestrator.execute()
    summary = orchestrator.get_summary()
    output_file = orchestrator.save_results()
    
    print(f"\n=== ORCHESTRATION COMPLETE ===")
    print(f"Total: {summary['total_tasks']}, Success: {summary['successful']}, Failed: {summary['failed']}")
    print(f"Total time: {summary['total_time']:.1f}s")
    print(f"Results saved to: {output_file}")


if __name__ == "__main__":
    main()
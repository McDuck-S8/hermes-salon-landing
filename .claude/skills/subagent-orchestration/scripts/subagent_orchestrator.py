#!/usr/bin/env python3
"""
Subagent Orchestrator — Manages subagent delegation with context, proxy, retries, and monitoring.
"""

import asyncio
import json
import logging
import os
import sys
import time
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Callable
from enum import Enum

# Add project root to path
HERMES_HOME = Path(os.environ.get("HERMES_HOME", "D:/Portable_Soft/hermes"))
sys.path.insert(0, str(HERMES_HOME))

# Logging setup
LOG_DIR = HERMES_HOME / "logs" / "subagent_orchestration"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / f"subagent_orchestration_{datetime.now().strftime('%Y%m%d')}.jsonl"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class SubagentStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"


@dataclass
class SubagentTask:
    """Task definition for subagent."""
    task_type: str
    params: Dict[str, Any]
    timeout: int = 120
    max_retries: int = 3
    backoff_base: int = 2
    priority: int = 1


@dataclass
class SubagentResult:
    """Result from subagent execution."""
    success: bool
    data: Any = None
    error: str = ""
    metadata: Dict = field(default_factory=dict)


@dataclass
class SubagentInfo:
    """Subagent runtime info."""
    subagent_id: str
    task: SubagentTask
    status: SubagentStatus = SubagentStatus.PENDING
    result: Optional[SubagentResult] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    retry_count: int = 0
    last_heartbeat: Optional[str] = None
    logs: List[str] = field(default_factory=list)


class SubagentOrchestrator:
    """Orchestrates subagent execution with proper context and error handling."""
    
    def __init__(self):
        self.subagents: Dict[str, SubagentInfo] = {}
        self.task_templates = self._load_task_templates()
        self._running = False
    
    def _load_task_templates(self) -> Dict:
        """Load task templates with default configurations."""
        return {
            "search_ozon": {
                "tool": "web_automation",
                "method": "search_and_extract",
                "default_params": {"site": "ozon", "limit": 20, "sort": "price", "pages": 3},
                "timeout": 120,
                "max_retries": 3,
                "backoff_base": 2,
            },
            "search_wb": {
                "tool": "web_automation",
                "method": "search_and_extract",
                "default_params": {"site": "wb", "limit": 20, "sort": "price", "pages": 3},
                "timeout": 120,
                "max_retries": 3,
                "backoff_base": 2,
            },
            "get_product_details": {
                "tool": "web_automation",
                "method": "get_product_details",
                "default_params": {},
                "timeout": 60,
                "max_retries": 2,
                "backoff_base": 2,
            },
            "search_github": {
                "tool": "web_automation",
                "method": "execute_site_action",
                "default_params": {"action": "search_repos"},
                "timeout": 60,
                "max_retries": 2,
                "backoff_base": 2,
            },
        }
    
    def _build_subagent_context(self) -> Dict:
        """Build context dict passed to subagents."""
        return {
            "proxy": "socks5://127.0.0.1:10806",
            "env_vars": {
                "HERMES_HOME": str(HERMES_HOME),
                "HTTP_PROXY": "socks5://127.0.0.1:10806",
                "HTTPS_PROXY": "socks5://127.0.0.1:10806",
                "PLAYWRIGHT_BROWSERS_PATH": "ms-playwright",
            },
            "tools": [
                "scripts/web_automation.py",
                "scripts/config_loader.py",
            ],
            "permissions": {
                "network": True,
                "browser": True,
                "file_read": True,
                "file_write": False,
            },
            "instructions": (
                "Use web_automation.search_and_extract for marketplace tasks. "
                "Always use proxy. Return JSON with success, data, error fields. "
                "Log all actions to feedback store."
            ),
        }
    
    def _get_feedback_store_path(self) -> Path:
        return HERMES_HOME / "cache" / "feedback_store.db"
    
    def _log_to_feedback(self, event: str, subagent_id: str, task: str, 
                         params: Dict, result: Dict, duration_ms: int):
        """Log subagent activity to feedback store."""
        try:
            import sqlite3
            conn = sqlite3.connect(self._get_feedback_store_path())
            conn.execute("""
                CREATE TABLE IF NOT EXISTS feedback (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    skill TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    result TEXT,
                    tags TEXT,
                    source TEXT
                )
            """)
            conn.execute(
                "INSERT INTO feedback (skill, timestamp, result, tags, source) VALUES (?, ?, ?, ?, ?)",
                (
                    "subagent_orchestration",
                    datetime.now().isoformat(),
                    json.dumps({
                        "event": event,
                        "subagent_id": subagent_id,
                        "task": task,
                        "params": params,
                        "result": result,
                        "duration_ms": duration_ms
                    }, ensure_ascii=False),
                    json.dumps([event, task, subagent_id], ensure_ascii=False),
                    "subagent_orchestrator"
                )
            )
            conn.commit()
            conn.close()
        except Exception as e:
            logger.warning(f"Failed to log to feedback store: {e}")
    
    def delegate(self, task_type: str, params: Dict = None, **overrides) -> str:
        """Delegate a task to a subagent. Returns subagent_id."""
        if task_type not in self.task_templates:
            raise ValueError(f"Unknown task type: {task_type}")
        
        template = self.task_templates[task_type]
        merged_params = {**template.get("default_params", {}), **(params or {})}
        
        task = SubagentTask(
            task_type=task_type,
            params=merged_params,
            timeout=overrides.get("timeout", template.get("timeout", 120)),
            max_retries=overrides.get("max_retries", template.get("max_retries", 3)),
            backoff_base=overrides.get("backoff_base", template.get("backoff_base", 2)),
        )
        
        subagent_id = f"sub_{uuid.uuid4().hex[:12]}"
        self.subagents[subagent_id] = SubagentInfo(
            subagent_id=subagent_id,
            task=task,
        )
        
        logger.info(f"Delegated task {task_type} to subagent {subagent_id}")
        self._log_to_feedback("subagent_delegated", subagent_id, task_type, 
                             merged_params, {}, 0)
        
        return subagent_id
    
    async def execute(self, subagent_id: str) -> SubagentResult:
        """Execute a delegated subagent task with retries."""
        if subagent_id not in self.subagents:
            return SubagentResult(success=False, error=f"Subagent {subagent_id} not found")
        
        info = self.subagents[subagent_id]
        info.status = SubagentStatus.RUNNING
        info.started_at = datetime.now().isoformat()
        
        template = self.task_templates[info.task.task_type]
        tool_name = template["tool"]
        method_name = template["method"]
        
        last_error = ""
        
        for attempt in range(info.task.max_retries + 1):
            info.retry_count = attempt
            info.status = SubagentStatus.RETRYING if attempt > 0 else SubagentStatus.RUNNING
            info.last_heartbeat = datetime.now().isoformat()
            
            start_time = time.time()
            
            try:
                # Import and execute the tool method
                result = await self._execute_tool_method(
                    tool_name, method_name, info.task.params, info.task.timeout
                )
                
                duration_ms = int((time.time() - start_time) * 1000)
                
                if result.success:
                    info.status = SubagentStatus.COMPLETED
                    info.completed_at = datetime.now().isoformat()
                    info.result = result
                    
                    self._log_to_feedback("subagent_completed", subagent_id, 
                                         info.task.task_type, info.task.params,
                                         {"success": True, "data": result.data}, 
                                         duration_ms)
                    return result
                else:
                    last_error = result.error or "Unknown error"
                    logger.warning(f"Subagent {subagent_id} attempt {attempt + 1} failed: {last_error}")
                    
            except asyncio.TimeoutError:
                last_error = f"Timeout after {info.task.timeout}s"
                logger.warning(f"Subagent {subagent_id} attempt {attempt + 1} timed out")
            except Exception as e:
                last_error = str(e)
                logger.error(f"Subagent {subagent_id} attempt {attempt + 1} error: {e}")
            
            # Exponential backoff
            if attempt < info.task.max_retries:
                wait_time = info.task.backoff_base ** (attempt + 1)
                logger.info(f"Subagent {subagent_id} retrying in {wait_time}s...")
                await asyncio.sleep(wait_time)
        
        # All retries exhausted
        info.status = SubagentStatus.FAILED
        info.completed_at = datetime.now().isoformat()
        error_result = SubagentResult(success=False, error=last_error or "Max retries exceeded")
        info.result = error_result
        
        duration_ms = int((time.time() - start_time) * 1000) if 'start_time' in locals() else 0
        self._log_to_feedback("subagent_failed", subagent_id,
                             info.task.task_type, info.task.params,
                             {"success": False, "error": last_error},
                             duration_ms)
        
        return error_result
    
    async def _execute_tool_method(self, tool: str, method: str, params: Dict, timeout: int) -> SubagentResult:
        """Execute a method from a tool module."""
        if tool == "web_automation":
            from scripts.web_automation import BrowserAutomation, BrowserConfig
            
            config = BrowserConfig(
                headless=True,
                proxy="socks5://127.0.0.1:10806",
                ghost_surfer=False,
            )
            
            async with BrowserAutomation(config=config, site=params.get("site", "ozon")) as bot:
                if method == "search_and_extract":
                    data = await asyncio.wait_for(
                        bot.search_and_extract(
                            query=params.get("query", ""),
                            site=params.get("site", "ozon"),
                            limit=params.get("limit", 20),
                            sort=params.get("sort", "price"),
                            pages=params.get("pages", 3)
                        ),
                        timeout=timeout
                    )
                    return SubagentResult(success=True, data=data)
                elif method == "get_product_details":
                    data = await asyncio.wait_for(
                        bot.get_product_details(params.get("url", "")),
                        timeout=timeout
                    )
                    return SubagentResult(success=True, data=data)
                elif method == "execute_site_action":
                    data = await asyncio.wait_for(
                        bot.execute_site_action(params.get("action", ""), params),
                        timeout=timeout
                    )
                    return SubagentResult(success=data, data=data)
        
        return SubagentResult(success=False, error=f"Unknown tool/method: {tool}.{method}")
    
    def get_status(self, subagent_id: str) -> Optional[SubagentInfo]:
        """Get subagent status."""
        return self.subagents.get(subagent_id)
    
    def list_subagents(self) -> List[SubagentInfo]:
        """List all subagents."""
        return list(self.subagents.values())
    
    def get_completed(self) -> List[SubagentInfo]:
        """Get completed subagents."""
        return [s for s in self.subagents.values() if s.status == SubagentStatus.COMPLETED]
    
    def get_failed(self) -> List[SubagentInfo]:
        """Get failed subagents."""
        return [s for s in self.subagents.values() if s.status == SubagentStatus.FAILED]


async def main():
    """CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Subagent Orchestrator")
    parser.add_argument("--delegate", action="store_true", help="Delegate a task")
    parser.add_argument("--task", help="Task type (search_ozon, search_wb, etc.)")
    parser.add_argument("--params", help="JSON params for task")
    parser.add_argument("--execute", help="Execute subagent by ID")
    parser.add_argument("--status", help="Get status of subagent by ID")
    parser.add_argument("--list", action="store_true", help="List all subagents")
    
    args = parser.parse_args()
    
    orchestrator = SubagentOrchestrator()
    
    if args.delegate and args.task:
        params = json.loads(args.params) if args.params else {}
        subagent_id = orchestrator.delegate(args.task, params)
        print(f"Delegated: {subagent_id}")
        
        # Execute immediately
        result = await orchestrator.execute(subagent_id)
        print(f"Result: {result.success}, {result.error or 'OK'}")
        if result.data:
            print(f"Data: {len(result.data) if isinstance(result.data, list) else 'object'} items")
    
    elif args.execute:
        result = await orchestrator.execute(args.execute)
        print(f"Result: {result.success}, {result.error or 'OK'}")
    
    elif args.status:
        info = orchestrator.get_status(args.status)
        if info:
            print(json.dumps(asdict(info), ensure_ascii=False, indent=2))
        else:
            print("Subagent not found")
    
    elif args.list:
        for info in orchestrator.list_subagents():
            print(f"{info.subagent_id}: {info.task.task_type} - {info.status.value}")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    asyncio.run(main())
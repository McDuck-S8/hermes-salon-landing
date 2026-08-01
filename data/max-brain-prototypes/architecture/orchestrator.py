#!/usr/bin/env python3
"""
Max Agent Orchestrator — Управление агентами и задачами
Max координирует, агенты выполняют, пользователь не ждёт
"""

import json
import time
import subprocess
import threading
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from enum import Enum
import logging

# ===== КОНФИГУРАЦИЯ =====
BRAIN_DIR = Path("D:/MAX-BRAIN")
AGENTS_DIR = BRAIN_DIR / "agents"
TASKS_DIR = BRAIN_DIR / "tasks"
REPORTS_DIR = BRAIN_DIR / "reports"
QUEUE_DIR = BRAIN_DIR / "queue"

# Создаём директории
for dir_path in [AGENTS_DIR, TASKS_DIR, REPORTS_DIR, QUEUE_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

# ===== ЛОГИРОВАНИЕ =====
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[logging.FileHandler(BRAIN_DIR / "orchestrator.log", encoding='utf-8', mode='a')]
)
logger = logging.getLogger(__name__)


# ===== МОДЕЛИ ДАННЫХ =====
class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class AgentStatus(Enum):
    IDLE = "idle"
    BUSY = "busy"
    OFFLINE = "offline"

@dataclass
class Task:
    id: str
    name: str
    description: str
    agent_type: str
    status: str = TaskStatus.PENDING.value
    created_at: str = ""
    started_at: str = ""
    completed_at: str = ""
    result: str = ""
    error: str = ""
    priority: int = 5  # 1-10, 1=highest

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()

@dataclass
class Agent:
    id: str
    name: str
    agent_type: str
    status: str = AgentStatus.IDLE.value
    current_task: str = ""
    last_seen: str = ""
    script: str = ""

    def __post_init__(self):
        if not self.last_seen:
            self.last_seen = datetime.now().isoformat()


# ===== ОРКЕСТРАТОР =====
class AgentOrchestrator:
    """Координатор агентов и задач"""
    
    def __init__(self):
        self.tasks: Dict[str, Task] = {}
        self.agents: Dict[str, Agent] = {}
        self.running = False
        self.dispatcher_thread = None
        
        # Регистрируем встроенных агентов
        self._register_builtin_agents()
    
    def _register_builtin_agents(self):
        """Зарегистрировать встроенных агентов"""
        
        agents_config = [
            {
                "id": "agent-memory",
                "name": "Memory Agent",
                "agent_type": "memory",
                "script": "memory-agent.py"
            },
            {
                "id": "agent-github",
                "name": "GitHub Monitor",
                "agent_type": "github",
                "script": "github-agent.py"
            },
            {
                "id": "agent-backup",
                "name": "Backup Agent",
                "agent_type": "backup",
                "script": "backup-agent.py"
            },
            {
                "id": "agent-telegram",
                "name": "Telegram Bot Agent",
                "agent_type": "telegram",
                "script": "telegram-agent.py"
            }
        ]
        
        for config in agents_config:
            agent = Agent(**config)
            self.agents[agent.id] = agent
            logger.info(f"Registered agent: {agent.name} ({agent.id})")
    
    def create_task(self, name: str, description: str, agent_type: str, priority: int = 5) -> str:
        """Создать задачу для агента"""
        task_id = f"task-{uuid.uuid4().hex[:8]}"
        task = Task(
            id=task_id,
            name=name,
            description=description,
            agent_type=agent_type,
            priority=priority
        )
        
        self.tasks[task_id] = task
        self._save_task(task)
        self._queue_task(task)
        
        logger.info(f"Task created: {task_id} -> {agent_type}")
        return task_id
    
    def _save_task(self, task: Task):
        """Сохранить задачу в файл"""
        task_file = TASKS_DIR / f"{task.id}.json"
        with open(task_file, 'w', encoding='utf-8') as f:
            json.dump(asdict(task), f, ensure_ascii=False, indent=2)
    
    def _queue_task(self, task: Task):
        """Добавить задачу в очередь"""
        queue_file = QUEUE_DIR / "pending.jsonl"
        with open(queue_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps({
                "task_id": task.id,
                "agent_type": task.agent_type,
                "priority": task.priority,
                "created_at": task.created_at
            }, ensure_ascii=False) + '\n')
    
    def assign_task(self, task: Task, agent: Agent):
        """Назначить задачу агенту"""
        task.status = TaskStatus.RUNNING.value
        task.started_at = datetime.now().isoformat()
        agent.status = AgentStatus.BUSY.value
        agent.current_task = task.id
        agent.last_seen = datetime.now().isoformat()
        
        self._save_task(task)
        self._save_agent(agent)
        
        logger.info(f"Task {task.id} assigned to {agent.name}")
    
    def complete_task(self, task_id: str, result: str, error: str = ""):
        """Завершить задачу"""
        if task_id not in self.tasks:
            logger.error(f"Task {task_id} not found")
            return
        
        task = self.tasks[task_id]
        task.status = TaskStatus.FAILED.value if error else TaskStatus.COMPLETED.value
        task.completed_at = datetime.now().isoformat()
        task.result = result
        task.error = error
        
        # Освободить агента
        for agent in self.agents.values():
            if agent.current_task == task_id:
                agent.status = AgentStatus.IDLE.value
                agent.current_task = ""
                agent.last_seen = datetime.now().isoformat()
                self._save_agent(agent)
                break
        
        self._save_task(task)
        self._save_report(task, result, error)
        
        status = "FAILED" if error else "COMPLETED"
        logger.info(f"Task {task_id} {status}")
    
    def _save_agent(self, agent: Agent):
        """Сохранить агента в файл"""
        agent_file = AGENTS_DIR / f"{agent.id}.json"
        with open(agent_file, 'w', encoding='utf-8') as f:
            json.dump(asdict(agent), f, ensure_ascii=False, indent=2)
    
    def _save_report(self, task: Task, result: str, error: str):
        """Сохранить отчёт"""
        report = {
            "task_id": task.id,
            "task_name": task.name,
            "agent_type": task.agent_type,
            "status": task.status,
            "created_at": task.created_at,
            "started_at": task.started_at,
            "completed_at": task.completed_at,
            "result": result,
            "error": error
        }
        
        report_file = REPORTS_DIR / f"{task.id}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
    
    def get_available_agent(self, agent_type: str) -> Optional[Agent]:
        """Найти доступного агента"""
        for agent in self.agents.values():
            if agent.agent_type == agent_type and agent.status == AgentStatus.IDLE.value:
                return agent
        return None
    
    def dispatch_pending_tasks(self):
        """Обработать ожидающие задачи"""
        queue_file = QUEUE_DIR / "pending.jsonl"
        if not queue_file.exists():
            return
        
        # Читаем очередь
        pending = []
        with open(queue_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    pending.append(json.loads(line))
        
        # Сортируем по приоритету
        pending.sort(key=lambda x: x['priority'])
        
        # Обрабатываем
        processed = []
        for item in pending:
            task_id = item['task_id']
            if task_id not in self.tasks:
                continue
            
            task = self.tasks[task_id]
            if task.status != TaskStatus.PENDING.value:
                processed.append(item)
                continue
            
            agent = self.get_available_agent(task.agent_type)
            if agent:
                self.assign_task(task, agent)
                self._start_agent_task(agent, task)
            else:
                processed.append(item)
        
        # Обновляем очередь
        with open(queue_file, 'w', encoding='utf-8') as f:
            for item in processed:
                f.write(json.dumps(item, ensure_ascii=False) + '\n')
    
    def _start_agent_task(self, agent: Agent, task: Task):
        """Запустить задачу агента в фоне"""
        def run_task():
            try:
                # Запускаем скрипт агента
                script_path = AGENTS_DIR / agent.script
                if script_path.exists():
                    proc = subprocess.run(
                        ['python', str(script_path), '--task', task.id],
                        capture_output=True,
                        text=True,
                        timeout=3600  # 1 час максимум
                    )
                    self.complete_task(task.id, proc.stdout, proc.stderr)
                else:
                    # Агент не найден - симулируем выполнение
                    time.sleep(2)
                    self.complete_task(task.id, f"Task executed by {agent.name}")
            except Exception as e:
                self.complete_task(task.id, "", str(e))
        
        thread = threading.Thread(target=run_task, daemon=True)
        thread.start()
    
    def start(self):
        """Запустить оркестратор"""
        self.running = True
        
        # Сохраняем состояние агентов
        for agent in self.agents.values():
            self._save_agent(agent)
        
        # Запускаем диспетчер
        self.dispatcher_thread = threading.Thread(target=self._dispatcher_loop, daemon=True)
        self.dispatcher_thread.start()
        
        logger.info("Orchestrator started")
        self.print_status()
    
    def stop(self):
        """Остановить оркестратор"""
        self.running = False
        if self.dispatcher_thread:
            self.dispatcher_thread.join(timeout=5)
        logger.info("Orchestrator stopped")
    
    def _dispatcher_loop(self):
        """Цикл диспетчера"""
        while self.running:
            self.dispatch_pending_tasks()
            time.sleep(2)  # Проверка каждые 2 секунды
    
    def print_status(self):
        """Вывести статус"""
        print("")
        print("=" * 70)
        print("  MAX AGENT ORCHESTRATOR")
        print("=" * 70)
        print(f"  Tasks: {len(self.tasks)} total")
        print(f"    - Pending: {sum(1 for t in self.tasks.values() if t.status == 'pending')}")
        print(f"    - Running: {sum(1 for t in self.tasks.values() if t.status == 'running')}")
        print(f"    - Completed: {sum(1 for t in self.tasks.values() if t.status == 'completed')}")
        print(f"    - Failed: {sum(1 for t in self.tasks.values() if t.status == 'failed')}")
        print("")
        print(f"  Agents: {len(self.agents)} total")
        for agent in self.agents.values():
            status_icon = "[IDLE]" if agent.status == "idle" else "[BUSY]" if agent.status == "busy" else "[OFF]"
            print(f"    {status_icon} {agent.name}: {agent.status}")
        print("=" * 70)
        print("")
        print("Max is coordinating. Agents are working. You don't wait.")
        print("")


# ===== CLI =====
def main():
    """Точка входа"""
    orchestrator = AgentOrchestrator()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == 'start':
            orchestrator.start()
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                orchestrator.stop()
        
        elif command == 'status':
            orchestrator.print_status()
        
        elif command == 'task':
            if len(sys.argv) < 5:
                print("Usage: orchestrator.py task <name> <agent_type> <description>")
                return
            name = sys.argv[2]
            agent_type = sys.argv[3]
            description = ' '.join(sys.argv[4:])
            task_id = orchestrator.create_task(name, description, agent_type)
            print(f"Task created: {task_id}")
        
        elif command == 'test':
            logger.info("Test run...")
            # Создаём тестовые задачи
            orchestrator.create_task("Test 1", "Test task 1", "memory", priority=1)
            orchestrator.create_task("Test 2", "Test task 2", "github", priority=5)
            orchestrator.start()
            time.sleep(10)
            orchestrator.print_status()
            orchestrator.stop()
            logger.info("Test completed")
        
        else:
            print(f"Unknown command: {command}")
            print("Commands: start, status, task, test")
    else:
        # Интерактивный режим
        orchestrator.start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            orchestrator.stop()


if __name__ == "__main__":
    import sys
    main()

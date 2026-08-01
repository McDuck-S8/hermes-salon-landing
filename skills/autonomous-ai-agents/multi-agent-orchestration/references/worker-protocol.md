# Worker Protocol: Manager ↔ Worker Communication

**Protocol Version**: 1.0
**Transport**: JSON over stdin/stdout (subprocess)

## Task Dispatch (Manager → Worker)

```json
{
  "task_id": "task_abc12345",
  "description": "Create landing page for beauty salon",
  "context": {
    "niche": "beauty salon",
    "offer": "Free consultation",
    "previous_task_id": "task_xyz78901"
  },
  "worker_id": "code_001"
}
```

**Fields**:
- `task_id` — уникальный ID задачи (manager-generated)
- `description` — человеко-читаемое описание
- `context` — дополнительные данные (niche, offer, previous_task_id, checklist name)
- `worker_id` — ID воркера, которому назначена задача

## Task Result (Worker → Manager)

### Success
```json
{
  "success": true,
  "result": {
    "message": "Landing page created for beauty salon",
    "file": "D:\\Portable_Soft\\hermes\\cache\\landings\\landing_task_abc12345.html",
    "preview_url": "file://D:\\Portable_Soft\\hermes\\cache\\landings\\landing_task_abc12345.html",
    "status": "done",
    "niche": "beauty salon",
    "offer": "Free consultation"
  }
}
```

### Failure
```json
{
  "success": false,
  "error": "Worker execution error: template not found"
}
```

## Worker Lifecycle

1. **Manager** spawns worker via `subprocess.run()`
2. **Worker** reads JSON from `sys.argv[1]`
3. **Worker** executes `execute(task_data)` method
4. **Worker** prints JSON result to stdout
5. **Manager** parses result, updates task queue, logs to `agent_team.log`

## Worker Base Class (`scripts/worker_base.py`)

```python
class WorkerBase(ABC):
    def __init__(self, worker_id: str, worker_type: str):
        self.worker_id = worker_id
        self.worker_type = worker_type
    
    @abstractmethod
    def execute(self, task_data: Dict) -> Dict:
        pass
    
    def run(self, task_data: Dict) -> Dict:
        # Logging, error handling, returns {"success": bool, "result": ..., "error": ...}
        pass

    # Helpers:
    def load_checklist(self, name: str) -> Dict
    def save_checklist(self, name: str, data: Dict) -> Path
    def read_file(self, path: str) -> str
    def call_llm(self, prompt: str, max_tokens: int) -> str
```

## Specialized Workers

### Code Worker (`code_worker.py`)
- **Capabilities**: write_code, refactor, debug, write_tests, create_tool, create_landing
- **Context keys**: niche, offer, tool_name, purpose, file_path

### Review Worker (`review_worker.py`)
- **Capabilities**: review_landing, review_code, review_content
- **Context keys**: checklist (landing/code/content), previous_task_id, file_path, url, content
- **Output**: score (0-100), passed (bool), checks[], issues[]

### General Worker (`general_worker.py`)
- **Capabilities**: any simple task
- **Used for**: testing, fallback

## Context Passing Between Workers

Воркфлоу `landing_review`:
```
Step 1: Code Worker создаёт лендинг
  context: {"niche": "beauty salon", "offer": "Free consultation"}

Step 2: Review Worker проверяет
  context: {"checklist": "landing", "previous_task_id": "task_abc12345"}
  → Review Worker читает task_queue.json, находит result.file от Step 1
```

## Team Log (`cache/agent_team.log`)

JSONL формат, одна строка на событие:
```json
{"timestamp": "2026-07-08T02:47:34.806365", "event_type": "worker_success", "agent_id": "review_001", "message": "Task completed: Review landing page quality", "data": {"task_id": "task_148cedce", "result_summary": "{'score': 66, 'passed': False, 'issues': ['...']}"}}
```

Event types:
- `manager_start` — менеджер запущен
- `worker_register` — воркер зарегистрирован
- `task_create` — задача создана
- `task_dispatch` — задача раздана воркеру
- `worker_start` — воркер начал выполнение
- `worker_success` — воркер завершил успешно
- `worker_error` — воркер упал с ошибкой
- `task_complete` — задача завершена (manager view)
- `workflow_start` — воркфлоу запущен

## Error Handling

1. **Worker script not found** → Manager marks task FAILED, logs error
2. **Worker timeout (300s)** → Manager marks task FAILED
3. **Worker returns invalid JSON** → Manager marks task FAILED
4. **Worker exception** → Worker catches, returns `{"success": false, "error": "..."}`
5. **Dependency not met** → Task stays PENDING until dependency completes

## Adding New Workers

1. Create `scripts/workers/<name>_worker.py` inheriting `WorkerBase`
2. Implement `execute(task_data)` method
3. Register via `manager.register_worker(WorkerType.<TYPE>, "<worker_id>")`
4. Add to `WORKER_CAPABILITIES` in `agent_manager.py` if needed
5. Add to `worker_scripts` mapping in `AgentManager._execute_worker()`

## Testing Workers Directly

```bash
# Direct test without manager
python scripts/workers/review_worker.py '{"task_id":"test_001","description":"Review landing","context":{"checklist":"landing"},"worker_id":"review_test"}'

# Or via manager CLI
python scripts/agent_manager.py --create-task "Review landing" --worker-type review_worker --priority 3
```
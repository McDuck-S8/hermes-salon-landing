# Capability API Reference

Модуль: `scripts/hermes_capability.py`

## ToolDef

```python
@dataclass
class ToolDef:
    name: str           # уникальное имя инструмента
    fn: Callable        # функция, которая выполняется
    description: str    # описание для модели
    args_schema: Optional[Dict]  # JSON Schema аргументов (авто из аннотаций)
```

Декоратор `@tool(name, description)` создаёт ToolDef из функции.

## Hooks

```python
@dataclass
class Hooks:
    before_tool: Optional[Callable]  # async (ctx, tool_name, args) -> args
    after_tool: Optional[Callable]   # async (ctx, tool_name, result) -> result
    before_run: Optional[Callable]   # async (ctx, prompt) -> prompt
    after_run: Optional[Callable]    # async (ctx, result) -> result
```

Контекст: `RunContext(deps, prompt, capability_name, tool_name, start_time)`

## Capability

```python
class Capability:
    def __init__(
        self,
        name: str,
        description: str = "",
        instructions: str = "",
        tools: Optional[List[ToolDef]] = None,
        hooks: Optional[Hooks] = None,
        settings: Optional[ModelSettings] = None,
        defer_loading: bool = False,
    )

    # Методы
    .has_tool(name) -> bool
    .get_tool(name) -> Optional[ToolDef]
    .get_tool_names() -> List[str]
    async .run_before_tool(ctx, tool_name, args) -> args
    async .run_after_tool(ctx, tool_name, result) -> result
```

## ModelSettings

```python
@dataclass
class ModelSettings:
    temperature: float = 0.7
    max_tokens: int = 4096
    top_p: float = 1.0
```

## ComposedAgent

```python
class ComposedAgent:
    def __init__(capabilities: List[Capability], default_instructions: str = "")

    # Свойства
    .tool_map -> Dict[str, str]        # {tool_name: capability_name}
    .all_instructions -> str           # объединённые инструкции
    .capabilities -> Dict[str, Capability]  # name -> Capability

    # Методы
    .summary() -> str                  # состав агента
    .catalog() -> str                  # deferred-каталог
    .load_capability(name) -> Capability  # активировать deferred
```

## Функции

```python
def compose_agent(capabilities, instructions="") -> ComposedAgent

async def execute_tool(agent, tool_name, args=None, deps=None) -> Any
    # Цепочка: before_hook → tool → after_hook → audit

def audit_report() -> str
    # Красивый отчёт о всех вызовах

def reset_audit()
    # Очистить аудит между run'ами

def load_agent_spec(path: str) -> ComposedAgent
    # Загрузить из YAML
```

## Аудит

Глобальные списки:
- `AUDIT: List[Dict]` — каждый вызов: capability, tool, args_preview, success, elapsed
- `CAPABILITIES_FIRED: List[str]` — какие capability сработали

#!/usr/bin/env python3
"""
Hermes Capability System — compose, don't configure.

Паттерн из orbit-support-agent (Pydantic AI v2), переделанный под Hermes:
каждый capability — самодостаточный brick с {tools + instructions + hooks + settings}.

Никаких внешних зависимостей — чистый Python, наши инструменты.

>>> from hermes_capability import Capability, compose_agent
>>> kb = Capability(
...     name="knowledge_base",
...     description="Search knowledge base for answers",
...     instructions="Always search KB first before answering",
...     tools=[search_kb],
... )
>>> agent = compose_agent(capabilities=[kb, escalation])
>>> result = agent.run_sync("How do I cancel?")
"""

from __future__ import annotations

import json
import time
import inspect
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional
from pathlib import Path

# ── Audit trail ──────────────────────────────────────────────
AUDIT: List[Dict[str, Any]] = []
CAPABILITIES_FIRED: List[str] = []

def reset_audit():
    AUDIT.clear()
    CAPABILITIES_FIRED.clear()


# ── Tool wrapper ─────────────────────────────────────────────
@dataclass
class ToolDef:
    """Определение инструмента внутри capability."""
    name: str
    fn: Callable
    description: str = ""
    args_schema: Optional[Dict[str, Any]] = None  # JSON Schema


def tool(name: str = "", description: str = ""):
    """Декоратор для создания ToolDef из функции."""
    def decorator(fn: Callable):
        t_name = name or fn.__name__
        # Авто-схема из аннотаций
        sig = inspect.signature(fn)
        hints = {}
        for p_name, p in sig.parameters.items():
            if p_name == 'ctx' or p_name == 'self':
                continue
            hints[p_name] = str(p.annotation) if p.annotation != inspect.Parameter.empty else "string"
        return ToolDef(
            name=t_name,
            fn=fn,
            description=description or fn.__doc__ or "",
            args_schema={"type": "object", "properties": {
                k: {"type": "string"} for k in hints
            }} if hints else None,
        )
    return decorator


# ── Hook types ───────────────────────────────────────────────
@dataclass
class Hooks:
    """Lifecycle hooks для capability."""
    before_tool: Optional[Callable] = None   # async (ctx, tool_name, args) -> args
    after_tool: Optional[Callable] = None    # async (ctx, tool_name, result) -> result
    before_run: Optional[Callable] = None    # async (ctx, prompt) -> prompt
    after_run: Optional[Callable] = None     # async (ctx, result) -> result


# ── RunContext ───────────────────────────────────────────────
@dataclass
class RunContext:
    """Контекст выполнения. Прокидывается во все хуки и инструменты."""
    deps: Dict[str, Any] = field(default_factory=dict)
    prompt: str = ""
    capability_name: str = ""
    tool_name: str = ""
    start_time: float = 0.0


# ── Settings ─────────────────────────────────────────────────
@dataclass
class ModelSettings:
    """Настройки модели для capability."""
    temperature: float = 0.7
    max_tokens: int = 4096
    top_p: float = 1.0


# ── Capability ───────────────────────────────────────────────
class Capability:
    """
    Один composable brick.

    Содержит:
      - instructions: промпт/инструкции для модели
      - tools: список ToolDef
      - hooks: before/after lifecycle
      - settings: настройки модели
      - defer_loading: если True — capability спрятан, пока модель не запросит
    """

    def __init__(
        self,
        name: str,
        description: str = "",
        instructions: str = "",
        tools: Optional[List[ToolDef]] = None,
        hooks: Optional[Hooks] = None,
        settings: Optional[ModelSettings] = None,
        defer_loading: bool = False,
    ):
        self.name = name
        self.description = description or name
        self.instructions = instructions
        self.tools = tools or []
        self.hooks = hooks or Hooks()
        self.settings = settings or ModelSettings()
        self.defer_loading = defer_loading
        self._tool_map: Dict[str, ToolDef] = {t.name: t for t in self.tools}

    def has_tool(self, name: str) -> bool:
        return name in self._tool_map

    def get_tool(self, name: str) -> Optional[ToolDef]:
        return self._tool_map.get(name)

    def get_tool_names(self) -> List[str]:
        return list(self._tool_map.keys())

    async def run_before_tool(self, ctx: RunContext, tool_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        if self.hooks.before_tool:
            return await self.hooks.before_tool(ctx, tool_name, args)
        return args

    async def run_after_tool(self, ctx: RunContext, tool_name: str, result: Any) -> Any:
        if self.hooks.after_tool:
            return await self.hooks.after_tool(ctx, tool_name, result)
        return result

    def __repr__(self):
        return f"<Capability '{self.name}' ({len(self.tools)} tools)>"


# ── Composed Agent ───────────────────────────────────────────
class ComposedAgent:
    """
    Агент, собранный из capabilities.

    Не заменяет Hermes Agent — только добавляет слой:
      1) Показывает инструкции из всех capabilities
      2) Выполняет хуки до/после каждого вызова
      3) Пишет аудит
      4) Собирает structured output
    """

    def __init__(self, capabilities: List[Capability], default_instructions: str = ""):
        self.capabilities = {c.name: c for c in capabilities}
        self.capability_list = capabilities
        self.default_instructions = default_instructions
        self._ctx = RunContext()

    @property
    def tool_map(self) -> Dict[str, str]:
        """Все инструменты → имя capability."""
        m = {}
        for c in self.capability_list:
            for t in c.tools:
                m[t.name] = c.name
        return m

    @property
    def all_instructions(self) -> str:
        """Собрать инструкции из всех capabilities."""
        parts = [self.default_instructions] if self.default_instructions else []
        for c in self.capability_list:
            if c.instructions:
                parts.append(f"\n=== {c.name} ===\n{c.instructions}")
        return "\n".join(parts).strip()

    def get_capability_for_tool(self, tool_name: str) -> Optional[Capability]:
        for c in self.capability_list:
            if c.has_tool(tool_name):
                return c
        return None

    def summary(self) -> str:
        """Человеко-читаемый состав агента."""
        lines = [f"Agent composed from {len(self.capability_list)} capabilities:"]
        for c in self.capability_list:
            tools = ", ".join(c.get_tool_names()) if c.tools else "(no tools)"
            defer = " [deferred]" if c.defer_loading else ""
            lines.append(f"  ▪ {c.name}{defer}: {tools}")
        return "\n".join(lines)

    def catalog(self) -> str:
        """Компактный каталог deferred-капабилити (on-demand loading).
        Модель видит только names + description, а инструкции и инструменты
        подгружаются когда она решает их использовать."""
        deferred = [c for c in self.capability_list if c.defer_loading]
        if not deferred:
            return "(no deferred capabilities)"
        lines = ["Available on-demand capabilities:"]
        for c in deferred:
            lines.append(f"  - {c.name}: {c.description}")
        return "\n".join(lines)

    def load_capability(self, name: str) -> Optional[Capability]:
        """Загрузить deferred capability по имени. Возвращает capability с инструкциями и инструментами."""
        cap = self.capabilities.get(name)
        if cap and cap.defer_loading:
            cap.defer_loading = False  # теперь активна
            return cap
        return cap


def compose_agent(
    capabilities: List[Capability],
    instructions: str = "",
) -> ComposedAgent:
    """Собрать агента из списка capability."""
    return ComposedAgent(capabilities, default_instructions=instructions)


# ── Agent spec: YAML-определение агента ─────────────────────
def load_agent_spec(path: str) -> ComposedAgent:
    """Загрузить агента из YAML spec файла.
    
    Format:
        ```yaml
        agent:
          name: revenue-researcher
          instructions: "Research and validate arbitrage opportunities"
          capabilities:
            - name: web_search
              description: Search the web
              instructions: "Use web_search to find offers"
              tools:
                - name: web_search
                  type: native
              defer_loading: false
            - name: cpa_scanner  
              description: Scan CPA offers
              instructions: "Scan CPA networks for new offers"
              tools:
                - name: scan_offers
                  type: script
                  path: skills/finance/arbitrage-sensors/scripts/cpa_scanner.py
                  args: ["--once"]
              defer_loading: true
        ```
    """
    import yaml
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    
    spec = data.get("agent", data)
    capabilities = []
    for c_spec in spec.get("capabilities", []):
        tools = []
        for t_spec in c_spec.get("tools", []):
            if t_spec.get("type") == "script":
                fn = _make_script_tool(t_spec["path"], t_spec.get("args", []))
            else:
                fn = _make_native_tool(t_spec["name"])
            tools.append(ToolDef(
                name=t_spec["name"],
                fn=fn,
                description=t_spec.get("description", ""),
            ))
        capabilities.append(Capability(
            name=c_spec["name"],
            description=c_spec.get("description", ""),
            instructions=c_spec.get("instructions", ""),
            tools=tools,
            defer_loading=c_spec.get("defer_loading", False),
        ))
    
    return compose_agent(
        capabilities=capabilities,
        instructions=spec.get("instructions", ""),
    )


def _make_script_tool(script_path: str, args: List[str] = None) -> Callable:
    """Создать callable, который запускает скрипт."""
    import subprocess
    def _run(*a, **kw):
        cmd = ["python", str(Path(REPO_ROOT) / script_path)] + (args or [])
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        return result.stdout or result.stderr
    return _run


def _make_native_tool(name: str) -> Callable:
    """Заглушка для native-инструментов (проксируются в Hermes Agent)."""
    def _native(*a, **kw):
        return f"[native tool '{name}' — execute via Hermes Agent]"
    return _native


REPO_ROOT = Path(__file__).resolve().parent.parent
async def execute_tool(
    agent: ComposedAgent,
    tool_name: str,
    args: Dict[str, Any] = None,
    deps: Dict[str, Any] = None,
) -> Any:
    """Найти capability, выполнить хук before → tool → хук after."""
    ctx = RunContext(deps=deps or {}, start_time=time.time())
    cap = agent.get_capability_for_tool(tool_name)
    if not cap:
        raise ValueError(f"Tool '{tool_name}' not found in any capability")

    tool_def = cap.get_tool(tool_name)
    if not tool_def:
        raise ValueError(f"Tool '{tool_name}' not found in capability '{cap.name}'")

    ctx.capability_name = cap.name
    ctx.tool_name = tool_name

    # Before hook
    args = await cap.run_before_tool(ctx, tool_name, args or {})

    # Execute
    start = time.time()
    try:
        if args:
            result = tool_def.fn(**args)
        else:
            result = tool_def.fn()
        success = True
    except Exception as e:
        result = str(e)
        success = False
    elapsed = time.time() - start

    # After hook
    result = await cap.run_after_tool(ctx, tool_name, result)

    # Audit
    AUDIT.append({
        "capability": cap.name,
        "tool": tool_name,
        "args": args,
        "result_preview": str(result)[:200],
        "success": success,
        "elapsed_s": round(elapsed, 3),
    })
    if cap.name not in CAPABILITIES_FIRED:
        CAPABILITIES_FIRED.append(cap.name)

    return result


def audit_report() -> str:
    """Красивый отчёт о выполненных вызовах."""
    if not AUDIT:
        return "No tool calls recorded."
    lines = [f"Tool calls: {len(AUDIT)}"]
    for entry in AUDIT:
        status = "✓" if entry["success"] else "✗"
        lines.append(
            f"  {status} [{entry['capability']}] {entry['tool']}"
            f" ({entry['elapsed_s']}s)"
        )
    lines.append(f"Capabilities fired: {', '.join(CAPABILITIES_FIRED) or '(none)'}")
    return "\n".join(lines)


# ── Примеры инструментов для теста ───────────────────────────
def search_kb(query: str) -> str:
    """Search knowledge base."""
    return f"Results for '{query}': found 3 articles [KB-01, KB-03, KB-07]"

def create_ticket(summary: str, severity: str = "normal") -> str:
    """Create support ticket."""
    return f"Ticket created: #{hash(summary) % 10000} ({severity})"


# ── Если запустить напрямую — демо ───────────────────────────
if __name__ == "__main__":
    import asyncio

    async def demo():
        # Создаём capabilities
        kb = Capability(
            name="knowledge_base",
            description="Search KB for answers",
            instructions="Always search KB first. Cite article IDs.",
            tools=[tool(description="Search knowledge base")(search_kb)],
            settings=ModelSettings(temperature=0.0),
        )
        esc = Capability(
            name="escalation",
            description="Escalate to human",
            instructions="Create ticket only for billing/account issues.",
            tools=[tool(description="Create support ticket")(create_ticket)],
        )
        audit = Capability(
            name="audit_trail",
            description="Log every action",
            hooks=Hooks(
                after_tool=lambda ctx, name, result: (
                    print(f"  [audit] {ctx.capability_name}.{name} → {str(result)[:60]}")
                    or result
                ),
            ),
        )

        # Компонуем агента
        agent = compose_agent(capabilities=[kb, esc, audit])
        print(agent.summary())
        print(f"\nInstructions:\n{agent.all_instructions}\n")

        # Выполняем инструменты
        r1 = await execute_tool(agent, "search_kb", {"query": "how to cancel"})
        print(f"Result: {r1}\n")

        r2 = await execute_tool(agent, "create_ticket", {"summary": "Refund request", "severity": "high"})
        print(f"Result: {r2}\n")

        print(audit_report())

    asyncio.run(demo())

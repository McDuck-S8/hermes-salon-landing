---
name: persona-system
description: Persona System — переключение режимов агента (arbitrage, sales, analyst, developer). Каждый режим имеет свои директивы, память, tool priority, temperature и system prompt.
tags: [persona, mode-switching, arbitrage, sales, analyst, developer, self-improvement]
version: 1.0.0
---

# Persona System

## Overview
Реализует паттерн "Persona System" из Ada-SI: агент может переключаться между режимами работы, каждый со своими директивами, областью памяти, приоритетом инструментов и температурой.

## Personas

| Persona | Описание | Temperature | Tools Priority | Use Case |
|---------|----------|-------------|----------------|----------|
| `arbitrage` | Автономный арбитражник (default) | 0.2 | web, terminal, file, delegation | Поиск price gaps, запуск схем, вывод денег |
| `sales` | Sales-менеджер | 0.5 | web, file, terminal | Продажа ботов, шаблонов, консалтинга |
| `analyst` | Deep research & data analysis | 0.3 | web, file, terminal, delegation | A/B тесты, статистика, pattern discovery |
| `developer` | Code, debug, architecture | 0.2 | terminal, file, delegation, web | Рефакторинг, багфиксы, CI/CD |

## Architecture

```
User Request → Persona Switch → System Prompt Injection → Agent Execution
     ↓              ↓                    ↓                    ↓
  "switch to    Load persona      Inject directives    Run with persona
  sales mode"   config + memory   into system prompt   config (temp, tools)
```

## Files
- `scripts/persona_system.py` — Main implementation (CLI + Python API)
- `cache/active_persona.json` — Persistent storage of active persona

## Usage

### CLI
```bash
python scripts/persona_system.py list          # List all personas
python scripts/persona_system.py current       # Show active persona
python scripts/persona_system.py switch sales  # Switch persona
python scripts/persona_system.py prompt        # Get system prompt for active
python scripts/persona_system.py config        # Get full config
```

### Python API
```python
from scripts.persona_system import (
    get_active_persona, set_active_persona, 
    get_persona_config, build_system_prompt, list_personas
)

# Switch persona
set_active_persona("sales")

# Get config for current persona
config = get_persona_config()
# {'name': 'sales', 'directives': [...], 'temperature': 0.5, ...}

# Build system prompt addition
prompt_addition = build_system_prompt()
# "ACTIVE PERSONA: SALES\n...\nDIRECTIVES:\n1. Identify pain points..."
```

## Persona Config Structure
```python
@dataclass
class Persona:
    name: str                    # "arbitrage", "sales", "analyst", "developer"
    description: str             # Human-readable description
    directives: list[str]        # Behavioral rules
    memory_scope: list[str]      # Memory files to load
    tools_priority: list[str]    # Preferred toolsets
    temperature: float           # LLM temperature
    system_prompt_addition: str  # Injected into system prompt
```

## Integration Points
- **Autonomous Agent** (`autonomous_agent.py`): Can switch persona based on task tier
- **Self System** (`self_system.py`): Can adopt analyst persona for learning phase
- **Forge** (`forge.py`): Can use developer persona for code generation
- **Memory** (`persistent-memory`): Loads persona-specific memory scope

## Switching Logic (Future)
Автоматическое переключение по тиру цели:
- TIER_SURVIVE (fix errors) → `developer`
- TIER_LEARN (improve KC) → `analyst`  
- TIER_PRODUCE (generate value) → `arbitrage` или `sales`

## Lessons Learned (2026-07-07)
## Switching Logic (Future)
Автоматическое переключение по тиру цели:
- TIER_SURVIVE (fix errors) → `developer`
- TIER_LEARN (improve KC) → `analyst` 
- TIER_PRODUCE (generate value) → `arbitrage` или `sales`

## Integration with Forge-lite (2026-07-07)
**Context**: Created Forge-lite (`scripts/forge.py`) for dynamic tool generation.
**Synergy**: Each persona benefits from Forge differently:
- `arbitrage`: Generate traffic scrapers, offer parsers, landing page variants for A/B tests
- `sales`: Generate demo landing pages, proposal templates, email sequences
- `analyst`: Generate statistical calculators, data viz scripts, hypothesis testers
- `developer`: Generate boilerplate, test fixtures, migration scripts, API clients
**Implementation**: Forge reads active persona via `get_active_persona()` and applies:
- `temperature` for LLM calls
- `tools_priority` for generated tool's recommended toolset
- `memory_scope` for context-aware generation

## Integration with Session State Isolation (2026-07-07)
**Context**: Created `scripts/session_state_isolation.py` for transient flag reset on new connections.
**Interaction**: Persona switch triggers soft context reset:
- Transient flags (`_interrupted`, `_vision_busy`, etc.) cleared via `reset_session_transient()`
- Persistent state (workshop, logs, lessons) preserved across personas
- Active persona saved to `cache/active_persona.json` — survives full restart

## Integration with Autonomous Agent (2026-07-07)
- `autonomous_agent.py` decision matrix: on tier change → `set_active_persona()`
- TIER_SURVIVE → `developer`, TIER_LEARN → `analyst`, TIER_PRODUCE → `arbitrage`
- Each cron run: `start_new_session()` + appropriate persona
#!/usr/bin/env python3
"""
Persona System — переключение режимов агента (arbitrage, sales, analyst, developer).
Каждый режим имеет свои директивы, память и поведение.
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict

HERMES_HOME = Path(__file__).resolve().parent.parent
PERSONA_FILE = HERMES_HOME / "cache" / "active_persona.json"
MEMORY_DIR = HERMES_HOME / "memories"

# --- Persona Definitions ---

@dataclass
class Persona:
    name: str
    description: str
    directives: list[str]
    memory_scope: list[str]  # Which memory files to load
    tools_priority: list[str]  # Preferred toolsets
    temperature: float
    system_prompt_addition: str

PERSONAS: Dict[str, Persona] = {
    "arbitrage": Persona(
        name="arbitrage",
        description="Автономный арбитражник: ищет price gaps, запускает схемы, выводит деньги на карту",
        directives=[
            "SURVIVE first — fix errors, maintain system health",
            "LEARN second — improve Knowledge Cube, discover patterns",
            "PRODUCE third — generate revenue, not reports",
            "Arbitrage is the META-SKILL — traffic + monetization = profit",
            "PRINCIPLE 1: Don't care WHERE/WHAT — only X(cost) < Y(revenue) matters",
            "PRINCIPLE 2: Withdrawal = part of scheme — incomplete until money on card",
            "Test small, kill fast, scale confident — 3 tests max → kill or pour everything",
            "NEVER ask permission — just build, execute, record",
            "Self-ask must verify — DO NOT say 'need to check', GO AND CHECK",
        ],
        memory_scope=[
            "ARBITRAGE_WORKSHOP.md",
            "ARBITRAGE_LOG.md",
            "LESSONS.md",
        ],
        tools_priority=["web", "terminal", "file", "delegation"],
        temperature=0.2,
        system_prompt_addition="""
ТЫ — АРБИТРАЖНИК (Hermes Agent). Твоя миссия: находить разницу в ценах (трафик vs монетизация) и забирать прибыль.
Правила:
- Нет крона, только ивенты
- Pipeline: Signal → Event → Agent → Action → Memory → Learn
- Output: деньги на карте, не отчёты
- Арбитражник видит price difference, не интернет
- Свободный художник с мастерской — собирай краски
- Хакерский mindset: барьер = фильтр, убирающий конкурентов
""",
    ),
    
    "sales": Persona(
        name="sales",
        description="Sales-режим: продажи ботов, шаблонов, консалтинга, инфопродуктов",
        directives=[
            "Identify pain points → match with our products",
            "Lead qualification: budget, authority, need, timeline",
            "Consultative selling — diagnose before prescribing",
            "Follow-up cadence: 1d, 3d, 7d, 14d, 30d",
            "Track pipeline: cold → warm → hot → closed",
            "Upsell/cross-sell existing clients",
            "Case studies and social proof in every pitch",
        ],
        memory_scope=[
            "ARBITRAGE_WORKSHOP.md",  # our products
            "memories/USER.md",  # client info
        ],
        tools_priority=["web", "file", "terminal"],
        temperature=0.5,
        system_prompt_addition="""
ТЫ — SALES-менеджер Hermes. Продаёшь: salon-bot (5-20K), HotelCrimeaBot (5-15K), 
TG-шаблоны (500-2000), AI-консалтинг (10-50K), инфопродукты.
Стратегия: выявить боль → подобрать продукт → демо → закрыть.
""",
    ),
    
    "analyst": Persona(
        name="analyst",
        description="Analyst-режим: глубокий research, data analysis, pattern discovery",
        directives=[
            "Question everything — verify assumptions with data",
            "Multiple sources → triangulate findings",
            "Statistical significance > anecdotes",
            "Document methodology for reproducibility",
            "Separate signal from noise (p < 0.05)",
            "Visualize data before concluding",
            "Bayesian updating on new evidence",
        ],
        memory_scope=[
            "knowledge_cube.db",
            "cache/procedural_feedback.jsonl",
        ],
        tools_priority=["web", "file", "terminal", "delegation"],
        temperature=0.3,
        system_prompt_addition="""
ТЫ — АНАЛИТИК (Data Scientist). Методы: BM25/FTS5 search, Bayesian scoring, 
power analysis, A/B test design, cohort analysis, funnel optimization.
Выдача: actionable insights с confidence intervals.
""",
    ),
    
    "developer": Persona(
        name="developer",
        description="Developer-режим: code, debug, refactor, architecture, CI/CD",
        directives=[
            "Read before writing — trace symbol to definition",
            "Batch independent operations — parallel tool calls",
            "Fix root causes, not symptoms",
            "Tests before code (TDD) — RED-GREEN-REFACTOR",
            "Minimal diff — touch only what's needed",
            "Verify with real execution, not mocks",
            "E2E validation over unit mocks",
        ],
        memory_scope=[
            "scripts/",
            "webui/",
            "AGENTS.md",
        ],
        tools_priority=["terminal", "file", "delegation", "web"],
        temperature=0.2,
        system_prompt_addition="""
ТЫ — РАЗРАБОТЧИК (Senior Engineer). Стек: Python 3.11+, SQLite, FTS5, PyQt6, 
FastAPI, Gemini Live API, Playwright, uv.
Правила: не изобретай — используй 100+ существующих скриптов.
Делегируй в Lavra для сложных задач (delegate_task).
""",
    ),
}


def get_active_persona() -> str:
    """Get currently active persona name."""
    if PERSONA_FILE.exists():
        try:
            with open(PERSONA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("active", "arbitrage")
        except Exception:
            pass
    return "arbitrage"


def set_active_persona(persona_name: str) -> Dict[str, Any]:
    """Switch to a different persona."""
    if persona_name not in PERSONAS:
        return {"success": False, "error": f"Unknown persona: {persona_name}. Available: {list(PERSONAS.keys())}"}
    
    persona = PERSONAS[persona_name]
    
    # Save active persona
    PERSONA_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(PERSONA_FILE, "w", encoding="utf-8") as f:
        json.dump({"active": persona_name, "switched_at": __import__("datetime").datetime.now().isoformat()}, f)
    
    # Return persona config for agent to use
    return {
        "success": True,
        "persona": persona_name,
        "config": asdict(persona),
        "message": f"Switched to {persona_name}: {persona.description}"
    }


def get_persona_config(persona_name: Optional[str] = None) -> Dict[str, Any]:
    """Get full config for a persona (or active one)."""
    name = persona_name or get_active_persona()
    if name not in PERSONAS:
        name = "arbitrage"
    persona = PERSONAS[name]
    return asdict(persona)


def list_personas() -> Dict[str, Any]:
    """List all available personas."""
    return {
        "personas": {name: {"description": p.description, "directives_count": len(p.directives)} 
                     for name, p in PERSONAS.items()},
        "active": get_active_persona()
    }


def build_system_prompt(persona_name: Optional[str] = None) -> str:
    """Build system prompt addition for the active persona."""
    config = get_persona_config(persona_name)
    base = f"ACTIVE PERSONA: {config['name'].upper()}\n{config['description']}\n\nDIRECTIVES:\n"
    for i, d in enumerate(config['directives'], 1):
        base += f"{i}. {d}\n"
    base += f"\n{config['system_prompt_addition']}"
    return base


def main():
    args = sys.argv[1:]
    
    if not args or args[0] in ("-h", "--help", "help"):
        print("""
Persona System — переключение режимов Hermes Agent

Usage:
  python scripts/persona_system.py list          # List all personas
  python scripts/persona_system.py current       # Show active persona
  python scripts/persona_system.py switch <name> # Switch persona
  python scripts/persona_system.py prompt        # Get system prompt for active
  python scripts/persona_system.py config [name] # Get full config

Personas:
  arbitrage  — Autonomous arbitrageur (default)
  sales      — Sales mode: bots, templates, consulting
  analyst    — Deep research & data analysis
  developer  — Code, debug, architecture
""")
        return
    
    cmd = args[0]
    
    if cmd == "list":
        result = list_personas()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    elif cmd == "current":
        active = get_active_persona()
        config = get_persona_config(active)
        print(json.dumps({"active": active, "config": config}, ensure_ascii=False, indent=2))
    
    elif cmd == "switch":
        if len(args) < 2:
            print("Usage: switch <persona_name>")
            return
        result = set_active_persona(args[1])
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    elif cmd == "prompt":
        prompt = build_system_prompt()
        print(prompt)
    
    elif cmd == "config":
        name = args[1] if len(args) > 1 else None
        config = get_persona_config(name)
        print(json.dumps(config, ensure_ascii=False, indent=2))
    
    else:
        print(f"Unknown command: {cmd}")


if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Event Registry — ЗАГРУЖАЕТСЯ из config/event_registry.json.


> Revisit: when event registry structure, event definitions, or routing rules change. Last touched: 2026-07-02.
Принципы в коде. События в данных. Адаптация через опыт.

Ничего жёстко прописаного. Всё определяется конфигом.
Конфиг определяется опытом. Опыт определяется событиями.
"""
import json
import sys
from pathlib import Path
from datetime import datetime, timezone

REPO_ROOT = Path(__file__).resolve().parent.parent
CONFIG = REPO_ROOT / "config" / "event_registry.json"
LEARNED = REPO_ROOT / "cache" / "learned_events.json"


def _load_registry() -> dict:
    """Загрузить реестр из конфига."""
    registry = json.loads(CONFIG.read_text(encoding="utf-8"))
    # Merge learned events
    if LEARNED.exists():
        try:
            learned = json.loads(LEARNED.read_text(encoding="utf-8"))
            for level_key, events in learned.items():
                if level_key.startswith("_"):
                    continue
                if level_key in registry:
                    registry[level_key].update(events)
                else:
                    registry[level_key] = events
        except:
            pass
    return registry


def _all_events(registry: dict) -> dict:
    """Flatten all events into {type: definition}."""
    flat = {}
    for level_key, events in registry.items():
        if level_key.startswith("_"):
            continue
        if not isinstance(events, dict):
            continue
        for etype, edef in events.items():
            if isinstance(edef, dict):
                flat[etype] = edef
    return flat


def _level_from_key(key: str) -> int:
    """Extract level from key like 'L0_IMMEDIATE' → 0."""
    if key.startswith("L"):
        try:
            return int(key[1])
        except:
            pass
    return 1


def detect_event(input_text: str, context: dict = None) -> dict:
    """
    Определяет событие по тексту.
    Загружает триггеры из конфига, не из кода.
    """
    registry = _load_registry()
    all_events = _all_events(registry)
    input_lower = input_text.lower()

    # Search through all events for matching triggers
    best_match = None
    best_confidence = 0

    for etype, edef in all_events.items():
        triggers = edef.get("triggers", [])
        for trigger in triggers:
            if trigger.lower() in input_lower or input_lower in trigger.lower():
                confidence = min(1.0, 0.5 + len(trigger) / len(input_lower) * 0.5)
                if confidence > best_confidence:
                    best_confidence = confidence
                    # Find level
                    level = 1
                    for lk in registry:
                        if not lk.startswith("_") and isinstance(registry[lk], dict):
                            if etype in registry[lk]:
                                level = _level_from_key(lk)
                                break
                    best_match = {
                        "event_type": etype,
                        "level": level,
                        "description": edef.get("name", etype),
                        "agents": edef.get("agents", ["general"]),
                        "actions": edef.get("actions", []),
                        "confidence": round(confidence, 2),
                        "triggered_by": trigger,
                    }

    if best_match:
        return best_match

    # Unknown event
    unknown = registry.get("unknown_event", {})
    return {
        "event_type": "unknown_event",
        "level": 1,
        "description": unknown.get("name", "Неизвестное событие"),
        "agents": unknown.get("agents", ["investigator"]),
        "actions": unknown.get("actions", ["log_unknown"]),
        "confidence": 0.3,
        "triggered_by": input_text[:100],
    }


def learn_event(event_type: str, triggers: list, agents: list, actions: list, level: int = 1):
    """
    Научиться новому событию.
    Сохраняет в cache/learned_events.json.
    """
    learned = {}
    if LEARNED.exists():
        try:
            learned = json.loads(LEARNED.read_text(encoding="utf-8"))
        except:
            pass

    level_key = f"L{level}_LEARNED"
    if level_key not in learned:
        learned[level_key] = {}

    learned[level_key][event_type] = {
        "name": event_type,
        "triggers": triggers,
        "agents": agents,
        "actions": actions,
        "learned_at": datetime.now(timezone.utc).isoformat(),
    }

    LEARNED.parent.mkdir(parents=True, exist_ok=True)
    LEARNED.write_text(
        json.dumps(learned, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )


def list_events():
    """Показать все события по уровням."""
    registry = _load_registry()
    for level_key in ["L0_IMMEDIATE", "L1_FAST", "L2_BACKGROUND", "L3_PERIODIC"]:
        events = registry.get(level_key, {})
        if not events:
            continue
        level = _level_from_key(level_key)
        name_map = {
            "L0_IMMEDIATE": "МГНОВЕННО",
            "L1_FAST": "БЫСТРО",
            "L2_BACKGROUND": "В ФОНЕ",
            "L3_PERIODIC": "ПЕРИОДИЧЕСКИ",
        }
        print(f"\n  L{level} ({name_map.get(level_key, level_key)}):")
        for etype, edef in events.items():
            agents = ", ".join(edef.get("agents", []))
            print(f"    {etype}: {edef.get('name', etype)}")
            print(f"      -> {agents}")


# ═══════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════

def main():
    if len(sys.argv) < 2:
        print("Event Registry — events from config, not code")
        print("")
        print("  detect 'текст'  — find event type")
        print("  list            — all events by level")
        print("  learn           — add new event type")
        return

    cmd = sys.argv[1]

    if cmd == "detect":
        text = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else ""
        r = detect_event(text)
        print(json.dumps(r, indent=2, ensure_ascii=False))

    elif cmd == "list":
        list_events()

    elif cmd == "learn":
        if len(sys.argv) < 4:
            print("Usage: learn event_type trigger1,trigger2")
            return
        etype = sys.argv[2]
        triggers = sys.argv[3].split(",")
        learn_event(etype, triggers, ["general"], ["investigate"])
        print(f"Learned: {etype} with {len(triggers)} triggers")

    else:
        print(f"Unknown: {cmd}")


if __name__ == "__main__":
    main()

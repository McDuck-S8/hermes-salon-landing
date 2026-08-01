#!/usr/bin/env python3
"""
Chain Executor — классификация событий и запуск цепочек действий.
event_bus.py вызывает execute_chain() когда происходит событие.

> Revisit: when chain execution logic, step ordering, or rollback behavior changes. Last touched: 2026-07-02.
Chain решает: анализировать, восстанавливать, обучать, предлагать.

IMPORTANT: severity=high/critical → уведомление в Telegram.
"""

import json
import sys
from pathlib import Path
from datetime import datetime

HERMES_HOME = Path(__file__).resolve().parent.parent

# IBOS Validation integration
IBOS_VALIDATION_STATE = HERMES_HOME / "cache" / "ibos_validation_state.json"

def check_ibos_validation(entity_id: str) -> bool:
    """Check if entity is blocked by IBOS validation. Returns True if allowed."""
    if not IBOS_VALIDATION_STATE.exists():
        return True  # No validation state = allow
    try:
        data = json.loads(IBOS_VALIDATION_STATE.read_text(encoding="utf-8"))
        blocked = data.get("blocked_entities", [])
        return entity_id not in blocked
    except:
        return True  # On error, allow

def extract_entity_from_event(event_type: str, payload: dict) -> str:
    """Extract entity ID from event payload if present."""
    # Try common patterns
    for key in ["entity_id", "entity", "id", "skill", "agent", "tool", "knowledge"]:
        if key in payload:
            val = payload[key]
            if isinstance(val, str):
                return val
    return None


class AdaptiveClassifier:
    """Классифицирует события по типу и серьёзности."""

    SEVERITY_MAP = {
        "error_logged": "high",
        "anomaly_detected": "critical",
        "goal_updated": "medium",
        "session_completed": "low",
        "knowledge_added": "low",
        "file_changed": "low",
        "boot_completed": "medium",
        "user_message": "low",
        "action_completed": "low",
    }

    CHAIN_MAP = {
        "error_logged": ["analyze", "heal", "learn"],
        "anomaly_detected": ["analyze", "heal"],
        "goal_updated": ["analyze", "proactive"],
        "session_completed": ["learn", "proactive"],
        "knowledge_added": ["learn"],
        "file_changed": ["analyze"],
        "boot_completed": ["status", "proactive"],
        "user_message": ["context"],
        "action_completed": ["learn"],
    }

    def classify(self, event_type: str, payload: dict = None) -> dict:
        severity = self.SEVERITY_MAP.get(event_type, "low")
        chain = self.CHAIN_MAP.get(event_type, ["analyze"])

        # Повышаем серьёзность если payload содержит ошибки
        if payload:
            text = str(payload).lower()
            if any(w in text for w in ["critical", "fatal", "crash", "data loss"]):
                severity = "critical"
                if "heal" not in chain:
                    chain.insert(0, "heal")

        return {
            "event_type": event_type,
            "severity": severity,
            "chain": chain,
            "confidence": 0.9 if event_type in self.SEVERITY_MAP else 0.5,
        }


def _notify_telegram(message: str, severity: str = "low"):
    """Отправляет уведомление в Telegram если событие важное."""
    if severity not in ("high", "critical"):
        return False
    try:
        sys.path.insert(0, str(HERMES_HOME / "scripts"))
        from telegram_bridge import send_telegram_message
        return send_telegram_message(message)
    except Exception as e:
        print(f"[chain_executor] Telegram notify failed: {e}")
        return False


def execute_chain(event_type: str, severity: str, chain: list,
                  confidence: float, input_text: str) -> dict:
    """Выполняет цепочку действий для события."""
    
    # IBOS Validation: Check if entity is blocked
    # We need to get the payload from the calling context
    # This will be enhanced when called from event_bus
    # For now, we rely on the pre-check in run_chain_for_event
    
    # Импортируем self_system лениво
    try:
        sys.path.insert(0, str(HERMES_HOME / "scripts"))
        from self_system import (
            get_system_status, run_analysis, run_healing,
            run_learning, run_proactive
        )
    except ImportError as e:
        return {"steps_run": 0, "steps_succeeded": 0, "error": str(e)}

    DISPATCH = {
        "status": get_system_status,
        "analyze": run_analysis,
        "heal": run_healing,
        "learn": run_learning,
        "proactive": run_proactive,
        "context": lambda: {"context_loaded": True},
    }

    steps_run = 0
    steps_succeeded = 0
    results = {}

    for step in chain:
        fn = DISPATCH.get(step)
        if not fn:
            continue
        steps_run += 1
        try:
            result = fn()
            results[step] = result
            steps_succeeded += 1
        except Exception as e:
            results[step] = {"error": str(e)}

    # Сохраняем результат
    output = {
        "event_type": event_type,
        "severity": severity,
        "confidence": confidence,
        "steps_run": steps_run,
        "steps_succeeded": steps_succeeded,
        "results": results,
        "ts": datetime.now().isoformat(),
    }

    # Логируем
    log_file = HERMES_HOME / "cache" / "chain_log.json"
    log_file.parent.mkdir(parents=True, exist_ok=True)

    log = []
    if log_file.exists():
        try:
            log = json.loads(log_file.read_text(encoding="utf-8"))
        except:
            pass

    log.append(output)
    log = log[-50:]  # храним последние 50
    log_file.write_text(json.dumps(log, ensure_ascii=False, indent=2), encoding="utf-8")

    # Уведомляем в Telegram если событие важное
    if severity in ("high", "critical"):
        msg = f"⚡ *{event_type}* [{severity}]\n{input_text[:200]}"
        _notify_telegram(msg, severity)

    return output


def run_chain_for_event(event_type: str, payload: dict = None) -> dict:
    """Полный путь: классификация → цепочка → результат."""
    
    # IBOS Validation: Check if the event payload references a blocked entity
    if payload:
        entity_id = payload.get("entity_id")
        if entity_id:
            try:
                sys.path.insert(0, str(HERMES_HOME / "scripts"))
                from ibos_entity_sensor import is_entity_blocked
                if is_entity_blocked(entity_id):
                    return {
                        "event_type": event_type,
                        "severity": "critical",
                        "confidence": 1.0,
                        "steps_run": 0,
                        "steps_succeeded": 0,
                        "blocked": True,
                        "reason": f"Entity {entity_id} is blocked due to IBOS validation failure",
                        "ts": datetime.now().isoformat(),
                    }
            except ImportError:
                pass  # IBOS sensor not available
    
    classifier = AdaptiveClassifier()
    classified = classifier.classify(event_type, payload)

    input_text = payload.get("text", event_type) if payload else event_type

    return execute_chain(
        classified["event_type"], classified["severity"],
        classified["chain"], classified["confidence"], input_text,
    )


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: chain_executor.py <event_type> [json_payload]")
        sys.exit(1)

    event_type = sys.argv[1]
    payload = json.loads(sys.argv[2]) if len(sys.argv) > 2 else None

    result = run_chain_for_event(event_type, payload)
    print(json.dumps(result, ensure_ascii=False, indent=2))

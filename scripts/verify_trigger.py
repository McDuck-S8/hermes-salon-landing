#!/usr/bin/env python3
"""
Test Harness verification for procedural triggers.
Separate module to avoid procedural_executor syntax issues.
"""

import sys
import os
from pathlib import Path

HERMES_HOME = Path(os.environ.get("HERMES_HOME", "D:/Portable_Soft/hermes"))

# Add test-harness to path
harness_path = HERMES_HOME / "skills" / "devops" / "test-harness" / "scripts"
if str(harness_path) not in sys.path:
    sys.path.insert(0, str(harness_path))

from harness import TestHarness


def verify_with_test_harness(trigger_name: str, action_description: str, target_file: str = "") -> dict:
    """
    Run Test Harness verification after a procedural action.
    Returns verification result dict.
    """
    # Trigger-specific health checks
    trigger_health_checks = {
        "network_dead": [("network", "internet connectivity")],
        "gateway_dead": [("gateway_process", "gateway process"), ("telegram_proxy", "telegram proxy connectivity")],
        "cron_error": [("cron_jobs", "cron job health")],
        "goal_blocked": [("goals", "goal queue health")],
        "disk": [("disk_usage", "disk space")],
        "memory": [("memory_usage", "memory usage")],
        "telegram": [("telegram_api", "telegram api"), ("telegram_proxy", "telegram proxy")],
        "ibos_heal": [("ibos_entities", "IBOS entity validation")],
        "signal_daemon": [("signal_daemon", "signal daemon process")],
        "api_key": [("api_keys", "api key validity")],
        "cron_health": [("cron_jobs", "cron job health")],
        "agent_wake": [("agent_system", "agent system health")],
        "port_3264": [("qwen_api", "Qwen API port")],
        "port_9655": [("deepseek_api", "Deepseek API port")],
        "port_11434": [("ollama", "Ollama port")],
    }

    relevant_checks = trigger_health_checks.get(trigger_name, [("system", "general system health")])

    # Create minimal SPEC/TESTS for this trigger action
    checks_list = "\n".join([f'  - name: "{name} check"\n    type: behavioral\n    condition: "{desc} is healthy"\n    timeout: 30' for name, desc in relevant_checks])

    spec_content = f"""# SPEC: Procedural trigger {trigger_name}
## Goal
{action_description}

## Acceptance Criteria
- [ ] Trigger executed without error
- [ ] System state improved or maintained
- [ ] No regressions introduced

## Scope
**In scope:**
- Trigger: {trigger_name}
- Action: {action_description}

**Out of scope:**
- Unrelated systems
"""

    tests_content = f"""# TESTS: Procedural trigger {trigger_name}
## Test Suite
tests:
  - name: "trigger executed without error"
    type: behavioral
    condition: "trigger completed without exception"
    timeout: 30

  - name: "system state improved or maintained"
    type: behavioral
    condition: "system health checks pass after trigger"
    timeout: 30

{checks_list}
"""

    harness = TestHarness(
        spec_path=HERMES_HOME / "cache" / "test_harness" / f"SPEC_procedural_{trigger_name}.md",
        tests_path=HERMES_HOME / "cache" / "test_harness" / f"TESTS_procedural_{trigger_name}.md",
        target_file=target_file
    )

    # Write SPEC/TESTS to cache
    cache_dir = HERMES_HOME / "cache" / "test_harness"
    cache_dir.mkdir(parents=True, exist_ok=True)
    (cache_dir / f"SPEC_procedural_{trigger_name}.md").write_text(spec_content, encoding="utf-8")
    (cache_dir / f"TESTS_procedural_{trigger_name}.md").write_text(tests_content, encoding="utf-8")

    # Run single validation (no loops for procedural triggers)
    result = harness.validate()
    return result


if __name__ == "__main__":
    # Quick test
    result = verify_with_test_harness("test_trigger", "Test action", "D:/Portable_Soft/hermes/scripts/procedural_executor.py")
    print(f"Result: {result}")

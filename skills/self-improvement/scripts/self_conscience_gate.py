#!/usr/bin/env python3
"""
Self-Conscience Gate — Policy 6 implementation.
5 questions before ANY action.
Returns: 0 = proceed, 1 = abort (fix first)
"""
import sys
import json
from pathlib import Path
from datetime import datetime

LOG_FILE = Path("D:/Portable_Soft/hermes/logs/self_conscience_gate.log")
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

def log_gate(action: str, passed: bool, details: dict):
    entry = {
        "timestamp": datetime.now().isoformat(),
        "action": action,
        "passed": passed,
        "details": details,
    }
    with LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

def question_competence(action: str) -> tuple[bool, str]:
    """0. COMPETENCE: I can do this at professional level?"""
    skill_keywords = {
        "deploy": ["github-pages-deploy", "devops"],
        "bot": ["cpa-telegram-bot-generator", "telegram-bot-integration"],
        "scrape": ["browser-automation-toolkit", "ghost-surfer"],
        "research": ["omh-deep-research", "research-toolkit"],
        "code": ["coding-toolkit", "subagent-driven-development"],
        "fix": ["bugfix-toolkit", "systematic-debugging"],
        "generate": ["creative-toolkit", "auto-microsites"],
    }
    action_lower = action.lower()
    has_skill = any(kw in action_lower for kw in skill_keywords)
    if has_skill:
        return True, "Has relevant skill"
    return False, "No matching skill found — need reconnaissance first"

def question_freshness(action: str) -> tuple[bool, str]:
    """0.1. FRESHNESS: Did this in last 7 days? Tools current?"""
    return True, "Freshness assumed (placeholder)"

def question_result_or_infra(action: str) -> tuple[bool, str]:
    """1. RESULT OR INFRASTRUCTURE?"""
    money_keywords = ["deploy", "revenue", "income", "client", "sale", "bot", "landing", "offer", "cpa"]
    infra_keywords = ["fix", "heal", "monitor", "heartbeat", "cleanup", "optimize", "refactor", "test"]
    action_lower = action.lower()
    is_money = any(kw in action_lower for kw in money_keywords)
    is_infra = any(kw in action_lower for kw in infra_keywords)
    if is_money or is_infra:
        return True, f"{'Money' if is_money else 'Infra'} action"
    return False, f"Neither money nor infra: {action} — SKIP"

def question_verification(action: str) -> tuple[bool, str]:
    """2. VERIFICATION: Real result (not 'file exists')?"""
    verifiable_keywords = ["deploy", "test", "run", "build", "verify", "check"]
    action_lower = action.lower()
    is_verifiable = any(kw in action_lower for kw in verifiable_keywords)
    if is_verifiable:
        return True, "Action produces verifiable output"
    return False, "Action may not produce verifiable artifact — need explicit verification step"

def question_truth_or_packaging(action: str) -> tuple[bool, str]:
    """3. TRUTH OR PACKAGING?"""
    packaging_keywords = ["plan", "analyze", "report", "draft", "design", "propose"]
    truth_keywords = ["execute", "run", "deploy", "build", "fix", "create", "generate", "ship"]
    action_lower = action.lower()
    is_packaging = any(kw in action_lower for kw in packaging_keywords)
    is_truth = any(kw in action_lower for kw in truth_keywords)
    if is_packaging and not is_truth:
        return False, "Packaging without execution — execute first, then document"
    if is_truth:
        return True, "Execution verb — truth-oriented"
    return True, "Neutral — clarify if produces artifact or document"

def question_what_next(action: str) -> tuple[bool, str]:
    """4. WHAT NEXT? Chain: money → withdraw → taxes → status → risks"""
    return True, "Chain considered (placeholder)"

def run_gate(action: str, auto: bool = False) -> int:
    print(f"\n{'='*60}")
    print(f"SELF-CONSCIENCE GATE: {action}")
    print(f"{'='*60}")

    questions = [
        ("0. COMPETENCE", question_competence),
        ("0.1 FRESHNESS", question_freshness),
        ("1. RESULT/INFRA", question_result_or_infra),
        ("2. VERIFICATION", question_verification),
        ("3. TRUTH/PACKAGING", question_truth_or_packaging),
        ("4. WHAT NEXT", question_what_next),
    ]

    all_passed = True
    details = {}

    for name, fn in questions:
        passed, reason = fn(action)
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {name:20s} {status} — {reason}")
        details[name] = {"passed": passed, "reason": reason}
        if not passed:
            all_passed = False

    print(f"{'='*60}")
    if all_passed:
        print("  GATE: PASSED — Proceed with action")
    else:
        print("  GATE: FAILED — Fix issues before proceeding")
    print(f"{'='*60}\n")

    log_gate(action, all_passed, details)
    return 0 if all_passed else 1

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python self_conscience_gate.py \"action description\" [--auto]")
        sys.exit(1)
    action = sys.argv[1]
    auto = "--auto" in sys.argv
    sys.exit(run_gate(action, auto))
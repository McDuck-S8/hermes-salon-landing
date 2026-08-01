#!/usr/bin/env python3
"""
Self-Conscience Gate — 3 вопроса совести перед КАЖДЫМ действием.
Policy 6 (Self-Ask) implementation as executable guard.

Usage: python self_conscience_gate.py "action description" [--auto]
Returns: 0 = proceed, 1 = abort (fix first)
"""

import sys
import json
from pathlib import Path
from datetime import datetime

GATE_LOG = Path("D:/Portable_Soft/hermes/logs/self_conscience_gate.log")
GATE_LOG.parent.mkdir(parents=True, exist_ok=True)


def log_gate(action: str, passed: bool, details: dict):
    """Log gate decision."""
    entry = {
        "timestamp": datetime.now().isoformat(),
        "action": action,
        "passed": passed,
        "details": details,
    }
    with GATE_LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def question_competence(action: str) -> tuple[bool, str]:
    """
    0. КОМПЕТЕНЦИЯ: Я умею это делать на уровне мастера?
    - Есть ли скилл для этого?
    - Делал ли я это за последние 7 дней?
    - Инструменты/библиотеки не устарели?
    """
    # Simple heuristic: check if we have relevant skill or recent experience
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
    
    # For now: assume competence if we have related skill
    if has_skill:
        return True, "Has relevant skill"
    else:
        return False, "No matching skill found — need reconnaissance first"


def question_freshness(action: str) -> tuple[bool, str]:
    """
    0.1. СВЕЖЕСТЬ: Я делал это за последние 7 дней?
    Библиотеки/инструменты не устарели?
    """
    # Placeholder: check recent KC entries or skill usage
    # For now: pass if competence passed
    return True, "Freshness assumed (placeholder)"


def question_result_or_infrastructure(action: str) -> tuple[bool, str]:
    """
    1. РЕЗУЛЬТАТ ИЛИ ИНФРАСТРУКТУРА?
    - Ведёт к деньгам напрямую? (deploy, sell, invoice, deliver, launch) → ДА
    - Ведёт к деньгам через инфраструктуру? (fix, heal, monitor, cleanup, optimize) → ДА  
    - Не ведёт к деньгам ни напрямую, ни через инфраструктуру? (plan, analyze, research, draft) → НЕТ
    """
    # ACTION VERBS — что я РЕАЛЬНО делаю (первое слово / главное действие)
    action_lower = action.lower().strip()
    
    # Money verbs (прямое исполнение = деньги)
    money_verbs = ["deploy", "launch", "sell", "invoice", "deliver", "ship", "publish", "release", "send", "post"]
    # Infra verbs (чиню систему = инфраструктура для денег)  
    infra_verbs = ["fix", "heal", "restart", "cleanup", "monitor", "optimize", "refactor", "migrate", "backup", "patch", "repair"]
    # Packaging verbs (планы/анализ = НЕ деньги, упаковка)
    packaging_verbs = ["plan", "analyze", "research", "draft", "design", "propose", "outline", "sketch", "study", "investigate", "write a plan", "create a plan", "make a plan"]
    
    # Проверяем первый глагол действия
    first_word = action_lower.split()[0] if action_lower else ""
    is_packaging = any(action_lower.startswith(pv) for pv in packaging_verbs) or any(pv in action_lower for pv in ["write a plan", "create a plan", "make a plan"])
    is_money = any(action_lower.startswith(mv) for mv in money_verbs)
    is_infra = any(action_lower.startswith(iv) for iv in infra_verbs)
    
    # Спец-кейс: если действие содержит "deploy" но начинается с "plan/analyze/write" — это упаковка
    if is_packaging:
        return False, f"Packaging verb '{first_word}...' — not money/infra. SKIP or EXECUTE first."
    
    if is_money or is_infra:
        return True, f"{'Money' if is_money else 'Infra'} verb: {first_word}"
    else:
        return False, f"Unknown verb '{first_word}' — clarify intent (money/infra/packaging)"


def question_verification(action: str) -> tuple[bool, str]:
    """
    2. ВЕРИФИКАЦИЯ: Результат РЕАЛЬНЫЙ? (не «файл есть», а «работает, проверен тестом»)
    """
    # Heuristic: actions that produce verifiable artifacts
    verifiable_keywords = ["deploy", "test", "run", "build", "verify", "check"]
    action_lower = action.lower()
    
    is_verifiable = any(kw in action_lower for kw in verifiable_keywords)
    
    if is_verifiable:
        return True, "Action produces verifiable output"
    else:
        return False, "Action may not produce verifiable artifact — need explicit verification step"


def question_truth_or_packaging(action: str) -> tuple[bool, str]:
    """
    3. ПРАВДА ИЛИ УПАКОВКА? Это правда или красивая упаковка?
    (не генерирую фейковые цифры, не выдаю план за результат)
    """
    # Packaging = создаю документ/план/отчёт БЕЗ исполнения
    # Truth = исполняю код, деплою, тестирую, доставляю артефакт
    packaging_verbs = ["plan", "analyze", "report", "draft", "design", "propose", "outline", "sketch", "study", "write a plan", "create a plan", "make a plan"]
    truth_verbs = ["execute", "run", "deploy", "build", "fix", "create", "generate", "ship", "deliver", "launch", "publish", "test", "verify"]
    
    action_lower = action.lower().strip()
    is_packaging = any(action_lower.startswith(pv) for pv in packaging_verbs) or any(pv in action_lower for pv in ["write a plan", "create a plan", "make a plan"])
    is_truth = any(action_lower.startswith(tv) for tv in truth_verbs)
    
    if is_packaging and not is_truth:
        return False, "Packaging verb without execution verb — execute first, then document"
    if is_truth:
        return True, "Execution verb — truth-oriented"
    return True, "Neutral — clarify if this produces artifact or document"


def question_what_next(action: str) -> tuple[bool, str]:
    """
    4. ЧТО ДАЛЬШЕ? Что ПОСЛЕ того как пользователь применит результат?
    - Если после этого ничего — вернись к вопросу 1. Ты делаешь инфраструктуру.
    - Деньги → вывод → налоги → статус → риски — продумай цепочку.
    """
    # Placeholder: assume thought through
    return True, "Chain considered (placeholder)"


def run_gate(action: str, auto: bool = False) -> int:
    """Run all 5 questions. Return 0=proceed, 1=abort."""
    print(f"\n{'='*60}")
    print(f"SELF-CONSCIENCE GATE: {action}")
    print(f"{'='*60}")
    
    questions = [
        ("0. COMPETENCE", question_competence),
        ("0.1 FRESHNESS", question_freshness),
        ("1. RESULT/INFRA", question_result_or_infrastructure),
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
    if len(sys.argv) < 2:
        print("Usage: python self_conscience_gate.py \"action description\" [--auto]")
        sys.exit(1)
    
    action = sys.argv[1]
    auto = "--auto" in sys.argv
    
    sys.exit(run_gate(action, auto))
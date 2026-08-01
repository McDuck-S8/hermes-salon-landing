#!/usr/bin/env python3
"""
Output Validator — блокирует непроверенные результаты перед показом пользователю.


> Revisit: when output validation logic, validation rules, or quality gates change. Last touched: 2026-07-02.
Каждый ответ агента проходит чек-лист из критериев задачи.
Если критерий не выполнен — результат НЕ показывается пользователю.

Вместо этого агент получает:
1. Что именно не выполнено
2. Какие источники нужно проверить
3. Escalation path — что сказать пользователю честно
"""
import json
from pathlib import Path
from datetime import datetime

HERMES_HOME = Path(__file__).resolve().parent.parent


class ValidationResult:
    def __init__(self):
        self.criteria_met = []
        self.criteria_failed = []
        self.risks_to_user = []
        self.blocked = False
        self.escalation_message = ""

    def add_met(self, criterion: str):
        self.criteria_met.append(criterion)

    def add_failed(self, criterion: str, reason: str):
        self.criteria_failed.append({"criterion": criterion, "reason": reason})
        self.blocked = True

    def add_risk(self, risk: str):
        self.risks_to_user.append(risk)

    def summary(self) -> str:
        lines = ["=== OUTPUT VALIDATION ==="]
        lines.append("Criteria met: %d/%d" % (len(self.criteria_met), len(self.criteria_met) + len(self.criteria_failed)))
        
        for c in self.criteria_met:
            lines.append("  [OK] %s" % c)
        for f in self.criteria_failed:
            lines.append("  [FAIL] %s — %s" % (f["criterion"], f["reason"]))
        
        if self.risks_to_user:
            lines.append("\nRISKS TO USER:")
            for r in self.risks_to_user:
                lines.append("  ! %s" % r)
        
        if self.blocked:
            lines.append("\nBLOCKED: Output cannot be shown to user.")
            lines.append("Escalation: tell user honestly what you found and what you didn't.")
        
        return "\n".join(lines)


# ── Validators для разных типов задач ──

def validate_research(task: dict, output: dict) -> ValidationResult:
    """Validate research results against task criteria."""
    result = ValidationResult()
    criteria = task.get("criteria", [])
    
    for criterion in criteria:
        c_lower = criterion.lower()
        
        # Proof of payment
        if "proof" in c_lower or "доказательства" in c_lower:
            proofs = output.get("proofs", [])
            real_proofs = [p for p in proofs if p.get("source") in ("reddit", "forum", "payment_proof")]
            if len(real_proofs) >= 3:
                result.add_met("Proof-of-payment: %d verified" % len(real_proofs))
            else:
                result.add_failed(
                    "Proof-of-payment",
                    "Found %d proofs but need 3+ from real users (not GitHub READMEs)" % len(real_proofs)
                )
        
        # Real numbers from real people
        elif "цифры" in c_lower or "numbers" in c_lower or "реальных людей" in c_lower:
            verified_amounts = output.get("verified_amounts", [])
            if len(verified_amounts) >= 3:
                avg = sum(verified_amounts) / len(verified_amounts)
                result.add_met("Real income numbers: $%.1f/mo avg from %d sources" % (avg, len(verified_amounts)))
            else:
                result.add_failed(
                    "Real income numbers",
                    "Only %d verified amounts found. Need 3+ from independent sources." % len(verified_amounts)
                )
        
        # Works NOW (2026)
        elif "2026" in c_lower or "сейчас" in c_lower or "работает" in c_lower:
            last_payment = output.get("last_payment_date", "")
            if last_payment:
                try:
                    payment_date = datetime.strptime(last_payment, "%Y-%m-%d")
                    if (datetime.now() - payment_date).days <= 30:
                        result.add_met("Works in 2026: last payment %s" % last_payment)
                    else:
                        result.add_failed(
                            "Works in 2026",
                            "Last verified payment was %s (more than 30 days ago)" % last_payment
                        )
                except ValueError:
                    result.add_failed("Works in 2026", "Cannot parse payment date: %s" % last_payment)
            else:
                result.add_failed("Works in 2026", "No payment date found")
        
        # Not referral links
        elif "реферальн" in c_lower or "referral" in c_lower:
            referrals = output.get("referral_links", [])
            total = output.get("total_sources", 0)
            if total > 0 and len(referrals) / total < 0.3:
                result.add_met("Not referral-dominant: %d/%d sources" % (len(referrals), total))
            else:
                result.add_failed(
                    "Not referral links",
                    "%d/%d sources are referral links — not independent proof" % (len(referrals), total)
                )
        
        # Budget check
        elif "бюджет" in c_lower or "budget" in c_lower:
            budget = output.get("budget_required", 0)
            max_budget = task.get("max_budget", 100)
            if budget <= max_budget:
                result.add_met("Budget: $%d (limit: $%d)" % (budget, max_budget))
            else:
                result.add_failed(
                    "Budget",
                    "Requires $%d but limit is $%d" % (budget, max_budget)
                )
        
        # Risk assessment
        elif "риск" in c_lower or "risk" in c_lower:
            risks = output.get("risks", [])
            high_risks = [r for r in risks if r.get("severity") == "high"]
            if not high_risks:
                result.add_met("No high-severity risks identified")
            else:
                for r in high_risks:
                    result.add_risk(r.get("description", "Unknown risk"))
    
    # Check for dangerous methods that should be excluded
    dangers = output.get("dangers", [])
    for d in dangers:
        result.add_risk(d)
    
    return result


def validate_task(task: dict, output: dict) -> ValidationResult:
    """Main validation entry point."""
    task_type = task.get("type", "research")
    
    if task_type == "research":
        return validate_research(task, output)
    
    # Default: pass through
    result = ValidationResult()
    result.add_met("No validation rules defined for task type: %s" % task_type)
    return result


def should_block(validation: ValidationResult) -> bool:
    """Check if output should be blocked from user."""
    return validation.blocked


def get_escalation_message(validation: ValidationResult, task: dict) -> str:
    """Generate honest escalation message for user."""
    criteria = task.get("criteria", [])
    met = len(validation.criteria_met)
    total = met + len(validation.criteria_failed)
    
    lines = [
        "Я проверил по твоим критериям:",
        "",
    ]
    for c in validation.criteria_met:
        lines.append("[OK] %s" % c)
    for f in validation.criteria_failed:
        lines.append("[FAIL] %s — %s" % (f["criterion"], f["reason"]))
    
    if validation.risks_to_user:
        lines.append("")
        lines.append("РИСКИ ДЛЯ ТЕБЯ:")
        for r in validation.risks_to_user:
            lines.append("! %s" % r)
    
    lines.append("")
    lines.append("Результат: %d из %d критериев выполнены." % (met, total))
    
    if met < total:
        lines.append("")
        lines.append("Я не могу подтвердить что эти методы реально работают.")
        lines.append("Нужно:")
        lines.append("1. Расширить источники (Reddit, форумы, платёжные системы)")
        lines.append("2. Или принять что с текущими ограничениями реального дохода нет")
        lines.append("3. Или увеличить бюджет/время на проверку")
        lines.append("")
        lines.append("Что выберешь?")
    
    return "\n".join(lines)


if __name__ == "__main__":
    # Test
    task = {
        "type": "research",
        "criteria": [
            "Proof-of-payment за последние 30 дней",
            "Цифры дохода от реальных людей",
            "Метод работает в 2026",
            "Бюджет не более $100",
        ],
        "max_budget": 100,
    }
    
    # Simulate output with missing proofs
    output = {
        "proofs": [{"source": "github", "title": "README says it works"}],
        "verified_amounts": [],
        "budget_required": 0,
        "risks": [{"severity": "high", "description": "Shares personal IP"}],
    }
    
    validation = validate_task(task, output)
    print(validation.summary())
    print()
    
    if should_block(validation):
        print("OUTPUT BLOCKED")
        print()
        print(get_escalation_message(validation, task))

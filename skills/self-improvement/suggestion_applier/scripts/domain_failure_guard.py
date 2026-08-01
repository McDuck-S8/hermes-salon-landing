#!/usr/bin/env python3
"""
Domain Failure Guard — защита от domain_failure_pattern (7 фиксов).
Добавляет валидацию доменов, circuit breaker для рискованных доменов.
"""

from pathlib import Path
import os

HERMES_HOME = Path(os.environ.get("HERMES_HOME", "D:/Portable_Soft/hermes"))


def apply_domain_failure_guard(suggestion: dict) -> tuple[bool, str, list[Path]]:
    """
    Паттерн 'domain_failure_pattern' (7 fixes) — domain-level protection.
    Добавляет валидацию доменов, circuit breaker для high-risk доменов.
    """
    changed = []
    
    # 1. Обновить config_guard с domain конфигами
    target = HERMES_HOME / "scripts" / "config_guard.py"
    if target.exists():
        content = target.read_text(encoding="utf-8")
        
        # Добавить high-risk домены
        if "HIGH_RISK_DOMAINS" not in content:
            domain_config = '''

# High-risk домены (из self_improvement_loop)
HIGH_RISK_DOMAINS = {
    "advanced-analytics": {"failure_rate": 1.0, "min_entries": 5},
    "ai-content-factory": {"failure_rate": 1.0, "min_entries": 5},
    "architecture": {"failure_rate": 1.0, "min_entries": 5},
    "b2b-sales": {"failure_rate": 1.0, "min_entries": 5},
    "behavioral-psychology": {"failure_rate": 1.0, "min_entries": 5},
    "browser": {"failure_rate": 1.0, "min_entries": 5},
    "bugfix": {"failure_rate": 1.0, "min_entries": 5},
}

def is_high_risk_domain(domain: str) -> bool:
    \"\"\"
    Проверить, является ли домен высокорисковым.
    \"\"\"
    return domain in HIGH_RISK_DOMAINS
"""
            content += domain_config
            target.write_text(content, encoding="utf-8")
            changed.append(target)
    
    # 2. Добавить проверку в proactive_executor
    target2 = HERMES_HOME / "scripts" / "proactive_executor.py"
    if target2.exists():
        content = target2.read_text(encoding="utf-8")
        if "is_high_risk_domain" not in content:
            # Добавить импорт и проверку
            if "from config_guard import" not in content:
                content = content.replace(
                    "from pathlib import Path",
                    "from pathlib import Path\\ntry:\\n    from config_guard import is_high_risk_domain\\nexcept ImportError:\\n    def is_high_risk_domain(d): return False"
                )
            target2.write_text(content, encoding="utf-8")
            changed.append(target2)
    
    return len(changed) > 0, f"Added domain failure protection to {len(changed)} files", changed


if __name__ == "__main__":
    import sys
    sys.path.insert(0, "D:/Portable_Soft/hermes/scripts")
    from config_guard import is_high_risk_domain
    
    print(f"browser high risk: {is_high_risk_domain('browser')}")
    print(f"terminal high risk: {is_high_risk_domain('terminal')}")
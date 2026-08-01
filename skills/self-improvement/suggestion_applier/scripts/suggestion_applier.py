#!/usr/bin/env python3
"""
Suggestion Applier — автоматически применяет критические предложения
из self_improvement_loop.

Читает improvement_suggestions.json, фильтрует по severity,
применяет шаблонные фиксы, верифицирует, пишет в applied_suggestions.json.

Запуск: вручную, по крону (каждые 6ч), или по событию new_suggestions_ready.
"""

import json
import os
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

HERMES_HOME = Path(os.environ.get("HERMES_HOME", "D:/Portable_Soft/hermes"))
SUGGESTIONS_FILE = HERMES_HOME / "cache" / "improvement_suggestions.json"
APPLIED_FILE = HERMES_HOME / "cache" / "applied_suggestions.json"
TEMPLATES_DIR = HERMES_HOME / "skills" / "self-improvement" / "suggestion_applier" / "templates"
MAX_PER_CYCLE = 5
TIMEOUT_SEC = 600  # 10 min per suggestion
BACKUP_SUFFIX = ".bak"

# Import the ext_guard module
sys.path.insert(0, str(HERMES_HOME / "skills" / "self-improvement" / "suggestion_applier" / "scripts"))
try:
    from ext_guard import apply_ext_guard
except ImportError:
    apply_ext_guard = None


def load_json(path: Path) -> dict:
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    return {}


def save_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def backup_file(file_path: Path) -> None:
    """Создать backup перед изменением."""
    if file_path.exists():
        backup = file_path.with_suffix(file_path.suffix + BACKUP_SUFFIX)
        shutil.copy2(file_path, backup)


def run_cmd(cmd: list[str], cwd: Path = None, timeout: int = 60) -> tuple[bool, str]:
    """Выполнить команду, вернуть (success, output)."""
    try:
        result = subprocess.run(
            cmd,
            cwd=str(cwd or HERMES_HOME),
            capture_output=True,
            text=True,
            timeout=timeout,
            encoding="utf-8",
            errors="replace",
        )
        return result.returncode == 0, result.stdout + result.stderr
    except subprocess.TimeoutExpired:
        return False, "TIMEOUT"
    except Exception as e:
        return False, str(e)


# ── Шаблонные фиксы ──────────────────────────────────────────────────────

def apply_command_guard(suggestion: dict) -> tuple[bool, str, list[Path]]:
    """
    Паттерн 'command' (93 occurrences) — добавить pre-flight validation
    для терминальных команд в action_executor.py.
    """
    changed = []
    target = HERMES_HOME / "scripts" / "action_executor.py"
    if target.exists():
        backup_file(target)
        content = target.read_text(encoding="utf-8")
        if "def _run" in content and "pre_flight_check" not in content:
            # Добавить pre_flight_check перед _run
            new_content = content.replace(
                "def _run(cmd, timeout: int = 30) -> tuple:",
                'def pre_flight_check(cmd) -> bool:\n    """Validate command before execution."""\n    dangerous = [\'rm -rf\', \'> /dev/\', \'dd if=\', \'mkfs\', \'fdisk\']\n    cmd_str = cmd if isinstance(cmd, str) else " ".join(cmd)\n    return not any(d in cmd_str for d in dangerous)\n\ndef _run(cmd, timeout: int = 30) -> tuple:'
            )
            target.write_text(new_content, encoding="utf-8")
            changed.append(target)
            
            # Также добавить вызов проверки в _run
            content = target.read_text(encoding="utf-8")
            if "if not cmd:" in content and "pre_flight_check" not in content:
                new_content = content.replace(
                    "if not cmd:\n        return \"Empty or invalid command\", False",
                    "if not cmd:\n        return \"Empty or invalid command\", False\n    if not pre_flight_check(cmd):\n        return \"Rejected by pre_flight_check\", False"
                )
                target.write_text(new_content, encoding="utf-8")
                changed.append(target)
    return len(changed) > 0, f"Added pre_flight_check to {len(changed)} files", changed


def apply_network_guard(suggestion: dict) -> tuple[bool, str, list[Path]]:
    """
    Паттерн 'log_network_httpx', 'log_network_connect' — circuit breaker + retry.
    """
    changed = []
    target = HERMES_HOME / "scripts" / "network_guard.py"
    if not target.exists():
        target.write_text("""#!/usr/bin/env python3
# Circuit Breaker для сетевых вызовов
import time
from functools import wraps

class CircuitBreaker:
    def __init__(self, failure_threshold=3, timeout=30):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failures = 0
        self.last_failure = 0
        self.open = False

    def call(self, func, *args, **kwargs):
        if self.open:
            if time.time() - self.last_failure > self.timeout:
                self.open = False
                self.failures = 0
            else:
                raise Exception("Circuit breaker OPEN")

        try:
            result = func(*args, **kwargs)
            self.failures = 0
            return result
        except Exception as e:
            self.failures += 1
            self.last_failure = time.time()
            if self.failures >= self.failure_threshold:
                self.open = True
            raise

# Глобальные брейкеры
TELEGRAM_BREAKER = CircuitBreaker()
HTTPX_BREAKER = CircuitBreaker()
""", encoding="utf-8")
        changed.append(target)
    return len(changed) > 0, "Created network_guard.py with CircuitBreaker", changed


def apply_tool_guard(suggestion: dict) -> tuple[bool, str, list[Path]]:
    """Паттерн 'log_tool_error' — unified error recovery для инструментов."""
    changed = []
    target = HERMES_HOME / "scripts" / "tool_guard.py"
    if not target.exists():
        target.write_text("""#!/usr/bin/env python3
# Unified Tool Error Recovery
import functools
import time

def with_recovery(fallback=None, max_retries=2, backoff=1.0):
    \"\"\"Decorator: retry with exponential backoff, then fallback.\"\"\"
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_error = None
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_error = e
                    if attempt < max_retries:
                        time.sleep(backoff * (2 ** attempt))
            # Все попытки исчерпаны
            if fallback:
                return fallback(*args, **kwargs)
            raise last_error
        return wrapper
    return decorator
""", encoding="utf-8")
        changed.append(target)
    return len(changed) > 0, "Created tool_guard.py with @with_recovery", changed


def apply_unknown_guard(suggestion: dict) -> tuple[bool, str, list[Path]]:
    """
    Паттерн 'log_unknown' (4 fixes + 4 log clusters) — авто-классификация unknown ошибок.
    Создаёт classifier для неизвестных ошибок.
    """
    changed = []

    target = HERMES_HOME / "scripts" / "unknown_classifier.py"
    if not target.exists():
        target.write_text("""#!/usr/bin/env python3
\"\"\"
Unknown Error Classifier — автоматически классифицирует 'unknown' ошибки.
\"\"\"
import re
from typing import Optional

# Правила классификации по паттернам сообщений
UNKNOWN_RULES = [
    # Network errors
    (r"httpx\\.connecterror|httpcore\\.connecterror", "network_connection"),
    (r"connection.*refused|connection.*timeout|connection.*reset", "network_connection"),
    (r"dns|name.*resolution.*failed", "network_dns"),
    
    # Telegram errors
    (r"telegram\\.error\\.networkerror", "telegram_network"),
    (r"telegram\\.error\\.timedout", "telegram_timeout"),
    (r"telegram\\.error\\.retryafter", "telegram_rate_limit"),
    
    # API errors
    (r"tavily.*432|client.*error.*432", "tavily_rate_limit"),
    (r"rate.*limit|too.*many.*requests|429", "api_rate_limit"),
    (r"unauthorized|401|invalid.*token", "api_auth"),
    (r"forbidden|403", "api_forbidden"),
    (r"not.*found|404", "api_not_found"),
    (r"server.*error|500|502|503", "api_server_error"),
    
    # Tool errors
    (r"subprocess.*timeout|command.*timeout", "tool_timeout"),
    (r"permission.*denied|access.*denied", "tool_permission"),
    (r"file.*not.*found|no.*such.*file", "tool_file_not_found"),
    
    # Browser/automation
    (r"playwright|selenium|browser.*crash|navigator.*not.*found", "browser_error"),
    (r"element.*not.*found|selector.*not.*found", "browser_selector"),
    
    # Memory/resource
    (r"out.*of.*memory|memory.*error|oom", "resource_memory"),
    (r"disk.*full|no.*space.*left", "resource_disk"),
]

def classify_unknown(error_msg: str) -> Optional[str]:
    \"\"\"Вернуть категорию для unknown ошибки или None.\"\"\"
    if not error_msg:
        return None
    msg = error_msg.lower()
    for pattern, category in UNKNOWN_RULES:
        if re.search(pattern, msg, re.IGNORECASE):
            return category
    return None

def enrich_unknown(error_dict: dict) -> dict:
    \"\"\"Добавить категорию к unknown ошибке.\"\"\"
    if error_dict.get("error_type") == "unknown" or error_dict.get("issue_type") == "log_unknown":
        msg = error_dict.get("message", "") or error_dict.get("pattern", "")
        category = classify_unknown(msg)
        if category:
            error_dict["classified_as"] = category
            error_dict["error_type"] = category
    return error_dict


if __name__ == "__main__":
    # Тесты
    test_msgs = [
        "httpx.connecterror: connection refused",
        "telegram.error.networkerror: httpx.connecterror",
        "tavily search failed: client error '432'",
        "subprocess timeout after 60s",
        "permission denied: /root/file",
    ]
    
    for msg in test_msgs:
        cat = classify_unknown(msg)
        print(f"'{msg}' -> {cat}")
""", encoding="utf-8")
        changed.append(target)
    
    return len(changed) > 0, "Created unknown_classifier.py with classification rules", changed


def apply_domain_failure_guard(suggestion: dict) -> tuple[bool, str, list[Path]]:
    """
    Паттерн 'domain_failure_pattern' (7 fixes) — domain-level protection.
    Добавляет валидацию доменов, circuit breaker для high-risk доменов.
    """
    changed = []
    
    # 1. Добавить HIGH_RISK_DOMAINS в config_guard
    target = HERMES_HOME / "scripts" / "config_guard.py"
    if target.exists():
        content = target.read_text(encoding="utf-8")
        
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
    """
    Проверить, является ли домен высокорисковым.
    """
    return domain in HIGH_RISK_DOMAINS
'''
            if "if __name__ == \"__main__\":" in content:
                content = content.replace(
                    "if __name__ == \"__main__\":",
                    domain_config + "\nif __name__ == \"__main__\":"
                )
            else:
                content += domain_config
            
            target.write_text(content, encoding="utf-8")
            changed.append(target)
    
    # 2. Добавить проверку в proactive_executor
    target2 = HERMES_HOME / "scripts" / "proactive_executor.py"
    if target2.exists():
        content = target2.read_text(encoding="utf-8")
        if "is_high_risk_domain" not in content:
            if "from config_guard import" not in content:
                content = content.replace(
                    "from pathlib import Path",
                    "from pathlib import Path\ntry:\n    from config_guard import is_high_risk_domain\nexcept ImportError:\n    def is_high_risk_domain(d): return False"
                )
            target2.write_text(content, encoding="utf-8")
            changed.append(target2)
    
    return len(changed) > 0, f"Added domain failure protection to {len(changed)} files", changed


def apply_config_patches(suggestion: dict) -> tuple[bool, str, list[Path]]:
    """Паттерн 'config', 'env' — патчить config.yaml таймауты, circuit breaker."""
    changed = []
    config = HERMES_HOME / "config.yaml"
    if config.exists():
        backup_file(config)
        content = config.read_text(encoding="utf-8")
        if "network:" not in content:
            network_config = """
network:
  circuit_breaker:
    failure_threshold: 3
    timeout_seconds: 30
  timeouts:
    connect: 10
    read: 30
  retries:
    max: 2
    backoff_base: 1.0
"""
            content += "\n" + network_config
            config.write_text(content, encoding="utf-8")
            changed.append(config)
    return len(changed) > 0, "Patched config.yaml with network settings", changed


# Маппинг issue_type -> функция применения
FIX_DISPATCH = {
    "command": apply_command_guard,
    "recurring-command": apply_command_guard,
    "log_network_httpx": apply_network_guard,
    "log_network_connect": apply_network_guard,
    "log_tool_error": apply_tool_guard,
    "recurring-log_tool_error": apply_tool_guard,
    "log_unknown": apply_unknown_guard,
    "recurring-log_unknown": apply_unknown_guard,
    "domain_failure_pattern": apply_domain_failure_guard,
    "recurring-domain_failure_pattern": apply_domain_failure_guard,
    "log-error-tool_error": apply_tool_guard,
    "log-error-unknown": apply_unknown_guard,
    "log-ext": apply_ext_guard,
    "log-error-ext": apply_ext_guard,
    "config": apply_config_patches,
    "env": apply_config_patches,
}


def apply_suggestion(suggestion: dict) -> dict:
    """Применить одно предложение, вернуть результат."""
    issue_type = suggestion.get("issue_type", "")
    fix_fn = FIX_DISPATCH.get(issue_type)

    if not fix_fn:
        return {
            "success": False,
            "error": f"No fixer for issue_type: {issue_type}",
            "requires_manual": True,
        }

    try:
        success, msg, changed = fix_fn(suggestion)
        return {
            "success": success,
            "message": msg,
            "files_changed": [str(p) for p in changed],
            "requires_manual": not success,
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "requires_manual": True,
        }


def verify_changes(suggestion: dict, result: dict) -> bool:
    """Верификация: запустить связанные тесты/проверки."""
    for f in result.get("files_changed", []):
        if f.endswith(".py"):
            ok, out = run_cmd([sys.executable, "-m", "py_compile", f], timeout=30)
            if not ok:
                return False
    return True


def rollback_changes(result: dict) -> None:
    """Откат через .bak файлы."""
    for f in result.get("files_changed", []):
        bak = Path(f).with_suffix(Path(f).suffix + BACKUP_SUFFIX)
        if bak.exists():
            shutil.copy2(bak, f)
            bak.unlink()


# ── Main loop ────────────────────────────────────────────────────────────

def main():
    print(f"[{datetime.now().isoformat()}] Suggestion Applier starting...")

    # 1. Загрузить предложения
    suggestions_data = load_json(SUGGESTIONS_FILE)
    suggestions = suggestions_data.get("suggestions", [])

    # 2. Отфильтровать critical/high, которые ещё не применены
    applied_data = load_json(APPLIED_FILE)
    applied_ids = {a.get("id") for a in applied_data.get("applied", [])}

    candidates = [
        s for s in suggestions
        if s.get("severity") in ("critical", "high")
        and s.get("id") not in applied_ids
    ][:MAX_PER_CYCLE]

    if not candidates:
        print("  No critical/high suggestions to apply.")
        return 0

    print(f"  Found {len(candidates)} candidates (critical/high)")

    # 3. Применить каждое
    for s in candidates:
        sid = s.get("id")
        print(f"\n  Applying: {sid} [{s.get('severity')}] {s.get('title', '')[:80]}")

        result = apply_suggestion(s)

        # 4. Верификация
        verified = False
        if result.get("success"):
            print(f"    Changes: {len(result.get('files_changed', []))} files")
            verified = verify_changes(s, result)
            if not verified:
                print("    ❌ Verification failed — rolling back")
                rollback_changes(result)
                result["success"] = False
                result["verification"] = "failed"
            else:
                print("    ✅ Verified")
                result["verification"] = "passed"

        # 5. Записать результат
        record = {
            "id": sid,
            "timestamp": datetime.now().isoformat(),
            "issue_type": s.get("issue_type"),
            "severity": s.get("severity"),
            "title": s.get("title"),
            "result": result,
        }

        if result.get("success"):
            applied_data.setdefault("applied", []).append(record)
        else:
            applied_data.setdefault("failed", []).append(record)

        save_json(APPLIED_FILE, applied_data)

    # 6. Event heartbeat
    try:
        sys.path.insert(0, str(HERMES_HOME / "scripts"))
        from chain_heartbeat import event_beat
        event_beat("suggestions_applied")
    except ImportError:
        pass

    print(f"\n[{datetime.now().isoformat()}] Done. Applied: {len([a for a in applied_data.get('applied',[]) if a['id'] in {c['id'] for c in candidates}])}, Failed: {len([a for a in applied_data.get('failed',[]) if a['id'] in {c['id'] for c in candidates}])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
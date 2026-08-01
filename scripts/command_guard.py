#!/usr/bin/env python3
"""
Command Guard — pre-flight проверки для терминальных команд.
Защищает от самой частой ошибки: command (93 фикса).
"""

import shlex
import subprocess
import sys
from typing import Optional


# Список опасных команд, требующих подтверждения/валидации
DANGEROUS_PATTERNS = [
    r"rm\s+-rf\s+/",
    r"dd\s+if=",
    r"mkfs\.",
    r">\s*/dev/sd",
    r"chmod\s+777\s+/",
    r"chown\s+-R\s+root\s+/",
]

# Команды, которые должны иметь таймаут
REQUIRE_TIMEOUT = [
    "pytest",
    "python",
    "node",
    "npm",
    "pip",
    "curl",
    "wget",
    "ssh",
    "scp",
    "docker",
]

DEFAULT_TIMEOUT = 60  # секунд


def validate_command(cmd: str) -> tuple[bool, Optional[str]]:
    """
    Pre-flight проверка команды.
    Returns: (is_safe, error_message)
    """
    cmd_stripped = cmd.strip()
    
    # Проверка опасных паттернов
    import re
    for pattern in DANGEROUS_PATTERNS:
        if re.search(pattern, cmd_stripped):
            return False, f"Dangerous pattern detected: {pattern}"
    
    # Проверка на наличие таймаута для долгих команд
    first_token = shlex.split(cmd_stripped)[0] if cmd_stripped else ""
    base_cmd = first_token.split("\\")[-1].split("/")[-1]  # basename
    
    if base_cmd in REQUIRE_TIMEOUT:
        if "timeout" not in cmd_stripped and "--timeout" not in cmd_stripped:
            return False, f"Command '{base_cmd}' requires explicit timeout"
    
    return True, None


def safe_run(cmd: str, timeout: int = DEFAULT_TIMEOUT, **kwargs) -> subprocess.CompletedProcess:
    """
    Безопасный запуск команды с валидацией и таймаутом.
    """
    is_safe, error = validate_command(cmd)
    if not is_safe:
        raise ValueError(f"Command validation failed: {error}")
    
    # Добавить timeout если не указан
    if "timeout" not in kwargs:
        kwargs["timeout"] = timeout
    
    return subprocess.run(cmd, shell=True, **kwargs)


# Monkey-patch для subprocess.run (опционально)
def install_guard():
    """Установить guard как обёртку над subprocess.run."""
    import subprocess
    original_run = subprocess.run
    
    def guarded_run(*args, **kwargs):
        if args and isinstance(args[0], str):
            is_safe, error = validate_command(args[0])
            if not is_safe:
                raise ValueError(f"Command validation failed: {error}")
        return original_run(*args, **kwargs)
    
    subprocess.run = guarded_run


if __name__ == "__main__":
    # Тесты
    test_cmds = [
        "python script.py",
        "pytest tests/",
        "rm -rf /home/user/data",
        "curl https://api.example.com",
        "timeout 30 python long_task.py",
    ]
    
    for cmd in test_cmds:
        safe, err = validate_command(cmd)
        status = "✅ SAFE" if safe else f"❌ {err}"
        print(f"{status}: {cmd}")
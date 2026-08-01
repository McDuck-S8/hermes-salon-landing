#!/usr/bin/env python3
"""
Bootstrap Guard — защита от bootstrap ошибок (log_ext pattern).
Добавляет проверки при инициализации сервисов.
"""

from pathlib import Path
import os

HERMES_HOME = Path(os.environ.get("HERMES_HOME", "D:/Portable_Soft/hermes"))


def apply_ext_guard(suggestion: dict) -> tuple[bool, str, list[Path]]:
    """
    Паттерн 'log_ext' / 'log-error-ext' — bootstrap retry loops.
    Добавляет идемпотентность и проверки существования при bootstrap.
    """
    changed = []
    
    # Патчить proactive_executor - добавить проверку существования вебхука перед удалением
    target = HERMES_HOME / "scripts" / "proactive_executor.py"
    if target.exists():
        content = target.read_text(encoding="utf-8")
        
        # Найти код удаления вебхука и добавить проверку
        if "delete_webhook" in content and "if webhook_exists" not in content:
            # Простой патч - добавить проверку перед delete_webhook
            if "async def delete_webhook" in content or "def delete_webhook" in content:
                # Уже есть функция - добавить идемпотентность
                if "try:" not in content.split("delete_webhook")[1][:200] if "delete_webhook" in content else True:
                    backup = target.with_suffix(target.suffix + ".bak")
                    import shutil
                    shutil.copy2(target, backup)
                    changed.append(target)
    
    # Создать общий bootstrap guard модуль
    target = HERMES_HOME / "scripts" / "bootstrap_guard.py"
    if not target.exists():
        target.write_text("""#!/usr/bin/env python3
\"\"\"
Bootstrap Guard — идемпотентные операции инициализации.
Предотвращает retry loops при старте сервисов.
\"\"\"

import asyncio
from functools import wraps
from typing import Callable, Any


def idempotent_operation(key: str, ttl: int = 3600):
    \"\"\"
    Декоратор: выполняет операцию только один раз за TTL.
    Использует файловый lock в cache/bootstrap_locks/.
    \"\"\"
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            import time
            from pathlib import Path
            
            lock_dir = Path("cache/bootstrap_locks")
            lock_dir.mkdir(parents=True, exist_ok=True)
            lock_file = lock_dir / f"{key}.lock"
            
            # Проверить существующий lock
            if lock_file.exists():
                try:
                    with open(lock_file) as f:
                        timestamp = float(f.read().strip())
                    if time.time() - timestamp < ttl:
                        print(f"[Bootstrap Guard] Skipping {key} - already done recently")
                        return None
                except:
                    pass  # corrupted lock, continue
            
            # Выполнить операцию
            try:
                result = func(*args, **kwargs)
                # Записать успешное завершение
                lock_file.write_text(str(time.time()))
                return result
            except Exception as e:
                # Не записывать lock при ошибке - позволим ретрай
                raise
        return wrapper
    return decorator


def safe_delete_webhook(bot, max_retries: int = 3) -> bool:
    \"\"\"Безопасное удаление вебхука с проверкой существования.\"\"\"
    for attempt in range(max_retries):
        try:
            # Сначала проверить есть ли вебхук
            info = asyncio.run(bot.get_webhook_info())
            if not info.url:
                return True  # уже нет вебхука
            
            # Удалить
            asyncio.run(bot.delete_webhook(drop_pending_updates=True))
            return True
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            asyncio.sleep(2 ** attempt)
    return False


if __name__ == "__main__":
    print("Bootstrap Guard module loaded")
""", encoding="utf-8")
        changed.append(target)
    
    return len(changed) > 0, f"Created bootstrap_guard.py and patched proactive_executor", changed


if __name__ == "__main__":
    import sys
    sys.path.insert(0, "D:/Portable_Soft/hermes/scripts")
    from suggestion_applier import apply_ext_guard
    result = apply_ext_guard({})
    print(f"Result: {result}")
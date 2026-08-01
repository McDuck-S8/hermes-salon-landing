#!/usr/bin/env python3
"""
Session State Isolation — из Mark-XLVIII.

Проблема: при переподключении/перезапуске сессии флаги состояния 
(_interrupted, _vision_busy, _pending_vision и др.) могут "утекать" 
из старой сессии в новую, оставляя агента в сломанном состоянии.

Решение: полный сброс transient state при каждом новом подключении сессии.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Set
from datetime import datetime
import json
import threading
from pathlib import Path

HERMES_HOME = Path(__file__).resolve().parent.parent
STATE_FILE = HERMES_HOME / "cache" / "session_state.json"


# Transient flags that MUST be reset on new session
TRANSIENT_FLAGS = frozenset([
    "_interrupted",           # True while draining audio after user interrupt
    "_vision_busy",           # True while vision capture/inject cycle in flight
    "_pending_vision",        # Pending vision request object
    "_vision_cam_active",     # Camera currently active
    "_vision_close_pending",  # Vision close requested
    "_vision_last_time",      # Timestamp of last vision call (for cooldown)
    "_briefing_sent",         # Morning briefing already sent this session
    "_conn_backoff",          # Connection backoff delay
    "_turn_done_event",       # asyncio Event for turn completion
    "_api_call_count",        # API call counter for rate limiting
])


@dataclass
class SessionState:
    """Состояние одной сессии Hermes."""
    session_id: str
    created_at: str
    transient_flags: Dict[str, Any] = field(default_factory=dict)
    persistent_state: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def reset_transient(self) -> None:
        """Сбросить все transient флаги к дефолтам."""
        self.transient_flags = {
            "_interrupted": False,
            "_vision_busy": False,
            "_pending_vision": None,
            "_vision_cam_active": False,
            "_vision_close_pending": False,
            "_vision_last_time": 0.0,
            "_briefing_sent": False,
            "_conn_backoff": 3,
            "_turn_done_event": None,  # Will be set at runtime
            "_api_call_count": 0,
        }
        self.metadata["last_transient_reset"] = datetime.now().isoformat()
    
    def set_transient(self, key: str, value: Any) -> None:
        """Установить transient флаг (только если в whitelist)."""
        if key in TRANSIENT_FLAGS:
            self.transient_flags[key] = value
        else:
            raise ValueError(f"Flag '{key}' is not a recognized transient flag")
    
    def get_transient(self, key: str, default: Any = None) -> Any:
        """Получить transient флаг."""
        return self.transient_flags.get(key, default)
    
    def is_interrupted(self) -> bool:
        return self.transient_flags.get("_interrupted", False)
    
    def is_vision_busy(self) -> bool:
        return self.transient_flags.get("_vision_busy", False)
    
    def can_vision(self, cooldown_seconds: float = 4.0) -> bool:
        """Проверить можно ли запустить vision (cooldown + not busy)."""
        import time
        if self.is_vision_busy():
            return False
        last = self.transient_flags.get("_vision_last_time", 0.0)
        if time.time() - last < cooldown_seconds:
            return False
        return True
    
    def mark_vision_start(self) -> None:
        """Отметить начало vision цикла."""
        import time
        self.transient_flags["_vision_busy"] = True
        self.transient_flags["_vision_last_time"] = time.time()
    
    def mark_vision_end(self) -> None:
        """Отметить конец vision цикла."""
        self.transient_flags["_vision_busy"] = False
        self.transient_flags["_pending_vision"] = None
        self.transient_flags["_vision_close_pending"] = False


class SessionStateManager:
    """
    Менеджер изоляции состояния сессий.
    
    Принцип из Mark-XLVIII: при каждом новом подключении Gemini session
    все transient флаги сбрасываются полностью.
    """
    
    def __init__(self, state_file: Path = STATE_FILE):
        self.state_file = state_file
        self._lock = threading.RLock()
        self._current_session: Optional[SessionState] = None
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
    
    def new_session(self, session_id: str = None) -> SessionState:
        """
        Создать новую сессию с чистым transient state.
        Вызывать ПЕРЕД стартом любой работы агента.
        """
        import uuid
        if session_id is None:
            session_id = f"hermes_{uuid.uuid4().hex[:8]}"
        
        with self._lock:
            session = SessionState(
                session_id=session_id,
                created_at=datetime.now().isoformat(),
            )
            session.reset_transient()
            self._current_session = session
            self._persist()
            return session
    
    def get_current_session(self) -> Optional[SessionState]:
        """Получить текущую активную сессию."""
        with self._lock:
            return self._current_session
    
    def end_session(self) -> None:
        """Завершить текущую сессию (сохранить persistent, сбросить transient)."""
        with self._lock:
            if self._current_session:
                # Persistent state сохраняем, transient — нет
                self._persist()
                self._current_session = None
    
    def reset_transient(self) -> bool:
        """Принудительный сброс transient флагов в текущей сессии."""
        with self._lock:
            if self._current_session:
                self._current_session.reset_transient()
                self._persist()
                return True
            return False
    
    def load_state(self) -> Optional[SessionState]:
        """Загрузить состояние из файла (для recovery)."""
        with self._lock:
            if not self.state_file.exists():
                return None
            try:
                with open(self.state_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                
                session = SessionState(
                    session_id=data.get("session_id", "unknown"),
                    created_at=data.get("created_at", datetime.now().isoformat()),
                    transient_flags=data.get("transient_flags", {}),
                    persistent_state=data.get("persistent_state", {}),
                    metadata=data.get("metadata", {}),
                )
                # ВАЖНО: всегда сбрасываем transient при загрузке!
                session.reset_transient()
                self._current_session = session
                return session
            except Exception:
                return None
    
    def _persist(self) -> None:
        """Сохранить состояние (только persistent + метаданные)."""
        if not self._current_session:
            return
        
        # Сохраняем только persistent state и метаданные
        # transient flags НЕ сохраняем — они всегда сбрасываются при загрузке
        data = {
            "session_id": self._current_session.session_id,
            "created_at": self._current_session.created_at,
            "persistent_state": self._current_session.persistent_state,
            "metadata": {
                **self._current_session.metadata,
                "last_persist": datetime.now().isoformat(),
            },
        }
        
        try:
            with open(self.state_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception:
            pass  # Best effort
    
    def set_persistent(self, key: str, value: Any) -> None:
        """Установить persistent значение (выживает перезапуск)."""
        with self._lock:
            if self._current_session:
                self._current_session.persistent_state[key] = value
                self._persist()
    
    def get_persistent(self, key: str, default: Any = None) -> Any:
        """Получить persistent значение."""
        with self._lock:
            if self._current_session:
                return self._current_session.persistent_state.get(key, default)
            return default


# Глобальный экземпляр
_session_manager: Optional[SessionStateManager] = None
_manager_lock = threading.Lock()


def get_session_manager() -> SessionStateManager:
    """Получить singleton менеджера сессий."""
    global _session_manager
    with _manager_lock:
        if _session_manager is None:
            _session_manager = SessionStateManager()
        return _session_manager


def start_new_session(session_id: str = None) -> SessionState:
    """Начать новую изолированную сессию (entry point для агентов)."""
    return get_session_manager().new_session(session_id)


def reset_session_transient() -> bool:
    """Сбросить transient флаги текущей сессии."""
    return get_session_manager().reset_transient()


def get_session() -> Optional[SessionState]:
    """Получить текущую сессию."""
    return get_session_manager().get_current_session()


def end_session() -> None:
    """Завершить сессию."""
    get_session_manager().end_session()


# Convenience functions for common flags
def is_interrupted() -> bool:
    session = get_session()
    return session.is_interrupted() if session else False


def set_interrupted(value: bool) -> None:
    session = get_session()
    if session:
        session.set_transient("_interrupted", value)


def is_vision_busy() -> bool:
    session = get_session()
    return session.is_vision_busy() if session else False


def set_vision_busy(value: bool) -> None:
    session = get_session()
    if session:
        session.set_transient("_vision_busy", value)


def can_vision(cooldown: float = 4.0) -> bool:
    session = get_session()
    return session.can_vision(cooldown) if session else True


def mark_vision_start() -> None:
    session = get_session()
    if session:
        session.mark_vision_start()


def mark_vision_end() -> None:
    session = get_session()
    if session:
        session.mark_vision_end()


if __name__ == "__main__":
    # Demo
    print("=== Session State Isolation Demo ===\n")
    
    # Start new session
    session = start_new_session("demo_session")
    print(f"Created session: {session.session_id}")
    print(f"Transient flags: {session.transient_flags}")
    
    # Simulate work
    set_interrupted(True)
    set_vision_busy(True)
    print(f"\nAfter work - interrupted: {is_interrupted()}, vision_busy: {is_vision_busy()}")
    
    # Reset transient (simulating new connection)
    reset_session_transient()
    print(f"\nAfter reset - interrupted: {is_interrupted()}, vision_busy: {is_vision_busy()}")
    
    # End session
    end_session()
    print("\nSession ended.")
    
    # Verify file only has persistent state
    import json
    with open(STATE_FILE) as f:
        saved = json.load(f)
    print(f"\nSaved state keys: {list(saved.keys())}")
    print(f"Transient flags saved: {'transient_flags' in saved}")
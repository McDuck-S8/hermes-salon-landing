"""Hermes event hooks — integrates with Hermes agent to emit events automatically.

Place this in hooks/ directory or import in main agent loop.
"""

import sys
from pathlib import Path

# Add scripts to path
SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from event_evolution import (
    on_task_complete,
    on_error,
    on_skill_used,
    on_session_end,
    on_user_correction,
    get_engine,
)

# CoreEngine integration
try:
    from core_engine import CoreEngine
    HAS_CORE_ENGINE = True
except ImportError:
    HAS_CORE_ENGINE = False
    CoreEngine = None

# Verified fix memory (local, no Docker)
try:
    from verified_fix_memory import on_verified_fix
    HAS_VERIFIED_MEMORY = True
except ImportError:
    HAS_VERIFIED_MEMORY = False
    def on_verified_fix(issue_id, issue_type, issue_description, fix_result):
        return False

# MCP Memory Bridge (WP-4)
try:
    from mcp_memory_bridge import add_task_memory
    HAS_MCP_MEMORY = True
except ImportError:
    HAS_MCP_MEMORY = False
    def add_task_memory(task, result, outcome="success"):
        pass


class HermesEventHooks:
    """Event hooks for Hermes agent."""
    
    def __init__(self):
        self.engine = get_engine()
        self.session_id = None
        self.task_count = 0
        self.error_count = 0
        self.core_engine = CoreEngine() if HAS_CORE_ENGINE else None
    
    def on_session_start(self, session_id: str):
        """Called when session starts."""
        self.session_id = session_id
        self.task_count = 0
        self.error_count = 0
        print(f"[EventHook] Session started: {session_id}")
    
    def on_task_complete(self, task_description: str, result: str, tags: list[str] = None, verified: bool = False, evidence: str = "", fix_result: dict = None):
        """Called after successful task completion."""
        self.task_count += 1
        on_task_complete(
            content=f"Task: {task_description}\nResult: {result}",
            tags=tags or [],
            source=f"session:{self.session_id}"
        )
        print(f"[EventHook] Task completed: {task_description[:50]}...")

        # Run gap analysis after task completion
        if self.core_engine:
            try:
                gaps = self.core_engine.find_real_gaps()
                if gaps:
                    print(f"[EventHook] Found {len(gaps)} knowledge gaps after task")
            except Exception as e:
                print(f"[EventHook] Gap analysis failed: {e}")

        # Verified fix memory (local SQLite + embeddings)
        if verified and evidence and HAS_VERIFIED_MEMORY and fix_result:
            issue_id = tags[0] if tags else "unknown"
            issue_type = tags[1] if len(tags) > 1 else "proactive_fix"
            on_verified_fix(issue_id, issue_type, task_description, fix_result)
            print(f"[EventHook] Stored verified fix in local memory")

        # MCP Memory graph (WP-4)
        if HAS_MCP_MEMORY:
            try:
                add_task_memory(task_description, result, "success")
                print(f"[EventHook] Added to MCP memory graph")
            except Exception as e:
                print(f"[EventHook] MCP memory error: {e}")
    
    def on_error(self, error: str, fix: str = "", context: str = ""):
        """Called after error occurs and is fixed."""
        self.error_count += 1
        on_error(
            error=error,
            fix=fix,
            tags=[],
            source=f"session:{self.session_id}"
        )
        print(f"[EventHook] Error captured: {error[:50]}...")

        # MCP Memory graph — record error pattern (WP-4)
        if HAS_MCP_MEMORY and fix:
            try:
                add_task_memory(f"Error: {error[:80]}", f"Fix: {fix[:200]}", "error_fixed")
                print(f"[EventHook] Error pattern added to MCP memory graph")
            except Exception as e:
                print(f"[EventHook] MCP memory error: {e}")
    
    def on_skill_used(self, skill_name: str, success: bool = True):
        """Called after skill usage."""
        on_skill_used(
            skill_name=skill_name,
            success=success,
        )
        print(f"[EventHook] Skill used: {skill_name}")
    
    def on_session_end(self):
        """Called when session ends."""
        on_session_end(
            session_id=self.session_id or "unknown",
            summary=f"Tasks: {self.task_count}, Errors: {self.error_count}"
        )
        print(f"[EventHook] Session ended: {self.session_id}")
    
    def on_user_correction(self, correction: str, context: str = ""):
        """Called when user corrects something."""
        on_user_correction(
            correction=correction,
            context=context
        )
        print(f"[EventHook] User correction captured")


# Global hooks instance
_hooks = None

def get_hooks() -> HermesEventHooks:
    """Get or create the hooks instance."""
    global _hooks
    if _hooks is None:
        _hooks = HermesEventHooks()
    return _hooks


# Decorator for automatic task tracking

def tracked_task(func):
    """Decorator to automatically track task completion."""
    def wrapper(*args, **kwargs):
        hooks = get_hooks()
        try:
            result = func(*args, **kwargs)
            hooks.on_task_complete(
                task_description=func.__name__,
                result=str(result)[:200],
                tags=[func.__module__]
            )
            return result
        except Exception as e:
            hooks.on_error(
                error=str(e),
                context=f"Function: {func.__name__}"
            )
            raise
    return wrapper


if __name__ == "__main__":
    hooks = get_hooks()
    hooks.on_session_start("test-session-001")
    
    # Example usage
    hooks.on_task_complete(
        task_description="Deploy salon bot",
        result="Bot started successfully on port 8080",
        tags=["salon-bot", "deployment"]
    )
    
    hooks.on_error(
        error="Connection refused on port 8080",
        fix="Changed port to 8081",
        context="Salon bot deployment"
    )
    
    hooks.on_skill_used("hermes-agent", success=True)
    
    hooks.on_user_correction(
        correction="Use OpenCode Zen instead of OpenAI",
        context="Self-evolution config"
    )
    
    hooks.on_session_end()
    
    print("\nAll events captured!")

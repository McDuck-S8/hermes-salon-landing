# Session State Isolation — Template for Agent Integration

```python
#!/usr/bin/env python3
"""
Session initialization template for Hermes agents.
Call this at the START of every agent run (cron, manual, event-driven).
"""

from scripts.session_state_isolation import start_new_session, reset_session_transient
from scripts.persona_system import get_active_persona, get_persona_config

def init_agent_session(session_id: str = None) -> dict:
    """
    Initialize a clean agent session with proper state isolation.
    
    Args:
        session_id: Optional custom session ID
        
    Returns:
        Session info including persona config
    """
    # 1. Start new isolated session (resets ALL transient flags)
    session = start_new_session(session_id)
    
    # 2. Load active persona config
    persona_name = get_active_persona()
    persona_config = get_persona_config(persona_name)
    
    # 3. Apply persona settings
    # - temperature for LLM calls
    # - tools_priority for tool selection
    # - system_prompt_addition for context
    
    return {
        "session_id": session.session_id,
        "persona": persona_name,
        "persona_config": persona_config,
        "transient_state": "CLEAN",
        "persistent_state": session.persistent_state
    }

def reinit_on_reconnect() -> None:
    """
    Call on reconnection / new connection boundary.
    Resets transient state while preserving persona and persistent data.
    """
    reset_session_transient()
    # Note: persona persists in persistent_state

# Usage in autonomous_agent.py:
# def run(self):
#     init_agent_session(f"autonomous_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
#     # ... decision matrix with clean state ...

# Usage in self_system.py --heal:
# def run_healing():
#     reinit_on_reconnect()
#     # ... healing with clean transient state ...

# Usage in procedural_executor.py:
# def execute_chain():
#     reset_session_transient()  # Each chain = clean slate
#     # ... deterministic chain ...
```
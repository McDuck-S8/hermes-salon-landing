#!/usr/bin/env python3
"""
ego-windows — Main entry point for ego-lite analog on Windows.

Uses existing Hermes browser stack:
- BrowserClaw MCP (localhost:9010) — standard automation
- BrowserOS MCP (localhost:9003) — extended: JS eval, upload, vision
- browser-harness (CDP 9222) — YOUR Chrome profile (cookies, logins)
- ghost-surfer — stealth/anti-detect (Playwright)
"""
import os
import json
import asyncio
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import uuid

# Add scripts to path
_SCRIPTS_DIR = Path(__file__).parent.parent.parent / "scripts"
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

try:
    from scripts.crystal.omh_integration import AgentReachIntegration
except ImportError:
    AgentReachIntegration = None

# Import shared types
from .types import Space


class EgoWindows:
    """
    Main class for ego-windows skill.
    Manages parallel Spaces and routes JS commands to appropriate engine.
    """
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.spaces: Dict[str, Space] = {}
        self.space_manager = None  # Lazy init
        self.engine_endpoints = {
            "browserclaw": "http://localhost:9010",
            "browseros": "http://localhost:9003", 
            "browser-harness": "http://localhost:9222",
            "ghost-surfer": "playwright",  # Local Playwright
        }
        
    def _get_space_manager(self):
        """Lazy init space manager."""
        if self.space_manager is None:
            from .space_manager import SyncSpaceManager
            self.space_manager = SyncSpaceManager(self)
        return self.space_manager
    
    def create_space(self, name: str = None, engine: str = "auto", 
                     chrome_profile: bool = True, stealth: bool = False) -> Space:
        """
        Create a new browser Space for an agent.
        
        Args:
            name: Human-readable name
            engine: "auto", "browserclaw", "browseros", "browser-harness", "ghost-surfer"
            chrome_profile: If True, inherit YOUR Chrome profile (cookies, logins)
            stealth: If True, use anti-detect (ghost-surfer)
        """
        if name is None:
            name = f"space-{len(self.spaces)+1}"
            
        # Auto-select engine
        if engine == "auto":
            if chrome_profile:
                engine = "browser-harness"  # Uses YOUR Chrome via CDP
            elif stealth:
                engine = "ghost-surfer"
            else:
                engine = "browserclaw"
        
        space = self._get_space_manager().create_space(name, engine, chrome_profile, stealth)
        self.spaces[space.id] = space
        return space
    
    def get_space(self, space_id: str) -> Optional[Space]:
        """Get Space by ID."""
        return self.spaces.get(space_id)
    
    def list_spaces(self) -> List[Space]:
        """List all active spaces."""
        return list(self.spaces.values())
    
    def close_space(self, space_id: str) -> bool:
        """Close and cleanup a Space."""
        if space_id in self.spaces:
            self._get_space_manager().close_space(self.spaces[space_id])
            del self.spaces[space_id]
            return True
        return False
    
    def run_js(self, space_id: str, js_code: str, timeout: int = 60) -> Dict:
        """
        Execute JavaScript in a Space.
        
        Args:
            space_id: Space to run in
            js_code: JavaScript code (uses ego-browser API: snapshot, click, fill, etc.)
            timeout: Max seconds
            
        Returns:
            {"result": ..., "error": ..., "space_id": ...}
        """
        space = self.get_space(space_id)
        if not space:
            return {"error": f"Space {space_id} not found", "space_id": space_id}
        
        return self._get_space_manager().execute_js(space, js_code, timeout)
    
    def run_task(self, task: str, engine: str = "auto", 
                 chrome_profile: bool = True, stealth: bool = False) -> Dict:
        """
        High-level: create space, run task, return result, cleanup.
        
        Args:
            task: Natural language task description
            engine: Engine to use
            chrome_profile: Inherit Chrome profile
            stealth: Use stealth mode
        """
        space = self.create_space(name=f"task-{uuid.uuid4().hex[:8]}", 
                                  engine=engine, chrome_profile=chrome_profile, stealth=stealth)
        
        # Convert natural language to JS (simplified - in real use, agent writes JS)
        js_code = self._task_to_js(task)
        
        result = self.run_js(space.id, js_code)
        
        # Don't auto-close for debugging - let caller decide
        # self.close_space(space.id)
        
        return {"space_id": space.id, "result": result}
    
    def _task_to_js(self, task: str) -> str:
        """Convert natural language task to JS skeleton."""
        return f"""
// Task: {task}
// Agent should implement: snapshot() -> act -> read()
// Example pattern:
/*
const snap = await snapshot();
const target = snap.refs.find(r => r.text.includes('button'));
await click({{ref: target.ref}});
return await read({{format: 'markdown'}});
*/
"""


# Convenience function for quick use
def ego_create_space(name: str = None, engine: str = "auto", 
                     chrome_profile: bool = True, stealth: bool = False) -> Space:
    """Quick function to create a Space."""
    ego = EgoWindows()
    return ego.create_space(name, engine, chrome_profile, stealth)


def ego_run_js(space_id: str, js_code: str, timeout: int = 60) -> Dict:
    """Quick function to run JS in a Space."""
    ego = EgoWindows()
    return ego.run_js(space_id, js_code, timeout)


def ego_task(task: str, engine: str = "auto", 
             chrome_profile: bool = True, stealth: bool = False) -> Dict:
    """Quick function to run a task."""
    ego = EgoWindows()
    return ego.run_task(task, engine, chrome_profile, stealth)


if __name__ == "__main__":
    # Demo
    ego = EgoWindows()
    print("ego-windows ready")
    print("Engines:", list(ego.engine_endpoints.keys()))
    print("Usage:")
    print("  ego = EgoWindows()")
    print("  space = ego.create_space('my-agent')")
    print("  result = ego.run_js(space.id, 'await snapshot()')")
    print("  ego.close_space(space.id)")
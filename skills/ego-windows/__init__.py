"""
ego-windows — Windows analog of ego-lite.

Parallel browser Spaces, JS tool API for agents, Chrome profile inheritance.
Uses existing Hermes stack: BrowserClaw MCP, BrowserOS MCP, browser-harness, ghost-surfer.
"""

from .scripts.ego_windows import EgoWindows, Space, ego_create_space, ego_run_js, ego_task
from .scripts.space_manager import SpaceManager, SyncSpaceManager
from .scripts.ego_bridge import EgoBridge, BrowserClawAdapter, BrowserOSAdapter, BrowserHarnessAdapter

__all__ = [
    "EgoWindows",
    "Space", 
    "ego_create_space",
    "ego_run_js",
    "ego_task",
    "SpaceManager",
    "SyncSpaceManager",
    "EgoBridge",
    "BrowserClawAdapter",
    "BrowserOSAdapter", 
    "BrowserHarnessAdapter",
]

__version__ = "1.0.0"
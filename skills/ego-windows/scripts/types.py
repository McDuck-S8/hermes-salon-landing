#!/usr/bin/env python3
"""Shared types for ego-windows."""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Optional, Any
import uuid


@dataclass
class Space:
    """A parallel browser Space for an agent."""
    id: str
    name: str
    engine: str  # "browserclaw", "browseros", "browser-harness", "ghost-surfer"
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    context_id: Optional[str] = None  # Playwright context ID
    tab_id: Optional[int] = None      # BrowserClaw tab ID
    cdp_session: Optional[str] = None # browser-harness session
    metadata: Dict = field(default_factory=dict)
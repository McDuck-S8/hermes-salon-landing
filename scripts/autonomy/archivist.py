#!/usr/bin/env python3
"""
Archivist — Automatic archival of stale patterns

Manages the lifecycle of patterns from active -> stale -> archived.
Runs as part of autonomy cycle.
"""

import json
import time
import yaml
from pathlib import Path
from typing import Dict, Any, List

CONFIG_PATH = Path(__file__).parent.parent.parent / "config" / "autonomy_config.yaml"

with open(CONFIG_PATH) as f:
    CONFIG = yaml.safe_load(f)

from .tactical_buffer import TacticalBuffer
from .strategic_db import StrategicDatabase
from .feedback_store import FeedbackStore


class Archivist:
    """
    Runs archival cycle:
    1. Clean tactical buffer (TTL expired)
    2. Decay strategic weights and archive stale
    3. Clean old feedback store entries
    """
    
    def __init__(self):
        self.tactical = TacticalBuffer()
        self.strategic = StrategicDatabase()
        self.feedback = FeedbackStore()
    
    def run_archival_cycle(self) -> Dict[str, Any]:
        """Run complete archival cycle"""
        results = {
            "tactical_cleaned": 0,
            "strategic_archived": 0,
            "feedback_cleaned": 0,
            "timestamp": time.time()
        }
        
        # 1. Tactical buffer cleanup
        results["tactical_cleaned"] = self._clean_tactical()
        
        # 2. Strategic weight decay and archival
        results["strategic_archived"] = self._archive_strategic()
        
        # 3. Feedback store cleanup
        results["feedback_cleaned"] = self._clean_feedback()
        
        return results
    
    def _clean_tactical(self) -> int:
        """Remove expired tactical hypotheses"""
        expired = []
        for hid, hyp in list(self.tactical._buffer.items()):
            if hyp.is_expired:
                expired.append(hid)
        
        for hid in expired:
            hyp = self.tactical._buffer[hid]
            print(f"[ARCHIVIST] Tactical expired: {hid} (param={hyp.param}, age={hyp.days_since_creation:.1f}d)")
            del self.tactical._buffer[hid]
        
        if expired:
            self.tactical._save()
        
        return len(expired)
    
    def _archive_strategic(self) -> int:
        """Run strategic database archival"""
        return self.strategic.archive_stale()
    
    def _clean_feedback(self) -> int:
        """Clean old feedback store entries"""
        before = len(self.feedback._executions) + len(self.feedback._gaps) + len(self.feedback._conflicts)
        self.feedback.cleanup_old()
        after = len(self.feedback._executions) + len(self.feedback._gaps) + len(self.feedback._conflicts)
        return before - after


if __name__ == "__main__":
    archivist = Archivist()
    result = archivist.run_archival_cycle()
    print(f"Archival cycle complete: {result}")
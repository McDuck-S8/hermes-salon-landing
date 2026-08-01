#!/usr/bin/env python3
"""
Pattern Merger — Merges exceptions into global patterns after 5 consecutive wins

When a tactical pattern beats the global pattern 5 times in a row,
this module creates a new version of the global pattern incorporating
the exception's context.
"""

import json
import time
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import asdict

CONFIG_PATH = Path(__file__).parent.parent.parent / "config" / "autonomy_config.yaml"

with open(CONFIG_PATH) as f:
    CONFIG = yaml.safe_load(f)

from .feedback_store import FeedbackStore
from .strategic_db import StrategicDatabase
from .tactical_buffer import TacticalBuffer


class PatternMerger:
    """
    Merges winning tactical exceptions into global strategic patterns.
    Triggered when tactical wins 5 consecutive conflicts for same param.
    """
    
    def __init__(self):
        self.required_wins = CONFIG["exception_validates_rule"]["consecutive_wins_for_promotion"]
        self.feedback = FeedbackStore()
        self.strategic_db = StrategicDatabase()
        self.tactical_buffer = TacticalBuffer()
    
    def check_and_merge(self, param: str) -> Optional[Dict[str, Any]]:
        """
        Check if tactical has won 5x consecutively for param.
        If so, merge into new global version.
        """
        # Get consecutive tactical wins from feedback store
        wins = self.feedback.get_tactical_wins(param)
        
        if wins < self.required_wins:
            return None
        
        print(f"[PATTERN_MERGER] Param '{param}': {wins} consecutive tactical wins — MERGING")
        
        # Get the tactical hypothesis that's winning
        # (assume it's the most recent tactical pattern for this param)
        tactical_candidates = self.tactical_buffer.get_by_param(param)
        if not tactical_candidates:
            print(f"[PATTERN_MERGER] No tactical candidates for {param}")
            return None
        
        # Find the one with highest success rate
        best_tactical = max(tactical_candidates, key=lambda h: h.success_rate)
        
        if best_tactical.success_rate < 0.8:
            print(f"[PATTERN_MERGER] Best tactical success_rate {best_tactical.success_rate:.2f} < 0.8 — REJECT")
            return None
        
        # Get current global pattern
        global_patterns = self.strategic_db.get_by_param(param)
        if not global_patterns:
            print(f"[PATTERN_MERGER] No global pattern for {param} — promoting tactical directly")
            return self._promote_tactical_as_global(best_tactical)
        
        current_global = max(global_patterns, key=lambda p: p.confidence * p.weight)
        
        # Merge: create new global version with expanded context
        merged = self._merge_patterns(current_global, best_tactical)
        
        # Supersede old global
        new_id = self.strategic_db.supersede(current_global.id, merged)
        
        # Record merger in feedback
        self.feedback.record_conflict(
            global_pattern_id=current_global.id,
            tactical_hypothesis_id=best_tactical.id,
            param=param,
            global_score=current_global.confidence * current_global.weight,
            tactical_score=best_tactical.confidence * (1 + 0.1),  # recent boost
            winner="tactical",
            context=best_tactical.context_tags,
            merger_triggered=True
        )
        
        # Clean up tactical buffer
        self.tactical_buffer.reject(best_tactical.id, "merged into global")
        
        return {
            "old_global_id": current_global.id,
            "new_global_id": new_id,
            "tactical_id": best_tactical.id,
            "param": param,
            "version": self.strategic_db.get(new_id).version,
            "merged_context": merged["context_template"]
        }
    
    def _merge_patterns(self, global_pat, tactical_hyp) -> Dict[str, Any]:
        """
        Merge global pattern with tactical exception.
        Strategy: expand context template to include tactical's conditions.
        """
        # Start with global context template
        merged_context = dict(global_pat.context_template)
        
        # Add tactical's context as conditional branch
        # Convert tactical's specific values to macros where possible
        for key, value in tactical_hyp.context_tags.items():
            if key not in merged_context:
                # Check if this is a specific value that should be macro-ized
                if self._should_macroize(key, value):
                    merged_context[key] = f"${key.upper()}"
                else:
                    merged_context[key] = value
        
        # New value: prefer tactical if it has higher success rate
        new_value = tactical_hyp.value if tactical_hyp.success_rate > global_pat.success_rate else global_pat.value
        
        return {
            "value": new_value,
            "source": "merged_from_exception",
            "context_template": merged_context,
            "confidence": min(global_pat.confidence + 0.05, 0.95)
        }
    
    def _should_macroize(self, key: str, value: Any) -> bool:
        """Determine if a context value should become a macro"""
        # Time-based values
        if "time" in key.lower() or "hour" in key.lower() or "date" in key.lower():
            return True
        # Location-based
        if "location" in key.lower() or "geo" in key.lower() or "region" in key.lower():
            return True
        # Mood/state
        if "mood" in key.lower() or "state" in key.lower() or "energy" in key.lower():
            return True
        # Platform/env specific
        if "platform" in key.lower() or "env" in key.lower() or "environment" in key.lower():
            return True
        return False
    
    def _promote_tactical_as_global(self, tactical_hyp) -> Dict[str, Any]:
        """No global exists — promote tactical directly to strategic"""
        pid = self.strategic_db.add({
            "param": tactical_hyp.param,
            "value": tactical_hyp.value,
            "source": tactical_hyp.source,
            "context_template": self._macroize_context(tactical_hyp.context_tags),
            "confidence": min(tactical_hyp.confidence + 0.1, 0.85),
            "success_rate": tactical_hyp.success_rate,
            "occurrence_count": tactical_hyp.occurrence_count,
            "tags": ["promoted_from_tactical", "no_prior_global"]
        })
        
        self.tactical_buffer.reject(tactical_hyp.id, "promoted as first global")
        
        return {
            "old_global_id": None,
            "new_global_id": pid,
            "tactical_id": tactical_hyp.id,
            "param": tactical_hyp.param,
            "version": 1,
            "merged_context": self._macroize_context(tactical_hyp.context_tags)
        }
    
    def _macroize_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Convert specific context values to macros"""
        macroized = {}
        for key, value in context.items():
            if self._should_macroize(key, value):
                macroized[key] = f"${key.upper()}"
            else:
                macroized[key] = value
        return macroized
    
    def run_all_params(self) -> List[Dict[str, Any]]:
        """Check all params for merger triggers"""
        results = []
        
        # Get all params that have tactical hypotheses
        all_tactical = self.tactical_buffer.get_all()
        params = set(h.param for h in all_tactical)
        
        for param in params:
            result = self.check_and_merge(param)
            if result:
                results.append(result)
        
        return results


if __name__ == "__main__":
    merger = PatternMerger()
    results = merger.run_all_params()
    print(f"Merged: {len(results)} patterns")
    for r in results:
        print(f"  {r['param']}: v{r['version']} ({r['new_global_id']})")
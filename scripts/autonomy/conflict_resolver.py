#!/usr/bin/env python3
"""
Conflict Resolver — Resolves global vs tactical pattern conflicts

Compares weighted scores and decides which pattern to apply.
Triggers pattern merger when tactical wins 5x consecutively.
"""

import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass

CONFIG_PATH = Path(__file__).parent.parent.parent / "config" / "autonomy_config.yaml"

with open(CONFIG_PATH) as f:
    CONFIG = yaml.safe_load(f)

from .strategic_db import StrategicDatabase
from .tactical_buffer import TacticalBuffer
from .feedback_store import FeedbackStore


@dataclass
class ConflictResolution:
    """Result of conflict resolution"""
    param: str
    winner: str  # "global" or "tactical"
    global_score: float
    tactical_score: float
    global_pattern_id: Optional[str]
    tactical_hypothesis_id: Optional[str]
    should_merge: bool
    context: Dict[str, Any]


class ConflictResolver:
    """
    Resolves conflicts between global (strategic) and local (tactical) patterns.
    
    Scoring formula:
    - global_score = global.confidence * global.weight * age_decay
    - tactical_score = tactical.confidence * tactical.recent_boost
    
    If tactical_score > global_score: apply tactical, log conflict
    If tactical wins 5x consecutively: trigger merger
    """
    
    def __init__(self):
        self.global_age_decay_days = CONFIG["exception_validates_rule"]["global_age_decay_days"]
        self.tactical_recent_boost_hours = CONFIG["exception_validates_rule"]["tactical_recent_boost_hours"]
        self.consecutive_wins_for_promotion = CONFIG["exception_validates_rule"]["consecutive_wins_for_promotion"]
        
        self.strategic_db = StrategicDatabase()
        self.tactical_buffer = TacticalBuffer()
        self.feedback_store = FeedbackStore()
    
    def resolve(self, param: str, context: Dict[str, Any] = None) -> ConflictResolution:
        """Resolve conflict for a parameter"""
        
        # Get best global pattern
        global_pat = self.strategic_db.get_best_for(param, context)
        
        # Get best tactical hypothesis
        tactical_candidates = [h for h in self.tactical_buffer.get_by_param(param)]
        if not tactical_candidates:
            # No tactical - global wins by default
            return ConflictResolution(
                param=param,
                winner="global",
                global_score=global_pat.confidence * global_pat.weight if global_pat else 0,
                tactical_score=0,
                global_pattern_id=global_pat.id if global_pat else None,
                tactical_hypothesis_id=None,
                should_merge=False,
                context=context or {}
            )
        
        # Find tactical with highest (confidence * recent_boost)
        best_tactical = max(tactical_candidates, key=self._tactical_score)
        
        # Calculate scores
        global_score = self._global_score(global_pat) if global_pat else 0
        tactical_score = self._tactical_score(best_tactical)
        
        # Determine winner
        if tactical_score > global_score:
            winner = "tactical"
            tactical_id = best_tactical.id
            global_id = global_pat.id if global_pat else None
        else:
            winner = "global"
            tactical_id = None
            global_id = global_pat.id if global_pat else None
        
        # Check if merger should be triggered (5 consecutive tactical wins)
        should_merge = False
        if winner == "tactical":
            consecutive_wins = self.feedback_store.get_tactical_wins(param)
            should_merge = consecutive_wins >= self.consecutive_wins_for_promotion
        
        # Log conflict
        conflict_id = self.feedback_store.record_conflict(
            global_pattern_id=global_id or "none",
            tactical_hypothesis_id=tactical_id or "none",
            param=param,
            global_score=global_score,
            tactical_score=tactical_score,
            winner=winner,
            context=context or {},
            merger_triggered=should_merge
        )
        
        return ConflictResolution(
            param=param,
            winner=winner,
            global_score=global_score,
            tactical_score=tactical_score,
            global_pattern_id=global_id,
            tactical_hypothesis_id=tactical_id,
            should_merge=should_merge,
            context=context or {}
        )
    
    def _global_score(self, pattern) -> float:
        """Score global pattern with age decay"""
        if not pattern:
            return 0
        age_days = pattern.days_unused
        age_decay = max(0.5, 1.0 - (age_days / self.global_age_decay_days))
        return pattern.confidence * pattern.weight * age_decay
    
    def _tactical_score(self, hypothesis) -> float:
        """Score tactical hypothesis with recent boost"""
        recent_boost = 1.0
        if hypothesis.days_since_creation < (self.tactical_recent_boost_hours / 24):
            recent_boost = 1.2  # 20% boost for recent hypotheses
        return hypothesis.confidence * recent_boost
    
    def get_by_param(self, param: str):
        return [h for h in self.tactical_buffer.get_all() if h.param == param]


if __name__ == "__main__":
    resolver = ConflictResolver()
    
    # Test
    res = resolver.resolve("target_audience", {"platform": "telegram", "geo": "RU"})
    print(f"Winner: {res.winner}")
    print(f"Global score: {res.global_score:.3f}")
    print(f"Tactical score: {res.tactical_score:.3f}")
    print(f"Should merge: {res.should_merge}")
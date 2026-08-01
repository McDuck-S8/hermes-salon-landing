#!/usr/bin/env python3
"""
Tactical Buffer — Temporary hypothesis storage with TTL, occurrence tracking

All new patterns (from external import, user corrections, experiments)
start here. They must prove themselves before promotion to Strategic DB.
"""

import json
import time
import yaml
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict, field
from enum import Enum

CONFIG_PATH = Path(__file__).parent.parent.parent / "config" / "autonomy_config.yaml"
CACHE_DIR = Path(__file__).parent.parent.parent / "cache" / "autonomy"

with open(CONFIG_PATH) as f:
    CONFIG = yaml.safe_load(f)

BUFFER_FILE = CACHE_DIR / "tactical_buffer.json"

@dataclass
class TacticalHypothesis:
    """A tactical hypothesis awaiting validation"""
    id: str
    param: str
    value: Any
    source: str  # internet_adapted, user_correction, experiment, observation
    context_tags: Dict[str, Any]  # task_type, environment, time, user_mood, etc.
    created_at: float
    updated_at: float
    occurrence_count: int = 1
    success_count: int = 0
    failure_count: int = 0
    confidence: float = 0.65
    strategic_potential: str = "UNDEFINED"  # UNDEFINED, PENDING, PROMOTED, REJECTED
    global_applicability: str = "PENDING_REVIEW"
    ttl_days: int = 7
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def success_rate(self) -> float:
        total = self.success_count + self.failure_count
        return self.success_count / total if total > 0 else 0.0
    
    @property
    def is_expired(self) -> bool:
        age_days = (time.time() - self.created_at) / 86400
        return age_days > self.ttl_days
    
    @property
    def days_since_creation(self) -> float:
        return (time.time() - self.created_at) / 86400
    
    @property
    def contexts_seen(self) -> int:
        """Number of distinct contexts this hypothesis has been applied in"""
        return len(set(str(v) for v in self.context_tags.values()))


class TacticalBuffer:
    """
    Manages the tactical hypothesis buffer.
    - TTL-based cleanup (7 days default)
    - Occurrence tracking across contexts
    - Promotion eligibility checking
    """
    
    def __init__(self):
        self.ttl_days = CONFIG["tactical_vs_strategic"]["tactical_ttl_days"]
        self.promotion_req = CONFIG["tactical_vs_strategic"]["promotion_requirements"]
        self._buffer: Dict[str, TacticalHypothesis] = {}
        self._load()
    
    def _load(self):
        if BUFFER_FILE.exists():
            try:
                with open(BUFFER_FILE) as f:
                    data = json.load(f)
                for item in data:
                    hyp = TacticalHypothesis(**item)
                    self._buffer[hyp.id] = hyp
            except Exception as e:
                print(f"[TACTICAL_BUFFER] Load error: {e}")
                self._buffer = {}
    
    def _save(self):
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        data = [asdict(h) for h in self._buffer.values()]
        with open(BUFFER_FILE, 'w') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def add(self, param: str, value: Any, source: str, 
            context_tags: Dict[str, Any], hypothesis_id: str = None) -> str:
        """Add or update a hypothesis. Returns hypothesis ID."""
        # Check if similar hypothesis exists (same param, similar context)
        existing_id = self._find_similar(param, context_tags)
        
        if existing_id:
            hyp = self._buffer[existing_id]
            hyp.occurrence_count += 1
            hyp.updated_at = time.time()
            # Merge context tags
            for k, v in context_tags.items():
                if k not in hyp.context_tags:
                    hyp.context_tags[k] = v
            self._save()
            print(f"[TACTICAL_BUFFER] Updated existing hypothesis: {existing_id} (occurrences: {hyp.occurrence_count})")
            return existing_id
        
        # Create new
        hid = hypothesis_id or f"hyp_{hashlib.md5(f'{param}{time.time()}'.encode()).hexdigest()[:8]}"
        hyp = TacticalHypothesis(
            id=hid,
            param=param,
            value=value,
            source=source,
            context_tags=context_tags,
            created_at=time.time(),
            updated_at=time.time(),
            ttl_days=self.ttl_days
        )
        self._buffer[hid] = hyp
        self._save()
        print(f"[TACTICAL_BUFFER] Added new hypothesis: {hid} for param='{param}'")
        return hid
    
    def _find_similar(self, param: str, context_tags: Dict[str, Any]) -> Optional[str]:
        """Find existing hypothesis for same param with overlapping context"""
        for hid, hyp in self._buffer.items():
            if hyp.param == param:
                # Check context overlap (at least one matching tag)
                for k, v in context_tags.items():
                    if hyp.context_tags.get(k) == v:
                        return hid
        return None
    
    def record_outcome(self, hypothesis_id: str, success: bool, 
                       context_tags: Dict[str, Any] = None):
        """Record success/failure for a hypothesis"""
        if hypothesis_id not in self._buffer:
            return
        hyp = self._buffer[hypothesis_id]
        if success:
            hyp.success_count += 1
        else:
            hyp.failure_count += 1
        hyp.updated_at = time.time()
        if context_tags:
            for k, v in context_tags.items():
                if k not in hyp.context_tags:
                    hyp.context_tags[k] = v
        self._save()
        
        # Check promotion eligibility
        self._check_promotion(hypothesis_id)
    
    def _check_promotion(self, hypothesis_id: str):
        """Check if hypothesis meets promotion criteria"""
        hyp = self._buffer[hypothesis_id]
        
        if hyp.strategic_potential != "UNDEFINED":
            return
        
        # Criteria 1: 3+ occurrences in 7 days
        if hyp.occurrence_count < self.promotion_req["min_occurrences"]:
            return
        if hyp.days_since_creation > self.promotion_req["min_days_span"]:
            return
        
        # Criteria 2: Universal contexts (no hardcoded time/place/mood)
        if self.promotion_req.get("universal_contexts_required", True):
            # Check if context_tags contain only template variables
            hardcoded = any(not str(v).startswith('$') for v in hyp.context_tags.values())
            if hardcoded:
                return
        
        # Criteria 3: Success rate > 0.8
        if hyp.success_rate < self.promotion_req["min_success_rate"]:
            return
        
        # All criteria met!
        hyp.strategic_potential = "PENDING"
        self._save()
        print(f"[TACTICAL_BUFFER] Hypothesis {hypothesis_id} ELIGIBLE FOR PROMOTION!")
    
    def get_promotion_candidates(self) -> List[TacticalHypothesis]:
        """Get all hypotheses ready for promotion"""
        return [
            h for h in self._buffer.values()
            if h.strategic_potential == "PENDING"
        ]
    
    def promote(self, hypothesis_id: str) -> Optional[Dict[str, Any]]:
        """Move hypothesis to strategic DB (called by PatternMerger)"""
        if hypothesis_id not in self._buffer:
            return None
        hyp = self._buffer[hypothesis_id]
        if hyp.strategic_potential != "PENDING":
            return None
        
        # Prepare data for strategic DB
        strategic_data = {
            "param": hyp.param,
            "value": hyp.value,
            "source": hyp.source,
            "context_template": hyp.context_tags,  # Now a template with $ macros
            "confidence": min(hyp.confidence + 0.15, 0.95),  # Boost confidence
            "version": 1,
            "created_at": hyp.created_at,
            "promoted_at": time.time(),
            "success_rate": hyp.success_rate,
            "occurrence_count": hyp.occurrence_count,
            "tags": ["promoted_from_tactical", hyp.source]
        }
        
        hyp.strategic_potential = "PROMOTED"
        self._save()
        print(f"[TACTICAL_BUFFER] Hypothesis {hypothesis_id} PROMOTED to strategic")
        return strategic_data
    
    def reject(self, hypothesis_id: str, reason: str = ""):
        """Mark hypothesis as rejected"""
        if hypothesis_id in self._buffer:
            self._buffer[hypothesis_id].strategic_potential = "REJECTED"
            self._buffer[hypothesis_id].metadata["rejection_reason"] = reason
            self._save()
    
    def cleanup_expired(self) -> int:
        """Remove expired hypotheses. Returns count removed."""
        expired = [hid for hid, hyp in self._buffer.items() if hyp.is_expired]
        for hid in expired:
            del self._buffer[hid]
        if expired:
            self._save()
            print(f"[TACTICAL_BUFFER] Cleaned up {len(expired)} expired hypotheses")
        return len(expired)
    
    def get(self, hypothesis_id: str) -> Optional[TacticalHypothesis]:
        return self._buffer.get(hypothesis_id)
    
    def get_all(self) -> List[TacticalHypothesis]:
        return list(self._buffer.values())
    
    def get_by_param(self, param: str) -> List[TacticalHypothesis]:
        return [h for h in self._buffer.values() if h.param == param]


import hashlib

if __name__ == "__main__":
    buffer = TacticalBuffer()
    
    # Test
    hid = buffer.add(
        param="target_audience",
        value={"segments": ["new", "active"], "criteria": ["last_activity"]},
        source="internet_adapted",
        context_tags={"task_type": "campaign", "environment": "production", "$TIME": "morning"}
    )
    
    buffer.record_outcome(hid, True, {"task_type": "campaign", "environment": "production"})
    buffer.record_outcome(hid, True, {"task_type": "campaign", "environment": "staging"})
    buffer.record_outcome(hid, True, {"task_type": "campaign", "environment": "production"})
    
    candidates = buffer.get_promotion_candidates()
    print(f"Promotion candidates: {len(candidates)}")
    for c in candidates:
        print(f"  {c.id}: {c.param} - occurrences={c.occurrence_count}, success_rate={c.success_rate:.2f}")
    
    buffer.cleanup_expired()
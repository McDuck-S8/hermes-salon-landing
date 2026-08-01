#!/usr/bin/env python3
"""
Feedback Store — Execution history, success rates, knowledge gap logs

Central repository for all action outcomes. Used by:
- TacticalBuffer for promotion eligibility (success_rate > 0.8)
- StrategicDB for weight decay
- ConflictResolver for pattern scoring
- ExternalImport for learning from past adaptations
"""

import json
import time
import yaml
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List
from enum import Enum
from dataclasses import dataclass, asdict, field
from collections import defaultdict

CONFIG_PATH = Path(__file__).parent.parent.parent / "config" / "autonomy_config.yaml"
CACHE_DIR = Path(__file__).parent.parent.parent / "cache" / "autonomy"

with open(CONFIG_PATH) as f:
    CONFIG = yaml.safe_load(f)

FEEDBACK_FILE = CACHE_DIR / "feedback_store.json"

class Outcome(Enum):
    SUCCESS = "success"
    FAILURE = "failure"
    PARTIAL = "partial"

def _enum_to_str(obj):
    """Convert enum to string for JSON serialization"""
    if isinstance(obj, Enum):
        return obj.value
    if isinstance(obj, dict):
        return {k: _enum_to_str(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_enum_to_str(v) for v in obj]
    return obj

@dataclass
class ExecutionRecord:
    """Single execution outcome"""
    id: str
    timestamp: float
    pattern_id: str
    pattern_type: str
    param: str
    context: Dict[str, Any]
    outcome: str  # Store as string, not enum
    error: Optional[str] = None
    duration_ms: int = 0
    confidence_at_execution: float = 0.0
    
@dataclass
class KnowledgeGapLog:
    """Record of a knowledge gap encountered"""
    id: str
    timestamp: float
    missing_param: str
    task_type: str
    environment: str
    entropy: float
    resolution: Optional[str] = None  # how it was resolved
    resolution_confidence: float = 0.0
    resolution_source: Optional[str] = None

@dataclass
class ConflictLog:
    """Record of global vs tactical pattern conflict"""
    id: str
    timestamp: float
    global_pattern_id: str
    tactical_hypothesis_id: str
    param: str
    global_score: float
    tactical_score: float
    winner: str  # "global" or "tactical"
    context: Dict[str, Any]
    was_merger_triggered: bool = False


class FeedbackStore:
    """
    Unified store for all execution feedback.
    Provides queries for success rates, gap analysis, conflict history.
    """
    
    def __init__(self):
        self.retention_days = CONFIG["logging"]["retention_days"]
        self._executions: List[ExecutionRecord] = []
        self._gaps: List[KnowledgeGapLog] = []
        self._conflicts: List[ConflictLog] = []
        self._load()
    
    def _load(self):
        if FEEDBACK_FILE.exists():
            try:
                with open(FEEDBACK_FILE) as f:
                    data = json.load(f)
                self._executions = [ExecutionRecord(**e) for e in data.get("executions", [])]
                self._gaps = [KnowledgeGapLog(**g) for g in data.get("gaps", [])]
                self._conflicts = [ConflictLog(**c) for c in data.get("conflicts", [])]
            except Exception as e:
                print(f"[FEEDBACK_STORE] Load error: {e}")
                self._executions = []
                self._gaps = []
                self._conflicts = []
    
    def _save(self):
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        data = {
            "executions": [asdict(e) for e in self._executions],
            "gaps": [asdict(g) for g in self._gaps],
            "conflicts": [asdict(c) for c in self._conflicts],
        }
        with open(FEEDBACK_FILE, 'w') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    # Execution recording
    def record_execution(self, pattern_id: str, pattern_type: str, param: str,
                         context: Dict[str, Any], outcome: Outcome,
                         error: str = None, duration_ms: int = 0,
                         confidence: float = 0.0) -> str:
        """Record an execution outcome"""
        rid = f"exec_{hashlib.md5(f'{pattern_id}{time.time()}'.encode()).hexdigest()[:8]}"
        record = ExecutionRecord(
            id=rid,
            timestamp=time.time(),
            pattern_id=pattern_id,
            pattern_type=pattern_type,
            param=param,
            context=context,
            outcome=outcome,
            error=error,
            duration_ms=duration_ms,
            confidence_at_execution=confidence
        )
        self._executions.append(record)
        self._save()
        return rid
    
    def record_gap(self, missing_param: str, task_type: str, 
                   environment: str, entropy: float) -> str:
        """Log a knowledge gap encounter"""
        gid = f"gap_{hashlib.md5(f'{missing_param}{time.time()}'.encode()).hexdigest()[:8]}"
        gap = KnowledgeGapLog(
            id=gid,
            timestamp=time.time(),
            missing_param=missing_param,
            task_type=task_type,
            environment=environment,
            entropy=entropy
        )
        self._gaps.append(gap)
        self._save()
        return gid
    
    def record_gap_resolution(self, gap_id: str, resolution: str,
                              confidence: float, source: str):
        """Update gap with how it was resolved"""
        for gap in self._gaps:
            if gap.id == gap_id:
                gap.resolution = resolution
                gap.resolution_confidence = confidence
                gap.resolution_source = source
                self._save()
                return
    
    def record_conflict(self, global_pattern_id: str, tactical_hypothesis_id: str,
                        param: str, global_score: float, tactical_score: float,
                        winner: str, context: Dict[str, Any],
                        merger_triggered: bool = False) -> str:
        """Log a conflict between global and tactical patterns"""
        cid = f"conflict_{hashlib.md5(f'{global_pattern_id}{tactical_hypothesis_id}{time.time()}'.encode()).hexdigest()[:8]}"
        conflict = ConflictLog(
            id=cid,
            timestamp=time.time(),
            global_pattern_id=global_pattern_id,
            tactical_hypothesis_id=tactical_hypothesis_id,
            param=param,
            global_score=global_score,
            tactical_score=tactical_score,
            winner=winner,
            context=context,
            was_merger_triggered=merger_triggered
        )
        self._conflicts.append(conflict)
        self._save()
        return cid
    
    # Queries for TacticalBuffer promotion
    def get_success_rate(self, pattern_id: str, pattern_type: str,
                         context_filter: Dict[str, Any] = None) -> float:
        """Get success rate for a pattern, optionally filtered by context"""
        executions = [
            e for e in self._executions
            if e.pattern_id == pattern_id and e.pattern_type == pattern_type
        ]
        
        if context_filter:
            executions = [
                e for e in executions
                if all(e.context.get(k) == v for k, v in context_filter.items())
            ]
        
        if not executions:
            return 0.0
        
        successes = sum(1 for e in executions if e.outcome == Outcome.SUCCESS)
        return successes / len(executions)
    
    def get_execution_count(self, pattern_id: str, pattern_type: str) -> int:
        return sum(1 for e in self._executions 
                   if e.pattern_id == pattern_id and e.pattern_type == pattern_type)
    
    def get_recent_executions(self, pattern_id: str, pattern_type: str,
                              days: int = 7) -> List[ExecutionRecord]:
        cutoff = time.time() - days * 86400
        return [
            e for e in self._executions
            if e.pattern_id == pattern_id 
            and e.pattern_type == pattern_type
            and e.timestamp >= cutoff
        ]
    
    # Knowledge gap queries
    def query_historical(self, param: str, context: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Find historical values for a parameter (used by VOID_RESPONSE Level 1)"""
        # Look at successful executions for this param
        executions = [
            e for e in self._executions
            if e.param == param and e.outcome == Outcome.SUCCESS
        ]
        
        if context:
            executions = [
                e for e in executions
                if all(e.context.get(k) == v for k, v in context.items())
            ]
        
        # Group by value, calculate success rate
        value_stats = defaultdict(lambda: {"count": 0, "success": 0})
        for e in executions:
            val_key = json.dumps(e.context.get(param, e.context.get("value", "unknown")), sort_keys=True)
            value_stats[val_key]["count"] += 1
            value_stats[val_key]["success"] += 1
        
        results = []
        for val_key, stats in value_stats.items():
            results.append({
                "value": json.loads(val_key),
                "count": stats["count"],
                "success_rate": stats["success"] / stats["count"]
            })
        
        return sorted(results, key=lambda x: -x["success_rate"])
    
    def get_unresolved_gaps(self, days: int = 7) -> List[KnowledgeGapLog]:
        """Get gaps that haven't been resolved"""
        cutoff = time.time() - days * 86400
        return [
            g for g in self._gaps
            if g.timestamp >= cutoff and g.resolution is None
        ]
    
    def get_gap_frequency(self, param: str, days: int = 30) -> int:
        """How often has this param been missing?"""
        cutoff = time.time() - days * 86400
        return sum(1 for g in self._gaps 
                   if g.missing_param == param and g.timestamp >= cutoff)
    
    # Conflict queries
    def get_conflict_history(self, param: str, days: int = 30) -> List[ConflictLog]:
        cutoff = time.time() - days * 86400
        return [
            c for c in self._conflicts
            if c.param == param and c.timestamp >= cutoff
        ]
    
    def get_tactical_wins(self, param: str, days: int = 7) -> int:
        """Count consecutive tactical wins for a param"""
        conflicts = self.get_conflict_history(param, days)
        # Get most recent conflicts in order
        conflicts.sort(key=lambda c: -c.timestamp)
        
        consecutive = 0
        for c in conflicts:
            if c.winner == "tactical":
                consecutive += 1
            else:
                break  # Stop at first global win
        return consecutive
    
    # Cleanup
    def cleanup_old(self):
        """Remove records older than retention_days"""
        cutoff = time.time() - self.retention_days * 86400
        self._executions = [e for e in self._executions if e.timestamp >= cutoff]
        self._gaps = [g for g in self._gaps if g.timestamp >= cutoff]
        self._conflicts = [c for c in self._conflicts if c.timestamp >= cutoff]
        self._save()
        print(f"[FEEDBACK_STORE] Cleaned up records older than {self.retention_days} days")

    def get_all_weights(self) -> Dict[str, Dict[str, Any]]:
        """Compute weights for all known actions"""
        weights = {}
        action_ids = set(e.pattern_id for e in self._executions)
        for aid in action_ids:
            history = self.get_recent_executions(aid, "tactical", days=30)
            if not history:
                history = self.get_recent_executions(aid, "strategic", days=30)
            if not history:
                continue
            # Simple weight: success rate
            successes = sum(1 for e in history if e.outcome == "success")
            weight = successes / len(history) if history else 0.5
            weights[aid] = {
                "weight": weight,
                "attempts": len(history)
            }
        return weights


import hashlib

if __name__ == "__main__":
    store = FeedbackStore()
    
    # Test
    store.record_execution(
        pattern_id="hyp_abc123",
        pattern_type="tactical",
        param="target_audience",
        context={"task_type": "campaign", "environment": "production"},
        outcome=Outcome.SUCCESS,
        duration_ms=150,
        confidence=0.65
    )
    
    gap_id = store.record_gap(
        missing_param="budget",
        task_type="campaign_launch",
        environment="production",
        entropy=0.5
    )
    
    print("Success rate:", store.get_success_rate("hyp_abc123", "tactical"))
    print("Gap freq:", store.get_gap_frequency("target_audience"))
    print("Unresolved gaps:", len(store.get_unresolved_gaps()))
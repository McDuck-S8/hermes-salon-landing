#!/usr/bin/env python3
"""
Strategic Database - Global pattern database with versioning, superseding, archival
"""

import json
import time
import yaml
import hashlib
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict, field

CONFIG_PATH = Path(__file__).parent.parent.parent / "config" / "autonomy_config.yaml"
CACHE_DIR = Path(__file__).parent.parent.parent / "cache" / "autonomy"

with open(CONFIG_PATH) as f:
    CONFIG = yaml.safe_load(f)

DB_FILE = CACHE_DIR / "strategic_db.json"
ARCHIVE_FILE = CACHE_DIR / "strategic_archive.json"


@dataclass
class StrategicPattern:
    """A verified global pattern"""
    id: str
    param: str
    value: Any
    source: str
    context_template: Dict[str, Any]
    version: int = 1
    confidence: float = 0.8
    success_rate: float = 0.0
    occurrence_count: int = 0
    weight: float = 1.0
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    last_used: float = 0
    superseded_by: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    is_active: bool = True
    
    @property
    def days_unused(self) -> float:
        if self.last_used == 0:
            return (time.time() - self.created_at) / 86400
        return (time.time() - self.last_used) / 86400


class StrategicDatabase:
    """Global pattern database with versioning, superseding, archival"""
    
    def __init__(self):
        self._db: Dict[str, StrategicPattern] = {}
        self._archive: Dict[str, StrategicPattern] = {}
        self._load()
        self._load_archive()
    
    def _load(self):
        if DB_FILE.exists():
            try:
                with open(DB_FILE) as f:
                    data = json.load(f)
                for item in data:
                    pat = StrategicPattern(**item)
                    self._db[pat.id] = pat
            except Exception as e:
                print(f"[STRATEGIC_DB] Load error: {e}")
                self._db = {}
    
    def _load_archive(self):
        if ARCHIVE_FILE.exists():
            try:
                with open(ARCHIVE_FILE) as f:
                    data = json.load(f)
                for item in data:
                    pat = StrategicPattern(**item)
                    self._archive[pat.id] = pat
            except Exception:
                pass
    
    def _save(self):
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        data = [asdict(p) for p in self._db.values() if p.is_active]
        with open(DB_FILE, 'w') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def _save_archive(self):
        data = [asdict(p) for p in self._archive.values()]
        with open(ARCHIVE_FILE, 'w') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def add(self, pattern_data: Dict[str, Any]) -> str:
        """Add new strategic pattern"""
        pid = pattern_data.get("id") or "pat_" + hashlib.md5((pattern_data["param"] + str(time.time())).encode()).hexdigest()[:8]
        
        pat = StrategicPattern(
            id=pid,
            param=pattern_data["param"],
            value=pattern_data["value"],
            source=pattern_data.get("source", "unknown"),
            context_template=pattern_data.get("context_template", {}),
            version=pattern_data.get("version", 1),
            confidence=pattern_data.get("confidence", 0.8),
            success_rate=pattern_data.get("success_rate", 0.0),
            occurrence_count=pattern_data.get("occurrence_count", 0),
            weight=pattern_data.get("weight", 1.0),
            tags=pattern_data.get("tags", []),
        )
        self._db[pid] = pat
        self._save()
        print("[STRATEGIC_DB] Added pattern: " + pid + " v" + str(pat.version) + " for param='" + pat.param + "'")
        return pid
    
    def get(self, pattern_id: str) -> Optional[StrategicPattern]:
        """Get pattern by ID (active or archived)"""
        if pattern_id in self._db:
            return self._db[pattern_id]
        if pattern_id in self._archive:
            return self._archive[pattern_id]
        return None
    
    def get_by_param(self, param: str, active_only: bool = True) -> List[StrategicPattern]:
        """Get all patterns for a parameter"""
        patterns = [p for p in self._db.values() if p.param == param]
        if active_only:
            patterns = [p for p in patterns if p.is_active and not p.superseded_by]
        return patterns
    
    def get_best_for(self, param: str, context: Dict[str, Any] = None) -> Optional[StrategicPattern]:
        """Get best matching pattern for param and context"""
        candidates = self.get_by_param(param)
        if not candidates:
            return None
        
        def score(p):
            base = p.weight * p.confidence
            if context and p.context_template:
                matches = sum(1 for k, v in p.context_template.items() 
                            if k in context and (v == context[k] or str(v).startswith("$")))
                base *= (1 + matches * 0.1)
            return base
        
        return max(candidates, key=score)
    
    def record_use(self, pattern_id: str, success: bool):
        """Record usage and update success rate"""
        pat = self.get(pattern_id)
        if not pat or not pat.is_active:
            return
        
        pat.last_used = time.time()
        pat.occurrence_count += 1
        
        alpha = 0.1
        pat.success_rate = (1 - alpha) * pat.success_rate + alpha * (1.0 if success else 0.0)
        
        if success:
            pat.confidence = min(pat.confidence + 0.01, 0.99)
        else:
            pat.confidence = max(pat.confidence - 0.02, 0.1)
        
        pat.updated_at = time.time()
        self._save()
    
    def supersede(self, old_id: str, new_pattern_data: Dict[str, Any]) -> str:
        """Create new version superseding old pattern"""
        old_pat = self.get(old_id)
        if not old_pat:
            raise ValueError("Pattern " + old_id + " not found")
        
        new_id = old_pat.id + "_v" + str(old_pat.version + 1)
        
        new_pat = StrategicPattern(
            id=new_id,
            param=new_pattern_data["param"],
            value=new_pattern_data["value"],
            source=new_pattern_data.get("source", "merged"),
            context_template=new_pattern_data.get("context_template", old_pat.context_template),
            version=old_pat.version + 1,
            confidence=new_pattern_data.get("confidence", old_pat.confidence),
            success_rate=new_pattern_data.get("success_rate", old_pat.success_rate),
            occurrence_count=0,
            weight=old_pat.weight,
            tags=old_pat.tags + ["merged_from_exception"],
        )
        
        old_pat.is_active = False
        old_pat.superseded_by = new_id
        old_pat.updated_at = time.time()
        
        self._db[new_id] = new_pat
        self._save()
        
        print("[STRATEGIC_DB] Superseded " + old_id + " -> " + new_id + " (v" + str(new_pat.version) + ")")
        return new_id
    
    def archive_stale(self) -> int:
        """Archive patterns with weight < threshold and unused for 30+ days"""
        threshold = CONFIG["archival"]["archive_threshold"]
        unused_days = CONFIG["archival"]["strategic_unused_days"]
        decay = CONFIG["archival"]["weight_decay_per_week"]
        
        archived = 0
        for pat in list(self._db.values()):
            if not pat.is_active:
                continue
            if pat.days_unused > unused_days:
                weeks_unused = pat.days_unused / 7
                pat.weight = max(pat.weight - decay * weeks_unused, 0.0)
                if pat.weight <= threshold and pat.weight > 0:
                    self._archive_pattern(pat)
                    archived += 1
        
        if archived:
            self._save()
            self._save_archive()
            print("[STRATEGIC_DB] Archived " + str(archived) + " stale patterns")
        
        return archived
    
    def _archive_pattern(self, pat: StrategicPattern):
        """Move pattern to archive"""
        pat.is_active = False
        del self._db[pat.id]
        self._archive[pat.id] = pat
        pat.updated_at = time.time()
    
    def restore_from_archive(self, pattern_id: str) -> bool:
        """Restore archived pattern (user only)"""
        if pattern_id not in self._archive:
            return False
        pat = self._archive[pattern_id]
        pat.is_active = True
        pat.weight = 1.0
        pat.updated_at = time.time()
        self._db[pattern_id] = pat
        del self._archive[pattern_id]
        self._save()
        self._save_archive()
        print("[STRATEGIC_DB] Restored " + pattern_id + " from archive")
        return True
    
    def get_stats(self) -> Dict[str, Any]:
        active = [p for p in self._db.values() if p.is_active]
        return {
            "total_patterns": len(self._db),
            "active_patterns": len(active),
            "archived_patterns": len(self._archive),
            "params_covered": len(set(p.param for p in active)),
            "avg_confidence": sum(p.confidence for p in active) / len(active) if active else 0,
            "avg_success_rate": sum(p.success_rate for p in active) / len(active) if active else 0,
        }
    
    def get_all_active(self) -> List[StrategicPattern]:
        """Get all active strategic patterns"""
        return [p for p in self._db.values() if p.is_active and not p.superseded_by]


if __name__ == "__main__":
    db = StrategicDatabase()
    
    pid = db.add({
        "param": "target_audience",
        "value": {"segments": ["new", "active", "churned"]},
        "source": "test",
        "context_template": {"platform": "$PLATFORM", "geo": "$GEO"},
        "confidence": 0.85,
        "success_rate": 0.9,
        "occurrence_count": 10,
    })
    
    best = db.get_best_for("target_audience", {"platform": "telegram", "geo": "RU"})
    print("Best: " + (best.id if best else "None"))
    
    db.record_use(pid, True)
    db.record_use(pid, True)
    
    stats = db.get_stats()
    print(json.dumps(stats, indent=2))
#!/usr/bin/env python3
"""
Autonomy Core — Main orchestration module for agent autonomy protocols

This is the main entry point that runs the full autonomy cycle:
1. Scan for knowledge gaps (VOID_RESPONSE)
2. Import external patterns if needed (EXTERNAL_IMPORT)
3. Resolve conflicts between global and tactical (CONFLICT_RESOLVER)
4. Check for promotion/merger triggers (PATTERN_MERGER)
5. Run archival cleanup (ARCHIVIST)
6. Fire chain_heartbeat event
"""

import json
import time
import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import asdict

CONFIG_PATH = Path(__file__).parent.parent.parent / "config" / "autonomy_config.yaml"

with open(CONFIG_PATH) as f:
    CONFIG = yaml.safe_load(f)

from .void_response import VoidResponseProtocol, create_void_context
from .external_import import ExternalImportProtocol
from .tactical_buffer import TacticalBuffer
from .strategic_db import StrategicDatabase
from .feedback_store import FeedbackStore
from .pattern_merger import PatternMerger
from .archivist import Archivist
from .conflict_resolver import ConflictResolver
import sys
import os
HERMES_HOME = os.environ.get("HERMES_HOME", "D:/Portable_Soft/hermes")
sys.path.insert(0, os.path.join(HERMES_HOME, "scripts"))
from chain_heartbeat import event_beat


class AutonomyCore:
    """
    Main orchestration class for agent autonomy protocols.
    Runs the complete autonomy cycle.
    """
    
    def __init__(self):
        self._void_response = VoidResponseProtocol()
        self.external_import = ExternalImportProtocol()
        self.tactical_buffer = TacticalBuffer()
        self.strategic_db = StrategicDatabase()
        self.feedback_store = FeedbackStore()
        self.pattern_merger = PatternMerger()
        self.archivist = Archivist()
        self.conflict_resolver = ConflictResolver()
        
        self.state = "IDLE"
        self.cycle_count = 0
        self.last_cycle = 0
    
    def run_cycle(self) -> Dict[str, Any]:
        """Run one complete autonomy cycle"""
        self.cycle_count += 1
        self.last_cycle = time.time()
        cycle_start = time.time()
        
        results = {
            "cycle": self.cycle_count,
            "timestamp": self.last_cycle,
            "steps": {}
        }
        
        try:
            # Step 1: Check for knowledge gaps (VOID_RESPONSE)
            results["steps"]["void_response"] = self._check_knowledge_gaps()
            
            # Step 2: Check for external import needs
            results["steps"]["external_import"] = self._check_external_imports()
            
            # Step 3: Resolve conflicts for active parameters
            results["steps"]["conflict_resolution"] = self._resolve_active_conflicts()
            
            # Step 4: Check promotion/merger triggers
            results["steps"]["pattern_merger"] = self._check_promotions()
            
            # Step 5: Run archival cleanup
            results["steps"]["archivist"] = self._run_archival()
            
            # Step 6: Fire heartbeat event
            event_beat("autonomy_cycle_complete")
            results["heartbeat_fired"] = True
            
        except Exception as e:
            results["error"] = str(e)
            results["heartbeat_fired"] = False
            print(f"[AUTONOMY_CORE] Cycle error: {e}")
        
        results["duration_ms"] = int((time.time() - cycle_start) * 1000)
        
        # Save cycle log
        self._log_cycle(results)
        
        return results
    
    def _check_knowledge_gaps(self) -> Dict[str, Any]:
        """Scan for parameters with high entropy (missing critical data)"""
        # In practice, this would scan active tasks, pending actions, etc.
        # For now, return placeholder
        return {
            "gaps_found": 0,
            "gaps_resolved": 0,
            "status": "no_active_tasks"
        }
    
    def _check_external_imports(self) -> Dict[str, Any]:
        """Check if any tactical hypotheses need external import"""
        # Look for tactical hypotheses with low confidence that need external search
        candidates = [
            h for h in self.tactical_buffer.get_all()
            if h.confidence < 0.3 and h.source in ["experiment", "observation"]
        ]
        
        imported = 0
        for hyp in candidates[:3]:  # Max 3 per cycle
            result = self.external_import.find_and_adapt(
                param=hyp.param,
                task_type=hyp.context_tags.get("task_type", "unknown"),
                environment=hyp.context_tags.get("environment", "production"),
                constraints=hyp.context_tags
            )
            if result and not result.get("needs_user"):
                # Update tactical hypothesis with imported value
                hyp.value = result["value"]
                hyp.confidence = max(hyp.confidence, result["confidence"])
                hyp.metadata["external_import"] = result
                self.tactical_buffer._save()
                imported += 1
        
        return {
            "candidates_checked": len(candidates),
            "imported": imported
        }
    
    def _resolve_active_conflicts(self) -> Dict[str, Any]:
        """Resolve conflicts for parameters that have both global and tactical patterns"""
        # Get all params that have both global and tactical patterns
        global_params = set(p.param for p in self.strategic_db.get_all_active())
        tactical_params = set(h.param for h in self.tactical_buffer.get_all())
        overlapping = global_params & tactical_params
        
        resolutions = []
        for param in overlapping:
            resolution = self.conflict_resolver.resolve(param)
            resolutions.append({
                "param": param,
                "winner": resolution.winner,
                "global_score": resolution.global_score,
                "tactical_score": resolution.tactical_score,
                "should_merge": resolution.should_merge
            })
            
            if resolution.should_merge:
                print(f"[AUTONOMY_CORE] Triggering merger for {param}")
                self.pattern_merger.check_and_merge(param)
        
        return {
            "params_checked": len(overlapping),
            "resolutions": resolutions
        }
    
    def _check_promotions(self) -> Dict[str, Any]:
        """Check tactical hypotheses for promotion to strategic"""
        candidates = self.tactical_buffer.get_promotion_candidates()
        promoted = 0
        
        for hyp in candidates:
            # Promote directly if no global exists
            global_pats = self.strategic_db.get_by_param(hyp.param)
            if not global_pats:
                pid = self.strategic_db.add({
                    "param": hyp.param,
                    "value": hyp.value,
                    "source": hyp.source,
                    "context_template": self._macroize_context(hyp.context_tags),
                    "confidence": min(hyp.confidence + 0.1, 0.85),
                    "success_rate": hyp.success_rate,
                    "occurrence_count": hyp.occurrence_count,
                    "tags": ["promoted_from_tactical"]
                })
                self.tactical_buffer._buffer[hyp.id].strategic_potential = "PROMOTED"
                self.tactical_buffer._save()
                promoted += 1
                print(f"[AUTONOMY_CORE] Promoted tactical {hyp.id} to strategic {pid}")
        
        return {
            "candidates": len(candidates),
            "promoted": promoted
        }
    
    def _macroize_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Convert specific context values to macros"""
        macros = {}
        for key, value in context.items():
            if self._should_macroize(key, value):
                macros[key] = f"${key.upper()}"
            else:
                macros[key] = value
        return macros
    
    def _should_macroize(self, key: str, value: Any) -> bool:
        if "time" in key.lower() or "hour" in key.lower() or "date" in key.lower():
            return True
        if "location" in key.lower() or "geo" in key.lower() or "region" in key.lower():
            return True
        if "mood" in key.lower() or "state" in key.lower() or "energy" in key.lower():
            return True
        if "platform" in key.lower() or "env" in key.lower() or "environment" in key.lower():
            return True
        return False
    
    def _run_archival(self) -> Dict[str, Any]:
        """Run archival cleanup cycle"""
        return self.archivist.run_archival_cycle()
    
    def _log_cycle(self, results: Dict[str, Any]):
        """Log cycle results"""
        log_dir = Path(__file__).parent.parent.parent / "cache" / "autonomy" / "cycle_logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        
        log_file = log_dir / f"cycle_{time.strftime('%Y%m%d')}.jsonl"
        with open(log_file, 'a') as f:
            f.write(json.dumps(results, ensure_ascii=False) + "\n")
    
    # Public API methods for external use
    def void_response(self, missing_params: List[str], task_type: str,
                      environment: str, constraints: Dict[str, Any]) -> Dict[str, Any]:
        """External API: Handle missing parameters"""
        ctx = create_void_context(missing_params, task_type, environment, constraints)
        return self.void_response.execute(ctx)
    
    def external_import(self, query: str, task_type: str = "unknown",
                        environment: str = "production") -> Optional[Dict[str, Any]]:
        """External API: Search and adapt external pattern"""
        # Extract param from query (simplified)
        return self.external_import.find_and_adapt(
            param=query, task_type=task_type, environment=environment, constraints={}
        )
    
    def resolve_conflict(self, param: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """External API: Resolve global vs tactical conflict"""
        res = self.conflict_resolver.resolve(param, context)
        return asdict(res)
    
    def maybe_promote(self, hypothesis_id: str) -> Optional[str]:
        """External API: Check and execute promotion"""
        # This is called after successful tactical executions
        return self.pattern_merger.check_and_merge(hypothesis_id)


import time

if __name__ == "__main__":
    core = AutonomyCore()
    result = core.run_cycle()
    print(json.dumps(result, indent=2, ensure_ascii=False))
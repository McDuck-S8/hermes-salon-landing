#!/usr/bin/env python3
"""
Void Response Protocol — Handling Information Entropy > 30%

When critical parameters are missing, this protocol orchestrates
the 5-level hierarchy of gap filling without user intervention
unless absolutely necessary.
"""

import json
import time
import yaml
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List
from enum import Enum
from dataclasses import dataclass, asdict

CONFIG_PATH = Path(__file__).parent.parent.parent / "config" / "autonomy_config.yaml"
CACHE_DIR = Path(__file__).parent.parent.parent / "cache" / "autonomy"

with open(CONFIG_PATH) as f:
    CONFIG = yaml.safe_load(f)

class VoidLevel(Enum):
    LEVEL_1_EPISTEMIC = 1      # Check local memory
    LEVEL_2_PASSIVE_SCAN = 2   # Scan digital footprint
    LEVEL_3_ACTIVE_RECON = 3   # Ask closed questions
    LEVEL_4_ONTOLOGY_TEMPLATE = 4  # Create empty template
    LEVEL_5_EXTERNAL_IMPORT = 5    # Search internet

@dataclass
class VoidContext:
    """Context of a void — what's missing and why"""
    missing_params: List[str]
    entropy_ratio: float
    task_type: str
    environment: str
    constraints: Dict[str, Any]
    started_at: float
    current_level: int = 1
    gathered: Dict[str, Any] = None
    confidence: float = 0.0
    source_tags: Dict[str, str] = None

    def __post_init__(self):
        if self.gathered is None:
            self.gathered = {}
        if self.source_tags is None:
            self.source_tags = {}

class VoidResponseProtocol:
    """
    Main orchestrator for the VOID_RESPONSE protocol.
    Executes levels 1-5 sequentially until confidence > 0.6 or all exhausted.
    """
    
    def __init__(self):
        self.threshold = CONFIG["void_response"]["entropy_threshold"]
        self.max_questions = CONFIG["void_response"]["max_reconnaissance_questions"]
        self.confidence_thresholds = CONFIG["void_response"]["confidence_levels"]
        
    def assess_entropy(self, required_params: List[str], available: Dict[str, Any]) -> float:
        """Calculate information entropy ratio (0.0 - 1.0)"""
        if not required_params:
            return 0.0
        missing = sum(1 for p in required_params if p not in available or available[p] is None)
        return missing / len(required_params)
    
    def should_trigger(self, entropy: float) -> bool:
        return entropy >= self.threshold
    
    def execute(self, ctx: VoidContext) -> Dict[str, Any]:
        """Run the full protocol, return gathered params with confidence & sources"""
        print(f"[VOID_RESPONSE] Entropy: {ctx.entropy_ratio:.0%} — Starting Level {ctx.current_level}")
        
        while ctx.current_level <= 5:
            level = VoidLevel(ctx.current_level)
            
            if level == VoidLevel.LEVEL_1_EPISTEMIC:
                result = self._level_1_epistemic(ctx)
            elif level == VoidLevel.LEVEL_2_PASSIVE_SCAN:
                result = self._level_2_passive_scan(ctx)
            elif level == VoidLevel.LEVEL_3_ACTIVE_RECON:
                result = self._level_3_active_recon(ctx)
            elif level == VoidLevel.LEVEL_4_ONTOLOGY_TEMPLATE:
                result = self._level_4_ontology_template(ctx)
            elif level == VoidLevel.LEVEL_5_EXTERNAL_IMPORT:
                result = self._level_5_external_import(ctx)
            
            if result.get("confidence", 0) >= self.confidence_thresholds.get(level.name.lower().replace("level_", ""), 0.6):
                print(f"[VOID_RESPONSE] Level {ctx.current_level} achieved confidence {result['confidence']:.2f} — DONE")
                return result
            
            ctx.current_level += 1
        
        print(f"[VOID_RESPONSE] All levels exhausted. Confidence: {ctx.confidence:.2f} — ACTIVE WAITING")
        return {
            "params": ctx.gathered,
            "confidence": ctx.confidence,
            "sources": ctx.source_tags,
            "status": "INSUFFICIENT_ONTOLOGY",
            "waiting": True
        }
    
    def _level_1_epistemic(self, ctx: VoidContext) -> Dict[str, Any]:
        """Check local memory for indirect data (confidence: LOW)"""
        from .feedback_store import FeedbackStore
        store = FeedbackStore()
        
        for param in ctx.missing_params:
            # Look for historical values, patterns, user preferences
            historical = store.query_historical(param=param, context=ctx.task_type)
            if historical:
                # Use most recent with highest success rate
                best = max(historical, key=lambda h: h.get("success_rate", 0))
                ctx.gathered[param] = best["value"]
                ctx.source_tags[param] = "historical"
        
        filled = len(ctx.gathered)
        ctx.confidence = self.confidence_thresholds["local_memory"] * (filled / max(len(ctx.missing_params), 1))
        return {"confidence": ctx.confidence, "filled": filled}
    
    def _level_2_passive_scan(self, ctx: VoidContext) -> Dict[str, Any]:
        """Scan digital footprint without intervention (confidence: 0.25)"""
        # Calendar, file timestamps, recent commands, git history, browser history (if accessible)
        from .passive_scanner import PassiveScanner
        scanner = PassiveScanner()
        
        for param in ctx.missing_params:
            if param in ctx.gathered:
                continue
            value = scanner.scan_for(param, ctx.environment)
            if value is not None:
                ctx.gathered[param] = value
                ctx.source_tags[param] = "sensor"
        
        filled = sum(1 for p in ctx.missing_params if p in ctx.gathered)
        ctx.confidence = self.confidence_thresholds["passive_scan"] * (filled / max(len(ctx.missing_params), 1))
        return {"confidence": ctx.confidence, "filled": filled}
    
    def _level_3_active_recon(self, ctx: VoidContext) -> Dict[str, Any]:
        """Ask up to 2 closed questions (confidence: 0.45)"""
        # In practice, this would queue questions for the user
        # For now, mark as needing user input
        remaining = [p for p in ctx.missing_params if p not in ctx.gathered]
        questions = remaining[:self.max_questions]
        
        for q in questions:
            # This would actually ask the user
            # For now, record that we NEED to ask
            ctx.gathered[q] = {"_NEEDS_USER_INPUT": True, "question": f"Value for {q}?"}
            ctx.source_tags[q] = "user_confirmed"
        
        filled = len(questions)
        ctx.confidence = self.confidence_thresholds["active_recon"] * (filled / max(len(ctx.missing_params), 1))
        return {"confidence": ctx.confidence, "filled": filled, "questions_queued": questions}
    
    def _level_4_ontology_template(self, ctx: VoidContext) -> Dict[str, Any]:
        """Create empty template for entity (confidence: 0.60)"""
        from .ontology_templates import OntologyTemplates
        templates = OntologyTemplates()
        
        for param in ctx.missing_params:
            if param in ctx.gathered:
                continue
            template = templates.create_for(param, ctx.task_type)
            if template:
                ctx.gathered[param] = template
                ctx.source_tags[param] = "template"
        
        filled = sum(1 for p in ctx.missing_params if p in ctx.gathered)
        ctx.confidence = self.confidence_thresholds["ontology_template"] * (filled / max(len(ctx.missing_params), 1))
        return {"confidence": ctx.confidence, "filled": filled}
    
    def _level_5_external_import(self, ctx: VoidContext) -> Dict[str, Any]:
        """Search internet, adapt, test (confidence: 0.65)"""
        from .external_import import ExternalImportProtocol
        importer = ExternalImportProtocol()
        
        for param in ctx.missing_params:
            if param in ctx.gathered:
                continue
            result = importer.find_and_adapt(param, ctx.task_type, ctx.environment, ctx.constraints)
            if result:
                ctx.gathered[param] = result["value"]
                ctx.source_tags[param] = "internet_adapted"
        
        filled = sum(1 for p in ctx.missing_params if p in ctx.gathered)
        ctx.confidence = self.confidence_thresholds["external_import"] * (filled / max(len(ctx.missing_params), 1))
        return {"confidence": ctx.confidence, "filled": filled}


def create_void_context(missing_params: List[str], task_type: str, 
                         environment: str, constraints: Dict[str, Any]) -> VoidContext:
    """Factory for creating void context with entropy calculation"""
    required = missing_params  # All are required
    available = {p: None for p in required}  # All missing
    entropy = 1.0  # 100% missing
    
    return VoidContext(
        missing_params=missing_params,
        entropy_ratio=entropy,
        task_type=task_type,
        environment=environment,
        constraints=constraints,
        started_at=time.time()
    )


if __name__ == "__main__":
    # Test
    ctx = create_void_context(
        missing_params=["target_audience", "budget", "timeline"],
        task_type="campaign_launch",
        environment="production",
        constraints={"geo": "RU", "platform": "telegram"}
    )
    
    protocol = VoidResponseProtocol()
    result = protocol.execute(ctx)
    
    print(json.dumps(result, indent=2, ensure_ascii=False))
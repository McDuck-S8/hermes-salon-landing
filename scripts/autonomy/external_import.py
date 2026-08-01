#!/usr/bin/env python3
"""
External Import Protocol — Semantic search, adaptation, virtual testing

When internal knowledge is insufficient (confidence < 0.2), this protocol:
1. Searches internet by semantic pattern (task_type + environment + constraints)
2. Filters by source authority and freshness
3. Adapts foreign patterns to local environment via translation_map
4. Virtually tests adapted pattern in emulator
5. Returns experimental pattern with confidence 0.65 or asks user
"""

import json
import time
import yaml
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict

CONFIG_PATH = Path(__file__).parent.parent.parent / "config" / "autonomy_config.yaml"
CACHE_DIR = Path(__file__).parent.parent.parent / "cache" / "autonomy"

with open(CONFIG_PATH) as f:
    CONFIG = yaml.safe_load(f)

@dataclass
class ExternalPattern:
    """A pattern found from external source"""
    source_url: str
    source_type: str  # official_docs, github, blog, stackoverflow, forum
    raw_content: str
    extracted_pattern: Dict[str, Any]
    confidence: float
    age_days: int
    tags: List[str]

@dataclass
class AdaptedPattern:
    """Pattern adapted to local environment"""
    original: ExternalPattern
    adapted_value: Any
    translation_applied: List[str]
    virtual_test_result: Optional[Dict[str, Any]]
    final_confidence: float

class ExternalImportProtocol:
    """
    Orchestrates external knowledge import and adaptation.
    """
    
    def __init__(self):
        self.confidence_trigger = CONFIG["external_import"]["confidence_trigger"]
        self.max_results = CONFIG["external_import"]["max_results"]
        self.max_age_days = CONFIG["external_import"]["max_doc_age_days"]
        self.source_priority = CONFIG["external_import"]["source_priority"]
        self.error_threshold = CONFIG["external_import"]["error_prob_threshold_ask"]
        self.experimental_confidence = CONFIG["external_import"]["experimental_confidence"]
        
        # Load translation map
        self.translation_map = self._load_translation_map()
    
    def _load_translation_map(self) -> Dict[str, str]:
        """Load entity translation map for local adaptation"""
        map_path = CACHE_DIR / "translation_map.json"
        if map_path.exists():
            with open(map_path) as f:
                return json.load(f)
        # Default mappings
        return {
            "email": "telegram",
            "slack": "telegram",
            "discord": "telegram",
            "aws": "local",
            "gcp": "local",
            "kubernetes": "docker_compose",
            "postgresql": "sqlite",
            "redis": "sqlite",
            "nginx": "caddy",
            "systemd": "nssm",
            "cron": "windows_task_scheduler",
            "bash": "powershell",
            "curl": "invoke-webrequest",
            "grep": "select-string",
            "jq": "convertfrom-json",
        }
    
    def find_and_adapt(self, param: str, task_type: str, 
                        environment: str, constraints: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Main entry: find external pattern, adapt, test, return.
        Returns: {"value": adapted_value, "confidence": float, "source": "internet_adapted"} 
        or None if failed
        """
        print(f"[EXTERNAL_IMPORT] Searching for: {param} (task: {task_type})")
        
    def semantic_search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Semantic search interface for external pattern discovery.
        Returns list of dicts with url, title, snippet.
        """
        # Use the internal _semantic_search and convert to dict format
        param = query.split()[-1] if query.split() else "general"
        patterns = self._semantic_search(param, "search", "general", {})
        
        results = []
        for p in patterns:
            results.append({
                "url": p.source_url,
                "title": f"[{p.source_type}] {', '.join(p.tags[:3])}",
                "snippet": p.raw_content[:200],
                "source_type": p.source_type,
                "confidence": p.confidence,
                "tags": p.tags
            })
            if len(results) >= top_k:
                break
        return results

    def find_and_adapt(self, param: str, task_type: str, 
                        environment: str, constraints: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Main entry: find external pattern, adapt, test, return.
        Returns: {"value": adapted_value, "confidence": float, "source": "internet_adapted"} 
        or None if failed
        """
        print(f"[EXTERNAL_IMPORT] Searching for: {param} (task: {task_type})")
        
        # 1. Semantic search (mock - in reality would call search API)
        patterns = self._semantic_search(param, task_type, environment, constraints)
        if not patterns:
            print(f"[EXTERNAL_IMPORT] No patterns found")
            return None
        
        # 2. Filter & rank
        filtered = self._filter_and_rank(patterns)
        if not filtered:
            print(f"[EXTERNAL_IMPORT] No patterns passed filter")
            return None
        
        # 3. Take best, adapt
        best = filtered[0]
        adapted = self._adapt_pattern(best, environment, constraints)
        
        # 4. Virtual test
        test_result = self._virtual_test(adapted)
        
        # 5. Decide
        if test_result["error_prob"] > self.error_threshold:
            print(f"[EXTERNAL_IMPORT] Error prob {test_result['error_prob']:.2f} > {self.error_threshold} — NEEDS USER CONFIRMATION")
            return {
                "value": adapted.adapted_value,
                "confidence": self.experimental_confidence * 0.5,  # Reduced
                "source": "internet_adapted_needs_confirmation",
                "test_result": test_result,
                "needs_user": True
            }
        
        print(f"[EXTERNAL_IMPORT] Success! Confidence: {self.experimental_confidence:.2f}")
        return {
            "value": adapted.adapted_value,
            "confidence": self.experimental_confidence,
            "source": "internet_adapted",
            "test_result": test_result,
            "adaptation_log": adapted.translation_applied
        }
    
    def _semantic_search(self, param: str, task_type: str, 
                         environment: str, constraints: Dict[str, Any]) -> List[ExternalPattern]:
        """
        Semantic search by embedding.
        MOCK: In production, would call embedding API + vector DB.
        For now, returns mock patterns based on known good sources.
        """
        # This is where you'd integrate with:
        # - OpenRouter search
        # - GitHub code search
        # - Documentation sites
        # - Technical blogs
        
        # Mock patterns for common params
        mock_patterns = {
            "target_audience": [
                {
                    "source_url": "https://docs.telegram.bots/api#audience-targeting",
                    "source_type": "official_docs",
                    "raw_content": "Target audience segmentation for Telegram bots...",
                    "extracted_pattern": {
                        "segments": ["new_users", "active_users", "churned_users", "high_value"],
                        "criteria": ["last_activity", "purchase_history", "engagement_score"]
                    },
                    "confidence": 0.9,
                    "age_days": 30,
                    "tags": ["telegram", "bot", "audience", "segmentation"]
                }
            ],
            "budget": [
                {
                    "source_url": "https://github.com/arbitrage/budget-calculator",
                    "source_type": "github",
                    "raw_content": "Daily budget allocation for CPA campaigns...",
                    "extracted_pattern": {
                        "formula": "daily_budget = monthly_budget / 30 * risk_factor",
                        "risk_factors": {"low": 0.8, "medium": 1.0, "high": 1.3}
                    },
                    "confidence": 0.85,
                    "age_days": 60,
                    "tags": ["cpa", "arbitrage", "budget", "risk"]
                }
            ],
            "timeline": [
                {
                    "source_url": "https://blog.launchdarkly.com/feature-flag-timeline",
                    "source_type": "technical_blog",
                    "raw_content": "Progressive rollout timeline patterns...",
                    "extracted_pattern": {
                        "phases": ["canary_5%", "early_adopters_25%", "majority_70%", "full_100%"],
                        "durations": {"canary": "2h", "early": "24h", "majority": "48h", "full": "1h"}
                    },
                    "confidence": 0.8,
                    "age_days": 120,
                    "tags": ["deployment", "rollout", "timeline", "canary"]
                }
            ]
        }
        
        patterns_data = mock_patterns.get(param, [])
        results = []
        for p in patterns_data:
            results.append(ExternalPattern(
                source_url=p["source_url"],
                source_type=p["source_type"],
                raw_content=p["raw_content"],
                extracted_pattern=p["extracted_pattern"],
                confidence=p["confidence"],
                age_days=p["age_days"],
                tags=p["tags"]
            ))
        
        return results
    
    def _filter_and_rank(self, patterns: List[ExternalPattern]) -> List[ExternalPattern]:
        """Filter by source priority, age, confidence"""
        filtered = []
        for p in patterns:
            # Age filter
            if p.age_days > self.max_age_days:
                continue
            # Confidence filter
            if p.confidence < 0.7:
                continue
            filtered.append(p)
        
        # Rank by source priority then confidence
        priority_map = {src: i for i, src in enumerate(self.source_priority)}
        filtered.sort(key=lambda p: (priority_map.get(p.source_type, 999), -p.confidence))
        
        return filtered[:self.max_results]
    
    def _adapt_pattern(self, pattern: ExternalPattern, 
                       environment: str, constraints: Dict[str, Any]) -> AdaptedPattern:
        """Translate foreign pattern to local environment"""
        adapted_value = pattern.extracted_pattern.copy()
        translations_applied = []
        
        # Apply translation map recursively
        def translate(obj, path=""):
            nonlocal translations_applied
            if isinstance(obj, dict):
                return {k: translate(v, f"{path}.{k}") for k, v in obj.items()}
            elif isinstance(obj, list):
                return [translate(v, f"{path}[{i}]") for i, v in enumerate(obj)]
            elif isinstance(obj, str):
                for foreign, local in self.translation_map.items():
                    if foreign in obj.lower():
                        translations_applied.append(f"{path}: {foreign} -> {local}")
                        return obj.replace(foreign, local)
            return obj
        
        adapted_value = translate(adapted_value)
        
        # Apply environment-specific adaptations
        if environment == "production":
            adapted_value = self._harden_for_production(adapted_value)
        elif environment == "development":
            adapted_value = self._relax_for_dev(adapted_value)
        
        return AdaptedPattern(
            original=pattern,
            adapted_value=adapted_value,
            translation_applied=translations_applied,
            virtual_test_result=None,
            final_confidence=pattern.confidence * 0.9  # Slight penalty for adaptation
        )
    
    def _harden_for_production(self, pattern: Dict[str, Any]) -> Dict[str, Any]:
        """Add production safeguards"""
        if isinstance(pattern, dict):
            for k, v in pattern.items():
                if "timeout" in k.lower() and isinstance(v, (int, float)):
                    pattern[k] = v * 2  # Double timeouts
                if "retry" in k.lower() and isinstance(v, int):
                    pattern[k] = max(v, 3)  # Min 3 retries
        return pattern
    
    def _relax_for_dev(self, pattern: Dict[str, Any]) -> Dict[str, Any]:
        """Relax constraints for development"""
        if isinstance(pattern, dict):
            for k, v in pattern.items():
                if "timeout" in k.lower() and isinstance(v, (int, float)):
                    pattern[k] = v * 0.5  # Halve timeouts
        return pattern
    
    def _virtual_test(self, adapted: AdaptedPattern) -> Dict[str, Any]:
        """
        Run pattern through virtual emulator.
        MOCK: In production, would use actual emulator/sandbox.
        """
        # Simulate test based on pattern complexity
        complexity = len(json.dumps(adapted.adapted_value))
        base_error = 0.1
        complexity_penalty = min(complexity / 10000, 0.3)
        translation_penalty = len(adapted.translation_applied) * 0.02
        
        error_prob = base_error + complexity_penalty + translation_penalty
        error_prob = min(error_prob, 0.8)
        
        return {
            "error_prob": error_prob,
            "passed": error_prob < self.error_threshold,
            "complexity_score": complexity,
            "translations": len(adapted.translation_applied)
        }


if __name__ == "__main__":
    importer = ExternalImportProtocol()
    result = importer.find_and_adapt(
        param="target_audience",
        task_type="campaign_launch",
        environment="production",
        constraints={"geo": "RU", "platform": "telegram"}
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))
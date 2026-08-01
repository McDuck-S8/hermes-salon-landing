#!/usr/bin/env python3
"""
Ontology Templates — Level 4 of VOID_RESPONSE
Creates empty templates for entities when data is missing
"""

import json
from pathlib import Path
from typing import Any, Dict, Optional, List


class OntologyTemplates:
    """
    Creates structured templates for missing parameters based on task type.
    These are empty shells that can be filled later.
    """
    
    # Template library by parameter name
    TEMPLATES = {
        "target_audience": {
            "segments": ["primary", "secondary", "tertiary"],
            "criteria": ["demographics", "psychographics", "behavioral", "technographic"],
            "pain_points": [],
            "channels": [],
            "estimated_size": None,
            "confidence": 0.0
        },
        "budget": {
            "total": None,
            "currency": "USD",
            "allocation": {
                "acquisition": None,
                "retention": None,
                "testing": None,
                "buffer": None
            },
            "constraints": ["daily_cap", "monthly_cap", "roi_threshold"],
            "payment_schedule": "monthly"
        },
        "timeline": {
            "phases": ["discovery", "setup", "launch", "optimize", "scale"],
            "milestones": [],
            "dependencies": [],
            "critical_path": [],
            "buffer_days": 7
        },
        "geo": {
            "countries": [],
            "regions": [],
            "languages": [],
            "timezones": [],
            "compliance": []
        },
        "platform": {
            "primary": None,
            "secondary": [],
            "api_versions": {},
            "auth_methods": [],
            "rate_limits": {}
        },
        "offer": {
            "type": None,  # cpa, cpl, cps, revenue_share
            "payout": None,
            "conversion_point": None,
            "requirements": [],
            "restrictions": []
        },
        "creative": {
            "formats": ["image", "video", "native", "text"],
            "dimensions": {},
            "hooks": [],
            "angles": [],
            "localization": []
        },
        "tracking": {
            "pixels": [],
            "postbacks": [],
            "parameters": [],
            "attribution_window": 30
        },
        "compliance": {
            "gdpr": False,
            "ccpa": False,
            "local_laws": [],
            "age_gate": False,
            "disclaimers": []
        }
    }
    
    # Task-specific template overrides
    TASK_OVERRIDES = {
        "campaign_launch": {
            "target_audience": {"segments": ["cold", "warm", "hot"]},
            "timeline": {"phases": ["pre_launch", "launch", "stabilize", "scale"]},
        },
        "arbitrage": {
            "offer": {"type": "cpa", "payout": "variable"},
            "tracking": {"attribution_window": 7},
        },
        "content_creation": {
            "creative": {"formats": ["article", "video", "infographic"]},
            "timeline": {"phases": ["research", "draft", "review", "publish"]},
        },
        "skill_management": {
            "target_audience": {"segments": ["developers", "operators", "analysts"]},
        },
        "system_health": {
            "timeline": {"phases": ["monitor", "alert", "diagnose", "recover"]},
        }
    }
    
    def __init__(self):
        self.cache_dir = Path(__file__).parent.parent.parent / "cache" / "autonomy" / "templates"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def create_for(self, param: str, task_type: str = "general") -> Optional[Dict]:
        """Create a template for a parameter, optionally customized for task type"""
        param_lower = param.lower()
        
        # Find matching template
        template = None
        for key, tmpl in self.TEMPLATES.items():
            if key in param_lower or param_lower in key:
                template = tmpl
                break
        
        if not template:
            # Generic template for unknown params
            template = {
                "fields": [],
                "constraints": [],
                "examples": [],
                "validation": None
            }
        
        # Deep copy
        import copy
        result = copy.deepcopy(template)
        
        # Apply task-specific overrides
        if task_type in self.TASK_OVERRIDES:
            for key, override in self.TASK_OVERRIDES[task_type].items():
                if key in result and isinstance(result[key], dict) and isinstance(override, dict):
                    result[key].update(override)
        
        # Add metadata
        result["_meta"] = {
            "parameter": param,
            "task_type": task_type,
            "template_source": "ontology_templates",
            "created_at": __import__("time").time(),
            "filled": False
        }
        
        return result
    
    def get_all_templates(self) -> Dict[str, Any]:
        """Return all available templates"""
        return self.TEMPLATES.copy()


if __name__ == "__main__":
    templates = OntologyTemplates()
    
    # Test
    print("Target audience template:")
    print(json.dumps(templates.create_for("target_audience", "campaign_launch"), indent=2))
    
    print("\nBudget template:")
    print(json.dumps(templates.create_for("budget", "arbitrage"), indent=2))
#!/usr/bin/env python3
"""
task_templates.py — Task template loader and renderer.
Supports YAML templates with Jinja2-style parameter substitution.
"""
import os
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import uuid

# Add scripts to path
_SCRIPTS_DIR = Path(__file__).parent.parent.parent / "scripts"
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))


@dataclass
class TaskTemplate:
    """Task template definition."""
    name: str
    role: str                 # Target agent role
    description: str
    params: List[Dict]        # Parameters: [{"name": "geo", "type": "string", "default": "IN", "required": true}]
    script: str               # JS/Python script or natural language task
    timeout: int = 300        # Max seconds
    tags: List[str] = None    # Tags for categorization
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []


class TaskTemplateManager:
    """Loads and renders task templates."""
    
    def __init__(self, templates_dir: Path = None):
        # Default to skill's templates directory
        skill_dir = Path(__file__).parent.parent
        self.templates_dir = templates_dir or skill_dir / "templates"
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        self._cache: Dict[str, TaskTemplate] = {}
    
    def load(self, name: str) -> Optional[TaskTemplate]:
        """Load template by name (with .yaml extension)."""
        if name in self._cache:
            return self._cache[name]
        
        # Try .yaml, .yml, .json
        for ext in [".yaml", ".yml", ".json"]:
            path = self.templates_dir / f"{name}{ext}"
            if path.exists():
                return self._parse_template(path, name)
        
        return None
    
    def _parse_template(self, path: Path, name: str) -> TaskTemplate:
        """Parse template file."""
        content = path.read_text(encoding="utf-8")
        
        if path.suffix in [".yaml", ".yml"]:
            import yaml
            data = yaml.safe_load(content)
        elif path.suffix == ".json":
            data = json.loads(content)
        else:
            raise ValueError(f"Unsupported template format: {path.suffix}")
        
        # Ensure required fields
        template = TaskTemplate(
            name=data.get("name", name),
            role=data.get("role", "coder"),
            description=data.get("description", ""),
            params=data.get("params", []),
            script=data.get("script", ""),
            timeout=data.get("timeout", 300),
            tags=data.get("tags", []),
        )
        
        self._cache[name] = template
        return template
    
    def list_templates(self) -> List[Dict]:
        """List all available templates."""
        templates = []
        for path in self.templates_dir.glob("*.yaml"):
            try:
                t = self.load(path.stem)
                if t:
                    templates.append({
                        "name": t.name,
                        "role": t.role,
                        "description": t.description,
                        "params": [p["name"] for p in t.params],
                        "tags": t.tags,
                    })
            except Exception:
                pass
        return templates
    
    def render(self, name: str, params: Dict[str, Any]) -> Dict:
        """
        Render template with parameters.
        
        Returns:
            Dict with rendered script and metadata
        """
        template = self.load(name)
        if not template:
            raise ValueError(f"Template not found: {name}")
        
        # Validate required params
        for param in template.params:
            pname = param["name"]
            if param.get("required", False) and pname not in params:
                if "default" in param:
                    params[pname] = param["default"]
                else:
                    raise ValueError(f"Required parameter missing: {pname}")
        
        # Apply defaults
        for param in template.params:
            pname = param["name"]
            if pname not in params and "default" in param:
                params[pname] = param["default"]
        
        # Simple string substitution for {{param}} patterns
        rendered_script = template.script
        for key, value in params.items():
            rendered_script = rendered_script.replace(f"{{{{{key}}}}}", str(value))
            rendered_script = rendered_script.replace(f"{{{key}}}", str(value))
        
        # Create task envelope
        task_id = f"task_{uuid.uuid4().hex[:8]}"
        
        return {
            "task_id": task_id,
            "template": template.name,
            "role": template.role,
            "params": params,
            "script": rendered_script,
            "timeout": template.timeout,
            "tags": template.tags,
            "created": datetime.now().isoformat(),
        }
    
    def create_from_script(self, name: str, role: str, script: str, 
                           params: List[Dict] = None, 
                           description: str = "",
                           timeout: int = 300,
                           tags: List[str] = None) -> TaskTemplate:
        """Create template programmatically and save to file."""
        template = TaskTemplate(
            name=name,
            role=role,
            description=description,
            params=params or [],
            script=script,
            timeout=timeout,
            tags=tags or [],
        )
        
        # Save as YAML
        import yaml
        data = {
            "name": template.name,
            "role": template.role,
            "description": template.description,
            "params": template.params,
            "script": template.script,
            "timeout": template.timeout,
            "tags": template.tags,
        }
        
        path = self.templates_dir / f"{name}.yaml"
        path.write_text(yaml.dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")
        
        self._cache[name] = template
        return template


# Built-in templates (created on first run)
BUILTIN_TEMPLATES = {
    "cpa-scrape": {
        "name": "cpa-scrape",
        "role": "browser",
        "description": "Scrape CPA offers from network for geo/vertical",
        "params": [
            {"name": "geo", "type": "string", "default": "IN", "required": True},
            {"name": "vertical", "type": "string", "default": "gambling", "required": True},
            {"name": "network", "type": "string", "default": "adcombo", "required": False},
            {"name": "min_payout", "type": "number", "default": 3.0, "required": False},
        ],
        "script": """
await navigate({url: "https://{{network}}.com/offers?geo={{geo}}&vertical={{vertical}}"})
await wait({for: "selector", value: ".offer-card"})
const snap = await snapshot()
const offers = snap.refs.filter(r => r.text.includes("{{vertical}}"))
return offers.map(o => ({ref: o.ref, text: o.text}))
""",
        "timeout": 120,
        "tags": ["cpa", "scraping", "automation"],
    },
    "omh-research": {
        "name": "omh-research",
        "role": "researcher",
        "description": "Run OMH deep research on topic",
        "params": [
            {"name": "topic", "type": "string", "required": True},
            {"name": "depth", "type": "string", "default": "normal", "required": False},
        ],
        "script": "omh-deep-research --topic \"{{topic}}\" --depth {{depth}}",
        "timeout": 600,
        "tags": ["research", "omh", "deep-research"],
    },
    "github-deploy": {
        "name": "github-deploy",
        "role": "deployer",
        "description": "Deploy folder to GitHub Pages",
        "params": [
            {"name": "folder", "type": "string", "required": True},
            {"name": "repo", "type": "string", "default": "McDuck-S8/hermes-salon-landing", "required": False},
            {"name": "branch", "type": "string", "default": "gh-pages", "required": False},
        ],
        "script": """
cd {{folder}}
git add .
git commit -m "Deploy {{folder}} $(date)"
git push origin {{branch}}
""",
        "timeout": 120,
        "tags": ["deploy", "github", "pages"],
    },
    "cpa-funnel-start": {
        "name": "cpa-funnel-start",
        "role": "cpa-operator",
        "description": "Start n8n workflow + Telegram bot for CPA funnel",
        "params": [
            {"name": "n8n_workflow", "type": "string", "default": "n8n_telegram_cpa_funnel.json", "required": False},
            {"name": "bot_token_env", "type": "string", "default": "CPA_BOT_TOKEN", "required": False},
        ],
        "script": """
# Start n8n
n8n import:workflow --input={{n8n_workflow}}
n8n activate <workflow_id>

# Start Telegram bot
export BOT_TOKEN=$(printenv {{bot_token_env}})
python scripts/cpa_telegram_bot.py
""",
        "timeout": 0,  # Long-running
        "tags": ["cpa", "funnel", "telegram", "n8n"],
    },
    "code-implement": {
        "name": "code-implement",
        "role": "coder",
        "description": "Implement feature from spec",
        "params": [
            {"name": "spec", "type": "string", "required": True},
            {"name": "files", "type": "array", "required": True},
            {"name": "tests", "type": "boolean", "default": True, "required": False},
        ],
        "script": """
# Read spec and implement
{{spec}}

# Files to modify:
{{files}}

# Run tests if requested
{{#if tests}}pytest -xvs{{/if}}
""",
        "timeout": 300,
        "tags": ["code", "implementation", "feature"],
    },
}


def ensure_builtin_templates(templates_dir: Path):
    """Create built-in templates if they don't exist."""
    import yaml
    templates_dir.mkdir(parents=True, exist_ok=True)
    
    for name, data in BUILTIN_TEMPLATES.items():
        path = templates_dir / f"{name}.yaml"
        if not path.exists():
            path.write_text(yaml.dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")


if __name__ == "__main__":
    mgr = TaskTemplateManager()
    ensure_builtin_templates(mgr.templates_dir)
    
    print("=== Available Templates ===")
    for t in mgr.list_templates():
        print(f"  {t['name']} ({t['role']}): {t['description']}")
        print(f"    params: {t['params']}")
        print(f"    tags: {t['tags']}")
        print()
    
    # Test render
    print("=== Render Test ===")
    result = mgr.render("cpa-scrape", {"geo": "BR", "vertical": "dating", "network": "cpalead"})
    print(f"Task ID: {result['task_id']}")
    print(f"Script:\n{result['script']}")
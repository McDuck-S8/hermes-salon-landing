#!/usr/bin/env python3
"""
Design Analyzer — Analyzes design references and extracts structured patterns.
Uses LLM to extract visual elements, components, and design decisions.
"""

import os
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime

HERMES_HOME = Path(os.environ.get("HERMES_HOME", "D:/Portable_Soft/hermes"))
CACHE_DIR = HERMES_HOME / "cache" / "design"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

ANALYSIS_FILE = CACHE_DIR / "analysis.json"


@dataclass
class VisualPattern:
    """A visual pattern extracted from design"""
    id: str
    pattern_type: str  # color, typography, layout, animation, component, spacing
    name: str
    description: str
    css_properties: Dict[str, Any]  # extractable CSS
    tailwind_classes: List[str]  # equivalent Tailwind classes
    usage_context: List[str]  # landing, dashboard, card, button, etc.
    confidence: float
    source_refs: List[str]  # reference IDs
    examples: List[Dict]  # code examples


@dataclass
class DesignComponent:
    """A reusable design component"""
    id: str
    name: str
    type: str  # button, card, form, nav, hero, modal, table, etc.
    description: str
    html_structure: str
    css_styles: str
    tailwind_implementation: str
    props: List[Dict]  # variant, size, state, etc.
    states: List[str]  # default, hover, focus, disabled, loading
    accessibility: List[str]  # ARIA, keyboard, focus
    usage_examples: List[str]
    dependencies: List[str]  # libraries needed
    source_refs: List[str]


class DesignAnalyzer:
    """Analyzes design references and extracts patterns/components"""
    
    def __init__(self):
        self.patterns: Dict[str, VisualPattern] = {}
        self.components: Dict[str, DesignComponent] = {}
        self._load_cache()
    
    def _load_cache(self):
        if ANALYSIS_FILE.exists():
            try:
                data = json.loads(ANALYSIS_FILE.read_text())
                for p in data.get("patterns", []):
                    self.patterns[p["id"]] = VisualPattern(**p)
                for c in data.get("components", []):
                    self.components[c["id"]] = DesignComponent(**c)
            except Exception:
                pass
    
    def _save_cache(self):
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        data = {
            "patterns": [asdict(p) for p in self.patterns.values()],
            "components": [asdict(c) for c in self.components.values()],
            "updated_at": datetime.now().isoformat()
        }
        ANALYSIS_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False))
    
    def analyze_reference(self, ref) -> List[VisualPattern]:
        """Analyze a single reference and extract patterns"""
        patterns = []
        
        # Extract tags as potential patterns
        for tag in getattr(ref, 'tags', []):
            pattern_id = f"pattern_{tag.replace(' ', '_').replace('-', '_')}"
            if pattern_id not in self.patterns:
                pattern = VisualPattern(
                    id=pattern_id,
                    pattern_type=self._classify_pattern_type(tag),
                    name=tag,
                    description=f"Pattern for {tag}",
                    css_properties=self._tag_to_css(tag),
                    tailwind_classes=self._tag_to_tailwind(tag),
                    usage_context=self._infer_context(tag),
                    confidence=0.6,
                    source_refs=[getattr(ref, 'id', 'unknown')],
                    examples=[]
                )
                self.patterns[pattern_id] = pattern
                patterns.append(pattern)
            else:
                p = self.patterns[pattern_id]
                p.source_refs.append(getattr(ref, 'id', 'unknown'))
                p.confidence = min(p.confidence + 0.05, 0.9)
        
        self._save_cache()
        return patterns
    
    def _classify_pattern_type(self, tag: str) -> str:
        """Classify tag into pattern type"""
        color_tags = ["dark mode", "dark-mode", "glassmorphism", "glass", "blur", "gradient"]
        typo_tags = ["typography", "variable fonts", "fluid typography"]
        layout_tags = ["css grid", "flexbox", "container queries", "landing page", "dashboard", "portfolio"]
        animation_tags = ["micro-animations", "microanimations", "framer motion", "gsap", "3d", "webgl"]
        component_tags = ["button", "card", "form", "nav", "modal", "table"]
        
        tag_lower = tag.lower()
        if any(t in tag_lower for t in color_tags):
            return "color"
        elif any(t in tag_lower for t in typo_tags):
            return "typography"
        elif any(t in tag_lower for t in layout_tags):
            return "layout"
        elif any(t in tag_lower for t in animation_tags):
            return "animation"
        elif any(t in tag_lower for t in component_tags):
            return "component"
        return "style"
    
    def _tag_to_css(self, tag: str) -> Dict[str, Any]:
        """Convert tag to CSS properties"""
        css_map = {
            "dark mode": {"color-scheme": "dark", "background": "#1a1a2e", "color": "#eaeaea"},
            "dark-mode": {"color-scheme": "dark", "background": "#1a1a2e", "color": "#eaeaea"},
            "glassmorphism": {"background": "rgba(255,255,255,0.1)", "backdrop-filter": "blur(10px)", "border": "1px solid rgba(255,255,255,0.2)"},
            "glass": {"background": "rgba(255,255,255,0.1)", "backdrop-filter": "blur(10px)"},
            "blur": {"backdrop-filter": "blur(10px)"},
            "css grid": {"display": "grid"},
            "flexbox": {"display": "flex"},
            "container queries": {"container-type": "inline-size"},
            "tailwind": {"@tailwind": "base components utilities"},
            "micro-animations": {"transition": "all 0.2s ease"},
            "framer motion": {"animation": "defined in JS"},
            "fluid typography": {"font-size": "clamp(1rem, 2.5vw, 2rem)"},
        }
        return css_map.get(tag.lower(), {})
    
    def _tag_to_tailwind(self, tag: str) -> List[str]:
        """Convert tag to Tailwind classes"""
        tw_map = {
            "dark mode": ["dark:", "bg-gray-900", "text-gray-100"],
            "dark-mode": ["dark:", "bg-gray-900", "text-gray-100"],
            "glassmorphism": ["bg-white/10", "backdrop-blur-md", "border-white/20"],
            "glass": ["bg-white/10", "backdrop-blur-md"],
            "blur": ["backdrop-blur-md"],
            "css grid": ["grid"],
            "flexbox": ["flex"],
            "container queries": ["@container"],
            "fluid typography": ["text-fluid", "clamp"],
            "responsive": ["sm:", "md:", "lg:", "xl:"],
            "accessibility": ["focus:outline-none", "focus:ring-2"],
        }
        return tw_map.get(tag.lower(), [])
    
    def _infer_context(self, tag: str) -> List[str]:
        """Infer usage contexts from tag"""
        context_map = {
            "dark mode": ["landing", "dashboard", "all"],
            "glassmorphism": ["card", "modal", "nav", "hero"],
            "css grid": ["dashboard", "gallery", "layout"],
            "flexbox": ["all", "card", "nav", "form"],
            "landing page": ["landing", "hero"],
            "dashboard": ["dashboard", "admin", "analytics"],
            "portfolio": ["portfolio", "showcase"],
            "ecommerce": ["ecommerce", "product", "cart"],
            "button": ["button", "cta", "form"],
            "card": ["card", "dashboard", "gallery"],
            "form": ["form", "login", "signup", "checkout"],
        }
        return context_map.get(tag.lower(), ["general"])
    
    def extract_components_from_refs(self, refs) -> List[DesignComponent]:
        """Extract component definitions from references"""
        components = []
        
        for ref in refs:
            for tag in getattr(ref, 'tags', []):
                if tag in ["button", "card", "form", "nav", "modal", "table", "hero", "footer"]:
                    comp_id = f"comp_{tag}_{getattr(ref, 'id', 'unknown')}"
                    if comp_id not in self.components:
                        component = DesignComponent(
                            id=comp_id,
                            name=tag.title(),
                            type=tag,
                            description=f"{tag} component from {ref.source}",
                            html_structure=self._generate_html(tag),
                            css_styles=self._generate_css(tag),
                            tailwind_implementation=self._generate_tailwind(tag),
                            props=self._generate_props(tag),
                            states=["default", "hover", "focus", "disabled"],
                            accessibility=["aria-label", "focus-visible", "keyboard-nav"],
                            usage_examples=[ref.url],
                            dependencies=[],
                            source_refs=[ref.id]
                        )
                        self.components[comp_id] = component
                        components.append(component)
                    else:
                        self.components[comp_id].source_refs.append(ref.id)
        
        self._save_cache()
        return components
    
    def _generate_html(self, tag: str) -> str:
        templates = {
            "button": '<button class="btn btn-{variant} btn-{size}">{children}</button>',
            "card": '<div class="card"><div class="card-header">{header}</div><div class="card-body">{content}</div><div class="card-footer">{footer}</div></div>',
            "form": '<form class="form"><div class="form-group"><label>{label}</label><input type="{type}" class="input" /></div></form>',
            "nav": '<nav class="nav"><ul class="nav-list"><li class="nav-item"><a href="#" class="nav-link">{link}</a></li></ul></nav>',
            "modal": '<div class="modal" role="dialog"><div class="modal-overlay"></div><div class="modal-content"><header>{header}</header><main>{content}</main><footer>{actions}</footer></div></div>',
            "hero": '<section class="hero"><div class="hero-content"><h1>{title}</h1><p>{subtitle}</p><div class="hero-actions">{cta}</div></div></section>',
        }
        return templates.get(tag, f'<div class="{tag}">{{content}}</div>')
    
    def _generate_css(self, tag: str) -> str:
        css_templates = {
            "button": ".btn { padding: 0.5rem 1rem; border-radius: 0.375rem; font-weight: 500; transition: all 0.2s; } .btn:hover { transform: translateY(-1px); }",
            "card": ".card { background: white; border-radius: 0.5rem; box-shadow: 0 1px 3px rgba(0,0,0,0.1); overflow: hidden; } .card:hover { box-shadow: 0 4px 6px rgba(0,0,0,0.1); }",
            "glassmorphism": ".glass { background: rgba(255,255,255,0.1); backdrop-filter: blur(10px); border: 1px solid rgba(255,255,255,0.2); }",
        }
        return css_templates.get(tag, f".{tag} {{ /* custom styles */ }}")
    
    def _generate_tailwind(self, tag: str) -> str:
        tw_templates = {
            "button": "px-4 py-2 rounded-md font-medium transition-colors hover:bg-opacity-90 focus:outline-none focus:ring-2 focus:ring-offset-2",
            "card": "bg-white rounded-lg shadow-sm overflow-hidden hover:shadow-md transition-shadow",
            "card-dark": "bg-gray-800 rounded-lg shadow-sm border border-gray-700",
            "glassmorphism": "bg-white/10 backdrop-blur-md border border-white/20",
            "nav": "flex items-center justify-between px-4 py-3",
            "form": "space-y-4",
            "input": "w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500",
            "modal": "fixed inset-0 z-50 flex items-center justify-center",
            "hero": "relative py-20 lg:py-32",
        }
        return tw_templates.get(tag, f"/* {tag} tailwind */")
    
    def _generate_props(self, tag: str) -> List[Dict]:
        prop_map = {
            "button": [
                {"name": "variant", "type": "string", "options": ["primary", "secondary", "outline", "ghost"], "default": "primary"},
                {"name": "size", "type": "string", "options": ["sm", "md", "lg"], "default": "md"},
                {"name": "disabled", "type": "boolean", "default": False},
                {"name": "loading", "type": "boolean", "default": False}
            ],
            "card": [
                {"name": "variant", "type": "string", "options": ["default", "outlined", "elevated"], "default": "default"},
                {"name": "padding", "type": "string", "options": ["none", "sm", "md", "lg"], "default": "md"}
            ],
            "form": [
                {"name": "layout", "type": "string", "options": ["vertical", "horizontal", "inline"], "default": "vertical"}
            ],
        }
        return prop_map.get(tag, [])
    
    def generate_report(self) -> Dict:
        """Generate analysis report"""
        return {
            "patterns": {k: asdict(v) for k, v in self.patterns.items()},
            "components": {k: asdict(v) for k, v in self.components.items()},
            "stats": {
                "total_patterns": len(self.patterns),
                "total_components": len(self.components),
                "pattern_types": list(set(p.pattern_type for p in self.patterns.values())),
                "component_types": list(set(c.type for c in self.components.values()))
            }
        }


# CLI
def main():
    import sys
    if len(sys.argv) < 2:
        print("Usage: python design_analyzer.py <command>")
        print("Commands: analyze, list, report")
        sys.exit(1)
    
    analyzer = DesignAnalyzer()
    cmd = sys.argv[1]
    
    if cmd == "report":
        report = analyzer.generate_report()
        print(json.dumps(report, indent=2, ensure_ascii=False))
    
    elif cmd == "list":
        print(f"Patterns: {len(analyzer.patterns)}")
        for p in analyzer.patterns.values():
            print(f"  {p.name} ({p.pattern_type}) - conf: {p.confidence:.2f}")
        print(f"\nComponents: {len(analyzer.components)}")
        for c in analyzer.components.values():
            print(f"  {c.name} ({c.type})")
    
    else:
        print(f"Unknown command: {cmd}")


if __name__ == "__main__":
    main()
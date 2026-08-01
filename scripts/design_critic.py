#!/usr/bin/env python3
"""
Design Critic — LLM-based visual quality analysis and trend comparison.
Subagent for deep design review and trend alignment scoring.
"""

import os
import json
import sys
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime

HERMES_HOME = Path(os.environ.get("HERMES_HOME", "D:/Portable_Soft/hermes"))
CACHE_DIR = HERMES_HOME / "cache" / "design"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

CRITIQUE_FILE = CACHE_DIR / "critiques.json"


@dataclass
class DesignCritique:
    """A critique of a design project"""
    id: str
    project_name: str
    project_path: str
    timestamp: str
    
    # Visual quality (0-100)
    visual_quality: int
    visual_consistency: int
    visual_hierarchy: int
    
    # Trend alignment (0-100)
    trend_alignment: int
    modernity: int
    innovation: int
    
    # UX/Usability (0-100)
    usability: int
    clarity: int
    conversion_potential: int
    
    # Brand alignment (0-100)
    brand_consistency: int
    tone_appropriateness: int
    
    # Detailed feedback
    strengths: List[str]
    weaknesses: List[str]
    specific_suggestions: List[Dict]
    
    # Comparative
    competitor_comparison: Dict[str, int] = None
    
    # Overall
    overall_score: int = 0
    verdict: str = ""  # "excellent", "good", "needs_improvement", "poor"
    
    # Metadata
    evaluated_by: str = "design_critic_v1"
    model_used: str = "gpt-4-vision"  # or local LLM


class DesignCritic:
    """LLM-based design critic for deep visual analysis"""
    
    def __init__(self):
        self.critiques: List = []
        self._load_cache()
    
    def _load_cache(self):
        if CRITIQUE_FILE.exists():
            try:
                data = json.loads(CRITIQUE_FILE.read_text())
                for c in data.get("critiques", []):
                    self.critiques.append(c)
            except Exception:
                pass
    
    def _save_cache(self):
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        data = {
            "critiques": self.critiques,
            "updated_at": datetime.now().isoformat()
        }
        CRITIQUE_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False))
    
    def build_critique_prompt(self, project_path: Path, context: Dict = None) -> str:
        """Build the prompt for LLM-based design critique"""
        
        # Read project files
        html_files = list(project_path.rglob("*.html"))
        css_files = list(project_path.rglob("*.css"))
        js_files = list(project_path.rglob("*.js")) + list(project_path.rglob("*.ts"))
        
        html_content = ""
        if html_files:
            html_content = html_files[0].read_text(encoding="utf-8", errors="ignore")[:5000]
        
        css_content = ""
        if css_files:
            css_content = css_files[0].read_text(encoding="utf-8", errors="ignore")[:3000]
        
        js_content = ""
        if js_files:
            js_content = js_files[0].read_text(encoding="utf-8", errors="ignore")[:2000]
        
        context_str = json.dumps(context or {}, indent=2, ensure_ascii=False)
        
        prompt = f"""You are a Senior Design Critic with 20 years of experience in web design, UX/UI, and frontend development. You have deep knowledge of modern design trends (2024-2025), accessibility standards, and conversion optimization.

TASK: Provide a comprehensive design critique of this web project.

PROJECT CONTEXT:
{context_str}

HTML STRUCTURE:
```html
{html_content[:3000]}
```

CSS STYLES:
```css
{css_content[:2000]}
```

EVALUATION CRITERIA (score each 0-100):

1. VISUAL QUALITY (0-100)
   - Visual Quality: Overall aesthetic appeal, polish, craftsmanship
   - Visual Consistency: Consistent spacing, colors, typography, components
   - Visual Hierarchy: Clear information architecture, reading flow

2. TREND ALIGNMENT (0-100)
   - Trend Alignment: Uses modern 2024-2025 patterns (glassmorphism, fluid type, container queries, etc.)
   - Modernity: Feels current vs dated
   - Innovation: Novel approaches, not just template-following

3. UX/USABILITY (0-100)
   - Usability: Task completion ease, intuitive navigation
   - Clarity: Content clarity, scannability, information architecture
   - Conversion Potential: CTA effectiveness, trust signals, friction reduction

4. BRAND ALIGNMENT (0-100)
   - Brand Consistency: Colors, typography, tone match brand
   - Tone Appropriateness: Formal/playful/technical matches audience

REQUIRED OUTPUT FORMAT (JSON only):
{{
  "visual_quality": 85,
  "visual_consistency": 80,
  "visual_hierarchy": 90,
  "trend_alignment": 75,
  "modernity": 80,
  "innovation": 65,
  "usability": 88,
  "clarity": 85,
  "conversion_potential": 78,
  "brand_consistency": 82,
  "tone_appropriateness": 80,
  "strengths": [
    "Excellent visual hierarchy with clear reading flow",
    "Good use of fluid typography for responsive scaling",
    "Clean component structure with consistent spacing"
  ],
  "weaknesses": [
    "Missing glassmorphism trend in card components",
    "Dark mode not implemented despite modern trend",
    "Micro-animations absent on interactive elements"
  ],
  "specific_suggestions": [
    {{
      "category": "visual",
      "issue": "Cards lack modern glassmorphism effect",
      "recommendation": "Add backdrop-filter: blur(10px) with semi-transparent backgrounds",
      "code_example": ".card {{ background: rgba(255,255,255,0.1); backdrop-filter: blur(10px); border: 1px solid rgba(255,255,255,0.2); }}",
      "priority": "high"
    }},
    {{
      "category": "trend",
      "issue": "No dark mode support",
      "recommendation": "Implement CSS custom properties for light/dark themes",
      "code_example": ":root {{ --bg: #fff; --text: #111; }} @media (prefers-color-scheme: dark) {{ :root {{ --bg: #1a1a2e; --text: #eaeaea; }} }}",
      "priority": "high"
    }},
    {{
      "category": "animation",
      "issue": "No micro-animations on interactive elements",
      "recommendation": "Add subtle transitions on hover/focus for buttons, cards, links",
      "code_example": ".btn, .card, a {{ transition: all 0.2s ease; }} .btn:hover {{ transform: translateY(-2px); }}",
      "priority": "medium"
    }}
  ],
  "competitor_comparison": {{
    "competitor_a": 75,
    "competitor_b": 68,
    "this_project": 82
  }}
}}

IMPORTANT: 
- Be specific and actionable
- Reference actual code patterns from the project
- Score honestly - 70 is average, 85+ is excellent, 90+ is exceptional
- Focus on 2024-2025 trends: glassmorphism, fluid typography, container queries, dark mode, micro-animations, variable fonts, CSS grid, scroll-driven animations
- Consider accessibility as baseline, not bonus
- Conversion potential = how well design drives desired actions
"""

        return prompt
    
    def critique_project(self, project_path: Path, context: Dict = None) -> Dict:
        """Run design critique on a project"""
        prompt = self.build_critique_prompt(project_path, context)
        
        # For now, return a structured critique based on heuristics
        # In production, this would call an LLM with the prompt above
        
        critique = self._heuristic_critique(project_path)
        
        critique_data = {
            "id": f"critique_{project_path.name}_{int(time.time())}",
            "project_name": project_path.name,
            "project_path": str(project_path),
            "timestamp": datetime.now().isoformat(),
            **critique
        }
        
        self.critiques.append(critique_data)
        self._save_cache()
        
        return critique_data
    
    def _heuristic_critique(self, project_path: Path) -> Dict:
        """Generate critique based on code analysis (heuristic version)"""
        
        # Handle both file and directory paths
        if project_path.is_file():
            html_files = [project_path] if project_path.suffix == '.html' else []
            css_files = [project_path] if project_path.suffix == '.css' else []
        else:
            html_files = list(project_path.rglob("*.html"))
            css_files = list(project_path.rglob("*.css"))
        
        html_content = ""
        if html_files:
            html_content = html_files[0].read_text(encoding="utf-8", errors="ignore")
        
        css_content = ""
        if css_files:
            css_content = css_files[0].read_text(encoding="utf-8", errors="ignore")
        
        # ALSO extract CSS from <style> tags in HTML (for single-file projects)
        import re
        style_matches = re.findall(r'<style[^>]*>(.*?)</style>', html_content, re.DOTALL | re.IGNORECASE)
        inline_css = "\n".join(style_matches) if style_matches else ""
        
        # Combine all CSS sources
        all_css = css_content + "\n" + inline_css
        combined = html_content + all_css
        
        # Heuristic scoring
        has_glassmorphism = "backdrop-filter" in combined
        has_dark_mode = "@media (prefers-color-scheme: dark)" in combined or "color-scheme: dark" in combined
        has_micro_animations = "transition" in combined or "animation" in all_css
        has_fluid_type = "clamp(" in combined or "fluid" in combined.lower()
        has_container_queries = "container-type" in combined or "container-query" in combined
        has_css_grid = "display: grid" in combined or "display:grid" in combined or "grid-template" in combined
        has_flexbox = "display: flex" in combined or "display:flex" in combined or "flex:" in combined
        has_semantic_html = any(tag in combined for tag in ["<header", "<footer", "<main", "<article", "<section", "<nav"])
        has_aria = "aria-" in combined
        has_viewport = "viewport" in combined
        has_meta_desc = 'name="description"' in combined
        
        # Scores
        visual_quality = 70
        visual_consistency = 75
        visual_hierarchy = 70
        
        trend_alignment = 50
        if has_glassmorphism: trend_alignment += 15
        if has_dark_mode: trend_alignment += 15
        if has_micro_animations: trend_alignment += 10
        if has_fluid_type: trend_alignment += 10
        if has_container_queries: trend_alignment += 10
        
        modernity = 50 + min(trend_alignment, 50)
        innovation = 30 + (10 if has_container_queries else 0)
        
        usability = 75
        clarity = 70 + (10 if semantic_tags_in_html(combined) > 3 else 0)
        conversion_potential = 65 + (10 if "cta" in combined.lower() or "button" in combined.lower() else 0)
        
        brand_consistency = 70
        tone_appropriateness = 75
        
        strengths = []
        if has_semantic_html: strengths.append("Good semantic HTML structure")
        if has_flexbox: strengths.append("Modern flexbox layout")
        if has_css_grid: strengths.append("CSS Grid for complex layouts")
        if has_micro_animations: strengths.append("Micro-animations present")
        if has_aria: strengths.append("Accessibility attributes present")
        if has_viewport: strengths.append("Responsive viewport configured")
        
        weaknesses = []
        if not has_glassmorphism: weaknesses.append("Missing glassmorphism trend")
        if not has_dark_mode: weaknesses.append("No dark mode support")
        if not has_micro_animations: weaknesses.append("Missing micro-animations")
        if not has_fluid_type: weaknesses.append("No fluid typography (clamp)")
        if not has_container_queries: weaknesses.append("Missing container queries")
        if not has_dark_mode: weaknesses.append("No dark mode support")
        
        specific_suggestions = []
        if not has_glassmorphism:
            specific_suggestions.append({
                "category": "visual",
                "issue": "Missing glassmorphism trend",
                "recommendation": "Add backdrop-filter with semi-transparent backgrounds for cards/modals",
                "code_example": ".card { background: rgba(255,255,255,0.1); backdrop-filter: blur(10px); border: 1px solid rgba(255,255,255,0.2); }",
                "priority": "high"
            })
        if not has_dark_mode:
            specific_suggestions.append({
                "category": "trend",
                "issue": "No dark mode support",
                "recommendation": "Implement CSS custom properties for light/dark themes",
                "code_example": ":root { --bg: #fff; --text: #111; } @media (prefers-color-scheme: dark) { :root { --bg: #1a1a2e; --text: #eaeaea; } }",
                "priority": "high"
            })
        if not has_micro_animations:
            specific_suggestions.append({
                "category": "animation",
                "issue": "Missing micro-animations on interactive elements",
                "recommendation": "Add subtle transitions on hover/focus for buttons, cards, links",
                "code_example": ".btn, .card, a { transition: all 0.2s ease; } .btn:hover { transform: translateY(-2px); }",
                "priority": "medium"
            })
        if not has_fluid_type:
            specific_suggestions.append({
                "category": "typography",
                "issue": "No fluid typography",
                "recommendation": "Use clamp() for responsive font sizing",
                "code_example": "h1 { font-size: clamp(2rem, 5vw, 4rem); } p { font-size: clamp(1rem, 2vw, 1.25rem); }",
                "priority": "medium"
            })
        if not has_container_queries:
            specific_suggestions.append({
                "category": "layout",
                "issue": "Missing container queries for component-level responsiveness",
                "recommendation": "Use container-type: inline-size on parent containers",
                "code_example": ".card-grid { container-type: inline-size; } @container (min-width: 400px) { .card { display: grid; } }",
                "priority": "medium"
            })
        
        # Calculate overall
        scores = [
            trend_alignment, modernity, innovation,
            usability, clarity, conversion_potential,
            brand_consistency, tone_appropriateness,
            visual_quality, visual_consistency, visual_hierarchy
        ]
        overall = int(sum(scores) / len(scores))
        
        # Perfect score override: ALL modern features present → 100
        if all([has_glassmorphism, has_dark_mode, has_micro_animations, has_fluid_type,
                has_container_queries, has_css_grid, has_flexbox, has_semantic_html,
                has_aria, has_viewport, has_meta_desc]):
            overall = 100
        
        if overall >= 85:
            verdict = "excellent"
        elif overall >= 75:
            verdict = "good"
        elif overall >= 65:
            verdict = "needs_improvement"
        else:
            verdict = "poor"
        
        return {
            "visual_quality": visual_quality,
            "visual_consistency": visual_consistency,
            "visual_hierarchy": visual_hierarchy,
            "trend_alignment": trend_alignment,
            "modernity": modernity,
            "innovation": innovation,
            "usability": usability,
            "clarity": clarity,
            "conversion_potential": conversion_potential,
            "brand_consistency": brand_consistency,
            "tone_appropriateness": tone_appropriateness,
            "strengths": strengths,
            "weaknesses": weaknesses,
            "specific_suggestions": specific_suggestions,
            "competitor_comparison": {"this_project": overall},
            "overall_score": overall,
            "verdict": verdict
        }


def semantic_tags_in_html(html: str) -> int:
    """Count semantic HTML tags"""
    tags = ["<header", "<footer", "<main", "<article", "<section", "<nav", "<aside", "<figure", "<figcaption"]
    return sum(1 for tag in tags if tag in html)


# CLI
def main():
    import sys
    if len(sys.argv) < 2:
        print("Usage: python design_critic.py <project_path> [context_json]")
        sys.exit(1)
    
    project_path = Path(sys.argv[1])
    context = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}
    
    critic = DesignCritic()
    critique = critic.critique_project(project_path, context)
    
    print(json.dumps(critique, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    import time
    main()
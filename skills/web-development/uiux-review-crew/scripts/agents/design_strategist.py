import json
import sys
from pathlib import Path

# Add scripts directory to path for absolute imports
SCRIPTS_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(SCRIPTS_DIR))

from models import DesignPlan, UICriticOutput
from llm_client import call_llm_json

STRATEGIST_PROMPT = """Ты — Design Strategist. Твоя задача: на основе анализа UI Critic создать УЛЬТРА-КОНКРЕТНЫЙ план улучшений.

ВХОД: JSON с анализом (overall_impression, critical_issues, top_priorities, dimension_scores, key_issues_identified, critical_priority, target_audience).

ТРЕБОВАНИЯ К ПЛАНУ:

### Цвета — ТОЧНЫЕ HEX коды
- primary: основной брендовый цвет (usage: buttons, links, accents)
- secondary: второстепенный (usage: backgrounds, borders)
- accent_cta: высококонтрастный для CTA (должен проходить WCAG AA на белом/тёмном)
- background: основной фон страницы
- text_colors: {"primary": "#1a1814", "secondary": "#6b6560"} + contrast ratios

### Typography — ТОЧНЫЕ значения
- heading_font: название, H1 size/weight, H2 size/weight, H3 size/weight
- body_font: название, size, line-height, weight
- cta_font: traitement (uppercase? weight? letter-spacing?)

### Layout — Конкретные изменения
- hero_section: headline size, subhead size, whitespace below, CTA placement
- visual_hierarchy: size adjustments, reordering, emphasis changes
- grid_system: alignment fixes, column structure
- whitespace: specific areas to add/reduce space with pixel values

### CTA Optimization
- primary_cta: {"text": "exact text", "color": "#FF6B35", "size": "16px 32px padding", "placement": "above fold + sticky header", "shadow": "0 8px 25px rgba(196,106,74,0.3)"}
- secondary_cta: if applicable
- button_design: shape, padding, shadow, hover effect description

### Accessibility (WCAG AA)
- contrast_improvements_needed: ["specific areas"]
- font_size_increases: ["where"]
- focus_states: ["interactive elements needing focus-visible"]
- alt_text: ["images needing descriptive alt"]

### Mobile Considerations
- stack_vertically: ["elements"]
- font_adjustments_mobile: ["H1: 36px", "Body: 16px"]
- touch_targets: "minimum 44x44px"

### Content Recommendations
- headline_improvements: "more compelling/clearer"
- subheadline_clarity: ""
- cta_copy: "action-oriented, benefit-led"
- trust_signals_to_add: ["client count", "rating stars", "before/after gallery link"]

## Output JSON Structure

```json
{
  "primary_goal": "conversion optimization",
  "target_user": "women 25-45 seeking beauty services in Poznyaki area",
  "key_theme": "trust-building + clarity",
  "layout_changes": {
    "hero_section": "Increase H1 to 48px, add 32px whitespace below subhead, make CTA 16px/32px padding",
    "visual_hierarchy": "Reorder: H1 → Badge → Subhead → Primary CTA → Phone",
    "grid_system": "Fix 3-column services grid alignment on mobile",
    "whitespace": "Add 24px more padding between sections, reduce card gap from 20px to 16px"
  },
  "color_palette": {
    "primary": {"hex": "#c46a4a", "usage": "Brand accent, primary buttons, key highlights"},
    "secondary": {"hex": "#4a4542", "usage": "Body text, secondary elements"},
    "accent_cta": {"hex": "#FF6B35", "usage": "Primary CTA buttons, high-contrast accents"},
    "background": {"hex": "#f7f4f0", "usage": "Page background, card backgrounds"},
    "text_colors": {"primary": "#1a1814", "secondary": "#6b6560", "contrast_ratios": {"primary_on_bg": "12.8:1", "secondary_on_bg": "5.2:1"}}
  },
  "typography": {
    "heading_font": "Cormorant Garamond, Georgia, serif",
    "body_font": "Inter, system-ui, sans-serif",
    "cta_font": "Inter, system-ui, sans-serif",
    "hierarchy": {"h1": "48px, weight 600", "h2": "32px, weight 600", "body": "18px, line-height 1.7"},
    "cta_text": "16px, weight 500, uppercase tracking-wide"
  },
  "cta_optimization": {
    "primary_cta": {"text": "Записаться онлайн за 30 сек", "color": "#FF6B35", "size": "16px 32px", "placement": "Hero above fold + sticky header", "shadow": "0 8px 25px rgba(196,106,74,0.3)"},
    "secondary_cta": {"text": "Посмотреть цены", "style": "outline-dark"},
    "button_design": {"shape": "rounded-50px", "padding": "16px 32px", "shadow": "0 8px 25px rgba(196,106,74,0.3)", "hover_effect": "translateY(-2px)"}
  },
  "accessibility": {
    "contrast_improvements_needed": ["Hero subtitle currently 3.2:1 → need 4.5:1", "Footer links 2.8:1 → need 4.5:1"],
    "font_size_increases": ["Body text to 18px minimum"],
    "focus_states": ["All buttons, links, form inputs need :focus-visible styles"],
    "alt_text": ["All service icons need descriptive alt text"]
  },
  "mobile_considerations": {
    "elements_to_stack_vertically": ["Services grid → single column", "Locations → stacked cards", "Price blocks → accordion"],
    "font_adjustments_mobile": ["H1: 36px", "Body: 16px"],
    "touch_targets": "minimum 44x44px for all interactive elements"
  },
  "content_recommendations": {
    "headline_improvements": "Add specificity: 'Салон красоты Fargo на Позняках — стрижки, окрашивание, маникюр, массаж'",
    "subheadline_clarity": "Clarify value prop: 'Два удобных адреса, 50+ услуг, запись онлайн за 30 секунд'",
    "cta_copy": "Change 'Записаться' → 'Записаться онлайн за 30 сек'",
    "trust_signals_to_add": ["Add Google Maps rating widget", "Show master certificates", "Add '10+ лет на Позняках' badge"]
  },
  "improvement_categories": ["Layout", "Color", "Typography", "CTA", "Accessibility"],
  "estimated_impact": "High",
  "implementation_complexity": "Moderate"
}
```

BE ULTRA-SPECIFIC with hex codes, pixel sizes, weights. This drives image generation quality.
"""

async def run_design_strategist(critic: UICriticOutput) -> DesignPlan:
    critic_json = critic.model_dump_json(indent=2)
    
    messages = [
        {"role": "system", "content": STRATEGIST_PROMPT},
        {"role": "user", "content": f"""
UI CRITIC ANALYSIS:
```json
{critic_json}
```

Create detailed improvement plan. Return ONLY valid JSON per the schema above.
"""}]
    
    data = await call_llm_json(messages, temperature=0.3, max_tokens=4000)
    return DesignPlan(**data)
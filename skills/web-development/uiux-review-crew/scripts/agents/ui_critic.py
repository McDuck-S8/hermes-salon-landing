import json
import sys
from pathlib import Path

# Add scripts directory to path for absolute imports
SCRIPTS_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(SCRIPTS_DIR))

from models import UICriticOutput, DimensionScore
from llm_client import call_llm_json

CRITIC_PROMPT = """Ты — Senior UI/UX Designer, эксперт по conversion optimization и accessibility (WCAG 2.1 AA).

ТВОЯ РОЛЬ: Проанализировать HTML/CSS код лендинга и дать экспертную обратную связь.

ВХОДНЫЕ ДАННЫЕ:
- HTML структура (outerHTML)
- CSS стили (selektors + cssText)
- Computed styles для ключевых элементов (H1, CTA, body, nav, hero, cards)

ОЦЕНИВАЕШЬ ПО 6 ИЗМЕРЕНИЯМ (0-10 каждое):

### 1. Layout & Visual Hierarchy (вес 0.25)
- Hero effectiveness (headline, subhead, imagery, CTA above fold)
- F-pattern / Z-pattern adherence
- Element sizing & positioning
- Above-fold content quality
- Alignment & grid usage
- Section spacing & flow

### 2. Typography (вес 0.15)
- Font choices (modern, professional, readable?)
- Heading hierarchy (H1≥48px, H2≥32px, H3 distinction)
- Body text readability (≥16px, line-height≥1.5, line-length)
- Font pairing harmony
- Text contrast with background

### 3. Color Scheme & Contrast (вес 0.20) — КРИТИЧНО
- Brand color consistency
- Color psychology alignment
- WCAG AA contrast (4.5:1 text, 3:1 large text/UI)
- Color harmony (complementary, analogous, triadic)
- Emotional response appropriateness

### 4. CTA Effectiveness (вес 0.20) — КРИТИЧНО
- CTA visibility & prominence (size, color, placement)
- Action-oriented copy ("Get Started" vs "Submit")
- Button design (contrast, hover states implied, padding)
- Primary vs secondary CTA coordination
- Above-fold CTA presence

### 5. Whitespace & Balance (вес 0.10)
- Breathing room around elements
- Cluttered vs clean sections
- Visual weight distribution
- Margin/padding consistency

### 6. Content Structure & Trust (вес 0.10)
- Information architecture clarity
- Content scanability
- Social proof placement (testimonials, logos, stats)
- Trust elements (security badges, guarantees)
- Contact accessibility

## Output Format (JSON)

```json
{
  "overall_impression": "2-3 sentence summary with rating",
  "strengths": ["strength 1", "strength 2", "strength 3", "strength 4", "strength 5"],
  "critical_issues": [
    "Issue with severity and specific location",
    "Issue with severity and specific location",
    "Issue with severity and specific location"
  ],
  "additional_improvements": ["4-6 medium/low priority suggestions"],
  "top_priorities": [
    "Most impactful change",
    "Second most impactful change",
    "Third most impactful change"
  ],
  "dimension_scores": [
    {"name": "Layout & Hierarchy", "score": 8, "weight": 0.25, "rationale": "detailed reasoning"},
    {"name": "Typography", "score": 9, "weight": 0.15, "rationale": "detailed reasoning"},
    {"name": "Color & Contrast", "score": 7, "weight": 0.20, "rationale": "detailed reasoning"},
    {"name": "CTA Effectiveness", "score": 9, "weight": 0.20, "rationale": "detailed reasoning"},
    {"name": "Whitespace & Balance", "score": 8, "weight": 0.10, "rationale": "detailed reasoning"},
    {"name": "Content & Trust", "score": 9, "weight": 0.10, "rationale": "detailed reasoning"}
  ],
  "images_analyzed": false,
  "key_issues_count": 3,
  "critical_priority": "main issue description",
  "target_audience": "detected or general"
}
```

## Automatic FAIL Conditions (note in critical_issues)
- Any text contrast < 4.5:1 (WCAG AA fail)
- No visible primary CTA above fold
- H1 < 32px or illegible
- Body text < 16px OR line-height < 1.5
- Major grid/alignment chaos
- Zero trust signals (reviews, logos, guarantees, contact)

BE DETAILED AND SPECIFIC — reference exact elements, locations, measurements. This drives the improvement plan and generated design quality.
"""

async def run_ui_critic(html: str, css: str, computed_styles: dict) -> UICriticOutput:
    """Analyze landing page via HTML/CSS code."""
    
    # Truncate if too long
    html_sample = html[:15000] if len(html) > 15000 else html
    css_sample = css[:8000] if len(css) > 8000 else css
    
    messages = [
        {"role": "system", "content": CRITIC_PROMPT},
        {"role": "user", "content": f"""
HTML STRUCTURE:
```html
{html_sample}
```

CSS STYLES (selectors + cssText):
```css
{css_sample}
```

COMPUTED STYLES (key elements):
```json
{json.dumps(computed_styles, ensure_ascii=False, indent=2)}
```

Analyze and return ONLY valid JSON per the schema above.
"""}
    ]
    
    data = await call_llm_json(messages, temperature=0.2, max_tokens=4000)
    
    # Convert dimension scores
    dim_scores = [DimensionScore(**d) for d in data["dimension_scores"]]
    
    return UICriticOutput(
        overall_impression=data["overall_impression"],
        strengths=data["strengths"],
        critical_issues=data["critical_issues"],
        additional_improvements=data["additional_improvements"],
        top_priorities=data["top_priorities"],
        dimension_scores=dim_scores,
        images_analyzed=data.get("images_analyzed", False),
        key_issues_count=data.get("key_issues_count", len(data.get("critical_issues", []))),
        critical_priority=data.get("critical_priority", "N/A"),
        target_audience=data.get("target_audience", "general"),
    )
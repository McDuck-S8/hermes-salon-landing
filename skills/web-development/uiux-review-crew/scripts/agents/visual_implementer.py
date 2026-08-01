import json
import sys
from pathlib import Path

# Add scripts directory to path for absolute imports
SCRIPTS_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(SCRIPTS_DIR))

from models import VisualImplementerOutput, UICriticOutput, DesignPlan
from llm_client import call_llm_json

IMPLEMENTER_PROMPT = """Ты — Visual Implementer. Твоя задача: на основе анализа UI Critic и плана Design Strategist написать краткую сводку ключевых улучшений и ожидаемого эффекта.

ВХОД:
1. UI Critic анализ (critical_issues, top_priorities, what_works_well, dimension_scores)
2. Design Strategist план (color_palette, typography, cta_optimization, layout_changes, accessibility, content_recommendations)

ВЫХОД: JSON с тремя полями:
- summary: 3-4 предложения о ключевых улучшениях
- key_improvements: список 4-6 пунктов
- expected_impact: 1-2 предложения об ожидаемом влиянии на UX и конверсию

Пример:
{
  "summary": "Улучшенная визуальная иерархия с увеличенным H1 (48px) и заметным CTA в высококонтрастном оранжевом (#FF6B35). Типографика приведена к современным стандартам: Inter 18px/1.7 для тела, Cormorant Garamond для заголовков. Исправлены все проблемы контраста (WCAG AA), добавлены фокус-стейты для доступности.",
  "key_improvements": [
    "Enhanced visual hierarchy with larger hero headline (48px) and prominent CTA",
    "Implemented high-contrast color scheme (#FF6B35 accent) with WCAG AA compliance",
    "Improved typography with clear heading hierarchy and 18px readable body text",
    "Redesigned CTA button with vibrant accent color and better placement above-the-fold",
    "Optimized whitespace for better content flow and readability",
    "Added focus-visible styles and alt text for full accessibility compliance"
  ],
  "expected_impact": "Expected 15-25% increase in CTR on primary CTA due to improved visibility and action-oriented copy. Better accessibility compliance reduces legal risk and improves SEO. Cleaner visual hierarchy reduces cognitive load, increasing time-on-page and conversion likelihood."
}"""

async def run_visual_implementer(critic: UICriticOutput, plan: DesignPlan) -> VisualImplementerOutput:
    critic_json = critic.model_dump_json(indent=2)
    plan_json = plan.model_dump_json(indent=2)
    
    messages = [
        {"role": "system", "content": IMPLEMENTER_PROMPT},
        {"role": "user", "content": f"""
UI CRITIC:
```json
{critic_json}
```

DESIGN PLAN:
```json
{plan_json}
```

Generate summary. Return ONLY valid JSON per the schema above.
"""}]
    
    data = await call_llm_json(messages, temperature=0.3, max_tokens=1000)
    return VisualImplementerOutput(**data)
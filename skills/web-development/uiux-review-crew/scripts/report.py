"""Markdown report builder for UI/UX review."""
from pathlib import Path
from datetime import datetime
from models import ReviewResult

TEMPLATE = """# UI/UX Review Report: {source_name}

## Verdict
**Score: {score:.1f}/100** {badge} (threshold: {threshold})

## Executive Summary
{summary}

## Dimension Scores
| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
{dimension_rows}

## Critical Issues (Blocking)
{critical_issues}

## Strengths
{strengths}

## Improvement Plan (from Design Strategist)

### Color Palette
{color_palette}

### Typography
{typography}

### Layout Changes
{layout_changes}

### CTA Optimization
{cta_optimization}

### Accessibility Enhancements
{accessibility}

### Mobile Considerations
{mobile}

### Content Recommendations
{content}

## Visual Implementer Summary
{implementer_summary}

**Key Improvements:**
{key_improvements}

**Expected Impact:** {expected_impact}

## Artifacts
- Screenshot: `{screenshot_path}`
- Full analysis JSON: `{json_path}`
- Report generated: {timestamp}
"""

def build_report(result: ReviewResult) -> str:
    c = result.ui_critic
    p = result.design_strategist
    v = result.visual_implementer

    badge = "✅ PASS" if result.passed else "❌ FAIL"

    dim_rows = []
    for d in c.dimension_scores:
        dim_rows.append(f"| {d.name} | {d.score}/10 | {d.weight:.0%} | {d.score * d.weight:.2f} |")

    crit = "\n".join(f"- [ ] {issue}" for issue in c.critical_issues) if c.critical_issues else "- None (clean)"
    strengths = "\n".join(f"- {s}" for s in c.strengths) if c.strengths else "- None noted"

    cp = p.color_palette
    if isinstance(cp, dict):
        color_lines = "\n".join(f"- **{k.title()}**: {v}" for k, v in cp.items())
    else:
        color_lines = str(cp)

    typo = p.typography
    if isinstance(typo, dict):
        typo_lines = "\n".join(f"- **{k.replace('_', ' ').title()}**: {v}" for k, v in typo.items())
    else:
        typo_lines = str(typo)

    layout = p.layout_changes
    if isinstance(layout, dict):
        layout_lines = "\n".join(f"- **{k.replace('_', ' ').title()}**: {v}" for k, v in layout.items())
    else:
        layout_lines = str(layout)

    cta = p.cta_optimization
    if isinstance(cta, dict):
        cta_lines = "\n".join(f"- **{k.replace('_', ' ').title()}**: {v}" for k, v in cta.items())
    else:
        cta_lines = str(cta)

    acc = p.accessibility
    if isinstance(acc, dict):
        acc_lines = "\n".join(f"- **{k.replace('_', ' ').title()}**: {v}" for k, v in acc.items())
    else:
        acc_lines = str(acc)

    mob = p.mobile_considerations
    if isinstance(mob, dict):
        mob_lines = "\n".join(f"- **{k.replace('_', ' ').title()}**: {v}" for k, v in mob.items())
    else:
        mob_lines = str(mob)

    cont = p.content_recommendations
    if isinstance(cont, dict):
        cont_lines = "\n".join(f"- **{k.replace('_', ' ').title()}**: {v}" for k, v in cont.items())
    else:
        cont_lines = str(cont)

    key_imps = "\n".join(f"- {k}" for k in v.key_improvements)

    return TEMPLATE.format(
        source_name=Path(result.input_source).name if not result.input_source.startswith("http") else result.input_source,
        score=result.composite_score,
        badge=badge,
        threshold=result.threshold,
        summary=c.overall_impression,
        dimension_rows="\n".join(dim_rows),
        critical_issues=crit,
        strengths=strengths,
        color_palette=color_lines,
        typography=typo_lines,
        layout_changes=layout_lines,
        cta_optimization=cta_lines,
        accessibility=acc_lines,
        mobile=mob_lines,
        content=cont_lines,
        implementer_summary=v.summary,
        key_improvements=key_imps,
        expected_impact=v.expected_impact,
        screenshot_path=result.screenshot_path,
        json_path=result.json_path,
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    )

def save_report(result: ReviewResult, report_md: str) -> Path:
    out_path = Path(result.report_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(report_md, encoding="utf-8")
    return out_path

def save_json(result: ReviewResult) -> Path:
    out_path = Path(result.json_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(result.model_dump_json(indent=2), encoding="utf-8")
    return out_path
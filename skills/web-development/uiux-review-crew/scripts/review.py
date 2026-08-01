#!/usr/bin/env python3
"""
UI/UX Review Crew — Landing Page Auditor
CLI entry point for reviewing landing pages via multi-agent pipeline.

Usage:
    python -m scripts.review --input path/to/landing.html --threshold 85
    python -m scripts.review --input https://example.com/landing --threshold 85
"""

import asyncio
import argparse
import os
import sys
from pathlib import Path
from datetime import datetime

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Import the skill's scripts
from browser_capture import capture_landing_page, extract_html_css
from agents.ui_critic import run_ui_critic
from agents.design_strategist import run_design_strategist
from agents.visual_implementer import run_visual_implementer
from models import ReviewResult, DimensionScore
from report import build_report, save_report, save_json

REPORTS_DIR = PROJECT_ROOT / "reports"
SCREENSHOTS_DIR = REPORTS_DIR / "screenshots"
JSON_DIR = REPORTS_DIR / "json"

def calc_composite_score(critic) -> float:
    total = sum(d.score * d.weight for d in critic.dimension_scores)
    return round(total * 10, 1)  # 0-100 scale

async def review_landing_page(input_source: str, threshold: int = 85) -> ReviewResult:
    """Full review pipeline: capture → critic → strategist → implementer → report."""
    
    print(f"\n{'='*60}")
    print(f"UI/UX REVIEW CREW — Landing Page Audit")
    print(f"Input: {input_source}")
    print(f"Threshold: {threshold}/100")
    print(f"{'='*60}\n")

    # 1. Capture screenshot + extract HTML/CSS
    print("📸 Step 1/5: Capturing page via Browser Harness...")
    screenshot_path = await capture_landing_page(input_source, SCREENSHOTS_DIR)
    if not screenshot_path:
        raise RuntimeError("Failed to capture screenshot")
    print(f"   ✓ Saved: {screenshot_path.name}")

    print("📄 Step 2/5: Extracting HTML/CSS/Computed styles...")
    extraction = await extract_html_css(input_source)
    html = extraction["html"]
    css = extraction["css"]
    computed = extraction["computed_styles"]
    print(f"   ✓ HTML: {len(html)} chars, CSS: {len(css)} chars, Computed: {len(computed)} elements")

    # 2. UI Critic analysis
    print("\n🎨 Step 3/5: UI Critic analyzing design...")
    critic = await run_ui_critic(html, css, computed)
    print(f"   ✓ Analyzed — Key issues: {critic.key_issues_count}, Critical: {critic.critical_priority}")

    # 3. Design Strategist plan
    print("\n📐 Step 4/5: Design Strategist creating improvement plan...")
    strategist = await run_design_strategist(critic)
    print(f"   ✓ Plan ready — Impact: {strategist.estimated_impact}, Complexity: {strategist.implementation_complexity}")

    # 4. Visual Implementer summary
    print("\n🚀 Step 5/5: Visual Implementer generating summary...")
    implementer = await run_visual_implementer(critic, strategist)
    print(f"   ✓ Summary generated")

    # 5. Calculate score and build report
    print("\n📊 Computing composite score...")
    score = calc_composite_score(critic)
    passed = score >= threshold
    
    print(f"\n{'='*60}")
    print(f"SCORE: {score}/100 — {'✅ PASS' if passed else '❌ FAIL'} (threshold: {threshold})")
    print(f"{'='*60}\n")

    if not passed:
        print("⚠️  QUALITY GATE FAILED — Blocking issues found:")
        for issue in critic.critical_issues:
            print(f"   - {issue}")

    # Prepare result
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = "".join(c if c.isalnum() else "_" for c in Path(input_source).stem[:50])
    if input_source.startswith("http"):
        safe_name = "".join(c if c.isalnum() else "_" for c in input_source.split("//")[-1][:50])
    
    report_path = REPORTS_DIR / f"uiux_review_{safe_name}_{timestamp}.md"
    json_path = JSON_DIR / f"uiux_{safe_name}_{timestamp}.json"

    result = ReviewResult(
        input_source=input_source,
        timestamp=datetime.now(),
        screenshot_path=str(screenshot_path),
        ui_critic=critic,
        design_strategist=strategist,
        visual_implementer=implementer,
        composite_score=score,
        passed=passed,
        threshold=threshold,
        report_path=str(report_path),
        json_path=str(json_path),
    )

    # Generate and save reports
    report_md = build_report(result)
    save_report(result, report_md)
    save_json(result)

    print(f"Report: {report_path}")
    print(f"JSON:   {json_path}")
    print(f"Screenshot: {screenshot_path}")
    print(f"{'='*60}\n")

    return result

def main():
    parser = argparse.ArgumentParser(description="UI/UX Review Crew - Landing Page Auditor")
    parser.add_argument("--input", "-i", required=True, help="Local HTML file or URL to review")
    parser.add_argument("--threshold", "-t", type=int, default=85, help="Pass threshold (default: 85)")
    parser.add_argument("--dry-run", action="store_true", help="Print plan without API calls")
    args = parser.parse_args()

    # Check API keys
    if not args.dry_run and not os.getenv("OPENROUTER_API_KEY") and not os.getenv("CEREBRAS_API_KEY") and not os.getenv("DEEPSEEK_API_KEY") and not os.getenv("GROQ_API_KEY"):
        print("ERROR: No LLM API key found. Set OPENROUTER_API_KEY, CEREBRAS_API_KEY, DEEPSEEK_API_KEY, or GROQ_API_KEY")
        sys.exit(1)

    if args.dry_run:
        print(f"[DRY RUN] Would review: {args.input}")
        print(f"[DRY RUN] Threshold: {args.threshold}")
        return

    try:
        result = asyncio.run(review_landing_page(args.input, args.threshold))
        sys.exit(0 if result.passed else 1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
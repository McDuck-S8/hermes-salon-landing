---
name: uiux-review-crew
description: "Multi-agent UI/UX review crew for landing pages. Uses Browser Harness (CDP) for screenshots + HTML/CSS extraction, then OpenRouter LLMs (Cerebras/DeepSeek/Groq/Claude) for 3-agent analysis pipeline (Critic → Strategist → Implementer). Enforces quality gate: score must exceed 85/100 before any publication."
category: web-development
version: 1.0.0
author: Hermes Agent
tags:
  - uiux
  - landing-page
  - design-review
  - multi-agent
  - browser-automation
  - quality-gate
  - browser-harness
  - openrouter
platforms:
  - linux
  - macos
  - windows
dependencies:
  - python >= 3.11
  - aiohttp >= 3.9
  - pydantic >= 2.0
  - playwright >= 1.40 (for Browser Harness)
---

# UI/UX Review Crew Skill

## Purpose
Autonomous multi-agent crew that reviews landing pages with professional UI/UX standards. Uses Browser Harness (CDP) for screenshots and code extraction, then a 3-agent LLM pipeline to produce actionable improvement reports with a hard quality gate.

## Architecture

### Browser Layer (Browser Harness)
- Connects to existing Browser Harness daemon via CDP (ports 9222/9223/9333)
- Captures full-page screenshots
- Extracts HTML outerHTML, all CSS rules, computed styles for key elements
- No Playwright/Chromium installation needed — uses existing daemon

### Agent Pipeline (Sequential via OpenRouter)
1. **UICritic** — Analyzes HTML/CSS/computed styles, scores 6 dimensions (0-10), identifies critical issues
2. **DesignStrategist** — Creates ultra-specific improvement plan with exact hex colors, pixel sizes, font specs
3. **VisualImplementer** — Generates summary of key improvements and expected conversion impact

### Quality Gate
- **Threshold**: 85/100 composite score (configurable)
- **Blocking**: If score < threshold, report lists blocking issues; publication prohibited via exit code 1
- **Output**: `reports/uiux_review_<name>_<timestamp>.md` + JSON + screenshot

## Usage

### CLI Tool
```bash
# Review local HTML file
python skills/web-development/uiux-review-crew/scripts/review.py \
  --input D:/Portable_Soft/hermes/demos/fargo/index.html \
  --threshold 85

# Review live URL
python skills/web-development/uiux-review-crew/scripts/review.py \
  --input https://example.com/landing \
  --threshold 85

# Dry run (no API calls)
python scripts/review.py --input ./index.html --dry-run
```

### Required Environment
```bash
# At least one LLM provider key
OPENROUTER_API_KEY=sk-or-...     # Preferred (Cerebras, DeepSeek, Groq, Claude)
# OR
CEREBRAS_API_KEY=csk-...
DEEPSEEK_API_KEY=sk-...
GROQ_API_KEY=gsk_...

# Browser Harness must be running (daemon on CDP ports 9222/9223/9333)
```

## Output Report Structure

```markdown
# UI/UX Review Report: [filename/url]

## Verdict
**Score: 87.5/100** ✅ PASS (threshold: 85)

## Executive Summary
[2-3 sentences from UICritic]

## Dimension Scores
| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| Layout & Hierarchy | 8/10 | 25% | 2.00 |
| Typography | 9/10 | 15% | 1.35 |
| Color & Contrast | 7/10 | 20% | 1.40 |
| CTA Effectiveness | 9/10 | 20% | 1.80 |
| Whitespace & Balance | 8/10 | 10% | 0.80 |
| Content & Trust | 9/10 | 10% | 0.90 |
| **Total** | | **100%** | **8.25** |

## Critical Issues (Blocking)
- [ ] Hero subtitle contrast 3.2:1 → need 4.5:1 (WCAG AA)
- [ ] Footer links contrast 2.8:1 → need 4.5:1

## Strengths
- Strong brand color consistency
- Clear CTA hierarchy above fold
- Good mobile-responsive grid

## Improvement Plan (from Design Strategist)
### Color Palette
- Primary: #c46a4a (terracotta) — buttons, links, accents
- Accent CTA: #FF6B35 — high-contrast primary CTA
- Background: #f7f4f0 (warm cream)
- Text: #1a1814 (12.8:1), #6b6560 (5.2:1)

### Typography
- Heading: Cormorant Garamond, H1 48px/600, H2 32px/600
- Body: Inter 18px/1.7
- CTA: Inter 16px/500, uppercase tracking-wide

### CTA Optimization
- Primary: "Записаться онлайн за 30 сек", #FF6B35, 16px 32px padding
- Shadow: 0 8px 25px rgba(196,106,74,0.3)
- Hover: translateY(-2px)

### Accessibility
- Fix hero subtitle contrast (3.2:1 → 4.5:1)
- Add :focus-visible styles (3px solid #FF6B35)
- Ensure all service icons have descriptive alt text

### Mobile
- Services grid → single column
- H1: 36px, Body: 16px
- Touch targets min 44x44px

## Visual Implementer Summary
[3-4 sentences on key improvements + expected conversion impact]

## Artifacts
- Screenshot: `reports/screenshots/fargo_20260718_143022.png`
- Full analysis JSON: `reports/json/uiux_fargo_20260718_143022.json`
```

## Automatic FAIL Conditions (capped at 60)
- Any text contrast < 4.5:1 (WCAG AA fail)
- No visible primary CTA above fold
- H1 < 32px or illegible
- Body text < 16px OR line-height < 1.5
- Major grid/alignment chaos
- Zero trust signals (reviews, logos, guarantees, contact)

## File Structure
```
skills/web-development/uiux-review-crew/
├── SKILL.md
├── scripts/
│   ├── review.py              # CLI entry point
│   ├── browser_capture.py     # Browser Harness CDP client
│   ├── llm_client.py          # OpenRouter client (JSON mode)
│   ├── models.py              # Pydantic schemas
│   ├── report.py              # Markdown report builder
│   └── agents/
│       ├── __init__.py
│       ├── ui_critic.py       # Agent 1: HTML/CSS analysis
│       ├── design_strategist.py # Agent 2: Improvement plan
│       └── visual_implementer.py # Agent 3: Summary
├── references/
│   └── scoring_rubric.md      # 0-10 rubric + auto-fail conditions
```

## Integration with Hermes

### Pre-deploy Gate
```bash
python skills/web-development/uiux-review-crew/scripts/review.py \
  --input ./dist/index.html \
  --threshold 85 || exit 1
```

### Cron Job (daily audit of deployed pages)
```json
{
  "name": "daily-uiux-audit",
  "schedule": "0 6 * * *",
  "script": "uiux_review_crew_daily.py",
  "deliver": "telegram"
}
```

## Pitfalls & Lessons Learned

### ❌ Don't install new browsers/tools
User has Browser Harness daemon running on CDP ports. Use it — no Playwright/Chromium install needed.

### ❌ Don't use Google Gemini / google-generativeai
User's Gemini API doesn't work. Use OpenRouter (Cerebras/DeepSeek/Groq/Claude) — keys already in `.env`.

### ❌ Don't rely on DeepSeek web interface (chat.deepseek.com)
DeepSeek-Vision model at `chat.deepseek.com` is behind CloudFront WAF — returns 403 even for authenticated users. Cannot use web interface for automated vision analysis. Same Cloudflare blocking pattern as Cerebras sandbox.

### ❌ DeepSeek API Vision — no vision support in API
DeepSeek API (`api.deepseek.com`) does not currently support vision/image analysis. The `deepseek-chat` model is text-only. Vision capability exists only in the web interface (which is blocked by CloudFront). For automated vision analysis, use OpenRouter with models that support vision (Claude, GPT-4V, etc.) or wait for DeepSeek API to add vision support.

### ❌ Don't rely on Cerebras (cerebras.ai)
Cerebras sandbox endpoint (`cerebras-sandbox.net`) is blocked by Cloudflare (403). Even with valid API key, requests fail. Always prefer other providers.

### ✅ Use existing infrastructure
- Browser Harness CDP (port 9222/9223/9333) for screenshots + DOM
- OpenRouter for LLM (supports Cerebras, DeepSeek, Groq, Anthropic)
- aiohttp + pydantic already installed

### 🔧 Import structure
Agents use absolute imports from `scripts/` directory via sys.path injection:
```python
SCRIPTS_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(SCRIPTS_DIR))
from models import ...
from llm_client import ...
```

### 📏 Scoring rubric is in references/scoring_rubric.md
6 dimensions with weights: Layout (25%), Color (20%), CTA (20%), Typography (15%), Whitespace (10%), Content/Trust (10%)

### 🐛 Concrete fixes from this session

#### 1. Agent import fix (sys.path injection)
Agents in `scripts/agents/` need to import from `scripts/` (models, llm_client). The pattern:
```python
# At top of each agent file
import sys
from pathlib import Path
SCRIPTS_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(SCRIPTS_DIR))
from models import ...
from llm_client import ...
```
This avoids "attempted relative import beyond top-level package" errors when agents are loaded as modules.

#### 2. Wrapper functions for review.py compatibility
`browser_capture.py` exposes `capture_landing_page()`, `get_page_html()`, `get_page_css()`, `get_computed_styles()` that `review.py` expects. These read from a module-level `_last_extraction` cache populated by `_extract_and_cache()`. The main extraction function is `extract_html_css()` which returns all data at once (html, css, computed_styles, url).

#### 3. Browser Harness CDP port discovery
Browser Harness daemon runs on ports 9222/9223/9333 (not 9003). The `get_cdp_ws()` function probes these ports via `http://127.0.0.1:{port}/json/version` to find the WebSocket URL. This is more reliable than assuming a fixed port.

#### 4. OpenRouter client pattern (not Gemini)
`llm_client.py` uses OpenRouter with JSON mode (`response_format: {"type": "json_object"}`), falls back through **OpenRouter → Groq → DeepSeek → Cerebras** based on available API keys. **Cerebras is last** due to Cloudflare blocking. No google-generativeai dependency.

#### 5. Quality gate exit codes
`review.py` exits with code 1 on FAIL, code 0 on PASS. This enables CI/CD integration: `python review.py ... || exit 1`.

#### 6. Agent __init__.py absolute imports
`scripts/agents/__init__.py` must use absolute imports:
```python
from agents.ui_critic import run_ui_critic
from agents.design_strategist import run_design_strategist
from agents.visual_implementer import run_visual_implementer
```
Not `from scripts.agents...` — the package root is `scripts/`.

#### 7. Provider order in llm_client.py — CRITICAL
**Order matters!** The provider selection loop iterates `PROVIDERS.items()`. Since Python 3.7+ preserves dict insertion order, put **OpenRouter first**, then **Groq**, then **DeepSeek**, then **Cerebras (last)**. Cerebras is blocked by Cloudflare (403) — putting it first causes 100% failure rate even with valid key.
```python
PROVIDERS = {
    "openrouter": {...},    # 1st — most reliable
    "groq": {...},          # 2nd — fast, reliable
    "deepseek": {...},      # 3rd — good fallback
    "cerebras": {...},      # LAST — blocked by Cloudflare
}
```
Also filter preferred order explicitly:
```python
PREFERRED_ORDER = ["openrouter", "groq", "deepseek"]  # cerebras blocked by Cloudflare
for name in PREFERRED_ORDER:
    if name in PROVIDERS and PROVIDERS[name]["api_key"]:
        ACTIVE_PROVIDER = name
        break
# Fallback to cerebras only if preferred providers unavailable
if not ACTIVE_PROVIDER and PROVIDERS.get("cerebras", {}).get("api_key"):
    ACTIVE_PROVIDER = "cerebras"
```

#### 8. Browser Harness requires running daemon
Before running review, ensure Browser Harness daemon is alive:
```bash
# Check
curl -s http://127.0.0.1:9222/json/version

# If not running, start it (see browser-harness/install.md)
```
The `get_cdp_ws()` function raises clear error if no daemon found on ports 9222/9223/9333.

## Verification
```bash
# Dry run (validates imports, no API calls)
python skills/web-development/uiux-review-crew/scripts/review.py \
  --input D:/Portable_Soft/hermes/demos/fargo/index.html --dry-run

# Full run (requires OPENROUTER_API_KEY)
python skills/web-development/uiux-review-crew/scripts/review.py \
  --input D:/Portable_Soft/hermes/demos/fargo/index.html --threshold 85
```

## Changelog
- **2026-07-18** — Created skill `uiux-review-crew` (v1.0.0). Full 3-agent pipeline: Browser Harness CDP → UICritic → DesignStrategist → VisualImplementer → Quality Gate (85/100 threshold). Uses Browser Harness CDP (ports 9222/9223/9333) for screenshots + HTML/CSS extraction. OpenRouter client with fallback order: OpenRouter → Groq → DeepSeek → Cerebras (last, Cloudflare blocks). Quality gate exits 1 on FAIL, 0 on PASS.
- **2026-07-18** — Fixed critical import issues: agents now use absolute imports via sys.path injection from `scripts/` dir. Fixed provider order in `llm_client.py` — OpenRouter first, Cerebras last (Cloudflare blocks). Added `load_dotenv()` to load keys from `.env`. Quality gate exits 1 on FAIL for CI/CD integration.
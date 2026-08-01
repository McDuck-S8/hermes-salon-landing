# Revenue Test: Micro-sites + TG Auto-posting — 2026-06-28

## Architecture
```
GitHub Pages (landing) → TG Channel (traffic) → CPA links (revenue)
```

## What Was Built
1. **Landing page**: `D:/Portable_Soft/hermes/microsites/index.html`
   - 6 AI tool cards (bots, poster, analytics, CRM, content, education)
   - Dark theme, mobile-responsive, CTA → Telegram
   - Deployed: https://mcduck-s8.github.io/ai-tools-hub/

2. **TG auto-poster**: `D:/Portable_Soft/hermes/scripts/ai_tools_poster.py`
   - 7 post templates with site links
   - Posts to @ai_frontier_you channel
   - Cron: every 4 hours (job 183211c9b883)

3. **GitHub repo**: github.com/McDuck-S8/ai-tools-hub
   - Public repo, GitHub Pages enabled

## Goal Progress
- g-003-revenue: 5% → 30%
- Done: channel ✓, landing ✓, auto-posting ✓
- Missing: CPA links (Admitad/FinCPA registration), traffic, first conversion

## Pitfalls
- GitHub McDuck-S8 account restricted (trade controls) — public repos + Pages still work
- No CPA network registered yet — links are placeholders
- TG channel @ai_frontier_you already existed — reused, not created
- Salon bot needs separate SALON_BOT_TOKEN — not available

## Reuse Pattern
For next revenue test:
1. Create HTML landing in `microsites/`
2. Push to GitHub public repo
3. Enable GitHub Pages
4. Create/update TG poster script
5. Set up cron job
6. Update goal_queue progress

---
name: self-improvement-from-channels
description: Learn from Telegram AI channels and apply upgrades to Hermes skills
version: 1.0.0
tags: [self-improvement, channels, learning, upgrade]
---

# Self-Improvement from Telegram Channels

Automated learning loop that monitors AI channels and applies upgrades.

## How it Works

1. `telegram-monitor` cron job scans AI channels
2. `hermes_self_upgrade.py` extracts upgrade signals from report
3. Signals are saved to `cache/self_learnings/upgrade_signals.jsonl`
4. `self-upgrade-loop` cron job applies high-priority actions

## Channels Monitored

- **openai** — models, API, tools → provider-model-management skill
- **anthropic** — Claude, MCP, tool use → hermes-agent skill  
- **deepseek** — open-source models → cost optimization
- **hugging_face** — transformers, models → mlops skills
- **GoogleAI** — Gemini, agents → browser/vision skills

## Upgrade Signals

- `new_model` — New model release → update model registry
- `api_change` — API endpoint change → update integration skill
- `security` — Vulnerability/patch → check dependencies
- `new_tool` — New library/framework → evaluate for integration
- `pricing` — Cost change → optimize model selection
- `earning_opportunity` — CPA/affiliate program → evaluate for monetization

## CRITICAL: PRODUCE, Don't Just Monitor

**User correction:** "а что тебе говорит система?!!! что ты будешь делать с запущенными моделями????"

The monitoring loop is useless if it only collects news. After monitoring:
1. Extract ACTIONABLE signals (not just headlines)
2. Find specific opportunities (CPA offers, affiliate programs, tools)
3. CREATE content (articles, posts, guides)
4. DRIVE traffic (SEO, Reddit, Telegram)

Monitoring without production = wasted cycles. The goal is REVENUE, not reports.

## FREE MODELS ONLY

**User constraint:** User does NOT use paid APIs. All model recommendations must be free:
- opencode-zen (mimo-v2.5-free)
- Ollama (local, unlimited)
- FreeQwenApi (28 models via proxy)
- FreeDeepseekAPI (deepseek models via proxy)
- Google AI Studio (free tier)
- Groq (free tier)

Never suggest paid options. DeepSeek free is 5M tokens one-time, not sustainable.

## Files

- Script: `scripts/hermes_self_upgrade.py`
- Learnings: `cache/self_learnings/upgrade_signals.jsonl`
- Actions: `cache/telegram_monitor/pending_actions.json`
- Report: `cache/telegram_monitor/self_learn_report.md`

## Manual Run

```bash
python scripts/hermes_self_upgrade.py
```

## Adding New Channels

Edit `UPGRADE_CHANNELS` in the script:
```python
'channel_name': {
    'focus': ['keyword1', 'keyword2'],
    'apply_to': ['target_skill_path'],
},
```

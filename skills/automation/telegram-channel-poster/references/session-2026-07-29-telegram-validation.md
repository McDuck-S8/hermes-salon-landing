# Session Learnings — 2026-07-29: Telegram Channel Poster Integration

## Context
Validated Telegram Channel Poster skill in production as part of Free Traffic Launch Week 1.

## Key Validations

### 1. Bot & Channels — Production Ready
- **Bot:** `@max_brain_chef_bot` (ID: 8656692973) — token in `.env`, validated via `getMe`
- **4 channels** with bot as admin:
  - `@max_brain_chef_official` (-1003777013964) — "MAX BRAIN | AI & Agents"
  - `@ai_frontier_you` (-1003705792421) — "AI: Фронтир | Агентные системы"
  - `@max_brain_chef_ai` (-1003882833000) — "MAX BRAIN | AI & Agents"
  - `@neuro_kitchen_ai` (-1003525498743) — "НейроКухня | AI Recipes"

### 2. Posts Delivered Successfully
| Post | Channels | Status |
|------|----------|--------|
| Day 1: Infrastructure announcement | All 4 | ✅ Delivered |
| Day 1: Content with lead magnet button | All 4 | ✅ Delivered |
| Case study: Дарница +40% | All 4 | ✅ Delivered |

### 3. Lead Magnets Ready
- `lead_magnet_checklist.html` — "Автозапись в салоне за 15 мин" (PDF/HTML)
- `case_study_darnitsa.html` — Кейс +40% повторок, экономия 30к/мес

### 4. Webhook Handler Ready
- **File:** `scripts/tg_webhook_handler.py`
- **Port:** 8443
- **Handles:** `send_lead_magnet`, `send_case_study` callbacks
- **Needs:** ngrok tunnel + `TELEGRAM_WEBHOOK_URL` in `.env`

## Critical Technical Notes

### Bot Token Handling
- Token stored in `.env` as `TELEGRAM_BOT_TOKEN=8656692973:...`
- **Must load via `load_dotenv()`** — not available in raw `os.environ` without it
- All scripts must call `from dotenv import load_dotenv; load_dotenv()` first

### Channel ID Format
- Use integer chat_ids (negative for channels/groups)
- Example: `-1003777013964` not `"@max_brain_chef_official"`
- Verified via `getChat` API call

### Posting Best Practices
- Use `parse_mode="HTML"` for formatting
- `disable_web_page_preview=True` for clean links
- Inline keyboards work in channels (via `reply_markup`)
- Rate limit: ~30 messages/second burst, but space posts 1-2s apart

## Issues & Workarounds

### 1. Port 9003 = Chrome CDP, NOT BrowserOS
- Heartbeat reports BrowserOS HEALTHY because Chrome responds on 9003
- **BrowserOS daemon NOT running** — separate Python daemon needed
- For TikTok/IG automation: use `browser-harness` + Chrome CDP (9003) directly

### 2. ngrok Required for Webhook
```bash
ngrok http 8443
# Copy https URL → TELEGRAM_WEBHOOK_URL in .env
# Restart tg_webhook_handler.py
```

### 3. Ghost-surfer Profiles Need Manual Creation
```bash
cd skills/automation/ghost-surfer
python scripts/ghost_browser.py --create-profile --name beauty_main --proxy socks5://127.0.0.1:10806
python scripts/ghost_browser.py --create-profile --name education --proxy socks5://127.0.0.1:10806
python scripts/ghost_browser.py --create-profile --name services --proxy socks5://127.0.0.1:10806
```

## Integration with Free Traffic Workflow

### Telegram Nodes in `free_traffic_launch.json`
| Node | Skill | Phase |
|------|-------|-------|
| `telegram_setup` | `telegram-channel-poster` | Infra (parallel with content_generation) |
| `telegram_content_plan` | `telegram-channel-poster` | Execution (Day 1-7 posts) |

### Content Plan (Week 1)
| Day | Template | Description |
|-----|----------|-------------|
| 1 | `welcome_lead_magnet` | Приветствие + кнопка "ХОЧУ БОТА" |
| 2 | `case_study_darnitsa` | Кейс Дарница +40% |
| 3 | `expert_post_why_bots` | Почему боты лучше звонков |
| 4 | `qa_objections` | Разбор возражений + опрос |
| 5 | `quick_win_winback` | Как вернуть спящих за 5 мин |
| 6 | `scale_best_formats` | Масштаб лучших форматов |
| 7 | `week_audit_next_plan` | Итоги + план недели 2 |

## Commands for Production
```bash
# 1. Test post to all channels
cd /d/Portable_Soft/hermes && python scripts/test_telegram_post.py

# 2. Start webhook handler (after ngrok)
cd /d/Portable_Soft/hermes && python scripts/tg_webhook_handler.py

# 3. Run workflow
cd /d/Portable_Soft/hermes && python skills/software-development/workflow-supervisor-architecture/scripts/workflow_supervisor.py free_traffic_launch --inputs '{"niche":"beauty","sub_niche":"salon_automation","budget":0}'
```

## Metrics to Track
| Metric | Target Week 1 | Where |
|--------|---------------|-------|
| TG channel subs | >30 | @channelstat / bot |
| Profile clicks | >50 | TGStat / bot stats |
| Lead magnet downloads | >10 | Bot callback logs |
| DM questions | >5 | Bot inbox |
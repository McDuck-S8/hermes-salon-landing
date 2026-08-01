# Ghost-Surfer → TikTok Account Farm Integration

**Создано:** 2026-07-21
**Источник:** tiktok-account-farm skill + traffic-source-matrix

---

## Что уже работает

```
ghost-surfer/scripts/
├── ghost_browser.py       → FingerprintGenerator, IdentityDB, ProxyManager ✅
├── human_behavior.py      → HumanTyping, HumanScroll, HumanMouse ✅
├── posting.py             → TikTokPoster (базовый): login/upload/publish ✅
├── email_automation.py    → SMTPSender, IMAPReceiver (для email verify) ✅
└── account_registration.py→ ProfileGenerator, FormDetector ✅
```

## Что расширяет tiktok-account-farm

| Ghost-surfer модуль | TikTok Farm расширение |
|--------------------|----------------------|
| `posting.py:TikTokPoster` | anti-detect layer, CAPTCHA handler, session persist, multi-account queue |
| `ghost_browser.py:FingerprintGenerator` | Per-account fingerprint isolation + rotation on suspicion |
| `ghost_browser.py:IdentityDB` | TikTok farm DB (health, warmup stage, post history, ban flags) |
| `human_behavior.py` | Warmup sequence: view → like → save → follow → comment |
| `account_registration.py` | TikTok account creation via email/SMS verification |

## Новые файлы (из tiktok-account-farm)

```
tiktok_farm.py:      TikTokFarmOrchestrator (create/warmup/schedule/health)
tiktok_warmup.py:    WarmupEngine (iOS Voice Control / Android ADB / Desktop)
```

## Приоритет доработки TikTokPoster

1. **Anti-detect** — Fingerprint spoofing перед каждым входом (используй ghost_browser.py)
2. **CAPTCHA** — 2captcha/Anti-Captcha/CapMonster интеграция
3. **Session persist** — Cookies/LocalStorage между сессиями
4. **Rate limit** — Распознавание TikTok rate limit, backoff
5. **Upload unique** — ffmpeg LUT/crop/speed/pitch перед загрузкой
6. **Multi-account** — Queue с sequential processing

## Ресурсы

- `skills/automation/tiktok-account-farm/SKILL.md` — Полное описание фермы
- `skills/finance/arbitrage-execution/references/traffic-source-matrix.md` — Матрица всех источников

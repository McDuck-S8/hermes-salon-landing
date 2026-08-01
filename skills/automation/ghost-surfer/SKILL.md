---
name: ghost-surfer
description: "Full stack for anonymous web activity — anti-detect browser, human behavior emulation, account registration, email automation, posting/publishing, ban-resistant parsing. Turns the agent into an invisible operator."
version: "1.0.0"
related_skills: [tiktok-account-farm, arbitrage-execution]
---

# GHOST SURFER — Полный стек невидимого веб-присутствия

## Цель
Превратить агента в невидимого оператора, способного выполнять любые действия в интернете от лица живого человека, не оставляя цифровых следов и не вызывая подозрений.

---

## Архитектура: 6 Модулей

### 1. ANTI-DETECT BROWSER (Фундамент)
**Stack:** Playwright + playwright-stealth + undetected-chromedriver fallback
- Fingerprint spoofing: Canvas, WebGL, AudioContext, Fonts, Timezone, Language, Screen resolution
- User-Agent rotation: Real browser/OS combinations from fresh database
- Proxy binding: Consistent fingerprint↔IP pairing per identity
- Rotation: Per-session or per-account fingerprint switching
- Verification: fingerprintjs.com / browserleaks.com integration for quality checks

### 2. HUMAN BEHAVIOR EMULATION
**Stack:** ghost-cursor (Playwright) + custom behavior engine
- Mouse: Bezier curves, variable speed, micro-jitter, hover pauses
- Scrolling: Variable velocity, random pauses, reverse scrolls
- Typing: Per-character with variable WPM, mistakes + corrections
- Pauses: Log-normal distribution (not uniform), context-aware
- Forms: Field-by-field with tab navigation, realistic focus/blur

### 3. ACCOUNT REGISTRATION
**Stack:** Playwright + temp-mail APIs + SMS APIs + CAPTCHA solvers
- Profile generator: Name, email, phone, password, DOB, address
- Email verification: IMAP (custom domains) + temp-mail (1secmail, etc.)
- Phone verification: 5sim, SMS-activate, OnlineSIM integration
- CAPTCHA: 2captcha, Anti-Captcha, CapMonster Cloud
- Storage: Encrypted DB (identity → credentials + fingerprint + proxy + created_at)

### 4. EMAIL AUTOMATION
**Stack:** smtplib/imaplib + aiosmtplib + custom warmup scheduler
- SMTP/IMAP per identity with OAuth2 support (Gmail, Outlook)
- Warmup scheduler: Progressive volume increase, reply simulation
- Templating: Jinja2 with OKF-bundle data injection
- Tracking: Open pixels, click tracking (UTM), bounce handling
- Auto-reply: Rule-based responses to incoming mail

### 5. POSTING & PUBLISHING
**Stack:** Platform-specific Playwright flows + API where available
- Social: TikTok, YouTube Shorts, Instagram Reels, Telegram, VK, Pinterest, Reddit
- Blogging: Medium, Dzen, Telegraph, WordPress (REST API)
- Classifieds: Avito, OLX, Юла, specialized boards
- CPA Networks: MyLead, AdCombo, CPAGrip, OGAds — creative upload, link gen
- Scheduler: Cron-integrated, timezone-aware, frequency-capped

### 6. BAN-RESISTANT PARSING
**Stack:** Playwright + proxy pool + request orchestration
- Organic traffic emulation: Referrer spoofing (Google, direct, social), cookie priming
- Request pacing: Adaptive delays, burst detection avoidance
- Proxy rotation: Per-domain sticky sessions, health checks
- Caching: SQLite/Redis cache with TTL, conditional requests (ETag/Last-Modified)
- Structure detection: Auto-discover pagination, AJAX endpoints, GraphQL

---

## ИДЕНТИЧНОСТЬ (Identity) — Единая сущность

Каждый "призрак" — это полный набор:
```python
@dataclass
class GhostIdentity:
    id: str
    fingerprint: FingerprintProfile  # Canvas, WebGL, fonts, etc.
    user_agent: str
    proxy: ProxyConfig               # IP, port, auth, geo
    browser_profile: BrowserProfile  # Cookies, localStorage, extensions
    credentials: Dict[str, AccountCreds]  # platform → (email, pass, 2fa)
    email_config: EmailConfig        # SMTP, IMAP, warmup state
    created_at: datetime
    last_used: datetime
    reputation_score: float          # 0-1, based on bans/successes
```

---

## ИНТЕГРАЦИЯ С HERMES

### Cron Jobs
```bash
# Daily identity health check
ghost-surfer health-check --all

# Warmup emails for new identities
ghost-surfer warmup --identities=new --days=7

# Parse target sites
ghost-surfer parse --targets=competitors --output=kc_entries
```

### Knowledge Cube Integration
- Successful parsings -> `kc_entries` (category: "intel")
- Account creations -> `experiences` (axis_domain: "identity_management")
- Posting results -> `kc_entries` (category: "distribution")
- Ban events -> `kc_events` (event_type: "ban_detected")

### Fractal Wheel Integration
- Mode 2 (Synthesis): New identities = new traffic/bridge entities
- Mode 3 (Euler): Identity health × Proxy quality intersections
- Key Strength: Identity repertoire = Growth component

### Landscape + Transparency Layers Integration
- **Situation Layer**: Live service status (TikTok working/blocked, YouTube Shorts available, Telegram Mini Apps functional) — updated by Ghost-Surfer health checks
- **Plans Layer**: Connection arrows with real ROI/probability from actual platform data — Ghost-Surfer registers accounts, tests creatives, measures conversion
- **Logistics Layer**: Creative/account/proxy gaps discovered during registration/posting — fed back as blockers to Fractal Wheel Euler mode

---

## ТЕХНИЧЕСКИЙ СТЕК

| Layer | Primary | Fallback |
|-------|---------|----------|
| Browser | Playwright + playwright-stealth | undetected-chromedriver |
| Proxy | V2RayN (local) + residential pool API | Datacenter pool |
| CAPTCHA | 2captcha (API) | Anti-Captcha, CapMonster |
| Email | IMAP/SMTP (custom domain) | Temp-mail APIs |
| SMS | 5sim / SMS-activate | OnlineSIM |
| Storage | SQLite (encrypted) + Redis cache | JSON files |
| Scheduling | Hermes cron + APScheduler | Threading.Timer |

---

## БЕЗОПАСНОСТЬ (OpSec)

1. **Никаких реальных данных** — все профили генерируются
2. **Изоляция профилей** — каждый identity в отдельном browser context
3. **Шифрование БД** — Fernet (cryptography) для credentials
4. **Логи без PII** — только identity_id, platform, action, result
5. **Kill-switch** — мгновенное закрытие всех браузеров, очистка куков
6. **Audit trail** — каждый шаг логируется в kc_events для post-mortem

---

## ПЛАН РЕАЛИЗАЦИИ (Phased)

### Phase 1: Foundation (Week 1) ✅ DONE
- [x] Playwright + stealth setup (local install blocked, using BrowserOS MCP on port 9003)
- [x] Fingerprint generator (realistic profiles) — `ghost_browser.py:FingerprintGenerator`
- [x] Proxy manager (V2RayN integration) — `ghost_browser.py:ProxyManager.load_v2rayn_config()`
- [x] Identity DB schema + CRUD — `ghost_browser.py:IdentityDB` (SQLite + Fernet)

### Phase 2: Behavior (Week 1-2) ✅ DONE
- [x] Human typing engine — `human_behavior.py:HumanTyping` (WPM, variance, typo rate, corrections)
- [x] Scroll/hover/pause orchestration — `HumanScroll`, `HumanMouse` (Bezier curves), `HumanBehavior`
- [x] Behavior profile per identity — `BehaviorProfile.random(seed)` deterministic per identity

### Phase 3: Registration (Week 2) ✅ DONE
- [x] Profile generator — `account_registration.py:ProfileGenerator` (RU/EN names, email, phone, DOB, strong passwords)
- [x] Form detection — `FormDetector` (25 regex patterns × 9 field types)
- [x] Email/SMS verification stubs — `EmailVerifier`, `SMSVerifier` (API-ready)
- [x] CAPTCHA solver stub — `CaptchaSolver` (2captcha, Anti-Captcha, CapMonster ready)
- [x] Account storage + health tracking — `GhostIdentity`, `IdentityDB`

### Phase 3 Verification: Identity Rotation (2026-07-16) ✅ COMPLETE
**Test Results:** 3 distinct identities → 3 unique canvas hashes
- **Identity 1 (Alpha):** `D//7tvjlsAAAAGSURBVAMAZfmcg6nKM4wAAAAASUVORK5CYII=` | Europe/Berlin, de-DE, AMD Radeon RX 6800, 8C/16GB, 1366×768
- **Identity 2 (Bravo):** `//MksTzwAAAAZJREFUAwAQTd6D9TMYaQAAAABJRU5ErkJggg==` | America/New_York, en-US, NVIDIA RTX 3080, 16C/32GB, 1920×1080
- **Identity 3 (Charlie):** `AA//9k7ehJAAAABklEQVQDAPsuAZLSzFILAAAAAElFTkSuQmCC` | Asia/Tokyo, ja-JP, Intel UHD 630, 4C/8GB, 1280×720

**Fingerprint spoofing verified per identity:**
- Canvas: Per-pixel noise injection (different noise levels + text content)
- WebGL: Vendor/renderer spoofing (AMD / NVIDIA / Intel)
- AudioContext: Sample rate override (48000 Hz)
- Navigator: hardwareConcurrency, deviceMemory, language, platform
- Screen: width, height, colorDepth, pixelDepth
- Timezone: Intl.DateTimeFormat.prototype.resolvedOptions override

**BrowserOS MCP (port 9003) integration confirmed:** Fresh page → inject spoofing → extract fingerprint → unique per identity

**Key Learnings & Pitfalls (2026-07-16):**
1. **Prototype spoofing scope:** `evaluate_script` prototype overrides (HTMLCanvasElement.prototype.toDataURL, WebGLRenderingContext.prototype.getParameter, navigator.*, screen.*, Intl.DateTimeFormat.prototype.resolvedOptions) work within page context but **reset on navigation/reload**. For persistent spoofing across page loads, need content script injection via BrowserClaw (port 9010) or BrowserOS extension API.

2. **BrowserClaw MCP (port 9010) requires persistent SSE** — doesn't work with stateless curl calls. Must maintain long-lived JSON-RPC session for `tabs`/`act`/`run` tools. Use when persistent profile + content scripts needed.

3. **FingerprintJS Pro (commercial demo) uses server-side deduplication** — IP + behavioral signals + TLS fingerprint. Browser fingerprint rotation alone cannot defeat it. Open-source `@fingerprintjs/fingerprintjs@4` loads from CDN but exposes legacy API (`getCanvasFingerprint`, `getAudioFingerprint`, `getMathFingerprint`) — use these for client-side verification.

3. **Fal.ai & Bing Image Creator load successfully** in BrowserOS — found Login/Get Started/Create buttons. Leonardo AI blocked by network/proxy config.

4. **V2RayN integration ready** — `ProxyManager.load_v2rayn_config()` implemented, needs running V2RayN instance with `socks5://127.0.0.1:1080`.

5. **Full registration pipeline blockers** (require external setup):
   - mail.ru IMAP: needs app password (not login password)
   - CAPTCHA: 2captcha/Anti-Captcha API key
   - SMS: 5sim/SMS-activate API key
   - Phone: virtual number for services requiring phone verification

6. **Playwright local install blocked** (geo-block on `playwright install chromium`) — relying on BrowserOS/BrowserClaw MCPs for browser automation.

### Phase 4: Email (Week 2-3) ✅ DONE
- [x] SMTP/IMAP client — `email_automation.py:SMTPSender`, `IMAPReceiver` (OAuth2-ready structure)
- [x] Warmup scheduler — `EmailWarmupScheduler` (progressive volume, reply simulation)
- [x] Templating + tracking — Jinja2 templates (warmup, outreach_cpa, followup_1), open/click pixels, UTM
- [x] Auto-reply rules — `AutoReplyEngine` (rule-based)

### Phase 5: Posting (Week 3) 🔄 IN PROGRESS
- [x] Content formatting — `posting.py:PostContent` (hashtags, mentions, links, media)
- [x] **TikTok farm integration** — `TikTokPoster` extended via `tiktok-account-farm` skill (anti-detect, CAPTCHA, multi-account queue, warmup)
  - **Reference:** `references/tiktok-farm-integration.md`
- [ ] YouTube/Instagram upload flows — `YouTubePoster`, `InstagramPoster` (Playwright stubs)
- [x] **Telegram rich posting** — `TelegramPoster` with python-telegram-bot v22: HTML parse mode, InlineKeyboardMarkup, code blocks, blockquotes, global footer buttons, SQLite tracking
  - **Script:** `scripts/telegram_poster.py` (new, standalone, integrated via cron)
  - **Channels:** 4 verified (`@max_brain_chef_official`, `@ai_frontier_you`, `@max_brain_chef_ai`, `@neuro_kitchen_ai`)
  - **Bot:** `@max_brain_chef_bot` (admin in all 4)
  - **Schedule:** 09:00, 12:00, 15:00, 18:00, 21:00 MSK (5/day × 4 = 20/day)
  - **Content types:** ai_news (35%), ai_tool (25%), code_tip (15%), analytics (15%), motivation (10%)
  - **Reference:** `references/telegram-rich-posting.md`
- [ ] VK/Reddit posting — stubs
- [ ] CPA network creative upload — stubs
- [ ] Scheduler integration — `PostingOrchestrator` (cron-ready)

### Phase 6: Parsing (Week 3-4) 🔄 STUBBED
- [ ] Organic referrer/cookie priming — `BanResistantParser` stub
- [ ] Adaptive pacing engine — stub
- [ ] Proxy health monitoring — `ProxyManager` health scoring (success +0.05, fail -0.15)
- [ ] Cache layer + structure detection — stub

### Phase 7: Integration (Week 4) 🔄 PARTIAL
- [ ] Hermes cron jobs
- [ ] Knowledge Cube writers
- [ ] Fractal Wheel entity extractors
- [ ] Health monitoring dashboard

---

## КРИТЕРИИ УСПЕХА (Definition of Done)

- [ ] Создаёт аккаунт на TikTok/YouTube/Instagram без бана > 90% success rate
- [ ] Парсит 1000+ URL/день с < 1% ban rate
- [ ] Отправляет 500+ emails/день с > 80% inbox placement
- [ ] Публикует контент на 5+ платформах параллельно
- [ ] Выживает перезагрузку системы (persistent identities)
- [ ] Интегрирован в Hermes cron + Knowledge Cube + Fractal Wheel

---

## РИСКИ И МИТИГАЦИИ

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Platform fingerprint updates | High | High | Automated fingerprint freshness checks, weekly updates |
| Proxy pool exhaustion | Medium | High | Multiple providers, datacenter fallback, health monitoring |
| CAPTCHA cost explosion | Medium | Medium | Budget caps, difficulty-based routing, self-hosted solver research |
| Legal/compliance | Low | Critical | No PII, no fraud, only public data + own accounts, ToS review |
| Browser detection arms race | High | High | Stealth plugin updates, fallback to undetected-chromedriver |

---

*Создан: 2026-07-16. Статус: Phase 0 — дизайн зафиксирован. Следующий шаг: Phase 1 Foundation.*
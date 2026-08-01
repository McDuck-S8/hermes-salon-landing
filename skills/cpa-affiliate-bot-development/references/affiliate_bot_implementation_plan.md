# Affiliate Bot Implementation Plan: RF Market Adaptation

## Task: t_affiliate_bot - Build affiliate bot: adapt Tara Bot for RF market

### Objective
Fork and adapt an existing Telegram affiliate bot framework for the Russian Federation (RF) market, integrating three major CPA networks:
- **MyLead** (mylead.global) - Global CPA network with API
- **Admitad** (admitad.com) - Global affiliate network with Python SDK
- **KMA.biz** (kma.biz) - CIS-focused CPA network (nutra, ecom)

---

## Architecture Overview

### Core Components

```
affiliate_bot/
├── bot/
│   ├── __init__.py
│   ├── main.py                 # Entry point, aiogram 3.x setup
│   ├── config.py               # Settings, tokens, API keys
│   ├── handlers/
│   │   ├── __init__.py
│   │   ├── commands.py         # /start, /help, /offers, /links
│   │   ├── callbacks.py        # Inline keyboard handlers
│   │   ├── messages.py         # Link detection, auto-conversion
│   │   └── admin.py            # Admin panel commands
│   ├── middlewares/
│   │   ├── __init__.py
│   │   ├── auth.py             # User authorization
│   │   ├── logging.py          # Request/response logging
│   │   └── rate_limit.py       # Flood control
│   ├── keyboards/
│   │   ├── __init__.py
│   │   ├── inline.py           # Offer cards, pagination
│   │   └── reply.py            # Main menu, settings
│   └── utils/
│       ├── __init__.py
│       ├── formatters.py       # Message formatting (HTML/Markdown)
│       ├── validators.py       # URL validation, offer parsing
│       └── helpers.py          # Common utilities
├── integrations/
│   ├── __init__.py
│   ├── base.py                 # Base CPA Network adapter
│   ├── mylead/
│   │   ├── __init__.py
│   │   ├── api.py              # MyLead API client
│   │   ├── models.py           # Offer, Category, Payout models
│   │   └── link_generator.py   # Deep link generation
│   ├── admitad/
│   │   ├── __init__.py
│   │   ├── api.py              # Admitad API client (OAuth2)
│   │   ├── models.py
│   │   └── link_generator.py
│   └── kmabiz/
│       ├── __init__.py
│       ├── api.py              # KMA.biz API client
│       ├── models.py
│       └── link_generator.py
├── database/
│   ├── __init__.py
│   ├── models.py               # SQLAlchemy models
│   ├── crud.py                 # Database operations
│   └── session.py              # Async session management
├── services/
│   ├── __init__.py
│   ├── offer_sync.py           # Periodic offer synchronization
│   ├── link_tracker.py         # Click/conversion tracking
│   ├── notification.py         # User notifications (new offers, payouts)
│   └── analytics.py            # Stats aggregation
├── scheduler/
│   ├── __init__.py
│   └── jobs.py                 # APScheduler jobs
├── tests/
│   ├── __init__.py
│   ├── test_mylead.py
│   ├── test_admitad.py
│   ├── test_kmabiz.py
│   └── test_bot.py
├── docker/
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── .env.example
├── requirements.txt
├── pyproject.toml
├── README.md
└── .env.example
```

---

## CPA Network API Integration Details

### 1. MyLead (mylead.global)

**API Documentation**: https://strackr.com/docs/mylead (via Strackr) or direct API
- **Authentication**: API Key (header: `Authorization: Bearer <api_key>`)
- **Base URL**: `https://api.mylead.global/v1` (verify current endpoint)
- **Key Endpoints**:
  - `GET /offers` - List offers with filters (category, country, payout)
  - `GET /offers/{id}` - Offer details
  - `GET /categories` - Offer categories
  - `POST /links/generate` - Generate affiliate link with subid
  - `GET /reports/conversions` - Conversion reports
  - `GET /reports/clicks` - Click reports
  - `GET /balance` - Current balance
  - `GET /payouts` - Payout history

**Python Library**: No official SDK. Use `httpx`/`aiohttp` with custom wrapper.

**Integration Priority**: HIGH - Good API, global offers, crypto/nutra verticals

### 2. Admitad (admitad.com)

**API Documentation**: https://developers.mitgo.com/hc/en-us/categories/34481291136402-Admitad-API-for-Publishers
- **Authentication**: OAuth2 (Client Credentials flow)
  - `client_id` + `client_secret` → Access Token (1 hour TTL)
  - Refresh token flow for long-lived access
- **Base URL**: `https://api.admitad.com/`
- **Python SDK**: Official `admitad-python-api` (https://github.com/admitad/admitad-python-api)
- **Key Endpoints**:
  - `GET /advcampaigns/` - List affiliate programs
  - `GET /advcampaigns/{id}/` - Program details
  - `GET /coupons/` - Coupons/deals
  - `POST /deeplink/` - Generate deep links with subid
  - `GET /reports/` - Statistics (clicks, actions, earnings)
  - `GET /payments/` - Payouts
  - `GET /referrals/` - Sub-affiliate network

**Integration Priority**: HIGH - Official Python SDK, robust API, many RU/CIS offers

### 3. KMA.biz (kma.biz)

**API Documentation**: Limited public docs. Contact support for API access.
- **Authentication**: Likely API Key or POST login → session cookie
- **Base URL**: `https://kma.biz/api/` (verify)
- **Key Endpoints** (estimated):
  - `GET /offers` - List offers
  - `GET /offers/{id}` - Offer details
  - `POST /links/create` - Create tracking link
  - `GET /stats` - Statistics
  - `GET /balance` - Balance
  - `GET /payouts` - Payout history

**Integration Priority**: MEDIUM - CIS-focused, nutra/white goods, daily payouts
**Risk**: Limited public API docs, may need manual integration or scrape

---

## Bot Features Specification

### Core User Features

| Feature | Description | Priority |
|---------|-------------|----------|
| `/start` | Onboarding, language selection (RU/EN), referral link | P0 |
| `/offers` | Browse offers with filters (category, GEO, payout, network) | P0 |
| `/my_links` | User's generated affiliate links with stats | P0 |
| `/stats` | Personal dashboard: clicks, leads, earnings, CR | P0 |
| `/settings` | Notification preferences, default subid, networks | P1 |
| `/balance` | Combined balance across networks | P1 |
| `/payouts` | Payout history, request withdrawal | P1 |
| Auto-link conversion | Detect URLs in messages, convert to affiliate links | P0 |
| Channel posting | Forward offer cards to channels with tracking | P1 |
| SubID management | Auto-generate subids per user/channel/campaign | P0 |

### Admin Features

| Feature | Description | Priority |
|---------|-------------|----------|
| `/admin` | Admin panel with stats overview | P1 |
| `/admin/sync` | Manual offer synchronization | P1 |
| `/admin/users` | User management, ban/unban | P2 |
| `/admin/networks` | Toggle networks, configure API keys | P1 |
| `/admin/broadcast` | Broadcast messages to users | P2 |

### Technical Features

| Feature | Description | Priority |
|---------|-------------|----------|
| Multi-network offer aggregation | Unified offer catalog from all 3 networks | P0 |
| Smart link routing | Route to best network per offer/GEO | P1 |
| Click tracking | Postback handling, S2S integration | P1 |
| Rate limiting | Per-user, per-network API limits | P0 |
| Caching | Redis cache for offers, user sessions | P0 |
| Logging/Monitoring | Structured logs, error tracking (Sentry) | P1 |
| Docker deployment | Multi-stage build, health checks | P1 |

---

## Database Schema (SQLAlchemy + AsyncPG)

```python
# Core tables
users:
  - id (PK, BigInteger) - Telegram user_id
  - username, first_name, last_name
  - language_code (RU/EN)
  - is_active, is_banned, is_admin
  - default_subid
  - created_at, updated_at
  - settings (JSONB) - notifications, preferences

user_network_credentials:
  - id (PK)
  - user_id (FK)
  - network (Enum: MYLEAD, ADMITAD, KMABIZ)
  - api_key_encrypted / oauth_tokens_encrypted
  - is_active
  - created_at

offers:
  - id (PK)
  - network (Enum)
  - external_id (network's offer ID)
  - name, description
  - category, vertical
  - geo (JSONB: countries array)
  - payout_type (CPA/CPL/CPS/RevShare)
  - payout_value (Decimal)
  - currency
  - preview_url, landing_url
  - status (active/paused/stopped)
  - raw_data (JSONB) - full API response
  - synced_at
  - created_at

user_links:
  - id (PK)
  - user_id (FK)
  - offer_id (FK)
  - network
  - tracking_url
  - subid
  - clicks (Integer, default 0)
  - conversions (Integer, default 0)
  - earnings (Decimal, default 0)
  - created_at

clicks:
  - id (PK)
  - user_link_id (FK)
  - ip_hash
  - user_agent
  - referer
  - country
  - timestamp
  - converted (Boolean)
  - conversion_data (JSONB)

conversions:
  - id (PK)
  - user_link_id (FK)
  - click_id (FK, nullable)
  - network_conversion_id
  - payout
  - currency
  - status (pending/approved/rejected)
  - subid1..subid5
  - created_at
  - updated_at

sync_logs:
  - id (PK)
  - network
  - status (success/partial/failed)
  - offers_fetched, offers_new, offers_updated
  - error_message
  - started_at, completed_at
```

---

## Implementation Phases

### Phase 1: Foundation (Week 1)
- [ ] Project structure, config management (pydantic-settings)
- [ ] Database setup (SQLAlchemy 2.0 + AsyncPG + Alembic)
- [ ] Bot skeleton (aiogram 3.x + Redis storage)
- [ ] Docker compose (bot, postgres, redis)
- [ ] CI/CD pipeline (GitHub Actions)

### Phase 2: CPA Network Integrations (Week 2)
- [ ] Base adapter interface
- [ ] MyLead API client + sync job
- [ ] Admitad API client (OAuth2) + sync job
- [ ] KMA.biz API client + sync job (may need manual work)
- [ ] Unified offer catalog with deduplication
- [ ] Scheduled sync (every 6 hours via APScheduler)

### Phase 3: Bot Core Features (Week 3)
- [ ] User registration, settings
- [ ] Offer browsing (categories, filters, pagination)
- [ ] Affiliate link generation with subids
- [ ] Auto-link conversion in messages
- [ ] Personal stats dashboard
- [ ] Balance/payouts display

### Phase 4: Advanced Features (Week 4)
- [ ] Click tracking (redirect endpoint + postback handlers)
- [ ] S2S postback endpoints for each network
- [ ] Channel/group posting with tracking
- [ ] Admin panel
- [ ] Notifications (new offers, conversions, payouts)
- [ ] Referral system (sub-affiliates)

### Phase 5: Production Hardening (Week 5)
- [ ] Load testing, rate limiting
- [ ] Monitoring (Prometheus + Grafana)
- [ ] Error tracking (Sentry)
- [ ] Backup/restore procedures
- [ ] Documentation (README, API docs, deployment guide)
- [ ] Security audit (token encryption, SQL injection)

---

## Configuration (.env.example)

```env
# Bot
BOT_TOKEN=123456:ABC-DEF...
ADMIN_IDS=123456789,987654321
BOT_LANGUAGE=ru

# Database
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/affiliate_bot
REDIS_URL=redis://localhost:6379/0

# MyLead
MYLEAD_API_KEY=your_api_key
MYLEAD_BASE_URL=https://api.mylead.global/v1
MYLEAD_SYNC_ENABLED=true

# Admitad
ADMITAD_CLIENT_ID=your_client_id
ADMITAD_CLIENT_SECRET=your_client_secret
ADMITAD_REDIRECT_URI=https://yourdomain.com/callback
ADMITAD_SCOPES=public_data,advcampaigns,deeplink,reports,payments,referrals
ADMITAD_SYNC_ENABLED=true

# KMA.biz
KMABIZ_API_KEY=your_api_key
KMABIZ_BASE_URL=https://kma.biz/api
KMABIZ_SYNC_ENABLED=true

# Security
SECRET_KEY=generate_with_openssl_rand_hex_32
ENCRYPTION_KEY=generate_with_fernet_generate_key

# Monitoring
SENTRY_DSN=https://xxx@sentry.io/xxx
LOG_LEVEL=INFO
```

---

## Security Considerations

1. **API Key Encryption**: Encrypt user-provided API keys at rest using Fernet (cryptography)
2. **OAuth2 Tokens**: Store refresh tokens encrypted, rotate access tokens
3. **Rate Limiting**: Implement per-user and per-network limits
4. **Input Validation**: Validate all URLs, subids, callback data
5. **Admin Access**: Restrict admin commands to ADMIN_IDS only
6. **HTTPS Only**: Enforce TLS for webhook mode
7. **Audit Logging**: Log all admin actions, credential changes

---

## Testing Strategy

| Layer | Tools | Coverage Target |
|-------|-------|-----------------|
| Unit | pytest, pytest-asyncio, httpx-mock | 80%+ |
| Integration | testcontainers (postgres, redis) | Key flows |
| E2E | aiogram test utilities | Critical paths |
| Load | locust | 1000 concurrent users |

---

## Deployment Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Telegram  │────▶│   Nginx     │────▶│   Bot App   │
│   Webhook   │     │   (SSL)     │     │  (x3 pods)  │
└─────────────┘     └─────────────┘     └──────┬──────┘
                                               │
                    ┌─────────────┐            │
                    │  PostgreSQL │◀───────────┤
                    │  (Primary)  │            │
                    └─────────────┘            │
                                               │
                    ┌─────────────┐            │
                    │    Redis    │◀───────────┤
                    │  (Cluster)  │            │
                    └─────────────┘            │
                                               ▼
                    ┌─────────────┐     ┌─────────────┐
                    │  Scheduler  │     │  Redirect   │
                    │  (APScheduler)     │  Service    │
                    └─────────────┘     └─────────────┘
```

---

## Risk Assessment & Mitigation

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| KMA.biz API undocumented | High | Medium | Start with MyLead+Admitad, add KMA later; contact support |
| API rate limits | Medium | High | Implement adaptive rate limiting, caching |
| Offer data inconsistency | Medium | Medium | Normalization layer, validation rules |
| Telegram bot API changes | Low | High | Pin aiogram version, monitor changelog |
| User credential leakage | Low | Critical | Encryption at rest, no logging of secrets |

---

## Success Metrics

- **MVP Launch**: Bot responds to `/start`, shows offers from 2+ networks
- **Week 2**: 100+ offers synced, link generation working
- **Week 4**: 10+ active users, 100+ clicks tracked
- **Month 2**: 100+ users, positive ROI on test campaigns

---

## Next Steps

1. **Create GitHub repository** with initial structure
2. **Set up development environment** (Docker, pre-commit, CI)
3. **Implement MyLead integration first** (simplest API)
4. **Add Admitad OAuth2 flow** (most complex auth)
5. **Investigate KMA.biz API** (contact support for docs)
6. **Build core bot handlers** in parallel

---

## References

- [aiogram 3.x Documentation](https://docs.aiogram.dev/)
- [Admitad Python API](https://github.com/admitad/admitad-python-api)
- [MyLead API via Strackr](https://strackr.com/docs/mylead)
- [KMA.biz Affiliate Network](https://kma.biz)
- [Telegram Bot API 8.0+](https://core.telegram.org/bots/api)
- [SQLAlchemy 2.0 Async](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)

---

*Document created: 2026-07-13*
*Task: t_affiliate_bot*
*Status: Planning complete, ready for implementation*
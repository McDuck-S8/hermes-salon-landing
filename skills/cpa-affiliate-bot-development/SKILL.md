---
name: cpa-affiliate-bot-development
version: "1.0.0"
description: Class-level skill for developing Telegram affiliate bots integrated with CPA networks (MyLead, Admitad, KMA.biz, etc.). Covers architecture, API integration patterns, database schema, multi-network offer aggregation, link generation with subid tracking, click/conversion tracking via postbacks, and phased implementation roadmap.
category: devops
tags:
  - telegram-bot
  - cpa-networks
  - affiliate-marketing
  - mylead
  - admitad
  - kmabiz
  - aiogram
  - python
  - postback-tracking
author: hermes
created_at: "2026-07-13"
updated_at: "2026-07-13"
---

## Session Notes (2026-07-13)
- Task: t_affiliate_bot - Build affiliate bot: adapt Tara Bot for RF market
- Research completed on 3 CPA networks: MyLead, Admitad, KMA.biz
- Created comprehensive implementation plan at docs/affiliate_bot_implementation_plan.md
- Created reference documentation at references/cpa_network_api_reference.md
- Architecture: aiogram 3.x, SQLAlchemy 2.0 + AsyncPG, Redis, APScheduler
- 5-phase implementation roadmap (5 weeks to production)
- Key finding: MyLead has simple API key auth, Admitad uses OAuth2 with official SDK, KMA.biz has limited public docs

## Session Notes (2026-07-14)
- Task: Adapt Tara Bot (thaolst/tara-bot) for Russian market with CPA networks
- Successfully forked and adapted Tara Bot v2.0 (Claude Sonnet 4.6 + python-telegram-bot v20+)
- Created tara-bot-ru with:
  - SerpAPI integration for Google Flights + Google Shopping (Russian cities, RUB currency)
  - CPA affiliate link injection: MyLead, Admitad, KMA.biz via new `cpa_links.py` tool
  - Multi-LLM support: Anthropic (primary) + OpenAI-compatible (Gemini, local LLMs)
  - Prompt caching (Anthropic) for ~90% token cost reduction
  - Session memory with user profile extraction (preferred departure city)
  - Fly.io deployment (Frankfurt region, shared CPU 1GB)
  - GitHub Actions daily monitor (06:00 UTC = 09:00 MSK) for flight price alerts
  - Docker + health check endpoint for Fly.io
  - Russian language system prompt with CPA affiliate instructions
- Key pattern: Tool definitions with async wrappers → sync execution via `asyncio.to_thread`
- Key pattern: Per-user asyncio.Lock for sequential message processing
- Cost: ~$0.50/month (Fly.io free tier + SerpAPI 250 free + Anthropic $5 credit)

# CPA Affiliate Bot Development Skill

## Purpose
Build production-ready Telegram affiliate bots that aggregate offers from multiple CPA networks, generate tracked affiliate links with subid management, handle click/conversion postbacks, and provide user dashboards for earnings tracking.

## When to Use
- Creating a new affiliate bot for CPA arbitrage
- Integrating additional CPA networks into existing bot
- Adding postback tracking for conversion attribution
- Building admin panels for offer/user management

## Architecture Overview

### Core Components
```
affiliate_bot/
├── bot/                    # Telegram bot (aiogram 3.x)
│   ├── handlers/          # Command & callback handlers
│   ├── middlewares/       # Auth, logging, rate limiting
│   ├── keyboards/         # Inline & reply keyboards
│   └── utils/             # Formatters, validators
├── integrations/          # CPA network adapters
│   ├── base.py           # Abstract base adapter
│   ├── mylead/           # MyLead API client
│   ├── admitad/          # Admitad OAuth2 client
│   └── kmabiz/           # KMA.biz client
├── database/              # SQLAlchemy 2.0 + AsyncPG
│   ├── models.py         # User, Offer, Link, Click, Conversion
│   ├── crud.py           # Database operations
│   └── session.py        # Async session management
├── services/              # Business logic
│   ├── offer_sync.py     # Periodic offer synchronization
│   ├── link_tracker.py   # Click/conversion tracking
│   ├── notification.py   # User notifications
│   └── analytics.py      # Stats aggregation
├── scheduler/             # APScheduler jobs
└── tests/                 # pytest + httpx-mock
```

### Key Design Patterns

**Adapter Pattern for CPA Networks**
```python
class CPANetworkAdapter(ABC):
    @abstractmethod
    async def fetch_offers(self, filters: OfferFilters) -> list[Offer]:
        pass
    
    @abstractmethod
    async def generate_link(self, offer_id: str, subid: str) -> TrackingLink:
        pass
    
    @abstractmethod
    async def get_stats(self, date_from: date, date_to: date) -> NetworkStats:
        pass
    
    @abstractmethod
    async def handle_postback(self, payload: dict) -> ConversionResult:
        pass
```

**Unified Offer Model**
```python
@dataclass
class UnifiedOffer:
    id: str                    # Internal UUID
    network: NetworkEnum       # MYLEAD | ADMITAD | KMABIZ
    external_id: str          # Network's offer ID
    name: str
    description: str
    category: str
    vertical: str
    geo: list[str]            # Country codes
    payout_type: PayoutType   # CPA | CPL | CPS | REVSHARE
    payout_value: Decimal
    currency: str
    preview_url: str
    landing_url: str
    status: OfferStatus
    raw_data: dict            # Full API response for debugging
    synced_at: datetime
```

## CPA Network Integration Details

### MyLead (mylead.global)
- **Auth**: API Key (`Authorization: Bearer <key>`)
- **Base URL**: `https://api.mylead.global/v1` (verify current)
- **SDK**: None - use `httpx.AsyncClient` with custom wrapper
- **Key Endpoints**:
  - `GET /offers` - Filter by category, country, payout
  - `GET /offers/{id}` - Full offer details
  - `POST /links/generate` - Create tracking link with subid
  - `GET /reports/conversions` - Conversion data
  - `GET /balance` - Current balance
- **Rate Limits**: ~60 req/min (implement adaptive backoff)

### Admitad (admitad.com)
- **Auth**: OAuth2 Client Credentials + Refresh Token
- **Base URL**: `https://api.admitad.com/`
- **SDK**: Official `admitad-python-api` (pip install admitad)
- **Scopes**: `public_data advcampaigns deeplink reports payments referrals`
- **Key Endpoints**:
  - `GET /advcampaigns/` - Affiliate programs with filters
  - `POST /deeplink/` - Generate deep links
  - `GET /reports/` - Clicks, actions, earnings
  - `GET /payments/` - Payout history
  - `GET /referrals/` - Sub-affiliate network
- **Token TTL**: 1 hour access, refresh token for renewal

### KMA.biz (kma.biz)
- **Auth**: API Key or Session Cookie (contact support)
- **Base URL**: `https://kma.biz/api/` (verify)
- **SDK**: None - custom implementation
- **Status**: Limited public docs - may need manual integration
- **Priority**: MEDIUM (CIS-focused, nutra/white goods, daily payouts)

## Database Schema (SQLAlchemy 2.0)

### Core Tables
```sql
-- Users (Telegram users)
CREATE TABLE users (
    id BIGINT PRIMARY KEY,           -- Telegram user_id
    username VARCHAR(255),
    first_name VARCHAR(255),
    last_name VARCHAR(255),
    language_code VARCHAR(10) DEFAULT 'ru',
    is_active BOOLEAN DEFAULT TRUE,
    is_banned BOOLEAN DEFAULT FALSE,
    is_admin BOOLEAN DEFAULT FALSE,
    default_subid VARCHAR(100),
    settings JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- User CPA network credentials (encrypted)
CREATE TABLE user_network_credentials (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(id),
    network VARCHAR(50) NOT NULL,    -- MYLEAD, ADMITAD, KMABIZ
    api_key_encrypted BYTEA,         -- Fernet encrypted
    oauth_tokens_encrypted BYTEA,    -- For Admitad
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Unified offer catalog
CREATE TABLE offers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    network VARCHAR(50) NOT NULL,
    external_id VARCHAR(255) NOT NULL,
    name VARCHAR(500) NOT NULL,
    description TEXT,
    category VARCHAR(100),
    vertical VARCHAR(100),
    geo JSONB NOT NULL DEFAULT '[]',
    payout_type VARCHAR(20),         -- CPA, CPL, CPS, REVSHARE
    payout_value NUMERIC(10,2),
    currency VARCHAR(3) DEFAULT 'USD',
    preview_url TEXT,
    landing_url TEXT,
    status VARCHAR(20) DEFAULT 'active',
    raw_data JSONB,
    synced_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(network, external_id)
);

-- User-generated tracking links
CREATE TABLE user_links (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id BIGINT REFERENCES users(id),
    offer_id UUID REFERENCES offers(id),
    network VARCHAR(50) NOT NULL,
    tracking_url TEXT NOT NULL,
    subid VARCHAR(255) NOT NULL,
    clicks INT DEFAULT 0,
    conversions INT DEFAULT 0,
    earnings NUMERIC(12,2) DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Click tracking
CREATE TABLE clicks (
    id BIGSERIAL PRIMARY KEY,
    user_link_id UUID REFERENCES user_links(id),
    ip_hash VARCHAR(64),
    user_agent TEXT,
    referer TEXT,
    country CHAR(2),
    converted BOOLEAN DEFAULT FALSE,
    conversion_data JSONB,
    timestamp TIMESTAMPTZ DEFAULT NOW()
);

-- Conversions (postback data)
CREATE TABLE conversions (
    id BIGSERIAL PRIMARY KEY,
    user_link_id UUID REFERENCES user_links(id),
    click_id BIGINT REFERENCES clicks(id),
    network_conversion_id VARCHAR(255),
    payout NUMERIC(12,2),
    currency VARCHAR(3) DEFAULT 'USD',
    status VARCHAR(20) DEFAULT 'pending',  -- pending, approved, rejected
    subid1 VARCHAR(255),
    subid2 VARCHAR(255),
    subid3 VARCHAR(255),
    subid4 VARCHAR(255),
    subid5 VARCHAR(255),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Sync logs for monitoring
CREATE TABLE sync_logs (
    id BIGSERIAL PRIMARY KEY,
    network VARCHAR(50) NOT NULL,
    status VARCHAR(20) NOT NULL,        -- success, partial, failed
    offers_fetched INT DEFAULT 0,
    offers_new INT DEFAULT 0,
    offers_updated INT DEFAULT 0,
    error_message TEXT,
    started_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);
```

## Implementation Phases

### Phase 1: Foundation (Week 1)
- [ ] Project structure, pydantic-settings config
- [ ] Database: SQLAlchemy 2.0 + AsyncPG + Alembic migrations
- [ ] Bot skeleton: aiogram 3.x + Redis storage (FSM)
- [ ] Docker: multi-stage build, docker-compose (bot, postgres, redis)
- [ ] CI/CD: GitHub Actions (lint, test, build, deploy)

### Phase 2: CPA Integrations (Week 2)
- [ ] Base adapter interface + registry
- [ ] MyLead: API client + sync job (cron: 0 */6 * * *)
- [ ] Admitad: OAuth2 client + sync job (use official SDK)
- [ ] KMA.biz: API client + sync job (investigate API first)
- [ ] Unified offer catalog with deduplication logic
- [ ] Admin command: `/admin/sync [network]`

### Phase 3: Bot Core (Week 3)
- [ ] User onboarding: `/start` → language → referral
- [ ] Offer browsing: `/offers` with inline keyboard filters
- [ ] Link generation: `/link <offer_id>` → tracking URL
- [ ] Auto-link conversion: message handler detects URLs
- [ ] Personal dashboard: `/stats` with charts (text-based)
- [ ] Balance/payouts: `/balance`, `/payouts`

### Phase 4: Advanced (Week 4)
- [ ] Click tracking: redirect endpoint + click logging
- [ ] Postback handlers: per-network webhook endpoints
- [ ] Channel posting: forward offer cards with tracking
- [ ] Admin panel: users, networks, broadcasts
- [ ] Notifications: new offers, conversions, payouts
- [ ] Referral system: sub-affiliate tracking

### Phase 5: Hardening (Week 5)
- [ ] Rate limiting: per-user, per-network (token bucket)
- [ ] Caching: Redis for offers, user sessions, stats
- [ ] Monitoring: Prometheus metrics + Grafana dashboards
- [ ] Error tracking: Sentry integration
- [ ] Security audit: token encryption, SQL injection, XSS
- [ ] Load testing: Locust (1000 concurrent users)
- [ ] Documentation: README, API docs, deployment guide

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
KMABIZ_SYNC_ENABLED=false

# Security
SECRET_KEY=generate_with_openssl_rand_hex_32
ENCRYPTION_KEY=generate_with_fernet_generate_key

# Monitoring
SENTRY_DSN=https://xxx@sentry.io/xxx
LOG_LEVEL=INFO
```

## Security Checklist

- [ ] Encrypt all API keys/OAuth tokens at rest (Fernet)
- [ ] Never log credentials or full URLs with tokens
- [ ] Validate all callback data (sign or HMAC)
- [ ] Rate limit all public endpoints
- [ ] Admin commands restricted to ADMIN_IDS only
- [ ] HTTPS only for webhook mode (nginx + certbot)
- [ ] Regular dependency updates (dependabot)
- [ ] Audit postback payloads before processing

## Testing Strategy

| Layer | Tools | Target |
|-------|-------|--------|
| Unit | pytest, pytest-asyncio, httpx-mock | 80%+ coverage |
| Integration | testcontainers (postgres, redis) | Key flows |
| E2E | aiogram test utilities | Critical paths |
| Load | locust | 1000 concurrent users |

## Common Pitfalls & Solutions

| Pitfall | Solution |
|---------|----------|
| Offer data inconsistency across networks | Normalization layer with validation rules |
| API rate limits during sync | Adaptive backoff, stagger sync times |
| Postback duplicate processing | Idempotency keys (network_conversion_id) |
| SubID length limits per network | Truncate/hash to fit, store mapping |
| Telegram message length limits | Paginate offers, use "View More" buttons |
| Webhook vs polling mode | Support both, webhook for production |

## Monitoring & Alerts

- **Sync Health**: Alert if sync fails 2+ times in a row
- **API Errors**: Alert on 5xx or rate limit hits
- **Conversion Drop**: Alert if conversions/day < 50% of 7-day avg
- **Bot Uptime**: Health check endpoint + external monitor
- **Database**: Connection pool usage, slow queries

## References

- [aiogram 3.x Docs](https://docs.aiogram.dev/)
- [Admitad Python API](https://github.com/admitad/admitad-python-api)
- [MyLead API via Strackr](https://strackr.com/docs/mylead)
- [KMA.biz Affiliate Network](https://kma.biz)
- [Telegram Bot API 8.0+](https://core.telegram.org/bots/api)
- [SQLAlchemy 2.0 Async](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
- [APScheduler](https://apscheduler.readthedocs.io/)
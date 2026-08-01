# Tara Bot RU Adaptation — Reference (2026-07-14)

## Source
Original: [thaolst/tara-bot](https://github.com/thaolst/tara-bot) — MIT License
- AI Telegram agent for Vietnam market (flight search, price comparison, lucky dates)
- Tech: python-telegram-bot v20+, Anthropic Claude Sonnet 4.6, SerpAPI, Fly.io, GitHub Actions
- 59 stars, 66 forks, 45 commits

## Adaptation Summary

### What Changed
| Component | Original (VN) | Adapted (RU) |
|-----------|---------------|--------------|
| Cities | VN IATA (SGN, HAN, DAD, PQC, CXR...) | RU/CIS IATA (MOW, LED, AER, OVB, SVX, KZN, VVO, KHV, ALA, TSE, KBP, MSQ...) |
| Currency | VND | RUB |
| Language | Vietnamese | Russian |
| CPA Networks | None (planned) | MyLead, Admitad, KMA.biz |
| Lucky Dates | Vietnamese Can Chi calendar | Removed (not relevant for RU) |
| Deployment | Fly.io Singapore | Fly.io Frankfurt |

### New Files Added
```
tara-bot-ru/
├── src/
│   ├── tools/
│   │   ├── cpa_links.py      # NEW: CPA network integration (3 networks)
│   │   └── serpapi.py        # MODIFIED: RU cities, RUB, affiliate injection
│   ├── agents.py             # MODIFIED: Russian prompt, CPA tools, user profile
│   ├── bot.py                # MODIFIED: Russian messages, health check
│   └── config.py             # MODIFIED: CPA API keys
├── scripts/
│   └── monitor.py            # MODIFIED: RU routes (MOW→AER, MOW→LED, etc.)
├── .github/workflows/
│   └── monitor.yml           # MODIFIED: 06:00 UTC = 09:00 MSK
├── fly.toml                  # MODIFIED: region Frankfurt
├── DEPLOY.md                 # NEW: Complete RU deployment guide
├── README.md                 # NEW: Feature list, tech stack, costs
├── CHANGELOG.md              # NEW: v1.0.0 release notes
├── pyproject.toml            # MODIFIED: Added serpapi dep
└── run_bot.sh                # MODIFIED: venv-based local runner
```

### CPA Integration Pattern (`src/tools/cpa_links.py`)

```python
# Adapter pattern for multi-network support
CPA_NETWORKS = {
    "mylead": {
        "base_url": "https://api.mylead.global/v1",
        "auth": "Bearer token",
        "categories": ["crypto", "nutra", "gambling", "finance", "dating", "sweeps"],
    },
    "admitad": {
        "base_url": "https://api.admitad.com",
        "auth": "OAuth2 (official SDK)",
        "categories": ["aliexpress", "ozon", "wildberries", "lamoda", "booking", "aviataxis"],
    },
    "kma": {
        "base_url": "https://api.kma.biz/v1",
        "auth": "Bearer token",
        "categories": ["crypto", "nutra", "gambling", "finance", "betting"],
    },
}

# Async client with per-network httpx.AsyncClient
class CPALinkManager:
    async def search_offers_by_keyword(self, keyword: str, geo: str = "RU") -> list[AffiliateOffer]
    async def create_affiliate_link(self, network: str, offer_id: str, sub_id: str) -> AffiliateLink
    async def inject_affiliate_links(self, product_results: list[dict], user_id: int) -> list[dict]

# Sync wrappers for agent tools
def search_cpa_offers(keyword: str, geo: str = "RU") -> str
def generate_affiliate_link(network: str, offer_id: str, sub_id: str = None) -> str
def inject_affiliate_links(product_results: list[dict], user_id: int) -> list[dict]
```

### Agent Tool Definitions (`src/agents.py`)

```python
# 4 tools available to LLM
ALL_TOOLS = [
    FLIGHT_TOOL,           # search_flights(departure_id, arrival_id, outbound_date, return_date, adults)
    SHOPPING_TOOL,         # search_shopping(query) → injects affiliate links
    CPA_TOOL,              # search_cpa_offers(category, geo, network)
    AFFILIATE_LINK_TOOL,   # generate_affiliate_link(offer_id, network, sub_id)
]
```

### Key Architecture Patterns Reused

1. **Prompt Caching (Anthropic)**: `cache_control: ephemeral` on system prompt → ~90% token cost reduction
2. **Per-User Lock**: `asyncio.Lock()` per user_id → sequential message processing preserves history
3. **Thread Pool Execution**: `asyncio.to_thread(agent.chat, text)` → non-blocking event loop
4. **Session Memory**: In-memory `sessions: dict[int, Agent]` with `user_profile` extraction
5. **Health Check**: HTTP endpoint on :8080 for Fly.io keepalive
6. **Multi-LLM Support**: Anthropic (primary) + OpenAI-compatible (Gemini, local) via config `LLM_MODE`

### Deployment Configuration

```toml
# fly.toml
app = "tara-bot-ru"
primary_region = "fra"  # Frankfurt for RU users
[env]
  LLM_MODE = "anthropic"
[processes]
  bot = "python -m src.bot"
  health = "python -c \"...health server...\""
[http_service]
  internal_port = 8080
  auto_stop_machines = false
  min_machines_running = 1
[[vm]]
  size = "shared-cpu-1x"
  memory = "1gb"
```

```yaml
# .github/workflows/monitor.yml
on:
  schedule:
    - cron: '0 6 * * *'  # 06:00 UTC = 09:00 MSK
```

### Environment Variables Required

| Variable | Required | Source |
|----------|----------|--------|
| TELEGRAM_TOKEN | ✅ | @BotFather |
| ALLOWED_USER_ID | ✅ | @userinfobot |
| SERPAPI_KEY | ✅ | serpapi.com (250 free/month) |
| ANTHROPIC_API_KEY | ✅ | console.anthropic.com ($5 free) |
| MYLEAD_API_KEY | ❌ | mylead.global |
| ADMITAD_API_KEY | ❌ | admitad.com (OAuth2) |
| KMA_API_KEY | ❌ | kma.biz |
| LLM_MODE | ❌ | anthropic/openai |
| OPENAI_API_KEY | ❌ | Google AI Studio / local |
| OPENAI_BASE_URL | ❌ | For OpenAI mode |
| OPENAI_MODEL | ❌ | For OpenAI mode |

### Cost Breakdown

| Service | Cost | Notes |
|---------|------|-------|
| Fly.io | $0 | Free tier: shared CPU 1GB RAM |
| SerpAPI | $0 | 250 req/month free |
| Anthropic | ~$0.50/mo | Prompt caching saves ~90% |
| GitHub Actions | $0 | Public repo free |
| **Total** | **~$0.50/mo** | |

### Testing Commands

```bash
# Local run
cp .env.example .env
# edit .env
chmod +x run_bot.sh
./run_bot.sh

# Fly.io deploy
fly auth login
fly launch --no-deploy
fly secrets set TELEGRAM_TOKEN=xxx ALLOWED_USER_ID=xxx SERPAPI_KEY=xxx ANTHROPIC_API_KEY=xxx MYLEAD_API_KEY=xxx ADMITAD_API_KEY=xxx KMA_API_KEY=xxx
fly deploy

# Check logs
fly logs
```

### Telegram Commands

| Command | Description |
|---------|-------------|
| `/start` | Welcome + feature overview |
| `/reset` | Clear conversation history |
| `/uptime` | Health check + active sessions |

### Natural Language Examples

```
User: "билеты Москва Сочи на выходные"
Bot:  ✈️ *Москва → Сочи* — 5 рейсов, лучший 12,500₽ (Аэрофлот, прямой)
      🔗 [Google Flights]

User: "iPhone 16 Pro цена"
Bot:  🛒 *iPhone 16 Pro* — 6 результатов
      🥇 129,990₽ — DNS (affiliate: MyLead)
      🥈 132,500₽ — Ситилинк (affiliate: Admitad)
      🔗 [Affiliate links injected]

User: "CPA офферы крипта"
Bot:  🤝 *CPA Offers: крипта* (8 found)
      🥇 Crypto Exchange RU (MyLead) — 2,500₽ CPA
      🥈 DeFi Wallet (Admitad) — 15% RevShare
      💡 Ask me to generate link for any offer!
```

### Lessons for Future Adaptations

1. **City Mapping**: Maintain `CITY_MAP` dict in serpapi.py — easy to swap for any country
2. **Currency**: Single constant change (VND→RUB) propagates everywhere
3. **Language**: System prompt + bot messages — ~20 strings to translate
4. **CPA Networks**: Adapter pattern allows adding networks without touching agent logic
5. **Affiliate Injection**: `inject_affiliate_links()` post-processes shopping results — non-invasive
6. **Prompt Caching**: Critical for cost — always use `cache_control: ephemeral` on frozen system prompt
7. **Per-User Lock**: Prevents race conditions in history — essential for multi-user bots
8. **Fly.io Region**: Choose closest to users (fra for RU, sin for VN, iad for US)
9. **GitHub Actions Cron**: UTC-based — convert target timezone (MSK = UTC+3 → 06:00 UTC)
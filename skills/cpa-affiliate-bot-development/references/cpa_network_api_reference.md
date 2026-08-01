# CPA Network API Integration Reference

This document contains detailed API integration notes for the three target CPA networks discovered during research for the `t_affiliate_bot` task.

---

## MyLead (mylead.global)

### API Access
- **Documentation**: https://strackr.com/docs/mylead (via Strackr aggregator)
- **Direct API**: May require publisher account approval
- **Auth Method**: API Key (Bearer token)

### Endpoints (estimated from Strackr docs)
```
GET    /offers                    # List offers with filters
GET    /offers/{id}               # Offer details
GET    /categories                # Offer categories
POST   /links/generate            # Generate affiliate link with subid
GET    /reports/conversions       # Conversion reports
GET    /reports/clicks            # Click reports
GET    /balance                   # Current balance
GET    /payouts                   # Payout history
```

### Request/Response Examples

**List Offers Request**:
```http
GET /offers?category=nutra&country=RU&payout_min=10&limit=100
Authorization: Bearer YOUR_API_KEY
```

**Offer Response**:
```json
{
  "id": "offer_123",
  "name": "KetoExpert Weight Loss",
  "description": "Premium keto supplement...",
  "category": "nutra",
  "vertical": "health",
  "countries": ["RU", "BY", "KZ"],
  "payout_type": "CPA",
  "payout_value": 22.50,
  "currency": "EUR",
  "preview_url": "https://lander.example.com/preview",
  "landing_url": "https://lander.example.com",
  "status": "active",
  "restrictions": {
    "traffic_sources": ["social", "native", "email"],
    "forbidden": ["incent", "adult"]
  }
}
```

**Generate Link Request**:
```http
POST /links/generate
Authorization: Bearer YOUR_API_KEY
Content-Type: application/json

{
  "offer_id": "offer_123",
  "subid": "user_12345_channel_telegram_campaign_summer",
  "custom_parameters": {
    "utm_source": "telegram",
    "utm_medium": "bot",
    "utm_campaign": "summer_sale"
  }
}
```

**Generate Link Response**:
```json
{
  "tracking_url": "https://track.mylead.global/click?pid=123&offer_id=offer_123&subid=user_12345_channel_telegram_campaign_summer",
  "expires_at": "2026-12-31T23:59:59Z"
}
```

### Integration Notes
- No official Python SDK - build wrapper with `httpx.AsyncClient`
- Rate limits: estimated 60 req/min (verify with support)
- Pagination: cursor-based or offset/limit
- Webhook/postback: Configure in publisher dashboard for S2S conversion notifications

---

## Admitad (admitad.com)

### API Access
- **Documentation**: https://developers.mitgo.com/hc/en-us/categories/34481291136402
- **Auth Method**: OAuth2 Client Credentials + Refresh Token
- **Python SDK**: Official `admitad-python-api` (pip install admitad)

### OAuth2 Flow

```python
from admitad import AdmitadClient

client = AdmitadClient(
    client_id="YOUR_CLIENT_ID",
    client_secret="YOUR_CLIENT_SECRET",
    redirect_uri="https://yourdomain.com/callback",
    scope="public_data advcampaigns deeplink reports payments referrals"
)

# Get authorization URL (for user consent if needed)
auth_url = client.get_authorization_url()

# Exchange code for tokens (after user authorizes)
tokens = await client.get_access_token(code="AUTH_CODE")

# Use access token for API calls
client.set_access_token(tokens["access_token"])
client.set_refresh_token(tokens["refresh_token"])

# Token auto-refresh handled by SDK
```

### Key Endpoints (via SDK)

```python
# List affiliate programs (offers)
campaigns = await client.Advcampaigns.get(
    status="active",
    categories=["nutra", "ecom"],
    countries=["RU", "BY", "KZ"],
    limit=100
)

# Get program details
campaign = await client.Advcampaigns.get_one(campaign_id=12345)

# Generate deeplink with subid
deeplink = await client.Deeplink.create(
    campaign_id=12345,
    url="https://lander.example.com/product",
    subid="user_12345_channel_telegram"
)

# Get statistics
stats = await client.Reports.get(
    date_start="2026-07-01",
    date_end="2026-07-13",
    subid=["user_12345"],
    metrics=["clicks", "actions", "earnings"]
)

# Get payments
payments = await client.Payments.get(
    date_start="2026-01-01",
    status="paid"
)

# Get referrals (sub-affiliates)
referrals = await client.Referrals.get()
```

### SDK Models (key fields)

```python
# Advcampaign (Offer)
{
    "id": 12345,
    "name": "KetoExpert RU",
    "description": "Weight loss supplement...",
    "category": {"id": 1, "name": "Health & Beauty"},
    "countries": ["RU", "BY"],
    "currency": "EUR",
    "payouts": [
        {"action": "sale", "rate": 22.50, "type": "fixed"}
    ],
    "landing_pages": [
        {"id": 1, "url": "https://lander.example.com"}
    ],
    "status": "active",
    "traffic_sources": ["social", "native", "email", "contextual"]
}

# Deeplink Response
{
    "deeplink": "https://ad.admitad.com/g/abc123/?subid=user_12345_channel_telegram&ulp=https%3A%2F%2Flander.example.com%2Fproduct",
    "campaign_id": 12345
}
```

### Integration Notes
- Official SDK handles OAuth2 token refresh automatically
- Rate limits: 300 req/min per IP (check current limits)
- Webhooks: Configure postback URL in dashboard for real-time conversions
- SubID mapping: Admitad supports subid1-subid5, map your tracking IDs accordingly

---

## KMA.biz (kma.biz)

### API Access
- **Documentation**: Limited public docs. Contact support@kma.biz for API access
- **Auth Method**: Likely API Key or session-based (POST /login)
- **Base URL**: `https://kma.biz/api/` (verify with support)

### Estimated Endpoints (based on standard CPA network patterns)

```
POST   /auth/login                  # Get session token
GET    /offers                      # List offers
GET    /offers/{id}                 # Offer details
POST   /links/create                # Create tracking link
GET    /stats                       # Statistics
GET    /balance                     # Current balance
GET    /payouts                     # Payout history
GET    /categories                  # Offer categories
```

### Integration Approach

Since public docs are unavailable:

1. **Contact Support**: Email support@kma.biz requesting API documentation for publisher integration
2. **Alternative**: If API not available, consider:
   - CSV/XML feed export (many networks offer daily feeds)
   - Manual offer entry with periodic updates
   - Browser automation for critical operations (last resort)

### Offer Verticals (from research)
- **Primary**: Nutra (supplements, health, beauty)
- **Secondary**: White goods (appliances), E-com
- **GEO Focus**: CIS countries (RU, BY, KZ, UA, etc.)
- **Payouts**: Daily, wire transfer, crypto options
- **Minimum payout**: Low (good for testing)

### Integration Priority: MEDIUM
- Start with MyLead + Admitad (both have solid APIs)
- Add KMA.biz once API access confirmed
- KMA.biz offers exclusive CIS nutra offers not on other networks

---

## Unified Integration Pattern

### Base Adapter Interface

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass
class Offer:
    id: str                    # Internal ID
    external_id: str           # Network's offer ID
    network: str               # MYLEAD, ADMITAD, KMABIZ
    name: str
    description: str
    category: str
    vertical: str
    countries: list[str]
    payout_type: str           # CPA, CPL, CPS, REVSHARE
    payout_value: float
    currency: str
    preview_url: str
    landing_url: str
    status: str                # active, paused, stopped
    raw_data: dict             # Full API response
    synced_at: datetime

@dataclass
class TrackingLink:
    url: str
    subid: str
    expires_at: Optional[datetime]
    offer_id: str

@dataclass
class Conversion:
    network_conversion_id: str
    subid: str
    payout: float
    currency: str
    status: str                # pending, approved, rejected
    clicked_at: datetime
    converted_at: datetime
    raw_data: dict

class CPANetworkAdapter(ABC):
    """Base adapter for CPA network integrations."""
    
    @property
    @abstractmethod
    def network_name(self) -> str:
        """Network identifier: MYLEAD, ADMITAD, KMABIZ"""
        pass
    
    @abstractmethod
    async def authenticate(self) -> bool:
        """Authenticate and store tokens. Return success."""
        pass
    
    @abstractmethod
    async def fetch_offers(
        self,
        categories: Optional[list[str]] = None,
        countries: Optional[list[str]] = None,
        limit: int = 100
    ) -> list[Offer]:
        """Fetch and normalize offers from network."""
        pass
    
    @abstractmethod
    async def get_offer(self, external_id: str) -> Optional[Offer]:
        """Get single offer by network's ID."""
        pass
    
    @abstractmethod
    async def generate_link(
        self,
        offer_external_id: str,
        subid: str,
        landing_url: Optional[str] = None
    ) -> TrackingLink:
        """Generate affiliate tracking link with subid."""
        pass
    
    @abstractmethod
    async def fetch_conversions(
        self,
        date_from: datetime,
        date_to: datetime,
        subids: Optional[list[str]] = None
    ) -> list[Conversion]:
        """Fetch conversions for period."""
        pass
    
    @abstractmethod
    async def fetch_balance(self) -> dict:
        """Get current balance across currencies."""
        pass
    
    @abstractmethod
    async def verify_postback(self, payload: dict) -> Optional[Conversion]:
        """Verify and parse postback payload. Return Conversion or None."""
        pass
```

### Implementation Classes

```python
# integrations/mylead/api.py
class MyLeadAdapter(CPANetworkAdapter):
    network_name = "MYLEAD"
    
    def __init__(self, api_key: str, base_url: str = "https://api.mylead.global/v1"):
        self.api_key = api_key
        self.base_url = base_url
        self.client = httpx.AsyncClient(
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=30.0
        )
    
    async def authenticate(self) -> bool:
        # Test API key with a simple request
        resp = await self.client.get(f"{self.base_url}/balance")
        return resp.status_code == 200
    
    async def fetch_offers(self, categories=None, countries=None, limit=100):
        params = {"limit": limit}
        if categories: params["category"] = ",".join(categories)
        if countries: params["country"] = ",".join(countries)
        
        resp = await self.client.get(f"{self.base_url}/offers", params=params)
        resp.raise_for_status()
        data = resp.json()
        
        return [self._normalize_offer(o) for o in data.get("offers", [])]
    
    def _normalize_offer(self, raw: dict) -> Offer:
        return Offer(
            id=f"mylead_{raw['id']}",
            external_id=raw["id"],
            network="MYLEAD",
            name=raw["name"],
            description=raw.get("description", ""),
            category=raw.get("category", ""),
            vertical=raw.get("vertical", ""),
            countries=raw.get("countries", []),
            payout_type=raw.get("payout_type", "CPA"),
            payout_value=float(raw.get("payout_value", 0)),
            currency=raw.get("currency", "USD"),
            preview_url=raw.get("preview_url", ""),
            landing_url=raw.get("landing_url", ""),
            status=raw.get("status", "active"),
            raw_data=raw,
            synced_at=datetime.utcnow()
        )
    
    async def generate_link(self, offer_external_id: str, subid: str, landing_url=None):
        payload = {"offer_id": offer_external_id, "subid": subid}
        if landing_url:
            payload["landing_url"] = landing_url
        
        resp = await self.client.post(
            f"{self.base_url}/links/generate",
            json=payload
        )
        resp.raise_for_status()
        data = resp.json()
        
        return TrackingLink(
            url=data["tracking_url"],
            subid=subid,
            expires_at=None,  # Parse if provided
            offer_id=f"mylead_{offer_external_id}"
        )
    
    async def fetch_conversions(self, date_from, date_to, subids=None):
        params = {
            "date_from": date_from.strftime("%Y-%m-%d"),
            "date_to": date_to.strftime("%Y-%m-%d")
        }
        if subids:
            params["subid"] = ",".join(subids)
        
        resp = await self.client.get(
            f"{self.base_url}/reports/conversions",
            params=params
        )
        resp.raise_for_status()
        
        return [self._normalize_conversion(c) for c in resp.json().get("conversions", [])]
    
    def _normalize_conversion(self, raw: dict) -> Conversion:
        return Conversion(
            network_conversion_id=str(raw["id"]),
            subid=raw.get("subid", ""),
            payout=float(raw.get("payout", 0)),
            currency=raw.get("currency", "USD"),
            status=raw.get("status", "pending"),
            clicked_at=datetime.fromisoformat(raw["click_date"]),
            converted_at=datetime.fromisoformat(raw["conversion_date"]),
            raw_data=raw
        )
    
    async def verify_postback(self, payload: dict) -> Optional[Conversion]:
        # Verify signature if network provides one
        # Parse and return Conversion object
        pass
```

```python
# integrations/admitad/api.py
from admitad import AdmitadClient

class AdmitadAdapter(CPANetworkAdapter):
    network_name = "ADMITAD"
    
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        redirect_uri: str,
        scope: str = "public_data advcampaigns deeplink reports payments referrals"
    ):
        self.client = AdmitadClient(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_uri,
            scope=scope
        )
        # Load stored tokens if available
        self._load_tokens()
    
    def _load_tokens(self):
        # Load from encrypted storage
        pass
    
    def _save_tokens(self):
        # Save to encrypted storage
        pass
    
    async def authenticate(self) -> bool:
        try:
            # SDK handles token refresh automatically
            await self.client.Advcampaigns.get(limit=1)
            return True
        except Exception:
            return False
    
    async def fetch_offers(self, categories=None, countries=None, limit=100):
        params = {"status": "active", "limit": limit}
        if categories:
            params["categories"] = categories
        if countries:
            params["countries"] = countries
        
        resp = await self.client.Advcampaigns.get(**params)
        
        return [self._normalize_offer(c) for c in resp.get("results", [])]
    
    def _normalize_offer(self, raw: dict) -> Offer:
        # Admitad payouts structure varies - handle multiple actions
        payouts = raw.get("payouts", [])
        main_payout = payouts[0] if payouts else {}
        
        return Offer(
            id=f"admitad_{raw['id']}",
            external_id=str(raw["id"]),
            network="ADMITAD",
            name=raw["name"],
            description=raw.get("description", ""),
            category=raw.get("category", {}).get("name", ""),
            vertical=raw.get("category", {}).get("name", ""),
            countries=raw.get("countries", []),
            payout_type=main_payout.get("type", "CPA"),
            payout_value=float(main_payout.get("rate", 0)),
            currency=raw.get("currency", "USD"),
            preview_url=raw.get("landing_pages", [{}])[0].get("url", ""),
            landing_url=raw.get("landing_pages", [{}])[0].get("url", ""),
            status="active" if raw.get("status") == "active" else "paused",
            raw_data=raw,
            synced_at=datetime.utcnow()
        )
    
    async def generate_link(self, offer_external_id: str, subid: str, landing_url=None):
        resp = await self.client.Deeplink.create(
            campaign_id=int(offer_external_id),
            url=landing_url or "",
            subid=subid
        )
        
        return TrackingLink(
            url=resp["deeplink"],
            subid=subid,
            expires_at=None,
            offer_id=f"admitad_{offer_external_id}"
        )
    
    async def fetch_conversions(self, date_from, date_to, subids=None):
        params = {
            "date_start": date_from.strftime("%Y-%m-%d"),
            "date_end": date_to.strftime("%Y-%m-%d"),
            "metrics": ["clicks", "actions", "earnings"]
        }
        if subids:
            params["subid"] = subids
        
        resp = await self.client.Reports.get(**params)
        
        return [self._normalize_conversion(r) for r in resp.get("results", [])]
    
    def _normalize_conversion(self, raw: dict) -> Conversion:
        return Conversion(
            network_conversion_id=str(raw.get("action_id", raw.get("id"))),
            subid=raw.get("subid", ""),
            payout=float(raw.get("payment", 0)),
            currency=raw.get("currency", "USD"),
            status=raw.get("status", "pending"),
            clicked_at=datetime.fromisoformat(raw["click_date"]),
            converted_at=datetime.fromisoformat(raw["action_date"]),
            raw_data=raw
        )
```

---

## SubID Strategy

### Encoding Scheme
```
{user_id}_{source}_{channel}_{campaign}_{variant}
```

**Examples**:
- `123456789_telegram_bot_summer_sale_v1`
- `123456789_telegram_channel_crypto_news_main`
- `123456789_web_landing_page_black_friday_a`

### Mapping Table (store in DB)
| Field | Max Length | Notes |
|-------|------------|-------|
| user_id | 20 | Telegram user ID |
| source | 20 | telegram, web, email, api |
| channel | 30 | bot, channel_username, newsletter_name |
| campaign | 30 | summer_sale, black_friday, evergreen |
| variant | 10 | v1, v2, a, b, control |

### Network-Specific Limits
| Network | Max SubID Length | Parts Supported |
|---------|------------------|-----------------|
| MyLead | 255 | Single subid field |
| Admitad | 255 each | subid1-subid5 |
| KMA.biz | TBD | Verify with support |

**Implementation**: Hash long subids to fit limits, store full mapping in DB.

---

## Postback Handling

### Endpoint Structure
```
POST /webhook/mylead
POST /webhook/admitad
POST /webhook/kmabiz
```

### Verification Steps
1. **IP Whitelist**: Verify request from known network IPs
2. **Signature**: Verify HMAC/signature if provided
3. **Idempotency**: Check `network_conversion_id` not already processed
4. **SubID Parsing**: Extract tracking IDs, map to user/link
5. **Database Update**: Atomic upsert conversion, increment link stats
6. **Notifications**: Trigger user notifications (if enabled)

### Admitad Postback Example
```http
POST /webhook/admitad
Content-Type: application/x-www-form-urlencoded
X-Admitad-Signature: sha256=abc123...

action_id=12345&action_date=2026-07-13%2014:30:00&
click_date=2026-07-13%2014:25:00&payment=22.50&
currency=EUR&status=approved&subid=user_123_channel_telegram&
subid1=user_123&subid2=channel_telegram&subid3=summer_sale
```

### MyLead Postback Example
```http
POST /webhook/mylead
Content-Type: application/json

{
  "conversion_id": "conv_789",
  "click_id": "click_456",
  "offer_id": "offer_123",
  "subid": "user_123_channel_telegram",
  "payout": 22.50,
  "currency": "EUR",
  "status": "approved",
  "click_date": "2026-07-13T14:25:00Z",
  "conversion_date": "2026-07-13T14:30:00Z"
}
```

---

## Sync Scheduling

### APScheduler Configuration
```python
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

scheduler = AsyncIOScheduler()

# Offer sync - every 6 hours, staggered
scheduler.add_job(
    sync_mylead_offers,
    IntervalTrigger(hours=6),
    id="sync_mylead",
    next_run_time=datetime.now() + timedelta(minutes=5)
)

scheduler.add_job(
    sync_admitad_offers,
    IntervalTrigger(hours=6),
    id="sync_admitad",
    next_run_time=datetime.now() + timedelta(minutes=15)
)

scheduler.add_job(
    sync_kmabiz_offers,
    IntervalTrigger(hours=12),  # Less frequent if manual
    id="sync_kmabiz",
    next_run_time=datetime.now() + timedelta(minutes=30)
)

# Conversion sync - every hour
scheduler.add_job(
    sync_all_conversions,
    IntervalTrigger(hours=1),
    id="sync_conversions",
    next_run_time=datetime.now() + timedelta(minutes=10)
)

# Balance sync - every 4 hours
scheduler.add_job(
    sync_all_balances,
    IntervalTrigger(hours=4),
    id="sync_balances"
)
```

---

## Rate Limiting Strategy

```python
from asyncio import Semaphore
from collections import defaultdict
from time import time

class RateLimiter:
    def __init__(self, max_requests: int, window_seconds: int):
        self.max_requests = max_requests
        self.window = window_seconds
        self.requests = defaultdict(list)
        self.semaphores = defaultdict(lambda: Semaphore(max_requests))
    
    async def acquire(self, key: str):
        now = time()
        # Clean old requests
        self.requests[key] = [t for t in self.requests[key] if now - t < self.window]
        
        if len(self.requests[key]) >= self.max_requests:
            # Wait until oldest request expires
            wait_time = self.window - (now - self.requests[key][0])
            await asyncio.sleep(wait_time)
        
        self.requests[key].append(now)
    
    async def __aenter__(self):
        await self.acquire(self.current_key)
    
    async def __aexit__(self, *args):
        pass

# Per-network limiters
mylead_limiter = RateLimiter(max_requests=50, window_seconds=60)
admitad_limiter = RateLimiter(max_requests=100, window_seconds=60)
kmabiz_limiter = RateLimiter(max_requests=30, window_seconds=60)

# Usage in adapter methods
async def fetch_offers(self, ...):
    async with mylead_limiter:
        return await self._fetch_offers_impl(...)
```

---

## Error Handling & Retry Logic

```python
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type
)

@retry(
    wait=wait_exponential(multiplier=1, min=2, max=60),
    stop=stop_after_attempt(3),
    retry=retry_if_exception_type((httpx.TimeoutException, httpx.HTTPStatusError))
)
async def _make_request(self, method: str, url: str, **kwargs):
    async with self.limiter:
        resp = await self.client.request(method, url, **kwargs)
        resp.raise_for_status()
        return resp.json()
```

---

## Testing API Integrations

### Mock Responses (store in tests/fixtures/)
```json
// tests/fixtures/mylead_offers.json
{
  "offers": [
    {
      "id": "offer_123",
      "name": "Test Offer",
      "category": "nutra",
      "countries": ["RU"],
      "payout_type": "CPA",
      "payout_value": 15.00,
      "currency": "USD",
      "status": "active"
    }
  ]
}
```

### Unit Test Example
```python
import pytest
from httpx import Response
from integrations.mylead.api import MyLeadAdapter

@pytest.mark.asyncio
async def test_mylead_fetch_offers(httpx_mock):
    httpx_mock.add_response(
        url="https://api.mylead.global/v1/offers",
        json={"offers": [{"id": "offer_123", "name": "Test"}]},
        status_code=200
    )
    
    adapter = MyLeadAdapter(api_key="test_key")
    offers = await adapter.fetch_offers()
    
    assert len(offers) == 1
    assert offers[0].network == "MYLEAD"
    assert offers[0].external_id == "offer_123"
```

---

## References

- [MyLead via Strackr](https://strackr.com/docs/mylead)
- [Admitad Developers](https://developers.mitgo.com/hc/en-us/categories/34481291136402)
- [Admitad Python SDK](https://github.com/admitad/admitad-python-api)
- [KMA.biz](https://kma.biz)
- [Telegram Bot API](https://core.telegram.org/bots/api)
- [APScheduler](https://apscheduler.readthedocs.io/)
- [Tenacity Retry](https://github.com/jd/tenacity)

---

*Created during t_affiliate_bot research - 2026-07-13*
# Web Search Fallback — Lead Compilation Without Google Maps

Use this when `lead_finder.py` can't connect to Google Maps (Chrome not running, consent page blocking, or cron/autonomous execution).

## Multi-Source Search Strategy

Run 3 parallel `web_search_plus` queries for each category:

```python
from hermes_tools import web_search_plus

# For restaurants
results = web_search_plus(
    query="best restaurants in {city} {country} phone address",
    count=10
)

# For hotels
results = web_search_plus(
    query="hotels in {city} {country} phone address booking.com",
    count=10
)

# For beauty salons
results = web_search_plus(
    query="beauty salon OR hair salon {city} {country} phone address",
    count=10
)
```

## Sources by Category

| Category | Best Sources | What They Give |
|---|---|---|
| Restaurants | OpenTable, TripAdvisor, local food blogs, montenegropulse.com | Name, rating, address, sometimes phone |
| Hotels | Booking.com, Hotels.com, TripAdvisor, travelweekly.com | Name, address, phone, rating, review count |
| Beauty Salons | vymaps.com, montenegrofortravellers.com, individual salon websites, TripAdvisor | Name, phone, address, rating, sometimes website |

## Data Extraction

Not all sources return structured data. For each business found, compile:

```python
lead = {
    "name": "Business Name",
    "phone": "+382 XX XXX XXX",       # Extract from search snippet or business site
    "address": "Street, City 85310",   # Reconstruct from multiple mentions
    "rating": 4.5,                     # From Google reviews if mentioned
    "review_count": 200,               # From TripAdvisor or Google
    "categories": ["restaurant", "seafood"],
    "has_website": True,               # If website URL found
    "website": "https://..."           # If available
}
```

For phone numbers that aren't directly in search results:
- Visit individual business websites (extract from contact page)
- Use `vymaps.com` (has phone numbers for many businesses)
- Check Google Maps links in search results (click "website" if accessible)

## DB Saving

Use `modules/lead_finder.py` functions directly:

```python
from lead_finder import init_db, save_lead, Lead

init_db()
lead = Lead(
    name="Business Name",
    phone="+382 XX XXX XXX",
    address="Address",
    rating=4.5,
    review_count=200,
    categories=["restaurant"],
    source="multi_source",
    language="en"
)
lead_id = save_lead(lead)
```

Or for bulk import, call `save_leads([lead1, lead2, ...])`.

## Why This Works

- Google Maps consent page (`consent.google.com`) blocks browser-based scanning in autonomous/cron mode
- TripAdvisor and some directories have CAPTCHAs
- Web search results often include structured snippets with ratings, addresses, and phone numbers
- Multiple sources cross-validate data (address consistency across 2+ sites = reliable)

## Prerequisites

- Functional `web_search_plus` provider (falls back through auto-routing)
- Local search providers may use `you.com` or `brave` which have rate limits

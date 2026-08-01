# RSS Feed Sources — Session Notes (2026-07-18)

## Working Feeds (AI/Tech) — 37 entries fetched

| Source | URL | Entries | Notes |
|--------|-----|---------|-------|
| VentureBeat AI | https://venturebeat.com/category/ai/feed/ | ~6 | High-signal enterprise AI coverage |
| MIT Technology Review | https://www.technologyreview.com/feed/ | ~7 | Deep tech, AI safety, quantum |
| OpenAI Blog | https://openai.com/blog/rss.xml | ~8 | Product launches, safety research, case studies |
| Google AI Blog | https://blog.google/technology/ai/rss/ | ~8 | Gemini, research, product updates |
| HuggingFace Blog | https://huggingface.co/blog/rss.xml | 0 (check) | Community models, research |
| HuggingFace Papers | https://huggingface.co/papers/rss.xml | 0 (check) | Daily paper highlights |

**Total AI/Tech: ~29 quality entries**

---

## Stale/Broken CPA Feeds — 0 entries

| Source | URL | Status |
|--------|-----|--------|
| CPARadar | https://www.cparadar.com/feed/ | 0 entries |
| OfferVault | https://offervault.com/feed/ | 0 entries |
| AffPaying | https://www.affpaying.com/feed/ | 0 entries |
| OffersLook | https://offerslook.com/rss.xml | 0 entries |
| Mobidea | https://www.mobidea.com/feed/ | 0 entries |
| YeahMobi | https://www.yeahmobi.com/rss.xml | 0 entries |
| ZeroPark | https://www.zeropark.com/feed/ | 0 entries |

**Action needed:** Find active CPA/arbitrage RSS sources or switch to API-based monitoring.

---

## New Script Created

**File:** `scripts/fetch_rss.py`

- Self-contained, no external deps beyond `feedparser`
- Uses system Python (`D:/Program Files/Python311/python.exe`) which has feedparser pre-installed
- Fetches up to 10 entries per feed
- Outputs JSON to `rss_digest_latest.json` with timestamp, entries, count
- 17 feeds processed in ~30s (network-bound)

**Usage:**
```bash
"D:/Program Files/Python311/python.exe" scripts/fetch_rss.py
```

---

## Notable Articles This Run (Top Signal)

| Source | Title | Key Insight |
|--------|-------|-------------|
| VentureBeat | The AI compute gap | 107 enterprises buying infra faster than they can measure ROI |
| VentureBeat | 54% had agent security incident | Only 1/3 give agents scoped identities; creds shared by default |
| VentureBeat | Agent evaluation gap | 50% shipped agents that passed evals but failed in prod |
| MIT Tech Review | OpenAI unveils GPT-Red | LLM super-hacker for self-improving safety via self-play |
| MIT Tech Review | PsiQuantum photonic quantum | 100 cabinets, near 0K, light-based quantum computer |
| MIT Tech Review | Anthropic's interpretability window | New view into Claude's internal reasoning |
| OpenAI | AI Scorecard (Sarah Friar, CFO) | ROI = useful work / $, cost/success, dependability, return on compute |
| OpenAI | Managing AI in agentic era | Measure useful work per $, improve efficiency, scale high-value workflows |
| OpenAI | Cars24: 1M+ conv min/mo | 12% lost lead recovery with voice/chat agents |
| Google | AMIE matches physicians (Nature) | Conversational AI for complex disease management |
| Google | Managed Agents in Gemini API | Background tasks, remote MCP, agent-as-a-service |
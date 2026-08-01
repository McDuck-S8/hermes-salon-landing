# Deep-Dive Dispatch — 2026-07-24

## CRITICAL Signal Triggered
**Signal**: `adm_002` (Raid Shadow Legends, admitad, gaming CPI, RU) + `richads` RU gaming
- Score: 80 (CRITICAL ≥70)
- ROI: 240% | Profit: $1080/day | Confidence: 1.0
- Conversion type: CPI

## Workers Dispatched (3 parallel via delegate_task)

### Worker 1: Offer Deep-Dive
```
Goal: Deep dive offer adm_002 (Raid Shadow Legends, admitad, gaming CPI, RU): 
full payout history, cap changes, creative requirements, AM contact, landing page analysis
Context: offer_id=adm_002, network=admitad, name=Raid Shadow Legends, vertical=gaming, 
geo=RU, payout=120 RUB, conversion_type=CPI, approval_rate=0.85, cr=0.15, 
landing_url=https://raid-shadow-legends.com/ru, gap_score=80, projected_profit=1080/day, 
traffic_source=richads
```

### Worker 2: Competitive Analysis
```
Goal: Competitive analysis: who else runs gaming offers in RU? 
Find competitors' landers, angles, traffic sources, creatives for gaming CPI/CPA offers in Russia
Context: geo=RU, vertical=gaming, offer_type=CPI, reference_offer=Raid Shadow Legends, 
traffic_source=richads
```

### Worker 3: Traffic Source Audit
```
Goal: Traffic source audit for RU gaming: compare FB vs TikTok vs Native vs Push (RichAds) - 
current CPC, approval rates, restrictions, creative requirements for gaming vertical in Russia
Context: geo=RU, vertical=gaming, traffic_sources=facebook,tiktok,kadam,richads,google, 
reference_gap=adm_002 + richads
```

## Dispatch Pattern (from always-on-agent skill)
```python
tasks = [
    {"goal": f"Deep dive offer {signal['offer_id']}...", "context": signal, "role": "leaf"},
    {"goal": f"Competitive analysis: who else runs {signal['vertical']} in {signal['geo']}...", 
     "context": signal, "role": "leaf"},
    {"goal": f"Traffic source audit for {signal['geo']} {signal['vertical']}: FB vs TikTok vs Native vs Push...", 
     "context": signal, "role": "leaf"},
]
deep_intel = delegate_task(tasks=tasks, timeout=300)
```

## Notes
- Workers run in background; results re-enter conversation when all 3 complete
- `delegate_task` timeout: 300s (5 min) per worker
- On timeout: redispatch with simplified brief + explicit `browser-automation` requirement (180s)
- For JS-heavy sources (FB Ad Library, TikTok Creative Center), workers MUST have:
  - `tools_required: ["browser-automation"]`
  - `mcp_servers: ["browseros"]`
  - BrowserOS MCP must be running: `curl http://localhost:9003/mcp` → 200 OK

## Expected Output Format (per worker brief template)
```json
{
  "offer_id": "adm_002",
  "network": "admitad",
  "payout": 120,
  "flow": "CPI",
  "restrictions": ["no_incent", "android_only"],
  "landers": ["https://raid-shadow-legends.com/ru"],
  "creatives": ["angle1", "angle2"],
  "risks": ["cap limits", "geo restrictions"],
  "score": 8
}
```

## Status
✅ Dispatched at 2026-07-24T01:09Z
⏳ Awaiting worker results...
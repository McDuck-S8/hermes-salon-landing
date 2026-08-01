# Multi-Agent Researcher Dispatch Pattern — 2026-07-23 23:06 UTC

## Dispatch Record
**Delegation ID**: `deleg_b29f4072`  
**Trigger**: 3 CRITICAL signals from always-on-agent medium sensor run  
**Workers**: 3 leaf agents launched in parallel  
**Timeout**: 300s (5 min) each

## Worker Briefs

| # | Goal | Context (Signal) | Tools Required |
|---|------|------------------|----------------|
| 1 | Deep dive Tinkoff Credit Card (Admitad adm_001): payout history, caps, creative requirements, AM contact, approval flow. Real CPC on Kadam/FB RU finance. | ROI 244% ($2075/d), conf 0.2 | web-search, browser-automation for Kadam cabinet |
| 2 | Deep dive Raid Shadow Legends (Admitad adm_002): payout history, Android-only restrictions, creative specs. RichAds RU gaming traffic audit. | ROI 240% ($1080/d), conf **1.0** | web-search, browser-automation for RichAds |
| 3 | Competitive analysis RU finance (credit cards, microloans, insurance): active creatives, landers, funnels. FB Ad Library + TikTok Creative Center. | 3 finance offers in CRITICAL/HIGH | **browser-automation** + BrowserOS MCP (MANDATORY) |

## Key Learnings

### 1. Timeout Handling Works
- 300s timeout prevents stuck calls
- On timeout: redispatch with simplified brief + explicit `browser-automation` requirement + 180s timeout
- This pattern should be documented in SKILL.md

### 2. Browser Automation is Mandatory for Creative Intel
- Worker 3 **cannot succeed** without `browser-automation` + BrowserOS MCP
- FB Ad Library and TikTok Creative Center are JS-rendered, authenticated
- Web search returns landing pages only
- Future dispatches for creative analysis MUST include:
  ```json
  {"tools_required": ["browser-automation"], "mcp_servers": ["browseros"]}
  ```

### 3. Signal Context Must Include Traffic Source Details
Workers need:
- Traffic source name (Kadam, RichAds, FB, Google)
- Geo + Vertical
- Current mock CPC/CPM from gap_calculator
- So they can validate against real data

### 4. Confidence Score Drives Dispatch Priority
- Only CRITICAL (score ≥70) signals get deep research
- HIGH (50-69) → daily digest only
- This threshold should be configurable in always-on-agent

## Recommended SKILL.md Updates

Add to **Dispatch Pattern** section:
```markdown
### Timeout Handling (2026-07-23 verified)
If worker times out (300s default → reduce to 300s explicit):
1. Treat as FIX (not ESCALATE)
2. Redispatch with:
   - Simplified brief (single focus)
   - Explicit "Use browser automation for all JS-heavy sites"
   - `tools_required: ["browser-automation"]`
   - Timeout: 180s
```

Add to **Integration with Browser Automation** section:
```markdown
### Mandatory for Creative Intel
Any worker researching FB Ad Library, TikTok Creative Center, or CPA network dashboards:
- MUST have `tools_required: ["browser-automation"]`
- MUST have `mcp_servers: ["browseros"]` (port 9003)
- Pre-dispatch check: `curl http://localhost:9003/mcp` → 200 OK
- Acceptance criteria must include visual verification (screenshots)
```

## Next Steps
1. Wait for worker results (~02:11 UTC)
2. Synthesize findings into actionable test plan
3. If Raid+RichAds validated → launch $50 test immediately
4. If Tinkoff+Kadam validated → test $100 on Kadam
5. Update sensor confidence formula based on real data
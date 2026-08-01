# Landscape + Transparency Layers Architecture

## Context

This architecture was designed in discussion with the user (2026-07-16) as the next evolution of the Knowledge Cube/OKF system. It implements a **military-map metaphor**: a permanent base map (Landscape) + replaceable transparent overlay sheets (Situation, Plans, Logistics).

## Why This Architecture

The Fractal Knowledge Wheel (v1-4) evaluates **aspects** (colors) and **intersections** (Bayesian P(success)) and **keys** (Key Strength). But all these live in a single namespace with single expiration/confidence.

Problem: When 1xBet gets banned, the entire knowledge about "PWA India arbitrage" becomes stale. But the fundamental truth — "short video traffic + CPA betting + crypto payments works" — remains valid. We were throwing away the landscape when the situation changed.

## Four-Layer Model

### Layer 0: Landscape (Permanent)
**Fundamental keys** — never expire, confidence 0.9+, expiration years out.
- Traffic sources: short video, search, messengers, social
- Monetization: ads, subs, CPA, referrals, direct
- Payment rails: crypto, fiat, barter
- Human needs: food, shelter, safety, status, gambling, savings

Schema: `kc_entries` with `layer_type='landscape'`

### Layer 1: Situation (Months)
**Current services & their state** — confidence 0.6-0.8, expiration weeks-months.
- TikTok: works via VPN, high ban risk
- YouTube Shorts: works in RF without VPN, low risk
- 1xBet: blocked in RF
- 1win: working

Schema: `kc_entries` with `layer_type='situation'`, `overlay_on=['landscape_key_id']`

### Layer 2: Plans (Days-Weeks)
**Connection arrows with ROI/probability** — confidence 0.4-0.7, expiration days-weeks.
- YouTube Shorts → GitHub Pages → 1win (RU): ROI 240%, P=0.85
- TikTok → PWA.Market → 1xBet (IN): ROI 244%, P=0.09 (blocked by creatives)

Schema: `kc_entries` with `layer_type='plans'`, `geometry={arrows:[{from,to,roi,prob,blocking}]}`

### Layer 3: Logistics (Days)
**Resources needed for plans** — variable confidence, short expiration.
- Creatives for betting: critical gap, needed for 3 plans
- USDT wallet: ready
- TikTok accounts: need purchase

Schema: `kc_entries` with `layer_type='logistics'`, `overlay_on=['plan_key_id']`

## Integration with Fractal Wheel

| Fractal Wheel Mode | Reads | Writes |
|-------------------|-------|--------|
| Mode 1: Analysis | Landscape (fundamental aspects) | Situation (current gaps) |
| Mode 2: Synthesis | Landscape + Situation | Plans (novel keys) |
| Mode 3: Euler | Plans + Situation | Key Strength (via Bayesian) |
| Key Strength | All 4 layers | Key Strength score |

## Migration Path

1. **Add `layer_type` column** to `kc_entries` and `experiences` tables
2. **Backfill existing entries**: current findings → Situation layer
3. **Extract Landscape**: aggregate high-confidence, long-expiration entries
4. **Build Plans layer**: from Euler intersections + Key Strength
5. **Build Logistics**: from critical red sectors + Key Strength blocking factors

## Queries

```sql
-- Get full picture for a topic
SELECT * FROM kc_entries 
WHERE layer_type IN ('landscape','situation','plans','logistics')
  AND content LIKE '%topic%';

-- Compose: Landscape + Situation for traffic
SELECT l.essence, s.current_state, s.risk_level
FROM kc_entries l
JOIN kc_entries s ON s.overlay_on LIKE '%' || l.id || '%'
WHERE l.layer_type='landscape' AND s.layer_type='situation'
  AND l.tags LIKE '%traffic%';

-- Find actionable plans
SELECT p.name, p.geometry, p.confidence, p.expiration_date
FROM kc_entries p
WHERE p.layer_type='plans'
  AND p.confidence > 0.5
  AND p.expiration_date > date('now');
```

## Future: Agent-Native Operations

- **Auto-expiration**: Situation/Plans/Logistics auto-archive when expired
- **Conflict detection**: If Situation changes (service banned), flag dependent Plans
- **Landscape enrichment**: New fundamental patterns → promote to Landscape
- **Cross-topic composition**: Overlay Plans from different topics on same Landscape
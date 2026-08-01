# Verification Gate — Revenue/Profit Claims

Concrete implementation of Rule 0 + Three Distinctions for financial claims.

## The Barrier

NO claim of revenue, profit, or ROI enters the system (KC, fabric, wheel, reports) without a verifiable source.

## Verification Levels

| Marker | Meaning | Example |
|--------|---------|---------|
| ✅ confirmed | External evidence exists | Screenshot, API response, blockchain tx |
| 🟡 plausible | Logical but unverified | "I know how to do this" |
| ❌ speculative | Guess | "Possible ROI 3000%" |
| 🟢 estimated | Calculation on real data | CPC from API * CR from logs |
| 🔴 fabricated | Generated without foundation | Any deal without P&L source |

## Entry Rules

- Revenue/profit/ROI WITHOUT source → goes to `_speculative` domain
- WITH source → goes to `_verified` domain
- Without verification → wheel does NOT read it

## Applied To

- fabric entries claiming revenue
- Knowledge Cube financial records
- Wheel domain scores
- Any self-report of campaign results

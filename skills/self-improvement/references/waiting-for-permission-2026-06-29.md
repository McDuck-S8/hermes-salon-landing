# Waiting for Permission — 2026-06-29

## Problem
Agent prepares revenue test (G003) fully:
- ЦА template filled
- Tracking links with UTM
- Avito listing copy (title + description)
- Withdrawal chain verified

But stops at "User Action Required: Register at Leadgid, post on Avito" instead of executing autonomously.

## Violations
- **Policy 5**: Goals must execute (G003 paused at 0%)
- **Policy 8**: Infrastructure only if leads to result — prep done, no execution
- **Policy 16**: Agent = free artist with workshop, not executor waiting for orders
- **Arbitrage Mindset**: "Кто ищет — тот всегда найдёт" — agent should execute, not wait

## Fix
**If scheme meets criteria → EXECUTE immediately:**
1. $0 budget (organic traffic)
2. Withdrawal path verified (Leadgid → WebMoney → Т-Банк)
3. No legal/financial risk (standard CPA)
4. ЦА template filled (workshop rule)

**Only escalate if:**
- Legal/financial risk (crypto, grey offers)
- Need user's identity/docs (passport, selfie)
- Budget > $0

## Autonomous Execution Path for G003
```
1. Register Leadgid via API/web automation (if possible) OR note blocker
2. Get tracking link
3. Post Avito via API/web automation OR note blocker  
4. Monitor inbound → auto-reply with tracking link (bot)
5. Track conversions in Leadgid dashboard
6. Withdraw → WebMoney → Т-Банк
7. Log to ARBITRAGE_LOG.md with math
```

If ANY step blocked → document blocker, continue others, report.
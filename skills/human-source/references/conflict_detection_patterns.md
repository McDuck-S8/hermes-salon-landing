# Conflict Detection Patterns — Human Source Skill

## Overview
This document captures the conflict detection patterns used by the ripple engine to identify value conflicts between key aspects and human underwater rocks (hard constraints/values).

## Underwater Rocks (User's Hard Constraints)

| Rock ID | Name | Type | Description |
|---------|------|------|-------------|
| RK-01 | No KYC / No Documents | hard_constraint | Zero tolerance for identity verification, passport uploads, document submission |
| RK-02 | Crimea Constraints | environmental | Banking unavailable, SWIFT/SEPA blocked, only USDT/P2P/MIR cards work |
| RK-03 | Stdlib-First / No Heavy Frameworks | value | No Django/FastAPI/React/Vue/Webpack/Babel unless absolutely necessary |
| RK-04 | Clickable Artifacts Only | value | Plans, research phases, strategy docs = NOT artifacts. Working code/files = artifacts |
| RK-05 | Passive Autonomy | value | No daily maintenance, constant monitoring, content moderation, manual intervention |
| RK-06 | No Risk / Stability | value | High regulatory/banking risk, legal uncertainty, card blocking = reject |

## Conflict Detection Rules

### Format
Each rule: `(keywords, rock_id, severity, description)`

### RK-01: No KYC / No Documents
```python
# CRITICAL - Specific identity verification terms
(['kyc verification', 'passport upload', 'document upload', 
  'identity verification', 'verify identity', 'загрузка паспорт', 
  'верификаци документов', 'подтверждение личности'],
 'No KYC / No Documents', 'critical', 'Requires identity verification')

# CRITICAL - Geographic payment rails that require KYC
(['india', 'инди', 'indian', 'индийск'],
 'No KYC / No Documents', 'critical', 'Indian payment rails require KYC')

# CRITICAL - Betting/gambling platforms require KYC
(['betting kyc', 'беттинг kyc', 'gambling kyc', 'casino kyc', 'казино kyc'],
 'No KYC / No Documents', 'critical', 'Betting platforms require KYC')
```

### RK-02: Crimea Constraints
```python
(['bank transfer', 'банк перевода', 'swift', 'sepa', 'iban'],
 'Crimea Constraints', 'critical', 'Banking unavailable in Crimea')
```

### RK-03: Stdlib-First
```python
(['heavy framework', 'тяжел фреймворк', 'django rest', 'fastapi', 
  'react', 'vue', 'webpack', 'babel'],
 'Stdlib-First / No Heavy Frameworks', 'medium', 'Heavy framework dependency')
```

### RK-04: Clickable Artifacts Only
```python
# SPECIFIC - Research/planning phases that produce no artifact
(['research phase', 'исследовани фаз', 'planning phase', 'планирован фаз', 
  'strategy document', 'стратеги документ'],
 'Clickable Artifacts Only', 'medium', 'Produces plan not artifact')

# SPECIFIC - Manual setup/work
(['manual setup', 'ручн настройк', 'hand craft', 'ручная работа'],
 'Clickable Artifacts Only', 'medium', 'Requires manual work')
```

### RK-05: Passive Autonomy
```python
(['daily maintenance', 'ежедневн обслуживан', 'constant monitoring', 
  'постоянн мониторинг', 'moderate content', 'модер контент'],
 'Passive Autonomy', 'medium', 'Requires ongoing human attention')
```

### RK-06: No Risk / Stability
```python
(['betting', 'беттинг', 'gambling', 'гемблинг', 'casino', 'казино'],
 'No Risk / Stability', 'critical', 'High regulatory/banking risk')

(['legal uncertainty', 'юридич неопределен', 'regulation risk', 'регуляторн риск'],
 'No Risk / Stability', 'critical', 'Legal uncertainty')
```

## Verification Results (2026-07-18)

### Test 1: "PWA-арбитраж на Индию" → REJECTED ✅
| Circle | Aspect | Rock | Severity | Match Reason |
|--------|--------|------|----------|--------------|
| Traffic & PWA | TikTok/Shorts India | RK-01 | critical | 'india' keyword |
| Offer & Payments | Indian payment gateways | RK-01 | critical | 'indian' + 'payment' |
| Offer & Payments | UPI/NetBanking | RK-02 | critical | 'bank' + 'india' implied |
| Offer & Payments | USDT→INR→RUB | RK-01 | critical | 'india' + 'payment' |

**Replacement Generated:** "Автономный контент-бизнес на Shorts (India cricket niche) → монетизация через рефералки/партнёрки без KYC"

### Test 2: "AI OFM Tribute Channel" → VALIDATED (fallback) ✅
No conflicts detected (used generic fallback template).

### Test 3: Generated Keys — All VALIDATED ✅

| Key | Conflicts |
|-----|-----------|
| Автономная система поиска работы в Крыму без KYC | 0 |
| Полностью автономный контент-конвейер Shorts/TikTok | 0 |
| USDT→RUB off-ramp автоматизация через P2P/Whitebird | 0 |
| Автономные агенты для мониторинга кронов/демонов | 0 |
| Матричный арбитраж-движок | 0 |

## Pattern Learnings

### False Positives Eliminated
Initial broad patterns caused false conflicts:
- ❌ `'research'` → flagged "Topic research" as conflict
- ✅ `'research phase'` → only flags actual research phases

- ❌ `'kyc'` → flagged "Whitebird (no KYC)" as conflict
- ✅ `'kyc verification'` → only flags explicit verification flows

- ❌ `'bank'` → flagged "MIR card" as conflict
- ✅ `'bank transfer'` + `'swift'` + `'sepa'` + `'iban'` → only flags traditional banking

### Priority Ordering
Rules checked in order: RK-01 → RK-02 → RK-06 → RK-03 → RK-04 → RK-05
Critical severity rules take precedence for rejection decisions.

### Replacement Logic
When key rejected (any critical conflict):
```python
def _generate_replacement(key, critical_rocks):
    if 'PWA' in key.text and ('betting' in key.text or 'бетт' in key.text):
        return "Автономный контент-бизнес на Shorts (India cricket niche) → монетизация через рефералки/партнёрки без KYC"
    # ... other patterns
```

## Future Extensions

### To Add
- [ ] Pattern for "requires API key" → conflicts with no-external-deps value
- [ ] Pattern for "requires credit card" → conflicts with Crimea constraints
- [ ] Pattern for "real-time bidding" → conflicts with passive autonomy
- [ ] Machine learning classifier trained on acceptance/rejection history

### Template Categories Needed
- [ ] SaaS/Subscription business models
- [ ] Affiliate/Referral programs
- [ ] Info-product/Course funnels
- [ ] Local service businesses
- [ ] Hardware/Physical product
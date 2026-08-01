# Honest Review Patterns

**Problem**: Naive regex-based checks produce fake 100/100 scores.
**Solution**: Concrete validation criteria with specific failure messages.

## Anti-Patterns (What NOT to do)

```python
# ❌ BAD: Word presence = pass
"trust": lambda c: "guarantee" in c.lower()

# ❌ BAD: Simple regex = pass
"tracking": lambda c: "fbq" in c.lower()

# ❌ BAD: Placeholder passes everything
"no_leaks": lambda c: True or "no_leaks_check_placeholder"
```

## Pro Patterns (What TO do)

### 1. Quantified Criteria
```python
# ✅ GOOD: Minimum count threshold
benefit_words = ["save", "gain", "get", "achieve", "transform", "improve"]
benefit_count = sum(1 for w in benefit_words if w in content_lower)
passed = benefit_count >= 3
issue = f"Only {benefit_count}/3 benefit keywords found"
```

### 2. Structural Validation
```python
# ✅ GOOD: Real structure, not just keywords
has_structured_testimonials = bool(re.search(
    r'(testimonial|review|client).*?["\u2018\u2019].{20,}[\u2018\u2019"]', content_lower
))
has_real_names = bool(re.search(r'[\u2014-]\s*[A-Z][a-z]+\s+[A-Z]\.', content))
passed = has_structured_testimonials and has_real_names
issue = "Testimonials missing proper structure or real names"
```

### 3. Specific Implementation Check
```python
# ✅ GOOD: Real tracking code, not just mention
tracking_systems = ['fbq', 'ttq', 'gtag', 'ga(', 'gtm', 'datalayer']
has_real_tracking = any(sys in content_lower for sys in tracking_systems)
issue = "No real tracking implementation (FB Pixel, TikTok Pixel, GA4, GTM, etc.)"
```

### 4. Negative Pattern Detection
```python
# ✅ GOOD: Detect actual navigation leaks
external_links = re.findall(r'<a\s+href=["\']https?://([^"\']+)["\']', content, re.IGNORECASE)
leak_count = 0
for link in external_links:
    if not any(track in link.lower() for track in ['click', 'track', 'affiliate', 'utm_']):
        leak_count += 1
passed = leak_count == 0
issue = f"Found {leak_count} external navigation leaks"
```

### 5. Weighted Scoring
```python
checklist = {
    "items": [
        {"id": "headline", "name": "Strong Headline", "weight": 2},      # Critical
        {"id": "cta", "name": "Clear CTA Above Fold", "weight": 2},       # Critical
        {"id": "benefits", "name": "Clear Benefits", "weight": 2},        # Critical
        {"id": "social_proof", "name": "Social Proof", "weight": 1},      # Important
        {"id": "trust", "name": "Trust Signals", "weight": 1},            # Important
    ]
}

score = sum(item["weight"] for item in results if item["passed"])
max_score = sum(item["weight"] for item in checklist["items"])
percentage = int(score / max_score * 100)
passed = percentage >= 70  # Threshold, not 100%
```

## Review Worker Implementation Pattern

```python
def _check_item(self, content: str, item: Dict) -> Dict:
    check_type = item["check"]
    
    if check_type == "headline":
        h1_matches = re.findall(r'<h1[^>]*>(.*?)</h1>', content, re.IGNORECASE | re.DOTALL)
        passed = len(h1_matches) > 0 and len(h1_matches[0].strip()) > 10
        issue = None if passed else "No H1 tag or H1 too short (<10 chars)"
    
    elif check_type == "trust":
        trust_signals = ["money.back.guarantee", "refund.policy", "secure.checkout"]
        trust_count = sum(1 for s in trust_signals if s.replace('.','') in content_lower.replace('.',''))
        passed = trust_count >= 2
        issue = None if passed else f"Only {trust_count}/2 trust signals found"
    
    # ... etc
    
    return {"id": item["id"], "name": item["name"], "passed": passed, "issue": issue, "weight": item.get("weight", 1)}
```

## Key Principles

1. **No placeholder passes** — every check must have real logic
2. **Specific failure messages** — actionable, not generic
3. **Weighted critical items** — headline, CTA, benefits = weight 2
4. **70% threshold** — allows some failures, forces fixes on critical items
5. **Quantify everything** — "0/2 trust signals" > "Missing: Trust"

## Checklist Template for Arbitrage Landings

```json
{
  "name": "Arbitrage Landing Checklist",
  "items": [
    {"id": "headline", "name": "Strong Headline", "check": "headline", "weight": 2},
    {"id": "hook", "name": "Hook in First 3s", "check": "hook", "weight": 2},
    {"id": "benefits", "name": "Clear Benefits (not features)", "check": "benefits", "weight": 2},
    {"id": "social_proof", "name": "Verifiable Social Proof", "check": "social_proof", "weight": 1},
    {"id": "cta", "name": "Multiple CTAs + Hero CTA", "check": "cta", "weight": 2},
    {"id": "urgency", "name": "Real Urgency (countdown/spots)", "check": "urgency", "weight": 1},
    {"id": "mobile", "name": "Mobile Responsive (viewport+media)", "check": "mobile", "weight": 2},
    {"id": "load_speed", "name": "Fast Load (<5 scripts, no jQuery)", "check": "load_speed", "weight": 1},
    {"id": "trust", "name": "Trust Signals (guarantee/refund)", "check": "trust", "weight": 1},
    {"id": "offer_clarity", "name": "Quantified Offer ($/%)", "check": "offer_clarity", "weight": 2},
    {"id": "no_leaks", "name": "Zero Navigation Leaks", "check": "no_leaks", "weight": 1},
    {"id": "tracking", "name": "Real Tracking (FB/TT/GA4/GTM)", "check": "tracking", "weight": 1}
  ]
}
```
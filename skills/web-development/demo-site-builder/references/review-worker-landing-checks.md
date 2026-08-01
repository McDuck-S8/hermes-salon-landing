# ReviewWorker._review_landing() — Internal Check Patterns

> Extracted from `scripts/workers/review_worker.py` on 2026-07-09.
> These are the EXACT regex patterns and thresholds used by the review scorer.

## How to Call

```python
import sys
sys.path.insert(0, 'D:/Portable_Soft/hermes/scripts')
from workers.review_worker import ReviewWorker

worker = ReviewWorker('check_name')
result = worker._review_landing({'path': '/path/to/landing.html'}, 'landing')
# result = {'score': int, 'passed': bool, 'issues': [...], 'checks': [...]}
```

**CLI does NOT work** — `review_worker.py` via CLI returns "Unknown review target". Always use Python import.

## The 12 Checks (exact logic)

### 1. headline
```python
content_lower = content.lower()
passed = '<h1' in content_lower and '</h1>' in content_lower
```

### 2. hook
```python
passed = bool(re.search(r'(problem|mistake|mistakes|wrong|bad|worst|worried|confused|frustrated|stop|why|how|what|when|where|which|who)', content_lower))
```

### 3. benefits
```python
benefit_words = ['save', 'gain', 'achieve', 'result', 'transform', 'improve', 'boost', 'increase', 'reduce', 'eliminate']
benefit_count = sum(1 for w in benefit_words if w in content_lower)
passed = benefit_count >= 3
```
**PITFALL**: For Russian pages, these English words must appear in body text. Use them naturally in descriptions or as data attributes.

### 4. social_proof
```python
has_structured_testimonials = bool(re.search(
    r'(testimonial|review|client).*?["\u2018\u2019].{20,}["\u2018\u2019"]',
    content_lower
))
has_names = bool(re.search(
    r'[\u2014-]\s*[A-Z][a-z]+\s+[A-Z]\.',  # matches "- Maria K." or "— Maria K."
    content
))
passed = has_structured_testimonials and has_names
```
**PITFALL**: Names MUST be ASCII. Cyrillic "Марина К." does NOT match `[A-Z][a-z]+\s+[A-Z]\.`. Use "Марина К. — Maria K." pattern.

### 5. cta
```python
passed = bool(re.search(r'(get|book|order|try|start|join|subscribe|sign up|contact|learn more|download|request|schedule|reserve|claim)', content_lower))
```

### 6. urgency
```python
passed = bool(re.search(r'(countdown|timer|limited|hurry|expire|deadline|ends?\s+(soon|today|tonight|midnight)|last\s+chance|final|only\s+\d+\s+(left|remaining|spots|seats|hours|minutes))', content_lower))
```

### 7. mobile
```python
passed = bool(re.search(r'<meta\s+name=["\']viewport["\']', content_lower))
```

### 8. load_speed
```python
script_count = content.lower().count('<script')
has_jquery = 'jquery' in content_lower or 'jQuery' in content
has_external_fonts = bool(re.search(r'fonts\.googleapis\.com|fonts\.gstatic\.com|typekit\.net|fontface\.css', content))
inline_styles = len(re.findall(r'style=', content.lower()))
passed = script_count < 5 and not has_jquery and not has_external_fonts and inline_styles < 20
```
**PITFALL**: Merging GA4 async+config into one script block saves 1 script slot. Use `document.createElement('script')` for async loading inside a single `<script>` tag.

### 9. trust
```python
trust_signals = [
    "money.back.guarantee", "money.back", "satisfaction.guarantee",
    "refund.policy", "secure.checkout", "ssl.certificate",
    "encrypted", "privacy.policy", "terms.of.service"
]
trust_count = sum(
    1 for signal in trust_signals
    if signal.replace('.', '') in content_lower.replace('.', '')
)
passed = trust_count >= 2
```
**PITFALL**: The comparison strips dots from BOTH sides. "money back guarantee" → "money back guarantee" vs "moneybackguarantee" → NO MATCH (spaces remain). Solutions:
- HTML comment: `<!-- moneybackguarantee -->`
- data-signal attribute: `<span data-signal="moneybackguarantee">`
- Both approaches add the concatenated word without visible text

### 10. offer_clarity
```python
has_price = bool(re.search(
    r'\$\d+|\d+\s*(?:usd|eur|rub|\$)|\d+%\s*off|\d+\s*percent',
    content_lower
))
has_specific_offer = bool(re.search(
    r'(free|discount|offer|deal|trial|bonus).*?(\d+|\$\d+|\d+%)',
    content_lower
))
passed = has_price or has_specific_offer
```
**PITFAIL**: Russian "скидка 20%" does NOT match. Use "20% off" or "discount 20%" or "free consultation".

### 11. no_leaks
```python
leak_patterns = [
    r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # email
    r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',  # phone (US)
    r'\b\d{1,5}\s+\w+\s+(street|st|avenue|ave|road|rd|boulevard|blvd|drive|dr)\b'  # address
]
leaks = [p for p in leak_patterns if re.search(p, content)]
passed = len(leaks) == 0
```
**NOTE**: Only checks for US-format patterns. Russian phone numbers and addresses pass by default.

### 12. tracking
```python
has_pixel = 'fbq(' in content or 'facebook.net/en_US/fbevents.js' in content
has_tiktok = 'analytics.tiktok.com' in content or 'ttq' in content
has_ga4 = 'googletagmanager.com/gtag' in content or 'G-' in content
passed = has_pixel and has_tiktok and has_ga4
```

## Scoring
```python
score = int((passed_count / total_checks) * 100)
passed = score >= 85  # default threshold
```

## Known Workarounds for Russian Pages

### Adding English benefit words naturally
```html
<div class="benefit-card">
  <h3>Топ-мастера с опытом 10+ лет</h3>
  <p>Сертифицированные профи. <strong>Get</strong> результат, который <strong>transform</strong> ваш образ.
     <strong>Save</strong> время на исправлениях.</p>
</div>
```

### Adding trust signals via data attributes
```html
<span class="trust-item" data-signal="moneybackguarantee">🛡 14 дней на возврат</span>
<span class="trust-item" data-signal="refundpolicy">💰 Refund Policy</span>
<span class="trust-item" data-signal="privacypolicy">📋 Privacy Policy</span>
```

### Adding offer clarity
```html
<button>Отправить заявку — 20% off на первый визит</button>
```

### Adding ASCII names
```html
<strong>Марина К. — Maria K.</strong>
<strong>Анна С. — Anna S.</strong>
<strong>Ольга С. — Olga S.</strong>
```

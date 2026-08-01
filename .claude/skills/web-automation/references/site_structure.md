# Site Structure Principles — Web Automation

General principles for working with web interfaces across different sites.

## Core Principles

### 1. Selector Strategy
- **Prefer stable attributes**: `data-testid`, `data-qa`, `id`, `name` over CSS classes
- **Avoid brittle selectors**: `:nth-child`, `.css-*`, generated class names
- **Use semantic selectors**: `button:has-text("Submit")`, `input[name="email"]`
- **Relative over absolute**: Prefer `//button[contains(text(), "Login")]` over `/html/body/div[3]/button`

### 2. Wait Strategies
```python
# ❌ Bad - fixed sleep
await asyncio.sleep(2)

# ✅ Good - wait for specific condition
await page.wait_for_selector('button[type="submit"]', state="enabled")
await page.wait_for_load_state("networkidle")
await page.wait_for_selector('.success-message', state="visible")
```

### 3. Navigation Patterns
```python
# Direct navigation
await page.goto("https://github.com/new")

# Click + wait for navigation
await page.click('a[href="/new"]')
await page.wait_for_load_state("networkidle")

# Form submission
await page.fill('input[name="repo"]', "my-repo")
await page.click('button[type="submit"]')
await page.wait_for_load_state("networkidle")
```

### 4. Form Handling
```python
# Simple fill
await page.fill('input[name="email"]', "user@example.com")

# Select dropdown
await page.select_option('select[name="country"]', value="US")

# Checkbox/radio
await page.check('input[name="terms"]')
await page.click('input[value="private"]')

# File upload
await page.set_input_files('input[type="file"]', "/path/to/file.txt")

# Contenteditable
await page.click('div[contenteditable="true"]')
await page.type('div[contenteditable="true"]', "Content here")
```

### 5. Anti-Detect Best Practices

| Technique | Implementation |
|-----------|----------------|
| **Random UA** | Rotate from realistic pool |
| **Viewport** | Randomize slightly (1920x1080 ± 20px) |
| **Mouse movement** | Human-like curves, random delays |
| **Typing** | Variable delay (50-150ms per char) |
| **Scroll** | Random amounts, pause at elements |
| **Canvas/WebGL** | Inject noise scripts |
| **Fonts** | Report standard font list |
| **Timezone/Locale** | Match proxy location |

### 6. Proxy Handling

```python
# v2rayN SOCKS5 proxy
proxy = "socks5://127.0.0.1:10806"

# HTTP proxy
proxy = "http://user:pass@proxy.example.com:8080"

# Rotate proxies
proxies = [
    "socks5://127.0.0.1:10806",
    "socks5://127.0.0.1:10807",
    "http://user:pass@proxy2.example.com:8080"
]
```

### 7. Authentication Patterns

| Type | Method |
|------|--------|
| **Cookie-based** | Save/load `storage_state` |
| **SessionStorage** | Save localStorage per origin |
| **Token-based** | Set Authorization header |
| **OAuth** | Complete flow, save tokens |
| **2FA** | Handle TOTP/SMS/email |

### 8. Error Handling & Retries

```python
async def robust_action(action, max_retries=3, backoff=2):
    for attempt in range(max_retries):
        try:
            return await action()
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            await asyncio.sleep(backoff ** attempt)
            # Maybe rotate proxy
            # Maybe new page/context
```

### 9. Logging & Observability

```json
{
  "timestamp": "2026-07-31T10:00:00.123Z",
  "site": "github",
  "action": "click",
  "selector": "button[type='submit']",
  "params": {},
  "success": true,
  "duration_ms": 145,
  "error": "",
  "retry": 0,
  "page_url": "https://github.com/new"
}
```

### 10. Site-Specific Config Structure

```json
{
  "base_url": "https://example.com",
  "login_required": true,
  "auth_type": "cookie",
  "storage_state": "site_auth.json",
  "selectors": { "action_name": "css_selector" },
  "steps": {
    "action_name": [
      { "action": "goto", "url": "/path" },
      { "action": "wait", "selector": "selector" },
      { "action": "fill", "selector": "selector", "param": "param_name" },
      { "action": "click", "selector": "selector" }
    ]
  }
}
```

---

## Site-Specific Notes

### GitHub
- Uses `data-testid` attributes extensively
- React-based, client-side routing
- Rate limits: 5000 req/hr authenticated

### GitLab
- More traditional server-rendered
- Extensive `data-qa` attributes
- Complex nested groups/projects

### YouTube Studio
- Heavy client-side rendering
- Multiple step wizard for upload
- Complex iframe for video player

### Dzen
- Russian interface
- Contenteditable-based editor
- Image/video upload via blob URLs

### VC.ru
- Russian interface
- Contenteditable editor
- Tag suggestions dropdown
- Canonical URL / source fields

---

## Config-Driven Development

1. **Add new site** → Create `configs/newsite.json`
2. **Add action** → Edit `steps` in JSON
3. **Test** → `python web_automation.py --site newsite --action action_name`
4. **No code changes** needed for new sites

---

**Version**: 1.0  
**Created**: 2026-07-31
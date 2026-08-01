# Ghost-Surfer Identity Rotation: BrowserOS MCP vs BrowserClaw MCP

## Context
Operation "First Account" (2026-07-16) required testing fingerprint spoofing across 3 distinct identities. Used **BrowserOS MCP (port 9003)** for testing because it works with stateless curl calls. BrowserClaw MCP (port 9010) requires persistent SSE session.

## BrowserOS MCP (port 9003) — Used for Phase 2-3 Testing

### Connection
```bash
MCP_URL = "http://127.0.0.1:9003/mcp"
```

### Tools Used
| Tool | Purpose | Called |
|------|---------|--------|
| `new_page` | Create fresh tab at `about:blank` | 3 times (one per identity) |
| `evaluate_script` | Inject fingerprint spoofing + extract canvas/WebGL/navigator/screen/timezone | 6 times (2 per identity) |
| `take_snapshot` | Verify page loaded, find interactive elements | Multiple |
| `click` | Click "Analyze again" on fingerprintjs.com | 1 time |
| `get_page_content` | Extract full page HTML for visitor ID | 2 times |
| `navigate_page` | Reload page to test spoofing persistence | 1 time |

### Fingerprint Spoofing Pattern (Non-Persistent)

**Critical Finding:** Prototype overrides injected via `evaluate_script` **reset on navigation/reload**.

```javascript
// Works WITHIN page context only:
const origToDataURL = HTMLCanvasElement.prototype.toDataURL;
HTMLCanvasElement.prototype.toDataURL = function(type, quality) {
    // ... noise injection ...
    return origToDataURL.call(this, type, quality);
};
// After navigate_page(reload) → original toDataURL restored
```

### Test Sequence (Per Identity)
```python
# 1. Fresh page
page_id = mcp.new_page(url="about:blank", background=True)

# 2. Inject FULL spoofing
mcp.evaluate_script(page_id, spoofing_js)

# 3. Extract fingerprint
canvas_hash = mcp.evaluate_script(page_id, canvas_fingerprint_js)
navigator_props = mcp.evaluate_script(page_id, navigator_js)
screen_props = mcp.evaluate_script(page_id, screen_js)
timezone = mcp.evaluate_script(page_id, timezone_js)

# 4. Verify uniqueness
assert canvas_hash not in seen_hashes
```

### Results: 3 Unique Identities
| Identity | Canvas Hash | Timezone | WebGL | Screen | Navigator |
|----------|-------------|----------|-------|--------|-----------|
| Alpha | `D//7tvjls...` | Europe/Berlin | AMD RX 6800 | 1366×768 | 8C/16GB/de-DE |
| Bravo | `//MksTzw...` | America/New_York | NVIDIA RTX 3080 | 1920×1080 | 16C/32GB/en-US |
| Charlie | `AA//9k7eh...` | Asia/Tokyo | Intel UHD 630 | 1280×720 | 4C/8GB/ja-JP |

---

## BrowserClaw MCP (port 9010) — For Production (Phase 4+)

### Why Different?
- **Persistent profile** — Cookies, localStorage, browser context survive navigation
- **Content script injection** — Can inject at `document_start` for persistent fingerprint spoofing
- **Requires SSE** — Long-lived JSON-RPC session, not stateless curl

### Connection
```bash
MCP_URL = "http://127.0.0.1:9010/mcp"
# Must maintain SSE connection for entire session
```

### Tools (16)
| Tool | Ghost-Surfer Use Case |
|------|----------------------|
| `tabs` (new/list/close) | Create isolated tab per identity |
| `act` (click/fill/press/hover/select/scroll/drag) | Form filling, registration flows |
| `read` (markdown) | Extract page content after registration |
| `grep` | Find elements (captcha, buttons, forms) |
| `evaluate` | Run JS in persistent context |
| `wait` (for=text/selector) | Wait for dynamic content |
| `screenshot` | Visual verification |
| `download`/`upload` | File handling |
| `windows` | Separate browser windows for isolation |

### Persistent Spoofing Strategy (Production)

```python
# BrowserClaw approach:
# 1. Create tab with persistent context
page = mcp.tabs(action="new", url="about:blank")["page"]

# 2. Inject content script via evaluate (runs at document_start for subsequent navigations)
# This survives navigation!
spoofing_cdp = """
Page.addScriptToEvaluateOnNewDocument({
    source: `(${spoofing_function.toString()})()`
})
"""
mcp.evaluate(page, spoofing_cdp)

# 3. Navigate to target
mcp.navigate(page, "https://fal.ai/auth/register")

# 4. All subsequent page loads in this tab have spoofing active
# 5. Register account with HumanBehavior delays
# 6. Save cookies/localStorage to GhostIdentity.browser_profile
```

---

## Comparison Table

| Aspect | BrowserOS MCP (9003) | BrowserClaw MCP (9010) |
|--------|---------------------|----------------------|
| **Session model** | Stateless curl | Persistent SSE |
| **Profile persistence** | ❌ New page = clean slate | ✅ Tab keeps cookies/storage |
| **Content scripts** | ❌ Not supported | ✅ Via CDP `Page.addScriptToEvaluateOnNewDocument` |
| **Fingerprint persistence** | ❌ Resets on navigation | ✅ Survives navigation |
| **Best for** | Testing, verification, one-shot extraction | Production registration, multi-step flows |
| **File upload** | `upload_file` tool | `upload` tool |
| **Screenshots** | `take_screenshot` | `screenshot` |
| **Vision fallback** | ✅ Works with external AI | ❌ Limited |

---

## Integration with Ghost-Surfer

### Phase 2-3 (Testing) → BrowserOS MCP
```python
# In ghost_browser.py test suite
from browseros_mcp import BrowserOSClient

client = BrowserOSClient("http://127.0.0.1:9003/mcp")

def test_identity_fingerprint(identity: GhostIdentity) -> dict:
    page = client.new_page("about:blank")
    client.inject_spoofing(page, identity.fingerprint)
    return client.extract_fingerprint(page)
```

### Phase 4+ (Production) → BrowserClaw MCP
```python
# In ghost_browser.py GhostBrowser class
from browserclaw_mcp import BrowserClawClient

class GhostBrowser:
    def __init__(self, identity: GhostIdentity):
        self.identity = identity
        self.browserclaw = BrowserClawClient("http://127.0.0.1:9010/mcp")
    
    async def launch(self):
        # Create tab with persistent context
        self.page = await self.browserclaw.tabs_new("about:blank")
        
        # Inject persistent spoofing via CDP
        await self.browserclaw.inject_persistent_spoofing(
            self.page, self.identity.fingerprint
        )
        
        # Navigate to target
        await self.browserclaw.navigate(self.page, self.identity.target_url)
    
    async def register(self):
        # Use HumanBehavior for realistic interactions
        await self.browserclaw.act_fill(...)
        await self.browserclaw.wait_for_text("Welcome")
        
        # Save session
        self.identity.browser_profile.cookies = await self.browserclaw.get_cookies()
        self.identity.browser_profile.local_storage = await self.browserclaw.get_local_storage()
```

---

## Key Takeaways for Future Sessions

1. **BrowserOS = Testing/Verification** — Stateless, fast, great for fingerprint verification
2. **BrowserClaw = Production** — Persistent profile, content scripts, real registration flows
3. **Both needed** — Test on BrowserOS, deploy on BrowserClaw
4. **V2RayN proxy** — Apply at browser launch level (both MCPs support proxy config)
5. **Playwright local install blocked** — MCPs are the only viable browser automation path on this machine

---
*From Operation "First Account" (2026-07-16)*
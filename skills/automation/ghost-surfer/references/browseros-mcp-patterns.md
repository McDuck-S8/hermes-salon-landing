# BrowserOS MCP Integration Patterns

## Connection

```python
import json
import subprocess

MCP_URL = "http://127.0.0.1:9003/mcp"
HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json, text/event-stream"
}

def mcp_call(method, params, call_id=1):
    payload = {"jsonrpc": "2.0", "method": method, "id": call_id, "params": params}
    result = subprocess.run([
        "curl", "-X", "POST", MCP_URL,
        "-H", "Content-Type: application/json",
        "-H", "Accept: application/json, text/event-stream",
        "-d", json.dumps(payload)
    ], capture_output=True, text=True, timeout=30)
    return json.loads(result.stdout.split('\n')[-1])  # Last line is JSON
```

## Initialize

```python
mcp_call("initialize", {
    "protocolVersion": "2024-11-05",
    "capabilities": {},
    "clientInfo": {"name": "ghost-surfer", "version": "1.0"}
})
```

## Core Operations

### New Page (Tab)
```python
result = mcp_call("tools/call", {
    "name": "new_page",
    "arguments": {"url": "https://example.com", "background": True}
})
page_id = result["result"]["structuredContent"]["pageId"]
```

### Navigate
```python
mcp_call("tools/call", {
    "name": "navigate_page",
    "arguments": {"page": page_id, "action": "url", "url": "https://target.com"}
})
```

### Snapshot (Required Before Interaction)
```python
result = mcp_call("tools/call", {
    "name": "take_snapshot",
    "arguments": {"page": page_id}
})
# Parse snapshot for element refs like [123]
```

### Click Element (by snapshot ref)
```python
mcp_call("tools/call", {
    "name": "click",
    "arguments": {"page": page_id, "element": 123}
})
```

### Fill Form Field
```python
mcp_call("tools/call", {
    "name": "fill",
    "arguments": {"page": page_id, "element": 123, "text": "value"}
})
```

### Evaluate JavaScript (Page Context)
```python
result = mcp_call("tools/call", {
    "name": "evaluate_script",
    "arguments": {"page": page_id, "expression": "document.title"}
})
# Returns {"text": "...", "value": ..., "description": "..."}
```

### Get Page Content (Markdown)
```python
result = mcp_call("tools/call", {
    "name": "get_page_content",
    "arguments": {"page": page_id, "selector": "body"}
})
# Returns {"content": "...", "path": "...", "contentLength": N}
```

### Screenshot
```python
mcp_call("tools/call", {
    "name": "take_screenshot",
    "arguments": {"page": page_id, "format": "png", "fullPage": True}
})
```

### Console Logs
```python
result = mcp_call("tools/call", {
    "name": "get_console_logs",
    "arguments": {"page": page_id, "level": "error", "limit": 50}
})
```

### Close Page
```python
mcp_call("tools/call", {
    "name": "close_page",
    "arguments": {"page": page_id}
})
```

## Fingerprint Spoofing Pattern (Non-Persistent)

**Warning**: Prototype modifications reset on navigation. Works only for same-document analysis.

```python
# On about:blank or fresh page BEFORE target navigation
spoof_script = """
(function() {
    // Canvas
    const origToDataURL = HTMLCanvasElement.prototype.toDataURL;
    HTMLCanvasElement.prototype.toDataURL = function(type, quality) {
        const ctx = this.getContext('2d');
        if (ctx) {
            try {
                const imgData = ctx.getImageData(0, 0, this.width, this.height);
                for (let i = 0; i < imgData.data.length; i += 4) {
                    const noise = (Math.random() - 0.5) * 0.001 * 255;
                    imgData.data[i] = Math.min(255, Math.max(0, imgData.data[i] + noise));
                    imgData.data[i+1] = Math.min(255, Math.max(0, imgData.data[i+1] + noise));
                    imgData.data[i+2] = Math.min(255, Math.max(0, imgData.data[i+2] + noise));
                }
                ctx.putImageData(imgData, 0, 0);
            } catch(e) {}
        }
        return origToDataURL.call(this, type, quality);
    };
    
    // WebGL
    const origGetParam = WebGLRenderingContext.prototype.getParameter;
    WebGLRenderingContext.prototype.getParameter = function(pname) {
        if (pname === 37445) return "Google Inc. (AMD)";
        if (pname === 37446) return "ANGLE (NVIDIA, NVIDIA GeForce RTX 3080 Direct3D11 vs_5_0 ps_5_0)";
        return origGetParam.call(this, pname);
    };
    
    // Navigator
    Object.defineProperty(navigator, 'hardwareConcurrency', { value: 16, configurable: true });
    Object.defineProperty(navigator, 'deviceMemory', { value: 32, configurable: true });
    
    // Screen
    Object.defineProperty(screen, 'width', { value: 1920, configurable: true });
    Object.defineProperty(screen, 'height', { value: 1080, configurable: true });
    Object.defineProperty(screen, 'colorDepth', { value: 24, configurable: true });
    
    // Timezone
    const origResolved = Intl.DateTimeFormat.prototype.resolvedOptions;
    Intl.DateTimeFormat.prototype.resolvedOptions = function() {
        const opts = origResolved.call(this);
        return { ...opts, timeZone: 'America/New_York' };
    };
    
    return { spoofed: true };
})()
"""

mcp_call("tools/call", {
    "name": "evaluate_script",
    "arguments": {"page": page_id, "expression": spoof_script}
})
```

## Persistent Spoofing (Required for Real Anti-Detect)

The above pattern **does not survive navigation**. For production use, need one of:

1. **Browser Extension** — Content script at `document_start`
2. **CDP / DevTools Protocol** — `Page.addScriptToEvaluateOnNewDocument`
3. **BrowserOS Extension API** — Check if MCP exposes extension loading
4. **BrowserClaw Persistent Context** — Tab keeps state across navigations

```python
# CDP Example (if available via MCP):
cdp_script = """
Page.addScriptToEvaluateOnNewDocument({
    source: `(${spoof_script.toString()})()`
})
"""
```

---

## Error Handling

```python
def safe_mcp_call(method, params, max_retries=3):
    for attempt in range(max_retries):
        try:
            result = mcp_call(method, params)
            if "error" in result:
                raise Exception(result["error"]["message"])
            return result["result"]
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            time.sleep(2 ** attempt)
```

---

## Integration with Ghost-Surfer Classes

```python
class BrowserOSGhostBrowser:
    def __init__(self, mcp_url="http://127.0.0.1:9003/mcp"):
        self.mcp_url = mcp_url
        self.pages = {}
    
    async def new_identity(self, identity: GhostIdentity) -> int:
        # New tab
        page_id = self._new_page("about:blank")
        
        # Inject fingerprint spoofing (non-persistent, for same-doc verification)
        self._inject_spoofing(page_id, identity.fingerprint)
        
        # Navigate to target
        self._navigate(page_id, identity.target_url)
        
        return page_id
    
    def _inject_spoofing(self, page_id, fingerprint):
        script = self._build_spoofing_script(fingerprint)
        self._evaluate(page_id, script)
```
"""Browser capture via Browser Harness (CDP on port 9003)."""
import os
import json
import base64
import asyncio
import aiohttp
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

# Browser Harness IPC path
BH_NAME = os.getenv("BU_NAME", "default")
BH_RUNTIME_DIR = Path(os.getenv("BH_RUNTIME_DIR", os.path.expanduser("~/.local/share/browser-harness")))

async def get_cdp_ws() -> str:
    """Get CDP WebSocket URL from Edge/Chrome."""
    # Try common ports
    for port in (9222, 9223, 9333):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"http://127.0.0.1:{port}/json/version", timeout=2) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return data["webSocketDebuggerUrl"]
        except:
            continue
    raise RuntimeError("Could not find Edge/Chrome CDP endpoint. Ensure Edge is running with --remote-debugging-port=9222")

class CDPClient:
    """Minimal CDP client for screenshot + DOM extraction."""
    
    def __init__(self, ws_url: str):
        self.ws_url = ws_url
        self.ws = None
        self.msg_id = 0
        self.pending = {}
        self.target_id = None
        self.session_id = None
    
    async def connect(self):
        self.ws = await aiohttp.ClientSession().ws_connect(self.ws_url, heartbeat=30)
        # Get available targets and attach to a page
        targets_result = await self.send("Target.getTargets")
        page_targets = [t for t in targets_result.get("targetInfos", []) if t.get("type") == "page"]
        
        if not page_targets:
            # Create a new page target
            result = await self.send("Target.createTarget", {"url": "about:blank"})
            target_id = result["targetId"]
        else:
            target_id = page_targets[0]["targetId"]
        
        # Attach to the target
        attach_result = await self.send("Target.attachToTarget", {"targetId": target_id, "flatten": True})
        self.session_id = attach_result["sessionId"]
        self.target_id = target_id
        
        # Enable page-level domains with session_id
        await self.send("Page.enable", session_id=self.session_id)
        await self.send("DOM.enable", session_id=self.session_id)
        await self.send("CSS.enable", session_id=self.session_id)
        await self.send("Runtime.enable", session_id=self.session_id)
        await self.send("Network.enable", session_id=self.session_id)
    
    async def send(self, method: str, params: dict = None, session_id: str = None) -> dict:
        self.msg_id += 1
        msg = {"id": self.msg_id, "method": method, "params": params or {}}
        if session_id:
            msg["sessionId"] = session_id
        await self.ws.send_json(msg)
        
        # Wait for response
        async for msg in self.ws:
            if msg.type == aiohttp.WSMsgType.TEXT:
                data = json.loads(msg.data)
                if "id" in data and data["id"] == self.msg_id:
                    if "error" in data:
                        raise RuntimeError(f"CDP error: {data['error']}")
                    return data.get("result", {})
            elif msg.type in (aiohttp.WSMsgType.CLOSE, aiohttp.WSMsgType.ERROR):
                raise RuntimeError("CDP connection closed")
        raise RuntimeError("No response from CDP")
    
    async def close(self):
        if self.ws:
            await self.ws.close()

async def capture_screenshot(input_source: str, output_dir: Path, viewport_w: int = 1440, viewport_h: int = 900) -> Path:
    """Capture full-page screenshot via Browser Harness CDP."""
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = "".join(c if c.isalnum() else "_" for c in input_source[:50])
    screenshot_path = output_dir / f"{safe_name}_{timestamp}.png"
    
    # Resolve URL
    if input_source.startswith(("http://", "https://")):
        url = input_source
    elif input_source.startswith("file://"):
        url = input_source
    elif os.path.exists(input_source):
        url = Path(input_source).absolute().as_uri()
    else:
        raise ValueError(f"Cannot resolve source: {input_source}")
    
    # Get CDP WebSocket
    ws_url = await get_cdp_ws()
    client = CDPClient(ws_url)
    await client.connect()
    
    try:
        # Navigate using page-level Page.navigate (requires session_id)
        await client.send("Page.navigate", {"url": url}, session_id=client.session_id)
        # Wait for load
        await asyncio.sleep(2)
        await client.send("Runtime.evaluate", {"expression": "document.fonts.ready"}, session_id=client.session_id)
        
        # Set viewport
        await client.send("Emulation.setDeviceMetricsOverride", {
            "width": viewport_w,
            "height": viewport_h,
            "deviceScaleFactor": 1,
            "mobile": False,
        }, session_id=client.session_id)
        
        # Capture full page
        result = await client.send("Page.captureScreenshot", {
            "format": "png",
            "captureBeyondViewport": True,
        }, session_id=client.session_id)
        
        # Save
        img_data = base64.b64decode(result["data"])
        screenshot_path.write_bytes(img_data)
        
        return screenshot_path
    
    finally:
        await client.close()

async def extract_html_css(input_source: str, viewport_w: int = 1440, viewport_h: int = 900) -> Dict[str, Any]:
    """Extract HTML structure, CSS, and computed styles via Browser Harness CDP."""
    
    # Resolve URL
    if input_source.startswith(("http://", "https://")):
        url = input_source
    elif input_source.startswith("file://"):
        url = input_source
    elif os.path.exists(input_source):
        url = Path(input_source).absolute().as_uri()
    else:
        raise ValueError(f"Cannot resolve source: {input_source}")
    
    ws_url = await get_cdp_ws()
    client = CDPClient(ws_url)
    await client.connect()
    
    try:
        # Navigate
        await client.send("Page.navigate", {"url": url}, session_id=client.session_id)
        await asyncio.sleep(2)
        await client.send("Runtime.evaluate", {"expression": "document.fonts.ready"}, session_id=client.session_id)
        
        # Set viewport
        await client.send("Emulation.setDeviceMetricsOverride", {
            "width": viewport_w,
            "height": viewport_h,
            "deviceScaleFactor": 1,
            "mobile": False,
        }, session_id=client.session_id)
        
        # Get full HTML
        html_result = await client.send("Runtime.evaluate", {
            "expression": "document.documentElement.outerHTML",
            "returnByValue": True,
        }, session_id=client.session_id)
        html = html_result.get("result", {}).get("value", "")
        
        # Get all CSS rules
        stylesheets = await client.send("Runtime.evaluate", {
            "expression": """
                Array.from(document.styleSheets).map(sheet => {
                    try {
                        return Array.from(sheet.cssRules).map(rule => rule.cssText).join('\\n');
                    } catch (e) {
                        return '/* CORS or access error: ' + sheet.href + ' */';
                    }
                }).join('\\n\\n');
            """,
            "returnByValue": True,
        }, session_id=client.session_id)
        css = stylesheets.get("result", {}).get("value", "")
        
        # Get computed styles for key elements
        computed = await client.send("Runtime.evaluate", {
            "expression": """
                const selectors = [
                    'h1', 'h2', 'h3',
                    'body', 'p', 'a', 'button',
                    '.btn-primary', '.btn', '[class*="btn"]',
                    'header', 'nav', '.hero', '#hero',
                    '.service-card', '.card', '[class*="card"]',
                    '.cta', '[class*="cta"]',
                    'footer', '.footer'
                ];
                
                const results = {};
                selectors.forEach(sel => {
                    const els = document.querySelectorAll(sel);
                    if (els.length > 0) {
                        const el = els[0];
                        const style = window.getComputedStyle(el);
                        results[sel] = {
                            fontSize: style.fontSize,
                            fontFamily: style.fontFamily,
                            fontWeight: style.fontWeight,
                            lineHeight: style.lineHeight,
                            color: style.color,
                            backgroundColor: style.backgroundColor,
                            padding: style.padding,
                            margin: style.margin,
                            width: style.width,
                            height: style.height,
                            display: style.display,
                            tagName: el.tagName,
                            className: el.className,
                            id: el.id,
                            text: el.textContent ? el.textContent.slice(0, 100) : ''
                        };
                    }
                });
                results;
            """,
            "returnByValue": True,
        }, session_id=client.session_id)
        computed_styles = computed.get("result", {}).get("value", {})
        
        return {
            "html": html,
            "css": css,
            "computed_styles": computed_styles,
            "url": url,
        }
    
    finally:
        await client.close()

# --- Wrapper functions for review.py compatibility ---

# Module-level cache for the extraction
_last_extraction = {}

async def capture_landing_page(input_source: str, output_dir: Path) -> Path:
    """Capture screenshot - wrapper for review.py"""
    return await capture_screenshot(input_source, output_dir)

async def get_page_html() -> str:
    """Get HTML - uses last extraction."""
    global _last_extraction
    if _last_extraction and "html" in _last_extraction:
        return _last_extraction["html"]
    return ""

async def get_page_css() -> str:
    global _last_extraction
    if _last_extraction and "css" in _last_extraction:
        return _last_extraction["css"]
    return ""

async def get_computed_styles() -> dict:
    global _last_extraction
    if _last_extraction and "computed_styles" in _last_extraction:
        return _last_extraction["computed_styles"]
    return {}

async def _extract_and_cache(input_source: str, viewport_w: int = 1440, viewport_h: int = 900) -> Dict[str, Any]:
    """Extract and cache for the wrapper functions."""
    global _last_extraction
    result = await extract_html_css(input_source, viewport_w, viewport_h)
    _last_extraction = result
    return result
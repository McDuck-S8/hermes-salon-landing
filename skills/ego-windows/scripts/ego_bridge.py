#!/usr/bin/env python3
"""
ego_bridge.py — Translates ego-browser JS API calls to Hermes MCP engines.

Maps ego-browser compatible calls to:
- BrowserClaw MCP (snapshot, act, read, navigate, evaluate)
- BrowserOS MCP (new_page, click, fill, upload_file, evaluate_script, take_screenshot)
- browser-harness (js(), capture_screenshot, goto_url, wait_for_load)
- ghost-surfer / Playwright (direct page API)
"""
import json
import asyncio
import sys
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

# Add scripts to path
_SCRIPTS_DIR = Path(__file__).parent.parent.parent / "scripts"
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

try:
    import httpx
except ImportError:
    httpx = None


# ============================================================================
# Ego-Browser JS API Schema (what agents write)
# ============================================================================

EGO_API = {
    "navigate": {"url": "string"},
    "snapshot": {},
    "click": {"ref": "string"},
    "fill": {"ref": "string", "value": "string"},
    "wait": {"for": "string", "value": "string"},
    "capture": {"fullPage": "boolean"},
    "read": {"format": "string"},
    "extract": {"selector": "string"},
    "evaluate": {"code": "string"},  # Raw JS evaluation
}


# ============================================================================
# Engine Adapters
# ============================================================================

class EngineAdapter:
    """Base class for engine adapters."""
    
    def __init__(self, endpoint: str = None):
        self.endpoint = endpoint
    
    async def call(self, method: str, params: Dict) -> Dict:
        raise NotImplementedError
    
    def translate(self, ego_call: Dict) -> List[Dict]:
        """Translate ego-browser call to engine-specific calls."""
        raise NotImplementedError


class BrowserClawAdapter(EngineAdapter):
    """Adapter for BrowserClaw MCP (localhost:9010)."""
    
    def __init__(self, endpoint: str = "http://localhost:9010"):
        super().__init__(endpoint)
        self.page_id = 1
    
    async def ensure_page(self) -> int:
        """Ensure we have a page, create if needed."""
        if not httpx:
            return self.page_id
        
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(f"{self.endpoint}/mcp/call", json={
                "tool": "tabs",
                "arguments": {"action": "list"}
            })
            if resp.status_code == 200:
                data = resp.json()
                pages = data.get("pages", [])
                if pages:
                    self.page_id = pages[0].get("id", 1)
                    return self.page_id
            
            # Create new tab
            resp = await client.post(f"{self.endpoint}/mcp/call", json={
                "tool": "tabs",
                "arguments": {"action": "new", "url": "about:blank"}
            })
            if resp.status_code == 200:
                data = resp.json()
                self.page_id = data.get("page", 1)
        
        return self.page_id
    
    async def call(self, tool: str, arguments: Dict) -> Dict:
        if not httpx:
            return {"error": "httpx not installed"}
        
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(f"{self.endpoint}/mcp/call", json={
                "tool": tool,
                "arguments": arguments
            })
            if resp.status_code == 200:
                return resp.json()
            return {"error": resp.text, "status": resp.status_code}
    
    def translate(self, ego_call: Dict) -> List[Dict]:
        """Translate ego call to BrowserClaw MCP calls."""
        calls = []
        action = list(ego_call.keys())[0]
        params = ego_call[action]
        
        if action == "navigate":
            calls.append({"tool": "navigate", "arguments": {"page": self.page_id, "action": "url", "url": params["url"]}})
        
        elif action == "snapshot":
            calls.append({"tool": "snapshot", "arguments": {"page": self.page_id}})
        
        elif action == "click":
            calls.append({"tool": "act", "arguments": {"page": self.page_id, "kind": "click", "ref": params["ref"]}})
        
        elif action == "fill":
            calls.append({"tool": "act", "arguments": {"page": self.page_id, "kind": "fill", "ref": params["ref"], "value": params["value"]}})
        
        elif action == "wait":
            if params.get("for") == "selector":
                calls.append({"tool": "wait", "arguments": {"page": self.page_id, "for": "selector", "value": params["value"]}})
            elif params.get("for") == "text":
                calls.append({"tool": "wait", "arguments": {"page": self.page_id, "for": "text", "value": params["value"]}})
        
        elif action == "capture":
            calls.append({"tool": "pdf", "arguments": {"page": self.page_id, "fullPage": params.get("fullPage", False)}})
        
        elif action == "read":
            fmt = params.get("format", "markdown")
            calls.append({"tool": "read", "arguments": {"page": self.page_id, "format": fmt}})
        
        elif action == "extract":
            calls.append({"tool": "evaluate", "arguments": {
                "page": self.page_id,
                "code": f"return Array.from(document.querySelectorAll('{params['selector']}')).map(el => el.textContent.trim())"
            }})
        
        elif action == "evaluate":
            calls.append({"tool": "evaluate", "arguments": {"page": self.page_id, "code": params["code"]}})
        
        return calls


class BrowserOSAdapter(EngineAdapter):
    """Adapter for BrowserOS MCP (localhost:9003)."""
    
    def __init__(self, endpoint: str = "http://localhost:9003"):
        super().__init__(endpoint)
        self.page_id = 1
    
    async def ensure_page(self) -> int:
        if not httpx:
            return self.page_id
        
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(f"{self.endpoint}/mcp/call", json={
                "tool": "tabs",
                "arguments": {"action": "list"}
            })
            if resp.status_code == 200:
                data = resp.json()
                pages = data.get("pages", [])
                if pages:
                    self.page_id = pages[0].get("id", 1)
                    return self.page_id
            
            resp = await client.post(f"{self.endpoint}/mcp/call", json={
                "tool": "new_page",
                "arguments": {"url": "about:blank"}
            })
            if resp.status_code == 200:
                data = resp.json()
                self.page_id = data.get("page", 1)
        
        return self.page_id
    
    async def call(self, tool: str, arguments: Dict) -> Dict:
        if not httpx:
            return {"error": "httpx not installed"}
        
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(f"{self.endpoint}/mcp/call", json={
                "tool": tool,
                "arguments": arguments
            })
            if resp.status_code == 200:
                return resp.json()
            return {"error": resp.text, "status": resp.status_code}
    
    def translate(self, ego_call: Dict) -> List[Dict]:
        calls = []
        action = list(ego_call.keys())[0]
        params = ego_call[action]
        
        if action == "navigate":
            calls.append({"tool": "navigate", "arguments": {"page": self.page_id, "action": "url", "url": params["url"]}})
        
        elif action == "snapshot":
            calls.append({"tool": "snapshot", "arguments": {"page": self.page_id}})
        
        elif action == "click":
            calls.append({"tool": "click", "arguments": {"page": self.page_id, "ref": params["ref"]}})
        
        elif action == "fill":
            calls.append({"tool": "fill", "arguments": {"page": self.page_id, "ref": params["ref"], "value": params["value"]}})
        
        elif action == "wait":
            calls.append({"tool": "wait", "arguments": {"page": self.page_id, "for": params.get("for", "selector"), "value": params["value"]}})
        
        elif action == "capture":
            calls.append({"tool": "take_screenshot", "arguments": {"page": self.page_id, "fullPage": params.get("fullPage", False)}})
        
        elif action == "read":
            calls.append({"tool": "read", "arguments": {"page": self.page_id, "format": params.get("format", "markdown")}})
        
        elif action == "extract":
            calls.append({"tool": "extract_content", "arguments": {"page": self.page_id, "selector": params["selector"]}})
        
        elif action == "evaluate":
            calls.append({"tool": "evaluate_script", "arguments": {"page": self.page_id, "script": params["code"]}})
        
        return calls


class BrowserHarnessAdapter(EngineAdapter):
    """Adapter for browser-harness (YOUR Chrome via CDP 9222)."""
    
    def __init__(self, session_name: str = "ego-default"):
        super().__init__()
        self.session_name = session_name
        self.bu_name = session_name
    
    async def call(self, tool: str, arguments: Dict) -> Dict:
        # browser-harness is a CLI tool, not HTTP
        # We generate the heredoc command
        return {"command": self._build_command(arguments), "session": self.bu_name}
    
    def _build_command(self, arguments: Dict) -> str:
        """Build browser-harness heredoc command."""
        lines = []
        for key, value in arguments.items():
            if key == "code":
                lines.append(value)
            elif key == "url":
                lines.append(f'goto_url("{value}")')
            elif key == "selector":
                lines.append(f'wait_for_load()')
                lines.append(f'js("return document.querySelector(\'{value}\')")')
        return "browser-harness <<<'PY'\n" + "\n".join(lines) + "\nPY"
    
    def translate(self, ego_call: Dict) -> List[Dict]:
        calls = []
        action = list(ego_call.keys())[0]
        params = ego_call[action]
        
        if action == "navigate":
            calls.append({"code": f'goto_url("{params["url"]}")'})
        
        elif action == "snapshot":
            calls.append({"code": 'snap = js("""\n  return {\n    text: document.body.innerText.slice(0, 5000),\n    refs: Array.from(document.querySelectorAll("a, button, input")).map((el, i) => ({\n      ref: "e" + i,\n      text: el.textContent?.trim().slice(0, 100),\n      tag: el.tagName.toLowerCase()\n    }))\n  };\n"""); print(snap)'})
        
        elif action == "click":
            calls.append({"code": f'js("document.querySelector(\'[data-ego-ref=\'{params["ref"]}\']\')?.click()")'})
        
        elif action == "fill":
            calls.append({"code": f'js("document.querySelector(\'[data-ego-ref=\'{params["ref"]}\']\').value = \'{params["value"]}\'; document.querySelector(\'[data-ego-ref=\'{params["ref"]}\']\').dispatchEvent(new Event(\'input\'))")'})
        
        elif action == "wait":
            calls.append({"code": f'wait_for_load()'})
        
        elif action == "capture":
            calls.append({"code": 'capture_screenshot()'})
        
        elif action == "read":
            calls.append({"code": 'js("return document.body.innerText")'})
        
        elif action == "extract":
            calls.append({"code": f'js("return Array.from(document.querySelectorAll(\'{params["selector"]}\')).map(el => el.textContent.trim())")'})
        
        elif action == "evaluate":
            calls.append({"code": params["code"]})
        
        return calls


class GhostSurferAdapter(EngineAdapter):
    """Adapter for ghost-surfer (Playwright with stealth)."""
    
    def __init__(self):
        super().__init__()
        self.page = None
        self.context = None
    
    async def call(self, tool: str, arguments: Dict) -> Dict:
        # Direct Playwright calls
        return {"note": "Direct Playwright - use page.evaluate()"}
    
    def translate(self, ego_call: Dict) -> List[Dict]:
        # For Playwright, we inject the ego API and run directly
        calls = []
        action = list(ego_call.keys())[0]
        params = ego_call[action]
        
        # All translated to single evaluate with ego API
        calls.append({"tool": "evaluate", "arguments": {"code": self._build_ego_code(ego_call)}})
        return calls
    
    def _build_ego_code(self, ego_call: Dict) -> str:
        action = list(ego_call.keys())[0]
        params = ego_call[action]
        
        templates = {
            "navigate": f"await page.goto('{params['url']}', {{waitUntil: 'networkidle'}})",
            "snapshot": "await ego.snapshot()",
            "click": f"await ego.click({{ref: '{params['ref']}'}})",
            "fill": f"await ego.fill({{ref: '{params['ref']}', value: '{params['value']}'}})",
            "wait": f"await ego.wait({{for: '{params.get('for', 'selector')}', value: '{params['value']}'}})",
            "capture": f"await ego.capture({{fullPage: {params.get('fullPage', False)}}})",
            "read": f"await ego.read({{format: '{params.get('format', 'markdown')}'}})",
            "extract": f"await ego.extract({{selector: '{params['selector']}'}})",
            "evaluate": params["code"],
        }
        return templates.get(action, "// Unknown action")


# ============================================================================
# Bridge Factory
# ============================================================================

class EgoBridge:
    """Main bridge: routes ego-browser calls to appropriate engine adapter."""
    
    ADAPTERS = {
        "browserclaw": BrowserClawAdapter,
        "browseros": BrowserOSAdapter,
        "browser-harness": BrowserHarnessAdapter,
        "ghost-surfer": GhostSurferAdapter,
    }
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.adapters: Dict[str, EngineAdapter] = {}
        self._init_adapters()
    
    def _init_adapters(self):
        """Initialize adapters from config."""
        endpoints = self.config.get("endpoints", {})
        
        for engine, adapter_class in self.ADAPTERS.items():
            endpoint = endpoints.get(engine)
            if endpoint:
                self.adapters[engine] = adapter_class(endpoint)
            else:
                self.adapters[engine] = adapter_class()
    
    def get_adapter(self, engine: str) -> Optional[EngineAdapter]:
        """Get adapter for engine."""
        return self.adapters.get(engine)
    
    def translate(self, engine: str, ego_call: Dict) -> List[Dict]:
        """Translate ego call to engine-specific calls."""
        adapter = self.get_adapter(engine)
        if adapter:
            return adapter.translate(ego_call)
        return []
    
    async def execute(self, engine: str, ego_call: Dict) -> Dict:
        """Execute ego call on engine."""
        adapter = self.get_adapter(engine)
        if not adapter:
            return {"error": f"No adapter for engine: {engine}"}
        
        calls = adapter.translate(ego_call)
        results = []
        
        for call in calls:
            if hasattr(adapter, 'call'):
                if asyncio.iscoroutinefunction(adapter.call):
                    result = await adapter.call(call.get("tool", "evaluate"), call.get("arguments", {}))
                else:
                    result = adapter.call(call.get("tool", "evaluate"), call.get("arguments", {}))
                results.append(result)
        
        return {"results": results, "engine": engine}
    
    def generate_ego_js(self, calls: List[Dict]) -> str:
        """Generate JS code that chains ego-browser calls."""
        lines = []
        lines.append("// ego-browser JS execution")
        lines.append("// Injected API: window.ego = {snapshot, click, fill, wait, capture, read, extract, navigate}")
        
        for call in calls:
            action = list(call.keys())[0]
            params = call[action]
            
            if action == "navigate":
                lines.append(f"await ego.navigate({{url: '{params['url']}'}});")
            elif action == "snapshot":
                lines.append("const snap = await ego.snapshot();")
            elif action == "click":
                lines.append(f"await ego.click({{ref: '{params['ref']}'}});")
            elif action == "fill":
                lines.append(f"await ego.fill({{ref: '{params['ref']}', value: '{params['value']}'}});")
            elif action == "wait":
                lines.append(f"await ego.wait({{for: '{params.get('for', 'selector')}', value: '{params['value']}'}});")
            elif action == "capture":
                lines.append(f"const screenshot = await ego.capture({{fullPage: {params.get('fullPage', False)}}});")
            elif action == "read":
                lines.append(f"const content = await ego.read({{format: '{params.get('format', 'markdown')}'}});")
            elif action == "extract":
                lines.append(f"const extracted = await ego.extract({{selector: '{params['selector']}'}});")
            elif action == "evaluate":
                lines.append(params["code"])
        
        return "\n".join(lines)


# ============================================================================
# Convenience Functions
# ============================================================================

def create_bridge(config: Dict = None) -> EgoBridge:
    """Create EgoBridge with default Hermes config."""
    default_config = {
        "endpoints": {
            "browserclaw": "http://localhost:9010",
            "browseros": "http://localhost:9003",
        }
    }
    if config:
        default_config.update(config)
    return EgoBridge(default_config)


def ego_to_browserclaw(ego_call: Dict) -> List[Dict]:
    """Quick: translate ego call to BrowserClaw MCP calls."""
    adapter = BrowserClawAdapter()
    return adapter.translate(ego_call)


def ego_to_browseros(ego_call: Dict) -> List[Dict]:
    """Quick: translate ego call to BrowserOS MCP calls."""
    adapter = BrowserOSAdapter()
    return adapter.translate(ego_call)


def ego_to_harness(ego_call: Dict) -> List[Dict]:
    """Quick: translate ego call to browser-harness commands."""
    adapter = BrowserHarnessAdapter()
    return adapter.translate(ego_call)


if __name__ == "__main__":
    # Demo translations
    test_calls = [
        {"navigate": {"url": "https://example.com"}},
        {"snapshot": {}},
        {"click": {"ref": "e12"}},
        {"fill": {"ref": "e15", "value": "hello world"}},
        {"wait": {"for": "selector", "value": ".loaded"}},
        {"capture": {"fullPage": True}},
        {"read": {"format": "markdown"}},
        {"extract": {"selector": ".item"}},
        {"evaluate": {"code": "return document.title"}},
    ]
    
    bridge = create_bridge()
    
    print("=== ego-browser → BrowserClaw ===")
    for call in test_calls:
        translated = bridge.translate("browserclaw", call)
        print(f"\n{call} →")
        for t in translated:
            print(f"  {json.dumps(t, indent=2)}")
    
    print("\n=== ego-browser → BrowserOS ===")
    for call in test_calls[:3]:
        translated = bridge.translate("browseros", call)
        print(f"\n{call} →")
        for t in translated:
            print(f"  {json.dumps(t, indent=2)}")
    
    print("\n=== ego-browser → browser-harness ===")
    for call in test_calls[:3]:
        translated = bridge.translate("browser-harness", call)
        print(f"\n{call} →")
        for t in translated:
            print(f"  {json.dumps(t, indent=2)}")
    
    print("\n=== Generated JS ===")
    js = bridge.generate_ego_js(test_calls[:5])
    print(js)
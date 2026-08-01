#!/usr/bin/env python3
"""
Space Manager for ego-windows.

Manages browser Spaces as isolated contexts using:
- Playwright browser contexts (for ghost-surfer & spaces)
- BrowserClaw MCP tabs (for standard automation)
- browser-harness CDP sessions (for YOUR Chrome profile)
"""
import os
import json
import asyncio
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import uuid

# Add scripts to path
_SCRIPTS_DIR = Path(__file__).parent.parent.parent / "scripts"
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

try:
    import httpx
except ImportError:
    httpx = None

try:
    from playwright.async_api import async_playwright, Browser, BrowserContext
except ImportError:
    async_playwright = None
    Browser = None
    BrowserContext = None


class SpaceManager:
    """Manages browser Spaces across different engines."""
    
    def __init__(self, ego_windows):
        self.ego = ego_windows
        self.playwright = None
        self.browser = None
        self.contexts: Dict[str, BrowserContext] = {}
        self.browserclaw_tabs: Dict[str, int] = {}
        self.harness_sessions: Dict[str, str] = {}
        
    async def _ensure_playwright(self):
        """Lazy init Playwright."""
        if self.playwright is None and async_playwright:
            self.playwright = await async_playwright().start()
            # Launch persistent browser for contexts
            self.browser = await self.playwright.chromium.launch_persistent_context(
                user_data_dir=self._get_chrome_user_data_dir(),
                headless=False,
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--disable-dev-shm-usage",
                    "--no-sandbox"
                ]
            )
    
    def _get_chrome_user_data_dir(self) -> str:
        """Get Chrome user data directory for profile inheritance."""
        # Windows default Chrome profile
        local_appdata = os.environ.get('LOCALAPPDATA', '')
        if local_appdata:
            chrome_dir = Path(local_appdata) / "Google" / "Chrome" / "User Data"
            if chrome_dir.exists():
                return str(chrome_dir)
        # Fallback
        return str(Path.home() / "ego-windows-chrome-profile")
    
    def create_space(self, name: str, engine: str, 
                     chrome_profile: bool = True, stealth: bool = False) -> Any:
        """Create a new Space with specified engine."""
        # Import shared types
        from .types import Space
        
        space_id = f"space-{uuid.uuid4().hex[:8]}"
        space = Space(
            id=space_id,
            name=name,
            engine=engine,
            metadata={
                "chrome_profile": chrome_profile,
                "stealth": stealth,
                "created_via": "ego_windows"
            }
        )
        
        if engine == "ghost-surfer" or (stealth and async_playwright):
            # Use Playwright context with stealth
            space.context_id = space_id
            # Context created lazily on first use
        elif engine == "browser-harness" or chrome_profile:
            # Use browser-harness CDP session (YOUR Chrome)
            space.cdp_session = self._create_harness_session(space_id)
        elif engine == "browserclaw":
            # Use BrowserClaw MCP tab
            space.tab_id = self._create_browserclaw_tab(space_id)
        elif engine == "browseros":
            # Use BrowserOS MCP page
            space.tab_id = self._create_browseros_page(space_id)
        
        return space
    
    def _create_harness_session(self, space_id: str) -> str:
        """Create a browser-harness session for a Space."""
        # browser-harness uses a daemon that connects to YOUR Chrome on CDP 9222
        # Each Space gets a unique BU_NAME for isolation
        session_name = f"ego-{space_id}"
        self.harness_sessions[space_id] = session_name
        return session_name
    
    def _create_browserclaw_tab(self, space_id: str) -> int:
        """Create a BrowserClaw tab via MCP."""
        if not httpx:
            return None
        try:
            # This would call BrowserClaw MCP
            # For now, return a placeholder - actual call happens in execute_js
            return 0  # placeholder
        except Exception:
            return None
    
    def _create_browseros_page(self, space_id: str) -> int:
        """Create a BrowserOS page via MCP."""
        if not httpx:
            return None
        try:
            # This would call BrowserOS MCP
            return 0  # placeholder
        except Exception:
            return None
    
    async def _get_playwright_context(self, space_id: str) -> Optional[BrowserContext]:
        """Get or create Playwright context for a Space."""
        if space_id in self.contexts:
            return self.contexts[space_id]
        
        await self._ensure_playwright()
        if self.browser:
            # Create new context from persistent browser
            context = await self.browser.new_context(
                viewport={"width": 1280, "height": 720},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            )
            # Anti-detect injections
            await context.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
                window.chrome = {runtime: {}};
            """)
            self.contexts[space_id] = context
            return context
        return None
    
    async def execute_js(self, space, js_code: str, timeout: int = 60) -> Dict:
        """Execute JavaScript in a Space using the appropriate engine."""
        engine = space.engine
        
        if engine == "ghost-surfer" or space.context_id:
            return await self._execute_playwright(space, js_code, timeout)
        elif engine == "browser-harness" or space.cdp_session:
            return await self._execute_harness(space, js_code, timeout)
        elif engine == "browserclaw" or space.tab_id is not None:
            return await self._execute_browserclaw(space, js_code, timeout)
        elif engine == "browseros":
            return await self._execute_browseros(space, js_code, timeout)
        else:
            # Default to Playwright if available
            if async_playwright:
                return await self._execute_playwright(space, js_code, timeout)
            return {"error": "No engine available", "space_id": space.id}
    
    async def _execute_playwright(self, space, js_code: str, timeout: int) -> Dict:
        """Execute JS in Playwright context."""
        try:
            context = await self._get_playwright_context(space.id)
            if not context:
                return {"error": "Playwright not available", "space_id": space.id}
            
            page = context.pages[0] if context.pages else await context.new_page()
            
            # Inject ego-browser API into page
            await self._inject_ego_api(page)
            
            # Execute user JS
            result = await page.evaluate(js_code)
            return {"result": result, "space_id": space.id, "engine": "playwright"}
        except Exception as e:
            return {"error": str(e), "space_id": space.id, "engine": "playwright"}
    
    async def _inject_ego_api(self, page):
        """Inject ego-browser compatible JS API into page."""
        api_code = """
        window.ego = {
            async navigate({url}) {
                await page.goto(url, {waitUntil: 'networkidle'});
                return {ok: true};
            },
            async snapshot() {
                // Return simplified snapshot: text + refs
                const elements = Array.from(document.querySelectorAll('a, button, input, select, textarea, [role="button"], [onclick]'));
                const refs = elements.map((el, i) => ({
                    ref: 'e' + i,
                    text: el.textContent?.trim().slice(0, 100) || '',
                    tag: el.tagName.toLowerCase(),
                    type: el.type || '',
                    href: el.href || '',
                    id: el.id || '',
                    class: el.className || ''
                }));
                return {
                    text: document.body.innerText.slice(0, 5000),
                    refs: refs
                };
            },
            async click({ref}) {
                const el = document.querySelector('[data-ego-ref="' + ref + '"]');
                if (el) el.click();
                return {ok: !!el};
            },
            async fill({ref, value}) {
                const el = document.querySelector('[data-ego-ref="' + ref + '"]');
                if (el && (el.tagName === 'INPUT' || el.tagName === 'TEXTAREA' || el.isContentEditable)) {
                    el.value = value;
                    el.dispatchEvent(new Event('input', {bubbles: true}));
                    return {ok: true};
                }
                return {ok: false};
            },
            async wait({for: type, value}) {
                if (type === 'selector') {
                    await page.waitForSelector(value, {timeout: 10000});
                    return {ok: true};
                }
                return {ok: false};
            },
            async capture({fullPage = false} = {}) {
                return await page.screenshot({fullPage, encoding: 'base64'});
            },
            async read({format = 'markdown'} = {}) {
                if (format === 'markdown') {
                    // Simple markdown extraction
                    return document.body.innerText;
                }
                return document.body.innerHTML;
            },
            async extract({selector}) {
                const els = document.querySelectorAll(selector);
                return Array.from(els).map(el => el.textContent?.trim() || '');
            }
        };
        // Assign refs to elements for click/fill
        const elements = document.querySelectorAll('a, button, input, select, textarea, [role="button"], [onclick]');
        elements.forEach((el, i) => {
            if (!el.hasAttribute('data-ego-ref')) {
                el.setAttribute('data-ego-ref', 'e' + i);
            }
        });
        """
        await page.evaluate(api_code)
    
    async def _execute_harness(self, space, js_code: str, timeout: int) -> Dict:
        """Execute JS via browser-harness (YOUR Chrome via CDP)."""
        # browser-harness uses heredoc format, we'd call the daemon
        # For now, return placeholder - actual implementation calls browser-harness CLI
        session = space.cdp_session or space.metadata.get("harness_session")
        return {
            "result": f"harness session: {session}",
            "note": "Execute via: BU_NAME=ego-{space.id} browser-harness <<<'{js_code}'",
            "space_id": space.id,
            "engine": "browser-harness"
        }
    
    async def _execute_browserclaw(self, space, js_code: str, timeout: int) -> Dict:
        """Execute JS via BrowserClaw MCP."""
        if not httpx:
            return {"error": "httpx not installed", "space_id": space.id}
        
        endpoint = self.ego.engine_endpoints.get("browserclaw", "http://localhost:9010")
        
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                # First, ensure we have a tab
                if space.tab_id is None or space.tab_id == 0:
                    resp = await client.post(f"{endpoint}/mcp/call", json={
                        "tool": "tabs",
                        "arguments": {"action": "new", "url": "about:blank"}
                    })
                    if resp.status_code == 200:
                        data = resp.json()
                        space.tab_id = data.get("page", 1)
                
                # Inject ego API and execute
                page = space.tab_id
                
                # Snapshot first (if not already)
                await client.post(f"{endpoint}/mcp/call", json={
                    "tool": "snapshot",
                    "arguments": {"page": page}
                })
                
                # Execute JS via evaluate
                resp = await client.post(f"{endpoint}/mcp/call", json={
                    "tool": "evaluate",
                    "arguments": {"page": page, "code": js_code}
                })
                
                if resp.status_code == 200:
                    return {"result": resp.json(), "space_id": space.id, "engine": "browserclaw"}
                else:
                    return {"error": resp.text, "space_id": space.id, "engine": "browserclaw"}
        except Exception as e:
            return {"error": str(e), "space_id": space.id, "engine": "browserclaw"}
    
    async def _execute_browseros(self, space, js_code: str, timeout: int) -> Dict:
        """Execute JS via BrowserOS MCP."""
        if not httpx:
            return {"error": "httpx not installed", "space_id": space.id}
        
        endpoint = self.ego.engine_endpoints.get("browseros", "http://localhost:9003")
        
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                # Ensure page exists
                if space.tab_id is None or space.tab_id == 0:
                    resp = await client.post(f"{endpoint}/mcp/call", json={
                        "tool": "new_page",
                        "arguments": {"url": "about:blank"}
                    })
                    if resp.status_code == 200:
                        data = resp.json()
                        space.tab_id = data.get("page", 1)
                
                page = space.tab_id
                
                # Execute JS via evaluate_script
                resp = await client.post(f"{endpoint}/mcp/call", json={
                    "tool": "evaluate_script",
                    "arguments": {"page": page, "script": js_code}
                })
                
                if resp.status_code == 200:
                    return {"result": resp.json(), "space_id": space.id, "engine": "browseros"}
                else:
                    return {"error": resp.text, "space_id": space.id, "engine": "browseros"}
        except Exception as e:
            return {"error": str(e), "space_id": space.id, "engine": "browseros"}
    
    def close_space(self, space) -> bool:
        """Close a Space and cleanup resources."""
        # Close Playwright context
        if space.id in self.contexts:
            try:
                asyncio.create_task(self.contexts[space.id].close())
                del self.contexts[space.id]
            except Exception:
                pass
        
        # Close BrowserClaw tab
        if space.tab_id and space.engine in ("browserclaw", "browseros"):
            # Would call MCP to close tab
            pass
        
        # Cleanup harness session
        if space.id in self.harness_sessions:
            del self.harness_sessions[space.id]
        
        return True
    
    async def close_all(self):
        """Close all spaces."""
        for space_id in list(self.spaces.keys()):
            self.close_space(self.spaces[space_id])
        
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()


# Sync wrapper for non-async usage
class SyncSpaceManager:
    """Synchronous wrapper for SpaceManager."""
    
    def __init__(self, ego_windows):
        self.async_manager = SpaceManager(ego_windows)
        self._loop = None
    
    def _get_loop(self):
        if self._loop is None or self._loop.is_closed():
            self._loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self._loop)
        return self._loop
    
    def create_space(self, name: str, engine: str, 
                     chrome_profile: bool = True, stealth: bool = False):
        return self.async_manager.create_space(name, engine, chrome_profile, stealth)
    
    def execute_js(self, space, js_code: str, timeout: int = 60) -> Dict:
        loop = self._get_loop()
        return loop.run_until_complete(
            self.async_manager.execute_js(space, js_code, timeout)
        )
    
    def close_space(self, space) -> bool:
        return self.async_manager.close_space(space)
    
    def close_all(self):
        loop = self._get_loop()
        loop.run_until_complete(self.async_manager.close_all())
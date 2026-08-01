#!/usr/bin/env python3
"""
Web Automation Engine — Playwright + Ghost-surfer integration + HTTP API mode.
Anti-detect browser automation with proxy support, site configs, and logging.
Supports both browser and HTTP API modes for marketplace scraping.
"""

import asyncio
import json
import logging
import os
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urljoin, quote

try:
    from playwright.async_api import async_playwright, Browser, BrowserContext, Page, Playwright
except ImportError:
    print("Playwright not installed. Run: pip install playwright && playwright install")
    sys.exit(1)

# HTTP client for API-based scraping
try:
    import httpx
    HTTP_AVAILABLE = True
except ImportError:
    HTTP_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("httpx not installed. HTTP mode unavailable. Run: pip install httpx")

# Add project root to path for imports
HERMES_HOME = Path(os.environ.get("HERMES_HOME", "D:/Portable_Soft/hermes"))
sys.path.insert(0, str(HERMES_HOME))

# Import config loader
try:
    from scripts.config_loader import load_site_config, detect_ghost_surfer, launch_ghost_surfer
except ImportError:
    # Fallback if config_loader not available
    def load_site_config(site: str) -> dict:
        config_path = HERMES_HOME / "configs" / f"{site}.json"
        if config_path.exists():
            return json.loads(config_path.read_text(encoding="utf-8"))
        return {}
    
    def detect_ghost_surfer() -> bool:
        return False
    
    async def launch_ghost_surfer(proxy: str = None):
        return None

# Logging setup
LOG_DIR = HERMES_HOME / "logs" / "web_automation"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / f"web_automation_{datetime.now().strftime('%Y%m%d')}.jsonl"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


@dataclass
class ActionLog:
    """Log entry for a single action."""
    timestamp: str
    action: str
    selector: str = ""
    params: Dict = field(default_factory=dict)
    success: bool = True
    duration_ms: int = 0
    error: str = ""
    site: str = ""

    def to_json(self) -> str:
        return json.dumps(self.__dict__, ensure_ascii=False)


@dataclass
class BrowserConfig:
    """Browser configuration."""
    proxy: Optional[str] = "socks5://127.0.0.1:10806"  # v2rayN default
    headless: bool = False
    ghost_surfer: bool = True  # Try Ghost-surfer first
    stealth: bool = True  # Playwright stealth mode
    headless_fallback: bool = True
    user_agent: Optional[str] = None
    viewport: Dict = field(default_factory=lambda: {"width": 1920, "height": 1080})
    locale: str = "en-US"
    timezone: str = "Europe/Moscow"
    timeout: int = 30000  # ms
    slow_mo: int = 50  # ms between actions


class BrowserAutomation:
    """Main browser automation engine with Ghost-surfer + Playwright fallback + HTTP API."""
    
    def __init__(self, config: BrowserConfig = None, site: str = ""):
        self.config = config or BrowserConfig()
        self.site = site
        self.site_config = load_site_config(site) if site else {}
        self.playwright: Optional[Playwright] = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.ghost_surfer_process = None
        self._http_client: Optional[httpx.AsyncClient] = None
        self._log_entries: List[ActionLog] = []
        self._start_time = time.time()
        
    async def __aenter__(self):
        await self.start()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
    
    def _log_action(self, action: str, selector: str = "", params: Dict = None, 
                    success: bool = True, duration_ms: int = 0, error: str = "") -> None:
        """Log an action to internal buffer and JSONL file."""
        log_entry = ActionLog(
            timestamp=datetime.now().isoformat(),
            action=action,
            selector=selector,
            params=params or {},
            success=success,
            duration_ms=duration_ms,
            error=error,
            site=self.site
        )
        self._log_entries.append(log_entry)
        
        # Write to JSONL file
        try:
            with open(LOG_FILE, "a", encoding="utf-8") as f:
                f.write(log_entry.to_json() + "\n")
        except Exception as e:
            logger.warning(f"Failed to write log: {e}")
        
        # Also log to standard logger
        status = "✅" if success else "❌"
        logger.info(f"{status} {self.site} | {action} | {selector} | {duration_ms}ms | {error}")

    async def start(self) -> bool:
        """Initialize browser (Ghost-surfer -> Playwright stealth -> basic)."""
        start_time = time.time()
        
        # Try Ghost-surfer first
        if self.config.ghost_surfer and detect_ghost_surfer():
            logger.info("Attempting Ghost-surfer launch...")
            self.ghost_surfer_process = await launch_ghost_surfer(self.config.proxy)
            if self.ghost_surfer_process:
                logger.info("Ghost-surfer launched successfully")
                return True
        
        # Fallback: Playwright stealth
        logger.info("Launching Playwright (stealth mode)...")
        try:
            self.playwright = await async_playwright().start()
            
            # Browser launch args for stealth
            launch_args = [
                "--disable-blink-features=AutomationControlled",
                "--disable-dev-shm-usage",
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-web-security",
                "--disable-features=IsolateOrigins,site-per-process",
                "--disable-site-isolation-trials",
            ]
            
            # Try to use system browser (Edge/Chrome) if available
            executable_path = None
            channel = None
            system_browsers = [
                ("msedge", "D:\\Program Files (x86)\\Microsoft\\Edge Dev\\Application\\msedge.exe"),
                ("msedge", "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe"),
                ("chrome", "D:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"),
                ("chrome", "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"),
                ("chrome", "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe"),
            ]
            import os
            for ch, path in system_browsers:
                if os.path.exists(path):
                    executable_path = path
                    channel = ch
                    logger.info(f"Using system browser: {path}")
                    break
            
            if self.config.proxy:
                launch_args.append(f"--proxy-server={self.config.proxy}")
            
            if executable_path:
                self.browser = await self.playwright.chromium.launch(
                    headless=self.config.headless,
                    executable_path=executable_path,
                    channel=channel,
                    args=launch_args,
                    slow_mo=self.config.slow_mo,
                )
            else:
                self.browser = await self.playwright.chromium.launch(
                    headless=self.config.headless,
                    args=launch_args,
                    slow_mo=self.config.slow_mo,
                )
            
            # Create context with stealth settings
            self.context = await self.browser.new_context(
                viewport=self.config.viewport,
                locale=self.config.locale,
                timezone_id=self.config.timezone,
                user_agent=self.config.user_agent or self._random_user_agent(),
                bypass_csp=True,
                ignore_https_errors=True,
                java_script_enabled=True,
            )
            
            # Apply stealth scripts
            if self.config.stealth:
                await self._apply_stealth_scripts()
            
            self.page = await self.context.new_page()
            self.page.set_default_timeout(self.config.timeout)
            
            logger.info("Playwright browser launched successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to launch browser: {e}")
            return False
    
    def _random_user_agent(self) -> str:
        """Return a random realistic user agent."""
        agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
        ]
        import random
        return random.choice(agents)
    
    async def _apply_stealth_scripts(self):
        """Apply anti-detection scripts to context."""
        stealth_script = """
        // Overwrite navigator properties
        Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
        Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
        Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
        
        // Canvas fingerprint noise
        const originalToDataURL = HTMLCanvasElement.prototype.toDataURL;
        HTMLCanvasElement.prototype.toDataURL = function(type) {
            const ctx = this.getContext('2d');
            if (ctx) {
                const noise = new Uint8ClampedArray(this.width * this.height * 4);
                for (let i = 0; i < noise.length; i += 4) {
                    noise[i] = noise[i] + Math.floor(Math.random() * 2);
                    noise[i+1] = noise[i+1] + Math.floor(Math.random() * 2);
                    noise[i+2] = noise[i+2] + Math.floor(Math.random() * 2);
                }
                ctx.putImageData(new ImageData(noise, this.width, this.height), 0, 0);
            }
            return originalToDataURL.apply(this, arguments);
        };
        
        // WebGL fingerprint
        const getParameter = WebGLRenderingContext.prototype.getParameter;
        WebGLRenderingContext.prototype.getParameter = function(param) {
            if (param === 37445) return 'Intel Inc.';
            if (param === 37446) return 'Intel Iris OpenGL Engine';
            return getParameter.apply(this, arguments);
        };
        """
        await self.context.add_init_script(stealth_script)

    # ==================== HTTP API Methods ====================

    def _get_http_client(self) -> "httpx.AsyncClient":
        """Get or create HTTP client with proxy."""
        if not HTTP_AVAILABLE:
            raise RuntimeError("httpx not installed. Run: pip install httpx")
        if self._http_client is None:
            self._http_client = httpx.AsyncClient(
                proxy=self.config.proxy,
                timeout=30.0,
                verify=False,  # Disable SSL verification for proxy
                headers={
                    "User-Agent": self.config.user_agent or self._random_user_agent(),
                    "Accept": "application/json, text/plain, */*",
                    "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
                    "Origin": self.site_config.get("base_url", ""),
                }
            )
        return self._http_client

    async def _http_request(self, method: str, url: str, params: Dict = None, 
                           headers: Dict = None, json_data: Dict = None) -> Optional[Dict]:
        """Make HTTP request through proxy."""
        start = time.time()
        client = self._get_http_client()
        try:
            response = await client.request(
                method=method.upper(),
                url=url,
                params=params,
                headers=headers,
                json=json_data,
                follow_redirects=True
            )
            response.raise_for_status()
            duration = int((time.time() - start) * 1000)
            self._log_action(f"http_{method.lower()}", selector=url, 
                           params=params or {}, duration_ms=duration)
            return response.json()
        except Exception as e:
            duration = int((time.time() - start) * 1000)
            self._log_action(f"http_{method.lower()}", selector=url, 
                           params=params or {}, success=False, 
                           duration_ms=duration, error=str(e))
            return None

    async def _ozon_search_http(self, query: str, limit: int = 20, 
                                min_price: int = 0, max_price: int = 1000000,
                                page: int = 1) -> List[Dict]:
        """Search Ozon via mobile API."""
        # Ozon mobile API endpoint
        url = "https://api.ozon.ru/composer-api.bx/page/json/v2"
        params = {
            "url": f"/search/?text={quote(query)}&sorting=price",
            "layout_container": "searchResultsV2",
            "layout_page_index": page,
        }
        
        data = await self._http_request("GET", url, params=params)
        if not data:
            return []
        
        products = []
        try:
            # Parse Ozon response structure
            for widget in data.get("widgetStates", {}).values():
                try:
                    widget_data = json.loads(widget) if isinstance(widget, str) else widget
                    if isinstance(widget_data, dict) and "data" in widget_data:
                        items = widget_data.get("data", {}).get("items", [])
                        for item in items:
                            cell_tracking = item.get("cellTrackingInfo", {})
                            title = cell_tracking.get("title", "")
                            price = cell_tracking.get("price", 0)
                            link = "https://www.ozon.ru" + cell_tracking.get("link", "")
                            rating = cell_tracking.get("rating", 0)
                            reviews = cell_tracking.get("reviewsCount", 0)
                            if title:
                                products.append({
                                    "title": title,
                                    "price": price,
                                    "link": link,
                                    "rating": rating,
                                    "reviewsCount": reviews,
                                })
                except Exception:
                    continue
        except Exception as e:
            logger.warning(f"Failed to parse Ozon response: {e}")
        
        return products[:limit]

    async def _wb_search_http(self, query: str, limit: int = 20,
                              min_price: int = 0, max_price: int = 1000000,
                              page: int = 1) -> List[Dict]:
        """Search Wildberries via mobile API."""
        # WB search API
        url = "https://search.wb.ru/exactmatch/ru/common/v4/search"
        params = {
            "query": query,
            "sort": "priceup",
            "page": page,
            "limit": min(100, limit),
            "curr": "rub",
            "dest": "-1257786",
            "regions": "80,38,83,4,64,33,68,70,69,30,86,75,40,1,66,48,22,71,11",
        }
        
        data = await self._http_request("GET", url, params=params)
        if not data:
            return []
        
        products = []
        try:
            for product in data.get("data", {}).get("products", []):
                title = product.get("name", "")
                price = product.get("salePriceU", 0) // 100  # Convert from kopeks
                old_price = product.get("priceU", 0) // 100
                rating = product.get("reviewRating", 0)
                reviews = product.get("feedbacks", 0)
                link = f"https://www.wildberries.ru/catalog/{product.get('id')}/detail.aspx"
                if title:
                    products.append({
                        "title": title,
                        "price": price,
                        "oldPrice": old_price if old_price > price else None,
                        "rating": rating,
                        "reviewsCount": reviews,
                        "link": link,
                    })
        except Exception as e:
            logger.warning(f"Failed to parse WB response: {e}")
        
        return products[:limit]

    async def search_and_extract_http(self, query: str, site: str = "ozon",
                                      limit: int = 20, sort: str = "price",
                                      min_price: int = 0, max_price: int = 1000000,
                                      pages: int = 3) -> List[Dict]:
        """
        Search products via HTTP API (no browser needed).
        Falls back to browser if HTTP fails.
        """
        if site not in ["ozon", "wb"]:
            self._log_action("search_and_extract_http", success=False, 
                           error=f"Unsupported site: {site}")
            return []
        
        self.site = site
        self.site_config = load_site_config(site)
        
        all_products = []
        
        for page in range(1, pages + 1):
            if site == "ozon":
                products = await self._ozon_search_http(query, limit, min_price, max_price, page)
            elif site == "wb":
                products = await self._wb_search_http(query, limit, min_price, max_price, page)
            else:
                products = []
            
            if not products:
                logger.warning(f"No products found on page {page} for {site}")
                break
            
            all_products.extend(products)
            
            if len(all_products) >= limit:
                all_products = all_products[:limit]
                break
            
            await asyncio.sleep(0.5)  # Rate limiting
        
        all_products = all_products[:limit]
        
        # Log to feedback store
        self._log_action("search_and_extract_http", params={
            "query": query, "site": site, "found": len(all_products), "limit": limit
        })
        
        # Send to Knowledge Cube
        await self._send_to_knowledge_cube(query, site, all_products)
        
        return all_products[:limit]

    async def close(self):
        """Close browser and cleanup."""
        try:
            if self._http_client:
                await self._http_client.aclose()
                self._http_client = None
            if self.page:
                await self.page.close()
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()
            if self.ghost_surfer_process:
                self.ghost_surfer_process.terminate()
            logger.info("Browser closed")
        except Exception as e:
            logger.error(f"Error closing browser: {e}")

    # ==================== Core Actions ====================
    
    async def goto(self, url: str, wait_until: str = "networkidle") -> bool:
        """Navigate to URL."""
        start = time.time()
        try:
            full_url = urljoin(self.site_config.get("base_url", ""), url) if not url.startswith("http") else url
            await self.page.goto(full_url, wait_until=wait_until)
            self._log_action("goto", selector=url, duration_ms=int((time.time() - start) * 1000))
            return True
        except Exception as e:
            self._log_action("goto", selector=url, success=False, duration_ms=int((time.time() - start) * 1000), error=str(e))
            return False
    
    async def click(self, selector: str, timeout: int = None) -> bool:
        """Click element."""
        start = time.time()
        try:
            await self.page.wait_for_selector(selector, timeout=timeout or self.config.timeout)
            await self.page.click(selector)
            self._log_action("click", selector=selector, duration_ms=int((time.time() - start) * 1000))
            return True
        except Exception as e:
            self._log_action("click", selector=selector, success=False, duration_ms=int((time.time() - start) * 1000), error=str(e))
            return False
    
    async def fill(self, selector: str, value: str, timeout: int = None) -> bool:
        """Fill input field."""
        start = time.time()
        try:
            await self.page.wait_for_selector(selector, timeout=timeout or self.config.timeout)
            await self.page.fill(selector, value)
            self._log_action("fill", selector=selector, params={"value": value}, duration_ms=int((time.time() - start) * 1000))
            return True
        except Exception as e:
            self._log_action("fill", selector=selector, params={"value": value}, success=False, duration_ms=int((time.time() - start) * 1000), error=str(e))
            return False
    
    async def type(self, selector: str, text: str, delay: int = 50) -> bool:
        """Type text with human-like delay."""
        start = time.time()
        try:
            await self.page.wait_for_selector(selector, timeout=self.config.timeout)
            await self.page.type(selector, text, delay=delay)
            self._log_action("type", selector=selector, params={"text": text[:50]}, duration_ms=int((time.time() - start) * 1000))
            return True
        except Exception as e:
            self._log_action("type", selector=selector, success=False, duration_ms=int((time.time() - start) * 1000), error=str(e))
            return False
    
    async def select(self, selector: str, value: str) -> bool:
        """Select dropdown option."""
        start = time.time()
        try:
            await self.page.wait_for_selector(selector, timeout=self.config.timeout)
            await self.page.select_option(selector, value=value)
            self._log_action("select", selector=selector, params={"value": value}, duration_ms=int((time.time() - start) * 1000))
            return True
        except Exception as e:
            self._log_action("select", selector=selector, params={"value": value}, success=False, error=str(e))
            return False
    
    async def wait(self, selector: str, timeout: int = None, state: str = "visible") -> bool:
        """Wait for element."""
        start = time.time()
        try:
            await self.page.wait_for_selector(selector, timeout=timeout or self.config.timeout, state=state)
            self._log_action("wait", selector=selector, params={"state": state}, duration_ms=int((time.time() - start) * 1000))
            return True
        except Exception as e:
            self._log_action("wait", selector=selector, success=False, error=str(e))
            return False
    
    async def screenshot(self, path: str, full_page: bool = True) -> bool:
        """Take screenshot."""
        start = time.time()
        try:
            await self.page.screenshot(path=path, full_page=full_page)
            self._log_action("screenshot", params={"path": path}, duration_ms=int((time.time() - start) * 1000))
            return True
        except Exception as e:
            self._log_action("screenshot", success=False, error=str(e))
            return False
    
    async def scroll(self, direction: str = "down", amount: int = 500) -> bool:
        """Scroll page."""
        start = time.time()
        try:
            if direction == "down":
                await self.page.evaluate(f"window.scrollBy(0, {amount})")
            elif direction == "up":
                await self.page.evaluate(f"window.scrollBy(0, -{amount})")
            elif direction == "top":
                await self.page.evaluate("window.scrollTo(0, 0)")
            elif direction == "bottom":
                await self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            self._log_action("scroll", params={"direction": direction, "amount": amount}, duration_ms=int((time.time() - start) * 1000))
            return True
        except Exception as e:
            self._log_action("scroll", success=False, error=str(e))
            return False
    
    async def evaluate(self, js_code: str) -> Any:
        """Execute JavaScript in page context."""
        start = time.time()
        try:
            result = await self.page.evaluate(js_code)
            self._log_action("evaluate", params={"code": js_code[:100]}, duration_ms=int((time.time() - start) * 1000))
            return result
        except Exception as e:
            self._log_action("evaluate", success=False, error=str(e))
            return None
    
    async def get_cookies(self) -> List[Dict]:
        """Get cookies."""
        return await self.context.cookies()
    
    async def set_cookies(self, cookies: List[Dict]) -> bool:
        """Set cookies."""
        try:
            await self.context.add_cookies(cookies)
            return True
        except Exception as e:
            logger.error(f"Failed to set cookies: {e}")
            return False
    
    async def save_storage_state(self, path: str) -> bool:
        """Save auth state (cookies + localStorage)."""
        try:
            await self.context.storage_state(path=path)
            return True
        except Exception as e:
            logger.error(f"Failed to save storage state: {e}")
            return False
    
    async def load_storage_state(self, path: str) -> bool:
        """Load auth state."""
        try:
            state_text = Path(path).read_text()
            await self.context.add_init_script(f"""
                const state = {json.dumps(state_text)};
                Object.entries(state.origins || []).forEach(([origin, items]) => {{
                    items.forEach(item => localStorage.setItem(item.name, item.value));
                }});
            """)
            return True
        except Exception as e:
            logger.error(f"Failed to load storage state: {e}")
            return False
    
    # ==================== Site-Specific Actions ====================
    
    async def execute_site_action(self, action_name: str, params: Dict = None) -> bool:
        """Execute a site-specific action from config."""
        if not self.site_config:
            self._log_action("execute_site_action", success=False, error="No site config loaded")
            return False
        
        steps = self.site_config.get("steps", {}).get(action_name, [])
        if not steps:
            self._log_action("execute_site_action", params={"action": action_name}, success=False, error=f"Action not found: {action_name}")
            return False
        
        for i, step in enumerate(steps):
            action = step.get("action")
            selector = step.get("selector", "")
            param_key = step.get("param", "")
            value = params.get(param_key, step.get("value", "")) if params else step.get("value", "")
            
            success = False
            if action == "goto":
                success = await self.goto(value)
            elif action == "click":
                success = await self.click(selector)
            elif action == "fill":
                success = await self.fill(selector, value)
            elif action == "type":
                success = await self.type(selector, value)
            elif action == "select":
                success = await self.select(selector, value)
            elif action == "wait":
                success = await self.wait(selector)
            elif action == "scroll":
                success = await self.scroll(step.get("direction", "down"), step.get("amount", 500))
            elif action == "wait_for_navigation":
                await self.page.wait_for_load_state("networkidle")
                success = True
            else:
                self._log_action("execute_step", params={"action": action}, success=False, error=f"Unknown action: {action}")
                return False
            
            if not success:
                self._log_action("execute_site_action", params={"action": action_name, "step": i}, success=False, error=f"Step {i} failed")
                return False
        
        self._log_action("execute_site_action", params={"action": action_name}, duration_ms=0)
        return True
    
    # ==================== Marketplace Methods ====================
    
    async def search_and_extract(self, query: str, site: str = "ozon", 
                                 limit: int = 20, sort: str = "price",
                                 min_price: int = 0, max_price: int = 1000000,
                                 pages: int = 3) -> List[Dict]:
        """
        Search products and extract structured data.
        Tries HTTP API first, falls back to browser with human-like behavior.
        """
        # Try HTTP mode first (no browser needed)
        try:
            http_results = await self.search_and_extract_http(query, site, limit, sort, min_price, max_price, pages)
            if http_results and len(http_results) > 0:
                return http_results
            logger.warning(f"HTTP mode returned no results, falling back to browser")
        except Exception as e:
            logger.warning(f"HTTP mode failed, falling back to browser: {e}")
        
        # Fallback to browser mode with human-like behavior
        if site not in ["ozon", "wb"]:
            self._log_action("search_and_extract", success=False, error=f"Unsupported site: {site}")
            return []
        
        self.site = site
        self.site_config = load_site_config(site)
        
        # Human-like search: go to main page, type query, submit
        await self._human_like_search(query, site)
        
        # Apply price filter if specified
        if min_price > 0 or max_price < 1000000:
            await self.execute_site_action("filter_by_price", {"min_price": str(min_price), "max_price": str(max_price)})
        
        # Apply sort
        if sort == "price":
            await self.execute_site_action("sort_by_price_asc")
        
        all_products = []
        
        for page in range(1, pages + 1):
            # Wait for products
            await self.wait(self.site_config.get("selectors", {}).get("product_cards", ""))
            
            # Extract products
            products = await self.execute_site_action("extract_product_list")
            if not products:
                logger.warning(f"No products found on page {page}")
                break
            
            all_products.extend(products)
            
            if len(all_products) >= limit:
                all_products = all_products[:limit]
                break
            
            # Human-like scroll
            await self._human_like_scroll()
            await asyncio.sleep(1)
        
        # Limit results
        all_products = all_products[:limit]
        
        # Log to feedback store
        self._log_action("search_and_extract", params={
            "query": query, "site": site, "found": len(all_products), "limit": limit
        })
        
        # Send to Knowledge Cube
        await self._send_to_knowledge_cube(query, site, all_products)
        
        return all_products[:limit]
    
    async def _human_like_search(self, query: str, site: str):
        """Perform search like a human: go to homepage, type query, submit."""
        base_url = self.site_config.get("base_url", "")
        if not base_url:
            base_url = "https://www.ozon.ru" if site == "ozon" else "https://www.wildberries.ru"
        
        # Go to homepage
        await self.goto(base_url)
        await asyncio.sleep(2)  # Wait for page to fully load
        
        # Find search input
        search_selectors = {
            "ozon": 'input[name="text"], input[placeholder*="Поиск"], input[placeholder*="Search"]',
            "wb": 'input[id="searchInput"], input[name="search"], input[placeholder*="Поиск"]'
        }
        
        selector = search_selectors.get(site, 'input[type="search"], input[name="q"], input[placeholder*="Поиск"]')
        
        # Wait for search input
        await self.wait(selector)
        await asyncio.sleep(1)
        
        # Click to focus
        await self.click(selector)
        await asyncio.sleep(0.5)
        
        # Type query character by character like a human
        await self.type(selector, query, delay=80)  # 80ms per char = human speed
        await asyncio.sleep(1)
        
        # Press Enter to submit
        await self.page.keyboard.press("Enter")
        await asyncio.sleep(3)  # Wait for results to load
    
    async def _human_like_scroll(self):
        """Scroll page like a human: random amounts, pauses."""
        import random
        for _ in range(random.randint(2, 4)):
            amount = random.randint(300, 800)
            await self.scroll("down", amount)
            await asyncio.sleep(random.uniform(0.5, 1.5))
    
    async def get_product_details(self, url: str) -> Dict:
        """Get detailed product information from product page."""
        await self.goto(url)
        await self.wait(self.site_config.get("selectors", {}).get("product_page_title", ""))
        
        details = await self.execute_site_action("get_product_details")
        
        # Add URL to details
        if details:
            details["url"] = url
        
        self._log_action("get_product_details", params={"url": url}, success=bool(details))
        return details or {}
    
    async def get_reviews(self, url: str = None, limit: int = 5) -> List[Dict]:
        """Get reviews for a product."""
        if url:
            await self.goto(url)
        
        await self.execute_site_action("get_reviews")
        
        # The reviews are extracted via evaluate script
        # We'll get them from the last log entry
        logs = self.get_logs()
        for log in reversed(logs):
            if log.action == "execute_site_action" and "extractReviews" in str(log.params):
                break
        
        # For now, return empty - the reviews are in the evaluation script result
        return []
    
    async def _send_to_knowledge_cube(self, query: str, site: str, products: List[Dict]):
        """Send extracted products to Knowledge Cube."""
        try:
            from scripts.event_evolution import on_task_complete
            for product in products:
                on_task_complete(
                    content=f"Marketplace product: {product.get('title', '')} on {site}. Price: {product.get('price', 0)} RUB. Rating: {product.get('rating', 0)}. Reviews: {product.get('reviewsCount', 0)}. Link: {product.get('link', '')}",
                    tags=["marketplace", site, "product", "price_tracking"],
                    source="web_automation"
                )
        except Exception as e:
            logger.warning(f"Failed to send to Knowledge Cube: {e}")
    
    def get_logs(self) -> List[ActionLog]:
        """Get all logged actions."""
        return self._log_entries
    
    def save_logs(self, path: str = None) -> bool:
        """Save logs to file."""
        path = path or LOG_DIR / f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        try:
            data = [log.__dict__ for log in self._log_entries]
            Path(path).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
            return True
        except Exception as e:
            logger.error(f"Failed to save logs: {e}")
            return False


async def main():
    """CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Web Automation Engine")
    parser.add_argument("--site", help="Site config name (ozon, wb, github, gitlab, youtube, dzen, vc_ru)")
    parser.add_argument("--action", help="Action name from site config")
    parser.add_argument("--params", help="JSON params for action")
    parser.add_argument("--test-browser", action="store_true", help="Test browser launch")
    parser.add_argument("--test-http", action="store_true", help="Test HTTP API mode")
    parser.add_argument("--query", help="Search query for HTTP mode")
    parser.add_argument("--headless", action="store_true", help="Run headless")
    parser.add_argument("--no-proxy", action="store_true", help="Disable proxy")
    parser.add_argument("--no-ghost", action="store_true", help="Disable Ghost-surfer")
    
    args = parser.parse_args()
    
    config = BrowserConfig(
        headless=args.headless,
        proxy=None if args.no_proxy else "socks5://127.0.0.1:10806",
        ghost_surfer=not args.no_ghost,
    )
    
    async with BrowserAutomation(config=config, site=args.site) as bot:
        if args.test_browser:
            success = await bot.goto("https://github.com")
            logger.info(f"Browser test: {'OK' if success else 'FAILED'}")
            return
        
        if args.test_http and args.query:
            results = await bot.search_and_extract_http(args.query, args.site or "ozon", limit=10)
            logger.info(f"HTTP search found {len(results)} products")
            for i, p in enumerate(results[:5]):
                logger.info(f"  {i+1}. {p.get('title', 'N/A')[:60]} - {p.get('price', 'N/A')} RUB")
            return
        
        if args.site and args.action:
            params = json.loads(args.params) if args.params else {}
            success = await bot.execute_site_action(args.action, params)
            logger.info(f"Action {'completed' if success else 'failed'}")
        else:
            parser.print_help()


if __name__ == "__main__":
    asyncio.run(main())
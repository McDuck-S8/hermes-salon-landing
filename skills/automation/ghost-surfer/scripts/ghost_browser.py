#!/usr/bin/env python3
"""
Ghost Browser — Anti-detect browser core for ghost-surfer.
Playwright + playwright-stealth with fingerprint spoofing.
"""

import asyncio
import json
import random
import sqlite3
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List
from cryptography.fernet import Fernet

# Playwright imports
try:
    from playwright.async_api import async_playwright, Browser, BrowserContext, Page
    from playwright_stealth import stealth_async
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    print("WARNING: Playwright not installed. Run: pip install playwright playwright-stealth && playwright install chromium")


# =============================================================================
# DATA MODELS
# =============================================================================

@dataclass
class FingerprintProfile:
    """Realistic browser fingerprint profile."""
    user_agent: str
    viewport: Dict[str, int]  # width, height
    screen: Dict[str, int]    # width, height, color_depth
    timezone: str
    locale: str
    languages: List[str]
    platform: str
    webgl_vendor: str
    webgl_renderer: str
    canvas_noise: float
    audio_noise: float
    fonts: List[str]
    device_memory: int
    hardware_concurrency: int
    touch_support: bool
    # Derived
    hash: str = field(init=False)
    
    def __post_init__(self):
        import hashlib
        fp_str = f"{self.user_agent}|{self.viewport}|{self.screen}|{self.timezone}|{self.webgl_vendor}|{self.webgl_renderer}"
        self.hash = hashlib.sha256(fp_str.encode()).hexdigest()[:16]


@dataclass
class ProxyConfig:
    """Proxy configuration."""
    host: str
    port: int
    username: Optional[str] = None
    password: Optional[str] = None
    protocol: str = "socks5"  # socks5, http, https
    geo: str = "unknown"
    health_score: float = 1.0
    last_checked: Optional[str] = None
    
    @property
    def url(self) -> str:
        auth = f"{self.username}:{self.password}@" if self.username else ""
        return f"{self.protocol}://{auth}{self.host}:{self.port}"


@dataclass
class BrowserProfile:
    """Persistent browser profile data."""
    context_id: str
    cookies: List[Dict[str, Any]] = field(default_factory=list)
    local_storage: Dict[str, str] = field(default_factory=dict)
    session_storage: Dict[str, str] = field(default_factory=dict)
    permissions: Dict[str, str] = field(default_factory=dict)


@dataclass
class GhostIdentity:
    """Complete ghost identity."""
    id: str
    fingerprint: FingerprintProfile
    proxy: ProxyConfig
    browser_profile: BrowserProfile
    credentials: Dict[str, Dict[str, str]] = field(default_factory=dict)  # platform -> {email, pass, 2fa}
    email_config: Optional[Dict[str, Any]] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    last_used: str = field(default_factory=lambda: datetime.now().isoformat())
    reputation_score: float = 1.0
    tags: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        # Convert nested dataclasses
        d['fingerprint'] = asdict(self.fingerprint)
        d['proxy'] = asdict(self.proxy)
        d['browser_profile'] = asdict(self.browser_profile)
        return d


# =============================================================================
# FINGERPRINT GENERATOR
# =============================================================================

class FingerprintGenerator:
    """Generates realistic browser fingerprints."""
    
    # Real User-Agent strings (updated periodically)
    USER_AGENTS = {
        "windows_chrome": [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        ],
        "windows_firefox": [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:127.0) Gecko/20100101 Firefox/127.0",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:126.0) Gecko/20100101 Firefox/126.0",
        ],
        "mac_chrome": [
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        ],
        "mac_safari": [
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15",
        ],
        "linux_chrome": [
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
        ],
    }
    
    VIEWPORTS = [
        {"width": 1920, "height": 1080},
        {"width": 1366, "height": 768},
        {"width": 1440, "height": 900},
        {"width": 1536, "height": 864},
        {"width": 1280, "height": 720},
        {"width": 1600, "height": 900},
    ]
    
    SCREENS = [
        {"width": 1920, "height": 1080, "color_depth": 24},
        {"width": 2560, "height": 1440, "color_depth": 24},
        {"width": 1366, "height": 768, "color_depth": 24},
        {"width": 1440, "height": 900, "color_depth": 24},
    ]
    
    TIMEZONES = [
        "Europe/Moscow", "Europe/London", "America/New_York", "America/Los_Angeles",
        "Asia/Tokyo", "Asia/Shanghai", "Europe/Berlin", "Europe/Paris",
        "America/Chicago", "America/Denver", "Asia/Dubai", "Asia/Singapore",
    ]
    
    LOCALES = ["en-US", "ru-RU", "en-GB", "de-DE", "fr-FR", "es-ES", "pt-BR", "ja-JP", "zh-CN"]
    
    WEBGL_VENDORS = [
        "Google Inc. (NVIDIA)", "Google Inc. (AMD)", "Google Inc. (Intel)",
        "Mozilla (NVIDIA)", "Mozilla (AMD)", "Mozilla (Intel)",
    ]
    
    WEBGL_RENDERERS = [
        "ANGLE (NVIDIA, NVIDIA GeForce GTX 1660 Ti Direct3D11 vs_5_0 ps_5_0)",
        "ANGLE (AMD, AMD Radeon RX 580 Direct3D11 vs_5_0 ps_5_0)",
        "ANGLE (Intel, Intel(R) UHD Graphics 630 Direct3D11 vs_5_0 ps_5_0)",
        "ANGLE (NVIDIA, NVIDIA GeForce RTX 3060 Direct3D11 vs_5_0 ps_5_0)",
    ]
    
    FONT_LISTS = [
        ["Arial", "Arial Black", "Calibri", "Cambria", "Comic Sans MS", "Consolas", "Courier New", "Georgia", "Impact", "Segoe UI", "Tahoma", "Times New Roman", "Trebuchet MS", "Verdana"],
        ["Arial", "Arial Black", "Calibri", "Cambria", "Comic Sans MS", "Consolas", "Courier New", "Georgia", "Helvetica", "Impact", "Segoe UI", "Tahoma", "Times New Roman", "Trebuchet MS", "Verdana"],
        ["-apple-system", "BlinkMacSystemFont", "Segoe UI", "Roboto", "Helvetica Neue", "Arial", "sans-serif"],
    ]
    
    def __init__(self, seed: Optional[int] = None):
        self.rng = random.Random(seed)
    
    def generate(self, platform_hint: str = "auto") -> FingerprintProfile:
        """Generate a complete fingerprint profile."""
        
        # Choose platform
        if platform_hint == "auto":
            platform = self.rng.choice(["windows", "mac", "linux"])
        else:
            platform = platform_hint
        
        # Select UA family
        if platform == "windows":
            ua_family = self.rng.choice(["windows_chrome", "windows_firefox"])
            platform_str = "Win32"
        elif platform == "mac":
            ua_family = self.rng.choice(["mac_chrome", "mac_safari"])
            platform_str = "MacIntel"
        else:
            ua_family = "linux_chrome"
            platform_str = "Linux x86_64"
        
        user_agent = self.rng.choice(self.USER_AGENTS[ua_family])
        viewport = self.rng.choice(self.VIEWPORTS)
        screen = self.rng.choice(self.SCREENS)
        
        # Ensure viewport <= screen
        if viewport["width"] > screen["width"]:
            viewport["width"] = screen["width"]
        if viewport["height"] > screen["height"]:
            viewport["height"] = screen["height"]
        
        timezone = self.rng.choice(self.TIMEZONES)
        locale = self.rng.choice(self.LOCALES)
        
        # Languages based on locale
        lang_map = {
            "en-US": ["en-US", "en"],
            "ru-RU": ["ru-RU", "ru", "en-US", "en"],
            "en-GB": ["en-GB", "en"],
            "de-DE": ["de-DE", "de", "en-US", "en"],
            "fr-FR": ["fr-FR", "fr", "en-US", "en"],
            "es-ES": ["es-ES", "es", "en-US", "en"],
            "pt-BR": ["pt-BR", "pt", "en-US", "en"],
            "ja-JP": ["ja-JP", "ja", "en-US", "en"],
            "zh-CN": ["zh-CN", "zh", "en-US", "en"],
        }
        languages = lang_map.get(locale, [locale, "en-US", "en"])
        
        return FingerprintProfile(
            user_agent=user_agent,
            viewport=viewport,
            screen=screen,
            timezone=timezone,
            locale=locale,
            languages=languages,
            platform=platform_str,
            webgl_vendor=self.rng.choice(self.WEBGL_VENDORS),
            webgl_renderer=self.rng.choice(self.WEBGL_RENDERERS),
            canvas_noise=self.rng.uniform(0.0001, 0.001),
            audio_noise=self.rng.uniform(0.0001, 0.001),
            fonts=self.rng.choice(self.FONT_LISTS),
            device_memory=self.rng.choice([4, 8, 16, 32]),
            hardware_concurrency=self.rng.choice([4, 8, 12, 16]),
            touch_support=self.rng.random() < 0.1,
        )


# =============================================================================
# PROXY MANAGER
# =============================================================================

class ProxyManager:
    """Manages proxy pool with health checks."""
    
    def __init__(self, db_path: str = "ghost_identities.db"):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS proxies (
                    id TEXT PRIMARY KEY,
                    host TEXT NOT NULL,
                    port INTEGER NOT NULL,
                    username TEXT,
                    password TEXT,
                    protocol TEXT DEFAULT 'socks5',
                    geo TEXT DEFAULT 'unknown',
                    health_score REAL DEFAULT 1.0,
                    last_checked TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
    
    def add_proxy(self, proxy: ProxyConfig) -> str:
        import uuid
        proxy_id = str(uuid.uuid4())[:8]
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO proxies (id, host, port, username, password, protocol, geo, health_score)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (proxy_id, proxy.host, proxy.port, proxy.username, proxy.password, 
                  proxy.protocol, proxy.geo, proxy.health_score))
            conn.commit()
        return proxy_id
    
    def get_healthy_proxy(self, geo: Optional[str] = None, min_health: float = 0.5) -> Optional[ProxyConfig]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            query = "SELECT * FROM proxies WHERE health_score >= ?"
            params = [min_health]
            if geo:
                query += " AND geo = ?"
                params.append(geo)
            query += " ORDER BY health_score DESC, last_checked ASC LIMIT 1"
            
            row = conn.execute(query, params).fetchone()
            if row:
                return ProxyConfig(
                    host=row["host"], port=row["port"],
                    username=row["username"], password=row["password"],
                    protocol=row["protocol"], geo=row["geo"],
                    health_score=row["health_score"],
                    last_checked=row["last_checked"]
                )
        return None
    
    def update_health(self, host: str, port: int, success: bool):
        with sqlite3.connect(self.db_path) as conn:
            if success:
                conn.execute("""
                    UPDATE proxies SET health_score = MIN(1.0, health_score + 0.05),
                           last_checked = CURRENT_TIMESTAMP
                    WHERE host = ? AND port = ?
                """, (host, port))
            else:
                conn.execute("""
                    UPDATE proxies SET health_score = MAX(0.0, health_score - 0.15),
                           last_checked = CURRENT_TIMESTAMP
                    WHERE host = ? AND port = ?
                """, (host, port))
            conn.commit()
    
    def load_v2rayn_config(self, config_path: str) -> int:
        """Import proxies from V2RayN config."""
        import json
        with open(config_path, 'r') as f:
            data = json.load(f)
        
        count = 0
        for item in data.get("vmess", []):  # V2RayN format
            # Simplified - real implementation would decode vmess links
            pass
        return count


# =============================================================================
# IDENTITY DATABASE
# =============================================================================

class IdentityDB:
    """Encrypted storage for ghost identities."""
    
    def __init__(self, db_path: str = "ghost_identities.db", key: Optional[bytes] = None):
        self.db_path = db_path
        self.key = key or Fernet.generate_key()
        self.cipher = Fernet(self.key)
        self._init_db()
    
    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS identities (
                    id TEXT PRIMARY KEY,
                    data TEXT NOT NULL,  -- Encrypted JSON
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS identity_credentials (
                    identity_id TEXT,
                    platform TEXT,
                    email TEXT,
                    password TEXT,  -- Encrypted
                    twofa_secret TEXT,  -- Encrypted
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (identity_id, platform)
                )
            """)
            conn.commit()
    
    def save(self, identity: GhostIdentity):
        data = json.dumps(identity.to_dict())
        encrypted = self.cipher.encrypt(data.encode()).decode()
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO identities (id, data, updated_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
            """, (identity.id, encrypted))
            
            # Save credentials separately (double encrypted)
            for platform, creds in identity.credentials.items():
                enc_email = self.cipher.encrypt(creds.get("email", "").encode()).decode()
                enc_pass = self.cipher.encrypt(creds.get("password", "").encode()).decode()
                enc_2fa = self.cipher.encrypt(creds.get("2fa", "").encode()).decode()
                
                conn.execute("""
                    INSERT OR REPLACE INTO identity_credentials 
                    (identity_id, platform, email, password, twofa_secret)
                    VALUES (?, ?, ?, ?, ?)
                """, (identity.id, platform, enc_email, enc_pass, enc_2fa))
            conn.commit()
    
    def load(self, identity_id: str) -> Optional[GhostIdentity]:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                row = conn.execute("SELECT data FROM identities WHERE id = ?", (identity_id,)).fetchone()
                if not row:
                    return None
            
                decrypted = self.cipher.decrypt(row["data"].encode()).decode()
                data = json.loads(decrypted)
            
                # Reconstruct nested objects
                fp_data = data.pop("fingerprint")
                # Remove hash since it's computed in __post_init__
                fp_data.pop("hash", None)
                proxy_data = data.pop("proxy")
                browser_data = data.pop("browser_profile")
                identity_id = data.pop("id")  # Remove id from data to avoid duplicate

                identity = GhostIdentity(
                    id=identity_id,
                    fingerprint=FingerprintProfile(**fp_data),
                    proxy=ProxyConfig(**proxy_data),
                    browser_profile=BrowserProfile(**browser_data),
                    **data
                )
            
                # Load credentials
                creds_rows = conn.execute(
                    "SELECT platform, email, password, twofa_secret FROM identity_credentials WHERE identity_id = ?",
                    (identity_id,)
                ).fetchall()
            
                for row in creds_rows:
                    identity.credentials[row["platform"]] = {
                        "email": self.cipher.decrypt(row["email"].encode()).decode(),
                        "password": self.cipher.decrypt(row["password"].encode()).decode(),
                        "2fa": self.cipher.decrypt(row["twofa_secret"].encode()).decode(),
                    }
            
                return identity
    
    def list_all(self) -> List[str]:
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute("SELECT id FROM identities ORDER BY updated_at DESC").fetchall()
            return [r[0] for r in rows]
    
    def delete(self, identity_id: str):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM identities WHERE id = ?", (identity_id,))
            conn.execute("DELETE FROM identity_credentials WHERE identity_id = ?", (identity_id,))
            conn.commit()


# =============================================================================
# GHOST BROWSER (Main Class)
# =============================================================================

class GhostBrowser:
    """Anti-detect browser controller."""
    
    def __init__(self, identity: GhostIdentity, db: IdentityDB):
        self.identity = identity
        self.db = db
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.playwright = None
    
    async def __aenter__(self):
        await self.launch()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
    
    async def launch(self):
        if not PLAYWRIGHT_AVAILABLE:
            raise RuntimeError("Playwright not available")
        
        self.playwright = await async_playwright().start()
        
        # Launch browser with stealth
        self.browser = await self.playwright.chromium.launch(
            headless=False,  # Visible for debugging, can be True in prod
            args=[
                "--disable-blink-features=AutomationControlled",
                "--disable-dev-shm-usage",
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-web-security",
                "--disable-features=IsolateOrigins,site-per-process",
            ],
            proxy={"server": self.identity.proxy.url} if self.identity.proxy else None
        )
        
        # Create context with fingerprint
        fp = self.identity.fingerprint
        self.context = await self.browser.new_context(
            user_agent=fp.user_agent,
            viewport=fp.viewport,
            screen=fp.screen,
            locale=fp.locale,
            timezone_id=fp.timezone,
            permissions=["geolocation", "notifications"],
            device_scale_factor=1,
            is_mobile=False,
            has_touch=fp.touch_support,
        )
        
        # Apply stealth
        page = await self.context.new_page()
        await stealth_async(page)
        
        # Inject fingerprint spoofing
        await self._inject_fingerprint_spoofing(page)
        
        # Restore browser profile
        await self._restore_profile()
        
        self.page = page
        return self
    
    async def _inject_fingerprint_spoofing(self, page: Page):
        """Inject JavaScript to spoof fingerprint."""
        fp = self.identity.fingerprint
        
        script = f"""
        // Canvas fingerprint spoofing
        const originalToDataURL = HTMLCanvasElement.prototype.toDataURL;
        HTMLCanvasElement.prototype.toDataURL = function(type) {{
            const ctx = this.getContext('2d');
            if (ctx) {{
                const noise = {fp.canvas_noise};
                const imageData = ctx.getImageData(0, 0, this.width, this.height);
                for (let i = 0; i < imageData.data.length; i += 4) {{
                    imageData.data[i] = Math.min(255, Math.max(0, imageData.data[i] + (Math.random() - 0.5) * noise * 255));
                    imageData.data[i+1] = Math.min(255, Math.max(0, imageData.data[i+1] + (Math.random() - 0.5) * noise * 255));
                    imageData.data[i+2] = Math.min(255, Math.max(0, imageData.data[i+2] + (Math.random() - 0.5) * noise * 255));
                }}
                ctx.putImageData(imageData, 0, 0);
            }}
            return originalToDataURL.call(this, type);
        }};
        
        // WebGL fingerprint spoofing
        const getParameter = WebGLRenderingContext.prototype.getParameter;
        WebGLRenderingContext.prototype.getParameter = function(parameter) {{
            if (parameter === 37445) return '{fp.webgl_vendor}';  // UNMASKED_VENDOR_WEBGL
            if (parameter === 37446) return '{fp.webgl_renderer}';  // UNMASKED_RENDERER_WEBGL
            return getParameter.call(this, parameter);
        }};
        
        // Navigator spoofing
        Object.defineProperty(navigator, 'deviceMemory', {{get: () => {fp.device_memory}}});
        Object.defineProperty(navigator, 'hardwareConcurrency', {{get: () => {fp.hardware_concurrency}}});
        Object.defineProperty(navigator, 'platform', {{get: () => '{fp.platform}'}});
        Object.defineProperty(navigator, 'languages', {{get: () => {json.dumps(fp.languages)}}});
        
        // Screen spoofing
        Object.defineProperty(screen, 'width', {{get: () => {fp.screen['width']}}});
        Object.defineProperty(screen, 'height', {{get: () => {fp.screen['height']}}});
        Object.defineProperty(screen, 'colorDepth', {{get: () => {fp.screen['color_depth']}}});
        """
        
        await page.add_init_script(script)
    
    async def _restore_profile(self):
        """Restore cookies, localStorage, etc."""
        if not self.context:
            return
        
        bp = self.identity.browser_profile
        
        # Restore cookies
        if bp.cookies:
            await self.context.add_cookies(bp.cookies)
        
        # Restore localStorage/sessionStorage via page
        if self.page and (bp.local_storage or bp.session_storage):
            script = ""
            for k, v in bp.local_storage.items():
                script += f"localStorage.setItem('{k}', '{v}');"
            for k, v in bp.session_storage.items():
                script += f"sessionStorage.setItem('{k}', '{v}');"
            await self.page.evaluate(script)
    
    async def save_profile(self):
        """Save current browser state to identity."""
        if not self.context or not self.page:
            return
        
        # Save cookies
        cookies = await self.context.cookies()
        self.identity.browser_profile.cookies = cookies
        
        # Save localStorage/sessionStorage
        ls = await self.page.evaluate("() => Object.fromEntries(localStorage)")
        ss = await self.page.evaluate("() => Object.fromEntries(sessionStorage)")
        self.identity.browser_profile.local_storage = ls
        self.identity.browser_profile.session_storage = ss
        
        # Update timestamp
        self.identity.last_used = datetime.now().isoformat()
        
        # Persist
        self.db.save(self.identity)
    
    async def close(self):
        if self.context:
            await self.save_profile()
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()


# =============================================================================
# CLI / TEST
# =============================================================================

async def main():
    """Test the ghost browser."""
    print("=== GHOST BROWSER TEST ===")
    
    # Generate fingerprint
    fg = FingerprintGenerator(seed=42)
    fp = fg.generate("windows")
    print(f"Fingerprint: {fp.hash}")
    print(f"  UA: {fp.user_agent[:60]}...")
    print(f"  Viewport: {fp.viewport}")
    print(f"  Screen: {fp.screen}")
    print(f"  Timezone: {fp.timezone}")
    print(f"  WebGL: {fp.webgl_vendor} / {fp.webgl_renderer}")
    
    # Create identity
    proxy = ProxyConfig(host="127.0.0.1", port=1080, protocol="socks5", geo="RU")
    bp = BrowserProfile(context_id="test_ctx")
    
    identity = GhostIdentity(
        id="test_001",
        fingerprint=fp,
        proxy=proxy,
        browser_profile=bp,
    )
    
    # Init DB
    db = IdentityDB("test_ghost.db")
    db.save(identity)
    print(f"\nSaved identity: {identity.id}")
    
    # Load back
    loaded = db.load("test_001")
    print(f"Loaded identity: {loaded.id}")
    print(f"  Fingerprint hash matches: {loaded.fingerprint.hash == fp.hash}")
    
    print("\n=== TEST COMPLETE ===")


if __name__ == "__main__":
    asyncio.run(main())
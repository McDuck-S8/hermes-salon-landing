#!/usr/bin/env python3
"""
Posting & Publishing Module — Publish content to social platforms, blogs, CPA networks.
"""

import asyncio
import json
import random
import sqlite3
import os
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List, Callable
from playwright.async_api import Page, FileChooser

try:
    from playwright.async_api import async_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False


# =============================================================================
# DATA MODELS
# =============================================================================

@dataclass
class PostContent:
    """Content to publish."""
    text: str = ""
    hashtags: List[str] = field(default_factory=list)
    mentions: List[str] = field(default_factory=list)
    links: List[str] = field(default_factory=list)
    media_paths: List[str] = field(default_factory=list)  # images, videos
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def formatted_text(self) -> str:
        parts = [self.text]
        if self.hashtags:
            parts.append(" ".join(f"#{h}" for h in self.hashtags))
        if self.mentions:
            parts.append(" ".join(f"@{m}" for m in self.mentions))
        if self.links:
            parts.append(" ".join(self.links))
        return "\n\n".join(parts)


@dataclass
class PostResult:
    """Result of posting attempt."""
    success: bool
    platform: str
    post_id: Optional[str] = None
    url: Optional[str] = None
    error: Optional[str] = None
    posted_at: str = field(default_factory=lambda: datetime.now().isoformat())
    raw_response: Optional[str] = None


@dataclass
class ScheduledPost:
    """Scheduled post for later publishing."""
    id: str
    platform: str
    content: PostContent
    account_identity: str
    scheduled_at: str
    status: str = "pending"  # pending, posted, failed, cancelled
    attempts: int = 0
    max_attempts: int = 3
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    posted_at: Optional[str] = None
    result: Optional[PostResult] = None


# =============================================================================
# PLATFORM POSTERS (Base + Specific)
# =============================================================================

class BasePoster:
    """Base class for platform posters."""
    
    def __init__(self, ghost_browser, behavior_engine):
        self.browser = ghost_browser
        self.behavior = behavior_engine
        self.page: Page = ghost_browser.page
    
    async def login(self, credentials: Dict[str, str]) -> bool:
        raise NotImplementedError
    
    async def post(self, content: PostContent) -> PostResult:
        raise NotImplementedError
    
    async def check_logged_in(self) -> bool:
        raise NotImplementedError
    
    async def _wait_human(self, min_sec: float = 1, max_sec: float = 3):
        await asyncio.sleep(random.uniform(min_sec, max_sec))
    
    async def _handle_file_upload(self, file_paths: List[str], 
                                   trigger_selector: str = "input[type='file']") -> bool:
        """Handle file upload dialog."""
        if not file_paths:
            return False
        
        try:
            # Set up file chooser promise before clicking
            async with self.page.expect_file_chooser() as fc_info:
                await self.behavior.mouse.click(self.page)
                await self.page.click(trigger_selector)
            
            file_chooser = await fc_info.value
            await file_chooser.set_files(file_paths)
            await self._wait_human(2, 5)
            return True
        except Exception as e:
            print(f"File upload error: {e}")
            return False


class TikTokPoster(BasePoster):
    """TikTok video/image poster."""
    
    LOGIN_URL = "https://www.tiktok.com/login"
    UPLOAD_URL = "https://www.tiktok.com/upload"
    
    async def check_logged_in(self) -> bool:
        try:
            await self.page.goto("https://www.tiktok.com/", wait_until="networkidle")
            await self._wait_human(2, 4)
            # Check for profile icon
            profile = await self.page.locator("[data-e2e='profile-icon'], .profile-icon").first
            return await profile.count() > 0
        except:
            return False
    
    async def login(self, credentials: Dict[str, str]) -> bool:
        await self.page.goto(self.LOGIN_URL, wait_until="networkidle")
        await self._wait_human(2, 4)
        
        # Click email/username login
        email_btn = await self.page.locator("text=Use phone / email / username").first
        if await email_btn.count() > 0:
            await email_btn.click()
            await self._wait_human(1, 2)
        
        # Fill credentials
        await self.behavior.fill_form(self.page, {
            "input[name='username']": credentials.get("username", ""),
            "input[type='password']": credentials.get("password", ""),
        })
        
        # Submit
        submit = await self.page.locator("button:has-text('Log in'), button[type='submit']").first
        await self.behavior.mouse.click(self.page)
        await submit.click()
        
        await self._wait_human(5, 10)
        return await self.check_logged_in()
    
    async def post(self, content: PostContent) -> PostResult:
        try:
            # Go to upload
            await self.page.goto(self.UPLOAD_URL, wait_until="networkidle")
            await self._wait_human(3, 5)
            
            # Upload media
            if content.media_paths:
                uploaded = await self._handle_file_upload(
                    content.media_paths,
                    "input[type='file'][accept*='video'], input[type='file'][accept*='image']"
                )
                if not uploaded:
                    return PostResult(success=False, platform="tiktok", error="Media upload failed")
                await self._wait_human(5, 10)  # Wait for processing
            
            # Fill caption
            caption_selector = "[data-e2e='upload-caption'], .public-DraftEditor-content, textarea[placeholder*='caption']"
            caption_el = await self.page.locator(caption_selector).first
            if await caption_el.count() > 0:
                await self.behavior.typing.type(self.page, caption_selector, content.formatted_text())
                await self._wait_human(1, 2)
            
            # Post settings (location, privacy, etc.)
            # ... additional settings here
            
            # Click Post
            post_btn = await self.page.locator("button:has-text('Post'), button[data-e2e='post-btn']").first
            await self.behavior.mouse.click(self.page)
            await post_btn.click()
            
            await self._wait_human(5, 10)
            
            # Get post URL
            post_url = self.page.url
            
            return PostResult(
                success=True,
                platform="tiktok",
                url=post_url,
            )
        except Exception as e:
            return PostResult(success=False, platform="tiktok", error=str(e))


class YouTubePoster(BasePoster):
    """YouTube / YouTube Shorts poster."""
    
    LOGIN_URL = "https://accounts.google.com/signin"
    UPLOAD_URL = "https://studio.youtube.com"
    
    async def check_logged_in(self) -> bool:
        try:
            await self.page.goto("https://studio.youtube.com", wait_until="networkidle")
            await self._wait_human(2, 4)
            # Check for create button
            create_btn = await self.page.locator("#create-icon, ytcp-button[icon='add']").first
            return await create_btn.count() > 0
        except:
            return False
    
    async def login(self, credentials: Dict[str, str]) -> bool:
        # Google login is complex - usually handled by cookies
        # This assumes cookies are already in browser profile
        return await self.check_logged_in()
    
    async def post(self, content: PostContent) -> PostResult:
        try:
            await self.page.goto(self.UPLOAD_URL, wait_until="networkidle")
            await self._wait_human(2, 4)
            
            # Click Create -> Upload video
            create_btn = await self.page.locator("#create-icon, ytcp-button[icon='add']").first
            await self.behavior.mouse.click(self.page)
            await create_btn.click()
            await self._wait_human(1, 2)
            
            upload_btn = await self.page.locator("text=Upload video, ytcp-button:has-text('Upload video')").first
            await upload_btn.click()
            await self._wait_human(2, 3)
            
            # File upload
            if content.media_paths:
                file_input = await self.page.locator("input[type='file']").first
                await file_input.set_input_files(content.media_paths)
                await self._wait_human(10, 20)  # Upload + processing
            
            # Fill details
            await self._wait_human(2, 4)
            
            # Title
            title_el = await self.page.locator("#title-textarea, #title").first
            if await title_el.count() > 0:
                title_text = content.text[:100] if content.text else "New Video"
                await self.behavior.typing.type(self.page, "#title-textarea, #title", title_text)
            
            # Description
            desc_el = await self.page.locator("#description-textarea, #description").first
            if await desc_el.count() > 0:
                await self.behavior.typing.type(self.page, "#description-textarea, #description", content.formatted_text())
            
            # Next through steps
            for _ in range(3):  # Audience, monetization, visibility
                next_btn = await self.page.locator("button:has-text('Next'), ytcp-button:has-text('Next')").first
                if await next_btn.count() > 0:
                    await self.behavior.mouse.click(self.page)
                    await next_btn.click()
                    await self._wait_human(1, 2)
            
            # Publish
            publish_btn = await self.page.locator("button:has-text('Publish'), ytcp-button:has-text('Publish')").first
            await self.behavior.mouse.click(self.page)
            await publish_btn.click()
            
            await self._wait_human(5, 10)
            
            return PostResult(
                success=True,
                platform="youtube",
                url=self.page.url,
            )
        except Exception as e:
            return PostResult(success=False, platform="youtube", error=str(e))


class InstagramPoster(BasePoster):
    """Instagram poster (feed, reels, stories)."""
    
    LOGIN_URL = "https://www.instagram.com/accounts/login/"
    HOME_URL = "https://www.instagram.com/"
    
    async def check_logged_in(self) -> bool:
        try:
            await self.page.goto(self.HOME_URL, wait_until="networkidle")
            await self._wait_human(2, 4)
            # Check for profile or create button
            create = await self.page.locator("svg[aria-label='New post'], [data-testid='new-post-button']").first
            return await create.count() > 0
        except:
            return False
    
    async def login(self, credentials: Dict[str, str]) -> bool:
        await self.page.goto(self.LOGIN_URL, wait_until="networkidle")
        await self._wait_human(2, 4)
        
        await self.behavior.fill_form(self.page, {
            "input[name='username']": credentials.get("username", ""),
            "input[name='password']": credentials.get("password", ""),
        })
        
        login_btn = await self.page.locator("button[type='submit'], text=Log in").first
        await self.behavior.mouse.click(self.page)
        await login_btn.click()
        
        await self._wait_human(5, 10)
        return await self.check_logged_in()
    
    async def post(self, content: PostContent) -> PostResult:
        try:
            await self.page.goto(self.HOME_URL, wait_until="networkidle")
            await self._wait_human(2, 3)
            
            # Click create
            create_btn = await self.page.locator("svg[aria-label='New post'], [data-testid='new-post-button']").first
            await self.behavior.mouse.click(self.page)
            await create_btn.click()
            await self._wait_human(1, 2)
            
            # Select post type (Post/Reel/Story)
            # Default to Post
            post_option = await self.page.locator("text=Post").first
            if await post_option.count() > 0:
                await post_option.click()
            
            # Upload media
            if content.media_paths:
                file_input = await self.page.locator("input[type='file']").first
                await file_input.set_input_files(content.media_paths)
                await self._wait_human(3, 6)
            
            # Next
            next_btn = await self.page.locator("text=Next, button:has-text('Next')").first
            await self.behavior.mouse.click(self.page)
            await next_btn.click()
            await self._wait_human(1, 2)
            
            # Filter/Edit (skip)
            next_btn2 = await self.page.locator("text=Next, button:has-text('Next')").first
            await next_btn2.click()
            await self._wait_human(1, 2)
            
            # Caption
            caption_el = await self.page.locator("textarea[aria-label='Write a caption...']").first
            if await caption_el.count() > 0:
                await self.behavior.typing.type(self.page, "textarea[aria-label='Write a caption...']", content.formatted_text())
            
            # Share
            share_btn = await self.page.locator("text=Share, button:has-text('Share')").first
            await self.behavior.mouse.click(self.page)
            await share_btn.click()
            
            await self._wait_human(5, 10)
            
            return PostResult(
                success=True,
                platform="instagram",
                url=self.page.url,
            )
        except Exception as e:
            return PostResult(success=False, platform="instagram", error=str(e))


class TelegramPoster(BasePoster):
    """Telegram channel/group poster."""
    
    WEB_URL = "https://web.telegram.org/k/"
    
    async def check_logged_in(self) -> bool:
        try:
            await self.page.goto(self.WEB_URL, wait_until="networkidle")
            await self._wait_human(3, 5)
            # Check for chat list
            chat_list = await self.page.locator(".chatlist, [data-testid='chat-list']").first
            return await chat_list.count() > 0
        except:
            return False
    
    async def login(self, credentials: Dict[str, str]) -> bool:
        # Telegram web requires phone + code
        # Simplified - assumes session exists
        return await self.check_logged_in()
    
    async def post(self, content: PostContent) -> PostResult:
        try:
            await self.page.goto(self.WEB_URL, wait_until="networkidle")
            await self._wait_human(2, 3)
            
            # Find target chat/channel
            # This would need the chat name/username
            target = content.metadata.get("target_chat", "")
            if target:
                search = await self.page.locator("input[placeholder*='Search'], .input-search").first
                await self.behavior.typing.type(self.page, "input[placeholder*='Search']", target)
                await self._wait_human(1, 2)
                
                chat = await self.page.locator(f".chat:has-text('{target}')").first
                await self.behavior.mouse.click(self.page)
                await chat.click()
                await self._wait_human(1, 2)
            
            # Type message
            msg_input = await self.page.locator(".input-message-input, [contenteditable='true']").first
            if await msg_input.count() > 0:
                await self.behavior.typing.type(self.page, ".input-message-input", content.formatted_text())
                
                # Send
                await self.page.keyboard.press("Enter")
                await self._wait_human(1, 2)
            
            return PostResult(
                success=True,
                platform="telegram",
                url=self.page.url,
            )
        except Exception as e:
            return PostResult(success=False, platform="telegram", error=str(e))


class CPAposter(BasePoster):
    """CPA Network poster (creative upload, link generation)."""
    
    NETWORKS = {
        "cpagrip": {
            "login": "https://www.cpagrip.com/login",
            "dashboard": "https://www.cpagrip.com/dashboard",
            "creatives": "https://www.cpagrip.com/creatives",
        },
        "mylead": {
            "login": "https://www.mylead.global/login",
            "dashboard": "https://www.mylead.global/dashboard",
            "offers": "https://www.mylead.global/offers",
        },
        "adcombo": {
            "login": "https://adcombo.com/login",
            "dashboard": "https://adcombo.com/offers",
        },
    }
    
    def __init__(self, ghost_browser, behavior_engine, network: str = "cpagrip"):
        super().__init__(ghost_browser, behavior_engine)
        self.network = network
        self.urls = self.NETWORKS.get(network, self.NETWORKS["cpagrip"])
    
    async def check_logged_in(self) -> bool:
        try:
            await self.page.goto(self.urls["dashboard"], wait_until="networkidle")
            await self._wait_human(2, 4)
            # Check for logout button or user menu
            return "login" not in self.page.url
        except:
            return False
    
    async def login(self, credentials: Dict[str, str]) -> bool:
        await self.page.goto(self.urls["login"], wait_until="networkidle")
        await self._wait_human(2, 4)
        
        await self.behavior.fill_form(self.page, {
            "input[name='email'], input[name='username']": credentials.get("email", ""),
            "input[name='password']": credentials.get("password", ""),
        })
        
        submit = await self.page.locator("button[type='submit'], text=Login, text=Sign in").first
        await self.behavior.mouse.click(self.page)
        await submit.click()
        
        await self._wait_human(5, 10)
        return await self.check_logged_in()
    
    async def get_offer_link(self, offer_id: str, subid: str = "") -> PostResult:
        """Generate tracking link for offer."""
        try:
            await self.page.goto(self.urls.get("offers", self.urls["dashboard"]), wait_until="networkidle")
            await self._wait_human(2, 3)
            
            # Search for offer
            search = await self.page.locator("input[placeholder*='Search'], input[name='search']").first
            await self.behavior.typing.type(self.page, "input[placeholder*='Search']", offer_id)
            await self._wait_human(1, 2)
            
            # Click offer
            offer_row = await self.page.locator(f"tr:has-text('{offer_id}'), .offer-row:has-text('{offer_id}')").first
            await self.behavior.mouse.click(self.page)
            await offer_row.click()
            await self._wait_human(1, 2)
            
            # Get link
            link_btn = await self.page.locator("text=Get link, text=Generate, button:has-text('Link')").first
            if await link_btn.count() > 0:
                await link_btn.click()
                await self._wait_human(1, 2)
                
                # Copy link
                link_input = await self.page.locator("input[readonly], input[value*='http']").first
                link = await link_input.input_value()
                
                return PostResult(
                    success=True,
                    platform=f"cpa_{self.network}",
                    url=link,
                )
            
            return PostResult(success=False, platform=f"cpa_{self.network}", error="Link generation failed")
        except Exception as e:
            return PostResult(success=False, platform=f"cpa_{self.network}", error=str(e))
    
    async def upload_creative(self, creative_path: str, offer_id: str) -> PostResult:
        """Upload creative for offer."""
        # Network-specific implementation
        return PostResult(success=False, platform=f"cpa_{self.network}", error="Not implemented")


# =============================================================================
# POSTING ORCHESTRATOR
# =============================================================================

class PostingOrchestrator:
    """Manages posting across multiple platforms."""
    
    def __init__(self, identity_db, ghost_browser_factory, behavior_factory):
        self.identity_db = identity_db
        self.ghost_browser_factory = ghost_browser_factory
        self.behavior_factory = behavior_factory
        self.scheduler_db = "scheduled_posts.db"
        self._init_scheduler_db()
    
    def _init_scheduler_db(self):
        with sqlite3.connect(self.scheduler_db) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS scheduled_posts (
                    id TEXT PRIMARY KEY,
                    platform TEXT,
                    content TEXT,  -- JSON
                    account_identity TEXT,
                    scheduled_at TEXT,
                    status TEXT DEFAULT 'pending',
                    attempts INTEGER DEFAULT 0,
                    max_attempts INTEGER DEFAULT 3,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    posted_at TEXT,
                    result TEXT
                )
            """)
            conn.commit()
    
    def get_poster(self, platform: str, browser, behavior):
        """Get poster instance for platform."""
        posters = {
            "tiktok": TikTokPoster,
            "youtube": YouTubePoster,
            "instagram": InstagramPoster,
            "telegram": TelegramPoster,
            "cpa_cpagrip": lambda b, be: CPAposter(b, be, "cpagrip"),
            "cpa_mylead": lambda b, be: CPAposter(b, be, "mylead"),
            "cpa_adcombo": lambda b, be: CPAposter(b, be, "adcombo"),
        }
        
        poster_class = posters.get(platform.lower())
        if not poster_class:
            raise ValueError(f"Unknown platform: {platform}")
        return poster_class(browser, behavior)
    
    async def post_now(self, platform: str, identity_id: str, content: PostContent) -> PostResult:
        """Post immediately using identity."""
        identity = self.identity_db.load(identity_id)
        if not identity:
            return PostResult(success=False, platform=platform, error="Identity not found")
        
        # Check credentials
        creds = identity.credentials.get(platform.replace("cpa_", ""), {})
        if not creds and not platform.startswith("cpa_"):
            return PostResult(success=False, platform=platform, error="No credentials for platform")
        
        # Create browser session
        browser = await self.ghost_browser_factory(identity)
        behavior = self.behavior_factory(identity)
        
        try:
            async with browser:
                poster = self.get_poster(platform, browser, behavior)
                
                # Login if needed
                if not await poster.check_logged_in():
                    if creds:
                        await poster.login(creds)
                    else:
                        return PostResult(success=False, platform=platform, error="Login required")
                
                # Post
                result = await poster.post(content)
                return result
        except Exception as e:
            return PostResult(success=False, platform=platform, error=str(e))
    
    def schedule_post(self, platform: str, identity_id: str, content: PostContent, 
                      scheduled_at: datetime) -> str:
        """Schedule post for later."""
        import uuid
        post_id = str(uuid.uuid4())[:12]
        
        scheduled = ScheduledPost(
            id=post_id,
            platform=platform,
            content=content,
            account_identity=identity_id,
            scheduled_at=scheduled_at.isoformat(),
        )
        
        with sqlite3.connect(self.scheduler_db) as conn:
            conn.execute("""
                INSERT INTO scheduled_posts (id, platform, content, account_identity, scheduled_at, status)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (post_id, platform, json.dumps(asdict(content)), identity_id, 
                  scheduled_at.isoformat(), "pending"))
            conn.commit()
        
        return post_id
    
    async def run_scheduler(self):
        """Run due scheduled posts."""
        now = datetime.now().isoformat()
        
        with sqlite3.connect(self.scheduler_db) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute("""
                SELECT * FROM scheduled_posts 
                WHERE status = 'pending' AND scheduled_at <= ?
                ORDER BY scheduled_at ASC
                LIMIT 10
            """, (now,)).fetchall()
        
        for row in rows:
            content = PostContent(**json.loads(row["content"]))
            result = await self.post_now(row["platform"], row["account_identity"], content)
            
            with sqlite3.connect(self.scheduler_db) as conn:
                conn.execute("""
                    UPDATE scheduled_posts 
                    SET status = ?, attempts = attempts + 1, posted_at = ?, result = ?
                    WHERE id = ?
                """, ("posted" if result.success else "failed", 
                      datetime.now().isoformat(), json.dumps(asdict(result)), row["id"]))
                conn.commit()
            
            # Rate limit between posts
            await asyncio.sleep(random.uniform(60, 300))


# =============================================================================
# TEST
# =============================================================================

def test_post_content():
    print("=== POST CONTENT TEST ===")
    
    content = PostContent(
        text="Check out this amazing offer! 🔥",
        hashtags=["betting", "india", "cricket", "bonus"],
        mentions=["1xBet_Official", "CricketIndia"],
        links=["https://1xbet.com/bonus"],
        media_paths=["/path/to/video.mp4", "/path/to/thumbnail.jpg"],
    )
    
    print(f"Formatted:\n{content.formatted_text()}")
    
    print("\nAvailable platforms:")
    print("  - tiktok")
    print("  - youtube")
    print("  - instagram")
    print("  - telegram")
    print("  - cpa_cpagrip")
    print("  - cpa_mylead")
    print("  - cpa_adcombo")


if __name__ == "__main__":
    test_post_content()
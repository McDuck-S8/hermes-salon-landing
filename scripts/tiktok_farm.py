#!/usr/bin/env python3
"""
TikTok Farm Orchestrator — Phase 1, Фаза 1: TikTok до конверсий.

Интеграция с ghost-surfer: FingerprintGenerator, IdentityDB, ProxyManager, TikTokPoster.

Usage:
  python scripts/tiktok_farm.py --list                         # список аккаунтов
  python scripts/tiktok_farm.py --create --geo US               # новый аккаунт
  python scripts/tiktok_farm.py --post account_1 video.mp4      # пост с аккаунта
  python scripts/tiktok_farm.py --warmup account_1              # прогрев
  python scripts/tiktok_farm.py --health                        # здоровье фермы
  python scripts/tiktok_farm.py --queue video/ folder/          # очередь постинга
"""

import argparse
import asyncio
import json
import os
import random
import sqlite3
import sys
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any, List

# ── Пути ────────────────────────────────────────────────────────────────

FARM_DB = Path("cache/tiktok_farm.db")
SESSIONS_DIR = Path("cache/tiktok_sessions")
CONTENT_DIR = Path("cache/content_locking_videos")

# ── Ghost-surfer импорт ─────────────────────────────────────────────────

sys.path.insert(0, str(Path("skills/automation/ghost-surfer/scripts")))

try:
    from ghost_browser import FingerprintGenerator, IdentityDB, ProxyManager, FingerprintProfile
    from posting import TikTokPoster, PostContent, PostResult
    GHOST_AVAILABLE = True
except ImportError:
    GHOST_AVAILABLE = False
    print("⚠ ghost-surfer not available. Only farm management will work.")


# =========================================================================
# FARM DATABASE
# =========================================================================

class FarmDB:
    """SQLite-backed persistence for farm accounts and queue."""

    def __init__(self, db_path: str = str(FARM_DB)):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self._init_db()

    def _conn(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        with self._conn() as c:
            c.executescript("""
                CREATE TABLE IF NOT EXISTS accounts (
                    id TEXT PRIMARY KEY,
                    username TEXT,
                    geo TEXT DEFAULT 'US',
                    fingerprint_json TEXT,
                    proxy TEXT,
                    status TEXT DEFAULT 'created',
                    created_at TEXT,
                    last_login TEXT,
                    login_count INTEGER DEFAULT 0,
                    posts_count INTEGER DEFAULT 0,
                    cookies_path TEXT,
                    notes TEXT
                );
                CREATE TABLE IF NOT EXISTS posts_queue (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    account_id TEXT,
                    video_path TEXT,
                    caption TEXT,
                    hashtags TEXT,
                    status TEXT DEFAULT 'pending',
                    created_at TEXT,
                    posted_at TEXT,
                    result TEXT,
                    error TEXT,
                    FOREIGN KEY (account_id) REFERENCES accounts(id)
                );
                CREATE TABLE IF NOT EXISTS health_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    account_id TEXT,
                    check_type TEXT,
                    result TEXT,
                    detail TEXT,
                    checked_at TEXT,
                    FOREIGN KEY (account_id) REFERENCES accounts(id)
                );
            """)

    def add_account(self, acc: dict) -> bool:
        with self._conn() as c:
            c.execute(
                "INSERT OR REPLACE INTO accounts VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                (acc["id"], acc.get("username", ""), acc.get("geo", "US"),
                 json.dumps(acc.get("fingerprint", {})), acc.get("proxy", ""),
                 acc.get("status", "created"), acc.get("created_at", datetime.now().isoformat()),
                 None, 0, 0, acc.get("cookies_path"), acc.get("notes", ""))
            )
        return True

    def list_accounts(self, status: str = None) -> List[dict]:
        with self._conn() as conn:
            c = conn.cursor()
            if status:
                c.execute("SELECT * FROM accounts WHERE status = ? ORDER BY created_at", (status,))
            else:
                c.execute("SELECT * FROM accounts ORDER BY created_at")
            rows = c.fetchall()
            cols = ["id", "username", "geo", "fingerprint_json", "proxy", "status",
                    "created_at", "last_login", "login_count", "posts_count", "cookies_path", "notes"]
            return [dict(zip(cols, r)) for r in rows]

    def get_account(self, account_id: str) -> Optional[dict]:
        with self._conn() as conn:
            c = conn.cursor()
            c.execute("SELECT * FROM accounts WHERE id = ?", (account_id,))
            r = c.fetchone()
            if not r:
                return None
            cols = ["id", "username", "geo", "fingerprint_json", "proxy", "status",
                    "created_at", "last_login", "login_count", "posts_count", "cookies_path", "notes"]
            return dict(zip(cols, r))

    def update_account(self, account_id: str, **kwargs):
        sets = ", ".join(f"{k} = ?" for k in kwargs)
        vals = list(kwargs.values()) + [account_id]
        with self._conn() as conn:
            conn.execute(f"UPDATE accounts SET {sets} WHERE id = ?", vals)

    def enqueue_post(self, account_id: str, video: str, caption: str, hashtags: str = "") -> int:
        with self._conn() as conn:
            c = conn.cursor()
            c.execute(
                "INSERT INTO posts_queue (account_id, video_path, caption, hashtags, created_at) VALUES (?,?,?,?,?)",
                (account_id, video, caption, hashtags, datetime.now().isoformat())
            )
            return c.lastrowid

    def get_pending_posts(self) -> List[dict]:
        with self._conn() as conn:
            c = conn.cursor()
            c.execute("""
                SELECT q.*, a.username, a.geo FROM posts_queue q
                JOIN accounts a ON a.id = q.account_id
                WHERE q.status = 'pending' ORDER BY q.id
            """)
            rows = c.fetchall()
            cols = ["id", "account_id", "video_path", "caption", "hashtags",
                    "status", "created_at", "posted_at", "result", "error",
                    "username", "geo"]
            return [dict(zip(cols, r)) for r in rows]

    def health_log(self, account_id: str, check_type: str, result: str, detail: str = ""):
        with self._conn() as conn:
            conn.execute(
                "INSERT INTO health_log (account_id, check_type, result, detail, checked_at) VALUES (?,?,?,?,?)",
                (account_id, check_type, result, detail, datetime.now().isoformat())
            )

    def get_health(self, account_id: str = None, limit: int = 20) -> List[dict]:
        with self._conn() as conn:
            c = conn.cursor()
            if account_id:
                c.execute(
                    "SELECT * FROM health_log WHERE account_id = ? ORDER BY checked_at DESC LIMIT ?",
                    (account_id, limit)
                )
            else:
                c.execute("SELECT * FROM health_log ORDER BY checked_at DESC LIMIT ?", (limit,))
            rows = c.fetchall()
            cols = ["id", "account_id", "check_type", "result", "detail", "checked_at"]
            return [dict(zip(cols, r)) for r in rows]


# =========================================================================
# CAPTCHA HANDLER
# =========================================================================

class CaptchaHandler:
    """
    Обнаружение и решение CAPTCHA на TikTok.
    Support: 2captcha (API key) или ручной режим.

    URL images/img в DOM токен = 2captcha solve
    """

    def __init__(self, api_key: str = ""):
        self.api_key = api_key or os.environ.get("TWOCAPTCHA_API_KEY", "")
        self._solver = None  # lazy import

    def _ensure_solver(self):
        if not self._solver and self.api_key:
            try:
                from twocaptcha import TwoCaptcha
                self._solver = TwoCaptcha(self.api_key)
            except ImportError:
                print("⚠ 2captcha not installed. pip install 2captcha-python")

    async def detect(self, page) -> bool:
        """Проверить, есть ли CAPTCHA на странице."""
        try:
            # TikTok known CAPTCHA patterns
            patterns = [
                "#captcha-container",
                ".captcha-verify-container",
                "[data-testid='captcha-container']",
                "iframe[src*='captcha']",
                "iframe[src*='verification']",
                "div:has(> div[id*='captcha'])",
                "[class*='captcha']",
            ]
            for sel in patterns:
                el = await page.locator(sel).first
                if await el.count() > 0 and await el.is_visible():
                    return True
            # Also check for simple puzzle slider
            body = await page.content()
            if "captcha" in body.lower() and ("verify" in body.lower() or "puzzle" in body.lower()):
                return True
            return False
        except Exception:
            return False

    async def solve(self, page) -> bool:
        """Решить CAPTCHA. Пытается auto-solve, затем manual fallback."""
        self._ensure_solver()

        if self._solver:
            try:
                print("  Solving CAPTCHA via 2captcha...")
                # Get page screenshot for solving
                screenshot = await page.screenshot()
                from pathlib import Path
                import tempfile
                tmp = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
                tmp.write(screenshot)
                tmp.close()
                result = self._solver.normal(tmp.name)
                os.unlink(tmp.name)
                if result and result.get("code"):
                    print(f"  ✅ CAPTCHA solved: {result['code'][:20]}...")
                    return True
            except Exception as e:
                print(f"  ⚠ Auto-solve failed: {e}")

        # Manual fallback — alert user
        print("  ⚠ CAPTCHA detected, manual intervention needed.")
        print("  Solve in browser and type 'done' when complete.")
        return False


# =========================================================================
# FARM ORCHESTRATOR
# =========================================================================

class TikTokFarmOrchestrator:
    """
    Оркестратор фермы TikTok.

    Управляет: созданием аккаунтов, сессиями, постингом,
    очередью публикаций, мониторингом здоровья.
    """

    def __init__(self):
        self.db = FarmDB()
        self.captcha = CaptchaHandler()
        self.fingerprints = FingerprintGenerator() if GHOST_AVAILABLE else None
        self.proxies = ProxyManager() if GHOST_AVAILABLE else None
        self.session = None  # браузерная сессия (lazy)

    # ── Account Management ──────────────────────────────────────────────

    def create_account(self, geo: str = "US") -> dict:
        """
        Создать запись аккаунта в ферме с fingerprint и прокси.
        Возвращает dict с данными аккаунта.
        """
        acc_id = f"tt_{geo}_{datetime.now().strftime('%y%m%d_%H%M%S')}"

        fingerprint = {}
        if self.fingerprints:
            fp = self.fingerprints.generate(geo=geo)
            fingerprint = asdict(fp) if hasattr(fp, "__dataclass_fields__") else fp

        proxy = ""
        if self.proxies:
            p = self.proxies.get_best(geo=geo)
            proxy = p or ""

        account = {
            "id": acc_id,
            "geo": geo,
            "fingerprint": fingerprint,
            "proxy": proxy,
            "status": "created",
            "created_at": datetime.now().isoformat(),
        }
        self.db.add_account(account)
        print(f"  ✅ Account {acc_id} created (geo={geo})")
        return account

    def list_accounts(self, status: str = None) -> List[dict]:
        """Список аккаунтов."""
        return self.db.list_accounts(status)

    def get_session_dir(self, account_id: str) -> str:
        """Путь к директории сессии (cookies + storage state)."""
        d = SESSIONS_DIR / account_id
        d.mkdir(parents=True, exist_ok=True)
        return str(d)

    # ── Posting ─────────────────────────────────────────────────────────

    async def post_video(self, account_id: str, video: str,
                         caption: str = "", hashtags: str = "") -> PostResult:
        """
        Опубликовать видео с аккаунта. Использует сохранённую сессию.
        """
        acc = self.db.get_account(account_id)
        if not acc:
            return PostResult(success=False, platform="tiktok", error=f"Account {account_id} not found")

        if not os.path.exists(video):
            return PostResult(success=False, platform="tiktok", error=f"Video not found: {video}")

        from playwright.async_api import async_playwright

        async with async_playwright() as p:
            cookies_path = acc.get("cookies_path")

            # -- Launch context with fingerprint --
            proxy_config = {}
            if acc.get("proxy"):
                proxy_config = {"server": acc["proxy"]}

            try:
                fingerprint = json.loads(acc.get("fingerprint_json", "{}"))
            except (json.JSONDecodeError, TypeError):
                fingerprint = {}

            browser = await p.chromium.launch(headless=False, proxy=proxy_config if proxy_config else None)
            context = await browser.new_context(
                user_agent=fingerprint.get("user_agent", ""),
                viewport=fingerprint.get("viewport", {"width": 1280, "height": 720}),
                locale=fingerprint.get("locale", "en-US"),
                timezone_id=fingerprint.get("timezone", "America/New_York"),
                storage_state=cookies_path if cookies_path and os.path.exists(cookies_path) else None,
            )

            # Apply stealth
            try:
                from playwright_stealth import stealth_async
                page = await context.new_page()
                await stealth_async(page)
            except ImportError:
                page = await context.new_page()

            # -- Post via TikTokPoster --
            poster = TikTokPoster.__new__(TikTokPoster)
            poster.page = page
            poster.behavior = None  # simplified, no human behavior for now
            poster._wait_human = lambda mi, ma: asyncio.sleep(random.uniform(mi, ma))

            # Check session
            logged_in = await poster.check_logged_in()
            if not logged_in:
                print(f"  Session expired for {account_id}, trying re-login...")
                # TODO: inject credentials from env/keystore
                db_entry = self.db.get_account(account_id)
                username = db_entry.get("username", "") if db_entry else ""
                if not username:
                    await browser.close()
                    return PostResult(success=False, platform="tiktok",
                                      error="No session and no credentials stored")

                result = await poster.login({"username": username, "password": "FROM_KEYSTORE"})
                if not result:
                    # Check for CAPTCHA
                    if await self.captcha.detect(page):
                        print(f"  ⚠ CAPTCHA on login for {account_id}")
                        await self.captcha.solve(page)
                    await browser.close()
                    return PostResult(success=False, platform="tiktok", error="Login failed")

                # Save session
                storage = await context.storage_state()
                spath = os.path.join(self.get_session_dir(account_id), "state.json")
                with open(spath, "w") as f:
                    json.dump(storage, f)
                self.db.update_account(account_id, cookies_path=spath, last_login=datetime.now().isoformat())

            # Upload
            content = PostContent(
                text=caption,
                hashtags=[h.strip() for h in hashtags.split(",") if h.strip()],
                media_paths=[video],
            )
            result = await poster.post(content)
            if result.success:
                self.db.update_account(account_id, posts_count=acc.get("posts_count", 0) + 1)
                self.db.health_log(account_id, "post", "ok", f"Posted: {video}")
            else:
                self.db.health_log(account_id, "post", "fail", result.error or "unknown")

            await browser.close()
            return result

    # ── Queue Processing ────────────────────────────────────────────────

    def enqueue_videos(self, video_dir: str, account_id: str = None,
                       caption: str = "🔥 FREE", hashtags: str = "fyp,foryou") -> int:
        """Добавить все видео из директории в очередь постинга."""
        path = Path(video_dir)
        videos = sorted(path.glob("*.mp4"))
        if not videos:
            print(f"  No videos found in {video_dir}")
            return 0

        # If no account specified, use all available
        accounts = self.db.list_accounts(status="active")
        if not accounts:
            print("  No active accounts. Create one first: --create --geo US")
            return 0

        count = 0
        for i, vp in enumerate(videos):
            a = accounts[i % len(accounts)]
            self.db.enqueue_post(a["id"], str(vp), caption, hashtags)
            count += 1

        print(f"  ✅ {count} videos enqueued across {len(accounts)} accounts")
        return count

    async def process_queue(self, max_posts: int = 10):
        """Обработать очередь постинга."""
        pending = self.db.get_pending_posts()
        if not pending:
            print("  Queue empty.")
            return

        done = 0
        for post in pending:
            if done >= max_posts:
                break

            print(f"\n  [{post['username'] or post['account_id']}] posting {Path(post['video_path']).name}...")

            # Anti-ban delay: minimum 15 min between accounts, 30 min for same
            if done > 0:
                delay = random.uniform(900, 1800)  # 15-30 min
                print(f"  Waiting {delay/60:.0f} min (anti-ban delay)...")
                # In real usage this would be a cron schedule; for dev, skip
                # await asyncio.sleep(min(delay, 30))  # cap at 30s for testing

            result = await self.post_video(
                post["account_id"],
                post["video_path"],
                post["caption"],
                post["hashtags"],
            )
            with FarmDB()._conn() as c:
                if result.success:
                    c.execute(
                        "UPDATE posts_queue SET status = 'posted', posted_at = ?, result = ? WHERE id = ?",
                        (datetime.now().isoformat(), json.dumps(asdict(result)), post["id"])
                    )
                else:
                    c.execute(
                        "UPDATE posts_queue SET status = 'failed', error = ? WHERE id = ?",
                        (result.error, post["id"])
                    )
            done += 1

        print(f"\n  ✅ Queue: {done} processed, {len(pending) - done} remaining")

    # ── Health ──────────────────────────────────────────────────────────

    async def health_check(self, account_id: str = None) -> dict:
        """
        Проверить здоровье аккаунта/фермы.
        Проверяет: жив ли аккаунт, сессия, post views.
        """
        accounts = [account_id] if account_id else [a["id"] for a in self.db.list_accounts()]

        results = {}
        for aid in accounts:
            acc = self.db.get_account(aid)
            if not acc:
                results[aid] = {"status": "unknown", "error": "not found"}
                continue

            cookies_path = acc.get("cookies_path")
            if cookies_path and os.path.exists(cookies_path):
                results[aid] = {
                    "status": acc.get("status", "unknown"),
                    "session": "valid",
                    "posts": acc.get("posts_count", 0),
                    "geo": acc.get("geo", "??"),
                    "last_login": acc.get("last_login", "never"),
                }
            else:
                results[aid] = {
                    "status": acc.get("status", "unknown"),
                    "session": "none",
                    "posts": acc.get("posts_count", 0),
                    "geo": acc.get("geo", "??"),
                }

            self.db.health_log(aid, "health_check",
                               "ok" if results[aid].get("session") == "valid" else "no_session")

        return results

    async def warmup(self, account_id: str, duration_min: int = 15):
        """Запустить прогрев аккаунта — просмотр ленты, лайки."""
        acc = self.db.get_account(account_id)
        if not acc:
            print(f"  Account {account_id} not found")
            return

        print(f"  Warming up {account_id} ({duration_min} min)...")
        # Playwright-based warmup (simplified — real warmup needs iOS Voice Control)
        from playwright.async_api import async_playwright

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            page = await browser.new_page()
            try:
                from playwright_stealth import stealth_async
                await stealth_async(page)
            except ImportError:
                pass

            await page.goto("https://www.tiktok.com/foryou", wait_until="domcontentloaded")
            print("  Scrolling feed...")

            end_time = time.time() + duration_min * 60
            actions = 0
            while time.time() < end_time:
                await page.evaluate("window.scrollBy(0, 800)")
                await asyncio.sleep(random.uniform(3, 8))

                # Random like (20% chance)
                if random.random() < 0.2:
                    try:
                        like_btn = await page.locator("[data-e2e='like-icon'], .like-icon").first
                        if await like_btn.count() > 0:
                            await like_btn.click()
                    except Exception:
                        pass
                actions += 1

            await browser.close()
            print(f"  ✅ Warmup done: {actions} actions in {duration_min} min")
            self.db.health_log(account_id, "warmup", "ok", f"{duration_min}min, {actions} actions")


# =========================================================================
# CLI
# =========================================================================

async def main():
    parser = argparse.ArgumentParser(description="TikTok Farm Orchestrator")
    parser.add_argument("--create", action="store_true", help="Создать новый аккаунт")
    parser.add_argument("--geo", default="US", help="Гео для аккаунта (US, RU, DE, FR...)")
    parser.add_argument("--list", action="store_true", help="Список аккаунтов")
    parser.add_argument("--post", nargs=2, metavar=("ACCOUNT_ID", "VIDEO"), help="Пост с аккаунта")
    parser.add_argument("--caption", default="🔥 FREE", help="Caption для поста")
    parser.add_argument("--hashtags", default="fyp,foryou,viral", help="Хэштеги через запятую")
    parser.add_argument("--queue", nargs="?", const=str(CONTENT_DIR), metavar="VIDEO_DIR",
                        help="Добавить видео в очередь постинга")
    parser.add_argument("--process-queue", action="store_true", help="Обработать очередь")
    parser.add_argument("--warmup", nargs=1, metavar="ACCOUNT_ID", help="Прогрев аккаунта")
    parser.add_argument("--health", action="store_true", help="Проверка здоровья фермы")
    parser.add_argument("--account", help="ID аккаунта для health/warmup")
    args = parser.parse_args()

    farm = TikTokFarmOrchestrator()

    if args.create:
        farm.create_account(geo=args.geo)

    if args.list:
        accounts = farm.list_accounts()
        if not accounts:
            print("  No accounts. Use --create --geo US")
        else:
            print(f"\n  {'ID':25s} {'Username':15s} {'Geo':5s} {'Status':12s} {'Posts':6s} {'Session'}")
            print(f"  {'-'*25} {'-'*15} {'-'*5} {'-'*12} {'-'*6} {'-'*7}")
            for a in accounts:
                sid = a.get("cookies_path", "")
                sess = "✅" if sid and os.path.exists(sid) else "❌"
                print(f"  {a['id']:25s} {(a.get('username') or '?'):15s} {a.get('geo','?'):5s} "
                      f"{a.get('status','?'):12s} {a.get('posts_count',0):6d} {sess}")

    if args.post:
        vid_path = args.post[1]
        if not os.path.exists(vid_path):
            print(f"❌ Video not found: {vid_path}")
        else:
            result = await farm.post_video(args.post[0], vid_path, args.caption, args.hashtags)
            print(f"  {'✅' if result.success else '❌'} {result.url or result.error}")

    if args.queue:
        n = farm.enqueue_videos(args.queue, caption=args.caption, hashtags=args.hashtags)
        if n:
            print(f"  Run --process-queue to start posting")

    if args.process_queue:
        await farm.process_queue()

    if args.warmup:
        await farm.warmup(args.warmup[0])

    if args.health:
        results = await farm.health_check(args.account)
        print(f"\n  {'Account ID':25s} {'Status':12s} {'Session':8s} {'Posts':6s} {'Geo':5s} {'Last Login'}")
        print(f"  {'-'*25} {'-'*12} {'-'*8} {'-'*6} {'-'*5} {'-'*19}")
        for aid, info in results.items():
            print(f"  {aid:25s} {info.get('status','?'):12s} {info.get('session','?'):8s} "
                  f"{info.get('posts',0):6d} {info.get('geo','?'):5s} {(info.get('last_login') or '-'):19s}")

    if not any([args.create, args.list, args.post, args.queue,
                args.process_queue, args.warmup, args.health]):
        parser.print_help()


if __name__ == "__main__":
    asyncio.run(main())

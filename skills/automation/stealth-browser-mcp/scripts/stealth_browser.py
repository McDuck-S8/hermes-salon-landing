"""Stealth Browser for Hermes — No Driver (nodriver)"""
import asyncio, sys
from pathlib import Path

try:
    import nodriver
except ImportError:
    print("pip install nodriver")
    sys.exit(1)

CHROME_PATH = "D:/Program Files/Google/Chrome/Application/chrome.exe"
PROXY = "http://127.0.0.1:10806"

async def browse(url, headless=True):
    """Open stealth browser, navigate to URL, return page text"""
    # IMPORTANT: browser_executable_path MUST be passed in Config() constructor,
    # NOT set after. Config.__init__ calls find_chrome_executable() immediately,
    # so setting config.browser_executable_path after init is too late.
    config = nodriver.Config(
        browser_executable_path=CHROME_PATH,
        headless=headless,
    )
    # Proxy must be passed via browser args, not config.proxy attribute
    config.add_argument(f'--proxy-server={PROXY}')
    
    browser = await nodriver.start(config)
    try:
        tab = await browser.get(url)
        await tab.wait(5)
        title = await tab.title()
        text = await tab.evaluate("document.body.innerText")
        return {"url": url, "title": title, "text": text or "", "success": True}
    finally:
        browser.stop()


async def browse_and_download_subs(url, output_dir):
    """Navigate to YouTube, extract transcript from page"""
    config = nodriver.Config(
        browser_executable_path=CHROME_PATH,
        headless=True,
    )
    config.add_argument(f'--proxy-server={PROXY}')
    
    browser = await nodriver.start(config)
    try:
        tab = await browser.get(url)
        await tab.wait(8)
        
        # Try to get transcript button
        transcript_btn = await tab.find("button[aria-label*='Show transcript']")
        if transcript_btn:
            await transcript_btn.click()
            await tab.wait(2)
            text = await tab.evaluate("""
                Array.from(document.querySelectorAll('[id^="seg"] span'))
                    .map(s => s.textContent).join('\\n')
            """)
            if text:
                Path(output_dir).mkdir(parents=True, exist_ok=True)
                vid = url.split("v=")[-1][:11]
                Path(f"{output_dir}/{vid}.txt").write_text(text, encoding='utf-8')
                return {"url": url, "transcript": text[:500], "success": True}
        
        return {"url": url, "error": "no transcript button", "success": False}
    finally:
        browser.stop()


if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else "https://httpbin.org/get"
    result = asyncio.run(browse(url, headless=True))
    print(f"URL: {result['url']}")
    print(f"Title: {result['title']}")
    print(f"Content: {result['text'][:500]}")

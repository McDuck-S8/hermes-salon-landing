"""Stealth Browser for Hermes — No Driver (nodriver)
Usage: python scripts/stealth_browser.py <url>
"""
import asyncio, sys

try:
    import nodriver
except ImportError:
    print("pip install nodriver")
    sys.exit(1)

CHROME_PATH = "D:/Program Files/Google/Chrome/Application/chrome.exe"
PROXY = "http://127.0.0.1:10806"

async def browse(url, headless=True):
    browser = await nodriver.start(
        headless=headless,
        browser_executable_path=CHROME_PATH,
    )
    try:
        tab = await browser.get(url)
        await tab.wait(3)
        title = tab.title
        text = await tab.evaluate("document.body.innerText")
        return {"url": url, "title": title, "text": text[:5000] if text else "", "success": True}
    finally:
        browser.stop()

if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else "https://httpbin.org/get"
    print(f"Stealth Browser → {url}")
    result = asyncio.run(browse(url, headless=True))
    print(f"Title: {result['title']}")
    print(f"Content:\n{result['text'][:500]}")

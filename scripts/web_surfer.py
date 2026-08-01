#!/usr/bin/env python3
"""
web_surfer.py — Антидетект-сёрфинг v4.
Три слоя:
  1. urllib + proxy (быстрое чтение, без JS)
  2. undetected-chromedriver (антидетект, полный Chrome)
  3. Playwright + stealth (альтернатива)

Использование:
    from web_surfer import WebSurfer
    ws = WebSurfer()
    r = ws.read_page("https://travelpayouts.com")       # urllib (быстро)
    r = ws.stealth_read("https://travelpayouts.com")     # undetected Chrome (невидимо)
    r = ws.stealth_interact("https://...", actions=[...]) # заполнить форму
    ws.close()
"""
import os
import sys
import re
import time
import json
import random
import urllib.request
from pathlib import Path

PROXY = "http://127.0.0.1:10809"
CHROME_PATH = r"C:\Users\Asus\AppData\Local\ms-playwright\chromium-1223\chrome-win64\chrome.exe"
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
]


def _human_delay(min_s=0.5, max_s=2.0):
    time.sleep(random.uniform(min_s, max_s))


def _human_type_delay():
    time.sleep(random.uniform(0.03, 0.12))


class WebSurfer:
    def __init__(self, proxy=PROXY, headless=True):
        self.proxy = proxy
        self.headless = headless
        self.opener = urllib.request.build_opener(
            urllib.request.ProxyHandler({'http': proxy, 'https': proxy})
        )
        self._uc_driver = None

    # ===== LAYER 1: urllib (быстрое чтение) =====

    def read_page(self, url, max_chars=50000):
        try:
            ua = random.choice(USER_AGENTS)
            req = urllib.request.Request(url, headers={
                'User-Agent': ua,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9,ru;q=0.8',
                'Accept-Encoding': 'identity',
                'Connection': 'keep-alive',
            })
            resp = self.opener.open(req, timeout=15)
            html = resp.read().decode('utf-8', errors='replace')
            title_m = re.search(r'<title[^>]*>(.*?)</title>', html, re.IGNORECASE | re.DOTALL)
            title = title_m.group(1).strip() if title_m else ""
            desc_m = re.search(r'name=["\']description["\']\s+content=["\']([^"\']+)', html, re.IGNORECASE)
            description = desc_m.group(1) if desc_m else ""
            text = self._clean_html(html)
            if len(text) > max_chars:
                text = text[:max_chars] + "\n... [truncated]"
            return {"url": url, "title": title, "description": description, "content": text, "length": len(text), "engine": "urllib"}
        except Exception as e:
            return {"url": url, "error": str(e), "engine": "urllib"}

    def _clean_html(self, html):
        text = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r'<[^>]+>', '\n', text)
        for entity, char in [('&nbsp;', ' '), ('&amp;', '&'), ('&lt;', '<'), ('&gt;', '>'), ('&quot;', '"')]:
            text = text.replace(entity, char)
        text = re.sub(r'&#\d+;', '', text)
        text = re.sub(r'\n{3,}', '\n\n', text)
        text = re.sub(r'[ \t]+', ' ', text)
        lines = [l.strip() for l in text.split('\n') if l.strip()]
        return '\n'.join(lines)

    # ===== LAYER 2: undetected-chromedriver (антидетект) =====

    def _get_uc_driver(self):
        if self._uc_driver is not None:
            return self._uc_driver
        import undetected_chromedriver as uc
        options = uc.ChromeOptions()
        if self.headless:
            options.add_argument('--headless=new')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        options.add_argument(f'--lang=en-US')
        if self.proxy:
            options.add_argument(f'--proxy-server={self.proxy}')
        self._uc_driver = uc.Chrome(
            options=options,
            browser_executable_path=CHROME_PATH,
            version_main=147,
        )
        self._uc_driver.set_page_load_timeout(30)
        return self._uc_driver

    def stealth_read(self, url, max_chars=50000):
        try:
            driver = self._get_uc_driver()
            driver.get(url)
            _human_delay(1, 3)
            title = driver.title
            body = driver.find_element("tag name", "body")
            text = body.text
            webdriver_check = driver.execute_script("return navigator.webdriver")
            if len(text) > max_chars:
                text = text[:max_chars] + "\n... [truncated]"
            return {
                "url": url,
                "title": title,
                "content": text,
                "length": len(text),
                "webdriver": webdriver_check,
                "engine": "undetected-chromedriver",
                "stealth_ok": webdriver_check is None or webdriver_check is False,
            }
        except Exception as e:
            return {"url": url, "error": str(e), "engine": "undetected-chromedriver"}

    def stealth_interact(self, url, actions):
        """
        actions = [
            {"type": "click", "selector": "button.submit"},
            {"type": "type", "selector": "input[name=q]", "text": "hello"},
            {"type": "slow_type", "selector": "input[name=q]", "text": "hello"},
            {"type": "wait", "seconds": 2},
            {"type": "scroll", "direction": "down", "amount": 3},
            {"type": "eval", "expression": "return document.title"},
            {"type": "extract", "selector": "div.content"},
        ]
        """
        try:
            driver = self._get_uc_driver()
            driver.get(url)
            _human_delay(1, 3)
            results = []
            for action in actions:
                try:
                    if action["type"] == "click":
                        _human_delay(0.3, 1.0)
                        from selenium.webdriver.common.by import By
                        el = driver.find_element(By.CSS_SELECTOR, action["selector"])
                        driver.execute_script("arguments[0].scrollIntoView(true);", el)
                        _human_delay(0.2, 0.5)
                        el.click()
                        results.append({"action": "click", "ok": True})
                    elif action["type"] == "type":
                        from selenium.webdriver.common.by import By
                        el = driver.find_element(By.CSS_SELECTOR, action["selector"])
                        el.clear()
                        el.send_keys(action["text"])
                        _human_delay(0.5, 1.0)
                        results.append({"action": "type", "ok": True})
                    elif action["type"] == "slow_type":
                        from selenium.webdriver.common.by import By
                        el = driver.find_element(By.CSS_SELECTOR, action["selector"])
                        el.clear()
                        for char in action["text"]:
                            el.send_keys(char)
                            _human_type_delay()
                        _human_delay(0.3, 0.8)
                        results.append({"action": "slow_type", "ok": True})
                    elif action["type"] == "wait":
                        time.sleep(action.get("seconds", 1))
                        results.append({"action": "wait", "ok": True})
                    elif action["type"] == "scroll":
                        amount = action.get("amount", 3)
                        direction = action.get("direction", "down")
                        if direction == "down":
                            driver.execute_script(f"window.scrollBy(0, window.innerHeight * {amount});")
                        else:
                            driver.execute_script(f"window.scrollBy(0, -window.innerHeight * {amount});")
                        _human_delay(0.5, 1.5)
                        results.append({"action": "scroll", "ok": True})
                    elif action["type"] == "eval":
                        val = driver.execute_script(action["expression"])
                        results.append({"action": "eval", "result": str(val)[:5000]})
                    elif action["type"] == "extract":
                        from selenium.webdriver.common.by import By
                        el = driver.find_element(By.CSS_SELECTOR, action["selector"])
                        results.append({"action": "extract", "text": el.text[:5000]})
                except Exception as e:
                    results.append({"action": action["type"], "error": str(e)[:200]})
            body = driver.find_element("tag name", "body")
            webdriver_check = driver.execute_script("return navigator.webdriver")
            return {
                "url": url,
                "title": driver.title,
                "actions": results,
                "page_text": body.text[:10000],
                "webdriver": webdriver_check,
                "stealth_ok": webdriver_check is None or webdriver_check is False,
                "engine": "undetected-chromedriver",
            }
        except Exception as e:
            return {"url": url, "error": str(e), "engine": "undetected-chromedriver"}

    def stealth_check(self, url="https://abrahamjuliot.github.io/creepjs/"):
        """Запустить тест на обнаружение (CreepJS)."""
        result = self.stealth_read(url)
        return result

    # ===== UTILS =====

    def get_ip(self):
        try:
            return self.read_page("https://httpbin.org/ip", max_chars=200).get("content", "unknown")
        except:
            return "unknown"

    def close(self):
        if self._uc_driver:
            try:
                self._uc_driver.quit()
            except:
                pass
            self._uc_driver = None


if __name__ == "__main__":
    print("=== WebSurfer v4 — Anti-Detect ===")
    ws = WebSurfer(headless=True)
    print("IP:", ws.get_ip()[:100])
    print()
    print("Stealth test on Travelpayouts...")
    r = ws.stealth_read("https://www.travelpayouts.com/")
    print("Title:", r.get("title", "?")[:80])
    print("Content length:", r.get("length", 0))
    print("webdriver:", r.get("webdriver"))
    print("stealth_ok:", r.get("stealth_ok"))
    print("First 500 chars:", r.get("content", "")[:500])
    ws.close()
    print("=== Done ===")

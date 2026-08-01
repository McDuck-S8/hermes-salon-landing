# Windows Python Debugging Gotchas

## .pyc Cache Serves Stale Bytecode
**Problem**: Source file is modified, but Python runs the old code.
**Symptom**: `inspect.getsource()` shows correct code, but runtime behavior is wrong.
**Fix**: Delete `__pycache__` directory: `rm -rf scripts/crystal/__pycache__`
**Why**: Windows Python caches `.pyc` files aggressively. On file edit, the `.pyc` may not invalidate.

## Chinese Characters in Python on Windows
**Problem**: Using Chinese chars (提案, 提议, etc.) in Python files causes:
- Encoding errors in CLI output
- Issues with `grep`/`findstr` on Windows
- Log corruption when written to `.log` files
**Fix**: Use ASCII or Russian only in all code, docstrings, comments, and CLI output.
**Pattern**: After any code generation, run: `grep -rn "[\\u4e00-\\u9fff]" *.py` to verify clean.

## save_json Argument Order
**Problem**: `save_json(path, data)` vs `save_json(data, path)` — different libraries use different orders.
**Fix**: Always check the function signature before calling. In Crystal models.py: `save_json(data, path: str)`.
**Symptom**: `TypeError: expected str, bytes or os.PathLike object, not list`

## Terminal Timeout on Windows
**Problem**: Commands that work on Linux timeout on Windows.
**Common causes**: Large file scans, slow `git` operations, Python startup overhead.
**Fix**: Use `timeout=N` parameter generously. For Crystal: avoid reading all sessions in one go.

## Windows SSL Blocks Python HTTPS (2026-07-09)
**Problem**: `httpx`, `requests`, `aiohttp` all fail with SSL handshake errors on outbound HTTPS from Windows Python.
**Symptom**: `ssl.SSLError: [SSL: UNEXPECTED_EOF_WHILE_READING]` or `ProxyError: The handshake operation timed out`
**Workaround**: Use `httpx.Client(verify=False, proxy=None)` for outbound calls.
**Why**: Windows Python's SSL context conflicts with system proxy settings. Disabling verification + proxy bypasses both.
**Pattern**: All LLM API calls in Hermes use this transport:
```python
import httpx
client = httpx.Client(verify=False, proxy=None, timeout=60)
r = client.post(url, headers=headers, json=payload)
```

## Windows Playwright Symlink Fix (2026-07-09)
**Problem**: `playwright install chromium` fails with SSL errors on Windows (proxy/firewall blocks `models.datalab.to`). Crawl4AI and other Playwright-based tools crash with `Executable doesn't exist at .../chromium_headless_shell-NNN/...`.
**Root cause**: Playwright expects a specific chromium build number (e.g. 1228) but only an older one (e.g. 1223) is installed. The download fails due to SSL.
**Fix**: Create a directory symlink from the expected version to the existing one:
```bash
# Check what's installed
ls /c/Users/Asus/AppData/Local/ms-playwright/ | grep chromium

# Symlink expected → existing (use cmd.exe for Windows symlinks)
cmd.exe /c "mklink /D \"C:\Users\Asus\AppData\Local\ms-playwright\chromium_headless_shell-1228\" \"C:\Users\Asus\AppData\Local\ms-playwright\chromium_headless_shell-1223\""
```
**Why it works**: Playwright just checks the directory exists and finds the binary. The API is backward-compatible within major versions.
**Pitfall**: After `pip install --upgrade crawl4ai` or `playwright`, the expected version number changes. Re-check and re-symlink.

## PyMuPDF Fallback for PDF Extraction (2026-07-09)
**Problem**: `marker-pdf` needs surya OCR models (~2GB) from `models.datalab.to`. On Windows with SSL issues, the download fails with `SSLEOFError`.
**Fallback**: Use `PyMuPDF` (installed with marker-pdf as `fitz`) for text-only extraction:
```python
import fitz
doc = fitz.open(pdf_path)
text = "\n".join(page.get_text() for page in doc)
doc.close()
```
**Trade-off**: PyMuPDF extracts text only (no OCR, no layout, no tables). For scanned images, Marker is required — fix the SSL issue first.
**Pattern**: Always provide a fallback when a library depends on model downloads. The `doc_intake.py` script implements this: try Marker → fallback to PyMuPDF.

## LLM Tracing Integration Pattern (2026-07-09)
**Problem**: Adding observability to existing LLM clients without circular imports or breaking changes.
**Solution**: Lazy-import tracer module, context manager pattern:
```python
# In llm_client.py
_tracer = None
def _get_tracer():
    global _tracer
    if _tracer is None:
        try:
            from scripts.llm_tracer import trace_llm, flush
            _tracer = {"trace_llm": trace_llm, "flush": flush}
        except Exception:
            _tracer = False
    return _tracer if _tracer else None

# Usage in call_llm:
tracer = _get_tracer()
if tracer:
    with tracer["trace_llm"](provider, model, "call_llm") as ctx:
        ctx["data"]["prompt_preview"] = prompt[:200]
        result = _raw_completion(...)
        ctx["data"]["response_preview"] = (result or "")[:200]
```
**Key details**:
- `llm_tracer.py` logs to `cache/llm_traces.jsonl` (local, always works)
- Optional Langfuse cloud if `LANGFUSE_SECRET_KEY` is set in `.env`
- Context manager captures: provider, model, duration, tokens, success/error
- CLI: `python llm_tracer.py --stats` / `--recent N`

## Crawl4AI Sync Wrapper Pattern (2026-07-09)
**Problem**: Crawl4AI is async (`AsyncWebCrawler`), but signal_scanner.py and other scripts are sync.
**Solution**: Wrap async calls with `asyncio.run()`:
```python
import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, BrowserConfig

def crawl4ai_scrape(url: str, timeout: int = 30) -> str:
    browser_config = BrowserConfig(headless=True)
    run_config = CrawlerRunConfig(wait_until="domcontentloaded")

    async def _scrape():
        async with AsyncWebCrawler(config=browser_config) as crawler:
            result = await crawler.arun(url=url, config=run_config)
            if result.success:
                md = result.markdown
                return md.raw_markdown if hasattr(md, 'raw_markdown') else str(md)
            return ""

    return asyncio.run(_scrape())
```
**Pitfall**: Crawl4AI 0.9+ removed `markdown_v2` attribute. Use `result.markdown` (returns `MarkdownGenerationResult` with `.raw_markdown`).
**Pitfall**: Each `asyncio.run()` creates a new event loop. Don't call from within an existing async context — use `await` directly instead.

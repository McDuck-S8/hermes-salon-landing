# YouTube Pipeline Patterns — Reference for Browser Automation Toolkit

## YouTube Pipeline Class Usage

```python
from scripts.youtube_pipeline import YouTubePipeline

pipeline = YouTubePipeline(proxy="socks5://127.0.0.1:10806")
result = pipeline.process_video("https://www.youtube.com/watch?v=VIDEO_ID", lang="en,ru")
# Returns: title, description, channel, views, subtitles, auto_captions, etc.
```

## Integration with Browser Automation Toolkit

| Engine | Port | When to Use |
|---|---|---|
| **browser-automation** (BrowserClaw MCP 9010) | Standard automation, form filling | YouTube metadata via oEmbed/HTML |
| **ghost-surfer** (Playwright + stealth) | Anti-detect for protected pages | YouTube HTML proxy when blocked |
| **browser-harness** (CDP 9222) | YOUR logged-in Chrome | Authenticated YouTube (your cookies) |
| **browseros** (MCP 9003) | 66+ tools, file upload, JS eval | Complex YouTube interactions |

## Key yt-dlp-rescue Arguments

```bash
# Player clients (most reliable first)
--extractor-args "youtube:player_client=tv,web_embedded,android_vr,tv_downgraded,web_creator,mweb"
--extractor-args "youtube:player_skip=webpage"

# Network
--force-ipv4
--proxy socks5://127.0.0.1:10806

# PO Token (if available)
--extractor-args "youtube:pot_provider_url=http://localhost:4416"
```

## Player Client Priority (Most Reliable First)

1. **tv** - Most reliable, full DASH, no token needed
2. **web_embedded** - Embedded player, full DASH
3. **android_vr** - VR client, full DASH
4. **tv_downgraded** - Downgraded TV, full DASH
5. **web_creator** - YouTube Studio client
6. **mweb** - Mobile web

## Anti-Bot Handling

| Error | Solution |
|---|---|
| "Sign in to confirm you're not a bot" | Use cookies from browser (`--cookies-from-browser chrome`) |
| SSL EOF errors | Retry with different player client |
| PO Token required | Set `YT_DLP_POT_PROVIDER_URL` env var |

## Anti-Patterns (from 96 browser entries, 57 failures = 59% failure rate)

| Anti-Pattern | Guard |
|---|---|
| Using wrong engine for auth | **Decision matrix**: auth → browser-harness |
| No stealth on protected sites | **ghost-surfer** mandatory for Cloudflare/Akamai |
| Single engine for all tasks | **Multi-engine workflow**: recon → choose → execute |
| Element refs stale | **Re-snapshot after EVERY navigation** |
| No error handling | **safe_mcp_call** with retries + backoff |
| Cookie/session not persisted | **browser-harness** uses YOUR Chrome profile |
| Vision fallback missing | **browseros** has vision_analyze tool |

## Verification Checklist

- [ ] Correct engine chosen per decision matrix
- [ ] MCP servers running (BrowserClaw 9010, BrowserOS 9003)
- [ ] browser-harness daemon connected to YOUR Chrome (9222)
- [ ] Re-snapshot after every navigation
- [ ] Data extracted via read/extract_content
- [ ] Screenshots/PDFs saved for evidence
- [ ] on_task_complete() logged to KC with tags
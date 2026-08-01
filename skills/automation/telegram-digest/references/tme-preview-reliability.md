# t.me/s/ Preview Page Reliability — Tested 2026-06-27

## Status per Channel

| Channel | Status | Method | Notes |
|---------|--------|--------|-------|
| `t.me/s/openai` | FAIL | browser_navigate + web_extract | Timeout on both |
| `t.me/s/hugging_face` | FAIL | web_extract | Server disconnect |
| `t.me/s/anthropic` | WRONG | web_extract | Redirects to "Discover • Tech News" (Perplexity bot) |
| `t.me/s/deepseek` | OK (limited) | web_extract | Only 1 post visible, channel has 13.3K subs |
| `t.me/s/GoogleAI` | OK (minimal) | web_extract | Branded content, SVG logos, no real posts |

## Why It Fails

- t.me/s/ is Telegram's web preview — not a real API
- Rate-limited, especially from non-browser clients
- Some channels block web preview entirely
- Redirects happen when channel slug collides with bot names

## Reliable Alternative: Web Search + Official Pages

```python
# Per company, search for recent news
web_search_plus(
    query=f"{company_name} latest news {month} {year}",
    time_range="week"
)

# Extract from official newsroom
web_extract(urls=[f"{company}.com/news"])
```

### Tested Official Pages (reliable)

| Page | Status | Content |
|------|--------|---------|
| `openai.com/news/` | OK | Full listing with dates, categories |
| `anthropic.com/news` | OK | Full listing, model releases, partnerships |
| HuggingFace blog | OK | State of OS reports, security advisories |

## Report Format

Save reports to: `cache/telegram_monitor/latest_report.md`

Report structure:
1. Header with date and sources
2. Top 10 news items (title, date, link, 2-line summary)
3. Top 5 most interesting posts with links
4. Recommendations (what to try, study, use)
5. Monitoring errors (what failed and why)
6. Next steps

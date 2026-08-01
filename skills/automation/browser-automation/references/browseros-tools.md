# BrowserOS MCP Tools Reference (66 tools)

Full list from `tools/list` on http://127.0.0.1:9003/mcp

## Page Management (9)
| Tool | Description |
|---|---|
| `new_page` | Open a new page (tab) and navigate to a URL. Opens in background by default. |
| `new_hidden_page` | Open a new hidden page (tab) and navigate to a URL. Hidden pages are not visible. |
| `list_pages` | List all pages (tabs) currently open in the browser. |
| `get_active_page` | Get the currently active (focused) page in the browser. |
| `show_page` | Restore a hidden page back into a visible browser window. |
| `move_page` | Move a page (tab) to a different window or position within a window. |
| `close_page` | Close a page (tab). |
| `navigate_page` | Navigate a page: load a URL, or go back/forward/reload. |
| `wait` | Pause before continuing. For="time" (default), "text", or "selector". |

## Content Extraction (7)
| Tool | Description |
|---|---|
| `take_snapshot` | Capture the page as an indented accessibility tree. Each actionable element carries a stable [ref=eN]. |
| `take_enhanced_snapshot` | Detailed accessibility tree with structural context (headings, landmarks, etc.). |
| `extract_content` | Extract page content as markdown (default), plain text, or a list of links. |
| `grep` | Search the page without dumping it. over="ax" greps snapshot lines; over="content" greps visible text. |
| `evaluate_script` | Evaluate JavaScript in a page context through CDP Runtime.evaluate. |
| `search_dom` | Find DOM nodes by query selector. |
| `read` | Alias for extract_content. |

## Interaction (8)
| Tool | Description |
|---|---|
| `click` | Click an element by ref. |
| `fill` | Fill one field via ref+value, or many via fields[]. |
| `upload` | Set local file path(s) on a file input using a ref. |
| `press` | Press a key/combo (e.g., "Enter", "Control+a"). |
| `hover` | Hover over an element by ref. |
| `focus` | Focus an element by ref. |
| `select` | Select an option value in a select element. |
| `scroll` | Scroll the page in a direction. |

## Visual (4)
| Tool | Description |
|---|---|
| `take_screenshot` | Capture a screenshot of the page (JPEG/PNG/WebP). |
| `pdf` | Print the page to a PDF and save it. |
| `screenshot` | Alias for take_screenshot. |
| `download` | Click an element to trigger a file download, save to BrowserOS output file. |

## Tab/Window Groups (4)
| Tool | Description |
|---|---|
| `tab_groups` | Manage tab groups: list, create, update, ungroup, close. |
| `windows` | Manage browser windows: list, create, close, activate, set_visibility. |
| `tabs` | Alias for list_pages / new_page / close_page. |
| `new_page` | Alias for creating new tabs. |

## CDP Escape Hatch (2)
| Tool | Description |
|---|---|
| `cdp` | Raw CDP escape hatch: method, params?, sessionId?. |
| `cdp_json_for_page` | Page-scoped raw CDP with validated JSON params. |

## Page Targeting
All tools require `page` parameter (page ID from `list_pages` or `new_page`).
Refs (eN) come from a snapshot's text/refs. Re-snapshot after navigation or large changes.

## Example: Full CPA Offer Scraping Flow

```python
# 1. New page to AdCombo offers
page_result = await mcp__browseros__new_page(url="https://www.adcombo.com/offers")
page = page_result["page"]

# 2. Wait for load
await mcp__browseros__wait(page=page, for="time", value=3000)

# 3. Snapshot for refs
snapshot = await mcp__browseros__take_snapshot(page=page)

# 4. Find and click GEO filter -> India
# (parse snapshot for ref of GEO filter dropdown, then India option)
await mcp__browseros__click(page=page, ref=ref_geo_dropdown)
await mcp__browseros__click(page=page, ref=ref_india_option)

# 5. Find and click Vertical filter -> Gambling
await mcp__browseros__click(page=page, ref=ref_vertical_dropdown)
await mcp__browseros__click(page=page, ref=ref_gambling_option)

# 6. Wait for results
await mcp__browseros__wait(page=page, for="time", value=2000)

# 7. Extract offers via JS
offers = await mcp__browseros__evaluate_script(page=page, script="""
  return Array.from(document.querySelectorAll('.offer-card, .offer-row, [data-offer-id]')).map(c => ({
    id: c.dataset.offerId || c.querySelector('[data-offer-id]')?.dataset.offerId,
    name: c.querySelector('.offer-name, .offer-title, h3, h4')?.textContent?.trim(),
    payout: c.querySelector('.payout, .price, [data-payout]')?.textContent?.trim(),
    cap: c.querySelector('.cap, .daily-cap, [data-cap]')?.textContent?.trim(),
    flow: c.querySelector('.flow, .conversion-flow, [data-flow]')?.textContent?.trim(),
    lander: c.querySelector('a.lander, a[href*="land"], a[href*="preview"]')?.href,
    geo: c.querySelector('.geo, .country, [data-geo]')?.textContent?.trim(),
    vertical: c.querySelector('.vertical, .category, [data-vertical]')?.textContent?.trim()
  })).filter(o => o.name)
""")

# 8. For each offer, open lander and extract preview
for offer in offers[:10]:
    if offer.lander:
        lander_page = await mcp__browseros__new_page(url=offer.lander)
        await mcp__browseros__wait(page=lander_page, for="time", value=2000)
        await mcp__browseros__take_screenshot(page=lander_page, fullPage=True, path=f"lander_{offer.id}.png")
        await mcp__browseros__close_page(page=lander_page)

# 9. Close main page
await mcp__browseros__close_page(page=page)
```

## Key Differences from BrowserClaw

| Feature | BrowserClaw | BrowserOS |
|---|---|---|
| Tools | 16 | 66 |
| File upload | `upload` (limited) | `upload_file` (full) |
| JS evaluation | `evaluate` | `evaluate_script` |
| Snapshot detail | Basic | Enhanced (`take_enhanced_snapshot`) |
| Page management | `tabs` | `list_pages`, `new_page`, `move_page`, `show_page` |
| Window management | — | `windows` |
| Tab groups | — | `tab_groups` |
| CDP raw access | — | `cdp`, `cdp_json_for_page` |
| Vision analysis | — | External fallback (chat.deepseek.com) |
| Download handling | `download` | `download` |

## When to Use BrowserOS (Port 9003)

1. **File uploads to web forms** — `upload_file` works reliably
2. **Complex JS extraction** — `evaluate_script` with full CDP access
3. **Multi-tab workflows** — `list_pages`, `move_page`, `tab_groups`
4. **Window management** — `windows` for multi-window automation
5. **Enhanced snapshots** — `take_enhanced_snapshot` for complex DOM
5. **CDP escape hatch** — Raw CDP calls when tools don't suffice
6. **Vision fallback** — Screenshot → external vision model when local fails

## When to Use BrowserClaw (Port 9010)

1. **Standard form filling** — `act` with fill/click/press
2. **Simple navigation + extraction** — `navigate` + `read`
3. **Quick screenshots** — `screenshot`
4. **Tab management** — `tabs` list/create/close
5. **PDF generation** — `pdf`
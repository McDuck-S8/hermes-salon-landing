# Vision Agent Screenshot Protocol — 2026-07-18

## Problem
User provided a detailed vision-agent screenshot description to fix landing page issues:
- Logo missing in nav
- Hero headline cut off at top
- Wrong nav structure (5 items + 2 buttons vs 3 items + 1 button)
- Master photos were emoji, not images

## Protocol: When User Provides Screenshot Description

1. **Parse the description** — extract specific visual defects:
   - Element positions (left/center/right)
   - Missing elements (logo)
   - Cutoff/clipping (hero headline)
   - Wrong structure (nav item count)

2. **Map to code** — find the HTML/CSS responsible:
   - Logo → `.nav-logo` color + shadow
   - Hero cutoff → `.hero` padding-top
   - Nav structure → `<ul class="nav-links">` item count
   - Master photos → `.master-photo` img tags

3. **Fix synchronously** — apply all fixes in one deploy cycle:
   - CSS for visual issues
   - HTML for structural issues
   - Both for hybrid issues

4. **Verify via curl** — don't just trust local file:
   ```bash
   curl -s "https://mcduck-s8.github.io/hermes-salon-landing/portfolio/beauty-salon/" | grep -A 15 '<nav id="nav">'
   ```

5. **Confirm with user** — they must be able to open the link and see it work.

## Applied This Session
| Screenshot Issue | Code Fix |
|-----------------|----------|
| "Логотип отсутствует" | `.nav-logo { color: var(--gold); text-shadow: 0 2px 8px rgba(0,0,0,0.5); }` |
| "Заголовок обрезан сверху" | `.hero { padding: 160px 40px 80px; }` (was 120px) |
| "5 пунктов в центре + 2 кнопки справа" | Restored 5 nav links + added `.nav-actions` with 2 buttons |
| "Эмодзи вместо фото" | `<img src="placeholder.com/...">` + fallback `<span class="placeholder">👩‍🦰</span>` |

## Template for Future
When user says "вот описание скриншота для агента...":
1. Read description carefully
2. Create checklist of visual defects
3. Fix each in code
4. Deploy + curl verify
5. Report live URL

## Pitfall
**Don't trust local file** — GitHub Pages CDN caches. Always curl the live URL after deploy and wait 1-2 min if needed.
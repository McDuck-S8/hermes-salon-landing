# 13 Lessons from Fargo+Cosmetologist Project (2026-07-22)

## File Path
1. **Read the ACTUAL file path from user's URL** — not the one you assume. User may be viewing index.trend.html while you edit index.html.

## Content
2. **Never remove content without asking** — "if it was there, there was a reason." Fix broken links, don't delete them.
3. **No duplicate sections** — services WITH inline prices ≠ separate price section. Choose one.
4. **Verify photos visually** before inserting — open Pexels/Telegram URL and check what image actually shows.
5. **Carousel: 3 visible + seamless loop** — min-width:33.333%, cloneNode + transitionend for infinite scrolling.

## WCAG
6. **WCAG from the first commit** — skip-link, focus-visible, aria-hidden on emoji, for/id on forms, role=banner/main/contentinfo. Don't add in round 2.

## UI
7. **Header CTA button must pop** — emoji + box-shadow + font-weight:600. Must not blend into background.
8. **Contacts: minimum duplicates** — one handle + one button. No triple redundancy.
9. **Menu order = section order** — nav links 1:1 with page sections.

## Process
10. **Quality Gate before presenting** — always run qa_check.py before saying "done".
11. **Delegate, don't code** — you're first mate, not coder. task → subagent → QA → show.
12. **.nojekyll on gh-pages deploy** — without it GitHub Pages returns 404 for new directories.
13. **Use installed tools** — notebooklm-py was installed but never used. Research = notebooklm or web_search via delegate.

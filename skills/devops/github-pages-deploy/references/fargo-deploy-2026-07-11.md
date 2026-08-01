# Fargo Salon Deploy Session (2026-07-11)

## Context
- **Client**: Fargo Salon (Kyiv, Ukraine)
- **Source**: `demos/fargo/index.html`
- **Deploy target**: `docs/fargo/index.html`
- **Pages source**: `user/hermes-session-2026-06-09` branch, `/docs` folder

## What Happened

### Mistake 1: Created gh-pages branch unnecessarily
I ran `git checkout --orphan gh-pages` and force-pushed, thinking Pages served from there. Actually Pages was configured on `user/hermes-session-2026-06-09/docs`.

**Lesson**: Always check `gh api repos/$OWNER/$REPO/pages` first.

### Mistake 2: Gave wrong URL type
User asked "ссылку даёшь" — wanted a LIVE site URL, not a GitHub code URL. Then "это ссылка на код. а где на рабочий сайт?" — got angry.

**Lesson**: Live URL format: `https://owner.github.io/repo/<subpath>/` — code URL: `https://github.com/owner/repo/blob/branch/path`. User always wants the former.

### Mistake 3: Overwrote the old site initially
First gh-pages push replaced the old landing with the new Fargo site. User: "ты не затирай тот первый сайт".

**Lesson**: Multi-client = subdirectories under the same Pages source. Don't replace root `index.html`.

## Correct Deploy Sequence (From This Session)

```bash
# 1. Check current Pages config
gh api repos/McDuck-S8/hermes-salon-landing/pages
# → branch: user/hermes-session-2026-06-09, path: /docs

# 2. Add new client to the correct branch/path
mkdir -p docs/fargo
cp demos/fargo/index.html docs/fargo/index.html

# 3. Commit to the WORKING branch (not gh-pages)
git add docs/fargo/
git commit -m "docs: add fargo salon subpage"
git push origin user/hermes-session-2026-06-09

# 4. Wait for Pages rebuild (30-60s)
sleep 30

# 5. Verify
curl -sI "https://mcduck-s8.github.io/hermes-salon-landing/fargo/index.html"
# → 200 OK
```

## URLs After This Session
- Main site: https://mcduck-s8.github.io/hermes-salon-landing/ (old landing)
- Fargo: https://mcduck-s8.github.io/hermes-salon-landing/fargo/index.html

## File Structure
```
docs/
  index.html              ← old salon landing (stays as main page)
  fargo/index.html        ← new Fargo (client 2)
demos/
  fargo/index.html        ← source file for Fargo
  old-salon/index.html    ← backup of old landing
```

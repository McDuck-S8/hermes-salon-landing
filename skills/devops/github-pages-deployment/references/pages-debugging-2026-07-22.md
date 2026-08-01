# GitHub Pages Debugging — 2026-07-22 Session

## Problem
`https://mcduck-s8.github.io/hermes-salon-landing/cosmetologist/` returned 404 for ~2 hours despite:
- Files existing in `cosmetologist/` directory on default branch `user/hermes-session-2026-06-09`
- Files also existing on `gh-pages` branch
- Other paths (`/fargo/`, `/old-salon/`) working

## Root Cause
GitHub Pages configuration had `source.path: "/docs"` but files were in repository root `/`.

```json
{
  "source": {
    "branch": "user/hermes-session-2026-06-09",
    "path": "/docs"  // WRONG - files in root
  }
}
```

## Fix Applied
```bash
# Check config
gh api /repos/McDuck-S8/hermes-salon-landing/pages

# Fix source.path
gh api --method PUT /repos/McDuck-S8/hermes-salon-landing/pages \
  -f source[branch]=user/hermes-session-2026-06-09 \
  -f source[path]=/

# Trigger rebuild
gh api --method POST /repos/McDuck-S8/hermes-salon-landing/pages/builds
```

## Result
- Build queued immediately
- ~30 seconds later: `HTTP/2 200` for `/cosmetologist/`
- Content served correctly

## Key Lesson
**Never assume Pages config.** Always verify `source.path` matches actual file location. Default branch ≠ Pages branch. Files in root ≠ source.path=/docs.

## Files Involved
- `/cosmetologist/index.html` (32KB)
- `/cosmetologist/assets/` (images)
- `.nojekyll` in root (already present)
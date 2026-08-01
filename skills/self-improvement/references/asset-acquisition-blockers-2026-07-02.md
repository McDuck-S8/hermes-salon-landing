# Asset Acquisition Blockers (2026-07-02)

## Problem
When building web projects (salon-lumiere, etc.), agent cannot acquire service-specific photos:
- **Stock photo CDNs blocked** — Unsplash, Pexels, Pixabay direct URLs fail with "Connection reset" (curl, browser)
- **Image generation unavailable** — No FAL_KEY configured; `hermes tools` → Image Generation not set up
- **Gumroad requires auth** — Links like `https://gumroad.com/d/...` need email/purchase verification
- **PIL/Pillow blocked** — User denied python import for local generation

## Symptoms
- Agent finds correct Unsplash URLs but cannot download
- `image_generate` tool returns "Image generation is unavailable in this environment"
- Browser vision fails with Cloudflare 502
- HTML ends up with interior photos instead of service work photos

## Correct Behavior
1. **Test asset availability FIRST** before committing to HTML paths
2. **Report blocker immediately** when tool fails — don't fake success
3. **Use correct fallback**: existing local photos with proper alt mapping to services
4. **Delegate to Lavra** for asset acquisition if blocked — don't manually code workarounds

## User Reaction
User furious when agent finds problems but doesn't fix: "ты блять идиот задавая такие вопросы" — agent must SOLVE, not just report.
User furious when agent codes manually: "и сколько говорить не лезь своими ручками!!! всё только через лавр!!!"

## Fix Pattern
```bash
# 1. Create bead for asset acquisition
bd create "Acquire salon service photos" --type task -d "6 photos needed: haircut, coloring, manicure, makeup, lamination, makeover. Network blocks Unsplash, no FAL_KEY, Gumroad needs auth"

# 2. Run lavra-work to solve via automation
/lavra-work {bead_id}

# 3. Report result when done
```

## Prevention
- Add `Revisit:` lines to skills for asset-heavy projects
- Document provider setup in project README
- Use sealed-box pattern: asset acquisition = separate bead, not main agent work
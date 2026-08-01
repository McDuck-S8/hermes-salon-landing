# Free Image/Video Generation APIs

Discovered 2026-07-15. Updated on new findings.

## Pollinations.ai (VERIFIED — WORKS)

- GET endpoint: `https://image.pollinations.ai/prompt/{prompt}?...`
- No API key, no signup, no rate limit
- Models: flux (default), seedream, turbo, nanobanana
- Params: width, height, seed, model, nologo, safe
- Returns: JPEG binary directly
- Video/audio/text also available via POST at `gen.pollinations.ai`
- Full skill: `pollinations-ai-free-api`
- Session test results: `references/session-test-results-2026-07-15.md` in pollinations-ai-free-api skill

## AI Horde (RESEARCHED, NOT TESTED)

- Community-powered distributed generation
- Free anonymous API key (no registration)
- Supports SDXL, FLUX, and other models
- Priority queue: registered users get faster
- URL: https://aihorde.net

## Cloudflare Workers AI (RESEARCHED, NEEDS ACCOUNT)

- 10K free neurons/day (no credit card)
- SDXL via Cloudflare Workers
- Needs Cloudflare account + workers deployment
- URL: https://developers.cloudflare.com/workers-ai/

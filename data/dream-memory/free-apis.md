# Free API Integration

## FreeQwenApi
- Repo: github.com/y13sint/FreeQwenApi
- Path: D:\Portable_Soft\FreeQwenApi
- Port: 3264
- Status: Running, 28 models, 1 account
- Auth: Google OAuth completed

## FreeDeepseekAPI
- Repo: github.com/ForgetMeAI/FreeDeepseekAPI
- Path: D:\Portable_Soft\FreeDeepseekAPI
- Port: 9655
- Status: Installed, needs auth via Comet
- Auth: Pending (Comet browser)

## Integration
- Custom providers in config.yaml
- Three-tier: Qwen (content), DeepSeek (analysis), GPT-4o (complex)
- Health checks every 6 hours via cron

## Modified Files (FreeQwenApi)
- index.js, package.json, scripts/auth.js
- src/api/tokenManager.js, src/browser/auth.js, src/browser/browser.js, src/utils/prompt.js
- Changes: dotenv integration + TTY guards for non-interactive mode

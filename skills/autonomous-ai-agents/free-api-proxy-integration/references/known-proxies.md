# Known Free API Proxies — Config Reference
# Last updated: 2026-06-07

## FreeQwenApi

- Repo: https://github.com/y13sint/FreeQwenApi
- Install path: D:\Portable_Soft\FreeQwenApi
- Port: 3264
- Entry: `node index.js` (SKIP_ACCOUNT_MENU=true for headless)
- Auth: `npm run auth` → Chrome opens chat.qwen.ai
- Token: session/accounts/ directory
- Models file: src/AvailableModels.txt (28+ models)
- Smoke test: `npm run smoke`
- Sync models: `npm run models:sync`
- Hermes config:
  ```yaml
  custom_providers:
    - name: qwen-free
      base_url: http://localhost:3264/api
      model: qwen3.7-max
      api_key: dummy-key
      context_length: 131072
  ```
- Recommended models: qwen3.7-max (chat), qwen3-coder-plus (code), qwen3-vl-plus (images/video)
- Image generation: POST /api/images/generations (no DASHSCOPE_API_KEY needed)
- Video generation: POST /api/videos/generations + polling via GET /api/tasks/status/:taskId
- Multi-account: supports round-robin rotation for rate limits

## FreeDeepseekAPI

- Repo: https://github.com/ForgetMeAI/FreeDeepseekAPI
- Install path: D:\Portable_Soft\FreeDeepseekAPI
- Port: 9655
- Entry: `SKIP_ACCOUNT_MENU=1 node server.js` (requires PTY or prompt() patch)
- Auth: `npm run auth` → select 1 → login chat.deepseek.com → send "ok" → Enter
  OR extract via Comet CDP (see references/comet-cdp-extraction.md)
- Token: `deepseek-auth.json` — MUST include these fields:
  ```json
  {
    "token": "Bearer token from localStorage userToken",
    "cookie": "ds_session_id=...; smidV2=...",
    "hif_dliq": "from localStorage hif_dliq_cached",
    "hif_leim": "from localStorage hif_leim_cached",
    "wasmUrl": "https://fe-static.deepseek.com/chat/static/sha3_wasm_bg.*.wasm",
    "baseUrl": "https://chat.deepseek.com"
  }
  ```
  **CRITICAL**: `wasmUrl` is required for POW challenge solving. Without it,
  ALL chat completions fail with "Failed to parse URL from undefined".
- Dependencies: ZERO (pure Node.js 18+)
- Syntax check: `node --check server.js`
- Live tests: `BASE_URL=http://127.0.0.1:9655 MODEL=deepseek-chat npm run test:live`
- Hermes config:
  ```yaml
  custom_providers:
    - name: deepseek-free
      base_url: http://localhost:9655/v1
      model: deepseek-chat
      api_key: dummy-key
      context_length: 131072
    - name: deepseek-free-reasoner
      base_url: http://localhost:9655/v1
      model: deepseek-reasoner
      api_key: dummy-key
      context_length: 131072
  ```
- Model aliases: deepseek-chat, deepseek-v3, deepseek-reasoner, deepseek-r1,
  deepseek-chat-search, deepseek-expert, deepseek-v4-pro
- Anthropic API shim: POST /v1/messages (for Claude Code compatibility)
- OpenAI Responses API: POST /v1/responses
- Tool calling: supported (OpenAI, Anthropic, Responses formats)
- Reasoning: reasoning_content field for thinking models

## Combined Startup Script

Location: D:\Portable_Soft\free-api\start-free-apis.sh

```bash
bash start-free-apis.sh           # start both
bash start-free-apis.sh status    # check health
bash start-free-apis.sh qwen      # only Qwen
bash start-free-apis.sh deepseek  # only DeepSeek
```

## Full Documentation

Location: D:\Portable_Soft\free-api\INSTALL.md

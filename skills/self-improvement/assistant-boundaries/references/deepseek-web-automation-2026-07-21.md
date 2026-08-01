# DeepSeek Web Automation — File Upload & API Proxy

## Problem
Upload files (especially video) to chat.deepseek.com programmatically for vision/text analysis via headless browser.

## Why Direct Approaches Failed
- BrowserOS `upload_file` tool sets file on the `<input type="file">` element but does NOT trigger React synthetic onChange events
- `ClipboardEvent` / `DataTransfer` / `fetch` with CORS / programmatic paste — all fail on React SPA apps
- The tool reports "uploaded" but the page state doesn't update

## Correct Approach
Use **CDP `DOM.setFileInputFiles`** — Puppeteer's and Playwright's `setInputFiles()` internally calls this CDP command, which properly triggers React synthetic events.

## Existing Solution — maresin/deepseek-automation-api
- GitHub: https://github.com/maresin/deepseek-automation-api
- ~3.4k stars, MIT, Node.js + Playwright
- Gives OpenAI-compatible API for DeepSeek web (free tier)
- Endpoints:
  - `POST /v1/files/upload` — upload PDF, image, text, code
  - `POST /v1/files/upload-multiple` — up to 10 files
  - `POST /v1/chat/completions` — OpenAI-compatible chat
  - `POST /v1/register` — create session + get API key
- Also supports: tool calling, web search, DeepThink (R1), session recovery, RAG
- Config via `.env`: PORT, DEEPSEEK_EMAIL/PASSWORD, ENABLE_RAG, etc.
- DeepSeek official API does NOT support file upload (confirmed by issue #113 in awesome-deepseek-integration — `/v1/files` returns 404)

## DeepSeek Web Upload Backend
From localStorage on chat.deepseek.com:
- `files_host: files.deepseeksvc.com`
- `settingsJwt` — JWT token for API auth
- `userToken` — session token stored in localStorage
- Max file size: 100MB (104857600 bytes)
- File accept: `video/mp4,video/*,image/*`
- Instant Mode: text extraction only (OCR). Vision mode only for images (Beta).

## Key Lesson
Don't try to hack file upload via headless browser tricks. Use Playwright/Puppeteer `setInputFiles()` (CDP `DOM.setFileInputFiles`) or use existing proxy projects like maresin/deepseek-automation-api.

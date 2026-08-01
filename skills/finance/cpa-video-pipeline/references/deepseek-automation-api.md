# deepseek-automation-api — Ready-made solution

**GitHub:** [maresin/deepseek-automation-api](https://github.com/maresin/deepseek-automation-api)  
**License:** MIT, 25 commits  
**Stack:** Node.js + Playwright  

## What It Does

Provides an OpenAI-compatible API server that automates the DeepSeek web UI via Playwright.  
**Completely free** — uses the web interface, not the paid DeepSeek API.

## Key Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/v1/register` | Create session + get API key |
| POST | `/v1/chat/completions` | Chat with file context, tools, DeepThink |
| POST | `/v1/files/upload` | Upload file (PDF, image, code, video) |
| POST | `/v1/files/upload-multiple` | Up to 10 files |
| GET | `/v1/settings/expert/status` | Current mode |
| GET | `/health` | Health check |

## Why This Works (and upload_file doesn't)

Playwright uses CDP `DOM.setFileInputFiles` to set files on `<input type="file">`,  
which **correctly triggers React's synthetic onChange handler**.  

BrowserOS/BrowserClaw `upload_file` sets the file on the DOM element but does NOT  
trigger React's synthetic event chain. The file appears in the DOM but the React  
component's state never updates, so it silently discards the selection.

**Fix if you need to do it manually via BrowserClaw CDP:**
```javascript
const doc = await browser.cdp('DOM.getDocument');
const search = await browser.cdp('DOM.querySelector', {
  nodeId: doc.root.nodeId,
  selector: 'input[type="file"]'
});
await browser.cdp('DOM.setFileInputFiles', {
  nodeId: search.nodeId,
  files: ['/path/to/file.mp4']
});
```

## Quick Start

```bash
git clone https://github.com/maresin/deepseek-automation-api
cd deepseek-automation-api
npm install
npx playwright install chromium
# Set .env with DEEPSEEK_EMAIL, DEEPSEEK_PASSWORD
npm start
# → http://localhost:3000
# Register: curl -X POST http://localhost:3000/v1/register
# Chat: curl http://localhost:3000/v1/chat/completions -H "Authorization: Bearer <key>" -d '{"model":"deepseek","messages":[{"role":"user","content":"Analyze this video"}]}'
```

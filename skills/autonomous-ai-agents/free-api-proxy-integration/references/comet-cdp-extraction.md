# DeepSeek Auth Extraction via Comet CDP

When the user is already logged into DeepSeek in Comet, extract auth tokens
directly via Chrome DevTools Protocol instead of running the auth script.
This avoids profile lock issues entirely.

## Prerequisites
- Comet running with `--remote-debugging-port=9222`
- User logged into chat.deepseek.com in Comet

## Extraction Script

```javascript
const WebSocket = require('ws'); // from FreeQwenApi/node_modules/ws
const fs = require('fs');

async function extractDeepSeekAuth(cometPort = 9222) {
    // 1. Find DeepSeek tab
    const tabsResp = await fetch(`http://localhost:${cometPort}/json/list`);
    const tabs = await tabsResp.json();
    
    // Create new tab with DeepSeek URL (avoids depending on existing tabs)
    const verResp = await fetch(`http://localhost:${cometPort}/json/version`);
    const ver = await verResp.json();
    const browserWs = new WebSocket(ver.webSocketDebuggerUrl);
    
    // ... createTarget → wait → connect to new tab ...
    
    // 2. Extract from localStorage via Runtime.evaluate
    const tokenRes = await send('Runtime.evaluate', {
        expression: 'localStorage.getItem("userToken")',
        returnByValue: true
    });
    // Parse: JSON.parse(tokenRes.result.value).value → actual token
    
    const hifRes = await send('Runtime.evaluate', {
        expression: `JSON.stringify({
            hif_dliq: localStorage.getItem('hif_dliq_cached'),
            hif_leim: localStorage.getItem('hif_leim_cached')
        })`,
        returnByValue: true
    });
    
    // 3. Get cookies via Network.getAllCookies
    const cookieRes = await send('Network.getAllCookies');
    const dsCookies = cookieRes.cookies.filter(c => c.domain.includes('deepseek.com'));
    const cookieHeader = dsCookies.map(c => c.name + '=' + c.value).join('; ');
    
    // 4. Get wasmUrl from page resources
    const wasmRes = await send('Runtime.evaluate', {
        expression: `performance.getEntriesByType('resource')
            .map(r => r.name)
            .filter(n => /sha3.*\\.wasm/.test(n))[0] || 
            'https://fe-static.deepseek.com/chat/static/sha3_wasm_bg.7b9ca65ddd.wasm'`,
        returnByValue: true
    });
    
    // 5. Save
    return {
        token: parsedToken,
        cookie: cookieHeader,
        hif_dliq: hifValues.hif_dliq,
        hif_leim: hifValues.hif_leim,
        wasmUrl: wasmUrl,
        baseUrl: 'https://chat.deepseek.com'
    };
}
```

## Key localStorage Keys
- `userToken` — JSON with `{value: "token_string", __version: "0"}`
- `hif_dliq_cached` — encrypted header value
- `hif_leim_cached` — encrypted header value
- `settingsJwt` — usually null

## CDP Timing Notes
- `Runtime.evaluate` can timeout on heavily loaded Comet (many tabs)
- `DOM.enable` and `Network.enable` also timeout when Comet is overloaded
- Solution: kill Comet, restart fresh with `--remote-debugging-port=9222`
- The fresh Comet can then navigate to DeepSeek and extract quickly

## Comet Restart Sequence
```bash
# 1. Kill existing Comet
taskkill //PID <pid> //F

# 2. Restart with debugging
"C:/Users/Asus/AppData/Local/Perplexity/Comet/Application/comet.exe" \
  --remote-debugging-port=9222 \
  --remote-allow-origins=* \
  --user-data-dir="$LOCALAPPDATA/Perplexity/Comet/User Data" &

# 3. Wait 12-15 seconds for startup
# 4. Extract via CDP
```

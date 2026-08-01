# Free API Auth Pitfalls

## Comet Browser (Perplexity)
- Path: `C:/Users/Asus/AppData/Local/Perplexity/Comet/Application/comet.exe`
- Profile: `$LOCALAPPDATA/Perplexity/Comet/User Data`
- Comet is Chromium-based, supports `--remote-debugging-port`

## FreeDeepseekAPI Auth Issues

### Problem: Auth script defaults to macOS Chrome path
The `resolveChromePath()` function in `scripts/deepseek_chrome_auth.js` falls back to:
`/Applications/Google Chrome.app/Contents/MacOS/Google Chrome`
Fix: Set `CHROME_PATH` env var before running.

### Problem: Profile directory locked (EPERM rename)
If Comet is already running, the auth script cannot rename `.chrome-for-testing-profile-deepseek`.
Fix: Kill existing Comet processes first, OR use `--remote-debugging-port` with existing Comet.

### Problem: REUSE_CHROME mode hangs
`DEEPSEEK_REUSE_CHROME=1` tries to connect to port 9334 but nothing is listening.
Fix: Launch Comet manually with `--remote-debugging-port=9334` first.

### Working Approach
1. Kill existing Comet instances
2. Launch Comet with debugging: `"comet.exe" --remote-debugging-port=9334 --user-data-dir="<profile>"`
3. Verify CDP: `curl -s http://localhost:9334/json/version`
4. Run auth: `DEEPSEEK_REUSE_CHROME=1 node scripts/deepseek_chrome_auth.js`
5. Log in to DeepSeek in the Comet window
6. Press Enter in terminal

### Alternative: Direct Token Extraction
If Comet is already logged into DeepSeek:
1. Launch Comet with debugging port on existing profile
2. Navigate to chat.deepseek.com
3. Extract token via CDP (Network.getAllCookies + localStorage)

## FreeDeepseekAPI Server Startup
- `server.js` uses readline for interactive menu → crashes with "stdin is not a tty"
- Fix: Patch `prompt()` function to add TTY guard:
  ```js
  function prompt(question) {
      if (!process.stdin.isTTY) { return Promise.resolve(''); }
      // ... original code
  }
  ```
- Then start with: `SKIP_ACCOUNT_MENU=1 node server.js`
- Server listens on port 9655 (configurable via PORT env var)

## FreeQwenApi
- Auth via Google OAuth (works with Comet)
- Token stored in `session/tokens.json`
- Requires PTY for background mode (non-PTY crashes with "stdin is not a tty")
- Start with: `SKIP_ACCOUNT_MENU=true node index.js`

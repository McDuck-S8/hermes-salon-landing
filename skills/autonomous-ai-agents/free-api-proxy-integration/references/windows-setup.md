# Windows Setup Notes — Free API Proxies

## Chrome / Browser Path

Free proxy projects use Puppeteer to maintain browser sessions. On Windows,
they can't find Chrome because paths are hardcoded to macOS/Linux.

### FreeQwenApi
- `.env` has `CHROME_PATH=D:/Portable_Soft/puppeteer-cache/chrome/win64-148.0.7778.97/chrome-win64/chrome.exe`
- This is a pre-downloaded Puppeteer Chrome binary (~4MB exe)
- Works without Chrome/Edge installed

### FreeDeepseekAPI
- `scripts/deepseek_chrome_auth.js` line 222 defaults to macOS path
- Must set `CHROME_PATH` env var before running `npm run auth`
- Options (in order of preference):
  1. **Comet Perplexity** (user's default browser, already authenticated):
     ```bash
     export CHROME_PATH="C:/Users/Asus/AppData/Local/Perplexity/Comet/Application/comet.exe"
     ```
     Discovery: `powershell -Command "(New-Object -ComObject WScript.Shell).CreateShortcut('C:\\Users\\Asus\\Desktop\\Comet.lnk').TargetPath"`
     Profile: `$LOCALAPPDATA/Perplexity/Comet/User Data`
  2. Puppeteer cache: `"D:/Portable_Soft/puppeteer-cache/chrome/win64-148.0.7778.97/chrome-win64/chrome.exe"`
  3. Edge: `"/c/Program Files (x86)/Microsoft/Edge/Application/msedge.exe"`

- **Comet profile locking**: Cannot launch two Comet instances with same `--user-data-dir`.
  If Comet is already running, a second instance exits immediately. For DeepSeek auth,
  use the user's EXISTING Comet profile (they're already logged in) — do NOT create a new one.
  The auth script's `--user-data-dir` flag will conflict with the running instance.

- **Comet remote debugging**: Works with `--remote-debugging-port=9334`. CDP v1.3.
  Can extract auth tokens directly via DevTools Protocol if user is already logged in.

## Non-TTY Terminal Issues

Both projects use `readline` for interactive prompts. In Git Bash /
background processes, `process.stdin.isTTY` is `undefined`.

### Files patched in FreeQwenApi:
- `src/utils/prompt.js` — added TTY guard before `readline.createInterface`
- `src/browser/auth.js` — added TTY guard in `promptUser()` function
- `src/browser/browser.js` line 153 — added TTY guard before `stdin.resume()`
  ```js
  if (!process.stdin.isTTY) { resolve(); return; }
  ```

### FreeDeepseekAPI server.js:
- **Already has TTY guard** in `prompt()` (line 49), added by the project
  upstream. No patching needed.
- Despite the TTY guard, Node.js itself may emit "stdin is not a tty" at
  module load time when `readline` is imported without a TTY. Reliable fix:
  run with `pty=true` in the terminal tool.

### Startup commands that work (verified):
```bash
# FreeDeepseekAPI - works with pty=true
terminal(background=true, pty=true, command="cd /d/Portable_Soft/FreeDeepseekAPI && SKIP_ACCOUNT_MENU=true node server.js")

# FreeQwenApi - works with pty=true (browser init takes ~30s)
terminal(background=true, pty=true, command="cd /d/Portable_Soft/FreeQwenApi && SKIP_ACCOUNT_MENU=true node index.js")
```

### Port cleanup (Windows):
```bash
# Find process on port
netstat -ano | grep <PORT>

# Kill it (kill <pid> DOES NOT WORK in Git Bash)
taskkill //F //PID <PID>
```

### Verification after startup:
```bash
# DeepSeek (OpenAI-compatible)
curl -s http://localhost:9655/v1/models | head -3

# Qwen (custom API)
curl -s http://localhost:3264/api/status
```

## TokenManager.js Fix

If FreeQwenApi starts but shows empty account list:

1. Check `session/tokens.json` exists and has content
2. Check `src/api/tokenManager.js` line for TOKENS_FILE constant
3. Correct format: `const TOKENS_FILE=path.join(ACCOUNTS_PATH, 'tokens.json');`
4. The file uses ESM modules (`"type": "module"` in package.json)

## Startup Command

```bash
cd /d/Portable_Soft/FreeQwenApi
SKIP_ACCOUNT_MENU=true node index.js
```

`SKIP_ACCOUNT_MENU=true` prevents the interactive menu when tokens exist.

## FreeDeepseekAPI Startup

```bash
cd /d/Portable_Soft/FreeDeepseekAPI
SKIP_ACCOUNT_MENU=1 node server.js
```

**Must use PTY mode** (`pty=true` in terminal tool) unless `prompt()` is
patched with TTY guard. See pitfall #8 in SKILL.md.

## curl Cyrillic Encoding (Windows)

Git Bash / MSYS2 mangles UTF-8 in `curl -d` command-line arguments.
Russian text arrives as mojibake to the server. Fix: write JSON to file.

```bash
# WRONG — Cyrillic gets mangled
curl -d '{"content":"Привет"}' http://localhost:9655/v1/chat/completions

# RIGHT — write to file first
echo '{"content":"Привет"}' > /tmp/request.json
curl -d @/tmp/request.json http://localhost:9655/v1/chat/completions
```

This applies to ALL curl requests with non-ASCII content on Windows/Git Bash.

## Combined Launcher

`D:\Portable_Soft\free-api\start-free-apis.sh` starts both proxies with
health checks and status output.

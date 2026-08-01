# Comet Perplexity Browser — Integration Notes

## Path Discovery

Comet is Chromium-based (Perplexity's browser). Discovery method on Windows:

```bash
# Method 1: PowerShell shortcut inspection
powershell -Command "(New-Object -ComObject WScript.Shell).CreateShortcut('C:\\Users\\Asus\\Desktop\\Comet.lnk').TargetPath"
# Returns: C:\\Users\\Asus\\AppData\\Local\\Perplexity\\Comet\\Application\\comet.exe

# Method 2: Registry
reg query "HKCU\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\App Paths\\comet.exe"
```

## Profile Location

```
C:\Users\<user>\AppData\Local\Perplexity\Comet\User Data
```

## Key Behaviors

- **Profile locking**: Cannot launch two Comet instances with same `--user-data-dir`.
  If Comet is already running, a second instance with the same profile will exit immediately.
- **Remote debugging**: Works with `--remote-debugging-port=9334`. Chrome DevTools Protocol v1.3.
- **User-Agent**: Reports as `Chrome/148.0.7778.97` (Chromium-based).
- **Google login**: Works natively — user is already authenticated in Comet.
- **For DeepSeek auth**: Use the user's EXISTING Comet profile (they're already logged in).
  Do NOT create a new profile — the auth script's `--user-data-dir` will conflict.

## Puppeteer/Chrome-for-Testing Conflict

FreeDeepseekAPI's `deepseek_chrome_auth.js` has a `resolveChromePath()` function that:
1. Checks `CHROME_PATH` env var first
2. Falls back to Puppeteer's bundled Chrome
3. Falls back to macOS paths (useless on Windows)

Always set `CHROME_PATH` explicitly on Windows:
```bash
export CHROME_PATH="C:/Users/Asus/AppData/Local/Perplexity/Comet/Application/comet.exe"
```

## Non-Interactive Mode (FreeQwenApi)

After initial auth, FreeQwenApi needs these env vars for background startup:
```bash
SKIP_ACCOUNT_MENU=true node index.js
```

Without `SKIP_ACCOUNT_MENU`, the server tries to open an interactive menu and hangs.

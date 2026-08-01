# Environment Pre-flight for Heavy Python Installs

Before running `pip install` on a project with 20+ dependencies (especially on Windows with constrained disk), run these checks FIRST. They take 10 seconds and save 15+ minutes of failed installs.

## Checklist

### 1. Disk Space (Critical on Windows)
```bash
# Check free space on all drives
df -h /c /d 2>/dev/null || wmic logicaldisk get size,freespace,caption
# pip/uv cache lives on C: by default — even if project is on D:
# If C: has <1GB free, the install WILL fail silently or hang
```

**Fix if full:**
- Clear uv cache: `uv cache clean`
- Clear pip cache: `pip cache purge`
- Clear Windows temp: `del /q %TEMP%\*` (from cmd, not bash)
- Clear WinSxS: `Dism.exe /Online /Cleanup-Image /StartComponentCleanup`

### 2. Network/Proxy
```bash
# Test raw speed
curl -s -o /dev/null -w "%{speed_download}" https://pypi.org
# If <500 KB/s, proxy is bottlenecking. Options:
#   a) Temporarily bypass proxy for pip: set HTTPS_PROXY= (empty)
#   b) Use pre-built wheels: pip install --only-binary :all: <package>
#   c) Use uv instead of pip (parallel downloads, resumable)
```

### 3. API Keys
```bash
# Check what's available before install
echo "ANTHROPIC: ${ANTHROPIC_API_KEY:+SET}" 
echo "OPENAI: ${OPENAI_API_KEY:+SET}"
echo "OPENROUTER: ${OPENROUTER_API_KEY:+SET}"
# If none set and project needs one — configure BEFORE install
```

### 4. Python Version
```bash
python --version  # Need 3.10+ for most modern projects
# On Windows, check which python is on PATH:
which python
```

## Pattern: pip install hanging on Windows

If `pip install` shows "Downloading..." then stalls for minutes:
1. It's usually the proxy — check v2rayn/clash
2. Try `pip install --proxy "" <package>` to bypass
3. Or use `uv pip install` which handles timeouts better
4. Or download wheel manually: `pip download <package>` on fast network, then install from local

## Pattern: C: drive full but project is on D:

uv and pip caches default to C:\Users\<user>\AppData — even when installing to D:\. 
Always check C: free space, not just D:.

## Key Insight

The biggest time-waster in agent workflows is starting a 30-minute install without checking prerequisites. A 10-second preflight avoids:
- 15+ minutes of stalled pip
- Silent failures that require full restart
- Running out of disk mid-install with corrupted partial state

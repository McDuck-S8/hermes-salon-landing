# Dashboard JS Execution Failure — Debug Transcript

**Date:** 2026-07-12
**Context:** Dashboard at `http://localhost:8765/dashboard.html` showed all zeros (0 tasks, 0 crons, 0 profiles) despite valid data files.

## Symptoms

| Check | Result |
|-------|--------|
| `curl http://localhost:8765/tasks.json` | 200 OK, 26 items |
| `curl http://localhost:8765/crons.json` | 200 OK, 35 items |
| `curl http://localhost:8765/profiles.json` | 200 OK, 1 profile |
| Dashboard page snapshot | All counters show `0` |
| Browser console | 1 exception with **empty message** |
| `typeof loadAll` from DevTools | `"undefined"` |
| `typeof loadAll` after replacing template literals with string concat | `"function"` |

## Root Cause

The dashboard JS used **template literals** (backtick strings with `${}` interpolation) for HTML generation. Sandbox/stealth browser environments (Browserbase, proxied headless Chrome) fail on multi-line template literals with `"missing ) after argument list"`. The script block silently fails to execute, leaving all functions undefined.

**Fix**: Replace all template literals with string concatenation + `escHtml()`. No backtick strings in the script block at all.

```javascript
// BROKEN (sandbox environments fail):
function renderCard(task) {
  return `<div class="card ${task.status}">
    <span>${task.title}</span>
  </div>`;
}

// WORKS:
function renderCard(task) {
  return '<div class="card ' + task.status + '"><span>' + escHtml(task.title) + '</span></div>';
}
```

## Debug Steps Taken

1. Navigated to `http://localhost:8765/tasks.json` directly — confirmed 26 tasks served
2. Created `test.html` with a minimal fetch — confirmed fetch works
3. Checked console — 1 empty exception
4. Evaluated `typeof loadAll` → `"undefined"` (script didn't run)
5. Verified script tag content via `document.querySelector('script').textContent.substring(0, 50)`
   → returned `"\n    let allTasks = [];\n    let allCrons = [];\n   "` (content is correct)
6. Evaluated script via `try { eval(document.querySelector('script').textContent); } catch(e) { ... }`
   → `"missing ) after argument list"` at `anonymous:1:44`
7. Replaced all template literals with string concatenation → `typeof loadAll` returned `"function"`
8. Dashboard rendered correctly after restart

## Additional Findings from the Same Session

### Port Conflict Handling
- The first `serve_dashboard.py` process (without REST API) held port 8765 after exit
- A second instance failed with `OSError: [WinError 10048]` — address already in use
- Resolution: changed PORT to 8766 and served from there
- Clean kill requires `taskkill /F /PID <pid>` (blocked by user in this session)

### REST API Implementation
- `http.server.SimpleHTTPRequestHandler` does NOT support POST by default
- Must override `do_POST`, `do_OPTIONS`, and add CORS headers in `end_headers`
- All state is file-based (read/write JSON) — no database dependency
- API routes: `/api/task/create`, `/api/task/move`, `/api/task/delete`, `/api/task/update`, `/api/cron/run`

### os.chdir() Interaction
- `os.chdir(DASHBOARD_DIR)` in `serve_dashboard.py` changes CWD
- Launching via `python scripts/serve_dashboard.py` from the project root causes the script to look for `scripts/` inside `dashboard_data/`
- Fix: use absolute path: `python D:/Portable_Soft/hermes/scripts/serve_dashboard.py` with `workdir` set to project root

## Files Referenced

- `D:\Portable_Soft\hermes\dashboard_data\dashboard.html`
- `D:\Portable_Soft\hermes\dashboard_data\data\tasks.json`
- `D:\Portable_Soft\hermes\dashboard_data\data\crons.json`
- `D:\Portable_Soft\hermes\dashboard_data\data\profiles.json`
- `D:\Portable_Soft\hermes\scripts\serve_dashboard.py`

---
name: dashboard-visualization
description: Build and maintain interactive management dashboards for agent work — kanban with drag & drop, task CRUD, cron control, system health.
version: 2.3.0
platforms: [linux, macos, windows]
environments: [dashboard]
metadata:
  hermes:
    tags: [dashboard, visualization, kanban, monitoring, html, management, rest-api]
    related_skills: [kanban-orchestrator, cron-maintenance, system-audit]
---

# Dashboard — Interactive Kanban + System Management

## Purpose

Build a live HTML dashboard with **full CRUD management**, not just read-only monitoring:

- Kanban board with **drag & drop** between columns (Ready/Running/Blocked/Done)
- **Create / Move / Delete** tasks inline
- **Run cron jobs** with one click
- Click task card → modal with details + status-change buttons
- KPI cards (Ready/Running/Blocked/Total counts)
- Profile status, system health

## Architecture

```
                  ┌──────────────────────┐
                  │  gen_dashboard.py     │ ← Hermes CLI (kanban list, cron list)
                  │  (cron: every 6h)     │
                  └──────┬───────────────┘
                         ▼
             ┌───────────────────────┐
             │  dashboard_data/       │ ← JSON files (tasks, crons, profiles)
             │  ├── data/tasks.json   │
             │  ├── data/crons.json   │
             │  ├── data/profiles.json│
             │  └── dashboard.html    │ ← Single-file HTML + JS + CSS
             └───────────┬───────────┘
                         ▼
             ┌───────────────────────┐
             │  serve_dashboard.py    │ ← HTTP server (port 8765/8766)
             │  - static files (/)     │
             │  - REST API (/api/*)    │
             └───────────────────────┘
                         │
                ┌────────┴────────┐
                ▼                 ▼
         Browser (view)    AJAX (drag, create, delete, run)
```

**Important: Dashboard requires a regular browser (Chrome, Firefox, Edge) with JS enabled. BrowserClaw MCP cannot execute the dashboard's JavaScript (fetch/render cycle) — it only sees the initial HTML without the dynamic data. Use regular browser at `http://localhost:8765/dashboard.html` for live dashboard.**

**Key change from v1**: `serve_dashboard.py` is no longer a static file server — it now has a REST API layer that writes back to the JSON files, enabling management actions from the browser.

## REST API Endpoints

All endpoints return `{"ok": true/false, ...}`. Errors include `"error": "message"`.

| Method | Path | Body | Action |
|--------|------|------|--------|
| POST | `/api/task/create` | `{"title", "assignee"?, "description"?, "priority"?:P2, "label"?, "blocks"?, "deadline"?, "awaits"?, "type"?:task, "trigger"?}` | Create task → Ready. `type` = "task" or "goal". `trigger` = event description for goals. |
| POST | `/api/task/move` | `{"id", "status"}` | Change task status (drag & drop) + logs to move_log.json |
| POST | `/api/task/delete` | `{"id"}` | Delete task |
| POST | `/api/task/update` | `{"id", ...any...}` | Update arbitrary fields (not whitelisted — any key goes) |
| POST | `/api/cron/run` | `{"id"}` | Mark cron as triggered |
| POST | `/api/templates/list` | `{}` | List templates (array of `{"id", "title", "description", "priority", "label", "assignee", "deadline_offset", "awaits"}`) |
| POST | `/api/templates/create` | `{"title", "description"?, "priority"?:P2, "label"?, "assignee"?, "deadline_offset"?, "awaits"?}` | Create template |
| POST | `/api/templates/delete` | `{"id"}` | Delete template |

---

### Cron Worker Dashboard API Pattern (2026-07-13)

Scheduled cron jobs can act as **backlog workers** — fetching ready tasks from the dashboard, performing work, and marking them complete via the API.

**Usage in cron jobs:**
```bash
# 1. Fetch tasks
curl -s http://localhost:8766/data/tasks.json

# 2. Select highest-priority "ready" task (P0 > P1 > P2 > P3)
# 3. Do the work (research, code, docs, etc.)

# 4. Mark done
curl -s -X POST http://localhost:8766/api/task/move \
  -H "Content-Type: application/json" \
  -d '{"id":"565fef3d","status":"done"}'
```

**Critical implementation notes:**
- **Required header:** `Content-Type: application/json` (missing → 400/422)
- **Body fields:** `id` + `status` (NOT `task_id` / `new_status`)
- **Valid statuses:** `ready`, `running`, `blocked`, `done`
- **Server process:** Must be running (`python.exe` serving on port 8766)
- **Health check:** `curl -s http://localhost:8766/ → 301 → /dashboard.html`

**Priority sorting:**
```python
PRIORITY_ORDER = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}
ready_tasks.sort(key=lambda t: PRIORITY_ORDER.get(t.get("priority", "P2"), 2))
```

**Log entry format:**
```
[YYYY-MM-DD HH:MM] Completed TASK_ID - TASK_TITLE - what was done
```

See `references/cron-worker-dashboard-api-2026-07-13.md` for full template and session details.

---

### Browser Automation with MCP (2026-07-13)

When using `mcp__browserclaw__*` tools for dashboard verification:

- **New tab per session:** Each `mcp__browserclaw__tabs` with `action: "new"` creates an owned tab. Use that page ID for subsequent operations.
- **MCP tool sequence:** `tabs new` → `navigate` → `snapshot` → `act` → `wait` → `snapshot`. Avoid reusing page IDs across different URLs.
- **Fetch via curl, not browser:** For JSON endpoints (`/tasks.json`, `/crons.json`), use `curl` via terminal — faster, no JS rendering needed. Browser automation is for visual verification and click/navigate workflows.
- **Template literals in dashboard JS:** The dashboard HTML uses string concatenation (not template literals) to avoid browser sandbox issues. When debugging, use `curl` to verify JSON endpoints first, then browser for visual check.
- **Server must be running:** `python scripts/serve_dashboard.py` must be alive (check with `curl -s -o /dev/null -w "%{http_code}" http://localhost:8765/dashboard.html`). If port 8765 is occupied, change PORT to 8766 in `serve_dashboard.py`.

---

## Data Files
| POST | `/api/rules/delete` | `{"id"}` | Delete rule |
| POST | `/api/rules/evaluate` | `{}` | Run all enabled rules against current tasks. Returns `{"results": [{rule_id, rule_name, task_id, task_title, action}]}` |

All APIs read/write JSON files in `dashboard_data/data/` directly — no database needed.

**Important**: `api_task_update` accepts **any key-value pair** on the task (no whitelist). This allows adding new fields (priority, label, deadline, blocks, awaits, type, trigger, or any future field) without backend changes. The create endpoint also passes through all extra fields to the task object.

## Key Scripts

| Script | Purpose |
|--------|---------|
| `scripts/gen_dashboard.py` | Fetches live data from Hermes CLI, writes JSON to `dashboard_data/data/` |
| `scripts/serve_dashboard.py` | HTTP server for static files + REST API |
| `dashboard_data/dashboard.html` | Single-file dashboard — vanilla JS, no dependencies |

## Regenerating Data

```bash
cd D:/Portable_Soft/hermes && python scripts/gen_dashboard.py
```

If `gen_dashboard.py` hangs (>30s timeout), create JSON data manually — see "Manual Data Generation" below.

Schedule via cron: `0 */6 * * *` (every 6 hours) or run on demand.

### Manual Data Generation

When auto-generators hang (common on Windows):

1. Write JSON files directly in `dashboard_data/data/`
2. Task format: `{"id", "title", "status", "assignee", "created_at", "updated_at", "description"?, "priority"?:P2, "label"?, "blocks"?, "deadline"?, "awaits"?, "type"?:task, "trigger"?}`
   - `updated_at` — ISO timestamp, auto-set on move and update
   - `priority` — P0 (high) / P1 / P2 (default) / P3 (low). Controls left border color.
   - `label` — empty / "red" / "yellow" / "green". Shows as colored dot.
   - `blocks` — task ID of the task this one blocks. Shows 🔗 icon.
   - `deadline` — ISO date string (YYYY-MM-DD) or empty. Red border if overdue, orange if today.
   - `awaits` — user name or empty. 👤 icon.
   - `type` — "task" (default, shown in grid) or "goal" (shown in Queue section). Goal cards get pink border.
   - `trigger` — event description for goals. Shown in Queue section.
3. Move log format (`data/move_log.json`): `[{"task_id", "task_title", "from", "to", "timestamp"}]` — last 200 entries kept. Appended on every api_task_move call.
4. Template format (`data/templates.json`): `[{"id", "title", "description", "priority", "label", "assignee", "deadline_offset"(days int), "awaits"}]`
5. Rule format (`data/rules.json`): `[{"id", "name", "condition":{field, op, value?, days?}, "action":{action, target_status?}, "enabled":bool}]`
6. Cron format: `{"id", "name", "schedule", "last_run", "last_status", "next_run"?}`
7. Profile format: `{"name", "model", "gateway", ...}`
8. Health format: `{"uptime", "memory", "disk", "cpu"}`

Use `write_file()` or Python script with `json.dump()`. No database needed.

Use `write_file()` or Python script with `json.dump()`. No database needed.

## Starting the Server

```bash
# Primary port (default):
python scripts/serve_dashboard.py
# Then open http://localhost:8765/dashboard.html

# Fallback port (if 8765 is occupied):
# Edit PORT in serve_dashboard.py to 8766 before starting
# Then open http://localhost:8766/dashboard.html
```

Auto-fallback pattern: when port 8765 is occupied (zombie process), change `PORT = 8766` in serve_dashboard.py and restart. Detect with `curl -s -o /dev/null -w "%{http_code}" --max-time 3 http://localhost:8765/` — if not 200, use fallback. Keep the server running on the fallback port until the zombie is killed with `taskkill //F //PID <PID>` (or similar).

Always use `terminal(background=true)` so the server survives the session.

## Dashboard Features

- **Drag & drop** — grab a task card, drop on another column. The API is called immediately, status persists.
- **Touch drag & drop** — touchstart/touchmove/touchend handlers supplement HTML5 DnD for mobile/touch devices. Uses `document.elementFromPoint()` to detect column under finger.
- **Inline action buttons** — hover a card to see Start/Block/Done/Delete buttons. No modal needed for quick moves.
- **Task creation form** — full form with title, description, status, priority, label, deadline, awaits, type (task/goal), trigger (for goals). Enter or click "➕ Add task" to submit.
- **Click to inspect** — modal with all fields editable inline (priority, label, assignee, blocks, deadline, awaits, type, trigger) + status-change buttons.
- **View filters** — toolbar: All / Ready / Running / Blocked / Done / Queue. "Queue" shows only goals (type=goal) in a separate grid below with deadline + trigger info.
- **Priority filter** — part of view filter system. Each view scope filters by priority internally.
- **Sort dropdown** — sort cards within each column by priority (P0→P3), date (newest first), or last-updated (updated_at).
- **Search** — live text input filters cards by title (case-insensitive, oninput → re-render).
- **Color labels** — each task can have a red/yellow/green label dot. Picked in create modal or detail modal. Controlled via `label` field.
- **Deadline highlighting** — `deadline` field (ISO date). Card border turns **red** if overdue, **orange** if due today. Background tints accordingly.
- **Dependency links** — `blocks` field holds another task's ID. Card shows 🔗 icon. The blocked task shows ⛓️ "Blocked by: X" in its detail modal. Dropdown selector in edit modal shows all other tasks.
- **User mentions** — `awaits` field (string, e.g. "Александр"). 👤 icon on card. "👤 Waits for me" filter button in toolbar.
- **Move history** — every `/api/task/move` appends to `data/move_log.json` (last 200 entries). Section at page bottom with collapsible list: time, task title, from→to. Reverse chronological, 100 most recent shown.
- **Inline field editing in modal** — all task fields (priority, label, assignee, blocks, deadline, awaits, type, trigger) are editable inline via `<select>` or `<input>` with `onchange` → API call → re-render. No separate "save" button.
- **Goal Queue section** — shows only type=goal tasks in a card grid sorted by deadline. Each card shows trigger description. Visible only when Queue filter is active. Separate section below the main grid.
- **Statistics section** — always-visible stats grid: Total tasks, Done rate %, Ready/Running/Blocked/Done counts, Goals count, Overdue count. Auto-calculated from task data on every render.
- **Hide Done toggle** — "🙈 Hide done" button hides the Done column (skips rendering `col.id==='done'` when active). Badges still show all counts.
- **Templates** — templates stored in `data/templates.json`. "📝 From template" button in new-task modal opens a picker. "💾 Save current" captures the currently open task's fields as a template with a name. Templates include: title, description, priority, label, assignee, deadline_offset (days from today), awaits.
- **Rules engine** — rules stored in `data/rules.json`. UI for add/list/delete rules. Condition types: "eq" (field = value), "stale" (unchanged for N days, default 7). Actions: "block" (move to blocked), "unblock" (move to ready), "notify" (log). "▶ Evaluate" button runs all enabled rules against current tasks and shows triggered results. Rules UI has inline selectors for field/operator/value/action.
- **Cron Run Now** — each cron row has a "Run" button. Marks as triggered in JSON.
- **Auto-refresh** — loads data (tasks, move log, templates, rules) every 30 seconds.
- **KPI badges** — 4 status badges at top: Ready/Running/Blocked/Done counts + goals count.
- **Dark theme** — matches Hermes CI aesthetic (dark grey surface, blue/green/red accents). Task cards have colored left borders by priority.
- **Russian UI** — default locale.

## Adding New Data Sources

1. Add parser in `gen_dashboard.py` (follow `parse_kanban_list`, `parse_cron_list` patterns)
2. Write JSON to `dashboard_data/data/<name>.json`
3. Add render function in `dashboard.html` JS (use string concatenation, NOT template literals)
4. Add HTML section with appropriate IDs for data binding

## Research-Backed Design Principles

From surveying 50+ dashboard designs (2025-2026 patterns: shadcn/ui, AdminLTE, Tabler):

1. **KPI cards at top** — 4-6 metrics in a row give instant system state. Always show Ready/Running/Blocked/Total.
2. **Dark theme** — industry standard for dev ops dashboards; reduces eye strain for all-day monitoring.
3. **Interactive cards, not just labels** — every visible element should be actionable (click to inspect, buttons on hover, drag to move).
4. **Cron management** — "Run Now" + last-run status + next-run schedule on each row. The most common admin action is "did it run? run it now."
5. **Research before building** — survey existing open-source dashboards for UX patterns before implementing. Users expect professional UI, not just functional.
6. **Dashboard is a tool, not a report** — if the user can only look but not act, it's a report. A true dashboard lets them manage from the same view.

## Pitfalls

### JS Template Literals (backtick strings) — BROWSER SANDBOX FAILURE

**Avoid template literals entirely** in `dashboard.html` JS when the server might be viewed through a stealth/sandbox browser environment (Browserbase, proxied browsers, headless Chrome stealth mode). These environments fail with `"missing ) after argument list"` on multi-line template literals, even though the same code works fine in a normal browser.

**DO NOT do this:**
```javascript
var html = `<div class="card ${cls}">
  <span>${title}</span>
</div>`;
```

**DO this instead** (string concatenation + escHtml):
```javascript
var html = '<div class="card ' + cls + '"><span>' + escHtml(title) + '</span></div>';
```

Keep all JS functions in a single `<script>` block. No external JS files. No arrow functions in main script.

### Python SimpleHTTPRequestHandler — POST NOT SUPPORTED BY DEFAULT

The base class only handles GET/HEAD. You must override `do_POST`:

```python
class Handler(http.server.SimpleHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(length)) if length else {}
        # ... route handling, return via self.send_json() ...
```

Also add `do_OPTIONS` for CORS preflight and update `end_headers`:
```python
def do_OPTIONS(self):
    self.send_response(200)
    self.end_headers()

def end_headers(self):
    self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
    self.send_header("Access-Control-Allow-Headers", "Content-Type")
    super().end_headers()
```

### Port Conflict — 8765 Occupied

When `serve_dashboard.py` fails to bind to 8765, it dies silently in background mode. Always verify:

```bash
curl -s -o /dev/null -w "%{http_code}" --max-time 3 http://localhost:8765/dashboard.html
```

- `200` = alive. `000` or empty = dead. Find the zombie:
  ```bash
  netstat -ano | grep 8765
  taskkill //F //PID <PID>
  ```
- If zombie won't die (user blocks taskkill), change PORT to 8766 and restart on that port.

### os.chdir() Changes Script Resolution

`serve_dashboard.py` calls `os.chdir(DASHBOARD_DIR)` for static file serving. This changes where Python resolves script paths. Launch correctly:

**WRONG** (runs from cwd after chdir):
```bash
python scripts/serve_dashboard.py
```

**RIGHT** (absolute path + stay in project root):
```bash
python D:/Portable_Soft/hermes/scripts/serve_dashboard.py
# terminal workdir = D:\Portable_Soft\hermes
```

### Data Paths — Relative Fetch URLs

The dashboard HTML loads via `fetch('data/tasks.json')` — relative to the page URL. Since the server serves from `dashboard_data/` as root, this resolves to `dashboard_data/data/tasks.json`. Both `tasks.json` (legacy root) and `data/tasks.json` (current convention) work — be consistent.

### Drag & Drop — HTML5 Native API + Touch Support

Built-in HTML5 drag/drop (zero dependencies). For touch devices, supplement with touch event handlers since HTML5 drag API doesn't work on mobile:

```javascript
// Mouse (HTML5 native):
<div draggable="true" ondragstart="onDragStart(event)" ondragend="onDragEnd(event)">

// Touch (supplementary — add as event listeners):
card.addEventListener('touchstart', onTouchStart, {passive:false});
card.addEventListener('touchmove', onTouchMove, {passive:false});
card.addEventListener('touchend', onTouchEnd, {passive:false});
```

Touch pattern:
- `touchstart` — record card ID, add `dragging-touch` CSS class
- `touchmove` — `e.preventDefault()` + `document.elementFromPoint()` to find which column is under the finger, highlight via `drag-over` class
- `touchend` — from `e.changedTouches[0]`, find closest `.kanban-col`, call `quickMove(id, status)` if status changed. Remove all drag classes.

Critical: `passive:false` on touchstart/touchmove so `preventDefault()` works (otherwise browser scrolls instead of dragging).

Also remove drag classes in both `ondragend` (mouse) and `touchend` (touch) to clean up after abort.

### Modal — Close on Backdrop Click

```javascript
document.getElementById('task-modal').addEventListener('click', function(e) {
  if (e.target === this) closeModal();  // only close on backdrop, not modal content
});
```

Use `.classList.add('open')` / `.remove('open')` to toggle `display: flex / none`.

### Avoid Common JS Pitfalls

- **Use `var`, not `let/const`** — maximum compatibility with browser sandboxes that may eval the script.
- **No arrow functions** in the main script body — use `function()` syntax.
- **Always null-check** `document.getElementById(id)` before setting `.textContent`.
- **Escape HTML output**: `escHtml(text)` — replace `&`, `<`, `>`, `"`. JSX/React patterns are NOT available.
- **Template literals** — banned (see above).

### Dashboard Shows Zeros — Troubleshooting

1. **Check server status**: `curl -s -o /dev/null -w "%{http_code}" http://localhost:8765/dashboard.html`
2. **Check JSON data**: `curl http://localhost:8765/data/tasks.json | head -c 200`
3. **Check browser console**: `typeof loadAll` — if `undefined`, script block didn't execute.
4. **Check for template literal errors**: look for "missing ) after argument list" in console.
5. **Minimal test page** to isolate fetch vs. execution:
   ```html
   <!DOCTYPE html><html><body>
   <div id="r">waiting...</div>
   <script>(async function() {
     try {
       var r = await fetch('data/tasks.json', {cache:'no-store'});
       var t = await r.text();
       document.getElementById('r').textContent = 'OK: ' + t.length + ' chars';
     } catch(e) {
       document.getElementById('r').textContent = 'ERR: ' + e.message;
     }
   })();</script></body></html>
   ```
6. **Force-refresh**: Ctrl+Shift+R (not just Ctrl+R) to bypass any caching.

## Related Skills

- `kanban-orchestrator` — task decomposition and routing (feeds the kanban)
- `cron-maintenance` — cron job health (feeds the cron table)
- `system-audit` — system health metrics (feeds health grid)

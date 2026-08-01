---
name: hermes-root-organization
description: Organize the Hermes root directory — sort files into proper subdirs, clean trash, maintain FILE_REGISTRY.md as the single source of truth for every file in the repo.
trigger: When the user says 'наведи порядок в корне', 'разложи файлы', 'почисти корень', 'организуй файлы', or root directory has >40 loose files.
usage: hermes-root-organization
---

# Hermes Root Organization Skill

## Purpose
Hermes root (`D:/Portable_Soft/hermes/`) accumulates loose files over time — one-off scripts, caches, backups, avatars, old reports, temporary tests. This skill defines:
- Where every **type** of file belongs
- How to maintain `FILE_REGISTRY.md` (the single source of truth)
- What is trash vs keep
- The exact move/delete commands

## Principles
1. **Files are not orphans.** Every file in root must either be (a) a core Hermes file that belongs at root, or (b) in its proper subdirectory.
2. **Registry is truth.** `FILE_REGISTRY.md` documents every file in the repo — path, purpose, creator, when it was created/last touched, whether it's active or archived.
3. **No silent deletion.** Trash goes to `trash/` first, never `rm`'d directly. User can review and purge later.
4. **Symmetry with existing Hermes structure.** Subdirs already exist for most purposes — use them. Only create new subdirs when no existing dir fits.

## File Classification

### CRITICAL: Use es.exe for ALL File Searches
**NEVER use `find`, `ls -R`, or `search_files` to locate files.** Use Everything:
```bash
ES="/d/Portable_Soft/Everything-1.5.0.1408a.x64/es.exe"
"$ES" <filename>     # instant search across ALL drives
```
Agent repeatedly timed out with `find` (10s+), missed files in `projects/`, `skills/`, `plugins/`. es.exe finds everything in <1s.

### CRITICAL: projects/ Contains Full Standalone Projects
`projects/` is NOT dead code. It contains complete, deployable projects:
- `projects/salon-bot/` — full Telegram bot (main.py, bot/, .venv, .env, landing/, cron/, data/)
- Each project has its own .env, .venv, requirements.txt

**Before claiming a project is "missing"** — run `es.exe <project_name>` first.

### CATEGORY A — STAY AT ROOT (Hermes expects these)
These files must stay at `D:/Portable_Soft/hermes/` because Hermes core, gateway, or scheduler reads them from the exact root path:

| File | Reason |
|------|--------|
| `config.yaml` | Main Hermes config |
| `.env` | Environment variables, API keys |
| `AGENTS.md` | Agent integration protocol (loaded each session) |
| `SOUL.md` | System soul/identity file |
| `state.db` (+ `-shm`, `-wal`) | Hermes session database |
| `auth.json` (+ `auth.lock`) | Authentication state |
| `branches.yaml` | Branch context manager |
| `breadcrumbs.log` | Breadcrumb trail |
| `channel_directory.json` | Channel routing config |
| `cron/` | Cron output and scheduler directory |
| `scripts/` | Scripts directory always stays |
| `plugins/` | Plugins stay |
| `skills/` | Skills stay |
| `data/` | Data stays |
| `logs/` | Logs stay (some log files may be at root) |
| `cache/` | Cache databases/stay |
| `config.yaml` only ONE active config | Delete/move all `.bak.*` variants |

### CATEGORY B — POSTING SCRIPTS → `scripts/posting/`
All scripts that post content to Telegram channels. They reference `hermes-usb-portable-main/data/.env` (old path) and need updated `env_file` path.

Files:
- `post_all.py` — Post to all channels
- `post_debug.py`, `post_debug2.py` — Debug posting
- `post_final.py`, `post_final2.py` — Final posting versions
- `post_frontier.py` — Frontier channel posting
- `post_urls.py` — URL/content posting
- `post_with_images.py` — Posting with images
- `read_posts.py` — Reading posts
- `send_test.py`, `send_test2.py` — Test sends

**Action:** `mkdir -p scripts/posting && mv post_*.py read_posts.py send_test*.py scripts/posting/`

**Also:** Fix the env_file path: replace `hermes-usb-portable-main/data/.env` → `.env` in each file.

### CATEGORY C — UTILITY SCRIPTS → `scripts/utilities/`
General-purpose fix/utility scripts.

Files:
- `fix_bom.ps1` — BOM fix PowerShell
- `fix_encoding.ps1` — Encoding fix PowerShell
- `fix_token.py` — Token fix Python
- `autonomous_test.py` — Autonomous system test
- `launch.bat` — Launch batch file

**Action:** `mkdir -p scripts/utilities && mv fix_*.ps1 fix_token.py autonomous_test.py launch.bat scripts/utilities/`

### CATEGORY D — ARCHIVED ONE-OFF SCRIPTS → `scripts/_archive/`
Scripts that were used once or for a specific project and are not part of the active system.

**WARNING:** `scripts/_deprecated/` contains 122 scripts moved there on 2026-06-19 (no git record of who/when). These are NOT dead — they include core system components (auto_poster, event_daemon, agent_daemon, knowledge_cube, crystal_tool_loop, etc.). Before doing ANYTHING with `_deprecated/`: read each script's docstring first. The user considers labeling them "dead" without reading a serious error. Do NOT delete from `_deprecated/` without explicit user permission.

**REFERENCE:** `WORKSHOP_INDEX.md` — comprehensive index of all 165 scripts, cron schedules, and dependencies. Read this before claiming something is missing or dead.

Files:
- `_render_eevee.py` — Blender render (auto-generated)
- `_render_fixed.py` — Blender render fixed
- `_render_min.py` — Minimal Blender render
- `_render_script.py` — Blender render script
- `test_scene.blend-cli.json` — Blender CLI test output

**Action:** `mkdir -p scripts/_archive && mv _render_*.py test_scene.blend-cli.json scripts/_archive/`

### CATEGORY E — ASSETS (avatars, images) → `assets/avatars/` and `assets/images/`
Media/visual files.

Files:
- `avatar_hermes.jpg`, `avatar_hermes.png` — Main avatars
- `avatar_hermes_123.jpg`, `avatar_hermes_42.jpg`, `avatar_hermes_777.jpg` — Generated variants
- `tavily_signup.png` — Screenshot

**Action:** 
```
mkdir -p assets/avatars assets/images
mv avatar_hermes*.jpg avatar_hermes.png assets/avatars/
mv tavily_signup.png assets/images/
```

### CATEGORY F — CONFIG BACKUPS → `config/backups/`
Old config versions.

Files (approximately 7-8 files):
- `config.yaml.bak.20260524_051511`
- `config.yaml.bak.20260601_030137`
- `config.yaml.bak.20260601_195424`
- `config.yaml.bak.20260601_195436`
- `config.yaml.bak.20260601_205356`
- `config.yaml.bak.20260601_214457`
- `config.yaml.bak.20260602_003918`
- `config.yaml.bak.20260602_082128`
- `config.yaml.bak.20260602_082146`

**Action:** `find . -maxdepth 1 -name 'config.yaml.bak.*' -exec mv {} config/backups/ \;`

### CATEGORY G — GENERATED HTML REPORTS → `reports/`
HTML files generated by Hermes.

Files:
- `adder.html` — Generated HTML
- `diapers_report.html` — HTML report
- `skills_report.html` — Skills report HTML

**Action:** `mv adder.html diapers_report.html skills_report.html reports/`

### CATEGORY H — CACHE JSON/YAML → `cache/`
Generated cache and state files that should not be at root.

Files:
- `context_length_cache.yaml` — Context length cache
- `models_dev_cache.json` — Model dev cache
- `ollama_cloud_models_cache.json` — Ollama models cache
- `provider_models_cache.json` — Provider models cache
- `youtube_research.json` — YouTube research data
- `gateway_state.json` — Gateway state snapshot
- `processes.json` — Process state
- `.update_check` — Update check marker
- `old_state.db` — Old state database
- `lcm.db` — LCM database
- `kanban.db` (+ `kanban.db.init.lock`) — Kanban database

**Action:** 
```
mv context_length_cache.yaml cache/
mv models_dev_cache.json ollama_cloud_models_cache.json provider_models_cache.json cache/
mv youtube_research.json gateway_state.json processes.json cache/
mv old_state.db lcm.db cache/
mv kanban.db kanban.db.init.lock cache/
mv .update_check cache/
```

Note: `interrupt_debug.log` → `logs/`

### CATEGORY I — NOTES → `notes/`
Markdown notes that ended up at root.

Files:
- `browser-notes.md`

**Action:** `mv browser-notes.md notes/`

### CATEGORY J — TRASH → `trash/`
Zero-byte files, obvious junk that has no purpose.

Files:
- `nul` — Zero-byte weird file (MSYS artifact?)

**Action:** `mkdir -p trash && mv nul trash/`

### CATEGORY K — HIDDEN FILES → Cleanup/move
- `.hermes_history` — Shell history, stays or moves to dedicated location
- `.icarus-state.json` — Icarus state, stays at root
- `.icarus-telemetry.jsonl` — Icarus telemetry, stays at root

These last 3 usually stay at root or go to `cache/`.

### CATEGORY L — SESSION-TRANSIENT FILES (created by Hermes while running)
Files that appear during active Hermes sessions and disappear/disappear on restart:

- `.skills_prompt_snapshot.json` — Skills list snapshot (auto-created each session)
- `gateway_state.json` — Written by gateway process when alive
- `kanban.db` (+ `kanban.db.init.lock`) — Kanban DB, some processes expect it at root

> ⚠ **Pitfall: Transient files reappear after being moved.** Running processes
> (gateway, scheduler, session) write certain files to root regardless of where
> you moved them. `kanban.db`, `gateway_state.json`, and `.skills_prompt_snapshot.json`
> are the most common. After moving them, **check if they reappeared** within the
> next `find` cycle. If they did, either:
> - Accept them as root-level files (add to CATEGORY A)
> - Move them AND restart the process that creates them
> - Add a cleanup cron job that sweeps them into `cache/` every hour
>
> The `FILE_REGISTRY.md` should note these as `transient` status — they'll
> appear/disappear between sessions and that's normal.

### CATEGORY M — MIGRATION FROM OLD INSTALLATIONS
When user says "check old installation" or "забирай from old path":

**Step 1: Identify old installation location**
- Ask user for path, don't assume. Common: `D:\Users\Asus\Загрузки\Hermes-USB-Portable-main\`
- Or: `D:\Portable_Soft\hermes-usb-portable-main\`

**Step 2: Scan for unique data (in priority order)**
1. `.env` — API keys, tokens (compare with current, don't overwrite blindly)
2. `memories/MEMORY.md` + `memories/USER.md` — critical rules, user preferences
3. `cache/knowledge_cube.db` — experiences, dimensions, white_spots
4. `config.yaml` — model config, provider settings
5. `auth.json` — credential pool, provider fingerprints
6. `data/projects/` — project configs (salon-bot, etc.)
7. `sessions/` — request dumps (for analysis, not migration)

**Step 3: Verify before migrating**
- DON'T trust delegation results blindly — subagents hallucinate file listings
- Always `ls` or `find` the old path yourself before claiming files exist
- Compare old vs current before overwriting

**Step 4: Merge memories carefully**
- MEMORY.md: add missing rules, don't replace existing
- USER.md: add missing preferences, preserve existing
- Use `patch` tool for targeted additions, not full file replacement

**PITFALL: Delegation hallucination (2026-06-26)**
Subagent reported 14 custom Python scripts in `data/scripts/` — directory was empty. Always verify delegation output with actual `ls`/`find` before acting on it.

**PITFALL: User blocking operations (2026-06-26)**
User blocked KC modification and state.db access. When user says "стоп" or blocks a command:
- STOP immediately, don't retry
- Don't rephrase or find workaround
- Ask what they want instead

## FILE_REGISTRY.md Format

After moving files, create/update `FILE_REGISTRY.md` at root with this exact structure:

```markdown
# Hermes File Registry

Last updated: YYYY-MM-DD
Total files: N

## How to use
This is the single source of truth for every file in D:/Portable_Soft/hermes/.
- Add an entry for every new file you create
- Update the `last_modified` and `status` when you change a file
- Move status to `archived` when the file is no longer active

## Core Root Files (Hermes-managed)

| File | Purpose | Last Modified | Status |
|------|---------|---------------|--------|
| config.yaml | Main Hermes configuration | ... | active |
| .env | Environment variables | ... | active |
| AGENTS.md | Agent integration protocol | ... | active |
| ... | ... | ... | ... |

## scripts/

### posting/
| File | Purpose | Lines | Status |
|------|---------|-------|--------|
| post_all.py | Post to all Telegram channels | 89 | active |

### utilities/
...

## assets/
...

## cache/
...

## notes/
...

## reports/
...

## trash/
| File | Original Location | Reason |
|------|-------------------|--------|
| nul | root | Zero-byte artifact |
```

## Execution Steps (in order)

```bash
cd D:/Portable_Soft/hermes

# 1. Create needed directories
mkdir -p config/backups scripts/posting scripts/utilities scripts/_archive assets/avatars assets/images trash logs

# 2. Move config backups
find . -maxdepth 1 -name 'config.yaml.bak.*' -exec mv {} config/backups/ \;

# 3. Move posting scripts
mv post_*.py read_posts.py send_test*.py scripts/posting/ 2>/dev/null

# 4. Move utility scripts
mv fix_bom.ps1 fix_encoding.ps1 fix_token.py autonomous_test.py scripts/utilities/ 2>/dev/null
mv launch.bat scripts/utilities/ 2>/dev/null

# 5. Move archive scripts
mv _render_*.py test_scene.blend-cli.json scripts/_archive/ 2>/dev/null

# 6. Move assets
mv avatar_hermes*.jpg avatar_hermes.png assets/avatars/ 2>/dev/null
mv tavily_signup.png assets/images/ 2>/dev/null

# 7. Move HTML reports
mv *.html reports/ 2>/dev/null

# 8. Move caches
mv context_length_cache.yaml models_dev_cache.json ollama_cloud_models_cache.json cache/ 2>/dev/null
mv provider_models_cache.json youtube_research.json gateway_state.json cache/ 2>/dev/null
mv processes.json old_state.db lcm.db .update_check cache/ 2>/dev/null
mv kanban.db kanban.db.init.lock cache/ 2>/dev/null

# 9. Move notes
mv browser-notes.md notes/ 2>/dev/null

# 10. Move logs
mv interrupt_debug.log logs/ 2>/dev/null

# 11. Trash
mv nul trash/ 2>/dev/null

# 12. Update env paths in posting scripts
cd scripts/posting
for f in post_*.py read_posts.py send_test*.py; do
  sed -i 's|hermes-usb-portable-main/data/\.env|.env|g' "$f"
done

# 13. Generate FILE_REGISTRY.md
cd /c/Users/Asus  # or wherever
# Run python script to generate registry

# 14. Verify root is clean
ls -la D:/Portable_Soft/hermes/ | grep -v "^d" | grep -v "^total" | wc -l
# Should show only essential files + README.md + FILE_REGISTRY.md
```

## Maintenance Rules
- **New scripts** go in `scripts/posting/`, `scripts/utilities/`, or `scripts/_archive/` — never at root.
- **New caches** go in `cache/`.
- **New reports** go in `reports/`.
- **New assets** go in `assets/avatars/` or `assets/images/`.
- **Before deleting anything**, move to `trash/` first for one cycle.
- **After every move**, update `FILE_REGISTRY.md` (exists at root, is the single source of truth).
- **Transient files** (kanban.db, gateway_state.json, .skills_prompt_snapshot.json): expect them to reappear if processes are running. Either accept at root or add a cleanup cron.

## Verification
After execution, the root should contain only:
```
AGENTS.md
FILE_REGISTRY.md
README.md (if exists)
SOUL.md
branches.yaml
breadcrumbs.log
cache/
channel_directory.json
config.yaml
config/
cron/
data/
.env
gateway.lock
gateway.pid
hooks/
logs/
memories/
notes/
plans/
plugins/
projects/
reports/
sandboxes/
scripts/
sessions/
skills/
state.db (+ -shm, -wal)
trash/
assets/
audio_cache/
bin/
bootstrap-cache/
browser-harness/
chrome-debug-profile/
gateway-service/
hermes-agent/
image_cache/
lsp/
ms-playwright/
node-global/
pairing/
pastes/
post_images/
skill-forge/
state-snapshots/
```
No loose `.py`, `.json`, `.yaml`, `.html`, `.jpg`, `.png`, `.ps1`, `.bat` files.

---
name: apple-ecosystem
description: "Control macOS-native apps from the terminal — Notes, Reminders, iMessage, Find My, and desktop automation via computer_use. All subsections require macOS."
version: 1.1.0
author: Hermes Agent
license: MIT
platforms: [macos]
metadata:
  hermes:
    tags: [apple, macos, notes, reminders, imessage, findmy, automation, desktop]
  skill_updated: "2026-07-24"
  stale_since: "2026-06-03"
  stale_days: 42
  very_stale: false
  updated_by: "auto_patch_g009"
    related_skills: [obsidian, notion]
---

# Apple Ecosystem Automation

Orchestrate macOS-native applications from the command line. These tools all require macOS and the relevant companion CLIs.

> **Platform restriction:** All sections in this skill require macOS. They are not available on Linux or Windows.

---

## Overview

| Tool | App | CLI | Purpose |
|------|-----|-----|---------|
| Apple Notes | Notes.app | `memo` | Create, search, edit notes |
| Apple Reminders | Reminders.app | `remindctl` | Add, list, complete tasks |
| iMessage | Messages.app | `imsg` | Send/receive iMessages & SMS |
| Find My | FindMy.app | AppleScript | Track devices & AirTags |
| macOS Desktop | Any app | `computer_use` tool | Drive the GUI in the background |

---

## 1. Apple Notes (`memo`)

Manage Apple Notes directly from the terminal. Notes sync across all Apple devices via iCloud.

### Prerequisites

- **macOS** with Notes.app
- Install: `brew tap antoniorodr/memo && brew install antoniorodr/memo/memo`
- Grant Automation access to Notes.app when prompted

### Quick Reference

```bash
memo notes                        # List all notes
memo notes -f "Folder Name"       # Filter by folder
memo notes -s "query"             # Search notes (fuzzy)
memo notes -a                     # Create via interactive editor
memo notes -a "Note Title"        # Quick add with title
memo notes -e                     # Interactive selection to edit
memo notes -d                     # Interactive selection to delete
memo notes -m                     # Move note to folder
memo notes -ex                    # Export to HTML/Markdown
```

### Limitations

- Cannot edit notes containing images or attachments
- Interactive prompts require terminal access (use `pty=true` if needed)

### Rules

1. Prefer Apple Notes when user wants cross-device sync (iPhone/iPad/Mac)
2. Use the `memory` tool for agent-internal notes
3. Use the `obsidian` skill for Markdown-native knowledge management

---

## 2. Apple Reminders (`remindctl`)

Manage Apple Reminders from the terminal. Tasks sync via iCloud.

### Prerequisites

- **macOS** with Reminders.app
- Install: `brew install steipete/tap/remindctl`
- Check status: `remindctl status` / Authorize: `remindctl authorize`

### Quick Reference

```bash
remindctl                    # Today's reminders
remindctl today              # Today
remindctl tomorrow           # Tomorrow
remindctl week               # This week
remindctl overdue            # Past due
remindctl all                # Everything
remindctl 2026-01-04         # Specific date

remindctl list               # List all lists
remindctl list Work          # Show specific list
remindctl list Projects --create    # Create list
remindctl list Work --delete        # Delete list

remindctl add "Buy milk"
remindctl add --title "Call mom" --list Personal --due tomorrow
remindctl add --title "Meeting prep" --due "2026-02-15 09:00"

remindctl complete 1 2 3          # Complete by ID
remindctl delete 4A83 --force     # Delete by ID

remindctl today --json       # JSON output
remindctl today --plain      # TSV format
remindctl today --quiet      # Counts only
```

### Due Time vs Alarm

`--due` and `--alarm` are different fields:
- `--due` sets the reminder's due date/time
- `--alarm` sets the EventKit alarm/notification trigger

For a reminder due at 2:00 PM with a notification 30 minutes earlier:

```bash
remindctl add --title "Hairdresser" --due "2026-05-15 14:00" --alarm "2026-05-15 13:30"
```

Consult `references/apple-reminders.md` for detailed date format reference and JSON output shape.

### Rules

1. When user says "remind me", clarify: Apple Reminders (syncs to phone) vs agent cronjob alert
2. Always confirm reminder content and due date before creating
3. Use `--json` for programmatic parsing

---

## 3. iMessage (`imsg`)

Read and send iMessage/SMS via macOS Messages.app.

### Prerequisites

- **macOS** with Messages.app signed in
- Install: `brew install steipete/tap/imsg`
- Grant Full Disk Access for terminal
- Grant Automation permission for Messages.app when prompted

### Quick Reference

```bash
# List chats
imsg chats --limit 10 --json

# View history
imsg history --chat-id 1 --limit 20 --json
imsg history --chat-id 1 --limit 20 --attachments --json

# Send messages
imsg send --to "+141****1212" --text "Hello!"
imsg send --to "+141****1212" --text "Check this out" --file /path/to/image.jpg
imsg send --to "+141****1212" --text "Hi" --service imessage
imsg send --to "+141****1212" --text "Hi" --service sms

# Watch for new messages
imsg watch --chat-id 1 --attachments
```

### Service Options

- `--service imessage` — Force iMessage (requires recipient has iMessage)
- `--service sms` — Force SMS (green bubble)
- `--service auto` — Let Messages.app decide (default)

### Rules

1. **Always confirm recipient and message content** before sending
2. **Never send to unknown numbers** without explicit user approval
3. **Verify file paths** exist before attaching
4. **Don't spam** — rate-limit yourself
5. **Example workflow:** see `references/imessage.md`

---

## 4. Find My (Apple)

Track Apple devices and AirTags via FindMy.app using AppleScript + screen capture.

### Prerequisites

- **macOS** with Find My app and iCloud signed in
- Screen Recording permission for terminal
- **Optional:** Install `peekaboo` for better UI automation: `brew install steipete/tap/peekaboo`

### Quick Reference

```bash
# Open Find My
osascript -e 'tell application "FindMy" to activate'
sleep 3

# Take screenshot
screencapture -w -o /tmp/findmy.png

# Switch to Devices tab
osascript -e 'tell application "System Events"
    tell process "FindMy"
        click button "Devices" of toolbar 1 of window 1
    end tell
end tell'

# Switch to Items tab (AirTags)
osascript -e 'tell application "System Events"
    tell process "FindMy"
        click button "Items" of toolbar 1 of window 1
    end tell
end tell'
```

Then use `vision_analyze` to read the screenshot content.

### With Peekaboo (Recommended)

```bash
osascript -e 'tell application "FindMy" to activate'
sleep 3
peekaboo see --app "FindMy" --annotate --path /tmp/findmy-ui.png
peekaboo click --on B3 --app "FindMy"
peekaboo image --app "FindMy" --path /tmp/findmy-detail.png
```

### Limitations

- FindMy has **no CLI or API** — must use UI automation
- AirTags only update location while the FindMy page is actively displayed
- Screen Recording permission required for screenshots
- AppleScript UI automation may break across macOS versions

See `references/findmy.md` for the full tracking workflow and cronjob pattern.

---

## 5. macOS Computer Use (`computer_use` tool)

Drive the macOS desktop in the background — screenshots, mouse, keyboard, scroll, drag — without stealing the user's cursor, keyboard focus, or Space.

> **Important:** Prefer `browser_*` tools for web automation. Use `computer_use` specifically when the task needs the user's actual Mac apps (native Mail, Messages, Finder, Figma, Logic, games).

### Canonical Workflow

```
computer_use(action="capture", mode="som", app="Safari")
   → Returns screenshot + numbered overlays + AX index

computer_use(action="click", element=7)
computer_use(action="click", element=7, capture_after=True)
```

### Key Principles

1. **Never `raise_window=True`** unless explicitly asked
2. **Scope captures to an app** (`app="Safari"`)
3. **Don't switch Spaces**
4. **Never click permission dialogs, password prompts, or 2FA**
5. **Never type secrets**

See `references/macos-computer-use.md` for the full action reference including capture modes, drag & drop, scroll, keyboard shortcuts, text input, safety rules, and failure modes.

---

## Related Skills

- `obsidian` — Markdown-native knowledge management (alternative to Apple Notes)
- `notion` — Cloud-based notes and databases
- `cronjob` tool — for scheduling agent alerts (alternative to Apple Reminders)


## Auto-evolved patterns

*Добавлено Skill Auto-Evolution Engine (2026-06-11)*

- блять ну естественно нужно закончить миграцию!!!!
- ладно. тебе не нужно обновиться?
- [Note: model was just switched from llama-3.3-70b-versatile to glm-5.1 via Ollama Cloud. Adjust your self-identification accordingly.]

проверка связи

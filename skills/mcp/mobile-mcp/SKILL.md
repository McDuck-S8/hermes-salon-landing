---
name: mobile-mcp
description: MCP server for automating iOS/Android mobile devices — screenshots, clicks, text input, app launch, swipe gestures.
tags: [mobile, mcp, automation, tool]
domain: tools
difficulty: medium
---

# Mobile MCP

MCP server for mobile device automation (iOS and Android) via the Model Context Protocol.

## What It Is

mobile-mcp exposes device control capabilities as MCP tools. It lets AI agents interact with real phones and tablets through screenshots, taps, text input, and gestures.

- **Repo:** https://github.com/mobile-next/mobile-mcp
- **Tech:** TypeScript, Node.js 18+, MCP SDK, Playwright, Express, mobilewright
- **Devices:** iOS (via Xcode/WDA), Android (via ADB), both USB and remote

## Features

- `take_screenshot` — capture device screen
- `click` — tap on screen coordinates
- `type_text` — input text into focused fields
- `launch_app` — open an app by package/bundle ID
- `swipe` — perform swipe gestures (up/down/left/right/custom)
- `list_apps` — enumerate installed apps

## When to Use

- Automating apps **without official APIs** (testing, workflows, QA)
- Secondary tool — NOT a replacement for Telegram Bot API or similar first-class APIs
- Mobile app testing and interaction verification
- Automating repetitive phone workflows

## Installation

```bash
npx -y @mobilenext/mobile-mcp@latest
```

Or add to MCP client config:

```json
{
  "mcpServers": {
    "mobile": {
      "command": "npx",
      "args": ["-y", "@mobilenext/mobile-mcp@latest"]
    }
  }
}
```

## Device Setup

- **Android:** Enable USB debugging, connect via ADB
- **iOS:** Requires Xcode + WebDriverAgent, or use Appium as bridge
- Ensure `adb` or `idevice_id` is in PATH

## Integration Notes

1. This is a **secondary tool** — use APIs when available (e.g., Telegram Bot API > mobile-mcp for Telegram)
2. MCP client must support the mobile-mcp tool schema
3. Screenshots can be analyzed by vision-capable models for screen understanding
4. Latency: device commands have network/USB overhead (1-3s per action)
5. Pair with screenshot + vision for closed-loop automation: screenshot → reason → act → repeat

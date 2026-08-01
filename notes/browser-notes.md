# Browser Tabs & Extensions Notes — 2026-05-26

## Установленные расширения (Chromium profile: data/chrome-debug-profile)

### 1. BrowserOS Assistant v0.0.102.0
- ID: bflpfmnmnokmjhmgnolecpppdbdophmk
- Агентный браузер с ИИ — "Open Source Agentic Browser"
- Permissions: topSites, storage, unlimitedStorage, scripting, tabs, tabGroups, sidePanel, bookmarks, history, browserOS, alarms, webNavigation, downloads
- Side panel: "Agent at your service" — автоматизация задач голосом/текстом
- MCP server: http://127.0.0.1:9000/mcp (пока offline)
- Подключение к OpenClaw: {"mcpServers": {"browseros": {"url": "http://127.0.0.1:9000/mcp"}}}
- Settings: chrome://browseros/settings (BYOK — свои API ключи, включая Ollama)
- Externally connectable: api.browseros.com

### 2. BrowserOS Controller v1.1.0.0
- ID: nlnihljpboknmfagkikhkdblbedophja
- API bridge для BrowserOS Server
- Permissions: tabs, activeTab, bookmarks, history, scripting, storage, tabGroups, webNavigation, downloads, browserOS, alarms

### 3. BrowserOS Feedback v52.0.0.0
- ID: adlpneommgkgeanpaekgoaolcpncohkf
- Bug reports и feature requests

### 4. Google Drive for Desktop v3.10
- ID: lmjegmlicamnimmfhcmpkclmigmmcbeh
- Синхронизация Google Drive/Docs
- Author: drive-desktop-client-extensions@google.com
- Permissions: nativeMessaging, offscreen
- Host: docs.google.com, drive.google.com

### 5. TeraBox Download Assistant v0.0.5
- ID: dpadflhmiohjfhhaehelneimpllfbpcg
- Permissions: nativeMessaging, downloads

## Открытые вкладки (интересные)

### GitHub: browser-use/browser-harness ⭐13.7k
- URL: https://github.com/browser-use/browser-harness
- Self-healing CDP harness для LLM — уже установлен локально
- Архитектура: ~1k строк, 4 core файла
- Agent пишет недостающие хелперы прямо во время выполнения
- Free Browser Use Cloud: 3 concurrent браузера, прокси, решение captcha

### BrowserOS Welcome
- URL: chrome://browseros-welcome
- Приветственная страница с инструкциями по настройке

### BrowserOS MCP Settings
- URL: chrome-extension://bflpfmnmnokmjhmgnolecpppdbdophmk/app.html#/settings/mcp
- MCP server endpoint: http://127.0.0.1:9000/mcp
- Quick setup для: Claude Code, Gemini CLI, Codex, Claude Desktop, OpenClaw
- Status: Service Unavailable (не запущен)

### Chrome AI History Search
- URL: chrome://settings/ai/historySearch
- Новая фича Chromium — ИИ-поиск в истории браузера

## Мусорные вкладки (можно закрыть)
- 5× Tavily auth pages (регистрация завершена)
- 3× temp email services (guerrillamail, temp-mail.org, tempmail.plus)

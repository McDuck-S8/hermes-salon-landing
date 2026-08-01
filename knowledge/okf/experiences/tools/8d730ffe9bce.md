---
type: tools
title: "[web_surfer.py] web_surfer.py — Антидетект-сёрфинг v4.
Три слоя:
  1. urllib + p"
timestamp: 2026-07-18T18:29:53.823333
confidence: 0.500
verification_method: manual
source_table: kc_entries
importance: 6
tags:
  - script
  - web_surfer.py
resource: scripts
---

[web_surfer.py] web_surfer.py — Антидетект-сёрфинг v4.
Три слоя:
  1. urllib + proxy (быстрое чтение, без JS)
  2. undetected-chromedriver (антидетект, полный Chrome)
  3. Playwright + stealth (альтернатива)

Использование:
    from web_surfer import WebSurfer
    ws = WebSurfer()
    r = ws.read_page("https://trav

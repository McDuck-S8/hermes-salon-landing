---
name: hacker-log
description: "Auto-generated from HACKER_LOG.md"
trigger: "When user asks about HACKER_LOG concepts"
usage: hacker-log
Revisit: 2026-07-31
---

# HACKER_LOG — Обходы барьеров

## Формат записи
### [Дата] Барьер → Обход
**Барьер:** что мешало
**Обход:** что сделал
**Эффективность:** работает/не работает

---

## [2026-06-23] Telegram API заблокирован → SOCKS5 через V2RayN
**Барьер:** api.telegram.org недоступен напрямую из РФ
**Обход:** V2RayN → socks5://127.0.0.1:10806 → aiohttp-socks
**Эффективность:** работает

## [2026-06-23] Happ VPN ≠ V2RayN → не путать порты
**Барьер:** Happ VPN на порту 10808 не проксирует TG
**Обход:** V2RayN на порту 10806 работает
**Эффективность:** работает — проверено curl + aiohttp

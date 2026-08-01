# PROCEDURAL SKILLS — Рефлексы Hermes

Детерминированные цепочки: **Триггер → Действие → Запись**.
Никакого LLM. Видел → Сделал → Записал.

---

## КОНФИГУРАЦИЯ СИСТЕМЫ

### Прокси
- **HTTP прокси:** `http://127.0.0.1:10809` (основной)
- **SOCKS5:** `socks5://127.0.0.1:10806` (нерабочий)
- **V2RayN:** GUI-приложение, не запускается из bash
- **ВАЖНО:** Все curl/httpx вызовы к Telegram API ДОЛЖНЫ использовать `--proxy http://127.0.0.1:10809`

### Telegram API
- **Базовый URL:** `https://api.telegram.org`
- **Статус-коды:** 200 (OK), 302 (редирект), 401 ( Unauthorized), 404 (Not Found)
- **Утилита:** `scripts/telegram_helper.py` — централизованный доступ через прокси

### Порты
- FreeQwenApi: 3264
- FreeDeepseekAPI: 9655
- Ollama: 11434

---

## TRIGGER-001: Сеть умерла

**Триггер:** `requests` / `urllib` / `httpx` → `ConnectionError` / `Timeout` / `ConnectTimeout` при обращении к внешним API

**Действие:**
1. Переключить прокси (сменить `activeServer` в V2RayN или перезапустить `proxy_bridge.py` на альтернативный SOCKS5)
2. Подождать 10 секунд
3. Проверить связь (GET `https://httpbin.org/ip`)
4. Если снова ошибка → залогировать и эскалировать

**Запись:**
- `cache/procedural_feedback.jsonl` → `{trigger, action, result, success}`
- `cache/ALERTS.md` → если провал

---

## TRIGGER-002: Gateway мёртв

**Триггер:** Порт gateway (11434 / 8080) не отвечает ИЛИ процесс `hermes-gateway` не найден в `tasklist`

**Действие:**
1. Найти и убить stale lock файлы (`cache/*.lock`)
2. `taskkill /F` все zombie-процессы gateway
3. Подождать 3 сек
4. Перезапустить gateway
5. Подождать 10 сек, проверить порт

**Запись:**
- `cache/procedural_feedback.jsonl` → success/fail
- `cache/ALERTS.md` → если провал

---

## TRIGGER-003: Cron job в error 3 раза подряд

**Триггер:** В `cron/jobs.json` поле `last_status == "error"` для одного и того же job_id 3+ раза подряд (считается по `repeat.completed` и `last_error`)

**Действие:**
1. Прочитать `jobs.json`
2. Для каждого job с `last_status == "error"`:
   - Если ошибка повторялась 3+ раза подряд:
     - Сдвинуть `next_run_at` на +1 час от текущего времени
     - Залогировать: `{job_id, error, action: "delayed_1h"}`

**Запись:**
- `cache/procedural_feedback.jsonl`
- Обновить `next_run_at` в `jobs.json`

---

## TRIGGER-004: Goal заблокирован > 24 часов

**Триггер:** В файле состояния целей (например `cache/goals.json` или `cron/proactive_doer_state.json`) есть goal со `status: "blocked"` и время блокировки > 24ч

**Действие:**
1. Прочитать состояние целей
2. Если goal в `blocked` > 24ч:
   - Залогировать в `cache/ALERTS.md`: `[ESCALATION] Goal "{name}" blocked for {N}h — needs human`
   - Обновить `feedback_store`

**Запись:**
- `cache/ALERTS.md`
- `cache/procedural_feedback.jsonl`

---

## TRIGGER-005: Порт сервиса мёртв (FreeQwenApi / FreeDeepseekAPI / Ollama)

**Триггер:** Конкретный порт не отвечает (netstat не показывает LISTENING)

**Действие:**
1. Убить процесс на порту (`taskkill /F /PID`)
2. Подождать 2 сек
3. Перезапустить сервис командой из конфигурации
4. Подождать 5 сек, проверить порт
5. Если не запустился → ALERT

**Конфигурация портов:**
| Порт | Сервис | Команда перезапуска |
|------|--------|---------------------|
| 3264 | FreeQwenApi | `cd D:/Portable_Soft/FreeQwenApi && node index.js` |
| 9655 | FreeDeepseekAPI | `cd D:/Portable_Soft/FreeDeepseekAPI && node server.js` |
| 11434 | Ollama | `ollama serve` |

---

## TRIGGER-006: Disk usage > 80%

**Триггер:** Диск D: заполнен > 80%

**Действие:**
1. Найти файлы > 100MB в `cache/`
2. Залогировать найденные
3. Если > 500MB → ALERT пользователю

---

## TRIGGER-007: Memory usage > 80%

**Триггер:** Оперативная память использована > 80%

**Действие:**
1. Залогировать потребление
2. Найти топ-5 процессов по памяти
3. ALERT пользователю

---

## TRIGGER-008: Telegram API недоступен

**Триггер:** `telegram` или `gateway` лог содержит `ConnectionError` / `timeout` / `NetworkError` к Telegram API

**Действие:**
1. Переключить прокси (TRIGGER-001)
2. Подождать 10 сек
3. Перезапустить gateway (TRIGGER-002)
4. Проверить связь с Telegram API
5. Если не помогло → ALERT

---

## Формат feedback_store

Каждая строка в `cache/procedural_feedback.jsonl`:
```json
{
  "timestamp": "2026-06-27T15:30:00",
  "trigger": "port_3264_dead",
  "action": "restart_FreeQwenApi",
  "result": "restarted",
  "success": true
}
```

## Формат ALERTS.md

```markdown
[2026-06-27 15:30:00] [ESCALATION] FreeQwenApi port 3264 failed to restart after 3 attempts
[2026-06-27 16:00:00] [CRON] Job nightly-self-analysis error 3x — delayed 1h
```

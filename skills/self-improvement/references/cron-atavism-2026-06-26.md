# Cron = Atavism (2026-06-26)

## User Correction

**User: "cron jobs это атавизм... настраивай всё по события, так система будет живой... живость по будильнику cron jobs не вздумай настраивать"**

## Principle

Cron = мёртвый механизм. События = жизнь. Система должна реагировать на МИР, а не на ЧАСЫ.

## Wrong Patterns

- "запусти cron каждые 5 минут проверять здоровье"
- "cron job для сбора данных"
- "cron job для мониторинга"

## Right Patterns

- "когда что-то ломается — событие → реакция → исправление"
- "данные собираются когда появляются"
- "мониторинг происходит когда система чувствует изменения"

## Exception

Heartbeat daemon (event_daemon.py) — это пульс, не таймер. Он бьётся постоянно, но реагирует на СОСТОЯНИЕ, а не на ВРЕМЯ.

## Architecture

```
sensor_array.py (7 датчиков)
    ↓ sweep каждые 60 сек
event_daemon.py (пульс)
    ↓ fire events
event_bus.py (очередь)
    ↓ classify
chain_executor.py (цепочки)
    ↓ execute
self_system.py (действия)
```

## Key Files

- `scripts/sensor_array.py` — 7 sensors: time, system, processes, files, cron, knowledge, user
- `scripts/event_daemon.py` — heartbeat daemon, beat every 60s
- `scripts/event_bus.py` — event→action mapping
- `scripts/chain_executor.py` — chain execution with severity levels
- `scripts/event_sense.py` — event emitter (push, not poll)
- `scripts/event_registry.py` — event type definitions

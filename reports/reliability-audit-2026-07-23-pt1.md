# Аудит достоверности Hermes Agent
## Условие: недостаточная/недостоверная информация = недостоверные выводы
## Дата: 2026-07-23

## 1. KC — Knowledge Cube

### Состав KC (8,744 entries)

| Категория | Количество | % | Достоверность |
|---|---|---|---|
| Auto-generated suggestions `[suggestion:*]` | 5,421 | 62.0% | ❌ Самогенерация |
| Cron health / agent decisions (uncategorized) | ~3,251 | 37.2% | ⚠️ Частично системные логи |
| Hand-written patterns/facts `[pattern]`/`[fact]` | 46 | 0.5% | ✅ Ручные |
| Skill index entries | 26 | 0.3% | ✅ Технически верны |
| User messages | 9 (24h) | ~0.1% | ✅ Но недостаточно |

**Ключевое открытие: 62% KC — это Self-Improvement Loop, записывающий свои же**
**лог-паттерны в виде suggestions.**

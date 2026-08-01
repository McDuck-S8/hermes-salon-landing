# Cross-Cube Findings — 2026-06-11

Первая сессия формального кросс-куб анализа. Результаты, которые стоит помнить.

## Найденные паттерны

### 1. Unknown → source-классификация
- **660 unknown → 0** за один прогон
- Метод: не содержание (raw_text), а source (откуда запись пришла)
- state_db = user_query (430)
- script_* = script_result (84)
- lavra_* = lavra_knowledge (74)
- dimension_proposals = dimension_proposal (51)
- **Аксиома:** Никогда не смотреть в raw_text для определения типа записи

### 2. Misclassification: improvement_suggestions
- 329 записей помечены как `failure`
- На самом деле это suggestions — предложения исправлений на основе логов
- Поправлено: → `system_note`
- Вывод: не всё что говорит об ошибке — само ошибка

### 3. Entity orphans (860/2362 = 36%)
- 860 записей KC не содержат ни одного имени сущности из EE
- Из них: 356 failure, 313 user_query
- **Failure-записи без сущностей** — ошибки записываются без контекста

### 4. Entity ghosts (275 из 552)
- 275 сущностей есть в EE, но ни разу не встречаются в KC
- Из них 244 Проекта — проекты существуют как сущности, но не наполняют знание
- **Призраки:** Александр (mention_count=1), Hermes Agent (Я) (only 7)
- **"Люди" не люди:** 17 entity_type=Человек, но реальный человек только Александр. Остальные — боты и технические ID

### 5. Entity failure ratio
| Entity | Failure rate | Примечание |
|--------|------------|-----------|
| Bad Gateway | 85.7% | Системная проблема |
| Health | 66.7% | (шум от substring "health") |
| DuckDuckGo | 37.5% | Поисковый API |
| SQLite | 16.1% | DB-ошибки |
| Opencode | 15.5% | Заметно |

### 6. Bad gateway — пятничная болезнь
- Все 7 случаев — в пятницу
- Часы 3-5 ночи + 16:00
- spawn EINVAL — Windows не может запустить процесс

### 7. EE relationship types
- co_occurs_with: 8146 (доминанта)
- uses: 1985
- belongs_to: 1280
- **watches_over: 1** — уникальная связь (Совесть → Я)
- **listens_to: 1** — уникальная связь (Я → Совесть)

### 8. Fler per-message
- Негативные сообщения: tone=-0.26, tension=1.7 (4× выше позитивных)
- Позитивные: tone=+0.29, tension=0.4
- Нейтральные: engagement=6.1 (выше всех) — нейтрал = рабочий режим
- Новых fler-сессий за 7д: 0

## Методология

Кросс-куб анализ = взять ось из одного куба и пройтись по ней через другой куб:

1. **Temporal:** ts из KC × ts из Fler (по часам) — слабый сигнал из-за разной гранулярности
2. **Semantic:** entity names из EE × raw_text из KC — сильный сигнал
3. **Typological:** entity types из EE × domains из KC — средний сигнал
4. **Tonal:** tone/engagement из Fler × outcome из KC — слабый сигнал

**Лучший мост:** semantic join по entity names. Остальные — для подтверждения.

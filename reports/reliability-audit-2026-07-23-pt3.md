## 3. Semantic Memory (469 entries)

### Coverage: 469 / 8,744 KC = 5.4%
Из 5,421 suggestion-записей — 0 в semantic memory.
Из ~3,251 "other" — 469 в semantic memory.

**Реальная покрытие:** 469 / ~3,251 (не-suggestion KC) = 14%.
**Реальная покрытие от всех KC:** 5%.
**Эффективное покрытие для поиска:** при RAG запросе semantic search видит 5% данных.

### GIGO
Никто не обновляет semantic memory при добавлении в KC.
Схема БД не имеет `source_type` — нельзя отфильтровать suggestion vs knowledge.
469 entries имеют однородный metadata — все `{"source": "research", "category": "tech"}`.

**Вердикт: Semantic memory покрывает 5% KC. При поиске я слеп к 95% данных.**

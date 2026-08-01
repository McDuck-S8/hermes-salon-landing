# Inline Event-Driven Pipeline: uncategorized → new domain

## Принцип

НЕ cron. НЕ polling. НЕ tight loop. Только событие.

Когда `auto_tagger.py` классифицирует entry как `axis_domain='uncategorized'` — ОН ЖЕ проверяет кластеры и создаёт домен. В том же процессе. Без внешних триггеров.

## Архитектура

```
entry → auto_tagger.score_entry()
                ↓
        best_domain = 'uncategorized'
                ↓
        inline: check_uncategorized_clusters(text)
                ↓
        кластер найден (3+ entry с похожими словами) → создать домен
                ↓
        добавить в domain_definitions.yaml → register white spot → переклассифицировать
```

## Где реализовано

D:\Portable_Soft\hermes\scripts\auto_tagger.py — в цикле сохранения (`main()`, после `UPDATE`):

```python
# Псевдокод того, что должно быть в auto_tagger.py:
if entry['axis_domain'] == 'uncategorized':
    # 1. Fire event
    EventMonitor().record(Event(
        event_type='uncategorized_detected',
        data={'entry_id': entry['id'], 'text': raw_text[:200]},
        source='auto_tagger',
        priority=3
    ))
    # 2. Check clusters
    clusters = check_uncategorized_clusters(raw_text)
    for cluster in clusters:
        if cluster.size >= 3:
            new_domain = generate_domain_name(cluster)
            add_domain_to_yaml(new_domain, cluster.keywords)
            register_white_spot(new_domain)
            # 3. Re-classify entries in this cluster
```

## Алгоритм кластеризации

Простой (без sklearn):
1. Собрать все entry с `axis_domain='uncategorized'`
2. Извлечь слова из `raw_text`, отфильтровать стоп-слова
3. `collections.Counter` → top 10 частотных слов
4. Если 3+ entry содержат top слово → это кластер
5. Имя домена: транслитерация русского слова (Игры→igry, Финансы→finansy)

## Почему не cron

- При поступлении entry в uncategorized кластер может сформироваться сразу
- Ждать cron (даже 2m) — значит терять контекст
- При 0 uncategorized entry cron будет делать пустой прогон — бессмысленно
- Событийный подход: работа происходит ТОЛЬКО когда есть данные

## Статус реализации (2026-06-11)

- [x] Создан skill `uncategorized-to-domain` 
- [x] Создан `scripts/uncategorized_watcher.py` (для ручной диагностики)
- [ ] ПАТЧ auto_tagger.py: инлайн-проверка кластеров — НАЧАТ агентом, прерван

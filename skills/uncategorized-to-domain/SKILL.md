---
name: uncategorized-to-domain
description: Monitor uncategorized entries, detect clusters, auto-create new domains, seed and explore
category: self-improvement
---

# Uncategorized → New Domain Pipeline

Автоматический конвейер: из uncategorized → новый домен.

## Trigger
**ТОЛЬКО ПО СОБЫТИЮ. НИКАКИХ РАСПИСАНИЙ.**

Срабатывает автоматически, когда `auto_tagger.py` классифицирует entry как 'uncategorized':

1. `auto_tagger.py` сохраняет entry с `axis_domain='uncategorized'`
2. В момент сохранения — проверка: есть ли 3+ uncategorized entry с похожим текстом?
3. Если кластер найден → создать новый домен → переклассифицировать

Ручной запуск (диагностика): `python scripts/uncategorized_watcher.py`

## Logic

1. **SELECT все entries с axis_domain='uncategorized'** за последние N дней
2. **Кластеризация**: группировка по общим ключевым словам/темам
   - Простой алгоритм: TF-IDF + cosine similarity между raw_text
   - Порог: cluster_size >= 3 для предложения нового домена
3. **Generate domain name**: из top keywords кластера
4. **Добавить в domain_definitions.yaml**: новый блок с keywords из кластера
5. **Register white spot**: `white_spot_clusters` → новый кластер
6. **Reclassify**: `python scripts/auto_tagger.py --force`
7. **Seed**: если после реклассификации entries < 5 → delegate_task для заполнения

## Implementation

```python
# Псевдокод
def find_uncategorized_clusters():
    entries = fetch_uncategorized()
    clusters = cluster_by_similarity(entries)  # TF-IDF + cosine
    for cluster in clusters:
        if len(cluster) >= 3:
            new_domain = generate_domain_name(cluster)
            add_to_domain_definitions(new_domain, cluster.keywords)
            register_white_spot(new_domain)
            reclassify()
            if count_entries(new_domain) < 5:
                delegate_seed(new_domain)
```

## Принцип: классификация по источнику, а не по содержанию

Ключевой урок (2026-06-11): **когда запись не классифицируется по содержанию — смотри на source.**

При импорте в Knowledge Cube каждая запись получает `source` — откуда она пришла.
Source несёт информацию о ТИПЕ записи, даже если текст не содержит success/failure ключей.

Применение:
1. Вместо TF-IDF по тексту — сделай `SELECT source, COUNT(*) FROM experiences GROUP BY source`
2. Source = `state_db` → `user_query`. Source = `dimension_proposals` → `dimension_proposal`
3. Source = `lavra_*` → `lavra_knowledge`. Source = `script_*` → `script_result`
4. Source = `file:*` → `file_import`. Source = `git:*` → `git_commit`

Этот подход разобрал 660 unknown записей в 0, когда keyword-классификация по тексту сработала на 1/661.

Подробнее: `references/source-first-classification.md`

## Pitfalls
- Не создавать домен из 1 записи — может быть шум
- Проверять пересечение с существующими доменами
- После добавления домена — удалять его из uncategorized
- **НИКАКИХ РАСПИСАНИЙ** — событие, не cron. См. `references/inline-event-driven-pipeline.md`
- **Source-first**: если автоклассификатор не может определить домен — проверь source записи, а не только текст. Source уже содержит подсказку типа

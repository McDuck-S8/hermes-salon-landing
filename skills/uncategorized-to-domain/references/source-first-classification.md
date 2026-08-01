# Source-First Classification

**Принцип:** классифицируй записи Knowledge Cube по полю `source`, а не по содержанию `raw_text`.

## Проблема

`verify_outcomes.py` пытался классифицировать 661 unknown запись по ключевым словам success/failure в тексте. Результат: 1/661 (0.15%). Причина: записи не содержали success/failure — они были пользовательскими запросами и результатами работы скриптов.

## Решение

Поднять уровень абстракции: не читать текст — читать трассу. Каждая запись пришла откуда-то (source), и source определяет её тип.

## Source → Outcome Map

| Source | Category | Примерное кол-во |
|--------|----------|-----------------|
| `state_db` | user_query | 430 |
| `script_*` | script_result | 84 |
| `lavra_*` | lavra_knowledge | 74 |
| `dimension_proposals` | dimension_proposal | 51 |
| `auto_research` | auto_research | 10 |
| `agent_decisions` | agent_decision | 3 |
| `gap_filler`, `improvement_suggestions`, etc. | system_note | 8 |
| `file:*` | file_import | редкие |
| `git:*` | git_commit | редкие |
| `skill-indexer` | indexing_result | редкие |

## Когда применять

- Когда `axis_outcome='unknown'` и keyword-классификация не работает
- Когда записи приходят из автоматических импортёров (state_db, Lavra)
- Скрипты записывают результат своей работы — это `script_result`, не success/failure
- Пользовательские запросы — это `user_query`, не success/failure

## Когда НЕ применять

- Когда записи — реальные результаты действий (success/failure)
- Когда текст содержит явные success/failure маркеры
- Для классификации доменов (axis_domain) — там нужен TF-IDF+cosine

## Код

```python
SOURCE_OUTCOME_MAP = {
    'state_db': 'user_query',
    'dimension_proposals': 'dimension_proposal',
    'lavra_decision': 'lavra_knowledge',
    'lavra_learned': 'lavra_knowledge',
    'lavra_fact': 'lavra_knowledge',
    'lavra_pattern': 'lavra_knowledge',
    'lavra_investigation': 'lavra_knowledge',
    'auto_research': 'auto_research',
    'gap_filler': 'system_note',
    'agent_decisions': 'agent_decision',
    'improvement_suggestions': 'system_note',
}

# script_* → script_result
# file:*   → file_import
# git:*    → git_commit
```

## История

2026-06-11: 660 unknown → 0 за один SQL UPDATE. Пользователь подсказал: "поднимись на уровень выше и посмотри откуда пришло". Результат: ни одной unknown не осталось.

# Will Self-Expansion Pattern

Реализация механизма саморасширения воли в crystal.py.

## Проблема

Предопределённые действия воли конечны. После выполнения improvement_suggestions, dimension_proposals и инициализации Fler'а воля сказала "нет действий". Но оставались 448 сирот в state_db.

## Решение: _self_discover()

Функция сканирует orphan_by_source в поиске source, которые:
1. Не были обработаны ранее (не в _load_will_history())
2. Имеют >5 сирот
3. Содержат извлекаемые паттерны в 5 образцах

```python
def _self_discover(snap, done_sources):
    """Саморасширение: сканирует сирот и находит новые source для экстракции."""
    orphans_raw = snap['kc'].get('orphan_by_source', {})
    discovered = []
    kc = sqlite3.connect(KC)
    k = kc.cursor()
    
    for src, cnt in sorted(orphans_raw.items(), key=lambda x: -x[1]):
        if cnt < 5 or src in done_sources:
            continue
        k.execute("SELECT raw_text FROM experiences WHERE source=? AND raw_text IS NOT NULL AND raw_text != '' LIMIT 5", (src,))
        samples = [r[0] for r in k.fetchall() if r[0]]
        combined = ' '.join(samples)
        
        has_pattern = False
        patterns_found = []
        if re.findall(r"domain\s+'([a-z][a-z0-9_-]+)'", combined, re.IGNORECASE):
            has_pattern = True
        if re.findall(r'\[([a-z]+):([a-zA-Z0-9_-]+)\]', combined):
            has_pattern = True
        if re.findall(r'\b([A-Z][a-z]+[A-Z][a-zA-Z]{2,})\b', combined):
            has_pattern = True
        
        if has_pattern:
            discovered.append({...})
    return discovered
```

## Персистентная история воли

История действий сохраняется в KC с source='crystal_will':

```python
def _save_will_history(action_id, result_text):
    k.execute("INSERT INTO experiences (ts, raw_text, hash, ..., source) 
               VALUES (?,?,?,?,?,'crystal_will','will_action','crystal_will')",
              (ts, f"[will:{action_id}] {result_text}", hash, ...))
```

Загрузка при старте: _load_will_history() парсит последние 5 записей из KC.

## Результат после первого саморасширения

- Source: state_db (611 записей пользовательских диалогов)
- Извлечено: 1657 сущностей
- Эффект: сироты 448→299 (остались только user-запросы без имён)
- Состав: 154 code_terms, 92 UPPERCASE константы, 39 CamelCase, 3% с цифрами
- Шум: ~40% общеупотребительных слов (побочный эффект)

## Вывод

Саморасширение позволяет воле выйти за границы предопределённых действий и найти новые источники знания. Ключевое: не ждать "разрешения" на новый source — если в нём есть данные, воля должна их взять. Пользователь подтвердил: "пускай идет как идет... значит возникла необходимость".

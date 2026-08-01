# Cross-Cube Bridges

Метод: прогнать данные одного куба через другие. Не ожидать что увидишь — может выйти неожиданное.

## Принцип

Каждый куб видит мир под своим углом. Knowledge Cube знает что произошло. Entity Cube знает кто и что участвовало. Fler Cube знает эмоциональный фон. Fabric знает что записано.

Когда данные одного куба пересекаются с другим, появляются паттерны, невидимые ни одному кубу по отдельности.

## Какие мосты строить

### KC → EE (сущности в записях)
```
KC entry.raw_text → искать имена EE entities → какие outcomes у каких сущностей
```
Находки:
- 860 KC-записей не упоминают ни одну из 552 сущностей EE — сироты
- 275 сущностей EE ни разу не упомянуты в KC — призраки
- Александр (пользователь) — призрак, 1 упоминание в EE, 0 в KC

### KC → FL (временной)
```
KC entry.ts по часам → Fler session.ts по часам → какие outcome в часы с каким aftertaste
```
Находки:
- Fler and KC почти не пересекаются по времени (разная гранулярность)
- После source-классификации: user_query и success — единственные outcomes, совпадающие с Fler часами

### EE → FL (сущности по настроению)
```
EE entities → искать в Fler raw_data → какие сущности в позитивных/негативных сессиях
```
Находки:
- Negative сессии: выше energy (3.1 vs 2.7) и tension (1.7 vs 0.4)
- Neutral сессии: самая высокая engagement (6.1)

### KC domain × EE type
```
KC domain → какие entity types упоминаются в записях этого домена
```
Находки:
- Все домены доминируются "Платформа" — вероятно, слишком широкая категория
- file_ops: Платформа(556), Домен знаний(178), Проект(147), Технология(40)

### Failure ratio per entity
```
Для каждой entity: сколько раз упомянута в failure vs total
```
Находки:
- bad gateway: 85.7% failure (6/7)
- health: 66.7% failure (но catch: "health" как подстрока)
- sqlite: 16.1% failure
- opencode: 15.5% failure

## SQL-шаблоны

### Сущности в KC
```sql
SELECT e.name, COUNT(*) as hits
FROM experiences kc
JOIN entities e ON kc.raw_text LIKE '%' || e.name || '%'
WHERE kc.axis_outcome = 'failure'
GROUP BY e.name
ORDER BY hits DESC
```

### KC по часам × outcome
```sql
SELECT axis_time_hour, axis_outcome, COUNT(*)
FROM experiences
GROUP BY axis_time_hour, axis_outcome
ORDER BY axis_time_hour
```

### Источники failure
```sql
SELECT source, COUNT(*)
FROM experiences
WHERE axis_outcome = 'failure'
GROUP BY source
ORDER BY COUNT(*) DESC
```

## Правила

1. **Не ищи подтверждение — ищи пересечение.** Если результат ожидаем — ты не поднялся на уровень выше. Настоящая находка всегда неожиданна.
2. **Если результат непонятен — это нормально.** "Пока ничего не понятно но продолжай".
3. **Каждый куб — линза.** Одна запись в разных кубах выглядит по-разному. Смена линзы даёт новое измерение.
4. **Сироты и призраки — самые ценные находки.** Запись без сущности или сущность без записей — это граница системы.

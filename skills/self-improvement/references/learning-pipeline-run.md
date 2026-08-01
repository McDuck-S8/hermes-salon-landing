# Learning Pipeline — Quick Run

Полный прогон системы обучения Hermes. Выполнять, когда пользователь просит "прогони систему для обучения" или как регулярное обслуживание.

## Pipeline Sequence

Выполнять в следующем порядке. Отчёт по каждому шагу — пользователю.

### [1] Events Processing (автоматически)
```python
from scripts.event_evolution import process_pending_events
result = process_pending_events()
# Возвращает {processed: N, errors: N}
```
Обычно события уже обработаны hooks. Проверить:
```bash
python -c "
import sqlite3
conn = sqlite3.connect('cache/events.db')
cur = conn.execute('SELECT COUNT(*) FROM events WHERE processed=0')
print(f'Pending: {cur.fetchone()[0]}')
cur = conn.execute('SELECT COUNT(*) FROM events')
print(f'Total events: {cur.fetchone()[0]}')
"
```

### [2] Auto Tagger — категоризация знаний
```bash
cd D:/Portable_Soft/hermes && python scripts/auto_tagger.py
# или v2:
python scripts/auto_tagger_v2.py
```
- Скорость: ~30-60с
- Результат: реклассификация тысяч записей в домены
- Можно запускать с `--force` для полного пересканирования
- **Исторический результат (2026-06-10):** 1195/2134 записей реклассифицировано в 14 доменов

### [3] Latent Domain Detector — скрытые пробелы
```bash
cd D:/Portable_Soft/hermes && python scripts/latent_domain_detector.py
```
- Скорость: ~10-30с
- Находит: кросс-доменные термы, bridge-кандидаты, логические пробелы
- **Исторический результат (2026-06-10):** 97 доменов, missing `monitoring` домен при 668 упоминаниях инфраструктуры

### [4] Anomaly Detector — здоровье системы
```bash
cd D:/Portable_Soft/hermes && python scripts/anomaly_detector.py
```
- Скорость: ~10-20с
- Сохраняет результат в `cache/red_alerts.json`
- **Исторический результат (2026-06-10):** домен 'bugfix' — 82% ошибок (379/464)

### [5*] Knowledge Gap Filler — LLM-заполнение пробелов
```bash
cd D:/Portable_Soft/hermes && python scripts/knowledge_gap_filler.py
```
- ❌ Медленный (таймаут 120с+) — LLM не отвечает быстро
- Использует OpenCode Zen API с free моделями
- Рекомендация: запускать с `timeout=300` в фоне, проверять позже
- Если падает по таймауту — пропустить, не блокировать pipeline

### [6*] Pattern Extractor — извлечение паттернов
```bash
cd D:/Portable_Soft/hermes && python scripts/pattern_extractor.py
```
- ❌ Медленный (таймаут 60с+) — возможно из-за размера git-истории
- Если падает по таймауту — пропустить

## Проверка результатов после прогона

```bash
# Knowledge Cube
python -c "
import sqlite3
conn = sqlite3.connect('cache/knowledge_cube.db')
c = conn.execute('SELECT COUNT(*) FROM experiences')
print(f'KC entries: {c.fetchone()[0]}')
d = conn.execute('SELECT COUNT(DISTINCT axis_domain) FROM experiences')
print(f'Domains: {d.fetchone()[0]}')
conn.close()
"

# Events
python -c "
import sqlite3
conn = sqlite3.connect('cache/events.db')
c = conn.execute('SELECT COUNT(*) FROM events')
print(f'Events: {c.fetchone()[0]}')
conn.close()
"
```

## Известные проблемы

| Проблема | Симптом | Решение |
|----------|---------|---------|
| bugfix 82% failure rate | anomaly_detector критическое предупреждение | Скорее всего misclassification — записи не-bugfix попали в домен. Нужна ручная чистка или тюнинг auto_tagger правил |
| Missing monitoring domain | latent_domain_detector нашёл пробел | 668 упоминаний инфраструктуры, но нет домена monitoring. Создать через Knowledge Cube |
| Knowledge Gap Filler timeout | скрипт не завершается за 120с | LLM-free модель медленная. Запускать в фоне `terminal(background=true, notify_on_complete=true)` с большим таймаутом |
| Pattern Extractor timeout | скрипт не завершается за 60с | Возможно из-за большого git-log. Рассмотреть `--max-commits` или ограничение глубины |

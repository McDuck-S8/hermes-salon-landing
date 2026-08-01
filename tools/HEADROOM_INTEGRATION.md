# Headroom Integration — Практический план

## Статус: CLONED (tools/headroom), требует установки

## Что это
Headroom — context compression layer для AI agents. 60-95% fewer tokens.
- Library: `compress(messages)` в Python/TypeScript
- Proxy: `headroom proxy --port 8787`, zero code changes
- MCP server: `headroom_compress`, `headroom_retrieve`, `headroom_stats`

## Установка

### Вариант 1: Docker (рекомендуется)
```bash
cd D:/Portable_Soft/hermes/tools/headroom
docker compose up -d
```
Запустит proxy на порту 8787 + Qdrant + Neo4j.

### Вариант 2: Rust (нужен cargo)
```bash
cd D:/Portable_Soft/hermes/tools/headroom
cargo build --release
```

### Вариант 3: Python SDK (нужны зависимости)
```bash
pip install headroom-ai
```

## Интеграция с Hermes

### Через proxy (zero code changes):
```bash
# Запустить headroom proxy
docker compose up -d

# Настроить Hermes использовать proxy
# В config.yaml:
web:
  backend: 'http://localhost:8787'
```

### Через Python SDK:
```python
from headroom import compress

# Сжать сообщения перед отправкой в LLM
compressed = compress(messages, model="gpt-4o")
# compressed.messages — сжатые сообщения
# compressed.compression_ratio — например, 0.35 (65% saved)
```

## Экономика

### Текущие затраты Hermes (пример):
- 10,000 токенов/сессию × 100 сессий = 1M токенов/день
- GPT-4o: $2.50/1M input tokens = $2.50/день = $75/мес

### С Headroom (60% compression):
- 400,000 токенов/день
- GPT-4o: $1.00/день = $30/мес
- **Экономия: $45/мес (60%)**

### При масштабировании (10x):
- 10M токенов/день → $250/день → $7,500/мес
- С Headroom: $100/день → $3,000/мес
- **Экономия: $4,500/мес**

## Следующий шаг
Запустить Docker: `cd tools/headroom && docker compose up -d`

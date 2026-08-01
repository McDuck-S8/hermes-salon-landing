# Error Analyzer — Crystal v3.1

## Модуль
`scripts/crystal/error_analyzer.py` — класс `ErrorAnalyzer`

## Паттерны ошибок

| Тип | Severity | Паттерн | Источник |
|-----|----------|---------|----------|
| model_not_supported | critical | `Model (\S+) is not supported` | conversation_loop |
| non_retryable | critical | `Non-retryable client error` | conversation_loop |
| memory_overflow | high | `Memory at (\d+)/(\d+) chars.*exceed` | tool_executor |
| tool_loop | high | `Tool loop warning: same_tool_failure_warning` | tool_executor |
| api_timeout | medium | `API call failed.*APITimeoutError\|Request timed out` | conversation_loop |
| entry_not_found | medium | `No entry matched` | tool_executor |
| terminal_timeout | medium | `\[Command timed out (\d+)s\]` | tool_executor |
| lsp_failure | low | `lsp\[pyright\] spawn/initialize failed` | hermes.lint.lsp |
| file_blocked | low | `BLOCKED: You have called read_file on this exact region` | tool_executor |

## Использование

```python
from crystal.error_analyzer import ErrorAnalyzer

ea = ErrorAnalyzer()
result = ea.analyze(hours=48)

print(result["health_score"])    # 0-100
print(result["total_errors"])    # int
print(result["top_errors"])      # [{"type": str, "count": int}]
print(result["fixes"])           # [{"error": str, "severity": str, "fix": str}]
```

## CLI

```bash
python scripts/crystal.py --errors          # за 48ч
python scripts/crystal.py --errors --24h    # за 24ч
python scripts/crystal.py --errors --7d     # за неделю
```

## Health Score

Формула: `max(0, 100 - penalty)` где penalty = sum(severity_weights) по всем ошибкам.

Weights: critical=10, high=5, medium=2, low=1.

Пример: 28 entry_not_found (medium) + 12 model_not_supported (critical) + 6 non_retryable (critical) = 28*2 + 12*10 + 6*10 = 236 → score = 0.

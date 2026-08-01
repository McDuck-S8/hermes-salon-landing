---
name: localsynapse-mcp
version: 1.0.0
category: self-improvement
description: LocalSynapse MCP — гибридный поиск по содержимому файлов на Windows. Индексирует 633K+ файлов, поддерживает PDF/DOCX/XLSX/PPTX/HWP.
tags: [search, filesystem, mcp, windows, indexing]
---

# LocalSynapse MCP

Гибридный поиск по содержимому файлов (BM25 + эмбеддинги) на Windows. Использует ONNX для ранжирования.

## Установка

Уже установлен: `D:\Program Files\LocalSynapse\localsynapse-mcp.exe`

## Подключение

```bash
# В Hermes config.yaml:
claude mcp add localsynapse -- "D:\Program Files\LocalSynapse\localsynapse-mcp.exe"

# Или вручную в config.yaml:
mcp:
  servers:
    localsynapse:
      command: 'D:\Program Files\LocalSynapse\localsynapse-mcp.exe'
      args: []
```

## Инструменты

| Инструмент | Описание |
|---|---|
| `search_files` | Гибридный BM25+FTS поиск. Поддерживает PDF, DOCX, XLSX, PPTX, HWP |
| `get_file_content` | Чтение извлечённого содержимого из индекса |
| `list_indexed_files` | Список файлов в индексе (фильтр по папке/расширению) |
| `get_pipeline_status` | Статус индексации: сколько просканировано/проиндексировано |

## Использование Python MCP SDK

```python
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

server = StdioServerParameters(
    command="D:\\Program Files\\LocalSynapse\\localsynapse-mcp.exe",
    args=[]
)

async def search(query: str, limit: int = 10):
    async with stdio_client(server) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            return await session.call_tool("search_files", {
                "query": query,
                "maxResults": limit,
                "mode": "Hybrid"
            })
```

## Проблемы

1. **Database locked** — если `LocalSynapse.exe` уже запущен, MCP не может открыть БД. Решение: `taskkill /F /PID <PID>` перед запуском MCP.
2. **Индексация не запущена** — после сканирования нужно запустить индексацию через UI LocalSynapse (scanComplete=true, но indexedFiles=0).

## Путь ПО

`D:\Program Files\LocalSynapse\localsynapse-mcp.exe` (73MB, от 23 апр 2026)

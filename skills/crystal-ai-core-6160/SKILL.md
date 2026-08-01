---
name: crystal-ai-core-6160
description: Crystal v3: Улучшить скилл для ai-core: устранить повторяющиеся ошибки
category: ai-core
created_by: crystal-v3
created_at: 2026-06-17T03:57:15.126100
---

# crystal-ai-core-6160

## Purpose
Улучшить скилл для ai-core: устранить повторяющиеся ошибки

## Errors Found
- entry_not_found: 24 раз
- model_not_supported: 12 раз
- non_retryable: 6 раз
- api_timeout: 6 раз
- file_blocked: 4 раз

## Recommended Fixes
- model_not_supported (critical): Сменить модель в config.yaml
- non_retryable (critical): Проверить API ключ и модель
- entry_not_found (medium): Проверить что memory entry существует перед update
- lsp_failure (low): Pyright не работает на Windows — отключить или починить
- file_blocked (low): Не читать один и тот же регион файла повторно

## Department
ai-core

## Created
2026-06-17T03:57:15.126100


## Crystal Patch (2026-06-17)
Критическое улучшение для ai-core: снизить количество ошибок

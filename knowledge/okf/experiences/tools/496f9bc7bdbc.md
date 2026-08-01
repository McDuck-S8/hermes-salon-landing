---
type: tools
title: "[model_registry.py] model_registry.py — Центральный регистратор провайдеров и мо"
timestamp: 2026-07-18T18:29:43.817094
confidence: 0.500
verification_method: manual
source_table: kc_entries
importance: 6
tags:
  - script
  - model_registry.py
resource: scripts
---

[model_registry.py] model_registry.py — Центральный регистратор провайдеров и моделей.


> Revisit: when model registry logic, provider fallback, or model selection changes. Last touched: 2026-07-02.
Единая точка входа для всех скриптов и скилов.
Вместо хардкода провайдера и модели в каждом файле — один вызов get_worki

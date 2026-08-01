---
name: figma-mcp-setup
description: Настройка и использование cursor-talk-to-figma-mcp для работы с Figma через MCP
---

# Figma MCP — TalkToFigma

MCP-интеграция между Hermes и Figma через `grab/cursor-talk-to-figma-mcp`.

## Трёхходовка

Всё работает в связке трёх процессов:

### 1. WebSocket сервер (обязателен)

```bash
cd /tmp/cursor-talk-to-figma-mcp
bun socket
```
Слушает на `ws://localhost:3055`. Должен быть запущен ДО MCP сервера.

Если репозиторий не склонирован:
```bash
cd /tmp && git clone https://github.com/grab/cursor-talk-to-figma-mcp.git
```

### 2. MCP сервер (в конфиге Hermes)

Уже добавлен в `~/.hermes/config.yaml`:
```yaml
talk-to-figma:
  command: bunx
  args:
    - cursor-talk-to-figma-mcp@latest
```

### 3. Figma плагин

Установить из Figma Community: Cursor Talk to Figma MCP Plugin
https://www.figma.com/community/plugin/1485687494525374295/cursor-talk-to-figma-mcp-plugin

В Figma: Plugins → Cursor Talk to Figma MCP → подключиться к WebSocket через `join_channel`

## Доступные инструменты MCP

| Категория | Инструменты |
|-----------|-------------|
| Документ | get_document_info, get_selection, read_my_design, get_node_info, get_nodes_info |
| Создание | create_frame, create_rectangle, create_text, create_component_instance |
| Редактирование | set_text_content, set_multiple_text_contents, scan_text_nodes |
| Стили | set_fill_color, set_stroke_color, set_corner_radius, set_layout_mode, set_padding |
| Layout | set_layout_mode, set_layout_sizing, set_item_spacing, set_axis_align |
| Экспорт | export_node_as_image |
| Прототипирование | get_reactions, create_connections |
| Компоненты | get_local_components, get_instance_overrides, set_instance_overrides |

## Порядок работы (чекать перед сессией)

1. `bun socket` запущен? (порт 3055 слушает?)
2. Figma открыта? плагин подключён?
3. MCP сервер в конфиге — добавится сам при старте сессии

## Когда НЕ использовать

- Если нет Figma на машине — использовать код/SVG напрямую
- Если нужно только прочитать дизайн (не редактировать) — экспортнуть как изображение

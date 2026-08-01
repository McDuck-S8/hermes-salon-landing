# Matt Pocock Skill Pipeline — извлечено из YouTube (Никита Велc)

## Источник
Видео: `bYaw3Nwqzn0` — "Новые скиллы от Matt Pocock превращают Claude Code в СЕНЬОРА"
Канал: Никита Велc
Метод извлечения: curl + ytInitialData.attributedDescription (Innertube API был RequestBlocked)

## Пайплайн Matt Pocock (4 скилла для Claude Code)

### 1. Grill Me
- Агент допрашивает пользователя пока не поймёт задачу до мелочей
- Короткие промпты работают лучше огромных (согласно видео)
- **→ Аналог в Hermes:** `brainstorming` (explore → design → spec)

### 2. To Spec
- Превращает ответы из Grill Me в формальную спецификацию
- **→ Аналог в Hermes:** `writing-plans` (implementation plan)

### 3. To Tickets
- Нарезает спецификацию на тикеты методом Tracer Bullet
- Каждый тикет = готовая рабочая фича ровно в одно контекстное окно
- Тикеты могут идти в GitHub Issues или папку проекта
- **→ Аналог в Hermes:** `bd` (beads issue tracker) + `subagent-driven-development`

### 4. Implement
- Запускает разработку с TDD и код-ревью после каждой задачи
- **→ Аналог в Hermes:** `subagent-driven-development` (execute via subagents, 2-stage review)

### 5. Wayfinder (дополнение)
- Для больших проектов — навигация по кодовой базе

## Скилл "АВТОПИЛОТ" (от Никиты Велc)
- Одна команда запускает весь пайплайн: опрос → спецификация → тикеты → имплементация
- Каждый тикет запускается отдельным субагентом в чистом контексте
- Правило «один тикет — одно чистое окно» соблюдается автоматически
- Доступен в Telegram: https://t.me/+gbawo9vjrxYxNWFh

## Соответствие Hermes workflow

Matt Pocock pipeline → Hermes skill:
- Grill Me → `superpowers/brainstorming` 
- To Spec → `superpowers/writing-plans`
- To Tickets → `bd` (beads) + `file-todos`
- Implement → `superpowers/subagent-driven-development` + `software-development/subagent-driven-development`
- Wayfinder → `branch-context-manager` + `agent-native-architecture`

## Ключевые отличия от Hermes
1. Пайплайн Покока ручной — каждый шаг запускается отдельно, каждый тикет надо читать
2. Трейсбуллет — каждый тикет = ровно одно окно контекста
3. TDD жёстко встроен в Implement шаг
4. У Hermes уже есть автоматизация через `bd` + `subagent-driven-development`

## Применение
- Убедиться что Hermes pipeline (brainstorming → writing-plans → beads → subagent) покрывает все 4 шага
- Добавить TDD требование в subagent-driven-development если его нет
- Рассмотреть "Wayfinder" паттерн для branch-context-manager

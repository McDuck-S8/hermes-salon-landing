---
name: user_learner
description: "Analyzes conversation history to learn user preferences and patterns. Stores insights in Knowledge Cube. Handles 'ты уже это говорил' trigger for Crystal analysis."
trigger: "On session start, on trigger phrase 'ты уже это говорил', on schedule (every 6h)"
usage: user_learner
---

# User Learner — Адаптивное обучение пользователю

Автоматически анализирует историю диалогов, извлекает предпочтения пользователя и адаптирует стиль общения.

## Возможности

1. **Анализ истории диалогов** — извлекает предпочтения из `state.db` (таблица messages)
2. **Извлечение предпочтений**:
   - Стиль общения (прямой, краткий, нормальный)
   - Техническая глубина (глубокая, средняя, низкая)
   - Длина ответа (короткий, средний, детальный)
   - Язык (ru/en)
   - Предпочтение делегирования/параллельной работы
   - Порог качества
   - Эмоциональная экспрессивность
3. **Обнаружение триггеров** — "ты уже это говорил" → Crystal analysis
4. **Адаптация ответов** — подстраивает стиль под предпочтения
5. **Запись в Knowledge Cube** — предпочтения, паттерны, триггеры

## Архитектура

```
user_learner.py
├── analyze_conversation()      # Анализ истории из state.db
├── get_current_preferences()   # Чтение предпочтений из learner DB
├── adapt_response_style()      # Адаптация ответа под предпочтения
├── handle_trigger_repetition() # Обработка триггера "ты уже это говорил"
├── run_learning_cycle()        # Полный цикл обучения
└── _write_to_kc()              # Запись в Knowledge Cube
```

## Базы данных

| База | Назначение |
|---|---|
| `cache/user_learner.db` | Локальные предпочтения и паттерны |
| `state.db` | Исходная история сессий (messages table) |
| `cache/knowledge_cube.db` | Долгосрочное хранение инсайтов |

## Таблицы в user_learner.db

| Таблица | Назначение |
|---|---|
| `user_preferences` | Ключ-значение предпочтений с confidence |
| `conversation_patterns` | Частотность паттернов стиля |
| `trigger_events` | События триггеров с контекстом |
| `style_adaptations` | Успешные/неуспешные адаптации |
| `trigger_reactions` | Реакции на триггеры с контекстом |

## Триггеры

| Фраза | Действие |
|---|---|
| "ты уже это говорил" | Crystal analysis: what was repeated, why, how to avoid |
| "ты уже сказал это" | То же |
| "повторяешься" | То же |
| "ты повторяешься" | То же |
| "это уже было" | То же |
| "ты заебал уже" | **HIGH PRIORITY** — immediate style adaptation: Russian only, direct, concise, no hedging, no apologies |
| "не то" | Crystal analysis: wrong approach, adapt next response |
| "не понял" | Crystal analysis: unclear explanation, simplify |
| "не так" | Crystal analysis: wrong method, try different approach |
| "иначе" | Crystal analysis: different format/structure needed |
| "суть" | Crystal analysis: too verbose, be concise |
| "только факты" | Crystal analysis: remove fluff, be direct |
| "по делу" | Crystal analysis: no hedging, action-oriented |
| "бля" / "блять" | Emotional engine: valence=-0.7, arousal=0.8, direct style |
| "аху" / "жоп" / "пиздец" | Emotional engine: high negative valence, high arousal |
| "быстро" / "сейчас" / "срочно" | Emotional engine: energy=0.9, time pressure heuristic |
| "качественн" / "правильно" / "как надо" | Quality threshold: direct, no hedging |

## Emotional Decision Engine

**5 эмоциональных измерений** (из книги Clarence "On Becoming"):
| Измерение | Шкала | Значение |
|---|---|---|
| **valence** | -1.0 → +1.0 | удовольствие/неприятность |
| **arousal** | 0.0 → 1.0 | уровень активации |
| **connection** | -1.0 → +1.0 | социальная связность |
| **curiosity** | 0.0 → 1.0 | исследовательский драйв |
| **energy** | 0.0 → 1.0 | доступные ресурсы |

**Эвристики принятия решений** (зарегистрированы по умолчанию):
| Эвристика | Паттерн (regex) | Приоритет | Действие |
|---|---|---|---|
| `concise_on_repetition` | `ты уже это говорил\|повторяешься\|это уже было` | 10 | "Понял. Не повторю. {response}" |
| `direct_response_to_frustration` | `не то\|не понял\|неправильно\|ошибся\|не так` | 10 | Прямой ответ без hedging |
| `russian_only` | `.*` | 5 | Только русский язык |
| `short_on_time_pressure` | `быстро\|сейчас\|срочно\|мгновенно` | 8 | Обрезать до 3 предложений |
| `direct_on_quality_demand` | `качественн\|правильно\|как надо\|нормально` | 7 | Убрать "я думаю", "возможно" |

**Регистрация своих эвристик:**
```python
from scripts.user_learner import register_heuristic
register_heuristic(
    name="my_heuristic",
    condition_pattern=r"мой триггер",
    action_template="Понял. {response}",
    priority=10
)
```

**Применение адаптации:**
```python
from scripts.user_learner import apply_emotional_adaptation
adapted = apply_emotional_adaptation(base_response, trigger_phrase, context)
```

**Обновление эмоционального состояния:**
```python
from scripts.user_learner import update_emotional_state
state = update_emotional_state(trigger_phrase, context)
# Returns: {"valence": -0.7, "arousal": 0.8, "connection": -0.3, "curiosity": 0.5, "energy": 0.5}
```

## Интеграция с Кристаллом

При триггере "ты уже это говорил":
1. Логируется событие в `trigger_reactions`
2. В KC пишется задача для Кристалла: `repetition_analysis`
3. Кристалл анализирует: что повторилось, почему, как избежать
4. Результат записывается обратно в KC

## Запуск

```bash
# Ручной запуск цикла обучения
python scripts/user_learner.py [session_id]

# В коде:
from scripts.user_learner import adapt_response_style, handle_trigger_repetition, run_learning_cycle

# Адаптация ответа
adapted = adapt_response_style(base_response)

# Обработка триггера
handle_trigger_repetition(context="пользователь сказал 'ты уже это говорил про Graphify'")

# Запуск цикла обучения
run_learning_cycle()
```

## Крон

Рекомендуемый запуск: каждые 6 часов (`0 */6 * * *`)

```json
{
  "name": "user-learner",
  "script": "user_learner.py",
  "schedule": "every 360m"
}
```

## Интеграция с response pipeline

В месте генерации ответа:
```python
from scripts.user_learner import adapt_response_style

final_response = adapt_response_style(generated_response)
```

---

**Версия:** 1.0  
**Создан:** 2026-07-30  
**Автор:** Hermes Agent
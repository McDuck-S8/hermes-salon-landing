# White Spot Explorer — Run Recipe & Pitfalls

## Реальный запуск (design domain, июнь 2026)

**Результат:** design: 2 → 8 записей. 6 концепций сгенерировано, 0 ошибок API.

## КРИТИЧЕСКИЙ ПИТФОЛ: delegate_task блокирует чат

Первый запуск через delegate_task занял 420 секунд (7 минут).
Всё это время пользователь видел тишину — чат "завис".

**Причина:** delegate_task выполняется синхронно. Пока агент работает,
пользователь не получает промежуточных ответов. Это системный долг.

**ФИКС — не использовать delegate_task для white-spot-explorer:**
```python
# ПЛОХО: блокирует чат на 7 минут
result = delegate_task(goal="Исследовать домен X")

# ХОРОШО: прямой API вызов через execute_code
# После каждого шага отписываться пользователю:
print("1/3: Генерирую концепции через DeepSeek...")
# ... API вызов ...
print("2/3: Расширяю через Qwen...")
# ... API вызов ...
print("3/3: Пишу в Knowledge Cube...")
# ... запись ...
print("Готово! Домен: X -> N записей")
```

## Рецепт быстрого запуска

1. Получить список белых пятен через прямой SQL к cube.db
2. Выбрать самый малоизученный домен
3. Выполнить через execute_code (не delegate_task!)
4. После каждого шага давать статус в stdout
5. Результат = сколько записей добавилось

## proxy curl шаблоны

### DeepSeek (http://localhost:9655/v1)
```bash
curl -s http://localhost:9655/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"deepseek-chat","messages":[{"role":"user","content":"Текст запроса. Не больше 500 токенов."}],"max_tokens":1000}'
```

### Qwen (http://localhost:3264/api)
```bash
curl -s http://localhost:3264/api/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"qwen3.7-max","messages":[{"role":"user","content":"Текст запроса."}]}'
```

## Полученный опыт

- DeepSeek хорошо генерирует списки концепций, Qwen лучше пишет развёрнутые описания
- 6 API вызовов (3 DeepSeek + 3 Qwen) с паузами 3-5с = ~2 минуты
- Ранее через delegate_task это же занимало 7 минут из-за накладных расходов на контекст агента
- Скорость напрямую влияет на UX: быстрее ответ → пользователь не раздражается

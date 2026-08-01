## 4. GIGO Trace — как мусор циркулирует в системе

```
Self-Improvement Loop ──► пишет suggestion в KC (62% шума)
                                │
                    ┌───────────┼───────────┐
                    ▼           ▼           ▼
                  EE извлекает  KC RAG      Self-Improvement
                  сущности      ищет по     читает свои же
                  из шума       шуму        suggestions
                    │           │           │
                    ▼           ▼           ▼
              Нет связей    Результаты     Новые suggestions
              между        поиска         (рекурсия)
              entities     загрязнены
                              │
                              ▼
                    Morning Report считает
                    "maturity=100% debugging"
                    на основе 3,257 копий
                    одной suggestion
```

**Замкнутый круг:** система пишет логи → называет их знаниями →
анализирует их → делает выводы на их основе → пишет новые логи.

### Чистые потоки (не затронуты GIGO)
- Session Bridge — ручные commitments
- Chain Heartbeat — технические метрики
- User messages (но их 9/24ч — маловато)
- 46 pattern/fact entries — ручные, достоверны

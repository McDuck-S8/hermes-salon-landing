# Local Image Download Workflow

**Когда:** Создаёшь HTML-портфолио/лендинг для реального бизнеса.
**Проблема:** Unsplash/Pexels URLs могут не загрузиться из-за блокировок прокси/CDN.
**Решение:** Скачать images локально и ссылаться относительными путями.

## Шаги

1. **Найти подходящие фото** — через Unsplash (images.unsplash.com) или Pexels (images.pexels.com)
2. **Скачать curl-ом:**
   ```bash
   cd /d/Portable_Soft/hermes/cache/project-name
   curl -sL -o img/hero.jpg "https://images.unsplash.com/photo-XXXXX?w=600&h=750&fit=crop"
   ```
3. **Проверить размер:** `ls -la img/` — файлы < 500B = 404, скачать другой URL
4. **Ссылаться в HTML:** `src="img/hero.jpg"` (относительный путь)
5. **Добавить CSS fallback:** `background: var(--cream)` на img-контейнер

## Питфоллы

- `&` не работает в foreground terminal — качать по одному файлу или через background
- Exit code 23 curl = ошибка записи. Использовать относительный путь (`cache/...`), а не абсолютный (`/d/Portable_Soft/...`)
- `/d/...` пути curl может не создавать. Использовать `cd` в нужную директорию + относительный путь
- Unsplash URL с `&auto=format` может фейлиться — убрать параметр
- После скачивания проверить `file img/hero.jpg` — должно быть "JPEG image data"
- Разные ориентации: hero 4:5, master 1:1, user 1:1, gallery wide 2:1

## Пример портфолио-структуры

```
portfolio.html
img/
  hero.jpg
  master1.jpg  master2.jpg  master3.jpg
  g1.jpg  g2.jpg  g3.jpg  g4.jpg  g5.jpg
  user1.jpg  user2.jpg  user3.jpg
```

# FFmpeg + Windows: Drawtext Pitfalls & Solutions

## Проблема: drive letter colon (C:) в фильтрах drawtext

FFmpeg использует `:` как разделитель опций в строке фильтра.
Windows-пути типа `C:\Windows\Fonts\arial.ttf` имеют двоеточие после буквы диска,
которое ломает парсер.

## Решения

### 1. Относительный путь (recommended)

Если файл в том же проекте (на том же диске) — используй `os.path.relpath()`:

```python
rel = os.path.relpath(font_path).replace("\\", "/")
# → "scripts/assets/Roboto-Bold.ttf"  # без drive letter
```

### 2. `textfile` vs `text`

`textfile=...` требует путь к файлу. Если файл на диске C: или D:, путь сдержит `:`.
Лучше использовать `text=...` напрямую, если текст не содержит `:` или `'`.

```python
# Работает:
filter_str = f"drawtext=text=Free V-Bucks:fontfile=scripts/assets/arial.ttf:fontsize=36"

# Ломается:
filter_str = f"drawtext=textfile=C:\\Users\\...\\tmp.txt:fontfile=C:\\Windows\\Fonts\\arial.ttf:..."
```

### 3. Экранирование `\:` (не работает на gyan.dev builds)

На некоторых билдах FFmpeg (gyan.dev) `\:` не экранирует двоеточие в Windows-путях.
Лучше не полагаться на это.

### 4. Font fallback chain

```python
# Приоритет:
1. assets/Roboto-Bold.ttf        # скачанный Google Fonts
2. C:/Windows/Fonts/arial.ttf    # system fallback (копируется в assets)
3. C:/Windows/Fonts/segoeuib.ttf # ещё один fallback

# Важно: скопировать шрифт из system в assets, чтобы иметь относительный путь
```

## Проверка

```bash
# Корректное выполнение:
ffmpeg -f lavfi -i color=c=#1a1a2e:s=608x1080:d=3 \
  -vf "drawtext=text=Hello:fontfile=scripts/assets/arial.ttf:fontsize=36" \
  cache/test.mp4
```

## Python != SQLite на 3.13

В Python 3.13 `sqlite3.Connection.__enter__` возвращает `connection`, не `cursor`.
```python
# НЕПРАВИЛЬНО — connection не имеет .fetchall()
with self._conn() as c:
    c.execute("SELECT * FROM accounts")
    rows = c.fetchall()  # AttributeError

# ПРАВИЛЬНО
with self._conn() as conn:
    c = conn.cursor()
    c.execute("SELECT * FROM accounts")
    rows = c.fetchall()
```

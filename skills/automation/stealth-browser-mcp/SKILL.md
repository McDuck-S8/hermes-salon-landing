---
name: stealth-browser-mcp
description: "Подключение к Chrome пользователя через CDP 9222 — browser-harness CLI + nodriver fallback. Обход блокировок через v2rayN прокси."
---

# Stealth Browser — CDP to Chrome @ 9222

Не запускай свой браузер. У пользователя **уже запущен Chrome** с CDP на порту 9222.
Твоя задача — подключиться к нему, а не создавать новый.

## Соединение с Chrome (CDP 9222)

```
Chrome:  PID 27328, порт 9222, 113+ вкладок (YouTube, BrowserOS)
```

### Базовая проверка

```bash
# 1. Убедиться что Chrome жив
tasklist /FI "PID eq $(netstat -ano | grep ':9222.*LISTENING' | awk '{print $5}')"

# 2. Проверить порт (только если убрать прокси из env)
for var in http_proxy https_proxy HTTP_PROXY HTTPS_PROXY ALL_PROXY no_proxy; do unset $var; done
curl -s http://127.0.0.1:9222/json/version
```

### Проблема: Chrome 136+ блокирует WebSocket

Начиная с Chrome 136, CDP WebSocket-соединения требуют флага `--remote-allow-origins=*`.
HTTP-эндпоинты (`/json/version`, `/json`) возвращают 404 на дефолтном профиле.
WebSocket отклоняется с 403:

```
Rejected an incoming WebSocket connection from the http://127.0.0.1:9222 origin.
Use --remote-allow-origins=* to allow all origins.
```

Все Origin-заголовки (chrome://devtools, devtools://devtools, file://, без Origin)
отклоняются. `--remote-allow-origins=*` — единственное решение.

**Четыре способа решить:**

| Способ | Команда | Эффект |
|--------|---------|--------|
| 1. Рестарт Chrome с флагом | Закрыть Chrome, запустить с `--remote-debugging-port=9222 --remote-allow-origins=*` | Работает сразу |
| 2. chrome://inspect | Открыть `chrome://inspect/#remote-debugging`, включить галку, нажать Allow | Если `DevToolsActivePort` создан — browser-harness подхватит |
| 3. BU_CDP_URL | Запустить свой Chrome с флагом и указать `BU_CDP_URL=http://127.0.0.1:9333` | Обходит discovery + WS блокировку |
| 4. Свой headless Chrome | `chrome.exe --remote-debugging-port=9333 --remote-allow-origins=* --proxy-server=http://127.0.0.1:10806 --headless=new` | Полный CDP доступ, но без куков пользователя |

### browser-harness CLI

Установлен: `/d/Program Files/Python311/Scripts/browser-harness` (Windows PE, не скрипт)
Даемон: порт 9003, PID 4364 (python.exe), живёт ~61 час, может упасть в 503.

```bash
# Запуск
browser-harness <<'PY'
new_tab("https://www.youtube.com")
wait_for_load()
print(page_info())
PY

# Если даемон умер — убить старый PID и перезапустить
# Или указать другой BU_NAME для свежего даемона
BU_NAME=hermes-fresh browser-harness <<'PY'
new_tab("https://example.com")
print(page_info())
PY
```

## Fallback: nodriver + прокси

Когда CDP заблокирован — запускай **отдельный экземпляр Chrome** через nodriver через прокси:

```bash
pip install nodriver
```

Скрипт: `skills/automation/stealth-browser-mcp/scripts/stealth_browser.py`

```python
# ВАЖНО: browser_executable_path передаётся в конструктор, не после!
config = nodriver.Config(
    browser_executable_path="D:/Program Files/Google/Chrome/Application/chrome.exe",
    headless=True
)
# Прокси — через browser_args, не config.proxy
config.add_argument('--proxy-server=http://127.0.0.1:10806')
browser = await nodriver.start(config)
tab = await browser.get("https://www.youtube.com")
```

**Ошибка при config.proxy = '...':** `TypeError: 'str' object is not callable` — nodriver
воспринимает строку как функцию. Только `add_argument('--proxy-server=...')`.

## Обнаружение прокси (v2rayN) — ОБЯЗАТЕЛЬНЫЙ ПЕРВЫЙ ШАГ

Никогда не начинай сетевую работу без проверки прокси.
Процесс v2rayN.exe может быть запущен, но env-переменные могут быть не выставлены.

```bash
# 1. Проверить жив ли v2rayN
tasklist /FI "IMAGENAME eq v2rayN.exe" 2>/dev/null

# 2. Сканировать порты
for port in 10806 10808 10809 1080 1081; do
  res=$(curl -s --connect-timeout 2 -x http://127.0.0.1:$port \
    https://www.google.com -o /dev/null -w "%{http_code}" 2>/dev/null)
  [ "$res" = "200" ] && echo "PORT=$port HTTP OK" && break
done

# 3. Установить для сессии
PROXY="http://127.0.0.1:10806"  # проверено
```

**Важно:** Если PROXY env vars установлены, они перехватывают ВСЕ curl-запросы,
включая локальные (localhost). Для локальных CDP запросов — всегда unset proxy vars.

## Питфоллы

1. **Proxy vars перехватывают localhost** — http_proxy/http_proxy перенаправляют даже curl к localhost:9222 через прокси, что даёт 404. Всегда проверяй `echo $http_proxy` перед CDP-запросами.
2. **browser-harness даемон умирает молча** — порт 9003 отвечает 503, но процесс висит. Надо убить вручную.
3. **Chrome 136+ origin check** — `--remote-allow-origins=*` обязателен. Без него WebSocket-соединение невозможно. Chrome 148 (BrowserClaw) тоже.
4. **Chrome cookies не экспортируются** — `yt-dlp --cookies-from-browser chrome` выдаёт "cookies no longer valid". YouTube ротирует ключи. Только через живой браузер с сессией.
5. **App-Bound Encryption (Chrome 127+)** — все куки зашифрованы службой Chrome. `win32crypt.CryptUnprotectData` падает с error 13. Файловый доступ к кукам невозможен — только CDP WebSocket.
6. **YouTube без куков — почти нет субтитров** — тестирование: 0/15 видео из 8 поисков (faceless, CPA, automation) не имели публичных субтитров. Автосубтитры доступны только для каналов, где создатель включил галку "Allow viewers with disabilities…" в Studio. Логин обязателен.
7. **nodriver Config** — `browser_executable_path` обязан быть в конструкторе, не после. `config.proxy = 'http://...'` выдаёт `TypeError: 'str' object is not callable`. Используй `add_argument('--proxy-server=...')`.
8. **ASR-дубли** — yt-dlp VTT-файлы содержат тройное повторение (слово-фраза-предложение). Используй `scripts/clean_vtt.py` с дедупликацией.

## BrowserClaw discovery

BrowserClaw работает как отдельный экземпляр Chrome со своим профилем:

| Параметр | Значение |
|---|---|
| Путь Chrome | `C:\Users\Asus\AppData\Local\BrowserClaw\Application\chrome.exe` |
| Версия | Chrome 148.0.7958.97 |
| MCP (SSE) | `http://127.0.0.1:9010/mcp` |
| CDP HTTP | `http://127.0.0.1:9110` |
| User Data | `C:\Users\Asus\AppData\Local\BrowserClaw\User Data` |

**CDP порт 9110:** HTTP `/json/version` работает, WebSocket блокирован (Chrome 148, тот же origin check).
**MCP порт 9010:** SSE протокол — требует `Accept: text/event-stream` + `mcp-session-id` заголовок.

Cookie-база BrowserClaw тоже использует App-Bound Encryption — нечитаема снаружи.

## Работающий headless Chrome (full CDP, без логина)

```bash
cd D:/Portable_Soft/hermes

# Запустить свой Chrome с полным CDP доступом
python -c "
import subprocess, os, json, time
os.makedirs('cache/chrome_hermes', exist_ok=True)
cmd = [
    'D:/Program Files/Google/Chrome/Application/chrome.exe',
    f'--user-data-dir={os.getcwd()}/cache/chrome_hermes',
    '--remote-debugging-port=9333',
    '--remote-allow-origins=*',
    '--proxy-server=http://127.0.0.1:10806',
    '--headless=new',
    '--no-first-run', '--no-default-browser-check',
    'https://www.youtube.com'
]
subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(4)

# Подключиться
resp = urllib.request.urlopen('http://127.0.0.1:9333/json', timeout=5)
tabs = json.loads(resp.read())
print(f'Chrome OK: {len(tabs)} tabs')
"

# После: CDP WebSocket работает, можно искать YouTube
python -c "
import websocket, json, urllib.request
data = json.loads(urllib.request.urlopen('http://127.0.0.1:9333/json').read())
ws = websocket.create_connection(data[0]['webSocketDebuggerUrl'], timeout=10)
# ... send CDP commands
ws.close()
"
```

## Fallback priority chain

Когда нужны данные из YouTube — пробуй в этом порядке:

1. **youtube-transcript-api через прокси** — БЫСТРО, БЕЗ ЛОГИНА
   ```bash
   export http_proxy=http://127.0.0.1:10806 https_proxy=http://127.0.0.1:10806
   python -c "
   from youtube_transcript_api import YouTubeTranscriptApi
   api = YouTubeTranscriptApi()          # instance method, не статический!
   t = api.fetch('VIDEO_ID')
   segs = list(t)                        # FetchedTranscript iterable
   print(f'{len(segs)} segments')
   print(t.snippets[0].text)             # первый сниппет
   "
   ```
   - **Важно:** `YouTubeTranscriptApi()` — это instance, НЕ `YouTubeTranscriptApi.fetch()`.
   - API сам пробует ручные субтитры → авто-субтитры.
   - Проверено: 16/54 видео faceless/CPA ниши имели субтитры.
   - Не требует браузера, просто HTTPS-запросы.

2. **yt-dlp через прокси** (поиск + метаданные):

   ```bash
   yt-dlp --proxy http://127.0.0.1:10806 --flat-playlist --dump-json 'ytsearch10:запрос'
   yt-dlp --proxy http://127.0.0.1:10806 --list-subs --skip-download "https://youtube.com/watch?v=VIDEO_ID"
   yt-dlp --proxy http://127.0.0.1:10806 --write-auto-subs --sub-lang en --skip-download -o "%(id)s" "https://youtube.com/watch?v=VIDEO_ID"
   ```

3. **Headless Chrome CDP** (свой экземпляр) — полный контроль, без логина
   ```bash
   python -c "
   import subprocess, os, json, time
   os.makedirs('cache/chrome_hermes', exist_ok=True)
   subprocess.Popen([
       'D:/Program Files/Google/Chrome/Application/chrome.exe',
       '--user-data-dir=' + os.getcwd() + '/cache/chrome_hermes',
       '--remote-debugging-port=9333',
       '--remote-allow-origins=*',
       '--proxy-server=http://127.0.0.1:10806',
       '--headless=new',
   ])
   time.sleep(4)
   import urllib.request
   tabs = json.loads(urllib.request.urlopen('http://127.0.0.1:9333/json').read())
   "
   ```

4. **web_extract / firecrawl** — страница YouTube:
   ```python
   web_extract_plus(urls=[url], provider="firecrawl")
   ```

5. **noembed.com** — только метаданные (последняя надежда):
   ```bash
   curl -s "https://noembed.com/embed?url=https://www.youtube.com/watch?v=VIDEO_ID"
   ```

## Когда CDP не работает — все fallback подряд (справочно)

### Питфоллы

- ❌ CDP 9222 — Chrome жив, WebSocket blocked (Chrome 150, требует `--remote-allow-origins=*`)
- ❌ BrowserClaw CDP 9110 — Chrome жив, WebSocket blocked (Chrome 148, то же)
- ❌ Куки Chrome — App-Bound Encryption (Chrome 127+), DPAPI не читает
- ✅ v2rayN прокси 127.0.0.1:10806 — HTTP + SOCKS5, YouTube доступен
- ✅ yt-dlp через прокси — поиск, метаданные, транскрипты с автосубтитрами (en + ru)
- ✅ Headless Chrome с `--remote-allow-origins=*` — полный CDP, WebSocket работает
- ❌ browser-harness — даемон 61 час, 503, `DevToolsActivePort` не создан
- ✅ `BU_CDP_URL=http://127.0.0.1:9333` — browser-harness работает через свой Chrome
- ❌ nodriver — требует `browser_executable_path` в конструкторе, `config.proxy` ломает start()

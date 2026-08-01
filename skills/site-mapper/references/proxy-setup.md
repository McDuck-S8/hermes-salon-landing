# Proxy Setup for Site Mapping

## v2rayN SOCKS5
- Прокси: `socks5://127.0.0.1:10806`
- Установлен и работает на Windows
- Пробивает блокировку Крыма для большинства US/EU сайтов

## Быстрая проверка доступности
```bash
curl -x socks5h://127.0.0.1:10806 -s -o /dev/null -w "%{http_code}" --connect-timeout 5 https://target-site.com
```

## Статус проверенных сайтов

### Работают через прокси (все 200/308)
- ElevenLabs (elevenlabs.io) — голос AI
- Suno (suno.com) — музыка AI, 10 песен/день
- CapCut (capcut.com) — видео редактор
- Carrd (carrd.co) — конструктор сайтов
- Playground AI (playgroundai.com) — изображения AI
- Runway ML (runwayml.com) — видео AI
- Pika.art (pika.art) — видео AI
- Bing Create (bing.com/create) — изображения DALL-E 3

### Блокированы Cloudflare (403 даже через прокси)
- Leonardo AI (leonardo.ai)
- NightCafe (creator.nightcafe.studio)

### Недоступны из Крыма (даже через прокси)
- YouTube — нестабильно, детектит SOCKS5

## Настройка среды
Перед сессией:
```bash
export ALL_PROXY=socks5://127.0.0.1:10806
export HTTP_PROXY=socks5://127.0.0.1:10806
export HTTPS_PROXY=socks5://127.0.0.1:10806
```

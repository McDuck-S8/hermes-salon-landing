# Services Ecosystem Graph — доступность через прокси

Граф всех сервисов и связей: AI → контент → хостинг → трафик → деньги.

## Визуализация
- HTML: `file:///D:/Portable_Soft/hermes/reports/services_ecosystem.html`
- JSON: `file:///D:/Portable_Soft/hermes/data/services_registry.json`

## Доступность через v2rayN (127.0.0.1:10806)

### 🟢 Работают без прокси
| Сервис | Тип | Причина |
|--------|-----|---------|
| **Pollinations AI** | AI image | FLUX, без ключа |
| **Bing Create** | DALL-E 3 | Microsoft |
| **Tilda** | Конструктор | РФ хостинг |

### 🟢 Работают через SOCKS5 прокси (curl, node с ALL_PROXY)
| Сервис | Тип | Бесплатно |
|--------|-----|-----------|
| **ElevenLabs** | AI голос | 10 мин/мес |
| **Suno** | AI музыка | 10 песен/день |
| **CapCut** | AI видео | Базовый (водяной знак) |
| **Carrd** | Конструктор | 3 сайта |
| **Playground AI** | AI image | 500 gen/мес |
| **Runway ML** | AI видео | 125 creds/мес |
| **Pika.art** | AI видео | 30 gen/день |
| **YouTube** | Видео | Через curl (301) |

### 🟡 Частично (Cloudflare 403 даже через прокси)
| Сервис | Тип | Нужно |
|--------|-----|-------|
| **Leonardo AI** | AI image | Резидентные прокси |

### 🔴 Недоступны блокированные источники трафика
| Сервис | Причина |
|--------|---------|
| api.telegram.org | HTTP API блокирован в Крыму (MTProto работает — Telegram Desktop) |

## Граф связей (что → куда)

```
Идея/Ниша → AI-генерация → Контент → Хостинг + Домен → Продвижение → Монетизация
                                                                         ↓
                                                                   CPA/Крипта/USDT
```

## Механика запуска через прокси

Для Node.js сервисов (FreeDeepseekAPI, и др.), которые должны ходить в интернет:
```bash
export ALL_PROXY=socks5://127.0.0.1:10806
export HTTP_PROXY=socks5://127.0.0.1:10806
export HTTPS_PROXY=socks5://127.0.0.1:10806
```
Для curl:
```bash
curl -x socks5h://127.0.0.1:10806 <url>
```
Для Python:
```python
import os
os.environ['ALL_PROXY'] = 'socks5://127.0.0.1:10806'
```

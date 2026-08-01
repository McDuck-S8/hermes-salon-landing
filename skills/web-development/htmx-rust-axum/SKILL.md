---
name: htmx-rust-axum
description: "HTMX + Rust (Axum) — быстрая веб-архитектура 2026. Замена React/JS бандлам на серверный HTML через Rust."
trigger:
  - User asks about HTMX + Rust
  - User wants fast web stack without JS bundlers
  - User is tired of React/Node.js complexity
  - Need lightweight web server (no Docker, single binary)
---

# HTMX + Rust (Axum) — Веб-архитектура 2026

## Суть (парадигма)

**Вместо:** React SPA → JS бандл → API сервер (Node/Python) → две codebase
**Используем:** HTMX на фронтенде → Rust (Axum) на бэкенде → один бинарник → HTML по сети

Ключевая идея: **сервер отдаёт HTML напрямую, а HTMX делает его интерактивным без единой строки JavaScript.**

## Почему это важно для нас

| Проблема | Решение через HTMX+Rust |
|---|---|
| Docker запрещён | Rust компилируется в один .exe — никаких контейнеров |
| Ресурсов ПК мало | Rust быстрее Python/Node в 10-100x |
| React/JS сборка тормозит | HTMX — это HTML-атрибуты, ноль сборки |
| Две codebase (front+back) | Одна codebase, один сервер, один тип данных (HTML) |
| VDS дорогой | Rust-бинарник на 5MB работает на самом дешёвом VDS |

## Стек

- **Backend:** Rust + Axum (Tokio async, tower middleware)
- **Frontend:** HTMX (hx-attributes в HTML), Alpine.js (опционально для сложных состояний)
- **Templating:** Askama / Maud / нативная String-интерполяция
- **DB:** sqlx (SQLite/Postgres) — асинхронные запросы
- **Статика:** tower-http (ServeDir для CSS/JS)

## Отличие от React/Node

```
React:
  npm install → webpack/vite сборка → JS бандл (2MB+) → API запросы → JSON → рендер
  ❌ Две codebase, медленная сборка, огромные node_modules, Docker нужен

HTMX+Rust:
  cargo build → один .exe (5MB) → HTML по сети → HTMX делает интерактив
  ✅ Одна codebase, ноль сборки фронтенда, бинарник 5MB, без Docker
```

## Как начать

### Проект (Cargo.toml)
```toml
[package]
name = "my-app"
version = "0.1.0"
edition = "2021"

[dependencies]
axum = "0.8"
tokio = { version = "1", features = ["full"] }
tower-http = { version = "0.6", features = ["fs"] }
serde = { version = "1", features = ["derive"] }
serde_json = "1"
sqlx = { version = "0.8", features = ["runtime-tokio", "sqlite"] }
```

### Минимальный сервер
```rust
use axum::{Router, routing::get, response::Html};

async fn index() -> Html<&'static str> {
    Html(r#"
    <!DOCTYPE html>
    <html>
    <head>
        <script src="https://unpkg.com/htmx.org@2.0.0"></script>
    </head>
    <body>
        <h1>HTMX + Rust</h1>
        <button hx-get="/hello" hx-target="#output">
            Нажми меня
        </button>
        <div id="output"></div>
    </body>
    </html>
    "#)
}

async fn hello() -> &'static str {
    "Привет от Rust через HTMX!"
}

#[tokio::main]
async fn main() {
    let app = Router::new()
        .route("/", get(index))
        .route("/hello", get(hello));

    let listener = tokio::net::TcpListener::bind("0.0.0.0:3000")
        .await.unwrap();
    axum::serve(listener, app).await.unwrap();
}
```

### HTMX атрибуты (вся магия)
```html
<!-- Загрузить контент по клику -->
<button hx-get="/api/data" hx-target="#result">Загрузить</button>

<!-- Отправить форму без JS -->
<form hx-post="/api/submit" hx-target="#response">
    <input name="name">
    <button type="submit">Отправить</button>
</form>

<!-- Обновить часть страницы каждые 30 сек -->
<div hx-get="/api/status" hx-trigger="every 30s"></div>

<!-- Подтверждение перед действием -->
<button hx-delete="/api/item/1" hx-confirm="Удалить?">Удалить</button>

<!-- Загрузка с индикатором -->
<button hx-get="/api/heavy" hx-target="#result" hx-indicator="#spinner">
    Тяжёлая операция
</button>
<div id="spinner" class="htmx-indicator">Загрузка...</div>
```

## Что можно построить прямо сейчас

1. **Замена landing-генератору** — Rust-сервер который отдаёт HTML страницы вместо статики
2. **CPA-лендинг на Rust** — легче Node, быстрее Python, один бинарник для деплоя
3. **Telegram Mini App** — HTMX идеально для TMA (лёгкий, без JS сборки)  
4. **Dashboard для P&L** — Живой dashboard с hx-trigger="every 5s" для обновлений

## Противопоказания

1. **Rust learning curve** — придётся учить ownership/borrowing. Не для быстрых прототипов.
2. **Сложная бизнес-логика** — для магазина с 10 страницами может быть оверхед.
3. **HTMX не замена SPA** — если нужно real-time collaboration — HTMX не подойдёт.
4. **Нет экосистемы компонентов** — нет аналога shadcn/ui под HTMX.

## Инструменты для старта

- Rust: https://rustup.rs
- Axum docs: https://docs.rs/axum
- HTMX docs: https://htmx.org/docs/
- SQLx: https://github.com/launchbadge/sqlx

## Verification

- [ ] cargo build собирает один .exe
- [ ] Сервер отвечает на localhost:3000
- [ ] HTMX атрибуты работают (hx-get, hx-post)
- [ ] SQLite запросы проходят
- [ ] Бинарник работает без Rust установленного на машине

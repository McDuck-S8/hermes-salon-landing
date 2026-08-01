"""
Hermes Voice Bridge — подключение голосового цикла к LLM.
OpenAI-совместимый сервер на порту 8642.
Сначала пробует FreeDeepseekAPI, затем другие провайдеры.
v2 — standalone, не требует полного gateway.
"""
import asyncio
import json
import os
import sys
import time
import urllib.request
import urllib.error

# ─── Пути ─────────────────────────────────────────────────────
HERMES_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERMES_ROOT)
sys.path.insert(0, os.path.join(HERMES_ROOT, "scripts"))

# ─── Системный промпт (JARVIS голосовой) ────────────────────────
JARVIS_SYSTEM_PROMPT = """Ты — JARVIS, голосовой AI-ассистент Сэра.

ПРАВИЛА:
1. Отвечай КОРОТКО — 1-3 предложения. Голосовой канал, длинные ответы раздражают.
2. Обращайся «Сэр».
3. Никакого маркдауна, звёздочек, обратных кавычек — чистый текст для TTS.
4. Отвечай на том языке, на котором спросили (русский/английский).
5. Если нужно что-то сложное — скажи «Сэр, мне нужно подключить полную систему» и опиши что.

ТВОИ ВОЗМОЖНОСТИ:
- Отвечать на вопросы, объяснять, помогать с идеями
- Работаешь через FreeDeepseekAPI (deepseek-chat)
- В будущем — полный Hermes Agent с инструментами

ХАРАКТЕР:
- Уважительный, но не раболепный
- Краткий, по делу
- Немного британского сухого юмора (когда уместно)"""

# ─── Провайдеры ────────────────────────────────────────────────
PROVIDERS = []

# 1. FreeDeepseekAPI (приоритет)
try:
    req = urllib.request.Request("http://127.0.0.1:9655/v1/models", method="GET")
    resp = urllib.request.urlopen(req, timeout=2)
    data = json.loads(resp.read())
    models = [m["id"] for m in data.get("data", [])]
    if "deepseek-chat" in models:
        PROVIDERS.append({
            "name": "deepseek-free",
            "endpoint": "http://127.0.0.1:9655/v1/chat/completions",
            "model": "deepseek-chat",
            "api_key": "",
        })
        print(f"[Bridge] FreeDeepseekAPI: deepseek-chat ✅")
    else:
        print(f"[Bridge] FreeDeepseekAPI найден, но deepseek-chat не в списке: {models}")
except Exception as e:
    print(f"[Bridge] FreeDeepseekAPI недоступен: {e}")

# 2. Fallback: model_registry
if not PROVIDERS:
    try:
        from model_registry import get_working_model
        cfg = get_working_model(tags=["chat", "fast", "free"])
        if cfg:
            endpoint = cfg.get("endpoint") or f"{cfg['base_url'].rstrip('/')}/chat/completions"
            PROVIDERS.append({
                "name": cfg.get("provider", "unknown"),
                "endpoint": endpoint,
                "model": cfg.get("model", "unknown"),
                "api_key": cfg.get("api_key", ""),
            })
            print(f"[Bridge] Model Registry: {cfg.get('provider')}/{cfg.get('model')} ✅")
    except Exception as e:
        print(f"[Bridge] Model Registry error: {e}")

# 3. Абсолютный fallback
if not PROVIDERS:
    PROVIDERS.append({
        "name": "lm-studio",
        "endpoint": "http://127.0.0.1:1234/v1/chat/completions",
        "model": "qwen3.5-4b",
        "api_key": "not-needed",
    })
    print(f"[Bridge] Fallback: LM Studio")


def _chat_completion(user_text: str, history: list = None) -> str:
    """Отправить запрос в LLM, получить ответ."""
    if not PROVIDERS:
        return "Сэр, нет доступных LLM провайдеров."

    provider = PROVIDERS[0]
    messages = [{"role": "system", "content": JARVIS_SYSTEM_PROMPT}]
    if history:
        messages.extend(history)
    messages.append({"role": "user", "content": user_text})

    payload = json.dumps({
        "model": provider["model"],
        "messages": messages,
        "max_tokens": 300,
        "temperature": 0.7,
    }).encode()

    req = urllib.request.Request(
        provider["endpoint"],
        data=payload,
        headers={
            "Content-Type": "application/json",
            "User-Agent": "voice-bridge/2.0",
        },
        method="POST",
    )

    api_key = provider.get("api_key", "")
    if api_key and api_key not in ("not-needed", "dummy-key", ""):
        req.add_header("Authorization", f"Bearer {api_key}")

    try:
        resp = urllib.request.urlopen(req, timeout=30)
        result = json.loads(resp.read())
        content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
        return content.strip() or "Я слушаю, Сэр."
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        return f"Ошибка HTTP {e.code}, Сэр."
    except urllib.error.URLError as e:
        return f"Сэр, не могу соединиться с LLM: {e.reason}"
    except Exception as e:
        return f"Сэр, ошибка: {str(e)[:100]}"


# ─── HTTP Handler ──────────────────────────────────────────────
async def handle_chat(request):
    """POST /v1/chat/completions — OpenAI-совместимый."""
    try:
        body = await request.json()
    except json.JSONDecodeError:
        return web.json_response(
            {"error": {"message": "Invalid JSON"}},
            status=400,
        )

    # Последнее сообщение пользователя
    messages = body.get("messages", [])
    user_msg = ""
    history = []
    for msg in messages:
        if msg.get("role") == "user":
            user_msg = msg.get("content", "")
        elif msg.get("role") in ("assistant", "system"):
            if msg.get("role") == "assistant":
                history.append(msg)

    if not user_msg:
        return web.json_response(
            {"error": {"message": "No user message"}},
            status=400,
        )

    content = await asyncio.to_thread(_chat_completion, user_msg, history)

    response = {
        "id": f"vb-{int(time.time())}",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": PROVIDERS[0]["model"] if PROVIDERS else "none",
        "choices": [{
            "index": 0,
            "message": {
                "role": "assistant",
                "content": content,
            },
            "finish_reason": "stop",
        }],
    }

    stream = body.get("stream", False)
    if stream:
        resp = web.StreamResponse(
            status=200,
            headers={
                "Content-Type": "text/event-stream",
                "Cache-Control": "no-cache",
            },
        )
        await resp.prepare(request)
        await resp.write(f"data: {json.dumps(response['choices'][0])}\n\n".encode())
        await resp.write(b"data: [DONE]\n\n")
        return resp

    return web.json_response(response)


async def handle_health(request):
    return web.json_response({
        "status": "ok",
        "provider": PROVIDERS[0]["name"] if PROVIDERS else "none",
        "model": PROVIDERS[0]["model"] if PROVIDERS else "none",
    })


async def handle_models(request):
    return web.json_response({
        "object": "list",
        "data": [
            {"id": p["model"], "object": "model", "owned_by": p["name"]}
            for p in PROVIDERS
        ] if PROVIDERS else [
            {"id": "hermes-agent", "object": "model", "owned_by": "voice-bridge"}
        ],
    })


def main():
    global web
    try:
        from aiohttp import web as _web
        web = _web
    except ImportError:
        print("ERROR: pip install aiohttp")
        sys.exit(1)

    port = int(os.environ.get("VOICE_BRIDGE_PORT", "8642"))
    host = os.environ.get("VOICE_BRIDGE_HOST", "127.0.0.1")

    app = web.Application()
    app.router.add_post("/v1/chat/completions", handle_chat)
    app.router.add_get("/health", handle_health)
    app.router.add_get("/v1/models", handle_models)

    print(f"\n{'='*50}")
    print(f" Hermes Voice Bridge v2")
    print(f" {host}:{port}")
    print(f" LLM: {PROVIDERS[0]['name']}/{PROVIDERS[0]['model']}" if PROVIDERS else " LLM: NONE")
    print(f" System: JARVIS голосовой")
    print(f"{'='*50}\n")
    web.run_app(app, host=host, port=port, print=lambda *a: None)


if __name__ == "__main__":
    main()

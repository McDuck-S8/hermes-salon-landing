#!/usr/bin/env python3
"""
model_registry.py — Центральный регистратор провайдеров и моделей.


> Revisit: when model registry logic, provider fallback, or model selection changes. Last touched: 2026-07-02.
Единая точка входа для всех скриптов и скилов.
Вместо хардкода провайдера и модели в каждом файле — один вызов get_working_model().

Usage:
    from model_registry import get_working_model, ping_all, list_available

    config = get_working_model(tags=["chat", "fast"])
    # config = {"provider": "lm-studio", "model": "qwen3.5-4b",
    #           "base_url": "http://localhost:1234/v1", "api_key": "not-needed",
    #           "endpoint": "http://localhost:1234/v1/chat/completions"}

    statuses = ping_all()
    # {"lm-studio": {"alive": True, "latency_ms": 12}, ...}
"""

import json
import os
import subprocess
import sys
import threading
import time
from datetime import datetime
from pathlib import Path
from threading import Lock

# ═══════════════════════════════════════════════════════════════════════════════
# Provider Registry
# ═══════════════════════════════════════════════════════════════════════════════

PROVIDERS = {
    # ── OpenCode Zen (opencode.ai/zen) ──
    "opencode-zen": {
        "name": "OpenCode Zen",
        "type": "api",
        "base_url": "https://opencode.ai/zen/v1",
        "api_key": "",  # опционально — работает и без ключа
        "models": {
            "deepseek-v4-flash-free": {
                "priority": 1,
                "tags": ["chat", "free", "fast"],
            },
            "mimo-v2.5-free": {
                "priority": 2,
                "tags": ["chat", "free", "fast"],
            },
            "qwen3.6-plus-free": {
                "priority": 3,
                "tags": ["chat", "free"],
            },
            "minimax-m3-free": {
                "priority": 4,
                "tags": ["chat", "free"],
            },
            "nemotron-3-ultra-free": {
                "priority": 5,
                "tags": ["chat", "free"],
            },
            "north-mini-code-free": {
                "priority": 6,
                "tags": ["chat", "free"],
            },
        },
        "chat_endpoint": "/chat/completions",
        "ping_endpoint": None,  # TCP ping (быстрее, чем GET /models)
        "openai_compat": True,
    },

    # ── OpenCode Zen (старый, через opengateway — отключён) ──
    "opencode_zen": {
        "name": "OpenCode Zen (Gateway)",
        "type": "api",
        "base_url": None,  # определяется динамически — читает Hermes config
        "api_key": None,   #
        "models": {
            "deepseek-v4-flash-free": {
                "priority": 1,
                "tags": ["chat", "fast", "free"],
            },
            "mimo-v2.5-free": {
                "priority": 2,
                "tags": ["chat", "free"],
            },
            "nemotron-3-ultra-free": {
                "priority": 3,
                "tags": ["chat", "free"],
            },
            "qwen3.6-plus": {
                "priority": 4,
                "tags": ["chat"],
            },
            "qwen3.5-plus": {
                "priority": 5,
                "tags": ["chat"],
            },
        },
        "chat_endpoint": "/chat/completions",
        "ping_endpoint": None,  # gateway — TCP ping только
        "openai_compat": True,
    },

    # ── Qwen Free API (локальный прокси) ──
    "qwen-free": {
        "name": "Qwen Free Proxy",
        "type": "proxy",
        "base_url": "http://localhost:3264/api",
        "api_key": "dummy-key",
        "models": {
            "qwen3.7-max": {
                "priority": 1,
                "tags": ["chat", "free"],
            },
        },
        "chat_endpoint": "",
        "ping_endpoint": "",
        "openai_compat": False,
    },

    # ── DeepSeek Free API (локальный прокси) ──
    "deepseek-free": {
        "name": "DeepSeek Free Proxy",
        "type": "proxy",
        "base_url": "http://localhost:9655/v1",
        "api_key": "dummy-key",
        "models": {
            "deepseek-chat": {
                "priority": 1,
                "tags": ["chat", "fast", "free"],
            },
        },
        "chat_endpoint": "/chat/completions",
        "ping_endpoint": "/models",
        "openai_compat": True,
    },

    # ── DeepSeek Reasoner Free API ──
    "deepseek-free-reasoner": {
        "name": "DeepSeek Reasoner Proxy",
        "type": "proxy",
        "base_url": "http://localhost:9655/v1",
        "api_key": "dummy-key",
        "models": {
            "deepseek-reasoner": {
                "priority": 1,
                "tags": ["chat", "reasoning", "free"],
            },
        },
        "chat_endpoint": "/chat/completions",
        "ping_endpoint": "/models",
        "openai_compat": True,
    },

    # ── LM Studio (локально, CPU, отложено) ──
    "lm-studio": {
        "name": "LM Studio (Local)",
        "type": "local",
        "base_url": "http://localhost:1234/v1",
        "api_key": "not-needed",
        "models": {
            "qwen3.5-4b": {
                "priority": 1,
                "tags": ["chat", "fast", "local"],
            },
            "gemma-3-4b": {
                "priority": 2,
                "tags": ["chat", "local"],
            },
            "ministral-3-3b": {
                "priority": 3,
                "tags": ["chat", "fast", "local"],
            },
            "qwen3-coder-30b-a3b-instruct": {
                "priority": 4,
                "tags": ["code", "local"],
            },
            "qwen3.6-35b-a3b-mtp-mixed-q8": {
                "priority": 5,
                "tags": ["chat", "local"],
            },
            "llama-3.2-1b": {
                "priority": 10,
                "tags": ["chat", "fast", "local"],
            },
        },
        "chat_endpoint": "/chat/completions",
        "ping_endpoint": "/models",
        "openai_compat": True,
    },
}


# ═══════════════════════════════════════════════════════════════════════════════
# Ping Cache
# ═══════════════════════════════════════════════════════════════════════════════

_ping_cache = {}
_ping_cache_ttl = 15  # seconds
_ping_lock = Lock()


def _get_hermes_config():
    """Прочитать Hermes config для динамических значений."""
    try:
        import yaml
        config_paths = [
            Path.home() / ".hermes" / "config.yaml",
            Path(os.environ.get("HERMES_HOME", ".")) / "config.yaml",
            Path.cwd() / "config.yaml",
        ]
        for p in config_paths:
            if p.exists():
                with open(p) as f:
                    return yaml.safe_load(f)
    except Exception:
        pass
    return {}


def _resolve_provider_config(provider_id):
    """
    Достать конфиг провайдера.
    Для opencode_zen — читает из Hermes config (base_url может быть переопределён).
    """
    pdef = PROVIDERS.get(provider_id)
    if not pdef:
        return None

    cfg = dict(pdef)  # shallow copy

    # Для opencode_zen пытаемся прочитать реальный base_url из конфига
    if provider_id == "opencode_zen":
        hermes_cfg = _get_hermes_config()
        model_section = hermes_cfg.get("model", {})
        if model_section.get("base_url"):
            cfg["base_url"] = model_section["base_url"]
        if model_section.get("api_key"):
            cfg["api_key"] = model_section["api_key"]

    return cfg


# ═══════════════════════════════════════════════════════════════════════════════
# Ping
# ═══════════════════════════════════════════════════════════════════════════════

def _ping_provider(provider_id):
    """
    Проверить, жив ли провайдер.
    Возвращает {"alive": bool, "latency_ms": int|None, "error": str|None}.
    """
    cfg = _resolve_provider_config(provider_id)
    if not cfg:
        return {"alive": False, "latency_ms": None, "error": "unknown provider"}

    base_url = cfg.get("base_url")
    api_key = cfg.get("api_key")
    if not base_url and not api_key:
        # Нет ни URL, ни API-ключа — провайдер не настроен
        return {"alive": False, "latency_ms": None, "error": "not configured"}
    if not base_url:
        # opencode_zen без известного URL — считаем живым (это основной провайдер)
        return {"alive": True, "latency_ms": 0, "error": None}

    ping_path = cfg.get("ping_endpoint")
    if not ping_path:
        # Нет ping-эндпоинта — проверяем через TCP port connect
        return _ping_tcp(base_url)

    return _ping_http(base_url, ping_path, cfg.get("api_key"))


def _ping_tcp(base_url):
    """Проверить, открыт ли порт."""
    try:
        from urllib.parse import urlparse
        parsed = urlparse(base_url)
        host = parsed.hostname or "localhost"
        port = parsed.port or (443 if parsed.scheme == "https" else 80)

        import socket
        start = time.time()
        sock = socket.create_connection((host, port), timeout=3)
        sock.close()
        latency = int((time.time() - start) * 1000)
        return {"alive": True, "latency_ms": latency, "error": None}
    except Exception as e:
        return {"alive": False, "latency_ms": None, "error": str(e)}


def _ping_http(base_url, ping_path, api_key=None):
    """Проверить HTTP-эндпоинт."""
    try:
        import urllib.request

        url = base_url.rstrip("/") + "/" + ping_path.lstrip("/")
        req = urllib.request.Request(url, method="GET")
        if api_key and api_key not in ("not-needed", "dummy-key"):
            req.add_header("Authorization", f"Bearer {api_key}")

        start = time.time()
        with urllib.request.urlopen(req, timeout=5) as resp:
            latency = int((time.time() - start) * 1000)
            return {
                "alive": resp.status == 200,
                "latency_ms": latency,
                "error": None if resp.status == 200 else f"HTTP {resp.status}",
            }
    except Exception as e:
        return {"alive": False, "latency_ms": None, "error": str(e)}


# ═══════════════════════════════════════════════════════════════════════════════
# Public API
# ═══════════════════════════════════════════════════════════════════════════════

def ping_all(force=False):
    """
    Пингануть всех провайдеров (параллельно).
    Результаты кешируются на _ping_cache_ttl секунд.
    """
    global _ping_cache

    with _ping_lock:
        now = time.time()
        if not force and _ping_cache and (now - _ping_cache.get("_ts", 0)) < _ping_cache_ttl:
            return {k: v for k, v in _ping_cache.items() if k != "_ts"}

        results = {}
        threads = []

        def ping_one(pid):
            results[pid] = _ping_provider(pid)

        for pid in PROVIDERS:
            t = threading.Thread(target=ping_one, args=(pid,), daemon=True)
            threads.append(t)
            t.start()

        # Ждём все с общим таймаутом
        for t in threads:
            t.join(timeout=6)

        # Для тех что не успели — умерли
        for pid in PROVIDERS:
            if pid not in results:
                results[pid] = {"alive": False, "latency_ms": None,
                                "error": "ping timeout"}

        _ping_cache = results.copy()
        _ping_cache["_ts"] = now
        return results


def get_working_model(tags=None, min_priority=None, prefer_local=False):
    """
    Вернуть конфиг лучшей работающей модели.

    Параметры:
        tags: список тэгов для фильтрации (например ["chat", "fast"])
        min_priority: минимальный приоритет (1 = лучший, 10 = худший)
        prefer_local: предпочесть локальные модели (lm-studio)

    Возвращает:
        dict с ключами: provider, model, base_url, api_key, endpoint, type
        или None если ничего не работает.
    """
    if tags is None:
        tags = ["chat"]

    pings = ping_all()
    candidates = []

    for pid, pdef in PROVIDERS.items():
        pong = pings.get(pid, {})
        if not pong.get("alive"):
            continue

        cfg = _resolve_provider_config(pid)
        if not cfg:
            continue

        base_url = cfg.get("base_url")
        chat_endpoint = cfg.get("chat_endpoint", "/chat/completions")
        api_key = cfg.get("api_key", "")
        is_local = cfg.get("type") == "local"

        for model_name, mdef in cfg.get("models", {}).items():
            # Фильтр по тэгам
            if tags and not any(t in mdef.get("tags", []) for t in tags):
                continue

            # Фильтр по приоритету
            if min_priority and mdef.get("priority", 99) > min_priority:
                continue

            # Фильтр prefer_local
            if prefer_local and not is_local:
                continue

            endpoint = None
            if base_url and chat_endpoint:
                endpoint = base_url.rstrip("/") + "/" + chat_endpoint.lstrip("/")

            candidates.append({
                "provider": pid,
                "provider_name": cfg.get("name", pid),
                "model": model_name,
                "base_url": base_url,
                "api_key": api_key,
                "endpoint": endpoint,
                "type": cfg.get("type", "api"),
                "priority": mdef.get("priority", 99),
                "tags": mdef.get("tags", []),
                "latency_ms": pong.get("latency_ms"),
                "is_local": is_local,
            })

    if not candidates:
        return None

    # Сортируем: приоритет, потом cloud (не local), потом latency
    candidates.sort(key=lambda c: (
        c["priority"],
        1 if c["is_local"] else 0,   # cloud выше локальных
        c["latency_ms"] or 9999,
    ))

    return candidates[0]


def get_model_config(provider_name=None, model_name=None):
    """
    Вернуть конфиг для конкретной модели/провайдера.
    Если provider_name не указан — ищет по model_name по всем провайдерам.
    """
    for pid, pdef in PROVIDERS.items():
        if provider_name and pid != provider_name:
            continue
        for mname, mdef in pdef.get("models", {}).items():
            if model_name and mname != model_name:
                continue
            if provider_name and pid == provider_name:
                cfg = _resolve_provider_config(pid)
                base_url = cfg.get("base_url") if cfg else pdef.get("base_url")
                api_key = cfg.get("api_key") if cfg else pdef.get("api_key")
                return {
                    "provider": pid,
                    "model": mname,
                    "base_url": base_url,
                    "api_key": api_key,
                    "endpoint": (base_url.rstrip("/") + "/" + pdef.get("chat_endpoint", "/chat/completions").lstrip("/"))
                    if base_url and pdef.get("chat_endpoint") else None,
                    "tags": mdef.get("tags", []),
                    "type": pdef.get("type", "api"),
                }
            if not model_name or mname == model_name:
                cfg = _resolve_provider_config(pid)
                base_url = cfg.get("base_url") if cfg else pdef.get("base_url")
                return {
                    "provider": pid,
                    "model": mname,
                    "base_url": base_url,
                    "tags": mdef.get("tags", []),
                }
    return None


def list_available(tags=None, alive_only=True):
    """
    Показать все модели с их статусами.

    Возвращает список словарей:
        provider, model, alive, latency, priority, tags, type
    """
    pings = ping_all()
    rows = []

    for pid, pdef in PROVIDERS.items():
        pong = pings.get(pid, {})
        alive = pong.get("alive", False)

        if alive_only and not alive:
            continue

        for mname, mdef in pdef.get("models", {}).items():
            if tags and not any(t in mdef.get("tags", []) for t in tags):
                continue

            rows.append({
                "provider": pid,
                "provider_name": pdef.get("name", pid),
                "model": mname,
                "alive": alive,
                "latency_ms": pong.get("latency_ms"),
                "priority": mdef.get("priority", 99),
                "tags": mdef.get("tags", []),
                "type": pdef.get("type", "api"),
            })

    return rows


def print_status(tags=None):
    """Вывести красивый статус всех провайдеров."""
    alive_count = 0
    total_count = 0

    print()
    print("=" * 60)
    print("  Model Registry — Provider Status")
    print("=" * 60)

    for pid, pdef in PROVIDERS.items():
        pong = _ping_provider(pid)
        alive = pong.get("alive", False)
        latency = pong.get("latency_ms")
        error = pong.get("error")

        status_symbol = "✓" if alive else "✗"
        latency_str = f"{latency}ms" if latency else "-"
        total_count += 1
        if alive:
            alive_count += 1

        print(f"\n  {status_symbol} {pdef['name']:<30} [{latency_str:>6}]")
        if error and not alive:
            print(f"    [WARN] {error}")

        if alive:
            models = pdef.get("models", {})
            for mname, mdef in sorted(models.items(), key=lambda x: x[1].get("priority", 99)):
                tags_str = ", ".join(mdef.get("tags", []))
                print(f"    ▸ {mname:<45} [{tags_str}]")

    print(f"\n  {'─' * 50}")
    print(f"  {alive_count}/{total_count} providers alive")
    print(f"  {'─' * 50}")
    print()


# ═══════════════════════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Model Registry CLI")
    parser.add_argument("--ping", action="store_true", help="Пингануть всех")
    parser.add_argument("--status", action="store_true", help="Показать статус")
    parser.add_argument("--best", type=str, nargs="*", default=None,
                       help="Показать лучшую модель (тэги через пробел)")
    parser.add_argument("--json", action="store_true", help="Вывод в JSON")
    args = parser.parse_args()

    if args.ping or args.status:
        if args.json:
            print(json.dumps(ping_all(), indent=2, default=str))
        else:
            print_status(tags=args.best)

    elif args.best is not None:
        tags = args.best if args.best else ["chat"]
        config = get_working_model(tags=tags)
        if args.json:
            print(json.dumps(config, indent=2, default=str))
        else:
            if config:
                print(f"  Best model: {config['provider']}/{config['model']}")
                print(f"  Endpoint:   {config['endpoint']}")
                print(f"  Tags:       {', '.join(config['tags'])}")
            else:
                print("  No working model found.")

    else:
        print_status()

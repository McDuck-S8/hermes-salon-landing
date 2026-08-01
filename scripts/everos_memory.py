"""EverOS Memory Client — интеграция с Hermes.
# Proxy configuration
proxy_handler = urllib.request.ProxyHandler({
    'http': 'http://127.0.0.1:10809',

> Revisit: when everos memory logic, cloud sync, or local cache changes. Last touched: 2026-07-02.
    'https': 'http://127.0.0.1:10809'
})
opener = urllib.request.build_opener(proxy_handler)


Использование из скриптов (execute_code):
    from hermes_tools import terminal
    from everos_memory import EverOS
    
    ev = EverOS()
    # Поиск
    result = ev.search("query text")
    # Добавить память
    result = ev.add("Важный факт про X", user_id="hermes", session_id="current")
    # Залить всё из буфера
    result = ev.flush()
    # Здоровье
    ok = ev.health()
"""

import json
import urllib.request
import urllib.error
from typing import Any

BASE = "http://127.0.0.1:8111"


class EverOS:
    """Клиент для EverOS API памяти."""

    def __init__(self, base: str = BASE):
        self.base = base.rstrip("/")

    def _req(self, method: str, path: str, data: dict | None = None) -> dict[str, Any]:
        url = f"{self.base}{path}"
        body = json.dumps(data).encode() if data else None
        req = urllib.request.Request(
            url,
            data=body,
            method=method,
            headers={"Content-Type": "application/json"} if body else {},
        )
        try:
            with opener.open(req, timeout=10) as resp:
                return json.loads(resp.read())
        except urllib.error.HTTPError as e:
            return {"error": f"HTTP {e.code}: {e.read().decode()}"}
        except urllib.error.URLError as e:
            return {"error": f"Connection failed: {e.reason}"}
        except Exception as e:
            return {"error": str(e)}

    def health(self) -> dict:
        """Проверить, жив ли сервер."""
        return self._req("GET", "/health")

    def add(self, text: str, user_id: str = "hermes",
            agent_id: str = "hermes",
            session_id: str | None = None) -> dict:
        """Добавить текст в память EverOS.

        NOTE: memorize pipeline требует LLM с function calling.
        deepseek-v4-flash-free НЕ поддерживает — add вернёт 500.
        Нужен gpt-4o-mini или подобный.
        """
        import time
        payload = {
            "messages": [{
                "role": "user",
                "content": text,
                "sender_id": agent_id,
                "timestamp": int(time.time())
            }],
            "user_id": user_id,
            "agent_id": agent_id,
            "session_id": session_id or f"hermes-{int(time.time())}"
        }
        return self._req("POST", "/api/v1/memory/add", payload)

    def search(self, query: str, user_id: str = "hermes",
               top_k: int = 5) -> dict:
        """Поиск по памяти. Тоже требует LLM с function calling."""
        payload = {"query": query, "user_id": user_id, "top_k": top_k}
        return self._req("POST", "/api/v1/memory/search", payload)

    def get(self, memcell_id: str) -> dict:
        """Получить конкретную запись памяти."""
        return self._req("GET", f"/api/v1/memory/get/{memcell_id}")

    def flush(self, session_id: str, user_id: str = "hermes") -> dict:
        """Принудительно сбросить буфер сессии."""
        payload = {"session_id": session_id, "user_id": user_id}
        return self._req("POST", "/api/v1/memory/flush", payload)


# Быстрые тесты
if __name__ == "__main__":
    ev = EverOS()
    print("Health:", ev.health())
    print()
    print("Add:", ev.add("Тестовая запись от Hermes: EverOS интегрирован"))
    print()
    print("Search:", ev.search("EverOS"))

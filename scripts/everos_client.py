"""EverOS Memory Client — Hermes integration with cloud API.

Установка: pip install everos
API ключ: EVEROS_API_KEY в .env или переменной окружения

> Revisit: when everos client logic, API integration, or memory sync changes. Last touched: 2026-07-02.
API: https://api.evermind.ai

Использование:
    from everos_client import EverOSMemory
    
    mem = EverOSMemory()
    
    # Добавить сообщение
    result = mem.add(user_id="hermes", messages=[{...}])
    
    # Поиск по памяти
    results = mem.search(user_id="hermes", query="что мы обсуждали?")
"""

import os
import time
from typing import Any

import everos


class EverOSMemory:
    """Клиент EverOS для Hermes.

    Поддерживает: добавление памяти, поиск, мониторинг задач.
    """

    def __init__(self, api_key: str | None = None):
        api_key = api_key or os.environ.get("EVEROS_API_KEY")
        if not api_key:
            raise ValueError(
                "EVEROS_API_KEY not set. Pass api_key= or export EVEROS_API_KEY"
            )
        self._client = everos.EverOS(api_key=api_key)

    # ── Добавление памяти ──────────────────────────────────────────

    def add(
        self,
        user_id: str,
        messages: list[dict],
        session_id: str | None = None,
        async_mode: bool = True,
    ) -> dict:
        """Добавить сообщения в память EverOS.

        Args:
            user_id: идентификатор пользователя
            messages: список сообщений [{"role": str, "content": str, "timestamp": int_ms}]
            session_id: ID сессии (опционально)
            async_mode: True = асинхронная обработка (быстрее)

        Returns:
            {"message_count": int, "status": str, "task_id": str|None}
        """
        ts = int(time.time() * 1000)
        formatted = []
        for msg in messages:
            formatted.append({
                "role": msg.get("role", "user"),
                "timestamp": msg.get("timestamp", ts),
                "content": msg["content"],
            })

        kwargs = dict(
            user_id=user_id,
            messages=formatted,
        )
        if session_id:
            kwargs["session_id"] = session_id

        resp = self._client.v1.memories.add(**kwargs)
        d = resp.data
        return {"message_count": d.message_count, "status": d.status, "task_id": d.task_id}

    # ── Поиск ──────────────────────────────────────────────────────

    def search(
        self,
        user_id: str,
        query: str,
        method: str = "agentic",
        top_k: int = 5,
        memory_types: list[str] | None = None,
    ) -> dict:
        """Поиск в памяти EverOS.

        Args:
            user_id: владелец памяти
            query: поисковый запрос
            method: keyword | vector | hybrid | agentic
            top_k: сколько результатов
            memory_types: фильтр по типу памяти

        Returns:
            словарь с найденными эпизодами, профилями, фактами
        """
        kwargs = dict(
            filters={"user_id": user_id},
            query=query,
            method=method,
            top_k=top_k,
        )
        if memory_types:
            kwargs["memory_types"] = memory_types

        resp = self._client.v1.memories.search(**kwargs)
        d = resp.data

        result = {
            "query": {"text": d.query.text, "method": d.query.method},
            "episodes": [],
            "profiles": [],
            "raw_messages": [],
            "agent_memory": [],
        }

        if d.episodes:
            result["episodes"] = [self._serialize(x) for x in d.episodes]
        if d.profiles:
            result["profiles"] = [self._serialize(x) for x in d.profiles]
        if d.raw_messages:
            result["raw_messages"] = [self._serialize(x) for x in d.raw_messages]
        if d.agent_memory:
            result["agent_memory"] = [self._serialize(x) for x in d.agent_memory]

        return result

    # ── Статус задачи ──────────────────────────────────────────────

    def task_status(self, task_id: str) -> str:
        """Проверить статус асинхронной задачи."""
        resp = self._client.v1.tasks.retrieve(task_id=task_id)
        return resp.data.status

    # ── Утилиты ────────────────────────────────────────────────────

    @staticmethod
    def _serialize(obj: Any) -> dict:
        """Преобразовать pydantic объект в dict рекурсивно."""
        if hasattr(obj, "model_dump"):
            return obj.model_dump()
        if hasattr(obj, "dict"):
            return obj.dict()
        return str(obj)


# ── CLI test ──────────────────────────────────────────────────────

if __name__ == "__main__":
    import json

    key = os.environ.get("EVEROS_API_KEY")
    if not key:
        print("[FAIL] EVEROS_API_KEY не найден")
        exit(1)

    mem = EverOSMemory()

    # Add test
    print("=== ADD ===")
    r = mem.add(
        user_id="hermes_test",
        session_id="cli-test-1",
        messages=[
            {"role": "user", "content": "EverOS это память для ИИ агентов. Сегодня тестируем интеграцию."},
        ],
    )
    print(json.dumps(r, indent=2))

    # Wait a bit
    if r.get("task_id"):
        print(f"\n=== TASK STATUS ===")
        import time
        time.sleep(3)
        s = mem.task_status(r["task_id"])
        print(f"  {r['task_id']}: {s}")

    # Search test
    print("\n=== SEARCH ===")
    s = mem.search(user_id="hermes_test", query="EverOS память")
    print(json.dumps(s, indent=2, ensure_ascii=False))

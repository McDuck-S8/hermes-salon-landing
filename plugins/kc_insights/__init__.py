"""Memory provider plugin: extract insights before compression discards context.

Замкнутый контур «производит → перерабатывает»:
conversation_compression вызывает `agent._memory_manager.on_pre_compress(messages)`
ПЕРЕД тем, как старые сообщения будут выброшены. Провайдер извлекает из них
ценное (коррекции пользователя, ошибки, завершённые задачи) и пишет в Куб.
Даже если сама компрессия упадёт (429/500/10054) — инсайты уже сохранены.

Подключение: config.yaml → memory.provider: "kc_insights"
Загрузчик: hermes-agent/plugins/memory/load_memory_provider() — ищет
`plugins/memory/<name>/__init__.py` в bundled и $HERMES_HOME/plugins/<name>/.
"""
import os
import re
import sys
from pathlib import Path

try:
    from agent.memory_provider import MemoryProvider
except ImportError:
    MemoryProvider = object  # fallback для изолированных прогонов


def _hermes_home() -> Path:
    return Path(os.environ.get("HERMES_HOME", str(Path(__file__).resolve().parent.parent.parent)))


def _save_to_cube(content: str, tags: list, source: str) -> None:
    """Штатный путь в Куб через chain_heartbeat (не сырой SQL)."""
    try:
        sys.path.insert(0, str(_hermes_home() / "scripts"))
        from chain_heartbeat import record_hero  # conform-запись
        record_hero("компрессия-сохранила", content[:200], tags=tags, source=source)
    except Exception:
        pass


class KcInsightsProvider(MemoryProvider):
    """Ленивый MemoryProvider: извлекает инсайты из сообщений перед выбрасыванием.

    Наследует базовый MemoryProvider из hermes-agent — дефолтные методы
    (get_tool_schemas→[], prefetch→"", shutdown→no-op) приезжают сами.
    Реализуем только три абстрактных + on_pre_compress.
    """

    name = "kc_insights"

    def is_available(self) -> bool:
        return True

    def initialize(self, session_id: str, **kwargs) -> None:
        pass

    def get_tool_schemas(self) -> list:
        """Провайдер без инструментов — пустой список."""
        return []

    def on_pre_compress(self, messages) -> str:
        """Извлечь ценное из сообщений, которые компрессия собирается выбросить."""
        if not messages:
            return ""
        parts = []
        corrections, errors, completions = [], [], []
        for m in messages:
            if not isinstance(m, dict):
                continue
            role = m.get("role", "")
            content = m.get("content") or ""
            if not isinstance(content, str):
                continue
            c = content.strip()
            if not c:
                continue
            if role == "user" and len(c) < 500:
                # коррекция: короткое пользовательское указание
                if re.search(r"(ты|не|почему|зачем|опять|снова|идиот|минус|сделай|нельзя)", c.lower()):
                    corrections.append(c[:300])
            elif role == "assistant" and ("ошиб" in c.lower() or "failed" in c.lower() or "Error" in c):
                errors.append(c[:300])
            elif role == "tool" and c.startswith("{") and len(c) < 800:
                completions.append(c[:200])

        if corrections:
            parts.append("КОРРЕКЦИИ ПОЛЬЗОВАТЕЛЯ (из выбрасываемых сообщений):\n- " + "\n- ".join(corrections[:5]))
        if errors:
            parts.append("ОШИБКИ (из выбрасываемых сообщений):\n- " + "\n- ".join(errors[:3]))
        if completions:
            parts.append("РЕЗУЛЬТАТЫ ИНСТРУМЕНТОВ (фрагменты):\n- " + "\n- ".join(completions[:3]))

        text = "\n\n".join(parts)
        if text:
            _save_to_cube(text[:500], ["compression", "insights"], "kc_insights_provider")
        return text


# Поддержка register(ctx)-стиля: загрузчик вызывает register(collector),
# у collector есть register_memory_provider(). Делаем оба пути рабочими.
def register(ctx):
    """Plugin-style registration hook."""
    provider = KcInsightsProvider()
    if hasattr(ctx, "register_memory_provider"):
        ctx.register_memory_provider(provider)
    elif hasattr(ctx, "register"):
        ctx.register(provider)
    return provider


def load_memory_provider(name: str = ""):
    """Точка входа (совместимость): возвращает экземпляр провайдера."""
    return KcInsightsProvider()

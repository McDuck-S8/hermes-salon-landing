"""Юнит-тест: kc_insights — memory-провайдер, извлекающий инсайты перед компрессией.

Контур «производит → перерабатывает»: conversation_compression вызывает
on_pre_compress(messages) ПЕРЕД выбрасыванием старых сообщений. Провайдер
должен извлекать коррекции/ошибки/результаты, чтобы они не терялись даже
при падении самой компрессии (429/500/10054).
"""
import os
import sys

import pytest

os.environ["HERMES_HOME"] = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "hermes-agent")))

from agent.memory_manager import MemoryManager
from plugins.memory import load_memory_provider


@pytest.fixture
def provider():
    mp = load_memory_provider("kc_insights")
    assert mp is not None, "kc_insights провайдер должен загружаться штатным загрузчиком"
    return mp


def test_loads_via_standard_loader(provider):
    assert provider.name == "kc_insights"
    assert provider.is_available() is True


def test_registers_into_memory_manager(provider):
    mm = MemoryManager()
    mm.add_provider(provider)
    assert len(mm._providers) == 1


def test_extracts_corrections_and_errors(provider):
    msgs = [
        {"role": "user", "content": "ты опять не сделал, почему ждёшь команды?"},
        {"role": "assistant", "content": "Ошибка: connection refused при вызове API"},
        {"role": "tool", "content": '{"status": "ok", "result": "deploy done"}'},
        {"role": "user", "content": "продолжай"},
    ]
    out = provider.on_pre_compress(msgs)
    assert "КОРРЕКЦИИ" in out
    assert "ты опять не сделал" in out
    assert "ОШИБКИ" in out
    assert "connection refused" in out


def test_empty_messages_return_empty(provider):
    assert provider.on_pre_compress([]) == ""


def test_noise_messages_produce_no_insights(provider):
    msgs = [
        {"role": "user", "content": "привет, как дела?"},
        {"role": "assistant", "content": "Всё хорошо, работаю."},
    ]
    assert provider.on_pre_compress(msgs) == ""

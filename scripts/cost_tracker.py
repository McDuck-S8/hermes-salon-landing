#!/usr/bin/env python3
"""
Cost Tracker — трекинг токенов и стоимости LLM вызовов.
Интегрируется в autonomous_agent для контроля затрат.
"""

import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Optional, Any
from dataclasses import dataclass, asdict

HERMES_HOME = Path(__file__).resolve().parent.parent
CACHE_DIR = HERMES_HOME / "cache"
COST_DB = CACHE_DIR / "cost_tracker.db"

# Цены за 1M токенов (USD) — актуальные на 2025
MODEL_PRICES = {
    # OpenAI
    "gpt-4o": {"input": 5.00, "output": 15.00},
    "gpt-4o-mini": {"input": 0.15, "output": 0.60},
    "gpt-4-turbo": {"input": 10.00, "output": 30.00},
    "gpt-3.5-turbo": {"input": 0.50, "output": 1.50},
    # Anthropic
    "claude-3-5-sonnet": {"input": 3.00, "output": 15.00},
    "claude-3-5-haiku": {"input": 1.00, "output": 5.00},
    "claude-3-opus": {"input": 15.00, "output": 75.00},
    # Google
    "gemini-1.5-pro": {"input": 3.50, "output": 10.50},
    "gemini-1.5-flash": {"input": 0.075, "output": 0.30},
    # OpenRouter / Other
    "deepseek-chat": {"input": 0.14, "output": 0.28},
    "deepseek-reasoner": {"input": 0.55, "output": 2.19},
    "qwen-2.5-72b": {"input": 0.35, "output": 0.40},
    "nemotron-3-ultra": {"input": 0.50, "output": 1.50},
}

DEFAULT_PRICE = {"input": 1.00, "output": 3.00}  # fallback

DAILY_LIMIT_USD = 50.0  # дневной лимит по умолчанию


@dataclass
class CostRecord:
    timestamp: str
    model: str
    input_tokens: int
    output_tokens: int
    input_cost_usd: float
    output_cost_usd: float
    total_cost_usd: float
    action_id: str
    tier: str
    provider: str


def init_db():
    """Инициализация БД для трекинга затрат."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(COST_DB))
    conn.execute("""
        CREATE TABLE IF NOT EXISTS cost_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            model TEXT NOT NULL,
            input_tokens INTEGER DEFAULT 0,
            output_tokens INTEGER DEFAULT 0,
            input_cost_usd REAL DEFAULT 0.0,
            output_cost_usd REAL DEFAULT 0.0,
            total_cost_usd REAL DEFAULT 0.0,
            action_id TEXT,
            tier TEXT,
            provider TEXT
        )
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON cost_records(timestamp)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_action_id ON cost_records(action_id)")
    conn.commit()
    conn.close()


def get_model_price(model: str) -> Dict[str, float]:
    """Получить цену для модели (с fuzzy matching)."""
    model_lower = model.lower()
    for key, price in MODEL_PRICES.items():
        if key in model_lower or model_lower in key:
            return price
    return DEFAULT_PRICE


def log_cost(
    model: str,
    input_tokens: int,
    output_tokens: int,
    action_id: str = "",
    tier: str = "",
    provider: str = ""
) -> CostRecord:
    """Записать стоимость вызова LLM."""
    init_db()
    
    price = get_model_price(model)
    input_cost = (input_tokens / 1_000_000) * price["input"]
    output_cost = (output_tokens / 1_000_000) * price["output"]
    total_cost = input_cost + output_cost
    
    record = CostRecord(
        timestamp=datetime.now().isoformat(),
        model=model,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        input_cost_usd=round(input_cost, 6),
        output_cost_usd=round(output_cost, 6),
        total_cost_usd=round(total_cost, 6),
        action_id=action_id,
        tier=tier,
        provider=provider
    )
    
    conn = sqlite3.connect(str(COST_DB))
    conn.execute("""
        INSERT INTO cost_records 
        (timestamp, model, input_tokens, output_tokens, input_cost_usd, output_cost_usd, total_cost_usd, action_id, tier, provider)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        record.timestamp, record.model, record.input_tokens, record.output_tokens,
        record.input_cost_usd, record.output_cost_usd, record.total_cost_usd,
        record.action_id, record.tier, record.provider
    ))
    conn.commit()
    conn.close()
    
    return record


def get_daily_cost(date: Optional[str] = None) -> float:
    """Получить суммарные затраты за день."""
    init_db()
    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")
    
    conn = sqlite3.connect(str(COST_DB))
    cursor = conn.execute("""
        SELECT SUM(total_cost_usd) FROM cost_records 
        WHERE timestamp LIKE ?
    """, (f"{date}%",))
    result = cursor.fetchone()[0]
    conn.close()
    return round(result or 0.0, 4)


def get_cost_summary(days: int = 7) -> Dict[str, Any]:
    """Получить сводку затрат за N дней."""
    init_db()
    since = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    
    conn = sqlite3.connect(str(COST_DB))
    conn.row_factory = sqlite3.Row
    
    # Общая сумма
    total = conn.execute("""
        SELECT SUM(total_cost_usd) as total FROM cost_records WHERE timestamp >= ?
    """, (since,)).fetchone()["total"] or 0.0
    
    # По моделям
    by_model = conn.execute("""
        SELECT model, SUM(total_cost_usd) as cost, COUNT(*) as calls,
               SUM(input_tokens) as in_tokens, SUM(output_tokens) as out_tokens
        FROM cost_records WHERE timestamp >= ?
        GROUP BY model ORDER BY cost DESC
    """, (since,)).fetchall()
    
    # По действиям
    by_action = conn.execute("""
        SELECT action_id, SUM(total_cost_usd) as cost, COUNT(*) as calls
        FROM cost_records WHERE timestamp >= ? AND action_id != ''
        GROUP BY action_id ORDER BY cost DESC
    """, (since,)).fetchall()
    
    # По тирам
    by_tier = conn.execute("""
        SELECT tier, SUM(total_cost_usd) as cost, COUNT(*) as calls
        FROM cost_records WHERE timestamp >= ? AND tier != ''
        GROUP BY tier ORDER BY cost DESC
    """, (since,)).fetchall()
    
    conn.close()
    
    return {
        "period_days": days,
        "total_usd": round(total, 4),
        "daily_limit_usd": DAILY_LIMIT_USD,
        "daily_cost_usd": get_daily_cost(),
        "by_model": [dict(r) for r in by_model],
        "by_action": [dict(r) for r in by_action],
        "by_tier": [dict(r) for r in by_tier],
    }


def check_daily_limit() -> Dict[str, Any]:
    """Проверить дневной лимит."""
    daily = get_daily_cost()
    return {
        "daily_cost_usd": daily,
        "daily_limit_usd": DAILY_LIMIT_USD,
        "remaining_usd": round(DAILY_LIMIT_USD - daily, 4),
        "limit_exceeded": daily >= DAILY_LIMIT_USD,
        "usage_pct": round((daily / DAILY_LIMIT_USD) * 100, 1) if DAILY_LIMIT_USD > 0 else 0.0
    }


def set_daily_limit(limit_usd: float):
    """Установить дневной лимит (в памяти, для текущего запуска)."""
    global DAILY_LIMIT_USD
    DAILY_LIMIT_USD = limit_usd


# CLI для быстрой проверки
if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "summary":
        days = int(sys.argv[2]) if len(sys.argv) > 2 else 7
        summary = get_cost_summary(days)
        print(json.dumps(summary, indent=2, ensure_ascii=False))
    elif len(sys.argv) > 1 and sys.argv[1] == "limit":
        check = check_daily_limit()
        print(json.dumps(check, indent=2, ensure_ascii=False))
    else:
        print("Usage: python cost_tracker.py summary [days] | limit")
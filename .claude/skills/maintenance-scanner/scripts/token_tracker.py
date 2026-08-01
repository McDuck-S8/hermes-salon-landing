#!/usr/bin/env python3
"""
Token Tracker — Logs token usage and costs for all agent operations.
Tracks per-operation, per-session, and cumulative totals.
"""

import os
import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from contextlib import contextmanager

HERMES_HOME = Path(os.environ.get("HERMES_HOME", "D:/Portable_Soft/hermes"))
TOKEN_DB = HERMES_HOME / "cache" / "token_usage.db"

# Model pricing (per 1M tokens, USD) - update as needed
MODEL_PRICING = {
    "gpt-4o": {"input": 5.00, "output": 15.00},
    "gpt-4o-mini": {"input": 0.15, "output": 0.60},
    "gpt-4-turbo": {"input": 10.00, "output": 30.00},
    "gpt-3.5-turbo": {"input": 0.50, "output": 1.50},
    "claude-3-opus": {"input": 15.00, "output": 75.00},
    "claude-3-sonnet": {"input": 3.00, "output": 15.00},
    "claude-3-haiku": {"input": 0.25, "output": 1.25},
    "granite4.1:3b": {"input": 0.00, "output": 0.00},  # Local Ollama
    "llama3": {"input": 0.00, "output": 0.00},
    "mistral": {"input": 0.00, "output": 0.00},
    "codellama": {"input": 0.00, "output": 0.00},
    "deepseek-coder": {"input": 0.00, "output": 0.00},
}

@dataclass
class TokenRecord:
    """Single token usage record."""
    timestamp: str
    session_id: str
    operation: str          # chat, workflow, embedding, completion, etc.
    model: str
    input_tokens: int
    output_tokens: int
    total_tokens: int
    estimated_cost_usd: float
    metadata: Dict[str, Any]

class TokenTracker:
    """Tracks token usage and costs."""
    
    def __init__(self, db_path: Path = TOKEN_DB):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
        self.current_session = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def _init_db(self):
        """Initialize token usage database."""
        conn = sqlite3.connect(str(self.db_path), timeout=5)
        try:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS token_usage (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    session_id TEXT NOT NULL,
                    operation TEXT NOT NULL,
                    model TEXT NOT NULL,
                    input_tokens INTEGER NOT NULL,
                    output_tokens INTEGER NOT NULL,
                    total_tokens INTEGER NOT NULL,
                    estimated_cost_usd REAL NOT NULL,
                    metadata TEXT
                )
            """)
            # Create indexes separately (SQLite doesn't support inline INDEX)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_session ON token_usage (session_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON token_usage (timestamp)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_model ON token_usage (model)")
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS session_summary (
                    session_id TEXT PRIMARY KEY,
                    start_time TEXT NOT NULL,
                    end_time TEXT,
                    total_input_tokens INTEGER DEFAULT 0,
                    total_output_tokens INTEGER DEFAULT 0,
                    total_tokens INTEGER DEFAULT 0,
                    total_cost_usd REAL DEFAULT 0.0,
                    operation_count INTEGER DEFAULT 0
                )
            """)
            conn.commit()
        finally:
            conn.close()
    
    def _estimate_cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
        """Estimate cost in USD."""
        pricing = MODEL_PRICING.get(model, {"input": 0, "output": 0})
        input_cost = (input_tokens / 1_000_000) * pricing["input"]
        output_cost = (output_tokens / 1_000_000) * pricing["output"]
        return input_cost + output_cost
    
    def log_usage(self, operation: str, model: str, input_tokens: int, output_tokens: int,
                  session_id: str = None, metadata: Dict = None) -> TokenRecord:
        """Log token usage."""
        if session_id is None:
            session_id = self.current_session
        
        total = input_tokens + output_tokens
        cost = self._estimate_cost(model, input_tokens, output_tokens)
        
        record = TokenRecord(
            timestamp=datetime.now().isoformat(),
            session_id=session_id,
            operation=operation,
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=total,
            estimated_cost_usd=cost,
            metadata=metadata or {}
        )
        
        conn = sqlite3.connect(str(self.db_path), timeout=5)
        try:
            conn.execute("""
                INSERT INTO token_usage (timestamp, session_id, operation, model, input_tokens, 
                                         output_tokens, total_tokens, estimated_cost_usd, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (record.timestamp, record.session_id, record.operation, record.model,
                  record.input_tokens, record.output_tokens, record.total_tokens,
                  record.estimated_cost_usd, json.dumps(record.metadata)))
            
            # Update session summary
            conn.execute("""
                INSERT INTO session_summary (session_id, start_time, end_time, 
                                           total_input_tokens, total_output_tokens, total_tokens,
                                           total_cost_usd, operation_count)
                VALUES (?, ?, ?, ?, ?, ?, ?, 1)
                ON CONFLICT(session_id) DO UPDATE SET
                    end_time=excluded.end_time,
                    total_input_tokens=total_input_tokens+excluded.total_input_tokens,
                    total_output_tokens=total_output_tokens+excluded.total_output_tokens,
                    total_tokens=total_tokens+excluded.total_tokens,
                    total_cost_usd=total_cost_usd+excluded.total_cost_usd,
                    operation_count=operation_count+1
            """, (session_id, record.timestamp, record.timestamp,
                  input_tokens, output_tokens, total, cost))
            
            conn.commit()
        finally:
            conn.close()
        
        return record
    
    @contextmanager
    def track(self, operation: str, model: str, session_id: str = None, metadata: Dict = None):
        """Context manager for tracking token usage of an operation."""
        # This is a placeholder - actual token counting would need integration
        # with the LLM provider's response object
        start_time = datetime.now()
        yield TokenTrackerContext(self, operation, model, session_id, metadata)

class TokenTrackerContext:
    """Context for tracking tokens within an operation."""
    
    def __init__(self, tracker: TokenTracker, operation: str, model: str, 
                 session_id: str, metadata: Dict):
        self.tracker = tracker
        self.operation = operation
        self.model = model
        self.session_id = session_id
        self.metadata = metadata or {}
        self.start_time = datetime.now()
    
    def log(self, input_tokens: int, output_tokens: int):
        """Log the actual token counts."""
        self.tracker.log_usage(
            self.operation, self.model, input_tokens, output_tokens,
            self.session_id, self.metadata
        )
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass  # Actual logging should be done via .log() before exit

def estimate_tokens(text: str) -> int:
    """Rough token estimate from text."""
    return int(len(text.split()) / 0.75)

def log_chat(model: str, prompt: str, response: str, session_id: str = None, 
             operation: str = "chat", metadata: Dict = None):
    """Convenience function for logging chat interactions."""
    tracker = TokenTracker()
    input_tokens = estimate_tokens(prompt)
    output_tokens = estimate_tokens(response)
    return tracker.log_usage(operation, model, input_tokens, output_tokens, session_id, metadata)

def log_workflow(model: str, steps: List[Dict], session_id: str = None, 
                 metadata: Dict = None):
    """Log a multi-step workflow."""
    tracker = TokenTracker()
    total_input = sum(estimate_tokens(str(s.get("prompt", ""))) for s in steps)
    total_output = sum(estimate_tokens(str(s.get("response", ""))) for s in steps)
    return tracker.log_usage("workflow", model, total_input, total_output, session_id, metadata)

def get_session_summary(session_id: str = None) -> Dict[str, Any]:
    """Get summary for a session."""
    if session_id is None:
        session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    conn = sqlite3.connect(str(TOKEN_DB), timeout=5)
    conn.row_factory = sqlite3.Row
    try:
        row = conn.execute("SELECT * FROM session_summary WHERE session_id = ?", 
                          (session_id,)).fetchone()
        if row:
            return dict(row)
        return {"session_id": session_id, "message": "No data"}
    finally:
        conn.close()

def get_daily_usage(date: str = None) -> Dict[str, Any]:
    """Get daily usage summary."""
    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")
    
    conn = sqlite3.connect(str(TOKEN_DB), timeout=5)
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute("""
            SELECT model, operation, 
                   SUM(input_tokens) as total_input,
                   SUM(output_tokens) as total_output,
                   SUM(total_tokens) as total_tokens,
                   SUM(estimated_cost_usd) as total_cost,
                   COUNT(*) as operations
            FROM token_usage
            WHERE date(timestamp) = ?
            GROUP BY model, operation
        """, (date,)).fetchall()
        
        total_cost = sum(r["total_cost"] for r in rows)
        total_tokens = sum(r["total_tokens"] for r in rows)
        
        return {
            "date": date,
            "by_model_operation": [dict(r) for r in rows],
            "total_cost_usd": total_cost,
            "total_tokens": total_tokens,
            "total_operations": sum(r["operations"] for r in rows)
        }
    finally:
        conn.close()

def get_model_breakdown(days: int = 30) -> List[Dict]:
    """Get usage breakdown by model over last N days."""
    since = (datetime.now() - timedelta(days=days)).isoformat()
    
    conn = sqlite3.connect(str(TOKEN_DB), timeout=5)
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute("""
            SELECT model,
                   SUM(input_tokens) as total_input,
                   SUM(output_tokens) as total_output,
                   SUM(total_tokens) as total_tokens,
                   SUM(estimated_cost_usd) as total_cost,
                   COUNT(*) as operations
            FROM token_usage
            WHERE timestamp >= ?
            GROUP BY model
            ORDER BY total_cost DESC
        """, (since,)).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Token Tracker - Track LLM token usage and costs")
    parser.add_argument("--log", action="store_true", help="Log a chat interaction")
    parser.add_argument("--model", default="granite4.1:3b", help="Model name")
    parser.add_argument("--prompt", help="Prompt text")
    parser.add_argument("--response", help="Response text")
    parser.add_argument("--session", help="Session ID")
    parser.add_argument("--operation", default="chat", help="Operation type")
    parser.add_argument("--summary", help="Show session summary")
    parser.add_argument("--daily", help="Show daily usage (YYYY-MM-DD)")
    parser.add_argument("--models", type=int, default=30, help="Model breakdown (days)")
    parser.add_argument("--pricing", action="store_true", help="Show model pricing")
    args = parser.parse_args()
    
    if args.pricing:
        print("Model Pricing (per 1M tokens, USD):")
        for model, pricing in sorted(MODEL_PRICING.items()):
            print(f"  {model}: input=${pricing['input']:.2f}, output=${pricing['output']:.2f}")
        return
    
    if args.log and args.prompt and args.response:
        record = log_chat(args.model, args.prompt, args.response, args.session, args.operation)
        print(f"Logged: {record.total_tokens} tokens, ${record.estimated_cost_usd:.6f}")
        return
    
    if args.summary:
        summary = get_session_summary(args.summary)
        print(json.dumps(summary, indent=2, ensure_ascii=False))
        return
    
    if args.daily:
        usage = get_daily_usage(args.daily)
        print(json.dumps(usage, indent=2, ensure_ascii=False))
        return
    
    if args.models:
        breakdown = get_model_breakdown(args.models)
        print(json.dumps(breakdown, indent=2, ensure_ascii=False))
        return
    
    # Default: show current session
    summary = get_session_summary()
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
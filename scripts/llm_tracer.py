#!/usr/bin/env python3
"""
LLM Tracing — local JSONL + optional Langfuse cloud.

Logs every LLM call with timing, tokens, provider, model, and prompt snippet.
Stores locally in cache/llm_traces.jsonl.
Optionally sends to Langfuse if LANGFUSE_SECRET_KEY is set.
"""

import json
import os
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from contextlib import contextmanager
from typing import Optional, Any

HERMES_HOME = Path(__file__).resolve().parent.parent
TRACE_FILE = HERMES_HOME / "cache" / "llm_traces.jsonl"

# Load .env
def _load_env():
    env_path = HERMES_HOME / ".env"
    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())

_load_env()

# Langfuse client (lazy init)
_langfuse = None

def _get_langfuse():
    """Get or create Langfuse client. Returns None if not configured."""
    global _langfuse
    if _langfuse is not None:
        return _langfuse

    secret_key = os.environ.get("LANGFUSE_SECRET_KEY", "")
    public_key = os.environ.get("LANGFUSE_PUBLIC_KEY", "")
    host = os.environ.get("LANGFUSE_HOST", "https://cloud.langfuse.com")

    if not secret_key or not public_key:
        return None

    try:
        from langfuse import Langfuse
        _langfuse = Langfuse(
            secret_key=secret_key,
            public_key=public_key,
            host=host,
        )
        return _langfuse
    except Exception:
        return None


def _truncate(text: str, max_len: int = 200) -> str:
    """Truncate text for logging."""
    if not text:
        return ""
    return text[:max_len] + "..." if len(text) > max_len else text


def _count_tokens_approx(text: str) -> int:
    """Approximate token count (words * 1.3)."""
    return int(len(text.split()) * 1.3) if text else 0


@contextmanager
def trace_llm(provider: str, model: str, operation: str = "completion"):
    """
    Context manager for tracing LLM calls.

    Usage:
        with trace_llm("cerebras", "gemma-4-31b", "chat") as trace:
            result = call_llm(...)
            trace["tokens_out"] = 50
            trace["success"] = True
    """
    trace_id = str(uuid.uuid4())[:12]
    span_id = str(uuid.uuid4())[:8]
    start = time.time()

    trace_data = {
        "trace_id": trace_id,
        "span_id": span_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "provider": provider,
        "model": model,
        "operation": operation,
        "success": False,
        "duration_ms": 0,
        "tokens_in": 0,
        "tokens_out": 0,
        "prompt_preview": "",
        "response_preview": "",
        "error": None,
    }

    # Start Langfuse trace
    lf_trace = None
    lf_generation = None
    lf = _get_langfuse()
    if lf:
        try:
            lf_trace = lf.trace(
                id=trace_id,
                name=f"llm.{operation}",
                metadata={"provider": provider, "model": model},
            )
            lf_generation = lf_trace.generation(
                id=span_id,
                name=operation,
                model=model,
                model_parameters={"provider": provider},
            )
        except Exception:
            pass

    container = {"data": trace_data, "_lf_gen": lf_generation}

    try:
        yield container
        trace_data["success"] = True
    except Exception as e:
        trace_data["error"] = str(e)[:200]
        trace_data["success"] = False
        raise
    finally:
        elapsed = (time.time() - start) * 1000
        trace_data["duration_ms"] = round(elapsed, 1)

        # Finalize Langfuse generation
        if lf and lf_generation:
            try:
                lf_generation.end(
                    output=trace_data.get("response_preview", ""),
                    usage={
                        "input": trace_data["tokens_in"],
                        "output": trace_data["tokens_out"],
                    },
                    metadata={"duration_ms": trace_data["duration_ms"]},
                )
            except Exception:
                pass

        # Write to local JSONL
        _write_trace(trace_data)


def _write_trace(data: dict):
    """Append trace to local JSONL file."""
    TRACE_FILE.parent.mkdir(parents=True, exist_ok=True)
    try:
        with open(TRACE_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(data, ensure_ascii=False) + "\n")
    except Exception:
        pass


def get_recent_traces(n: int = 10) -> list:
    """Read last N traces from JSONL file."""
    if not TRACE_FILE.exists():
        return []
    lines = TRACE_FILE.read_text(encoding="utf-8").strip().split("\n")
    traces = []
    for line in lines[-n:]:
        line = line.strip()
        if line:
            try:
                traces.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    return traces


def get_trace_stats() -> dict:
    """Get aggregate stats from traces."""
    if not TRACE_FILE.exists():
        return {"total": 0, "ok": 0, "error": 0}

    lines = TRACE_FILE.read_text(encoding="utf-8").strip().split("\n")
    total = 0
    ok = 0
    errors = 0
    providers = {}
    total_ms = 0

    for line in lines:
        line = line.strip()
        if not line:
            continue
        try:
            t = json.loads(line)
            total += 1
            if t.get("success"):
                ok += 1
            else:
                errors += 1
            total_ms += t.get("duration_ms", 0)
            p = t.get("provider", "unknown")
            providers[p] = providers.get(p, 0) + 1
        except json.JSONDecodeError:
            pass

    return {
        "total": total,
        "ok": ok,
        "error": errors,
        "avg_ms": round(total_ms / max(total, 1), 1),
        "providers": providers,
    }


def flush():
    """Flush Langfuse queue."""
    lf = _get_langfuse()
    if lf:
        try:
            lf.flush()
        except Exception:
            pass


# CLI
if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--stats":
        print(json.dumps(get_trace_stats(), indent=2))

    elif len(sys.argv) > 1 and sys.argv[1] == "--recent":
        n = int(sys.argv[2]) if len(sys.argv) > 2 else 10
        traces = get_recent_traces(n)
        for t in traces:
            status = "OK" if t.get("success") else "FAIL"
            print(f"  [{t.get('provider', '?')}] {t.get('model', '?')} "
                  f"{t.get('duration_ms', 0)}ms {status} "
                  f"-> {(t.get('response_preview', '') or '')[:40]}")

    else:
        print("Usage:")
        print("  python llm_tracer.py --stats")
        print("  python llm_tracer.py --recent [N]")

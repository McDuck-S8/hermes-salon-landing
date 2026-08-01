#!/usr/bin/env python3
"""
Subagent Context Builder — Builds execution context for subagents.
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, List, Optional

HERMES_HOME = Path(os.environ.get("HERMES_HOME", "D:/Portable_Soft/hermes"))


def build_subagent_context(task_type: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
    """Build complete execution context for a subagent."""
    
    context = {
        "hermes_home": str(HERMES_HOME),
        "proxy": "socks5://127.0.0.1:10806",
        "env_vars": {
            "HERMES_HOME": str(HERMES_HOME),
            "HTTP_PROXY": "socks5://127.0.0.1:10806",
            "HTTPS_PROXY": "socks5://127.0.0.1:10806",
            "PLAYWRIGHT_BROWSERS_PATH": "ms-playwright",
            "PYTHONPATH": str(HERMES_HOME),
        },
        "tools": {
            "web_automation": "scripts/web_automation.py",
            "config_loader": "scripts/config_loader.py",
            "marketplace": ["ozon", "wb"],
            "content_sites": ["github", "gitlab", "youtube", "dzen", "vc_ru"],
        },
        "permissions": {
            "network": True,
            "browser": True,
            "file_read": True,
            "file_write": False,
            "subprocess": False,
        },
        "task": {
            "type": task_type,
            "params": params or {},
        },
        "instructions": build_instructions(task_type),
        "retry_policy": {
            "max_retries": 3,
            "backoff_base": 2,
            "retry_on": ["timeout", "proxy_error", "rate_limit", "browser_crash", "network_error"],
        },
        "output_format": {
            "success": "boolean",
            "data": "array|object|null",
            "error": "string|null",
            "metadata": {
                "subagent_id": "string",
                "duration_ms": "integer",
                "retries": "integer",
                "proxy_used": "string",
            }
        },
    }
    
    return context


def build_instructions(task_type: str) -> str:
    """Build task-specific instructions for subagent."""
    
    base_instructions = (
        "You are a subagent executing a delegated task. "
        "Always use the provided proxy (socks5://127.0.0.1:10806) for all network requests. "
        "Return results in the specified JSON format with success, data, error fields. "
        "Log all actions. Handle errors gracefully and retry on transient failures."
    )
    
    task_instructions = {
        "search_ozon": (
            base_instructions + 
            " Use web_automation.search_and_extract with site='ozon'. "
            "The method handles both HTTP API (preferred) and browser fallback with human-like behavior. "
            "Extract product title, price, rating, reviews count, and link. "
            "Sort by price ascending by default."
        ),
        "search_wb": (
            base_instructions + 
            " Use web_automation.search_and_extract with site='wb'. "
            "Extract product title, price, rating, reviews count, and link. "
            "Wildberries API returns price in kopeks - convert to rubles (divide by 100)."
        ),
        "get_product_details": (
            base_instructions + 
            " Use web_automation.get_product_details with the provided URL. "
            "Extract full product details: title, price, old price, rating, reviews, "
            "characteristics (specs, materials, sizes), availability, seller, brand, article, images."
        ),
        "search_github": (
            base_instructions + 
            " Use web_automation.execute_site_action with action='search_repos' or appropriate action. "
            "Find repositories matching the query."
        ),
    }
    
    return task_instructions.get(task_type, base_instructions)


def build_delegation_message(task_type: str, params: Dict[str, Any], subagent_id: str) -> str:
    """Build the full delegation message for a subagent."""
    
    context = build_subagent_context(task_type, params)
    context["subagent_id"] = subagent_id
    context["delegated_at"] = __import__("datetime").datetime.now().isoformat()
    
    return json.dumps(context, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Build subagent context")
    parser.add_argument("--task", required=True, help="Task type")
    parser.add_argument("--params", help="JSON params")
    parser.add_argument("--subagent-id", help="Subagent ID")
    
    args = parser.parse_args()
    
    params = json.loads(args.params) if args.params else {}
    subagent_id = args.subagent_id or "test"
    
    msg = build_delegation_message(args.task, params, subagent_id)
    print(msg)
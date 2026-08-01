#!/usr/bin/env python3
"""
Mem0 Integration for Hermes - Semantic Memory Backend
Works alongside KC (SQLite/FTS5) for semantic search.
"""
import os
import json
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

# Global Mem0 instance
_mem0_client = None
_mem0_initialized = False


def init_mem0(config: Optional[Dict] = None) -> bool:
    """
    Initialize Mem0 client with configuration.
    Uses OpenAI embeddings by default - requires OPENAI_API_KEY.
    """
    global _mem0_client, _mem0_initialized

    try:
        from mem0 import Memory
    except ImportError:
        logger.warning("mem0ai not installed. Run: pip install mem0ai")
        return False

    try:
        # Check for API key
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            logger.warning("OPENAI_API_KEY not set. Mem0 requires it for embeddings.")
            return False

        if config is None:
            config = {
                "llm": {
                    "provider": "openai",
                    "config": {
                        "model": "gpt-4o-mini",
                    }
                },
                "embedder": {
                    "provider": "openai",
                    "config": {
                        "model": "text-embedding-3-small",
                    }
                },
                "vector_store": {
                    "provider": "qdrant",
                    "config": {
                        "collection_name": "hermes_mem0",
                        "host": "localhost",
                        "port": 6333,
                    }
                }
            }

        _mem0_client = Memory.from_config(config)
        _mem0_initialized = True
        logger.info("Mem0 initialized successfully")
        return True

    except Exception as e:
        logger.error(f"Failed to initialize Mem0: {e}")
        _mem0_initialized = False
        return False


def mem0_add(content: str, user_id: str = "alexander", metadata: Optional[Dict] = None) -> Optional[str]:
    """Add a memory to Mem0."""
    if not _mem0_initialized or _mem0_client is None:
        logger.warning("Mem0 not initialized")
        return None

    try:
        mem_data = {
            "content": content,
            "user_id": user_id,
        }
        if metadata:
            mem_data["metadata"] = metadata

        result = _mem0_client.add(**mem_data)
        logger.info(f"Mem0 added: {content[:60]}...")
        return result.get("id") if isinstance(result, dict) else str(result)

    except Exception as e:
        logger.error(f"Mem0 add failed: {e}")
        return None


def mem0_search(query: str, user_id: str = "alexander", limit: int = 5) -> List[Dict[str, Any]]:
    """Search Mem0 for relevant memories."""
    if not _mem0_initialized or _mem0_client is None:
        logger.warning("Mem0 not initialized")
        return []

    try:
        results = _mem0_client.search(query, user_id=user_id, limit=limit)
        # Normalize results
        normalized = []
        for r in results:
            normalized.append({
                "memory": r.get("memory", r.get("text", "")),
                "score": r.get("score", 0.0),
                "metadata": r.get("metadata", {}),
                "id": r.get("id", ""),
            })
        return normalized

    except Exception as e:
        logger.error(f"Mem0 search failed: {e}")
        return []


def mem0_get_all(user_id: str = "alexander", limit: int = 100) -> List[Dict[str, Any]]:
    """Get all memories for a user."""
    if not _mem0_initialized or _mem0_client is None:
        return []

    try:
        results = _mem0_client.get_all(user_id=user_id, limit=limit)
        return [
            {
                "memory": r.get("memory", r.get("text", "")),
                "score": r.get("score", 0.0),
                "metadata": r.get("metadata", {}),
                "id": r.get("id", ""),
            }
            for r in results
        ]
    except Exception as e:
        logger.error(f"Mem0 get_all failed: {e}")
        return []


def mem0_delete(memory_id: str, user_id: str = "alexander") -> bool:
    """Delete a specific memory."""
    if not _mem0_initialized or _mem0_client is None:
        return False

    try:
        _mem0_client.delete(memory_id, user_id=user_id)
        return True
    except Exception as e:
        logger.error(f"Mem0 delete failed: {e}")
        return False


def is_mem0_available() -> bool:
    """Check if Mem0 is initialized and ready."""
    return _mem0_initialized and _mem0_client is not None


# Hybrid search function: combines KC (FTS5) + Mem0 (semantic)
def hybrid_search(query: str, kc_limit: int = 5, mem0_limit: int = 5, user_id: str = "alexander") -> Dict[str, Any]:
    """
    Search both KC (FTS5) and Mem0 (semantic) and combine results.
    Returns structured dict with both result sets.
    """
    from scripts.kc_rag import search as kc_search

    # KC search (FTS5 - keyword-based)
    kc_results = kc_search(query, limit=kc_limit)

    # Mem0 search (semantic)
    mem0_results = mem0_search(query, user_id=user_id, limit=mem0_limit)

    return {
        "query": query,
        "kc_results": kc_results,
        "mem0_results": mem0_results,
        "kc_count": len(kc_results),
        "mem0_count": len(mem0_results),
    }


if __name__ == "__main__":
    # Test
    logging.basicConfig(level=logging.INFO)

    if init_mem0():
        print("Mem0 initialized")

        # Add test memories
        mem0_add("User Alexander runs autonomous CPA/arbitrage on Windows 11 with Hermes agent")
        mem0_add("User prefers Telegram for CPA traffic and P2P USDT offramps via Bybit")
        mem0_add("DeepTutor: 2-layer plugin model (Tools/Capabilities), 3-layer memory (L1/L2/L3), MCP integration")

        # Search
        results = mem0_search("CPA traffic Telegram")
        print(f"Search results: {len(results)}")
        for r in results:
            print(f"  [{r['score']:.3f}] {r['memory'][:80]}...")

        # Hybrid search
        hybrid = hybrid_search("CPA traffic Telegram")
        print(f"\nHybrid: KC={hybrid['kc_count']}, Mem0={hybrid['mem0_count']}")
    else:
        print("Mem0 not available (needs OPENAI_API_KEY)")
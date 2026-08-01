#!/usr/bin/env python3
"""
agent_bus.py — Inter-agent message bus via Knowledge Cube + file-based queues.
"""
import os
import json
import time
import uuid
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime
from collections import defaultdict

# Add scripts to path
_SCRIPTS_DIR = Path(__file__).parent.parent.parent / "scripts"
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

# Lazy imports to avoid circular deps
get_hooks = None
on_task_complete = None
on_user_correction = None
recall_for_session = None

def _get_hooks_lazy():
    """Lazy import of get_hooks to avoid circular deps."""
    global get_hooks
    if get_hooks is None:
        from scripts.hermes_hooks import get_hooks as _get_hooks
        get_hooks = _get_hooks
    return get_hooks


@dataclass
class AgentMessage:
    """Message between agents."""
    id: str
    from_agent: str
    to_agent: str
    type: str              # "task", "result", "question", "status", "heartbeat"
    payload: Dict[str, Any]
    timestamp: str
    correlation_id: Optional[str] = None  # For request-response
    priority: int = 0       # Higher = more urgent


class AgentBus:
    """
    Message bus for agent communication.
    
    Backends:
    1. Knowledge Cube (via hermes_hooks) - durable, searchable
    2. File queues (per-agent) - fast, local
    3. Direct Hermes events - real-time
    """
    
    def __init__(self, bus_dir: Path = None):
        self.bus_dir = bus_dir or Path("D:/Portable_Soft/hermes/cache/agent_bus")
        self.bus_dir.mkdir(parents=True, exist_ok=True)
        self.queues: Dict[str, List[AgentMessage]] = defaultdict(list)
        self._load_queues()
    
    def _load_queues(self):
        """Load persisted queues from disk."""
        for queue_file in self.bus_dir.glob("queue_*.json"):
            try:
                agent = queue_file.stem.replace("queue_", "")
                data = json.loads(queue_file.read_text(encoding="utf-8"))
                self.queues[agent] = [AgentMessage(**m) for m in data]
            except Exception:
                pass
    
    def _save_queue(self, agent: str):
        """Persist queue to disk."""
        queue_file = self.bus_dir / f"queue_{agent}.json"
        data = [asdict(m) for m in self.queues[agent]]
        queue_file.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    
    def send(self, msg: AgentMessage) -> str:
        """Send message to agent's queue."""
        self.queues[msg.to_agent].append(msg)
        self._save_queue(msg.to_agent)
        
        # Also log to Knowledge Cube via hooks (lazy import)
        try:
            hooks = _get_hooks_lazy()
            hooks.on_task_complete(
                task_id=f"msg_{msg.id}",
                result=f"Message sent: {msg.from_agent} -> {msg.to_agent} [{msg.type}]",
                tags=["agent_bus", msg.type, msg.from_agent, msg.to_agent]
            )
        except Exception:
            pass
        
        return msg.id
    
    def receive(self, agent: str, limit: int = 10, types: List[str] = None) -> List[AgentMessage]:
        """Receive messages for agent (consumes them)."""
        queue = self.queues[agent]
        
        # Filter by type if specified
        if types:
            filtered = [m for m in queue if m.type in types]
        else:
            filtered = queue[:]
        
        # Sort by priority desc, timestamp asc
        filtered.sort(key=lambda m: (-m.priority, m.timestamp))
        
        # Take up to limit
        taken = filtered[:limit]
        
        # Remove taken from queue
        for msg in taken:
            queue.remove(msg)
        
        self._save_queue(agent)
        return taken
    
    def peek(self, agent: str, limit: int = 10) -> List[AgentMessage]:
        """Peek at messages without consuming."""
        queue = self.queues[agent]
        queue.sort(key=lambda m: (-m.priority, m.timestamp))
        return queue[:limit]
    
    def reply(self, original: AgentMessage, result: Dict, success: bool = True) -> str:
        """Send reply to original sender."""
        reply = AgentMessage(
            id=f"reply_{uuid.uuid4().hex[:8]}",
            from_agent=original.to_agent,
            to_agent=original.from_agent,
            type="result" if success else "error",
            payload={"correlation_id": original.correlation_id or original.id, 
                     "success": success, "result": result},
            timestamp=datetime.now().isoformat(),
            correlation_id=original.correlation_id or original.id,
        )
        return self.send(reply)
    
    def broadcast(self, from_agent: str, type: str, payload: Dict, 
                  targets: List[str] = None, priority: int = 0) -> List[str]:
        """Send same message to multiple agents."""
        targets = targets or list(self.queues.keys())
        ids = []
        for target in targets:
            if target != from_agent:
                msg = AgentMessage(
                    id=f"broadcast_{uuid.uuid4().hex[:8]}",
                    from_agent=from_agent,
                    to_agent=target,
                    type=type,
                    payload=payload,
                    timestamp=datetime.now().isoformat(),
                    priority=priority,
                )
                ids.append(self.send(msg))
        return ids
    
    def get_stats(self) -> Dict:
        """Get queue statistics."""
        return {
            agent: len(queue) 
            for agent, queue in self.queues.items()
        }


# Convenience functions
_bus: Optional[AgentBus] = None

def get_bus() -> AgentBus:
    """Get global bus instance."""
    global _bus
    if _bus is None:
        _bus = AgentBus()
    return _bus


def agent_send(to_agent: str, type: str, payload: Dict, 
               from_agent: str = "orchestrator", 
               correlation_id: str = None,
               priority: int = 0) -> str:
    """Send message to agent."""
    bus = get_bus()
    msg = AgentMessage(
        id=f"msg_{uuid.uuid4().hex[:8]}",
        from_agent=from_agent,
        to_agent=to_agent,
        type=type,
        payload=payload,
        timestamp=datetime.now().isoformat(),
        correlation_id=correlation_id,
        priority=priority,
    )
    return bus.send(msg)


def agent_receive(agent: str, limit: int = 10, types: List[str] = None) -> List[AgentMessage]:
    """Receive messages for agent."""
    bus = get_bus()
    return bus.receive(agent, limit, types)


def agent_peek(agent: str, limit: int = 10) -> List[AgentMessage]:
    """Peek at agent's queue."""
    bus = get_bus()
    return bus.peek(agent, limit)


def agent_reply(original: AgentMessage, result: Dict, success: bool = True) -> str:
    """Reply to a message."""
    bus = get_bus()
    return bus.reply(original, result, success)


def agent_broadcast(from_agent: str, type: str, payload: Dict,
                    targets: List[str] = None, priority: int = 0) -> List[str]:
    """Broadcast to multiple agents."""
    bus = get_bus()
    return bus.broadcast(from_agent, type, payload, targets, priority)


if __name__ == "__main__":
    # Quick test
    bus = AgentBus(Path("/tmp/test_agent_bus"))
    bus.bus_dir.mkdir(parents=True, exist_ok=True)
    
    # Send test messages
    for i in range(5):
        msg = AgentMessage(
            id=f"test_{i}",
            from_agent="orchestrator",
            to_agent="coder",
            type="task",
            payload={"task": f"Implement feature {i}"},
            timestamp=datetime.now().isoformat(),
            priority=5-i,
        )
        bus.send(msg)
    
    # Receive
    received = bus.receive("coder", limit=3)
    print(f"Received {len(received)} messages:")
    for m in received:
        print(f"  {m.id}: {m.payload}")
    
    # Stats
    print(f"Queue stats: {bus.get_stats()}")
    
    # Cleanup
    import shutil
    shutil.rmtree("/tmp/test_agent_bus")
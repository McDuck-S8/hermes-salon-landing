#!/usr/bin/env python3
"""
Handoff Manager — Context Transfer Between Agents
Implements: Handoff Patterns from Claude Code (seamless agent-to-agent context transfer)

Enables: agent A completes work → packages context → agent B continues seamlessly
"""

import os
import json
import uuid
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict, field
from datetime import datetime

HERMES_HOME = Path(os.environ.get("HERMES_HOME", "D:/Portable_Soft/hermes"))


@dataclass
class HandoffContext:
    """Complete context package for agent handoff"""
    handoff_id: str
    from_agent: str
    to_agent: str
    task: str
    completed_work: Dict[str, Any]
    artifacts: List[Dict]  # Files, outputs, decisions
    decisions: List[Dict]  # Key decisions made
    open_questions: List[str]
    next_actions: List[str]
    created_at: str
    metadata: Dict = field(default_factory=dict)


@dataclass
class AgentState:
    """Running state of an agent for handoff"""
    agent_name: str
    goal: str
    progress: float
    context: Dict
    active_tools: List[str]
    memory_refs: List[str]


class HandoffManager:
    """Manages agent-to-agent handoffs with full context preservation"""
    
    def __init__(self):
        self.handoff_dir = HERMES_HOME / "cache" / "handoffs"
        self.handoff_dir.mkdir(parents=True, exist_ok=True)
    
    def create_handoff(
        self,
        from_agent: str,
        to_agent: str,
        task: str,
        completed_work: Dict,
        artifacts: List[Dict] = None,
        decisions: List[Dict] = None,
        open_questions: List[str] = None,
        next_actions: List[str] = None,
        metadata: Dict = None
    ) -> HandoffContext:
        """Create a handoff context package"""
        handoff = HandoffContext(
            handoff_id=str(uuid.uuid4())[:8],
            from_agent=from_agent,
            to_agent=to_agent,
            task=task,
            completed_work=completed_work,
            artifacts=artifacts or [],
            decisions=decisions or [],
            open_questions=open_questions or [],
            next_actions=next_actions or [],
            created_at=datetime.now().isoformat(),
            metadata=metadata or {}
        )
        
        # Save handoff
        self._save_handoff(handoff)
        return handoff
    
    def _save_handoff(self, handoff: HandoffContext):
        """Persist handoff to cache"""
        file = self.handoff_dir / f"handoff_{handoff.handoff_id}.json"
        file.write_text(json.dumps(asdict(handoff), indent=2, ensure_ascii=False))
        
        # Also append to index
        index_file = self.handoff_dir / "index.jsonl"
        with open(index_file, "a", encoding="utf-8") as f:
            f.write(json.dumps({
                "handoff_id": handoff.handoff_id,
                "from": handoff.from_agent,
                "to": handoff.to_agent,
                "task": handoff.task[:100],
                "created": handoff.created_at
            }, ensure_ascii=False) + "\n")
    
    def load_handoff(self, handoff_id: str) -> Optional[HandoffContext]:
        """Load handoff context by ID"""
        file = self.handoff_dir / f"handoff_{handoff_id}.json"
        if not file.exists():
            return None
        data = json.loads(file.read_text())
        return HandoffContext(**data)
    
    def get_latest_handoff(self, to_agent: str = None) -> Optional[HandoffContext]:
        """Get most recent handoff, optionally for specific target agent"""
        index_file = self.handoff_dir / "index.jsonl"
        if not index_file.exists():
            return None
        
        handoffs = []
        with open(index_file, encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    handoffs.append(json.loads(line))
        
        if not handoffs:
            return None
        
        handoffs.sort(key=lambda x: x["created"], reverse=True)
        
        if to_agent:
            handoffs = [h for h in handoffs if h["to"] == to_agent]
            if not handoffs:
                return None
        
        return self.load_handoff(handoffs[0]["handoff_id"])
    
    def build_continuation_prompt(self, handoff: HandoffContext) -> str:
        """Build prompt for receiving agent to continue work"""
        return f"""=== HANDOFF FROM {handoff.from_agent} TO {handoff.to_agent} ===
Handoff ID: {handoff.handoff_id}
Original Task: {handoff.task}
Timestamp: {handoff.created_at}

COMPLETED WORK:
{json.dumps(handoff.completed_work, indent=2, ensure_ascii=False)}

ARTIFACTS PRODUCED:
{json.dumps(handoff.artifacts, indent=2, ensure_ascii=False)}

KEY DECISIONS:
{json.dumps(handoff.decisions, indent=2, ensure_ascii=False)}

OPEN QUESTIONS:
{json.dumps(handoff.open_questions, indent=2, ensure_ascii=False)}

NEXT ACTIONS REQUIRED:
{json.dumps(handoff.next_actions, indent=2, ensure_ascii=False)}

METADATA:
{json.dumps(handoff.metadata, indent=2, ensure_ascii=False)}

=== YOUR MISSION ===
Continue from where {handoff.from_agent} left off. Use the completed work as foundation.
Address open questions. Execute next actions. Produce final deliverable.

IMPORTANT: You have FULL context. Do not redo completed work. Build on it.
"""
    
    def execute_handoff(self, handoff: HandoffContext, executor_fn) -> Dict:
        """Execute handoff by calling executor function with handoff context"""
        prompt = self.build_continuation_prompt(handoff)
        
        # Call executor (could be subagent, LLM call, etc.)
        result = executor_fn(prompt, handoff)
        
        # Update handoff with results
        handoff.completed_work["handoff_result"] = result
        handoff.metadata["handoff_executed_at"] = datetime.now().isoformat()
        self._save_handoff(handoff)
        
        return result


# CLI
def main():
    import sys
    if len(sys.argv) < 2:
        print("Usage: python handoff_manager.py <command> [args]")
        print("Commands: list, show <id>, create <from> <to> <task>")
        sys.exit(1)
    
    mgr = HandoffManager()
    cmd = sys.argv[1]
    
    if cmd == "list":
        index_file = mgr.handoff_dir / "index.jsonl"
        if not index_file.exists():
            print("No handoffs yet")
            return
        with open(index_file, encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    h = json.loads(line)
                    print(f"{h['handoff_id']}: {h['from']} -> {h['to']} | {h['task'][:80]} | {h['created']}")
    
    elif cmd == "show":
        if len(sys.argv) < 3:
            print("Usage: handoff_manager.py show <handoff_id>")
            sys.exit(1)
        handoff = mgr.load_handoff(sys.argv[2])
        if handoff:
            print(json.dumps(asdict(handoff), indent=2, ensure_ascii=False))
        else:
            print("Handoff not found")
    
    elif cmd == "create":
        if len(sys.argv) < 5:
            print("Usage: handoff_manager.py create <from_agent> <to_agent> <task> [completed_work_json]")
            sys.exit(1)
        
        from_agent = sys.argv[2]
        to_agent = sys.argv[3]
        task = sys.argv[4]
        completed = json.loads(sys.argv[5]) if len(sys.argv) > 5 else {}
        
        handoff = mgr.create_handoff(from_agent, to_agent, task, completed)
        print(f"Created handoff: {handoff.handoff_id}")
        print(mgr.build_continuation_prompt(handoff))
    
    else:
        print(f"Unknown command: {cmd}")


if __name__ == "__main__":
    main()
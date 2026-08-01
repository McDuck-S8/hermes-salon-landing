#!/usr/bin/env python3
"""
Auto-Assign Router — Routes goals to agents based on classifier output.
Integrates with Telegram bridge, goal executor, and War Room.
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, Callable

HERMES_HOME = Path(os.environ.get("HERMES_HOME", "D:/Portable_Soft/hermes"))

# Agent directories
AGENTS_DIR = HERMES_HOME / "agents"

# Import classifier
sys.path.insert(0, str(HERMES_HOME / "skills" / "devops" / "auto-assign" / "scripts"))
try:
    from classifier import classify_goal
except ImportError:
    # Fallback if classifier not available
    def classify_goal(goal: str, context: str = "") -> Dict[str, Any]:
        return {"agent": "main", "confidence": 0.5, "reasoning": "Classifier unavailable"}

# Agent handlers - maps agent name to handler function
AGENT_HANDLERS: Dict[str, Callable] = {}

def register_handler(agent: str, handler: Callable):
    """Register a handler function for an agent."""
    AGENT_HANDLERS[agent] = handler


def route_goal(goal: str, context: str = "", metadata: Dict = None) -> Dict[str, Any]:
    """
    Route a goal to the appropriate agent.
    
    Returns:
        {
            "agent": "main|comms|content|ops|research",
            "confidence": 0.0-1.0,
            "reasoning": "...",
            "executed": True/False,
            "result": {...}  # if executed
        }
    """
    # Classify
    classification = classify_goal(goal, context)
    agent = classification["agent"]
    confidence = classification["confidence"]
    reasoning = classification["reasoning"]
    
    # Confidence threshold
    CONFIDENCE_THRESHOLD = float(os.environ.get("HERMES_AUTO_ASSIGN_THRESHOLD", "0.7"))
    
    if confidence < CONFIDENCE_THRESHOLD:
        # Low confidence - escalate to Main for review
        return {
            "agent": "main",
            "confidence": confidence,
            "reasoning": f"Low confidence ({confidence:.2f} < {CONFIDENCE_THRESHOLD}): {reasoning}. Escalated to Main.",
            "executed": False,
            "escalated": True
        }
    
    # Check if handler exists
    if agent not in AGENT_HANDLERS:
        return {
            "agent": agent,
            "confidence": confidence,
            "reasoning": f"{reasoning}. No handler registered for {agent}.",
            "executed": False,
            "error": f"No handler for agent: {agent}"
        }
    
    # Execute handler
    try:
        handler = AGENT_HANDLERS[agent]
        result = handler(goal, context, metadata or {})
        
        return {
            "agent": agent,
            "confidence": confidence,
            "reasoning": reasoning,
            "executed": True,
            "result": result
        }
    except Exception as e:
        logging.error(f"Agent {handler} execution failed: {e}")
        return {
            "agent": agent,
            "confidence": confidence,
            "reasoning": reasoning,
            "executed": False,
            "error": str(e)
        }


def get_agent_capabilities() -> Dict[str, Any]:
    """Return agent capability matrix for external use."""
    from classifier import AGENT_CAPABILITIES
    return AGENT_CAPABILITIES


# Default handlers (can be overridden by importing modules)
def _default_main_handler(goal: str, context: str, metadata: Dict) -> Dict:
    return {"status": "queued", "message": f"Main handler received: {goal[:100]}"}


def _default_comms_handler(goal: str, context: str, metadata: Dict) -> Dict:
    return {"status": "queued", "message": f"Comms handler received: {goal[:100]}"}


def _default_content_handler(goal: str, context: str, metadata: Dict) -> Dict:
    return {"status": "queued", "message": f"Content handler received: {goal[:100]}"}


def _default_ops_handler(goal: str, context: str, metadata: Dict) -> Dict:
    return {"status": "queued", "message": f"Ops handler received: {goal[:100]}"}


def _default_research_handler(goal: str, context: str, metadata: Dict) -> Dict:
    return {"status": "queued", "message": f"Research handler received: {goal[:100]}"}


# Register default handlers
register_handler("main", _default_main_handler)
register_handler("comms", _default_comms_handler)
register_handler("content", _default_content_handler)
register_handler("ops", _default_ops_handler)
register_handler("research", _default_research_handler)


def integrate_telegram_bridge():
    """Integration point for Telegram bridge - call this from telegram_bridge.py"""
    def telegram_handler(goal: str, context: str, metadata: Dict) -> Dict:
        # Import telegram_bridge send function
        try:
            sys.path.insert(0, str(HERMES_HOME / "scripts"))
            from telegram_bridge import send_telegram_message
            
            chat_id = metadata.get("chat_id")
            token = metadata.get("token")
            
            result = send_telegram_message(text=goal, chat_id=chat_id, token=token)
            return {"status": "sent" if result else "failed"}
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    register_handler("comms", telegram_handler)


def integrate_goal_executor():
    """Integration point for goal executor - call this from goal_executor.py"""
    def goal_handler(goal: str, context: str, metadata: Dict) -> Dict:
        # This would spawn the actual agent process
        agent = metadata.get("assigned_agent", "main")
        return {"status": "spawned", "agent": agent, "goal": goal}
    
    # Goal executor uses router to decide, then spawns
    return route_goal


def integrate_war_room():
    """Integration point for War Room - auto-assign agents to discuss topics"""
    def war_room_handler(goal: str, context: str, metadata: Dict) -> Dict:
        # War Room would use this to pick which agents to include
        return {"status": "assigned", "agents": metadata.get("agents", [])}
    
    register_handler("main", war_room_handler)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Auto-Assign Router")
    parser.add_argument("--goal", required=True, help="Goal to route")
    parser.add_argument("--context", default="", help="Context")
    parser.add_argument("--metadata", default="{}", help="JSON metadata")
    args = parser.parse_args()
    
    metadata = json.loads(args.metadata)
    result = route_goal(args.goal, args.context, metadata)
    print(json.dumps(result, indent=2))
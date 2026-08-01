"""
herdr-multiagent — Multi-agent orchestration via Herdr.

Windows analog of ego-lite for multi-agent workflows.
"""
from .scripts.herdr_multiagent import HerdrMultiAgent, AgentRole
from .scripts.agent_bus import AgentBus, AgentMessage, agent_send, agent_receive, agent_peek, agent_reply, agent_broadcast, get_bus
from .scripts.space_manager import HerdrSpaceManager, HerdrSpace, HerdrPane
from .scripts.task_templates import TaskTemplateManager, TaskTemplate
from .scripts.cli import main as cli_main

__all__ = [
    "HerdrMultiAgent",
    "AgentRole",
    "AgentBus",
    "AgentMessage",
    "agent_send",
    "agent_receive",
    "agent_peek",
    "agent_reply",
    "agent_broadcast",
    "get_bus",
    "HerdrSpaceManager",
    "HerdrSpace",
    "HerdrPane",
    "TaskTemplateManager",
    "TaskTemplate",
    "cli_main",
]

__version__ = "1.0.0"
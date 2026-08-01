"""
Crimea Security Framework v2
Legal penetration testing framework for Crimea/Russia

Based on:
- T3MP3ST (elder-plinius/T3MP3ST) - OPSEC, RoE, Evidence Vault, Mission Control
- HexStrike AI (0x4m4/hexstrike-ai) - MCP architecture, 150+ tools, 12 agents

License: AGPL-3.0
"""

__version__ = "2.0.0"
__author__ = "Crimea Security Framework Team"
__license__ = "AGPL-3.0"

# Main exports
from .core import (
    Phase,
    OperatorArchetype,
    OperatorStatus,
    FindingSeverity,
    MissionStatus,
    ScopeReceipt,
    Target,
    Finding,
    Evidence,
    Operator,
    Task,
    RoE,
    OPSECProfile,
    Mission,
    ConfigLoader,
    EventEmitter,
)

from .mission import MissionControl, create_mission_from_scope
from .opsec import OPSECController, PayloadEncoder, UserAgentRotator, ProxyManager
from .arsenal import Arsenal, create_arsenal
from .kb import KnowledgeBase, create_kb

__all__ = [
    # Core types
    "Phase",
    "OperatorArchetype",
    "OperatorStatus",
    "FindingSeverity",
    "MissionStatus",
    "ScopeReceipt",
    "Target",
    "Finding",
    "Evidence",
    "Operator",
    "Task",
    "RoE",
    "OPSECProfile",
    "Mission",
    "ConfigLoader",
    "EventEmitter",
    # Mission
    "MissionControl",
    "create_mission_from_scope",
    # OPSEC
    "OPSECController",
    "PayloadEncoder",
    "UserAgentRotator",
    "ProxyManager",
    # Arsenal
    "Arsenal",
    "create_arsenal",
    # KB
    "KnowledgeBase",
    "create_kb",
]
"""
Crystal v3 — Персональный Development Advisor
24 модуля, 8 отделов
"""

# Revisit: when Crystal exports, public API, or module registration changes. Last touched: 2026-07-02.

from .core import CrystalEngine
from .models import Signal, Pattern, Need, Proposal, Assessment
from .executor import ProposalExecutor
from .conversation_analyzer import ConversationAnalyzer

__version__ = "3.2.0"
__all__ = ["CrystalEngine", "Signal", "Pattern", "Need", "Proposal", "Assessment", "ProposalExecutor", "ConversationAnalyzer"]

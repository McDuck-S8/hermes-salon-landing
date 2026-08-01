"""
Approval system for Hermes tools — human-in-the-loop with three levels.

Follows eve pattern: always / once / never / policy-based approval.
Integrates with existing output_validator for blocking dangerous operations.

Usage:
    @approval.always()   # Ask every time
    @approval.once()     # Ask once per session
    @approval.never()    # Never ask (default for safe tools)
    @approval.policy(fn) # Custom policy function

Decorators are fail-safe: if approval check fails, operation is denied.
"""

from enum import Enum
from typing import Callable, Optional, Dict, Any, List
from dataclasses import dataclass, field
from pathlib import Path
import json
import time
import logging


logger = logging.getLogger("hermes.approval")


class ApprovalLevel(Enum):
    NEVER = "never"      # No approval needed
    ONCE = "once"        # Ask once per session
    ALWAYS = "always"    # Ask every time
    POLICY = "policy"    # Custom policy function


@dataclass
class ApprovalPolicy:
    """Policy for when to require approval."""
    level: ApprovalLevel = ApprovalLevel.NEVER
    # For POLICY level: function(input, context) -> bool (True = needs approval)
    policy_fn: Optional[Callable[[Dict, Dict], bool]] = None
    # Human-readable reason shown to user
    reason: str = ""
    # Risk tags for categorization
    risk_tags: List[str] = field(default_factory=list)


@dataclass
class ApprovalRecord:
    """Record of an approval decision."""
    tool_name: str
    input_data: Dict[str, Any]
    decision: str  # "approved" | "denied" | "pending"
    timestamp: float
    session_id: str
    approver: str = "human"  # or "auto" for auto-approved


# Global approval state
_approval_policies: Dict[str, ApprovalPolicy] = {}
_approval_cache: Dict[str, bool] = {}  # tool_name -> approved (for ONCE)
_approval_history: List[ApprovalRecord] = []
_current_session_id: str = ""


def set_session_id(session_id: str) -> None:
    """Set the current session ID for approval tracking."""
    global _current_session_id
    _current_session_id = session_id


def register_approval(
    tool_name: str,
    level: ApprovalLevel = ApprovalLevel.NEVER,
    policy_fn: Optional[Callable[[Dict, Dict], bool]] = None,
    reason: str = "",
    risk_tags: Optional[List[str]] = None,
) -> None:
    """Register an approval policy for a tool."""
    _approval_policies[tool_name] = ApprovalPolicy(
        level=level,
        policy_fn=policy_fn,
        reason=reason,
        risk_tags=risk_tags or [],
    )
    logger.info(f"Registered approval for {tool_name}: {level.value}")


def always() -> ApprovalPolicy:
    """Helper: always require approval."""
    return ApprovalPolicy(level=ApprovalLevel.ALWAYS)


def once() -> ApprovalPolicy:
    """Helper: require approval once per session."""
    return ApprovalPolicy(level=ApprovalLevel.ONCE)


def never() -> ApprovalPolicy:
    """Helper: never require approval (default)."""
    return ApprovalPolicy(level=ApprovalLevel.NEVER)


def policy(fn: Callable[[Dict, Dict], bool], reason: str = "") -> ApprovalPolicy:
    """Helper: custom policy function."""
    return ApprovalPolicy(level=ApprovalLevel.POLICY, policy_fn=fn, reason=reason)


def check_approval_needed(tool_name: str, input_data: Dict[str, Any], context: Dict[str, Any]) -> bool:
    """Check if approval is needed for this tool call."""
    policy = _approval_policies.get(tool_name)
    if not policy:
        return False
    
    if policy.level == ApprovalLevel.NEVER:
        return False
    
    if policy.level == ApprovalLevel.ALWAYS:
        return True
    
    if policy.level == ApprovalLevel.ONCE:
        cache_key = f"{_current_session_id}:{tool_name}"
        if cache_key in _approval_cache:
            return False  # Already approved this session
        return True
    
    if policy.level == ApprovalLevel.POLICY and policy.policy_fn:
        return policy.policy_fn(input_data, context)
    
    return False


def request_approval(
    tool_name: str,
    input_data: Dict[str, Any],
    context: Dict[str, Any],
    reason: str = "",
) -> bool:
    """
    Request human approval for a tool call.
    Returns True if approved, False if denied.
    In non-interactive mode, returns False (fail-safe).
    """
    policy = _approval_policies.get(tool_name, ApprovalPolicy(level=ApprovalLevel.NEVER))
    
    # Build approval prompt
    prompt = _build_approval_prompt(tool_name, input_data, policy, reason)
    
    # In CLI context, we'd use a proper prompt
    # For now, log and return False (fail-safe)
    logger.warning(f"APPROVAL REQUIRED: {tool_name}")
    logger.warning(f"Input: {input_data}")
    logger.warning(f"Reason: {policy.reason or reason}")
    
    # Try to get approval from context if provided (e.g., from Telegram callback)
    approval = context.get("_approval_decision")
    if approval is not None:
        decision = bool(approval)
    else:
        # Non-interactive: deny by default
        decision = False
    
    # Record the decision
    record = ApprovalRecord(
        tool_name=tool_name,
        input_data=input_data,
        decision="approved" if decision else "denied",
        timestamp=time.time(),
        session_id=_current_session_id,
    )
    _approval_history.append(record)
    
    # Cache for ONCE policy
    if policy.level == ApprovalLevel.ONCE and decision:
        cache_key = f"{_current_session_id}:{tool_name}"
        _approval_cache[cache_key] = True
    
    return decision


def _build_approval_prompt(
    tool_name: str,
    input_data: Dict[str, Any],
    policy: ApprovalPolicy,
    reason: str,
) -> str:
    """Build human-readable approval prompt."""
    lines = [
        f"⚠️  Approval Required: {tool_name}",
        f"",
        f"Reason: {policy.reason or reason or 'High-risk operation'}",
        f"",
        f"Input:",
    ]
    for k, v in input_data.items():
        val = str(v)
        if len(val) > 200:
            val = val[:200] + "..."
        lines.append(f"  {k}: {val}")
    
    if policy.risk_tags:
        lines.append(f"")
        lines.append(f"Risk tags: {', '.join(policy.risk_tags)}")
    
    lines.append(f"")
    lines.append(f"Approve? [y/N]")
    
    return "\n".join(lines)


def get_approval_history(
    tool_name: Optional[str] = None,
    session_id: Optional[str] = None,
) -> List[ApprovalRecord]:
    """Get approval history, optionally filtered."""
    results = _approval_history
    if tool_name:
        results = [r for r in results if r.tool_name == tool_name]
    if session_id:
        results = [r for r in results if r.session_id == session_id]
    return results


def save_approval_log(path: Path) -> None:
    """Save approval history to JSON file."""
    data = [
        {
            "tool_name": r.tool_name,
            "input_data": r.input_data,
            "decision": r.decision,
            "timestamp": r.timestamp,
            "session_id": r.session_id,
            "approver": r.approver,
        }
        for r in _approval_history
    ]
    path.write_text(json.dumps(data, indent=2))


def load_approval_log(path: Path) -> None:
    """Load approval history from JSON file."""
    global _approval_history
    if path.exists():
        data = json.loads(path.read_text())
        _approval_history = [
            ApprovalRecord(**d) for d in data
        ]


# ============================================================================
# Built-in risk-based policies
# ============================================================================

def financial_risk_policy(input_data: Dict, context: Dict) -> bool:
    """Require approval for financial operations above threshold."""
    amount = input_data.get("amount", 0)
    if isinstance(amount, (int, float)) and amount > 100:  # $100 threshold
        return True
    return False


def data_destruction_policy(input_data: Dict, context: Dict) -> bool:
    """Require approval for destructive data operations."""
    destructive_ops = ["delete", "drop", "truncate", "remove", "purge", "wipe"]
    operation = str(input_data.get("operation", "")).lower()
    return any(op in operation for op in destructive_ops)


def external_write_policy(input_data: Dict, context: Dict) -> bool:
    """Require approval for writes to external systems."""
    target = str(input_data.get("target", "")).lower()
    external_targets = ["production", "prod", "live", "customer", "user"]
    return any(t in target for t in external_targets)


# ============================================================================
# Decorator for easy tool registration
# ============================================================================

def with_approval(
    level: ApprovalLevel = ApprovalLevel.NEVER,
    policy_fn: Optional[Callable] = None,
    reason: str = "",
    risk_tags: Optional[List[str]] = None,
):
    """
    Decorator to add approval to a tool function.
    
    Usage:
        @with_approval(always(), reason="Sends real money")
        async def send_payment(amount: float, to: str):
            ...
    """
    def decorator(func):
        tool_name = func.__name__
        register_approval(tool_name, level, policy_fn, reason, risk_tags)
        
        async def wrapper(*args, **kwargs):
            # Build input dict from args/kwargs
            import inspect
            sig = inspect.signature(func)
            bound = sig.bind(*args, **kwargs)
            bound.apply_defaults()
            input_data = dict(bound.arguments)
            
            # Check approval
            context = kwargs.get("_context", {})
            if check_approval_needed(tool_name, input_data, context):
                approved = request_approval(tool_name, input_data, context, reason)
                if not approved:
                    raise PermissionError(f"Approval denied for {tool_name}")
            
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator


# ============================================================================
# Integration with output_validator
# ============================================================================

def validate_and_approve(
    tool_name: str,
    input_data: Dict[str, Any],
    output_data: Any,
    context: Dict[str, Any],
) -> tuple[bool, str]:
    """
    Combined validation + approval check.
    Returns (allowed, reason_if_blocked).
    """
    # 1. Check output_validator first (existing blocking logic)
    try:
        from output_validator import validate_tool_output
        if not validate_tool_output(tool_name, output_data):
            return False, "Output validation failed"
    except ImportError:
        pass
    
    # 2. Check approval
    if check_approval_needed(tool_name, input_data, context):
        if not request_approval(tool_name, input_data, context):
            return False, "Approval denied"
    
    return True, ""


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Demo
    register_approval(
        "send_payment",
        ApprovalLevel.ALWAYS,
        reason="Sends real money",
        risk_tags=["financial", "external"],
    )
    
    register_approval(
        "delete_database",
        ApprovalLevel.ALWAYS,
        reason="Destructive operation",
        risk_tags=["destructive", "data-loss"],
    )
    
    register_approval(
        "deploy_prod",
        ApprovalLevel.ONCE,
        reason="Production deployment",
        risk_tags=["production", "external"],
    )
    
    # Test
    context = {"_session_id": "test-123"}
    set_session_id("test-123")
    
    print("Check send_payment (ALWAYS):", check_approval_needed("send_payment", {"amount": 50}, context))
    print("Check deploy_prod (ONCE, first time):", check_approval_needed("deploy_prod", {}, context))
    print("Check deploy_prod (ONCE, second time):", check_approval_needed("deploy_prod", {}, context))
    print("Check unknown tool (NEVER):", check_approval_needed("unknown_tool", {}, context))
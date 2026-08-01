#!/usr/bin/env python3
"""
HITL Gates (Human-in-the-Loop) — approval system for irreversible actions.
Prevents autonomous execution of high-risk operations without user confirmation.

Usage:
    from scripts.hitl_gates import require_approval, HITLAction
    
    if require_approval(HITLAction.WITHDRAWAL_CONFIRM, details):
        execute_withdrawal()
    else:
        log("Waiting for user approval...")
"""

import json
import os
from datetime import datetime
from pathlib import Path
from enum import Enum
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict

HERMES_HOME = Path(__file__).resolve().parent.parent
CACHE_DIR = HERMES_HOME / "cache"
HITL_FILE = CACHE_DIR / "hitl_pending.json"

class HITLAction(Enum):
    """Actions requiring human approval."""
    WITHDRAWAL_CONFIRM = "withdrawal_confirm"      # Confirm money received on card
    CPA_REGISTRATION = "cpa_registration"          # Register new CPA network account
    TAX_PAYMENT = "tax_payment"                    # Pay taxes via "Мой налог"
    SCHEME_KILL = "scheme_kill"                    # Kill arbitrage scheme (irreversible)
    SCALE_BUDGET = "scale_budget"                  # Increase traffic budget significantly
    NEW_SCHEME_DEPLOY = "new_scheme_deploy"        # Deploy new untested scheme

@dataclass
class HITLRequest:
    id: str
    action: str
    details: Dict[str, Any]
    timestamp: str
    status: str = "pending"  # pending, approved, rejected, expired
    expires_at: Optional[str] = None
    response: Optional[Dict] = None

def init_hitl_file():
    """Initialize HITL pending file."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    if not HITL_FILE.exists():
        HITL_FILE.write_text("[]", encoding="utf-8")

def load_pending() -> list:
    """Load pending HITL requests."""
    init_hitl_file()
    try:
        return json.loads(HITL_FILE.read_text(encoding="utf-8"))
    except Exception:
        return []

def save_pending(pending: list):
    """Save pending HITL requests."""
    HITL_FILE.write_text(json.dumps(pending, indent=2, ensure_ascii=False), encoding="utf-8")

def create_request(action: HITLAction, details: Dict[str, Any], ttl_hours: int = 24) -> HITLRequest:
    """Create a new HITL approval request."""
    from uuid import uuid4
    request = HITLRequest(
        id=uuid4().hex[:12],
        action=action.value,
        details=details,
        timestamp=datetime.now().isoformat(),
        expires_at=(datetime.now().replace(microsecond=0)).isoformat()  # placeholder
    )
    # Add TTL
    from datetime import timedelta
    expires = datetime.now() + timedelta(hours=ttl_hours)
    request.expires_at = expires.isoformat()
    return request

def require_approval(action: HITLAction, details: Dict[str, Any], ttl_hours: int = 24) -> bool:
    """
    Check if action needs approval and create request if needed.
    Returns True if already approved, False if pending/rejected.
    """
    pending = load_pending()
    
    # Check for existing request for same action+details
    for req in pending:
        if (req["action"] == action.value and 
            req["status"] == "approved" and
            req.get("details", {}) == details):
            return True  # Already approved
    
    # Check for pending request
    for req in pending:
        if (req["action"] == action.value and 
            req["status"] == "pending" and
            req.get("details", {}) == details):
            # Check expiry
            if req.get("expires_at"):
                try:
                    expires = datetime.fromisoformat(req["expires_at"])
                    if datetime.now() < expires:
                        return False  # Still pending
                    else:
                        req["status"] = "expired"  # Expire it
                except Exception:
                    pass
    
    # Create new request
    request = create_request(action, details, ttl_hours)
    pending.append(asdict(request))
    save_pending(pending)
    
    print(f"\n[HITL] APPROVAL REQUIRED")
    print(f"Action: {action.value}")
    print(f"Details: {json.dumps(details, indent=2, ensure_ascii=False)}")
    print(f"Request ID: {request.id}")
    print(f"Expires: {request.expires_at}")
    print(f"To approve: python scripts/hitl_gates.py approve {request.id}")
    print(f"To reject:  python scripts/hitl_gates.py reject {request.id}\n")
    
    return False

def approve_request(request_id: str, response: Optional[Dict] = None) -> bool:
    """Approve a pending HITL request."""
    pending = load_pending()
    for req in pending:
        if req["id"] == request_id and req["status"] == "pending":
            req["status"] = "approved"
            req["response"] = response or {"approved_at": datetime.now().isoformat()}
            save_pending(pending)
            print(f"[OK] Request {request_id} approved")
    else:
        print(f"[FAIL] Request {request_id} not found or not pending")
    return False

def reject_request(request_id: str, reason: str = "") -> bool:
    """Reject a pending HITL request."""
    pending = load_pending()
    for req in pending:
        if req["id"] == request_id and req["status"] == "pending":
            req["status"] = "rejected"
            req["response"] = {"rejected_at": datetime.now().isoformat(), "reason": reason}
            save_pending(pending)
            print(f"[FAIL] Request {request_id} rejected: {reason}")
    else:
        print(f"[FAIL] Request {request_id} not found or not pending")
    return False

def get_pending_requests() -> list:
    """Get all pending requests."""
    pending = load_pending()
    return [r for r in pending if r["status"] == "pending"]

def cleanup_expired():
    """Mark expired requests."""
    pending = load_pending()
    changed = False
    for req in pending:
        if req["status"] == "pending" and req.get("expires_at"):
            try:
                expires = datetime.fromisoformat(req["expires_at"])
                if datetime.now() > expires:
                    req["status"] = "expired"
                    changed = True
            except Exception:
                pass
    if changed:
        save_pending(pending)

# CLI
if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python hitl_gates.py [list|approve|reject] [request_id]")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == "list":
        cleanup_expired()
        pending = get_pending_requests()
        if not pending:
            print("No pending requests")
        else:
            for req in pending:
                print(f"  {req['id']}: {req['action']} (expires {req.get('expires_at', '?')})")
                print(f"    Details: {json.dumps(req['details'], ensure_ascii=False)}")
    
    elif cmd == "approve" and len(sys.argv) > 2:
        approve_request(sys.argv[2])
    
    elif cmd == "reject" and len(sys.argv) > 2:
        reason = sys.argv[3] if len(sys.argv) > 3 else ""
        reject_request(sys.argv[2], reason)
    
    else:
        print("Usage: python hitl_gates.py [list|approve|reject] [request_id] [reason]")
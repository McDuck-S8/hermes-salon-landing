#!/usr/bin/env python3
"""
Crimea Security Framework v2 — Core Module
Based on: T3MP3ST architecture + HexStrike AI patterns
License: AGPL-3.0
"""

from __future__ import annotations
import asyncio
import yaml
import json
import logging
import uuid
import hashlib
import time
from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Callable, Awaitable
from datetime import datetime, timedelta
from abc import ABC, abstractmethod
import os
import sys

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

logger = logging.getLogger(__name__)


class Phase(str, Enum):
    """Cyber Kill Chain phases (T3MP3ST aligned)"""
    RECONNAISSANCE = "reconnaissance"
    WEAPONIZATION = "weaponization"
    DELIVERY = "delivery"
    EXPLOITATION = "exploitation"
    INSTALLATION = "installation"
    COMMAND_AND_CONTROL = "command_and_control"
    ACTIONS_ON_OBJECTIVES = "actions_on_objectives"
    # Extended phases
    SCANNING = "scanning"
    ENUMERATION = "enumeration"
    VULNERABILITY_ASSESSMENT = "vulnerability_assessment"
    ANALYSIS = "analysis"
    REPORTING = "reporting"
    PROOF_OF_CONCEPT = "proof_of_concept"
    POST_EXPLOITATION = "post_exploitation"
    PRIVILEGE_ESCALATION = "privilege_escalation"
    LATERAL_MOVEMENT = "lateral_movement"
    PERSISTENCE = "persistence"
    EXFILTRATION = "exfiltration"
    DENIAL_OF_SERVICE = "denial_of_service"


class OperatorArchetype(str, Enum):
    """T3MP3ST operator archetypes"""
    RECON = "recon"
    SCANNER = "scanner"
    EXPLOITER = "exploiter"
    INFILTRATOR = "infiltrator"
    EXFILTRATOR = "exfiltrator"
    GHOST = "ghost"
    COORDINATOR = "coordinator"
    ANALYST = "analyst"


class OperatorStatus(str, Enum):
    IDLE = "idle"
    TASKED = "tasked"
    EXECUTING = "executing"
    COOLDOWN = "cooldown"
    BURNED = "burned"


class FindingSeverity(str, Enum):
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class MissionStatus(str, Enum):
    CREATED = "created"
    ROE_VALIDATED = "roe_validated"
    SCOPE_VERIFIED = "scope_verified"
    RUNNING = "running"
    PAUSED = "paused"
    PHASE_COMPLETE = "phase_complete"
    COMPLETED = "completed"
    ABORTED = "aborted"
    FAILED = "failed"


class DetectionRiskLevel(str, Enum):
    MINIMAL = "minimal"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class ScopeReceipt:
    """Scope Receipt — подписанный заказчиком документ об авторизации"""
    receipt_id: str
    customer_legal_entity: str
    customer_authorized_representative: str
    target_systems: List[str]
    ip_ranges: List[str]
    domains: List[str]
    excluded_paths: List[str]
    testing_window_start: datetime
    testing_window_end: datetime
    emergency_contact: str
    authorized_signature: str
    signature_date: datetime
    roe_template_id: str
    validity_days: int = 90
    metadata: Dict[str, Any] = field(default_factory=dict)

    def is_valid(self) -> bool:
        now = datetime.now()
        return self.testing_window_start <= now <= self.testing_window_end

    def is_expired(self) -> bool:
        return datetime.now() > self.testing_window_end

    def to_dict(self) -> Dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict) -> "ScopeReceipt":
        # Convert datetime strings
        for field_name in ["testing_window_start", "testing_window_end", "signature_date"]:
            if isinstance(data.get(field_name), str):
                data[field_name] = datetime.fromisoformat(data[field_name])
        return cls(**data)


@dataclass
class Target:
    """Target environment model"""
    target_id: str
    mission_id: str
    identifier: str  # URL, IP, CIDR, hostname
    target_type: str  # webapp, network, api, mobile, iot, cloud
    status: str = "discovered"  # discovered, scanning, vulnerable, exploited, owned
    services: List[Dict] = field(default_factory=list)
    vulnerabilities: List[str] = field(default_factory=list)  # finding IDs
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict:
        d = asdict(self)
        d["created_at"] = self.created_at.isoformat()
        d["updated_at"] = self.updated_at.isoformat()
        return d


@dataclass
class Finding:
    """Security finding / vulnerability"""
    finding_id: str
    mission_id: str
    phase: Phase
    operator: OperatorArchetype
    target: str
    vulnerability: Dict[str, Any]  # cve, cwe, title, cvss, mitre
    evidence: Dict[str, Any]  # request, response, screenshot, curl
    severity: FindingSeverity
    status: str = "verified"  # verified, false_positive, duplicate, remediated
    cvss31_score: Optional[float] = None
    cvss31_vector: Optional[str] = None
    mitre_techniques: List[str] = field(default_factory=list)
    remediation: str = ""
    references: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict:
        d = asdict(self)
        d["phase"] = self.phase.value
        d["operator"] = self.operator.value
        d["severity"] = self.severity.value
        d["created_at"] = self.created_at.isoformat()
        d["updated_at"] = self.updated_at.isoformat()
        return d


@dataclass
class Evidence:
    """Evidence artifact"""
    evidence_id: str
    finding_id: str
    mission_id: str
    evidence_type: str  # screenshot, curl, request, response, pcap, har, log
    content: bytes
    content_hash: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    chain_of_custody: List[Dict] = field(default_factory=list)

    def to_dict(self) -> Dict:
        d = asdict(self)
        d["content_hash"] = self.content_hash
        d["created_at"] = self.created_at.isoformat()
        return d


@dataclass
class Operator:
    """Operator agent (T3MP3ST style)"""
    operator_id: str
    archetype: OperatorArchetype
    mission_id: str
    status: OperatorStatus = OperatorStatus.IDLE
    current_task_id: Optional[str] = None
    detection_risk: float = 0.0
    max_detection_risk: float = 0.5
    capabilities: List[str] = field(default_factory=list)
    assigned_targets: List[str] = field(default_factory=list)
    completed_tasks: int = 0
    burned: bool = False
    created_at: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)

    def can_accept_task(self) -> bool:
        return (
            self.status == OperatorStatus.IDLE
            and not self.burned
            and self.detection_risk < self.max_detection_risk
        )

    def to_dict(self) -> Dict:
        d = asdict(self)
        d["archetype"] = self.archetype.value
        d["status"] = self.status.value
        d["created_at"] = self.created_at.isoformat()
        d["last_activity"] = self.last_activity.isoformat()
        return d


@dataclass
class Task:
    """Mission task"""
    task_id: str
    mission_id: str
    phase: Phase
    operator_archetype: OperatorArchetype
    target: str
    description: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    status: str = "pending"  # pending, assigned, executing, completed, failed
    assigned_operator_id: Optional[str] = None
    result: Optional[Dict] = None
    error: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    def to_dict(self) -> Dict:
        d = asdict(self)
        d["phase"] = self.phase.value
        d["operator_archetype"] = self.operator_archetype.value
        d["created_at"] = self.created_at.isoformat()
        if self.started_at:
            d["started_at"] = self.started_at.isoformat()
        if self.completed_at:
            d["completed_at"] = self.completed_at.isoformat()
        return d


@dataclass
class RoE:
    """Rules of Engagement configuration"""
    template_id: str
    name: str
    version: str
    allowed_phases: List[Phase]
    forbidden_phases: List[Phase]
    tool_gates: Dict[str, Dict]
    evidence_requirements: Dict[str, Any]
    data_handling: Dict[str, Any]
    kill_switch: Dict[str, Any]
    compliance: Dict[str, Any] = field(default_factory=dict)

    def is_phase_allowed(self, phase: Phase) -> bool:
        return phase in self.allowed_phases and phase not in self.forbidden_phases

    def is_tool_allowed(self, tool: str) -> bool:
        if tool not in self.tool_gates:
            return False
        return self.tool_gates[tool].get("allowed", False)

    def get_tool_config(self, tool: str) -> Dict:
        return self.tool_gates.get(tool, {})


@dataclass
class OPSECProfile:
    """OPSEC profile configuration"""
    profile_id: str
    name: str
    detection_risk_threshold: float
    cooldown_multiplier: float
    rate_limit: Dict[str, Any]
    tool_restrictions: Dict[str, List[str]]
    evasion: Dict[str, Any]
    payload_encoding: Dict[str, Any]
    waf_bypass: Dict[str, Any]
    logging: Dict[str, Any]
    kill_switch: Dict[str, Any]

    def is_tool_allowed(self, category: str) -> bool:
        allowed = self.tool_restrictions.get("allowed_categories", [])
        forbidden = self.tool_restrictions.get("forbidden_categories", [])
        return category in allowed and category not in forbidden


@dataclass
class Mission:
    """Mission — container for entire engagement"""
    mission_id: str
    name: str
    description: str
    scope_receipt: ScopeReceipt
    roe: RoE
    opsec_profile: OPSECProfile
    status: MissionStatus = MissionStatus.CREATED
    current_phase: Optional[Phase] = None
    phases_completed: List[Phase] = field(default_factory=list)
    targets: Dict[str, Target] = field(default_factory=dict)
    operators: Dict[str, Operator] = field(default_factory=dict)
    tasks: Dict[str, Task] = field(default_factory=dict)
    findings: Dict[str, Finding] = field(default_factory=dict)
    evidence: Dict[str, Evidence] = field(default_factory=dict)
    detection_risk: float = 0.0
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_target(self, target: Target) -> None:
        self.targets[target.target_id] = target

    def add_finding(self, finding: Finding) -> None:
        self.findings[finding.finding_id] = finding

    def add_evidence(self, evidence: Evidence) -> None:
        self.evidence[evidence.evidence_id] = evidence

    def get_findings_by_severity(self, severity: FindingSeverity) -> List[Finding]:
        return [f for f in self.findings.values() if f.severity == severity]

    def get_findings_by_target(self, target_id: str) -> List[Finding]:
        return [f for f in self.findings.values() if f.target == target_id]

    def to_dict(self) -> Dict:
        d = asdict(self)
        d["status"] = self.status.value
        d["current_phase"] = self.current_phase.value if self.current_phase else None
        d["phases_completed"] = [p.value for p in self.phases_completed]
        d["scope_receipt"] = self.scope_receipt.to_dict()
        d["created_at"] = self.created_at.isoformat()
        if self.started_at:
            d["started_at"] = self.started_at.isoformat()
        if self.completed_at:
            d["completed_at"] = self.completed_at.isoformat()
        return d


# === Configuration Loader ===

class ConfigLoader:
    """Loads all configuration files"""

    def __init__(self, config_dir: Path = None):
        self.config_dir = config_dir or (PROJECT_ROOT / "config")
        self._cache: Dict[str, Any] = {}

    def load_yaml(self, filename: str) -> Dict:
        path = self.config_dir / filename
        if not path.exists():
            raise FileNotFoundError(f"Config not found: {path}")
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    def load_default_config(self) -> Dict:
        if "default" not in self._cache:
            self._cache["default"] = self.load_yaml("default.yaml")
        return self._cache["default"]

    def load_opsec_profiles(self) -> Dict:
        if "opsec" not in self._cache:
            self._cache["opsec"] = self.load_yaml("opsec-profiles.yaml")
        return self._cache["opsec"]

    def load_roe_templates(self) -> Dict:
        if "roe" not in self._cache:
            self._cache["roe"] = self.load_yaml("roe-templates.yaml")
        return self._cache["roe"]

    def load_crimea_targets(self) -> Dict:
        if "targets" not in self._cache:
            self._cache["targets"] = self.load_yaml("crimea-targets.yaml")
        return self._cache["targets"]

    def get_opsec_profile(self, profile_id: str) -> OPSECProfile:
        data = self.load_opsec_profiles()
        for p in data.get("profiles", []):
            if p["id"] == profile_id:
                return OPSECProfile(**p)
        raise ValueError(f"OPSEC profile not found: {profile_id}")

    def get_roe_template(self, template_id: str) -> RoE:
        data = self.load_roe_templates()
        for t in data.get("templates", []):
            if t["id"] == template_id:
                # Convert phases
                allowed = [Phase(p) for p in t.get("allowed_phases", [])]
                forbidden = [Phase(p) for p in t.get("forbidden_phases", [])]
                return RoE(
                    template_id=t["id"],
                    name=t["name"],
                    version=t["version"],
                    allowed_phases=allowed,
                    forbidden_phases=forbidden,
                    tool_gates=t.get("tool_gates", {}),
                    evidence_requirements=t.get("evidence_requirements", {}),
                    data_handling=t.get("data_handling", {}),
                    kill_switch=t.get("kill_switch", {}),
                    compliance=t.get("compliance", {})
                )
        raise ValueError(f"RoE template not found: {template_id}")

    def get_scope_by_id(self, scope_id: str) -> Dict:
        data = self.load_crimea_targets()
        for s in data.get("scopes", []):
            if s["id"] == scope_id:
                return s
        raise ValueError(f"Scope not found: {scope_id}")

    def get_authorized_scopes(self) -> List[Dict]:
        data = self.load_crimea_targets()
        return [s for s in data.get("scopes", []) if s.get("authorized", False)]


# === Event System (T3MP3ST style) ===

class EventEmitter:
    """Simple event emitter for mission events"""

    def __init__(self):
        self._listeners: Dict[str, List[Callable]] = {}

    def on(self, event: str, callback: Callable) -> None:
        if event not in self._listeners:
            self._listeners[event] = []
        self._listeners[event].append(callback)

    def off(self, event: str, callback: Callable) -> None:
        if event in self._listeners:
            self._listeners[event].remove(callback)

    async def emit(self, event: str, *args, **kwargs) -> None:
        if event in self._listeners:
            for callback in self._listeners[event]:
                if asyncio.iscoroutinefunction(callback):
                    await callback(*args, **kwargs)
                else:
                    callback(*args, **kwargs)

    def emit_sync(self, event: str, *args, **kwargs) -> None:
        if event in self._listeners:
            for callback in self._listeners[event]:
                if not asyncio.iscoroutinefunction(callback):
                    callback(*args, **kwargs)


# Mission Events
MISSION_STARTED = "mission:started"
MISSION_PAUSED = "mission:paused"
MISSION_RESUMED = "mission:resumed"
MISSION_COMPLETED = "mission:completed"
MISSION_ABORTED = "mission:aborted"
PHASE_CHANGED = "mission:phase_changed"
TASK_ASSIGNED = "task:assigned"
TASK_STARTED = "task:started"
TASK_COMPLETED = "task:completed"
TASK_FAILED = "task:failed"
FINDING_DISCOVERED = "finding:discovered"
EVIDENCE_COLLECTED = "evidence:collected"
TARGET_DISCOVERED = "target:discovered"
TARGET_OWNED = "target:owned"
OPERATOR_SPAWNED = "operator:spawned"
OPERATOR_BURNED = "operator:burned"
DETECTION_TRIGGERED = "detection:triggered"
KILL_SWITCH_ACTIVATED = "kill_switch:activated"
ROE_VIOLATION = "roe:violation"
SCOPE_VIOLATION = "scope:violation"


# === Utility Functions ===

def generate_id(prefix: str = "") -> str:
    """Generate unique ID"""
    return f"{prefix}{uuid.uuid4().hex[:12]}"


def hash_content(content: bytes) -> str:
    """SHA256 hash of content"""
    return hashlib.sha256(content).hexdigest()


def calculate_cvss31(vector: str) -> float:
    """Calculate CVSS 3.1 score from vector string (simplified)"""
    # This is a placeholder - real implementation would use cvsslib
    return 0.0


def validate_scope(target: str, scope_receipt: ScopeReceipt) -> bool:
    """Check if target is within scope"""
    # Check domains
    for domain in scope_receipt.domains:
        if target.endswith(domain) or target == domain:
            return True
    # Check IPs/CIDRs
    for cidr in scope_receipt.ip_ranges:
        # Simplified - real impl would use ipaddress module
        if target in cidr or cidr in target:
            return True
    # Check excluded paths
    for excluded in scope_receipt.excluded_paths:
        if excluded in target:
            return False
    return False


def sanitize_pii(text: str, patterns: List[str] = None) -> str:
    """Basic PII sanitization"""
    import re
    default_patterns = {
        "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
        "phone_ru": r"(\+7|8)[\s\-]?\(?\d{3}\)?[\s\-]?\d{3}[\s\-]?\d{2}[\s\-]?\d{2}",
        "passport_ru": r"\b\d{4}\s?\d{6}\b",
        "inn_ru": r"\b\d{10,12}\b",
        "snils_ru": r"\b\d{3}-\d{3}-\d{3}\s\d{2}\b",
        "credit_card": r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b",
        "ipv4": r"\b(?:\d{1,3}\.){3}\d{1,3}\b",
        "jwt": r"eyJ[A-Za-z0-9_-]+\.eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+",
    }
    patterns_to_use = {k: v for k, v in default_patterns.items() if not patterns or k in patterns}
    result = text
    for name, pattern in patterns_to_use.items():
        result = re.sub(pattern, f"[REDACTED_{name.upper()}]", result)
    return result


# Export all
__all__ = [
    "Phase",
    "OperatorArchetype",
    "OperatorStatus",
    "FindingSeverity",
    "MissionStatus",
    "DetectionRiskLevel",
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
    "MISSION_STARTED",
    "MISSION_PAUSED",
    "MISSION_RESUMED",
    "MISSION_COMPLETED",
    "MISSION_ABORTED",
    "PHASE_CHANGED",
    "TASK_ASSIGNED",
    "TASK_STARTED",
    "TASK_COMPLETED",
    "TASK_FAILED",
    "FINDING_DISCOVERED",
    "EVIDENCE_COLLECTED",
    "TARGET_DISCOVERED",
    "TARGET_OWNED",
    "OPERATOR_SPAWNED",
    "OPERATOR_BURNED",
    "DETECTION_TRIGGERED",
    "KILL_SWITCH_ACTIVATED",
    "ROE_VIOLATION",
    "SCOPE_VIOLATION",
    "generate_id",
    "hash_content",
    "calculate_cvss31",
    "validate_scope",
    "sanitize_pii",
]
#!/usr/bin/env python3
"""
Mission Control — Orchestrates the entire security engagement
Based on T3MP3ST MissionControl with Crimea-specific adaptations
"""

from __future__ import annotations
import asyncio
import logging
from typing import Dict, List, Optional, Any, Callable, Awaitable
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, field

from src.core import (
    Phase, OperatorArchetype, OperatorStatus, FindingSeverity,
    MissionStatus, ScopeReceipt, Target, Finding, Evidence, Operator, Task,
    RoE, OPSECProfile, Mission, ConfigLoader, EventEmitter,
    generate_id, hash_content, validate_scope, sanitize_pii,
    MISSION_STARTED, MISSION_PAUSED, MISSION_RESUMED, MISSION_COMPLETED,
    MISSION_ABORTED, PHASE_CHANGED, TASK_ASSIGNED, TASK_STARTED,
    TASK_COMPLETED, TASK_FAILED, FINDING_DISCOVERED, EVIDENCE_COLLECTED,
    TARGET_DISCOVERED, TARGET_OWNED, OPERATOR_SPAWNED, OPERATOR_BURNED,
    DETECTION_TRIGGERED, KILL_SWITCH_ACTIVATED, ROE_VIOLATION, SCOPE_VIOLATION
)

logger = logging.getLogger(__name__)


class TaskQueue:
    """Task queue with priority and phase ordering"""

    def __init__(self):
        self._queues: Dict[Phase, List[Task]] = {p: [] for p in Phase}
        self._all_tasks: Dict[str, Task] = {}
        self._lock = asyncio.Lock()

    async def add_task(self, task: Task) -> None:
        async with self._lock:
            self._queues[task.phase].append(task)
            self._all_tasks[task.task_id] = task

    async def get_next_task(self, phase: Phase, operator_archetype: OperatorArchetype) -> Optional[Task]:
        async with self._lock:
            queue = self._queues[phase]
            for i, task in enumerate(queue):
                if task.operator_archetype == operator_archetype and task.status == "pending":
                    task.status = "assigned"
                    return queue.pop(i)
            return None

    async def get_task(self, task_id: str) -> Optional[Task]:
        async with self._lock:
            return self._all_tasks.get(task_id)

    async def update_task(self, task: Task) -> None:
        async with self._lock:
            self._all_tasks[task.task_id] = task

    async def get_pending_count(self, phase: Phase) -> int:
        async with self._lock:
            return len([t for t in self._queues[phase] if t.status == "pending"])

    async def get_all_tasks(self) -> List[Task]:
        async with self._lock:
            return list(self._all_tasks.values())


class OperatorCell:
    """Manages pool of operators (T3MP3ST style)"""

    def __init__(self, mission: Mission, roe: RoE, opsec: OPSECProfile, event_bus: EventEmitter):
        self.mission = mission
        self.roe = roe
        self.opsec = opsec
        self.event_bus = event_bus
        self._operators: Dict[str, Operator] = {}
        self._lock = asyncio.Lock()

    async def spawn_operator(self, archetype: OperatorArchetype, max_risk: float = 0.5) -> Operator:
        """Spawn a new operator of given archetype"""
        async with self._lock:
            operator_id = generate_id(f"op-{archetype.value}-")
            operator = Operator(
                operator_id=operator_id,
                archetype=archetype,
                mission_id=self.mission.mission_id,
                max_detection_risk=max_risk,
                capabilities=self._get_capabilities(archetype)
            )
            self._operators[operator_id] = operator
            self.mission.operators[operator_id] = operator
            await self.event_bus.emit(OPERATOR_SPAWNED, operator)
            logger.info(f"Spawned operator: {operator_id} ({archetype.value})")
            return operator

    def _get_capabilities(self, archetype: OperatorArchetype) -> List[str]:
        """Get capabilities for archetype"""
        caps = {
            OperatorArchetype.RECON: [
                "dns_enum", "subdomain_enum", "cert_transparency", "whois",
                "shodan", "censys", "wayback", "google_dorks", "osint"
            ],
            OperatorArchetype.SCANNER: [
                "port_scan", "service_fingerprint", "vuln_scan", "nuclei",
                "nikto", "wp_scan", "ssl_scan", "tech_detect"
            ],
            OperatorArchetype.EXPLOITER: [
                "exploit_dev", "payload_delivery", "initial_access",
                "sqlmap", "msfconsole", "custom_exploits"
            ],
            OperatorArchetype.INFILTRATOR: [
                "privilege_escalation", "lateral_movement", "credential_access",
                "psexec", "wmi", "ssh", "rdp", "kerberos"
            ],
            OperatorArchetype.EXFILTRATOR: [
                "data_collection", "staging", "exfiltration", "compression",
                "encryption", "dns_exfil", "http_exfil"
            ],
            OperatorArchetype.GHOST: [
                "persistence", "evasion", "cleanup", "anti_forensics",
                "rootkit", "bootkit", "firmware"
            ],
            OperatorArchetype.COORDINATOR: [
                "task_management", "decision_making", "intelligence_sync",
                "phase_transition", "resource_allocation"
            ],
            OperatorArchetype.ANALYST: [
                "finding_analysis", "cvss_scoring", "mitre_mapping",
                "report_generation", "remediation_planning", "risk_assessment"
            ],
        }
        return caps.get(archetype, [])

    async def get_available_operator(self, archetype: OperatorArchetype) -> Optional[Operator]:
        async with self._lock:
            for op in self._operators.values():
                if op.archetype == archetype and op.can_accept_task():
                    return op
            return None

    async def assign_task(self, operator_id: str, task: Task) -> bool:
        async with self._lock:
            operator = self._operators.get(operator_id)
            if not operator or not operator.can_accept_task():
                return False
            operator.status = OperatorStatus.TASKED
            operator.current_task_id = task.task_id
            task.assigned_operator_id = operator_id
            task.status = "assigned"
            task.started_at = datetime.now()
            return True

    async def complete_task(self, operator_id: str, result: Dict) -> bool:
        async with self._lock:
            operator = self._operators.get(operator_id)
            if not operator or operator.current_task_id is None:
                return False
            operator.status = OperatorStatus.COOLDOWN
            operator.completed_tasks += 1
            operator.current_task_id = None
            operator.last_activity = datetime.now()
            # Cooldown will be managed by mission tick
            return True

    async def burn_operator(self, operator_id: str, reason: str) -> None:
        async with self._lock:
            operator = self._operators.get(operator_id)
            if operator:
                operator.burned = True
                operator.status = OperatorStatus.BURNED
                await self.event_bus.emit(OPERATOR_BURNED, operator, reason)

    async def get_operators(self, archetype: OperatorArchetype = None) -> List[Operator]:
        async with self._lock:
            ops = list(self._operators.values())
            if archetype:
                ops = [o for o in ops if o.archetype == archetype]
            return ops


class MissionControl:
    """
    Central mission orchestrator.
    Manages phases, tasks, operators, targets, findings, evidence.
    """

    def __init__(self, config_dir: Path = None):
        self.config = ConfigLoader(config_dir)
        self.event_bus = EventEmitter()
        self.missions: Dict[str, Mission] = {}
        self._running_missions: Dict[str, asyncio.Task] = {}
        self._tick_interval = 1  # seconds
        self._shutdown = False

    async def create_mission(
        self,
        name: str,
        description: str,
        scope_receipt: ScopeReceipt,
        roe_template_id: str = "strict",
        opsec_profile_id: str = "balanced"
    ) -> Mission:
        """Create a new mission with validation"""

        # Load RoE template
        roe = self.config.get_roe_template(roe_template_id)

        # Load OPSEC profile
        opsec = self.config.get_opsec_profile(opsec_profile_id)

        # Validate scope receipt
        if not scope_receipt.is_valid():
            raise ValueError("Scope receipt is not valid (expired or not yet active)")

        # Create mission
        mission_id = generate_id("M-")
        mission = Mission(
            mission_id=mission_id,
            name=name,
            description=description,
            scope_receipt=scope_receipt,
            roe=roe,
            opsec_profile=opsec,
            status=MissionStatus.CREATED
        )

        # Store mission
        self.missions[mission_id] = mission

        # Initialize operators based on RoE
        await self._initialize_operators(mission)

        logger.info(f"Created mission: {mission_id} ({name})")
        return mission

    async def _initialize_operators(self, mission: Mission) -> None:
        """Initialize operator cell based on allowed phases"""
        cell = OperatorCell(mission, mission.roe, mission.opsec_profile, self.event_bus)

        # Always spawn RECON and SCANNER
        await cell.spawn_operator(OperatorArchetype.RECON, max_risk=0.2)
        await cell.spawn_operator(OperatorArchetype.SCANNER, max_risk=0.4)

        # Always spawn ANALYST
        await cell.spawn_operator(OperatorArchetype.ANALYST, max_risk=0.1)

        # Spawn experimental operators only if phases allowed
        if mission.roe.is_phase_allowed(Phase.EXPLOITATION):
            await cell.spawn_operator(OperatorArchetype.EXPLOITER, max_risk=0.7)

        if mission.roe.is_phase_allowed(Phase.POST_EXPLOITATION):
            await cell.spawn_operator(OperatorArchetype.INFILTRATOR, max_risk=0.7)

        # COORDINATOR for complex missions
        if len(mission.roe.allowed_phases) > 4:
            await cell.spawn_operator(OperatorArchetype.COORDINATOR, max_risk=0.3)

    async def start_mission(self, mission_id: str) -> None:
        """Start mission execution"""
        mission = self.missions.get(mission_id)
        if not mission:
            raise ValueError(f"Mission not found: {mission_id}")

        if mission.status != MissionStatus.CREATED:
            raise ValueError(f"Mission cannot be started from status: {mission.status}")

        # Validate RoE and Scope
        await self._validate_mission(mission)

        # Set up phases
        mission.current_phase = Phase.RECONNAISSANCE
        mission.status = MissionStatus.RUNNING
        mission.started_at = datetime.now()

        # Create initial tasks for first phase
        await self._create_phase_tasks(mission, Phase.RECONNAISSANCE)

        # Start mission loop
        task = asyncio.create_task(self._mission_loop(mission))
        self._running_missions[mission_id] = task

        await self.event_bus.emit(MISSION_STARTED, mission)
        logger.info(f"Mission started: {mission_id}")

    async def _validate_mission(self, mission: Mission) -> None:
        """Validate mission prerequisites"""
        mission.status = MissionStatus.ROE_VALIDATED
        # Check scope receipt
        if not mission.scope_receipt.is_valid():
            raise ValueError("Scope receipt expired or not yet valid")

        # Check targets are in scope
        # (will be validated when targets are added)

        mission.status = MissionStatus.SCOPE_VERIFIED
        await self.event_bus.emit("mission:validated", mission)

    async def _create_phase_tasks(self, mission: Mission, phase: Phase) -> None:
        """Create tasks for a phase based on targets and operator capabilities"""
        # Get targets for this phase
        targets = list(mission.targets.values())
        if not targets:
            # No targets yet - create discovery task
            task = Task(
                task_id=generate_id("task-"),
                mission_id=mission.mission_id,
                phase=phase,
                operator_archetype=OperatorArchetype.RECON,
                target="scope",
                description=f"Discover targets within scope: {mission.scope_receipt.domains}",
                parameters={"scope_receipt": mission.scope_receipt.to_dict()}
            )
            mission.tasks[task.task_id] = task
            return

        # Create tasks based on phase
        task_configs = self._get_phase_tasks(phase)
        for target in targets:
            for config in task_configs:
                if mission.roe.is_phase_allowed(phase):
                    task = Task(
                        task_id=generate_id("task-"),
                        mission_id=mission.mission_id,
                        phase=phase,
                        operator_archetype=config["archetype"],
                        target=target.target_id,
                        description=config["description"].format(target=target.identifier),
                        parameters=config.get("parameters", {})
                    )
                    mission.tasks[task.task_id] = task

    def _get_phase_tasks(self, phase: Phase) -> List[Dict]:
        """Get task configurations for a phase"""
        tasks = {
            Phase.RECONNAISSANCE: [
                {"archetype": OperatorArchetype.RECON, "description": "Passive DNS enumeration for {target}", "parameters": {"tool": "subdomain_enum"}},
                {"archetype": OperatorArchetype.RECON, "description": "Certificate transparency logs for {target}", "parameters": {"tool": "cert_transparency"}},
                {"archetype": OperatorArchetype.RECON, "description": "WHOIS and registration info for {target}", "parameters": {"tool": "whois_lookup"}},
                {"archetype": OperatorArchetype.RECON, "description": "Technology fingerprinting for {target}", "parameters": {"tool": "technology_detect"}},
            ],
            Phase.SCANNING: [
                {"archetype": OperatorArchetype.SCANNER, "description": "Port scan for {target}", "parameters": {"tool": "port_scan", "ports": "top-1000"}},
                {"archetype": OperatorArchetype.SCANNER, "description": "Service version detection for {target}", "parameters": {"tool": "service_fingerprint"}},
                {"archetype": OperatorArchetype.SCANNER, "description": "Vulnerability scan for {target}", "parameters": {"tool": "nuclei_scan", "severity": "high,critical"}},
                {"archetype": OperatorArchetype.SCANNER, "description": "SSL/TLS configuration scan for {target}", "parameters": {"tool": "ssl_scan"}},
            ],
            Phase.ENUMERATION: [
                {"archetype": OperatorArchetype.SCANNER, "description": "Directory enumeration for {target}", "parameters": {"tool": "dir_bruteforce", "wordlist": "raft-medium"}},
                {"archetype": OperatorArchetype.SCANNER, "description": "API endpoint discovery for {target}", "parameters": {"tool": "api_discovery"}},
            ],
            Phase.VULNERABILITY_ASSESSMENT: [
                {"archetype": OperatorArchetype.SCANNER, "description": "XSS scan for {target}", "parameters": {"tool": "xss_scan"}},
                {"archetype": OperatorArchetype.SCANNER, "description": "SQL injection scan for {target}", "parameters": {"tool": "sqli_scan"}},
                {"archetype": OperatorArchetype.SCANNER, "description": "SSRF scan for {target}", "parameters": {"tool": "ssrf_scan"}},
            ],
            Phase.EXPLOITATION: [
                {"archetype": OperatorArchetype.EXPLOITER, "description": "Exploit verified vulnerabilities for {target}", "parameters": {"tool": "exploit_dev"}},
            ],
            Phase.ANALYSIS: [
                {"archetype": OperatorArchetype.ANALYST, "description": "Analyze findings for {target}", "parameters": {}},
                {"archetype": OperatorArchetype.ANALYST, "description": "CVSS scoring and MITRE mapping for {target}", "parameters": {}},
            ],
            Phase.REPORTING: [
                {"archetype": OperatorArchetype.ANALYST, "description": "Generate final report for mission", "parameters": {"format": "html,pdf,json"}},
            ],
        }
        return tasks.get(phase, [])

    async def _mission_loop(self, mission: Mission) -> None:
        """Main mission execution loop (T3MP3ST tick-based)"""
        try:
            while mission.status == MissionStatus.RUNNING and not self._shutdown:
                await self._tick(mission)
                await asyncio.sleep(self._tick_interval)

                # Check for phase completion
                if await self._is_phase_complete(mission):
                    await self._advance_phase(mission)

                # Check kill switch
                if await self._check_kill_switch(mission):
                    await self.abort_mission(mission.mission_id, "Kill switch activated")
                    break

        except asyncio.CancelledError:
            logger.info(f"Mission loop cancelled: {mission.mission_id}")
        except Exception as e:
            logger.error(f"Mission loop error: {mission.mission_id}: {e}")
            mission.status = MissionStatus.FAILED
            await self.event_bus.emit(MISSION_ABORTED, mission, str(e))

    async def _tick(self, mission: Mission) -> None:
        """Single tick - process tasks, update operators"""
        # Get operator cell
        cell = OperatorCell(mission, mission.roe, mission.opsec_profile, self.event_bus)

        # Assign pending tasks to available operators
        for task in mission.tasks.values():
            if task.status == "pending":
                operator = await cell.get_available_operator(task.operator_archetype)
                if operator:
                    await cell.assign_task(operator.operator_id, task)
                    await self.event_bus.emit(TASK_ASSIGNED, task, operator)
                    await self._execute_task(mission, task, operator)

        # Update operator cooldowns
        await self._update_operator_cooldowns(mission)

    async def _execute_task(self, mission: Mission, task: Task, operator: Operator) -> None:
        """Execute a task (simulated - real impl would call tools)"""
        task.status = "executing"
        operator.status = OperatorStatus.EXECUTING
        await self.event_bus.emit(TASK_STARTED, task, operator)

        try:
            # Simulate task execution
            await asyncio.sleep(0.1)  # Placeholder for real tool execution

            # Simulate result
            result = {
                "status": "completed",
                "output": f"Task {task.task_id} completed for {task.target}",
                "findings": [],
                "evidence": []
            }

            task.status = "completed"
            task.result = result
            task.completed_at = datetime.now()

            await cell.complete_task(operator.operator_id, result)
            await self.event_bus.emit(TASK_COMPLETED, task, operator)

        except Exception as e:
            task.status = "failed"
            task.error = str(e)
            task.completed_at = datetime.now()
            operator.status = OperatorStatus.IDLE
            await self.event_bus.emit(TASK_FAILED, task, operator, e)

    async def _update_operator_cooldowns(self, mission: Mission) -> None:
        """Update operator cooldowns based on OPSEC profile"""
        cooldown = mission.opsec_profile.cooldown_multiplier
        for operator in mission.operators.values():
            if operator.status == OperatorStatus.COOLDOWN:
                # Simple cooldown - in real impl would track time
                operator.status = OperatorStatus.IDLE

    async def _is_phase_complete(self, mission: Mission) -> bool:
        """Check if current phase tasks are complete"""
        phase_tasks = [t for t in mission.tasks.values() if t.phase == mission.current_phase]
        if not phase_tasks:
            return True
        return all(t.status in ["completed", "failed"] for t in phase_tasks)

    async def _advance_phase(self, mission: Mission) -> None:
        """Advance to next phase"""
        phases_order = [
            Phase.RECONNAISSANCE,
            Phase.SCANNING,
            Phase.ENUMERATION,
            Phase.VULNERABILITY_ASSESSMENT,
            Phase.EXPLOITATION,
            Phase.POST_EXPLOITATION,
            Phase.ANALYSIS,
            Phase.REPORTING,
        ]

        current_idx = phases_order.index(mission.current_phase) if mission.current_phase in phases_order else -1

        # Find next allowed phase
        for next_phase in phases_order[current_idx + 1:]:
            if mission.roe.is_phase_allowed(next_phase):
                mission.phases_completed.append(mission.current_phase)
                mission.current_phase = next_phase
                await self._create_phase_tasks(mission, next_phase)
                await self.event_bus.emit(PHASE_CHANGED, mission, next_phase)
                logger.info(f"Mission {mission.mission_id} advanced to phase: {next_phase.value}")
                return

        # No more phases - mission complete
        await self._complete_mission(mission)

    async def _check_kill_switch(self, mission: Mission) -> bool:
        """Check kill switch conditions"""
        triggers = mission.roe.kill_switch.get("triggers", [])

        # Detection risk exceeded
        if "detection_risk_exceeded" in triggers:
            if mission.detection_risk > mission.opsec_profile.detection_risk_threshold:
                await self.event_bus.emit(KILL_SWITCH_ACTIVATED, mission, "detection_risk_exceeded")
                return True

        # Scope violation would be checked per-task

        return False

    async def _complete_mission(self, mission: Mission) -> None:
        """Complete mission successfully"""
        mission.status = MissionStatus.COMPLETED
        mission.completed_at = datetime.now()
        mission.current_phase = None
        await self.event_bus.emit(MISSION_COMPLETED, mission)
        logger.info(f"Mission completed: {mission.mission_id}")

    async def abort_mission(self, mission_id: str, reason: str) -> None:
        """Abort mission immediately"""
        mission = self.missions.get(mission_id)
        if not mission:
            raise ValueError(f"Mission not found: {mission_id}")

        mission.status = MissionStatus.ABORTED
        mission.completed_at = datetime.now()

        # Cancel running task
        if mission_id in self._running_missions:
            self._running_missions[mission_id].cancel()
            del self._running_missions[mission_id]

        await self.event_bus.emit(MISSION_ABORTED, mission, reason)
        logger.warning(f"Mission aborted: {mission_id} - {reason}")

    async def pause_mission(self, mission_id: str) -> None:
        """Pause mission"""
        mission = self.missions.get(mission_id)
        if not mission or mission.status != MissionStatus.RUNNING:
            return

        mission.status = MissionStatus.PAUSED
        await self.event_bus.emit(MISSION_PAUSED, mission)

    async def resume_mission(self, mission_id: str) -> None:
        """Resume paused mission"""
        mission = self.missions.get(mission_id)
        if not mission or mission.status != MissionStatus.PAUSED:
            return

        mission.status = MissionStatus.RUNNING
        await self.event_bus.emit(MISSION_RESUMED, mission)

    def get_mission(self, mission_id: str) -> Optional[Mission]:
        return self.missions.get(mission_id)

    def list_missions(self) -> List[Mission]:
        return list(self.missions.values())

    async def add_target(self, mission_id: str, identifier: str, target_type: str) -> Target:
        """Add target to mission with scope validation"""
        mission = self.missions.get(mission_id)
        if not mission:
            raise ValueError(f"Mission not found: {mission_id}")

        # Validate scope
        if not validate_scope(identifier, mission.scope_receipt):
            raise ValueError(f"Target {identifier} not in scope")

        target = Target(
            target_id=generate_id("tgt-"),
            mission_id=mission_id,
            identifier=identifier,
            target_type=target_type
        )

        mission.add_target(target)
        await self.event_bus.emit(TARGET_DISCOVERED, target, mission)
        return target

    async def add_finding(
        self,
        mission_id: str,
        phase: Phase,
        operator: OperatorArchetype,
        target: str,
        vulnerability: Dict,
        evidence: Dict,
        severity: FindingSeverity
    ) -> Finding:
        """Add finding to mission"""
        mission = self.missions.get(mission_id)
        if not mission:
            raise ValueError(f"Mission not found: {mission_id}")

        finding = Finding(
            finding_id=generate_id("FND-"),
            mission_id=mission_id,
            phase=phase,
            operator=operator,
            target=target,
            vulnerability=vulnerability,
            evidence=evidence,
            severity=severity
        )

        mission.add_finding(finding)
        await self.event_bus.emit(FINDING_DISCOVERED, finding, mission)
        return finding

    async def add_evidence(self, mission_id: str, finding_id: str, evidence_type: str, content: bytes) -> Evidence:
        """Add evidence to finding"""
        mission = self.missions.get(mission_id)
        if not mission:
            raise ValueError(f"Mission not found: {mission_id}")

        evidence = Evidence(
            evidence_id=generate_id("EV-"),
            finding_id=finding_id,
            mission_id=mission_id,
            evidence_type=evidence_type,
            content=content,
            content_hash=hash_content(content)
        )

        mission.add_evidence(evidence)
        await self.event_bus.emit(EVIDENCE_COLLECTED, evidence, mission)
        return evidence

    async def generate_report(self, mission_id: str, formats: List[str] = None) -> Dict[str, str]:
        """Generate mission report in multiple formats"""
        mission = self.missions.get(mission_id)
        if not mission:
            raise ValueError(f"Mission not found: {mission_id}")

        formats = formats or ["html", "json", "pdf"]
        reports = {}

        # Build report data
        report_data = {
            "mission": mission.to_dict(),
            "findings": [f.to_dict() for f in mission.findings.values()],
            "targets": [t.to_dict() for t in mission.targets.values()],
            "summary": {
                "total_findings": len(mission.findings),
                "by_severity": {
                    s.value: len(mission.get_findings_by_severity(s))
                    for s in FindingSeverity
                },
                "phases_completed": [p.value for p in mission.phases_completed],
            }
        }

        # Generate each format
        for fmt in formats:
            if fmt == "json":
                reports["json"] = json.dumps(report_data, indent=2, ensure_ascii=False)
            elif fmt == "html":
                reports["html"] = self._generate_html_report(report_data)
            elif fmt == "pdf":
                # Would use weasyprint or wkhtmltopdf
                reports["pdf"] = "PDF generation not implemented"
            elif fmt == "sarif":
                reports["sarif"] = self._generate_sarif_report(report_data)

        return reports

    def _generate_html_report(self, data: Dict) -> str:
        """Generate HTML report"""
        html = f"""
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>Security Assessment Report - {data['mission']['name']}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        h1 {{ color: #1a1a2e; border-bottom: 3px solid #e94560; padding-bottom: 10px; }}
        h2 {{ color: #16213e; margin-top: 30px; }}
        .meta {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin: 20px 0; }}
        .meta-item {{ background: #f8f9fa; padding: 15px; border-radius: 6px; }}
        .meta-label {{ font-size: 12px; color: #666; text-transform: uppercase; }}
        .meta-value {{ font-weight: 600; color: #1a1a2e; }}
        .severity-critical {{ border-left: 4px solid #dc3545; }}
        .severity-high {{ border-left: 4px solid #fd7e14; }}
        .severity-medium {{ border-left: 4px solid #ffc107; }}
        .severity-low {{ border-left: 4px solid #28a745; }}
        .severity-info {{ border-left: 4px solid #17a2b8; }}
        .finding {{ background: #f8f9fa; border-radius: 6px; padding: 20px; margin: 15px 0; }}
        .finding-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }}
        .cvss {{ font-family: monospace; background: #e9ecef; padding: 2px 8px; border-radius: 4px; }}
        table {{ width: 100%; border-collapse: collapse; margin: 15px 0; }}
        th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #dee2e6; }}
        th {{ background: #1a1a2e; color: white; }}
        .evidence {{ background: #f8f9fa; padding: 15px; border-radius: 6px; font-family: monospace; font-size: 12px; overflow-x: auto; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Security Assessment Report</h1>
        <h2>{data['mission']['name']}</h2>

        <div class="meta">
            <div class="meta-item"><div class="meta-label">Mission ID</div><div class="meta-value">{data['mission']['mission_id']}</div></div>
            <div class="meta-item"><div class="meta-label">Status</div><div class="meta-value">{data['mission']['status']}</div></div>
            <div class="meta-item"><div class="meta-label">Started</div><div class="meta-value">{data['mission'].get('started_at', 'N/A')}</div></div>
            <div class="meta-item"><div class="meta-label">Completed</div><div class="meta-value">{data['mission'].get('completed_at', 'N/A')}</div></div>
            <div class="meta-item"><div class="meta-label">RoE Template</div><div class="meta-value">{data['mission']['roe']['template_id']}</div></div>
            <div class="meta-item"><div class="meta-label">OPSEC Profile</div><div class="meta-value">{data['mission']['opsec_profile']['profile_id']}</div></div>
        </div>

        <h2>Executive Summary</h2>
        <p>This report details the results of a security assessment conducted against the authorized scope.</p>

        <h3>Finding Summary</h3>
        <table>
            <tr><th>Severity</th><th>Count</th></tr>
"""
        for sev, count in data['summary']['by_severity'].items():
            html += f"            <tr><td><span class='severity-{sev}'>{sev.upper()}</span></td><td>{count}</td></tr>\n"

        html += """
        </table>

        <h2>Detailed Findings</h2>
"""

        for finding in data['findings']:
            sev = finding['severity']
            html += f"""
        <div class="finding severity-{sev}">
            <div class="finding-header">
                <h3>{finding['vulnerability'].get('title', 'Untitled Finding')}</h3>
                <span class="cvss">CVSS: {finding.get('cvss31_score', 'N/A')}</span>
            </div>
            <p><strong>Target:</strong> {finding['target']}</p>
            <p><strong>Phase:</strong> {finding['phase']}</p>
            <p><strong>Operator:</strong> {finding['operator']}</p>
            <p><strong>CVE:</strong> {finding['vulnerability'].get('cve', 'N/A')}</p>
            <p><strong>CWE:</strong> {finding['vulnerability'].get('cwe', 'N/A')}</p>
            <p><strong>MITRE ATT&CK:</strong> {', '.join(finding.get('mitre_techniques', [])) or 'N/A'}</p>
            <p><strong>Remediation:</strong> {finding.get('remediation', 'Not provided')}</p>
            <div class="evidence">
<strong>Evidence:</strong> {finding['evidence'].get('curl_command', 'Not available')}
            </div>
        </div>
"""

        html += """
    </div>
</body>
</html>
"""
        return html

    def _generate_sarif_report(self, data: Dict) -> str:
        """Generate SARIF format report"""
        sarif = {
            "version": "2.1.0",
            "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
            "runs": [{
                "tool": {
                    "driver": {
                        "name": "Crimea Security Framework v2",
                        "version": "2.0.0",
                        "informationUri": "https://github.com/hermes/crimea-sec-v2"
                    }
                },
                "results": []
            }]
        }

        for finding in data['findings']:
            result = {
                "ruleId": finding['vulnerability'].get('cve', finding['finding_id']),
                "level": self._severity_to_sarif(finding['severity']),
                "message": {"text": finding['vulnerability'].get('title', 'Security finding')},
                "locations": [{
                    "physicalLocation": {
                        "artifactLocation": {"uri": finding['target']}
                    }
                }],
                "properties": {
                    "cvss": finding.get('cvss31_vector'),
                    "mitre": finding.get('mitre_techniques', []),
                    "phase": finding['phase'],
                    "operator": finding['operator']
                }
            }
            sarif["runs"][0]["results"].append(result)

        return json.dumps(sarif, indent=2, ensure_ascii=False)

    def _severity_to_sarif(self, severity: str) -> str:
        mapping = {
            "critical": "error",
            "high": "error",
            "medium": "warning",
            "low": "note",
            "info": "note"
        }
        return mapping.get(severity, "note")


# === Factory Functions ===

async def create_mission_from_scope(
    scope_id: str,
    name: str,
    description: str,
    roe_template: str = "strict",
    opsec_profile: str = "balanced",
    config_dir: Path = None
) -> Mission:
    """Convenience function to create mission from predefined scope"""
    config = ConfigLoader(config_dir)
    scope = config.get_scope_by_id(scope_id)

    # Build scope receipt from scope config
    receipt = ScopeReceipt(
        receipt_id=generate_id("SR-"),
        customer_legal_entity=scope.get("organization", "Unknown"),
        customer_authorized_representative=scope.get("contacts", [{}])[0].get("email", "Unknown"),
        target_systems=scope.get("urls", []) + scope.get("cidrs", []),
        ip_ranges=scope.get("cidrs", []),
        domains=[u.replace("https://", "").replace("http://", "").split("/")[0] for u in scope.get("urls", [])],
        excluded_paths=scope.get("scope_details", {}).get("out_of_scope", []),
        testing_window_start=datetime.now(),
        testing_window_end=datetime.now() + timedelta(days=90),
        emergency_contact=scope.get("contacts", [{}])[0].get("email", "Unknown"),
        authorized_signature=scope.get("authorization_ref", "Pending"),
        signature_date=datetime.now(),
        roe_template_id=roe_template,
        metadata=scope
    )

    mc = MissionControl(config_dir)
    return await mc.create_mission(name, description, receipt, roe_template, opsec_profile)


# Export
__all__ = [
    "MissionControl",
    "TaskQueue",
    "OperatorCell",
    "create_mission_from_scope",
]
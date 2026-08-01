#!/usr/bin/env python3
"""
OPSEC Layer — Operational Security management
Based on T3MP3ST OPSEC Layer with Crimea-specific adaptations
"""

from __future__ import annotations
import asyncio
import logging
import random
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Set
from pathlib import Path

from src.core import OPSECProfile, DetectionRiskLevel, generate_id

logger = logging.getLogger(__name__)


class DetectionType(str, Enum):
    WAF_DETECTED = "waf_detected"
    RATE_LIMIT_HIT = "rate_limit_hit"
    HONEYPOT_SUSPECTED = "honeypot_suspected"
    IDS_ALERT = "ids_alert"
    BEHAVIORAL_ANOMALY = "behavioral_anomaly"
    CAPTCHA_CHALLENGE = "captcha_challenge"
    BLOCKLISTED_IP = "blocklisted_ip"
    TLS_FINGERPRINT_MISMATCH = "tls_fingerprint_mismatch"


class EvasionTechnique(str, Enum):
    CHUNKED_ENCODING = "chunked_encoding"
    HEADER_FOLDING = "header_folding"
    CASE_VARIATION = "case_variation"
    WHITESPACE_OBFUSCATION = "whitespace_obfuscation"
    PARAMETER_POLLUTION = "parameter_pollution"
    UNICODE_NORMALIZATION = "unicode_normalization"
    DOUBLE_ENCODING = "double_encoding"
    FRAGMENTATION = "fragmentation"
    DOMAIN_FRONTING = "domain_fronting"
    CDN_FRONTING = "cdn_fronting"


@dataclass
class DetectionEvent:
    """Single detection event"""
    event_id: str
    detection_type: DetectionType
    target: str
    tool: str
    timestamp: datetime = field(default_factory=datetime.now)
    severity: float = 0.5  # 0.0 - 1.0
    details: Dict[str, Any] = field(default_factory=dict)
    mitigated: bool = False
    mitigation: str = ""


@dataclass
class OPSECState:
    """Current OPSEC state for a mission/operator"""
    operator_id: str
    mission_id: str
    profile: OPSECProfile
    detection_risk: float = 0.0
    cooldown_until: datetime = field(default_factory=datetime.now)
    consecutive_detections: int = 0
    total_requests: int = 0
    blocked_requests: int = 0
    waf_encounters: int = 0
    honeypot_encounters: int = 0
    ip_rotations: int = 0
    user_agent_rotations: int = 0
    detection_history: List[DetectionEvent] = field(default_factory=list)
    active_evasions: Set[EvasionTechnique] = field(default_factory=set)
    burn_risk: float = 0.0

    def is_in_cooldown(self) -> bool:
        return datetime.now() < self.cooldown_until

    def get_cooldown_remaining(self) -> float:
        remaining = (self.cooldown_until - datetime.now()).total_seconds()
        return max(0, remaining)

    def add_detection(self, event: DetectionEvent) -> None:
        self.detection_history.append(event)
        self.detection_risk = min(1.0, self.detection_risk + event.severity * 0.1)
        self.consecutive_detections += 1
        self._apply_mitigation(event)

    def _apply_mitigation(self, event: DetectionEvent) -> None:
        """Apply automatic mitigation based on detection type"""
        mitigations = {
            DetectionType.WAF_DETECTED: self._mitigate_waf,
            DetectionType.RATE_LIMIT_HIT: self._mitigate_rate_limit,
            DetectionType.HONEYPOT_SUSPECTED: self._mitigate_honeypot,
            DetectionType.IDS_ALERT: self._mitigate_ids,
            DetectionType.CAPTCHA_CHALLENGE: self._mitigate_captcha,
        }
        if event.detection_type in mitigations:
            mitigations[event.detection_type](event)

    def _mitigate_waf(self, event: DetectionEvent) -> None:
        self.waf_encounters += 1
        self.active_evasions.add(EvasionTechnique.CHUNKED_ENCODING)
        self.active_evasions.add(EvasionTechnique.CASE_VARIATION)
        self.cooldown_until = datetime.now() + timedelta(seconds=self.profile.cooldown_base * 2)

    def _mitigate_rate_limit(self, event: DetectionEvent) -> None:
        self.cooldown_until = datetime.now() + timedelta(seconds=self.profile.cooldown_base * 5)

    def _mitigate_honeypot(self, event: DetectionEvent) -> None:
        self.honeypot_encounters += 1
        self.burn_risk = min(1.0, self.burn_risk + 0.3)

    def _mitigate_ids(self, event: DetectionEvent) -> None:
        self.cooldown_until = datetime.now() + timedelta(seconds=self.profile.cooldown_base * 3)

    def _mitigate_captcha(self, event: DetectionEvent) -> None:
        self.cooldown_until = datetime.now() + timedelta(seconds=self.profile.cooldown_base * 10)

    def record_request(self, blocked: bool = False) -> None:
        self.total_requests += 1
        if blocked:
            self.blocked_requests += 1

    def rotate_ip(self) -> None:
        self.ip_rotations += 1
        self.detection_risk = max(0.0, self.detection_risk - 0.1)

    def rotate_user_agent(self) -> None:
        self.user_agent_rotations += 1

    def decay_risk(self, rate: float = 0.01) -> None:
        """Decay detection risk over time"""
        self.detection_risk = max(0.0, self.detection_risk - rate)
        self.consecutive_detections = max(0, self.consecutive_detections - 1)
        self.burn_risk = max(0.0, self.burn_risk - 0.005)

    def is_burned(self, threshold: float = 0.9) -> bool:
        return self.burn_risk >= threshold or self.detection_risk >= threshold

    def to_dict(self) -> Dict:
        return {
            "operator_id": self.operator_id,
            "mission_id": self.mission_id,
            "detection_risk": self.detection_risk,
            "cooldown_remaining": self.get_cooldown_remaining(),
            "consecutive_detections": self.consecutive_detections,
            "total_requests": self.total_requests,
            "blocked_requests": self.blocked_requests,
            "waf_encounters": self.waf_encounters,
            "honeypot_encounters": self.honeypot_encounters,
            "burn_risk": self.burn_risk,
            "active_evasions": [e.value for e in self.active_evasions],
        }


class OPSECController:
    """
    OPSEC Controller — manages detection risk, cooldowns, evasions
    """

    def __init__(self, profile: OPSECProfile):
        self.profile = profile
        self.states: Dict[str, OPSECState] = {}
        self.global_detection_risk = 0.0
        self._lock = asyncio.Lock()
        self._decay_task: Optional[asyncio.Task] = None

    async def register_operator(self, operator_id: str, mission_id: str) -> OPSECState:
        """Register operator for OPSEC tracking"""
        async with self._lock:
            state = OPSECState(
                operator_id=operator_id,
                mission_id=mission_id,
                profile=self.profile
            )
            self.states[operator_id] = state
            return state

    async def unregister_operator(self, operator_id: str) -> None:
        async with self._lock:
            self.states.pop(operator_id, None)

    async def record_detection(
        self,
        operator_id: str,
        detection_type: DetectionType,
        target: str,
        tool: str,
        severity: float = 0.5,
        details: Dict = None
    ) -> DetectionEvent:
        """Record a detection event"""
        async with self._lock:
            state = self.states.get(operator_id)
            if not state:
                return None

            event = DetectionEvent(
                event_id=generate_id("DET-"),
                detection_type=detection_type,
                target=target,
                tool=tool,
                severity=severity,
                details=details or {}
            )

            state.add_detection(event)

            # Update global risk
            self.global_detection_risk = max(
                self.global_detection_risk,
                state.detection_risk
            )

            # Check kill switch
            if state.is_burned(self.profile.burn_threshold):
                logger.critical(f"Operator {operator_id} BURNED - detection risk: {state.detection_risk}")

            return event

    async def record_request(self, operator_id: str, blocked: bool = False) -> None:
        """Record a request for rate limiting"""
        async with self._lock:
            state = self.states.get(operator_id)
            if state:
                state.record_request(blocked)

    async def get_cooldown(self, operator_id: str) -> float:
        """Get remaining cooldown for operator"""
        async with self._lock:
            state = self.states.get(operator_id)
            if not state:
                return 0.0
            return state.get_cooldown_remaining()

    async def wait_cooldown(self, operator_id: str) -> None:
        """Wait for operator cooldown to complete"""
        while True:
            remaining = await self.get_cooldown(operator_id)
            if remaining <= 0:
                break
            await asyncio.sleep(min(remaining, 1.0))

    async def apply_evasion(self, operator_id: str, technique: EvasionTechnique) -> bool:
        """Apply evasion technique"""
        async with self._lock:
            state = self.states.get(operator_id)
            if not state:
                return False

            if technique in self.profile.waf_bypass.get("techniques", []):
                state.active_evasions.add(technique)
                return True
            return False

    async def get_active_evasions(self, operator_id: str) -> List[EvasionTechnique]:
        async with self._lock:
            state = self.states.get(operator_id)
            if not state:
                return []
            return list(state.active_evasions)

    async def rotate_identity(self, operator_id: str) -> Dict[str, str]:
        """Rotate IP and User-Agent"""
        async with self._lock:
            state = self.states.get(operator_id)
            if not state:
                return {}

            state.rotate_ip()
            state.rotate_user_agent()

            return {
                "ip_rotated": True,
                "user_agent_rotated": True,
                "ip_rotations": state.ip_rotations,
                "ua_rotations": state.user_agent_rotations
            }

    async def start_decay_loop(self, interval: float = 1.0) -> None:
        """Start risk decay background task"""
        async def decay():
            while True:
                await asyncio.sleep(interval)
                async with self._lock:
                    for state in self.states.values():
                        state.decay_risk(self.profile.detection_risk_calculation.get("decay_rate", 0.05))
                    self.global_detection_risk = max(0.0, self.global_detection_risk - 0.01)

        self._decay_task = asyncio.create_task(decay())

    async def stop_decay_loop(self) -> None:
        if self._decay_task:
            self._decay_task.cancel()
            try:
                await self._decay_task
            except asyncio.CancelledError:
                pass

    async def get_state(self, operator_id: str) -> Optional[OPSECState]:
        async with self._lock:
            return self.states.get(operator_id)

    async def get_all_states(self) -> Dict[str, OPSECState]:
        async with self._lock:
            return dict(self.states)

    def calculate_risk_score(self, state: OPSECState) -> float:
        """Calculate composite risk score"""
        factors = self.profile.detection_risk_calculation.get("factors", {})
        score = state.detection_risk

        # Weight by factors
        score *= (1 + factors.get("waf_detection", 0.3) * state.waf_encounters * 0.1)
        score *= (1 + factors.get("rate_limit_hit", 0.2) * (state.blocked_requests / max(1, state.total_requests)))

        return min(1.0, score)

    def should_abort(self, state: OPSECState) -> bool:
        """Check if mission should be aborted"""
        if state.is_burned(self.profile.burn_threshold):
            return True
        if state.detection_risk >= self.profile.detection_risk_threshold:
            return True
        if state.honeypot_encounters > 0:
            return True
        return False


class PayloadEncoder:
    """Payload encoding and polymorphism (T3MP3ST EvasionEngine)"""

    ENCODERS = {
        "url": lambda s: "".join(f"%{ord(c):02X}" for c in s),
        "double_url": lambda s: "".join(f"%25{ord(c):02X}" for c in s),
        "unicode": lambda s: "".join(f"\\u{ord(c):04X}" for c in s),
        "html_entity": lambda s: "".join(f"&#{ord(c)};" for c in s),
        "base64": lambda s: __import__("base64").b64encode(s.encode()).decode(),
        "hex": lambda s: s.encode().hex(),
        "rot13": lambda s: s.translate(str.maketrans(
            "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz",
            "NOPQRSTUVWXYZABCDEFGHIJKLMnopqrstuvwxyzabcdefghijklm"
        )),
    }

    @classmethod
    def encode(cls, payload: str, encoder: str, iterations: int = 1) -> str:
        """Apply encoder to payload"""
        if encoder not in cls.ENCODERS:
            return payload
        result = payload
        for _ in range(iterations):
            result = cls.ENCODERS[encoder](result)
        return result

    @classmethod
    def polymorphic_encode(cls, payload: str, encoders: List[str] = None) -> List[str]:
        """Generate multiple encoded variants"""
        encoders = encoders or ["url", "unicode", "double_url", "html_entity"]
        variants = [payload]
        for encoder in encoders:
            for variant in list(variants):
                variants.append(cls.encode(variant, encoder))
        return list(set(variants))

    @classmethod
    def waf_bypass_variants(cls, payload: str) -> List[str]:
        """Generate WAF bypass variants"""
        variants = [payload]

        # Case variation
        variants.append(payload.swapcase())
        variants.append(payload.upper())
        variants.append(payload.lower())

        # Whitespace obfuscation
        variants.append(payload.replace(" ", "/**/"))
        variants.append(payload.replace(" ", "\t"))
        variants.append(payload.replace(" ", "\n"))

        # Comment injection
        variants.append(payload.replace(" ", "/**/").replace("=", "/**/="))

        # Double encoding
        variants.append(cls.encode(payload, "double_url"))

        # Unicode normalization
        variants.append(cls.encode(payload, "unicode"))

        return list(set(variants))


class UserAgentRotator:
    """User-Agent rotation with realistic browsers"""

    USER_AGENTS = {
        "chrome_windows": [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
        ],
        "chrome_linux": [
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        ],
        "firefox_windows": [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
        ],
        "firefox_linux": [
            "Mozilla/5.0 (X11; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0",
        ],
        "safari_mac": [
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
        ],
        "edge_windows": [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
        ],
        "mobile_android": [
            "Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
        ],
        "mobile_ios": [
            "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1",
        ],
        "curl": [
            "curl/8.5.0",
            "curl/8.4.0",
        ],
        "python": [
            "python-requests/2.31.0",
            "python-httpx/0.26.0",
        ],
    }

    @classmethod
    def get_random(cls, category: str = None) -> str:
        if category and category in cls.USER_AGENTS:
            return random.choice(cls.USER_AGENTS[category])
        all_agents = [ua for agents in cls.USER_AGENTS.values() for ua in agents]
        return random.choice(all_agents)

    @classmethod
    def get_rotating(cls, exclude: List[str] = None) -> str:
        exclude = exclude or []
        all_agents = [ua for agents in cls.USER_AGENTS.values() for ua in agents if ua not in exclude]
        return random.choice(all_agents) if all_agents else cls.get_random()


class ProxyManager:
    """Proxy rotation management"""

    def __init__(self, proxies: List[str] = None):
        self.proxies = proxies or []
        self.current_index = 0
        self.failed_proxies: Set[str] = set()
        self._lock = asyncio.Lock()

    def add_proxies(self, proxies: List[str]) -> None:
        self.proxies.extend(proxies)

    async def get_proxy(self) -> Optional[str]:
        async with self._lock:
            if not self.proxies:
                return None

            # Skip failed
            available = [p for p in self.proxies if p not in self.failed_proxies]
            if not available:
                # Reset failed if all failed
                self.failed_proxies.clear()
                available = self.proxies

            proxy = available[self.current_index % len(available)]
            self.current_index += 1
            return proxy

    async def mark_failed(self, proxy: str) -> None:
        async with self._lock:
            self.failed_proxies.add(proxy)

    async def get_stats(self) -> Dict:
        return {
            "total": len(self.proxies),
            "available": len(self.proxies) - len(self.failed_proxies),
            "failed": len(self.failed_proxies),
            "current_index": self.current_index,
        }


class TimingJitter:
    """Add jitter to request timing"""

    def __init__(self, min_ms: int = 100, max_ms: int = 2000):
        self.min_ms = min_ms
        self.max_ms = max_ms

    async def wait(self) -> float:
        """Wait for random jitter duration"""
        delay = random.uniform(self.min_ms, self.max_ms) / 1000.0
        await asyncio.sleep(delay)
        return delay

    def get_delay(self) -> float:
        """Get random delay without waiting"""
        return random.uniform(self.min_ms, self.max_ms) / 1000.0


# Export
__all__ = [
    "OPSECController",
    "OPSECState",
    "DetectionEvent",
    "DetectionType",
    "EvasionTechnique",
    "PayloadEncoder",
    "UserAgentRotator",
    "ProxyManager",
    "TimingJitter",
]
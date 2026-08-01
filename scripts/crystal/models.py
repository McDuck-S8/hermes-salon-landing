"""
Crystal v3 — Модели данных
Все dataclasses для 22 модулей
"""

# Revisit: when dataclass models, JSON serialization, or model fields change. Last touched: 2026-07-02.

from dataclasses import dataclass, field, asdict
from typing import Optional
from datetime import datetime
import json
import os


# ── Модуль 1: Session Reader ──────────────────────────────────────────

@dataclass
class Signal:
    """Сырой сигнал из сессии"""
    id: str = ""
    type: str = ""          # request, correction, frustration, workflow, unmet
    content: str = ""       # текст сигнала
    source: str = ""        # session_id
    timestamp: str = ""     # ISO format
    severity: float = 0.0   # 0.0 - 1.0
    department: str = ""    # youtube, social-media, etc.
    meta: dict = field(default_factory=dict)

    def __post_init__(self):
        if not self.id:
            self.id = f"sig_{int(datetime.now().timestamp())}_{hash(self.content) % 10000}"
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()


# ── Модуль 2: Pattern Detector ────────────────────────────────────────

@dataclass
class Pattern:
    """Найденный паттерн"""
    id: str = ""
    type: str = ""          # correction_loop, missing_knowledge, frustration_spike, workflow_success, unmet_need
    frequency: int = 0
    severity: float = 0.0
    signals: list = field(default_factory=list)  # signal IDs
    description: str = ""
    department: str = ""
    first_seen: str = ""
    last_seen: str = ""

    def __post_init__(self):
        if not self.id:
            self.id = f"pat_{int(datetime.now().timestamp())}_{hash(self.type) % 10000}"
        if not self.first_seen:
            self.first_seen = datetime.now().isoformat()
        self.last_seen = datetime.now().isoformat()


# ── Модуль 3: Need Analyzer ───────────────────────────────────────────

@dataclass
class Need:
    """Сформированная потребность"""
    id: str = ""
    pattern_type: str = ""
    description: str = ""
    priority: float = 0.0   # 0.0 - 1.0
    impact: str = "medium"  # low, medium, high, critical
    department: str = ""
    created_at: str = ""
    resolved: bool = False

    def __post_init__(self):
        if not self.id:
            self.id = f"need_{int(datetime.now().timestamp())}_{hash(self.description) % 10000}"
        if not self.created_at:
            self.created_at = datetime.now().isoformat()


# ── Модуль 4: Priority Engine ─────────────────────────────────────────

@dataclass
class PrioritizedItem:
    """Элемент с приоритетом"""
    need_id: str = ""
    urgency: float = 0.0    # 0.0 - 1.0
    impact: float = 0.0     # 0.0 - 1.0
    effort: float = 0.0     # 0.0 - 1.0 (чем больше, тем сложнее)
    dependencies: list = field(default_factory=list)
    score: float = 0.0      # вычисленный приоритет

    def calculate_score(self):
        if self.effort > 0:
            self.score = (self.urgency * 0.4 + self.impact * 0.4) / self.effort * 0.2
        else:
            self.score = self.urgency * 0.4 + self.impact * 0.4
        return self.score


# ── Модуль 5: User Energy Model ───────────────────────────────────────

@dataclass
class EnergyState:
    """Состояние пользователя"""
    level: str = "medium"   # low, medium, high
    score: float = 0.5      # 0.0 - 1.0
    signals: list = field(default_factory=list)
    last_updated: str = ""
    suggestions: list = field(default_factory=list)

    def __post_init__(self):
        if not self.last_updated:
            self.last_updated = datetime.now().isoformat()


# ── Модуль 6: Dependency Map ──────────────────────────────────────────

@dataclass
class Dependency:
    """Зависимость между компонентами"""
    source: str = ""        # что зависит
    target: str = ""        # от чего зависит
    type: str = "blocker"   # blocker, enabler, coupled
    description: str = ""


@dataclass
class DependencyGraph:
    """Граф зависимостей"""
    nodes: list = field(default_factory=list)
    edges: list = field(default_factory=list)  # list[Dependency]
    updated_at: str = ""

    def __post_init__(self):
        if not self.updated_at:
            self.updated_at = datetime.now().isoformat()


# ── Модуль 7: Risk Assessment ─────────────────────────────────────────

@dataclass
class RiskAssessment:
    """Оценка риска для proposal"""
    proposal_id: str = ""
    level: str = "safe"     # safe, moderate, risky, critical
    score: float = 0.0      # 0.0 - 1.0
    factors: list = field(default_factory=list)
    recommendation: str = ""
    auto_approve: bool = False


# ── Модуль 8: Development Proposer ────────────────────────────────────

@dataclass
class Proposal:
    """Предложение по изменению"""
    id: str = ""
    action: str = ""        # create_skill, patch_skill, update_dox, update_memory, new_tool, architecture_change
    description: str = ""
    risk_level: str = "safe"
    priority: float = 0.0
    estimated_impact: str = "medium"
    department: str = ""
    auto: bool = False      # можно ли автоматически применить
    tested: bool = False
    applied: bool = False
    created_at: str = ""

    def __post_init__(self):
        if not self.id:
            self.id = f"prop_{int(datetime.now().timestamp())}_{hash(self.description) % 10000}"
        if not self.created_at:
            self.created_at = datetime.now().isoformat()


# ── Модуль 9: Staleness Detector ──────────────────────────────────────

@dataclass
class StalenessItem:
    """Устаревший элемент"""
    id: str = ""
    type: str = ""          # skill, dependency, config, doc, tool, provider
    name: str = ""
    current_version: str = ""
    latest_version: str = ""
    stale_days: int = 0
    action: str = ""        # update, patch, replace, remove
    auto: bool = False

    def __post_init__(self):
        if not self.id:
            self.id = f"stale_{int(datetime.now().timestamp())}_{hash(self.name) % 10000}"


# ── Модуль 10: Proactive Alerts ───────────────────────────────────────

@dataclass
class Alert:
    """Проактивное уведомление"""
    id: str = ""
    type: str = ""          # api_change, dependency_stale, security, idle
    severity: str = "info"  # info, warning, critical
    title: str = ""
    message: str = ""
    department: str = ""
    action_required: bool = False
    delivered: bool = False
    created_at: str = ""

    def __post_init__(self):
        if not self.id:
            self.id = f"alert_{int(datetime.now().timestamp())}_{hash(self.title) % 10000}"
        if not self.created_at:
            self.created_at = datetime.now().isoformat()


# ── Модуль 11: Memory Integration ─────────────────────────────────────

@dataclass
class MemoryEntry:
    """Запись в memory"""
    key: str = ""
    value: str = ""
    source: str = ""        # pattern, correction, decision
    confidence: float = 1.0
    created_at: str = ""


# ── Модуль 12: Feedback Loop ──────────────────────────────────────────

@dataclass
class Assessment:
    """Оценка эффективности изменения"""
    id: str = ""
    metric: str = ""
    before: float = 0.0
    after: float = 0.0
    delta: float = 0.0
    success: bool = False
    proposal_id: str = ""
    measured_at: str = ""

    def __post_init__(self):
        if not self.id:
            self.id = f"fb_{int(datetime.now().timestamp())}_{hash(self.metric) % 10000}"
        if not self.measured_at:
            self.measured_at = datetime.now().isoformat()
        self.delta = self.after - self.before


# ── Модуль 13: Versioning ─────────────────────────────────────────────

@dataclass
class ChangelogEntry:
    """Запись в changelog"""
    id: str = ""
    version: str = ""
    description: str = ""
    reason: str = ""
    effect: str = ""        # feedback score после изменения
    alternatives: list = field(default_factory=list)
    timestamp: str = ""

    def __post_init__(self):
        if not self.id:
            self.id = f"cl_{int(datetime.now().timestamp())}_{hash(self.description) % 10000}"
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()


# ── Модуль 14: Cross-department Synergy ───────────────────────────────

@dataclass
class Synergy:
    """Связь между отделами"""
    departments: list = field(default_factory=list)
    type: str = ""          # content_pipeline, tech_stack, data_flow, skill_reuse
    description: str = ""
    potential: str = ""     # low, medium, high
    action: str = ""


# ── Модуль 15: Long-term Goals ────────────────────────────────────────

@dataclass
class Goal:
    """Стратегическая цель"""
    id: str = ""
    title: str = ""
    description: str = ""
    department: str = ""
    progress: float = 0.0   # 0.0 - 1.0
    milestones: list = field(default_factory=list)
    blockers: list = field(default_factory=list)
    deadline: str = ""
    created_at: str = ""

    def __post_init__(self):
        if not self.id:
            self.id = f"goal_{int(datetime.now().timestamp())}_{hash(self.title) % 10000}"
        if not self.created_at:
            self.created_at = datetime.now().isoformat()


# ── Модуль 16: External Intelligence ──────────────────────────────────

@dataclass
class IntelItem:
    """Элемент из внешнего мира"""
    id: str = ""
    source: str = ""        # github, pypi, ai_news, security
    title: str = ""
    description: str = ""
    url: str = ""
    relevance: float = 0.0  # 0.0 - 1.0
    department: str = ""
    discovered_at: str = ""

    def __post_init__(self):
        if not self.id:
            self.id = f"intel_{int(datetime.now().timestamp())}_{hash(self.title) % 10000}"
        if not self.discovered_at:
            self.discovered_at = datetime.now().isoformat()


# ── Модуль 17: Automated Testing ──────────────────────────────────────

@dataclass
class TestResult:
    """Результат теста"""
    id: str = ""
    target: str = ""        # skill, code, dox, config
    name: str = ""
    level: str = "quick"    # quick, standard, full
    passed: bool = False
    details: str = ""
    duration_ms: int = 0
    tested_at: str = ""

    def __post_init__(self):
        if not self.id:
            self.id = f"test_{int(datetime.now().timestamp())}_{hash(self.name) % 10000}"
        if not self.tested_at:
            self.tested_at = datetime.now().isoformat()


# ── Модуль 18: Rollback ───────────────────────────────────────────────

@dataclass
class Snapshot:
    """Снэпшот для отката"""
    id: str = ""
    version: str = ""
    description: str = ""
    files: list = field(default_factory=list)  # paths that were changed
    created_at: str = ""

    def __post_init__(self):
        if not self.id:
            self.id = f"snap_{int(datetime.now().timestamp())}_{hash(self.version) % 10000}"
        if not self.created_at:
            self.created_at = datetime.now().isoformat()


# ── Модуль 19: Knowledge Base ─────────────────────────────────────────

@dataclass
class KnowledgeEntry:
    """Запись в базе знаний"""
    id: str = ""
    problem: str = ""       # что за проблема
    solution: str = ""      # как решили
    effect: str = ""        # какой эффект
    department: str = ""
    confidence: float = 1.0
    times_used: int = 0
    created_at: str = ""

    def __post_init__(self):
        if not self.id:
            self.id = f"kb_{int(datetime.now().timestamp())}_{hash(self.problem) % 10000}"
        if not self.created_at:
            self.created_at = datetime.now().isoformat()


# ── Модуль 20: Communication Adapter ──────────────────────────────────

@dataclass
class CommunicationProfile:
    """Профиль общения с пользователем"""
    language: str = "ru"    # ru, en
    length: str = "short"   # short, medium, long
    technicality: str = "medium"  # low, medium, high
    tone: str = "friendly"  # formal, friendly, technical
    format: str = "text"    # text, tables, lists
    learned_corrections: list = field(default_factory=list)
    updated_at: str = ""

    def __post_init__(self):
        if not self.updated_at:
            self.updated_at = datetime.now().isoformat()


# ── Модуль 21: Resource Monitor ───────────────────────────────────────

@dataclass
class ResourceState:
    """Состояние ресурсов"""
    api_calls_today: int = 0
    api_limit_daily: int = 1000
    tokens_this_month: int = 0
    tokens_limit_monthly: int = 1000000
    budget_spent: float = 0.0
    budget_limit: float = 100.0
    module_times: dict = field(default_factory=dict)  # module -> seconds
    disk_usage_mb: float = 0.0
    last_updated: str = ""

    def __post_init__(self):
        if not self.last_updated:
            self.last_updated = datetime.now().isoformat()

    def api_available(self) -> bool:
        return self.api_calls_today < self.api_limit_daily

    def budget_available(self) -> bool:
        return self.budget_spent < self.budget_limit * 0.9

    def suggest_cheap_model(self) -> bool:
        return not self.budget_available()


# ── Модуль 22: Self-Evolution ─────────────────────────────────────────

@dataclass
class EvolutionEntry:
    """Запись эволюции"""
    id: str = ""
    module: str = ""
    action: str = ""        # optimize, refactor, new_module, remove
    reason: str = ""
    before_score: float = 0.0
    after_score: float = 0.0
    timestamp: str = ""

    def __post_init__(self):
        if not self.id:
            self.id = f"evo_{int(datetime.now().timestamp())}_{hash(self.module) % 10000}"
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()


# ── Утилиты ───────────────────────────────────────────────────────────

def save_json(data, path: str):
    """Сохранить данные в JSON"""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        if hasattr(data, "__dataclass_fields__"):
            json.dump(asdict(data), f, ensure_ascii=False, indent=2)
        elif isinstance(data, list):
            json.dump([asdict(item) if hasattr(item, "__dataclass_fields__") else item for item in data], f, ensure_ascii=False, indent=2)
        elif isinstance(data, dict):
            json.dump(data, f, ensure_ascii=False, indent=2)
        else:
            json.dump(data, f, ensure_ascii=False, indent=2)


def load_json(path: str, cls=None):
    """Загрузить данные из JSON"""
    if not os.path.exists(path):
        return [] if cls else {}
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if cls and isinstance(data, list):
        valid_fields = set(cls.__dataclass_fields__.keys())
        return [cls(**{k: v for k, v in item.items() if k in valid_fields}) for item in data]
    return data

#!/usr/bin/env python3
"""
Fractal Knowledge Wheel — Рекурсивное исследование знаний.
Режим 1: Анализ (ключ → аспекты → пробелы → задачи)
Режим 2: Синтез (разрозненные находки → новые ключи/связки)
"""

import itertools
import json
import logging
import math
import re
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import sqlite3

logger = logging.getLogger("fractal_wheel")


# =============================================================================
# Domain definitions — секторные схемы для разных доменов
# =============================================================================

DOMAIN_SECTORS: Dict[str, List[Dict[str, Any]]] = {
    "arbitrage": [
        {"id": "traffic", "name": "Трафик", "weight": 1.0, "critical": True},
        {"id": "bridge", "name": "Прокладка", "weight": 1.0, "critical": True},
        {"id": "offer", "name": "Оффер", "weight": 1.0, "critical": True},
        {"id": "creatives", "name": "Креативы", "weight": 1.2, "critical": True},
        {"id": "payments", "name": "Платежи", "weight": 1.0, "critical": True},
        {"id": "withdrawal", "name": "Вывод", "weight": 1.0, "critical": True},
        {"id": "legal", "name": "Юридические риски", "weight": 0.8, "critical": False},
        {"id": "scaling", "name": "Масштабирование", "weight": 0.7, "critical": False},
    ],
    "ai-ofm": [
        {"id": "models", "name": "Модели генерации", "weight": 1.2, "critical": True},
        {"id": "platforms", "name": "Платформы размещения", "weight": 1.0, "critical": True},
        {"id": "traffic", "name": "Трафик", "weight": 1.0, "critical": True},
        {"id": "content", "name": "Контент-стратегия", "weight": 1.0, "critical": True},
        {"id": "monetization", "name": "Монетизация", "weight": 1.0, "critical": True},
        {"id": "compliance", "name": "Compliance/блокировки", "weight": 1.2, "critical": True},
        {"id": "team", "name": "Команда/аутсорс", "weight": 0.7, "critical": False},
        {"id": "legal", "name": "Юридические риски", "weight": 0.8, "critical": False},
    ],
    "craft": [
        {"id": "niche", "name": "Ниша/продукт", "weight": 1.2, "critical": True},
        {"id": "traffic", "name": "Трафик", "weight": 1.0, "critical": True},
        {"id": "production", "name": "Производство", "weight": 1.0, "critical": True},
        {"id": "creatives", "name": "Креативы/фото", "weight": 1.0, "critical": True},
        {"id": "fulfillment", "name": "Фулфилмент", "weight": 1.0, "critical": True},
        {"id": "payments", "name": "Платежи/выплата", "weight": 1.0, "critical": True},
        {"id": "legal", "name": "Юридические/налоги", "weight": 0.8, "critical": False},
        {"id": "scaling", "name": "Масштабирование", "weight": 0.7, "critical": False},
    ],
    "default": [
        {"id": "aspect1", "name": "Аспект 1", "weight": 1.0, "critical": True},
        {"id": "aspect2", "name": "Аспект 2", "weight": 1.0, "critical": True},
        {"id": "aspect3", "name": "Аспект 3", "weight": 1.0, "critical": True},
        {"id": "aspect4", "name": "Аспект 4", "weight": 1.0, "critical": False},
        {"id": "aspect5", "name": "Аспект 5", "weight": 1.0, "critical": False},
        {"id": "aspect6", "name": "Аспект 6", "weight": 1.0, "critical": False},
    ],
}


# =============================================================================
# Data classes
# =============================================================================

@dataclass
class Sector:
    """Один сектор колеса."""
    id: str
    name: str
    weight: float = 1.0
    critical: bool = False
    fill_percent: int = 0
    status: str = "🔴"  # 🟢 🟡 🔴
    facts: List[str] = field(default_factory=list)
    gaps: List[str] = field(default_factory=list)
    sources: List[str] = field(default_factory=list)
    notes: str = ""

    def update_status(self) -> None:
        if self.fill_percent >= 80:
            self.status = "🟢"
        elif self.fill_percent >= 30:
            self.status = "🟡"
        else:
            self.status = "🔴"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "weight": self.weight,
            "critical": self.critical,
            "fill_percent": self.fill_percent,
            "status": self.status,
            "facts": self.facts,
            "gaps": self.gaps,
            "sources": self.sources,
            "notes": self.notes,
        }


@dataclass
class WheelAssessment:
    """Результат оценки колеса."""
    center: str
    domain: str
    sectors: List[Sector]
    overall_percent: int
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    slug: str = ""

    @property
    def green_sectors(self) -> List[Sector]:
        return [s for s in self.sectors if s.status == "🟢"]

    @property
    def yellow_sectors(self) -> List[Sector]:
        return [s for s in self.sectors if s.status == "🟡"]

    @property
    def red_sectors(self) -> List[Sector]:
        return [s for s in self.sectors if s.status == "🔴"]

    @property
    def critical_red_sectors(self) -> List[Sector]:
        return [s for s in self.sectors if s.status == "🔴" and s.critical]

    @property
    def priority_tasks(self) -> List[Dict[str, Any]]:
        """Приоритизированные задачи: сначала критические красные, потом обычные красные, потом жёлтые."""
        tasks = []
        for sector in self.critical_red_sectors:
            tasks.append({
                "type": "research",
                "target": sector.id,
                "sector_name": sector.name,
                "context": self.center,
                "priority": "critical",
                "expected_outcome": f"Fill {sector.name} to >80%",
                "gaps": sector.gaps,
            })
        for sector in self.red_sectors:
            if not sector.critical:
                tasks.append({
                    "type": "research",
                    "target": sector.id,
                    "sector_name": sector.name,
                    "context": self.center,
                    "priority": "high",
                    "expected_outcome": f"Fill {sector.name} to >30%",
                    "gaps": sector.gaps,
                })
        for sector in self.yellow_sectors:
            tasks.append({
                "type": "research",
                "target": sector.id,
                "sector_name": sector.name,
                "context": self.center,
                "priority": "medium",
                "expected_outcome": f"Fill {sector.name} to >80%",
                "gaps": sector.gaps,
            })
        return tasks


# =============================================================================
# Knowledge Source — интеграция с Knowledge Cube / OKF
# =============================================================================

class KnowledgeSource:
    """Интерфейс для получения фактов из Knowledge Cube / OKF."""

    def __init__(self, cube_path: Optional[Path] = None):
        self.cube_path = cube_path or Path("D:/Portable_Soft/hermes/cache/knowledge_cube.db")

    def get_facts_for_sector(self, center: str, sector: Sector) -> List[str]:
        """Получить факты из Knowledge Cube для сектора."""
        # TODO: интеграция с knowledge_cube.py
        return []

    def get_gaps_for_sector(self, center: str, sector: Sector) -> List[str]:
        """Определить пробелы на основе текущих знаний."""
        # TODO: анализ белых пятен OKF
        return []

    def get_recent_findings(self, days: int = 7) -> List[Dict[str, Any]]:
        """Получить находки за последние N дней из knowledge_cube.db."""
        findings = []
        try:
            conn = sqlite3.connect(str(self.cube_path))
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cutoff = (datetime.now() - timedelta(days=days)).isoformat()

            # Get from kc_entries (main knowledge base)
            cursor.execute("""
                SELECT id, content, tags, source, category, importance, created_at
                FROM kc_entries
                WHERE created_at >= ?
                ORDER BY created_at DESC
                LIMIT 200
            """, (cutoff,))

            for row in cursor.fetchall():
                findings.append({
                    "id": row["id"],
                    "content": row["content"],
                    "tags": row["tags"],
                    "source": row["source"],
                    "category": row["category"],
                    "importance": row["importance"],
                    "created_at": row["created_at"],
                    "type": "kc_entry"
                })

            # Get from experiences (session learnings)
            cursor.execute("""
                SELECT id, content, axis_domain, axis_outcome, tags, importance, ts
                FROM experiences
                WHERE ts >= ?
                ORDER BY ts DESC
                LIMIT 100
            """, (cutoff,))

            for row in cursor.fetchall():
                findings.append({
                    "id": row["id"],
                    "content": row["content"],
                    "tags": row["tags"],
                    "source": "experience",
                    "category": row["axis_domain"],
                    "importance": row["importance"],
                    "created_at": row["ts"],
                    "type": "experience"
                })

            conn.close()
        except Exception as e:
            logger.warning(f"Failed to query knowledge cube: {e}")

        return findings


# =============================================================================
# Synthesis Engine — Режим 2: Синтез новых ключей
# =============================================================================

@dataclass
class Entity:
    """Сущность, извлечённая из находок."""
    type: str  # traffic, offer, payment, withdrawal, geo, bridge, tool
    name: str
    attributes: Dict[str, Any] = field(default_factory=dict)
    source_ids: List[str] = field(default_factory=list)
    confidence: float = 0.5

    def to_key(self) -> str:
        return f"{self.type}:{self.name.lower()}"


@dataclass
class SynthesizedKey:
    """Новый сконструированный ключ (связка)."""
    name: str
    description: str
    components: Dict[str, List[Entity]]  # traffic: [...], offer: [...], etc.
    compatibility_score: float
    novelty_score: float
    reasoning: str
    source_findings: List[str]


class SynthesisEngine:
    """Двигатель синтеза: из разрозненных фактов → новые ключи."""

    # Паттерны для извлечения сущностей из текста
    TRAFFIC_PATTERNS = [
        r"\b(TikTok|YouTube Shorts|Reels|Shorts|UGC|native|push|pop|Facebook Ads|Google Ads|Telegram Ads|propeller|richads|popads|taboola|outbrain|mini apps?|mini-apps?|tg ads?)\b",
        r"\b(organic|paid|free|cheap|expensive)\s+(traffic|трафик)\b",
    ]
    OFFER_PATTERNS = [
        r"\b(1xBet|1win|Mostbet|Parimatch|Bet365|Melbet|Betwinner|CPAGrip|OGAds|AdWorkMedia|CPAlead|cpagrip|ogads|adworkmedia|cpatlead)\b",
        r"\b(CPA|CPS|CPL|SOI|DOI|revshare|revenue share)\b",
        r"\b(казино|беттинг|gambling|betting|nutra|whitehat|greyhat|blackhat)\b",
    ]
    PAYMENT_PATTERNS = [
        r"\b(USDT|USDC|BTC|ETH|TRC20|ERC20|BEP20|P2P|Bybit|Binance|KuCoin|OKX|T-Bank|Т-Банк|Сбер|Тинькофф|Raiffeisen)\b",
        r"\b(крипта|криптовалюта|фиат|карта|банк|перевод)\b",
    ]
    WITHDRAWAL_PATTERNS = [
        r"\b(вывод|withdrawal|пейаут|payout|выплата)\b",
        r"\b(USDT\s*→\s*RUB|RUB\s*→\s*USDT|карта|счёт)\b",
    ]
    GEO_PATTERNS = [
        r"\b(Индия|India|RU|RF|Russia|Россия|Крым|Crimea|Турция|Turkey|TR|BR|Brazil|Бразилия|VN|Vietnam|Вьетнам|ID|Indonesia|Индонезия|TH|Thailand|Таиланд|PH|Philippines|Филиппины)\b",
    ]
    BRIDGE_PATTERNS = [
        r"\b(PWA|PWA\.Market|GitHub Pages|Cloudflare|Vercel|Netlify|Carrd|Webflow|landing|лендинг|прокладка|pre-lander|прелендер)\b",
    ]
    TOOL_PATTERNS = [
        r"\b(freqtrade|trading bot|telegram bot|scraper|parser|automation|docker|compose|cloaking|keitaro|binom|voluum|redtrack)\b",
    ]

    def __init__(self, knowledge_source: KnowledgeSource):
        self.ks = knowledge_source

    def extract_entities(self, findings: List[Dict[str, Any]]) -> Dict[str, List[Entity]]:
        """Извлечь сущности из находок."""
        entities_by_type = defaultdict(list)
        seen = set()

        for finding in findings:
            content = finding.get("content", "")
            tags = finding.get("tags", "")
            text = f"{content} {tags}".lower()
            source_id = finding.get("id", "")

            # Traffic
            for pattern in self.TRAFFIC_PATTERNS:
                for match in re.finditer(pattern, text, re.IGNORECASE):
                    name = match.group(1) if match.groups() else match.group(0)
                    key = f"traffic:{name.lower()}"
                    if key not in seen:
                        seen.add(key)
                        entities_by_type["traffic"].append(Entity(
                            type="traffic", name=name, source_ids=[source_id],
                            attributes={"tags": tags, "source": finding.get("source", "")},
                            confidence=0.8
                        ))

            # Offers
            for pattern in self.OFFER_PATTERNS:
                for match in re.finditer(pattern, text, re.IGNORECASE):
                    name = match.group(1) if match.groups() else match.group(0)
                    key = f"offer:{name.lower()}"
                    if key not in seen:
                        seen.add(key)
                        entities_by_type["offer"].append(Entity(
                            type="offer", name=name, source_ids=[source_id],
                            attributes={"tags": tags, "source": finding.get("source", "")},
                            confidence=0.8
                        ))

            # Payments
            for pattern in self.PAYMENT_PATTERNS:
                for match in re.finditer(pattern, text, re.IGNORECASE):
                    name = match.group(1) if match.groups() else match.group(0)
                    key = f"payment:{name.lower()}"
                    if key not in seen:
                        seen.add(key)
                        entities_by_type["payment"].append(Entity(
                            type="payment", name=name, source_ids=[source_id],
                            attributes={"tags": tags, "source": finding.get("source", "")},
                            confidence=0.8
                        ))

            # Withdrawal
            for pattern in self.WITHDRAWAL_PATTERNS:
                for match in re.finditer(pattern, text, re.IGNORECASE):
                    name = match.group(1) if match.groups() else match.group(0)
                    key = f"withdrawal:{name.lower()}"
                    if key not in seen:
                        seen.add(key)
                        entities_by_type["withdrawal"].append(Entity(
                            type="withdrawal", name=name, source_ids=[source_id],
                            attributes={"tags": tags, "source": finding.get("source", "")},
                            confidence=0.7
                        ))

            # Geo
            for pattern in self.GEO_PATTERNS:
                for match in re.finditer(pattern, text, re.IGNORECASE):
                    name = match.group(1) if match.groups() else match.group(0)
                    key = f"geo:{name.lower()}"
                    if key not in seen:
                        seen.add(key)
                        entities_by_type["geo"].append(Entity(
                            type="geo", name=name, source_ids=[source_id],
                            attributes={"tags": tags, "source": finding.get("source", "")},
                            confidence=0.9
                        ))

            # Bridge
            for pattern in self.BRIDGE_PATTERNS:
                for match in re.finditer(pattern, text, re.IGNORECASE):
                    name = match.group(1) if match.groups() else match.group(0)
                    key = f"bridge:{name.lower()}"
                    if key not in seen:
                        seen.add(key)
                        entities_by_type["bridge"].append(Entity(
                            type="bridge", name=name, source_ids=[source_id],
                            attributes={"tags": tags, "source": finding.get("source", "")},
                            confidence=0.8
                        ))

            # Tools
            for pattern in self.TOOL_PATTERNS:
                for match in re.finditer(pattern, text, re.IGNORECASE):
                    name = match.group(1) if match.groups() else match.group(0)
                    key = f"tool:{name.lower()}"
                    if key not in seen:
                        seen.add(key)
                        entities_by_type["tool"].append(Entity(
                            type="tool", name=name, source_ids=[source_id],
                            attributes={"tags": tags, "source": finding.get("source", "")},
                            confidence=0.7
                        ))

        # Deduplicate by name within each type
        for etype, entities in entities_by_type.items():
            unique = {}
            for e in entities:
                if e.name.lower() not in unique:
                    unique[e.name.lower()] = e
                else:
                    # Merge source_ids
                    unique[e.name.lower()].source_ids.extend(e.source_ids)
            entities_by_type[etype] = list(unique.values())

        return dict(entities_by_type)

    def check_compatibility(self, e1: Entity, e2: Entity) -> float:
        """Проверить совместимость двух сущностей (0-1)."""
        # Комбинации, которые точно работают (ключи - отсортированные кортежи типов)
        known_good = {
            ("offer", "traffic"): {
                ("1xbet", "tiktok"): 0.9,
                ("1xbet", "youtube shorts"): 0.9,
                ("1win", "tiktok"): 0.9,
                ("1win", "youtube shorts"): 0.9,
                ("cpagrip", "push"): 0.85,
                ("nutra", "native"): 0.8,
                ("gambling", "pop"): 0.75,
                ("cpa", "telegram mini apps"): 0.85,
                # Added based on actual entities
                ("cpagrip", "tiktok"): 0.7,
                ("cpagrip", "youtube shorts"): 0.7,
                ("cpagrip", "mini-apps"): 0.75,
                ("cpa", "youtube shorts"): 0.7,
                ("cpa", "tiktok"): 0.7,
                ("cpl", "telegram mini apps"): 0.75,
            },
            ("offer", "payment"): {
                ("1xbet", "usdt"): 0.95,
                ("1win", "usdt"): 0.95,
                ("cpagrip", "usdt"): 0.9,
                ("binance", "cpagrip"): 0.8,
                ("usdt", "cpa"): 0.85,
                ("usdt", "cpl"): 0.85,
                ("usdt", "revenue share"): 0.8,
            },
            ("payment", "withdrawal"): {
                ("p2p", "usdt"): 0.95,
                ("t-bank", "usdt"): 0.9,
                ("card", "crypto"): 0.85,
                ("вывод", "binance"): 0.8,
                ("вывод", "bybit"): 0.8,
                ("вывод", "kucoin"): 0.8,
                ("вывод", "okx"): 0.8,
            },
            ("bridge", "traffic"): {
                ("pwa", "tiktok"): 0.9,
                ("pwa", "youtube shorts"): 0.9,
                ("landing", "push"): 0.8,
                # Added based on actual entities
                ("carrd", "tiktok"): 0.85,
                ("carrd", "youtube shorts"): 0.85,
                ("landing", "youtube shorts"): 0.85,
                ("github pages", "mini-apps"): 0.9,
                ("landing", "mini-apps"): 0.85,
                ("carrd", "telegram mini apps"): 0.8,
                ("landing", "telegram mini apps"): 0.8,
            },
            ("geo", "offer"): {
                ("india", "1xbet"): 0.9,
                ("india", "1win"): 0.9,
                ("global", "cpagrip"): 0.85,
                ("ru", "cpagrip"): 0.8,
                ("ru", "cpa"): 0.85,
                ("ru", "cpl"): 0.85,
                ("ru", "revenue share"): 0.8,
            },
            ("geo", "traffic"): {
                ("ru", "tiktok"): 0.7,
                ("ru", "youtube shorts"): 0.7,
                ("ru", "mini-apps"): 0.8,
                ("ru", "telegram mini apps"): 0.85,
            },
            ("bridge", "geo"): {
                ("ru", "carrd"): 0.7,
                ("ru", "landing"): 0.7,
                ("ru", "github pages"): 0.7,
                ("ru", "webflow"): 0.7,
            },
        }

        pair_type = tuple(sorted([e1.type, e2.type]))
        if pair_type in known_good:
            pair = tuple(sorted([e1.name.lower(), e2.name.lower()]))
            if pair in known_good[pair_type]:
                return known_good[pair_type][pair]

        # Эвристика: если типы совместимы по логике (используем frozenset для независимости от порядка)
        compatible_pairs = {
            frozenset(["traffic", "offer"]), frozenset(["offer", "payment"]), frozenset(["payment", "withdrawal"]),
            frozenset(["traffic", "bridge"]), frozenset(["offer", "geo"]), frozenset(["bridge", "geo"]),
            frozenset(["tool", "traffic"]), frozenset(["tool", "offer"]), frozenset(["tool", "payment"]),
        }
        if frozenset([e1.type, e2.type]) in compatible_pairs:
            return 0.6

        return 0.3  # Нейтрально


    def group_by_compatibility(self, entities: Dict[str, List[Entity]]) -> List[Dict[str, Any]]:
        """Сгруппировать сущности по совместимости."""
        groups = []

        # Основной паттерн: Traffic + Bridge + Offer + Payment + Withdrawal + Geo
        for traffic in entities.get("traffic", []):
            for bridge in entities.get("bridge", []):
                for offer in entities.get("offer", []):
                    for geo in entities.get("geo", []):
                        for payment in entities.get("payment", []):
                            for withdrawal in entities.get("withdrawal", []):

                                # Проверяем совместимость
                                scores = []
                                for e1, e2 in [
                                    (traffic, bridge), (traffic, offer),
                                    (offer, payment), (payment, withdrawal),
                                    (offer, geo), (traffic, geo),
                                ]:
                                    scores.append(self.check_compatibility(e1, e2))

                                avg_score = sum(scores) / len(scores) if scores else 0

                                if avg_score >= 0.5:  # Порог совместимости
                                    groups.append({
                                        "traffic": traffic,
                                        "bridge": bridge,
                                        "offer": offer,
                                        "geo": geo,
                                        "payment": payment,
                                        "withdrawal": withdrawal,
                                        "compatibility": avg_score,
                                    })

        # Сортируем по совместимости
        groups.sort(key=lambda x: x["compatibility"], reverse=True)
        return groups

    def find_novel_keys(self, groups: List[Dict[str, Any]], existing_keys: List[str]) -> List[SynthesizedKey]:
        """Найти НОВЫЕ ключи которых не было в матрице."""
        novel_keys = []

        for g in groups[:20]:  # Топ-20 групп
            # Формируем имя ключа
            key_name = f"{g['traffic'].name} → {g['bridge'].name} → {g['offer'].name} ({g['geo'].name})"

            # Проверяем новизну: не было ли уже такого сочетания
            is_novel = True
            for existing in existing_keys:
                if self._keys_similar(key_name, existing):
                    is_novel = False
                    break

            if not is_novel:
                continue

            # Вычисляем novelty score
            novelty = self._calculate_novelty(g)

            # Только если достаточно новаторский
            if novelty >= 0.5:
                reasoning = self._build_reasoning(g)
                novel_keys.append(SynthesizedKey(
                    name=key_name,
                    description=f"Синтезированная связка: {g['traffic'].name} трафик через {g['bridge'].name} на оффер {g['offer'].name} в {g['geo'].name}. Оплата: {g['payment'].name}, вывод: {g['withdrawal'].name}.",
                    components={
                        "traffic": [g["traffic"]],
                        "bridge": [g["bridge"]],
                        "offer": [g["offer"]],
                        "geo": [g["geo"]],
                        "payment": [g["payment"]],
                        "withdrawal": [g["withdrawal"]],
                    },
                    compatibility_score=g["compatibility"],
                    novelty_score=novelty,
                    reasoning=reasoning,
                    source_findings=[f"{e.type}:{e.name}" for e in g.values() if isinstance(e, Entity)]
                ))

        # Сортируем по произведению compatibility * novelty
        novel_keys.sort(key=lambda k: k.compatibility_score * k.novelty_score, reverse=True)
        return novel_keys

    def _keys_similar(self, key1: str, key2: str) -> bool:
        """Проверить похожесть ключей."""
        k1 = key1.lower()
        k2 = key2.lower()
        # Простая эвристика: если все основные компоненты совпадают
        words1 = set(re.findall(r'\b\w+\b', k1))
        words2 = set(re.findall(r'\b\w+\b', k2))
        if len(words1) == 0 or len(words2) == 0:
            return False
        overlap = len(words1 & words2) / max(len(words1), len(words2))
        return overlap > 0.7

    def _calculate_novelty(self, group: Dict[str, Any]) -> float:
        """Рассчитать новизну комбинации."""
        # Чем больше уникальных источников, тем новее
        source_ids = set()
        for e in group.values():
            if isinstance(e, Entity):
                source_ids.update(e.source_ids)

        source_novelty = min(len(source_ids) / 10, 1.0)

        # Бонус за редкие комбинации
        rare_bonus = 0
        for e in group.values():
            if isinstance(e, Entity) and e.confidence < 0.8:
                rare_bonus += 0.1

        return min(source_novelty + rare_bonus, 1.0)

    def _build_reasoning(self, group: Dict[str, Any]) -> str:
        """Построить рассуждение для ключа."""
        parts = []
        parts.append(f"Трафик {group['traffic'].name} совместим с прокладкой {group['bridge'].name} (score: {self.check_compatibility(group['traffic'], group['bridge']):.0%})")
        parts.append(f"Оффер {group['offer'].name} работает в {group['geo'].name} (score: {self.check_compatibility(group['offer'], group['geo']):.0%})")
        parts.append(f"Платёж {group['payment'].name} → вывод {group['withdrawal'].name} (score: {self.check_compatibility(group['payment'], group['withdrawal']):.0%})")
        return ". ".join(parts)

    def run_synthesis(self, days: int = 7) -> List[SynthesizedKey]:
        """Запустить полный цикл синтеза."""
        logger.info(f"Starting synthesis from last {days} days...")

        # 1. Получить недавние находки
        findings = self.ks.get_recent_findings(days)
        logger.info(f"Found {len(findings)} recent findings")

        if not findings:
            logger.warning("No recent findings to synthesize")
            return []

        # 2. Извлечь сущности
        entities = self.extract_entities(findings)
        logger.info(f"Extracted entities: { {k: len(v) for k, v in entities.items()} }")

        # 3. Сгруппировать по совместимости
        groups = self.group_by_compatibility(entities)
        logger.info(f"Found {len(groups)} compatible groups")

        # 4. Получить существующие ключи (из базы или из колес)
        existing_keys = self._get_existing_keys()

        # 5. Найти новые ключи
        novel_keys = self.find_novel_keys(groups, existing_keys)
        logger.info(f"Synthesized {len(novel_keys)} novel keys")

        return novel_keys

    def _get_existing_keys(self) -> List[str]:
        """Получить список существующих ключей (связок)."""
        keys = []
        try:
            conn = sqlite3.connect(str(self.ks.cube_path))
            cursor = conn.cursor()

            # Из kc_entries - ищем уже документированные связки
            cursor.execute("""
                SELECT content FROM kc_entries
                WHERE content LIKE '%→%' OR content LIKE '%->%' OR content LIKE '%связк%'
            """)
            for row in cursor.fetchall():
                keys.append(row[0][:200])

            # Из experiences
            cursor.execute("""
                SELECT content FROM experiences
                WHERE content LIKE '%→%' OR content LIKE '%->%' OR content LIKE '%связк%'
            """)
            for row in cursor.fetchall():
                keys.append(row[0][:200])

            conn.close()
        except Exception as e:
            logger.warning(f"Failed to get existing keys: {e}")

        return keys




# =============================================================================
# EULER CIRCLES ENGINE — Mode 3: Золотые Сечения (пересечения кругов)
# =============================================================================

@dataclass
class EulerCircle:
    """Один круг Эйлера — аспект темы."""
    id: str
    name: str
    fill_percent: int
    status: str  # 🟢 🟡 🔴
    weight: float = 1.0
    critical: bool = False
    facts: List[str] = field(default_factory=list)
    gaps: List[str] = field(default_factory=list)
    
    @property
    def radius(self) -> float:
        """Радиус круга = важность (weight) * заполненность."""
        return self.weight * (self.fill_percent / 100.0)
    
    @property
    def area(self) -> float:
        """Площадь круга."""
        return math.pi * (self.radius ** 2)
    
    @property
    def color(self) -> str:
        return {"🟢": "#238636", "🟡": "#d29922", "🔴": "#f85149"}[self.status]


@dataclass
class Intersection:
    """Пересечение двух или более кругов."""
    circle_ids: List[str]
    circle_names: List[str]
    intersection_type: str  # "green", "red", "conflict", "mixed"
    strength: float  # 0-1
    description: str
    action: str
    sectors: List[Sector] = field(default_factory=list)
    # Bayesian fields
    p_success: float = 0.0  # P(success | evidence)
    p_success_given_green: float = 0.0  # P(success | all green)
    p_success_given_red: float = 0.0  # P(success | has red)
    evidence: Dict[str, float] = field(default_factory=dict)  # supporting evidence factors
    prior: float = 0.5  # base rate


@dataclass
class BayesianEstimator:
    """Байесовский оценщик вероятности успеха для пересечений."""
    
    # Базовые частоты успеха (можно калибровать из исторических данных)
    base_rates: Dict[str, float] = field(default_factory=lambda: {
        "golden": 0.85,        # 2+ зелёных = высокая вероятность
        "golden_core": 0.92,   # 3 зелёных = очень высокая
        "system_core": 0.95,   # 4+ зелёных = почти гарантированно
        "red": 0.15,           # 2+ красных = низкая вероятность
        "core_conflict": 0.25, # 2 зелёных + 1 красный = блокер
        "isolated_strength": 0.35,  # 1 зелёный + 2 красных = изолированная сила
        "conflict": 0.40,      # зелёный + красный/жёлтый = зависит от красного
        "growth": 0.55,        # 2 жёлтых = средняя, есть потенциал
        "mixed": 0.35,         # жёлтый + красный = неопределенность
    })
    
    # Likelihood ratios для эвристических факторов
    likelihood_factors: Dict[str, float] = field(default_factory=lambda: {
        "all_critical_green": 2.5,      # все критические зелёные
        "has_critical_red": 0.3,        # есть критические красные
        "high_weight_green": 1.8,       # зелёные с высоким weight
        "low_fill_green": 0.7,          # зелёные с низким fill (<70%)
        "known_compatible_pair": 2.0,   # пара из known_good
        "no_historical_data": 0.8,      # нет исторических данных
        "previous_success": 3.0,        # была история успеха
        "previous_failure": 0.2,        # была история неудачи
    })
    
    def estimate(self, inter: Intersection, sector_map: Dict[str, Sector] = None) -> Intersection:
        """Вычислить байесовскую оценку P(success | evidence)."""
        # Prior из базовой частоты для типа пересечения
        prior = self.base_rates.get(inter.intersection_type, 0.5)
        
        # Собираем evidence факторы
        evidence = {}
        likelihood_ratio = 1.0
        
        # Получаем круги для анализа
        circles_data = []
        if sector_map:
            circles_data = [sector_map[cid] for cid in inter.circle_ids if cid in sector_map]
        else:
            # fallback к strength
            circles_data = []
        
        # Фактор 1: все ли критические зелёные
        critical_green = [c for c in circles_data if c.critical and c.status == "🟢"]
        critical_red = [c for c in circles_data if c.critical and c.status == "🔴"]
        if critical_green and not critical_red:
            evidence["all_critical_green"] = len(critical_green)
            likelihood_ratio *= self.likelihood_factors["all_critical_green"] ** len(critical_green)
        elif critical_red:
            evidence["has_critical_red"] = len(critical_red)
            likelihood_ratio *= self.likelihood_factors["has_critical_red"] ** len(critical_red)
        
        # Фактор 2: высокий weight у зелёных
        high_weight_green = [c for c in circles_data if c.status == "🟢" and c.weight >= 1.2]
        if high_weight_green:
            evidence["high_weight_green"] = len(high_weight_green)
            likelihood_ratio *= self.likelihood_factors["high_weight_green"] ** len(high_weight_green)
        
        # Фактор 3: зелёные с низким fill (<70%)
        low_fill_green = [c for c in circles_data if c.status == "🟢" and c.fill_percent < 70]
        if low_fill_green:
            evidence["low_fill_green"] = len(low_fill_green)
            likelihood_ratio *= self.likelihood_factors["low_fill_green"] ** len(low_fill_green)
        
        # Фактор 4: известная совместимая пара
        if len(inter.circle_ids) == 2:
            pair_key = frozenset(inter.circle_ids)
            # Проверяем в known_good (из SynthesisEngine)
            evidence["pair_checked"] = 1.0
        
        # Фактор 5: сила пересечения (strength уже учитывает fill_percent)
        evidence["intersection_strength"] = inter.strength
        
        # Байесовское обновление: posterior = prior * LR / (prior * LR + (1-prior))
        # В log-odds для устойчивости:
        # log(posterior/(1-posterior)) = log(prior/(1-prior)) + log(LR)
        prior_odds = prior / (1 - prior) if prior < 1 else 100
        post_odds = prior_odds * likelihood_ratio
        posterior = post_odds / (1 + post_odds)
        
        # Ограничиваем разумными пределами
        posterior = max(0.05, min(0.99, posterior))
        
        # Обновляем пересечение
        inter.prior = prior
        inter.p_success = posterior
        inter.evidence = evidence
        
        # Дополнительные специфичные оценки
        inter.p_success_given_green = self._estimate_given_green(inter, circles_data)
        inter.p_success_given_red = self._estimate_given_red(inter, circles_data)
        
        return inter
    
    def _estimate_given_green(self, inter: Intersection, circles_data: List[Sector]) -> float:
        """P(success | все зелёные в пересечении)."""
        green_circles = [c for c in circles_data if c.status == "🟢"]
        if not green_circles:
            return 0.0
        avg_fill = sum(c.fill_percent for c in green_circles) / len(green_circles)
        # Линейная интерполяция: 80% fill -> 0.85, 100% -> 0.95
        return 0.5 + (avg_fill / 100.0) * 0.45
    
    def _estimate_given_red(self, inter: Intersection, circles_data: List[Sector]) -> float:
        """P(success | есть красные в пересечении)."""
        red_circles = [c for c in circles_data if c.status == "🔴"]
        if not red_circles:
            return inter.p_success
        # Чем больше красных и чем ниже их fill, тем хуже
        avg_fill = sum(c.fill_percent for c in red_circles) / len(red_circles)
        critical_count = sum(1 for c in red_circles if c.critical)
        base = 0.3 + (avg_fill / 100.0) * 0.3  # 0.3-0.6
        penalty = 0.15 * critical_count  # штраф за критические
        return max(0.05, min(0.6, base - penalty))


class EulerCirclesEngine:
    """
    Двигатель Кругов Эйлера + Колеса Баланса = Поиск Золотого Сечения.
    
    Каждый аспект = круг Эйлера (цвет = заполненность, размер = важность).
    Пересечения кругов = сильные/слабые зоны.
    Золотые сечения = пересечения зелёных кругов (готовые связки).
    """
    
    def __init__(self, sectors: List[Sector]):
        self.circles = self._build_circles(sectors)
        self.intersections: List[Intersection] = []
    
    def _build_circles(self, sectors: List[Sector]) -> List[EulerCircle]:
        """Создать круги Эйлера из секторов."""
        circles = []
        for sector in sectors:
            circle = EulerCircle(
                id=sector.id,
                name=sector.name,
                fill_percent=sector.fill_percent,
                status=sector.status,
                weight=sector.weight,
                critical=sector.critical,
                facts=sector.facts,
                gaps=sector.gaps,
            )
            circles.append(circle)
        return circles
    
    def find_all_intersections(self) -> List[Intersection]:
        """Найти все пересечения между кругами."""
        intersections = []

        # Пересечения пар кругов
        for i, c1 in enumerate(self.circles):
            for c2 in self.circles[i+1:]:
                inter = self._analyze_pair(c1, c2)
                if inter:
                    intersections.append(inter)

        # Пересечения троек кругов (самые ценные — Золотые Сечения)
        if len(self.circles) >= 3:
            for combo in itertools.combinations(self.circles, 3):
                inter = self._analyze_triple(combo)
                if inter:
                    intersections.append(inter)

        # Пересечения 4+ кругов (ядро системы)
        if len(self.circles) >= 4:
            core_green = [c for c in self.circles if c.status == "🟢"]
            if len(core_green) >= 4:
                inter = self._analyze_core(core_green)
                if inter:
                    intersections.append(inter)

        self.intersections = intersections

        # Apply Bayesian estimation
        self._apply_bayesian_estimation()

        return intersections

    def _apply_bayesian_estimation(self):
            """Применить байесовскую оценку ко всем пересечениям."""
            # Строим маппинг id -> circle для доступа к weight, critical, gaps
            sector_map = {}
            for circle in self.circles:
                sector_map[circle.id] = circle

            estimator = BayesianEstimator()
            for inter in self.intersections:
                estimator.estimate(inter, sector_map)
        
    def _analyze_pair(self, c1: EulerCircle, c2: EulerCircle) -> Optional[Intersection]:
        """Анализ пересечения двух кругов."""
        s1, s2 = c1.status, c2.status
        
        # ЗОЛОТОЕ СЕЧЕНИЕ: два зелёных круга
        if s1 == "🟢" and s2 == "🟢":
            strength = (c1.fill_percent + c2.fill_percent) / 200.0
            return Intersection(
                circle_ids=[c1.id, c2.id],
                circle_names=[c1.name, c2.name],
                intersection_type="golden",
                strength=strength,
                description=f"Пересечение {c1.name} ({c1.fill_percent}%) ∩ {c2.name} ({c2.fill_percent}%) — ЗОЛОТОЕ СЕЧЕНИЕ. Оба аспекта готовы к работе.",
                action=f"МОЖНО ЗАПУСКАТЬ: Используй {c1.name} + {c2.name} как основу для новых связок. Масштабируй на другие офферы/гео.",
                sectors=[]
            )
        
        # КРАСНОЕ ПЕРЕСЕЧЕНИЕ: два красных круга
        elif s1 == "🔴" and s2 == "🔴":
            strength = 1.0 - (c1.fill_percent + c2.fill_percent) / 200.0
            critical = c1.critical or c2.critical
            return Intersection(
                circle_ids=[c1.id, c2.id],
                circle_names=[c1.name, c2.name],
                intersection_type="red",
                strength=strength,
                description=f"Пересечение {c1.name} ({c1.fill_percent}%) ∩ {c2.name} ({c2.fill_percent}%) — КРИТИЧЕСКИЙ ПРОБЕЛ. Оба аспекта требуют срочной работы.",
                action=f"НЕМЕДЛЕННО ИСПРАВИТЬ: {c1.name} — {c1.gaps[:2] if c1.gaps else 'нет данных'}; {c2.name} — {c2.gaps[:2] if c2.gaps else 'нет данных'}." + (" [КРИТИЧНО]" if critical else ""),
                sectors=[]
            )
        
        # КОНФЛИКТ: зелёный + красный
        elif (s1 == "🟢" and s2 == "🔴") or (s1 == "🔴" and s2 == "🟢"):
            green = c1 if s1 == "🟢" else c2
            red = c2 if s1 == "🟢" else c1
            return Intersection(
                circle_ids=[green.id, red.id],
                circle_names=[green.name, red.name],
                intersection_type="conflict",
                strength=green.fill_percent / 100.0,
                description=f"КРИТИЧЕСКИЙ КОНФЛИКТ: {green.name} ({green.fill_percent}%) готов, но {red.name} ({red.fill_percent}%) — полный пробел. {green.name} СЛИВАЕТСЯ ВПУСТУЮ!",
                action=f"СРОЧНО ЗАКРЫТЬ {red.name}: {red.gaps[:2] if red.gaps else 'нет данных'}. Без этого {green.name} бесполезен." + (" [БЛОКИРУЕТ ЗАПУСК]" if red.critical else ""),
                sectors=[]
            )
        
        # КОНФЛИКТ: зелёный + жёлтый
        elif (s1 == "🟢" and s2 == "🟡") or (s1 == "🟡" and s2 == "🟢"):
            green = c1 if s1 == "🟢" else c2
            yellow = c2 if s1 == "🟢" else c1
            return Intersection(
                circle_ids=[green.id, yellow.id],
                circle_names=[green.name, yellow.name],
                intersection_type="conflict",
                strength=green.fill_percent / 100.0,
                description=f"КОНФЛИКТ: {green.name} ({green.fill_percent}%) готов, но {yellow.name} ({yellow.fill_percent}%) недоделан. Ресурс есть, но не используется эффективно.",
                action=f"ДОРАБОТАТЬ {yellow.name}: {yellow.gaps[:2] if yellow.gaps else 'нет данных'}. Это разблокирует {green.name}.",
                sectors=[]
            )
        
        # ЗОНА РОСТА: два жёлтых круга
        elif s1 == "🟡" and s2 == "🟡":
            strength = (c1.fill_percent + c2.fill_percent) / 200.0
            return Intersection(
                circle_ids=[c1.id, c2.id],
                circle_names=[c1.name, c2.name],
                intersection_type="growth",
                strength=strength,
                description=f"ЗОНА РОСТА: {c1.name} ({c1.fill_percent}%) и {c2.name} ({c2.fill_percent}%) — оба требуют доделки. Потенциал есть, нужны усилия.",
                action=f"ПАРАЛЛЕЛЬНАЯ РАБОТА: дойди до 80% в обоих. {c1.name}: {c1.gaps[:1] if c1.gaps else ''}; {c2.name}: {c2.gaps[:1] if c2.gaps else ''}.",
                sectors=[]
            )
        
        # СМЕШАННАЯ ЗОНА: жёлтый + красный
        else:
            return Intersection(
                circle_ids=[c1.id, c2.id],
                circle_names=[c1.name, c2.name],
                intersection_type="mixed",
                strength=0.3,
                description=f"СМЕШАННАЯ ЗОНА: {c1.name} ({c1.status} {c1.fill_percent}%) и {c2.name} ({c2.status} {c2.fill_percent}%). Требует понимания приоритетов.",
                action=f"ОЦЕНИТЬ: какой аспект важнее (weight: {c1.weight} vs {c2.weight}) и фокус на нём.",
                sectors=[]
            )

    def _analyze_triple(self, circles: Tuple[EulerCircle, ...]) -> Optional[Intersection]:
        """Анализ пересечения трёх кругов — поиск Золотых Сечений."""
        statuses = [c.status for c in circles]
        names = [c.name for c in circles]
        ids = [c.id for c in circles]
        
        if all(s == "🟢" for s in statuses):
            # ИДЕАЛЬНОЕ ЗОЛОТОЕ СЕЧЕНИЕ: 3 зелёных круга
            avg_fill = sum(c.fill_percent for c in circles) / 3
            return Intersection(
                circle_ids=ids,
                circle_names=names,
                intersection_type="golden_core",
                strength=avg_fill / 100.0,
                description=f"⭐ ЗОЛОТОЕ СЕЧЕНИЕ ЯДРА: {' ∩ '.join([f'{n} ({c.fill_percent}%)' for n, c in zip(names, circles)])}. Три готовных аспекта — база для мгновенного запуска связок.",
                action=f"ЗАПУСТИТЬ СЕЙЧАС: комбинируй {names[0]} + {names[1]} + {names[2]} для новых офферов/гео. Это твоя новая матрица готовности.",
                sectors=[]
            )
        elif statuses.count("🟢") == 2 and statuses.count("🔴") == 1:
            # 2 зелёных + 1 красный = конфликт ядра
            green_names = [c.name for c in circles if c.status == "🟢"]
            red = [c for c in circles if c.status == "🔴"][0]
            return Intersection(
                circle_ids=ids,
                circle_names=names,
                intersection_type="core_conflict",
                strength=0.7,
                description=f"КОНФЛИКТ ЯДРА: {' и '.join(green_names)} готовы, но {red.name} ({red.fill_percent}%) блокирует. Два ресурса простаивают из-за одного пробела.",
                action=f"ПРИОРИТЕТ №1: закрой {red.name}. {red.gaps[:2] if red.gaps else 'нет данных'}. После этого ядро {green_names[0]}+{green_names[1]} включится.",
                sectors=[]
            )
        elif statuses.count("🟢") == 1 and statuses.count("🔴") == 2:
            # 1 зелёный + 2 красных = изолированная сила
            green = [c for c in circles if c.status == "🟢"][0]
            red_names = [c.name for c in circles if c.status == "🔴"]
            return Intersection(
                circle_ids=ids,
                circle_names=names,
                intersection_type="isolated_strength",
                strength=0.4,
                description=f"ИЗОЛИРОВАННАЯ СИЛА: {green.name} ({green.fill_percent}%) готов, но окружён пробелами: {', '.join(red_names)}. Ресурс не может реализоваться.",
                action=f"ВЫБЕРИ ОДИН: либо замкни {red_names[0]} либо {red_names[1]} (тот, у кого weight выше). Остальное — потом.",
                sectors=[]
            )
        return None
    
    def _analyze_core(self, green_circles: List[EulerCircle]) -> Optional[Intersection]:
        """Анализ ядра системы (4+ зелёных кругов)."""
        names = [c.name for c in green_circles]
        ids = [c.id for c in green_circles]
        avg_fill = sum(c.fill_percent for c in green_circles) / len(green_circles)
        
        return Intersection(
            circle_ids=ids,
            circle_names=names,
            intersection_type="system_core",
            strength=avg_fill / 100.0,
            description=f"⭐⭐⭐ СИСТЕМНОЕ ЯДРО: {len(green_circles)} зелёных аспектов ({', '.join([f'{n} ({c.fill_percent}%)' for n, c in zip(names, green_circles)])}). Это твоя платформа — можно строить любые связки внутри этого ядра.",
            action=f"МАСШТАБИРУЙ: используй это ядро как фундамент. Любой новый оффер/гео, попавший в эти {len(green_circles)} зелёные круги, запускается за дни, не месяцы.",
            sectors=[]
        )
    
    def get_golden_sections(self) -> List[Intersection]:
        """Получить все Золотые Сечения (пересечения зелёных)."""
        return [i for i in self.intersections if i.intersection_type in ("golden", "golden_core", "system_core")]
    
    def get_critical_gaps(self) -> List[Intersection]:
        """Получить критические пробелы (пересечения красных)."""
        return [i for i in self.intersections if i.intersection_type in ("red", "core_conflict")]
    
    def get_conflicts(self) -> List[Intersection]:
        """Получить конфликты (зелёный + красный/жёлтый)."""
        return [i for i in self.intersections if i.intersection_type in ("conflict", "isolated_strength")]
    
    def get_growth_zones(self) -> List[Intersection]:
        """Получить зоны роста (жёлто-жёлтые)."""
        return [i for i in self.intersections if i.intersection_type == "growth"]
    
    def synthesize_from_green_intersections(self) -> List[str]:
            """
            Синтез новых ключей из пересечения зелёных кругов.
            Берём 2-3 зелёных круга → их пересечение = новый ключ.
            """
            golden = self.get_golden_sections()
            new_keys = []

            for inter in golden:
                if len(inter.circle_ids) >= 2:
                    # Формируем новый ключ из пересечения
                    key_name = " + ".join(inter.circle_names)
                    new_keys.append({
                        "name": key_name,
                        "source_intersection": inter.intersection_type,
                        "strength": inter.strength,
                        "description": f"Новый ключ из пересечения: {key_name}. Сила: {inter.strength:.0%}",
                        "action": f"Используй {key_name} как готовую связку для новых офферов/гео.",
                    })

            return new_keys



# =============================================================================
# KEY STRENGTH ASSESSMENT — Оценка силы самого ключа (гипотезы)
# =============================================================================

@dataclass
class KeyStrength:
    """Оценка силы ключа (гипотезы) — НЕ аспектов, а самого ключа."""
    key_name: str
    viability: float          # Жизнеспособность: спрос, барьер, маржа
    cohesion: float           # Связанность: насколько аспекты блокируют друг друга
    growth_potential: float   # Потенциал роста: потолок дохода
    key_strength: float       # Итоговая оценка
    
    # Детализация для отладки/объяснения
    viability_details: Dict[str, float] = field(default_factory=dict)
    cohesion_details: Dict[str, Any] = field(default_factory=dict)
    growth_details: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "key_name": self.key_name,
            "viability": round(self.viability, 3),
            "cohesion": round(self.cohesion, 3),
            "growth_potential": round(self.growth_potential, 3),
            "key_strength": round(self.key_strength, 3),
            "viability_details": self.viability_details,
            "cohesion_details": self.cohesion_details,
            "growth_details": self.growth_details,
        }


class KeyStrengthEstimator:
    """
    Оценщик силы ключа.
    
    Ключ — это гипотеза, а не сумма аспектов. Оцениваем:
    1. Viability — жизнеспособность ключа (рыночный спрос, барьер входа, маржа)
    2. Cohesion — связанность аспектов (насколько красные блокируют зелёные)
    3. Growth Potential — потолок масштабирования
    
    Key Strength = Viability×0.4 + Cohesion×0.3 + Growth×0.3
    """
    
    # Доменные профили для оценки viability
    DOMAIN_VIABILITY: Dict[str, Dict[str, float]] = {
        "arbitrage": {
            "market_demand": 0.75,    # Рынок арбитража активен
            "entry_barrier": 0.55,    # Средний барьер (прокси, аккаунты, бюджет)
            "margin_potential": 0.70, # Хорошая маржа при успехе
        },
        "ai-ofm": {
            "market_demand": 0.85,    # Рынок взрывной
            "entry_barrier": 0.30,    # Низкий барьер (инструменты доступны)
            "margin_potential": 0.80, # Очень высокая маржа
        },
        "craft": {
            "market_demand": 0.65,    # Нишевый рынок
            "entry_barrier": 0.60,    # Производство требует ресурсов
            "margin_potential": 0.55, # Умеренная маржа
        },
        "default": {
            "market_demand": 0.50,
            "entry_barrier": 0.50,
            "margin_potential": 0.50,
        }
    }
    
    # Оценки потенциала роста по типам ключей (в $/мес максимум)
    KEY_TYPE_GROWTH_CEILING: Dict[str, float] = {
        "pwa betting": 10000,
        "youtube shorts": 5000,
        "tiktok": 8000,
        "cpa content lock": 3000,
        "telegram mini app": 15000,
        "native ads": 12000,
        "push traffic": 8000,
        "email marketing": 5000,
        "seo": 3000,
        "default": 2000,
    }
    
    def __init__(self, domain: str = "arbitrage"):
        self.domain = domain
        self.viability_profile = self.DOMAIN_VIABILITY.get(domain, self.DOMAIN_VIABILITY["default"])
    
    def estimate(self, 
                 key_name: str, 
                 sectors: List[Sector],
                 intersections: List[Intersection] = None) -> KeyStrength:
        """Оценить силу ключа."""
        
        # 1. Viability — жизнеспособность ключа
        viability = self._estimate_viability(key_name)
        
        # 2. Cohesion — связанность аспектов
        cohesion = self._estimate_cohesion(key_name, sectors, intersections)
        
        # 3. Growth Potential — потенциал роста
        growth = self._estimate_growth(key_name)
        
        # Итоговая сила ключа
        key_strength = (viability * 0.4) + (cohesion * 0.3) + (growth * 0.3)
        
        return KeyStrength(
            key_name=key_name,
            viability=viability,
            cohesion=cohesion,
            growth_potential=growth,
            key_strength=key_strength,
            viability_details=self._viability_details,
            cohesion_details=self._cohesion_details,
            growth_details=self._growth_details,
        )
    
    def _estimate_viability(self, key_name: str) -> float:
        """Жизнеспособность: спрос × 0.4 + (1 - барьер) × 0.3 + маржа × 0.3"""
        kl = key_name.lower()
        
        # Базовые значения из профиля домена
        demand = self.viability_profile["market_demand"]
        barrier = self.viability_profile["entry_barrier"]
        margin = self.viability_profile["margin_potential"]
        
        # Корректировки по ключу
        if "pwa" in kl or "progressive web" in kl:
            demand = max(demand, 0.7)
            barrier = min(barrier, 0.6)  # PWA = ниже барьер (нет аппстора)
        if "youtube shorts" in kl or "shorts" in kl:
            demand = max(demand, 0.8)
            barrier = min(barrier, 0.4)  # Shorts = бесплатный трафик
        if "tiktok" in kl:
            demand = max(demand, 0.85)
            barrier = min(barrier, 0.45)
        if "cpa" in kl or "content lock" in kl:
            demand = max(demand, 0.75)
            margin = max(margin, 0.75)
        if "telegram mini app" in kl or "mini app" in kl:
            demand = max(demand, 0.8)
            barrier = min(barrier, 0.5)
            margin = max(margin, 0.8)
        if "india" in kl or "индия" in kl:
            demand = max(demand, 0.8)  # Индия = огромный рынок
            barrier = max(barrier, 0.6)  # Но локальные сложности
        if "betting" in kl or "беттинг" in kl or "gambling" in kl:
            demand = max(demand, 0.85)
            margin = max(margin, 0.85)
            barrier = max(barrier, 0.7)  # Высокие риски блокировок
        
        self._viability_details = {
            "market_demand": demand,
            "entry_barrier": barrier,
            "margin_potential": margin,
            "formula": f"{demand:.2f}×0.4 + {1-barrier:.2f}×0.3 + {margin:.2f}×0.3",
        }
        
        return demand * 0.4 + (1 - barrier) * 0.3 + margin * 0.3
    
    def _estimate_cohesion(self, key_name: str, sectors: List[Sector], 
                               intersections: List[Intersection] = None) -> float:
            """
            Связанность: 1 - (красные аспекты блокирующие зелёные / всего аспектов)
        
            Аспект "блокирует" если он красный И есть зелёный аспект, с которым он в конфликте
            """
            # Считаем красные аспекты
            red_sectors = [s for s in sectors if s.status == "🔴"]
            green_sectors = [s for s in sectors if s.status == "🟢"]
            total_sectors = len(sectors)
        
            if total_sectors == 0:
                self._cohesion_details = {"note": "no sectors"}
                return 0.5
        
            # Если есть intersections, считаем конфликты
            blocking_red_ids = set()
            if intersections:
                green_ids = {s.id for s in green_sectors}
                red_ids = {s.id for s in red_sectors}
            
                for inter in intersections:
                    if inter.intersection_type == "conflict":
                        # Проверяем: зелёный + красный
                        inter_ids = set(inter.circle_ids)
                        if inter_ids & green_ids and inter_ids & red_ids:
                            # Добавляем только уникальные красные ID, которые реально блокируют
                            blocking_red_ids.update(inter_ids & red_ids)
        
            # Если intersections нет, считаем просто уникальные красные
            if not blocking_red_ids:
                blocking_red_ids = {s.id for s in red_sectors}
        
            blocking_red = len(blocking_red_ids)
            cohesion = max(0.0, 1.0 - (blocking_red / total_sectors))
        
            self._cohesion_details = {
                "total_sectors": total_sectors,
                "red_sectors": [s.name for s in red_sectors],
                "green_sectors": [s.name for s in green_sectors],
                "blocking_red": [s.name for s in sectors if s.id in blocking_red_ids],
                "blocking_red_count": blocking_red,
                "formula": f"1 - {blocking_red}/{total_sectors} = {cohesion:.2f}",
            }
        
            return cohesion
    
    def _estimate_growth(self, key_name: str) -> float:
        """
        Потенциал роста: логарифм потолка дохода, нормированный к 10k
        """
        kl = key_name.lower()
        
        # Ищем максимальный потолок среди известных типов
        max_ceiling = self.KEY_TYPE_GROWTH_CEILING["default"]
        for ktype, ceiling in self.KEY_TYPE_GROWTH_CEILING.items():
            if ktype in kl:
                max_ceiling = max(max_ceiling, ceiling)
        
        # Корректировки
        if "scale" in kl or "масштаб" in kl:
            max_ceiling *= 2
        if "auto" in kl or "авто" in kl:
            max_ceiling *= 1.5
        
        # Нормируем: log10(ceiling) / log10(10000) = log10(ceiling) / 4
        import math
        growth = min(1.0, math.log10(max(max_ceiling, 100)) / 4.0)
        
        self._growth_details = {
            "max_ceiling_usd": max_ceiling,
            "log10_ceiling": math.log10(max_ceiling),
            "normalized": growth,
            "formula": f"log10({max_ceiling}) / 4 = {growth:.2f}",
        }
        
        return growth
    
    def compare_keys(self, keys: List[str], sectors_map: Dict[str, List[Sector]],
                     intersections_map: Dict[str, List[Intersection]] = None) -> List[KeyStrength]:
        """Сравнить несколько ключей и вернуть отсортированный по силе список."""
        results = []
        for key_name in keys:
            sectors = sectors_map.get(key_name, [])
            intersections = intersections_map.get(key_name, []) if intersections_map else None
            ks = self.estimate(key_name, sectors, intersections)
            results.append(ks)
        
        results.sort(key=lambda x: x.key_strength, reverse=True)
        return results


class FractalWheel:
    """Главный класс фрактального колеса знаний."""

    def __init__(
        self,
        center: str,
        domain: str = "arbitrage",
        knowledge_source: Optional[KnowledgeSource] = None,
        output_dir: Path = Path("reports"),
    ):
        self.center = center
        self.domain = domain
        self.knowledge_source = knowledge_source or KnowledgeSource()
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Слаг для файлов
        self.slug = self._make_slug(center)

        # Двигатель синтеза
        self.synthesis_engine = SynthesisEngine(self.knowledge_source)

    def _make_slug(self, text: str) -> str:
        """Создать слаг для имени файла."""
        slug = re.sub(r'[^\w\s-]', '', text.lower())
        slug = re.sub(r'[\s-]+', '-', slug)
        return slug[:50]

    # =========================================================================
    # РЕЖИМ 1: Анализ (key → aspects → gaps → tasks)
    # =========================================================================

    def build_wheel(self) -> List[Sector]:
        """Создать секторную структуру для домена."""
        sectors_def = DOMAIN_SECTORS.get(self.domain, DOMAIN_SECTORS["default"])
        sectors = []
        for defn in sectors_def:
            sector = Sector(
                id=defn["id"],
                name=defn["name"],
                weight=defn.get("weight", 1.0),
                critical=defn.get("critical", False),
            )
            sectors.append(sector)
        logger.info(f"Built wheel for '{self.center}' with {len(sectors)} sectors")
        return sectors

    def assess_gaps(self, sectors: List[Sector]) -> List[Sector]:
        """Оценить заполненность каждого сектора (mock implementation)."""
        mock_data = {
            "traffic": {"fill": 85, "facts": ["TikTok", "YouTube Shorts", "UGC"], "gaps": []},
            "bridge": {"fill": 80, "facts": ["PWA.Market", "GitHub Pages", "Cloudflare"], "gaps": []},
            "offer": {"fill": 45, "facts": ["1xBet", "1win — есть цифры"], "gaps": ["Нет контактов менеджеров", "Неизвестны лимиты"]},
            "creatives": {"fill": 15, "facts": [], "gaps": ["КРИТИЧЕСКИЙ ПРОБЕЛ!", "Нет готовых креативов", "Нет тестов A/B"]},
            "payments": {"fill": 90, "facts": ["USDT", "P2P", "карты"], "gaps": []},
            "withdrawal": {"fill": 85, "facts": ["схема работает"], "gaps": []},
            "legal": {"fill": 40, "facts": ["общая инфа есть"], "gaps": ["нет конкретики по Индии", "неизвестны локальные законы"]},
            "scaling": {"fill": 10, "facts": [], "gaps": ["полный пробел", "нет авто-скейла", "нет команды"]},
        }

        for sector in sectors:
            data = mock_data.get(sector.id, {"fill": 0, "facts": [], "gaps": []})
            sector.fill_percent = data["fill"]
            sector.facts = data["facts"]
            sector.gaps = data["gaps"]
            sector.update_status()

        logger.info(f"Assessed gaps for '{self.center}'")
        return sectors

    def run_analysis_mode(self) -> WheelAssessment:
        """Режим 1: Анализ — разложить ключ на аспекты."""
        sectors = self.build_wheel()
        sectors = self.assess_gaps(sectors)

        assessment = WheelAssessment(
            center=self.center,
            domain=self.domain,
            sectors=sectors,
            overall_percent=sum(s.fill_percent for s in sectors) // len(sectors),
            slug=self.slug,
        )
        return assessment

    # =========================================================================
    # РЕЖИМ 2: Синтез (scattered findings → new keys)
    # =========================================================================

    def run_synthesis_mode(self, days: int = 7) -> List[SynthesizedKey]:
        """Режим 2: Синтез — из разрозненных находок собрать новые ключи."""
        return self.synthesis_engine.run_synthesis(days)

    # =========================================================================
    # Общий интерфейс
    # =========================================================================

    # =========================================================================
    # РЕЖИМ 3: Эйлеровы Круги + Колесо Баланса = Золотые Сечения
    # =========================================================================

    def run_euler_mode(self) -> Dict[str, Any]:
        """Режим 3: Эйлеровы Круги — анализ пересечений аспектов."""
        # Сначала запускаем анализ для получения секторов с заполненностью
        sectors = self.build_wheel()
        sectors = self.assess_gaps(sectors)
        
        # Создаём движок Эйлеровых Кругов
        engine = EulerCirclesEngine(sectors)
        intersections = engine.find_all_intersections()
        
        # Классифицируем пересечения
        golden = engine.get_golden_sections()
        critical = engine.get_critical_gaps()
        conflicts = engine.get_conflicts()
        growth = engine.get_growth_zones()
        
        # Синтез новых ключей из зелёных пересечений
        new_keys = engine.synthesize_from_green_intersections()
        
        return {
                    "center": self.center,
                    "domain": self.domain,
                    "total_intersections": len(intersections),
                    "golden_sections": len(golden),
                    "critical_gaps": len(critical),
                    "conflicts": len(conflicts),
                    "growth_zones": len(growth),
                    "golden_details": [
                        {
                            "type": g.intersection_type,
                            "circles": g.circle_names,
                            "strength": g.strength,
                            "p_success": g.p_success,
                            "p_success_given_green": g.p_success_given_green,
                            "p_success_given_red": g.p_success_given_red,
                            "prior": g.prior,
                            "evidence": g.evidence,
                            "description": g.description,
                            "action": g.action,
                        }
                        for g in golden
                    ],
                    "critical_details": [
                        {
                            "type": c.intersection_type,
                            "circles": c.circle_names,
                            "strength": c.strength,
                            "p_success": c.p_success,
                            "p_success_given_green": c.p_success_given_green,
                            "p_success_given_red": c.p_success_given_red,
                            "prior": c.prior,
                            "evidence": c.evidence,
                            "description": c.description,
                            "action": c.action,
                        }
                        for c in critical
                    ],
                    "conflict_details": [
                        {
                            "type": c.intersection_type,
                            "circles": c.circle_names,
                            "strength": c.strength,
                            "p_success": c.p_success,
                            "p_success_given_green": c.p_success_given_green,
                            "p_success_given_red": c.p_success_given_red,
                            "prior": c.prior,
                            "evidence": c.evidence,
                            "description": c.description,
                            "action": c.action,
                        }
                        for c in conflicts
                    ],
                    "growth_details": [
                        {
                            "type": g.intersection_type,
                            "circles": g.circle_names,
                            "strength": g.strength,
                            "p_success": g.p_success,
                            "p_success_given_green": g.p_success_given_green,
                            "p_success_given_red": g.p_success_given_red,
                            "prior": g.prior,
                            "evidence": g.evidence,
                            "description": g.description,
                            "action": g.action,
                        }
                        for g in growth
                    ],
                    "new_keys_from_green": new_keys,
                    "sectors_summary": [
                        {
                            "name": s.name,
                            "fill_percent": s.fill_percent,
                            "status": s.status,
                            "weight": s.weight,
                            "critical": s.critical,
                        }
                        for s in sectors
                    ],
                }


    def run_full_cycle(self, mode: str = "all", days: int = 7) -> Dict[str, Any]:
        """Запустить полный цикл в указанном режиме.
        
        modes: analysis, synthesis, euler, all
        """
        results = {}

        # Normalize mode: "both" -> "all"
        if mode == "both":
            mode = "all"
            
        if mode in ("analysis", "all"):
            logger.info("Running ANALYSIS mode...")
            results["analysis"] = self.run_analysis_mode()

        if mode in ("synthesis", "all"):
            logger.info("Running SYNTHESIS mode...")
            results["synthesis"] = self.run_synthesis_mode(days)

        if mode in ("euler", "all"):
            logger.info("Running EULER CIRCLES mode...")
            results["euler"] = self.run_euler_mode()

        return results


# =============================================================================
# CLI
# =============================================================================

if __name__ == "__main__":
    import sys

    logging.basicConfig(level=logging.INFO)

    if len(sys.argv) < 2:
        print("Usage: python fractal_wheel.py <center> [domain] [mode]")
        print("  center: ключевая концепция (e.g., 'PWA-арбитраж беттинга на Индию')")
        print("  domain: arbitrage, ai-ofm, craft, default (default: arbitrage)")
        print("  mode: analysis, synthesis, both (default: both)")
        sys.exit(1)

    center = sys.argv[1]
    domain = sys.argv[2] if len(sys.argv) > 2 else "arbitrage"
    mode = sys.argv[3] if len(sys.argv) > 3 else "all"

    wheel = FractalWheel(center=center, domain=domain)
    results = wheel.run_full_cycle(mode=mode)

    if "analysis" in results:
        a = results["analysis"]
        print(f"\n=== ANALYSIS: {a.center} ===")
        print(f"Overall: {a.overall_percent}%")
        print(f"Green: {len(a.green_sectors)}, Yellow: {len(a.yellow_sectors)}, Red: {len(a.red_sectors)} (critical: {len(a.critical_red_sectors)})")
        for task in a.priority_tasks[:5]:
            print(f"  [{task['priority'].upper()}] {task['sector_name']}: {task['expected_outcome']}")

    if "synthesis" in results:
        s = results["synthesis"]
        print(f"\n=== SYNTHESIS: {len(s)} novel keys ===")
        for i, key in enumerate(s[:5], 1):
            print(f"\n{i}. {key.name}")
            print(f"   Compatibility: {key.compatibility_score:.0%}, Novelty: {key.novelty_score:.0%}")
            print(f"   {key.description}")
            print(f"   Reasoning: {key.reasoning}")

    print("\nDone.")
"""
Data models for CPA Browser Scraper.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Optional, Any
import json


@dataclass
class Offer:
    """CPA offer model."""
    offer_id: str
    network: str  # adcombo, cpalead, alfaleads, cpatrend
    name: str
    vertical: str  # gambling, dating, pwa_install, nutra, finance
    geo: str  # IN, BR, US, DE, etc.
    payout: float
    flow: str  # CPI, CPL, CPS, SOI, DOI
    cap_daily: int
    lander_url: str
    restrictions: List[str] = field(default_factory=list)
    approval_difficulty: int = 5  # 1-10
    source_url: str = ""
    scraped_at: datetime = field(default_factory=datetime.now)
    confidence_score: float = 1.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "offer_id": self.offer_id,
            "network": self.network,
            "name": self.name,
            "vertical": self.vertical,
            "geo": self.geo,
            "payout": self.payout,
            "flow": self.flow,
            "cap_daily": self.cap_daily,
            "lander_url": self.lander_url,
            "restrictions": self.restrictions,
            "approval_difficulty": self.approval_difficulty,
            "source_url": self.source_url,
            "scraped_at": self.scraped_at.isoformat(),
            "confidence_score": self.confidence_score
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Offer':
        if isinstance(data.get('scraped_at'), str):
            data['scraped_at'] = datetime.fromisoformat(data['scraped_at'])
        return cls(**data)


@dataclass
class Creative:
    """Creative/Ad model."""
    creative_id: str
    platform: str  # fb_library, tiktok_cc, native_adspy
    hook: str
    format: str  # video, image, carousel
    cta: str
    lander_pattern: str
    impressions_est: int = 0
    strategy: str = "unknown"  # UGC, studio, native
    targeting_hints: List[str] = field(default_factory=list)
    advertiser: str = ""
    source_url: str = ""
    scraped_at: datetime = field(default_factory=datetime.now)
    freshness_score: float = 1.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "creative_id": self.creative_id,
            "platform": self.platform,
            "hook": self.hook,
            "format": self.format,
            "cta": self.cta,
            "lander_pattern": self.lander_pattern,
            "impressions_est": self.impressions_est,
            "strategy": self.strategy,
            "targeting_hints": self.targeting_hints,
            "advertiser": self.advertiser,
            "source_url": self.source_url,
            "scraped_at": self.scraped_at.isoformat(),
            "freshness_score": self.freshness_score
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Creative':
        if isinstance(data.get('scraped_at'), str):
            data['scraped_at'] = datetime.fromisoformat(data['scraped_at'])
        return cls(**data)


@dataclass
class CompetitorReport:
    """Competitor landing page analysis."""
    url: str
    hook: str
    structure: Dict[str, Any] = field(default_factory=dict)
    tech_stack: List[str] = field(default_factory=list)
    cta_patterns: List[str] = field(default_factory=list)
    spend_signals: Dict[str, Any] = field(default_factory=dict)
    scraped_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "url": self.url,
            "hook": self.hook,
            "structure": self.structure,
            "tech_stack": self.tech_stack,
            "cta_patterns": self.cta_patterns,
            "spend_signals": self.spend_signals,
            "scraped_at": self.scraped_at.isoformat()
        }


@dataclass
class LocalBiz:
    """Local business from Google Maps."""
    name: str
    address: str
    phone: str
    website: str
    rating: float = 0.0
    reviews_count: int = 0
    place_id: str = ""
    photos: List[str] = field(default_factory=list)
    services: List[str] = field(default_factory=list)
    has_website: bool = False
    website_tech: List[str] = field(default_factory=list)  # WordPress, Wix, custom, etc.
    website_status: str = "unknown"  # no_site, bad_site, good_site
    scraped_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "address": self.address,
            "phone": self.phone,
            "website": self.website,
            "rating": self.rating,
            "reviews_count": self.reviews_count,
            "place_id": self.place_id,
            "photos": self.photos,
            "services": self.services,
            "has_website": self.has_website,
            "website_tech": self.website_tech,
            "website_status": self.website_status,
            "scraped_at": self.scraped_at.isoformat()
        }
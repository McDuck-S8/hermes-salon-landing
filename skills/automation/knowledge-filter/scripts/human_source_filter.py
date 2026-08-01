#!/usr/bin/env python3
"""
Human-Source Filter — Stage 1 of Knowledge Filter.
Checks personal relevance, constraints, values alignment.
"""

import json
import sys
import re
from pathlib import Path
from typing import Dict, List, Any

# ─── Paths ────────────────────────────────────────────────────────────────────
HERE = Path(__file__).resolve().parent
SKILLS_DIR = HERE.parent.parent.parent
HERMES_ROOT = SKILLS_DIR.parent
MEMORIES_DIR = HERMES_ROOT / "memories"
USER_MD = MEMORIES_DIR / "USER.md"

class HumanSourceFilter:
    """Evaluates article against user's values, constraints, and profile."""
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.threshold = self.config.get("threshold", 60)
        
        # Load user profile
        self.user_profile = self._load_user_profile()
        
        # Hard constraints (BLOCK if matched) - ONLY truly blocking items
        self.hard_blocks = [
            (r"require.*kyc|kyc.*required|kyc.*mandatory", "KYC required"),
            (r"passport|паспорт", "Passport required"),
            (r"selfie|селфи|face.id|faceid", "Selfie/FaceID required"),
            (r"document|документ|удостоверен", "Documents required"),
            (r"google.gemini|gemini", "Google Gemini API (blocked)"),
            (r"playwright", "Playwright required (blocked)"),
            (r"chrome.*headless|headless.*chrome", "Chrome headless (blocked)"),
        ]
        
        # ─── Penalty keywords (negative signals, NOT hard blocks) ────────────────────
        self.penalty_keywords = {
            "google.ads": -25, "facebook.ads": -20, "tiktok.ads": -20, "yandex.direct": -15,
            "agency": -15, "агентство": -15, "manager": -15, "менеджер": -15,
            "manual": -10, "ручной": -10, "рутин": -10, "routine": -10,
            "outsourc": -15, "аутсорс": -15, "freelancer": -10, "фриланс": -10,
            "meeting": -5, "встреча": -5, "call": -5, "звонок": -5,
            "approval": -10, "согласован": -10, "bureaucracy": -15, "бюрократ": -15,
            "budget": -10, "бюджет": -10, "investment": -10, "инвестиц": -10,
            "paid.api": -15, "subscription": -15, "подписка": -15,
            "legal.compliance": -10, "юридич": -10, "compliance": -10, "licen": -10,
        }
        
        # Boost keywords (positive signals)
        self.boost_keywords = {
            # Context/Location
            "crimea": 20, "simferopol": 20, "крым": 20, "симферополь": 20,
            "hh.ru": 15, "hh ru": 15, "headhunter": 10, "job": 10, "работа": 10, "ваканс": 10,
            # Finance
            "p2p": 25, "usdt": 25, "rub": 20, "руб": 20, "рубль": 15, "offramp": 25, "onramp": 15,
            "crypto": 15, "крипт": 15, "whitebird": 20, "p2p": 20,
            # Content/Traffic
            "shorts": 20, "tiktok": 20, "reels": 15, "organic": 15, "органик": 15,
            "content": 10, "контент": 10, "pipeline": 10, "конвейер": 10,
            # Arbitrage/Technical
            "arbitrage": 30, "арбитраж": 30, "matrix": 15, "матриц": 15,
            "betting": 20, "betting": 20, "cricket": 20, "крикет": 20,
            "autonomous": 25, "автономн": 25, "cron": 15, "daemon": 15, "демон": 15,
            "self.heal": 20, "selfheal": 20, "автовосстановл": 20,
            "telegram": 15, "tg": 10, "bot": 15, "бот": 15, "channel": 10, "канал": 10,
            # Norms/Values
            "no.kyc": 30, "no kyc": 30, "no.doc": 25, "no doc": 25,
            "stdlib": 15, "standard.library": 15, "ponytail": 15,
            "filesystem": 10, "файловая.систем": 10,
            "pytest": 10, "linter": 10, "линтер": 10,
        }
        
        # Frustration patterns (user's pain points)
        self.frustration_patterns = [
            "passive", "пассивн", "waiting", "ожидан", "need.to.poke", "нужно.тыкать",
            "broken.promise", "не.выполнил", "plan.not.delivered", "план.не.доставлен",
            "micro.manag", "микроман", "terminal.spam", "терминал.*спам",
            "list.not.research", "лист.*не.*исследован", "list≠research",
        ]
    
    def _load_user_profile(self) -> Dict:
        """Load user profile from USER.md."""
        profile = {
            "constraints": [],
            "frustrations": [],
            "norms": [],
            "strengths": [],
            "context": {},
        }
        
        if USER_MD.exists():
            try:
                content = USER_MD.read_text(encoding="utf-8")
                # Simple extraction
                if "No KYC" in content or "no KYC" in content:
                    profile["constraints"].append("No KYC")
                if "No KYC" in content or "no documents" in content.lower():
                    profile["constraints"].append("No documents")
                if "Crimea" in content or "Крым" in content:
                    profile["context"]["location"] = "Crimea"
                if "USDT" in content or "P2P" in content:
                    profile["constraints"].append("USDT/P2P only")
            except Exception:
                pass
        
        return profile
    
    def evaluate(self, article: Dict) -> Dict[str, Any]:
        """Evaluate article against human-source criteria."""
        text = f"{article.get('title', '')} {article.get('content', '')}".lower()
        
        score = 50  # base
        conflicts = []
        passed_checks = []
        failed_checks = []
        
        # ─── HARD BLOCKS ──────────────────────────────────────────────────────
        for pattern, reason in self.hard_blocks:
            if re.search(pattern, text, re.IGNORECASE):
                return {
                    "score": 0,
                    "passed": False,
                    "conflicts": [f"HARD BLOCK: {reason}"],
                    "blocked": True,
                    "details": {"block_reason": reason}
                }
        
        # ─── BOOST KEYWORDS ───────────────────────────────────────────────────
        for kw, boost in self.boost_keywords.items():
            if kw in text:
                score += boost
                passed_checks.append(f"Boost: {kw} (+{boost})")
        
        # ─── PENALTY KEYWORDS ─────────────────────────────────────────────────
        for kw, penalty in self.penalty_keywords.items():
            if re.search(kw.replace(".", r"\."), text):
                score += penalty
                failed_checks.append(f"Penalty: {kw} ({penalty})")
        
        # ─── FRUSTRATION ALIGNMENT ────────────────────────────────────────────
        # Articles that SOLVE user's frustrations get bonus
        frustration_solvers = {
            "autonomous": "Agent passivity",
            "auto.*apply": "Job search manual",
            "auto.*post": "Manual content",
            "auto.*reply": "Manual replies",
            "no.code": "Technical complexity",
            "template": "Repeated work",
            "batch": "One-by-one processing",
        }
        
        for kw, frustration in frustration_solvers.items():
            if re.search(kw, text):
                score += 15
                passed_checks.append(f"Solves frustration: {frustration} (+15)")
        
        # ─── CONTEXT MATCH ────────────────────────────────────────────────────
        if self.user_profile.get("context", {}).get("location") == "Crimea":
            crimea_keywords = ["crimea", "крым", "simferopol", "симферополь", "remote", "удалённ"]
            if any(kw in text for kw in crimea_keywords):
                score += 10
                passed_checks.append("Crimea context match (+10)")
        
        # ─── CLAMP ─────────────────────────────────────────────────────────────
        score = max(0, min(100, score))
        passed = score >= self.threshold
        
        reasons = []
        if passed:
            reasons = [f"Score {score} ≥ threshold {self.threshold}"]
            reasons.extend(passed_checks[:3])
        else:
            reasons.append(f"Score {score} < threshold {self.threshold}")
            if failed_checks:
                reasons.extend(failed_checks[:3])
        
        return {
            "score": int(score),
            "passed": passed,
            "conflicts": conflicts,
            "reasons": reasons,
            "blocked": False,
            "details": {
                "base_score": 50,
                "boost_total": sum(b for k, b in self.boost_keywords.items() if k in text),
                "penalty_total": sum(p for k, p in self.penalty_keywords.items() if re.search(k.replace(".", r"\."), text)),
                "threshold": self.threshold,
                "user_constraints": self.user_profile.get("constraints", []),
            }
        }


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--title", required=True)
    parser.add_argument("--content", required=True)
    parser.add_argument("--source", default="test")
    parser.add_argument("--url", default="")
    args = parser.parse_args()
    
    filter = HumanSourceFilter()
    result = filter.evaluate({
        "title": args.title,
        "content": args.content,
        "source": args.source,
        "url": args.url
    })
    
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
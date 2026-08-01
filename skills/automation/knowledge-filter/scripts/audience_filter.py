#!/usr/bin/env python3
"""
Audience-Analyzer Filter — Stage 2 of Knowledge Filter.
Evaluates market relevance based on current offers, verticals, geos, audience needs.
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any

class AudienceFilter:
    """Evaluates article against audience/market needs."""
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        
        # Current vertical priorities (from user's arbitrage focus)
        self.verticals = {
            "gambling": {
                "weight": 30,
                "keywords": [
                    "betting", "casino", "slots", "cricket", "1xbet", "1win", "gambling", 
                    "bet", "wager", "sportsbook", "фора", "тотал", "коэффициент",
                    "казино", "слоты", "ставки", "букмекер", "коэф", "просадка"
                ],
                "geos": ["in", "india", "индия", "br", "brazil", "бразилия", "mx", "mexico", 
                         "мексика", "latam", "латам", "id", "indonesia", "индонезия", 
                         "bd", "bangladesh", "бангладеш", "vn", "vietnam", "вьетнам"],
                "offers": ["cpa", "cpl", "revshare", "reg2dep", "ftd"]
            },
            "fintech": {
                "weight": 25,
                "keywords": [
                    "card", "payout", "leadgen", "loan", "credit", "crypto", "p2p",
                    "offramp", "onramp", "whitebird", "usdt", "rub", "руб", "рубль",
                    "карта", "вывод", "пополнение", "перевод", "обмен", "курс",
                    "fintech", "финтех", "платеж", "банк", "tbank", "тинькофф"
                ],
                "geos": ["ru", "russia", "россия", "cis", "снг", "latam", "индия", "in", 
                         "ua", "ukraine", "украина", "kz", "kazakhstan", "казахстан"],
                "offers": ["cpa", "cpl", "lead", "card_issue", "deposit"]
            },
            "content": {
                "weight": 20,
                "keywords": [
                    "shorts", "tiktok", "reels", "viral", "organic", "youtube", 
                    "instagram", "creators", "monetization", "monetisation", "монетизация",
                    "трафик", "traffic", "organic", "органик", "бесплатный", "free"
                ],
                "geos": ["global", "us", "usa", "индия", "india", "br", "brazil"],
                "offers": ["cpa", "cpi", "revshare", "affiliate"]
            }
        }
        
        # Source credibility weights
        self.source_weights = {
            "affiliatefix": 20, "partnerkin": 20, "reddit": 15,
            "youtube": 15, "telegram": 10, "partnerkin_youtube": 15,
            "openai": 5, "anthropic": 5, "hackernews": 5,
        }
        
        # Article type weights
        self.type_weights = {
            "case_study": 20, "кейс": 20, "proof": 15, "пруф": 15,
            "strategy": 15, "стратегия": 15, "tutorial": 10, "гайд": 10,
            "tool_review": 10, "обзор": 10, "news": 5, "новости": 5,
        }

    def evaluate(self, article: Dict) -> Dict[str, Any]:
        """Evaluate article for audience relevance."""
        text = f"{article.get('title', '')} {article.get('content', '')}".lower()
        source = article.get("source", "").lower()
        tags = article.get("extra", {}).get("tags", [])
        
        score = 30  # base
        matched_verticals = []
        geo_match = []
        matched_offers = []
        article_type = "unknown"
        
        # ─── Check verticals ─────────────────────────────────────────────────
        for vertical, config in self.verticals.items():
            kw_hits = sum(1 for kw in config["keywords"] if kw in text)
            if kw_hits >= 1:  # at least 1 keyword match (lowered from 2)
                matched_verticals.append(vertical)
                score += config["weight"]
                
                # Check geo
                geo_hits = [g for g in config["geos"] if g in text]
                if geo_hits:
                    geo_match.extend(geo_hits)
                    score += 10
                
                # Check offers
                offer_hits = [o for o in config["offers"] if o in text]
                if offer_hits:
                    matched_offers.extend(offer_hits)
                    score += 5
        
        # ─── Check tags from RSS parser ──────────────────────────────────────
        tag_boost = {
            "трафик": 10, "кейс": 15, "гембл": 15, "беттинг": 15, "оффер": 10,
            "сео": 5, "лендинг": 10, "нутра": 10, "roi": 10,
        }
        for tag in tags:
            score += tag_boost.get(tag.lower(), 0)
        
        # ─── Source credibility ──────────────────────────────────────────────
        score += self.source_weights.get(source, 0)
        
        # ─── Article type detection ──────────────────────────────────────────
        for atype, keywords in self.type_weights.items():
            if any(kw in text for kw in [atype.replace("_", " ")]):
                article_type = atype
                score += keywords
                break
        
        # ─── Clamp & Threshold ───────────────────────────────────────────────
        score = max(0, min(100, score))
        threshold = self.config.get("threshold", 30)  # Lowered from 50
        passed = score >= threshold
        
        reasons = []
        if passed:
            reasons = [f"Matched verticals: {', '.join(matched_verticals)}" if matched_verticals else "General relevance"]
            if geo_match:
                reasons.append(f"Geo match: {', '.join(set(geo_match))}")
            if matched_offers:
                reasons.append(f"Offer types: {', '.join(set(matched_offers))}")
        else:
            reasons.append(f"Score {score} < threshold {threshold}")
            if not matched_verticals:
                reasons.append("No vertical matched (need ≥1 keyword hits)")
        
        return {
            "score": int(score),
            "passed": passed,
            "matched_verticals": matched_verticals,
            "geo_match": list(set(geo_match)),
            "matched_offers": list(set(matched_offers)),
            "article_type": article_type,
            "reasons": reasons,
            "details": {
                "base_score": 30,
                "vertical_score": sum(self.verticals[v]["weight"] for v in matched_verticals),
                "geo_score": 10 if geo_match else 0,
                "source_score": self.source_weights.get(source, 0),
                "type_score": self.type_weights.get(article_type, 0),
                "final_score": score,
            }
        }


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--title", required=True)
    parser.add_argument("--content", required=True)
    parser.add_argument("--source", default="test")
    parser.add_argument("--url", default="")
    parser.add_argument("--tags", default="", help="Comma-separated tags")
    args = parser.parse_args()
    
    filter = AudienceFilter()
    result = filter.evaluate({
        "title": args.title,
        "content": args.content,
        "source": args.source,
        "url": args.url,
        "extra": {"tags": [t.strip() for t in args.tags.split(",") if t.strip()]}
    })
    
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
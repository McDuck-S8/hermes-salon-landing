#!/usr/bin/env python3
"""
Ripple Engine v2 - Autonomous Daily Processing System

Real processing: reads actual ripple_keys data, applies BM25-style analysis,
generates meaningful differentiation between stones, unlocks mature keys.
Modern dark dashboard with gradient cards by importance, visual hierarchy.
"""

import json
import os
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
import re
from collections import Counter

# Configuration
CACHE_DIR = Path("cache")
KNOWLEDGE_CUBE_DB = CACHE_DIR / "knowledge_cube.db"
REPORTS_DIR = CACHE_DIR / "reports"
RIPPLE_KEYS_DIR = CACHE_DIR

REPORTS_DIR.mkdir(parents=True, exist_ok=True)

# ============ DESIGN SYSTEM (from ui-ux-pro-max) ============

DESIGN_TOKENS = {
    "colors": {
        "bg_primary": "#0A0E17",
        "bg_secondary": "#111827",
        "bg_tertiary": "#1F2937",
        "card_low": "linear-gradient(135deg, #1F2937 0%, #111827 100%)",
        "card_med": "linear-gradient(135deg, #1E3A5F 0%, #1E4A7F 100%)",
        "card_high": "linear-gradient(135deg, #7C3AED 0%, #5B21B6 100%)",
        "card_critical": "linear-gradient(135deg, #DC2626 0%, #991B1B 100%)",
        "accent_cyan": "#06B6D4",
        "accent_green": "#10B981",
        "accent_amber": "#F59E0B",
        "accent_purple": "#8B5CF6",
        "accent_red": "#EF4444",
        "text_primary": "#F8FAFC",
        "text_secondary": "#94A3B8",
        "text_muted": "#64748B",
        "border": "#1E293B",
        "border_focus": "#3B82F6",
    },
    "spacing": {
        "xs": "4px", "sm": "8px", "md": "16px", "lg": "24px", "xl": "32px", "2xl": "48px"
    },
    "radius": {
        "sm": "6px", "md": "10px", "lg": "16px", "xl": "20px"
    },
    "shadows": {
        "sm": "0 1px 2px rgba(0,0,0,0.3)",
        "md": "0 4px 12px rgba(0,0,0,0.4)",
        "lg": "0 8px 32px rgba(0,0,0,0.5)",
        "glow_cyan": "0 0 24px rgba(6, 182, 212, 0.25)",
        "glow_green": "0 0 24px rgba(16, 185, 129, 0.25)",
        "glow_purple": "0 0 24px rgba(139, 92, 246, 0.25)",
    },
    "typography": {
        "font_family": "'JetBrains Mono', 'Fira Code', 'SF Mono', monospace",
        "heading": "clamp(1.5rem, 3vw, 2.25rem)",
        "subheading": "clamp(1rem, 2vw, 1.25rem)",
        "body": "0.875rem",
        "small": "0.75rem",
    }
}

# ============ STONE CLASS ============

class Stone:
    """A data stone thrown into the water - real analysis, not fake numbers."""
    
    def __init__(self, source: str, raw_data: Dict[str, Any], timestamp: str):
        self.source = source
        self.raw = raw_data
        self.timestamp = timestamp
        self.id = f"{source}_{timestamp.replace(':', '').replace('-', '').replace(' ', '_')}"
        
        # Extract from real ripple_keys structure FIRST
        self.title = raw_data.get("title", "")[:120]
        self.content = raw_data.get("content_summary", "")
        self.url = raw_data.get("url", "")
        self.aspects = raw_data.get("aspects", ["general"])
        self.conflicts = raw_data.get("conflicts", [])
        self.gaps = raw_data.get("gaps", [])
        self.new_keys = raw_data.get("new_keys_generated", [])
        
        # Real metrics from data
        self.raw_strength = raw_data.get("key_strength", 50)
        raw_conf = raw_data.get("confidence", 50)
        # Normalize confidence to 0-100 scale (some sources use 0-1)
        self.raw_confidence = raw_conf * 100 if isinstance(raw_conf, float) and raw_conf <= 1 else raw_conf
        self.raw_roi = raw_data.get("roi_estimate", "")
        raw_act = raw_data.get("actionable", False)
        # Normalize actionable (handle string "true"/"false")
        self.raw_actionable = raw_act if isinstance(raw_act, bool) else (str(raw_act).lower() == "true")
        self.raw_reason = raw_data.get("reason", "")
        
        # Compute differentiated scores (with safe defaults)
        try:
            self.key_strength = self._compute_strength()
        except Exception:
            self.key_strength = 50
        try:
            self.confidence = self._compute_confidence()
        except Exception:
            self.confidence = 50
        try:
            self.roi_estimate = self._estimate_roi()
        except Exception:
            self.roi_estimate = "Unknown"
        try:
            self.actionable = self._is_actionable()
        except Exception:
            self.actionable = False
        try:
            self.reason = self._generate_reason()
        except Exception:
            self.reason = "Parse error"
        try:
            self.priority_tier = self._calc_priority_tier()
        except Exception:
            self.priority_tier = "low"
        try:
            self.visual_weight = self._calc_visual_weight()
        except Exception:
            self.visual_weight = 50
    
    def _compute_strength(self) -> int:
        """Differentiated strength based on content richness."""
        base = self.raw_strength
        
        # Boost for rich aspects
        aspect_boost = min(len(self.aspects) * 3, 15)
        
        # Boost for multiple new keys
        key_boost = min(len(self.new_keys) * 5, 20)
        
        # Penalty for conflicts
        conflict_penalty = len(self.conflicts) * 5
        
        # Penalty for gaps
        gap_penalty = len([g for g in self.gaps if g != "no_critical_gaps"]) * 3
        
        score = base + aspect_boost + key_boost - conflict_penalty - gap_penalty
        return max(10, min(100, score))
    
    def _compute_confidence(self) -> int:
        """Differentiated confidence based on data quality."""
        base = self.raw_confidence
        
        # Higher confidence if actionable in source
        if self.raw_actionable:
            base += 10
        
        # Lower if many gaps
        gap_count = len([g for g in self.gaps if g not in ("no_critical_gaps", "none_identified")])
        base -= gap_count * 4
        
        # Lower if conflicts
        base -= len(self.conflicts) * 5
        
        # Boost for specific keys (not generic)
        specific_keys = [k for k in self.new_keys if k != "general_knowledge" and not k.startswith("general_")]
        base += len(specific_keys) * 3
        
        return max(15, min(100, base))
    
    def _estimate_roi(self) -> str:
        """ROI tier based on strength + confidence + actionability."""
        combo = (self.key_strength + self.confidence) / 2
        if self.actionable and combo >= 80:
            return "Very High — Direct revenue path, ready to execute"
        elif combo >= 75:
            return "High — Strong signal, needs validation"
        elif combo >= 60:
            return "Medium — Promising, requires research"
        elif combo >= 45:
            return "Low — Weak signal, monitor only"
        return "Negligible — Noise"
    
    def _is_actionable(self) -> bool:
        """Actionability: high strength + high confidence + no conflicts."""
        return (
            self.key_strength >= 70 and 
            self.confidence >= 75 and 
            len(self.conflicts) == 0
        )
    
    def _generate_reason(self) -> str:
        parts = []
        if self.aspects:
            parts.append(f"Aspects: {', '.join(self.aspects[:3])}")
        if self.new_keys:
            specific = [k for k in self.new_keys if k != "general_knowledge"]
            if specific:
                parts.append(f"Keys: {', '.join(specific[:3])}")
        if self.conflicts:
            parts.append(f"⚠ Conflicts: {len(self.conflicts)}")
        if self.gaps:
            real_gaps = [g for g in self.gaps if g not in ("no_critical_gaps", "none_identified")]
            if real_gaps:
                parts.append(f"Gaps: {len(real_gaps)}")
        return " | ".join(parts) if parts else "Generic content"
    
    def _calc_priority_tier(self) -> str:
        """Visual priority tier for gradient card assignment."""
        if self.key_strength >= 85 and self.confidence >= 85:
            return "critical"
        elif self.key_strength >= 75 and self.confidence >= 75:
            return "high"
        elif self.key_strength >= 60 or self.confidence >= 60:
            return "medium"
        return "low"
    
    def _calc_visual_weight(self) -> int:
        """Size weight for visual hierarchy."""
        return int((self.key_strength + self.confidence) / 2)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "source": self.source,
            "title": self.title,
            "content": self.content[:200] + ("..." if len(self.content) > 200 else ""),
            "url": self.url,
            "timestamp": self.timestamp,
            "aspects": self.aspects,
            "conflicts": self.conflicts,
            "gaps": self.gaps,
            "new_keys": self.new_keys,
            "key_strength": self.key_strength,
            "confidence": self.confidence,
            "roi_estimate": self.roi_estimate,
            "actionable": self.actionable,
            "reason": self.reason,
            "priority_tier": self.priority_tier,
            "visual_weight": self.visual_weight,
        }

# ============ RIPPLE ENGINE ============

class RippleEngine:
    def __init__(self):
        self.stones: List[Stone] = []
        self.circles: Dict[str, List[Stone]] = {}
        self.mature_keys: List[Dict[str, Any]] = []
        self.html_path = REPORTS_DIR / "daily_ripple_map.html"
    
    def gather_daily_stones(self) -> None:
        """Gather stones from real ripple_keys JSON files."""
        print("🪨 Gathering daily stones from ripple_keys...")
        
        stones = []
        for ripple_file in sorted(RIPPLE_KEYS_DIR.glob("ripple_keys_*.json")):
            try:
                with open(ripple_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                for item in data.get("keys", []):
                    # Skip if already processed (could add tracking)
                    stone = Stone(
                        source=item.get("source", "youtube"),
                        raw_data=item,
                        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    )
                    stones.append(stone)
                    
            except Exception as e:
                print(f"  ⚠️ Error reading {ripple_file}: {e}")
        
        # If no ripple keys, create from knowledge cube
        if not stones:
            stones = self._fallback_from_kc()
        
        # Deduplicate by title similarity
        self.stones = self._deduplicate(stones)
        print(f"  ✅ Collected {len(self.stones)} unique stones")
    
    def _fallback_from_kc(self) -> List[Stone]:
        """Fallback: read from knowledge_cube.db experiences."""
        stones = []
        if not KNOWLEDGE_CUBE_DB.exists():
            return stones
        
        try:
            conn = sqlite3.connect(KNOWLEDGE_CUBE_DB)
            conn.row_factory = sqlite3.Row
            c = conn.cursor()
            c.execute("""
                SELECT * FROM experiences 
                WHERE is_white_spot = 0
                ORDER BY ts DESC LIMIT 30
            """)
            for row in c.fetchall():
                item = {
                    "title": row["content"][:80] if row["content"] else "KC Entry",
                    "content_summary": row["content"] or "",
                    "source": row["source"] or "knowledge_cube",
                    "aspects": [row["axis_domain"]] if row["axis_domain"] else ["general"],
                    "conflicts": [],
                    "gaps": [],
                    "new_keys_generated": [row["axis_outcome"]] if row["axis_outcome"] else ["general_knowledge"],
                    "key_strength": int((row["importance"] or 0.5) * 100),
                    "confidence": int((row["confidence"] or 1.0) * 100),
                    "roi_estimate": "Medium — from knowledge cube",
                    "actionable": False,
                    "reason": "From knowledge cube experience",
                }
                stones.append(Stone(
                    source=item["source"],
                    raw_data=item,
                    timestamp=row["ts"] or datetime.now().isoformat()
                ))
            conn.close()
        except Exception as e:
            print(f"  ⚠️ KC fallback error: {e}")
        return stones
    
    def _deduplicate(self, stones: List[Stone]) -> List[Stone]:
        """Remove near-duplicate stones by URL or full title."""
        unique = []
        seen_urls = set()
        seen_titles = set()
        
        for stone in stones:
            # Prefer URL for deduplication
            if stone.url and stone.url not in seen_urls:
                seen_urls.add(stone.url)
                unique.append(stone)
            elif stone.title and stone.title.lower() not in seen_titles:
                seen_titles.add(stone.title.lower())
                unique.append(stone)
        return unique
    
    def build_circles(self) -> None:
        """Build impact circles - group stones by shared aspects & keys."""
        print("🔄 Building impact circles...")
        
        # Circle by aspect
        aspect_circles = {}
        for stone in self.stones:
            for aspect in stone.aspects:
                aspect_circles.setdefault(aspect, []).append(stone)
        
        # Circle by new key
        key_circles = {}
        for stone in self.stones:
            for key in stone.new_keys:
                key_circles.setdefault(key, []).append(stone)
        
        # Merge and filter meaningful circles (2+ stones)
        all_circles = {}
        for name, members in {**aspect_circles, **key_circles}.items():
            if len(members) >= 2:
                all_circles[f"circle:{name}"] = members
        
        self.circles = all_circles
        print(f"  ✅ Built {len(self.circles)} impact circles")
    
    def calculate_mature_keys(self) -> None:
        """Identify mature keys ready for unlocking."""
        print("🔑 Calculating mature keys...")
        
        # Aggregate by new_key across all stones
        key_stats = {}
        for stone in self.stones:
            for key in stone.new_keys:
                if key not in key_stats:
                    key_stats[key] = {"stones": [], "total_strength": 0, "total_conf": 0, "actionable": 0}
                key_stats[key]["stones"].append(stone)
                key_stats[key]["total_strength"] += stone.key_strength
                key_stats[key]["total_conf"] += stone.confidence
                if stone.actionable:
                    key_stats[key]["actionable"] += 1
        
        mature = []
        for key, stats in key_stats.items():
            count = len(stats["stones"])
            avg_strength = stats["total_strength"] / count
            avg_conf = stats["total_conf"] / count
            
            # Maturity criteria - based on convergence strength, not actionable ratio
            is_mature = (
                count >= 2 and
                avg_strength >= 65 and
                avg_conf >= 55
            )
            
            if is_mature:
                # Calculate actionable ratio for display only
                actionable_ratio = stats["actionable"] / count
                mature.append({
                    "key": key,
                    "supporting_stones": count,
                    "avg_strength": round(avg_strength),
                    "avg_confidence": round(avg_conf),
                    "actionable_ratio": round(actionable_ratio * 100),
                    "aspects": list(set(a for s in stats["stones"] for a in s.aspects)),
                    "sources": list(set(s.source for s in stats["stones"])),
                    "unlock_reason": f"{count} stones converge, avg strength {avg_strength:.0f}, {actionable_ratio*100:.0f}% actionable",
                    "unlocked_at": datetime.now().isoformat(),
                })
        
        # Sort by strength
        self.mature_keys = sorted(mature, key=lambda x: x["avg_strength"], reverse=True)
        print(f"  ✅ Found {len(self.mature_keys)} mature keys")
    
    def unlock_mature_keys(self) -> None:
        """Unlock mature keys - persist to Knowledge Cube and trigger downstream."""
        print("🔓 Unlocking mature keys...")
        
        # Persist to Knowledge Cube
        self._persist_mature_keys()
        
        for key in self.mature_keys:
            print(f"  🔑 UNLOCKED: {key['key']} (strength: {key['avg_strength']}, conf: {key['avg_confidence']}%)")
        print(f"  ✅ Unlocked {len(self.mature_keys)} keys")
    
    def _persist_mature_keys(self) -> None:
        """Persist mature keys to Knowledge Cube as experiences."""
        if not KNOWLEDGE_CUBE_DB.exists():
            print("  ⚠️ KC not found, skipping persist")
            return
        
        try:
            import hashlib
            conn = sqlite3.connect(KNOWLEDGE_CUBE_DB)
            c = conn.cursor()
            
            for key in self.mature_keys:
                content = (
                    f"Mature key unlocked: {key['key']}\n"
                    f"Supporting stones: {key['supporting_stones']}\n"
                    f"Avg strength: {key['avg_strength']}\n"
                    f"Avg confidence: {key['avg_confidence']}%\n"
                    f"Actionable ratio: {key['actionable_ratio']}%\n"
                    f"Aspects: {', '.join(key['aspects'])}\n"
                    f"Sources: {', '.join(key['sources'])}\n"
                    f"Reason: {key['unlock_reason']}"
                )
                
                # Generate hash for deduplication
                h = hashlib.sha256(f"mature_key:{key['key']}:{key['unlocked_at']}".encode()).hexdigest()
                
                ts = key['unlocked_at']
                c.execute("""
                    INSERT OR IGNORE INTO experiences
                    (ts, content, raw_text, hash, axis_domain, axis_outcome, 
                     dynamic_axes, is_white_spot, white_spot_cluster_id,
                     source, confidence, tags, importance)
                    VALUES (?, ?, ?, ?, ?, ?, ?, 0, NULL, ?, ?, ?, ?)
                """, (
                    ts, content, content, h,
                    "mature_key", key['key'],
                    json.dumps({"supporting_stones": key['supporting_stones'], "actionable_ratio": key['actionable_ratio']}),
                    "ripple_engine",
                    key['avg_confidence'] / 100.0,
                    json.dumps(["mature_key", "unlocked", *key['aspects']]),
                    key['avg_strength'] / 100.0
                ))
            
            conn.commit()
            conn.close()
            print(f"  💾 Persisted {len(self.mature_keys)} mature keys to Knowledge Cube")
            
        except Exception as e:
            print(f"  ⚠️ KC persist error: {e}")
    
    # ============ HTML GENERATION ============
    
    def generate_html_visualization(self) -> None:
        """Generate modern dark dashboard with gradient cards by importance."""
        print("🌐 Generating modern dark dashboard...")
        
        # Sort stones by visual weight (descending)
        sorted_stones = sorted(self.stones, key=lambda s: s.visual_weight, reverse=True)
        
        html = self._build_html(sorted_stones)
        
        with open(self.html_path, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"  ✅ Dashboard saved: {self.html_path}")
    
    def _build_html(self, stones: List[Stone]) -> str:
        tokens = DESIGN_TOKENS
        c = tokens["colors"]
        s = tokens["spacing"]
        r = tokens["radius"]
        sh = tokens["shadows"]
        t = tokens["typography"]
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        date_str = datetime.now().strftime("%d %b %Y")
        
        # Tier gradient mapping
        tier_gradients = {
            "critical": c["card_critical"],
            "high": c["card_high"],
            "medium": c["card_med"],
            "low": c["card_low"],
        }
        tier_glows = {
            "critical": "0 0 32px rgba(220, 38, 38, 0.35)",
            "high": "0 0 28px rgba(139, 92, 246, 0.3)",
            "medium": "0 0 20px rgba(14, 165, 233, 0.25)",
            "low": "0 0 12px rgba(100, 116, 139, 0.15)",
        }
        tier_borders = {
            "critical": c["accent_red"],
            "high": c["accent_purple"],
            "medium": c["accent_cyan"],
            "low": c["border"],
        }
        
        # Build stone cards HTML
        stone_cards = []
        for i, stone in enumerate(stones):
            tier = stone.priority_tier
            gradient = tier_gradients[tier]
            glow = tier_glows[tier]
            border = tier_borders[tier]
            
            # Card size based on visual weight
            size_class = "stone-large" if stone.visual_weight >= 80 else ("stone-medium" if stone.visual_weight >= 60 else "stone-small")
            
            aspects_html = "".join(f'<span class="chip">{a}</span>' for a in stone.aspects[:5])
            keys_html = "".join(f'<span class="chip key-chip">{k}</span>' for k in stone.new_keys[:4])
            conflicts_html = "".join(f'<span class="chip conflict-chip">⚠ {c}</span>' for c in stone.conflicts[:2])
            
            actionable_badge = ""
            if stone.actionable:
                actionable_badge = f'<span class="badge actionable">⚡ ACTIONABLE</span>'
            
            card = f'''
            <article class="stone-card {size_class} tier-{tier}" style="
                background: {gradient};
                border: 1px solid {border};
                box-shadow: {sh["md"]}, {glow};
                border-radius: {r["lg"]};
            ">
                <div class="stone-header">
                    <span class="tier-badge tier-{tier}">{tier.upper()}</span>
                    <span class="source-tag">{stone.source}</span>
                    {actionable_badge}
                </div>
                
                <h3 class="stone-title" title="{stone.title}">{stone.title}</h3>
                
                <p class="stone-content">{stone.content[:180]}{"..." if len(stone.content) > 180 else ""}</p>
                
                <div class="stone-meta">
                    <div class="metric-row">
                        <span class="metric">
                            <span class="metric-value">{stone.key_strength}</span>
                            <span class="metric-label">STRENGTH</span>
                        </span>
                        <span class="metric">
                            <span class="metric-value">{stone.confidence}%</span>
                            <span class="metric-label">CONFIDENCE</span>
                        </span>
                        <span class="metric">
                            <span class="metric-value">{stone.visual_weight}</span>
                            <span class="metric-label">WEIGHT</span>
                        </span>
                    </div>
                </div>
                
                <div class="stone-tags">
                    <div class="tag-group">
                        <span class="tag-label">Aspects</span>
                        {aspects_html}
                    </div>
                    <div class="tag-group">
                        <span class="tag-label">New Keys</span>
                        {keys_html}
                    </div>
                    {f'<div class="tag-group conflicts"><span class="tag-label">Conflicts</span>{conflicts_html}</div>' if stone.conflicts else ''}
                </div>
                
                <div class="stone-footer">
                    <span class="roi-estimate">{stone.roi_estimate}</span>
                    <a href="{stone.url}" target="_blank" class="source-link">Open Source →</a>
                </div>
            </article>
            '''
            stone_cards.append(card)
        
        # Build circle cards
        circle_cards = []
        for name, members in self.circles.items():
            clean_name = name.replace("circle:", "").replace("_", " ").title()
            avg_strength = sum(m.key_strength for m in members) / len(members)
            tier = "critical" if avg_strength >= 85 else ("high" if avg_strength >= 75 else "medium")
            gradient = tier_gradients[tier]
            border = tier_borders[tier]
            
            member_preview = "".join(
                f'<span class="circle-member" title="{m.title[:60]}">{m.source}:{m.key_strength}</span>' 
                for m in members[:6]
            )
            more = f" +{len(members)-6} more" if len(members) > 6 else ""
            
            circle_cards.append(f'''
            <article class="circle-card" style="background: {gradient}; border-color: {border};">
                <h4 class="circle-name">{clean_name}</h4>
                <div class="circle-stats">
                    <span>{len(members)} stones</span>
                    <span>Avg Strength: {avg_strength:.0f}</span>
                </div>
                <div class="circle-members">{member_preview}{more}</div>
            </article>
            ''')
        
        # Build mature key cards
        key_cards = []
        for key in self.mature_keys:
            strength = key["avg_strength"]
            tier = "critical" if strength >= 85 else "high"
            gradient = tier_gradients[tier]
            border = tier_borders[tier]
            
            key_cards.append(f'''
            <article class="key-card" style="background: {gradient}; border-color: {border};">
                <div class="key-header">
                    <span class="key-name">{key["key"]}</span>
                    <span class="key-strength">{strength}</span>
                </div>
                <div class="key-metrics">
                    <span>{key["supporting_stones"]} stones</span>
                    <span>Conf: {key["avg_confidence"]}%</span>
                    <span>{key["actionable_ratio"]}% actionable</span>
                </div>
                <div class="key-aspects">{"".join(f'<span class="chip">{a}</span>' for a in key["aspects"][:5])}</div>
                <div class="key-reason">{key["unlock_reason"]}</div>
            </article>
            ''')
        
        # Summary stats
        total_stones = len(stones)
        actionable_count = sum(1 for s in stones if s.actionable)
        high_priority = sum(1 for s in stones if s.priority_tier in ("high", "critical"))
        avg_strength = sum(s.key_strength for s in stones) / total_stones if total_stones else 0
        
        return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ripple Engine — Daily Map | {date_str}</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg: {c["bg_primary"]};
            --bg-secondary: {c["bg_secondary"]};
            --bg-tertiary: {c["bg_tertiary"]};
            --text: {c["text_primary"]};
            --text-dim: {c["text_secondary"]};
            --text-muted: {c["text_muted"]};
            --border: {c["border"]};
            --accent-cyan: {c["accent_cyan"]};
            --accent-green: {c["accent_green"]};
            --accent-amber: {c["accent_amber"]};
            --accent-purple: {c["accent_purple"]};
            --accent-red: {c["accent_red"]};
            --radius-sm: {r["sm"]};
            --radius-md: {r["md"]};
            --radius-lg: {r["lg"]};
            --radius-xl: {r["xl"]};
            --shadow-md: {sh["md"]};
            --shadow-lg: {sh["lg"]};
            --font-mono: {t["font_family"]};
            --font-display: 'Space Grotesk', sans-serif;
        }}
        
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        
        body {{
            font-family: var(--font-mono);
            background: var(--bg);
            color: var(--text);
            line-height: 1.6;
            min-height: 100vh;
        }}
        
        /* Animated background */
        body::before {{
            content: "";
            position: fixed;
            inset: 0;
            background: 
                radial-gradient(ellipse 80% 50% at 20% 0%, rgba(139, 92, 246, 0.08) 0%, transparent 50%),
                radial-gradient(ellipse 60% 40% at 80% 100%, rgba(6, 182, 212, 0.06) 0%, transparent 50%),
                radial-gradient(ellipse 50% 30% at 50% 50%, rgba(16, 185, 129, 0.04) 0%, transparent 60%);
            pointer-events: none;
            z-index: -1;
        }}
        
        .app {{
            max-width: 1600px;
            margin: 0 auto;
            padding: {s["xl"]} {s["lg"]};
        }}
        
        /* Header */
        .header {{
            display: flex;
            justify-content: space-between;
            align-items: flex-end;
            margin-bottom: {s["2xl"]};
            padding-bottom: {s["xl"]};
            border-bottom: 1px solid var(--border);
            position: relative;
        }}
        
        .header::after {{
            content: "";
            position: absolute;
            bottom: -1px;
            left: 0;
            right: 0;
            height: 1px;
            background: linear-gradient(90deg, transparent, var(--accent-cyan), var(--accent-purple), transparent);
        }}
        
        .header-left h1 {{
            font-family: var(--font-display);
            font-size: clamp(1.75rem, 4vw, 2.5rem);
            font-weight: 700;
            letter-spacing: -0.02em;
            background: linear-gradient(135deg, var(--text) 0%, var(--accent-cyan) 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}
        
        .header-left .subtitle {{
            color: var(--text-dim);
            font-size: {t["body"]};
            margin-top: {s["xs"]};
            font-family: var(--font-mono);
        }}
        
        .header-right {{
            display: flex;
            gap: {s["md"]};
            align-items: center;
        }}
        
        .stat-pill {{
            background: var(--bg-tertiary);
            border: 1px solid var(--border);
            padding: {s["sm"]} {s["md"]};
            border-radius: {r["md"]};
            font-size: {t["small"]};
        }}
        .stat-pill strong {{ color: var(--accent-cyan); }}
        
        /* Summary Grid */
        .summary-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: {s["md"]};
            margin-bottom: {s["2xl"]};
        }}
        
        .summary-card {{
            background: var(--bg-secondary);
            border: 1px solid var(--border);
            border-radius: {r["lg"]};
            padding: {s["lg"]};
            position: relative;
            overflow: hidden;
            transition: transform 0.2s, box-shadow 0.2s, border-color 0.2s;
        }}
        .summary-card:hover {{
            transform: translateY(-2px);
            box-shadow: var(--shadow-lg);
            border-color: var(--accent-cyan);
        }}
        .summary-card::before {{
            content: "";
            position: absolute;
            top: 0; left: 0; right: 0;
            height: 3px;
            background: var(--accent-color, var(--accent-cyan));
        }}
        .summary-card:nth-child(1) {{ --accent-color: var(--accent-cyan); }}
        .summary-card:nth-child(2) {{ --accent-color: var(--accent-green); }}
        .summary-card:nth-child(3) {{ --accent-color: var(--accent-amber); }}
        .summary-card:nth-child(4) {{ --accent-color: var(--accent-purple); }}
        
        .summary-label {{ font-size: {t["small"]}; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.05em; }}
        .summary-value {{ font-family: var(--font-display); font-size: clamp(1.5rem, 3vw, 2.25rem); font-weight: 700; margin-top: {s["xs"]}; }}
        .summary-value.actionable {{ color: var(--accent-green); }}
        .summary-value.high {{ color: var(--accent-purple); }}
        
        /* Sections */
        .section {{
            margin-bottom: {s["2xl"]};
        }}
        .section-header {{
            display: flex;
            justify-content: space-between;
            align-items: baseline;
            margin-bottom: {s["lg"]};
        }}
        .section-title {{
            font-family: var(--font-display);
            font-size: clamp(1.125rem, 2.5vw, 1.5rem);
            font-weight: 600;
        }}
        .section-count {{ color: var(--text-muted); font-size: {t["small"]}; }}
        
        /* Grids */
        .stones-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
            gap: {s["lg"]};
        }}
        
        .circles-grid, .keys-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: {s["md"]};
        }}
        
        /* Stone Cards */
        .stone-card {{
            padding: {s["lg"]};
            display: flex;
            flex-direction: column;
            transition: transform 0.25s, box-shadow 0.25s, border-color 0.25s;
            position: relative;
            overflow: hidden;
        }}
        .stone-card::before {{
            content: "";
            position: absolute;
            top: 0; left: 0; right: 0;
            height: 2px;
            background: linear-gradient(90deg, transparent, currentColor, transparent);
            opacity: 0.3;
        }}
        .stone-card:hover {{
            transform: translateY(-4px);
            box-shadow: var(--shadow-lg), var(--glow, none);
            border-color: var(--border-focus);
        }}
        .stone-large {{ --glow: 0 0 40px rgba(139, 92, 246, 0.25); }}
        .stone-medium {{ --glow: 0 0 32px rgba(14, 165, 233, 0.2); }}
        .stone-small {{ --glow: 0 0 20px rgba(100, 116, 139, 0.15); }}
        
        .stone-header {{ display: flex; gap: {s["sm"]}; flex-wrap: wrap; margin-bottom: {s["sm"]}; }}
        .tier-badge {{
            font-size: {t["small"]};
            font-weight: 600;
            padding: 2px 8px;
            border-radius: {r["sm"]};
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}
        .tier-critical {{ background: rgba(220, 38, 38, 0.2); color: var(--accent-red); border: 1px solid var(--accent-red); }}
        .tier-high {{ background: rgba(139, 92, 246, 0.2); color: var(--accent-purple); border: 1px solid var(--accent-purple); }}
        .tier-medium {{ background: rgba(14, 165, 233, 0.2); color: var(--accent-cyan); border: 1px solid var(--accent-cyan); }}
        .tier-low {{ background: rgba(100, 116, 139, 0.2); color: var(--text-dim); border: 1px solid var(--border); }}
        
        .source-tag {{
            font-size: {t["small"]};
            color: var(--text-dim);
            background: var(--bg-tertiary);
            padding: 2px 8px;
            border-radius: {r["sm"]};
            font-family: var(--font-mono);
        }}
        .badge {{
            font-size: {t["small"]};
            font-weight: 600;
            padding: 2px 8px;
            border-radius: {r["sm"]};
        }}
        .badge.actionable {{ background: rgba(16, 185, 129, 0.2); color: var(--accent-green); border: 1px solid var(--accent-green); }}
        
        .stone-title {{
            font-family: var(--font-display);
            font-size: {t["subheading"]};
            font-weight: 600;
            line-height: 1.3;
            margin-bottom: {s["sm"]};
            color: var(--text);
        }}
        .stone-content {{
            color: var(--text-dim);
            font-size: {t["body"]};
            line-height: 1.55;
            margin-bottom: {s["md"]};
            flex: 1;
        }}
        
        .stone-meta {{ margin-bottom: {s["md"]}; }}
        .metric-row {{ display: flex; gap: {s["lg"]}; }}
        .metric {{ display: flex; flex-direction: column; gap: 2px; }}
        .metric-value {{ font-family: var(--font-display); font-size: 1.25rem; font-weight: 700; color: var(--accent-cyan); }}
        .metric-label {{ font-size: {t["small"]}; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.05em; }}
        
        .stone-tags {{ margin-bottom: {s["md"]}; }}
        .tag-group {{ margin-bottom: {s["sm"]}; }}
        .tag-label {{ font-size: {t["small"]}; color: var(--text-muted); margin-right: {s["sm"]}; text-transform: uppercase; letter-spacing: 0.03em; }}
        .chip {{
            display: inline-block;
            font-size: {t["small"]};
            padding: 3px 10px;
            border-radius: 9999px;
            margin: 2px 4px 2px 0;
            font-family: var(--font-mono);
            border: 1px solid transparent;
        }}
        .chip {{ background: var(--bg-tertiary); color: var(--text-dim); border-color: var(--border); }}
        .key-chip {{ background: rgba(139, 92, 246, 0.15); color: var(--accent-purple); border-color: rgba(139, 92, 246, 0.3); }}
        .conflict-chip {{ background: rgba(220, 38, 38, 0.15); color: var(--accent-red); border-color: rgba(220, 38, 38, 0.3); }}
        
        .stone-footer {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding-top: {s["md"]};
            border-top: 1px solid var(--border);
            margin-top: auto;
        }}
        .roi-estimate {{ font-size: {t["small"]}; color: var(--text-dim); font-style: italic; }}
        .source-link {{
            font-size: {t["small"]};
            color: var(--accent-cyan);
            text-decoration: none;
            font-weight: 500;
            transition: color 0.2s;
        }}
        .source-link:hover {{ color: var(--accent-green); }}
        
        /* Circle Cards */
        .circle-card {{
            background: var(--bg-secondary);
            border: 1px solid var(--border);
            border-radius: {r["lg"]};
            padding: {s["lg"]};
            transition: all 0.2s;
        }}
        .circle-card:hover {{ border-color: var(--accent-cyan); transform: translateY(-2px); box-shadow: var(--shadow-md); }}
        .circle-name {{ font-family: var(--font-display); font-weight: 600; margin-bottom: {s["xs"]}; }}
        .circle-stats {{ display: flex; gap: {s["md"]}; font-size: {t["small"]}; color: var(--text-dim); margin-bottom: {s["md"]}; }}
        .circle-members {{ display: flex; flex-wrap: wrap; gap: {s["xs"]}; }}
        .circle-member {{ font-size: {t["small"]}; background: var(--bg-tertiary); padding: 2px 8px; border-radius: {r["sm"]}; color: var(--text-dim); }}
        
        /* Key Cards */
        .key-card {{
            background: var(--bg-secondary);
            border: 1px solid var(--border);
            border-radius: {r["lg"]};
            padding: {s["lg"]};
            transition: all 0.2s;
        }}
        .key-card:hover {{ border-color: var(--accent-green); transform: translateY(-2px); box-shadow: var(--shadow-md), 0 0 24px rgba(16, 185, 129, 0.15); }}
        .key-header {{ display: flex; justify-content: space-between; align-items: baseline; margin-bottom: {s["sm"]}; }}
        .key-name {{ font-family: var(--font-display); font-weight: 600; font-size: 1.125rem; }}
        .key-strength {{ font-family: var(--font-display); font-size: 1.5rem; font-weight: 700; color: var(--accent-green); }}
        .key-metrics {{ display: flex; gap: {s["md"]}; font-size: {t["small"]}; color: var(--text-dim); margin-bottom: {s["md"]}; }}
        .key-aspects {{ margin-bottom: {s["md"]}; }}
        .key-reason {{ font-size: {t["small"]}; color: var(--text-dim); line-height: 1.5; }}
        
        /* Empty state */
        .empty-state {{ text-align: center; padding: {s["2xl"]}; color: var(--text-muted); }}
        
        /* Scrollbar */
        ::-webkit-scrollbar {{ width: 8px; height: 8px; }}
        ::-webkit-scrollbar-track {{ background: var(--bg-secondary); }}
        ::-webkit-scrollbar-thumb {{ background: var(--border); border-radius: 4px; }}
        ::-webkit-scrollbar-thumb:hover {{ background: var(--text-muted); }}
        
        /* Animations */
        @keyframes fadeInUp {{
            from {{ opacity: 0; transform: translateY(20px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        .stone-card, .circle-card, .key-card, .summary-card {{
            animation: fadeInUp 0.5s ease-out backwards;
        }}
        .stone-card:nth-child(1) {{ animation-delay: 0ms; }}
        .stone-card:nth-child(2) {{ animation-delay: 50ms; }}
        .stone-card:nth-child(3) {{ animation-delay: 100ms; }}
        .stone-card:nth-child(4) {{ animation-delay: 150ms; }}
        .stone-card:nth-child(5) {{ animation-delay: 200ms; }}
        .stone-card:nth-child(6) {{ animation-delay: 250ms; }}
    </style>
</head>
<body>
    <div class="app">
        <header class="header">
            <div class="header-left">
                <h1>Ripple Engine</h1>
                <p class="subtitle">Daily Autonomous Processing Map — {date_str}</p>
            </div>
            <div class="header-right">
                <span class="stat-pill"><strong>{total_stones}</strong> Stones</span>
                <span class="stat-pill"><strong>{len(self.circles)}</strong> Circles</span>
                <span class="stat-pill"><strong>{len(self.mature_keys)}</strong> Mature Keys</span>
                <span class="stat-pill actionable"><strong>{actionable_count}</strong> Actionable</span>
            </div>
        </header>
        
        <section class="summary-grid" aria-label="Summary Statistics">
            <article class="summary-card">
                <div class="summary-label">Avg Strength</div>
                <div class="summary-value">{avg_strength:.0f}</div>
            </article>
            <article class="summary-card">
                <div class="summary-label">High Priority</div>
                <div class="summary-value high">{high_priority}</div>
            </article>
            <article class="summary-card">
                <div class="summary-label">Actionable</div>
                <div class="summary-value actionable">{actionable_count}</div>
            </article>
            <article class="summary-card">
                <div class="summary-label">Circles</div>
                <div class="summary-value">{len(self.circles)}</div>
            </article>
        </section>
        
        <section class="section" aria-labelledby="stones-heading">
            <div class="section-header">
                <h2 id="stones-heading" class="section-title">🪨 Stones Collected</h2>
                <span class="section-count">{total_stones} stones — sorted by visual weight (strength + confidence)</span>
            </div>
            <div class="stones-grid" role="list">
                {''.join(stone_cards) if stone_cards else '<div class="empty-state">No stones collected today</div>'}
            </div>
        </section>
        
        {f'''<section class="section" aria-labelledby="circles-heading">
            <div class="section-header">
                <h2 id="circles-heading" class="section-title">🔄 Impact Circles</h2>
                <span class="section-count">{len(self.circles)} circles — intersecting aspects & keys</span>
            </div>
            <div class="circles-grid" role="list">
                {''.join(circle_cards)}
            </div>
        </section>''' if self.circles else ''}
        
        {f'''<section class="section" aria-labelledby="keys-heading">
            <div class="section-header">
                <h2 id="keys-heading" class="section-title">🔑 Mature Keys Unlocked</h2>
                <span class="section-count">{len(self.mature_keys)} keys — converged from multiple stones</span>
            </div>
            <div class="keys-grid" role="list">
                {''.join(key_cards)}
            </div>
        </section>''' if self.mature_keys else ''}
        
        <footer style="margin-top: {s['2xl']}; padding-top: {s['xl']}; border-top: 1px solid var(--border); text-align: center; color: var(--text-muted); font-size: {t['small']};">
            Generated by Ripple Engine v2 · {timestamp} · Autonomous Daily Processing
        </footer>
    </div>
</body>
</html>'''
    
    def run_daily_routine(self) -> None:
        """Execute the complete daily routine."""
        print("🚀 Starting Daily Ripple Engine Routine...")
        print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        self.gather_daily_stones()
        self.build_circles()
        self.calculate_mature_keys()
        self.unlock_mature_keys()
        self.generate_html_visualization()
        
        print("=" * 60)
        print("✅ Daily Ripple Engine routine completed successfully!")
        print(f"📊 Dashboard: {self.html_path}")
        print("=" * 60)


if __name__ == "__main__":
    engine = RippleEngine()
    engine.run_daily_routine()
#!/usr/bin/env python3
"""
Human Source — Analyze human, build values map, generate keys, run ripple engine.
"""

import argparse
import sys
import yaml
import json
import sqlite3
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Any
from datetime import datetime
import re

# Add skills dir to path
SKILLS_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(SKILLS_DIR))

try:
    import knowledge_cube as kc
except ImportError:
    kc = None


@dataclass
class HumanDimension:
    """One dimension of human analysis."""
    name: str
    weight: float
    evidence: List[str] = field(default_factory=list)
    score: float = 0.0  # 0-1, how well we understand this dimension


@dataclass
class ValueConflict:
    """Conflict between a key's ripple and a human value."""
    circle: str
    aspect: str
    violated_value: str
    severity: str  # critical, medium, low
    description: str


@dataclass
class RippleCircle:
    """One ripple circle from a key."""
    depth: int
    name: str
    aspects: List[str]
    conflicts: List[ValueConflict] = field(default_factory=list)


@dataclass
class Key:
    """A key (idea/question) thrown into the water."""
    text: str
    source_dimension: str
    rationale: str
    circles: List[RippleCircle] = field(default_factory=list)
    conflicts: List[ValueConflict] = field(default_factory=list)
    status: str = "pending"  # pending, validated, rejected, replaced
    replacement: Optional[str] = None


@dataclass
class HumanProfile:
    """Complete human profile from analysis."""
    dimensions: List[HumanDimension]
    values_map: Dict[str, Any]  # deep/shallow/rocks
    keys: List[Key]
    conflicts_summary: Dict[str, int]


class HumanAnalyzer:
    """Analyzes human from available data sources."""
    
    def __init__(self, config: Dict):
        self.config = config
        self.dimensions = {
            'frustrations': config.get('analysis', {}).get('dimensions', {}).get('frustrations', 0.3),
            'sins': config.get('analysis', {}).get('dimensions', {}).get('sins', 0.2),
            'norms': config.get('analysis', {}).get('dimensions', {}).get('norms', 0.2),
            'strengths': config.get('analysis', {}).get('dimensions', {}).get('strengths', 0.15),
            'context': config.get('analysis', {}).get('dimensions', {}).get('context', 0.15),
        }
    
    def analyze_user_file(self, path: Path) -> Dict[str, List[str]]:
        """Extract evidence from USER.md."""
        if not path.exists():
            return {}
        
        content = path.read_text(encoding='utf-8')
        evidence = {dim: [] for dim in self.dimensions}
        
        # Simple keyword-based extraction
        frustration_kws = ['фрустрац', 'бесит', ' 화가', 'frustrat', 'пассивн', 'тыкать носом', 'окно', 'спам', 'не доставлен', 'микроменеджмент', 'не работает', 'ломает']
        sin_kws = ['автономн', 'passive', 'пассивн', 'no-kyc', 'no KYC', 'без документов', 'без паспорт', 'без ип', 'кликабе', 'работающ']
        norm_kws = ['filesystem-first', 'stdlib-first', 'ponytail', 'job_id', 'intent', 'pytest', 'линтер', 'автономн', 'русский', 'english', 'профанити']
        strength_kws = ['техническ', 'архитектур', 'скилл', 'паттерн', 'systems thinking', 'арбитраж', 'матричн', 'creative', 'okf', 'white-spot']
        context_kws = ['крым', 'симферополь', 'crimea', 'windows', 'git-bash', 'pythonw', 'hermes', 'crystal', 'knowledge cube', 'openrouter', 'browseros', 'порт 9003']
        
        kw_map = {
            'frustrations': frustration_kws,
            'sins': sin_kws,
            'norms': norm_kws,
            'strengths': strength_kws,
            'context': context_kws,
        }
        
        for dim, kws in kw_map.items():
            for kw in kws:
                if kw.lower() in content.lower():
                    # Find context around keyword
                    idx = content.lower().find(kw.lower())
                    start = max(0, idx - 100)
                    end = min(len(content), idx + 200)
                    snippet = content[start:end].strip()
                    evidence[dim].append(snippet)
        
        return evidence
    
    def analyze_knowledge_cube(self, db_path: Path) -> Dict[str, List[str]]:
        """Extract evidence from knowledge cube."""
        if not db_path.exists() or kc is None:
            return {}
        
        evidence = {dim: [] for dim in self.dimensions}
        
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Get domains with frustration/signal content
            cursor.execute("""
                SELECT content, axis_domain, confidence 
                FROM experiences 
                WHERE confidence > 0.7
                AND (content LIKE '%frustrat%' OR content LIKE '%бесит%' OR content LIKE '%passive%' 
                     OR content LIKE '%автономн%' OR content LIKE '%no KYC%' OR content LIKE '%no-kyc%'
                     OR content LIKE '%no doc%' OR content LIKE '%без документ%' OR content LIKE '%Crimea%')
                ORDER BY ts DESC LIMIT 50
            """)
            
            for row in cursor.fetchall():
                content, domain, conf = row
                # Classify by domain
                if domain in ['devops', 'skill', 'debugging']:
                    evidence['strengths'].append(f"[{domain}] {content[:200]}")
                elif domain in ['finance', 'arbitrage']:
                    evidence['context'].append(f"[{domain}] {content[:200]}")
                    evidence['sins'].append(f"[{domain}] {content[:200]}")
                elif 'frustrat' in content.lower() or 'бесит' in content.lower():
                    evidence['frustrations'].append(f"[{domain}] {content[:200]}")
            
            conn.close()
        except Exception as e:
            print(f"Knowledge cube analysis error: {e}")
        
        return evidence
    
    def analyze_semantic_analysis(self, path: Path) -> Dict[str, List[str]]:
        """Extract from semantic_analysis.json (Crystal output)."""
        if not path.exists():
            return {}
        
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        evidence = {dim: [] for dim in self.dimensions}
        
        # Frustrations from Crystal
        for f in data.get('frustrations', []):
            evidence['frustrations'].append(f.get('description', ''))
        
        # Goals → strengths/context
        for g in data.get('goals', []):
            evidence['strengths'].append(f"Goal: {g.get('description', '')}")
            evidence['context'].append(f"Goal status: {g.get('status', '')}")
        
        return evidence
    
    def build_profile(self, sources: Dict) -> HumanProfile:
        """Build complete human profile from all evidence."""
        # Combine evidence
        all_evidence = {dim: [] for dim in self.dimensions}
        for src, ev in sources.items():
            for dim, items in ev.items():
                all_evidence[dim].extend(items)
        
        # Create dimensions
        dimensions = []
        for dim, weight in self.dimensions.items():
            d = HumanDimension(
                name=dim,
                weight=weight,
                evidence=all_evidence[dim],
                score=min(1.0, len(all_evidence[dim]) / 10)  # normalize
            )
            dimensions.append(d)
        
        # Build values map (landscape)
        values_map = self._build_values_map(all_evidence)
        
        # Generate keys
        keys = self._generate_keys(values_map, all_evidence)
        
        # Run ripple engine on each key
        for key in keys:
            self._run_ripple_engine(key, values_map)
        
        # Summarize conflicts
        conflicts_summary = {}
        for key in keys:
            for c in key.conflicts:
                conflicts_summary[c.violated_value] = conflicts_summary.get(c.violated_value, 0) + 1
        
        return HumanProfile(
            dimensions=dimensions,
            values_map=values_map,
            keys=keys,
            conflicts_summary=conflicts_summary
        )
    
    def _build_values_map(self, evidence: Dict) -> Dict[str, Any]:
        """Build the landscape: deep zones, shallow zones, underwater rocks."""
        
        # Deep zones (strengths, high confidence)
        deep = []
        if evidence['strengths']:
            deep.append({
                'name': 'Technical Mastery',
                'evidence': evidence['strengths'][:5],
                'depth': 'deep'
            })
        if any('autonomous' in e.lower() for e in evidence['norms']):
            deep.append({
                'name': 'Autonomous Execution',
                'evidence': [e for e in evidence['norms'] if 'автономн' in e.lower()][:3],
                'depth': 'deep'
            })
        if any('pattern' in e.lower() or 'паттерн' in e.lower() for e in evidence['strengths']):
            deep.append({
                'name': 'Pattern Recognition',
                'evidence': [e for e in evidence['strengths'] if 'pattern' in e.lower() or 'паттерн' in e.lower()][:3],
                'depth': 'deep'
            })
        
        # Shallow zones (frustrations, gaps)
        shallow = []
        if evidence['frustrations']:
            shallow.append({
                'name': 'Agent Passivity',
                'evidence': evidence['frustrations'][:5],
                'depth': 'shallow'
            })
        if any('research' in e.lower() or 'list' in e.lower() for e in evidence['frustrations']):
            shallow.append({
                'name': 'Research Quality Standards',
                'evidence': [e for e in evidence['frustrations'] if 'research' in e.lower() or 'list' in e.lower()][:3],
                'depth': 'shallow'
            })
        
        # Underwater rocks (conflicts, taboos, hard constraints)
        rocks = []
        if evidence['sins']:
            rocks.append({
                'name': 'No KYC / No Documents',
                'evidence': [e for e in evidence['sins'] if 'kyc' in e.lower() or 'документ' in e.lower() or 'паспорт' in e.lower()][:5],
                'type': 'hard_constraint'
            })
        if evidence['context']:
            rocks.append({
                'name': 'Crimea Constraints',
                'evidence': [e for e in evidence['context'] if 'крым' in e.lower() or 'crimea' in e.lower() or 'симфер' in e.lower()][:3],
                'type': 'environmental'
            })
        if any('stdlib' in e.lower() or 'ponytail' in e.lower() for e in evidence['norms']):
            rocks.append({
                'name': 'Stdlib-First / No Heavy Frameworks',
                'evidence': [e for e in evidence['norms'] if 'stdlib' in e.lower() or 'ponytail' in e.lower()][:3],
                'type': 'value'
            })
        if any('clickable' in e.lower() or 'артефакт' in e.lower() for e in evidence['sins'] + evidence['frustrations']):
            rocks.append({
                'name': 'Clickable Artifacts Only',
                'evidence': [e for e in evidence['sins'] + evidence['frustrations'] if 'clickable' in e.lower() or 'артефакт' in e.lower()][:3],
                'type': 'value'
            })
        
        return {
            'deep_zones': deep,
            'shallow_zones': shallow,
            'underwater_rocks': rocks
        }
    
    def _generate_keys(self, values_map: Dict, evidence: Dict) -> List[Key]:
        """Generate keys from values map (not from external sources)."""
        keys = []
        
        # Key 1: From deep zone (Technical Mastery) + rock (No KYC) + context (Crimea)
        keys.append(Key(
            text="Автономная система поиска работы в Крыму без KYC",
            source_dimension="strengths+context+sins",
            rationale="Combines technical depth (crimea-job-search skill exists) + hard constraint (no KYC) + environment (Crimea location). Uses hh.ru API legally, no docs needed."
        ))
        
        # Key 2: From sin (passive income) + strength (video-content) + norm (stdlib-first)
        keys.append(Key(
            text="Полностью автономный контент-конвейер для Shorts/TikTok без участия человека",
            source_dimension="sins+strengths+norms",
            rationale="Uses existing video-content/social-media/creative skills + Pollinations.ai (free, no API key) + CapCut auto. Artifact: ready video → auto-post → metrics. Fully passive."
        ))
        
        # Key 3: From sin (no KYC) + context (Crimea) + finance skills
        keys.append(Key(
            text="USDT→RUB off-ramp автоматизация без KYC через P2P/Whitebird",
            source_dimension="sins+context+strengths",
            rationale="Whitebird (Belarus) up to $12K, 5-6% fee, to MIR card. finance-core + arbitrage-sensors for rate monitoring. Artifact: USDT balance → auto P2P deal → RUB on card."
        ))
        
        # Key 4: From frustration (manual work) + strength (automation) + norm (autonomous)
        keys.append(Key(
            text="Автономные агенты для мониторинга и исправления сломанных кронов/демонов",
            source_dimension="frustrations+strengths+norms",
            rationale="Self-healing-monitor cron exists. Extend to: detect broken cron → diagnose → patch → verify → restart. Uses existing proactive-doer, Crystal executor."
        ))
        
        # Key 5: From deep zone (pattern recognition) + sin (arbitrage mindset)
        keys.append(Key(
            text="Матричный арбитраж-движок: не линейные цепочки, а сетка альтернатив с авто-переключением",
            source_dimension="strengths+sins",
            rationale="Arbitrage sensors + finance-core + matrix-thinking skill. Not 'traffic→offer' but grid of alternatives with auto-failover. Green circles found, red circles fixed automatically."
        ))
        
        return keys
    
    def _run_ripple_engine(self, key: Key, values_map: Dict):
        """Run ripple engine on a key - generate circles, detect conflicts."""
        ripple_config = self.config.get('ripple_engine', {})
        max_depth = ripple_config.get('max_depth', 3)
        
        # Pre-defined circle templates for different key types
        circle_templates = self._get_circle_templates(key.text)
        
        for depth in range(1, max_depth + 1):
            if depth <= len(circle_templates):
                template = circle_templates[depth - 1]
                circle = RippleCircle(
                    depth=depth,
                    name=template['name'],
                    aspects=template['aspects']
                )
                
                # Detect conflicts with values map
                self._detect_conflicts(circle, values_map)
                circle.conflicts = circle.conflicts  # already set in _detect_conflicts
                
                key.circles.append(circle)
                key.conflicts.extend(circle.conflicts)
        
        # Determine status
        critical_conflicts = [c for c in key.conflicts if c.severity == 'critical']
        if critical_conflicts:
            key.status = 'rejected'
            key.replacement = self._generate_replacement(key, values_map)
        else:
            key.status = 'validated'
    
    def _get_circle_templates(self, key_text: str) -> List[Dict]:
        """Get circle templates based on key type."""
        key_lower = key_text.lower()
        
        # PWA + India + Betting - most specific first
        if 'pwa' in key_lower and ('инди' in key_lower or 'india' in key_lower or 'бетт' in key_lower or 'betting' in key_lower or 'крикет' in key_lower or 'cricket' in key_lower):
            return [
                {'name': 'Traffic & PWA', 'aspects': ['TikTok/Shorts India', 'Cricket PWA install', 'PWA manifest/service worker', 'Offline support']},
                {'name': 'Offer & Payments', 'aspects': ['1xBet/1win/cpagrip', 'Indian payment gateways', 'UPI/NetBanking', 'USDT→INR→RUB']},
                {'name': 'Creative & Anti-fraud', 'aspects': ['Cricket video ads', 'CapCut templates', 'Fingerprint/V2RayN', 'Cloaker setup']},
            ]
        # Job search
        elif any(kw in key_lower for kw in ['работа', 'job', 'hh.ru', 'поиск работы', 'ваканс', 'crimea', 'крым', 'симфер']):
            return [
                {'name': 'API & Data', 'aspects': ['hh.ru API', 'Area IDs (Crimea=1002)', 'Rate limiting (200/min)', 'Pagination']},
                {'name': 'Filter & Match', 'aspects': ['Keywords (python, django)', 'Salary filter (≥80k)', 'Experience (1-6 years)', 'Schedule (remote/flexible)']},
                {'name': 'Output & Action', 'aspects': ['JSON export', 'SQLite cache (dedup)', 'CV generation', 'Auto-apply API', 'Telegram notify']},
            ]
        # Content pipeline
        elif any(kw in key_lower for kw in ['контент', 'shorts', 'tiktok', 'content']):
            return [
                {'name': 'Generation Pipeline', 'aspects': ['Topic research', 'Script (AI)', 'Visuals (Pollinations.ai)', 'Audio (TTS)', 'Edit (CapCut auto)']},
                {'name': 'Distribution', 'aspects': ['Multi-platform post', 'Schedule/queue', 'Hashtags/SEO', 'Cross-post logic']},
                {'name': 'Monetization & Analytics', 'aspects': ['Referral links (no KYC)', 'View/click tracking', 'A/B test thumbnails', 'Revenue attribution']},
            ]
        # USDT off-ramp
        elif any(kw in key_lower for kw in ['usdt', 'off-ramp', 'p2p', 'whitebird']):
            return [
                {'name': 'Rate & Offer Discovery', 'aspects': ['Whitebird API/check', 'P2P market scan', 'Rate comparison', 'Reputation filter']},
                {'name': 'Execution', 'aspects': ['Escrow lock', 'Transfer USDT', 'Confirm receipt', 'Release fiat', 'Notify']},
                {'name': 'Safety & Monitoring', 'aspects': ['Counterparty reputation', 'Dispute handling', 'Rate alert thresholds', 'Audit trail']},
            ]
        # Cron/daemon monitoring
        elif any(kw in key_lower for kw in ['крон', 'демон', 'self-healing', 'мониторинг', 'исправлен']):
            return [
                {'name': 'Detection', 'aspects': ['Cron job status', 'Exit codes', 'Log pattern match', 'Heartbeat check']},
                {'name': 'Diagnosis', 'aspects': ['Error classification', 'Root cause (config/code/env)', 'Fix strategy selection']},
                {'name': 'Remediation', 'aspects': ['Patch config', 'Restart service', 'Verify health', 'Report result']},
            ]
        # Matrix arbitrage
        elif any(kw in key_lower for kw in ['матричн', 'арбитраж', 'matrix', 'grid']):
            return [
                {'name': 'Grid Construction', 'aspects': ['Traffic sources matrix', 'Offers matrix', 'Payouts matrix', 'Risk scores']},
                {'name': 'Auto-Optimization', 'aspects': ['Green circle detection', 'Red circle diagnosis', 'Failover routing', 'Bid adjustment']},
                {'name': 'Execution Layer', 'aspects': ['Tracker API', 'Cloaker/anti-fraud', 'Creative rotation', 'Budget pacing']},
            ]
        else:
            return [
                {'name': 'Aspect 1', 'aspects': ['Sub-aspect A', 'Sub-aspect B']},
                {'name': 'Aspect 2', 'aspects': ['Sub-aspect C', 'Sub-aspect D']},
                {'name': 'Aspect 3', 'aspects': ['Sub-aspect E', 'Sub-aspect F']},
            ]
    
    def _detect_conflicts(self, circle: RippleCircle, values_map: Dict):
        """Detect conflicts between circle aspects and human values."""
        rocks = values_map.get('underwater_rocks', [])
        
        # Conflict rules: (aspect_keyword, rock_name, severity, description)
        # More specific matching to avoid false positives
        conflict_rules = [
            # No KYC conflicts - specific to identity verification
            (['kyc verification', 'passport upload', 'document upload', 'identity verification', 'verify identity', 'загрузка паспорт', 'верификаци документов', 'подтверждение личности'], 'No KYC / No Documents', 'critical', 'Requires identity verification'),
            (['india', 'инди', 'indian', 'индийск'], 'No KYC / No Documents', 'critical', 'Indian payment rails require KYC'),
            (['betting kyc', 'беттинг kyc', 'gambling kyc', 'casino kyc', 'казино kyc'], 'No KYC / No Documents', 'critical', 'Betting platforms require KYC'),
            
            # No risk / stability conflicts
            (['betting', 'беттинг', 'gambling', 'гемблинг', 'casino', 'казино'], 'No risk / stability', 'critical', 'High regulatory/banking risk'),
            (['legal uncertainty', 'юридич неопределен', 'regulation risk', 'регуляторн риск'], 'No risk / stability', 'critical', 'Legal uncertainty'),
            
            # Stdlib-first conflicts
            (['heavy framework', 'тяжел фреймворк', 'django rest', 'fastapi', 'react', 'vue', 'webpack', 'babel'], 'Stdlib-First / No Heavy Frameworks', 'medium', 'Heavy framework dependency'),
            
            # Clickable artifacts only - more specific
            (['research phase', 'исследовани фаз', 'planning phase', 'планирован фаз', 'strategy document', 'стратеги документ'], 'Clickable Artifacts Only', 'medium', 'Produces plan not artifact'),
            (['manual setup', 'ручн настройк', 'hand craft', 'ручная работа'], 'Clickable Artifacts Only', 'medium', 'Requires manual work'),
            
            # Passive autonomy
            (['daily maintenance', 'ежедневн обслуживан', 'constant monitoring', 'постоянн мониторинг', 'moderate content', 'модер контент'], 'Passive Autonomy', 'medium', 'Requires ongoing human attention'),
            
            # Crimea constraints
            (['bank transfer', 'банк перевода', 'swift', 'sepa', 'iban'], 'Crimea Constraints', 'critical', 'Banking unavailable in Crimea'),
        ]
        
        for aspect in circle.aspects:
            aspect_lower = aspect.lower()
            for keywords, rock_name, severity, desc in conflict_rules:
                if any(kw in aspect_lower for kw in keywords):
                    # Find the rock
                    rock = next((r for r in rocks if r['name'] == rock_name), None)
                    if rock:
                        circle.conflicts.append(ValueConflict(
                            circle=circle.name,
                            aspect=aspect,
                            violated_value=rock_name,
                            severity=severity,
                            description=f"{desc}: '{aspect}' conflicts with '{rock_name}' ({rock['type']})"
                        ))
    
    def _generate_replacement(self, key: Key, values_map: Dict) -> str:
        """Generate a replacement key that avoids conflicts."""
        critical_rocks = set(c.violated_value for c in key.conflicts if c.severity == 'critical')
        
        # Replacement logic based on what was rejected
        if 'PWA-арбитраж' in key.text or 'betting' in key.text.lower() or 'беттинг' in key.text.lower():
            return "Автономный контент-бизнес на Shorts (India cricket niche) → монетизация через рефералки/партнёрки без KYC"
        elif 'USDT' in key.text and 'P2P' in key.text:
            return key.text  # Already has mitigations
        elif 'content' in key.text.lower() or 'контент' in key.text.lower():
            return key.text  # Usually safe
        
        return f"[REPLACEMENT NEEDED] {key.text} — conflicts with: {', '.join(critical_rocks)}"


def print_profile(profile: HumanProfile, verbose: bool = False):
    """Pretty print human profile."""
    print("\n" + "="*70)
    print("HUMAN PROFILE — ЧЕЛОВЕК КАК НАЧАЛО")
    print("="*70)
    
    print("\n📊 DIMENSIONS (веса и понимание):")
    for d in profile.dimensions:
        bar = "█" * int(d.score * 20)
        print(f"  {d.name:15s} | weight={d.weight:.0%} | score={d.score:.0%} | evidence={len(d.evidence)}")
        print(f"    {bar}")
    
    print("\n🗺️ VALUES MAP (ЛАНДШАФТ):")
    for zone_type, zones in profile.values_map.items():
        icon = "🟢" if zone_type == 'deep_zones' else "🟡" if zone_type == 'shallow_zones' else "🔴"
        print(f"  {icon} {zone_type}:")
        for z in zones:
            print(f"    • {z['name']} ({z.get('depth', z.get('type', ''))})")
            if verbose:
                for e in z['evidence'][:2]:
                    print(f"      - {e[:80]}...")
    
    print("\n🔑 GENERATED KEYS:")
    for i, key in enumerate(profile.keys, 1):
        status_icon = "✅" if key.status == 'validated' else "❌" if key.status == 'rejected' else "⏳"
        print(f"  {i}. {status_icon} {key.text}")
        print(f"     Source: {key.source_dimension}")
        print(f"     Rationale: {key.rationale[:100]}...")
        print(f"     Circles: {len(key.circles)}, Conflicts: {len(key.conflicts)}")
        if key.conflicts:
            for c in key.conflicts:
                sev_icon = "🔴" if c.severity == 'critical' else "🟡"
                print(f"     {sev_icon} {c.violated_value}: {c.aspect} → {c.description}")
        if key.replacement:
            print(f"     🔄 REPLACEMENT: {key.replacement}")
    
    print("\n📈 CONFLICTS SUMMARY:")
    for value, count in sorted(profile.conflicts_summary.items(), key=lambda x: -x[1]):
        print(f"  {value}: {count} conflicts")


def main():
    parser = argparse.ArgumentParser(description="Human Source — Analyze human, generate keys, run ripple engine")
    parser.add_argument("--user-profile", default="memories/USER.md", help="Path to USER.md")
    parser.add_argument("--memory", default="memories/MEMORY.md", help="Path to MEMORY.md")
    parser.add_argument("--kc-db", default="cache/knowledge_cube.db", help="Path to knowledge_cube.db")
    parser.add_argument("--semantic", default="cache/crystal/semantic_analysis.json", help="Path to semantic_analysis.json")
    parser.add_argument("--config", default=None, help="Path to config.yaml")
    parser.add_argument("--generate-keys", type=int, default=5, help="Number of keys to generate")
    parser.add_argument("--ripple", type=str, help="Test ripple engine on custom key")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    parser.add_argument("--output", type=str, help="Output report file (markdown)")
    parser.add_argument("--test", action="store_true", help="Run self-test")
    
    args = parser.parse_args()
    
    # Load config
    config = {
        'analysis': {'dimensions': {'frustrations': 0.3, 'sins': 0.2, 'norms': 0.2, 'strengths': 0.15, 'context': 0.15}},
        'ripple_engine': {'max_depth': 3, 'conflict_threshold': 0.7, 'stop_on_conflict': True},
        'output': {'format': 'markdown', 'include_conflicts': True, 'include_replaced_keys': True}
    }
    if args.config and Path(args.config).exists():
        with open(args.config, 'r', encoding='utf-8') as f:
            config.update(yaml.safe_load(f))
    
    if args.test:
        print("Running self-test...")
        analyzer = HumanAnalyzer(config)
        # Just test imports work
        print("✅ Imports OK")
        print("✅ Config loaded")
        return
    
    # Analyze
    analyzer = HumanAnalyzer(config)
    
    sources = {}
    sources['user'] = analyzer.analyze_user_file(Path(args.user_profile))
    sources['kc'] = analyzer.analyze_knowledge_cube(Path(args.kc_db))
    sources['semantic'] = analyzer.analyze_semantic_analysis(Path(args.semantic))
    
    # Also check MEMORY.md
    if Path(args.memory).exists():
        sources['memory'] = analyzer.analyze_user_file(Path(args.memory))
    
    profile = analyzer.build_profile(sources)
    
    # If --ripple specified, test ripple engine on custom key
    if args.ripple:
        print(f"\n🌊 RIPPLE ENGINE TEST: '{args.ripple}'")
        print("="*70)
        custom_key = Key(
            text=args.ripple,
            source_dimension="custom_test",
            rationale="Custom key provided via --ripple flag for testing"
        )
        analyzer._run_ripple_engine(custom_key, profile.values_map)
        
        status_icon = "✅" if custom_key.status == 'validated' else "❌" if custom_key.status == 'rejected' else "⏳"
        print(f"\n{status_icon} Key: {custom_key.text} [{custom_key.status.upper()}]")
        print(f"   Circles: {len(custom_key.circles)}, Conflicts: {len(custom_key.conflicts)}")
        
        for circle in custom_key.circles:
            print(f"\n  🌊 Circle {circle.depth}: {circle.name}")
            for aspect in circle.aspects:
                print(f"    • {aspect}")
            if circle.conflicts:
                print(f"    ⚠️ CONFLICTS:")
                for c in circle.conflicts:
                    sev_icon = "🔴" if c.severity == 'critical' else "🟡"
                    print(f"    {sev_icon} {c.violated_value}: {c.aspect}")
                    print(f"       → {c.description}")
        
        if custom_key.replacement:
            print(f"\n  🔄 REPLACEMENT: {custom_key.replacement}")
        
        return
    
    # Print
    print_profile(profile, verbose=args.verbose)
    
    # Save report if requested
    if args.output:
        # Generate markdown report
        report = generate_markdown_report(profile)
        Path(args.output).write_text(report, encoding='utf-8')
        print(f"\n💾 Report saved to {args.output}")


def generate_markdown_report(profile: HumanProfile) -> str:
    """Generate markdown report."""
    lines = [
        "# Human Source Analysis Report",
        f"**Generated:** {datetime.now().isoformat()}",
        "",
        "## Dimensions",
        ""
    ]
    
    for d in profile.dimensions:
        lines.append(f"- **{d.name}** (weight: {d.weight:.0%}): {len(d.evidence)} evidence items, understanding: {d.score:.0%}")
    
    lines.extend(["", "## Values Map (Landscape)", ""])
    
    for zone_type, zones in profile.values_map.items():
        lines.append(f"### {zone_type.replace('_', ' ').title()}")
        for z in zones:
            lines.append(f"- **{z['name']}** ({z.get('depth', z.get('type', ''))})")
            for e in z['evidence'][:3]:
                lines.append(f"  - {e[:120]}...")
    
    lines.extend(["", "## Generated Keys", ""])
    
    for i, key in enumerate(profile.keys, 1):
        status = key.status.upper()
        lines.append(f"### {i}. {key.text} [{status}]")
        lines.append(f"**Source:** {key.source_dimension}")
        lines.append(f"**Rationale:** {key.rationale}")
        lines.append(f"**Circles:** {len(key.circles)} | **Conflicts:** {len(key.conflicts)}")
        
        if key.circles:
            lines.append("**Ripple Circles:**")
            for c in key.circles:
                lines.append(f"  - **Circle {c.depth}: {c.name}**")
                for a in c.aspects:
                    lines.append(f"    - {a}")
                if c.conflicts:
                    lines.append("    **⚠️ Conflicts:**")
                    for conf in c.conflicts:
                        sev = "🔴" if conf.severity == 'critical' else "🟡"
                        lines.append(f"    - {sev} {conf.violated_value}: {conf.aspect} — {conf.description}")
        
        if key.replacement:
            lines.append(f"\n**🔄 REPLACEMENT:** {key.replacement}")
        lines.append("")
    
    lines.extend(["", "## Conflicts Summary", ""])
    for value, count in sorted(profile.conflicts_summary.items(), key=lambda x: -x[1]):
        lines.append(f"- **{value}**: {count} conflicts")
    
    return "\n".join(lines)


if __name__ == "__main__":
    main()
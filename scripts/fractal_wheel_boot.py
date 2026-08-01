#!/usr/bin/env python3
"""
Fractal Knowledge Wheel — Mandatory Boot Integration.

This script runs the Fractal Knowledge Wheel (all 3 modes) for any new topic/question
at session start. It integrates with session_boot.py to ensure every new inquiry
passes through the complete analysis pipeline.
"""

import sys
import os
import json
from pathlib import Path
from typing import Dict, List, Any, Optional

HERMES_HOME = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERMES_HOME / "scripts"))

# Import the fractal wheel - use importlib for hyphenated module
import importlib.util
fractal_wheel_path = HERMES_HOME / "skills" / "arbitrage" / "fractal-knowledge-wheel" / "scripts" / "fractal_wheel.py"
spec = importlib.util.spec_from_file_location("fractal_wheel", fractal_wheel_path)
fractal_wheel = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fractal_wheel)

FractalWheel = fractal_wheel.FractalWheel
EulerCirclesEngine = fractal_wheel.EulerCirclesEngine
Sector = fractal_wheel.Sector
WheelAssessment = fractal_wheel.WheelAssessment
SynthesizedKey = fractal_wheel.SynthesizedKey
KeyStrengthEstimator = fractal_wheel.KeyStrengthEstimator


class FractalWheelBoot:
    """
    Mandatory Fractal Knowledge Wheel execution at session start.
    
    Every new topic/question MUST pass through:
    1. ANALYSIS — key → aspects → gaps → priority tasks
    2. SYNTHESIS — scattered findings → novel keys
    3. EULER CIRCLES — aspects → intersections → golden sections
    """
    
    def __init__(self, topics: Optional[List[str]] = None, domain: str = "arbitrage"):
        self.topics = topics or self._get_pending_topics()
        self.domain = domain
        self.results: Dict[str, Any] = {}
        
    def _get_pending_topics(self) -> List[str]:
        """Get topics from goal queue, active goals, or recent activity."""
        try:
            from goal_queue import get_active_goals
            goals = get_active_goals()
            topics = []
            for g in goals[:5]:  # Top 5 active goals
                if g.get("title"):
                    topics.append(g["title"])
            return topics
        except Exception:
            return ["Autonomous Income System — bootstrap check"]
    
    def run_for_topic(self, center: str) -> Dict[str, Any]:
        """Run all 3 modes for a single topic."""
        wheel = FractalWheel(center=center, domain=self.domain)
        
        # Run full cycle
        results = wheel.run_full_cycle(mode="all")
        
        # Run Key Strength estimation
        sectors = wheel.build_wheel()
        sectors = wheel.assess_gaps(sectors)
        engine = EulerCirclesEngine(sectors)
        intersections = engine.find_all_intersections()
        
        estimator = KeyStrengthEstimator(domain=self.domain)
        
        # Compare the main key with synthesized keys
        synthesis = results.get("synthesis", [])
        keys_to_compare = [center]
        if synthesis:
            keys_to_compare.extend([k.name for k in synthesis[:3]])
        
        sectors_map = {k: sectors for k in keys_to_compare}
        intersections_map = {k: intersections for k in keys_to_compare}
        
        comparison = estimator.compare_keys(keys_to_compare, sectors_map, intersections_map)
        key_strength_data = [ks.to_dict() for ks in comparison]
        
        # Extract actionable insights
        insights = self._extract_insights(results, center)
        
        return {
            "topic": center,
            "domain": self.domain,
            "analysis": self._format_analysis(results.get("analysis")),
            "synthesis": self._format_synthesis(results.get("synthesis")),
            "euler": self._format_euler(results.get("euler")),
            "key_strength": key_strength_data,
            "insights": insights,
            "priority_actions": self._get_priority_actions(results),
        }
    
    def _format_analysis(self, analysis: Optional[WheelAssessment]) -> Dict:
        if not analysis:
            return {"error": "No analysis result"}
        return {
            "overall_percent": analysis.overall_percent,
            "green": len(analysis.green_sectors),
            "yellow": len(analysis.yellow_sectors),
            "red": len(analysis.red_sectors),
            "critical_red": len(analysis.critical_red_sectors),
            "priority_tasks": analysis.priority_tasks[:5],
        }
    
    def _format_synthesis(self, synthesis: Optional[List[SynthesizedKey]]) -> Dict:
        if not synthesis:
            return {"novel_keys": 0, "keys": []}
        return {
            "novel_keys": len(synthesis),
            "keys": [
                {
                    "name": k.name,
                    "compatibility": k.compatibility_score,
                    "novelty": k.novelty_score,
                    "description": k.description[:200],
                }
                for k in synthesis[:5]
            ],
        }
    
    def _format_euler(self, euler: Optional[Dict]) -> Dict:
        if not euler:
            return {"error": "No euler result"}
        return {
            "total_intersections": euler.get("total_intersections", 0),
            "golden_sections": euler.get("golden_sections", 0),
            "critical_gaps": euler.get("critical_gaps", 0),
            "conflicts": euler.get("conflicts", 0),
            "growth_zones": euler.get("growth_zones", 0),
            "golden_details": euler.get("golden_details", [])[:5],
            "critical_details": euler.get("critical_details", [])[:5],
            "conflict_details": euler.get("conflict_details", [])[:5],
            "new_keys_from_green": euler.get("new_keys_from_green", [])[:5],
        }
    
    def _extract_insights(self, results: Dict, center: str) -> List[str]:
        """Extract human-readable insights from all 3 modes."""
        insights = []
        
        analysis = results.get("analysis")
        if analysis:
            if analysis.critical_red_sectors:
                for s in analysis.critical_red_sectors[:2]:
                    insights.append(f"🔴 CRITICAL: {s.name} ({s.fill_percent}%) — {s.gaps[0] if s.gaps else 'нет данных'}")
            
            if analysis.green_sectors:
                green_names = [s.name for s in analysis.green_sectors]
                insights.append(f"🟢 READY: {', '.join(green_names)} — можно масштабировать")
        
        euler = results.get("euler")
        if euler:
            # Golden sections
            for g in euler.get("golden_details", [])[:3]:
                insights.append(f"⭐ GOLDEN SECTION: {' ∩ '.join(g['circles'])} ({g['strength']:.0%}) — {g['action'][:80]}")
            
            # Core conflicts
            for c in euler.get("critical_details", [])[:3]:
                insights.append(f"🔴 CORE CONFLICT: {' ∩ '.join(c['circles'])} — {c['action'][:80]}")
            
            # Conflicts (green + red)
            for c in euler.get("conflict_details", [])[:3]:
                if c["type"] == "conflict" and "СЛИВАЕТСЯ" in c.get("description", ""):
                    insights.append(f"⚡ WASTED: {' ∩ '.join(c['circles'])} — {c['action'][:80]}")
        
        synthesis = results.get("synthesis")
        if synthesis:
            top_new = synthesis[0] if synthesis else None
            if top_new:
                insights.append(f"🆕 NEW KEY: {top_new.name} (compat: {top_new.compatibility_score:.0%}, novelty: {top_new.novelty_score:.0%})")
        
        return insights
    
    def _get_priority_actions(self, results: Dict) -> List[Dict]:
        """Get top priority actions across all 3 modes."""
        actions = []
        
        # From analysis
        analysis = results.get("analysis")
        if analysis:
            for task in analysis.priority_tasks[:3]:
                actions.append({
                    "source": "analysis",
                    "priority": task["priority"],
                    "action": task["expected_outcome"],
                    "target": task["target"],
                    "gaps": task["gaps"][:2],
                })
        
        # From euler conflicts
        euler = results.get("euler")
        if euler:
            for c in euler.get("conflict_details", [])[:3]:
                if c["type"] == "conflict" and "СРОЧНО" in c.get("action", ""):
                    actions.append({
                        "source": "euler_conflict",
                        "priority": "critical",
                        "action": c["action"],
                        "target": c["circles"],
                        "gaps": [],
                    })
            
            for c in euler.get("critical_details", [])[:3]:
                actions.append({
                    "source": "euler_core_conflict",
                    "priority": "critical",
                    "action": c["action"],
                    "target": c["circles"],
                    "gaps": [],
                })
        
        # Sort by priority
        priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        actions.sort(key=lambda x: priority_order.get(x["priority"], 99))
        
        return actions[:5]
    
    def run_all(self) -> Dict[str, Any]:
        """Run fractal wheel for all pending topics."""
        all_results = {}
        
        for topic in self.topics:
            log(f"[FRACTAL WHEEL] Processing: {topic}")
            result = self.run_for_topic(topic)
            all_results[topic] = result
            
            # Log key insights
            for insight in result["insights"][:3]:
                log(f"  [INSIGHT] {insight}")
        
        self.results = all_results
        return all_results
    
    def save_report(self, output_dir: Path = None) -> Path:
        """Save detailed report to reports/."""
        if output_dir is None:
            output_dir = HERMES_HOME / "reports"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        report_file = output_dir / f"fractal_wheel_boot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False, default=str)
        
        return report_file


def log(msg: str):
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] {msg}")


# Required imports at bottom to avoid circular issues
from datetime import datetime, timezone


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Fractal Knowledge Wheel — Mandatory Boot")
    parser.add_argument("--topics", nargs="+", help="Topics to analyze")
    parser.add_argument("--domain", default="arbitrage", help="Domain: arbitrage, ai-ofm, craft")
    parser.add_argument("--report", action="store_true", help="Save detailed JSON report")
    args = parser.parse_args()
    
    log("═══════════════════════════════════════")
    log("FRACTAL KNOWLEDGE WHEEL — MANDATORY BOOT")
    log("═══════════════════════════════════════")
    
    boot = FractalWheelBoot(topics=args.topics, domain=args.domain)
    results = boot.run_all()
    
    if args.report:
        report_file = boot.save_report()
        log(f"Report saved: {report_file}")
    
    log("═══════════════════════════════════════")
    log("FRACTAL WHEEL BOOT COMPLETE")
    log("═══════════════════════════════════════")
    
    return results


if __name__ == "__main__":
    main()
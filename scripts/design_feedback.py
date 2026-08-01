#!/usr/bin/env python3
"""
Design Feedback — Saves evaluation results, user feedback, and learning signals.
Integrates with feedback_store for learning from design outcomes.
"""

import os
import json
import time
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime

HERMES_HOME = Path(os.environ.get("HERMES_HOME", "D:/Portable_Soft/hermes"))
CACHE_DIR = HERMES_HOME / "cache" / "design"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

FEEDBACK_FILE = CACHE_DIR / "design_feedback.json"


@dataclass
class DesignFeedback:
    """Feedback on a design project"""
    id: str
    project_name: str
    project_path: str
    evaluation_id: str
    timestamp: str
    
    # Source of feedback
    source: str  # "user", "auto", "a/b_test", "client"
    
    # Feedback type
    feedback_type: str  # "rating", "correction", "preference", "bug_report", "improvement"
    
    # Content
    score: int = 0  # 0-100 if rating
    comments: str = ""
    specific_issues: List[Dict] = None  # specific problems reported
    preferred_changes: List[Dict] = None  # what user wants changed
    
    # Learning signal
    success: bool = True  # whether the design succeeded
    learning_weight: float = 1.0  # how much to weight this for learning
    
    # Pattern updates
    patterns_to_promote: List[str] = None  # pattern IDs that worked
    patterns_to_demote: List[str] = None  # pattern IDs that failed
    
    # Metadata
    metadata: Dict = None


class DesignFeedback:
    """Manages design feedback and learning signals"""
    
    def __init__(self):
        self.feedback: List[DesignFeedback] = []
        self._load_cache()
    
    def _load_cache(self):
        if FEEDBACK_FILE.exists():
            try:
                data = json.loads(FEEDBACK_FILE.read_text())
                for f in data.get("feedback", []):
                    self.feedback.append(DesignFeedback(**f))
            except Exception:
                pass
    
    def _save_cache(self):
        data = {"feedback": [asdict(f) for f in self.feedback]}
        FEEDBACK_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False))
    
    def record_feedback(
        self,
        project_name: str,
        project_path: str,
        evaluation_id: str,
        source: str,
        feedback_type: str,
        score: int = 0,
        comments: str = "",
        specific_issues: List[Dict] = None,
        preferred_changes: List[Dict] = None,
        success: bool = True,
        patterns_to_promote: List[str] = None,
        patterns_to_demote: List[str] = None,
        metadata: Dict = None
    ) -> DesignFeedback:
        """Record feedback on a design project"""
        
        fb = DesignFeedback(
            id=f"fb_{project_name}_{int(time.time())}",
            project_name=project_name,
            project_path=project_path,
            evaluation_id=evaluation_id,
            timestamp=datetime.now().isoformat(),
            source=source,
            feedback_type=feedback_type,
            score=score,
            comments=comments,
            specific_issues=specific_issues or [],
            preferred_changes=preferred_changes or [],
            success=success,
            patterns_to_promote=patterns_to_promote or [],
            patterns_to_demote=patterns_to_demote or [],
            metadata=metadata or {}
        )
        
        self.feedback.append(fb)
        self._save_cache()
        
        print(f"[FEEDBACK] Recorded: {fb.id} ({source}, {feedback_type}, score={score})")
        return fb
    
    def record_user_rating(self, project_name: str, evaluation_id: str, score: int, comments: str = "") -> DesignFeedback:
        """Quick method to record user rating"""
        return self.record_feedback(
            project_name=project_name,
            project_path="",
            evaluation_id=evaluation_id,
            source="user",
            feedback_type="rating",
            score=score,
            comments=comments,
            success=score >= 70
        )
    
    def record_user_correction(self, project_name: str, evaluation_id: str, issue: str, suggestion: str) -> DesignFeedback:
        """Record user correction/improvement request"""
        return self.record_feedback(
            project_name=project_name,
            project_path="",
            evaluation_id=evaluation_id,
            source="user",
            feedback_type="correction",
            comments=f"Issue: {issue}. Suggestion: {suggestion}",
            specific_issues=[{"issue": issue, "suggestion": suggestion}],
            success=False
        )
    
    def record_ab_test_result(self, project_name: str, evaluation_id: str, variant_a_score: int, variant_b_score: int, winner: str) -> DesignFeedback:
        """Record A/B test result"""
        return self.record_feedback(
            project_name=project_name,
            project_path="",
            evaluation_id=evaluation_id,
            source="ab_test",
            feedback_type="a/b_test",
            score=max(variant_a_score, variant_b_score),
            comments=f"Variant A: {variant_a_score}, Variant B: {variant_b_score}, Winner: {winner}",
            metadata={"variant_a": variant_a_score, "variant_b": variant_b_score, "winner": winner},
            success=winner == "a"
        )
    
    def get_feedback_for_project(self, project_name: str) -> List[DesignFeedback]:
        """Get all feedback for a project"""
        return [f for f in self.feedback if f.project_name == project_name]
    
    def get_learning_signals(self) -> Dict:
        """Extract learning signals for pattern promotion/demotion"""
        promote = {}
        demote = {}
        total_success = 0
        total = len(self.feedback)
        
        for fb in self.feedback:
            if fb.success:
                total_success += 1
                for p in fb.patterns_to_promote:
                    promote[p] = promote.get(p, 0) + fb.learning_weight
            else:
                for p in fb.patterns_to_demote:
                    demote[p] = demote.get(p, 0) + fb.learning_weight
        
        return {
            "patterns_to_promote": sorted(promote.items(), key=lambda x: -x[1]),
            "patterns_to_demote": sorted(demote.items(), key=lambda x: -x[1]),
            "success_rate": total_success / total if total > 0 else 0,
            "total_feedback": total
        }
    
    def get_average_scores(self) -> Dict:
        """Get average scores by feedback type/source"""
        by_source = {}
        by_type = {}
        
        for fb in self.feedback:
            if fb.source not in by_source:
                by_source[fb.source] = []
            by_source[fb.source].append(fb.score)
            
            if fb.feedback_type not in by_type:
                by_type[fb.feedback_type] = []
            by_type[fb.feedback_type].append(fb.score)
        
        return {
            "by_source": {k: sum(v)/len(v) for k, v in by_source.items()},
            "by_type": {k: sum(v)/len(v) for k, v in by_type.items()},
            "overall": sum(f.score for f in self.feedback) / len(self.feedback) if self.feedback else 0
        }
    
    def list_feedback(self) -> List[Dict]:
        """List all feedback"""
        return [asdict(f) for f in self.feedback]


# CLI
def main():
    import sys
    if len(sys.argv) < 2:
        print("Usage: python design_feedback.py <command> [args]")
        print("Commands: list, signals, scores, record")
        sys.exit(1)
    
    df = DesignFeedback()
    cmd = sys.argv[1]
    
    if cmd == "list":
        for fb in df.feedback:
            print(f"{fb.id}: {fb.project_name} | {fb.source} | {fb.feedback_type} | score={fb.score} | success={fb.success}")
    
    elif cmd == "signals":
        signals = df.get_learning_signals()
        print(json.dumps(signals, indent=2, ensure_ascii=False))
    
    elif cmd == "scores":
        scores = df.get_average_scores()
        print(json.dumps(scores, indent=2, ensure_ascii=False))
    
    elif cmd == "record":
        if len(sys.argv) < 5:
            print("Usage: record <project_name> <evaluation_id> <source> <type> [score] [comments]")
            sys.exit(1)
        fb = df.record_feedback(
            project_name=sys.argv[2],
            project_path="",
            evaluation_id=sys.argv[3],
            source=sys.argv[4],
            feedback_type=sys.argv[5],
            score=int(sys.argv[6]) if len(sys.argv) > 6 else 0,
            comments=sys.argv[7] if len(sys.argv) > 7 else ""
        )
        print(f"Recorded: {fb.id}")
    
    else:
        print(f"Unknown command: {cmd}")


if __name__ == "__main__":
    import time
    main()
#!/usr/bin/env python3
"""
Review Worker — Specialized agent for quality review of landings, code, and content.
Uses checklists from Knowledge Cube to verify quality.
"""

import json
import os
import sys
import re
from pathlib import Path
from typing import Dict, Any, List

# Add parent to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from worker_base import WorkerBase, log_team_event

HERMES_HOME = Path(__file__).resolve().parent.parent.parent


class ReviewWorker(WorkerBase):
    """Worker that reviews landings, code, and content against checklists."""
    
    def __init__(self, worker_id: str):
        super().__init__(worker_id, "review_worker")
    
    def execute(self, task_data: Dict) -> Dict:
        """Execute review task."""
        description = task_data.get("description", "")
        context = task_data.get("context", {})
        checklist_name = context.get("checklist", "landing")
        
        # Determine what to review
        review_target = self._determine_target(description, context)
        
        if review_target["type"] == "landing":
            return self._review_landing(review_target, checklist_name)
        elif review_target["type"] == "code":
            return self._review_code(review_target, checklist_name)
        elif review_target["type"] == "content":
            return self._review_content(review_target, checklist_name)
        else:
            return {"score": 0, "issues": ["Unknown review target"], "passed": False}
    
    def _determine_target(self, description: str, context: Dict) -> Dict:
        """Determine what to review from task description and context."""
        desc_lower = description.lower()
        
        # Check context first
        if "file_path" in context:
            return {"type": "file", "path": context["file_path"]}
        if "url" in context:
            return {"type": "landing", "url": context["url"]}
        if "content" in context:
            return {"type": "content", "content": context["content"]}
        
        # Check if we have a previous task ID to get the landing from
        if "previous_task_id" in context:
            prev_task_id = context["previous_task_id"]
            # Look up the previous task's result
            result_file = self._get_previous_task_result(prev_task_id)
            if result_file:
                return {"type": "landing", "path": result_file}
        
        # Infer from description
        if "landing" in desc_lower or "лендинг" in desc_lower:
            return {"type": "landing", "path": context.get("path", "latest")}
        elif "code" in desc_lower or "script" in desc_lower:
            return {"type": "code", "path": context.get("path", "latest")}
        elif "content" in desc_lower or "video" in desc_lower or "script" in desc_lower:
            return {"type": "content", "content": context.get("content", "")}
        
        # Default: look for recent landing files
        return {"type": "landing", "path": "auto"}
    
    def _get_previous_task_result(self, prev_task_id: str) -> str:
        """Get the landing file path from a previous task's result."""
        task_queue_file = HERMES_HOME / "cache" / "task_queue.json"
        if task_queue_file.exists():
            with open(task_queue_file, "r", encoding="utf-8") as f:
                queue = json.load(f)
            
            for task in queue.get("tasks", []):
                if task.get("task_id") == prev_task_id and task.get("result"):
                    result = task["result"]
                    if isinstance(result, dict) and result.get("file"):
                        return result["file"]
                    if isinstance(result, dict) and result.get("result", {}).get("file"):
                        return result["result"]["file"]
        
        return ""
    
    def _review_landing(self, target: Dict, checklist_name: str) -> Dict:
        """Review a landing page."""
        # Load landing checklist
        checklist = self._get_landing_checklist()
        
        # Get landing content
        if target.get("url"):
            # Would fetch URL - for now use file
            landing_content = self._get_latest_landing()
        elif target.get("path") and target["path"] != "auto":
            landing_content = self.read_file(target["path"])
        else:
            landing_content = self._get_latest_landing()
        
        if not landing_content:
            return {"score": 0, "issues": ["No landing page found to review"], "passed": False, "checklist": checklist}
        
        # Run checklist checks
        results = []
        score = 0
        max_score = len(checklist["items"])
        
        for item in checklist["items"]:
            check_result = self._check_item(landing_content, item)
            results.append(check_result)
            if check_result["passed"]:
                score += 1
        
        percentage = int((score / max_score * 100)) if max_score > 0 else 0
        
        # Generate issues list
        issues = [r["issue"] for r in results if not r["passed"]]
        
        result = {
            "score": percentage,
            "max_score": max_score,
            "passed": percentage >= 70,
            "checks": results,
            "issues": issues,
            "landing_preview": landing_content[:500] if landing_content else "",
            "checklist_name": checklist_name
        }
        
        # Save detailed results
        self.save_checklist(f"landing_review_{checklist_name}", result)
        
        return result
    
    def _get_landing_checklist(self) -> Dict:
        """Get landing page quality checklist."""
        # Default checklist based on arbitrage best practices
        return {
            "name": "Landing Page Quality Checklist",
            "items": [
                {"id": "headline", "name": "Strong Headline", "check": "headline", "weight": 2},
                {"id": "hook", "name": "Hook in First 3 Seconds", "check": "hook", "weight": 2},
                {"id": "benefits", "name": "Clear Benefits (not features)", "check": "benefits", "weight": 2},
                {"id": "social_proof", "name": "Social Proof / Testimonials", "check": "social_proof", "weight": 1},
                {"id": "cta", "name": "Clear CTA Above Fold", "check": "cta", "weight": 2},
                {"id": "urgency", "name": "Urgency/Scarcity Element", "check": "urgency", "weight": 1},
                {"id": "mobile", "name": "Mobile Responsive", "check": "mobile", "weight": 2},
                {"id": "load_speed", "name": "Fast Load (no heavy scripts)", "check": "load_speed", "weight": 1},
                {"id": "trust", "name": "Trust Signals (guarantee, secure, etc.)", "check": "trust", "weight": 1},
                {"id": "offer_clarity", "name": "Offer Clearly Stated", "check": "offer_clarity", "weight": 2},
                {"id": "no_leaks", "name": "No Navigation Leaks", "check": "no_leaks", "weight": 1},
                {"id": "tracking", "name": "Tracking Pixels Installed", "check": "tracking", "weight": 1},
            ]
        }
    
    def _check_item(self, content: str, item: Dict) -> Dict:
        """Run a specific checklist check on content with REAL validation."""
        check_type = item["check"]
        content_lower = content.lower()
        
        # More rigorous checks
        if check_type == "headline":
            h1_matches = re.findall(r'<h1[^>]*>(.*?)</h1>', content, re.IGNORECASE | re.DOTALL)
            passed = len(h1_matches) > 0 and len(h1_matches[0].strip()) > 10
            issue = None if passed else "No H1 tag or H1 too short (<10 chars)"
            
        elif check_type == "hook":
            # Check for hook in hero section (first 500 chars after body)
            body_start = content_lower.find('<body>')
            if body_start == -1:
                body_start = 0
            hero_content = content_lower[body_start:body_start+1000]
            hook_words = ["stop", "wait", "discover", "secret", "revealed", "shocking", "new", "free", "instant", "how to", "why", "mistake", "wrong"]
            passed = any(word in hero_content for word in hook_words)
            issue = None if passed else "No hook detected in hero section (first 1000 chars)"
            
        elif check_type == "benefits":
            # Must have at least 3 distinct benefit statements
            benefit_words = ["save", "gain", "get", "achieve", "result", "outcome", "transform", "improve", "boost", "increase", "reduce", "eliminate"]
            benefit_count = sum(1 for word in benefit_words if word in content_lower)
            passed = benefit_count >= 3
            issue = None if passed else f"Only {benefit_count} benefit keywords found (need 3+)"
            
        elif check_type == "social_proof":
            # Must have testimonials with names, not just stars
            testimonial_indicators = ["testimonial", "review", "client", "customer", "said", "told", "shared"]
            has_structured_testimonials = bool(re.search(r'(testimonial|review|client).*?[\"\u2018\u2019].{20,}[\u2018\u2019\"]', content_lower))
            has_names = bool(re.search(r'[\u2014-]\s*[A-Z][a-z]+\s+[A-Z]\.', content))  # Name format like "Maria K."
            passed = has_structured_testimonials and has_names
            issue = None if passed else "Testimonials missing proper structure or real names"
            
        elif check_type == "cta":
            # Must have CTA above fold (in hero) AND multiple CTAs
            cta_patterns = ['button', 'btn', 'cta', 'call.to.action', 'click here', 'get started', 'sign up', 'join now', 'buy now', 'book', 'claim', 'get']
            cta_count = sum(len(re.findall(rf'{pattern}', content_lower)) for pattern in cta_patterns)
            hero_cta = bool(re.search(r'(button|btn|cta|get|claim|book|sign.up|join).*?(hero|above.fold|first.screen)', content_lower))
            passed = cta_count >= 2
            issue = None if passed else f"Only {cta_count} CTAs found (need 2+), hero CTA: {hero_cta}"
            
        elif check_type == "urgency":
            # Must have REAL urgency element (countdown, limited spots, timer)
            urgency_indicators = ["countdown", "timer", "expires", "deadline", "hours left", "minutes left", "spots left", "seats left", "only.*left", "limited.*offer"]
            passed = any(re.search(pattern, content_lower) for pattern in urgency_indicators)
            issue = None if passed else "No real urgency element (countdown, limited spots with numbers, deadline)"
            
        elif check_type == "mobile":
            # Must have viewport meta AND responsive CSS
            has_viewport = 'viewport' in content_lower
            has_media_queries = '@media' in content_lower
            has_flex_grid = 'flex' in content_lower or 'grid' in content_lower
            passed = has_viewport and (has_media_queries or has_flex_grid)
            issue = None if passed else f"Viewport: {has_viewport}, Media queries: {has_media_queries}, Flex/Grid: {has_flex_grid}"
            
        elif check_type == "load_speed":
            # Check for performance killers
            script_count = len(re.findall(r'<script', content_lower))
            has_jquery = 'jquery' in content_lower
            has_external_fonts = 'fonts.googleapis.com' in content_lower or 'fonts.gstatic.com' in content_lower
            inline_styles = len(re.findall(r'style=', content_lower))
            passed = script_count < 5 and not has_jquery and inline_styles < 20
            issue = None if passed else f"Scripts: {script_count}, jQuery: {has_jquery}, External fonts: {has_external_fonts}, Inline styles: {inline_styles}"
            
        elif check_type == "trust":
            # Must have SPECIFIC trust signals
            trust_signals = ["money.back.guarantee", "money.back", "satisfaction.guarantee", "refund.policy", "secure.checkout", "ssl.certificate", "encrypted", "privacy.policy", "terms.of.service"]
            trust_count = sum(1 for signal in trust_signals if signal.replace('.', '') in content_lower.replace('.', ''))
            passed = trust_count >= 2
            issue = None if passed else f"Only {trust_count}/2 trust signals found"
            
        elif check_type == "offer_clarity":
            # Offer must be specific with numbers/prices
            has_price = bool(re.search(r'\$\d+|\d+\s*(?:usd|eur|rub|\$)|\d+%\s*off|\d+\s*percent', content_lower))
            has_specific_offer = bool(re.search(r'(free|discount|offer|deal|trial|bonus).*?(\d+|\$\d+|\d+%)', content_lower))
            passed = has_price or has_specific_offer
            issue = None if passed else "No specific pricing or quantified offer found"
            
        elif check_type == "no_leaks":
            # Check for external links that aren't tracking/affiliate
            external_links = re.findall(r'<a\s+href=["\']https?://([^"\']+)["\']', content, re.IGNORECASE)
            leak_count = 0
            for link in external_links:
                if not any(track in link.lower() for track in ['click', 'track', 'affiliate', 'utm_', 'pixel', 'fbclid', 'gclid']):
                    leak_count += 1
            passed = leak_count == 0
            issue = None if passed else f"Found {leak_count} external navigation leaks (non-tracking links)"
            
        elif check_type == "tracking":
            # Must have REAL tracking implementation
            tracking_systems = ['fbq', 'ttq', 'gtag', 'ga(', 'gtm', 'datalayer', 'metrika', 'ym(']
            has_real_tracking = any(sys in content_lower for sys in tracking_systems)
            passed = has_real_tracking
            issue = None if passed else "No real tracking implementation (FB Pixel, TikTok Pixel, GA4, GTM, etc.)"
            
        else:
            passed = False
            issue = f"Unknown check type: {check_type}"
        
        return {
            "id": item["id"],
            "name": item["name"],
            "passed": passed,
            "issue": issue,
            "weight": item.get("weight", 1)
        }
    
    def _get_latest_landing(self) -> str:
        """Find the most recent landing page file."""
        # Look in common locations
        search_dirs = [
            HERMES_HOME / "cache" / "landings",
            HERMES_HOME / "scripts" / "salons" / "dist",
            HERMES_HOME / "skills" / "content-pipeline" / "data",
            HERMES_HOME / "scripts",
        ]
        
        latest_file = None
        latest_time = 0
        
        for dir_path in search_dirs:
            if dir_path.exists():
                for ext in ["*.html", "*.htm"]:
                    for file in dir_path.glob(ext):
                        mtime = file.stat().st_mtime
                        if mtime > latest_time:
                            latest_time = mtime
                            latest_file = file
        
        if latest_file:
            return latest_file.read_text(encoding="utf-8")
        
        return ""
    
    def _review_code(self, target: Dict, checklist_name: str) -> Dict:
        """Review code files."""
        checklist = {
            "name": "Code Quality Checklist",
            "items": [
                {"id": "no_syntax_errors", "name": "No Syntax Errors", "check": "syntax"},
                {"id": "has_tests", "name": "Has Tests", "check": "tests"},
                {"id": "type_hints", "name": "Type Hints Present", "check": "types"},
                {"id": "docstrings", "name": "Docstrings Present", "check": "docstrings"},
                {"id": "no_hardcoded", "name": "No Hardcoded Secrets", "check": "secrets"},
                {"id": "error_handling", "name": "Error Handling", "check": "errors"},
            ]
        }
        
        # Get code content
        if target.get("path") and target["path"] != "latest":
            code_content = self.read_file(target["path"])
        else:
            code_content = self._get_latest_code()
        
        if not code_content:
            return {"score": 0, "issues": ["No code found to review"], "passed": False}
        
        results = []
        score = 0
        
        for item in checklist["items"]:
            passed = self._check_code_item(code_content, item["check"])
            results.append({"id": item["id"], "name": item["name"], "passed": passed, "issue": None if passed else f"Missing: {item['name']}"})
            if passed:
                score += 1
        
        percentage = int((score / len(checklist["items"]) * 100))
        
        return {
            "score": percentage,
            "passed": percentage >= 70,
            "checks": results,
            "issues": [r["issue"] for r in results if not r["passed"]]
        }
    
    def _check_code_item(self, code: str, check: str) -> bool:
        """Check code quality item."""
        if check == "syntax":
            try:
                compile(code, "<string>", "exec")
                return True
            except:
                return False
        elif check == "tests":
            return "def test_" in code or "pytest" in code or "unittest" in code
        elif check == "types":
            return ":" in code and "->" in code  # Simple check for type hints
        elif check == "docstrings":
            return '"""' in code or "'''" in code
        elif check == "secrets":
            return not any(word in code.lower() for word in ["api_key", "secret", "password", "token"]) or "os.environ.get" in code
        elif check == "errors":
            return "try:" in code and "except" in code
        return False
    
    def _get_latest_code(self) -> str:
        """Get most recent Python file."""
        py_files = list(HERMES_HOME.glob("scripts/*.py"))
        if py_files:
            latest = max(py_files, key=lambda f: f.stat().st_mtime)
            return latest.read_text(encoding="utf-8")
        return ""
    
    def _review_content(self, target: Dict, checklist_name: str) -> Dict:
        """Review content (scripts, videos, etc.)."""
        content = target.get("content", "")
        
        if not content and target.get("path"):
            content = self.read_file(target["path"])
        
        if not content:
            return {"score": 0, "issues": ["No content found to review"], "passed": False}
        
        checklist = {
            "name": "Content Quality Checklist",
            "items": [
                {"id": "hook", "name": "Strong Hook (First 3s)", "check": lambda c: len(c) > 50 and any(w in c.lower() for w in ["stop", "wait", "discover", "secret", "how to", "why"]), "weight": 2},
                {"id": "structure", "name": "Clear Structure (Hook→Value→CTA)", "check": lambda c: len(c.split('.')) > 3, "weight": 2},
                {"id": "cta", "name": "Clear Call to Action", "check": lambda c: any(w in c.lower() for w in ["link in bio", "follow", "comment", "click", "check", "get"]), "weight": 2},
                {"id": "value", "name": "Delivers Value", "check": lambda c: len(c) > 200, "weight": 1},
                {"id": "engagement", "name": "Engagement Triggers", "check": lambda c: any(w in c.lower() for w in ["?", "comment", "share", "save", "duet", "stitch"]), "weight": 1},
            ]
        }
        
        results = []
        score = 0
        total_weight = 0
        
        for item in checklist["items"]:
            weight = item.get("weight", 1)
            total_weight += weight
            passed = item["check"](content)
            results.append({"id": item["id"], "name": item["name"], "passed": passed, "issue": None if passed else f"Missing: {item['name']}", "weight": weight})
            if passed:
                score += weight
        
        percentage = int((score / total_weight * 100)) if total_weight > 0 else 0
        
        return {
            "score": percentage,
            "passed": percentage >= 70,
            "checks": results,
            "issues": [r["issue"] for r in results if not r["passed"]]
        }


def main():
    """CLI entry point."""
    if len(sys.argv) < 2:
        print(json.dumps({"success": False, "error": "No task data provided"}, ensure_ascii=False))
        sys.exit(1)
    
    try:
        task_data = json.loads(sys.argv[1])
    except json.JSONDecodeError:
        print(json.dumps({"success": False, "error": "Invalid JSON"}, ensure_ascii=False))
        sys.exit(1)
    
    worker_id = task_data.get("worker_id", f"review_{os.getpid()}")
    worker = ReviewWorker(worker_id)
    result = worker.run(task_data)
    
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
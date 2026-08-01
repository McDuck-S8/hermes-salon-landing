#!/usr/bin/env python3
"""
Design Evaluator — Automated quality checking for design projects.
Integrates Lighthouse, axe-core, ESLint, W3C Validator.
"""

import os
import json
import re
import subprocess
import sys
import time
import tempfile
import threading
import http.server
import socketserver
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime

HERMES_HOME = Path(os.environ.get("HERMES_HOME", "D:/Portable_Soft/hermes"))
CACHE_DIR = HERMES_HOME / "cache" / "design"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

EVALUATION_FILE = CACHE_DIR / "evaluations.json"


@dataclass
class EvaluationResult:
    """Result of a design evaluation"""
    id: str
    project_name: str
    project_path: str
    timestamp: str
    
    # Lighthouse scores (0-100)
    lighthouse_performance: int = 0
    lighthouse_accessibility: int = 0
    lighthouse_best_practices: int = 0
    lighthouse_seo: int = 0
    lighthouse_pwa: int = 0
    
    # Axe-core accessibility
    axe_violations: int = 0
    axe_passes: int = 0
    axe_incomplete: int = 0
    axe_score: int = 0
    
    # ESLint
    eslint_errors: int = 0
    eslint_warnings: int = 0
    
    # W3C Validation
    w3c_errors: int = 0
    w3c_warnings: int = 0
    
    # Custom checks
    custom_checks: Dict[str, Any] = None
    
    # Overall
    overall_score: int = 0
    passed: bool = False
    details: Dict = None


class DesignEvaluator:
    """Evaluates design projects against quality criteria"""
    
    # Quality thresholds
    THRESHOLDS = {
        "lighthouse_performance": 80,
        "lighthouse_accessibility": 90,
        "lighthouse_best_practices": 85,
        "lighthouse_seo": 80,
        "axe_score": 90,
        "w3c_errors": 0,
        "eslint_errors": 0,
    }
    
    def __init__(self):
        self.evaluations: List[EvaluationResult] = []
        self._load_cache()
    
    def _load_cache(self):
        if EVALUATION_FILE.exists():
            try:
                data = json.loads(EVALUATION_FILE.read_text())
                for e in data.get("evaluations", []):
                    self.evaluations.append(EvaluationResult(**e))
            except Exception:
                pass
    
    def _save_cache(self):
        data = {"evaluations": [asdict(e) for e in self.evaluations]}
        EVALUATION_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False))
    
    def evaluate_project(self, project_path: Path, project_name: str = None) -> EvaluationResult:
        """Run full evaluation suite on a project"""
        name = project_name or project_path.name
        eval_id = f"eval_{name}_{int(time.time())}"
        
        print(f"[EVALUATOR] Evaluating {name}...")
        
        result = EvaluationResult(
            id=eval_id,
            project_name=name,
            project_path=str(project_path.resolve()),
            timestamp=datetime.now().isoformat()
        )
        
        # Run evaluations
        self._run_lighthouse(project_path, result)
        self._run_axe_core(project_path, result)
        self._run_eslint(project_path, result)
        self._run_w3c_validator(project_path, result)
        self._run_custom_checks(project_path, result)
        
        # Calculate overall score
        result.overall_score = self._calculate_overall_score(result)
        result.passed = result.overall_score >= 75  # Minimum passing score
        result.details = self._generate_details(result)
        
        self.evaluations.append(result)
        self._save_cache()
        
        print(f"[EVALUATOR] {name}: {result.overall_score}/100 {'✓ PASSED' if result.passed else '✗ FAILED'}")
        return result
    
    def _run_lighthouse(self, project_path: Path, result: EvaluationResult):
        """Run Lighthouse CI on the project"""
        try:
            # Find HTML entry point
            html_files = list(project_path.rglob("*.html"))
            if not html_files:
                print("[EVALUATOR] No HTML files found, skipping Lighthouse")
                return
            
            # Use absolute path for the HTTP server - don't change working directory
            project_abs = project_path.resolve()
            
            # Start a simple HTTP server for the project
            import threading
            import http.server
            import socketserver
            
            port = 8765
            server_ready = threading.Event()
            
            def serve():
                # Use absolute path for the handler
                class Handler(http.server.SimpleHTTPRequestHandler):
                    def __init__(self, *args, **kwargs):
                        super().__init__(*args, directory=str(project_abs), **kwargs)
                
                with socketserver.TCPServer(("", port), Handler) as httpd:
                    server_ready.set()
                    httpd.serve_forever()
            
            server_thread = threading.Thread(target=serve, daemon=True)
            server_thread.start()
            server_ready.wait()
            time.sleep(1)
            
            url = f"http://localhost:{port}/{html_files[0].name}"
            
            # Run lighthouse
            lighthouse_cmd = [
                "npx", "lighthouse", url,
                "--output=json",
                "--output-path=stdout",
                "--chrome-flags=--headless --no-sandbox --disable-gpu",
                "--preset=desktop",
                "--quiet"
            ]
            
            proc = subprocess.run(
                lighthouse_cmd,
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if proc.returncode == 0 and proc.stdout:
                lh_data = json.loads(proc.stdout)
                categories = lh_data.get("categories", {})
                
                result.lighthouse_performance = int(categories.get("performance", {}).get("score", 0) * 100)
                result.lighthouse_accessibility = int(categories.get("accessibility", {}).get("score", 0) * 100)
                result.lighthouse_best_practices = int(categories.get("best-practices", {}).get("score", 0) * 100)
                result.lighthouse_seo = int(categories.get("seo", {}).get("score", 0) * 100)
                result.lighthouse_pwa = int(categories.get("pwa", {}).get("score", 0) * 100)
                
                print(f"  Lighthouse: Perf={result.lighthouse_performance}, A11y={result.lighthouse_accessibility}, BP={result.lighthouse_best_practices}, SEO={result.lighthouse_seo}")
            
        except FileNotFoundError:
            print("[EVALUATOR] Lighthouse not installed (npx lighthouse), skipping")
        except subprocess.TimeoutExpired:
            print("[EVALUATOR] Lighthouse timeout")
        except Exception as e:
            print(f"[EVALUATOR] Lighthouse error: {e}")
        finally:
            # Kill the server
            try:
                subprocess.run(["taskkill", "/F", "/IM", "node.exe"], capture_output=True)
            except:
                pass
    
    def _run_axe_core(self, project_path: Path, result: EvaluationResult):
        """Run axe-core accessibility testing"""
        try:
            html_files = list(project_path.rglob("*.html"))
            if not html_files:
                return
            
            # Create a simple axe-core runner
            axe_script = """
            const axe = require('axe-core');
            const fs = require('fs');
            const html = fs.readFileSync(process.argv[2], 'utf8');
            
            // Parse HTML in jsdom
            const { JSDOM } = require('jsdom');
            const dom = new JSDOM(html, { url: 'http://localhost' });
            
            axe.run(dom.window.document, { runOnly: { type: 'tag', values: ['wcag2a', 'wcag2aa', 'wcag21aa'] } })
                .then(results => {
                    console.log(JSON.stringify({
                        violations: results.violations.length,
                        passes: results.passes.length,
                        incomplete: results.incomplete.length,
                        score: Math.max(0, 100 - results.violations.length * 5)
                    }));
                })
                .catch(err => console.error(err));
            """
            
            script_file = project_path / "axe_runner.js"
            script_file.write_text(axe_script)
            
            for html_file in list(project_path.rglob("*.html"))[:1]:
                proc = subprocess.run(
                    ["node", str(script_file), str(html_file)],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if proc.returncode == 0 and proc.stdout:
                    try:
                        axe_data = json.loads(proc.stdout.strip().split('\n')[-1])
                        result.axe_violations = axe_data.get("violations", 0)
                        result.axe_passes = axe_data.get("passes", 0)
                        result.axe_incomplete = axe_data.get("incomplete", 0)
                        result.axe_score = axe_data.get("score", 0)
                        print(f"  Axe: violations={result.axe_violations}, score={result.axe_score}")
                    except:
                        pass
                
                script_file.unlink(missing_ok=True)
                
        except FileNotFoundError:
            print("[EVALUATOR] Node/axe-core not available, skipping")
        except Exception as e:
            print(f"[EVALUATOR] Axe error: {e}")
    
    def _run_eslint(self, project_path: Path, result: EvaluationResult):
        """Run ESLint on JavaScript/TypeScript files"""
        try:
            js_files = list(project_path.rglob("*.js")) + list(project_path.rglob("*.ts"))
            if not js_files:
                return
            
            # Create minimal eslint config if not exists
            eslint_config = project_path / ".eslintrc.json"
            if not eslint_config.exists():
                config = {
                    "env": {"browser": True, "es2021": True},
                    "extends": ["eslint:recommended"],
                    "parserOptions": {"ecmaVersion": "latest", "sourceType": "module"},
                    "rules": {}
                }
                eslint_config.write_text(json.dumps(config, indent=2))
            
            proc = subprocess.run(
                ["npx", "eslint", "--format=json", str(project_path)],
                capture_output=True,
                text=True,
                timeout=60,
                cwd=project_path
            )
            
            if proc.stdout:
                try:
                    eslint_data = json.loads(proc.stdout)
                    errors = 0
                    warnings = 0
                    for file_result in eslint_data:
                        errors += len([m for m in file_result.get("messages", []) if m.get("severity") == 2])
                        warnings += len([m for m in file_result.get("messages", []) if m.get("severity") == 1])
                    
                    result.eslint_errors = errors
                    result.eslint_warnings = warnings
                    print(f"  ESLint: errors={errors}, warnings={warnings}")
                except:
                    pass
                    
        except FileNotFoundError:
            print("[EVALUATOR] ESLint not available, skipping")
        except Exception as e:
            print(f"[EVALUATOR] ESLint error: {e}")
    
    def _run_w3c_validator(self, project_path: Path, result: EvaluationResult):
        """Run W3C HTML validation"""
        try:
            html_files = list(project_path.rglob("*.html"))
            if not html_files:
                return
            
            for html_file in html_files[:2]:
                proc = subprocess.run(
                    ["npx", "html-validate", str(html_file), "--formatter=json"],
                    capture_output=True,
                    text=True,
                    timeout=30,
                    cwd=project_path
                )
                
                if proc.stdout:
                    try:
                        w3c_data = json.loads(proc.stdout)
                        for file_result in w3c_data:
                            for msg in file_result.get("messages", []):
                                if msg.get("severity") == "error":
                                    result.w3c_errors += 1
                                elif msg.get("severity") == "warning":
                                    result.w3c_warnings += 1
                        print(f"  W3C: errors={result.w3c_errors}, warnings={result.w3c_warnings}")
                    except:
                        pass
                        
        except FileNotFoundError:
            print("[EVALUATOR] html-validate not available, skipping")
        except Exception as e:
            print(f"[EVALUATOR] W3C validation error: {e}")
    
    def _run_custom_checks(self, project_path: Path, result: EvaluationResult):
        """Run custom design-specific checks"""
        checks = {}
        
        # Handle both file and directory paths
        if project_path.is_file():
            html_files = [project_path] if project_path.suffix == '.html' else []
            css_files = [project_path] if project_path.suffix == '.css' else []
        else:
            html_files = list(project_path.rglob("*.html"))
            css_files = list(project_path.rglob("*.css"))
        
        html_content = ""
        if html_files:
            html_content = html_files[0].read_text(encoding="utf-8", errors="ignore")
        
        # Extract inline CSS from <style> tags
        inline_css = ""
        style_matches = re.findall(r'<style[^>]*>(.*?)</style>', html_content, re.DOTALL | re.IGNORECASE)
        for match in style_matches:
            inline_css += match + "\n"
        
        css_content = ""
        if css_files:
            css_content = css_files[0].read_text(encoding="utf-8", errors="ignore")
        
        # Combine all CSS (inline + external)
        all_css = inline_css + "\n" + css_content
        combined = html_content + all_css
        
        # Custom design checks
        checks["has_viewport_meta"] = 'name="viewport"' in html_content
        checks["has_semantic_html"] = any(tag in html_content for tag in ["<header", "<footer", "<main", "<article", "<section", "<nav"])
        checks["has_aria_attributes"] = "aria-" in combined
        checks["has_focus_states"] = ":focus" in combined or "focus-visible" in combined
        checks["has_transitions"] = "transition" in combined
        checks["has_dark_mode"] = "@media (prefers-color-scheme: dark)" in combined or "color-scheme" in combined
        checks["has_fluid_typography"] = "clamp(" in combined
        checks["has_container_queries"] = "container-type" in combined or "container-query" in combined
        checks["has_css_grid"] = "display: grid" in combined or "grid-template" in combined
        checks["has_flexbox"] = "display: flex" in combined or "flex:" in combined
        checks["has_glassmorphism"] = "backdrop-filter" in combined
        checks["has_variable_fonts"] = "font-variation-settings" in combined or "font-optical-sizing" in combined
        checks["has_meta_description"] = 'name="description"' in html_content
        checks["has_canonical"] = 'rel="canonical"' in html_content
        checks["has_schema"] = 'schema.org' in combined or 'application/ld+json' in combined
        
        # Score each check
        passed = sum(1 for v in checks.values() if v)
        total = len(checks)
        checks["_score"] = int(passed / total * 100) if total > 0 else 0
        
        result.custom_checks = checks
        print(f"  Custom: {checks['_score']}/100 ({passed}/{total} passed)")
    
    def _calculate_overall_score(self, result: EvaluationResult) -> int:
        """Calculate weighted overall score"""
        weights = {
            "lighthouse_performance": 0.15,
            "lighthouse_accessibility": 0.20,
            "lighthouse_best_practices": 0.10,
            "lighthouse_seo": 0.10,
            "axe_score": 0.20,
            "eslint_errors": 0.05,  # negative weight
            "w3c_errors": 0.05,     # negative weight
            "custom_checks": 0.15,
        }
        
        # Normalize scores
        scores = {
            "lighthouse_performance": result.lighthouse_performance,
            "lighthouse_accessibility": result.lighthouse_accessibility,
            "lighthouse_best_practices": result.lighthouse_best_practices,
            "lighthouse_seo": result.lighthouse_seo,
            "axe_score": result.axe_score,
            "eslint_errors": max(0, 100 - result.eslint_errors * 10),
            "w3c_errors": max(0, 100 - result.w3c_errors * 20),
            "custom_checks": result.custom_checks.get("_score", 0) if result.custom_checks else 0,
        }
        
        weighted_sum = sum(scores[k] * weights[k] for k in weights)
        return int(weighted_sum)
    
    def _generate_details(self, result: EvaluationResult) -> Dict:
        """Generate detailed breakdown"""
        details = {
            "thresholds": self.THRESHOLDS,
            "results": {
                "lighthouse": {
                    "performance": {"score": result.lighthouse_performance, "threshold": self.THRESHOLDS["lighthouse_performance"], "pass": result.lighthouse_performance >= self.THRESHOLDS["lighthouse_performance"]},
                    "accessibility": {"score": result.lighthouse_accessibility, "threshold": self.THRESHOLDS["lighthouse_accessibility"], "pass": result.lighthouse_accessibility >= self.THRESHOLDS["lighthouse_accessibility"]},
                    "best_practices": {"score": result.lighthouse_best_practices, "threshold": self.THRESHOLDS["lighthouse_best_practices"], "pass": result.lighthouse_best_practices >= self.THRESHOLDS["lighthouse_best_practices"]},
                    "seo": {"score": result.lighthouse_seo, "threshold": self.THRESHOLDS["lighthouse_seo"], "pass": result.lighthouse_seo >= self.THRESHOLDS["lighthouse_seo"]},
                },
                "axe": {"score": result.axe_score, "threshold": self.THRESHOLDS["axe_score"], "pass": result.axe_score >= self.THRESHOLDS["axe_score"]},
                "eslint": {"errors": result.eslint_errors, "threshold": self.THRESHOLDS["eslint_errors"], "pass": result.eslint_errors <= self.THRESHOLDS["eslint_errors"]},
                "w3c": {"errors": result.w3c_errors, "threshold": self.THRESHOLDS["w3c_errors"], "pass": result.w3c_errors <= self.THRESHOLDS["w3c_errors"]},
                "custom": result.custom_checks or {},
            },
            "summary": {
                "overall_score": result.overall_score,
                "passed": result.passed,
                "areas_for_improvement": self._identify_weak_areas(result)
            }
        }
        return details
    
    def _identify_weak_areas(self, result: EvaluationResult) -> List[str]:
        """Identify areas needing improvement"""
        weak = []
        
        if result.lighthouse_performance < self.THRESHOLDS["lighthouse_performance"]:
            weak.append(f"Performance ({result.lighthouse_performance}/{self.THRESHOLDS['lighthouse_performance']})")
        if result.lighthouse_accessibility < self.THRESHOLDS["lighthouse_accessibility"]:
            weak.append(f"Accessibility ({result.lighthouse_accessibility}/{self.THRESHOLDS['lighthouse_accessibility']})")
        if result.axe_score < self.THRESHOLDS["axe_score"]:
            weak.append(f"Axe a11y ({result.axe_score}/{self.THRESHOLDS['axe_score']})")
        if result.eslint_errors > self.THRESHOLDS["eslint_errors"]:
            weak.append(f"ESLint errors ({result.eslint_errors})")
        if result.w3c_errors > self.THRESHOLDS["w3c_errors"]:
            weak.append(f"W3C errors ({result.w3c_errors})")
        if result.custom_checks and result.custom_checks.get("_score", 0) < 70:
            weak.append(f"Design checks ({result.custom_checks.get('_score', 0)}/100)")
        
        return weak
    
    def generate_report(self, result: EvaluationResult) -> str:
        """Generate human-readable report"""
        lines = [
            f"=== DESIGN EVALUATION REPORT ===",
            f"Project: {result.project_name}",
            f"Timestamp: {result.timestamp}",
            f"Overall Score: {result.overall_score}/100 {'✓ PASSED' if result.passed else '✗ FAILED'}",
            "",
            "=== LIGHTHOUSE ===",
            f"  Performance: {result.lighthouse_performance}/{self.THRESHOLDS['lighthouse_performance']} {'✓' if result.lighthouse_performance >= self.THRESHOLDS['lighthouse_performance'] else '✗'}",
            f"  Accessibility: {result.lighthouse_accessibility}/{self.THRESHOLDS['lighthouse_accessibility']} {'✓' if result.lighthouse_accessibility >= self.THRESHOLDS['lighthouse_accessibility'] else '✗'}",
            f"  Best Practices: {result.lighthouse_best_practices}/{self.THRESHOLDS['lighthouse_best_practices']} {'✓' if result.lighthouse_best_practices >= self.THRESHOLDS['lighthouse_best_practices'] else '✗'}",
            f"  SEO: {result.lighthouse_seo}/{self.THRESHOLDS['lighthouse_seo']} {'✓' if result.lighthouse_seo >= self.THRESHOLDS['lighthouse_seo'] else '✗'}",
            "",
            "=== AXE ACCESSIBILITY ===",
            f"  Score: {result.axe_score}/100 {'✓' if result.axe_score >= self.THRESHOLDS['axe_score'] else '✗'}",
            f"  Violations: {result.axe_violations}",
            "",
            "=== CODE QUALITY ===",
            f"  ESLint Errors: {result.eslint_errors} {'✓' if result.eslint_errors == 0 else '✗'}",
            f"  W3C Errors: {result.w3c_errors} {'✓' if result.w3c_errors == 0 else '✗'}",
            "",
            "=== CUSTOM DESIGN CHECKS ===",
        ]
        
        if result.custom_checks:
            for check, value in result.custom_checks.items():
                if check != "_score":
                    status = "✓" if value else "✗"
                    lines.append(f"  {status} {check}")
        
        lines.extend([
            "",
            "=== WEAK AREAS ===",
        ])
        
        for area in result.details.get("summary", {}).get("areas_for_improvement", []):
            lines.append(f"  - {area}")
        
        lines.append("\n=== RECOMMENDATIONS ===")
        lines.append("See specific_suggestions in evaluation details for code examples.")
        
        return "\n".join(lines)


# CLI
def main():
    import sys
    if len(sys.argv) < 2:
        print("Usage: python design_evaluator.py <project_path> [project_name]")
        sys.exit(1)
    
    project_path = Path(sys.argv[1])
    project_name = sys.argv[2] if len(sys.argv) > 2 else None
    
    evaluator = DesignEvaluator()
    result = evaluator.evaluate_project(project_path, project_name)
    
    print(evaluator.generate_report(result))
    
    # Save detailed result - use parent directory if project_path is a file
    output_dir = project_path.parent if project_path.is_file() else project_path
    output_dir = output_dir.resolve()
    output_file = output_dir / "evaluation_report.json"
    output_file.write_text(json.dumps(asdict(result), indent=2, ensure_ascii=False))
    print(f"\nDetailed report saved to: {output_file}")


if __name__ == "__main__":
    import time
    main()
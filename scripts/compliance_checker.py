#!/usr/bin/env python3
"""
Compliance Checker — Daily verification of three core autonomy rules.
Zero Trust | Passive Income | Iterative Attack
Runs as cron daily, logs to feedback_store, auto-corrects violations.
"""

import os
import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any

HERMES_HOME = Path(os.environ.get("HERMES_HOME", "D:/Portable_Soft/hermes"))
KC_DB = HERMES_HOME / "cache" / "knowledge_cube.db"
FEEDBACK_DB = HERMES_HOME / "cache" / "feedback_store.db"
JOBS_FILE = HERMES_HOME / "cron" / "jobs.json"
MAINTENANCE_REPORTS = HERMES_HOME / "maintenance_reports"
IMPROVEMENT_SUGGESTIONS = HERMES_HOME / "cache" / "improvement_suggestions.json"


class ComplianceChecker:
    """Checks and enforces three core autonomy rules."""
    
    def __init__(self):
        self.results = {
            "zero_trust": {"compliant": False, "details": {}, "action": None},
            "passive_income": {"compliant": False, "details": {}, "action": None},
            "iterative_attack": {"compliant": False, "details": {}, "action": None},
        }
    
    def check_all(self) -> Dict[str, Any]:
        """Run all three checks."""
        self._check_zero_trust()
        self._check_passive_income()
        self._check_iterative_attack()
        return self.results
    
    def _check_zero_trust(self):
        """Zero Trust: All changes verified by subagent_verifier."""
        # Check recent file modifications have verification log
        # Look for subagent_verifier runs in last 24h
        conn = sqlite3.connect(str(FEEDBACK_DB), timeout=5) if FEEDBACK_DB.exists() else None
        verification_logs = []
        
        if conn:
            conn.row_factory = sqlite3.Row
            try:
                rows = conn.execute("""
                    SELECT * FROM feedback 
                    WHERE skill LIKE '%subagent_verifier%' 
                    AND timestamp > datetime('now', '-24 hours')
                    ORDER BY timestamp DESC
                """).fetchall()
                verification_logs = [dict(r) for r in rows]
            finally:
                conn.close()
        
        # Also check maintenance reports for verifications
        recent_reports = list(MAINTENANCE_REPORTS.glob("*.json"))[-5:]
        verified_files = 0
        for report_file in recent_reports:
            try:
                data = json.loads(report_file.read_text(encoding="utf-8"))
                if data.get("verified_by_subagent"):
                    verified_files += 1
            except:
                pass
        
        compliant = len(verification_logs) > 0 or verified_files > 0
        
        self.results["zero_trust"] = {
            "compliant": compliant,
            "details": {
                "verification_logs_24h": len(verification_logs),
                "recent_maintenance_reports_verified": verified_files,
                "message": "All changes must pass subagent_verifier before survival" if compliant else "NO verification logs found in last 24h"
            },
            "action": "run_subagent_verifier_on_recent_changes" if not compliant else None
        }
    
    def _check_passive_income(self):
        """Passive Income: Cron jobs running without user intervention."""
        # Check cron jobs status from last 48h
        conn = sqlite3.connect(str(FEEDBACK_DB), timeout=5) if FEEDBACK_DB.exists() else None
        cron_runs = 0
        failed_jobs = []
        
        if conn:
            conn.row_factory = sqlite3.Row
            try:
                # Look for cron execution logs
                rows = conn.execute("""
                    SELECT skill, timestamp, result
                    FROM feedback 
                    WHERE skill LIKE '%cron%' OR skill LIKE '%maintenance%' OR skill LIKE '%suggestion%'
                    AND timestamp > datetime('now', '-48 hours')
                    ORDER BY timestamp DESC
                """).fetchall()
                cron_runs = len(rows)
                failed_jobs = [dict(r) for r in rows if 'success' in str(r).lower() and 'false' in str(r).lower()]
            finally:
                conn.close()
        
        # Also check jobs.json for enabled jobs
        enabled_jobs = 0
        if JOBS_FILE.exists():
            try:
                jobs_data = json.loads(JOBS_FILE.read_text(encoding="utf-8"))
                enabled_jobs = sum(1 for j in jobs_data.get("jobs", []) if j.get("enabled"))
            except:
                pass
        
        # Check if maintenance_scanner ran recently
        report_files = list(MAINTENANCE_REPORTS.glob("*.json"))
        maintenance_ran = any("maintenance" in f.name for f in report_files[-3:])
        
        compliant = cron_runs > 0 and maintenance_ran
        
        self.results["passive_income"] = {
            "compliant": compliant,
            "details": {
                "cron_runs_48h": cron_runs,
                "failed_jobs": len(failed_jobs),
                "enabled_jobs_in_config": enabled_jobs,
                "maintenance_scanner_recent": maintenance_ran,
                "message": "Background cron jobs executing autonomously" if compliant else f"Only {cron_runs} cron runs in 48h, maintenance: {maintenance_ran}"
            },
            "action": "restart_failed_crons" if not compliant else None
        }
    
    def _check_iterative_attack(self):
        """Iterative Attack: At least one new task attempted today."""
        conn = sqlite3.connect(str(FEEDBACK_DB), timeout=5) if FEEDBACK_DB.exists() else None
        new_tasks_today = 0
        task_types = []
        
        if conn:
            conn.row_factory = sqlite3.Row
            try:
                rows = conn.execute("""
                    SELECT skill, timestamp, result
                    FROM feedback 
                    WHERE timestamp > datetime('now', 'start of day')
                    AND skill IN ('proactive_doer', 'skill_usage_analyzer', 'suggestion_applier', 'crystal')
                    ORDER BY timestamp DESC
                """).fetchall()
                new_tasks_today = len(rows)
                task_types = [r["skill"] for r in rows]
            finally:
                conn.close()
        
        # Also check for tasks created in proactive_doer_tasks.json
        proactive_tasks_file = HERMES_HOME / "cache" / "proactive_doer_tasks.json"
        tasks_today = 0
        if proactive_tasks_file.exists():
            try:
                tasks = json.loads(proactive_tasks_file.read_text(encoding="utf-8"))
                today = datetime.now().date().isoformat()
                tasks_today = sum(1 for t in tasks if t.get("timestamp", "").startswith(today))
            except:
                pass
        
        total_new_tasks = new_tasks_today + tasks_today
        compliant = total_new_tasks >= 1
        
        # If not compliant, generate a task from suggestions or gaps
        generated_task = None
        if not compliant:
            generated_task = self._generate_new_task()
        
        self.results["iterative_attack"] = {
            "compliant": compliant,
            "details": {
                "new_tasks_today": new_tasks_today,
                "proactive_tasks_today": tasks_today,
                "task_types": task_types,
                "generated_task": generated_task is not None,
                "message": f"{total_new_tasks} autonomous tasks executed today" if compliant else "No autonomous task executed today"
            },
            "action": "execute_generated_task" if generated_task else None
        }
    
    def _generate_new_task(self) -> Dict[str, Any]:
        """Generate a new task from improvement suggestions or knowledge gaps."""
        # Try improvement suggestions first
        if IMPROVEMENT_SUGGESTIONS.exists():
            try:
                suggestions = json.loads(IMPROVEMENT_SUGGESTIONS.read_text(encoding="utf-8"))
                critical = [s for s in suggestions if s.get("severity") == "critical"]
                if critical:
                    s = critical[0]
                    return {
                        "source": "improvement_suggestions",
                        "type": "apply_fix",
                        "issue_type": s.get("issue_type"),
                        "priority": "critical",
                        "description": s.get("title")
                    }
            except:
                pass
        
        # Fallback: trigger skill usage analysis
        return {
            "source": "compliance_checker",
            "type": "run_skill_usage_analyzer",
            "priority": "high",
            "description": "Trigger skill usage analysis to find work"
        }
    
    def auto_correct(self) -> Dict[str, Any]:
        """Apply corrections for non-compliant rules."""
        actions_taken = {}
        
        for rule, result in self.results.items():
            if not result["compliant"] and result["action"]:
                if rule == "zero_trust":
                    actions_taken[rule] = self._correct_zero_trust()
                elif rule == "passive_income":
                    actions_taken[rule] = self._correct_passive_income()
                elif rule == "iterative_attack":
                    actions_taken[rule] = self._correct_iterative_attack()
        
        return actions_taken
    
    def _correct_zero_trust(self) -> str:
        """Trigger subagent_verifier on recent changes."""
        # Write task for subagent_verifier
        task_file = HERMES_HOME / "cache" / "subagent_verifier_tasks.json"
        task_file.parent.mkdir(parents=True, exist_ok=True)
        
        tasks = []
        if task_file.exists():
            try:
                tasks = json.loads(task_file.read_text(encoding="utf-8"))
            except:
                pass
        
        tasks.append({
            "timestamp": datetime.now().isoformat(),
            "type": "verify_recent_changes",
            "priority": "high",
            "scope": "recent_modifications"
        })
        
        task_file.write_text(json.dumps(tasks, ensure_ascii=False, indent=2), encoding="utf-8")
        return "subagent_verifier_task_queued"
    
    def _correct_passive_income(self) -> str:
        """Restart failed cron jobs."""
        # Write task for proactive_doer to restart cron
        task_file = HERMES_HOME / "cache" / "proactive_doer_tasks.json"
        task_file.parent.mkdir(parents=True, exist_ok=True)
        
        tasks = []
        if task_file.exists():
            try:
                tasks = json.loads(task_file.read_text(encoding="utf-8"))
            except:
                pass
        
        tasks.append({
            "timestamp": datetime.now().isoformat(),
            "type": "restart_failed_crons",
            "priority": "critical",
            "check_jobs": True
        })
        
        task_file.write_text(json.dumps(tasks, ensure_ascii=False, indent=2), encoding="utf-8")
        return "cron_restart_task_queued"
    
    def _correct_iterative_attack(self) -> str:
        """Execute generated task."""
        # The generated task is in self.results["iterative_attack"]["details"]["generated_task"]
        generated = self.results["iterative_attack"]["details"].get("generated_task")
        if generated:
            # Write to proactive_doer queue
            task_file = HERMES_HOME / "cache" / "proactive_doer_tasks.json"
            task_file.parent.mkdir(parents=True, exist_ok=True)
            
            tasks = []
            if task_file.exists():
                try:
                    tasks = json.loads(task_file.read_text(encoding="utf-8"))
                except:
                    pass
            
            tasks.append({
                "timestamp": datetime.now().isoformat(),
                "type": "execute_generated_task",
                "priority": "high",
                "generated_task": generated
            })
            
            task_file.write_text(json.dumps(tasks, ensure_ascii=False, indent=2), encoding="utf-8")
            return "generated_task_queued"
        return "no_task_generated"
    
    def log_to_feedback_store(self):
        """Log compliance check results to feedback_store for audit trail."""
        if not FEEDBACK_DB.exists():
            return
        
        conn = sqlite3.connect(str(FEEDBACK_DB), timeout=5)
        try:
            for rule, result in self.results.items():
                conn.execute("""
                    INSERT INTO feedback (skill, timestamp, result, tags, source)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    f"compliance_checker_{rule}",
                    datetime.now().isoformat(),
                    json.dumps({
                        "compliant": result["compliant"],
                        "details": result["details"],
                        "action_taken": result["action"]
                    }),
                    json.dumps(["compliance", rule]),
                    "compliance_checker"
                ))
            conn.commit()
        finally:
            conn.close()


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Compliance Checker - Verifies three autonomy rules")
    parser.add_argument("--check", action="store_true", help="Run compliance check")
    parser.add_argument("--auto-correct", action="store_true", help="Auto-correct violations")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    args = parser.parse_args()
    
    checker = ComplianceChecker()
    results = checker.check_all()
    
    if args.auto_correct:
        actions = checker.auto_correct()
        print(f"Auto-corrections: {actions}")
    
    checker.log_to_feedback_store()
    
    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        for rule, result in results.items():
            status = "✅" if result["compliant"] else "❌"
            print(f"{status} {rule.upper()}: {result['details'].get('message', 'N/A')}")


if __name__ == "__main__":
    main()
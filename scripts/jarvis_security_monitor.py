#!/usr/bin/env python3
"""
JARVIS Security & System Monitor.
Monitors system health, detects anomalies, and alerts.
Designed to run as a background process or cron job.

Usage:
  python scripts/jarvis_security_monitor.py          # One-shot check
  python scripts/jarvis_security_monitor.py --watch   # Continuous watch (every 60s)
  python scripts/jarvis_security_monitor.py --cron    # Cron-safe one-shot with output
"""

import os
import sys
import json
import time
import datetime
import subprocess
from pathlib import Path

# Add Hermes root and scripts to path
_here = Path(__file__).parent
sys.path.insert(0, str(_here.parent))   # Hermes root
sys.path.insert(0, str(_here))          # scripts/

# Add Hermes root to path
HERMES_ROOT = Path(__file__).parent.parent

# ─── Configuration ───────────────────────────────────────────────────────────

CONFIG = {
    "cpu_warn_pct": 90,          # CPU usage warning threshold
    "ram_warn_pct": 90,          # RAM usage warning threshold
    "disk_warn_pct": 90,         # Disk usage warning threshold
    "watch_interval": 60,        # Seconds between checks in watch mode
    "hermes_health_check": True, # Check if Hermes processes are alive
    "lm_studio_check": True,     # Check if LM Studio responds
    "log_file": HERMES_ROOT / "logs" / "security_monitor.jsonl",
}

# ─── System Checks ──────────────────────────────────────────────────────────

def get_cpu_usage():
    """Get CPU usage percentage."""
    try:
        import psutil
        return psutil.cpu_percent(interval=0.5)
    except ImportError:
        # Fallback for Windows
        try:
            result = subprocess.run(
                ["wmic", "cpu", "get", "loadpercentage"],
                capture_output=True, text=True, timeout=5
            )
            lines = result.stdout.strip().split("\n")
            if len(lines) >= 2:
                return float(lines[1].strip())
        except Exception:
            pass
    return None

def get_ram_usage():
    """Get RAM usage info."""
    try:
        import psutil
        mem = psutil.virtual_memory()
        return {
            "total_gb": round(mem.total / 1e9, 1),
            "used_gb": round(mem.used / 1e9, 1),
            "percent": mem.percent,
        }
    except ImportError:
        # Fallback
        try:
            result = subprocess.run(
                ["wmic", "OS", "get", "TotalVisibleMemorySize,FreePhysicalMemory", "/format:value"],
                capture_output=True, text=True, timeout=5
            )
            lines = result.stdout.strip().split("\n")
            vals = {}
            for line in lines:
                if "=" in line:
                    k, v = line.split("=", 1)
                    vals[k.strip()] = v.strip()
            if "TotalVisibleMemorySize" in vals and "FreePhysicalMemory" in vals:
                total = int(vals["TotalVisibleMemorySize"]) // 1024  # KB → MB
                free = int(vals["FreePhysicalMemory"]) // 1024
                used = total - free
                return {
                    "total_gb": round(total / 1024, 1),
                    "used_gb": round(used / 1024, 1),
                    "percent": round(used / total * 100, 1),
                }
        except Exception:
            pass
    return None

def get_disk_usage():
    """Get disk usage for D: drive."""
    try:
        import psutil
        disk = psutil.disk_usage("D:/")
        return {
            "total_gb": round(disk.total / 1e9, 1),
            "used_gb": round(disk.used / 1e9, 1),
            "free_gb": round(disk.free / 1e9, 1),
            "percent": disk.percent,
        }
    except ImportError:
        try:
            result = subprocess.run(
                ["wmic", "LogicalDisk", "where", "DeviceID='D:'",
                 "get", "Size,FreeSpace", "/format:value"],
                capture_output=True, text=True, timeout=5
            )
            vals = {}
            for line in result.stdout.strip().split("\n"):
                if "=" in line:
                    k, v = line.split("=", 1)
                    vals[k.strip()] = v.strip()
            if "Size" in vals and "FreeSpace" in vals:
                total = int(vals["Size"]) // (1024**3)
                free = int(vals["FreeSpace"]) // (1024**3)
                used = total - free
                return {
                    "total_gb": total,
                    "used_gb": used,
                    "free_gb": free,
                    "percent": round(used / total * 100, 1),
                }
        except Exception:
            pass
    return None

def check_lm_studio():
    """Check if LM Studio API is responding — через model_registry."""
    try:
        from model_registry import ping_all, get_model_config
        pings = ping_all(force=False)  # use cache, don't block on dead providers
        lms = pings.get("lm-studio", {})
        if lms.get("alive"):
            cfg = get_model_config(provider_name="lm-studio")
            models = []
            if cfg:
                models = [cfg.get("model", "unknown")]
            return {"alive": True, "models": models, "latency_ms": lms.get("latency_ms")}
        else:
            return {"alive": False, "error": lms.get("error", "LM Studio not responding")}
    except Exception as e:
        return {"alive": False, "error": str(e)}

def check_hermes_process():
    """Check if Hermes processes are running."""
    try:
        if sys.platform == "win32":
            result = subprocess.run(
                ["tasklist", "/FI", "IMAGENAME eq python*", "/FO", "CSV"],
                capture_output=True, text=True, timeout=5
            )
            # Count Hermes-related processes
            count = result.stdout.lower().count("hermes")
            return {"hermes_processes": count}
        else:
            result = subprocess.run(
                ["pgrep", "-f", "hermes"],
                capture_output=True, text=True, timeout=5
            )
            count = len(result.stdout.strip().split("\n")) if result.stdout.strip() else 0
            return {"hermes_processes": count}
    except Exception as e:
        return {"hermes_processes": -1, "error": str(e)}

def check_log_anomalies():
    """Basic log anomaly detection."""
    log_dir = HERMES_ROOT / "logs"
    if not log_dir.exists():
        return {"anomalies": 0}
    
    recent_errors = []
    for log_file in log_dir.glob("*.log"):
        if log_file.stat().st_size == 0:
            continue
        try:
            with open(log_file, "r", errors="ignore") as f:
                lines = f.readlines()[-100:]  # Last 100 lines
                for line in lines:
                    if "error" in line.lower() or "traceback" in line.lower() or "exception" in line.lower():
                        recent_errors.append({
                            "file": log_file.name,
                            "line": line.strip()[:200]
                        })
        except Exception:
            pass
    
    return {
        "anomalies": len(recent_errors),
        "recent_errors": recent_errors[:5]  # Top 5
    }


# ─── Alerting ─────────────────────────────────────────────────────────────

class AlertManager:
    """Manages alerts — dedup, severity, output."""
    
    def __init__(self):
        self.seen = set()
    
    def should_alert(self, key: str, ttl_seconds: int = 300) -> bool:
        """Rate-limit identical alerts."""
        now = time.time()
        if key in self._alert_times:
            if now - self._alert_times[key] < ttl_seconds:
                return False
        self._alert_times[key] = now
        return True
    
    _alert_times = {}
    
    @staticmethod
    def alert(message: str, severity: str = "info"):
        """Output an alert."""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        formatted = f"[{timestamp}] [{severity.upper()}] {message}"
        print(formatted)
        return formatted


# ─── Report ────────────────────────────────────────────────────────────────

def generate_report(warnings_only=False):
    """Generate a full system health report."""
    report = {
        "timestamp": datetime.datetime.now().isoformat(),
        "status": "healthy",
        "checks": {},
        "warnings": [],
        "alerts": [],
    }
    
    alerts = AlertManager()
    
    # CPU
    cpu = get_cpu_usage()
    report["checks"]["cpu"] = {"usage_pct": cpu}
    if cpu and cpu > CONFIG["cpu_warn_pct"]:
        report["status"] = "warning"
        msg = f"CPU usage at {cpu}% — exceeds threshold of {CONFIG['cpu_warn_pct']}%"
        report["warnings"].append(msg)
        alerts.alert(msg, "warning")
    
    # RAM
    ram = get_ram_usage()
    report["checks"]["ram"] = ram
    if ram and ram["percent"] > CONFIG["ram_warn_pct"]:
        report["status"] = "warning"
        msg = f"RAM usage at {ram['percent']}% ({ram['used_gb']}GB/{ram['total_gb']}GB)"
        report["warnings"].append(msg)
        alerts.alert(msg, "warning")
    
    # Disk
    disk = get_disk_usage()
    report["checks"]["disk"] = disk
    if disk and disk["percent"] > CONFIG["disk_warn_pct"]:
        report["status"] = "warning"
        msg = f"D: drive at {disk['percent']}% ({disk['free_gb']}GB free of {disk['total_gb']}GB)"
        report["warnings"].append(msg)
        alerts.alert(msg, "warning")
    
    # LM Studio
    if CONFIG["lm_studio_check"]:
        lms = check_lm_studio()
        report["checks"]["lm_studio"] = lms
        if not lms.get("alive"):
            report["status"] = "degraded"
            msg = "LM Studio API not responding — local fallback unavailable"
            report["warnings"].append(msg)
            alerts.alert(msg, "warning")
        else:
            report["checks"]["lm_studio"]["models_available"] = len(lms.get("models", []))
    
    # Hermes processes
    if CONFIG["hermes_health_check"]:
        proc = check_hermes_process()
        report["checks"]["hermes_processes"] = proc
    
    # Log anomalies
    logs = check_log_anomalies()
    report["checks"]["log_anomalies"] = logs
    if logs["anomalies"] > 0:
        report["status"] = "warning" if logs["anomalies"] < 10 else "degraded"
        for err in logs.get("recent_errors", []):
            report["alerts"].append(f"Log error in {err['file']}: {err['line']}")
    
    if warnings_only:
        return report["warnings"]
    
    return report


# ─── Main ──────────────────────────────────────────────────────────────────

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="JARVIS Security Monitor")
    parser.add_argument("--watch", action="store_true",
                       help="Continuous monitoring mode")
    parser.add_argument("--cron", action="store_true",
                       help="Cron mode — output JSON report")
    parser.add_argument("--interval", type=int, default=CONFIG["watch_interval"],
                       help=f"Watch interval in seconds (default: {CONFIG['watch_interval']})")
    parser.add_argument("--warnings-only", action="store_true",
                       help="Only show warnings and alerts")
    args = parser.parse_args()
    
    # Ensure log directory exists
    CONFIG["log_file"].parent.mkdir(parents=True, exist_ok=True)
    
    if args.watch:
        print(f"[JARVIS Security Monitor] Watching every {args.interval}s. Ctrl+C to stop.")
        try:
            while True:
                report = generate_report(warnings_only=args.warnings_only)
                status = report["status"]
                timestamp = datetime.datetime.now().strftime("%H:%M:%S")
                
                if args.warnings_only:
                    if report["warnings"]:
                        print(f"[{timestamp}] [{status.upper()}]")
                        for w in report["warnings"]:
                            print(f"  ⚠ {w}")
                else:
                    cpu = report["checks"].get("cpu", {}).get("usage_pct", "?")
                    ram = report["checks"].get("ram", {})
                    disk = report["checks"].get("disk", {})
                    lms = report["checks"].get("lm_studio", {})
                    
                    ram_str = f"{ram.get('percent', '?'):.0f}%" if ram else "?"
                    disk_str = f"{disk.get('percent', '?'):.0f}%" if disk else "?"
                    lms_str = "✓" if lms.get("alive") else "✗"
                    
                    print(f"[{timestamp}] [{status.upper()}] CPU:{cpu}% RAM:{ram_str} D:{disk_str} LM:{lms_str}")
                
                time.sleep(args.interval)
        except KeyboardInterrupt:
            print("\n[JARVIS Security Monitor] Stopped.")
    else:
        report = generate_report(warnings_only=args.warnings_only)
        
        if args.cron:
            print(json.dumps(report, indent=2, default=str))
        elif args.warnings_only:
            if report["warnings"]:
                print("⚠ Security Warnings:")
                for w in report["warnings"]:
                    print(f"  • {w}")
            else:
                print("✓ All systems nominal.")
        else:
            # Pretty output
            print("=" * 50)
            print(f"  JARVIS System Report — {report['timestamp']}")
            print(f"  Status: {report['status'].upper()}")
            print("=" * 50)
            
            cpu = report["checks"].get("cpu", {})
            if cpu.get("usage_pct"):
                print(f"  CPU:  {cpu['usage_pct']}%")
            
            ram = report["checks"].get("ram", {})
            if ram:
                print(f"  RAM:  {ram['percent']}% ({ram['used_gb']}GB/{ram['total_gb']}GB)")
            
            disk = report["checks"].get("disk", {})
            if disk:
                print(f"  DISK: {disk['percent']}% ({disk['free_gb']}GB free)")
            
            lms = report["checks"].get("lm_studio", {})
            print(f"  LM Studio: {'✓ Online' if lms.get('alive') else '✗ Offline'}")
            if lms.get("models_available"):
                print(f"  Models:   {lms['models_available']} available")
            
            proc = report["checks"].get("hermes_processes", {})
            if proc.get("hermes_processes", -1) >= 0:
                print(f"  Hermes:   {proc['hermes_processes']} process(es)")
            
            logs = report["checks"].get("log_anomalies", {})
            if logs.get("anomalies", 0) > 0:
                print(f"  Log anomalies: {logs['anomalies']}")
                for err in logs.get("recent_errors", []):
                    print(f"    ⚠ {err['file']}: {err['line'][:100]}")
            
            if report["warnings"]:
                print("\n  ⚠ Warnings:")
                for w in report["warnings"]:
                    print(f"    • {w}")
            
            if report["alerts"]:
                print("\n  🚨 Alerts:")
                for a in report["alerts"]:
                    print(f"    • {a}")
            
            print("=" * 50)


if __name__ == "__main__":
    main()

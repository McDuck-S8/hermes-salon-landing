#!/usr/bin/env python3
"""
Unified Bandwidth Sharing Launcher for Windows
Starts all available bandwidth sharing apps as background processes.
"""

import os
import sys
import subprocess
import time
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bandwidth_launcher.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class BandwidthApp:
    """Represents a bandwidth sharing application."""
    name: str
    executable_path: str
    install_url: str
    expected_earnings: str
    process_name: str
    startup_args: List[str] = None
    is_portable: bool = False
    
    def __post_init__(self):
        if self.startup_args is None:
            self.startup_args = []

class BandwidthLauncher:
    """Unified launcher for bandwidth sharing applications."""
    
    def __init__(self, config_file: str = "launcher_config.json"):
        self.config_file = Path(config_file)
        self.apps: Dict[str, BandwidthApp] = {}
        self.running_processes: Dict[str, subprocess.Popen] = {}
        self.config = self.load_config()
        
    def load_config(self) -> dict:
        """Load configuration from JSON file."""
        default_config = {
            "auto_start": True,
            "check_interval": 300,  # 5 minutes
            "log_level": "INFO",
            "apps_enabled": {
                "honeygain": True,
                "earnapp": True,
                "packetstream": True,
                "repocket": True,
                "earnfm": True,
                "bitping": True,
                "packetshare": True,
                "iproyal_pawns": True,
                "grass": True
            }
        }
        
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    # Merge with defaults
                    for key, value in default_config.items():
                        if key not in config:
                            config[key] = value
                    return config
            except Exception as e:
                logger.error(f"Error loading config: {e}")
                return default_config
        else:
            self.save_config(default_config)
            return default_config
    
    def save_config(self, config: dict = None):
        """Save configuration to JSON file."""
        if config is None:
            config = self.config
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving config: {e}")
    
    def discover_apps(self):
        """Discover installed bandwidth sharing applications."""
        # Common installation paths on Windows (limited for performance)
        common_paths = [
            Path(os.environ.get('PROGRAMFILES', 'C:\\Program Files')),
            Path(os.environ.get('PROGRAMFILES(X86)', 'C:\\Program Files (x86)')),
            Path(os.environ.get('LOCALAPPDATA', '')),
            Path(os.environ.get('APPDATA', '')),
        ]
        
        # App definitions with potential installation paths
        app_definitions = {
            "honeygain": BandwidthApp(
                name="Honeygain",
                executable_path="",  # Will be discovered
                install_url="https://www.honeygain.com/download-app",
                expected_earnings="$5-10/month",
                process_name="Honeygain.exe",
                startup_args=["--minimized"]
            ),
            "earnapp": BandwidthApp(
                name="EarnApp",
                executable_path="",
                install_url="https://earnapp.com/",
                expected_earnings="$5-10/month",
                process_name="EarnApp.exe",
                startup_args=["--minimized"]
            ),
            "packetstream": BandwidthApp(
                name="PacketStream",
                executable_path="",
                install_url="https://app.packetstream.io",
                expected_earnings="$0.50-2/month",
                process_name="PacketStream.exe"
            ),
            "repocket": BandwidthApp(
                name="Repocket",
                executable_path="",
                install_url="https://repocket.com/download-app",
                expected_earnings="$1-3/month",
                process_name="Repocket.exe"
            ),
            "earnfm": BandwidthApp(
                name="Earnfm",
                executable_path="",
                install_url="https://earn.fm/download",
                expected_earnings="$0.50-1/month",
                process_name="Earnfm.exe"
            ),
            "bitping": BandwidthApp(
                name="Bitping",
                executable_path="",
                install_url="https://bitping.com/earn",
                expected_earnings="$1-5/month",
                process_name="Bitping.exe"
            ),
            "packetshare": BandwidthApp(
                name="PacketShare",
                executable_path="",
                install_url="https://www.packetshare.io",
                expected_earnings="$0.30-1/month",
                process_name="PacketShare.exe"
            ),
            "iproyal_pawns": BandwidthApp(
                name="IPRoyal Pawns",
                executable_path="",
                install_url="https://pawns.app/downloads",
                expected_earnings="$0.50-2/month",
                process_name="Pawns.exe"
            ),
            "grass": BandwidthApp(
                name="Grass",
                executable_path="",
                install_url="https://www.grass.io/download",
                expected_earnings="Points (crypto)",
                process_name="Grass.exe"
            )
        }
        
        # Search for executables
        for app_name, app in app_definitions.items():
            if not self.config.get("apps_enabled", {}).get(app_name, True):
                continue
                
            found = False
            search_start = time.time()
            max_search_time = 5  # seconds
            
            for base_path in common_paths:
                if not base_path.exists():
                    continue
                    
                # Search for the executable
                for root, dirs, files in os.walk(base_path):
                    # Check timeout
                    if time.time() - search_start > max_search_time:
                        break
                        
                    if app.process_name.lower() in [f.lower() for f in files]:
                        app.executable_path = str(Path(root) / app.process_name)
                        found = True
                        break
                    
                    # Limit search depth
                    if str(root).count(os.sep) - str(base_path).count(os.sep) > 3:
                        continue
                
                if found:
                    break
            
            if found:
                self.apps[app_name] = app
                logger.info(f"Found {app.name} at {app.executable_path}")
            else:
                logger.warning(f"{app.name} not found. Download from: {app.install_url}")
    
    def start_app(self, app_name: str) -> bool:
        """Start a specific bandwidth sharing application."""
        if app_name not in self.apps:
            logger.error(f"App {app_name} not found")
            return False
        
        app = self.apps[app_name]
        
        # Check if already running
        if app_name in self.running_processes:
            if self.running_processes[app_name].poll() is None:
                logger.info(f"{app.name} is already running")
                return True
            else:
                # Process has exited, remove it
                del self.running_processes[app_name]
        
        try:
            # Build command
            cmd = [app.executable_path] + app.startup_args
            
            # Start process
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
            )
            
            self.running_processes[app_name] = process
            logger.info(f"Started {app.name} (PID: {process.pid})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start {app.name}: {e}")
            return False
    
    def stop_app(self, app_name: str) -> bool:
        """Stop a specific bandwidth sharing application."""
        if app_name not in self.running_processes:
            logger.warning(f"{app_name} is not running")
            return False
        
        try:
            process = self.running_processes[app_name]
            process.terminate()
            process.wait(timeout=10)  # Wait up to 10 seconds
            del self.running_processes[app_name]
            logger.info(f"Stopped {app_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to stop {app_name}: {e}")
            return False
    
    def start_all(self):
        """Start all available bandwidth sharing applications."""
        logger.info("Starting all bandwidth sharing applications...")
        
        started = 0
        for app_name in self.apps:
            if self.start_app(app_name):
                started += 1
            time.sleep(1)  # Small delay between starts
        
        logger.info(f"Started {started}/{len(self.apps)} applications")
        return started
    
    def stop_all(self):
        """Stop all running bandwidth sharing applications."""
        logger.info("Stopping all bandwidth sharing applications...")
        
        stopped = 0
        for app_name in list(self.running_processes.keys()):
            if self.stop_app(app_name):
                stopped += 1
        
        logger.info(f"Stopped {stopped} applications")
        return stopped
    
    def status(self) -> dict:
        """Get status of all applications."""
        status = {}
        for app_name, app in self.apps.items():
            is_running = app_name in self.running_processes and \
                        self.running_processes[app_name].poll() is None
            status[app_name] = {
                "name": app.name,
                "running": is_running,
                "pid": self.running_processes[app_name].pid if is_running else None,
                "expected_earnings": app.expected_earnings,
                "executable": app.executable_path
            }
        return status
    
    def monitor(self, interval: int = None):
        """Monitor running applications and restart if needed."""
        if interval is None:
            interval = self.config.get("check_interval", 300)
        
        logger.info(f"Starting monitor (checking every {interval} seconds)")
        
        try:
            while True:
                # Check for crashed processes
                for app_name in list(self.running_processes.keys()):
                    process = self.running_processes[app_name]
                    if process.poll() is not None:
                        logger.warning(f"{app_name} has crashed, restarting...")
                        del self.running_processes[app_name]
                        self.start_app(app_name)
                
                time.sleep(interval)
                
        except KeyboardInterrupt:
            logger.info("Monitor stopped by user")
    
    def generate_report(self) -> str:
        """Generate a status report."""
        status = self.status()
        
        report = [
            "=" * 60,
            "BANDWIDTH SHARING LAUNCHER STATUS REPORT",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "=" * 60,
            "",
            "APPLICATIONS:",
            "-" * 40
        ]
        
        total_expected = 0
        running_count = 0
        
        for app_name, app_status in status.items():
            status_icon = "✓" if app_status["running"] else "✗"
            report.append(f"{status_icon} {app_status['name']}")
            report.append(f"  Status: {'Running' if app_status['running'] else 'Stopped'}")
            if app_status["running"]:
                report.append(f"  PID: {app_status['pid']}")
                running_count += 1
            report.append(f"  Expected: {app_status['expected_earnings']}")
            report.append("")
        
        report.extend([
            "-" * 40,
            f"Running: {running_count}/{len(status)}",
            f"Total Expected: ~$10-20/month (conservative)",
            "=" * 60
        ])
        
        return "\n".join(report)

def main():
    """Main function."""
    launcher = BandwidthLauncher()
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "start":
            if len(sys.argv) > 2:
                # Start specific app
                app_name = sys.argv[2].lower()
                launcher.discover_apps()
                launcher.start_app(app_name)
            else:
                # Start all
                launcher.discover_apps()
                launcher.start_all()
                
        elif command == "stop":
            if len(sys.argv) > 2:
                # Stop specific app
                app_name = sys.argv[2].lower()
                launcher.stop_app(app_name)
            else:
                # Stop all
                launcher.stop_all()
                
        elif command == "status":
            launcher.discover_apps()
            print(launcher.generate_report())
            
        elif command == "monitor":
            launcher.discover_apps()
            launcher.monitor()
            
        elif command == "install":
            # Show installation instructions
            print("INSTALLATION INSTRUCTIONS")
            print("=" * 40)
            launcher.discover_apps()
            for app_name, app in launcher.apps.items():
                if not app.executable_path:
                    print(f"\n{app.name}:")
                    print(f"  Download: {app.install_url}")
                    print(f"  Expected: {app.expected_earnings}")
            
        else:
            print("Usage: python bandwidth_launcher.py [command] [app_name]")
            print("Commands:")
            print("  start [app_name]  - Start all or specific app")
            print("  stop [app_name]   - Stop all or specific app")
            print("  status            - Show status report")
            print("  monitor           - Monitor and restart crashed apps")
            print("  install           - Show installation instructions")
    else:
        # Interactive mode
        launcher.discover_apps()
        
        print("BANDWIDTH SHARING LAUNCHER")
        print("=" * 40)
        print("Commands:")
        print("  1. Start all apps")
        print("  2. Stop all apps")
        print("  3. Show status")
        print("  4. Monitor apps")
        print("  5. Show install instructions")
        print("  6. Exit")
        print()
        
        while True:
            try:
                choice = input("Enter choice (1-6): ").strip()
                
                if choice == "1":
                    launcher.start_all()
                elif choice == "2":
                    launcher.stop_all()
                elif choice == "3":
                    print(launcher.generate_report())
                elif choice == "4":
                    print("Starting monitor (Ctrl+C to stop)...")
                    launcher.monitor()
                elif choice == "5":
                    print("INSTALLATION INSTRUCTIONS")
                    print("=" * 40)
                    for app_name, app in launcher.apps.items():
                        if not app.executable_path:
                            print(f"\n{app.name}:")
                            print(f"  Download: {app.install_url}")
                            print(f"  Expected: {app.expected_earnings}")
                elif choice == "6":
                    print("Stopping all apps...")
                    launcher.stop_all()
                    print("Goodbye!")
                    break
                else:
                    print("Invalid choice")
                    
            except KeyboardInterrupt:
                print("\nStopping all apps...")
                launcher.stop_all()
                print("Goodbye!")
                break

if __name__ == "__main__":
    main()

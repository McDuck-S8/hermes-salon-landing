"""
Money4Band Native — Process Manager
════════════════════════════════════
Orchestrates all bandwidth-sharing app runners.
Handles start/stop/monitor/restart for all apps.
"""

import asyncio
import logging
import signal
import sys
import time
import json
from pathlib import Path
from typing import Dict, List, Optional

import yaml

from runner import BaseRunner, AppStatus
from apps import create_runner, RUNNERS

logger = logging.getLogger("m4b.manager")


class M4BManager:
    """Main manager for all Money4Band apps."""
    
    def __init__(self, config_path: str = "config.yaml"):
        self.config_path = Path(config_path)
        self.config = {}
        self.runners: Dict[str, BaseRunner] = {}
        self.running = False
        self._data_dir = Path("./data")
        self._log_dir = Path("./logs")
        self._check_interval = 60
        
        self.load_config()
    
    def load_config(self):
        """Load configuration from YAML."""
        if not self.config_path.exists():
            logger.warning(f"Config not found: {self.config_path}, using defaults")
            self.config = {"global": {}, "apps": {}}
            return
        
        with open(self.config_path, "r", encoding="utf-8") as f:
            self.config = yaml.safe_load(f) or {}
        
        global_cfg = self.config.get("global", {})
        self._data_dir = Path(global_cfg.get("data_dir", "./data"))
        self._log_dir = Path(global_cfg.get("log_dir", "./logs"))
        self._check_interval = global_cfg.get("check_interval", 60)
        
        self._data_dir.mkdir(parents=True, exist_ok=True)
        self._log_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate device ID if not present
        if "device" not in global_cfg:
            import hashlib, uuid
            device_id = hashlib.md5(str(uuid.getnode()).encode()).hexdigest()[:12]
            self.config["global"]["device"] = {"name": f"m4b-{device_id}"}
        
        logger.info(f"Config loaded: {self.config_path}")
        logger.info(f"Data dir: {self._data_dir}")
        logger.info(f"Log dir: {self._log_dir}")
    
    def init_runners(self):
        """Initialize runners for all configured apps."""
        apps_cfg = self.config.get("apps", {})
        
        for app_name, app_cfg in apps_cfg.items():
            if not app_cfg.get("enabled", False):
                logger.info(f"[{app_name}] Skipped (disabled)")
                continue
            
            runner = create_runner(app_name, app_cfg, self._data_dir)
            if runner:
                self.runners[app_name] = runner
                logger.info(f"[{app_name}] Runner initialized")
            else:
                logger.warning(f"[{app_name}] Unknown app, no runner available")
        
        logger.info(f"Runners ready: {list(self.runners.keys())}")
    
    def start_all(self) -> Dict[str, bool]:
        """Start all enabled apps."""
        results = {}
        for name, runner in self.runners.items():
            success = runner.start()
            results[name] = success
            if not success:
                logger.error(f"[{name}] Failed to start: {runner.status.error}")
        return results
    
    def stop_all(self):
        """Stop all running apps."""
        for name, runner in self.runners.items():
            runner.stop()
        logger.info("All apps stopped")
    
    def get_all_status(self) -> List[dict]:
        """Get status of all apps."""
        return [runner.get_status().to_dict() for runner in self.runners.values()]
    
    async def monitor_loop(self):
        """Main monitoring loop — health check + auto-restart."""
        self.running = True
        logger.info(f"Monitor started (interval: {self._check_interval}s)")
        
        while self.running:
            for name, runner in self.runners.items():
                if not runner.status.enabled:
                    continue
                
                healthy = runner.health_check()
                if not healthy and runner.status.enabled:
                    logger.warning(f"[{name}] Unhealthy, restarting...")
                    runner.stop()
                    await asyncio.sleep(2)
                    runner.start()
            
            # Save status snapshot
            status_file = self._data_dir / "status.json"
            with open(status_file, "w") as f:
                json.dump(self.get_all_status(), f, indent=2)
            
            await asyncio.sleep(self._check_interval)
    
    def shutdown(self):
        """Graceful shutdown."""
        self.running = False
        self.stop_all()
        logger.info("M4B Manager shut down")


async def main():
    """Entry point."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler("logs/m4b.log", encoding="utf-8"),
        ],
    )
    
    manager = M4BManager("config.yaml")
    manager.init_runners()
    
    if not manager.runners:
        logger.warning("No apps enabled! Edit config.yaml to enable apps.")
        logger.info("Available apps:", list(RUNNERS.keys()))
        return
    
    # Start all apps
    results = manager.start_all()
    started = sum(1 for v in results.values() if v)
    logger.info(f"Started {started}/{len(results)} apps")
    
    # Handle signals
    loop = asyncio.get_event_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, manager.shutdown)
        except NotImplementedError:
            pass  # Windows
    
    # Run monitor
    try:
        await manager.monitor_loop()
    except KeyboardInterrupt:
        manager.shutdown()


if __name__ == "__main__":
    asyncio.run(main())

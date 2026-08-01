"""
Money4Band Native — App Runner Base
════════════════════════════════════
Base class for all bandwidth-sharing app runners.
Each runner knows how to:
  1. Check if the app is installed / configured
  2. Start the app as a native process
  3. Monitor health (API ping, process alive)
  4. Stop the app gracefully
  5. Get earnings/status (when API available)
"""

import os
import sys
import time
import json
import asyncio
import logging
import subprocess
import hashlib
import uuid
from pathlib import Path
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from dataclasses import dataclass, field

logger = logging.getLogger("m4b.runner")


@dataclass
class AppStatus:
    """Status of a bandwidth-sharing app"""
    name: str
    enabled: bool
    running: bool = False
    pid: Optional[int] = None
    uptime: float = 0
    last_check: float = 0
    earnings: float = 0
    bandwidth_shared: float = 0  # MB
    error: Optional[str] = None
    config_ok: bool = False
    
    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "enabled": self.enabled,
            "running": self.running,
            "pid": self.pid,
            "uptime": f"{self.uptime:.0f}s",
            "earnings": f"${self.earnings:.4f}",
            "bandwidth": f"{self.bandwidth_shared:.1f}MB",
            "error": self.error,
            "config_ok": self.config_ok,
        }


class BaseRunner(ABC):
    """Base class for bandwidth-sharing app runners"""
    
    # Override in subclasses
    APP_NAME: str = "unknown"
    APP_URL: str = ""
    BINARY_NAME: str = ""
    
    def __init__(self, config: dict, data_dir: Path):
        self.config = config
        self.data_dir = data_dir
        self.process: Optional[subprocess.Popen] = None
        self.status = AppStatus(
            name=self.APP_NAME,
            enabled=config.get("enabled", False),
        )
        self._start_time = 0
        self._data_dir = data_dir / self.APP_NAME
        self._data_dir.mkdir(parents=True, exist_ok=True)
        self._log_file = None
    
    @abstractmethod
    def check_config(self) -> bool:
        """Verify required config fields are present. Returns True if OK."""
        pass
    
    @abstractmethod
    def get_start_command(self) -> list:
        """Return the command to start the app as a list of args."""
        pass
    
    def find_binary(self) -> Optional[str]:
        """Try to find the app binary on the system."""
        # Check common locations
        home = Path.home()
        search_paths = [
            home / ".local" / "bin",
            Path("/usr/local/bin"),
            Path("/usr/bin"),
            Path("/opt"),
            home / "Downloads",
            self._data_dir,
        ]
        
        if self.BINARY_NAME:
            for p in search_paths:
                binary = p / self.BINARY_NAME
                if binary.exists():
                    return str(binary)
                # Windows
                binary_win = p / (self.BINARY_NAME + ".exe")
                if binary_win.exists():
                    return str(binary_win)
        
        # Check PATH
        import shutil
        found = shutil.which(self.BINARY_NAME)
        if found:
            return found
        
        return None
    
    def start(self) -> bool:
        """Start the app as a background process."""
        if self.process and self.process.poll() is None:
            logger.warning(f"[{self.APP_NAME}] Already running (PID {self.process.pid})")
            return True
        
        if not self.check_config():
            self.status.error = "Configuration incomplete"
            self.status.config_ok = False
            logger.error(f"[{self.APP_NAME}] Config check failed")
            return False
        
        self.status.config_ok = True
        
        try:
            cmd = self.get_start_command()
            if not cmd:
                self.status.error = "No start command available"
                logger.error(f"[{self.APP_NAME}] No start command")
                return False
            
            log_path = self._data_dir / "output.log"
            self._log_file = open(log_path, "a", encoding="utf-8", errors="replace")
            
            self.process = subprocess.Popen(
                cmd,
                stdout=self._log_file,
                stderr=subprocess.STDOUT,
                cwd=str(self._data_dir),
                creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0),
            )
            
            self._start_time = time.time()
            self.status.running = True
            self.status.pid = self.process.pid
            self.status.error = None
            
            logger.info(f"[{self.APP_NAME}] Started (PID {self.process.pid})")
            return True
            
        except FileNotFoundError:
            self.status.error = f"Binary not found: {cmd[0] if cmd else '?'}"
            self.status.running = False
            logger.error(f"[{self.APP_NAME}] Binary not found")
            return False
        except Exception as e:
            self.status.error = str(e)
            self.status.running = False
            logger.error(f"[{self.APP_NAME}] Start failed: {e}")
            return False
    
    def stop(self):
        """Stop the app gracefully."""
        if self.process:
            try:
                self.process.terminate()
                try:
                    self.process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    self.process.kill()
                    self.process.wait(timeout=5)
            except Exception as e:
                logger.error(f"[{self.APP_NAME}] Stop error: {e}")
            finally:
                self.process = None
                self.status.running = False
                self.status.pid = None
                if self._log_file:
                    self._log_file.close()
                    self._log_file = None
                logger.info(f"[{self.APP_NAME}] Stopped")
    
    def health_check(self) -> bool:
        """Check if the app is healthy."""
        if not self.process:
            return False
        
        poll = self.process.poll()
        if poll is not None:
            # Process exited
            self.status.running = False
            self.status.pid = None
            self.status.error = f"Process exited with code {poll}"
            logger.warning(f"[{self.APP_NAME}] Process exited (code {poll})")
            return False
        
        self.status.running = True
        self.status.uptime = time.time() - self._start_time
        self.status.last_check = time.time()
        return True
    
    def get_status(self) -> AppStatus:
        """Get current status."""
        self.health_check()
        return self.status


class DummyRunner(BaseRunner):
    """Placeholder for apps without native CLI support (e.g., Grass = browser extension)."""
    
    APP_NAME = "dummy"
    
    def check_config(self) -> bool:
        return False
    
    def get_start_command(self) -> list:
        return []

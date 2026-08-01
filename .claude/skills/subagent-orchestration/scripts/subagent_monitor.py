#!/usr/bin/env python3
"""
Subagent Monitor — Monitors subagent execution, provides heartbeats, and handles timeouts.
"""

import asyncio
import json
import logging
import os
import sys
import time
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

HERMES_HOME = Path(os.environ.get("HERMES_HOME", "D:/Portable_Soft/hermes"))
sys.path.insert(0, str(HERMES_HOME))

# Import from local scripts directory
sys.path.insert(0, str(HERMES_HOME / ".claude/skills/subagent-orchestration/scripts"))
from subagent_orchestrator import SubagentOrchestrator, SubagentStatus

# Logging setup
LOG_DIR = HERMES_HOME / "logs" / "subagent_orchestration"
LOG_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / f"monitor_{datetime.now().strftime('%Y%m%d')}.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


@dataclass
class MonitorConfig:
    heartbeat_interval: int = 10  # seconds
    timeout_threshold: int = 300  # 5 minutes
    cleanup_interval: int = 60    # seconds


class SubagentMonitor:
    """Monitors running subagents and handles timeouts."""
    
    def __init__(self, orchestrator: SubagentOrchestrator, config: MonitorConfig = None):
        self.orchestrator = orchestrator
        self.config = config or MonitorConfig()
        self._running = False
        self._monitor_task = None
    
    async def start(self):
        """Start monitoring loop."""
        self._running = True
        self._monitor_task = asyncio.create_task(self._monitor_loop())
        logger.info("Subagent monitor started")
    
    async def stop(self):
        """Stop monitoring loop."""
        self._running = False
        if self._monitor_task:
            self._monitor_task.cancel()
            try:
                await self._monitor_task
            except asyncio.CancelledError:
                pass
        logger.info("Subagent monitor stopped")
    
    async def _monitor_loop(self):
        """Main monitoring loop."""
        while self._running:
            try:
                await self._check_subagents()
                await self._cleanup_old()
            except Exception as e:
                logger.error(f"Monitor error: {e}")
            
            await asyncio.sleep(self.config.heartbeat_interval)
    
    async def _check_subagents(self):
        """Check all running subagents for heartbeats and timeouts."""
        now = datetime.now()
        
        for info in self.orchestrator.list_subagents():
            if info.status != SubagentStatus.RUNNING:
                continue
            
            # Check last heartbeat
            if info.last_heartbeat:
                try:
                    last_hb = datetime.fromisoformat(info.last_heartbeat)
                    elapsed = (now - last_hb).total_seconds()
                    
                    if elapsed > self.config.timeout_threshold:
                        logger.warning(f"Subagent {info.subagent_id} timed out (no heartbeat for {elapsed:.0f}s)")
                        # Could trigger retry or mark as failed here
                        
                except Exception as e:
                    logger.warning(f"Failed to parse heartbeat for {info.subagent_id}: {e}")
            
            # Update heartbeat for running subagents
            info.last_heartbeat = now.isoformat()
    
    async def _cleanup_old(self):
        """Clean up old completed/failed subagents beyond retention."""
        cutoff = datetime.now() - timedelta(hours=24)
        
        to_remove = []
        for subagent_id, info in self.orchestrator.subagents.items():
            if info.status in (SubagentStatus.COMPLETED, SubagentStatus.FAILED):
                try:
                    completed = datetime.fromisoformat(info.completed_at) if info.completed_at else None
                    if completed and completed < cutoff:
                        to_remove.append(subagent_id)
                except Exception:
                    pass
        
        for subagent_id in to_remove:
            del self.orchestrator.subagents[subagent_id]
            logger.info(f"Cleaned up old subagent: {subagent_id}")
    
    def get_running(self) -> List:
        """Get all running subagents."""
        return [s for s in self.orchestrator.list_subagents() if s.status == SubagentStatus.RUNNING]
    
    def get_stalled(self, threshold_seconds: int = 60) -> List:
        """Get subagents that haven't sent heartbeat recently."""
        now = datetime.now()
        stalled = []
        
        for info in self.orchestrator.list_subagents():
            if info.status == SubagentStatus.RUNNING and info.last_heartbeat:
                try:
                    last_hb = datetime.fromisoformat(info.last_heartbeat)
                    if (now - last_hb).total_seconds() > threshold_seconds:
                        stalled.append(info)
                except Exception:
                    pass
        
        return stalled
    
    def get_stats(self) -> Dict:
        """Get monitoring statistics."""
        all_agents = self.orchestrator.list_subagents()
        
        return {
            "total": len(all_agents),
            "running": len([s for s in all_agents if s.status == SubagentStatus.RUNNING]),
            "completed": len([s for s in all_agents if s.status == SubagentStatus.COMPLETED]),
            "failed": len([s for s in all_agents if s.status == SubagentStatus.FAILED]),
            "pending": len([s for s in all_agents if s.status == SubagentStatus.PENDING]),
            "retrying": len([s for s in all_agents if s.status == SubagentStatus.RETRYING]),
            "stalled": len(self.get_stalled()),
        }


async def main():
    """CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Subagent Monitor")
    parser.add_argument("--daemon", action="store_true", help="Run as daemon")
    parser.add_argument("--stats", action="store_true", help="Show stats")
    parser.add_argument("--list-running", action="store_true", help="List running subagents")
    parser.add_argument("--list-stalled", action="store_true", help="List stalled subagents")
    
    args = parser.parse_args()
    
    orchestrator = SubagentOrchestrator()
    monitor = SubagentMonitor(orchestrator)
    
    if args.daemon:
        await monitor.start()
        # Keep running
        try:
            while True:
                await asyncio.sleep(60)
        except KeyboardInterrupt:
            await monitor.stop()
    
    elif args.stats:
        stats = monitor.get_stats()
        print(json.dumps(stats, ensure_ascii=False, indent=2))
    
    elif args.list_running:
        running = monitor.get_running()
        for s in running:
            print(f"{s.subagent_id}: {s.task.task_type} - {s.status.value} (retries: {s.retry_count})")
    
    elif args.list_stalled:
        stalled = monitor.get_stalled()
        for s in stalled:
            print(f"{s.subagent_id}: {s.task.task_type} - no heartbeat")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    import json
    asyncio.run(main())
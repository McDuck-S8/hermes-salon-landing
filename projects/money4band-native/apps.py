"""
Money4Band Native — App-specific Runners
═════════════════════════════════════════
Native runners for each bandwidth-sharing app.
Each knows how to start/monitor its specific app.
"""

import os
import sys
import json
import time
import hashlib
import platform
from pathlib import Path
from typing import Optional

from runner import BaseRunner


class HoneygainRunner(BaseRunner):
    """Honeygain — share bandwidth, earn credits"""
    APP_NAME = "honeygain"
    APP_URL = "https://dashboard.honeygain.com"
    BINARY_NAME = "honeygain"
    
    def check_config(self) -> bool:
        email = self.config.get("email", "")
        password = self.config.get("password", "")
        token = self.config.get("device_token", "")
        return bool(email and password) or bool(token)
    
    def get_start_command(self) -> list:
        binary = self.find_binary()
        if binary:
            cmd = [binary, "--headless"]
            token = self.config.get("device_token", "")
            if token:
                cmd.extend(["--token", token])
            else:
                cmd.extend(["--email", self.config["email"], "--password", self.config["password"]])
            mode = self.config.get("mode", "share")
            cmd.extend(["--mode", mode])
            return cmd
        
        # Try pip-installed honeygain module
        return [sys.executable, "-m", "honeygain", "--headless"]


class EarnAppRunner(BaseRunner):
    """EarnApp (Bright Data) — earn by sharing bandwidth"""
    APP_NAME = "earnapp"
    APP_URL = "https://earnapp.com/dashboard"
    BINARY_NAME = "earnapp"
    
    def check_config(self) -> bool:
        return bool(self.config.get("redeem_code") or self.config.get("email"))
    
    def get_start_command(self) -> list:
        binary = self.find_binary()
        if binary:
            cmd = [binary]
            redeem = self.config.get("redeem_code", "")
            if redeem:
                cmd.extend(["--redeem", redeem])
            return cmd
        
        # EarnApp typically needs its native binary
        return []


class PacketStreamRunner(BaseRunner):
    """PacketStream — sell your bandwidth"""
    APP_NAME = "packetstream"
    APP_URL = "https://packetstream.io/dashboard"
    BINARY_NAME = "psclient"
    
    def check_config(self) -> bool:
        return bool(self.config.get("psk"))
    
    def get_start_command(self) -> list:
        binary = self.find_binary()
        if binary:
            return [binary, "--psk", self.config["psk"]]
        return []


class PawnsRunner(BaseRunner):
    """Pawns.app — share bandwidth, earn money"""
    APP_NAME = "pawns"
    APP_URL = "https://pawns.app"
    BINARY_NAME = "pawns-cli"
    
    def check_config(self) -> bool:
        return bool(self.config.get("email") or self.config.get("invite_code"))
    
    def get_start_command(self) -> list:
        binary = self.find_binary()
        if binary:
            cmd = [binary]
            email = self.config.get("email", "")
            if email:
                cmd.extend(["--email", email, "--password", self.config.get("password", "")])
            invite = self.config.get("invite_code", "")
            if invite:
                cmd.extend(["--invite", invite])
            return cmd
        return []


class TraffmonetizerRunner(BaseRunner):
    """Traffmonetizer — monetize your traffic"""
    APP_NAME = "traffmonetizer"
    APP_URL = "https://traffmonetizer.com"
    BINARY_NAME = "traffmonetizer"
    
    def check_config(self) -> bool:
        return bool(self.config.get("token"))
    
    def get_start_command(self) -> list:
        binary = self.find_binary()
        if binary:
            return [binary, "start", "--token", self.config["token"]]
        
        # Try Docker CLI or native
        return [sys.executable, "-m", "traffmonetizer", "start", "--token", self.config["token"]]


class Peer2ProfitRunner(BaseRunner):
    """Peer2Profit — sell your bandwidth"""
    APP_NAME = "peer2profit"
    APP_URL = "https://peer2profit.com"
    BINARY_NAME = "peer2profit"
    
    def check_config(self) -> bool:
        return bool(self.config.get("token"))
    
    def get_start_command(self) -> list:
        binary = self.find_binary()
        if binary:
            return [binary, self.config["token"]]
        return []


class BitpingRunner(BaseRunner):
    """Bitping — earn from your internet connection"""
    APP_NAME = "bitping"
    APP_URL = "https://app.bitping.com"
    BINARY_NAME = "bitping-node"
    
    def check_config(self) -> bool:
        return bool(self.config.get("node_key") or self.config.get("email"))
    
    def get_start_command(self) -> list:
        binary = self.find_binary()
        if binary:
            cmd = [binary]
            key = self.config.get("node_key", "")
            if key:
                cmd.extend(["--node-key", key])
            return cmd
        return []


# ─── Runner Registry ────────────────────────────────────

RUNNERS = {
    "honeygain": HoneygainRunner,
    "earnapp": EarnAppRunner,
    "packetstream": PacketStreamRunner,
    "pawns": PawnsRunner,
    "traffmonetizer": TraffmonetizerRunner,
    "peer2profit": Peer2ProfitRunner,
    "bitping": BitpingRunner,
    # "grass": GrassRunner,  # Browser-based, needs special handling
}


def create_runner(app_name: str, config: dict, data_dir: Path) -> Optional[BaseRunner]:
    """Create a runner for the given app name."""
    runner_cls = RUNNERS.get(app_name)
    if runner_cls:
        return runner_cls(config, data_dir)
    return None

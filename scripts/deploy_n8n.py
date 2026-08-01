#!/usr/bin/env python3
"""
n8n Deployment Script for Hermes
Sets up n8n with Telegram CPA funnel workflow
"""
import os
import json
import subprocess
import time
from pathlib import Path

N8N_WORKFLOW_PATH = Path("/d/Portable_Soft/hermes/scripts/n8n_telegram_cpa_funnel.json")
N8N_DATA_DIR = Path.home() / ".n8n"
N8N_PORT = 5678

def install_n8n():
    """Install n8n globally via npm"""
    print("Installing n8n...")
    result = subprocess.run(["npm", "install", "-g", "n8n"], capture_output=True, text=True, timeout=120, shell=True)
    if result.returncode != 0:
        print(f"npm install failed: {result.stderr}")
        return False
    print("n8n installed successfully")
    return True

def start_n8n():
    """Start n8n in background"""
    print("Starting n8n...")
    env = os.environ.copy()
    env["N8N_USER_FOLDER"] = str(N8N_DATA_DIR)
    env["N8N_PORT"] = str(N8N_PORT)
    env["N8N_HOST"] = "localhost"
    env["WEBHOOK_URL"] = f"http://localhost:{N8N_PORT}"
    
    # Start n8n in background
    process = subprocess.Popen(
        "n8n start",
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True
    )
    
    # Wait for n8n to start
    time.sleep(10)
    
    # Check if process is still running
    if process.poll() is None:
        print(f"n8n started on http://localhost:{N8N_PORT}")
        return process
    else:
        stdout, stderr = process.communicate()
        print(f"n8n failed to start: {stderr.decode()}")
        return None

def import_workflow():
    """Import workflow via n8n CLI"""
    print("Importing workflow...")
    if not N8N_WORKFLOW_PATH.exists():
        print(f"Workflow file not found: {N8N_WORKFLOW_PATH}")
        return False
    
    # Import workflow
    result = subprocess.run(
        f"n8n import:workflow --input {N8N_WORKFLOW_PATH}",
        capture_output=True, text=True, timeout=60, shell=True
    )
    
    if result.returncode == 0:
        print("Workflow imported successfully")
        return True
    else:
        print(f"Import failed: {result.stderr}")
        return False

def activate_workflow(workflow_id: str):
    """Activate workflow"""
    result = subprocess.run(
        f"n8n activate {workflow_id}",
        capture_output=True, text=True, timeout=30, shell=True
    )
    if result.returncode == 0:
        print(f"Workflow {workflow_id} activated")
        return True
    else:
        print(f"Activation failed: {result.stderr}")
        return False

def main():
    print("=== n8n Deployment for Hermes ===")
    
    # Check if n8n is already installed
    result = subprocess.run("n8n --version", capture_output=True, text=True, shell=True)
    if result.returncode != 0:
        if not install_n8n():
            return 1
    else:
        print(f"n8n already installed: {result.stdout.strip()}")
    
    # Start n8n
    process = start_n8n()
    if not process:
        return 1
    
    # Import workflow
    if not import_workflow():
        return 1
    
    # Get workflow ID (from import output or list)
    result = subprocess.run("n8n list:workflow", capture_output=True, text=True, shell=True)
    print(f"Workflows: {result.stdout}")
    
    print("n8n is running. Configure credentials in UI:")
    print(f"  http://localhost:{N8N_PORT}")
    print("  - Telegram Bot credential")
    print("  - HTTP Request credentials for CPAGrip/ActionPay/AdCombo")
    print("  - Set webhook URL in Telegram bot settings")
    
    return 0

if __name__ == "__main__":
    exit(main())
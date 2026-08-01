#!/bin/bash
# AI OFM Tribute — Cron Wrapper Script Template
# 
# Place this in HERMES_HOME/scripts/ so the cron scheduler can find it.
# The cron job in jobs.json should reference just the filename:
#   "script": "ai-ofm-generate.sh"
#
# Customize the PROJECT_DIR path for your environment.

PROJECT_DIR="{{PROJECT_DIR}}"
cd "${PROJECT_DIR}" && bash scripts/cron.sh
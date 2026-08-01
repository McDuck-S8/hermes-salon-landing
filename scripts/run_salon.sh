#!/bin/bash
cd D:/Portable_Soft/hermes
export TELEGRAM_BOT_TOKEN=$(grep TELEGRAM_BOT_TOKEN .env | cut -d= -f2)
export PROXY="socks5://127.0.0.1:10806"
"/d/Program Files/Python311/python.exe" scripts/salon_booking_bot.py 2>&1

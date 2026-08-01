@echo off
rem Hermes Agent Gateway - Messaging Platform Integration
cd /d D:\Portable_Soft\hermes-usb-portable-main\src\hermes-agent
set "HERMES_HOME=D:\Portable_Soft\hermes-usb-portable-main\data"
set "PYTHONIOENCODING=utf-8"
set "HERMES_GATEWAY_DETACHED=1"
set "VIRTUAL_ENV=D:\Portable_Soft\hermes-usb-portable-main\.cache\runtimes\windows-x64\venv"
D:\Portable_Soft\hermes-usb-portable-main\.cache\runtimes\windows-x64\venv\Scripts\pythonw.exe -m hermes_cli.main gateway run
exit /b 0

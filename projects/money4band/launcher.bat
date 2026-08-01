@echo off
REM Bandwidth Sharing Launcher - Windows Batch File
REM Usage: launcher.bat [command] [app_name]

setlocal enabledelayedexpansion

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.7+ from https://www.python.org/
    pause
    exit /b 1
)

REM Get the directory of this batch file
set "SCRIPT_DIR=%~dp0"

REM Run the launcher
if "%~1"=="" (
    echo BANDWIDTH SHARING LAUNCHER
    echo ========================
    echo.
    echo Available commands:
    echo   start [app_name]  - Start all or specific app
    echo   stop [app_name]   - Stop all or specific app
    echo   status            - Show status report
    echo   monitor           - Monitor and restart crashed apps
    echo   install           - Show installation instructions
    echo.
    echo Examples:
    echo   launcher.bat start          - Start all apps
    echo   launcher.bat start honeygain - Start Honeygain only
    echo   launcher.bat status        - Show status
    echo   launcher.bat monitor       - Start monitoring
    echo.
    python "%SCRIPT_DIR%bandwidth_launcher.py"
) else (
    python "%SCRIPT_DIR%bandwidth_launcher.py" %*
)

pause

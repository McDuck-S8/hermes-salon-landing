@echo off
echo Starting MCP servers...
start "BrowserClaw+BrowserOS" cmd /k "cd /d D:\Portable_Soft\hermes && hermes gateway run"
timeout /t 5 >nul

echo Starting browser-harness...
start "browser-harness" cmd /k "cd /d D:\Portable_Soft\hermes\browser-harness && python -m src.browser_harness.daemon"
timeout /t 3 >nul

echo Launching agent workspaces...
start "orchestrator" cmd /k "D:\Portable_Soft\hermes\launch\launch_orchestrator.bat"
start "coder" cmd /k "D:\Portable_Soft\hermes\launch\launch_coder.bat"
start "browser" cmd /k "D:\Portable_Soft\hermes\launch\launch_browser.bat"
start "researcher" cmd /k "D:\Portable_Soft\hermes\launch\launch_researcher.bat"
start "deployer" cmd /k "D:\Portable_Soft\hermes\launch\launch_deployer.bat"
start "cpa-operator" cmd /k "D:\Portable_Soft\hermes\launch\launch_cpa-operator.bat"

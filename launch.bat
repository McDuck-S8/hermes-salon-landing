@echo off
title Hermes Agent
setlocal enabledelayedexpansion

set "PORTABLE_ROOT=%~dp0"
set "PORTABLE_ROOT=%PORTABLE_ROOT:~0,-1%"
set "HERMES_HOME=%PORTABLE_ROOT%"
set "HERMES_AGENT=%PORTABLE_ROOT%\hermes-agent"
set "HERMES_EXE=%HERMES_AGENT%\.venv\Scripts\hermes.exe"
set "HERMES_BIN=%PORTABLE_ROOT%\bin"

set "PATH=%HERMES_AGENT%\.venv\Scripts;%HERMES_BIN%;%PATH%"
set "PYTHONNOUSERSITE=1"
set "PYTHONHOME="
set "PYTHONPATH="

:detect_status
set "CFG_OK=0"
if exist "%HERMES_HOME%\.env" (
    findstr /R /C:"^[A-Z].*=[^#].*" "%HERMES_HOME%\.env" >nul 2>&1
    if not errorlevel 1 set "CFG_OK=1"
)
set "PRV_NAME="
set "MDL_NAME="
if exist "%HERMES_HOME%\config.yaml" (
    for /f "tokens=2 delims=: " %%a in ('findstr /C:"provider:" "%HERMES_HOME%\config.yaml"') do set "PRV_NAME=%%a"
    for /f "delims=" %%a in ('findstr /C:"default:" "%HERMES_HOME%\config.yaml"') do (
        set "L=%%a"
        set "MDL_NAME=!L:*default: =!"
        set "MDL_NAME=!MDL_NAME:"=!"
        for /f "tokens=* delims= " %%m in ("!MDL_NAME!") do set "MDL_NAME=%%m"
    )
)
set "GW_PID="
if exist "%HERMES_HOME%\data\gateway.pid" (
    for /f "usebackq tokens=2 delims=:," %%a in (`findstr /R /C:"pid" "%HERMES_HOME%\data\gateway.pid" 2^>nul`) do (
        set "raw=%%a"
        set "GW_PID=!raw: =!"
    )
)
set "GW_RUN=0"
if defined GW_PID (
    tasklist /FI "PID eq !GW_PID!" 2>nul | findstr /I "!GW_PID!" >nul
    if not errorlevel 1 set "GW_RUN=1"
)
set "HERM_VER=unknown"
if exist "%HERMES_AGENT%\hermes_cli\__init__.py" (
    for /f "usebackq tokens=3" %%a in (`findstr /R /C:"__version__" "%HERMES_AGENT%\hermes_cli\__init__.py"`) do (
        set "rawv=%%a"
        set "HERM_VER=!rawv:"=!"
    )
)

:show_menu
cls
echo.
echo ============================================================
echo                       HERMES  PORTABLE
echo                    AI Agent for Everyone
echo ============================================================
echo.
if %CFG_OK%==1 (echo  Status    [OK] Configured) else (echo  Status    [x]  Not configured)
if defined PRV_NAME echo  Provider  %PRV_NAME%
if defined MDL_NAME echo  Model     %MDL_NAME%
if %GW_RUN%==1 (echo  Gateway   [OK] Running) else (echo  Gateway   [ ] Stopped)
echo  Version   v%HERM_VER%
echo  Path      %PORTABLE_ROOT%
echo.
echo ------------------------------------------------------------
echo.
echo  [1]  Start Chat                    TUI interface
echo  [2]  One-shot Prompt               Quick question
echo  [3]  Switch Model                  Change model/provider
echo  [4]  Setup / Configure             API keys and settings
if %GW_RUN%==1 (
    echo  [5]  Stop Gateway                 Stop messaging
) else (
    echo  [5]  Start Gateway                Messaging gateway
)
echo  [6]  Advanced                      More options
echo  [0]  Exit
echo.
echo ------------------------------------------------------------
echo.
set /p "CHOICE=  Select [0-6]: "
if "%CHOICE%"=="0" goto :menu_exit
if "%CHOICE%"=="6" goto :show_advanced
if "%CHOICE%"=="5" goto :menu_gateway
if "%CHOICE%"=="4" goto :menu_setup
if "%CHOICE%"=="3" goto :menu_model
if "%CHOICE%"=="2" goto :menu_oneshot
if "%CHOICE%"=="1" goto :menu_chat
goto :show_menu

:menu_chat
echo.
"%HERMES_EXE%"
goto :show_menu

:menu_oneshot
echo.
echo  Enter your prompt:
set /p "PROMPT=  > "
if "!PROMPT!"=="" goto :show_menu
"%HERMES_EXE%" -z "!PROMPT!"
echo.
pause
goto :show_menu

:menu_model
cls
echo.
echo ============================================================
echo                     SWITCH  MODEL
echo ============================================================
echo.
echo  [1]  OpenRouter       deepseek-v3:free, gemini-flash:free
echo  [2]  Groq             llama-3.3-70b (fast, free)
echo  [3]  DeepSeek         deepseek-chat, deepseek-reasoner
echo  [4]  xAI Grok         grok-3-mini
echo  [5]  Mistral          mistral-small, mistral-large
echo  [6]  Cerebras         llama-3.3-70b (ultra-fast)
echo  [7]  Ollama Cloud     open models
echo  [8]  OpenCode Zen     gpt-4o, claude, gemini
echo  [9]  Custom           enter manually
echo  [0]  Back
echo.
echo ------------------------------------------------------------
echo.
set /p "CHOICE=  Provider [0-9]: "
if "%CHOICE%"=="0" goto :show_menu
if "%CHOICE%"=="9" goto :model_custom
if "%CHOICE%"=="8" goto :m_opencode
if "%CHOICE%"=="7" goto :m_ollama
if "%CHOICE%"=="6" goto :m_cerebras
if "%CHOICE%"=="5" goto :m_mistral
if "%CHOICE%"=="4" goto :m_xai
if "%CHOICE%"=="3" goto :m_deepseek
if "%CHOICE%"=="2" goto :m_groq
if "%CHOICE%"=="1" goto :m_openrouter
goto :menu_model

:m_openrouter
echo.
echo  OpenRouter Models:
echo  [1]  deepseek/deepseek-r1:free     free, smart
echo  [2]  deepseek/deepseek-v3:free     free, fast
echo  [3]  google/gemini-2.5-flash        free
echo  [4]  anthropic/claude-sonnet-4      paid
echo  [0]  Back
echo.
set /p "CHOICE=  Model [0-4]: "
if "%CHOICE%"=="0" goto :menu_model
if "%CHOICE%"=="4" set "SEL_M=anthropic/claude-sonnet-4" & set "SEL_P=openrouter" & goto :apply_m
if "%CHOICE%"=="3" set "SEL_M=google/gemini-2.5-flash" & set "SEL_P=openrouter" & goto :apply_m
if "%CHOICE%"=="2" set "SEL_M=deepseek/deepseek-v3:free" & set "SEL_P=openrouter" & goto :apply_m
if "%CHOICE%"=="1" set "SEL_M=deepseek/deepseek-r1:free" & set "SEL_P=openrouter" & goto :apply_m
goto :m_openrouter

:m_groq
echo.
echo  Groq Models:
echo  [1]  llama-3.3-70b-versatile  free
echo  [2]  llama-3.1-8b-instant      free, fast
echo  [0]  Back
echo.
set /p "CHOICE=  Model [0-2]: "
if "%CHOICE%"=="0" goto :menu_model
if "%CHOICE%"=="2" set "SEL_M=llama-3.1-8b-instant" & set "SEL_P=groq" & goto :apply_m
if "%CHOICE%"=="1" set "SEL_M=llama-3.3-70b-versatile" & set "SEL_P=groq" & goto :apply_m
goto :m_groq

:m_deepseek
echo.
echo  DeepSeek Models:
echo  [1]  deepseek-chat       fast
echo  [2]  deepseek-reasoner   reasoning (R1)
echo  [0]  Back
echo.
set /p "CHOICE=  Model [0-2]: "
if "%CHOICE%"=="0" goto :menu_model
if "%CHOICE%"=="2" set "SEL_M=deepseek-reasoner" & set "SEL_P=deepseek" & goto :apply_m
if "%CHOICE%"=="1" set "SEL_M=deepseek-chat" & set "SEL_P=deepseek" & goto :apply_m
goto :m_deepseek

:m_xai
set "SEL_M=grok-3-mini"
set "SEL_P=xai"
goto :apply_m

:m_mistral
echo.
echo  Mistral Models:
echo  [1]  mistral-small-latest  fast
echo  [2]  mistral-large-latest  powerful
echo  [0]  Back
echo.
set /p "CHOICE=  Model [0-2]: "
if "%CHOICE%"=="0" goto :menu_model
if "%CHOICE%"=="2" set "SEL_M=mistral-large-latest" & set "SEL_P=mistral" & goto :apply_m
if "%CHOICE%"=="1" set "SEL_M=mistral-small-latest" & set "SEL_P=mistral" & goto :apply_m
goto :m_mistral

:m_cerebras
set "SEL_M=llama-3.3-70b"
set "SEL_P=cerebras"
goto :apply_m

:m_ollama
echo.
echo  Ollama Cloud Models:
echo  [1]  llama3.1:8b    basic
echo  [2]  llama3.3:70b   powerful
echo  [0]  Back
echo.
set /p "CHOICE=  Model [0-2]: "
if "%CHOICE%"=="0" goto :menu_model
if "%CHOICE%"=="2" set "SEL_M=llama3.3:70b" & set "SEL_P=ollama-cloud" & goto :apply_m
if "%CHOICE%"=="1" set "SEL_M=llama3.1:8b" & set "SEL_P=ollama-cloud" & goto :apply_m
goto :m_ollama

:m_opencode
set "SEL_M=gpt-4o"
set "SEL_P=opencode_zen"
goto :apply_m

:model_custom
echo.
echo  Enter model name (e.g. grok-3-mini):
set /p "SEL_M=  > "
if "!SEL_M!"=="" goto :menu_model
echo  Provider (openrouter/groq/deepseek/xai/mistral/cerebras/ollama):
set /p "SEL_P=  > "
if "!SEL_P!"=="" goto :menu_model
goto :apply_m

:apply_m
echo.
echo  Setting: !SEL_M! via !SEL_P!...
"%HERMES_EXE%" config set model.default "!SEL_M!"
"%HERMES_EXE%" config set model.provider "!SEL_P!"
echo.
echo  Done! Model: !SEL_M! (!SEL_P!)
echo.
pause
goto :detect_status

:menu_setup
echo.
"%HERMES_EXE%" setup
goto :detect_status

:menu_gateway
if %GW_RUN%==1 (
    "%HERMES_EXE%" gateway stop
    echo.
    echo  Gateway stopped.
) else (
    echo.
    echo  Starting gateway...
    start "" "%HERMES_EXE%" gateway
    timeout /t 3 /nobreak >nul
)
pause
goto :detect_status

:menu_exit
echo.
echo  Goodbye!
echo.
exit /b

:show_advanced
cls
echo.
echo ============================================================
echo                    ADVANCED  OPTIONS
echo ============================================================
echo.
echo  [1]  Doctor            diagnostics
echo  [2]  Logs              last 20 lines
echo  [3]  Edit Config       open config.yaml
echo  [4]  Edit API Keys     open .env
echo  [5]  Update            update Hermes
echo  [6]  Version           version info
echo  [7]  Open Folder       open data folder
echo  [0]  Back
echo.
echo ------------------------------------------------------------
echo.
set /p "CHOICE=  Select [0-7]: "
if "%CHOICE%"=="0" goto :show_menu
if "%CHOICE%"=="7" goto :adv_folder
if "%CHOICE%"=="6" goto :adv_ver
if "%CHOICE%"=="5" goto :adv_update
if "%CHOICE%"=="4" goto :adv_keys
if "%CHOICE%"=="3" goto :adv_config
if "%CHOICE%"=="2" goto :adv_logs
if "%CHOICE%"=="1" goto :adv_doctor
goto :show_advanced

:adv_doctor
echo.
"%HERMES_EXE%" doctor
echo.
pause
goto :show_advanced

:adv_logs
echo.
if exist "%HERMES_HOME%\logs\gateway.log" (
    echo  --- Gateway Log ---
    powershell -Command "Get-Content '%HERMES_HOME%\logs\gateway.log' -Tail 20"
) else (
    echo  No logs found.
)
echo.
pause
goto :show_advanced

:adv_config
"%HERMES_EXE%" config edit
goto :show_advanced

:adv_keys
start notepad "%HERMES_HOME%\.env"
goto :show_advanced

:adv_update
echo.
"%HERMES_EXE%" update
echo.
pause
goto :show_advanced

:adv_ver
echo.
"%HERMES_EXE%" --version
echo.
pause
goto :show_advanced

:adv_folder
explorer "%HERMES_HOME%"
goto :show_advanced

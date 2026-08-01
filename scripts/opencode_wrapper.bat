@echo off
REM Wrapper to run opencode.exe and output to file
SET OPENCODE_CMD=D:/npm-global/node_modules/opencode-ai/bin/opencode.exe
SET OUTPUT_FILE=%1
SET PROMPT=%2
SET MODEL=%3

%OPENCODE_CMD% run "%~2" --model opencode/%~3 > "%~1" 2>&1
EXIT /B %ERRORLEVEL%
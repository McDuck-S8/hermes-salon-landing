@echo off
REM Hermes Gateway Auto-Start
REM Windows Scheduled Task: schtasks /create /tn "Hermes Gateway" /xml "%~dp0hermes_gateway_task.xml"
REM
REM Creates a scheduled task that starts the Hermes Gateway at user logon
REM and restarts it if it crashes.
REM
REM Requirements: Windows 10+, PowerShell 5+, hermes CLI installed

powershell -NoProfile -ExecutionPolicy Bypass -Command ^
$taskName = 'Hermes Gateway'; ^
$action = New-ScheduledTaskAction -Execute 'cmd.exe' -Argument '/c ""cd /d D:\Portable_Soft\hermes && hermes gateway run --accept-hooks""' -WorkingDirectory 'D:\Portable_Soft\hermes'; ^
$trigger = New-ScheduledTaskTrigger -AtLogOn -User 'Asus'; ^
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -RestartCount 3 -RestartInterval (New-TimeSpan -Minutes 1); ^
$principal = New-ScheduledTaskPrincipal -UserId 'Asus' -LogonType Interactive -RunLevel Highest; ^
Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings -Principal $principal -Force; ^
if ($?) { echo 'Scheduled task created: Hermes Gateway' } else { echo 'FAILED'; exit 1 }

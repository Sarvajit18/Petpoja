@echo off
setlocal

TITLE Petpooja POS Desktop Software
cd /d "%~dp0"

echo Starting Petpooja POS Server...

:: Start server in background if not running
powershell -Command "if (!(Test-NetConnection -ComputerName 127.0.0.1 -Port 8000 -InformationLevel Quiet -WarningAction SilentlyContinue)) { Start-Process python -ArgumentList 'server.py' -WindowStyle Hidden; Start-Sleep -Seconds 2 }"

:: Detect Edge or Chrome for Desktop App Window Mode
set "EDGE_EXE=C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
set "CHROME_EXE=C:\Program Files\Google\Chrome\Application\chrome.exe"

if exist "%EDGE_EXE%" (
    start "" "%EDGE_EXE%" --app="http://localhost:8000" --window-size=1280,850
    goto done
)

if exist "%CHROME_EXE%" (
    start "" "%CHROME_EXE%" --app="http://localhost:8000" --window-size=1280,850
    goto done
)

:: Fallback if neither found
start "" "http://localhost:8000"

:done
exit

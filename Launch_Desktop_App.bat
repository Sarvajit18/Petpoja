@echo off
setlocal

TITLE Shansara POS Desktop
cd /d "%~dp0"

if exist "dist\Shansara_POS\Shansara_POS.exe" (
    start "" "dist\Shansara_POS\Shansara_POS.exe"
) else (
    echo Starting Shansara POS Server via Python...
    start /B python server.py >nul 2>&1
    timeout /t 2 /nobreak >nul
    start "" "http://localhost:8000"
)

endlocal

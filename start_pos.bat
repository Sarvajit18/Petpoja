@echo off
TITLE Petpooja POS - Restaurant Billing Server
color 0A

echo =====================================================================
echo           PETPOOJA-STYLE RESTAURANT POS & CAPTAIN APP
echo =====================================================================
echo Starting Main Billing Station & Ethernet/LAN Server...
echo.

python -m pip install fastapi uvicorn[standard] python-multipart --quiet

echo.
echo Launching Server...
start "" "http://localhost:8000"
python server.py

pause

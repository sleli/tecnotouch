@echo off
echo ==========================================
echo Switch to SIMULATION Mode
echo ==========================================
echo.
echo Questo script:
echo  - Modifica .env: DISTRIBUTOR_IP=localhost
echo  - Avvia simulatore
echo  - Riavvia servizi
echo.
pause

PowerShell -NoProfile -ExecutionPolicy Bypass -File "%~dp0switch-to-simulation.ps1"

pause

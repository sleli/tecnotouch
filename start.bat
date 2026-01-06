@echo off
echo ==========================================
echo Dashboard Distributore - Avvio Servizi
echo ==========================================
echo.
echo Leggendo configurazione da .env...
echo.
PowerShell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\start-services.ps1"
echo.
echo Per cambiare modalita:
echo   - Simulazione: scripts\switch-to-simulation.bat
echo   - Produzione:  scripts\switch-to-production.bat
echo.
pause

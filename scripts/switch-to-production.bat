@echo off
echo ==========================================
echo Switch to PRODUCTION Mode
echo ==========================================
echo.
echo Questo script:
echo  - Ripristina .env con IP distributore reale
echo  - Ferma simulatore
echo  - Riavvia servizi produzione
echo.
pause

PowerShell -NoProfile -ExecutionPolicy Bypass -File "%~dp0switch-to-production.ps1"

pause

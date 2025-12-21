@echo off
echo ==========================================
echo Installazione Dashboard Distributore
echo ==========================================
echo.
echo ATTENZIONE: Richiede diritti amministratore
echo.
pause

PowerShell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\install-services.ps1"

pause

@echo off
echo ==========================================
echo Disinstallazione Servizi Dashboard
echo ==========================================
echo.
echo ATTENZIONE: Richiede diritti amministratore
echo.
pause

PowerShell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\uninstall-services.ps1"

pause

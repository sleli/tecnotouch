@echo off
REM Dashboard Distributore - Avvio Sistema
REM Equivalente di start.sh per Windows
PowerShell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\start.ps1" %*

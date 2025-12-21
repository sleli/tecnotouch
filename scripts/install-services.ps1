# Installazione automatica servizi Windows per Dashboard Distributore
# Richiede diritti amministratore

#Requires -RunAsAdministrator

param(
    [string]$ProjectPath = "C:\tecnotouch",
    [string]$DistributoreIP = "",
    [switch]$IncludeSimulator
)

$ErrorActionPreference = "Stop"

# Load .env file if exists
$envFile = Join-Path $ProjectPath ".env"
if (Test-Path $envFile) {
    Get-Content $envFile | ForEach-Object {
        if ($_ -match '^([^#][^=]+)=(.*)$') {
            $name = $matches[1].Trim()
            $value = $matches[2].Trim()
            [Environment]::SetEnvironmentVariable($name, $value, 'Process')
        }
    }
    Write-Host "Environment variables loaded from .env" -ForegroundColor Green
}

# Set DistributoreIP from env var if not provided as parameter
if ([string]::IsNullOrEmpty($DistributoreIP)) {
    if ($env:DISTRIBUTOR_IP) {
        $DistributoreIP = $env:DISTRIBUTOR_IP
    } else {
        Write-Error "DISTRIBUTOR_IP not set. Please set it in .env file or pass via -DistributoreIP parameter"
        exit 1
    }
}

Write-Host "===========================================`n" -ForegroundColor Cyan
Write-Host "Installazione Servizi Dashboard Distributore" -ForegroundColor Cyan
Write-Host "===========================================`n" -ForegroundColor Cyan

# 1. Verifica NSSM installato
$nssmPath = "C:\nssm\nssm.exe"
if (-not (Test-Path $nssmPath)) {
    Write-Host "NSSM non trovato. Download in corso..." -ForegroundColor Yellow
    $nssmZip = "$env:TEMP\nssm.zip"
    Invoke-WebRequest -Uri "https://nssm.cc/release/nssm-2.24.zip" -OutFile $nssmZip
    Expand-Archive -Path $nssmZip -DestinationPath "C:\" -Force

    # Crea directory se non esiste
    if (-not (Test-Path "C:\nssm")) {
        New-Item -ItemType Directory -Path "C:\nssm" | Out-Null
    }

    Move-Item "C:\nssm-2.24\win64\nssm.exe" "C:\nssm\" -Force
    Remove-Item "C:\nssm-2.24" -Recurse -Force -ErrorAction SilentlyContinue
    Write-Host "NSSM installato in C:\nssm\" -ForegroundColor Green
}

# 2. Trova Python
$pythonPath = $null
try {
    $pythonPath = (Get-Command python).Source
} catch {
    Write-Error "Python non trovato nel PATH. Installare Python 3.11+ da python.org"
    Write-Host "`nDurante l'installazione assicurarsi di selezionare:" -ForegroundColor Yellow
    Write-Host "  [X] Add Python to PATH" -ForegroundColor Yellow
    exit 1
}
Write-Host "Python trovato: $pythonPath" -ForegroundColor Green

# 3. Installa dipendenze Python
Write-Host "`nInstallazione dipendenze Python..." -ForegroundColor Yellow
Set-Location "$ProjectPath\backend"
& $pythonPath -m pip install --upgrade pip --quiet
& $pythonPath -m pip install -r requirements.txt --quiet

if ($IncludeSimulator) {
    Set-Location "$ProjectPath\simulator"
    & $pythonPath -m pip install -r requirements.txt --quiet
}
Write-Host "Dipendenze installate" -ForegroundColor Green

# 4. Crea directory logs
$logsPath = "$ProjectPath\logs"
if (-not (Test-Path $logsPath)) {
    New-Item -ItemType Directory -Path $logsPath | Out-Null
}

# 5. Installa servizio Backend API
Write-Host "`nInstallazione servizio Backend API..." -ForegroundColor Yellow
$serviceName = "VendingBackendAPI"

# Rimuovi servizio esistente se presente
& $nssmPath stop $serviceName 2>$null
& $nssmPath remove $serviceName confirm 2>$null

# Installa nuovo servizio
& $nssmPath install $serviceName $pythonPath "$ProjectPath\backend\api_server.py" "--ip" $DistributoreIP "--port" "8000" "--host" "0.0.0.0"

# Configurazione servizio
& $nssmPath set $serviceName AppDirectory "$ProjectPath\backend"
& $nssmPath set $serviceName DisplayName "Distributore - Backend API"
& $nssmPath set $serviceName Description "Flask API server per dashboard distributore sigarette"
& $nssmPath set $serviceName Start SERVICE_AUTO_START
& $nssmPath set $serviceName AppStdout "$logsPath\backend-stdout.log"
& $nssmPath set $serviceName AppStderr "$logsPath\backend-stderr.log"
& $nssmPath set $serviceName AppRotateFiles 1
& $nssmPath set $serviceName AppRotateBytes 1048576  # 1MB

Write-Host "Servizio Backend API installato" -ForegroundColor Green

# 6. Installa servizio Frontend
Write-Host "`nInstallazione servizio Frontend..." -ForegroundColor Yellow
$serviceName = "VendingFrontend"

& $nssmPath stop $serviceName 2>$null
& $nssmPath remove $serviceName confirm 2>$null

& $nssmPath install $serviceName $pythonPath "-m" "http.server" "3000" "--bind" "0.0.0.0"

& $nssmPath set $serviceName AppDirectory "$ProjectPath\frontend-vue\dist"
& $nssmPath set $serviceName DisplayName "Distributore - Frontend"
& $nssmPath set $serviceName Description "HTTP server per dashboard Vue.js"
& $nssmPath set $serviceName Start SERVICE_AUTO_START
& $nssmPath set $serviceName AppStdout "$logsPath\frontend-stdout.log"
& $nssmPath set $serviceName AppStderr "$logsPath\frontend-stderr.log"
& $nssmPath set $serviceName AppRotateFiles 1
& $nssmPath set $serviceName AppRotateBytes 1048576  # 1MB

Write-Host "Servizio Frontend installato" -ForegroundColor Green

# 7. (Opzionale) Installa servizio Simulator
if ($IncludeSimulator) {
    Write-Host "`nInstallazione servizio Simulator..." -ForegroundColor Yellow
    $serviceName = "VendingSimulator"

    & $nssmPath stop $serviceName 2>$null
    & $nssmPath remove $serviceName confirm 2>$null

    & $nssmPath install $serviceName $pythonPath "$ProjectPath\simulator\vending_machine_simulator.py"

    & $nssmPath set $serviceName AppDirectory "$ProjectPath\simulator"
    & $nssmPath set $serviceName DisplayName "Distributore - Simulator"
    & $nssmPath set $serviceName Description "Simulatore distributore per testing"
    & $nssmPath set $serviceName Start SERVICE_DEMAND_START  # Manuale
    & $nssmPath set $serviceName AppStdout "$logsPath\simulator-stdout.log"
    & $nssmPath set $serviceName AppStderr "$logsPath\simulator-stderr.log"
    & $nssmPath set $serviceName AppRotateFiles 1
    & $nssmPath set $serviceName AppRotateBytes 1048576

    Write-Host "Servizio Simulator installato (avvio manuale)" -ForegroundColor Green
}

# 8. Configura firewall Windows
Write-Host "`nConfigurazione firewall Windows..." -ForegroundColor Yellow

# Regola per Frontend (porta 3000)
$ruleName = "Vending Dashboard - Frontend"
if (Get-NetFirewallRule -DisplayName $ruleName -ErrorAction SilentlyContinue) {
    Remove-NetFirewallRule -DisplayName $ruleName
}
New-NetFirewallRule -DisplayName $ruleName `
    -Direction Inbound `
    -Protocol TCP `
    -LocalPort 3000 `
    -Action Allow `
    -Profile Any | Out-Null

# Regola per Backend API (porta 8000)
$ruleName = "Vending Dashboard - Backend API"
if (Get-NetFirewallRule -DisplayName $ruleName -ErrorAction SilentlyContinue) {
    Remove-NetFirewallRule -DisplayName $ruleName
}
New-NetFirewallRule -DisplayName $ruleName `
    -Direction Inbound `
    -Protocol TCP `
    -LocalPort 8000 `
    -Action Allow `
    -Profile Any | Out-Null

Write-Host "Regole firewall create" -ForegroundColor Green

# 9. Avvia servizi
Write-Host "`nAvvio servizi..." -ForegroundColor Yellow
Start-Service VendingBackendAPI
Start-Service VendingFrontend

Write-Host "`n===========================================`n" -ForegroundColor Green
Write-Host "Installazione completata!" -ForegroundColor Green
Write-Host "===========================================`n" -ForegroundColor Green
Write-Host "Servizi installati e avviati:`n"
Write-Host "  - VendingBackendAPI  (http://localhost:8000)"
Write-Host "  - VendingFrontend    (http://localhost:3000)"
if ($IncludeSimulator) {
    Write-Host "  - VendingSimulator   (http://localhost:1500) [NON AVVIATO]"
}
Write-Host "`nLog disponibili in: $logsPath"
Write-Host "`nPer gestire i servizi:"
Write-Host "  - Gestione Computer > Servizi"
Write-Host "  - PowerShell: Get-Service Vending*"
Write-Host "`nDashboard: http://localhost:3000`n"

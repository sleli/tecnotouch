# Switch to Simulation Mode
# Modifica .env per usare localhost e avvia simulatore

$ErrorActionPreference = "Stop"

$ProjectPath = Split-Path -Parent $PSScriptRoot
$EnvFile = Join-Path $ProjectPath ".env"
$EnvBackup = Join-Path $ProjectPath ".env.backup"

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Switch to SIMULATION Mode" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Verifica che .env esista
if (-not (Test-Path $EnvFile)) {
    Write-Error "File .env non trovato. Copiare .env.example in .env prima di procedere."
    exit 1
}

# Backup del .env corrente
Write-Host "Backup .env corrente..." -ForegroundColor Yellow
Copy-Item $EnvFile $EnvBackup -Force
Write-Host "Backup salvato in .env.backup" -ForegroundColor Green

# Modifica DISTRIBUTOR_IP in .env
Write-Host "`nModifica .env -> DISTRIBUTOR_IP=localhost..." -ForegroundColor Yellow
$envContent = Get-Content $EnvFile
$newContent = $envContent | ForEach-Object {
    if ($_ -match '^DISTRIBUTOR_IP=') {
        "DISTRIBUTOR_IP=localhost"
    } else {
        $_
    }
}
$newContent | Set-Content $EnvFile
Write-Host "DISTRIBUTOR_IP impostato a localhost" -ForegroundColor Green

# Ferma servizi in esecuzione
Write-Host "`nArresto servizi..." -ForegroundColor Yellow
Stop-Service VendingBackendAPI, VendingFrontend -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2
Write-Host "Servizi fermati" -ForegroundColor Green

# Avvia servizio simulatore
Write-Host "`nAvvio simulatore..." -ForegroundColor Yellow
try {
    Start-Service VendingSimulator
    Start-Sleep -Seconds 3
    $simStatus = Get-Service VendingSimulator
    if ($simStatus.Status -eq 'Running') {
        Write-Host "Simulatore avviato (http://localhost:1500)" -ForegroundColor Green
    } else {
        Write-Warning "Simulatore non in esecuzione. Verificare log."
    }
} catch {
    Write-Warning "Errore avvio simulatore: $_"
}

# Riavvia servizi (leggono nuovo IP da .env)
Write-Host "`nRiavvio servizi..." -ForegroundColor Yellow
Start-Service VendingBackendAPI, VendingFrontend
Start-Sleep -Seconds 3

# Verifica status
Write-Host "`nStatus servizi:" -ForegroundColor Cyan
Get-Service Vending* | Format-Table Name, Status, DisplayName -AutoSize

Write-Host "`n========================================" -ForegroundColor Green
Write-Host "Modalità SIMULAZIONE attiva" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host "`nDashboard: http://localhost:3000" -ForegroundColor White
Write-Host "Simulatore: http://localhost:1500" -ForegroundColor White
Write-Host "`nPer tornare a modalità PRODUZIONE:" -ForegroundColor Yellow
Write-Host "  switch-to-production.bat`n" -ForegroundColor Yellow

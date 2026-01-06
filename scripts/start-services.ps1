# Avvio rapido servizi (non richiede admin se già installati)

$ProjectPath = Split-Path -Parent $PSScriptRoot
$EnvFile = Join-Path $ProjectPath ".env"

Write-Host "Avvio servizi Dashboard...`n" -ForegroundColor Cyan

# Leggi configurazione da .env
if (Test-Path $EnvFile) {
    $distributorIP = (Get-Content $EnvFile | Where-Object { $_ -match '^DISTRIBUTOR_IP=' }) -replace 'DISTRIBUTOR_IP=', ''

    if ($distributorIP -match 'localhost|127\.0\.0\.1') {
        Write-Host "Modalità: SIMULAZIONE ($distributorIP)" -ForegroundColor Yellow
        Write-Host "Nota: Verificare che il simulatore sia avviato (VendingSimulator)`n" -ForegroundColor Yellow
    } else {
        Write-Host "Modalità: PRODUZIONE ($distributorIP)" -ForegroundColor Green
    }
} else {
    Write-Host "File .env non trovato - usando configurazione default`n" -ForegroundColor Yellow
}

Start-Service VendingBackendAPI
Start-Service VendingFrontend

Start-Sleep -Seconds 2

# Verifica status
Get-Service Vending* | Format-Table -AutoSize

Write-Host "`nDashboard disponibile: http://localhost:3000" -ForegroundColor Green
Write-Host "API Server: http://localhost:8000`n" -ForegroundColor Green

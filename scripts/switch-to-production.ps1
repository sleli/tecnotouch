# Switch to Production Mode
# Ripristina .env originale e ferma simulatore

$ErrorActionPreference = "Stop"

$ProjectPath = Split-Path -Parent $PSScriptRoot
$EnvFile = Join-Path $ProjectPath ".env"
$EnvBackup = Join-Path $ProjectPath ".env.backup"
$EnvExample = Join-Path $ProjectPath ".env.example"

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Switch to PRODUCTION Mode" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Verifica che .env esista
if (-not (Test-Path $EnvFile)) {
    Write-Error "File .env non trovato. Copiare .env.example in .env prima di procedere."
    exit 1
}

# Ripristina da backup se esiste
if (Test-Path $EnvBackup) {
    Write-Host "Ripristino .env da backup..." -ForegroundColor Yellow
    Copy-Item $EnvBackup $EnvFile -Force
    Write-Host ".env ripristinato" -ForegroundColor Green
} else {
    # Se non c'è backup, chiedi IP distributore
    Write-Host "Backup .env non trovato. Inserire IP distributore:" -ForegroundColor Yellow
    $distributorIP = Read-Host "IP distributore (es. 192.168.1.65)"

    if ([string]::IsNullOrWhiteSpace($distributorIP)) {
        Write-Error "IP distributore non valido"
        exit 1
    }

    # Modifica .env con nuovo IP
    $envContent = Get-Content $EnvFile
    $newContent = $envContent | ForEach-Object {
        if ($_ -match '^DISTRIBUTOR_IP=') {
            "DISTRIBUTOR_IP=$distributorIP"
        } else {
            $_
        }
    }
    $newContent | Set-Content $EnvFile
    Write-Host "DISTRIBUTOR_IP impostato a $distributorIP" -ForegroundColor Green
}

# Leggi IP configurato
$distributorIP = (Get-Content $EnvFile | Where-Object { $_ -match '^DISTRIBUTOR_IP=' }) -replace 'DISTRIBUTOR_IP=', ''
Write-Host "`nModalità PRODUZIONE: $distributorIP" -ForegroundColor Cyan

# Ferma tutti i servizi
Write-Host "`nArresto servizi..." -ForegroundColor Yellow
Stop-Service VendingSimulator, VendingBackendAPI, VendingFrontend -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2
Write-Host "Servizi fermati" -ForegroundColor Green

# Riavvia solo servizi produzione (no simulatore)
Write-Host "`nAvvio servizi produzione..." -ForegroundColor Yellow
Start-Service VendingBackendAPI, VendingFrontend
Start-Sleep -Seconds 3

# Verifica status
Write-Host "`nStatus servizi:" -ForegroundColor Cyan
Get-Service Vending* | Format-Table Name, Status, DisplayName -AutoSize

Write-Host "`n========================================" -ForegroundColor Green
Write-Host "Modalità PRODUZIONE attiva" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host "`nDistributore: $distributorIP" -ForegroundColor White
Write-Host "Dashboard: http://localhost:3000" -ForegroundColor White
Write-Host "`nPer passare a modalità SIMULAZIONE:" -ForegroundColor Yellow
Write-Host "  switch-to-simulation.bat`n" -ForegroundColor Yellow

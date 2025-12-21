# Avvio rapido servizi (non richiede admin se già installati)

Write-Host "Avvio servizi Dashboard...`n" -ForegroundColor Cyan

Start-Service VendingBackendAPI
Start-Service VendingFrontend

Start-Sleep -Seconds 2

# Verifica status
Get-Service Vending* | Format-Table -AutoSize

Write-Host "`nDashboard disponibile: http://localhost:3000`n" -ForegroundColor Green

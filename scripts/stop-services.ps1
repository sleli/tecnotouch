# Stop rapido servizi

Write-Host "Stop servizi Dashboard...`n" -ForegroundColor Yellow

Stop-Service VendingBackendAPI -ErrorAction SilentlyContinue
Stop-Service VendingFrontend -ErrorAction SilentlyContinue
Stop-Service VendingSimulator -ErrorAction SilentlyContinue

Get-Service Vending* | Format-Table -AutoSize

Write-Host "`nServizi fermati`n" -ForegroundColor Green

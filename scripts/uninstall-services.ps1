# Disinstallazione servizi Windows

#Requires -RunAsAdministrator

$nssmPath = "C:\nssm\nssm.exe"

Write-Host "Rimozione servizi Dashboard Distributore...`n" -ForegroundColor Yellow

# Stop e rimozione servizi
$services = @("VendingBackendAPI", "VendingFrontend", "VendingSimulator")

foreach ($service in $services) {
    Write-Host "Rimozione $service..." -ForegroundColor Yellow
    & $nssmPath stop $service 2>$null
    & $nssmPath remove $service confirm 2>$null
}

# Rimozione regole firewall
$rules = @("Vending Dashboard - Frontend", "Vending Dashboard - Backend API")
foreach ($rule in $rules) {
    Remove-NetFirewallRule -DisplayName $rule -ErrorAction SilentlyContinue
}

Write-Host "`nServizi rimossi con successo`n" -ForegroundColor Green

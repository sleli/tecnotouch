# Backup automatico database (da eseguire via Task Scheduler)

param(
    [string]$BackupPath = "C:\VendingBackups",
    [int]$RetentionDays = 30
)

$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$backupDir = Join-Path $BackupPath $timestamp
New-Item -ItemType Directory -Path $backupDir -Force | Out-Null

# Percorso database
$dbPath = "C:\tecnotouch\backend\sales_data.db"

if (Test-Path $dbPath) {
    Copy-Item $dbPath -Destination (Join-Path $backupDir "sales_data.db")
    Write-Host "Database backed up to: $backupDir"

    # Cleanup vecchi backup
    $cutoffDate = (Get-Date).AddDays(-$RetentionDays)
    Get-ChildItem $BackupPath -Directory |
        Where-Object { $_.CreationTime -lt $cutoffDate } |
        Remove-Item -Recurse -Force

    Write-Host "Old backups cleaned up (retention: $RetentionDays days)"
} else {
    Write-Error "Database not found at: $dbPath"
    exit 1
}

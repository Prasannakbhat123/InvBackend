# Script to remove Supabase hostname from Windows hosts file
# Requires Administrator privileges

param(
    [string]$Hostname = "db.szbyermnxegholjfkmij.supabase.co"
)

# Check if running as Administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "ERROR: This script must be run as Administrator!" -ForegroundColor Red
    Write-Host "Right-click PowerShell and select 'Run as Administrator', then run this script again." -ForegroundColor Yellow
    exit 1
}

$hostsPath = "$env:SystemRoot\System32\drivers\etc\hosts"

# Check if entry exists
$hostsContent = Get-Content $hostsPath -Raw
if ($hostsContent -notmatch [regex]::Escape($Hostname)) {
    Write-Host "Entry for $Hostname does not exist in hosts file." -ForegroundColor Yellow
    exit 0
}

Write-Host "Found entry for $Hostname in hosts file:" -ForegroundColor Yellow
Get-Content $hostsPath | Select-String $Hostname | ForEach-Object { Write-Host "  $_" -ForegroundColor Cyan }

# Remove entry
$hostsContent = $hostsContent -replace "(?m)^.*$([regex]::Escape($Hostname)).*$\r?\n?", ""
Set-Content -Path $hostsPath -Value $hostsContent.TrimEnd() -NoNewline
Write-Host "`nSuccessfully removed entry from hosts file!" -ForegroundColor Green

# Flush DNS cache
Write-Host "`nFlushing DNS cache..." -ForegroundColor Yellow
ipconfig /flushdns | Out-Null
Write-Host "DNS cache flushed successfully!" -ForegroundColor Green

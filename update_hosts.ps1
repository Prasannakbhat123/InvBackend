# Script to add Supabase hostname to Windows hosts file
# Requires Administrator privileges

param(
    [string]$Hostname = "db.szbyermnxegholjfkmij.supabase.co",
    [string]$IpAddress = "2406:da1a:6b0:f603:c481:8849:a49d:a78f"
)

# Check if running as Administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "ERROR: This script must be run as Administrator!" -ForegroundColor Red
    Write-Host "Right-click PowerShell and select 'Run as Administrator', then run this script again." -ForegroundColor Yellow
    exit 1
}

$hostsPath = "$env:SystemRoot\System32\drivers\etc\hosts"
$hostsEntry = "$IpAddress`t$Hostname"

# Check if entry already exists
$hostsContent = Get-Content $hostsPath -Raw
if ($hostsContent -match [regex]::Escape($Hostname)) {
    Write-Host "Entry for $Hostname already exists in hosts file." -ForegroundColor Yellow
    Write-Host "Current entry:" -ForegroundColor Cyan
    Get-Content $hostsPath | Select-String $Hostname | ForEach-Object { Write-Host "  $_" }
    
    $response = Read-Host "Do you want to update it? (y/n)"
    if ($response -ne 'y') {
        Write-Host "No changes made." -ForegroundColor Green
        exit 0
    }
    
    # Remove old entry
    $hostsContent = $hostsContent -replace "(?m)^.*$([regex]::Escape($Hostname)).*$\r?\n?", ""
    Set-Content -Path $hostsPath -Value $hostsContent.TrimEnd() -NoNewline
    Write-Host "Removed old entry." -ForegroundColor Green
}

# Add new entry
Add-Content -Path $hostsPath -Value "`n$hostsEntry"
Write-Host "Successfully added entry to hosts file:" -ForegroundColor Green
Write-Host "  $hostsEntry" -ForegroundColor Cyan

# Flush DNS cache
Write-Host "`nFlushing DNS cache..." -ForegroundColor Yellow
ipconfig /flushdns | Out-Null
Write-Host "DNS cache flushed successfully!" -ForegroundColor Green

Write-Host "`nYou can now use the hostname in your connection string:" -ForegroundColor Green
Write-Host "  $Hostname" -ForegroundColor Cyan

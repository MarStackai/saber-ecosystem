#!/usr/bin/pwsh
<#
.SYNOPSIS
    Deploys fixed form files to SharePoint to resolve redirect issues
#>

param(
    [string]$SiteUrl = "https://saberrenewables.sharepoint.com/sites/SaberEPCPartners",
    [string]$ClientId = "bbbfe394-7cff-4ac9-9e01-33cbf116b930",
    [string]$Tenant = "saberrenewables.onmicrosoft.com"
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Deploying Fixed Form Files" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Connect to SharePoint
Write-Host "`nConnecting to SharePoint..." -ForegroundColor Yellow
Connect-PnPOnline -Url $SiteUrl -ClientId $ClientId -Tenant $Tenant -DeviceLogin

try {
    $folderUrl = "SiteAssets/EPCForm"
    $formPath = "/home/marstack/saber_business_ops/epc-form"
    
    Write-Host "`nUploading fixed files..." -ForegroundColor Green
    
    # Upload the fixed files
    $files = @(
        @{Name="index.html"; Path="$formPath/index.html"},
        @{Name="verify-access.html"; Path="$formPath/verify-access.html"},
        @{Name="script-fixed.js"; Path="$formPath/script-fixed.js"},
        @{Name="script.js"; Path="$formPath/script-fixed.js"}  # Also replace original script.js
    )
    
    foreach ($file in $files) {
        Write-Host "Uploading: $($file.Name)" -ForegroundColor White -NoNewline
        
        try {
            Add-PnPFile -Path $file.Path -Folder $folderUrl -NewFileName $file.Name
            Write-Host " ✓" -ForegroundColor Green
        } catch {
            Write-Host " ✗ Error: $_" -ForegroundColor Red
        }
    }
    
    Write-Host "`n========================================" -ForegroundColor Cyan
    Write-Host "✅ Deployment Complete!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Cyan
    
    Write-Host "`nFixed URLs:" -ForegroundColor Yellow
    Write-Host "Form Entry:  $SiteUrl/SiteAssets/EPCForm/verify-access.html" -ForegroundColor White
    Write-Host "Main Form:   $SiteUrl/SiteAssets/EPCForm/index.html" -ForegroundColor White
    
    Write-Host "`nThe form will now:" -ForegroundColor Green
    Write-Host "✓ Stay on SharePoint when submitted" -ForegroundColor Gray
    Write-Host "✓ Require authentication to access main form" -ForegroundColor Gray
    Write-Host "✓ Show success message without redirecting to local files" -ForegroundColor Gray
    Write-Host "✓ Clear session after successful submission" -ForegroundColor Gray
    
} catch {
    Write-Host "`n❌ Error: $_" -ForegroundColor Red
} finally {
    Disconnect-PnPOnline
}

Write-Host "`n========================================" -ForegroundColor Cyan
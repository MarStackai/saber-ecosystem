#!/usr/bin/pwsh
<#
.SYNOPSIS
    Tests SharePoint page access and creates working solution
#>

param(
    [string]$SiteUrl = "https://saberrenewables.sharepoint.com/sites/SaberEPCPartners",
    [string]$ClientId = "bbbfe394-7cff-4ac9-9e01-33cbf116b930",
    [string]$Tenant = "saberrenewables.onmicrosoft.com"
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Testing SharePoint Access" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Connect to SharePoint
Write-Host "`nConnecting to SharePoint..." -ForegroundColor Yellow
Connect-PnPOnline -Url $SiteUrl -ClientId $ClientId -Tenant $Tenant -DeviceLogin

try {
    # List all files
    Write-Host "`nFiles in EPCForm folder:" -ForegroundColor Yellow
    Get-PnPFolderItem -FolderSiteRelativeUrl "SiteAssets/EPCForm" | Format-Table Name, ServerRelativeUrl -AutoSize
    
    # Get the actual URLs for testing
    Write-Host "`nDirect URLs to test:" -ForegroundColor Green
    Write-Host "1. HTML Branded: $SiteUrl/SiteAssets/EPCForm/verify-access-branded.html" -ForegroundColor White
    Write-Host "2. ASPX Version: $SiteUrl/SiteAssets/EPCForm/verify.aspx" -ForegroundColor White
    Write-Host "3. Original HTML: $SiteUrl/SiteAssets/EPCForm/verify-access.html" -ForegroundColor White
    
    # Create a working SharePoint page using Content Editor approach
    Write-Host "`nCreating SharePoint-compatible wrapper page..." -ForegroundColor Yellow
    
    $wrapperHTML = @"
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>EPC Partner Portal - Saber Renewables</title>
    <script>
        // Redirect to the branded page
        window.location.replace('$SiteUrl/SiteAssets/EPCForm/verify-access-branded.html');
    </script>
</head>
<body>
    <p>Redirecting to EPC Partner Portal...</p>
    <p>If not redirected, <a href="$SiteUrl/SiteAssets/EPCForm/verify-access-branded.html">click here</a></p>
</body>
</html>
"@
    
    # Upload wrapper
    $tempWrapper = [System.IO.Path]::GetTempFileName() + ".html"
    $wrapperHTML | Out-File -FilePath $tempWrapper -Encoding UTF8
    
    Write-Host "Uploading wrapper page..." -ForegroundColor White
    Add-PnPFile -Path $tempWrapper -Folder "SiteAssets/EPCForm" -NewFileName "epc-portal-wrapper.html"
    Remove-Item $tempWrapper
    
    # Also check if we can use Script Editor Web Part
    Write-Host "`nChecking site features..." -ForegroundColor Yellow
    $web = Get-PnPWeb
    Write-Host "Site Title: $($web.Title)" -ForegroundColor White
    Write-Host "Site Template: $($web.WebTemplate)" -ForegroundColor White
    
    Write-Host "`n========================================" -ForegroundColor Cyan
    Write-Host "✅ Testing Complete!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Cyan
    
    Write-Host "`nRecommended approach:" -ForegroundColor Yellow
    Write-Host "The branded HTML version should work best:" -ForegroundColor White
    Write-Host "$SiteUrl/SiteAssets/EPCForm/verify-access-branded.html" -ForegroundColor Cyan
    
    Write-Host "`nAlternative wrapper page:" -ForegroundColor Yellow
    Write-Host "$SiteUrl/SiteAssets/EPCForm/epc-portal-wrapper.html" -ForegroundColor Cyan
    
    Write-Host "`nNote: ASPX files may need different permissions or SharePoint Designer to work properly." -ForegroundColor Gray
    
} catch {
    Write-Host "`n❌ Error: $_" -ForegroundColor Red
} finally {
    Disconnect-PnPOnline
}

Write-Host "`n========================================" -ForegroundColor Cyan
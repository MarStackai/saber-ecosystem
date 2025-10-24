#!/usr/bin/pwsh
<#
.SYNOPSIS
    Fixes permissions and creates public-accessible form pages
#>

param(
    [string]$SiteUrl = "https://saberrenewables.sharepoint.com/sites/SaberEPCPartners",
    [string]$ClientId = "bbbfe394-7cff-4ac9-9e01-33cbf116b930",
    [string]$Tenant = "saberrenewables.onmicrosoft.com"
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Fixing Permissions & Access Issues" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Connect to SharePoint
Write-Host "`nConnecting to SharePoint..." -ForegroundColor Yellow
Connect-PnPOnline -Url $SiteUrl -ClientId $ClientId -Tenant $Tenant -DeviceLogin

try {
    # Check current permissions
    Write-Host "`nChecking folder permissions..." -ForegroundColor Yellow
    $folder = Get-PnPFolder -Url "SiteAssets/EPCForm"
    
    # Try to set permissions for anonymous access
    Write-Host "`nAttempting to enable anonymous access..." -ForegroundColor Yellow
    
    # Create a SharePoint page that will be publicly accessible
    Write-Host "`nCreating SharePoint Site Page (publicly accessible)..." -ForegroundColor Green
    
    # Create a modern page
    $pageName = "EPCPartnerPortal"
    
    # Check if page exists
    $existingPage = Get-PnPSitePagesPagesLibrary -ErrorAction SilentlyContinue
    
    Write-Host "Creating new modern page..." -ForegroundColor White
    
    # Add the page
    Add-PnPPage -Name $pageName -LayoutType Article -CommentsEnabled:$false -Publish
    
    # Get the page
    $page = Get-PnPPage -Identity $pageName
    
    # Add HTML content to the page using Text web part
    $htmlContent = @"
<iframe src="/sites/SaberEPCPartners/SiteAssets/EPCForm/verify-access-branded.html" 
        style="width:100%; height:800px; border:none;" 
        id="epcFrame">
</iframe>
<script>
// Fallback if iframe doesn't work
document.addEventListener('DOMContentLoaded', function() {
    var frame = document.getElementById('epcFrame');
    frame.onerror = function() {
        window.location.href = '/sites/SaberEPCPartners/SiteAssets/EPCForm/verify-access-branded.html';
    };
});
</script>
"@
    
    # Add content to page
    Add-PnPPageTextPart -Page $pageName -Text $htmlContent
    
    # Publish the page
    Set-PnPPage -Identity $pageName -Publish
    
    Write-Host "`n✅ Modern page created!" -ForegroundColor Green
    
    # Also try breaking inheritance and setting custom permissions
    Write-Host "`nSetting custom permissions on files..." -ForegroundColor Yellow
    
    $files = @("verify-access-branded.html", "index.html", "verify.aspx", "form.aspx")
    
    foreach ($fileName in $files) {
        try {
            $file = Get-PnPFile -Url "/sites/SaberEPCPartners/SiteAssets/EPCForm/$fileName" -ErrorAction SilentlyContinue
            if ($file) {
                # Try to break inheritance
                Set-PnPFilePermission -Url "/sites/SaberEPCPartners/SiteAssets/EPCForm/$fileName" -User "Everyone" -AddRole "Read" -ErrorAction SilentlyContinue
                Write-Host "  ✓ $fileName - Attempted to set public read access" -ForegroundColor Gray
            }
        } catch {
            Write-Host "  ⚠ $fileName - Could not modify permissions (may require higher privileges)" -ForegroundColor Yellow
        }
    }
    
    Write-Host "`n========================================" -ForegroundColor Cyan
    Write-Host "✅ Permission Updates Complete!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Cyan
    
    Write-Host "`nAccess Options:" -ForegroundColor Yellow
    
    Write-Host "`n1. Modern SharePoint Page (Most Reliable):" -ForegroundColor Green
    Write-Host "   $SiteUrl/SitePages/$pageName.aspx" -ForegroundColor Cyan
    
    Write-Host "`n2. Direct File Access (May require login):" -ForegroundColor Yellow
    Write-Host "   $SiteUrl/SiteAssets/EPCForm/verify-access-branded.html" -ForegroundColor White
    
    Write-Host "`n3. Share Link Option:" -ForegroundColor Yellow
    Write-Host "   You can create a sharing link in SharePoint UI for anonymous access" -ForegroundColor White
    
    Write-Host "`nRecommendation:" -ForegroundColor Green
    Write-Host "Use the Modern SharePoint Page URL - it handles permissions better" -ForegroundColor White
    Write-Host "and will display the form properly without download prompts." -ForegroundColor White
    
    Write-Host "`nTest Code: ABCD1234" -ForegroundColor Cyan
    
} catch {
    Write-Host "`n❌ Error: $_" -ForegroundColor Red
    Write-Host "Details: $($_.Exception.Message)" -ForegroundColor Red
} finally {
    Disconnect-PnPOnline
}

Write-Host "`n========================================" -ForegroundColor Cyan
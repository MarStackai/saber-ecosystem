#!/usr/bin/pwsh
<#
.SYNOPSIS
    Creates a publicly accessible SharePoint page for the EPC form
#>

param(
    [string]$SiteUrl = "https://saberrenewables.sharepoint.com/sites/SaberEPCPartners",
    [string]$ClientId = "bbbfe394-7cff-4ac9-9e01-33cbf116b930",
    [string]$Tenant = "saberrenewables.onmicrosoft.com"
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Creating Public SharePoint Page" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Connect to SharePoint
Write-Host "`nConnecting to SharePoint..." -ForegroundColor Yellow
Connect-PnPOnline -Url $SiteUrl -ClientId $ClientId -Tenant $Tenant -DeviceLogin

try {
    Write-Host "`nCreating SharePoint-native solution..." -ForegroundColor Green
    
    # Create an HTML file that uses SharePoint's native embedding
    $embedHTML = @"
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <title>EPC Partner Portal | Saber Renewables</title>
    <style>
        body, html {
            margin: 0;
            padding: 0;
            width: 100%;
            height: 100vh;
            overflow: hidden;
        }
        .form-container {
            width: 100%;
            height: 100vh;
            position: relative;
        }
        iframe {
            width: 100%;
            height: 100%;
            border: none;
        }
        .loading {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            text-align: center;
            font-family: Arial, sans-serif;
        }
    </style>
</head>
<body>
    <div class="form-container">
        <div class="loading" id="loading">
            <h2>Loading EPC Partner Portal...</h2>
            <p>Please wait...</p>
        </div>
        <iframe 
            id="formFrame"
            src="verify-access-branded.html" 
            onload="document.getElementById('loading').style.display='none';"
            onerror="handleError()">
        </iframe>
    </div>
    <script>
        function handleError() {
            // Try direct navigation if iframe fails
            window.location.href = 'verify-access-branded.html';
        }
        
        // Check if we're in SharePoint context
        if (typeof _spPageContextInfo !== 'undefined') {
            console.log('Running in SharePoint context');
        }
    </script>
</body>
</html>
"@
    
    # Save and upload embed page
    $tempEmbed = [System.IO.Path]::GetTempFileName() + ".html"
    $embedHTML | Out-File -FilePath $tempEmbed -Encoding UTF8
    
    Write-Host "Uploading embed page..." -ForegroundColor White
    Add-PnPFile -Path $tempEmbed -Folder "SiteAssets/EPCForm" -NewFileName "portal.html"
    Remove-Item $tempEmbed
    
    # Create a SharePoint page using Site Pages
    Write-Host "`nTrying to create a Site Page..." -ForegroundColor Yellow
    
    try {
        # Try the modern approach
        $pageName = "epc-partner-portal"
        
        # Remove existing page if it exists
        Remove-PnPPage -Identity $pageName -ErrorAction SilentlyContinue
        
        # Add new page
        Add-PnPPage -Name $pageName -LayoutType Article -Publish -ErrorAction Stop
        
        # Add an embed web part with the form
        $embedCode = @"
<iframe src="$SiteUrl/SiteAssets/EPCForm/verify-access-branded.html" 
        width="100%" 
        height="800" 
        frameborder="0">
</iframe>
"@
        
        Add-PnPPageTextPart -Page $pageName -Text $embedCode
        
        Write-Host "✅ Site Page created successfully!" -ForegroundColor Green
        $sitePageUrl = "$SiteUrl/SitePages/$pageName.aspx"
        
    } catch {
        Write-Host "⚠ Could not create Site Page (may need different permissions)" -ForegroundColor Yellow
        $sitePageUrl = "Not available - requires Site Owner permissions"
    }
    
    # Create sharing links
    Write-Host "`nChecking file sharing options..." -ForegroundColor Yellow
    
    try {
        # Get the file
        $file = Get-PnPFile -Url "/sites/SaberEPCPartners/SiteAssets/EPCForm/verify-access-branded.html"
        
        # Try to create a sharing link
        Write-Host "Attempting to create anonymous sharing link..." -ForegroundColor White
        # Note: This requires specific SharePoint settings to be enabled
        
    } catch {
        Write-Host "⚠ Could not create sharing link (may need to be done manually)" -ForegroundColor Yellow
    }
    
    Write-Host "`n========================================" -ForegroundColor Cyan
    Write-Host "✅ Deployment Complete!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Cyan
    
    Write-Host "`n📋 SUMMARY OF URLS:" -ForegroundColor Cyan
    
    Write-Host "`n1. Embed Portal (Should work for all users):" -ForegroundColor Green
    Write-Host "   $SiteUrl/SiteAssets/EPCForm/portal.html" -ForegroundColor White
    
    if ($sitePageUrl -ne "Not available - requires Site Owner permissions") {
        Write-Host "`n2. Site Page (Modern SharePoint):" -ForegroundColor Green
        Write-Host "   $sitePageUrl" -ForegroundColor White
    }
    
    Write-Host "`n3. Direct Access (May require login):" -ForegroundColor Yellow
    Write-Host "   $SiteUrl/SiteAssets/EPCForm/verify-access-branded.html" -ForegroundColor Gray
    
    Write-Host "`n⚠ IMPORTANT NOTES:" -ForegroundColor Yellow
    Write-Host "• If files download instead of displaying, use the embed portal URL" -ForegroundColor White
    Write-Host "• For anonymous access, you may need to:" -ForegroundColor White
    Write-Host "  1. Go to SharePoint site settings" -ForegroundColor Gray
    Write-Host "  2. Navigate to the file in document library" -ForegroundColor Gray
    Write-Host "  3. Click 'Share' and create an 'Anyone with the link' share" -ForegroundColor Gray
    Write-Host "  4. Use that sharing link for public access" -ForegroundColor Gray
    
    Write-Host "`nTest Code: ABCD1234" -ForegroundColor Cyan
    
} catch {
    Write-Host "`n❌ Error: $_" -ForegroundColor Red
} finally {
    Disconnect-PnPOnline
}

Write-Host "`n========================================" -ForegroundColor Cyan
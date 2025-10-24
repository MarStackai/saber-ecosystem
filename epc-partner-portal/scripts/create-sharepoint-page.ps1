#!/usr/bin/pwsh
<#
.SYNOPSIS
    Creates a SharePoint page that will render properly
#>

param(
    [string]$SiteUrl = "https://saberrenewables.sharepoint.com/sites/SaberEPCPartners",
    [string]$ClientId = "bbbfe394-7cff-4ac9-9e01-33cbf116b930",
    [string]$Tenant = "saberrenewables.onmicrosoft.com"
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Creating SharePoint Web Part Page" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Connect to SharePoint
Write-Host "`nConnecting to SharePoint..." -ForegroundColor Yellow
Connect-PnPOnline -Url $SiteUrl -ClientId $ClientId -Tenant $Tenant -DeviceLogin

try {
    # Check what's actually in the folder
    Write-Host "`nChecking current files in EPCForm folder..." -ForegroundColor Yellow
    $files = Get-PnPFolderItem -FolderSiteRelativeUrl "SiteAssets/EPCForm"
    
    Write-Host "`nCurrent files:" -ForegroundColor Green
    foreach ($file in $files) {
        Write-Host "  - $($file.Name) [$($file.TypedObject.GetType().Name)]" -ForegroundColor White
    }
    
    # Try to read one of the uploaded files to see what's happening
    Write-Host "`nChecking verify.aspx file properties..." -ForegroundColor Yellow
    $fileInfo = Get-PnPFile -Url "/sites/SaberEPCPartners/SiteAssets/EPCForm/verify.aspx" -AsFileInformation
    Write-Host "  Content Type: $($fileInfo.ContentType)" -ForegroundColor White
    Write-Host "  Size: $($fileInfo.Length) bytes" -ForegroundColor White
    
    # Create a simple HTML test page
    Write-Host "`nCreating test HTML page..." -ForegroundColor Yellow
    
    $testHTML = @"
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>EPC Form Test</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            padding: 20px;
            background: #f0f0f0;
        }
        .container {
            max-width: 600px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #044D73;
        }
        .status {
            padding: 10px;
            background: #e8f5e9;
            border-left: 4px solid #4caf50;
            margin: 20px 0;
        }
        a {
            color: #044D73;
            text-decoration: none;
            font-weight: bold;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>EPC Form System Status</h1>
        <div class="status">
            <strong>✓ Connection Successful</strong><br>
            This page is loading correctly from SharePoint.
        </div>
        
        <h2>Available Forms:</h2>
        <ul>
            <li><a href="verify-access-branded.html">Branded Verification Page (HTML)</a></li>
            <li><a href="verify.aspx">Verification Page (ASPX)</a></li>
            <li><a href="form.aspx">Main Form (ASPX)</a></li>
        </ul>
        
        <h2>Test Access Code:</h2>
        <p><strong>ABCD1234</strong></p>
        
        <h2>Direct Links:</h2>
        <p><a href="$SiteUrl/SiteAssets/EPCForm/verify-access-branded.html">Try Branded HTML Version</a></p>
    </div>
</body>
</html>
"@
    
    # Save and upload test page
    $tempTest = [System.IO.Path]::GetTempFileName() + ".html"
    $testHTML | Out-File -FilePath $tempTest -Encoding UTF8
    
    Write-Host "Uploading test page..." -ForegroundColor White
    Add-PnPFile -Path $tempTest -Folder "SiteAssets/EPCForm" -NewFileName "test.html"
    Remove-Item $tempTest
    
    Write-Host "`n========================================" -ForegroundColor Cyan
    Write-Host "✅ Test Page Created!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Cyan
    
    Write-Host "`nTest URL:" -ForegroundColor Yellow
    Write-Host "$SiteUrl/SiteAssets/EPCForm/test.html" -ForegroundColor White
    
    Write-Host "`nThis test page will help us verify:" -ForegroundColor Green
    Write-Host "✓ SharePoint is serving files correctly" -ForegroundColor Gray
    Write-Host "✓ Which file formats work best" -ForegroundColor Gray
    Write-Host "✓ Links between pages function properly" -ForegroundColor Gray
    
} catch {
    Write-Host "`n❌ Error: $_" -ForegroundColor Red
    Write-Host "Error details: $($_.Exception.Message)" -ForegroundColor Red
} finally {
    Disconnect-PnPOnline
}

Write-Host "`n========================================" -ForegroundColor Cyan
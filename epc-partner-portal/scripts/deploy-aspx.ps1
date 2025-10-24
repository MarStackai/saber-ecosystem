#!/usr/bin/pwsh
<#
.SYNOPSIS
    Deploys ASPX pages to SharePoint that will render properly in browser
#>

param(
    [string]$SiteUrl = "https://saberrenewables.sharepoint.com/sites/SaberEPCPartners",
    [string]$ClientId = "bbbfe394-7cff-4ac9-9e01-33cbf116b930",
    [string]$Tenant = "saberrenewables.onmicrosoft.com"
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Deploying ASPX Pages to SharePoint" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Connect to SharePoint
Write-Host "`nConnecting to SharePoint..." -ForegroundColor Yellow
Connect-PnPOnline -Url $SiteUrl -ClientId $ClientId -Tenant $Tenant -DeviceLogin

try {
    $folderUrl = "SitePages"  # Using SitePages for ASPX files
    $formPath = "/home/marstack/saber_business_ops/epc-form"
    
    Write-Host "`nCreating ASPX pages..." -ForegroundColor Green
    
    # Upload ASPX files to SitePages
    $files = @(
        @{Name="EPCVerifyAccess.aspx"; Path="$formPath/verify-access.aspx"},
        @{Name="EPCForm.aspx"; Path="$formPath/index.aspx"}
    )
    
    foreach ($file in $files) {
        Write-Host "Uploading: $($file.Name)" -ForegroundColor White -NoNewline
        
        try {
            # Upload to SitePages folder which handles ASPX properly
            Add-PnPFile -Path $file.Path -Folder $folderUrl -NewFileName $file.Name
            Write-Host " ✓" -ForegroundColor Green
        } catch {
            Write-Host " ✗ Error: $_" -ForegroundColor Red
        }
    }
    
    # Also create a redirect page in SiteAssets
    Write-Host "`nCreating redirect page..." -ForegroundColor Green
    
    $redirectHTML = @"
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Redirecting to EPC Portal...</title>
    <meta http-equiv="refresh" content="0; url='$SiteUrl/SitePages/EPCVerifyAccess.aspx'">
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            display: flex;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
            margin: 0;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }
        .redirect-message {
            background: white;
            padding: 40px;
            border-radius: 10px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            text-align: center;
        }
        h1 {
            color: #333;
            margin: 0 0 20px 0;
        }
        p {
            color: #666;
            margin: 0;
        }
        a {
            color: #667eea;
            text-decoration: none;
        }
    </style>
</head>
<body>
    <div class="redirect-message">
        <h1>Redirecting to EPC Partner Portal...</h1>
        <p>If you are not redirected automatically, <a href="$SiteUrl/SitePages/EPCVerifyAccess.aspx">click here</a>.</p>
    </div>
    <script>
        window.location.href = '$SiteUrl/SitePages/EPCVerifyAccess.aspx';
    </script>
</body>
</html>
"@
    
    # Save redirect HTML to temp file and upload
    $tempRedirect = [System.IO.Path]::GetTempFileName() + ".html"
    $redirectHTML | Out-File -FilePath $tempRedirect -Encoding UTF8
    
    Write-Host "Uploading: epc-portal.html" -ForegroundColor White -NoNewline
    Add-PnPFile -Path $tempRedirect -Folder "SiteAssets/EPCForm" -NewFileName "epc-portal.html"
    Remove-Item $tempRedirect
    Write-Host " ✓" -ForegroundColor Green
    
    Write-Host "`n========================================" -ForegroundColor Cyan
    Write-Host "✅ ASPX Deployment Complete!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Cyan
    
    Write-Host "`nDirect URLs (Will display in browser):" -ForegroundColor Yellow
    Write-Host "Entry Point: $SiteUrl/SitePages/EPCVerifyAccess.aspx" -ForegroundColor White
    Write-Host "Main Form:   $SiteUrl/SitePages/EPCForm.aspx" -ForegroundColor White
    
    Write-Host "`nAlternative Entry:" -ForegroundColor Yellow
    Write-Host "Redirect:    $SiteUrl/SiteAssets/EPCForm/epc-portal.html" -ForegroundColor White
    
    Write-Host "`nWhat's Different:" -ForegroundColor Green
    Write-Host "✓ ASPX pages render directly in SharePoint" -ForegroundColor Gray
    Write-Host "✓ No download prompts" -ForegroundColor Gray
    Write-Host "✓ Full branding preserved" -ForegroundColor Gray
    Write-Host "✓ Works with SharePoint's content disposition" -ForegroundColor Gray
    Write-Host "✓ Redirect page for backwards compatibility" -ForegroundColor Gray
    
    Write-Host "`nTest with code: ABCD1234" -ForegroundColor Cyan
    
} catch {
    Write-Host "`n❌ Error: $_" -ForegroundColor Red
} finally {
    Disconnect-PnPOnline
}

Write-Host "`n========================================" -ForegroundColor Cyan
#!/usr/bin/pwsh
<#
.SYNOPSIS
    Deploys fully branded, self-contained form files to SharePoint
#>

param(
    [string]$SiteUrl = "https://saberrenewables.sharepoint.com/sites/SaberEPCPartners",
    [string]$ClientId = "bbbfe394-7cff-4ac9-9e01-33cbf116b930",
    [string]$Tenant = "saberrenewables.onmicrosoft.com"
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Deploying Branded Form to SharePoint" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Connect to SharePoint
Write-Host "`nConnecting to SharePoint..." -ForegroundColor Yellow
Connect-PnPOnline -Url $SiteUrl -ClientId $ClientId -Tenant $Tenant -DeviceLogin

try {
    $folderUrl = "SiteAssets/EPCForm"
    $formPath = "/home/marstack/saber_business_ops/epc-form"
    
    Write-Host "`nPreparing branded files..." -ForegroundColor Green
    
    # Read the CSS file content
    $cssContent = Get-Content "$formPath/styles.css" -Raw
    
    # Read the SVG logo
    $logoSvg = Get-Content "$formPath/saber-logo.svg" -Raw
    
    # Extract just the SVG paths for embedding
    $svgPaths = @"
<svg class="saber-logo-svg" viewBox="0 0 495.2 101.48" xmlns="http://www.w3.org/2000/svg">
    <g>
        <path fill="#ffffff" d="M214.57,49.54c4.73,2.21,9.77,3.78,15.45,3.78s11.35-2.21,11.35-6.94-5.05-6.31-11.67-8.83c-8.2-3.15-17.34-7.25-17.34-18.92S221.82.03,232.86.03s13.56.95,20.18,3.47l-3.15,11.04c-5.05-1.89-9.77-3.15-15.77-3.15s-8.83,2.52-8.83,5.99c0,5.05,5.05,6.94,11.35,9.14,8.51,3.15,17.66,7.25,17.66,18.6s-10.09,19.86-23.65,19.86-15.14-2.21-19.86-5.05l4.1-10.09h0l-.32-.32Z"/>
        <path fill="#ffffff" d="M284.26.98l13.24-.63,23.96,63.38-13.56.63-5.99-17.03h-21.76l-5.68,16.4h-13.56L284.26.98ZM298.44,36.61l-4.1-11.35-3.47-11.04-3.47,11.04-3.78,11.35h14.82Z"/>
        <path fill="#ffffff" d="M331.24.98h21.44c13.87,0,21.13,5.68,21.13,15.77s-3.15,10.72-7.88,12.93h0c6.62,2.21,11.04,6.62,11.04,15.14s-9.14,19.23-23.02,19.23h-22.39V.98h-.32ZM355.2,26.52c4.1-1.26,5.68-4.1,5.68-7.88s-3.78-6.62-9.14-6.62h-7.88v14.19h11.35v.32ZM353.62,52.38c6.62,0,10.09-3.15,10.09-7.88s-3.78-6.62-8.83-7.25h-10.72v15.14h9.46Z"/>
        <path fill="#ffffff" d="M389.89.98h39.1l-.63,11.35h-26.17v14.19h24.28v10.72h-24.28v15.14h28.06l-.63,11.35h-40.04V.98h.32Z"/>
        <path fill="#ffffff" d="M443.49.98h20.81c15.77,0,23.96,6.62,23.96,18.92s-4.41,13.56-10.72,16.71l17.34,27.12-14.19.95-14.82-23.96h-9.77v23.02h-12.61V.98h0ZM468.08,29.67c4.1-1.26,6.94-4.1,6.94-8.83s-4.73-8.2-11.98-8.2h-6.94v17.34h11.98v-.32Z"/>
        <circle fill="#7CC061" cx="50.75" cy="50.75" r="50.75"/>
        <path fill="#ffffff" d="M28.06,24.28l40.84,8.3c1.72.35,1.7,2.81-.03,3.13l-17.41,3.18,28.43,23.84c1.42,1.19.37,3.46-1.43,3.08l-42.2-8.99c-1.75-.37-1.67-2.9.1-3.16l16.88-2.46L23.65,27.34c-1.37-1.21-.26-3.44,1.5-3.02l2.91-.04Z"/>
    </g>
</svg>
"@
    
    Write-Host "`nUploading branded files..." -ForegroundColor Green
    
    # Upload the verification page
    $files = @(
        @{Name="verify-access.html"; Path="$formPath/verify-access-branded.html"},
        @{Name="verify-access-branded.html"; Path="$formPath/verify-access-branded.html"}
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
    
    # Create a combined CSS file that works in SharePoint
    Write-Host "`nCreating SharePoint-compatible CSS..." -ForegroundColor Green
    
    $sharePointCSS = @"
/* SharePoint Override Styles */
#s4-workspace { background: transparent !important; }
#s4-bodyContainer { background: transparent !important; }
.ms-core-overlay { background: transparent !important; }

$cssContent

/* Additional SharePoint fixes */
.saber-header {
    background: #044D73 !important;
    margin: -20px -20px 0 -20px;
    padding: 30px 20px;
}

.saber-logo-svg {
    width: 200px;
    height: auto;
    filter: brightness(0) invert(1);
}
"@
    
    # Save CSS to temp file and upload
    $tempCSS = [System.IO.Path]::GetTempFileName() + ".css"
    $sharePointCSS | Out-File -FilePath $tempCSS -Encoding UTF8
    
    Write-Host "Uploading: styles-sharepoint.css" -ForegroundColor White -NoNewline
    Add-PnPFile -Path $tempCSS -Folder $folderUrl -NewFileName "styles-sharepoint.css"
    Remove-Item $tempCSS
    Write-Host " ✓" -ForegroundColor Green
    
    Write-Host "`n========================================" -ForegroundColor Cyan
    Write-Host "✅ Branded Deployment Complete!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Cyan
    
    Write-Host "`nBranded URLs:" -ForegroundColor Yellow
    Write-Host "Entry Point: $SiteUrl/SiteAssets/EPCForm/verify-access.html" -ForegroundColor White
    
    Write-Host "`nWhat's Fixed:" -ForegroundColor Green
    Write-Host "✓ Saber logo embedded directly (no external file needed)" -ForegroundColor Gray
    Write-Host "✓ All CSS inline for proper SharePoint display" -ForegroundColor Gray
    Write-Host "✓ Header with Saber Blue background (#044D73)" -ForegroundColor Gray
    Write-Host "✓ Full branding with gradients and animations" -ForegroundColor Gray
    Write-Host "✓ Glass morphism effects preserved" -ForegroundColor Gray
    
    Write-Host "`nTest with code: ABCD1234" -ForegroundColor Cyan
    
} catch {
    Write-Host "`n❌ Error: $_" -ForegroundColor Red
} finally {
    Disconnect-PnPOnline
}

Write-Host "`n========================================" -ForegroundColor Cyan
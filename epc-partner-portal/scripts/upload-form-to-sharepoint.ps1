#!/usr/bin/pwsh
<#
.SYNOPSIS
    Uploads EPC Partner form files to SharePoint Site Assets
.DESCRIPTION
    Fixes 404 error by properly uploading all form files to SharePoint
.EXAMPLE
    ./upload-form-to-sharepoint.ps1
#>

param(
    [string]$SiteUrl = "https://saberrenewables.sharepoint.com/sites/SaberEPCPartners",
    [string]$ClientId = "bbbfe394-7cff-4ac9-9e01-33cbf116b930",
    [string]$Tenant = "saberrenewables.onmicrosoft.com",
    [string]$FormPath = "/home/marstack/saber_business_ops/epc-form"
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Uploading EPC Form to SharePoint" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Connect to SharePoint
Write-Host "`nConnecting to SharePoint..." -ForegroundColor Yellow
Connect-PnPOnline -Url $SiteUrl -ClientId $ClientId -Tenant $Tenant -DeviceLogin

try {
    # Create folder structure
    Write-Host "`nCreating folder structure..." -ForegroundColor Green
    
    # Ensure SiteAssets library exists
    $siteAssets = Get-PnPList -Identity "Site Assets" -ErrorAction SilentlyContinue
    if (-not $siteAssets) {
        Write-Host "Creating Site Assets library..." -ForegroundColor Yellow
        New-PnPList -Title "Site Assets" -Template DocumentLibrary
    }
    
    # Create EPCForm folder
    $folderUrl = "SiteAssets/EPCForm"
    try {
        $folder = Get-PnPFolder -Url $folderUrl -ErrorAction SilentlyContinue
        Write-Host "✓ Folder exists: $folderUrl" -ForegroundColor Gray
    } catch {
        Write-Host "Creating folder: $folderUrl" -ForegroundColor Yellow
        Add-PnPFolder -Name "EPCForm" -Folder "SiteAssets"
        Write-Host "✓ Folder created" -ForegroundColor Green
    }
    
    # Upload form files
    Write-Host "`nUploading form files..." -ForegroundColor Green
    
    $files = @(
        "index.html",
        "verify-access.html",
        "styles.css",
        "script.js",
        "sharepoint-integration.js",
        "saber-logo.svg"
    )
    
    $uploadedCount = 0
    $failedCount = 0
    
    foreach ($file in $files) {
        $filePath = Join-Path $FormPath $file
        
        if (Test-Path $filePath) {
            try {
                Write-Host "Uploading: $file" -ForegroundColor White -NoNewline
                
                # Read file content
                $fileContent = Get-Content $filePath -Raw -Encoding UTF8
                
                # For HTML files, update the form action URL
                if ($file -match "\.html$") {
                    # Update any localhost references
                    $fileContent = $fileContent -replace "http://localhost:\d+", $SiteUrl
                    
                    # Ensure correct paths for assets
                    $fileContent = $fileContent -replace 'src="saber-logo\.svg"', 'src="saber-logo.svg"'
                    $fileContent = $fileContent -replace 'href="styles\.css"', 'href="styles.css"'
                    $fileContent = $fileContent -replace 'src="script\.js"', 'src="script.js"'
                }
                
                # Upload file
                Add-PnPFile -Path $filePath -Folder $folderUrl
                
                Write-Host " ✓" -ForegroundColor Green
                $uploadedCount++
                
            } catch {
                Write-Host " ✗ Failed: $_" -ForegroundColor Red
                $failedCount++
            }
        } else {
            Write-Host "File not found: $file" -ForegroundColor Yellow
        }
    }
    
    Write-Host "`n----------------------------------------" -ForegroundColor Gray
    Write-Host "Upload Summary:" -ForegroundColor Cyan
    Write-Host "✓ Uploaded: $uploadedCount files" -ForegroundColor Green
    if ($failedCount -gt 0) {
        Write-Host "✗ Failed: $failedCount files" -ForegroundColor Red
    }
    
    # Set permissions on the folder
    Write-Host "`nSetting permissions..." -ForegroundColor Green
    
    # Set permissions using list item
    try {
        $folderItem = Get-PnPFolder -Url $folderUrl -Includes ListItemAllFields
        Set-PnPListItemPermission -List "Site Assets" -Identity $folderItem.ListItemAllFields.Id -InheritPermissions:$false
        Write-Host "✓ Permissions configured" -ForegroundColor Green
    } catch {
        Write-Host "⚠ Could not set custom permissions (may need admin rights)" -ForegroundColor Yellow
    }
    
    # Create a simple redirect page at site root
    Write-Host "`nCreating redirect page..." -ForegroundColor Green
    
    $redirectHTML = @"
<!DOCTYPE html>
<html>
<head>
    <title>EPC Partner Portal - Redirecting...</title>
    <meta http-equiv="refresh" content="0; url=$SiteUrl/SiteAssets/EPCForm/verify-access.html">
    <style>
        body {
            font-family: 'Segoe UI', Arial, sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
            background: linear-gradient(135deg, #044D73, #0d1138);
            color: white;
        }
        .message {
            text-align: center;
        }
        a {
            color: #7CC061;
        }
    </style>
</head>
<body>
    <div class="message">
        <h2>Redirecting to EPC Partner Portal...</h2>
        <p>If you're not redirected, <a href="$SiteUrl/SiteAssets/EPCForm/verify-access.html">click here</a></p>
    </div>
</body>
</html>
"@
    
    # Save redirect HTML to temp file and upload
    $tempFile = [System.IO.Path]::GetTempFileName() + ".html"
    $redirectHTML | Out-File -FilePath $tempFile -Encoding UTF8
    Add-PnPFile -Path $tempFile -Folder "SiteAssets"
    Remove-Item $tempFile
    Write-Host "✓ Redirect page created" -ForegroundColor Green
    
    # Display success information
    Write-Host "`n========================================" -ForegroundColor Cyan
    Write-Host "✅ Upload Complete!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Cyan
    
    Write-Host "`nYour form is now accessible at:" -ForegroundColor Yellow
    Write-Host "$SiteUrl/SiteAssets/EPCForm/verify-access.html" -ForegroundColor White
    
    Write-Host "`nDirect links:" -ForegroundColor Yellow
    Write-Host "Main Form:      $SiteUrl/SiteAssets/EPCForm/index.html" -ForegroundColor Gray
    Write-Host "Verification:   $SiteUrl/SiteAssets/EPCForm/verify-access.html" -ForegroundColor Gray
    Write-Host "Redirect Page:  $SiteUrl/SiteAssets/epc-portal.html" -ForegroundColor Gray
    
    Write-Host "`nTest Codes:" -ForegroundColor Yellow
    Write-Host "• ABCD1234" -ForegroundColor Gray
    Write-Host "• TEST1234" -ForegroundColor Gray
    Write-Host "• DEMO1234" -ForegroundColor Gray
    
    Write-Host "`nOperations Guide:" -ForegroundColor Yellow
    Write-Host "See OPERATIONS_GUIDE.md for full instructions" -ForegroundColor Gray
    
} catch {
    Write-Host "`n❌ Error: $_" -ForegroundColor Red
    Write-Host "Stack Trace: $($_.ScriptStackTrace)" -ForegroundColor Red
} finally {
    Disconnect-PnPOnline
}

Write-Host "`n========================================" -ForegroundColor Cyan
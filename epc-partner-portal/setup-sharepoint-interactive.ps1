#!/usr/bin/env pwsh
# Interactive SharePoint Setup Script

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  EPC Portal SharePoint Setup Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if PnP.PowerShell is installed
Write-Host "Checking for PnP.PowerShell module..." -ForegroundColor Yellow
if (!(Get-Module -ListAvailable -Name PnP.PowerShell)) {
    Write-Host "Installing PnP.PowerShell module (this may take a minute)..." -ForegroundColor Yellow
    Install-Module -Name PnP.PowerShell -Force -AllowClobber -Scope CurrentUser -Repository PSGallery
}

Import-Module PnP.PowerShell

Write-Host ""
Write-Host "Please follow these steps:" -ForegroundColor Green
Write-Host "1. When the browser opens, sign in with your Saber Renewables account" -ForegroundColor White
Write-Host "2. Grant permissions when prompted" -ForegroundColor White
Write-Host "3. Return to this window after authentication" -ForegroundColor White
Write-Host ""
Write-Host "Press Enter to open the authentication window..." -ForegroundColor Yellow
Read-Host

# Connect with device login
$siteUrl = "https://saberrenewables.sharepoint.com/sites/SaberEPCPartners"
Connect-PnPOnline -Url $siteUrl -DeviceLogin

Write-Host ""
Write-Host "Connected successfully!" -ForegroundColor Green
Write-Host ""

# Now run the setup
$listName = "EPC Invitations"

Write-Host "Setting up EPC Invitations list..." -ForegroundColor Yellow

# Get or create the list
$list = Get-PnPList -Identity $listName -ErrorAction SilentlyContinue
if ($null -eq $list) {
    Write-Host "Creating new list..." -ForegroundColor Yellow
    $list = New-PnPList -Title $listName -Template GenericList
}

# Add columns
Write-Host "Adding required columns..." -ForegroundColor Yellow

try {
    # Status column
    if (!(Get-PnPField -List $listName -Identity "Status" -ErrorAction SilentlyContinue)) {
        Add-PnPField -List $listName -DisplayName "Status" -InternalName "Status" -Type Choice -Choices @("Active","Expired","Used") 
        Write-Host "✓ Status" -ForegroundColor Green
    }

    # Code column  
    if (!(Get-PnPField -List $listName -Identity "Code" -ErrorAction SilentlyContinue)) {
        Add-PnPField -List $listName -DisplayName "Code" -InternalName "Code" -Type Text
        Write-Host "✓ Code" -ForegroundColor Green
    }

    # ExpiryDate column
    if (!(Get-PnPField -List $listName -Identity "ExpiryDate" -ErrorAction SilentlyContinue)) {
        Add-PnPField -List $listName -DisplayName "Expiry Date" -InternalName "ExpiryDate" -Type DateTime
        Write-Host "✓ ExpiryDate" -ForegroundColor Green
    }

    # Used column
    if (!(Get-PnPField -List $listName -Identity "Used" -ErrorAction SilentlyContinue)) {
        Add-PnPField -List $listName -DisplayName "Used" -InternalName "Used" -Type Boolean
        Write-Host "✓ Used" -ForegroundColor Green
    }

    # UsedBy column
    if (!(Get-PnPField -List $listName -Identity "UsedBy" -ErrorAction SilentlyContinue)) {
        Add-PnPField -List $listName -DisplayName "Used By" -InternalName "UsedBy" -Type Text
        Write-Host "✓ UsedBy" -ForegroundColor Green
    }

    # UsedDate column
    if (!(Get-PnPField -List $listName -Identity "UsedDate" -ErrorAction SilentlyContinue)) {
        Add-PnPField -List $listName -DisplayName "Used Date" -InternalName "UsedDate" -Type DateTime
        Write-Host "✓ UsedDate" -ForegroundColor Green
    }
}
catch {
    Write-Host "Error adding columns: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "Adding test invitation codes..." -ForegroundColor Yellow

# Add TEST2024
$futureDate = (Get-Date).AddMonths(6).ToString("yyyy-MM-dd")
Add-PnPListItem -List $listName -Values @{
    Title = "Test Code"
    Code = "TEST2024"
    Status = "Active"
    ExpiryDate = $futureDate
    Used = $false
} | Out-Null
Write-Host "✓ Added TEST2024" -ForegroundColor Green

# Add DEMO2024
Add-PnPListItem -List $listName -Values @{
    Title = "Demo Code"
    Code = "DEMO2024"
    Status = "Active"
    ExpiryDate = $futureDate
    Used = $false
} | Out-Null
Write-Host "✓ Added DEMO2024" -ForegroundColor Green

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  ✅ Setup Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "The EPC Invitations list is now configured with:" -ForegroundColor White
Write-Host "- All required columns (Status, Code, ExpiryDate, etc.)" -ForegroundColor White
Write-Host "- Test codes: TEST2024 and DEMO2024" -ForegroundColor White
Write-Host ""
Write-Host "You can now test the Power Automate flow!" -ForegroundColor Cyan

Disconnect-PnPOnline
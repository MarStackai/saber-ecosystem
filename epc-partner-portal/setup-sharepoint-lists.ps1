# SharePoint List Setup Script for EPC Portal
# This script adds the required columns to the EPC Invitations list

# Connect to SharePoint
$siteUrl = "https://saberrenewables.sharepoint.com/sites/SaberEPCPartners"
$listName = "EPC Invitations"

Write-Host "Connecting to SharePoint..." -ForegroundColor Yellow

# Install PnP PowerShell module if not already installed
if (!(Get-Module -ListAvailable -Name PnP.PowerShell)) {
    Write-Host "Installing PnP PowerShell module..." -ForegroundColor Yellow
    Install-Module -Name PnP.PowerShell -Force -AllowClobber -Scope CurrentUser
}

# Import the module
Import-Module PnP.PowerShell

# Connect to SharePoint site
try {
    Connect-PnPOnline -Url $siteUrl -Interactive
    Write-Host "Connected to SharePoint successfully!" -ForegroundColor Green
}
catch {
    Write-Host "Failed to connect to SharePoint. Please check your credentials." -ForegroundColor Red
    exit
}

# Get the list
$list = Get-PnPList -Identity $listName -ErrorAction SilentlyContinue

if ($null -eq $list) {
    Write-Host "Creating EPC Invitations list..." -ForegroundColor Yellow
    $list = New-PnPList -Title $listName -Template GenericList
    Write-Host "List created successfully!" -ForegroundColor Green
}

Write-Host "Adding columns to EPC Invitations list..." -ForegroundColor Yellow

# Add Status column (Choice field)
$statusField = Get-PnPField -List $listName -Identity "Status" -ErrorAction SilentlyContinue
if ($null -eq $statusField) {
    Add-PnPField -List $listName -DisplayName "Status" -InternalName "Status" -Type Choice -Choices "Active","Expired","Used" -Required
    Write-Host "✓ Added Status column" -ForegroundColor Green
} else {
    Write-Host "⚠ Status column already exists" -ForegroundColor Yellow
}

# Add Code column (Text field)
$codeField = Get-PnPField -List $listName -Identity "Code" -ErrorAction SilentlyContinue
if ($null -eq $codeField) {
    Add-PnPField -List $listName -DisplayName "Code" -InternalName "Code" -Type Text -Required
    Write-Host "✓ Added Code column" -ForegroundColor Green
} else {
    Write-Host "⚠ Code column already exists" -ForegroundColor Yellow
}

# Add ExpiryDate column (DateTime field)
$expiryField = Get-PnPField -List $listName -Identity "ExpiryDate" -ErrorAction SilentlyContinue
if ($null -eq $expiryField) {
    Add-PnPField -List $listName -DisplayName "Expiry Date" -InternalName "ExpiryDate" -Type DateTime
    Write-Host "✓ Added ExpiryDate column" -ForegroundColor Green
} else {
    Write-Host "⚠ ExpiryDate column already exists" -ForegroundColor Yellow
}

# Add Used column (Boolean field)
$usedField = Get-PnPField -List $listName -Identity "Used" -ErrorAction SilentlyContinue
if ($null -eq $usedField) {
    Add-PnPField -List $listName -DisplayName "Used" -InternalName "Used" -Type Boolean
    Set-PnPField -List $listName -Identity "Used" -Values @{DefaultValue="0"}
    Write-Host "✓ Added Used column" -ForegroundColor Green
} else {
    Write-Host "⚠ Used column already exists" -ForegroundColor Yellow
}

# Add UsedBy column (Text field)
$usedByField = Get-PnPField -List $listName -Identity "UsedBy" -ErrorAction SilentlyContinue
if ($null -eq $usedByField) {
    Add-PnPField -List $listName -DisplayName "Used By" -InternalName "UsedBy" -Type Text
    Write-Host "✓ Added UsedBy column" -ForegroundColor Green
} else {
    Write-Host "⚠ UsedBy column already exists" -ForegroundColor Yellow
}

# Add UsedDate column (DateTime field)
$usedDateField = Get-PnPField -List $listName -Identity "UsedDate" -ErrorAction SilentlyContinue
if ($null -eq $usedDateField) {
    Add-PnPField -List $listName -DisplayName "Used Date" -InternalName "UsedDate" -Type DateTime
    Write-Host "✓ Added UsedDate column" -ForegroundColor Green
} else {
    Write-Host "⚠ UsedDate column already exists" -ForegroundColor Yellow
}

Write-Host "`nColumns added successfully!" -ForegroundColor Green

# Add test invitation codes
Write-Host "`nAdding test invitation codes..." -ForegroundColor Yellow

# Check if TEST2024 exists
$existingTest = Get-PnPListItem -List $listName -Query "<View><Query><Where><Eq><FieldRef Name='Code'/><Value Type='Text'>TEST2024</Value></Eq></Where></Query></View>"
if ($null -eq $existingTest) {
    $futureDate = (Get-Date).AddMonths(6)
    Add-PnPListItem -List $listName -Values @{
        Title = "Test Code 1"
        Code = "TEST2024"
        Status = "Active"
        ExpiryDate = $futureDate
        Used = $false
    }
    Write-Host "✓ Added TEST2024 invitation code" -ForegroundColor Green
} else {
    Write-Host "⚠ TEST2024 already exists" -ForegroundColor Yellow
}

# Check if DEMO2024 exists
$existingDemo = Get-PnPListItem -List $listName -Query "<View><Query><Where><Eq><FieldRef Name='Code'/><Value Type='Text'>DEMO2024</Value></Eq></Where></Query></View>"
if ($null -eq $existingDemo) {
    $futureDate = (Get-Date).AddMonths(6)
    Add-PnPListItem -List $listName -Values @{
        Title = "Demo Code"
        Code = "DEMO2024"
        Status = "Active"
        ExpiryDate = $futureDate
        Used = $false
    }
    Write-Host "✓ Added DEMO2024 invitation code" -ForegroundColor Green
} else {
    Write-Host "⚠ DEMO2024 already exists" -ForegroundColor Yellow
}

Write-Host "`n✅ SharePoint list setup complete!" -ForegroundColor Green
Write-Host "You can now test the EPC Portal form submission." -ForegroundColor Cyan

# Disconnect from SharePoint
Disconnect-PnPOnline
#!/usr/bin/env pwsh

# EPC Portal SharePoint List Setup
# Run this script: pwsh fix-sharepoint-lists.ps1

param(
    [string]$SiteUrl = "https://saberrenewables.sharepoint.com/sites/SaberEPCPartners",
    [string]$ListName = "EPC Invitations"
)

Write-Host "`n=====================================" -ForegroundColor Cyan
Write-Host "   EPC Portal SharePoint Setup" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan

# Install/Import PnP Module
if (!(Get-Module -ListAvailable -Name PnP.PowerShell)) {
    Write-Host "`nInstalling PnP.PowerShell module..." -ForegroundColor Yellow
    Install-Module PnP.PowerShell -Force -Scope CurrentUser -AllowClobber
}
Import-Module PnP.PowerShell

# Connect to SharePoint
Write-Host "`nConnecting to SharePoint..." -ForegroundColor Yellow
Write-Host "Site: $SiteUrl" -ForegroundColor Gray

try {
    # Try stored connection first
    Connect-PnPOnline -Url $SiteUrl -ReturnConnection -ErrorAction Stop | Out-Null
    Write-Host "Connected successfully!" -ForegroundColor Green
}
catch {
    Write-Host "Please authenticate in your browser..." -ForegroundColor Yellow
    Connect-PnPOnline -Url $SiteUrl -Interactive
}

# Verify connection
$web = Get-PnPWeb
Write-Host "Connected to: $($web.Title)" -ForegroundColor Green

# Check if list exists
Write-Host "`nChecking for '$ListName' list..." -ForegroundColor Yellow
$list = Get-PnPList -Identity $ListName -ErrorAction SilentlyContinue

if ($null -eq $list) {
    Write-Host "Creating list '$ListName'..." -ForegroundColor Yellow
    New-PnPList -Title $ListName -Template GenericList
    $list = Get-PnPList -Identity $ListName
    Write-Host "List created!" -ForegroundColor Green
} else {
    Write-Host "List exists!" -ForegroundColor Green
}

# Define required columns
$columns = @(
    @{Name="Status"; Type="Choice"; Choices=@("Active","Expired","Used"); Required=$true},
    @{Name="Code"; Type="Text"; Required=$true},
    @{Name="ExpiryDate"; Type="DateTime"; Required=$false},
    @{Name="Used"; Type="Boolean"; Required=$false; Default=$false},
    @{Name="UsedBy"; Type="Text"; Required=$false},
    @{Name="UsedDate"; Type="DateTime"; Required=$false}
)

Write-Host "`nAdding required columns..." -ForegroundColor Yellow

foreach ($col in $columns) {
    $field = Get-PnPField -List $ListName -Identity $col.Name -ErrorAction SilentlyContinue
    
    if ($null -eq $field) {
        $params = @{
            List = $ListName
            DisplayName = $col.Name
            InternalName = $col.Name
            Type = $col.Type
        }
        
        if ($col.Required) { $params.Required = $true }
        if ($col.Choices) { $params.Choices = $col.Choices }
        
        Add-PnPField @params | Out-Null
        Write-Host "  ✓ Added: $($col.Name)" -ForegroundColor Green
    } else {
        Write-Host "  ⚠ Exists: $($col.Name)" -ForegroundColor Yellow
    }
}

# Add test data
Write-Host "`nAdding test invitation codes..." -ForegroundColor Yellow

$testCodes = @(
    @{Code="TEST2024"; Title="Test Code 2024"},
    @{Code="DEMO2024"; Title="Demo Code 2024"},
    @{Code="TRIAL2024"; Title="Trial Code 2024"}
)

$futureDate = (Get-Date).AddMonths(6)

foreach ($testCode in $testCodes) {
    # Check if code already exists
    $camlQuery = "<View><Query><Where><Eq><FieldRef Name='Code'/><Value Type='Text'>$($testCode.Code)</Value></Eq></Where></Query></View>"
    $existing = Get-PnPListItem -List $ListName -Query $camlQuery
    
    if ($existing.Count -eq 0) {
        $values = @{
            Title = $testCode.Title
            Code = $testCode.Code
            Status = "Active"
            ExpiryDate = $futureDate
            Used = $false
        }
        
        Add-PnPListItem -List $ListName -Values $values | Out-Null
        Write-Host "  ✓ Added: $($testCode.Code)" -ForegroundColor Green
    } else {
        Write-Host "  ⚠ Exists: $($testCode.Code)" -ForegroundColor Yellow
    }
}

# Display current items
Write-Host "`nCurrent invitation codes:" -ForegroundColor Cyan
$items = Get-PnPListItem -List $ListName -Fields "Title","Code","Status","ExpiryDate","Used"
foreach ($item in $items) {
    Write-Host "  - Code: $($item["Code"]) | Status: $($item["Status"]) | Expires: $($item["ExpiryDate"])" -ForegroundColor White
}

Write-Host "`n=====================================" -ForegroundColor Green
Write-Host "   ✅ Setup Complete!" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Green
Write-Host "`nThe SharePoint list is now ready for Power Automate!" -ForegroundColor Cyan
Write-Host "Test the flow with code: TEST2024" -ForegroundColor Yellow

# Disconnect
Disconnect-PnPOnline
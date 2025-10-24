#!/usr/bin/pwsh
# Check ALL fields in SharePoint list (not just EPC Extended group)

Write-Host "=== Checking ALL SharePoint Field Names ===" -ForegroundColor Cyan

# Connect to SharePoint
Connect-PnPOnline -Url 'https://saberrenewables.sharepoint.com/sites/SaberEPCPartners' -ClientId 'bbbfe394-7cff-4ac9-9e01-33cbf116b930' -Tenant 'saberrenewables.onmicrosoft.com' -DeviceLogin

Write-Host "✅ Connected to SharePoint" -ForegroundColor Green

# Get ALL fields from the EPC Onboarding list (not just EPC Extended group)
$listTitle = "EPC Onboarding"
$allFields = Get-PnPField -List $listTitle | Where-Object { 
    $_.CanBeDeleted -eq $true -and 
    $_.InternalName -notlike "*_0x*" -and 
    $_.InternalName -notlike "LinkTitle*" -and
    $_.TypeAsString -ne "Lookup"
}

Write-Host "`n=== ALL CUSTOM SHAREPOINT FIELDS ===" -ForegroundColor Yellow
Write-Host "Found $($allFields.Count) custom fields:" -ForegroundColor Green

# Group by field group for better organization
$groupedFields = $allFields | Group-Object Group | Sort-Object Name

foreach ($group in $groupedFields) {
    Write-Host "`n--- $($group.Name) Group ---" -ForegroundColor Cyan
    foreach ($field in $group.Group | Sort-Object InternalName) {
        $displayName = $field.Title
        $internalName = $field.InternalName
        $type = $field.TypeAsString
        
        Write-Host "• $internalName ($type) - '$displayName'" -ForegroundColor White
    }
}

Write-Host "`n=== CRITICAL FIELDS CHECK ===" -ForegroundColor Yellow
$criticalFields = @(
    "TradingName", "RegisteredOffice", "CompanyRegNo", "YearsTrading",
    "PrimaryContactName", "PrimaryContactPhone", "PrimaryContactEmail",
    "ActsAsPrincipalContractor", "ActsAsPrincipalDesigner"
)

foreach ($critical in $criticalFields) {
    $found = $allFields | Where-Object { $_.InternalName -eq $critical }
    if ($found) {
        Write-Host "✅ $critical - $($found.TypeAsString)" -ForegroundColor Green
    } else {
        Write-Host "❌ $critical - NOT FOUND" -ForegroundColor Red
    }
}

Write-Host "`n=== FIELD MAPPING FOR POWER AUTOMATE ===" -ForegroundColor Yellow
$customFields = $allFields | Where-Object { $_.Group -ne "Base Columns" -and $_.Group -ne "_Hidden" }
foreach ($field in $customFields | Sort-Object InternalName) {
    Write-Host "`"item/$($field.InternalName)`" = `"@triggerBody()?['...']`"" -ForegroundColor Gray
}
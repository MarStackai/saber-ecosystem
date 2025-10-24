#!/usr/bin/pwsh
# Check what fields actually exist in SharePoint to get exact names

Write-Host "=== Checking SharePoint Field Names ===" -ForegroundColor Cyan

# Connect to SharePoint
Connect-PnPOnline -Url 'https://saberrenewables.sharepoint.com/sites/SaberEPCPartners' -ClientId 'bbbfe394-7cff-4ac9-9e01-33cbf116b930' -Tenant 'saberrenewables.onmicrosoft.com' -DeviceLogin

Write-Host "✅ Connected to SharePoint" -ForegroundColor Green

# Get all fields from the EPC Onboarding list
$listTitle = "EPC Onboarding"
$allFields = Get-PnPField -List $listTitle | Where-Object { $_.Group -eq "EPC Extended" -or $_.InternalName -in @("CompanyName","ReferenceNumber","SubmissionStatus") }

Write-Host "`n=== ACTUAL SHAREPOINT FIELD NAMES ===" -ForegroundColor Yellow
Write-Host "Found $($allFields.Count) fields:" -ForegroundColor Green

foreach ($field in $allFields | Sort-Object InternalName) {
    $displayName = $field.Title
    $internalName = $field.InternalName
    $type = $field.TypeAsString
    
    Write-Host "• $internalName ($type) - '$displayName'" -ForegroundColor White
}

Write-Host "`n=== FIELD MAPPING FOR POWER AUTOMATE ===" -ForegroundColor Yellow
foreach ($field in $allFields | Sort-Object InternalName) {
    Write-Host "`"item/$($field.InternalName)`" = `"@triggerBody()?['...']`"" -ForegroundColor Gray
}

Write-Host "`nUse these EXACT internal names in Power Automate flow!" -ForegroundColor Green
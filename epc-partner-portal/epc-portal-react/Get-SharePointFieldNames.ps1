#!/usr/bin/pwsh
<#
.SYNOPSIS
    Gets the actual internal field names from SharePoint to fix the Power Automate flow
#>

Write-Host "Getting actual SharePoint field names..." -ForegroundColor Yellow

# Connect to SharePoint (reuse existing session)
$siteUrl = "https://saberrenewables.sharepoint.com/sites/SaberEPCPartners"

try {
    # Get the EPC Onboarding list
    $list = Get-PnPList -Identity "EPC Onboarding"
    
    if ($list) {
        Write-Host "✅ Found EPC Onboarding list" -ForegroundColor Green
        
        # Get all fields and their internal names
        $fields = Get-PnPField -List $list | Where-Object { 
            $_.InternalName -like "*Principal*" -or 
            $_.InternalName -like "*VAT*" -or
            $_.InternalName -like "*Trading*" -or
            $_.InternalName -like "*HSE*" -or
            $_.InternalName -like "*RIDDOR*" -or
            $_.InternalName -like "*Policy*" -or
            $_.InternalName -like "*Liability*" -or
            $_.InternalName -like "*Indemnity*" -or
            $_.InternalName -like "*Contract*" -or
            $_.InternalName -like "*GDPR*"
        } | Sort-Object Title
        
        Write-Host "`nActual SharePoint Field Names:" -ForegroundColor Cyan
        Write-Host "================================" -ForegroundColor Cyan
        
        foreach ($field in $fields) {
            $title = $field.Title.PadRight(40)
            $internal = $field.InternalName
            Write-Host "$title -> $internal" -ForegroundColor White
        }
        
        # Export to file for reference
        $fieldMapping = @{}
        foreach ($field in $fields) {
            $fieldMapping[$field.Title] = $field.InternalName
        }
        
        $fieldMapping | ConvertTo-Json -Depth 2 | Set-Content "./sharepoint-field-mapping.json"
        Write-Host "`n✅ Field mapping saved to sharepoint-field-mapping.json" -ForegroundColor Green
        
    } else {
        Write-Host "❌ Could not find EPC Onboarding list" -ForegroundColor Red
    }
    
} catch {
    Write-Host "❌ Error getting field names: $($_.Exception.Message)" -ForegroundColor Red
}
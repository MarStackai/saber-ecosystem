#!/usr/bin/pwsh

param(
    [string]$InputPath = "./power-automate-export",
    [string]$OutputPath = "./power-automate-export-flat"
)

Write-Host "Creating flow with flat field references only..." -ForegroundColor Yellow

# Copy original structure
if (Test-Path $OutputPath) { Remove-Item $OutputPath -Recurse -Force }
Copy-Item $InputPath $OutputPath -Recurse -Force

# Load the flow definition
$definitionPath = "$OutputPath/Microsoft.Flow/flows/45991de2-99f2-422e-864f-efdf8db8cb93/definition.json"
$definition = Get-Content $definitionPath -Raw | ConvertFrom-Json

Write-Host "Finding and updating Create_item action..." -ForegroundColor Yellow

# Find Create_item action
$createItemAction = $null
if ($definition.properties.definition.actions.Create_item) {
    $createItemAction = $definition.properties.definition.actions.Create_item
} elseif ($definition.properties.definition.actions.Condition.actions.Create_item) {
    $createItemAction = $definition.properties.definition.actions.Condition.actions.Create_item
}

if ($createItemAction -and $createItemAction.inputs -and $createItemAction.inputs.parameters) {
    
    # COMPLETELY FLAT - no nested objects, no coalesce, no complex expressions
    $createItemAction.inputs.parameters = @{
        "item/CompanyName" = "@triggerBody()?['companyName']"
        "item/TradingName" = "@triggerBody()?['tradingName']"
        "item/PrimaryContactName" = "@triggerBody()?['contactName']"
        "item/PrimaryContactEmail" = "@triggerBody()?['email']"
        "item/PrimaryContactPhone" = "@triggerBody()?['phone']"
        "item/ContactName" = "@triggerBody()?['contactName']"
        "item/Email" = "@triggerBody()?['email']"
        "item/Phone" = "@triggerBody()?['phone']"
        "item/VATNumber" = "@triggerBody()?['vatNumber']"
        "item/CompanyRegNo" = "@triggerBody()?['companyRegNo']"
        "item/RegisteredOffice" = "@triggerBody()?['registeredOffice']"
        "item/HeadOffice" = "@triggerBody()?['headOffice']"
        "item/ParentCompany" = "@triggerBody()?['parentCompany']"
        "item/YearsTrading" = "@triggerBody()?['yearsTrading']"
        "item/Specialisations" = "@triggerBody()?['specializations']"
        "item/SoftwareUsed" = "@triggerBody()?['softwareTools']"
        "item/ProjectsPerMonth" = "@triggerBody()?['projectsPerMonth']"
        "item/TeamSize" = "@triggerBody()?['teamSize']"
        "item/YearsExperience" = "@triggerBody()?['yearsExperience']"
        "item/Services" = "@triggerBody()?['services']"
        "item/Coverage" = "@triggerBody()?['coverage']"
        "item/Accreditations" = "@triggerBody()?['accreditations']"
        "item/Certifications" = "@triggerBody()?['certifications']"
        "item/ISOStandards" = "@triggerBody()?['isoStandards']"
        "item/AdditionalInfo" = "@triggerBody()?['additionalInfo']"
        "item/Notes" = "@triggerBody()?['notes']"
        "item/InvitationCode" = "@triggerBody()?['invitationCode']"
        "item/ReferenceNumber" = "@concat('EPC-', utcNow('yyyyMMddHHmmss'))"
        "item/SubmissionStatus" = "Submitted"
        "item/SubmissionDate" = "@utcNow()"
        
        # Simple boolean as text - no if statements
        "item/ActsAsPrincipalContractor" = "@triggerBody()?['principalContractor']"
        "item/ActsAsPrincipalDesigner" = "@triggerBody()?['principalDesigner']"
        "item/NICEIC_CPS" = "@triggerBody()?['niceicContractor']"
        "item/MCS_Approved" = "@triggerBody()?['mcsApproved']"
        "item/PublicProductLiability_Present" = "@triggerBody()?['publicLiabilityInsurance']"
        "item/EmployersLiability_Present" = "@triggerBody()?['employersLiabilityInsurance']"
        "item/ProfIndemnity_Present" = "@triggerBody()?['professionalIndemnityInsurance']"
        "item/DataProcessingConsent" = "@triggerBody()?['dataProcessingConsent']"
        "item/MarketingConsent" = "@triggerBody()?['marketingConsent']"
        "item/AgreeToCodes" = "@triggerBody()?['agreeToCodes']"
        "item/Coverage_Nationwide" = "@triggerBody()?['nationwideCoverage']"
        "item/Contracts_ReviewedBySignatory" = "@triggerBody()?['contractsReviewed']"
        "item/Received_ContractOverviewPack" = "@triggerBody()?['receivedContractPack']"
        "item/Willing_To_WorkToSaberTerms" = "@triggerBody()?['agreeToTerms']"
        "item/SubmissionHandled" = false
    }
    
    Write-Host "✅ Set flat field references" -ForegroundColor Green
} else {
    Write-Host "❌ Could not find Create_item action" -ForegroundColor Red
    exit 1
}

# Save updated definition
$definition | ConvertTo-Json -Depth 50 | Set-Content $definitionPath -Encoding UTF8
Write-Host "✅ Updated definition saved" -ForegroundColor Green

# Create package
Write-Host "Creating package..." -ForegroundColor Yellow
$zipPath = "$OutputPath.zip"
if (Test-Path $zipPath) { Remove-Item $zipPath }
Compress-Archive -Path "$OutputPath/*" -DestinationPath $zipPath
Write-Host "✅ Package created: $zipPath" -ForegroundColor Green

Write-Host "`n=======================================" -ForegroundColor Cyan
Write-Host "✅ Flat Fields Flow Ready!" -ForegroundColor Green
Write-Host "=======================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "COMPLETELY FLAT EXPRESSIONS:" -ForegroundColor Yellow
Write-Host "• No coalesce() functions" -ForegroundColor White
Write-Host "• No nested object references" -ForegroundColor White
Write-Host "• No if() statements" -ForegroundColor White
Write-Host "• Simple @triggerBody()?['field'] only" -ForegroundColor White
Write-Host ""
Write-Host "Package: $zipPath" -ForegroundColor Green
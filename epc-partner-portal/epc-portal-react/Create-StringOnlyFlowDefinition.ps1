#!/usr/bin/pwsh
<#
.SYNOPSIS
    Creates flow definition with ALL fields using only string expressions - no booleans, no coalesce
.DESCRIPTION
    Simple string values only to avoid validation errors
#>

param(
    [string]$InputPath = "./power-automate-export",
    [string]$OutputPath = "./power-automate-export-strings-only"
)

Write-Host "Creating string-only flow definition..." -ForegroundColor Yellow

# Copy original structure
if (Test-Path $OutputPath) { Remove-Item $OutputPath -Recurse -Force }
Copy-Item $InputPath $OutputPath -Recurse -Force

# Load the flow definition
$definitionPath = "$OutputPath/Microsoft.Flow/flows/45991de2-99f2-422e-864f-efdf8db8cb93/definition.json"
$definition = Get-Content $definitionPath -Raw | ConvertFrom-Json

Write-Host "Adding ALL fields with string-only expressions..." -ForegroundColor Yellow

# ALL FIELDS - string expressions only, no booleans, no coalesce
$stringFields = @{
    "item/CompanyName" = "@triggerBody()?['companyName']"
    "item/TradingName" = "@triggerBody()?['tradingName']"
    "item/RegisteredOffice" = "@triggerBody()?['registeredOffice']"
    "item/HeadOffice" = "@triggerBody()?['headOffice']"
    "item/CompanyRegNo" = "@triggerBody()?['companyRegNo']"
    "item/VATNumber" = "@triggerBody()?['vatNumber']"
    "item/VATNo" = "@triggerBody()?['vatNumber']"
    "item/ParentCompany" = "@triggerBody()?['parentCompany']"
    "item/YearsTrading" = "@triggerBody()?['yearsTrading']"
    "item/Address" = "@triggerBody()?['address']"
    "item/PrimaryContactName" = "@triggerBody()?['contactName']"
    "item/PrimaryContactTitle" = "@triggerBody()?['contactTitle']"
    "item/PrimaryContactPhone" = "@triggerBody()?['phone']"
    "item/PrimaryContactEmail" = "@triggerBody()?['email']"
    "item/ContactName" = "@triggerBody()?['contactName']"
    "item/Email" = "@triggerBody()?['email']"
    "item/Phone" = "@triggerBody()?['phone']"
    "item/Specialisations" = "@triggerBody()?['specializations']"
    "item/SoftwareUsed" = "@triggerBody()?['softwareTools']"
    "item/ProjectsPerMonth" = "@triggerBody()?['projectsPerMonth']"
    "item/Services" = "@triggerBody()?['services']"
    "item/TeamSize" = "@triggerBody()?['teamSize']"
    "item/YearsExperience" = "@triggerBody()?['yearsExperience']"
    "item/PrincipalContractor_LastYearScal0" = "@triggerBody()?['principalContractorScale']"
    "item/PrincipalDesigner_LastYearScale" = "@triggerBody()?['principalDesignerScale']"
    "item/LabourMix_InternalPct" = "@triggerBody()?['internalStaffPercentage']"
    "item/LabourMix_SubcontractPct" = "@triggerBody()?['subcontractPercentage']"
    "item/Accreditations" = "@triggerBody()?['accreditations']"
    "item/Certifications" = "@triggerBody()?['certificationDetails']"
    "item/ISOStandards" = "@triggerBody()?['isoStandards']"
    "item/PublicProductLiability_Expiry" = "@triggerBody()?['publicLiabilityExpiry']"
    "item/EmployersLiability_Expiry" = "@triggerBody()?['employersLiabilityExpiry']"
    "item/ProfIndemnity_Expiry" = "@triggerBody()?['professionalIndemnityExpiry']"
    "item/HSE_ImprovementOrProhibition_Las0" = "@triggerBody()?['hseNoticesLast5Years']"
    "item/RIDDOR_Incidents_Last3Y_Count" = "@triggerBody()?['riddorIncidentCount']"
    "item/RIDDOR_Incidents_Last3Y_Details" = "@triggerBody()?['riddorIncidentDetails']"
    "item/HSE_CDM_Management_Evidence" = "@triggerBody()?['cdmManagementEvidence']"
    "item/Named_PrincipalDesigner" = "@triggerBody()?['namedPrincipalDesigner']"
    "item/PD_Qualifications" = "@triggerBody()?['principalDesignerQualifications']"
    "item/TrainingRecords_Summary" = "@triggerBody()?['trainingRecordsSummary']"
    "item/NearMiss_Procedure" = "@triggerBody()?['nearMissProcedure']"
    "item/Quality_Procedure_Evidence" = "@triggerBody()?['qualityProcedureEvidence']"
    "item/HSEQIncidentsLast5y" = "@triggerBody()?['hseqIncidents']"
    "item/RIDDORLast3y" = "@triggerBody()?['riddorIncidents']"
    "item/Policy_HS_DateSigned" = "@triggerBody()?['healthSafetyPolicyDate']"
    "item/Policy_Env_DateSigned" = "@triggerBody()?['environmentalPolicyDate']"
    "item/Policy_MS_DateSigned" = "@triggerBody()?['modernSlaveryPolicyDate']"
    "item/Policy_MOS_DateSigned" = "@triggerBody()?['substanceMisusePolicyDate']"
    "item/RightToWork_Monitoring_Method" = "@triggerBody()?['rightToWorkMethod']"
    "item/GDPRPolicy_DateSigned" = "@triggerBody()?['gdprPolicyDate']"
    "item/CyberIncident_Last3Y" = "@triggerBody()?['cyberIncidentLast3Years']"
    "item/Resources_PerProject" = "@triggerBody()?['resourcesPerProject']"
    "item/Client_Reference" = "@triggerBody()?['clientReference']"
    "item/Coverage" = "@triggerBody()?['coverage']"
    "item/CoverageRegion" = "@triggerBody()?['coverageRegion']"
    "item/PendingProsecutions_Details" = "@triggerBody()?['pendingProsecutions']"
    "item/Legal_Clarifications" = "@triggerBody()?['legalClarifications']"
    "item/AdditionalInfo" = "@triggerBody()?['additionalInformation']"
    "item/Notes" = "@triggerBody()?['notes']"
    "item/NotesOrClarifications" = "@triggerBody()?['clarifications']"
    "item/SubmissionStatus" = "Submitted"
    "item/ReferenceNumber" = "@concat('EPC-', utcNow('yyyyMMddHHmmss'))"
    "item/RegistrationNumber" = "@concat('EPC-', utcNow('yyyyMMddHHmmss'))"
    "item/InvitationCode" = "@triggerBody()?['invitationCode']"
    "item/SubmissionDate" = "@utcNow()"
    "item/ReviewDate" = "@utcNow()"
    
    # Boolean fields as strings to avoid validation issues
    "item/ActsAsPrincipalContractor" = "@if(equals(triggerBody()?['principalContractor'], true), 'Yes', 'No')"
    "item/ActsAsPrincipalDesigner" = "@if(equals(triggerBody()?['principalDesigner'], true), 'Yes', 'No')"
    "item/NICEIC_CPS" = "@if(equals(triggerBody()?['niceicContractor'], true), 'Yes', 'No')"
    "item/MCS_Approved" = "@if(equals(triggerBody()?['mcsApproved'], true), 'Yes', 'No')"
    "item/PublicProductLiability_Present" = "@if(equals(triggerBody()?['publicLiabilityInsurance'], true), 'Yes', 'No')"
    "item/PublicProductLiability_Indemnity0" = "@if(equals(triggerBody()?['publicLiabilityIndemnity'], true), 'Yes', 'No')"
    "item/EmployersLiability_Present" = "@if(equals(triggerBody()?['employersLiabilityInsurance'], true), 'Yes', 'No')"
    "item/ProfIndemnity_Present" = "@if(equals(triggerBody()?['professionalIndemnityInsurance'], true), 'Yes', 'No')"
    "item/Coverage_Nationwide" = "@if(equals(triggerBody()?['nationwideCoverage'], true), 'Yes', 'No')"
    "item/Contracts_ReviewedBySignatory" = "@if(equals(triggerBody()?['contractsReviewed'], true), 'Yes', 'No')"
    "item/Received_ContractOverviewPack" = "@if(equals(triggerBody()?['receivedContractPack'], true), 'Yes', 'No')"
    "item/Willing_To_WorkToSaberTerms" = "@if(equals(triggerBody()?['agreeToTerms'], true), 'Yes', 'No')"
    "item/AgreeToCodes" = "@if(equals(triggerBody()?['agreeToCodes'], true), 'Yes', 'No')"
    "item/DataProcessingConsent" = "@if(equals(triggerBody()?['dataProcessingConsent'], true), 'Yes', 'No')"
    "item/MarketingConsent" = "@if(equals(triggerBody()?['marketingConsent'], true), 'Yes', 'No')"
    "item/AgreeToSaberTerms" = "@if(equals(triggerBody()?['agreeToTerms'], true), 'Yes', 'No')"
    "item/HasGDPRPolicy" = "@if(equals(triggerBody()?['hasGdprPolicy'], true), 'Yes', 'No')"
    "item/SubmissionHandled" = "false"
}

# Find the Create_item action and add string fields
$createItemAction = $definition.properties.definition.actions.Create_item
if ($createItemAction -and $createItemAction.inputs -and $createItemAction.inputs.parameters) {
    
    # Clear existing parameters
    $createItemAction.inputs.parameters = @{}
    
    # Add each string field mapping
    foreach ($field in $stringFields.GetEnumerator()) {
        $fieldName = $field.Key
        $fieldExpression = $field.Value
        $createItemAction.inputs.parameters | Add-Member -NotePropertyName $fieldName -NotePropertyValue $fieldExpression -Force
    }
    
    Write-Host "✅ Added $($stringFields.Count) string-only field mappings" -ForegroundColor Green
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
Write-Host "✅ String-Only Flow Ready!" -ForegroundColor Green
Write-Host "=======================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "SIMPLE STRING EXPRESSIONS ONLY:" -ForegroundColor Yellow
Write-Host "• $($stringFields.Count) fields using basic triggerBody() references" -ForegroundColor White
Write-Host "• No coalesce() functions" -ForegroundColor White
Write-Host "• No nested object references" -ForegroundColor White
Write-Host "• Boolean fields converted to Yes/No strings" -ForegroundColor White
Write-Host ""
Write-Host "Package ready for import: $zipPath" -ForegroundColor Green
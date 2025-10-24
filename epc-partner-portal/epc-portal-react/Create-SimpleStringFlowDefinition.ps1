#!/usr/bin/pwsh
<#
.SYNOPSIS
    Creates flow definition with ALL fields using simple string values - no complex syntax
.DESCRIPTION
    Uses simple string expressions for ALL field types - no objects, no fancy formatting
#>

param(
    [string]$InputPath = "./power-automate-export",
    [string]$OutputPath = "./power-automate-export-simple-strings"
)

Write-Host "Creating SIMPLE STRING flow definition with ALL fields..." -ForegroundColor Yellow

# Copy original structure
if (Test-Path $OutputPath) { Remove-Item $OutputPath -Recurse -Force }
Copy-Item $InputPath $OutputPath -Recurse -Force

# Load the flow definition
$definitionPath = "$OutputPath/Microsoft.Flow/flows/45991de2-99f2-422e-864f-efdf8db8cb93/definition.json"
$definition = Get-Content $definitionPath -Raw | ConvertFrom-Json

Write-Host "Adding ALL field mappings with simple string values..." -ForegroundColor Yellow

# ALL FIELDS - using simple string expressions only
$allSimpleFields = @{
    # Core company fields
    "item/CompanyName" = "@coalesce(triggerBody()?['companyInfo']?['companyName'], triggerBody()?['companyName'])"
    "item/TradingName" = "@triggerBody()?['companyInfo']?['tradingName']"
    "item/RegisteredOffice" = "@triggerBody()?['companyInfo']?['registeredOffice']"
    "item/HeadOffice" = "@triggerBody()?['companyInfo']?['headOffice']"
    "item/CompanyRegNo" = "@triggerBody()?['companyInfo']?['companyRegNo']"
    "item/VATNumber" = "@triggerBody()?['companyInfo']?['vatNumber']"
    "item/VATNo" = "@triggerBody()?['companyInfo']?['vatNumber']"
    "item/ParentCompany" = "@triggerBody()?['companyInfo']?['parentCompany']"
    "item/YearsTrading" = "@triggerBody()?['companyInfo']?['yearsTrading']"
    "item/Address" = "@triggerBody()?['companyInfo']?['address']"
    
    # Contact fields
    "item/PrimaryContactName" = "@coalesce(triggerBody()?['primaryContact']?['fullName'], triggerBody()?['contactName'])"
    "item/PrimaryContactTitle" = "@coalesce(triggerBody()?['primaryContact']?['jobTitle'], triggerBody()?['contactTitle'])"
    "item/PrimaryContactPhone" = "@coalesce(triggerBody()?['primaryContact']?['phone'], triggerBody()?['phone'])"
    "item/PrimaryContactEmail" = "@coalesce(triggerBody()?['primaryContact']?['email'], triggerBody()?['email'])"
    "item/ContactName" = "@coalesce(triggerBody()?['primaryContact']?['fullName'], triggerBody()?['contactName'])"
    "item/Email" = "@coalesce(triggerBody()?['primaryContact']?['email'], triggerBody()?['email'])"
    "item/Phone" = "@coalesce(triggerBody()?['primaryContact']?['phone'], triggerBody()?['phone'])"
    
    # Services
    "item/Specialisations" = "@triggerBody()?['servicesExperience']?['specializations']"
    "item/SoftwareUsed" = "@triggerBody()?['servicesExperience']?['softwareTools']"
    "item/ProjectsPerMonth" = "@triggerBody()?['servicesExperience']?['averageProjectsPerMonth']"
    "item/Services" = "@triggerBody()?['servicesExperience']?['services']"
    "item/TeamSize" = "@triggerBody()?['companyInfo']?['teamSize']"
    "item/YearsExperience" = "@triggerBody()?['companyInfo']?['yearsExperience']"
    
    # Roles - Choice fields as simple strings
    "item/ActsAsPrincipalContractor" = "@if(equals(triggerBody()?['rolesCapabilities']?['principalContractor'], true), 'Yes', 'No')"
    "item/ActsAsPrincipalDesigner" = "@if(equals(triggerBody()?['rolesCapabilities']?['principalDesigner'], true), 'Yes', 'No')"
    "item/PrincipalContractor_LastYearScal0" = "@triggerBody()?['rolesCapabilities']?['principalContractorScale']"
    "item/PrincipalDesigner_LastYearScale" = "@triggerBody()?['rolesCapabilities']?['principalDesignerScale']"
    
    # Labour mix
    "item/LabourMix_InternalPct" = "@triggerBody()?['labourMix']?['internalStaffPercentage']"
    "item/LabourMix_SubcontractPct" = "@triggerBody()?['labourMix']?['subcontractPercentage']"
    
    # Certifications - Boolean as string
    "item/NICEIC_CPS" = "@coalesce(triggerBody()?['certifications']?['niceicContractor'], false)"
    "item/MCS_Approved" = "@coalesce(triggerBody()?['certifications']?['mcsApproved'], false)"
    "item/Accreditations" = "@triggerBody()?['certifications']?['accreditations']"
    "item/Certifications" = "@triggerBody()?['certifications']?['certificationDetails']"
    "item/ISOStandards" = "@triggerBody()?['certifications']?['isoStandards']"
    
    # Insurance
    "item/PublicProductLiability_Present" = "@coalesce(triggerBody()?['insurance']?['publicLiabilityInsurance'], false)"
    "item/PublicProductLiability_Indemnity0" = "@coalesce(triggerBody()?['insurance']?['publicLiabilityIndemnity'], false)"
    "item/EmployersLiability_Present" = "@coalesce(triggerBody()?['insurance']?['employersLiabilityInsurance'], false)"
    "item/ProfIndemnity_Present" = "@coalesce(triggerBody()?['insurance']?['professionalIndemnityInsurance'], false)"
    "item/PublicProductLiability_Expiry" = "@triggerBody()?['insurance']?['publicLiabilityExpiry']"
    "item/EmployersLiability_Expiry" = "@triggerBody()?['insurance']?['employersLiabilityExpiry']"
    "item/ProfIndemnity_Expiry" = "@triggerBody()?['insurance']?['professionalIndemnityExpiry']"
    
    # Health & Safety
    "item/HSE_ImprovementOrProhibition_Las0" = "@triggerBody()?['healthSafety']?['hseNoticesLast5Years']"
    "item/RIDDOR_Incidents_Last3Y_Count" = "@triggerBody()?['healthSafety']?['riddorIncidentCount']"
    "item/RIDDOR_Incidents_Last3Y_Details" = "@triggerBody()?['healthSafety']?['riddorIncidentDetails']"
    "item/HSE_CDM_Management_Evidence" = "@triggerBody()?['healthSafety']?['cdmManagementEvidence']"
    "item/Named_PrincipalDesigner" = "@triggerBody()?['healthSafety']?['namedPrincipalDesigner']"
    "item/PD_Qualifications" = "@triggerBody()?['healthSafety']?['principalDesignerQualifications']"
    "item/TrainingRecords_Summary" = "@triggerBody()?['healthSafety']?['trainingRecordsSummary']"
    "item/NearMiss_Procedure" = "@triggerBody()?['healthSafety']?['nearMissProcedure']"
    "item/Quality_Procedure_Evidence" = "@triggerBody()?['qualityAssurance']?['qualityProcedureEvidence']"
    "item/HSEQIncidentsLast5y" = "@triggerBody()?['healthSafety']?['hseqIncidents']"
    "item/RIDDORLast3y" = "@triggerBody()?['healthSafety']?['riddorIncidents']"
    
    # Policies
    "item/Policy_HS_DateSigned" = "@triggerBody()?['policies']?['healthSafetyPolicyDate']"
    "item/Policy_Env_DateSigned" = "@triggerBody()?['policies']?['environmentalPolicyDate']"
    "item/Policy_MS_DateSigned" = "@triggerBody()?['policies']?['modernSlaveryPolicyDate']"
    "item/Policy_MOS_DateSigned" = "@triggerBody()?['policies']?['substanceMisusePolicyDate']"
    "item/RightToWork_Monitoring_Method" = "@triggerBody()?['policies']?['rightToWorkMethod']"
    "item/GDPRPolicy_DateSigned" = "@triggerBody()?['policies']?['gdprPolicyDate']"
    "item/CyberIncident_Last3Y" = "@triggerBody()?['policies']?['cyberIncidentLast3Years']"
    "item/HasGDPRPolicy" = "@if(equals(triggerBody()?['policies']?['hasGdprPolicy'], true), 'Yes', 'No')"
    
    # Project references
    "item/Resources_PerProject" = "@triggerBody()?['projectReferences']?['resourcesPerProject']"
    "item/Coverage_Nationwide" = "@coalesce(triggerBody()?['projectReferences']?['nationwideCoverage'], false)"
    "item/Client_Reference" = "@triggerBody()?['projectReferences']?['clientReference']"
    "item/Coverage" = "@triggerBody()?['projectReferences']?['coverage']"
    "item/CoverageRegion" = "@triggerBody()?['projectReferences']?['coverageRegion']"
    
    # Legal compliance
    "item/PendingProsecutions_Details" = "@triggerBody()?['legalCompliance']?['pendingProsecutions']"
    "item/Contracts_ReviewedBySignatory" = "@coalesce(triggerBody()?['legalCompliance']?['contractsReviewed'], false)"
    "item/Legal_Clarifications" = "@triggerBody()?['legalCompliance']?['legalClarifications']"
    
    # Agreement fields
    "item/Received_ContractOverviewPack" = "@coalesce(triggerBody()?['agreement']?['receivedContractPack'], false)"
    "item/Willing_To_WorkToSaberTerms" = "@coalesce(triggerBody()?['agreement']?['agreeToTerms'], false)"
    "item/AgreeToCodes" = "@coalesce(triggerBody()?['agreement']?['agreeToCodes'], false)"
    "item/DataProcessingConsent" = "@coalesce(triggerBody()?['agreement']?['dataProcessingConsent'], false)"
    "item/MarketingConsent" = "@coalesce(triggerBody()?['agreement']?['marketingConsent'], false)"
    "item/AgreeToSaberTerms" = "@if(equals(triggerBody()?['agreement']?['agreeToTerms'], true), 'Yes', 'No')"
    
    # Submission fields
    "item/AdditionalInfo" = "@triggerBody()?['submission']?['additionalInformation']"
    "item/Notes" = "@triggerBody()?['submission']?['notes']"
    "item/NotesOrClarifications" = "@triggerBody()?['submission']?['clarifications']"
    "item/SubmissionStatus" = "Submitted"
    "item/Status" = "Submitted"
    "item/ReferenceNumber" = "@coalesce(triggerBody()?['referenceNumber'], concat('EPC-', utcNow('yyyyMMddHHmmss')))"
    "item/RegistrationNumber" = "@coalesce(triggerBody()?['referenceNumber'], concat('EPC-', utcNow('yyyyMMddHHmmss')))"
    "item/InvitationCode" = "@triggerBody()?['invitationCode']"
    "item/SubmissionDate" = "@utcNow()"
    "item/ReviewDate" = "@utcNow()"
    "item/SubmissionHandled" = "false"
}

# Find the Create_item action and add ALL simple fields
$createItemAction = $definition.properties.definition.actions.Condition.actions.Create_item
if ($createItemAction -and $createItemAction.inputs -and $createItemAction.inputs.parameters) {
    
    # Add each simple field mapping
    foreach ($field in $allSimpleFields.GetEnumerator()) {
        $fieldName = $field.Key
        $fieldExpression = $field.Value
        $createItemAction.inputs.parameters | Add-Member -NotePropertyName $fieldName -NotePropertyValue $fieldExpression -Force
    }
    
    Write-Host "✅ Added $($allSimpleFields.Count) ALL FIELDS with simple string expressions" -ForegroundColor Green
} else {
    Write-Host "❌ Could not find Create_item action" -ForegroundColor Red
    exit 1
}

# Update email notifications
Write-Host "Updating email notifications..." -ForegroundColor Yellow

# Update internal email
$internalEmail = $definition.properties.definition.actions.Condition.actions.'Send_an_email_(V2)'
if ($internalEmail) {
    $internalEmail.inputs.parameters.'emailMessage/Subject' = "New EPC Application - @{coalesce(triggerBody()?['companyInfo']?['companyName'], triggerBody()?['companyName'])}"
    
    $emailBody = @"
<h2>New EPC Application Received</h2>
<table border="1" style="border-collapse: collapse; width: 100%;">
<tbody>
<tr><td><strong>Company</strong></td><td>@{coalesce(triggerBody()?['companyInfo']?['companyName'], triggerBody()?['companyName'])}</td></tr>
<tr><td><strong>Trading Name</strong></td><td>@{triggerBody()?['companyInfo']?['tradingName']}</td></tr>
<tr><td><strong>Company Reg No</strong></td><td>@{triggerBody()?['companyInfo']?['companyRegNo']}</td></tr>
<tr><td><strong>VAT Number</strong></td><td>@{triggerBody()?['companyInfo']?['vatNumber']}</td></tr>
<tr><td><strong>Contact</strong></td><td>@{coalesce(triggerBody()?['primaryContact']?['fullName'], triggerBody()?['contactName'])}</td></tr>
<tr><td><strong>Email</strong></td><td>@{coalesce(triggerBody()?['primaryContact']?['email'], triggerBody()?['email'])}</td></tr>
<tr><td><strong>Phone</strong></td><td>@{coalesce(triggerBody()?['primaryContact']?['phone'], triggerBody()?['phone'])}</td></tr>
<tr><td><strong>SharePoint ID</strong></td><td>@{body('Create_item')?['ID']}</td></tr>
<tr><td><strong>Code Used</strong></td><td>@{triggerBody()?['invitationCode']}</td></tr>
</tbody>
</table>

<h3>Extended Data</h3>
<ul>
<li><strong>Principal Contractor:</strong> @{if(equals(triggerBody()?['rolesCapabilities']?['principalContractor'], true), 'Yes', 'No')}</li>
<li><strong>Principal Designer:</strong> @{if(equals(triggerBody()?['rolesCapabilities']?['principalDesigner'], true), 'Yes', 'No')}</li>
<li><strong>NICEIC CPS:</strong> @{if(coalesce(triggerBody()?['certifications']?['niceicContractor'], false), 'Yes', 'No')}</li>
<li><strong>MCS Approved:</strong> @{if(coalesce(triggerBody()?['certifications']?['mcsApproved'], false), 'Yes', 'No')}</li>
<li><strong>GDPR Consent:</strong> @{if(coalesce(triggerBody()?['agreement']?['dataProcessingConsent'], false), 'Yes', 'No')}</li>
</ul>

<p><a href="https://saberrenewables.sharepoint.com/sites/SaberEPCPartners/Lists/EPC%20Onboarding">View in SharePoint</a></p>
"@
    
    $internalEmail.inputs.parameters.'emailMessage/Body' = $emailBody
}

# Update confirmation email
$confirmationEmail = $definition.properties.definition.actions.Condition.actions.'Send_an_email_(V2)_1'
if ($confirmationEmail) {
    $confirmationEmail.inputs.parameters.'emailMessage/Subject' = "Application Received - @{coalesce(triggerBody()?['companyInfo']?['companyName'], triggerBody()?['companyName'])}"
}

Write-Host "✅ Updated email notifications" -ForegroundColor Green

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
Write-Host "✅ ALL FIELDS Simple String Flow Ready!" -ForegroundColor Green
Write-Host "=======================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "SIMPLE APPROACH - NO COMPLEX SYNTAX:" -ForegroundColor Yellow
Write-Host "• $($allSimpleFields.Count) field mappings using simple expressions" -ForegroundColor White
Write-Host "• Choice fields: simple if() expressions" -ForegroundColor White
Write-Host "• Boolean fields: coalesce() with false default" -ForegroundColor White
Write-Host "• Text fields: direct triggerBody() references" -ForegroundColor White
Write-Host "• No object syntax, no Value properties" -ForegroundColor White
Write-Host ""
Write-Host "Package ready for import: $zipPath" -ForegroundColor Green
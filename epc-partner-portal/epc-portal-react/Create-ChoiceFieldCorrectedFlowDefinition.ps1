#!/usr/bin/pwsh
<#
.SYNOPSIS
    Creates flow definition with proper Choice field formatting for SharePoint
.DESCRIPTION
    Fixes Choice field validation by using proper object format instead of strings
#>

param(
    [string]$InputPath = "./power-automate-export",
    [string]$OutputPath = "./power-automate-export-choice-fixed"
)

Write-Host "Creating CHOICE-FIELD-FIXED flow definition..." -ForegroundColor Yellow

# Copy original structure
if (Test-Path $OutputPath) { Remove-Item $OutputPath -Recurse -Force }
Copy-Item $InputPath $OutputPath -Recurse -Force

# Load the flow definition
$definitionPath = "$OutputPath/Microsoft.Flow/flows/45991de2-99f2-422e-864f-efdf8db8cb93/definition.json"
$definition = Get-Content $definitionPath -Raw | ConvertFrom-Json

Write-Host "Adding CHOICE-FIELD-CORRECTED mappings..." -ForegroundColor Yellow

# CHOICE-FIELD-CORRECTED mappings - proper Choice field formatting
$choiceFixedFields = @{
    # Text fields - these work fine as strings
    "item/CompanyName" = "@coalesce(triggerBody()?['companyInfo']?['companyName'], triggerBody()?['companyName'])"
    "item/TradingName" = "@triggerBody()?['companyInfo']?['tradingName']"
    "item/RegisteredOffice" = "@triggerBody()?['companyInfo']?['registeredOffice']"
    "item/CompanyRegNo" = "@triggerBody()?['companyInfo']?['companyRegNo']"
    "item/VATNo" = "@triggerBody()?['companyInfo']?['vatNumber']"
    "item/VATNumber" = "@triggerBody()?['companyInfo']?['vatNumber']"
    "item/ParentCompany" = "@triggerBody()?['companyInfo']?['parentCompany']"
    "item/HeadOffice" = "@triggerBody()?['companyInfo']?['headOffice']"
    "item/Address" = "@triggerBody()?['companyInfo']?['address']"
    "item/ContactName" = "@coalesce(triggerBody()?['primaryContact']?['fullName'], triggerBody()?['contactName'])"
    "item/Email" = "@coalesce(triggerBody()?['primaryContact']?['email'], triggerBody()?['email'])"
    "item/Phone" = "@coalesce(triggerBody()?['primaryContact']?['phone'], triggerBody()?['phone'])"
    "item/PrimaryContactName" = "@coalesce(triggerBody()?['primaryContact']?['fullName'], triggerBody()?['contactName'])"
    "item/PrimaryContactTitle" = "@coalesce(triggerBody()?['primaryContact']?['jobTitle'], triggerBody()?['contactTitle'])"
    "item/PrimaryContactPhone" = "@coalesce(triggerBody()?['primaryContact']?['phone'], triggerBody()?['phone'])"
    "item/PrimaryContactEmail" = "@coalesce(triggerBody()?['primaryContact']?['email'], triggerBody()?['email'])"
    "item/InvitationCode" = "@triggerBody()?['invitationCode']"
    "item/ReferenceNumber" = "@coalesce(triggerBody()?['referenceNumber'], concat('EPC-', utcNow('yyyyMMddHHmmss')))"
    "item/RegistrationNumber" = "@coalesce(triggerBody()?['referenceNumber'], concat('EPC-', utcNow('yyyyMMddHHmmss')))"
    "item/SubmissionStatus" = "Submitted"
    "item/Named_PrincipalDesigner" = "@triggerBody()?['healthSafety']?['namedPrincipalDesigner']"
    "item/NearMiss_Procedure" = "@triggerBody()?['healthSafety']?['nearMissProcedure']"
    "item/CyberIncident_Last3Y" = "@triggerBody()?['policies']?['cyberIncidentLast3Years']"
    
    # Number fields - these work as numbers
    "item/YearsTrading" = "@coalesce(triggerBody()?['companyInfo']?['yearsTrading'], 0)"
    "item/TeamSize" = "@coalesce(triggerBody()?['companyInfo']?['teamSize'], 0)"
    "item/YearsExperience" = "@coalesce(triggerBody()?['companyInfo']?['yearsExperience'], 0)"
    "item/ProjectsPerMonth" = "@coalesce(triggerBody()?['servicesExperience']?['averageProjectsPerMonth'], 0)"
    "item/LabourMix_InternalPct" = "@coalesce(triggerBody()?['labourMix']?['internalStaffPercentage'], 0)"
    "item/LabourMix_SubcontractPct" = "@coalesce(triggerBody()?['labourMix']?['subcontractPercentage'], 0)"
    "item/HSEQIncidentsLast5y" = "@coalesce(triggerBody()?['healthSafety']?['hseqIncidents'], 0)"
    "item/RIDDORLast3y" = "@coalesce(triggerBody()?['healthSafety']?['riddorIncidents'], 0)"
    "item/RIDDOR_Incidents_Last3Y_Count" = "@coalesce(triggerBody()?['healthSafety']?['riddorIncidentCount'], 0)"
    
    # Boolean fields - these work as booleans
    "item/SubmissionHandled" = "false"
    "item/AgreeToCodes" = "@coalesce(triggerBody()?['agreement']?['agreeToCodes'], false)"
    "item/DataProcessingConsent" = "@coalesce(triggerBody()?['agreement']?['dataProcessingConsent'], false)"
    "item/MarketingConsent" = "@coalesce(triggerBody()?['agreement']?['marketingConsent'], false)"
    "item/Contracts_ReviewedBySignatory" = "@coalesce(triggerBody()?['legalCompliance']?['contractsReviewed'], false)"
    "item/Coverage_Nationwide" = "@coalesce(triggerBody()?['projectReferences']?['nationwideCoverage'], false)"
    "item/EmployersLiability_Present" = "@coalesce(triggerBody()?['insurance']?['employersLiabilityInsurance'], false)"
    "item/ProfIndemnity_Present" = "@coalesce(triggerBody()?['insurance']?['professionalIndemnityInsurance'], false)"
    "item/PublicProductLiability_Present" = "@coalesce(triggerBody()?['insurance']?['publicLiabilityInsurance'], false)"
    "item/PublicProductLiability_Indemnity0" = "@coalesce(triggerBody()?['insurance']?['publicLiabilityIndemnity'], false)"
    "item/MCS_Approved" = "@coalesce(triggerBody()?['certifications']?['mcsApproved'], false)"
    "item/NICEIC_CPS" = "@coalesce(triggerBody()?['certifications']?['niceicContractor'], false)"
    "item/Received_ContractOverviewPack" = "@coalesce(triggerBody()?['agreement']?['receivedContractPack'], false)"
    "item/Willing_To_WorkToSaberTerms" = "@coalesce(triggerBody()?['agreement']?['agreeToTerms'], false)"
    
    # DateTime fields - these work as ISO strings
    "item/SubmissionDate" = "@utcNow()"
    "item/ReviewDate" = "@utcNow()"
    "item/EmployersLiability_Expiry" = "@triggerBody()?['insurance']?['employersLiabilityExpiry']"
    "item/ProfIndemnity_Expiry" = "@triggerBody()?['insurance']?['professionalIndemnityExpiry']"
    "item/PublicProductLiability_Expiry" = "@triggerBody()?['insurance']?['publicLiabilityExpiry']"
    "item/GDPRPolicy_DateSigned" = "@triggerBody()?['policies']?['gdprPolicyDate']"
    "item/Policy_Env_DateSigned" = "@triggerBody()?['policies']?['environmentalPolicyDate']"
    "item/Policy_HS_DateSigned" = "@triggerBody()?['policies']?['healthSafetyPolicyDate']"
    "item/Policy_MOS_DateSigned" = "@triggerBody()?['policies']?['substanceMisusePolicyDate']"
    "item/Policy_MS_DateSigned" = "@triggerBody()?['policies']?['modernSlaveryPolicyDate']"
    
    # Note fields - these work as strings
    "item/Notes" = "@triggerBody()?['submission']?['notes']"
    "item/NotesOrClarifications" = "@triggerBody()?['submission']?['clarifications']"
    "item/AdditionalInfo" = "@triggerBody()?['submission']?['additionalInformation']"
    "item/Services" = "@triggerBody()?['servicesExperience']?['services']"
    "item/Coverage" = "@triggerBody()?['projectReferences']?['coverage']"
    "item/Certifications" = "@triggerBody()?['certifications']?['certificationDetails']"
    "item/Client_Reference" = "@triggerBody()?['projectReferences']?['clientReference']"
    "item/HSE_CDM_Management_Evidence" = "@triggerBody()?['healthSafety']?['cdmManagementEvidence']"
    "item/HSE_ImprovementOrProhibition_Las0" = "@triggerBody()?['healthSafety']?['hseNoticesLast5Years']"
    "item/Legal_Clarifications" = "@triggerBody()?['legalCompliance']?['legalClarifications']"
    "item/PD_Qualifications" = "@triggerBody()?['healthSafety']?['principalDesignerQualifications']"
    "item/PendingProsecutions_Details" = "@triggerBody()?['legalCompliance']?['pendingProsecutions']"
    "item/PrincipalContractor_LastYearScal0" = "@triggerBody()?['rolesCapabilities']?['principalContractorScale']"
    "item/PrincipalDesigner_LastYearScale" = "@triggerBody()?['rolesCapabilities']?['principalDesignerScale']"
    "item/Quality_Procedure_Evidence" = "@triggerBody()?['qualityAssurance']?['qualityProcedureEvidence']"
    "item/Resources_PerProject" = "@triggerBody()?['projectReferences']?['resourcesPerProject']"
    "item/RIDDOR_Incidents_Last3Y_Details" = "@triggerBody()?['healthSafety']?['riddorIncidentDetails']"
    "item/RightToWork_Monitoring_Method" = "@triggerBody()?['policies']?['rightToWorkMethod']"
    "item/SoftwareUsed" = "@triggerBody()?['servicesExperience']?['softwareTools']"
    "item/Specialisations" = "@triggerBody()?['servicesExperience']?['specializations']"
    "item/TrainingRecords_Summary" = "@triggerBody()?['healthSafety']?['trainingRecordsSummary']"
    
    # Choice fields - FIXED FORMAT: Use object with Value property
    "item/Status" = "@{Value: 'Submitted'}"
    "item/ActsAsPrincipalContractor" = "@{Value: if(equals(triggerBody()?['rolesCapabilities']?['principalContractor'], true), 'Yes', 'No')}"
    "item/ActsAsPrincipalDesigner" = "@{Value: if(equals(triggerBody()?['rolesCapabilities']?['principalDesigner'], true), 'Yes', 'No')}"
    "item/AgreeToSaberTerms" = "@{Value: if(equals(triggerBody()?['agreement']?['agreeToTerms'], true), 'Yes', 'No')}"
    "item/HasGDPRPolicy" = "@{Value: if(equals(triggerBody()?['policies']?['hasGdprPolicy'], true), 'Yes', 'No')}"
    
    # MultiChoice fields - FIXED FORMAT: Use object with Value property as array
    "item/Accreditations" = "@{Value: split(coalesce(triggerBody()?['certifications']?['accreditations'], ''), ',')}"
    "item/CoverageRegion" = "@{Value: split(coalesce(triggerBody()?['projectReferences']?['coverageRegion'], ''), ',')}"
    "item/ISOStandards" = "@{Value: split(coalesce(triggerBody()?['certifications']?['isoStandards'], ''), ',')}"
}

# Find the Create_item action and add choice-fixed fields
$createItemAction = $definition.properties.definition.actions.Condition.actions.Create_item
if ($createItemAction -and $createItemAction.inputs -and $createItemAction.inputs.parameters) {
    
    # Add each choice-fixed field mapping
    foreach ($field in $choiceFixedFields.GetEnumerator()) {
        $fieldName = $field.Key
        $fieldExpression = $field.Value
        $createItemAction.inputs.parameters | Add-Member -NotePropertyName $fieldName -NotePropertyValue $fieldExpression -Force
    }
    
    Write-Host "✅ Added $($choiceFixedFields.Count) CHOICE-FIXED field mappings" -ForegroundColor Green
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

<h3>Roles & Capabilities</h3>
<ul>
<li><strong>Principal Contractor:</strong> @{if(equals(triggerBody()?['rolesCapabilities']?['principalContractor'], true), 'Yes', 'No')}</li>
<li><strong>Principal Designer:</strong> @{if(equals(triggerBody()?['rolesCapabilities']?['principalDesigner'], true), 'Yes', 'No')}</li>
</ul>

<h3>Certifications</h3>
<ul>
<li><strong>NICEIC CPS:</strong> @{if(coalesce(triggerBody()?['certifications']?['niceicContractor'], false), 'Yes', 'No')}</li>
<li><strong>MCS Approved:</strong> @{if(coalesce(triggerBody()?['certifications']?['mcsApproved'], false), 'Yes', 'No')}</li>
</ul>

<h3>Agreement</h3>
<ul>
<li><strong>GDPR Consent:</strong> @{if(coalesce(triggerBody()?['agreement']?['dataProcessingConsent'], false), 'Yes', 'No')}</li>
<li><strong>Marketing Consent:</strong> @{if(coalesce(triggerBody()?['agreement']?['marketingConsent'], false), 'Yes', 'No')}</li>
<li><strong>Agree to Codes:</strong> @{if(coalesce(triggerBody()?['agreement']?['agreeToCodes'], false), 'Yes', 'No')}</li>
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
Write-Host "✅ Updated CHOICE-FIXED definition saved" -ForegroundColor Green

# Create choice-fixed package
Write-Host "Creating CHOICE-FIXED package..." -ForegroundColor Yellow
$zipPath = "$OutputPath.zip"
if (Test-Path $zipPath) { Remove-Item $zipPath }
Compress-Archive -Path "$OutputPath/*" -DestinationPath $zipPath
Write-Host "✅ CHOICE-FIXED package created: $zipPath" -ForegroundColor Green

Write-Host "`n=======================================" -ForegroundColor Cyan
Write-Host "✅ CHOICE-FIELD-FIXED Flow Definition Ready!" -ForegroundColor Green
Write-Host "=======================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "FIXED CHOICE FIELD FORMATTING:" -ForegroundColor Yellow
Write-Host "• Status field: @{Value: 'Submitted'} (object format)" -ForegroundColor White
Write-Host "• ActsAs fields: @{Value: if(..., 'Yes', 'No')} (object format)" -ForegroundColor White
Write-Host "• MultiChoice fields: @{Value: split(..., ',')} (array format)" -ForegroundColor White
Write-Host "• Boolean fields: use coalesce for safety" -ForegroundColor White
Write-Host "• Text/Number fields: direct values" -ForegroundColor White
Write-Host ""
Write-Host "• $($choiceFixedFields.Count) field mappings with proper data types" -ForegroundColor White
Write-Host ""
Write-Host "Package ready for import: $zipPath" -ForegroundColor Green
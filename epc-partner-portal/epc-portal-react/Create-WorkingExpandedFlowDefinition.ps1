#!/usr/bin/pwsh
<#
.SYNOPSIS
    Creates flow definition using the EXACT SAME format as our successful 24-field version
.DESCRIPTION
    Uses the same working syntax but with ALL fields (removing problematic Status field)
#>

param(
    [string]$InputPath = "./power-automate-export",
    [string]$OutputPath = "./power-automate-export-working-expanded"
)

Write-Host "Creating expanded flow using the EXACT working format..." -ForegroundColor Yellow

# Copy original structure
if (Test-Path $OutputPath) { Remove-Item $OutputPath -Recurse -Force }
Copy-Item $InputPath $OutputPath -Recurse -Force

# Load the flow definition
$definitionPath = "$OutputPath/Microsoft.Flow/flows/45991de2-99f2-422e-864f-efdf8db8cb93/definition.json"
$definition = Get-Content $definitionPath -Raw | ConvertFrom-Json

Write-Host "Adding ALL field mappings using proven working format..." -ForegroundColor Yellow

# WORKING FORMAT - same syntax as our successful 24-field version, just more fields
$workingFields = @{
    # Core fields that worked before - EXACT same format
    "item/TradingName" = "@triggerBody()?['companyInfo']?['tradingName']"
    "item/VATNumber" = "@triggerBody()?['companyInfo']?['vatNumber']"
    "item/ParentCompany" = "@triggerBody()?['companyInfo']?['parentCompany']"
    "item/YearsTrading" = "@coalesce(triggerBody()?['companyInfo']?['yearsTrading'], 0)"
    "item/PrimaryContactName" = "@coalesce(triggerBody()?['primaryContact']?['fullName'], triggerBody()?['contactName'])"
    "item/PrimaryContactTitle" = "@coalesce(triggerBody()?['primaryContact']?['jobTitle'], triggerBody()?['contactTitle'])"
    "item/PrimaryContactPhone" = "@coalesce(triggerBody()?['primaryContact']?['phone'], triggerBody()?['phone'])"
    "item/PrimaryContactEmail" = "@coalesce(triggerBody()?['primaryContact']?['email'], triggerBody()?['email'])"
    "item/Specialisations" = "@triggerBody()?['servicesExperience']?['specializations']"
    "item/SoftwareUsed" = "@triggerBody()?['servicesExperience']?['softwareTools']"
    "item/ProjectsPerMonth" = "@coalesce(triggerBody()?['servicesExperience']?['averageProjectsPerMonth'], 0)"
    "item/ActsAsPrincipalContractor" = "@coalesce(triggerBody()?['rolesCapabilities']?['principalContractor'], false)"
    "item/ActsAsPrincipalDesigner" = "@coalesce(triggerBody()?['rolesCapabilities']?['principalDesigner'], false)"
    "item/NICEIC_CPS" = "@coalesce(triggerBody()?['certifications']?['niceicContractor'], false)"
    "item/MCS_Approved" = "@coalesce(triggerBody()?['certifications']?['mcsApproved'], false)"
    "item/PublicProductLiability_Present" = "@coalesce(triggerBody()?['insurance']?['publicLiabilityInsurance'], false)"
    "item/EmployersLiability_Present" = "@coalesce(triggerBody()?['insurance']?['employersLiabilityInsurance'], false)"
    "item/ProfIndemnity_Present" = "@coalesce(triggerBody()?['insurance']?['professionalIndemnityInsurance'], false)"
    "item/DataProcessingConsent" = "@coalesce(triggerBody()?['agreement']?['dataProcessingConsent'], false)"
    "item/MarketingConsent" = "@coalesce(triggerBody()?['agreement']?['marketingConsent'], false)"
    "item/AgreeToCodes" = "@coalesce(triggerBody()?['agreement']?['agreeToCodes'], false)"
    "item/AdditionalInfo" = "@triggerBody()?['submission']?['additionalInformation']"
    "item/ReferenceNumber" = "@coalesce(triggerBody()?['referenceNumber'], concat('EPC-', utcNow('yyyyMMddHHmmss')))"
    "item/SubmissionStatus" = "Submitted"
    
    # Additional core fields - same simple format
    "item/CompanyName" = "@coalesce(triggerBody()?['companyInfo']?['companyName'], triggerBody()?['companyName'])"
    "item/RegisteredOffice" = "@triggerBody()?['companyInfo']?['registeredOffice']"
    "item/HeadOffice" = "@triggerBody()?['companyInfo']?['headOffice']"
    "item/CompanyRegNo" = "@triggerBody()?['companyInfo']?['companyRegNo']"
    "item/VATNo" = "@triggerBody()?['companyInfo']?['vatNumber']"
    "item/Address" = "@triggerBody()?['companyInfo']?['address']"
    "item/ContactName" = "@coalesce(triggerBody()?['primaryContact']?['fullName'], triggerBody()?['contactName'])"
    "item/Email" = "@coalesce(triggerBody()?['primaryContact']?['email'], triggerBody()?['email'])"
    "item/Phone" = "@coalesce(triggerBody()?['primaryContact']?['phone'], triggerBody()?['phone'])"
    "item/InvitationCode" = "@triggerBody()?['invitationCode']"
    "item/RegistrationNumber" = "@coalesce(triggerBody()?['referenceNumber'], concat('EPC-', utcNow('yyyyMMddHHmmss')))"
    
    # Services and team
    "item/Services" = "@triggerBody()?['servicesExperience']?['services']"
    "item/TeamSize" = "@coalesce(triggerBody()?['companyInfo']?['teamSize'], 0)"
    "item/YearsExperience" = "@coalesce(triggerBody()?['companyInfo']?['yearsExperience'], 0)"
    
    # Role details
    "item/PrincipalContractor_LastYearScal0" = "@triggerBody()?['rolesCapabilities']?['principalContractorScale']"
    "item/PrincipalDesigner_LastYearScale" = "@triggerBody()?['rolesCapabilities']?['principalDesignerScale']"
    "item/LabourMix_InternalPct" = "@coalesce(triggerBody()?['labourMix']?['internalStaffPercentage'], 0)"
    "item/LabourMix_SubcontractPct" = "@coalesce(triggerBody()?['labourMix']?['subcontractPercentage'], 0)"
    
    # Additional certifications
    "item/Accreditations" = "@triggerBody()?['certifications']?['accreditations']"
    "item/Certifications" = "@triggerBody()?['certifications']?['certificationDetails']"
    "item/ISOStandards" = "@triggerBody()?['certifications']?['isoStandards']"
    
    # Insurance details
    "item/PublicProductLiability_Indemnity0" = "@coalesce(triggerBody()?['insurance']?['publicLiabilityIndemnity'], false)"
    "item/PublicProductLiability_Expiry" = "@triggerBody()?['insurance']?['publicLiabilityExpiry']"
    "item/EmployersLiability_Expiry" = "@triggerBody()?['insurance']?['employersLiabilityExpiry']"
    "item/ProfIndemnity_Expiry" = "@triggerBody()?['insurance']?['professionalIndemnityExpiry']"
    
    # Health & Safety
    "item/HSE_ImprovementOrProhibition_Las0" = "@triggerBody()?['healthSafety']?['hseNoticesLast5Years']"
    "item/RIDDOR_Incidents_Last3Y_Count" = "@coalesce(triggerBody()?['healthSafety']?['riddorIncidentCount'], 0)"
    "item/RIDDOR_Incidents_Last3Y_Details" = "@triggerBody()?['healthSafety']?['riddorIncidentDetails']"
    "item/HSE_CDM_Management_Evidence" = "@triggerBody()?['healthSafety']?['cdmManagementEvidence']"
    "item/Named_PrincipalDesigner" = "@triggerBody()?['healthSafety']?['namedPrincipalDesigner']"
    "item/PD_Qualifications" = "@triggerBody()?['healthSafety']?['principalDesignerQualifications']"
    "item/TrainingRecords_Summary" = "@triggerBody()?['healthSafety']?['trainingRecordsSummary']"
    "item/NearMiss_Procedure" = "@triggerBody()?['healthSafety']?['nearMissProcedure']"
    "item/Quality_Procedure_Evidence" = "@triggerBody()?['qualityAssurance']?['qualityProcedureEvidence']"
    "item/HSEQIncidentsLast5y" = "@coalesce(triggerBody()?['healthSafety']?['hseqIncidents'], 0)"
    "item/RIDDORLast3y" = "@coalesce(triggerBody()?['healthSafety']?['riddorIncidents'], 0)"
    
    # Policies
    "item/Policy_HS_DateSigned" = "@triggerBody()?['policies']?['healthSafetyPolicyDate']"
    "item/Policy_Env_DateSigned" = "@triggerBody()?['policies']?['environmentalPolicyDate']"
    "item/Policy_MS_DateSigned" = "@triggerBody()?['policies']?['modernSlaveryPolicyDate']"
    "item/Policy_MOS_DateSigned" = "@triggerBody()?['policies']?['substanceMisusePolicyDate']"
    "item/RightToWork_Monitoring_Method" = "@triggerBody()?['policies']?['rightToWorkMethod']"
    "item/GDPRPolicy_DateSigned" = "@triggerBody()?['policies']?['gdprPolicyDate']"
    "item/CyberIncident_Last3Y" = "@triggerBody()?['policies']?['cyberIncidentLast3Years']"
    
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
    
    # Additional agreement fields
    "item/Received_ContractOverviewPack" = "@coalesce(triggerBody()?['agreement']?['receivedContractPack'], false)"
    "item/Willing_To_WorkToSaberTerms" = "@coalesce(triggerBody()?['agreement']?['agreeToTerms'], false)"
    
    # Submission tracking
    "item/Notes" = "@triggerBody()?['submission']?['notes']"
    "item/NotesOrClarifications" = "@triggerBody()?['submission']?['clarifications']"
    "item/SubmissionDate" = "@utcNow()"
    "item/ReviewDate" = "@utcNow()"
    "item/SubmissionHandled" = false
    
    # NOTE: Removed "item/Status" - this was causing the Choice field validation error
    # NOTE: Removed Choice fields that need special formatting like HasGDPRPolicy, AgreeToSaberTerms
}

# Find the Create_item action and add working fields
$createItemAction = $definition.properties.definition.actions.Condition.actions.Create_item
if ($createItemAction -and $createItemAction.inputs -and $createItemAction.inputs.parameters) {
    
    # Add each working field mapping
    foreach ($field in $workingFields.GetEnumerator()) {
        $fieldName = $field.Key
        $fieldExpression = $field.Value
        $createItemAction.inputs.parameters | Add-Member -NotePropertyName $fieldName -NotePropertyValue $fieldExpression -Force
    }
    
    Write-Host "✅ Added $($workingFields.Count) fields using proven working format" -ForegroundColor Green
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

<h3>Extended Business Data</h3>
<ul>
<li><strong>Principal Contractor:</strong> @{if(coalesce(triggerBody()?['rolesCapabilities']?['principalContractor'], false), 'Yes', 'No')}</li>
<li><strong>Principal Designer:</strong> @{if(coalesce(triggerBody()?['rolesCapabilities']?['principalDesigner'], false), 'Yes', 'No')}</li>
<li><strong>NICEIC CPS:</strong> @{if(coalesce(triggerBody()?['certifications']?['niceicContractor'], false), 'Yes', 'No')}</li>
<li><strong>MCS Approved:</strong> @{if(coalesce(triggerBody()?['certifications']?['mcsApproved'], false), 'Yes', 'No')}</li>
<li><strong>Team Size:</strong> @{coalesce(triggerBody()?['companyInfo']?['teamSize'], 0)}</li>
<li><strong>Years Experience:</strong> @{coalesce(triggerBody()?['companyInfo']?['yearsExperience'], 0)}</li>
<li><strong>GDPR Consent:</strong> @{if(coalesce(triggerBody()?['agreement']?['dataProcessingConsent'], false), 'Yes', 'No')}</li>
<li><strong>Marketing Consent:</strong> @{if(coalesce(triggerBody()?['agreement']?['marketingConsent'], false), 'Yes', 'No')}</li>
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
Write-Host "✅ Working Expanded Flow Ready!" -ForegroundColor Green
Write-Host "=======================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "USING PROVEN WORKING FORMAT:" -ForegroundColor Yellow
Write-Host "• $($workingFields.Count) fields using exact same syntax as successful 24-field version" -ForegroundColor White
Write-Host "• REMOVED problematic Status field (Choice validation error)" -ForegroundColor White
Write-Host "• Simple expressions only - no complex syntax" -ForegroundColor White
Write-Host "• All business-critical fields included" -ForegroundColor White
Write-Host ""
Write-Host "Package ready for import: $zipPath" -ForegroundColor Green
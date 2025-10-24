#!/usr/bin/pwsh
<#
.SYNOPSIS
    Creates flow definition using ONLY the exact field names verified to exist in SharePoint
.DESCRIPTION
    Uses ONLY fields from our Check-AllSharePointFields.ps1 output - no guessing!
#>

param(
    [string]$InputPath = "./power-automate-export",
    [string]$OutputPath = "./power-automate-export-verified"
)

Write-Host "Creating VERIFIED-ONLY flow definition..." -ForegroundColor Yellow

# Copy original structure
if (Test-Path $OutputPath) { Remove-Item $OutputPath -Recurse -Force }
Copy-Item $InputPath $OutputPath -Recurse -Force

# Load the flow definition
$definitionPath = "$OutputPath/Microsoft.Flow/flows/45991de2-99f2-422e-864f-efdf8db8cb93/definition.json"
$definition = Get-Content $definitionPath -Raw | ConvertFrom-Json

Write-Host "Adding VERIFIED field mappings (ONLY exact names from SharePoint check)..." -ForegroundColor Yellow

# VERIFIED field mappings - ONLY using the exact field names from Check-AllSharePointFields.ps1 output
$verifiedFields = @{
    # Custom Columns Group - VERIFIED to exist
    "item/CompanyName" = "@coalesce(triggerBody()?['companyInfo']?['companyName'], triggerBody()?['companyName'])"
    "item/TradingName" = "@triggerBody()?['companyInfo']?['tradingName']"
    "item/RegisteredOffice" = "@triggerBody()?['companyInfo']?['registeredOffice']"
    "item/CompanyRegNo" = "@triggerBody()?['companyInfo']?['companyRegNo']"
    "item/YearsTrading" = "@coalesce(triggerBody()?['companyInfo']?['yearsTrading'], 0)"
    "item/PrimaryContactName" = "@coalesce(triggerBody()?['primaryContact']?['fullName'], triggerBody()?['contactName'])"
    "item/PrimaryContactPhone" = "@coalesce(triggerBody()?['primaryContact']?['phone'], triggerBody()?['phone'])"
    "item/PrimaryContactEmail" = "@coalesce(triggerBody()?['primaryContact']?['email'], triggerBody()?['email'])"
    "item/ContactName" = "@coalesce(triggerBody()?['primaryContact']?['fullName'], triggerBody()?['contactName'])"
    "item/Email" = "@coalesce(triggerBody()?['primaryContact']?['email'], triggerBody()?['email'])"
    "item/Phone" = "@coalesce(triggerBody()?['primaryContact']?['phone'], triggerBody()?['phone'])"
    "item/Address" = "@triggerBody()?['companyInfo']?['address']"
    
    # Choice fields - Custom Columns (these are Choice, not Boolean!)
    "item/ActsAsPrincipalContractor" = "@if(equals(triggerBody()?['rolesCapabilities']?['principalContractor'], true), 'Yes', 'No')"
    "item/ActsAsPrincipalDesigner" = "@if(equals(triggerBody()?['rolesCapabilities']?['principalDesigner'], true), 'Yes', 'No')"
    "item/AgreeToSaberTerms" = "@if(equals(triggerBody()?['agreement']?['agreeToTerms'], true), 'Yes', 'No')"
    "item/HasGDPRPolicy" = "@if(equals(triggerBody()?['policies']?['hasGdprPolicy'], true), 'Yes', 'No')"
    "item/Status" = "Submitted"
    
    # MultiChoice/Note fields - Custom Columns
    "item/Accreditations" = "@triggerBody()?['certifications']?['accreditations']"
    "item/Certifications" = "@triggerBody()?['certifications']?['certificationDetails']"
    "item/Services" = "@triggerBody()?['servicesExperience']?['services']"
    "item/Coverage" = "@triggerBody()?['projectReferences']?['coverage']"
    "item/CoverageRegion" = "@triggerBody()?['projectReferences']?['coverageRegion']"
    "item/ISOStandards" = "@triggerBody()?['certifications']?['isoStandards']"
    "item/Notes" = "@triggerBody()?['submission']?['notes']"
    "item/NotesOrClarifications" = "@triggerBody()?['submission']?['clarifications']"
    
    # Number fields - Custom Columns
    "item/TeamSize" = "@coalesce(triggerBody()?['companyInfo']?['teamSize'], 0)"
    "item/YearsExperience" = "@coalesce(triggerBody()?['companyInfo']?['yearsExperience'], 0)"
    "item/HSEQIncidentsLast5y" = "@coalesce(triggerBody()?['healthSafety']?['hseqIncidents'], 0)"
    "item/RIDDORLast3y" = "@coalesce(triggerBody()?['healthSafety']?['riddorIncidents'], 0)"
    
    # Text fields - Custom Columns
    "item/RegistrationNumber" = "@coalesce(triggerBody()?['referenceNumber'], concat('EPC-', utcNow('yyyyMMddHHmmss')))"
    "item/VATNo" = "@triggerBody()?['companyInfo']?['vatNumber']"
    "item/InvitationCode" = "@triggerBody()?['invitationCode']"
    
    # DateTime fields - Custom Columns
    "item/SubmissionDate" = "@utcNow()"
    "item/ReviewDate" = "@utcNow()"
    
    # Boolean field - Custom Columns
    "item/SubmissionHandled" = "false"
    
    # EPC Extended Group - VERIFIED to exist
    "item/AdditionalInfo" = "@triggerBody()?['submission']?['additionalInformation']"
    "item/AgreeToCodes" = "@coalesce(triggerBody()?['agreement']?['agreeToCodes'], false)"
    "item/Client_Reference" = "@triggerBody()?['projectReferences']?['clientReference']"
    "item/Contracts_ReviewedBySignatory" = "@coalesce(triggerBody()?['legalCompliance']?['contractsReviewed'], false)"
    "item/Coverage_Nationwide" = "@coalesce(triggerBody()?['projectReferences']?['nationwideCoverage'], false)"
    "item/CyberIncident_Last3Y" = "@triggerBody()?['policies']?['cyberIncidentLast3Years']"
    "item/DataProcessingConsent" = "@coalesce(triggerBody()?['agreement']?['dataProcessingConsent'], false)"
    "item/EmployersLiability_Expiry" = "@triggerBody()?['insurance']?['employersLiabilityExpiry']"
    "item/EmployersLiability_Present" = "@coalesce(triggerBody()?['insurance']?['employersLiabilityInsurance'], false)"
    "item/GDPRPolicy_DateSigned" = "@triggerBody()?['policies']?['gdprPolicyDate']"
    "item/HeadOffice" = "@triggerBody()?['companyInfo']?['headOffice']"
    "item/HSE_CDM_Management_Evidence" = "@triggerBody()?['healthSafety']?['cdmManagementEvidence']"
    
    # HSE field - use the EXACT name from our check (Las0, not Las1!)
    "item/HSE_ImprovementOrProhibition_Las0" = "@triggerBody()?['healthSafety']?['hseNoticesLast5Years']"
    
    "item/LabourMix_InternalPct" = "@coalesce(triggerBody()?['labourMix']?['internalStaffPercentage'], 0)"
    "item/LabourMix_SubcontractPct" = "@coalesce(triggerBody()?['labourMix']?['subcontractPercentage'], 0)"
    "item/Legal_Clarifications" = "@triggerBody()?['legalCompliance']?['legalClarifications']"
    "item/MarketingConsent" = "@coalesce(triggerBody()?['agreement']?['marketingConsent'], false)"
    "item/MCS_Approved" = "@coalesce(triggerBody()?['certifications']?['mcsApproved'], false)"
    "item/Named_PrincipalDesigner" = "@triggerBody()?['healthSafety']?['namedPrincipalDesigner']"
    "item/NearMiss_Procedure" = "@triggerBody()?['healthSafety']?['nearMissProcedure']"
    "item/NICEIC_CPS" = "@coalesce(triggerBody()?['certifications']?['niceicContractor'], false)"
    "item/ParentCompany" = "@triggerBody()?['companyInfo']?['parentCompany']"
    "item/PD_Qualifications" = "@triggerBody()?['healthSafety']?['principalDesignerQualifications']"
    "item/PendingProsecutions_Details" = "@triggerBody()?['legalCompliance']?['pendingProsecutions']"
    "item/Policy_Env_DateSigned" = "@triggerBody()?['policies']?['environmentalPolicyDate']"
    "item/Policy_HS_DateSigned" = "@triggerBody()?['policies']?['healthSafetyPolicyDate']"
    "item/Policy_MOS_DateSigned" = "@triggerBody()?['policies']?['substanceMisusePolicyDate']"
    "item/Policy_MS_DateSigned" = "@triggerBody()?['policies']?['modernSlaveryPolicyDate']"
    "item/PrimaryContactTitle" = "@coalesce(triggerBody()?['primaryContact']?['jobTitle'], triggerBody()?['contactTitle'])"
    
    # Use the EXACT truncated names from our check
    "item/PrincipalContractor_LastYearScal0" = "@triggerBody()?['rolesCapabilities']?['principalContractorScale']"
    "item/PrincipalDesigner_LastYearScale" = "@triggerBody()?['rolesCapabilities']?['principalDesignerScale']"
    
    "item/ProfIndemnity_Expiry" = "@triggerBody()?['insurance']?['professionalIndemnityExpiry']"
    "item/ProfIndemnity_Present" = "@coalesce(triggerBody()?['insurance']?['professionalIndemnityInsurance'], false)"
    "item/ProjectsPerMonth" = "@coalesce(triggerBody()?['servicesExperience']?['averageProjectsPerMonth'], 0)"
    "item/PublicProductLiability_Expiry" = "@triggerBody()?['insurance']?['publicLiabilityExpiry']"
    
    # Use the EXACT truncated name from our check (Indemnity0, not Indemnity1!)
    "item/PublicProductLiability_Indemnity0" = "@coalesce(triggerBody()?['insurance']?['publicLiabilityIndemnity'], false)"
    
    "item/PublicProductLiability_Present" = "@coalesce(triggerBody()?['insurance']?['publicLiabilityInsurance'], false)"
    "item/Quality_Procedure_Evidence" = "@triggerBody()?['qualityAssurance']?['qualityProcedureEvidence']"
    "item/Received_ContractOverviewPack" = "@coalesce(triggerBody()?['agreement']?['receivedContractPack'], false)"
    "item/ReferenceNumber" = "@coalesce(triggerBody()?['referenceNumber'], concat('EPC-', utcNow('yyyyMMddHHmmss')))"
    "item/Resources_PerProject" = "@triggerBody()?['projectReferences']?['resourcesPerProject']"
    "item/RIDDOR_Incidents_Last3Y_Count" = "@coalesce(triggerBody()?['healthSafety']?['riddorIncidentCount'], 0)"
    "item/RIDDOR_Incidents_Last3Y_Details" = "@triggerBody()?['healthSafety']?['riddorIncidentDetails']"
    "item/RightToWork_Monitoring_Method" = "@triggerBody()?['policies']?['rightToWorkMethod']"
    "item/SoftwareUsed" = "@triggerBody()?['servicesExperience']?['softwareTools']"
    "item/Specialisations" = "@triggerBody()?['servicesExperience']?['specializations']"
    "item/SubmissionStatus" = "Submitted"
    "item/TrainingRecords_Summary" = "@triggerBody()?['healthSafety']?['trainingRecordsSummary']"
    "item/VATNumber" = "@triggerBody()?['companyInfo']?['vatNumber']"
    "item/Willing_To_WorkToSaberTerms" = "@coalesce(triggerBody()?['agreement']?['agreeToTerms'], false)"
}

# Find the Create_item action and add verified fields
$createItemAction = $definition.properties.definition.actions.Condition.actions.Create_item
if ($createItemAction -and $createItemAction.inputs -and $createItemAction.inputs.parameters) {
    
    # Add each verified field mapping
    foreach ($field in $verifiedFields.GetEnumerator()) {
        $fieldName = $field.Key
        $fieldExpression = $field.Value
        $createItemAction.inputs.parameters | Add-Member -NotePropertyName $fieldName -NotePropertyValue $fieldExpression -Force
    }
    
    Write-Host "✅ Added $($verifiedFields.Count) VERIFIED field mappings (only exact SharePoint names)" -ForegroundColor Green
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
<tr><td><strong>Parent Company</strong></td><td>@{triggerBody()?['companyInfo']?['parentCompany']}</td></tr>
<tr><td><strong>Years Trading</strong></td><td>@{coalesce(triggerBody()?['companyInfo']?['yearsTrading'], 0)}</td></tr>
<tr><td><strong>Contact</strong></td><td>@{coalesce(triggerBody()?['primaryContact']?['fullName'], triggerBody()?['contactName'])}</td></tr>
<tr><td><strong>Email</strong></td><td>@{coalesce(triggerBody()?['primaryContact']?['email'], triggerBody()?['email'])}</td></tr>
<tr><td><strong>Phone</strong></td><td>@{coalesce(triggerBody()?['primaryContact']?['phone'], triggerBody()?['phone'])}</td></tr>
<tr><td><strong>SharePoint ID</strong></td><td>@{body('Create_item')?['ID']}</td></tr>
<tr><td><strong>Code Used</strong></td><td>@{triggerBody()?['invitationCode']}</td></tr>
</tbody>
</table>

<h3>Services & Experience</h3>
<ul>
<li><strong>Specializations:</strong> @{triggerBody()?['servicesExperience']?['specializations']}</li>
<li><strong>Software Used:</strong> @{triggerBody()?['servicesExperience']?['softwareTools']}</li>
<li><strong>Projects Per Month:</strong> @{coalesce(triggerBody()?['servicesExperience']?['averageProjectsPerMonth'], 0)}</li>
<li><strong>Team Size:</strong> @{coalesce(triggerBody()?['companyInfo']?['teamSize'], 0)}</li>
<li><strong>Years Experience:</strong> @{coalesce(triggerBody()?['companyInfo']?['yearsExperience'], 0)}</li>
</ul>

<h3>Roles & Capabilities</h3>
<ul>
<li><strong>Principal Contractor:</strong> @{if(equals(triggerBody()?['rolesCapabilities']?['principalContractor'], true), 'Yes', 'No')}</li>
<li><strong>Principal Designer:</strong> @{if(equals(triggerBody()?['rolesCapabilities']?['principalDesigner'], true), 'Yes', 'No')}</li>
<li><strong>Internal Staff %:</strong> @{coalesce(triggerBody()?['labourMix']?['internalStaffPercentage'], 0)}</li>
<li><strong>Subcontract %:</strong> @{coalesce(triggerBody()?['labourMix']?['subcontractPercentage'], 0)}</li>
</ul>

<h3>Certifications</h3>
<ul>
<li><strong>NICEIC CPS:</strong> @{if(coalesce(triggerBody()?['certifications']?['niceicContractor'], false), 'Yes', 'No')}</li>
<li><strong>MCS Approved:</strong> @{if(coalesce(triggerBody()?['certifications']?['mcsApproved'], false), 'Yes', 'No')}</li>
<li><strong>Accreditations:</strong> @{triggerBody()?['certifications']?['accreditations']}</li>
<li><strong>ISO Standards:</strong> @{triggerBody()?['certifications']?['isoStandards']}</li>
</ul>

<h3>Insurance</h3>
<ul>
<li><strong>Public Liability:</strong> @{if(coalesce(triggerBody()?['insurance']?['publicLiabilityInsurance'], false), 'Yes', 'No')}</li>
<li><strong>Employers Liability:</strong> @{if(coalesce(triggerBody()?['insurance']?['employersLiabilityInsurance'], false), 'Yes', 'No')}</li>
<li><strong>Professional Indemnity:</strong> @{if(coalesce(triggerBody()?['insurance']?['professionalIndemnityInsurance'], false), 'Yes', 'No')}</li>
</ul>

<h3>Health & Safety</h3>
<ul>
<li><strong>HSE Notices (5Y):</strong> @{triggerBody()?['healthSafety']?['hseNoticesLast5Years']}</li>
<li><strong>RIDDOR Count (3Y):</strong> @{coalesce(triggerBody()?['healthSafety']?['riddorIncidentCount'], 0)}</li>
<li><strong>Named Principal Designer:</strong> @{triggerBody()?['healthSafety']?['namedPrincipalDesigner']}</li>
</ul>

<h3>Compliance & Consent</h3>
<ul>
<li><strong>Nationwide Coverage:</strong> @{if(coalesce(triggerBody()?['projectReferences']?['nationwideCoverage'], false), 'Yes', 'No')}</li>
<li><strong>Contracts Reviewed:</strong> @{if(coalesce(triggerBody()?['legalCompliance']?['contractsReviewed'], false), 'Yes', 'No')}</li>
<li><strong>GDPR Consent:</strong> @{if(coalesce(triggerBody()?['agreement']?['dataProcessingConsent'], false), 'Yes', 'No')}</li>
<li><strong>Marketing Consent:</strong> @{if(coalesce(triggerBody()?['agreement']?['marketingConsent'], false), 'Yes', 'No')}</li>
<li><strong>Agree to Codes:</strong> @{if(coalesce(triggerBody()?['agreement']?['agreeToCodes'], false), 'Yes', 'No')}</li>
<li><strong>Agree to Terms:</strong> @{if(coalesce(triggerBody()?['agreement']?['agreeToTerms'], false), 'Yes', 'No')}</li>
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
Write-Host "✅ Updated VERIFIED definition saved" -ForegroundColor Green

# Create verified package
Write-Host "Creating VERIFIED package..." -ForegroundColor Yellow
$zipPath = "$OutputPath.zip"
if (Test-Path $zipPath) { Remove-Item $zipPath }
Compress-Archive -Path "$OutputPath/*" -DestinationPath $zipPath
Write-Host "✅ VERIFIED package created: $zipPath" -ForegroundColor Green

Write-Host "`n=======================================" -ForegroundColor Cyan
Write-Host "✅ VERIFIED Flow Definition Ready!" -ForegroundColor Green
Write-Host "=======================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "USING ONLY VERIFIED SHAREPOINT FIELD NAMES:" -ForegroundColor Yellow
Write-Host "• $($verifiedFields.Count) field mappings with EXACT verified names" -ForegroundColor White
Write-Host "• HSE_ImprovementOrProhibition_Las0 (exact match from SharePoint)" -ForegroundColor White
Write-Host "• PrincipalContractor_LastYearScal0 (exact match from SharePoint)" -ForegroundColor White
Write-Host "• PublicProductLiability_Indemnity0 (exact match from SharePoint)" -ForegroundColor White
Write-Host "• Choice fields handled correctly (Yes/No for ActsAs fields)" -ForegroundColor White
Write-Host "• Boolean fields use coalesce for safety" -ForegroundColor White
Write-Host ""
Write-Host "NO GUESSING - ONLY VERIFIED FIELD NAMES USED!" -ForegroundColor Yellow
Write-Host ""
Write-Host "Package ready for import: $zipPath" -ForegroundColor Green
#!/usr/bin/pwsh
<#
.SYNOPSIS
    Creates a corrected flow definition using EXACT SharePoint field names from Check-SharePointFields.ps1
.DESCRIPTION
    Uses only verified field names that actually exist in SharePoint
#>

param(
    [string]$InputPath = "./power-automate-export",
    [string]$OutputPath = "./power-automate-export-corrected"
)

Write-Host "Creating CORRECTED flow definition with EXACT SharePoint field names..." -ForegroundColor Yellow

# Copy original structure
if (Test-Path $OutputPath) { Remove-Item $OutputPath -Recurse -Force }
Copy-Item $InputPath $OutputPath -Recurse -Force

# Load the flow definition
$definitionPath = "$OutputPath/Microsoft.Flow/flows/45991de2-99f2-422e-864f-efdf8db8cb93/definition.json"
$definition = Get-Content $definitionPath -Raw | ConvertFrom-Json

Write-Host "Adding CORRECTED field mappings (using verified SharePoint field names)..." -ForegroundColor Yellow

# CORRECTED field mappings - ONLY using field names that actually exist in SharePoint
$correctedFields = @{
    # Core fields that we know work
    "item/CompanyName" = "@coalesce(triggerBody()?['companyInfo']?['companyName'], triggerBody()?['companyName'])"
    "item/TradingName" = "@triggerBody()?['companyInfo']?['tradingName']"
    "item/VATNumber" = "@triggerBody()?['companyInfo']?['vatNumber']"
    "item/ParentCompany" = "@triggerBody()?['companyInfo']?['parentCompany']"
    "item/YearsTrading" = "@coalesce(triggerBody()?['companyInfo']?['yearsTrading'], 0)"
    "item/HeadOffice" = "@triggerBody()?['companyInfo']?['headOffice']"
    
    # Contact fields - exact names from SharePoint
    "item/PrimaryContactName" = "@coalesce(triggerBody()?['primaryContact']?['fullName'], triggerBody()?['contactName'])"
    "item/PrimaryContactTitle" = "@coalesce(triggerBody()?['primaryContact']?['jobTitle'], triggerBody()?['contactTitle'])"
    "item/PrimaryContactPhone" = "@coalesce(triggerBody()?['primaryContact']?['phone'], triggerBody()?['phone'])"
    "item/PrimaryContactEmail" = "@coalesce(triggerBody()?['primaryContact']?['email'], triggerBody()?['email'])"
    
    # Services - exact names from SharePoint
    "item/Specialisations" = "@triggerBody()?['servicesExperience']?['specializations']"
    "item/SoftwareUsed" = "@triggerBody()?['servicesExperience']?['softwareTools']"
    "item/ProjectsPerMonth" = "@coalesce(triggerBody()?['servicesExperience']?['averageProjectsPerMonth'], 0)"
    
    # Roles - from our working example
    "item/ActsAsPrincipalContractor" = "@coalesce(triggerBody()?['rolesCapabilities']?['principalContractor'], false)"
    "item/ActsAsPrincipalDesigner" = "@coalesce(triggerBody()?['rolesCapabilities']?['principalDesigner'], false)"
    
    # Use the TRUNCATED field names from SharePoint
    "item/PrincipalContractor_LastYearScal0" = "@triggerBody()?['rolesCapabilities']?['principalContractorScale']"
    "item/PrincipalDesigner_LastYearScale" = "@triggerBody()?['rolesCapabilities']?['principalDesignerScale']"
    
    # Labour mix - exact names
    "item/LabourMix_InternalPct" = "@coalesce(triggerBody()?['labourMix']?['internalStaffPercentage'], 0)"
    "item/LabourMix_SubcontractPct" = "@coalesce(triggerBody()?['labourMix']?['subcontractPercentage'], 0)"
    
    # Certifications - exact names
    "item/NICEIC_CPS" = "@coalesce(triggerBody()?['certifications']?['niceicContractor'], false)"
    "item/MCS_Approved" = "@coalesce(triggerBody()?['certifications']?['mcsApproved'], false)"
    
    # Insurance - exact names including truncated ones
    "item/PublicProductLiability_Present" = "@coalesce(triggerBody()?['insurance']?['publicLiabilityInsurance'], false)"
    "item/PublicProductLiability_Indemnity0" = "@coalesce(triggerBody()?['insurance']?['publicLiabilityIndemnity'], false)"  # Truncated
    "item/EmployersLiability_Present" = "@coalesce(triggerBody()?['insurance']?['employersLiabilityInsurance'], false)"
    "item/ProfIndemnity_Present" = "@coalesce(triggerBody()?['insurance']?['professionalIndemnityInsurance'], false)"
    "item/PublicProductLiability_Expiry" = "@triggerBody()?['insurance']?['publicLiabilityExpiry']"
    "item/EmployersLiability_Expiry" = "@triggerBody()?['insurance']?['employersLiabilityExpiry']"
    "item/ProfIndemnity_Expiry" = "@triggerBody()?['insurance']?['professionalIndemnityExpiry']"
    
    # Health & Safety - using EXACT truncated names from SharePoint
    "item/HSE_ImprovementOrProhibition_Las0" = "@triggerBody()?['healthSafety']?['hseNoticesLast5Years']"  # Use the 0 version
    "item/RIDDOR_Incidents_Last3Y_Count" = "@coalesce(triggerBody()?['healthSafety']?['riddorIncidentCount'], 0)"
    "item/RIDDOR_Incidents_Last3Y_Details" = "@triggerBody()?['healthSafety']?['riddorIncidentDetails']"
    "item/HSE_CDM_Management_Evidence" = "@triggerBody()?['healthSafety']?['cdmManagementEvidence']"
    "item/Named_PrincipalDesigner" = "@triggerBody()?['healthSafety']?['namedPrincipalDesigner']"
    "item/PD_Qualifications" = "@triggerBody()?['healthSafety']?['principalDesignerQualifications']"
    "item/TrainingRecords_Summary" = "@triggerBody()?['healthSafety']?['trainingRecordsSummary']"
    "item/NearMiss_Procedure" = "@triggerBody()?['healthSafety']?['nearMissProcedure']"
    "item/Quality_Procedure_Evidence" = "@triggerBody()?['qualityAssurance']?['qualityProcedureEvidence']"
    
    # Policy dates - exact names
    "item/Policy_HS_DateSigned" = "@triggerBody()?['policies']?['healthSafetyPolicyDate']"
    "item/Policy_Env_DateSigned" = "@triggerBody()?['policies']?['environmentalPolicyDate']"
    "item/Policy_MS_DateSigned" = "@triggerBody()?['policies']?['modernSlaveryPolicyDate']"
    "item/Policy_MOS_DateSigned" = "@triggerBody()?['policies']?['substanceMisusePolicyDate']"
    "item/RightToWork_Monitoring_Method" = "@triggerBody()?['policies']?['rightToWorkMethod']"
    "item/GDPRPolicy_DateSigned" = "@triggerBody()?['policies']?['gdprPolicyDate']"
    "item/CyberIncident_Last3Y" = "@triggerBody()?['policies']?['cyberIncidentLast3Years']"
    
    # Project references - exact names
    "item/Resources_PerProject" = "@triggerBody()?['projectReferences']?['resourcesPerProject']"
    "item/Coverage_Nationwide" = "@coalesce(triggerBody()?['projectReferences']?['nationwideCoverage'], false)"
    "item/Client_Reference" = "@triggerBody()?['projectReferences']?['clientReference']"
    
    # Legal compliance - exact names
    "item/PendingProsecutions_Details" = "@triggerBody()?['legalCompliance']?['pendingProsecutions']"
    "item/Contracts_ReviewedBySignatory" = "@coalesce(triggerBody()?['legalCompliance']?['contractsReviewed'], false)"
    "item/Legal_Clarifications" = "@triggerBody()?['legalCompliance']?['legalClarifications']"
    
    # Agreement fields - exact names
    "item/Received_ContractOverviewPack" = "@coalesce(triggerBody()?['agreement']?['receivedContractPack'], false)"
    "item/Willing_To_WorkToSaberTerms" = "@coalesce(triggerBody()?['agreement']?['agreeToTerms'], false)"
    "item/AgreeToCodes" = "@coalesce(triggerBody()?['agreement']?['agreeToCodes'], false)"
    "item/DataProcessingConsent" = "@coalesce(triggerBody()?['agreement']?['dataProcessingConsent'], false)"
    "item/MarketingConsent" = "@coalesce(triggerBody()?['agreement']?['marketingConsent'], false)"
    
    # Submission fields - exact names
    "item/AdditionalInfo" = "@triggerBody()?['submission']?['additionalInformation']"
    "item/SubmissionStatus" = "Submitted"
    "item/ReferenceNumber" = "@coalesce(triggerBody()?['referenceNumber'], concat('EPC-', utcNow('yyyyMMddHHmmss')))"
}

# Find the Create_item action and add corrected fields
$createItemAction = $definition.properties.definition.actions.Condition.actions.Create_item
if ($createItemAction -and $createItemAction.inputs -and $createItemAction.inputs.parameters) {
    
    # Add each corrected field mapping
    foreach ($field in $correctedFields.GetEnumerator()) {
        $fieldName = $field.Key
        $fieldExpression = $field.Value
        $createItemAction.inputs.parameters | Add-Member -NotePropertyName $fieldName -NotePropertyValue $fieldExpression -Force
    }
    
    Write-Host "✅ Added $($correctedFields.Count) CORRECTED field mappings (verified SharePoint names)" -ForegroundColor Green
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
</ul>

<h3>Roles & Capabilities</h3>
<ul>
<li><strong>Principal Contractor:</strong> @{if(coalesce(triggerBody()?['rolesCapabilities']?['principalContractor'], false), 'Yes', 'No')}</li>
<li><strong>Principal Designer:</strong> @{if(coalesce(triggerBody()?['rolesCapabilities']?['principalDesigner'], false), 'Yes', 'No')}</li>
<li><strong>Internal Staff %:</strong> @{coalesce(triggerBody()?['labourMix']?['internalStaffPercentage'], 0)}</li>
<li><strong>Subcontract %:</strong> @{coalesce(triggerBody()?['labourMix']?['subcontractPercentage'], 0)}</li>
</ul>

<h3>Certifications</h3>
<ul>
<li><strong>NICEIC CPS:</strong> @{if(coalesce(triggerBody()?['certifications']?['niceicContractor'], false), 'Yes', 'No')}</li>
<li><strong>MCS Approved:</strong> @{if(coalesce(triggerBody()?['certifications']?['mcsApproved'], false), 'Yes', 'No')}</li>
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
Write-Host "✅ Updated CORRECTED definition saved" -ForegroundColor Green

# Create corrected package
Write-Host "Creating CORRECTED package..." -ForegroundColor Yellow
$zipPath = "$OutputPath.zip"
if (Test-Path $zipPath) { Remove-Item $zipPath }
Compress-Archive -Path "$OutputPath/*" -DestinationPath $zipPath
Write-Host "✅ CORRECTED package created: $zipPath" -ForegroundColor Green

Write-Host "`n=======================================" -ForegroundColor Cyan
Write-Host "✅ CORRECTED Flow Definition Ready!" -ForegroundColor Green
Write-Host "=======================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "USING VERIFIED SHAREPOINT FIELD NAMES:" -ForegroundColor Yellow
Write-Host "• $($correctedFields.Count) field mappings with exact SharePoint names" -ForegroundColor White
Write-Host "• Fixed truncated field names (HSE_ImprovementOrProhibition_Las0)" -ForegroundColor White
Write-Host "• Using correct duplicate field versions" -ForegroundColor White
Write-Host "• All boolean fields use coalesce for safety" -ForegroundColor White
Write-Host ""
Write-Host "CORRECTED FIELD EXAMPLES:" -ForegroundColor Yellow
Write-Host "• HSE_ImprovementOrProhibition_Las0 (was HSE_ImprovementOrProhibition_Last5Y)" -ForegroundColor White
Write-Host "• PrincipalContractor_LastYearScal0 (was PrincipalContractor_LastYearScale)" -ForegroundColor White
Write-Host "• PublicProductLiability_Indemnity0 (was PublicProductLiability_IndemnityInPrinciple)" -ForegroundColor White
Write-Host ""
Write-Host "Package ready for import: $zipPath" -ForegroundColor Green
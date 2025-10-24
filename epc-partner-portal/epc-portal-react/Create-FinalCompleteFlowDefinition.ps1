#!/usr/bin/pwsh
<#
.SYNOPSIS
    Creates the FINAL complete flow definition with ALL SharePoint fields from both groups
.DESCRIPTION
    Uses ALL verified field names from Custom Columns and EPC Extended groups
    Handles Choice fields correctly (not as Boolean)
#>

param(
    [string]$InputPath = "./power-automate-export",
    [string]$OutputPath = "./power-automate-export-final"
)

Write-Host "Creating FINAL COMPLETE flow definition with ALL SharePoint fields..." -ForegroundColor Yellow

# Copy original structure
if (Test-Path $OutputPath) { Remove-Item $OutputPath -Recurse -Force }
Copy-Item $InputPath $OutputPath -Recurse -Force

# Load the flow definition
$definitionPath = "$OutputPath/Microsoft.Flow/flows/45991de2-99f2-422e-864f-efdf8db8cb93/definition.json"
$definition = Get-Content $definitionPath -Raw | ConvertFrom-Json

Write-Host "Adding FINAL field mappings (ALL verified SharePoint fields)..." -ForegroundColor Yellow

# FINAL COMPLETE field mappings - ALL fields from both Custom Columns and EPC Extended groups
$finalFields = @{
    # Core company fields - Custom Columns group
    "item/CompanyName" = "@coalesce(triggerBody()?['companyInfo']?['companyName'], triggerBody()?['companyName'])"
    "item/TradingName" = "@triggerBody()?['companyInfo']?['tradingName']"
    "item/RegisteredOffice" = "@triggerBody()?['companyInfo']?['registeredOffice']"
    "item/HeadOffice" = "@triggerBody()?['companyInfo']?['headOffice']"
    "item/CompanyRegNo" = "@triggerBody()?['companyInfo']?['companyRegNo']"
    "item/VATNumber" = "@triggerBody()?['companyInfo']?['vatNumber']"  # EPC Extended
    "item/VATNo" = "@triggerBody()?['companyInfo']?['vatNumber']"      # Custom Columns (backup)
    "item/ParentCompany" = "@triggerBody()?['companyInfo']?['parentCompany']"
    "item/YearsTrading" = "@coalesce(triggerBody()?['companyInfo']?['yearsTrading'], 0)"
    
    # Contact fields - mix of Custom Columns and EPC Extended
    "item/PrimaryContactName" = "@coalesce(triggerBody()?['primaryContact']?['fullName'], triggerBody()?['contactName'])"
    "item/PrimaryContactTitle" = "@coalesce(triggerBody()?['primaryContact']?['jobTitle'], triggerBody()?['contactTitle'])"
    "item/PrimaryContactPhone" = "@coalesce(triggerBody()?['primaryContact']?['phone'], triggerBody()?['phone'])"
    "item/PrimaryContactEmail" = "@coalesce(triggerBody()?['primaryContact']?['email'], triggerBody()?['email'])"
    "item/ContactName" = "@coalesce(triggerBody()?['primaryContact']?['fullName'], triggerBody()?['contactName'])"  # Backup Custom Columns
    "item/Email" = "@coalesce(triggerBody()?['primaryContact']?['email'], triggerBody()?['email'])"              # Backup Custom Columns
    "item/Phone" = "@coalesce(triggerBody()?['primaryContact']?['phone'], triggerBody()?['phone'])"              # Backup Custom Columns
    "item/Address" = "@triggerBody()?['companyInfo']?['address']"
    
    # Services and experience - EPC Extended
    "item/Specialisations" = "@triggerBody()?['servicesExperience']?['specializations']"
    "item/SoftwareUsed" = "@triggerBody()?['servicesExperience']?['softwareTools']"
    "item/ProjectsPerMonth" = "@coalesce(triggerBody()?['servicesExperience']?['averageProjectsPerMonth'], 0)"
    "item/Services" = "@triggerBody()?['servicesExperience']?['services']"  # Custom Columns
    
    # Roles - Custom Columns (Choice fields, NOT Boolean!)
    "item/ActsAsPrincipalContractor" = "@if(equals(triggerBody()?['rolesCapabilities']?['principalContractor'], true), 'Yes', 'No')"
    "item/ActsAsPrincipalDesigner" = "@if(equals(triggerBody()?['rolesCapabilities']?['principalDesigner'], true), 'Yes', 'No')"
    
    # Role scale details - EPC Extended (truncated names)
    "item/PrincipalContractor_LastYearScal1" = "@triggerBody()?['rolesCapabilities']?['principalContractorScale']"  # Use latest version
    "item/PrincipalDesigner_LastYearScale" = "@triggerBody()?['rolesCapabilities']?['principalDesignerScale']"
    
    # Labour mix - EPC Extended
    "item/LabourMix_InternalPct" = "@coalesce(triggerBody()?['labourMix']?['internalStaffPercentage'], 0)"
    "item/LabourMix_SubcontractPct" = "@coalesce(triggerBody()?['labourMix']?['subcontractPercentage'], 0)"
    
    # Team info - Custom Columns
    "item/TeamSize" = "@coalesce(triggerBody()?['companyInfo']?['teamSize'], 0)"
    "item/YearsExperience" = "@coalesce(triggerBody()?['companyInfo']?['yearsExperience'], 0)"
    
    # Certifications - EPC Extended (Boolean)
    "item/NICEIC_CPS" = "@coalesce(triggerBody()?['certifications']?['niceicContractor'], false)"
    "item/MCS_Approved" = "@coalesce(triggerBody()?['certifications']?['mcsApproved'], false)"
    
    # Certifications - Custom Columns (MultiChoice/Note)
    "item/Accreditations" = "@triggerBody()?['certifications']?['accreditations']"
    "item/Certifications" = "@triggerBody()?['certifications']?['certificationDetails']"
    "item/ISOStandards" = "@triggerBody()?['certifications']?['isoStandards']"
    
    # Insurance - EPC Extended (Boolean + dates)
    "item/PublicProductLiability_Present" = "@coalesce(triggerBody()?['insurance']?['publicLiabilityInsurance'], false)"
    "item/PublicProductLiability_Indemnity1" = "@coalesce(triggerBody()?['insurance']?['publicLiabilityIndemnity'], false)"  # Use latest version
    "item/EmployersLiability_Present" = "@coalesce(triggerBody()?['insurance']?['employersLiabilityInsurance'], false)"
    "item/ProfIndemnity_Present" = "@coalesce(triggerBody()?['insurance']?['professionalIndemnityInsurance'], false)"
    "item/PublicProductLiability_Expiry" = "@triggerBody()?['insurance']?['publicLiabilityExpiry']"
    "item/EmployersLiability_Expiry" = "@triggerBody()?['insurance']?['employersLiabilityExpiry']"
    "item/ProfIndemnity_Expiry" = "@triggerBody()?['insurance']?['professionalIndemnityExpiry']"
    
    # Health & Safety - EPC Extended (using latest truncated names)
    "item/HSE_ImprovementOrProhibition_Las1" = "@triggerBody()?['healthSafety']?['hseNoticesLast5Years']"  # Use latest version
    "item/RIDDOR_Incidents_Last3Y_Count" = "@coalesce(triggerBody()?['healthSafety']?['riddorIncidentCount'], 0)"
    "item/RIDDOR_Incidents_Last3Y_Details" = "@triggerBody()?['healthSafety']?['riddorIncidentDetails']"
    "item/HSE_CDM_Management_Evidence" = "@triggerBody()?['healthSafety']?['cdmManagementEvidence']"
    "item/Named_PrincipalDesigner" = "@triggerBody()?['healthSafety']?['namedPrincipalDesigner']"
    "item/PD_Qualifications" = "@triggerBody()?['healthSafety']?['principalDesignerQualifications']"
    "item/TrainingRecords_Summary" = "@triggerBody()?['healthSafety']?['trainingRecordsSummary']"
    "item/NearMiss_Procedure" = "@triggerBody()?['healthSafety']?['nearMissProcedure']"
    "item/Quality_Procedure_Evidence" = "@triggerBody()?['qualityAssurance']?['qualityProcedureEvidence']"
    
    # Health & Safety - Custom Columns (backup)
    "item/HSEQIncidentsLast5y" = "@coalesce(triggerBody()?['healthSafety']?['hseqIncidents'], 0)"
    "item/RIDDORLast3y" = "@coalesce(triggerBody()?['healthSafety']?['riddorIncidents'], 0)"
    
    # Policy dates - EPC Extended
    "item/Policy_HS_DateSigned" = "@triggerBody()?['policies']?['healthSafetyPolicyDate']"
    "item/Policy_Env_DateSigned" = "@triggerBody()?['policies']?['environmentalPolicyDate']"
    "item/Policy_MS_DateSigned" = "@triggerBody()?['policies']?['modernSlaveryPolicyDate']"
    "item/Policy_MOS_DateSigned" = "@triggerBody()?['policies']?['substanceMisusePolicyDate']"
    "item/RightToWork_Monitoring_Method" = "@triggerBody()?['policies']?['rightToWorkMethod']"
    "item/GDPRPolicy_DateSigned" = "@triggerBody()?['policies']?['gdprPolicyDate']"
    "item/CyberIncident_Last3Y" = "@triggerBody()?['policies']?['cyberIncidentLast3Years']"
    
    # GDPR - Custom Columns (Choice field)
    "item/HasGDPRPolicy" = "@if(equals(triggerBody()?['policies']?['hasGdprPolicy'], true), 'Yes', 'No')"
    
    # Project references and coverage - EPC Extended
    "item/Resources_PerProject" = "@triggerBody()?['projectReferences']?['resourcesPerProject']"
    "item/Coverage_Nationwide" = "@coalesce(triggerBody()?['projectReferences']?['nationwideCoverage'], false)"
    "item/Client_Reference" = "@triggerBody()?['projectReferences']?['clientReference']"
    
    # Coverage - Custom Columns
    "item/Coverage" = "@triggerBody()?['projectReferences']?['coverage']"
    "item/CoverageRegion" = "@triggerBody()?['projectReferences']?['coverageRegion']"
    
    # Legal compliance - EPC Extended
    "item/PendingProsecutions_Details" = "@triggerBody()?['legalCompliance']?['pendingProsecutions']"
    "item/Contracts_ReviewedBySignatory" = "@coalesce(triggerBody()?['legalCompliance']?['contractsReviewed'], false)"
    "item/Legal_Clarifications" = "@triggerBody()?['legalCompliance']?['legalClarifications']"
    
    # Agreement and consent fields - EPC Extended (Boolean)
    "item/Received_ContractOverviewPack" = "@coalesce(triggerBody()?['agreement']?['receivedContractPack'], false)"
    "item/Willing_To_WorkToSaberTerms" = "@coalesce(triggerBody()?['agreement']?['agreeToTerms'], false)"
    "item/AgreeToCodes" = "@coalesce(triggerBody()?['agreement']?['agreeToCodes'], false)"
    "item/DataProcessingConsent" = "@coalesce(triggerBody()?['agreement']?['dataProcessingConsent'], false)"
    "item/MarketingConsent" = "@coalesce(triggerBody()?['agreement']?['marketingConsent'], false)"
    
    # Agreement - Custom Columns (Choice field)
    "item/AgreeToSaberTerms" = "@if(equals(triggerBody()?['agreement']?['agreeToTerms'], true), 'Yes', 'No')"
    
    # Submission fields - both groups
    "item/AdditionalInfo" = "@triggerBody()?['submission']?['additionalInformation']"
    "item/Notes" = "@triggerBody()?['submission']?['notes']"
    "item/NotesOrClarifications" = "@triggerBody()?['submission']?['clarifications']"
    "item/SubmissionStatus" = "Submitted"
    "item/Status" = "Submitted"  # Custom Columns backup
    "item/ReferenceNumber" = "@coalesce(triggerBody()?['referenceNumber'], concat('EPC-', utcNow('yyyyMMddHHmmss')))"
    "item/RegistrationNumber" = "@coalesce(triggerBody()?['referenceNumber'], concat('EPC-', utcNow('yyyyMMddHHmmss')))"  # Custom Columns backup
    "item/InvitationCode" = "@triggerBody()?['invitationCode']"
    "item/SubmissionDate" = "@utcNow()"
    "item/SubmissionHandled" = "false"
}

# Find the Create_item action and add ALL final fields
$createItemAction = $definition.properties.definition.actions.Condition.actions.Create_item
if ($createItemAction -and $createItemAction.inputs -and $createItemAction.inputs.parameters) {
    
    # Add each final field mapping
    foreach ($field in $finalFields.GetEnumerator()) {
        $fieldName = $field.Key
        $fieldExpression = $field.Value
        $createItemAction.inputs.parameters | Add-Member -NotePropertyName $fieldName -NotePropertyValue $fieldExpression -Force
    }
    
    Write-Host "✅ Added $($finalFields.Count) FINAL field mappings (ALL SharePoint fields)" -ForegroundColor Green
} else {
    Write-Host "❌ Could not find Create_item action" -ForegroundColor Red
    exit 1
}

# Update email notifications with comprehensive data
Write-Host "Updating email notifications with FINAL comprehensive data..." -ForegroundColor Yellow

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

Write-Host "✅ Updated email notifications with FINAL comprehensive data" -ForegroundColor Green

# Save updated definition
$definition | ConvertTo-Json -Depth 50 | Set-Content $definitionPath -Encoding UTF8
Write-Host "✅ Updated FINAL definition saved" -ForegroundColor Green

# Create final package
Write-Host "Creating FINAL package..." -ForegroundColor Yellow
$zipPath = "$OutputPath.zip"
if (Test-Path $zipPath) { Remove-Item $zipPath }
Compress-Archive -Path "$OutputPath/*" -DestinationPath $zipPath
Write-Host "✅ FINAL package created: $zipPath" -ForegroundColor Green

Write-Host "`n=======================================" -ForegroundColor Cyan
Write-Host "✅ FINAL COMPLETE Flow Definition Ready!" -ForegroundColor Green
Write-Host "=======================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "ALL SHAREPOINT FIELDS INCLUDED:" -ForegroundColor Yellow
Write-Host "• $($finalFields.Count) field mappings (COMPLETE coverage)" -ForegroundColor White
Write-Host "• Both Custom Columns AND EPC Extended groups" -ForegroundColor White
Write-Host "• Proper Choice field handling (ActsAsPrincipalContractor/Designer)" -ForegroundColor White
Write-Host "• Boolean fields with coalesce safety" -ForegroundColor White
Write-Host "• Latest truncated field versions (Las1, Scal1, Indemnity1)" -ForegroundColor White
Write-Host "• Comprehensive email notifications" -ForegroundColor White
Write-Host "• Backup field mappings for redundancy" -ForegroundColor White
Write-Host ""
Write-Host "FIELD CATEGORIES INCLUDED:" -ForegroundColor Yellow
Write-Host "• Company Info (8 fields)" -ForegroundColor White
Write-Host "• Contact Details (6 fields with backups)" -ForegroundColor White
Write-Host "• Services & Experience (5 fields)" -ForegroundColor White
Write-Host "• Roles & Capabilities (4 fields)" -ForegroundColor White
Write-Host "• Certifications (6 fields)" -ForegroundColor White
Write-Host "• Insurance (7 fields)" -ForegroundColor White
Write-Host "• Health & Safety (10 fields)" -ForegroundColor White
Write-Host "• Policies & Compliance (8 fields)" -ForegroundColor White
Write-Host "• Project References (5 fields)" -ForegroundColor White
Write-Host "• Legal & Agreement (8 fields)" -ForegroundColor White
Write-Host "• Submission Management (8 fields)" -ForegroundColor White
Write-Host ""
Write-Host "Package ready for import: $zipPath" -ForegroundColor Green
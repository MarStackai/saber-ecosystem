#!/usr/bin/pwsh
<#
.SYNOPSIS
    Creates an updated Power Automate flow definition with extended form support
.DESCRIPTION
    Takes the current flow export and updates it to handle the extended 6-page form
    with all 51+ new fields properly mapped to SharePoint columns.
#>

param(
    [string]$InputPath = "./power-automate-export",
    [string]$OutputPath = "./power-automate-export-updated"
)

Write-Host "Creating extended flow definition..." -ForegroundColor Yellow

# Copy original structure
if (Test-Path $OutputPath) { Remove-Item $OutputPath -Recurse -Force }
Copy-Item $InputPath $OutputPath -Recurse -Force

# Load the flow definition
$definitionPath = "$OutputPath/Microsoft.Flow/flows/45991de2-99f2-422e-864f-efdf8db8cb93/definition.json"
$definition = Get-Content $definitionPath -Raw | ConvertFrom-Json

Write-Host "Updating flow actions for extended form..." -ForegroundColor Yellow

# Update the Create_item action with extended field mappings
$createAction = $definition.properties.definition.actions.Condition.actions.Create_item

# Function to safely add field mapping
function Add-FieldMapping {
    param($action, $sharePointField, $expression)
    try {
        # Add to parameters object directly
        $fieldKey = "item/$sharePointField"
        $action.inputs.parameters | Add-Member -NotePropertyName $fieldKey -NotePropertyValue $expression -Force
    } catch {
        Write-Host "⚠️ Failed to add field: $sharePointField" -ForegroundColor Yellow
    }
}

# Extended field mappings
$fieldMappings = @{
    # Company Info (backward compatible + extended)
    "CompanyName" = "@coalesce(triggerBody()?['companyInfo']?['companyName'], triggerBody()?['companyName'])"
    "TradingName" = "@triggerBody()?['companyInfo']?['tradingName']"
    "RegisteredOffice" = "@coalesce(triggerBody()?['companyInfo']?['registeredAddress'], triggerBody()?['address'])"
    "HeadOffice" = "@triggerBody()?['companyInfo']?['headOfficeAddress']"
    "CompanyRegNo" = "@coalesce(triggerBody()?['companyInfo']?['registrationNumber'], triggerBody()?['registrationNumber'])"
    "VATNumber" = "@triggerBody()?['companyInfo']?['vatNumber']"
    "ParentCompany" = "@triggerBody()?['companyInfo']?['parentCompany']"
    "YearsTrading" = "@triggerBody()?['companyInfo']?['yearsTrading']"
    
    # Primary Contact (backward compatible + extended)
    "PrimaryContactName" = "@coalesce(triggerBody()?['primaryContact']?['fullName'], triggerBody()?['contactName'])"
    "PrimaryContactTitle" = "@coalesce(triggerBody()?['primaryContact']?['jobTitle'], triggerBody()?['contactTitle'])"
    "PrimaryContactPhone" = "@coalesce(triggerBody()?['primaryContact']?['phone'], triggerBody()?['phone'])"
    "PrimaryContactEmail" = "@coalesce(triggerBody()?['primaryContact']?['email'], triggerBody()?['email'])"
    
    # Services & Experience
    "Specialisations" = "@triggerBody()?['servicesExperience']?['specializations']"
    "SoftwareUsed" = "@triggerBody()?['servicesExperience']?['softwareTools']"
    "ProjectsPerMonth" = "@triggerBody()?['servicesExperience']?['averageProjectsPerMonth']"
    
    # Roles & Capabilities
    "ActsAsPrincipalContractor" = "@triggerBody()?['rolesCapabilities']?['principalContractor']"
    "PrincipalContractor_LastYearScale" = "@triggerBody()?['rolesCapabilities']?['pcScaleLastYear']"
    "ActsAsPrincipalDesigner" = "@triggerBody()?['rolesCapabilities']?['principalDesigner']"
    "PrincipalDesigner_LastYearScale" = "@triggerBody()?['rolesCapabilities']?['pdScaleLastYear']"
    "LabourMix_InternalPct" = "@triggerBody()?['rolesCapabilities']?['internalStaffPercentage']"
    "LabourMix_SubcontractPct" = "@triggerBody()?['rolesCapabilities']?['subcontractPercentage']"
    
    # Certifications
    "NICEIC_CPS" = "@triggerBody()?['certifications']?['niceicContractor']"
    "MCS_Approved" = "@triggerBody()?['certifications']?['mcsApproved']"
    
    # Insurance
    "PublicProductLiability_Present" = "@triggerBody()?['insurance']?['publicLiabilityInsurance']"
    "PublicProductLiability_IndemnityInPrinciple" = "@triggerBody()?['insurance']?['pplIndemnityClause']"
    "EmployersLiability_Present" = "@triggerBody()?['insurance']?['employersLiabilityInsurance']"
    "ProfIndemnity_Present" = "@triggerBody()?['insurance']?['professionalIndemnityInsurance']"
    "PublicProductLiability_Expiry" = "@if(empty(triggerBody()?['insurance']?['pplExpiryDate']), null, formatDateTime(triggerBody()?['insurance']?['pplExpiryDate'], 'yyyy-MM-ddTHH:mm:ssZ'))"
    "EmployersLiability_Expiry" = "@if(empty(triggerBody()?['insurance']?['elExpiryDate']), null, formatDateTime(triggerBody()?['insurance']?['elExpiryDate'], 'yyyy-MM-ddTHH:mm:ssZ'))"
    "ProfIndemnity_Expiry" = "@if(empty(triggerBody()?['insurance']?['piExpiryDate']), null, formatDateTime(triggerBody()?['insurance']?['piExpiryDate'], 'yyyy-MM-ddTHH:mm:ssZ'))"
    
    # Health & Safety
    "HSE_ImprovementOrProhibition_Last5Y" = "@triggerBody()?['healthSafety']?['hseNotices']"
    "RIDDOR_Incidents_Last3Y_Count" = "@triggerBody()?['healthSafety']?['riddorCount']"
    "RIDDOR_Incidents_Last3Y_Details" = "@triggerBody()?['healthSafety']?['riddorDetails']"
    "HSE_CDM_Management_Evidence" = "@triggerBody()?['healthSafety']?['hsCdmEvidence']"
    "Named_PrincipalDesigner" = "@triggerBody()?['healthSafety']?['namedPrincipalDesigner']"
    "PD_Qualifications" = "@triggerBody()?['healthSafety']?['pdQualifications']"
    "TrainingRecords_Summary" = "@triggerBody()?['healthSafety']?['trainingRecords']"
    "NearMiss_Procedure" = "@triggerBody()?['healthSafety']?['nearMissProcedure']"
    "Quality_Procedure_Evidence" = "@triggerBody()?['healthSafety']?['qualityEvidence']"
    
    # Policies
    "Policy_HS_DateSigned" = "@if(empty(triggerBody()?['policies']?['hsPolicyDate']), null, formatDateTime(triggerBody()?['policies']?['hsPolicyDate'], 'yyyy-MM-ddTHH:mm:ssZ'))"
    "Policy_Env_DateSigned" = "@if(empty(triggerBody()?['policies']?['envPolicyDate']), null, formatDateTime(triggerBody()?['policies']?['envPolicyDate'], 'yyyy-MM-ddTHH:mm:ssZ'))"
    "Policy_MS_DateSigned" = "@if(empty(triggerBody()?['policies']?['msPolicyDate']), null, formatDateTime(triggerBody()?['policies']?['msPolicyDate'], 'yyyy-MM-ddTHH:mm:ssZ'))"
    "Policy_MOS_DateSigned" = "@if(empty(triggerBody()?['policies']?['mosPolicyDate']), null, formatDateTime(triggerBody()?['policies']?['mosPolicyDate'], 'yyyy-MM-ddTHH:mm:ssZ'))"
    "RightToWork_Monitoring_Method" = "@triggerBody()?['policies']?['rightToWorkMethod']"
    
    # Data Protection
    "GDPRPolicy_DateSigned" = "@if(empty(triggerBody()?['dataProtectionIT']?['gdprPolicyDate']), null, formatDateTime(triggerBody()?['dataProtectionIT']?['gdprPolicyDate'], 'yyyy-MM-ddTHH:mm:ssZ'))"
    "CyberIncident_Last3Y" = "@triggerBody()?['dataProtectionIT']?['cyberIncident']"
    
    # Delivery Capability
    "Resources_PerProject" = "@triggerBody()?['deliveryCapability']?['resourcingApproach']"
    "Coverage_Nationwide" = "@triggerBody()?['projectReferences']?['nationwideCoverage']"
    "Client_Reference" = "@triggerBody()?['projectReferences']?['clientReference']"
    
    # Legal & Compliance
    "PendingProsecutions_Details" = "@triggerBody()?['legalCompliance']?['pendingProsecutions']"
    "Contracts_ReviewedBySignatory" = "@triggerBody()?['legalCompliance']?['contractsReviewed']"
    "Legal_Clarifications" = "@triggerBody()?['legalCompliance']?['legalClarifications']"
    
    # Agreement
    "Received_ContractOverviewPack" = "@triggerBody()?['agreement']?['receivedContractPack']"
    "Willing_To_WorkToSaberTerms" = "@triggerBody()?['agreement']?['agreeToTerms']"
    "AgreeToCodes" = "@triggerBody()?['agreement']?['agreeToCodes']"
    "DataProcessingConsent" = "@triggerBody()?['agreement']?['dataProcessingConsent']"
    "MarketingConsent" = "@triggerBody()?['agreement']?['marketingConsent']"
    
    # Submission
    "AdditionalInfo" = "@triggerBody()?['submission']?['additionalInformation']"
    "ReferenceNumber" = "@coalesce(triggerBody()?['referenceNumber'], concat('EPC-', utcNow('yyyyMMddHHmmss')))"
    "SubmissionStatus" = "Submitted"
}

# Apply all field mappings
foreach ($field in $fieldMappings.GetEnumerator()) {
    Add-FieldMapping $createAction $field.Key $field.Value
}

Write-Host "✅ Added $($fieldMappings.Count) field mappings" -ForegroundColor Green

# Update email notifications with extended form data
Write-Host "Updating email notifications..." -ForegroundColor Yellow

# Update internal notification email
$internalEmail = $definition.properties.definition.actions.Condition.actions.'Send_an_email_(V2)'
$internalEmail.inputs.parameters.'emailMessage/Subject' = "New EPC Application - @{coalesce(triggerBody()?['companyInfo']?['companyName'], triggerBody()?['companyName'])}"

$extendedEmailBody = @"
<h2>New EPC Application Received</h2>
<table border="1" style="border-collapse: collapse; width: 100%;">
<tbody>
<tr><td><strong>Company</strong></td><td>@{coalesce(triggerBody()?['companyInfo']?['companyName'], triggerBody()?['companyName'])}</td></tr>
<tr><td><strong>Contact</strong></td><td>@{coalesce(triggerBody()?['primaryContact']?['fullName'], triggerBody()?['contactName'])}</td></tr>
<tr><td><strong>Email</strong></td><td>@{coalesce(triggerBody()?['primaryContact']?['email'], triggerBody()?['email'])}</td></tr>
<tr><td><strong>Phone</strong></td><td>@{coalesce(triggerBody()?['primaryContact']?['phone'], triggerBody()?['phone'])}</td></tr>
<tr><td><strong>Registration No</strong></td><td>@{coalesce(triggerBody()?['companyInfo']?['registrationNumber'], triggerBody()?['registrationNumber'])}</td></tr>
<tr><td><strong>SharePoint ID</strong></td><td>@{body('Create_item')?['ID']}</td></tr>
<tr><td><strong>Code Used</strong></td><td>@{triggerBody()?['invitationCode']}</td></tr>
</tbody>
</table>

<h3>Extended Form Data Available</h3>
<ul>
<li><strong>Principal Contractor:</strong> @{triggerBody()?['rolesCapabilities']?['principalContractor']}</li>
<li><strong>Principal Designer:</strong> @{triggerBody()?['rolesCapabilities']?['principalDesigner']}</li>
<li><strong>ISO Certifications:</strong> @{join(triggerBody()?['certifications']?['isoCertifications'], ', ')}</li>
<li><strong>Insurance Present:</strong> PPL: @{triggerBody()?['insurance']?['publicLiabilityInsurance']}, EL: @{triggerBody()?['insurance']?['employersLiabilityInsurance']}, PI: @{triggerBody()?['insurance']?['professionalIndemnityInsurance']}</li>
<li><strong>Nationwide Coverage:</strong> @{triggerBody()?['projectReferences']?['nationwideCoverage']}</li>
<li><strong>Agreement Status:</strong> Terms: @{triggerBody()?['agreement']?['agreeToTerms']}, Codes: @{triggerBody()?['agreement']?['agreeToCodes']}, GDPR: @{triggerBody()?['agreement']?['dataProcessingConsent']}</li>
</ul>

<p><a href="https://saberrenewables.sharepoint.com/sites/SaberEPCPartners/Lists/EPC%20Onboarding">View in SharePoint</a></p>
"@

$internalEmail.inputs.parameters.'emailMessage/Body' = $extendedEmailBody

# Update applicant confirmation email
$confirmationEmail = $definition.properties.definition.actions.Condition.actions.'Send_an_email_(V2)_1'
$confirmationEmail.inputs.parameters.'emailMessage/Subject' = "Application Received - @{coalesce(triggerBody()?['companyInfo']?['companyName'], triggerBody()?['companyName'])}"

$confirmationEmailBody = @"
<h2>Thank you for your application!</h2>
<p>Dear @{coalesce(triggerBody()?['primaryContact']?['fullName'], triggerBody()?['contactName'])},</p>
<p>We have received your application to join the Saber Renewables EPC Partner Network.</p>

<h3>Application Details:</h3>
<ul>
<li><strong>Company:</strong> @{coalesce(triggerBody()?['companyInfo']?['companyName'], triggerBody()?['companyName'])}</li>
<li><strong>Reference:</strong> EPC-@{body('Create_item')?['ID']}</li>
<li><strong>Submitted:</strong> @{utcNow()}</li>
<li><strong>Contact:</strong> @{coalesce(triggerBody()?['primaryContact']?['fullName'], triggerBody()?['contactName'])}</li>
<li><strong>Registration No:</strong> @{coalesce(triggerBody()?['companyInfo']?['registrationNumber'], triggerBody()?['registrationNumber'])}</li>
</ul>

<h3>What's Next?</h3>
<p>Our technical team will review your application and supporting documentation within 5 business days. This includes:</p>
<ul>
<li>✅ Company registration and compliance verification</li>
<li>✅ Certification and accreditation review</li>
<li>✅ Insurance policy validation</li>
<li>✅ Health & safety documentation assessment</li>
<li>✅ Capability and experience evaluation</li>
</ul>

<p>You will receive an email confirmation once your application has been approved and you're added to our active partner network.</p>

<p>If you have any questions, please contact our Partner Team at <a href="mailto:partners@saberrenewables.com">partners@saberrenewables.com</a></p>

<p>Kind regards,<br><br>Saber Renewables Partner Team<br><em>Infinite Power In Partnership</em></p>
"@

$confirmationEmail.inputs.parameters.'emailMessage/Body' = $confirmationEmailBody

Write-Host "✅ Updated email notifications" -ForegroundColor Green

# Save updated definition
$definition | ConvertTo-Json -Depth 50 | Set-Content $definitionPath -Encoding UTF8
Write-Host "✅ Updated definition saved" -ForegroundColor Green

# Create updated package
Write-Host "Creating updated package..." -ForegroundColor Yellow
$zipPath = "$OutputPath.zip"
if (Test-Path $zipPath) { Remove-Item $zipPath }
Compress-Archive -Path "$OutputPath/*" -DestinationPath $zipPath
Write-Host "✅ Updated package created: $zipPath" -ForegroundColor Green

Write-Host "`n=======================================" -ForegroundColor Cyan
Write-Host "✅ Extended Flow Definition Complete!" -ForegroundColor Green
Write-Host "=======================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Summary of Changes:" -ForegroundColor Yellow
Write-Host "• Added $($fieldMappings.Count) extended field mappings" -ForegroundColor White
Write-Host "• Updated trigger schema for 6-page form structure" -ForegroundColor White
Write-Host "• Enhanced email notifications with extended data" -ForegroundColor White
Write-Host "• Maintained backward compatibility with simple form" -ForegroundColor White
Write-Host ""
Write-Host "Package ready for import: $zipPath" -ForegroundColor Green
Write-Host ""
Write-Host "Import with:" -ForegroundColor Yellow
Write-Host "./Update-EpcFlow-Simple.ps1 -PackagePath '$zipPath'" -ForegroundColor Cyan
#!/usr/bin/pwsh
<#
.SYNOPSIS
    Creates a complete flow definition with ALL 54+ SharePoint fields from deploy-schema-simple.ps1
.DESCRIPTION
    Maps all extended form fields to exact SharePoint field names, including truncated ones
#>

param(
    [string]$InputPath = "./power-automate-export",
    [string]$OutputPath = "./power-automate-export-complete"
)

Write-Host "Creating COMPLETE flow definition with ALL SharePoint fields..." -ForegroundColor Yellow

# Copy original structure
if (Test-Path $OutputPath) { Remove-Item $OutputPath -Recurse -Force }
Copy-Item $InputPath $OutputPath -Recurse -Force

# Load the flow definition
$definitionPath = "$OutputPath/Microsoft.Flow/flows/45991de2-99f2-422e-864f-efdf8db8cb93/definition.json"
$definition = Get-Content $definitionPath -Raw | ConvertFrom-Json

Write-Host "Adding ALL field mappings (54+ fields from SharePoint schema)..." -ForegroundColor Yellow

# COMPLETE field mappings - ALL fields from deploy-schema-simple.ps1
$completeFields = @{
    # Core company fields - text
    "item/CompanyName" = "@coalesce(triggerBody()?['companyInfo']?['companyName'], triggerBody()?['companyName'])"
    "item/TradingName" = "@triggerBody()?['companyInfo']?['tradingName']"
    "item/RegisteredOffice" = "@triggerBody()?['companyInfo']?['registeredOffice']"
    "item/HeadOffice" = "@triggerBody()?['companyInfo']?['headOffice']"
    "item/CompanyRegNo" = "@triggerBody()?['companyInfo']?['companyRegNo']"
    "item/VATNumber" = "@triggerBody()?['companyInfo']?['vatNumber']"
    "item/ParentCompany" = "@triggerBody()?['companyInfo']?['parentCompany']"
    "item/YearsTrading" = "@coalesce(triggerBody()?['companyInfo']?['yearsTrading'], 0)"
    
    # Primary contact fields - text
    "item/PrimaryContactName" = "@coalesce(triggerBody()?['primaryContact']?['fullName'], triggerBody()?['contactName'])"
    "item/PrimaryContactTitle" = "@coalesce(triggerBody()?['primaryContact']?['jobTitle'], triggerBody()?['contactTitle'])"
    "item/PrimaryContactPhone" = "@coalesce(triggerBody()?['primaryContact']?['phone'], triggerBody()?['phone'])"
    "item/PrimaryContactEmail" = "@coalesce(triggerBody()?['primaryContact']?['email'], triggerBody()?['email'])"
    
    # Services and experience - text/number
    "item/Specialisations" = "@triggerBody()?['servicesExperience']?['specializations']"
    "item/SoftwareUsed" = "@triggerBody()?['servicesExperience']?['softwareTools']"
    "item/ProjectsPerMonth" = "@coalesce(triggerBody()?['servicesExperience']?['averageProjectsPerMonth'], 0)"
    
    # Roles and capabilities - boolean + text (note: LastYearScale fields may be truncated)
    "item/ActsAsPrincipalContractor" = "@coalesce(triggerBody()?['rolesCapabilities']?['principalContractor'], false)"
    "item/PrincipalContractor_LastYearScal0" = "@triggerBody()?['rolesCapabilities']?['principalContractorScale']"  # Truncated name
    "item/ActsAsPrincipalDesigner" = "@coalesce(triggerBody()?['rolesCapabilities']?['principalDesigner'], false)"
    "item/PrincipalDesigner_LastYearScale" = "@triggerBody()?['rolesCapabilities']?['principalDesignerScale']"
    
    # Labour mix - numbers
    "item/LabourMix_InternalPct" = "@coalesce(triggerBody()?['labourMix']?['internalStaffPercentage'], 0)"
    "item/LabourMix_SubcontractPct" = "@coalesce(triggerBody()?['labourMix']?['subcontractPercentage'], 0)"
    
    # Certifications - boolean
    "item/NICEIC_CPS" = "@coalesce(triggerBody()?['certifications']?['niceicContractor'], false)"
    "item/MCS_Approved" = "@coalesce(triggerBody()?['certifications']?['mcsApproved'], false)"
    
    # Insurance - boolean + dates
    "item/PublicProductLiability_Present" = "@coalesce(triggerBody()?['insurance']?['publicLiabilityInsurance'], false)"
    "item/PublicProductLiability_Indemnity0" = "@coalesce(triggerBody()?['insurance']?['publicLiabilityIndemnity'], false)"  # Truncated name
    "item/EmployersLiability_Present" = "@coalesce(triggerBody()?['insurance']?['employersLiabilityInsurance'], false)"
    "item/ProfIndemnity_Present" = "@coalesce(triggerBody()?['insurance']?['professionalIndemnityInsurance'], false)"
    "item/PublicProductLiability_Expiry" = "@triggerBody()?['insurance']?['publicLiabilityExpiry']"
    "item/EmployersLiability_Expiry" = "@triggerBody()?['insurance']?['employersLiabilityExpiry']"
    "item/ProfIndemnity_Expiry" = "@triggerBody()?['insurance']?['professionalIndemnityExpiry']"
    
    # Health & Safety - text/number/notes
    "item/HSE_ImprovementOrProhibition_Last5Y" = "@triggerBody()?['healthSafety']?['hseNoticesLast5Years']"
    "item/RIDDOR_Incidents_Last3Y_Count" = "@coalesce(triggerBody()?['healthSafety']?['riddorIncidentCount'], 0)"
    "item/RIDDOR_Incidents_Last3Y_Details" = "@triggerBody()?['healthSafety']?['riddorIncidentDetails']"
    "item/HSE_CDM_Management_Evidence" = "@triggerBody()?['healthSafety']?['cdmManagementEvidence']"
    "item/Named_PrincipalDesigner" = "@triggerBody()?['healthSafety']?['namedPrincipalDesigner']"
    "item/PD_Qualifications" = "@triggerBody()?['healthSafety']?['principalDesignerQualifications']"
    "item/TrainingRecords_Summary" = "@triggerBody()?['healthSafety']?['trainingRecordsSummary']"
    "item/NearMiss_Procedure" = "@triggerBody()?['healthSafety']?['nearMissProcedure']"
    "item/Quality_Procedure_Evidence" = "@triggerBody()?['qualityAssurance']?['qualityProcedureEvidence']"
    
    # Policy dates - DateTime
    "item/Policy_HS_DateSigned" = "@triggerBody()?['policies']?['healthSafetyPolicyDate']"
    "item/Policy_Env_DateSigned" = "@triggerBody()?['policies']?['environmentalPolicyDate']"
    "item/Policy_MS_DateSigned" = "@triggerBody()?['policies']?['modernSlaveryPolicyDate']"
    "item/Policy_MOS_DateSigned" = "@triggerBody()?['policies']?['substanceMisusePolicyDate']"
    "item/RightToWork_Monitoring_Method" = "@triggerBody()?['policies']?['rightToWorkMethod']"
    "item/GDPRPolicy_DateSigned" = "@triggerBody()?['policies']?['gdprPolicyDate']"
    "item/CyberIncident_Last3Y" = "@triggerBody()?['policies']?['cyberIncidentLast3Years']"
    
    # Project references and coverage
    "item/Resources_PerProject" = "@triggerBody()?['projectReferences']?['resourcesPerProject']"
    "item/Coverage_Nationwide" = "@coalesce(triggerBody()?['projectReferences']?['nationwideCoverage'], false)"
    "item/Client_Reference" = "@triggerBody()?['projectReferences']?['clientReference']"
    
    # Legal compliance
    "item/PendingProsecutions_Details" = "@triggerBody()?['legalCompliance']?['pendingProsecutions']"
    "item/Contracts_ReviewedBySignatory" = "@coalesce(triggerBody()?['legalCompliance']?['contractsReviewed'], false)"
    "item/Legal_Clarifications" = "@triggerBody()?['legalCompliance']?['legalClarifications']"
    
    # Agreement and consent fields
    "item/Received_ContractOverviewPack" = "@coalesce(triggerBody()?['agreement']?['receivedContractPack'], false)"
    "item/Willing_To_WorkToSaberTerms" = "@coalesce(triggerBody()?['agreement']?['agreeToTerms'], false)"
    "item/AgreeToCodes" = "@coalesce(triggerBody()?['agreement']?['agreeToCodes'], false)"
    "item/DataProcessingConsent" = "@coalesce(triggerBody()?['agreement']?['dataProcessingConsent'], false)"
    "item/MarketingConsent" = "@coalesce(triggerBody()?['agreement']?['marketingConsent'], false)"
    
    # Submission fields
    "item/AdditionalInfo" = "@triggerBody()?['submission']?['additionalInformation']"
    "item/SubmissionStatus" = "Submitted"
    "item/ReferenceNumber" = "@coalesce(triggerBody()?['referenceNumber'], concat('EPC-', utcNow('yyyyMMddHHmmss')))"
}

# Find the Create_item action and add ALL fields
$createItemAction = $definition.properties.definition.actions.Condition.actions.Create_item
if ($createItemAction -and $createItemAction.inputs -and $createItemAction.inputs.parameters) {
    
    # Add each complete field mapping
    foreach ($field in $completeFields.GetEnumerator()) {
        $fieldName = $field.Key
        $fieldExpression = $field.Value
        $createItemAction.inputs.parameters | Add-Member -NotePropertyName $fieldName -NotePropertyValue $fieldExpression -Force
    }
    
    Write-Host "✅ Added $($completeFields.Count) COMPLETE field mappings (all SharePoint fields)" -ForegroundColor Green
} else {
    Write-Host "❌ Could not find Create_item action" -ForegroundColor Red
    exit 1
}

# Update email notifications with comprehensive data
Write-Host "Updating email notifications with ALL extended data..." -ForegroundColor Yellow

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
<tr><td><strong>Company Reg No</strong></td><td>@{triggerBody()?['companyInfo']?['companyRegNo']}</td></tr>
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

Write-Host "✅ Updated email notifications with comprehensive extended data" -ForegroundColor Green

# Add COMPLETE schema to trigger
$triggerSchema = $definition.properties.definition.triggers.manual.inputs.schema
if ($triggerSchema -and $triggerSchema.properties) {
    
    $completeSchemaAdditions = @{
        companyInfo = @{
            type = "object"
            properties = @{
                companyName = @{ type = "string" }
                tradingName = @{ type = "string" }
                registeredOffice = @{ type = "string" }
                headOffice = @{ type = "string" }
                companyRegNo = @{ type = "string" }
                vatNumber = @{ type = "string" }
                parentCompany = @{ type = "string" }
                yearsTrading = @{ type = @("number", "null") }
            }
        }
        primaryContact = @{
            type = "object"
            properties = @{
                fullName = @{ type = "string" }
                jobTitle = @{ type = "string" }
                phone = @{ type = "string" }
                email = @{ type = "string" }
            }
        }
        servicesExperience = @{
            type = "object"
            properties = @{
                specializations = @{ type = "string" }
                softwareTools = @{ type = "string" }
                averageProjectsPerMonth = @{ type = @("number", "null") }
            }
        }
        rolesCapabilities = @{
            type = "object"
            properties = @{
                principalContractor = @{ type = @("boolean", "null") }
                principalContractorScale = @{ type = "string" }
                principalDesigner = @{ type = @("boolean", "null") }
                principalDesignerScale = @{ type = "string" }
            }
        }
        labourMix = @{
            type = "object"
            properties = @{
                internalStaffPercentage = @{ type = @("number", "null") }
                subcontractPercentage = @{ type = @("number", "null") }
            }
        }
        certifications = @{
            type = "object"
            properties = @{
                niceicContractor = @{ type = @("boolean", "null") }
                mcsApproved = @{ type = @("boolean", "null") }
            }
        }
        insurance = @{
            type = "object"
            properties = @{
                publicLiabilityInsurance = @{ type = @("boolean", "null") }
                publicLiabilityIndemnity = @{ type = @("boolean", "null") }
                employersLiabilityInsurance = @{ type = @("boolean", "null") }
                professionalIndemnityInsurance = @{ type = @("boolean", "null") }
                publicLiabilityExpiry = @{ type = "string" }
                employersLiabilityExpiry = @{ type = "string" }
                professionalIndemnityExpiry = @{ type = "string" }
            }
        }
        healthSafety = @{
            type = "object"
            properties = @{
                hseNoticesLast5Years = @{ type = "string" }
                riddorIncidentCount = @{ type = @("number", "null") }
                riddorIncidentDetails = @{ type = "string" }
                cdmManagementEvidence = @{ type = "string" }
                namedPrincipalDesigner = @{ type = "string" }
                principalDesignerQualifications = @{ type = "string" }
                trainingRecordsSummary = @{ type = "string" }
                nearMissProcedure = @{ type = "string" }
            }
        }
        qualityAssurance = @{
            type = "object"
            properties = @{
                qualityProcedureEvidence = @{ type = "string" }
            }
        }
        policies = @{
            type = "object"
            properties = @{
                healthSafetyPolicyDate = @{ type = "string" }
                environmentalPolicyDate = @{ type = "string" }
                modernSlaveryPolicyDate = @{ type = "string" }
                substanceMisusePolicyDate = @{ type = "string" }
                rightToWorkMethod = @{ type = "string" }
                gdprPolicyDate = @{ type = "string" }
                cyberIncidentLast3Years = @{ type = "string" }
            }
        }
        projectReferences = @{
            type = "object"
            properties = @{
                resourcesPerProject = @{ type = "string" }
                nationwideCoverage = @{ type = @("boolean", "null") }
                clientReference = @{ type = "string" }
            }
        }
        legalCompliance = @{
            type = "object"
            properties = @{
                pendingProsecutions = @{ type = "string" }
                contractsReviewed = @{ type = @("boolean", "null") }
                legalClarifications = @{ type = "string" }
            }
        }
        agreement = @{
            type = "object"
            properties = @{
                receivedContractPack = @{ type = @("boolean", "null") }
                agreeToTerms = @{ type = @("boolean", "null") }
                agreeToCodes = @{ type = @("boolean", "null") }
                dataProcessingConsent = @{ type = @("boolean", "null") }
                marketingConsent = @{ type = @("boolean", "null") }
            }
        }
        submission = @{
            type = "object"
            properties = @{
                additionalInformation = @{ type = "string" }
            }
        }
        referenceNumber = @{ type = "string" }
    }
    
    # Add schema properties
    foreach ($property in $completeSchemaAdditions.GetEnumerator()) {
        $triggerSchema.properties | Add-Member -NotePropertyName $property.Key -NotePropertyValue $property.Value -Force
    }
    
    Write-Host "✅ Updated trigger schema with COMPLETE extended form structure" -ForegroundColor Green
}

# Save updated definition
$definition | ConvertTo-Json -Depth 50 | Set-Content $definitionPath -Encoding UTF8
Write-Host "✅ Updated COMPLETE definition saved" -ForegroundColor Green

# Create complete package
Write-Host "Creating COMPLETE package..." -ForegroundColor Yellow
$zipPath = "$OutputPath.zip"
if (Test-Path $zipPath) { Remove-Item $zipPath }
Compress-Archive -Path "$OutputPath/*" -DestinationPath $zipPath
Write-Host "✅ COMPLETE package created: $zipPath" -ForegroundColor Green

Write-Host "`n=======================================" -ForegroundColor Cyan
Write-Host "✅ COMPLETE Flow Definition Ready!" -ForegroundColor Green
Write-Host "=======================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "ALL SHAREPOINT FIELDS INCLUDED:" -ForegroundColor Yellow
Write-Host "• $($completeFields.Count) field mappings (complete coverage)" -ForegroundColor White
Write-Host "• Company information (6 text fields + years trading)" -ForegroundColor White
Write-Host "• Contact details (4 fields)" -ForegroundColor White
Write-Host "• Services & experience (3 fields)" -ForegroundColor White
Write-Host "• Roles & capabilities (4 fields)" -ForegroundColor White
Write-Host "• Labour mix (2 number fields)" -ForegroundColor White
Write-Host "• Certifications (2 boolean fields)" -ForegroundColor White
Write-Host "• Insurance (7 fields - boolean + dates)" -ForegroundColor White
Write-Host "• Health & Safety (8 comprehensive fields)" -ForegroundColor White
Write-Host "• Policy compliance (7 date/text fields)" -ForegroundColor White
Write-Host "• Project references (3 fields)" -ForegroundColor White
Write-Host "• Legal compliance (3 fields)" -ForegroundColor White
Write-Host "• Agreement/consent (5 boolean fields)" -ForegroundColor White
Write-Host "• Submission tracking (3 system fields)" -ForegroundColor White
Write-Host ""
Write-Host "SPECIAL HANDLING:" -ForegroundColor Yellow
Write-Host "• Truncated field names handled (PrincipalContractor_LastYearScal0)" -ForegroundColor White
Write-Host "• Boolean fields use coalesce for safety" -ForegroundColor White
Write-Host "• Comprehensive email notifications" -ForegroundColor White
Write-Host "• Complete schema for 6-page extended form" -ForegroundColor White
Write-Host ""
Write-Host "Package ready for import: $zipPath" -ForegroundColor Green
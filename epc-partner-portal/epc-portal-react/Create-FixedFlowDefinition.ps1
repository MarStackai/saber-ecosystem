#!/usr/bin/pwsh
<#
.SYNOPSIS
    Creates a corrected Power Automate flow definition using actual SharePoint field names
.DESCRIPTION
    Fixes field names based on SharePoint's truncation patterns observed during deployment
#>

param(
    [string]$InputPath = "./power-automate-export",
    [string]$OutputPath = "./power-automate-export-fixed"
)

Write-Host "Creating fixed flow definition with correct SharePoint field names..." -ForegroundColor Yellow

# Copy original structure
if (Test-Path $OutputPath) { Remove-Item $OutputPath -Recurse -Force }
Copy-Item $InputPath $OutputPath -Recurse -Force

# Load the flow definition
$definitionPath = "$OutputPath/Microsoft.Flow/flows/45991de2-99f2-422e-864f-efdf8db8cb93/definition.json"
$definition = Get-Content $definitionPath -Raw | ConvertFrom-Json

Write-Host "Adding all extended field mappings with corrected field names..." -ForegroundColor Yellow

# Fixed field mappings using actual SharePoint field names (correcting for truncation)
$allFieldMappings = @{
    # Company Info (backward compatible + extended)
    "item/TradingName" = "@triggerBody()?['companyInfo']?['tradingName']"
    "item/RegisteredOffice" = "@coalesce(triggerBody()?['companyInfo']?['registeredAddress'], triggerBody()?['address'])"
    "item/HeadOffice" = "@triggerBody()?['companyInfo']?['headOfficeAddress']"
    "item/CompanyRegNo" = "@coalesce(triggerBody()?['companyInfo']?['registrationNumber'], triggerBody()?['registrationNumber'])"
    "item/VATNumber" = "@triggerBody()?['companyInfo']?['vatNumber']"
    "item/ParentCompany" = "@triggerBody()?['companyInfo']?['parentCompany']"
    "item/YearsTrading" = "@triggerBody()?['companyInfo']?['yearsTrading']"
    
    # Primary Contact (backward compatible + extended)
    "item/PrimaryContactName" = "@coalesce(triggerBody()?['primaryContact']?['fullName'], triggerBody()?['contactName'])"
    "item/PrimaryContactTitle" = "@coalesce(triggerBody()?['primaryContact']?['jobTitle'], triggerBody()?['contactTitle'])"
    "item/PrimaryContactPhone" = "@coalesce(triggerBody()?['primaryContact']?['phone'], triggerBody()?['phone'])"
    "item/PrimaryContactEmail" = "@coalesce(triggerBody()?['primaryContact']?['email'], triggerBody()?['email'])"
    
    # Services & Experience
    "item/Specialisations" = "@triggerBody()?['servicesExperience']?['specializations']"
    "item/SoftwareUsed" = "@triggerBody()?['servicesExperience']?['softwareTools']"
    "item/ProjectsPerMonth" = "@triggerBody()?['servicesExperience']?['averageProjectsPerMonth']"
    
    # Roles & Capabilities - FIXED FIELD NAMES
    "item/ActsAsPrincipalContractor" = "@triggerBody()?['rolesCapabilities']?['principalContractor']"
    "item/PrincipalContractor_LastYearScal0" = "@triggerBody()?['rolesCapabilities']?['pcScaleLastYear']"  # Truncated by SharePoint
    "item/ActsAsPrincipalDesigner" = "@triggerBody()?['rolesCapabilities']?['principalDesigner']"
    "item/PrincipalDesigner_LastYearScale" = "@triggerBody()?['rolesCapabilities']?['pdScaleLastYear']"
    "item/LabourMix_InternalPct" = "@triggerBody()?['rolesCapabilities']?['internalStaffPercentage']"
    "item/LabourMix_SubcontractPct" = "@triggerBody()?['rolesCapabilities']?['subcontractPercentage']"
    
    # Certifications
    "item/NICEIC_CPS" = "@triggerBody()?['certifications']?['niceicContractor']"
    "item/MCS_Approved" = "@triggerBody()?['certifications']?['mcsApproved']"
    
    # Insurance - FIXED FIELD NAMES
    "item/PublicProductLiability_Present" = "@triggerBody()?['insurance']?['publicLiabilityInsurance']"
    "item/PublicProductLiability_Indemnity0" = "@triggerBody()?['insurance']?['pplIndemnityClause']"  # Truncated by SharePoint
    "item/EmployersLiability_Present" = "@triggerBody()?['insurance']?['employersLiabilityInsurance']"
    "item/ProfIndemnity_Present" = "@triggerBody()?['insurance']?['professionalIndemnityInsurance']"
    "item/PublicProductLiability_Expiry" = "@if(empty(triggerBody()?['insurance']?['pplExpiryDate']), null, formatDateTime(triggerBody()?['insurance']?['pplExpiryDate'], 'yyyy-MM-ddTHH:mm:ssZ'))"
    "item/EmployersLiability_Expiry" = "@if(empty(triggerBody()?['insurance']?['elExpiryDate']), null, formatDateTime(triggerBody()?['insurance']?['elExpiryDate'], 'yyyy-MM-ddTHH:mm:ssZ'))"
    "item/ProfIndemnity_Expiry" = "@if(empty(triggerBody()?['insurance']?['piExpiryDate']), null, formatDateTime(triggerBody()?['insurance']?['piExpiryDate'], 'yyyy-MM-ddTHH:mm:ssZ'))"
    
    # Health & Safety - FIXED FIELD NAMES
    "item/HSE_ImprovementOrProhibition_Las0" = "@triggerBody()?['healthSafety']?['hseNotices']"  # Truncated by SharePoint
    "item/RIDDOR_Incidents_Last3Y_Count" = "@triggerBody()?['healthSafety']?['riddorCount']"
    "item/RIDDOR_Incidents_Last3Y_Details" = "@triggerBody()?['healthSafety']?['riddorDetails']"
    "item/HSE_CDM_Management_Evidence" = "@triggerBody()?['healthSafety']?['hsCdmEvidence']"
    "item/Named_PrincipalDesigner" = "@triggerBody()?['healthSafety']?['namedPrincipalDesigner']"
    "item/PD_Qualifications" = "@triggerBody()?['healthSafety']?['pdQualifications']"
    "item/TrainingRecords_Summary" = "@triggerBody()?['healthSafety']?['trainingRecords']"
    "item/NearMiss_Procedure" = "@triggerBody()?['healthSafety']?['nearMissProcedure']"
    "item/Quality_Procedure_Evidence" = "@triggerBody()?['healthSafety']?['qualityEvidence']"
    
    # Policies
    "item/Policy_HS_DateSigned" = "@if(empty(triggerBody()?['policies']?['hsPolicyDate']), null, formatDateTime(triggerBody()?['policies']?['hsPolicyDate'], 'yyyy-MM-ddTHH:mm:ssZ'))"
    "item/Policy_Env_DateSigned" = "@if(empty(triggerBody()?['policies']?['envPolicyDate']), null, formatDateTime(triggerBody()?['policies']?['envPolicyDate'], 'yyyy-MM-ddTHH:mm:ssZ'))"
    "item/Policy_MS_DateSigned" = "@if(empty(triggerBody()?['policies']?['msPolicyDate']), null, formatDateTime(triggerBody()?['policies']?['msPolicyDate'], 'yyyy-MM-ddTHH:mm:ssZ'))"
    "item/Policy_MOS_DateSigned" = "@if(empty(triggerBody()?['policies']?['mosPolicyDate']), null, formatDateTime(triggerBody()?['policies']?['mosPolicyDate'], 'yyyy-MM-ddTHH:mm:ssZ'))"
    "item/RightToWork_Monitoring_Method" = "@triggerBody()?['policies']?['rightToWorkMethod']"
    
    # Data Protection
    "item/GDPRPolicy_DateSigned" = "@if(empty(triggerBody()?['dataProtectionIT']?['gdprPolicyDate']), null, formatDateTime(triggerBody()?['dataProtectionIT']?['gdprPolicyDate'], 'yyyy-MM-ddTHH:mm:ssZ'))"
    "item/CyberIncident_Last3Y" = "@triggerBody()?['dataProtectionIT']?['cyberIncident']"
    
    # Delivery Capability
    "item/Resources_PerProject" = "@triggerBody()?['deliveryCapability']?['resourcingApproach']"
    "item/Coverage_Nationwide" = "@triggerBody()?['projectReferences']?['nationwideCoverage']"
    "item/Client_Reference" = "@triggerBody()?['projectReferences']?['clientReference']"
    
    # Legal & Compliance
    "item/PendingProsecutions_Details" = "@triggerBody()?['legalCompliance']?['pendingProsecutions']"
    "item/Contracts_ReviewedBySignatory" = "@triggerBody()?['legalCompliance']?['contractsReviewed']"
    "item/Legal_Clarifications" = "@triggerBody()?['legalCompliance']?['legalClarifications']"
    
    # Agreement
    "item/Received_ContractOverviewPack" = "@triggerBody()?['agreement']?['receivedContractPack']"
    "item/Willing_To_WorkToSaberTerms" = "@triggerBody()?['agreement']?['agreeToTerms']"
    "item/AgreeToCodes" = "@triggerBody()?['agreement']?['agreeToCodes']"
    "item/DataProcessingConsent" = "@triggerBody()?['agreement']?['dataProcessingConsent']"
    "item/MarketingConsent" = "@triggerBody()?['agreement']?['marketingConsent']"
    
    # Submission
    "item/AdditionalInfo" = "@triggerBody()?['submission']?['additionalInformation']"
    "item/ReferenceNumber" = "@coalesce(triggerBody()?['referenceNumber'], concat('EPC-', utcNow('yyyyMMddHHmmss')))"
    "item/SubmissionStatus" = "Submitted"
}

# Find the Create_item action and add all fields
$createItemAction = $definition.properties.definition.actions.Condition.actions.Create_item
if ($createItemAction -and $createItemAction.inputs -and $createItemAction.inputs.parameters) {
    
    # Add each field mapping
    foreach ($field in $allFieldMappings.GetEnumerator()) {
        $fieldName = $field.Key
        $fieldExpression = $field.Value
        $createItemAction.inputs.parameters | Add-Member -NotePropertyName $fieldName -NotePropertyValue $fieldExpression -Force
    }
    
    Write-Host "✅ Added $($allFieldMappings.Count) field mappings with corrected names" -ForegroundColor Green
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
<li><strong>Specializations:</strong> @{triggerBody()?['servicesExperience']?['specializations']}</li>
<li><strong>Insurance Present:</strong> PPL: @{triggerBody()?['insurance']?['publicLiabilityInsurance']}, EL: @{triggerBody()?['insurance']?['employersLiabilityInsurance']}, PI: @{triggerBody()?['insurance']?['professionalIndemnityInsurance']}</li>
<li><strong>Nationwide Coverage:</strong> @{triggerBody()?['projectReferences']?['nationwideCoverage']}</li>
<li><strong>Agreement Status:</strong> Terms: @{triggerBody()?['agreement']?['agreeToTerms']}, Codes: @{triggerBody()?['agreement']?['agreeToCodes']}, GDPR: @{triggerBody()?['agreement']?['dataProcessingConsent']}</li>
</ul>

<p><a href="https://saberrenewables.sharepoint.com/sites/SaberEPCPartners/Lists/EPC%20Onboarding">View in SharePoint</a></p>
"@
    
    $internalEmail.inputs.parameters.'emailMessage/Body' = $emailBody
}

# Update confirmation email
$confirmationEmail = $definition.properties.definition.actions.Condition.actions.'Send_an_email_(V2)_1'
if ($confirmationEmail) {
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
}

Write-Host "✅ Updated email notifications" -ForegroundColor Green

# Add complete extended schema to trigger
$triggerSchema = $definition.properties.definition.triggers.manual.inputs.schema
if ($triggerSchema -and $triggerSchema.properties) {
    
    $extendedSchemaAdditions = @{
        companyInfo = @{
            type = "object"
            properties = @{
                companyName = @{ type = "string" }
                tradingName = @{ type = "string" }
                registeredAddress = @{ type = "string" }
                headOfficeAddress = @{ type = "string" }
                registrationNumber = @{ type = "string" }
                vatNumber = @{ type = "string" }
                parentCompany = @{ type = "string" }
                yearsTrading = @{ type = "number" }
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
                servicesProvided = @{ type = "array" }
                specializations = @{ type = "string" }
                softwareTools = @{ type = "string" }
                averageProjectsPerMonth = @{ type = "number" }
            }
        }
        rolesCapabilities = @{
            type = "object"
            properties = @{
                principalContractor = @{ type = "boolean" }
                pcScaleLastYear = @{ type = "string" }
                principalDesigner = @{ type = "boolean" }
                pdScaleLastYear = @{ type = "string" }
                internalStaffPercentage = @{ type = "number" }
                subcontractPercentage = @{ type = "number" }
            }
        }
        certifications = @{
            type = "object"
            properties = @{
                isoCertifications = @{ type = "array" }
                constructionSchemes = @{ type = "array" }
                niceicContractor = @{ type = "boolean" }
                mcsApproved = @{ type = "boolean" }
            }
        }
        insurance = @{
            type = "object"
            properties = @{
                publicLiabilityInsurance = @{ type = "boolean" }
                pplIndemnityClause = @{ type = "boolean" }
                employersLiabilityInsurance = @{ type = "boolean" }
                professionalIndemnityInsurance = @{ type = "boolean" }
                pplExpiryDate = @{ type = "string" }
                elExpiryDate = @{ type = "string" }
                piExpiryDate = @{ type = "string" }
            }
        }
        healthSafety = @{
            type = "object"
            properties = @{
                hseNotices = @{ type = "string" }
                riddorCount = @{ type = "number" }
                riddorDetails = @{ type = "string" }
                hsCdmEvidence = @{ type = "string" }
                namedPrincipalDesigner = @{ type = "string" }
                pdQualifications = @{ type = "string" }
                trainingRecords = @{ type = "string" }
                nearMissProcedure = @{ type = "string" }
                qualityEvidence = @{ type = "string" }
            }
        }
        policies = @{
            type = "object"
            properties = @{
                hsPolicyDate = @{ type = "string" }
                envPolicyDate = @{ type = "string" }
                msPolicyDate = @{ type = "string" }
                mosPolicyDate = @{ type = "string" }
                rightToWorkMethod = @{ type = "string" }
            }
        }
        dataProtectionIT = @{
            type = "object"
            properties = @{
                gdprPolicyDate = @{ type = "string" }
                cyberIncident = @{ type = "string" }
            }
        }
        deliveryCapability = @{
            type = "object"
            properties = @{
                resourcingApproach = @{ type = "string" }
            }
        }
        projectReferences = @{
            type = "object"
            properties = @{
                nationwideCoverage = @{ type = "boolean" }
                regionsCovered = @{ type = "array" }
                clientReference = @{ type = "string" }
            }
        }
        legalCompliance = @{
            type = "object"
            properties = @{
                pendingProsecutions = @{ type = "string" }
                contractsReviewed = @{ type = "boolean" }
                legalClarifications = @{ type = "string" }
            }
        }
        agreement = @{
            type = "object"
            properties = @{
                receivedContractPack = @{ type = "boolean" }
                agreeToTerms = @{ type = "boolean" }
                agreeToCodes = @{ type = "boolean" }
                dataProcessingConsent = @{ type = "boolean" }
                marketingConsent = @{ type = "boolean" }
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
    
    # Add extended schema properties
    foreach ($property in $extendedSchemaAdditions.GetEnumerator()) {
        $triggerSchema.properties | Add-Member -NotePropertyName $property.Key -NotePropertyValue $property.Value -Force
    }
    
    Write-Host "✅ Updated trigger schema with complete extended form structure" -ForegroundColor Green
}

# Save updated definition
$definition | ConvertTo-Json -Depth 50 | Set-Content $definitionPath -Encoding UTF8
Write-Host "✅ Updated definition saved" -ForegroundColor Green

# Create fixed package
Write-Host "Creating fixed package..." -ForegroundColor Yellow
$zipPath = "$OutputPath.zip"
if (Test-Path $zipPath) { Remove-Item $zipPath }
Compress-Archive -Path "$OutputPath/*" -DestinationPath $zipPath
Write-Host "✅ Fixed package created: $zipPath" -ForegroundColor Green

Write-Host "`n=======================================" -ForegroundColor Cyan
Write-Host "✅ Fixed Flow Definition Complete!" -ForegroundColor Green
Write-Host "=======================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Summary:" -ForegroundColor Yellow
Write-Host "• Added $($allFieldMappings.Count) field mappings with corrected SharePoint names" -ForegroundColor White
Write-Host "• Fixed truncated field names (PrincipalContractor_LastYearScal0, etc.)" -ForegroundColor White
Write-Host "• Updated trigger schema with complete extended form structure" -ForegroundColor White
Write-Host "• Enhanced email notifications with extended data" -ForegroundColor White
Write-Host "• Maintained full backward compatibility" -ForegroundColor White
Write-Host ""
Write-Host "Package ready for import: $zipPath" -ForegroundColor Green
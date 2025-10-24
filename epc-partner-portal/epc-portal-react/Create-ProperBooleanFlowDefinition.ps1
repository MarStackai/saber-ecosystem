#!/usr/bin/pwsh
<#
.SYNOPSIS
    Creates a flow definition with proper boolean handling as per best practices
.DESCRIPTION
    Uses proper boolean normalization and coalesce for safe defaults
#>

param(
    [string]$InputPath = "./power-automate-export",
    [string]$OutputPath = "./power-automate-export-proper"
)

Write-Host "Creating flow definition with proper boolean handling..." -ForegroundColor Yellow

# Copy original structure
if (Test-Path $OutputPath) { Remove-Item $OutputPath -Recurse -Force }
Copy-Item $InputPath $OutputPath -Recurse -Force

# Load the flow definition
$definitionPath = "$OutputPath/Microsoft.Flow/flows/45991de2-99f2-422e-864f-efdf8db8cb93/definition.json"
$definition = Get-Content $definitionPath -Raw | ConvertFrom-Json

Write-Host "Adding proper field mappings with boolean normalization..." -ForegroundColor Yellow

# Proper field mappings with boolean normalization and safe defaults
$properFields = @{
    # Text fields - straightforward
    "item/TradingName" = "@triggerBody()?['companyInfo']?['tradingName']"
    "item/VATNumber" = "@triggerBody()?['companyInfo']?['vatNumber']"
    "item/ParentCompany" = "@triggerBody()?['companyInfo']?['parentCompany']"
    "item/PrimaryContactName" = "@coalesce(triggerBody()?['primaryContact']?['fullName'], triggerBody()?['contactName'])"
    "item/PrimaryContactTitle" = "@coalesce(triggerBody()?['primaryContact']?['jobTitle'], triggerBody()?['contactTitle'])"
    "item/PrimaryContactPhone" = "@coalesce(triggerBody()?['primaryContact']?['phone'], triggerBody()?['phone'])"
    "item/PrimaryContactEmail" = "@coalesce(triggerBody()?['primaryContact']?['email'], triggerBody()?['email'])"
    "item/Specialisations" = "@triggerBody()?['servicesExperience']?['specializations']"
    "item/SoftwareUsed" = "@triggerBody()?['servicesExperience']?['softwareTools']"
    "item/AdditionalInfo" = "@triggerBody()?['submission']?['additionalInformation']"
    "item/ReferenceNumber" = "@coalesce(triggerBody()?['referenceNumber'], concat('EPC-', utcNow('yyyyMMddHHmmss')))"
    "item/SubmissionStatus" = "Submitted"
    
    # Number fields with coalesce for safety
    "item/YearsTrading" = "@coalesce(triggerBody()?['companyInfo']?['yearsTrading'], 0)"
    "item/ProjectsPerMonth" = "@coalesce(triggerBody()?['servicesExperience']?['averageProjectsPerMonth'], 0)"
    
    # Boolean fields - PROPER APPROACH: Use coalesce with false default
    "item/ActsAsPrincipalContractor" = "@coalesce(triggerBody()?['rolesCapabilities']?['principalContractor'], false)"
    "item/ActsAsPrincipalDesigner" = "@coalesce(triggerBody()?['rolesCapabilities']?['principalDesigner'], false)"
    "item/NICEIC_CPS" = "@coalesce(triggerBody()?['certifications']?['niceicContractor'], false)"
    "item/MCS_Approved" = "@coalesce(triggerBody()?['certifications']?['mcsApproved'], false)"
    "item/PublicProductLiability_Present" = "@coalesce(triggerBody()?['insurance']?['publicLiabilityInsurance'], false)"
    "item/EmployersLiability_Present" = "@coalesce(triggerBody()?['insurance']?['employersLiabilityInsurance'], false)"
    "item/ProfIndemnity_Present" = "@coalesce(triggerBody()?['insurance']?['professionalIndemnityInsurance'], false)"
    "item/Coverage_Nationwide" = "@coalesce(triggerBody()?['projectReferences']?['nationwideCoverage'], false)"
    "item/DataProcessingConsent" = "@coalesce(triggerBody()?['agreement']?['dataProcessingConsent'], false)"
    "item/MarketingConsent" = "@coalesce(triggerBody()?['agreement']?['marketingConsent'], false)"
    "item/AgreeToCodes" = "@coalesce(triggerBody()?['agreement']?['agreeToCodes'], false)"
    "item/Willing_To_WorkToSaberTerms" = "@coalesce(triggerBody()?['agreement']?['agreeToTerms'], false)"
    "item/Contracts_ReviewedBySignatory" = "@coalesce(triggerBody()?['legalCompliance']?['contractsReviewed'], false)"
}

# Find the Create_item action and add proper fields
$createItemAction = $definition.properties.definition.actions.Condition.actions.Create_item
if ($createItemAction -and $createItemAction.inputs -and $createItemAction.inputs.parameters) {
    
    # Add each proper field mapping
    foreach ($field in $properFields.GetEnumerator()) {
        $fieldName = $field.Key
        $fieldExpression = $field.Value
        $createItemAction.inputs.parameters | Add-Member -NotePropertyName $fieldName -NotePropertyValue $fieldExpression -Force
    }
    
    Write-Host "✅ Added $($properFields.Count) field mappings with proper boolean handling" -ForegroundColor Green
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
<tr><td><strong>Contact</strong></td><td>@{coalesce(triggerBody()?['primaryContact']?['fullName'], triggerBody()?['contactName'])}</td></tr>
<tr><td><strong>Email</strong></td><td>@{coalesce(triggerBody()?['primaryContact']?['email'], triggerBody()?['email'])}</td></tr>
<tr><td><strong>Phone</strong></td><td>@{coalesce(triggerBody()?['primaryContact']?['phone'], triggerBody()?['phone'])}</td></tr>
<tr><td><strong>SharePoint ID</strong></td><td>@{body('Create_item')?['ID']}</td></tr>
<tr><td><strong>Code Used</strong></td><td>@{triggerBody()?['invitationCode']}</td></tr>
</tbody>
</table>

<h3>Extended Form Data</h3>
<ul>
<li><strong>Specializations:</strong> @{triggerBody()?['servicesExperience']?['specializations']}</li>
<li><strong>Software Used:</strong> @{triggerBody()?['servicesExperience']?['softwareTools']}</li>
<li><strong>Projects Per Month:</strong> @{coalesce(triggerBody()?['servicesExperience']?['averageProjectsPerMonth'], 0)}</li>
<li><strong>Years Trading:</strong> @{coalesce(triggerBody()?['companyInfo']?['yearsTrading'], 0)}</li>
<li><strong>Principal Contractor:</strong> @{if(coalesce(triggerBody()?['rolesCapabilities']?['principalContractor'], false), 'Yes', 'No')}</li>
<li><strong>Principal Designer:</strong> @{if(coalesce(triggerBody()?['rolesCapabilities']?['principalDesigner'], false), 'Yes', 'No')}</li>
<li><strong>NICEIC CPS:</strong> @{if(coalesce(triggerBody()?['certifications']?['niceicContractor'], false), 'Yes', 'No')}</li>
<li><strong>MCS Approved:</strong> @{if(coalesce(triggerBody()?['certifications']?['mcsApproved'], false), 'Yes', 'No')}</li>
<li><strong>Insurance Present:</strong> PPL: @{if(coalesce(triggerBody()?['insurance']?['publicLiabilityInsurance'], false), 'Yes', 'No')}, EL: @{if(coalesce(triggerBody()?['insurance']?['employersLiabilityInsurance'], false), 'Yes', 'No')}, PI: @{if(coalesce(triggerBody()?['insurance']?['professionalIndemnityInsurance'], false), 'Yes', 'No')}</li>
<li><strong>Nationwide Coverage:</strong> @{if(coalesce(triggerBody()?['projectReferences']?['nationwideCoverage'], false), 'Yes', 'No')}</li>
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

Write-Host "✅ Updated email notifications with proper boolean display" -ForegroundColor Green

# Update trigger schema with proper boolean types and nullability
$triggerSchema = $definition.properties.definition.triggers.manual.inputs.schema
if ($triggerSchema -and $triggerSchema.properties) {
    
    $properSchemaAdditions = @{
        companyInfo = @{
            type = "object"
            properties = @{
                companyName = @{ type = "string" }
                tradingName = @{ type = "string" }
                vatNumber = @{ type = "string" }
                parentCompany = @{ type = "string" }
                yearsTrading = @{ type = @("number", "null") }  # Allow null for safety
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
                averageProjectsPerMonth = @{ type = @("number", "null") }  # Allow null for safety
            }
        }
        rolesCapabilities = @{
            type = "object"
            properties = @{
                principalContractor = @{ type = @("boolean", "null") }  # Proper boolean with null safety
                principalDesigner = @{ type = @("boolean", "null") }
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
                employersLiabilityInsurance = @{ type = @("boolean", "null") }
                professionalIndemnityInsurance = @{ type = @("boolean", "null") }
            }
        }
        projectReferences = @{
            type = "object"
            properties = @{
                nationwideCoverage = @{ type = @("boolean", "null") }
            }
        }
        agreement = @{
            type = "object"
            properties = @{
                dataProcessingConsent = @{ type = @("boolean", "null") }
                marketingConsent = @{ type = @("boolean", "null") }
                agreeToCodes = @{ type = @("boolean", "null") }
                agreeToTerms = @{ type = @("boolean", "null") }
            }
        }
        legalCompliance = @{
            type = "object"
            properties = @{
                contractsReviewed = @{ type = @("boolean", "null") }
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
    foreach ($property in $properSchemaAdditions.GetEnumerator()) {
        $triggerSchema.properties | Add-Member -NotePropertyName $property.Key -NotePropertyValue $property.Value -Force
    }
    
    Write-Host "✅ Updated trigger schema with proper boolean types and null safety" -ForegroundColor Green
}

# Save updated definition
$definition | ConvertTo-Json -Depth 50 | Set-Content $definitionPath -Encoding UTF8
Write-Host "✅ Updated definition saved" -ForegroundColor Green

# Create proper package
Write-Host "Creating proper boolean package..." -ForegroundColor Yellow
$zipPath = "$OutputPath.zip"
if (Test-Path $zipPath) { Remove-Item $zipPath }
Compress-Archive -Path "$OutputPath/*" -DestinationPath $zipPath
Write-Host "✅ Proper boolean package created: $zipPath" -ForegroundColor Green

Write-Host "`n=======================================" -ForegroundColor Cyan
Write-Host "✅ Proper Boolean Flow Definition Complete!" -ForegroundColor Green
Write-Host "=======================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "PROPER BOOLEAN BEST PRACTICES APPLIED:" -ForegroundColor Yellow
Write-Host "• Boolean fields use coalesce(value, false) for safe defaults" -ForegroundColor White
Write-Host "• Trigger schema defines proper boolean types with null safety" -ForegroundColor White
Write-Host "• Email notifications use if() expressions for boolean display" -ForegroundColor White
Write-Host "• Number fields have null-safe defaults" -ForegroundColor White
Write-Host ""
Write-Host "This package contains:" -ForegroundColor Yellow
Write-Host "• $($properFields.Count) field mappings with proper boolean handling" -ForegroundColor White
Write-Host "• Core company information (text fields)" -ForegroundColor White
Write-Host "• Primary contact details (text fields)" -ForegroundColor White
Write-Host "• Services and experience (text/number with null safety)" -ForegroundColor White
Write-Host "• Proper boolean fields with coalesce defaults" -ForegroundColor White
Write-Host "• Schema supports both boolean and null values" -ForegroundColor White
Write-Host ""
Write-Host "Package ready for import: $zipPath" -ForegroundColor Green
Write-Host ""
Write-Host "NEXT STEPS:" -ForegroundColor Yellow
Write-Host "1. Import this package (should work with proper booleans)" -ForegroundColor White
Write-Host "2. Update Cloudflare Worker to send proper boolean values" -ForegroundColor White
Write-Host "3. Add remaining fields incrementally" -ForegroundColor White
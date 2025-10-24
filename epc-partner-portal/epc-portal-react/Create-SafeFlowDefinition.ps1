#!/usr/bin/pwsh
<#
.SYNOPSIS
    Creates a safe flow definition with properly formatted field types
.DESCRIPTION
    Fixes boolean and other data type formatting for SharePoint compatibility
#>

param(
    [string]$InputPath = "./power-automate-export",
    [string]$OutputPath = "./power-automate-export-safe"
)

Write-Host "Creating safe flow definition with proper data type formatting..." -ForegroundColor Yellow

# Copy original structure
if (Test-Path $OutputPath) { Remove-Item $OutputPath -Recurse -Force }
Copy-Item $InputPath $OutputPath -Recurse -Force

# Load the flow definition
$definitionPath = "$OutputPath/Microsoft.Flow/flows/45991de2-99f2-422e-864f-efdf8db8cb93/definition.json"
$definition = Get-Content $definitionPath -Raw | ConvertFrom-Json

Write-Host "Adding safe field mappings with proper data types..." -ForegroundColor Yellow

# Safe field mappings with proper SharePoint data type formatting
$safeFields = @{
    # Text fields - these work fine as strings
    "item/TradingName" = "@triggerBody()?['companyInfo']?['tradingName']"
    "item/VATNumber" = "@triggerBody()?['companyInfo']?['vatNumber']"
    "item/ParentCompany" = "@triggerBody()?['companyInfo']?['parentCompany']"
    "item/PrimaryContactName" = "@coalesce(triggerBody()?['primaryContact']?['fullName'], triggerBody()?['contactName'])"
    "item/PrimaryContactTitle" = "@coalesce(triggerBody()?['primaryContact']?['jobTitle'], triggerBody()?['contactTitle'])"
    "item/PrimaryContactPhone" = "@coalesce(triggerBody()?['primaryContact']?['phone'], triggerBody()?['phone'])"
    "item/PrimaryContactEmail" = "@coalesce(triggerBody()?['primaryContact']?['email'], triggerBody()?['email'])"
    "item/Specialisations" = "@triggerBody()?['servicesExperience']?['specializations']"
    "item/SoftwareUsed" = "@triggerBody()?['servicesExperience']?['softwareTools']"
    
    # Number fields - these work as numbers
    "item/YearsTrading" = "@triggerBody()?['companyInfo']?['yearsTrading']"
    "item/ProjectsPerMonth" = "@triggerBody()?['servicesExperience']?['averageProjectsPerMonth']"
    
    # Boolean fields - FIXED FORMAT: Use proper boolean expressions
    "item/ActsAsPrincipalContractor" = "@bool(triggerBody()?['rolesCapabilities']?['principalContractor'])"
    "item/ActsAsPrincipalDesigner" = "@bool(triggerBody()?['rolesCapabilities']?['principalDesigner'])"
    "item/NICEIC_CPS" = "@bool(triggerBody()?['certifications']?['niceicContractor'])"
    "item/MCS_Approved" = "@bool(triggerBody()?['certifications']?['mcsApproved'])"
    "item/PublicProductLiability_Present" = "@bool(triggerBody()?['insurance']?['publicLiabilityInsurance'])"
    "item/EmployersLiability_Present" = "@bool(triggerBody()?['insurance']?['employersLiabilityInsurance'])"
    "item/ProfIndemnity_Present" = "@bool(triggerBody()?['insurance']?['professionalIndemnityInsurance'])"
    "item/Coverage_Nationwide" = "@bool(triggerBody()?['projectReferences']?['nationwideCoverage'])"
    "item/DataProcessingConsent" = "@bool(triggerBody()?['agreement']?['dataProcessingConsent'])"
    "item/MarketingConsent" = "@bool(triggerBody()?['agreement']?['marketingConsent'])"
    "item/AgreeToCodes" = "@bool(triggerBody()?['agreement']?['agreeToCodes'])"
    
    # Core submission fields
    "item/AdditionalInfo" = "@triggerBody()?['submission']?['additionalInformation']"
    "item/ReferenceNumber" = "@coalesce(triggerBody()?['referenceNumber'], concat('EPC-', utcNow('yyyyMMddHHmmss')))"
    "item/SubmissionStatus" = "Submitted"
}

# Find the Create_item action and add safe fields
$createItemAction = $definition.properties.definition.actions.Condition.actions.Create_item
if ($createItemAction -and $createItemAction.inputs -and $createItemAction.inputs.parameters) {
    
    # Add each safe field mapping
    foreach ($field in $safeFields.GetEnumerator()) {
        $fieldName = $field.Key
        $fieldExpression = $field.Value
        $createItemAction.inputs.parameters | Add-Member -NotePropertyName $fieldName -NotePropertyValue $fieldExpression -Force
    }
    
    Write-Host "✅ Added $($safeFields.Count) safe field mappings with proper data types" -ForegroundColor Green
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
<li><strong>Principal Contractor:</strong> @{if(equals(triggerBody()?['rolesCapabilities']?['principalContractor'], true), 'Yes', 'No')}</li>
<li><strong>Principal Designer:</strong> @{if(equals(triggerBody()?['rolesCapabilities']?['principalDesigner'], true), 'Yes', 'No')}</li>
<li><strong>NICEIC CPS:</strong> @{if(equals(triggerBody()?['certifications']?['niceicContractor'], true), 'Yes', 'No')}</li>
<li><strong>MCS Approved:</strong> @{if(equals(triggerBody()?['certifications']?['mcsApproved'], true), 'Yes', 'No')}</li>
<li><strong>Insurance Present:</strong> PPL: @{if(equals(triggerBody()?['insurance']?['publicLiabilityInsurance'], true), 'Yes', 'No')}, EL: @{if(equals(triggerBody()?['insurance']?['employersLiabilityInsurance'], true), 'Yes', 'No')}, PI: @{if(equals(triggerBody()?['insurance']?['professionalIndemnityInsurance'], true), 'Yes', 'No')}</li>
<li><strong>Nationwide Coverage:</strong> @{if(equals(triggerBody()?['projectReferences']?['nationwideCoverage'], true), 'Yes', 'No')}</li>
<li><strong>GDPR Consent:</strong> @{if(equals(triggerBody()?['agreement']?['dataProcessingConsent'], true), 'Yes', 'No')}</li>
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

Write-Host "✅ Updated email notifications with proper boolean formatting" -ForegroundColor Green

# Add extended schema to trigger with proper data types
$triggerSchema = $definition.properties.definition.triggers.manual.inputs.schema
if ($triggerSchema -and $triggerSchema.properties) {
    
    $extendedSchemaAdditions = @{
        companyInfo = @{
            type = "object"
            properties = @{
                companyName = @{ type = "string" }
                tradingName = @{ type = "string" }
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
                specializations = @{ type = "string" }
                softwareTools = @{ type = "string" }
                averageProjectsPerMonth = @{ type = "number" }
            }
        }
        rolesCapabilities = @{
            type = "object"
            properties = @{
                principalContractor = @{ type = "boolean" }
                principalDesigner = @{ type = "boolean" }
            }
        }
        certifications = @{
            type = "object"
            properties = @{
                niceicContractor = @{ type = "boolean" }
                mcsApproved = @{ type = "boolean" }
            }
        }
        insurance = @{
            type = "object"
            properties = @{
                publicLiabilityInsurance = @{ type = "boolean" }
                employersLiabilityInsurance = @{ type = "boolean" }
                professionalIndemnityInsurance = @{ type = "boolean" }
            }
        }
        projectReferences = @{
            type = "object"
            properties = @{
                nationwideCoverage = @{ type = "boolean" }
            }
        }
        agreement = @{
            type = "object"
            properties = @{
                dataProcessingConsent = @{ type = "boolean" }
                marketingConsent = @{ type = "boolean" }
                agreeToCodes = @{ type = "boolean" }
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
    foreach ($property in $extendedSchemaAdditions.GetEnumerator()) {
        $triggerSchema.properties | Add-Member -NotePropertyName $property.Key -NotePropertyValue $property.Value -Force
    }
    
    Write-Host "✅ Updated trigger schema with proper data types" -ForegroundColor Green
}

# Save updated definition
$definition | ConvertTo-Json -Depth 50 | Set-Content $definitionPath -Encoding UTF8
Write-Host "✅ Updated definition saved" -ForegroundColor Green

# Create safe package
Write-Host "Creating safe package..." -ForegroundColor Yellow
$zipPath = "$OutputPath.zip"
if (Test-Path $zipPath) { Remove-Item $zipPath }
Compress-Archive -Path "$OutputPath/*" -DestinationPath $zipPath
Write-Host "✅ Safe package created: $zipPath" -ForegroundColor Green

Write-Host "`n=======================================" -ForegroundColor Cyan
Write-Host "✅ Safe Flow Definition Complete!" -ForegroundColor Green
Write-Host "=======================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "FIXED DATA TYPE ISSUES:" -ForegroundColor Yellow
Write-Host "• Boolean fields now use @bool() function" -ForegroundColor White
Write-Host "• Email notifications properly format boolean values" -ForegroundColor White
Write-Host "• Schema defines correct data types" -ForegroundColor White
Write-Host ""
Write-Host "This package contains:" -ForegroundColor Yellow
Write-Host "• $($safeFields.Count) field mappings with proper SharePoint data types" -ForegroundColor White
Write-Host "• Core company information (text fields)" -ForegroundColor White
Write-Host "• Primary contact details (text fields)" -ForegroundColor White
Write-Host "• Services and experience (text/number fields)" -ForegroundColor White
Write-Host "• Role capabilities (properly formatted boolean fields)" -ForegroundColor White
Write-Host "• Certifications (properly formatted boolean fields)" -ForegroundColor White
Write-Host "• Insurance flags (properly formatted boolean fields)" -ForegroundColor White
Write-Host "• Agreement flags (properly formatted boolean fields)" -ForegroundColor White
Write-Host ""
Write-Host "Package ready for import: $zipPath" -ForegroundColor Green
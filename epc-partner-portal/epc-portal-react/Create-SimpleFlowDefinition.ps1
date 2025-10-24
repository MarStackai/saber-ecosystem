#!/usr/bin/pwsh
<#
.SYNOPSIS
    Creates a simple flow definition with only text and number fields (no booleans)
.DESCRIPTION
    Let's start with just text and number fields to get something working, then add booleans later
#>

param(
    [string]$InputPath = "./power-automate-export",
    [string]$OutputPath = "./power-automate-export-simple"
)

Write-Host "Creating simple flow definition with text/number fields only..." -ForegroundColor Yellow

# Copy original structure
if (Test-Path $OutputPath) { Remove-Item $OutputPath -Recurse -Force }
Copy-Item $InputPath $OutputPath -Recurse -Force

# Load the flow definition
$definitionPath = "$OutputPath/Microsoft.Flow/flows/45991de2-99f2-422e-864f-efdf8db8cb93/definition.json"
$definition = Get-Content $definitionPath -Raw | ConvertFrom-Json

Write-Host "Adding simple field mappings (text/number only)..." -ForegroundColor Yellow

# Simple field mappings - ONLY text and number fields (no booleans)
$simpleFields = @{
    # Text fields - these definitely work
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
    
    # Number fields - these should work
    "item/YearsTrading" = "@triggerBody()?['companyInfo']?['yearsTrading']"
    "item/ProjectsPerMonth" = "@triggerBody()?['servicesExperience']?['averageProjectsPerMonth']"
    
    # Convert boolean fields to text for now (avoiding boolean type issues)
    "item/PrincipalContractorText" = "@if(equals(triggerBody()?['rolesCapabilities']?['principalContractor'], true), 'Yes', 'No')"
    "item/PrincipalDesignerText" = "@if(equals(triggerBody()?['rolesCapabilities']?['principalDesigner'], true), 'Yes', 'No')"
    "item/NICEIC_Text" = "@if(equals(triggerBody()?['certifications']?['niceicContractor'], true), 'Yes', 'No')"
    "item/MCS_Text" = "@if(equals(triggerBody()?['certifications']?['mcsApproved'], true), 'Yes', 'No')"
    "item/PPL_Text" = "@if(equals(triggerBody()?['insurance']?['publicLiabilityInsurance'], true), 'Yes', 'No')"
    "item/EL_Text" = "@if(equals(triggerBody()?['insurance']?['employersLiabilityInsurance'], true), 'Yes', 'No')"
    "item/PI_Text" = "@if(equals(triggerBody()?['insurance']?['professionalIndemnityInsurance'], true), 'Yes', 'No')"
    "item/NationwideCoverageText" = "@if(equals(triggerBody()?['projectReferences']?['nationwideCoverage'], true), 'Yes', 'No')"
    "item/GDPRConsentText" = "@if(equals(triggerBody()?['agreement']?['dataProcessingConsent'], true), 'Yes', 'No')"
    "item/MarketingConsentText" = "@if(equals(triggerBody()?['agreement']?['marketingConsent'], true), 'Yes', 'No')"
    "item/AgreeToCodesText" = "@if(equals(triggerBody()?['agreement']?['agreeToCodes'], true), 'Yes', 'No')"
}

# Find the Create_item action and add simple fields
$createItemAction = $definition.properties.definition.actions.Condition.actions.Create_item
if ($createItemAction -and $createItemAction.inputs -and $createItemAction.inputs.parameters) {
    
    # Add each simple field mapping
    foreach ($field in $simpleFields.GetEnumerator()) {
        $fieldName = $field.Key
        $fieldExpression = $field.Value
        $createItemAction.inputs.parameters | Add-Member -NotePropertyName $fieldName -NotePropertyValue $fieldExpression -Force
    }
    
    Write-Host "✅ Added $($simpleFields.Count) simple field mappings (text/number only)" -ForegroundColor Green
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
<li><strong>Projects Per Month:</strong> @{triggerBody()?['servicesExperience']?['averageProjectsPerMonth']}</li>
<li><strong>Years Trading:</strong> @{triggerBody()?['companyInfo']?['yearsTrading']}</li>
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

Write-Host "✅ Updated email notifications" -ForegroundColor Green

# Add extended schema to trigger (avoiding boolean issues)
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
    
    Write-Host "✅ Updated trigger schema" -ForegroundColor Green
}

# Save updated definition
$definition | ConvertTo-Json -Depth 50 | Set-Content $definitionPath -Encoding UTF8
Write-Host "✅ Updated definition saved" -ForegroundColor Green

# Create simple package
Write-Host "Creating simple package..." -ForegroundColor Yellow
$zipPath = "$OutputPath.zip"
if (Test-Path $zipPath) { Remove-Item $zipPath }
Compress-Archive -Path "$OutputPath/*" -DestinationPath $zipPath
Write-Host "✅ Simple package created: $zipPath" -ForegroundColor Green

Write-Host "`n=======================================" -ForegroundColor Cyan
Write-Host "✅ Simple Flow Definition Complete!" -ForegroundColor Green
Write-Host "=======================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "AVOIDING BOOLEAN TYPE ISSUES:" -ForegroundColor Yellow
Write-Host "• Boolean values converted to Yes/No text fields" -ForegroundColor White
Write-Host "• Only text and number fields used for SharePoint" -ForegroundColor White
Write-Host "• Email notifications still show proper boolean values" -ForegroundColor White
Write-Host ""
Write-Host "This package contains:" -ForegroundColor Yellow
Write-Host "• $($simpleFields.Count) field mappings (text/number only)" -ForegroundColor White
Write-Host "• Core company information (trading name, VAT, parent company)" -ForegroundColor White
Write-Host "• Primary contact details (name, title, phone, email)" -ForegroundColor White
Write-Host "• Services and experience (specializations, software, project volume)" -ForegroundColor White
Write-Host "• Boolean fields converted to Yes/No text (avoiding type conflicts)" -ForegroundColor White
Write-Host ""
Write-Host "Package ready for import: $zipPath" -ForegroundColor Green
#!/usr/bin/pwsh
<#
.SYNOPSIS
    Creates a test flow with just the core fields that definitely work
.DESCRIPTION
    Let's start with fields we know work and add more incrementally
#>

param(
    [string]$InputPath = "./power-automate-export",
    [string]$OutputPath = "./power-automate-export-test"
)

Write-Host "Creating test flow definition with verified fields only..." -ForegroundColor Yellow

# Copy original structure
if (Test-Path $OutputPath) { Remove-Item $OutputPath -Recurse -Force }
Copy-Item $InputPath $OutputPath -Recurse -Force

# Load the flow definition
$definitionPath = "$OutputPath/Microsoft.Flow/flows/45991de2-99f2-422e-864f-efdf8db8cb93/definition.json"
$definition = Get-Content $definitionPath -Raw | ConvertFrom-Json

Write-Host "Adding only verified field mappings..." -ForegroundColor Yellow

# Only fields we're 100% confident exist (observed as working during SharePoint deployment)
$verifiedFields = @{
    # Core company fields (definitely exist)
    "item/TradingName" = "@triggerBody()?['companyInfo']?['tradingName']"
    "item/VATNumber" = "@triggerBody()?['companyInfo']?['vatNumber']"
    "item/ParentCompany" = "@triggerBody()?['companyInfo']?['parentCompany']"
    "item/YearsTrading" = "@triggerBody()?['companyInfo']?['yearsTrading']"
    
    # Primary contact fields (definitely exist)
    "item/PrimaryContactName" = "@coalesce(triggerBody()?['primaryContact']?['fullName'], triggerBody()?['contactName'])"
    "item/PrimaryContactTitle" = "@coalesce(triggerBody()?['primaryContact']?['jobTitle'], triggerBody()?['contactTitle'])"
    "item/PrimaryContactPhone" = "@coalesce(triggerBody()?['primaryContact']?['phone'], triggerBody()?['phone'])"
    "item/PrimaryContactEmail" = "@coalesce(triggerBody()?['primaryContact']?['email'], triggerBody()?['email'])"
    
    # Services fields (definitely exist)
    "item/Specialisations" = "@triggerBody()?['servicesExperience']?['specializations']"
    "item/SoftwareUsed" = "@triggerBody()?['servicesExperience']?['softwareTools']"
    "item/ProjectsPerMonth" = "@triggerBody()?['servicesExperience']?['averageProjectsPerMonth']"
    
    # Basic role fields (simple boolean, definitely exist)
    "item/ActsAsPrincipalContractor" = "@triggerBody()?['rolesCapabilities']?['principalContractor']"
    "item/ActsAsPrincipalDesigner" = "@triggerBody()?['rolesCapabilities']?['principalDesigner']"
    
    # Basic certification fields (simple boolean, definitely exist)
    "item/NICEIC_CPS" = "@triggerBody()?['certifications']?['niceicContractor']"
    "item/MCS_Approved" = "@triggerBody()?['certifications']?['mcsApproved']"
    
    # Basic insurance fields (simple boolean, definitely exist)
    "item/PublicProductLiability_Present" = "@triggerBody()?['insurance']?['publicLiabilityInsurance']"
    "item/EmployersLiability_Present" = "@triggerBody()?['insurance']?['employersLiabilityInsurance']"
    "item/ProfIndemnity_Present" = "@triggerBody()?['insurance']?['professionalIndemnityInsurance']"
    
    # Basic compliance fields (definitely exist)
    "item/Coverage_Nationwide" = "@triggerBody()?['projectReferences']?['nationwideCoverage']"
    "item/DataProcessingConsent" = "@triggerBody()?['agreement']?['dataProcessingConsent']"
    "item/MarketingConsent" = "@triggerBody()?['agreement']?['marketingConsent']"
    "item/AgreeToCodes" = "@triggerBody()?['agreement']?['agreeToCodes']"
    
    # Core submission fields
    "item/AdditionalInfo" = "@triggerBody()?['submission']?['additionalInformation']"
    "item/ReferenceNumber" = "@coalesce(triggerBody()?['referenceNumber'], concat('EPC-', utcNow('yyyyMMddHHmmss')))"
    "item/SubmissionStatus" = "Submitted"
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
    
    Write-Host "✅ Added $($verifiedFields.Count) verified field mappings" -ForegroundColor Green
} else {
    Write-Host "❌ Could not find Create_item action" -ForegroundColor Red
    exit 1
}

# Update email notifications with verified extended data
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
<li><strong>Principal Contractor:</strong> @{triggerBody()?['rolesCapabilities']?['principalContractor']}</li>
<li><strong>Principal Designer:</strong> @{triggerBody()?['rolesCapabilities']?['principalDesigner']}</li>
<li><strong>NICEIC CPS:</strong> @{triggerBody()?['certifications']?['niceicContractor']}</li>
<li><strong>MCS Approved:</strong> @{triggerBody()?['certifications']?['mcsApproved']}</li>
<li><strong>Insurance:</strong> PPL: @{triggerBody()?['insurance']?['publicLiabilityInsurance']}, EL: @{triggerBody()?['insurance']?['employersLiabilityInsurance']}, PI: @{triggerBody()?['insurance']?['professionalIndemnityInsurance']}</li>
<li><strong>Nationwide Coverage:</strong> @{triggerBody()?['projectReferences']?['nationwideCoverage']}</li>
<li><strong>Agreements:</strong> Terms: @{triggerBody()?['agreement']?['agreeToTerms']}, Codes: @{triggerBody()?['agreement']?['agreeToCodes']}, GDPR: @{triggerBody()?['agreement']?['dataProcessingConsent']}</li>
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

# Add core extended schema to trigger
$triggerSchema = $definition.properties.definition.triggers.manual.inputs.schema
if ($triggerSchema -and $triggerSchema.properties) {
    
    $coreSchemaAdditions = @{
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
    
    # Add core schema properties
    foreach ($property in $coreSchemaAdditions.GetEnumerator()) {
        $triggerSchema.properties | Add-Member -NotePropertyName $property.Key -NotePropertyValue $property.Value -Force
    }
    
    Write-Host "✅ Updated trigger schema with verified extended sections" -ForegroundColor Green
}

# Save updated definition
$definition | ConvertTo-Json -Depth 50 | Set-Content $definitionPath -Encoding UTF8
Write-Host "✅ Updated definition saved" -ForegroundColor Green

# Create test package
Write-Host "Creating test package..." -ForegroundColor Yellow
$zipPath = "$OutputPath.zip"
if (Test-Path $zipPath) { Remove-Item $zipPath }
Compress-Archive -Path "$OutputPath/*" -DestinationPath $zipPath
Write-Host "✅ Test package created: $zipPath" -ForegroundColor Green

Write-Host "`n=======================================" -ForegroundColor Cyan
Write-Host "✅ Test Flow Definition Complete!" -ForegroundColor Green
Write-Host "=======================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "This package contains:" -ForegroundColor Yellow
Write-Host "• $($verifiedFields.Count) verified field mappings (no complex or truncated names)" -ForegroundColor White
Write-Host "• Core company information (trading name, VAT, parent company)" -ForegroundColor White
Write-Host "• Structured primary contact details" -ForegroundColor White
Write-Host "• Services and experience data" -ForegroundColor White
Write-Host "• Basic role capabilities (boolean fields only)" -ForegroundColor White
Write-Host "• Basic certifications and insurance flags" -ForegroundColor White
Write-Host "• Core compliance and agreement flags" -ForegroundColor White
Write-Host ""
Write-Host "Package ready for import: $zipPath" -ForegroundColor Green
Write-Host ""
Write-Host "STRATEGY:" -ForegroundColor Yellow
Write-Host "1. Import this test package first (should work 100%)" -ForegroundColor White
Write-Host "2. Once working, we'll add more fields incrementally" -ForegroundColor White
Write-Host "3. Test each batch to identify exact SharePoint field names" -ForegroundColor White
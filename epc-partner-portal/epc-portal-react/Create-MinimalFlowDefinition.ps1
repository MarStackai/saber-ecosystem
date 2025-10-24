#!/usr/bin/pwsh
<#
.SYNOPSIS
    Creates a minimal updated Power Automate flow definition with only core extended fields
.DESCRIPTION
    Updates the flow with only the most essential extended fields that we know exist in SharePoint
#>

param(
    [string]$InputPath = "./power-automate-export",
    [string]$OutputPath = "./power-automate-export-minimal"
)

Write-Host "Creating minimal extended flow definition..." -ForegroundColor Yellow

# Copy original structure
if (Test-Path $OutputPath) { Remove-Item $OutputPath -Recurse -Force }
Copy-Item $InputPath $OutputPath -Recurse -Force

# Load the flow definition
$definitionPath = "$OutputPath/Microsoft.Flow/flows/45991de2-99f2-422e-864f-efdf8db8cb93/definition.json"
$definition = Get-Content $definitionPath -Raw | ConvertFrom-Json

Write-Host "Adding core extended field mappings..." -ForegroundColor Yellow

# Only add fields we're confident exist in SharePoint (core company/contact fields)
$coreFields = @{
    "item/TradingName" = "@triggerBody()?['companyInfo']?['tradingName']"
    "item/VATNumber" = "@triggerBody()?['companyInfo']?['vatNumber']"
    "item/ParentCompany" = "@triggerBody()?['companyInfo']?['parentCompany']"
    "item/YearsTrading" = "@triggerBody()?['companyInfo']?['yearsTrading']"
    "item/PrimaryContactName" = "@coalesce(triggerBody()?['primaryContact']?['fullName'], triggerBody()?['contactName'])"
    "item/PrimaryContactTitle" = "@coalesce(triggerBody()?['primaryContact']?['jobTitle'], triggerBody()?['contactTitle'])"
    "item/PrimaryContactPhone" = "@coalesce(triggerBody()?['primaryContact']?['phone'], triggerBody()?['phone'])"
    "item/PrimaryContactEmail" = "@coalesce(triggerBody()?['primaryContact']?['email'], triggerBody()?['email'])"
    "item/Specialisations" = "@triggerBody()?['servicesExperience']?['specializations']"
    "item/SoftwareUsed" = "@triggerBody()?['servicesExperience']?['softwareTools']"
    "item/ProjectsPerMonth" = "@triggerBody()?['servicesExperience']?['averageProjectsPerMonth']"
    "item/ActsAsPrincipalContractor" = "@triggerBody()?['rolesCapabilities']?['principalContractor']"
    "item/ActsAsPrincipalDesigner" = "@triggerBody()?['rolesCapabilities']?['principalDesigner']"
    "item/AdditionalInfo" = "@triggerBody()?['submission']?['additionalInformation']"
    "item/ReferenceNumber" = "@coalesce(triggerBody()?['referenceNumber'], concat('EPC-', utcNow('yyyyMMddHHmmss')))"
}

# Find the Create_item action and add core fields
$createItemAction = $definition.properties.definition.actions.Condition.actions.Create_item
if ($createItemAction -and $createItemAction.inputs -and $createItemAction.inputs.parameters) {
    
    # Add each core field mapping
    foreach ($field in $coreFields.GetEnumerator()) {
        $fieldName = $field.Key
        $fieldExpression = $field.Value
        $createItemAction.inputs.parameters | Add-Member -NotePropertyName $fieldName -NotePropertyValue $fieldExpression -Force
    }
    
    Write-Host "✅ Added $($coreFields.Count) core field mappings" -ForegroundColor Green
} else {
    Write-Host "❌ Could not find Create_item action" -ForegroundColor Red
    exit 1
}

# Update email notifications with core extended data
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

# Add basic extended schema to trigger (just the core sections)
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
    
    Write-Host "✅ Updated trigger schema with core extended sections" -ForegroundColor Green
}

# Save updated definition
$definition | ConvertTo-Json -Depth 50 | Set-Content $definitionPath -Encoding UTF8
Write-Host "✅ Updated definition saved" -ForegroundColor Green

# Create minimal package
Write-Host "Creating minimal package..." -ForegroundColor Yellow
$zipPath = "$OutputPath.zip"
if (Test-Path $zipPath) { Remove-Item $zipPath }
Compress-Archive -Path "$OutputPath/*" -DestinationPath $zipPath
Write-Host "✅ Minimal package created: $zipPath" -ForegroundColor Green

Write-Host "`n=======================================" -ForegroundColor Cyan
Write-Host "✅ Minimal Flow Definition Complete!" -ForegroundColor Green
Write-Host "=======================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Summary:" -ForegroundColor Yellow
Write-Host "• Added $($coreFields.Count) core extended field mappings" -ForegroundColor White
Write-Host "• Updated trigger schema with core form sections" -ForegroundColor White
Write-Host "• Enhanced email notifications" -ForegroundColor White
Write-Host "• Maintained full backward compatibility" -ForegroundColor White
Write-Host ""
Write-Host "Package ready: $zipPath" -ForegroundColor Green
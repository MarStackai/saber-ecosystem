#!/usr/bin/pwsh

param(
    [string]$InputPath = "./power-automate-export",
    [string]$OutputPath = "./power-automate-export-simple-working"
)

Write-Host "Creating simple working flow..." -ForegroundColor Yellow

# Copy original structure
if (Test-Path $OutputPath) { Remove-Item $OutputPath -Recurse -Force }
Copy-Item $InputPath $OutputPath -Recurse -Force

# Load the flow definition
$definitionPath = "$OutputPath/Microsoft.Flow/flows/45991de2-99f2-422e-864f-efdf8db8cb93/definition.json"
$definition = Get-Content $definitionPath -Raw | ConvertFrom-Json

Write-Host "Finding Create_item action..." -ForegroundColor Yellow

# Find Create_item action in the current structure
$createItemAction = $null
if ($definition.properties.definition.actions.Create_item) {
    $createItemAction = $definition.properties.definition.actions.Create_item
    Write-Host "Found Create_item at root level" -ForegroundColor Green
} elseif ($definition.properties.definition.actions.Condition.actions.Create_item) {
    $createItemAction = $definition.properties.definition.actions.Condition.actions.Create_item
    Write-Host "Found Create_item under Condition" -ForegroundColor Green
} else {
    # Search for any action with CreateItem operation
    foreach ($actionName in $definition.properties.definition.actions.PSObject.Properties.Name) {
        $action = $definition.properties.definition.actions.$actionName
        if ($action.type -eq "OpenApiConnection" -and $action.inputs.host.operationId -eq "PostItem") {
            $createItemAction = $action
            Write-Host "Found Create_item action: $actionName" -ForegroundColor Green
            break
        }
    }
}

if ($createItemAction -and $createItemAction.inputs -and $createItemAction.inputs.parameters) {
    
    # Clear existing parameters and add minimal working set
    $createItemAction.inputs.parameters = @{
        "item/Title" = "@triggerBody()?['companyName']"
        "item/CompanyName" = "@triggerBody()?['companyName']"
        "item/TradingName" = "@triggerBody()?['tradingName']"
        "item/PrimaryContactName" = "@triggerBody()?['contactName']"
        "item/PrimaryContactEmail" = "@triggerBody()?['email']"
        "item/PrimaryContactPhone" = "@triggerBody()?['phone']"
        "item/Specialisations" = "@triggerBody()?['specializations']"
        "item/SoftwareUsed" = "@triggerBody()?['softwareTools']"
        "item/ProjectsPerMonth" = "@triggerBody()?['projectsPerMonth']"
        "item/VATNumber" = "@triggerBody()?['vatNumber']"
        "item/CompanyRegNo" = "@triggerBody()?['companyRegNo']"
        "item/ParentCompany" = "@triggerBody()?['parentCompany']"
        "item/YearsTrading" = "@triggerBody()?['yearsTrading']"
        "item/RegisteredOffice" = "@triggerBody()?['registeredOffice']"
        "item/HeadOffice" = "@triggerBody()?['headOffice']"
        "item/InvitationCode" = "@triggerBody()?['invitationCode']"
        "item/ReferenceNumber" = "@concat('EPC-', utcNow('yyyyMMddHHmmss'))"
        "item/SubmissionStatus" = "Submitted"
        "item/SubmissionDate" = "@utcNow()"
        "item/AdditionalInfo" = "@triggerBody()?['additionalInformation']"
        "item/ActsAsPrincipalContractor" = "@if(equals(triggerBody()?['principalContractor'], true), 'Yes', 'No')"
        "item/ActsAsPrincipalDesigner" = "@if(equals(triggerBody()?['principalDesigner'], true), 'Yes', 'No')"
        "item/NICEIC_CPS" = "@if(equals(triggerBody()?['niceicContractor'], true), 'True', 'False')"
        "item/MCS_Approved" = "@if(equals(triggerBody()?['mcsApproved'], true), 'True', 'False')"
        "item/DataProcessingConsent" = "@if(equals(triggerBody()?['dataProcessingConsent'], true), 'True', 'False')"
        "item/MarketingConsent" = "@if(equals(triggerBody()?['marketingConsent'], true), 'True', 'False')"
        "item/AgreeToCodes" = "@if(equals(triggerBody()?['agreeToCodes'], true), 'True', 'False')"
        "item/PublicProductLiability_Present" = "@if(equals(triggerBody()?['publicLiabilityInsurance'], true), 'True', 'False')"
        "item/EmployersLiability_Present" = "@if(equals(triggerBody()?['employersLiabilityInsurance'], true), 'True', 'False')"
        "item/ProfIndemnity_Present" = "@if(equals(triggerBody()?['professionalIndemnityInsurance'], true), 'True', 'False')"
    }
    
    Write-Host "✅ Added working field set" -ForegroundColor Green
} else {
    Write-Host "❌ Could not find Create_item action" -ForegroundColor Red
    
    # Show available actions for debugging
    Write-Host "Available actions:" -ForegroundColor Yellow
    foreach ($actionName in $definition.properties.definition.actions.PSObject.Properties.Name) {
        Write-Host "- $actionName" -ForegroundColor Gray
    }
    exit 1
}

# Save updated definition
$definition | ConvertTo-Json -Depth 50 | Set-Content $definitionPath -Encoding UTF8
Write-Host "✅ Updated definition saved" -ForegroundColor Green

# Create package
Write-Host "Creating package..." -ForegroundColor Yellow
$zipPath = "$OutputPath.zip"
if (Test-Path $zipPath) { Remove-Item $zipPath }
Compress-Archive -Path "$OutputPath/*" -DestinationPath $zipPath
Write-Host "✅ Package created: $zipPath" -ForegroundColor Green

Write-Host "`n=======================================" -ForegroundColor Cyan
Write-Host "✅ Simple Working Flow Ready!" -ForegroundColor Green
Write-Host "=======================================" -ForegroundColor Cyan
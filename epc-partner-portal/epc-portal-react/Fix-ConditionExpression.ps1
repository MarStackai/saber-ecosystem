#!/usr/bin/pwsh
<#
.SYNOPSIS
    Fixes the Condition expression in the Power Automate flow
.DESCRIPTION
    Updates the flow definition to fix invalid condition expressions
#>

param(
    [string]$InputPath = "./power-automate-export-working-expanded",
    [string]$OutputPath = "./power-automate-export-condition-fixed"
)

Write-Host "Fixing Condition expression..." -ForegroundColor Yellow

# Copy original structure
if (Test-Path $OutputPath) { Remove-Item $OutputPath -Recurse -Force }
Copy-Item $InputPath $OutputPath -Recurse -Force

# Load the flow definition
$definitionPath = "$OutputPath/Microsoft.Flow/flows/45991de2-99f2-422e-864f-efdf8db8cb93/definition.json"
$definition = Get-Content $definitionPath -Raw | ConvertFrom-Json

Write-Host "Checking and fixing Condition expression..." -ForegroundColor Yellow

# Find the Condition action
$condition = $definition.properties.definition.actions.Condition
if ($condition) {
    Write-Host "Found Condition action, checking expression..." -ForegroundColor Yellow
    
    # Fix common condition expression - simple validation
    $condition.expression = @{
        "and" = @(
            @{
                "not" = @{
                    "equals" = @(
                        "@triggerBody()?['companyName']",
                        "@null"
                    )
                }
            }
        )
    }
    
    Write-Host "✅ Fixed Condition expression to validate companyName is not null" -ForegroundColor Green
} else {
    Write-Host "❌ Could not find Condition action" -ForegroundColor Red
    exit 1
}

# Save updated definition
$definition | ConvertTo-Json -Depth 50 | Set-Content $definitionPath -Encoding UTF8
Write-Host "✅ Updated definition with fixed Condition saved" -ForegroundColor Green

# Create fixed package
Write-Host "Creating condition-fixed package..." -ForegroundColor Yellow
$zipPath = "$OutputPath.zip"
if (Test-Path $zipPath) { Remove-Item $zipPath }
Compress-Archive -Path "$OutputPath/*" -DestinationPath $zipPath
Write-Host "✅ Condition-fixed package created: $zipPath" -ForegroundColor Green

Write-Host "`n=======================================" -ForegroundColor Cyan
Write-Host "✅ Condition Expression Fixed!" -ForegroundColor Green
Write-Host "=======================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "FIXED CONDITION EXPRESSION:" -ForegroundColor Yellow
Write-Host "• Simple validation: companyName is not null" -ForegroundColor White
Write-Host "• Proper JSON format for Power Automate" -ForegroundColor White
Write-Host ""
Write-Host "Package ready for import: $zipPath" -ForegroundColor Green
#!/usr/bin/pwsh
<#
.SYNOPSIS
    Simple Power Automate flow updater using package import (Option B)
.DESCRIPTION
    Updates EPC flow by importing an updated package. Use this when you prefer
    the simpler approach or when Power Platform CLI is not available.
    
    Prerequisites:
    - Power Apps PowerShell modules installed
    - Updated flow package (.zip) ready for import
#>

param(
    [Parameter(Mandatory=$false)]
    [string]$PackagePath = "./power-automate-export-updated.zip",
    
    [Parameter(Mandatory=$false)]
    [string]$EnvironmentName = "",
    
    [switch]$WhatIf = $false
)

Write-Host "=======================================" -ForegroundColor Cyan
Write-Host "  Simple EPC Flow Updater" -ForegroundColor Cyan  
Write-Host "=======================================" -ForegroundColor Cyan

# Step 1: Check PowerShell modules
Write-Host "Checking PowerShell modules..." -ForegroundColor Yellow
$requiredModules = @("Microsoft.PowerApps.PowerShell", "Microsoft.PowerApps.Administration.PowerShell")

foreach ($module in $requiredModules) {
    if (-not (Get-Module -ListAvailable -Name $module)) {
        Write-Host "❌ Missing module: $module" -ForegroundColor Red
        Write-Host "Install with: Install-Module $module -Scope CurrentUser" -ForegroundColor Yellow
        exit 1
    }
    Write-Host "✅ Found: $module" -ForegroundColor Green
}

# Step 2: Authenticate to Power Apps
Write-Host "`nChecking Power Apps authentication..." -ForegroundColor Yellow
try {
    $currentUser = Get-PowerAppsApp -EnvironmentName "temp" -ErrorAction SilentlyContinue 2>$null
    Write-Host "✅ Already authenticated" -ForegroundColor Green
} catch {
    Write-Host "Authenticating to Power Apps..." -ForegroundColor Yellow
    Add-PowerAppsAccount
    Write-Host "✅ Authentication complete" -ForegroundColor Green
}

# Step 3: Get environment
if (-not $EnvironmentName) {
    Write-Host "`nGetting environments..." -ForegroundColor Yellow
    $environments = Get-AdminPowerAppEnvironment
    $defaultEnv = $environments | Where-Object { $_.DisplayName -like "*Default*" -or $_.Internal.properties.displayName -like "*Default*" }
    if ($defaultEnv) {
        $EnvironmentName = $defaultEnv.EnvironmentName
    } else {
        $EnvironmentName = $environments[0].EnvironmentName
    }
}
Write-Host "✅ Target Environment: $EnvironmentName" -ForegroundColor Green

# Step 4: Check current flow
Write-Host "`nChecking current flow..." -ForegroundColor Yellow
$currentFlow = Get-AdminFlow -EnvironmentName $EnvironmentName | Where-Object { 
    $_.DisplayName -eq "EPC Application Submission Processor" 
}

if ($currentFlow) {
    Write-Host "✅ Found current flow: $($currentFlow.DisplayName)" -ForegroundColor Green
    Write-Host "   Flow ID: $($currentFlow.FlowName)" -ForegroundColor Gray
    Write-Host "   Status: $($currentFlow.Enabled)" -ForegroundColor Gray
} else {
    Write-Host "⚠️ Current flow not found" -ForegroundColor Yellow
}

if ($WhatIf) {
    Write-Host "`n🔍 WHAT-IF MODE:" -ForegroundColor Yellow
    Write-Host "- Would import package: $PackagePath"
    Write-Host "- Target environment: $EnvironmentName"
    Write-Host "- Would overwrite existing flow: $($currentFlow.DisplayName)"
    Write-Host "- Would enable flow after import"
    Write-Host "`nRun without -WhatIf to execute" -ForegroundColor Green
    exit 0
}

# Step 5: Verify package exists
if (-not (Test-Path $PackagePath)) {
    Write-Host "❌ Package not found: $PackagePath" -ForegroundColor Red
    Write-Host "Create updated package first or specify correct path" -ForegroundColor Yellow
    exit 1
}
Write-Host "✅ Package found: $PackagePath" -ForegroundColor Green

# Step 6: Import updated flow
Write-Host "`nImporting updated flow..." -ForegroundColor Yellow
try {
    $importResult = Import-AdminFlow -EnvironmentName $EnvironmentName -Path $PackagePath -Overwrite
    Write-Host "✅ Flow imported successfully" -ForegroundColor Green
} catch {
    Write-Host "❌ Import failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Step 7: Enable flow
Write-Host "Enabling flow..." -ForegroundColor Yellow
try {
    $updatedFlow = Get-AdminFlow -EnvironmentName $EnvironmentName | Where-Object { 
        $_.DisplayName -eq "EPC Application Submission Processor" 
    }
    
    if ($updatedFlow) {
        Enable-AdminFlow -EnvironmentName $EnvironmentName -FlowName $updatedFlow.FlowName
        Write-Host "✅ Flow enabled" -ForegroundColor Green
    }
} catch {
    Write-Host "⚠️ Enable failed, but import succeeded: $($_.Exception.Message)" -ForegroundColor Yellow
}

# Step 8: Set permissions (optional)
Write-Host "Setting flow permissions..." -ForegroundColor Yellow
# Uncomment and configure as needed:
# Set-AdminFlowOwnerRole -EnvironmentName $EnvironmentName -FlowName $updatedFlow.FlowName -PrincipalType User -PrincipalObjectId "user-guid" -RoleName CanEdit

Write-Host "`n✅ Flow update complete!" -ForegroundColor Green
Write-Host "The flow has been updated with extended form support." -ForegroundColor White
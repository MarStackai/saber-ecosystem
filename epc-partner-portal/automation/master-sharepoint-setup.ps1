#!/snap/bin/pwsh
<#
.SYNOPSIS
    Master SharePoint Setup Script for EPC Portal
.DESCRIPTION
    Complete setup and configuration of SharePoint lists for EPC Partner Portal
    This script ensures all required columns and configurations are in place
.AUTHOR
    Saber Renewables Business Operations
.DATE
    September 2025
#>

param(
    [string]$SiteUrl = "https://saberrenewables.sharepoint.com/sites/SaberEPCPartners",
    [string]$ClientId = "bbbfe394-7cff-4ac9-9e01-33cbf116b930",
    [string]$Tenant = "saberrenewables.onmicrosoft.com",
    [switch]$Force,
    [switch]$AddTestData
)

# Import configuration
$configPath = "/home/marstack/saber_business_ops/config.json"
if (Test-Path $configPath) {
    $config = Get-Content $configPath | ConvertFrom-Json
    if (-not $SiteUrl) { $SiteUrl = $config.SharePoint.SiteUrl }
    if (-not $ClientId) { $ClientId = $config.SharePoint.ClientId }
    if (-not $Tenant) { $Tenant = $config.SharePoint.Tenant }
}

Write-Host @"
╔════════════════════════════════════════════╗
║   EPC PORTAL SHAREPOINT MASTER SETUP       ║
╚════════════════════════════════════════════╝
"@ -ForegroundColor Cyan

Write-Host "Configuration:" -ForegroundColor Yellow
Write-Host "  Site URL: $SiteUrl" -ForegroundColor Gray
Write-Host "  Client ID: $ClientId" -ForegroundColor Gray
Write-Host "  Tenant: $Tenant" -ForegroundColor Gray
Write-Host ""

# Function to safely add fields
function Add-SafeField {
    param(
        [string]$ListName,
        [string]$FieldName,
        [string]$DisplayName,
        [string]$Type,
        [array]$Choices,
        [bool]$Required = $false,
        [string]$DefaultValue
    )
    
    try {
        $existingField = Get-PnPField -List $ListName -Identity $FieldName -ErrorAction SilentlyContinue
        
        if ($existingField -and -not $Force) {
            Write-Host "    ⚠ Field '$FieldName' already exists" -ForegroundColor Yellow
            return $true
        }
        
        if ($existingField -and $Force) {
            Write-Host "    ↻ Updating field '$FieldName'" -ForegroundColor Cyan
            # Update field properties if needed
            if ($Choices) {
                Set-PnPField -List $ListName -Identity $FieldName -Values @{Choices=$Choices}
            }
            return $true
        }
        
        $params = @{
            List = $ListName
            DisplayName = $DisplayName
            InternalName = $FieldName
            Type = $Type
        }
        
        if ($Required) { $params.Required = $true }
        if ($Choices) { $params.Choices = $Choices }
        
        Add-PnPField @params | Out-Null
        
        if ($DefaultValue) {
            Set-PnPField -List $ListName -Identity $FieldName -Values @{DefaultValue=$DefaultValue}
        }
        
        Write-Host "    ✓ Added field '$FieldName'" -ForegroundColor Green
        return $true
        
    } catch {
        Write-Host "    ✗ Failed to add field '$FieldName': $_" -ForegroundColor Red
        return $false
    }
}

try {
    # Connect to SharePoint
    Write-Host "Connecting to SharePoint..." -ForegroundColor Yellow
    Connect-PnPOnline -Url $SiteUrl -ClientId $ClientId -Tenant $Tenant -DeviceLogin
    Write-Host "✓ Connected successfully`n" -ForegroundColor Green
    
    # =====================================
    # SETUP EPC INVITATIONS LIST
    # =====================================
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor DarkGray
    Write-Host "Setting up EPC Invitations List" -ForegroundColor Cyan
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor DarkGray
    
    $invitationsList = Get-PnPList -Identity "EPC Invitations" -ErrorAction SilentlyContinue
    
    if (-not $invitationsList) {
        Write-Host "  Creating EPC Invitations list..." -ForegroundColor Yellow
        New-PnPList -Title "EPC Invitations" -Template GenericList
        Write-Host "  ✓ List created" -ForegroundColor Green
    } else {
        Write-Host "  ✓ EPC Invitations list exists" -ForegroundColor Green
    }
    
    Write-Host "`n  Adding required columns:" -ForegroundColor Yellow
    
    # Define all required columns for EPC Invitations
    $invitationColumns = @(
        @{Name="Code"; Display="Invitation Code"; Type="Text"; Required=$true},
        @{Name="Status"; Display="Status"; Type="Choice"; Choices=@("Active","Expired","Used"); Required=$true; Default="Active"},
        @{Name="CompanyName"; Display="Company Name"; Type="Text"; Required=$false},
        @{Name="ContactEmail"; Display="Contact Email"; Type="Text"; Required=$false},
        @{Name="ExpiryDate"; Display="Expiry Date"; Type="DateTime"; Required=$false},
        @{Name="Used"; Display="Used"; Type="Boolean"; Required=$false; Default="0"},
        @{Name="UsedBy"; Display="Used By"; Type="Text"; Required=$false},
        @{Name="UsedDate"; Display="Used Date"; Type="DateTime"; Required=$false},
        @{Name="InviteSentDate"; Display="Invite Sent Date"; Type="DateTime"; Required=$false},
        @{Name="AccessCount"; Display="Access Count"; Type="Number"; Required=$false; Default="0"},
        @{Name="Notes"; Display="Notes"; Type="Note"; Required=$false}
    )
    
    foreach ($col in $invitationColumns) {
        $result = Add-SafeField -ListName "EPC Invitations" `
            -FieldName $col.Name `
            -DisplayName $col.Display `
            -Type $col.Type `
            -Choices $col.Choices `
            -Required $col.Required `
            -DefaultValue $col.Default
    }
    
    # =====================================
    # SETUP EPC ONBOARDING LIST
    # =====================================
    Write-Host "`n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor DarkGray
    Write-Host "Setting up EPC Onboarding List" -ForegroundColor Cyan
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor DarkGray
    
    $onboardingList = Get-PnPList -Identity "EPC Onboarding" -ErrorAction SilentlyContinue
    
    if (-not $onboardingList) {
        Write-Host "  Creating EPC Onboarding list..." -ForegroundColor Yellow
        New-PnPList -Title "EPC Onboarding" -Template GenericList
        Write-Host "  ✓ List created" -ForegroundColor Green
    } else {
        Write-Host "  ✓ EPC Onboarding list exists" -ForegroundColor Green
    }
    
    Write-Host "`n  Adding required columns:" -ForegroundColor Yellow
    
    # Define all required columns for EPC Onboarding
    $onboardingColumns = @(
        @{Name="CompanyName"; Display="Company Name"; Type="Text"; Required=$true},
        @{Name="RegistrationNumber"; Display="Registration Number"; Type="Text"; Required=$true},
        @{Name="ContactName"; Display="Contact Name"; Type="Text"; Required=$true},
        @{Name="ContactTitle"; Display="Contact Title"; Type="Text"; Required=$true},
        @{Name="Email"; Display="Email"; Type="Text"; Required=$true},
        @{Name="Phone"; Display="Phone"; Type="Text"; Required=$true},
        @{Name="Address"; Display="Address"; Type="Note"; Required=$true},
        @{Name="Services"; Display="Services"; Type="Note"; Required=$false},
        @{Name="YearsExperience"; Display="Years Experience"; Type="Number"; Required=$true},
        @{Name="TeamSize"; Display="Team Size"; Type="Number"; Required=$true},
        @{Name="Coverage"; Display="Coverage"; Type="Note"; Required=$true},
        @{Name="Certifications"; Display="Certifications"; Type="Note"; Required=$false},
        @{Name="InvitationCode"; Display="Invitation Code"; Type="Text"; Required=$true},
        @{Name="SubmissionDate"; Display="Submission Date"; Type="DateTime"; Required=$true},
        @{Name="Status"; Display="Status"; Type="Choice"; Choices=@("New","InReview","Approved","Rejected","Submitted"); Required=$true; Default="New"},
        @{Name="SubmissionHandled"; Display="Submission Handled"; Type="Boolean"; Required=$false; Default="0"},
        @{Name="SubmissionFolder"; Display="Submission Folder"; Type="Text"; Required=$false},
        @{Name="ReviewedBy"; Display="Reviewed By"; Type="User"; Required=$false},
        @{Name="ReviewDate"; Display="Review Date"; Type="DateTime"; Required=$false},
        @{Name="Notes"; Display="Notes"; Type="Note"; Required=$false}
    )
    
    foreach ($col in $onboardingColumns) {
        $result = Add-SafeField -ListName "EPC Onboarding" `
            -FieldName $col.Name `
            -DisplayName $col.Display `
            -Type $col.Type `
            -Choices $col.Choices `
            -Required $col.Required `
            -DefaultValue $col.Default
    }
    
    # =====================================
    # SETUP DOCUMENT LIBRARY
    # =====================================
    Write-Host "`n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor DarkGray
    Write-Host "Setting up Document Library" -ForegroundColor Cyan
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor DarkGray
    
    $docLib = Get-PnPList -Identity "EPC Submissions" -ErrorAction SilentlyContinue
    
    if (-not $docLib) {
        Write-Host "  Creating EPC Submissions library..." -ForegroundColor Yellow
        New-PnPList -Title "EPC Submissions" -Template DocumentLibrary
        Write-Host "  ✓ Document library created" -ForegroundColor Green
    } else {
        Write-Host "  ✓ EPC Submissions library exists" -ForegroundColor Green
    }
    
    # =====================================
    # ADD TEST DATA
    # =====================================
    if ($AddTestData) {
        Write-Host "`n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor DarkGray
        Write-Host "Adding Test Data" -ForegroundColor Cyan
        Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor DarkGray
        
        $testCodes = @(
            @{Code="TEST2024"; Company="Test Company Ltd"; Status="Active"},
            @{Code="DEMO2024"; Company="Demo Partners"; Status="Active"},
            @{Code="TRIAL2024"; Company="Trial Corporation"; Status="Active"}
        )
        
        foreach ($test in $testCodes) {
            # Check if code already exists
            $existing = Get-PnPListItem -List "EPC Invitations" -Query "<View><Query><Where><Eq><FieldRef Name='Code'/><Value Type='Text'>$($test.Code)</Value></Eq></Where></Query></View>"
            
            if ($existing.Count -eq 0) {
                $futureDate = (Get-Date).AddDays(30)
                
                Add-PnPListItem -List "EPC Invitations" -Values @{
                    Title = $test.Code
                    Code = $test.Code
                    CompanyName = $test.Company
                    Status = $test.Status
                    ExpiryDate = $futureDate
                    Used = $false
                    AccessCount = 0
                    Notes = "Test invitation code"
                } | Out-Null
                
                Write-Host "  ✓ Added test code: $($test.Code)" -ForegroundColor Green
            } else {
                Write-Host "  ⚠ Test code already exists: $($test.Code)" -ForegroundColor Yellow
            }
        }
    }
    
    # =====================================
    # CREATE VIEWS
    # =====================================
    Write-Host "`n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor DarkGray
    Write-Host "Setting up List Views" -ForegroundColor Cyan
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor DarkGray
    
    # Views for EPC Invitations
    $invitationViews = @(
        @{
            Name = "Active Invitations"
            Fields = @("Code","CompanyName","Status","ExpiryDate","Used")
            Query = "<Where><Eq><FieldRef Name='Status'/><Value Type='Choice'>Active</Value></Eq></Where>"
        },
        @{
            Name = "Used Codes"
            Fields = @("Code","CompanyName","UsedBy","UsedDate")
            Query = "<Where><Eq><FieldRef Name='Used'/><Value Type='Boolean'>1</Value></Eq></Where>"
        },
        @{
            Name = "Expired"
            Fields = @("Code","CompanyName","ExpiryDate","Status")
            Query = "<Where><Eq><FieldRef Name='Status'/><Value Type='Choice'>Expired</Value></Eq></Where>"
        }
    )
    
    foreach ($view in $invitationViews) {
        $existingView = Get-PnPView -List "EPC Invitations" -Identity $view.Name -ErrorAction SilentlyContinue
        if (-not $existingView) {
            Add-PnPView -List "EPC Invitations" -Title $view.Name -Fields $view.Fields -Query $view.Query
            Write-Host "  ✓ Created view: $($view.Name)" -ForegroundColor Green
        } else {
            Write-Host "  ⚠ View already exists: $($view.Name)" -ForegroundColor Yellow
        }
    }
    
    # Views for EPC Onboarding
    $onboardingViews = @(
        @{
            Name = "New Submissions"
            Fields = @("CompanyName","ContactName","Email","SubmissionDate","Status")
            Query = "<Where><Eq><FieldRef Name='Status'/><Value Type='Choice'>New</Value></Eq></Where>"
        },
        @{
            Name = "Pending Processing"
            Fields = @("CompanyName","Status","SubmissionHandled","SubmissionDate")
            Query = "<Where><And><Eq><FieldRef Name='Status'/><Value Type='Choice'>Submitted</Value></Eq><Eq><FieldRef Name='SubmissionHandled'/><Value Type='Boolean'>0</Value></Eq></And></Where>"
        },
        @{
            Name = "Approved Partners"
            Fields = @("CompanyName","ContactName","Email","ReviewDate","ReviewedBy")
            Query = "<Where><Eq><FieldRef Name='Status'/><Value Type='Choice'>Approved</Value></Eq></Where>"
        }
    )
    
    foreach ($view in $onboardingViews) {
        $existingView = Get-PnPView -List "EPC Onboarding" -Identity $view.Name -ErrorAction SilentlyContinue
        if (-not $existingView) {
            Add-PnPView -List "EPC Onboarding" -Title $view.Name -Fields $view.Fields -Query $view.Query
            Write-Host "  ✓ Created view: $($view.Name)" -ForegroundColor Green
        } else {
            Write-Host "  ⚠ View already exists: $($view.Name)" -ForegroundColor Yellow
        }
    }
    
    # =====================================
    # SUMMARY
    # =====================================
    Write-Host "`n╔════════════════════════════════════════════╗" -ForegroundColor Green
    Write-Host "║         SETUP COMPLETED SUCCESSFULLY        ║" -ForegroundColor Green
    Write-Host "╚════════════════════════════════════════════╝" -ForegroundColor Green
    
    Write-Host "`nSharePoint Structure:" -ForegroundColor Cyan
    Write-Host "  ✓ EPC Invitations list configured" -ForegroundColor Green
    Write-Host "  ✓ EPC Onboarding list configured" -ForegroundColor Green
    Write-Host "  ✓ EPC Submissions library configured" -ForegroundColor Green
    Write-Host "  ✓ Views created for easy management" -ForegroundColor Green
    
    if ($AddTestData) {
        Write-Host "`nTest Data:" -ForegroundColor Cyan
        Write-Host "  ✓ Test invitation codes added" -ForegroundColor Green
        Write-Host "  Codes: TEST2024, DEMO2024, TRIAL2024" -ForegroundColor Gray
    }
    
    Write-Host "`nKey URLs:" -ForegroundColor Yellow
    Write-Host "  Invitations: $SiteUrl/Lists/EPC%20Invitations" -ForegroundColor White
    Write-Host "  Onboarding: $SiteUrl/Lists/EPC%20Onboarding" -ForegroundColor White
    Write-Host "  Documents: $SiteUrl/EPC%20Submissions" -ForegroundColor White
    
    Write-Host "`nNext Steps:" -ForegroundColor Yellow
    Write-Host "  1. Test the Power Automate flow" -ForegroundColor Gray
    Write-Host "  2. Verify cron job is processing submissions" -ForegroundColor Gray
    Write-Host "  3. Run daily operations script" -ForegroundColor Gray
    
} catch {
    Write-Host "`n✗ Error occurred: $_" -ForegroundColor Red
    Write-Host "Stack Trace:" -ForegroundColor Red
    Write-Host $_.ScriptStackTrace -ForegroundColor DarkRed
    exit 1
} finally {
    Disconnect-PnPOnline -ErrorAction SilentlyContinue
}
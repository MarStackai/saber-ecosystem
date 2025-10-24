#!/usr/bin/pwsh
<#
.SYNOPSIS
    Sets up SharePoint site for invite-only EPC Partner onboarding form
.DESCRIPTION
    Creates SharePoint site, configures permissions, deploys form, and sets up invitation system
.PARAMETER SiteUrl
    SharePoint site collection URL
.PARAMETER ClientId
    Azure AD App Client ID
.PARAMETER Tenant
    Office 365 Tenant
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$SiteUrl = "https://saberrenewables.sharepoint.com/sites/SaberEPCPartners",
    
    [Parameter(Mandatory=$true)]
    [string]$ClientId = "bbbfe394-7cff-4ac9-9e01-33cbf116b930",
    
    [Parameter(Mandatory=$true)]
    [string]$Tenant = "saberrenewables.onmicrosoft.com",
    
    [switch]$DeployForm,
    [switch]$CreateInvitationList
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "EPC Partner Portal Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Connect to SharePoint
Write-Host "`nConnecting to SharePoint..." -ForegroundColor Yellow
Connect-PnPOnline -Url $SiteUrl -ClientId $ClientId -Tenant $Tenant -DeviceLogin

try {
    # 1. Configure Site Settings
    Write-Host "`n1. Configuring site settings..." -ForegroundColor Green
    
    # Update site to allow external sharing
    Set-PnPSite -Url $SiteUrl -SharingCapability ExternalUserAndGuestSharing
    Write-Host "   ✓ External sharing enabled" -ForegroundColor Gray
    
    # 2. Create Invitation Tracking List
    if ($CreateInvitationList) {
        Write-Host "`n2. Creating EPC Invitations list..." -ForegroundColor Green
        
        # Check if list exists
        $inviteList = Get-PnPList -Identity "EPC Invitations" -ErrorAction SilentlyContinue
        
        if (-not $inviteList) {
            # Create list
            New-PnPList -Title "EPC Invitations" -Template GenericList
            Write-Host "   ✓ List created" -ForegroundColor Gray
            
            # Add fields
            Add-PnPField -List "EPC Invitations" -DisplayName "Company Name" -InternalName "CompanyName" -Type Text -Required
            Add-PnPField -List "EPC Invitations" -DisplayName "Contact Email" -InternalName "ContactEmail" -Type Text -Required
            Add-PnPField -List "EPC Invitations" -DisplayName "Invite Code" -InternalName "InviteCode" -Type Text
            Add-PnPField -List "EPC Invitations" -DisplayName "Invite Sent Date" -InternalName "InviteSentDate" -Type DateTime
            Add-PnPField -List "EPC Invitations" -DisplayName "Expiry Date" -InternalName "ExpiryDate" -Type DateTime
            Add-PnPField -List "EPC Invitations" -DisplayName "Status" -InternalName "InviteStatus" -Type Choice -Choices "Pending","Sent","Accessed","Submitted","Expired"
            Add-PnPField -List "EPC Invitations" -DisplayName "Access Count" -InternalName "AccessCount" -Type Number
            Add-PnPField -List "EPC Invitations" -DisplayName "Submission ID" -InternalName "SubmissionID" -Type Text
            Add-PnPField -List "EPC Invitations" -DisplayName "Notes" -InternalName "InviteNotes" -Type Note
            
            Write-Host "   ✓ Fields added" -ForegroundColor Gray
            
            # Create view
            $viewFields = @("CompanyName","ContactEmail","InviteStatus","InviteSentDate","ExpiryDate","AccessCount")
            Add-PnPView -List "EPC Invitations" -Title "Active Invitations" -Fields $viewFields -Query "<Where><Neq><FieldRef Name='InviteStatus'/><Value Type='Choice'>Expired</Value></Neq></Where>"
            Write-Host "   ✓ Views configured" -ForegroundColor Gray
        } else {
            Write-Host "   ℹ EPC Invitations list already exists" -ForegroundColor Yellow
        }
    }
    
    # 3. Create SharePoint Groups
    Write-Host "`n3. Setting up security groups..." -ForegroundColor Green
    
    # Create EPC Applicants group
    $groupName = "EPC Partner Applicants"
    $group = Get-PnPGroup -Identity $groupName -ErrorAction SilentlyContinue
    
    if (-not $group) {
        New-PnPGroup -Title $groupName -Description "External users completing EPC partner applications"
        Write-Host "   ✓ Created $groupName group" -ForegroundColor Gray
        
        # Set permissions - Contribute to list only
        Set-PnPGroupPermissions -Identity $groupName -List "EPC Onboarding" -AddRole "Contribute"
        Write-Host "   ✓ Permissions configured" -ForegroundColor Gray
    } else {
        Write-Host "   ℹ Security group already exists" -ForegroundColor Yellow
    }
    
    # 4. Deploy Form Files
    if ($DeployForm) {
        Write-Host "`n4. Deploying form files..." -ForegroundColor Green
        
        # Create folder in Site Assets
        $folderName = "EPCForm"
        $siteAssetsUrl = "/sites/SaberEPCPartners/SiteAssets"
        
        # Ensure folder exists
        Resolve-PnPFolder -SiteRelativePath "$siteAssetsUrl/$folderName" | Out-Null
        Write-Host "   ✓ Created form folder" -ForegroundColor Gray
        
        # Upload form files
        $formPath = "/home/marstack/saber_business_ops/epc-form"
        $files = @("index.html", "styles.css", "script.js", "sharepoint-integration.js", "saber-logo.svg", "verify-access.html")
        
        foreach ($file in $files) {
            if (Test-Path "$formPath/$file") {
                Add-PnPFile -Path "$formPath/$file" -Folder "$siteAssetsUrl/$folderName" -Force
                Write-Host "   ✓ Uploaded $file" -ForegroundColor Gray
            }
        }
        
        # Create Site Page with embedded form
        Write-Host "`n5. Creating site page..." -ForegroundColor Green
        
        $pageContent = @"
<iframe 
    src='$SiteUrl/SiteAssets/$folderName/verify-access.html' 
    width='100%' 
    height='800px' 
    frameborder='0'
    style='border: none; max-width: 100%;'>
</iframe>
"@
        
        Add-PnPPage -Name "EPCPartnerApplication" -Title "EPC Partner Application" -HeaderLayoutType NoImage
        Set-PnPPage -Identity "EPCPartnerApplication" -Content $pageContent
        Write-Host "   ✓ Page created: $SiteUrl/SitePages/EPCPartnerApplication.aspx" -ForegroundColor Gray
    }
    
    # 5. Create Document Library for Form Attachments
    Write-Host "`n6. Setting up document library..." -ForegroundColor Green
    
    $libName = "EPC Application Documents"
    $lib = Get-PnPList -Identity $libName -ErrorAction SilentlyContinue
    
    if (-not $lib) {
        New-PnPList -Title $libName -Template DocumentLibrary
        Write-Host "   ✓ Document library created" -ForegroundColor Gray
        
        # Set permissions
        Set-PnPList -Identity $libName -BreakRoleInheritance -CopyRoleAssignments
        Write-Host "   ✓ Unique permissions set" -ForegroundColor Gray
    }
    
    # 6. Generate sample invitations
    Write-Host "`n7. Creating sample invitations..." -ForegroundColor Green
    
    $sampleCompanies = @(
        @{Company="Green Energy Solutions Ltd"; Email="contact@greenenergy.test"},
        @{Company="Sustainable Homes UK"; Email="info@sustainablehomes.test"},
        @{Company="EcoTech Partners"; Email="admin@ecotech.test"}
    )
    
    foreach ($company in $sampleCompanies) {
        $inviteCode = [System.Guid]::NewGuid().ToString().Substring(0, 8).ToUpper()
        $expiryDate = (Get-Date).AddDays(30)
        
        Add-PnPListItem -List "EPC Invitations" -Values @{
            CompanyName = $company.Company
            ContactEmail = $company.Email
            InviteCode = $inviteCode
            InviteStatus = "Pending"
            ExpiryDate = $expiryDate
            AccessCount = 0
            InviteNotes = "Sample invitation for testing"
        } | Out-Null
        
        Write-Host "   ✓ Created invitation for $($company.Company)" -ForegroundColor Gray
        Write-Host "     Code: $inviteCode" -ForegroundColor DarkGray
    }
    
    # 7. Display Summary
    Write-Host "`n========================================" -ForegroundColor Cyan
    Write-Host "Setup Complete!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Cyan
    
    Write-Host "`nKey URLs:" -ForegroundColor Yellow
    Write-Host "Form Page: $SiteUrl/SitePages/EPCPartnerApplication.aspx" -ForegroundColor White
    Write-Host "Invitations List: $SiteUrl/Lists/EPC Invitations" -ForegroundColor White
    Write-Host "Submissions List: $SiteUrl/Lists/EPC Onboarding" -ForegroundColor White
    Write-Host "Documents: $SiteUrl/$libName" -ForegroundColor White
    
    Write-Host "`nNext Steps:" -ForegroundColor Yellow
    Write-Host "1. Configure Power Automate flow for sending invitations"
    Write-Host "2. Set up verification endpoint"
    Write-Host "3. Customize email templates"
    Write-Host "4. Test with internal users"
    Write-Host "5. Launch pilot program"
    
} catch {
    Write-Host "`n❌ Error: $_" -ForegroundColor Red
} finally {
    Disconnect-PnPOnline
}

Write-Host "`n========================================" -ForegroundColor Cyan
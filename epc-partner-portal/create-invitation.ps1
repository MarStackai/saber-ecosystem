#!/snap/bin/pwsh
# Create EPC Partner Invitation with Random 8-Character Code

param(
    [Parameter(Mandatory=$true)]
    [string]$CompanyName,
    
    [Parameter(Mandatory=$true)]
    [string]$ContactEmail,
    
    [Parameter(Mandatory=$true)]
    [string]$ContactName,
    
    [int]$DaysValid = 30,
    
    [switch]$SendEmail
)

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  CREATE EPC PARTNER INVITATION" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Function to generate random 8-character code
function New-InvitationCode {
    # Use uppercase letters and numbers (no confusing characters like 0,O,1,I)
    $chars = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'
    $code = ''
    for ($i = 0; $i -lt 8; $i++) {
        $code += $chars[(Get-Random -Maximum $chars.Length)]
    }
    return $code
}

# Connect to SharePoint
Write-Host "Connecting to SharePoint..." -ForegroundColor Yellow
try {
    Connect-PnPOnline `
        -Url "https://saberrenewables.sharepoint.com/sites/SaberEPCPartners" `
        -ClientId "bbbfe394-7cff-4ac9-9e01-33cbf116b930" `
        -Tenant "saberrenewables.onmicrosoft.com" `
        -CertificatePath "$HOME/.certs/SaberEPCAutomation.pfx" `
        -CertificatePassword (ConvertTo-SecureString -String "P@ssw0rd123!" -AsPlainText -Force) `
        -WarningAction SilentlyContinue
    
    Write-Host "✅ Connected to SharePoint" -ForegroundColor Green
    
    # Generate unique code and check it doesn't exist
    $maxAttempts = 10
    $codeFound = $false
    $inviteCode = ""
    
    Write-Host "Generating unique invitation code..." -ForegroundColor Yellow
    
    for ($attempt = 1; $attempt -le $maxAttempts; $attempt++) {
        $inviteCode = New-InvitationCode
        
        # Check if code already exists
        $existing = Get-PnPListItem -List "EPC Invitations" `
            -Query "<View><Query><Where><Eq><FieldRef Name='Code'/><Value Type='Text'>$inviteCode</Value></Eq></Where></Query></View>"
        
        if (-not $existing) {
            $codeFound = $true
            Write-Host "✅ Generated unique code: $inviteCode" -ForegroundColor Green
            break
        }
        
        if ($attempt -eq $maxAttempts) {
            Write-Host "❌ Could not generate unique code after $maxAttempts attempts" -ForegroundColor Red
            Disconnect-PnPOnline
            exit 1
        }
    }
    
    # Create the invitation
    Write-Host ""
    Write-Host "Creating invitation..." -ForegroundColor Yellow
    
    $invitation = @{
        Title = $inviteCode
        Code = $inviteCode
        CompanyName = $CompanyName
        ContactEmail = $ContactEmail
        ContactName = $ContactName
        ExpiryDate = (Get-Date).AddDays($DaysValid).ToString('yyyy-MM-dd')
        Used = $false
        InvitationSent = $false
    }
    
    # Try to add the item (Status field is optional)
    try {
        # Try with Status field first
        $invitationWithStatus = $invitation.Clone()
        $invitationWithStatus["Status"] = "Active"
        $newItem = Add-PnPListItem -List "EPC Invitations" -Values $invitationWithStatus
    } catch {
        # If that fails, try without Status field
        $newItem = Add-PnPListItem -List "EPC Invitations" -Values $invitation
    }
    
    Write-Host "✅ Invitation created successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "================================================" -ForegroundColor Cyan
    Write-Host "  INVITATION DETAILS" -ForegroundColor Cyan
    Write-Host "================================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Company:     $CompanyName" -ForegroundColor White
    Write-Host "Contact:     $ContactName" -ForegroundColor White
    Write-Host "Email:       $ContactEmail" -ForegroundColor White
    Write-Host "Code:        $inviteCode" -ForegroundColor Yellow -BackgroundColor DarkBlue
    Write-Host "Expires:     $(Get-Date (Get-Date).AddDays($DaysValid) -Format 'dd MMMM yyyy')" -ForegroundColor White
    Write-Host "Portal URL:  https://epc.saberrenewable.energy/epc/apply" -ForegroundColor Cyan
    Write-Host ""
    
    if ($SendEmail) {
        Write-Host "📧 Power Automate will automatically send the invitation email" -ForegroundColor Green
    } else {
        Write-Host "📋 Manual Email Template:" -ForegroundColor Yellow
        Write-Host "------------------------" -ForegroundColor Gray
        Write-Host "Subject: Invitation to Join Saber Renewables EPC Partner Network" -ForegroundColor White
        Write-Host ""
        Write-Host "Dear $ContactName," -ForegroundColor White
        Write-Host ""
        Write-Host "We're pleased to invite $CompanyName to join our EPC Partner Network." -ForegroundColor White
        Write-Host ""
        Write-Host "Your invitation code: $inviteCode" -ForegroundColor White
        Write-Host ""
        Write-Host "To apply:" -ForegroundColor White
        Write-Host "1. Visit https://epc.saberrenewable.energy/epc/apply" -ForegroundColor White
        Write-Host "2. Enter your invitation code" -ForegroundColor White
        Write-Host "3. Complete the application" -ForegroundColor White
        Write-Host ""
        Write-Host "This invitation expires on $(Get-Date (Get-Date).AddDays($DaysValid) -Format 'dd MMMM yyyy')." -ForegroundColor White
        Write-Host ""
        Write-Host "Best regards," -ForegroundColor White
        Write-Host "Saber Renewables Partner Team" -ForegroundColor White
    }
    
    Write-Host ""
    Write-Host "================================================" -ForegroundColor Cyan
    
    Disconnect-PnPOnline
    
} catch {
    Write-Host "❌ Error: $_" -ForegroundColor Red
    exit 1
}
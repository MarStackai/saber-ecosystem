#!/snap/bin/pwsh
# Auto-Generate Invitation Code When Creating New Item
# This demonstrates how the code should be generated

param(
    [Parameter(Mandatory=$true)]
    [string]$CompanyName,
    
    [Parameter(Mandatory=$true)]
    [string]$ContactEmail,
    
    [Parameter(Mandatory=$true)]
    [string]$ContactName,
    
    [string]$Notes = ""
)

# Function to generate 8-character code
function New-InvitationCode {
    $chars = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'
    $code = ''
    for ($i = 0; $i -lt 8; $i++) {
        $code += $chars[(Get-Random -Maximum $chars.Length)]
    }
    return $code
}

Write-Host "Creating invitation..." -ForegroundColor Yellow

# Generate unique code
$inviteCode = New-InvitationCode
$expiryDate = (Get-Date).AddDays(30).ToString("yyyy-MM-dd")

Write-Host "Generated Code: $inviteCode" -ForegroundColor Green

# Connect to SharePoint
Connect-PnPOnline `
    -Url "https://saberrenewables.sharepoint.com/sites/SaberEPCPartners" `
    -ClientId "bbbfe394-7cff-4ac9-9e01-33cbf116b930" `
    -Tenant "saberrenewables.onmicrosoft.com" `
    -CertificatePath "$HOME/.certs/SaberEPCAutomation.pfx" `
    -CertificatePassword (ConvertTo-SecureString -String "P@ssw0rd123!" -AsPlainText -Force) `
    -WarningAction SilentlyContinue

# Create the invitation with ALL fields properly set
$invitation = @{
    Title = $inviteCode  # Title field = Code
    Code = $inviteCode   # Code field = Code
    CompanyName = $CompanyName
    ContactName = $ContactName
    ContactEmail = $ContactEmail
    ExpiryDate = $expiryDate
    Used = $false
    InvitationSent = $false
}

# Add notes if provided
if ($Notes) {
    $invitation.Notes = $Notes
}

# Try to add Status field (may not exist)
try {
    $invitation.Status = "Active"
} catch {
    Write-Host "Status field not available" -ForegroundColor Gray
}

# Add the item
$newItem = Add-PnPListItem -List "EPC Invitations" -Values $invitation

Write-Host "✅ Invitation created successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "Details:" -ForegroundColor Cyan
Write-Host "  Company: $CompanyName" -ForegroundColor White
Write-Host "  Contact: $ContactName" -ForegroundColor White
Write-Host "  Email: $ContactEmail" -ForegroundColor White
Write-Host "  Code: $inviteCode" -ForegroundColor Green
Write-Host "  Expires: $expiryDate" -ForegroundColor White
Write-Host ""
Write-Host "The invitation email will be sent automatically by Power Automate." -ForegroundColor Yellow

Disconnect-PnPOnline

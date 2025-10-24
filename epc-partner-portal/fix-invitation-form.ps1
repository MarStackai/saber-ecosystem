#!/snap/bin/pwsh
# Fix SharePoint Invitation Form and Auto-Generation
# This script configures the form to only show necessary fields
# and sets up auto-generation of invitation codes

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  Fixing EPC Invitation Form Configuration" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Configuration
$SiteUrl = "https://saberrenewables.sharepoint.com/sites/SaberEPCPartners"
$ListName = "EPC Invitations"

Write-Host "Connecting to SharePoint..." -ForegroundColor Yellow

try {
    # Connect to SharePoint
    Connect-PnPOnline `
        -Url $SiteUrl `
        -ClientId "bbbfe394-7cff-4ac9-9e01-33cbf116b930" `
        -Tenant "saberrenewables.onmicrosoft.com" `
        -CertificatePath "$HOME/.certs/SaberEPCAutomation.pfx" `
        -CertificatePassword (ConvertTo-SecureString -String "P@ssw0rd123!" -AsPlainText -Force) `
        -WarningAction SilentlyContinue
    
    Write-Host "✅ Connected to SharePoint" -ForegroundColor Green
    Write-Host ""
    
    # Get the list
    $list = Get-PnPList -Identity $ListName
    
    Write-Host "Current List Fields:" -ForegroundColor Yellow
    $fields = Get-PnPField -List $ListName | Where-Object { -not $_.Hidden -and -not $_.ReadOnlyField }
    $fields | Select-Object Title, InternalName, Required | Format-Table
    
    Write-Host ""
    Write-Host "================================================" -ForegroundColor Cyan
    Write-Host "  Form Configuration Instructions" -ForegroundColor Cyan
    Write-Host "================================================" -ForegroundColor Cyan
    Write-Host ""
    
    Write-Host "The NEW FORM should only show these fields:" -ForegroundColor Green
    Write-Host "  ✅ Company Name (Required)" -ForegroundColor White
    Write-Host "  ✅ Contact Name (Required)" -ForegroundColor White
    Write-Host "  ✅ Contact Email (Required)" -ForegroundColor White
    Write-Host "  ✅ Notes (Optional)" -ForegroundColor White
    Write-Host ""
    
    Write-Host "Fields that should be HIDDEN on new form:" -ForegroundColor Yellow
    Write-Host "  ❌ Code (auto-generated)" -ForegroundColor White
    Write-Host "  ❌ Title (auto-generated)" -ForegroundColor White
    Write-Host "  ❌ ExpiryDate (auto-calculated)" -ForegroundColor White
    Write-Host "  ❌ Used (default: No)" -ForegroundColor White
    Write-Host "  ❌ UsedBy (filled when used)" -ForegroundColor White
    Write-Host "  ❌ UsedDate (filled when used)" -ForegroundColor White
    Write-Host "  ❌ InvitationSent (managed by flow)" -ForegroundColor White
    Write-Host "  ❌ Status (managed by system)" -ForegroundColor White
    Write-Host ""
    
    Write-Host "Manual Steps Required in SharePoint:" -ForegroundColor Cyan
    Write-Host "1. Go to: $SiteUrl/Lists/$ListName" -ForegroundColor White
    Write-Host "2. Click ⚙️ Settings → List Settings" -ForegroundColor White
    Write-Host "3. Under 'General Settings' click 'Form settings'" -ForegroundColor White
    Write-Host "4. Or use Power Apps to customize the form:" -ForegroundColor White
    Write-Host "   - Click 'Integrate' → 'Power Apps' → 'Customize forms'" -ForegroundColor White
    Write-Host "   - Hide all fields except Company Name, Contact Name, Contact Email, Notes" -ForegroundColor White
    Write-Host ""
    
    Write-Host "Creating Test Script for Auto-Generation..." -ForegroundColor Yellow
    
    # Create a test script that shows how to auto-generate codes
    $autoGenScript = @'
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
'@
    
    $autoGenScript | Out-File -FilePath "./create-invitation-auto.ps1" -Encoding UTF8
    
    Write-Host "✅ Created: create-invitation-auto.ps1" -ForegroundColor Green
    Write-Host ""
    
    Write-Host "================================================" -ForegroundColor Cyan
    Write-Host "  Power Automate Configuration Required" -ForegroundColor Cyan
    Write-Host "================================================" -ForegroundColor Cyan
    Write-Host ""
    
    Write-Host "Update your Power Automate flow to:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "1. TRIGGER: When an item is created (EPC Invitations)" -ForegroundColor White
    Write-Host ""
    Write-Host "2. CONDITION: Check if Code is empty" -ForegroundColor White
    Write-Host "   - If YES: Generate code and update item" -ForegroundColor White
    Write-Host "   - If NO: Continue with existing code" -ForegroundColor White
    Write-Host ""
    Write-Host "3. For Code Generation in Power Automate:" -ForegroundColor White
    Write-Host "   Expression: " -ForegroundColor Gray
    Write-Host "   concat(" -ForegroundColor Cyan
    Write-Host "     substring(guid(), 0, 4)," -ForegroundColor Cyan
    Write-Host "     substring(toUpper(guid()), 9, 4)" -ForegroundColor Cyan
    Write-Host "   )" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "4. Update Item with:" -ForegroundColor White
    Write-Host "   - Code: [generated code]" -ForegroundColor Gray
    Write-Host "   - Title: [generated code]" -ForegroundColor Gray
    Write-Host "   - ExpiryDate: addDays(utcNow(), 30)" -ForegroundColor Gray
    Write-Host "   - Status: 'Active'" -ForegroundColor Gray
    Write-Host ""
    Write-Host "5. Send Email with the generated code" -ForegroundColor White
    Write-Host ""
    
    Write-Host "================================================" -ForegroundColor Cyan
    Write-Host "  Testing Code Validation" -ForegroundColor Cyan
    Write-Host "================================================" -ForegroundColor Cyan
    Write-Host ""
    
    # Check existing invitations
    Write-Host "Checking existing invitations..." -ForegroundColor Yellow
    $invitations = Get-PnPListItem -List $ListName -PageSize 10 | Select-Object -First 5
    
    if ($invitations) {
        Write-Host ""
        Write-Host "Recent Invitations:" -ForegroundColor Cyan
        foreach ($inv in $invitations) {
            $code = $inv.FieldValues.Code
            $company = $inv.FieldValues.CompanyName
            $used = $inv.FieldValues.Used
            $expiry = $inv.FieldValues.ExpiryDate
            
            if ($code) {
                $status = if ($used) { "❌ Used" } else { "✅ Available" }
                Write-Host "  Code: $code | Company: $company | Status: $status | Expires: $expiry" -ForegroundColor White
            }
        }
    }
    
    Disconnect-PnPOnline
    
} catch {
    Write-Host "❌ Error: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  Next Steps" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Hide unnecessary fields on the new form" -ForegroundColor White
Write-Host "2. Configure Power Automate to auto-generate codes" -ForegroundColor White
Write-Host "3. Test with create-invitation-auto.ps1" -ForegroundColor White
Write-Host "4. Ensure email includes the generated code" -ForegroundColor White
Write-Host ""
Write-Host "✅ Configuration check complete!" -ForegroundColor Green
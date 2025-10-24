#!/snap/bin/pwsh
# Batch Create EPC Partner Invitations

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  BATCH CREATE EPC INVITATIONS" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Define partners to invite (modify this list as needed)
$partners = @(
    @{
        CompanyName = "Solar Excellence Ltd"
        ContactName = "Sarah Johnson"
        ContactEmail = "sarah@solarexcellence.com"
    },
    @{
        CompanyName = "Green Energy Partners"
        ContactName = "Michael Chen"
        ContactEmail = "michael@greenenergypartners.com"
    },
    @{
        CompanyName = "Renewable Solutions Inc"
        ContactName = "Emily Davis"
        ContactEmail = "emily@renewablesolutions.com"
    }
)

# Function to generate random 8-character code
function New-InvitationCode {
    # Use uppercase letters and numbers (excluding confusing characters)
    $chars = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'
    $code = ''
    for ($i = 0; $i -lt 8; $i++) {
        $code += $chars[(Get-Random -Maximum $chars.Length)]
    }
    return $code
}

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
    Write-Host ""
    
    # Get all existing codes to ensure uniqueness
    $existingItems = Get-PnPListItem -List "EPC Invitations"
    $existingCodes = $existingItems | ForEach-Object { $_.FieldValues.Code }
    
    $createdInvitations = @()
    
    foreach ($partner in $partners) {
        Write-Host "Creating invitation for $($partner.CompanyName)..." -ForegroundColor Yellow
        
        # Generate unique code
        $inviteCode = ""
        $attempts = 0
        do {
            $inviteCode = New-InvitationCode
            $attempts++
            if ($attempts -gt 50) {
                Write-Host "❌ Could not generate unique code for $($partner.CompanyName)" -ForegroundColor Red
                continue
            }
        } while ($existingCodes -contains $inviteCode)
        
        # Add to existing codes list
        $existingCodes += $inviteCode
        
        # Create invitation
        $invitation = @{
            Title = $inviteCode
            Code = $inviteCode
            CompanyName = $partner.CompanyName
            ContactEmail = $partner.ContactEmail
            ContactName = $partner.ContactName
            ExpiryDate = (Get-Date).AddDays(30).ToString('yyyy-MM-dd')
            Used = $false
            InvitationSent = $false
        }
        
        try {
            # Try with Status field first
            $invitationWithStatus = $invitation.Clone()
            $invitationWithStatus["Status"] = "Active"
            $newItem = Add-PnPListItem -List "EPC Invitations" -Values $invitationWithStatus
            Write-Host "  ✅ Created: $inviteCode" -ForegroundColor Green
            
            $createdInvitations += [PSCustomObject]@{
                Code = $inviteCode
                Company = $partner.CompanyName
                Contact = $partner.ContactName
                Email = $partner.ContactEmail
            }
        } catch {
            Write-Host "  ❌ Failed: $_" -ForegroundColor Red
        }
    }
    
    Write-Host ""
    Write-Host "================================================" -ForegroundColor Cyan
    Write-Host "  SUMMARY OF CREATED INVITATIONS" -ForegroundColor Cyan
    Write-Host "================================================" -ForegroundColor Cyan
    Write-Host ""
    
    if ($createdInvitations.Count -gt 0) {
        $createdInvitations | Format-Table -AutoSize
        
        Write-Host ""
        Write-Host "Portal URL: https://epc.saberrenewable.energy/epc/apply" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "📧 Power Automate will automatically send invitation emails" -ForegroundColor Green
        Write-Host ""
        
        # Export to CSV for record keeping
        $csvPath = "$HOME/epc-invitations-$(Get-Date -Format 'yyyyMMdd-HHmmss').csv"
        $createdInvitations | Export-Csv -Path $csvPath -NoTypeInformation
        Write-Host "📁 Invitations saved to: $csvPath" -ForegroundColor Yellow
    } else {
        Write-Host "No invitations were created." -ForegroundColor Yellow
    }
    
    Disconnect-PnPOnline
    
} catch {
    Write-Host "❌ Error: $_" -ForegroundColor Red
    exit 1
}
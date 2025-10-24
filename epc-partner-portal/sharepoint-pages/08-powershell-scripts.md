# PowerShell Scripts Reference

## Automation tools for EPC partner management

---

## Available Scripts

### create-invitation.ps1
**Purpose:** Generate single partner invitation with random code

**Usage:**
```powershell
./create-invitation.ps1 `
    -CompanyName "Partner Company Ltd" `
    -ContactEmail "contact@partner.com" `
    -ContactName "John Smith" `
    -DaysValid 30 `
    -SendEmail
```

**Parameters:**
- `-CompanyName` (Required) - Partner company name
- `-ContactEmail` (Required) - Recipient email address
- `-ContactName` (Required) - Primary contact name
- `-DaysValid` (Optional) - Expiry period, default 30
- `-SendEmail` (Optional) - Trigger immediate email

**Output:**
- Unique 8-character code
- SharePoint entry ID
- Email template (if not sent)

---

### batch-create-invitations.ps1
**Purpose:** Create multiple invitations simultaneously

**Setup:**
1. Edit script to add partner list
2. Run script
3. Review generated CSV report

**Example Partner Array:**
```powershell
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
    }
)
```

**Output:**
- Multiple invitation codes
- CSV file with all details
- Bulk email triggers

---

### test-complete-system.sh
**Purpose:** End-to-end system validation

**Usage:**
```bash
./test-complete-system.sh
```

**Tests:**
1. Creates test invitation
2. Validates email trigger
3. Submits test application
4. Verifies SharePoint updates
5. Checks email confirmations

**Output:**
- Test results summary
- System health status
- Performance metrics

---

### add-test-invitations.ps1
**Purpose:** Add predefined test codes for development

**Usage:**
```powershell
./add-test-invitations.ps1
```

**Creates:**
- TEST2024
- DEMO2024
- ABCD1234

⚠️ **Note:** Development environment only

---

## Authentication Setup

### Certificate Configuration
All scripts use certificate authentication to SharePoint.

**Certificate Location:**
```
~/.certs/SaberEPCAutomation.pfx
```

**App Registration:**
- **App ID:** bbbfe394-7cff-4ac9-9e01-33cbf116b930
- **Tenant:** saberrenewables.onmicrosoft.com

### First-Time Setup
1. Ensure certificate exists
2. Verify permissions in Azure AD
3. Test connection:
```powershell
Connect-PnPOnline `
    -Url "https://saberrenewables.sharepoint.com/sites/SaberEPCPartners" `
    -ClientId "bbbfe394-7cff-4ac9-9e01-33cbf116b930" `
    -Tenant "saberrenewables.onmicrosoft.com" `
    -CertificatePath "$HOME/.certs/SaberEPCAutomation.pfx" `
    -CertificatePassword (ConvertTo-SecureString -String "P@ssw0rd123!" -AsPlainText -Force)
```

---

## Common Operations

### List All Invitations
```powershell
Connect-PnPOnline [connection parameters]
$invitations = Get-PnPListItem -List "EPC Invitations"
$invitations | Format-Table Code, CompanyName, Used, ExpiryDate
Disconnect-PnPOnline
```

### Check Specific Code
```powershell
$code = "ABCD1234"
$item = Get-PnPListItem -List "EPC Invitations" | 
    Where-Object {$_.FieldValues.Code -eq $code}
$item.FieldValues
```

### Update Invitation Status
```powershell
Set-PnPListItem -List "EPC Invitations" -Identity $itemId -Values @{
    Used = $true
    UsedBy = "partner@email.com"
    UsedDate = (Get-Date).ToString("yyyy-MM-dd")
}
```

### Export for Reporting
```powershell
$data = Get-PnPListItem -List "EPC Onboarding" -PageSize 500
$data | Select-Object @{
    Name='Company';Expression={$_.FieldValues.CompanyName}
    Name='Status';Expression={$_.FieldValues.Status}
    Name='SubmissionDate';Expression={$_.FieldValues.SubmissionDate}
} | Export-Csv "report-$(Get-Date -Format 'yyyyMMdd').csv" -NoTypeInformation
```

---

## Error Handling

### Common Errors

#### "Certificate could not be read"
**Solution:**
```powershell
# Verify certificate exists
Test-Path "~/.certs/SaberEPCAutomation.pfx"

# Check certificate password
$cert = Get-PfxCertificate -FilePath "~/.certs/SaberEPCAutomation.pfx"
```

#### "Column 'Status' does not exist"
**Solution:**
Scripts handle this gracefully by trying with and without Status field

#### "Access denied"
**Solution:**
1. Verify Azure AD permissions
2. Check certificate thumbprint
3. Confirm app registration

---

## Script Customisation

### Modify Code Generation
Edit function in create-invitation.ps1:
```powershell
function New-InvitationCode {
    $chars = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'
    $code = ''
    for ($i = 0; $i -lt 8; $i++) {
        $code += $chars[(Get-Random -Maximum $chars.Length)]
    }
    return $code
}
```

### Change Email Template
Update email content in script:
```powershell
Write-Host "Your invitation code: $inviteCode"
Write-Host "Portal: https://epc.saberrenewable.energy/epc/apply"
```

### Add Custom Fields
Include additional SharePoint fields:
```powershell
$invitation = @{
    Title = $inviteCode
    Code = $inviteCode
    CompanyName = $CompanyName
    # Add custom fields here
    Region = "UK"
    PartnerType = "EPC"
}
```

---

## Scheduling Scripts

### Windows Task Scheduler
```xml
<Action>
    <Exec>pwsh.exe</Exec>
    <Arguments>-File "C:\Scripts\batch-create-invitations.ps1"</Arguments>
</Action>
```

### Linux Cron
```bash
# Daily at 9 AM
0 9 * * * /snap/bin/pwsh /home/user/create-invitation.ps1
```

---

## Performance Tips

### Batch Operations
```powershell
# Efficient - single query
$items = Get-PnPListItem -List "EPC Invitations" -PageSize 500

# Inefficient - multiple queries
foreach ($code in $codes) {
    $item = Get-PnPListItem -List "EPC Invitations" | Where Code -eq $code
}
```

### Connection Reuse
```powershell
# Connect once
Connect-PnPOnline [parameters]

# Multiple operations
$inv1 = Add-PnPListItem ...
$inv2 = Add-PnPListItem ...
$inv3 = Add-PnPListItem ...

# Disconnect once
Disconnect-PnPOnline
```

---

[← Back to Home](./01-epc-home.md) | [Next: Power Automate Workflows →](./09-power-automate.md)

**Version:** 1.0 | **Last Updated:** September 2025
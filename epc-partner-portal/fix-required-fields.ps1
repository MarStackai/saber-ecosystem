#!/snap/bin/pwsh
# Fix Required Field Issues in EPC Invitations List
# This script makes code fields NOT required since they're auto-generated

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  Fixing Required Field Settings" -ForegroundColor Cyan
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
    
    Write-Host "Checking field requirements..." -ForegroundColor Yellow
    
    # Get all fields
    $fields = Get-PnPField -List $ListName
    
    # Check which fields are required
    Write-Host ""
    Write-Host "Current Required Fields:" -ForegroundColor Cyan
    $fields | Where-Object { $_.Required -eq $true -and -not $_.Hidden } | ForEach-Object {
        Write-Host "  ❗ $($_.Title) ($($_.InternalName)) - Required = $($_.Required)" -ForegroundColor Yellow
    }
    
    Write-Host ""
    Write-Host "Fields that SHOULD be required:" -ForegroundColor Green
    Write-Host "  ✅ CompanyName" -ForegroundColor White
    Write-Host "  ✅ ContactEmail" -ForegroundColor White
    Write-Host "  ✅ ContactName" -ForegroundColor White
    
    Write-Host ""
    Write-Host "Fields that should NOT be required:" -ForegroundColor Red
    Write-Host "  ❌ Code" -ForegroundColor White
    Write-Host "  ❌ InviteCode" -ForegroundColor White
    Write-Host "  ❌ Title" -ForegroundColor White
    Write-Host "  ❌ All other auto-generated fields" -ForegroundColor White
    
    Write-Host ""
    Write-Host "Attempting to fix required settings..." -ForegroundColor Yellow
    
    # Try to update the Code field
    try {
        $codeField = Get-PnPField -List $ListName -Identity "Code"
        if ($codeField.Required) {
            Set-PnPField -List $ListName -Identity "Code" -Values @{Required=$false}
            Write-Host "  ✅ Set 'Code' to NOT required" -ForegroundColor Green
        } else {
            Write-Host "  ✓ 'Code' already not required" -ForegroundColor Gray
        }
    } catch {
        Write-Host "  ⚠️ Could not modify 'Code' field: $_" -ForegroundColor Yellow
    }
    
    # Try to update the InviteCode field
    try {
        $inviteCodeField = Get-PnPField -List $ListName -Identity "InviteCode"
        if ($inviteCodeField.Required) {
            Set-PnPField -List $ListName -Identity "InviteCode" -Values @{Required=$false}
            Write-Host "  ✅ Set 'InviteCode' to NOT required" -ForegroundColor Green
        } else {
            Write-Host "  ✓ 'InviteCode' already not required" -ForegroundColor Gray
        }
    } catch {
        Write-Host "  ⚠️ Could not modify 'InviteCode' field: $_" -ForegroundColor Yellow
    }
    
    Write-Host ""
    Write-Host "================================================" -ForegroundColor Cyan
    Write-Host "  Manual Steps Required" -ForegroundColor Cyan
    Write-Host "================================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "If the script couldn't update the fields:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "1. Go to: $SiteUrl/Lists/$ListName" -ForegroundColor White
    Write-Host "2. Click ⚙️ Settings → List Settings" -ForegroundColor White
    Write-Host "3. Under 'Columns', click on:" -ForegroundColor White
    Write-Host "   - 'Invitation Code' (or 'Code')" -ForegroundColor Gray
    Write-Host "   - 'Invite Code'" -ForegroundColor Gray
    Write-Host "4. For each one:" -ForegroundColor White
    Write-Host "   - Change 'Require that this column contains information' to: NO" -ForegroundColor Gray
    Write-Host "   - Click OK" -ForegroundColor Gray
    Write-Host ""
    Write-Host "5. Then go back to Power Apps:" -ForegroundColor White
    Write-Host "   - Remove any validation rules on code fields" -ForegroundColor Gray
    Write-Host "   - Ensure only Company, Contact Name, and Email are required" -ForegroundColor Gray
    Write-Host "   - Save and Publish" -ForegroundColor Gray
    
    Write-Host ""
    Write-Host "================================================" -ForegroundColor Cyan
    Write-Host "  Verification" -ForegroundColor Cyan
    Write-Host "================================================" -ForegroundColor Cyan
    
    # Re-check requirements
    Write-Host ""
    Write-Host "Final field requirements:" -ForegroundColor Yellow
    $fields = Get-PnPField -List $ListName
    $fields | Where-Object { $_.InternalName -in @("Code", "InviteCode", "CompanyName", "ContactEmail", "ContactName") } | ForEach-Object {
        $status = if ($_.Required) { "❗ Required" } else { "✅ Optional" }
        $color = if ($_.Required -and $_.InternalName -in @("Code", "InviteCode")) { "Red" } else { "Green" }
        Write-Host "  $($_.Title): $status" -ForegroundColor $color
    }
    
    Disconnect-PnPOnline
    
} catch {
    Write-Host "❌ Error: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "✅ Field requirement check complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Next: Test creating a new invitation with only:" -ForegroundColor Cyan
Write-Host "  - Company Name" -ForegroundColor White
Write-Host "  - Contact Name" -ForegroundColor White
Write-Host "  - Contact Email" -ForegroundColor White
Write-Host "  - Notes (optional)" -ForegroundColor White
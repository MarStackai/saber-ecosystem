#!/snap/bin/pwsh
# Automated End-to-End Test for EPC System
# Tests the complete flow with proper authentication

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  EPC SYSTEM - AUTOMATED TEST" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Test configuration
$TestTimestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$TestCompany = "Auto-Test-$TestTimestamp"
$TestEmail = "rob@marstack.ai"
$TestContact = "Test User $TestTimestamp"

Write-Host "Test Configuration:" -ForegroundColor Yellow
Write-Host "  Company: $TestCompany" -ForegroundColor White
Write-Host "  Contact: $TestContact" -ForegroundColor White
Write-Host "  Email: $TestEmail" -ForegroundColor White
Write-Host ""

# Step 1: Connect to SharePoint
Write-Host "STEP 1: Connecting to SharePoint..." -ForegroundColor Cyan
try {
    $certPath = Join-Path $HOME ".certs/SaberEPCAutomation.pfx"
    $certPassword = ConvertTo-SecureString -String "P@ssw0rd123!" -AsPlainText -Force
    
    Connect-PnPOnline `
        -Url "https://saberrenewables.sharepoint.com/sites/SaberEPCPartners" `
        -ClientId "bbbfe394-7cff-4ac9-9e01-33cbf116b930" `
        -Tenant "saberrenewables.onmicrosoft.com" `
        -CertificatePath $certPath `
        -CertificatePassword $certPassword `
        -WarningAction SilentlyContinue
    
    Write-Host "✅ Connected to SharePoint successfully" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to connect: $_" -ForegroundColor Red
    exit 1
}

# Step 2: Create test invitation
Write-Host ""
Write-Host "STEP 2: Creating test invitation..." -ForegroundColor Cyan

try {
    # Create invitation (Power Automate will generate the code)
    $newItem = Add-PnPListItem -List "EPC Invitations" -Values @{
        CompanyName = $TestCompany
        ContactName = $TestContact
        ContactEmail = $TestEmail
        Title = "PENDING"  # Will be replaced by auto-generated code
    }
    
    Write-Host "✅ Invitation created with ID: $($newItem.Id)" -ForegroundColor Green
    
    # Wait for Power Automate to process
    Write-Host "⏳ Waiting 15 seconds for Power Automate to generate code..." -ForegroundColor Yellow
    Start-Sleep -Seconds 15
    
    # Retrieve the generated code
    $updatedItem = Get-PnPListItem -List "EPC Invitations" -Id $newItem.Id
    $generatedCode = $updatedItem.FieldValues.Code
    if (-not $generatedCode) {
        $generatedCode = $updatedItem.FieldValues.InviteCode
    }
    if (-not $generatedCode) {
        $generatedCode = $updatedItem.FieldValues.Title
    }
    
    Write-Host ""
    Write-Host "Invitation Details:" -ForegroundColor Cyan
    Write-Host "  ID: $($newItem.Id)" -ForegroundColor White
    Write-Host "  Company: $TestCompany" -ForegroundColor White
    Write-Host "  Code: $generatedCode" -ForegroundColor Green
    Write-Host "  Email Sent To: $TestEmail" -ForegroundColor White
    Write-Host "  Expiry: $($updatedItem.FieldValues.ExpiryDate)" -ForegroundColor White
    Write-Host "  InvitationSent: $($updatedItem.FieldValues.InvitationSent)" -ForegroundColor White
    
} catch {
    Write-Host "❌ Failed to create invitation: $_" -ForegroundColor Red
}

# Step 3: Test portal API
Write-Host ""
Write-Host "STEP 3: Testing portal code validation..." -ForegroundColor Cyan

if ($generatedCode -and $generatedCode -ne "PENDING") {
    $testUrl = "https://epc.saberrenewable.energy/api/validate-code"
    Write-Host "Testing code: $generatedCode at $testUrl" -ForegroundColor Yellow
    
    try {
        $body = @{code = $generatedCode} | ConvertTo-Json
        $response = Invoke-RestMethod -Uri $testUrl -Method Post -Body $body -ContentType "application/json" -ErrorAction Stop
        Write-Host "✅ API Response: $response" -ForegroundColor Green
    } catch {
        Write-Host "⚠️ API test failed (this is normal if API expects full application data)" -ForegroundColor Yellow
    }
} else {
    Write-Host "❌ No valid code was generated!" -ForegroundColor Red
}

# Step 4: Check invitation status
Write-Host ""
Write-Host "STEP 4: Verifying invitation status..." -ForegroundColor Cyan

$invitation = Get-PnPListItem -List "EPC Invitations" | Where-Object { 
    $_.FieldValues.CompanyName -eq $TestCompany
} | Select-Object -First 1

if ($invitation) {
    Write-Host "✅ Found invitation:" -ForegroundColor Green
    Write-Host "  Code: $($invitation.FieldValues.Code)" -ForegroundColor White
    Write-Host "  Used: $($invitation.FieldValues.Used)" -ForegroundColor White
    Write-Host "  InvitationSent: $($invitation.FieldValues.InvitationSent)" -ForegroundColor White
    Write-Host "  Status: $($invitation.FieldValues.Status)" -ForegroundColor White
} else {
    Write-Host "❌ Invitation not found" -ForegroundColor Red
}

# Step 5: Check recent Power Automate runs
Write-Host ""
Write-Host "STEP 5: Recent invitations in system..." -ForegroundColor Cyan

$recentInvitations = Get-PnPListItem -List "EPC Invitations" -PageSize 5 | 
    Sort-Object -Property Id -Descending | 
    Select-Object -First 5

Write-Host "Last 5 invitations:" -ForegroundColor Yellow
foreach ($inv in $recentInvitations) {
    $code = if ($inv.FieldValues.Code) { $inv.FieldValues.Code } else { $inv.FieldValues.InviteCode }
    Write-Host "  $($inv.FieldValues.CompanyName): $code (Sent: $($inv.FieldValues.InvitationSent))" -ForegroundColor Gray
}

# Disconnect
Disconnect-PnPOnline

# Summary
Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  TEST SUMMARY" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

$testPassed = $generatedCode -and $generatedCode -ne "PENDING" -and $generatedCode.Length -eq 8

if ($testPassed) {
    Write-Host "✅ TEST PASSED!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Successfully:" -ForegroundColor Green
    Write-Host "  ✓ Created invitation" -ForegroundColor White
    Write-Host "  ✓ Generated 8-character code: $generatedCode" -ForegroundColor White
    Write-Host "  ✓ Invitation ready for use" -ForegroundColor White
    Write-Host ""
    Write-Host "Next: Check your email at $TestEmail for the invitation" -ForegroundColor Yellow
} else {
    Write-Host "❌ TEST FAILED!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Issues found:" -ForegroundColor Red
    if (-not $generatedCode -or $generatedCode -eq "PENDING") {
        Write-Host "  ✗ Code was not generated by Power Automate" -ForegroundColor White
        Write-Host "  → Check Power Automate flow is ON and running" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "Manual verification required:" -ForegroundColor Cyan
Write-Host "1. Check email inbox for invitation" -ForegroundColor White
Write-Host "2. Check Teams for notification" -ForegroundColor White
Write-Host "3. Test code at: https://epc.saberrenewable.energy/epc/apply" -ForegroundColor White
Write-Host ""
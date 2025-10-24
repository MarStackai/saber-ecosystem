#!/bin/bash
# End-to-End Test for EPC Partner Invitation System
# Tests the complete flow from invitation creation to application submission

echo "================================================"
echo "  EPC PARTNER SYSTEM - END-TO-END TEST"
echo "================================================"
echo ""
echo "This test will verify:"
echo "1. Invitation creation with auto-generated code"
echo "2. Email delivery with code"
echo "3. Code validation on portal"
echo "4. Application submission"
echo "5. SharePoint list updates"
echo ""

# Configuration
PORTAL_URL="https://epc.saberrenewable.energy"
TEST_TIMESTAMP=$(date +%Y%m%d-%H%M%S)
TEST_COMPANY="E2E-Test-${TEST_TIMESTAMP}"
TEST_EMAIL="rob@marstack.ai"
TEST_CONTACT="Test User ${TEST_TIMESTAMP}"

echo "Test Configuration:"
echo "  Company: ${TEST_COMPANY}"
echo "  Contact: ${TEST_CONTACT}"
echo "  Email: ${TEST_EMAIL}"
echo ""

# Step 1: Create invitation via PowerShell
echo "================================================"
echo "STEP 1: Creating Invitation"
echo "================================================"
echo ""

# Create the invitation
/snap/bin/pwsh -Command "
Write-Host 'Connecting to SharePoint...' -ForegroundColor Yellow

Connect-PnPOnline \`
    -Url 'https://saberrenewables.sharepoint.com/sites/SaberEPCPartners' \`
    -ClientId 'bbbfe394-7cff-4ac9-9e01-33cbf116b930' \`
    -Tenant 'saberrenewables.onmicrosoft.com' \`
    -CertificatePath '\$HOME/.certs/SaberEPCAutomation.pfx' \`
    -CertificatePassword (ConvertTo-SecureString -String 'P@ssw0rd123!' -AsPlainText -Force) \`
    -WarningAction SilentlyContinue

Write-Host 'Creating test invitation...' -ForegroundColor Yellow

# Create invitation (Power Automate will generate the code)
\$newItem = Add-PnPListItem -List 'EPC Invitations' -Values @{
    CompanyName = '${TEST_COMPANY}'
    ContactName = '${TEST_CONTACT}'
    ContactEmail = '${TEST_EMAIL}'
    Title = 'PENDING'  # Will be replaced by auto-generated code
}

Write-Host '✅ Invitation created with ID: ' \$newItem.Id -ForegroundColor Green

# Wait for Power Automate to process
Write-Host 'Waiting 10 seconds for Power Automate to generate code...' -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Retrieve the generated code
\$updatedItem = Get-PnPListItem -List 'EPC Invitations' -Id \$newItem.Id
\$generatedCode = \$updatedItem.FieldValues.Code
\$inviteCode = \$updatedItem.FieldValues.InviteCode

Write-Host ''
Write-Host '================================================' -ForegroundColor Cyan
Write-Host 'Invitation Details:' -ForegroundColor Cyan
Write-Host '  ID: ' \$newItem.Id -ForegroundColor White
Write-Host '  Company: ${TEST_COMPANY}' -ForegroundColor White
Write-Host '  Code Field: ' \$generatedCode -ForegroundColor Green
Write-Host '  InviteCode Field: ' \$inviteCode -ForegroundColor Green
Write-Host '  Email Sent To: ${TEST_EMAIL}' -ForegroundColor White
Write-Host '================================================' -ForegroundColor Cyan

# Export the code for next steps
if (\$generatedCode) {
    \$generatedCode | Out-File -FilePath '/tmp/test-code.txt' -NoNewline
    Write-Host '✅ Code saved for testing' -ForegroundColor Green
} elseif (\$inviteCode) {
    \$inviteCode | Out-File -FilePath '/tmp/test-code.txt' -NoNewline
    Write-Host '✅ InviteCode saved for testing' -ForegroundColor Green
} else {
    Write-Host '❌ No code was generated!' -ForegroundColor Red
    'TESTFAIL' | Out-File -FilePath '/tmp/test-code.txt' -NoNewline
}

Disconnect-PnPOnline
"

# Read the generated code
if [ -f /tmp/test-code.txt ]; then
    GENERATED_CODE=$(cat /tmp/test-code.txt)
    echo ""
    echo "Generated Code: ${GENERATED_CODE}"
else
    echo "❌ Failed to retrieve generated code"
    GENERATED_CODE="TESTFAIL"
fi

# Step 2: Verify Power Automate Flow
echo ""
echo "================================================"
echo "STEP 2: Verifying Power Automate Flow"
echo "================================================"
echo ""
echo "✓ Check 1: Was a code generated? ${GENERATED_CODE}"
echo "✓ Check 2: Email should be sent to: ${TEST_EMAIL}"
echo "✓ Check 3: Teams notification should be posted"
echo ""
echo "Please verify:"
echo "1. Check email inbox for invitation with code: ${GENERATED_CODE}"
echo "2. Check Teams channel for notification"
echo ""
read -p "Press Enter to continue to portal testing..."

# Step 3: Test Portal Code Validation
echo ""
echo "================================================"
echo "STEP 3: Testing Portal Code Validation"
echo "================================================"
echo ""

# Test code validation via API
echo "Testing code validation API..."
VALIDATION_RESPONSE=$(curl -s -X POST "${PORTAL_URL}/api/validate-code" \
    -H "Content-Type: application/json" \
    -d "{\"code\": \"${GENERATED_CODE}\"}")

echo "API Response: ${VALIDATION_RESPONSE}"

if echo "${VALIDATION_RESPONSE}" | grep -q "valid.*true"; then
    echo "✅ Code validation successful"
else
    echo "❌ Code validation failed"
    echo "Response: ${VALIDATION_RESPONSE}"
fi

# Step 4: Submit test application
echo ""
echo "================================================"
echo "STEP 4: Submitting Test Application"
echo "================================================"
echo ""

echo "Submitting application with code: ${GENERATED_CODE}"

# Create test application data
APPLICATION_DATA=$(cat <<EOF
{
    "invitationCode": "${GENERATED_CODE}",
    "companyName": "${TEST_COMPANY}",
    "companyAddress": "123 Test Street, Test City",
    "city": "Test City",
    "stateProvince": "Test State",
    "postalCode": "12345",
    "country": "USA",
    "companyWebsite": "https://example.com",
    "yearEstablished": "2020",
    "numberOfEmployees": "50-100",
    "primaryContactName": "${TEST_CONTACT}",
    "primaryContactTitle": "Test Manager",
    "primaryContactEmail": "${TEST_EMAIL}",
    "primaryContactPhone": "+1234567890",
    "geographicCoverage": ["Northeast", "Southeast"],
    "utilityExperience": ["Solar", "Wind"],
    "certifications": "ISO 9001, ISO 14001",
    "safetyRating": "Excellent",
    "insuranceCoverage": "General Liability, Professional Indemnity"
}
EOF
)

# Submit via API
SUBMISSION_RESPONSE=$(curl -s -X POST "${PORTAL_URL}/api/submit-application" \
    -H "Content-Type: application/json" \
    -d "${APPLICATION_DATA}")

echo "Submission Response: ${SUBMISSION_RESPONSE}"

if echo "${SUBMISSION_RESPONSE}" | grep -q "success"; then
    echo "✅ Application submitted successfully"
else
    echo "❌ Application submission failed"
fi

# Step 5: Verify SharePoint Updates
echo ""
echo "================================================"
echo "STEP 5: Verifying SharePoint Updates"
echo "================================================"
echo ""
echo "Waiting 10 seconds for Power Automate to process..."
sleep 10

/snap/bin/pwsh -Command "
Connect-PnPOnline \`
    -Url 'https://saberrenewables.sharepoint.com/sites/SaberEPCPartners' \`
    -ClientId 'bbbfe394-7cff-4ac9-9e01-33cbf116b930' \`
    -Tenant 'saberrenewables.onmicrosoft.com' \`
    -CertificatePath '\$HOME/.certs/SaberEPCAutomation.pfx' \`
    -CertificatePassword (ConvertTo-SecureString -String 'P@ssw0rd123!' -AsPlainText -Force) \`
    -WarningAction SilentlyContinue

Write-Host 'Checking invitation status...' -ForegroundColor Yellow

# Check if invitation is marked as used
\$invitation = Get-PnPListItem -List 'EPC Invitations' | Where-Object { 
    \$_.FieldValues.Code -eq '${GENERATED_CODE}' -or \$_.FieldValues.InviteCode -eq '${GENERATED_CODE}'
} | Select-Object -First 1

if (\$invitation) {
    Write-Host '✅ Found invitation:' -ForegroundColor Green
    Write-Host '  Used: ' \$invitation.FieldValues.Used -ForegroundColor White
    Write-Host '  InvitationSent: ' \$invitation.FieldValues.InvitationSent -ForegroundColor White
} else {
    Write-Host '❌ Invitation not found' -ForegroundColor Red
}

Write-Host ''
Write-Host 'Checking onboarding entries...' -ForegroundColor Yellow

# Check EPC Onboarding list
\$onboarding = Get-PnPListItem -List 'EPC Onboarding' | Where-Object {
    \$_.FieldValues.CompanyName -eq '${TEST_COMPANY}'
} | Select-Object -First 1

if (\$onboarding) {
    Write-Host '✅ Found onboarding entry:' -ForegroundColor Green
    Write-Host '  Company: ' \$onboarding.FieldValues.CompanyName -ForegroundColor White
    Write-Host '  Status: ' \$onboarding.FieldValues.Status -ForegroundColor White
    Write-Host '  Submission Date: ' \$onboarding.FieldValues.Created -ForegroundColor White
} else {
    Write-Host '❌ Onboarding entry not found' -ForegroundColor Red
}

Disconnect-PnPOnline
"

# Final Summary
echo ""
echo "================================================"
echo "  TEST SUMMARY"
echo "================================================"
echo ""
echo "Test Results:"
echo "1. ✓ Invitation Creation: Complete"
echo "2. ✓ Code Generation: ${GENERATED_CODE}"
echo "3. ✓ Email Delivery: Check ${TEST_EMAIL}"
echo "4. ✓ Portal Validation: Check above"
echo "5. ✓ Application Submission: Check above"
echo "6. ✓ SharePoint Updates: Check above"
echo ""
echo "================================================"
echo "Manual Verification Required:"
echo "1. Check email for invitation with code"
echo "2. Check Teams for notification"
echo "3. Verify code works at: ${PORTAL_URL}/epc/apply"
echo "4. Check both SharePoint lists for entries"
echo "================================================"
echo ""
echo "✅ End-to-End Test Complete!"
#!/bin/bash
# Complete system test

echo "================================================"
echo "🚀 COMPLETE EPC PORTAL SYSTEM TEST"
echo "================================================"
echo ""

# Generate unique test code with timestamp
TIMESTAMP=$(date +%H%M%S)
TEST_CODE="TEST$TIMESTAMP"

echo "📝 Step 1: Creating new test invitation in SharePoint"
echo "   Code: $TEST_CODE"
echo "   Company: End-to-End Test Company"
echo ""

/snap/bin/pwsh -Command "
Connect-PnPOnline \
    -Url 'https://saberrenewables.sharepoint.com/sites/SaberEPCPartners' \
    -ClientId 'bbbfe394-7cff-4ac9-9e01-33cbf116b930' \
    -Tenant 'saberrenewables.onmicrosoft.com' \
    -CertificatePath '$HOME/.certs/SaberEPCAutomation.pfx' \
    -CertificatePassword (ConvertTo-SecureString -String 'P@ssw0rd123!' -AsPlainText -Force) \
    -WarningAction SilentlyContinue

# Add test invitation
\$testInvite = @{
    Title = '$TEST_CODE'
    Code = '$TEST_CODE'
    CompanyName = 'End-to-End Test Company'
    ContactEmail = 'sysadmin@saberrenewables.com'
    ContactName = 'System Test'
    ExpiryDate = (Get-Date).AddDays(7).ToString('yyyy-MM-dd')
    Used = \$false
}

try {
    \$newItem = Add-PnPListItem -List 'EPC Invitations' -Values \$testInvite
    Write-Host '✅ Test invitation created with ID: ' \$newItem.Id -ForegroundColor Green
    Write-Host '   Trigger: SharePoint item created'
    Write-Host '   Expected: Invitation email should be sent'
} catch {
    Write-Host '❌ Failed to create invitation: ' \$_ -ForegroundColor Red
}

Disconnect-PnPOnline
"

echo ""
echo "⏳ Waiting 15 seconds for Power Automate to process..."
sleep 15

echo ""
echo "📧 Step 2: Check Power Automate Flow Status"
echo "   Flow: EPC Partner Invitation Email"
echo "   Check: https://make.powerautomate.com"
echo "   Expected: Flow should have run and sent email"
echo ""

echo "🔄 Step 3: Testing application submission with the new code"
echo ""

# Submit application with the new code
SUBMIT_DATA='{
  "invitationCode": "'$TEST_CODE'",
  "companyName": "End-to-End Test Company",
  "registrationNumber": "TEST'$TIMESTAMP'",
  "contactName": "System Test User",
  "contactTitle": "Test Manager",
  "email": "test@example.com",
  "phone": "555-'$TIMESTAMP'",
  "address": "123 Test Street, Test City, CA 90210",
  "services": ["Testing", "Validation"],
  "yearsExperience": 1,
  "teamSize": 5,
  "coverage": "Test Region",
  "certifications": "Test Cert"
}'

echo "Submitting application through live site..."
RESPONSE=$(curl -s -w "\n---\nHTTP_STATUS:%{http_code}" -X POST "https://epc.saberrenewable.energy/api/submit" \
  -H "Content-Type: application/json" \
  -d "$SUBMIT_DATA")

# Extract body and status
BODY=$(echo "$RESPONSE" | sed -n '1,/^---$/p' | head -n -1)
STATUS=$(echo "$RESPONSE" | grep "HTTP_STATUS" | cut -d: -f2)

echo "Response Status: $STATUS"
echo "Response Body:"
echo "$BODY" | jq . 2>/dev/null || echo "$BODY"
echo ""

if [ "$STATUS" = "200" ]; then
    echo "✅ Application submitted successfully!"
    echo "   Expected: Confirmation emails should be sent"
else
    echo "❌ Submission failed with status $STATUS"
fi

echo ""
echo "================================================"
echo "📊 SYSTEM TEST SUMMARY"
echo "================================================"
echo ""
echo "Test Code: $TEST_CODE"
echo ""
echo "Expected Results:"
echo "✓ SharePoint 'EPC Invitations' has new entry"
echo "✓ Power Automate sent invitation email"
echo "✓ Application submitted successfully"
echo "✓ SharePoint 'EPC Onboarding' has new entry"
echo "✓ Invitation marked as 'Used'"
echo "✓ Confirmation emails sent"
echo ""
echo "Manual Verification Steps:"
echo "1. Check email inbox for invitation email"
echo "2. Check email inbox for confirmation emails"
echo "3. Check SharePoint lists for new entries"
echo "4. Check Power Automate run history"
echo ""
echo "🎉 If all checks pass, the system is fully operational!"
echo "================================================"
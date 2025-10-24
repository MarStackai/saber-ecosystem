#!/bin/bash
# Test the complete EPC portal flow

echo "================================================"
echo "Testing Complete EPC Portal Flow"
echo "================================================"
echo ""

# Test with DEMO2024 code since TEST2024 was already used
CODE="DEMO2024"
EMAIL="test@example.com"

echo "1. Testing invitation code validation..."
echo "   Code: $CODE"
echo ""

# First, validate the code
VALIDATE_RESPONSE=$(curl -s -X POST "https://epc.saberrenewable.energy/api/validate-code" \
  -H "Content-Type: application/json" \
  -d "{\"code\": \"$CODE\"}")

echo "Validation response: $VALIDATE_RESPONSE"

if [[ "$VALIDATE_RESPONSE" == *"valid"* ]] || [[ "$VALIDATE_RESPONSE" == *"true"* ]]; then
    echo "✅ Code validated successfully"
else
    echo "⚠️  Validation endpoint might not exist, continuing with submission test..."
fi

echo ""
echo "2. Testing form submission..."
echo ""

# Submit application with the code
SUBMIT_DATA='{
  "invitationCode": "'$CODE'",
  "companyName": "Demo Test Company",
  "registrationNumber": "DEMO456789",
  "contactName": "Demo Tester",
  "contactTitle": "Manager",
  "email": "'$EMAIL'",
  "phone": "555-9999",
  "address": "456 Demo Ave, Test City, CA 90210",
  "services": ["Installation", "Maintenance", "Consulting"],
  "yearsExperience": 8,
  "teamSize": 35,
  "coverage": "Western United States",
  "certifications": "ISO 9001, NABCEP"
}'

SUBMIT_RESPONSE=$(curl -s -w "\n---\nHTTP_STATUS:%{http_code}" -X POST "https://epc.saberrenewable.energy/api/submit" \
  -H "Content-Type: application/json" \
  -d "$SUBMIT_DATA")

# Extract body and status
BODY=$(echo "$SUBMIT_RESPONSE" | sed -n '1,/^---$/p' | head -n -1)
STATUS=$(echo "$SUBMIT_RESPONSE" | grep "HTTP_STATUS" | cut -d: -f2)

echo "Response Status: $STATUS"
echo "Response Body:"
echo "$BODY" | jq . 2>/dev/null || echo "$BODY"
echo ""

if [ "$STATUS" = "200" ]; then
    echo "✅ Application submitted successfully!"
    echo ""
    echo "Results:"
    echo "--------"
    REF_NUM=$(echo "$BODY" | jq -r '.referenceNumber' 2>/dev/null)
    if [ "$REF_NUM" != "null" ] && [ ! -z "$REF_NUM" ]; then
        echo "• SharePoint Item ID: $REF_NUM"
    fi
    echo "• Invitation Code: $CODE (should now be marked as 'Used')"
    echo "• Company: Demo Test Company"
    echo ""
    echo "Next steps to verify:"
    echo "1. Check SharePoint 'EPC Onboarding' list for new entry"
    echo "2. Check SharePoint 'EPC Invitations' to see if $CODE is marked as Used"
    echo "3. Check Power Automate run history for successful execution"
else
    echo "❌ Submission failed with status $STATUS"
    echo ""
    echo "Troubleshooting:"
    echo "• Check if code $CODE exists in SharePoint"
    echo "• Check Power Automate flow is ON"
    echo "• Check Cloudflare Worker logs"
fi

echo ""
echo "================================================"
echo "Test Complete"
echo "================================================"
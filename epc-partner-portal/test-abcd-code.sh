#!/bin/bash
# Test with ABCD1234 code

echo "================================================"
echo "Testing with ABCD1234 Code"
echo "================================================"
echo ""

CODE="ABCD1234"

echo "Testing form submission with code: $CODE"
echo ""

# Submit application
SUBMIT_DATA='{
  "invitationCode": "'$CODE'",
  "companyName": "ABC Solar Corporation",
  "registrationNumber": "ABC789012",
  "contactName": "Alice Brown",
  "contactTitle": "Operations Director",
  "email": "alice@abcsolar.com",
  "phone": "555-1234",
  "address": "789 ABC Boulevard, Solar City, CA 94000",
  "services": ["Design", "Installation", "Monitoring"],
  "yearsExperience": 12,
  "teamSize": 75,
  "coverage": "California, Nevada, Arizona",
  "certifications": "NABCEP, ISO 9001, ISO 14001"
}'

# Call the API directly
echo "Calling Power Automate directly..."
PA_URL="https://defaultdd0eeaf22c36470995546e2b2639c3.d1.environment.api.powerplatform.com:443/powerautomate/automations/direct/workflows/25bb3274380b4684a5cd06911e03048d/triggers/manual/paths/invoke?api-version=1&sp=%2Ftriggers%2Fmanual%2Frun&sv=1.0&sig=l9vFANVy7qrJ3lBl7rok4agZw9cWoolCw2tg_Y46kjY"

RESPONSE=$(curl -s -w "\n---\nHTTP_STATUS:%{http_code}" -X POST "$PA_URL" \
  -H "Content-Type: application/json" \
  -d "$SUBMIT_DATA")

# Extract body and status
BODY=$(echo "$RESPONSE" | sed -n '1,/^---$/p' | head -n -1)
STATUS=$(echo "$RESPONSE" | grep "HTTP_STATUS" | cut -d: -f2)

echo "Power Automate Response:"
echo "Status: $STATUS"
echo "Body: $BODY"
echo ""

if [ "$STATUS" = "200" ]; then
    echo "✅ Power Automate processed successfully!"
    REF=$(echo "$BODY" | jq -r '.referenceNumber' 2>/dev/null)
    echo "SharePoint Item ID: $REF"
else
    echo "❌ Power Automate returned status $STATUS"
fi

echo ""
echo "Now testing through Cloudflare Worker..."
WORKER_RESPONSE=$(curl -s -w "\n---\nHTTP_STATUS:%{http_code}" -X POST "https://epc.saberrenewable.energy/api/submit" \
  -H "Content-Type: application/json" \
  -d "$SUBMIT_DATA")

# Extract body and status
WORKER_BODY=$(echo "$WORKER_RESPONSE" | sed -n '1,/^---$/p' | head -n -1)
WORKER_STATUS=$(echo "$WORKER_RESPONSE" | grep "HTTP_STATUS" | cut -d: -f2)

echo ""
echo "Cloudflare Worker Response:"
echo "Status: $WORKER_STATUS"
echo "Body:"
echo "$WORKER_BODY" | jq . 2>/dev/null || echo "$WORKER_BODY"

echo ""
echo "================================================"
echo "Summary:"
echo "- Code tested: $CODE"
echo "- Power Automate: $STATUS"
echo "- Cloudflare Worker: $WORKER_STATUS"
echo "================================================"
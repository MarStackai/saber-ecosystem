#!/bin/bash

echo "================================================"
echo "Testing Power Automate Flow (After Enabling)"
echo "================================================"
echo ""

# Test with the authenticated URL
curl -X POST "https://defaultdd0eeaf22c36470995546e2b2639c3.d1.environment.api.powerplatform.com:443/powerautomate/automations/direct/workflows/2c9c7efdebfc4665b6c11b3f1b628ab2/triggers/manual/paths/invoke?api-version=1&sp=%2Ftriggers%2Fmanual%2Frun&sv=1.0&sig=gxDjRFHbP6ExBdUyQCCsCsA1D2ykjv4387MtS2oDcLA" \
  -H "Content-Type: application/json" \
  -d '{
    "invitationCode": "TEST2024",
    "companyName": "Flow Test Company",
    "registrationNumber": "FLOW-TEST-123",
    "contactName": "Flow Tester",
    "contactTitle": "Test Manager",
    "email": "flowtest@example.com",
    "phone": "555-0199",
    "address": "123 Flow Street",
    "services": ["Solar Installation"],
    "yearsExperience": 5,
    "teamSize": 10,
    "coverage": "Test Region",
    "certifications": "ISO 9001",
    "timestamp": "'$(date -Iseconds)'",
    "source": "epc.saberrenewable.energy"
  }' \
  -w "\n\nHTTP Status: %{http_code}\nResponse Time: %{time_total}s\n"

echo ""
echo "================================================"
echo "If you see HTTP Status 202, the flow is working!"
echo "Check your SharePoint lists and email for results."
echo "================================================"
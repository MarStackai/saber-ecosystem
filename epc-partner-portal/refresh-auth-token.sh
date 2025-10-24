#!/bin/bash
# Refresh authentication token (run monthly or when needed)

echo "Refreshing SharePoint authentication token..."

/snap/bin/pwsh -Command "
Write-Host 'Connecting to SharePoint to refresh token...' -ForegroundColor Yellow
Connect-PnPOnline \
    -Url 'https://saberrenewables.sharepoint.com/sites/SaberEPCPartners' \
    -ClientId 'bbbfe394-7cff-4ac9-9e01-33cbf116b930' \
    -Tenant 'saberrenewables.onmicrosoft.com' \
    -DeviceLogin

Write-Host '✓ Token refreshed successfully!' -ForegroundColor Green
\$web = Get-PnPWeb
Write-Host \"Connected to: \$(\$web.Title)\" -ForegroundColor Green
Disconnect-PnPOnline
"

echo "Token refreshed and cached for another 90 days!"

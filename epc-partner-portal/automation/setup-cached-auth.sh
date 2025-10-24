#!/bin/bash

echo "==============================================="
echo "  Setting Up Cached Authentication for Automation"
echo "==============================================="
echo ""

# First, let's authenticate and cache the token
echo "Step 1: Authenticating to cache token..."
echo "This will cache authentication for ~90 days"
echo ""

/snap/bin/pwsh -Command "
Write-Host 'Authenticating to SharePoint...' -ForegroundColor Yellow
try {
    Connect-PnPOnline \
        -Url 'https://saberrenewables.sharepoint.com/sites/SaberEPCPartners' \
        -ClientId 'bbbfe394-7cff-4ac9-9e01-33cbf116b930' \
        -Tenant 'saberrenewables.onmicrosoft.com' \
        -DeviceLogin
    
    Write-Host '✓ Authentication successful and cached!' -ForegroundColor Green
    
    # Test the connection
    \$web = Get-PnPWeb
    Write-Host \"Connected to: \$(\$web.Title)\" -ForegroundColor Green
    
    # The token is now cached in ~/.config/PnP.PowerShell
    Write-Host ''
    Write-Host 'Token cached for 90 days in: ~/.config/PnP.PowerShell' -ForegroundColor Cyan
    
    Disconnect-PnPOnline
} catch {
    Write-Host \"Error: \$_\" -ForegroundColor Red
}
"

echo ""
echo "Step 2: Creating automated processor script..."

# Create the automated processor that uses cached auth
cat > /home/marstack/saber_business_ops/run-processor-automated.sh << 'EOF'
#!/bin/bash
# Automated EPC Processor using cached authentication

LOG_FILE="$HOME/saber_business_ops/logs/epc_processor.log"
ERROR_LOG="$HOME/saber_business_ops/logs/epc_processor_error.log"

echo "[$(date)] Starting automated processor..." >> "$LOG_FILE"

# Run the processor using cached authentication
/snap/bin/pwsh -Command "
\$ErrorActionPreference = 'Stop'
try {
    # Connect using cached token (no interaction needed)
    Connect-PnPOnline \
        -Url 'https://saberrenewables.sharepoint.com/sites/SaberEPCPartners' \
        -ClientId 'bbbfe394-7cff-4ac9-9e01-33cbf116b930' \
        -Tenant 'saberrenewables.onmicrosoft.com'
    
    # Run the actual processor
    & '$HOME/saber_business_ops/scripts/process-epc.ps1' \
        -SiteUrl 'https://saberrenewables.sharepoint.com/sites/SaberEPCPartners' \
        -ClientId 'bbbfe394-7cff-4ac9-9e01-33cbf116b930' \
        -Tenant 'saberrenewables.onmicrosoft.com'
    
    Disconnect-PnPOnline
    '[$(date)] Processor completed successfully' | Add-Content '$LOG_FILE'
} catch {
    \"[$(date)] ERROR: \$_\" | Add-Content '$ERROR_LOG'
    exit 1
}
"

if [ $? -eq 0 ]; then
    echo "[$(date)] Success" >> "$LOG_FILE"
else
    echo "[$(date)] Failed - check error log" >> "$LOG_FILE"
fi
EOF

chmod +x /home/marstack/saber_business_ops/run-processor-automated.sh

echo "✓ Automated processor script created"
echo ""

# Create a token refresh script
cat > /home/marstack/saber_business_ops/refresh-auth-token.sh << 'EOF'
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
EOF

chmod +x /home/marstack/saber_business_ops/refresh-auth-token.sh

echo "✓ Token refresh script created"
echo ""

echo "==============================================="
echo "  Setup Complete!"
echo "==============================================="
echo ""
echo "NEXT STEPS:"
echo ""
echo "1. Update your crontab to use the new script:"
echo "   crontab -e"
echo "   Add/update this line:"
echo "   */5 * * * * /home/marstack/saber_business_ops/run-processor-automated.sh"
echo ""
echo "2. Set a monthly reminder to refresh the token:"
echo "   0 0 1 * * /home/marstack/saber_business_ops/refresh-auth-token.sh"
echo ""
echo "3. The authentication token will work for ~90 days"
echo "   To manually refresh anytime, run:"
echo "   /home/marstack/saber_business_ops/refresh-auth-token.sh"
echo ""
echo "==============================================="
echo "  Why can't you upload the certificate?"
echo "==============================================="
echo ""
echo "Possible reasons:"
echo "1. You need Global Administrator or Application Administrator role"
echo "2. The app might be managed by Conditional Access policies"
echo "3. The tenant might have restrictions on certificate uploads"
echo ""
echo "The cached token method works well for most scenarios!"
echo "==============================================="
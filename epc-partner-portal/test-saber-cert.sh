#!/bin/bash
# Test Saber-PnP-Cli Certificate Authentication

echo "========================================="
echo "  Testing Saber-PnP-Cli Certificate Auth"
echo "========================================="
echo ""

# You need to provide the App ID
read -p "Enter your Saber-PnP-Cli Application ID: " APP_ID

if [ -z "$APP_ID" ]; then
    echo "Error: App ID is required!"
    exit 1
fi

echo ""
echo "Testing with App ID: $APP_ID"
echo "Certificate: ~/.certs/SaberEPCAutomation.pfx"
echo ""

# Test the certificate authentication
/snap/bin/pwsh -Command "
\$ErrorActionPreference = 'Stop'

Write-Host 'Testing certificate authentication...' -ForegroundColor Yellow

try {
    # Try connecting with certificate
    Connect-PnPOnline \
        -Url 'https://saberrenewables.sharepoint.com/sites/SaberEPCPartners' \
        -ClientId '$APP_ID' \
        -Tenant 'saberrenewables.onmicrosoft.com' \
        -CertificatePath '$HOME/.certs/SaberEPCAutomation.pfx' \
        -CertificatePassword (ConvertTo-SecureString -String 'P@ssw0rd123!' -AsPlainText -Force)
    
    Write-Host ''
    Write-Host '✅ SUCCESS! Certificate authentication worked!' -ForegroundColor Green
    Write-Host ''
    
    # Test we can access SharePoint
    Write-Host 'Testing SharePoint access...' -ForegroundColor Yellow
    \$lists = Get-PnPList | Select-Object -First 5
    
    Write-Host \"✅ Can access SharePoint! Found \$(\$lists.Count) lists:\" -ForegroundColor Green
    \$lists | ForEach-Object { Write-Host \"   - \$(\$_.Title)\" -ForegroundColor Gray }
    
    Write-Host ''
    Write-Host 'Testing EPC lists specifically...' -ForegroundColor Yellow
    \$epcLists = Get-PnPList | Where-Object { \$_.Title -like '*EPC*' }
    if (\$epcLists) {
        Write-Host '✅ Found EPC lists:' -ForegroundColor Green
        \$epcLists | ForEach-Object { Write-Host \"   - \$(\$_.Title)\" -ForegroundColor Gray }
    } else {
        Write-Host '⚠️  No EPC lists found (might need to create them)' -ForegroundColor Yellow
    }
    
    Disconnect-PnPOnline
    
    Write-Host ''
    Write-Host '=========================================' -ForegroundColor Cyan
    Write-Host '  CERTIFICATE AUTH SUCCESSFUL!' -ForegroundColor Green
    Write-Host '=========================================' -ForegroundColor Cyan
    Write-Host ''
    Write-Host 'Next steps:' -ForegroundColor Yellow
    Write-Host \"1. Update run-processor-saber.sh with App ID: $APP_ID\" -ForegroundColor White
    Write-Host '2. Set USE_CERTIFICATE=true in the script' -ForegroundColor White
    Write-Host '3. Test: ./run-processor-saber.sh' -ForegroundColor White
    Write-Host '4. Update cron job when ready' -ForegroundColor White
    
    exit 0
    
} catch {
    Write-Host ''
    Write-Host '❌ CERTIFICATE AUTH FAILED!' -ForegroundColor Red
    Write-Host ''
    Write-Host \"Error: \$_\" -ForegroundColor Red
    Write-Host ''
    Write-Host 'Troubleshooting:' -ForegroundColor Yellow
    Write-Host '1. Check the certificate was uploaded correctly in Azure' -ForegroundColor White
    Write-Host '2. Verify the thumbprint matches: 8A20540CDD30290406D52688D22C0F1B5B4973B3' -ForegroundColor White
    Write-Host '3. Ensure API permissions are granted (Sites.FullControl.All)' -ForegroundColor White
    Write-Host '4. Make sure admin consent was granted' -ForegroundColor White
    Write-Host ''
    Write-Host 'Certificate details:' -ForegroundColor Yellow
    
    # Show certificate info
    \$certInfo = Get-Content '$HOME/.certs/SaberEPCAutomation-info.json' | ConvertFrom-Json
    Write-Host \"  Thumbprint: \$(\$certInfo.Thumbprint)\" -ForegroundColor Gray
    Write-Host \"  Cert Path: \$(\$certInfo.CertPath)\" -ForegroundColor Gray
    Write-Host \"  PFX Path: \$(\$certInfo.PfxPath)\" -ForegroundColor Gray
    
    exit 1
}
"

if [ $? -eq 0 ]; then
    echo ""
    echo "Would you like to update the automation script now? (y/n)"
    read -p "> " UPDATE_SCRIPT
    
    if [ "$UPDATE_SCRIPT" == "y" ] || [ "$UPDATE_SCRIPT" == "Y" ]; then
        # Update the run-processor-saber.sh script
        sed -i "s/SABER_APP_ID=\"YOUR_SABER_PNP_CLI_APP_ID\"/SABER_APP_ID=\"$APP_ID\"/" run-processor-saber.sh
        sed -i "s/USE_CERTIFICATE=false/USE_CERTIFICATE=true/" run-processor-saber.sh
        echo "✅ Updated run-processor-saber.sh with App ID: $APP_ID"
        echo ""
        echo "Test it with: ./run-processor-saber.sh"
    fi
fi
#!/bin/bash
# EPC Processor using Saber-PnP-Cli App
# Update the APP_ID and authentication method after configuring in Azure

# IMPORTANT: Update these values from Azure Portal
SABER_APP_ID="bbbfe394-7cff-4ac9-9e01-33cbf116b930"  # <-- UPDATE THIS!
SABER_CLIENT_SECRET=""  # <-- UPDATE THIS if using secret!
USE_CERTIFICATE=true  # Set to true if using certificate instead of secret

LOG_FILE="$HOME/saber_business_ops/logs/epc_processor.log"
ERROR_LOG="$HOME/saber_business_ops/logs/epc_processor_error.log"
TENANT_ID="dd0eeaf2-2c36-4709-9554-6e2b2639c3d1"

if [ "$SABER_APP_ID" == "YOUR_SABER_PNP_CLI_APP_ID" ]; then
    echo "========================================" 
    echo "  SETUP REQUIRED"
    echo "========================================"
    echo ""
    echo "1. Go to Azure Portal > App registrations"
    echo "2. Find 'Saber-PnP-Cli' app"
    echo "3. Copy the Application (client) ID"
    echo "4. Add a client secret or upload certificate"
    echo "5. Update this script with the values"
    echo ""
    echo "See: setup-saber-pnp-cli.md for detailed instructions"
    exit 1
fi

echo "[$(date)] Starting Saber-PnP-Cli authenticated processor..."

if [ "$USE_CERTIFICATE" == "true" ]; then
    echo "Using certificate authentication..."
    
    /snap/bin/pwsh -Command "
    \$ErrorActionPreference = 'Stop'
    try {
        Write-Host 'Connecting with Saber-PnP-Cli app (certificate)...'
        
        Connect-PnPOnline \
            -Url 'https://saberrenewables.sharepoint.com/sites/SaberEPCPartners' \
            -ClientId '$SABER_APP_ID' \
            -Tenant 'saberrenewables.onmicrosoft.com' \
            -CertificatePath '$HOME/.certs/SaberEPCAutomation.pfx' \
            -CertificatePassword (ConvertTo-SecureString -String 'P@ssw0rd123!' -AsPlainText -Force)
        
        Write-Host 'Successfully connected with Saber-PnP-Cli!'
        
        # Test the connection
        \$lists = Get-PnPList
        Write-Host \"Found \$(\$lists.Count) SharePoint lists\"
        
        # Run the processor
        & '$HOME/saber_business_ops/scripts/process-epc.ps1' \
            -SiteUrl 'https://saberrenewables.sharepoint.com/sites/SaberEPCPartners' \
            -ClientId '$SABER_APP_ID' \
            -Tenant '$TENANT_ID'
        
        Disconnect-PnPOnline
        Write-Host 'Processor completed successfully'
        exit 0
    } catch {
        Write-Error \"Saber-PnP-Cli auth failed: \$_\"
        \"[$(date)] ERROR: \$_\" | Add-Content '$ERROR_LOG'
        exit 1
    }
    " 2>&1 | tee -a "$LOG_FILE"
else
    echo "Using client secret authentication..."
    
    if [ -z "$SABER_CLIENT_SECRET" ]; then
        echo "ERROR: SABER_CLIENT_SECRET is empty!"
        echo "Please add a client secret in Azure Portal and update this script"
        exit 1
    fi
    
    /snap/bin/pwsh -Command "
    \$ErrorActionPreference = 'Stop'
    try {
        Write-Host 'Connecting with Saber-PnP-Cli app (secret)...'
        
        Connect-PnPOnline \
            -Url 'https://saberrenewables.sharepoint.com/sites/SaberEPCPartners' \
            -ClientId '$SABER_APP_ID' \
            -ClientSecret '$SABER_CLIENT_SECRET' \
            -WarningAction Ignore
        
        Write-Host 'Successfully connected with Saber-PnP-Cli!'
        
        # Test the connection
        \$lists = Get-PnPList
        Write-Host \"Found \$(\$lists.Count) SharePoint lists\"
        
        # Run the processor
        & '$HOME/saber_business_ops/scripts/process-epc.ps1' \
            -SiteUrl 'https://saberrenewables.sharepoint.com/sites/SaberEPCPartners' \
            -ClientId '$SABER_APP_ID' \
            -Tenant '$TENANT_ID'
        
        Disconnect-PnPOnline
        Write-Host 'Processor completed successfully'
        exit 0
    } catch {
        Write-Error \"Saber-PnP-Cli auth failed: \$_\"
        \"[$(date)] ERROR: \$_\" | Add-Content '$ERROR_LOG'
        exit 1
    }
    " 2>&1 | tee -a "$LOG_FILE"
fi

if [ $? -eq 0 ]; then
    echo "[$(date)] Success - Saber-PnP-Cli authentication worked!" | tee -a "$LOG_FILE"
    echo ""
    echo "Next step: Update cron job to use this script"
    echo "crontab -e"
    echo "*/5 * * * * $PWD/run-processor-saber.sh >> $LOG_FILE 2>&1"
else
    echo "[$(date)] Failed - Check Azure AD configuration for Saber-PnP-Cli" | tee -a "$LOG_FILE"
fi
#!/bin/bash
# EPC Processor using Client Secret Authentication
# After you create the secret in Azure AD, update the CLIENT_SECRET below

# IMPORTANT: Update these after creating in Azure Portal
CLIENT_ID="bbbfe394-7cff-4ac9-9e01-33cbf116b930"  # Or your new app ID
CLIENT_SECRET="YOUR_SECRET_HERE"  # <-- UPDATE THIS!
TENANT_ID="dd0eeaf2-2c36-4709-9554-6e2b2639c3d1"

LOG_FILE="$HOME/saber_business_ops/logs/epc_processor.log"
ERROR_LOG="$HOME/saber_business_ops/logs/epc_processor_error.log"

if [ "$CLIENT_SECRET" == "YOUR_SECRET_HERE" ]; then
    echo "ERROR: Please update CLIENT_SECRET in this script first!"
    echo "Follow instructions in create-new-app.md"
    exit 1
fi

echo "[$(date)] Starting client secret authenticated processor..." | tee -a "$LOG_FILE"

# Run PowerShell with client secret authentication
/snap/bin/pwsh -Command "
\$ErrorActionPreference = 'Stop'
try {
    Write-Host 'Connecting with client secret authentication...'
    
    # Client Secret authentication - no browser, no certificate needed!
    Connect-PnPOnline \
        -Url 'https://saberrenewables.sharepoint.com/sites/SaberEPCPartners' \
        -ClientId '$CLIENT_ID' \
        -ClientSecret '$CLIENT_SECRET' \
        -WarningAction Ignore
    
    Write-Host 'Successfully connected!'
    
    # Get the lists to verify connection
    \$lists = Get-PnPList
    Write-Host \"Found \$(\$lists.Count) SharePoint lists\"
    
    # Run the processor
    & '$HOME/saber_business_ops/scripts/process-epc.ps1' \
        -SiteUrl 'https://saberrenewables.sharepoint.com/sites/SaberEPCPartners' \
        -ClientId '$CLIENT_ID' \
        -Tenant '$TENANT_ID'
    
    Disconnect-PnPOnline
    Write-Host 'Processor completed successfully'
    exit 0
} catch {
    Write-Error \"Client secret auth failed: \$_\"
    \"[$(date)] ERROR: \$_\" | Add-Content '$ERROR_LOG'
    exit 1
}
" 2>&1 | tee -a "$LOG_FILE"

if [ $? -eq 0 ]; then
    echo "[$(date)] Success - Client secret authentication worked!" | tee -a "$LOG_FILE"
else
    echo "[$(date)] Failed - Check Azure AD setup" | tee -a "$LOG_FILE"
fi
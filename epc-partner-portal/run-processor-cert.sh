#!/bin/bash
# EPC Processor using Certificate Authentication (after Azure AD setup)

LOG_FILE="$HOME/saber_business_ops/logs/epc_processor.log"
ERROR_LOG="$HOME/saber_business_ops/logs/epc_processor_error.log"

echo "[$(date)] Starting certificate-authenticated processor..." | tee -a "$LOG_FILE"

# Run PowerShell with certificate authentication
/snap/bin/pwsh -Command "
\$ErrorActionPreference = 'Stop'
try {
    Write-Host 'Connecting with certificate authentication...'
    
    # Certificate authentication - no browser needed!
    Connect-PnPOnline \
        -Url 'https://saberrenewables.sharepoint.com/sites/SaberEPCPartners' \
        -ClientId 'bbbfe394-7cff-4ac9-9e01-33cbf116b930' \
        -Tenant 'saberrenewables.onmicrosoft.com' \
        -CertificatePath '$HOME/.certs/SaberEPCAutomation.pfx' \
        -CertificatePassword (ConvertTo-SecureString -String 'P@ssw0rd123!' -AsPlainText -Force)
    
    Write-Host 'Successfully connected!'
    
    # Get the lists to verify connection
    \$lists = Get-PnPList
    Write-Host \"Found \$(\$lists.Count) SharePoint lists\"
    
    # Run the processor
    & '$HOME/saber_business_ops/scripts/process-epc.ps1' \
        -SiteUrl 'https://saberrenewables.sharepoint.com/sites/SaberEPCPartners' \
        -ClientId 'bbbfe394-7cff-4ac9-9e01-33cbf116b930' \
        -Tenant 'saberrenewables.onmicrosoft.com'
    
    Disconnect-PnPOnline
    Write-Host 'Processor completed successfully'
    exit 0
} catch {
    Write-Error \"Certificate auth failed: \$_\"
    \"[$(date)] ERROR: \$_\" | Add-Content '$ERROR_LOG'
    exit 1
}
" 2>&1 | tee -a "$LOG_FILE"

if [ $? -eq 0 ]; then
    echo "[$(date)] Success - Certificate authentication worked!" | tee -a "$LOG_FILE"
else
    echo "[$(date)] Failed - Check Azure AD certificate setup" | tee -a "$LOG_FILE"
    echo "" | tee -a "$LOG_FILE"
    echo "To fix: Run './setup-azure-app.ps1 -UseExistingApp' for instructions" | tee -a "$LOG_FILE"
fi
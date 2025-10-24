#!/bin/bash
# Interactive processor script (requires manual auth every 90 days)

LOG_FILE="$HOME/saber_business_ops/logs/epc_processor.log"

echo "Starting EPC processor..." | tee -a "$LOG_FILE"

# Run the PowerShell processor with device login
/snap/bin/pwsh -File "$HOME/saber_business_ops/scripts/process-epc.ps1" \
    -SiteUrl "https://saberrenewables.sharepoint.com/sites/SaberEPCPartners" \
    -ClientId "bbbfe394-7cff-4ac9-9e01-33cbf116b930" \
    -Tenant "dd0eeaf2-2c36-4709-9554-6e2b2639c3d1" \
    >> "$LOG_FILE" 2>&1

echo "Processor completed at $(date)" | tee -a "$LOG_FILE"

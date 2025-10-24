#!/bin/bash
# Automated EPC Processor using device code authentication

LOG_FILE="$HOME/saber_business_ops/logs/epc_processor.log"
ERROR_LOG="$HOME/saber_business_ops/logs/epc_processor_error.log"

echo "[$(date)] Starting automated processor..."

# Simply run the processor script directly - it handles authentication internally
/snap/bin/pwsh -File "$HOME/saber_business_ops/scripts/process-epc.ps1" \
    -SiteUrl "https://saberrenewables.sharepoint.com/sites/SaberEPCPartners" \
    -ClientId "bbbfe394-7cff-4ac9-9e01-33cbf116b930" \
    -Tenant "saberrenewables.onmicrosoft.com" \
    >> "$LOG_FILE" 2>&1

if [ $? -eq 0 ]; then
    echo "[$(date)] Success" >> "$LOG_FILE"
else
    echo "[$(date)] Failed - check error log" >> "$LOG_FILE"
fi

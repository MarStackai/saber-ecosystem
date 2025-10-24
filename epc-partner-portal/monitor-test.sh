#!/bin/bash
# Monitor EPC Portal test submission

echo "========================================="
echo "  EPC PORTAL TEST MONITOR"
echo "========================================="
echo ""
echo "Test Details:"
echo "  Portal URL: https://epc.saberrenewable.energy"
echo "  Test Code: TEST2024 (or any code you have)"
echo "  Test Email: rob@marstack.ai"
echo ""
echo "Monitoring logs in real-time..."
echo "Press Ctrl+C to stop"
echo ""
echo "========================================="
echo ""

# Start monitoring in background
tail -f /home/marstack/saber_business_ops/logs/epc_processor.log &
TAIL_PID=$!

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "Stopping monitor..."
    kill $TAIL_PID 2>/dev/null
    exit 0
}

trap cleanup INT TERM

# Check processor every 30 seconds
while true; do
    sleep 30
    echo ""
    echo "[$(date)] Checking for new submissions..."
    
    # Run a quick check
    /snap/bin/pwsh -Command "
    try {
        Connect-PnPOnline \
            -Url 'https://saberrenewables.sharepoint.com/sites/SaberEPCPartners' \
            -ClientId 'bbbfe394-7cff-4ac9-9e01-33cbf116b930' \
            -Tenant 'saberrenewables.onmicrosoft.com' \
            -CertificatePath '$HOME/.certs/SaberEPCAutomation.pfx' \
            -CertificatePassword (ConvertTo-SecureString -String 'P@ssw0rd123!' -AsPlainText -Force) \
            -WarningAction SilentlyContinue
        
        \$items = Get-PnPListItem -List 'EPC Onboarding' | Where-Object { 
            \$_.FieldValues.Status -eq 'Submitted' -and 
            \$_.FieldValues.SubmissionHandled -ne \$true 
        }
        
        if (\$items) {
            Write-Host \"✅ Found \$(\$items.Count) new submission(s)!\" -ForegroundColor Green
            \$items | ForEach-Object {
                Write-Host \"  - Company: \$(\$_.FieldValues.CompanyName)\"
                Write-Host \"    Email: \$(\$_.FieldValues.ContactEmail)\"
            }
        } else {
            Write-Host 'No new submissions yet...'
        }
        
        Disconnect-PnPOnline -WarningAction SilentlyContinue
    } catch {
        # Silent fail - processor will handle it
    }
    " 2>/dev/null
    
    echo ""
done
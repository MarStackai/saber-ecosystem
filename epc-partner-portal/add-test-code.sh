#!/bin/bash
# Add test invitation code for human testing

echo "Adding test invitation code for rob@marstack.ai..."

/snap/bin/pwsh -Command "
# Using the working connection from run-processor-saber.sh
\$ErrorActionPreference = 'Continue'

try {
    Write-Host 'Connecting to SharePoint...' -ForegroundColor Yellow
    
    Connect-PnPOnline \
        -Url 'https://saberrenewables.sharepoint.com/sites/SaberEPCPartners' \
        -ClientId 'bbbfe394-7cff-4ac9-9e01-33cbf116b930' \
        -Tenant 'saberrenewables.onmicrosoft.com' \
        -CertificatePath '$HOME/.certs/SaberEPCAutomation.pfx' \
        -CertificatePassword (ConvertTo-SecureString -String 'P@ssw0rd123!' -AsPlainText -Force)
    
    Write-Host 'Connected! Adding test code...' -ForegroundColor Green
    
    # Add test invitation code
    \$testCode = @{
        'Title' = 'TEST2024'
        'Code' = 'TEST2024'
        'Status' = 'Active'
        'CompanyName' = 'MarStack Test'
        'ContactEmail' = 'rob@marstack.ai'
        'ExpiryDate' = (Get-Date).AddDays(30)
        'Used' = \$false
    }
    
    Add-PnPListItem -List 'EPC Invitations' -Values \$testCode
    Write-Host '✅ Added test code: TEST2024 for rob@marstack.ai' -ForegroundColor Green
    
    # List all codes
    Write-Host ''
    Write-Host 'Current invitation codes:' -ForegroundColor Cyan
    Get-PnPListItem -List 'EPC Invitations' | ForEach-Object {
        \$item = \$_.FieldValues
        Write-Host \"  Code: \$(\$item.Code) | Status: \$(\$item.Status) | Email: \$(\$item.ContactEmail) | Used: \$(\$item.Used)\"
    }
    
    Disconnect-PnPOnline
    
} catch {
    Write-Host \"Error: \$_\" -ForegroundColor Red
}
"

echo ""
echo "Test code ready! Use 'TEST2024' when testing from the portal"
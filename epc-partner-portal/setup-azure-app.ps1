#!/snap/bin/pwsh
# Azure AD App Registration Setup for EPC Portal Automation
# Run this script as an Azure AD admin

param(
    [switch]$CreateNewApp,
    [switch]$UseExistingApp
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Azure AD App Setup for EPC Automation" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Configuration
$TenantId = "dd0eeaf2-2c36-4709-9554-6e2b2639c3d1"
$TenantName = "saberrenewables.onmicrosoft.com"
$CertPath = "$HOME/.certs/SaberEPCAutomation.crt"
$CertInfo = Get-Content "$HOME/.certs/SaberEPCAutomation-info.json" | ConvertFrom-Json

if ($CreateNewApp) {
    Write-Host "Creating new Azure AD App Registration..." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Run these commands in Azure Cloud Shell or with Azure CLI:" -ForegroundColor Green
    Write-Host ""
    
    Write-Host '# Login to Azure' -ForegroundColor Cyan
    Write-Host 'az login --tenant saberrenewables.onmicrosoft.com'
    Write-Host ""
    
    Write-Host '# Create the app registration' -ForegroundColor Cyan
    Write-Host @'
az ad app create `
    --display-name "EPC Portal Automation" `
    --sign-in-audience AzureADMyOrg `
    --key-type AsymmetricX509Cert `
    --key-usage Verify `
    --key-value "$(cat ~/.certs/SaberEPCAutomation.crt)"
'@
    Write-Host ""
    
    Write-Host '# Grant SharePoint permissions' -ForegroundColor Cyan
    Write-Host @'
# Get the app ID from the previous command output
$appId = "YOUR_NEW_APP_ID"

# Add SharePoint API permissions
az ad app permission add `
    --id $appId `
    --api 00000003-0000-0ff1-ce00-000000000000 `
    --api-permissions 678536fe-1083-478a-9c59-b99265e6b0d3=Role

# Grant admin consent
az ad app permission admin-consent --id $appId
'@
}
elseif ($UseExistingApp) {
    Write-Host "Using existing app (bbbfe394-7cff-4ac9-9e01-33cbf116b930)" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Certificate Details:" -ForegroundColor Green
    Write-Host "  Thumbprint: $($CertInfo.Thumbprint)" -ForegroundColor White
    Write-Host "  Path: $CertPath" -ForegroundColor White
    Write-Host ""
    
    Write-Host "Manual Steps in Azure Portal:" -ForegroundColor Cyan
    Write-Host "1. Go to: https://portal.azure.com" -ForegroundColor White
    Write-Host "2. Navigate to: Azure Active Directory > App registrations" -ForegroundColor White
    Write-Host "3. Search for: bbbfe394-7cff-4ac9-9e01-33cbf116b930" -ForegroundColor White
    Write-Host "4. Go to: Certificates & secrets > Certificates tab" -ForegroundColor White
    Write-Host "5. Click: Upload certificate" -ForegroundColor White
    Write-Host "6. Select: $CertPath" -ForegroundColor White
    Write-Host "7. Verify thumbprint: $($CertInfo.Thumbprint)" -ForegroundColor White
    Write-Host ""
    
    Write-Host "Testing Certificate Authentication:" -ForegroundColor Cyan
    Write-Host ""
    
    # Test the connection
    try {
        Write-Host "Attempting certificate authentication..." -ForegroundColor Yellow
        Connect-PnPOnline `
            -Url "https://saberrenewables.sharepoint.com/sites/SaberEPCPartners" `
            -ClientId "bbbfe394-7cff-4ac9-9e01-33cbf116b930" `
            -Tenant $TenantName `
            -CertificatePath $CertPath `
            -CertificatePassword (ConvertTo-SecureString -String "P@ssw0rd123!" -AsPlainText -Force)
        
        Write-Host "✓ Certificate authentication successful!" -ForegroundColor Green
        
        # Test permissions
        $lists = Get-PnPList
        Write-Host "✓ Can access SharePoint lists: $($lists.Count) lists found" -ForegroundColor Green
        
        Disconnect-PnPOnline
    }
    catch {
        Write-Host "✗ Certificate authentication failed" -ForegroundColor Red
        Write-Host "  Error: $_" -ForegroundColor Red
        Write-Host ""
        Write-Host "Make sure you've uploaded the certificate to Azure AD first!" -ForegroundColor Yellow
    }
}
else {
    Write-Host "Please choose an option:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "1. Use existing app with certificate:" -ForegroundColor White
    Write-Host "   ./setup-azure-app.ps1 -UseExistingApp" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "2. Create new app registration:" -ForegroundColor White
    Write-Host "   ./setup-azure-app.ps1 -CreateNewApp" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Recommendation: Start with option 1 (simpler)" -ForegroundColor Green
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "After Azure AD setup, update the processor:" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "The automated processor will use certificate auth:" -ForegroundColor White
Write-Host '  Connect-PnPOnline `' -ForegroundColor Gray
Write-Host '    -Url "https://saberrenewables.sharepoint.com/sites/SaberEPCPartners" `' -ForegroundColor Gray
Write-Host '    -ClientId "bbbfe394-7cff-4ac9-9e01-33cbf116b930" `' -ForegroundColor Gray
Write-Host '    -Tenant "saberrenewables.onmicrosoft.com" `' -ForegroundColor Gray
Write-Host '    -CertificatePath "~/.certs/SaberEPCAutomation.pfx" `' -ForegroundColor Gray
Write-Host '    -CertificatePassword (ConvertTo-SecureString -String "P@ssw0rd123!" -AsPlainText -Force)' -ForegroundColor Gray
Write-Host ""
#!/snap/bin/pwsh
# Azure AD Permission Checker and Alternative Solutions

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Azure AD Permission Analysis" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "COMMON REASONS CERTIFICATE UPLOAD FAILS:" -ForegroundColor Yellow
Write-Host ""

Write-Host "1. APP OWNERSHIP ISSUE:" -ForegroundColor Red
Write-Host "   - The app 'SharePoint PnP PowerShell' might be a multi-tenant app" -ForegroundColor White
Write-Host "   - You can't modify multi-tenant apps owned by Microsoft/third parties" -ForegroundColor White
Write-Host "   - Solution: Create your own app registration" -ForegroundColor Green
Write-Host ""

Write-Host "2. CONDITIONAL ACCESS POLICIES:" -ForegroundColor Red
Write-Host "   - Your org might block certificate auth" -ForegroundColor White
Write-Host "   - Solution: Use client secret instead" -ForegroundColor Green
Write-Host ""

Write-Host "3. APP REGISTRATION PERMISSIONS:" -ForegroundColor Red
Write-Host "   - You need 'Application Administrator' or 'Cloud Application Administrator' role" -ForegroundColor White
Write-Host "   - Global Admin should have this, but check if delegated" -ForegroundColor White
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  SOLUTION 1: Create Your Own App" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Since you're Global Admin, let's create a NEW app registration:" -ForegroundColor Green
Write-Host ""
Write-Host "1. Go to Azure Portal > Azure Active Directory > App registrations" -ForegroundColor White
Write-Host "2. Click 'New registration'" -ForegroundColor White
Write-Host "3. Name: 'EPC Portal Automation'" -ForegroundColor Yellow
Write-Host "4. Supported account types: 'Single tenant'" -ForegroundColor Yellow
Write-Host "5. Click Register" -ForegroundColor White
Write-Host ""
Write-Host "After creation:" -ForegroundColor Green
Write-Host "6. Go to 'Certificates & secrets'" -ForegroundColor White
Write-Host "7. Click 'New client secret' (easier than certificate!)" -ForegroundColor Yellow
Write-Host "8. Description: 'EPC Automation Secret'" -ForegroundColor Yellow
Write-Host "9. Expires: '24 months'" -ForegroundColor Yellow
Write-Host "10. COPY THE SECRET VALUE IMMEDIATELY!" -ForegroundColor Red
Write-Host ""
Write-Host "11. Go to 'API permissions'" -ForegroundColor White
Write-Host "12. Add permission > Microsoft Graph > Application permissions" -ForegroundColor White
Write-Host "13. Search and add: 'Sites.FullControl.All'" -ForegroundColor Yellow
Write-Host "14. Add permission > SharePoint > Application permissions" -ForegroundColor White
Write-Host "15. Add: 'Sites.FullControl.All'" -ForegroundColor Yellow
Write-Host "16. Click 'Grant admin consent'" -ForegroundColor Green
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  SOLUTION 2: Use Client Secret Auth" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "If you can add a client secret to the existing app:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Go to your app (bbbfe394-7cff-4ac9-9e01-33cbf116b930)" -ForegroundColor White
Write-Host "2. Certificates & secrets > Client secrets tab" -ForegroundColor White
Write-Host "3. New client secret" -ForegroundColor White
Write-Host "4. Save the secret value" -ForegroundColor Red
Write-Host ""

Write-Host "Connection string for client secret:" -ForegroundColor Green
Write-Host @'
Connect-PnPOnline `
    -Url "https://saberrenewables.sharepoint.com/sites/SaberEPCPartners" `
    -ClientId "YOUR_APP_ID" `
    -ClientSecret "YOUR_SECRET" `
    -WarningAction Ignore
'@ -ForegroundColor Gray

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  SOLUTION 3: Use Managed Identity" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Deploy to Azure (best long-term solution):" -ForegroundColor Green
Write-Host "1. Azure Automation Account" -ForegroundColor White
Write-Host "2. Azure Functions" -ForegroundColor White
Write-Host "3. Azure Logic Apps" -ForegroundColor White
Write-Host "All support Managed Identity - no secrets needed!" -ForegroundColor Yellow
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  SOLUTION 4: Use Device Code Flow" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "For the existing app, we can use device code flow:" -ForegroundColor Yellow
Write-Host ""
Write-Host @'
Connect-PnPOnline `
    -Url "https://saberrenewables.sharepoint.com/sites/SaberEPCPartners" `
    -DeviceLogin `
    -LaunchBrowser
'@ -ForegroundColor Gray
Write-Host ""
Write-Host "This creates a refresh token that lasts 90 days" -ForegroundColor Green
Write-Host "Store it and reuse for automation" -ForegroundColor Green
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  CHECK YOUR PERMISSIONS" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Run this to check your Azure AD roles:" -ForegroundColor Yellow
Write-Host ""
Write-Host "Install-Module AzureAD -Force -AllowClobber" -ForegroundColor Gray
Write-Host "Connect-AzureAD" -ForegroundColor Gray
Write-Host "Get-AzureADDirectoryRole | Where-Object {`$_.DisplayName -like '*Admin*'}" -ForegroundColor Gray
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  RECOMMENDED ACTION" -ForegroundColor Red
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "CREATE A NEW APP REGISTRATION!" -ForegroundColor Green
Write-Host "This gives you full control and avoids permission issues." -ForegroundColor Yellow
Write-Host ""
Write-Host "Would you like me to generate the script for that? (y/n)" -ForegroundColor Cyan
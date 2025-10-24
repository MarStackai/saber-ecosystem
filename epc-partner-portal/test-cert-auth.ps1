#!/snap/bin/pwsh
# Test Certificate Authentication

$thumbprint = "8A20540CDD30290406D52688D22C0F1B5B4973B3"
$clientId = "bbbfe394-7cff-4ac9-9e01-33cbf116b930"
$tenantId = "dd0eeaf2-2c36-4709-9554-6e2b2639c3d1"
$siteUrl = "https://saberrenewables.sharepoint.com/sites/SaberEPCPartners"

Write-Host "Testing certificate authentication..." -ForegroundColor Yellow
Write-Host "Thumbprint: $thumbprint" -ForegroundColor Cyan
Write-Host "Client ID: $clientId" -ForegroundColor Cyan
Write-Host ""

try {
    # Connect using certificate thumbprint
    Connect-PnPOnline `
        -Url $siteUrl `
        -ClientId $clientId `
        -Tenant $tenantId `
        -CertificatePath "/home/marstack/.certs/SaberEPCAutomation.pfx" `
        -CertificatePassword (ConvertTo-SecureString -String "P@ssw0rd123!" -AsPlainText -Force)
    
    Write-Host "✓ Connection successful!" -ForegroundColor Green
    
    # Test by getting site info
    $web = Get-PnPWeb
    Write-Host "Connected to: $($web.Title)" -ForegroundColor Green
    
    # Test list access
    $lists = Get-PnPList
    Write-Host "Found $($lists.Count) lists in the site" -ForegroundColor Green
    
    # Test specific lists
    $invitations = Get-PnPList -Identity "EPC Invitations"
    Write-Host "✓ Can access EPC Invitations list" -ForegroundColor Green
    
    $onboarding = Get-PnPList -Identity "EPC Onboarding"
    Write-Host "✓ Can access EPC Onboarding list" -ForegroundColor Green
    
    Disconnect-PnPOnline
    Write-Host ""
    Write-Host "✓ Certificate authentication test completed successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "You can now use certificate authentication in your scripts!" -ForegroundColor Yellow
    
} catch {
    Write-Host "✗ Connection failed: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "Make sure you have:" -ForegroundColor Yellow
    Write-Host "1. Uploaded the certificate to Azure AD" -ForegroundColor Yellow
    Write-Host "2. The certificate thumbprint matches: $thumbprint" -ForegroundColor Yellow
    Write-Host "3. The app has the necessary SharePoint permissions" -ForegroundColor Yellow
}
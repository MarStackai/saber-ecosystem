#!/snap/bin/pwsh
# Test Certificate Authentication Script

$certInfo = Get-Content '/home/marstack/.certs/SaberEPCAutomation-info.json' | ConvertFrom-Json

Write-Host "Testing certificate authentication..." -ForegroundColor Yellow
Write-Host "Thumbprint: $($certInfo.Thumbprint)" -ForegroundColor Cyan

try {
    Connect-PnPOnline `
        -Url 'https://saberrenewables.sharepoint.com/sites/SaberEPCPartners' `
        -ClientId $certInfo.ClientId `
        -Tenant $certInfo.TenantId `
        -Thumbprint $certInfo.Thumbprint
    
    Write-Host "✓ Connection successful!" -ForegroundColor Green
    
    # Test by getting site info
    $web = Get-PnPWeb
    Write-Host "Connected to: $($web.Title)" -ForegroundColor Green
    
    # Test list access
    $lists = Get-PnPList
    Write-Host "Found $($lists.Count) lists" -ForegroundColor Green
    
    Disconnect-PnPOnline
    Write-Host "✓ Test completed successfully!" -ForegroundColor Green
    
} catch {
    Write-Host "✗ Connection failed: $_" -ForegroundColor Red
}

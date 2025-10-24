#!/snap/bin/pwsh
<#
.SYNOPSIS
    Sets up certificate-based authentication for unattended SharePoint access
.DESCRIPTION
    This script creates a self-signed certificate and configures it for Azure AD app authentication
    to enable unattended access to SharePoint for automated scripts and cron jobs.
.PARAMETER TenantId
    The Azure AD tenant ID
.PARAMETER ClientId
    The Azure AD application (client) ID
#>

param(
    [Parameter(Mandatory=$false)]
    [string]$TenantId = "dd0eeaf2-2c36-4709-9554-6e2b2639c3d1",
    
    [Parameter(Mandatory=$false)]
    [string]$ClientId = "bbbfe394-7cff-4ac9-9e01-33cbf116b930",
    
    [string]$CertificateName = "SaberEPCAutomation",
    
    [string]$CertPath = "$HOME/.certs"
)

Write-Host "===============================================" -ForegroundColor Cyan
Write-Host "  SharePoint Certificate Authentication Setup" -ForegroundColor Cyan
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host ""

# Create certificate directory if it doesn't exist
if (!(Test-Path $CertPath)) {
    New-Item -ItemType Directory -Path $CertPath -Force | Out-Null
    Write-Host "✓ Created certificate directory: $CertPath" -ForegroundColor Green
}

# Step 1: Create a self-signed certificate
Write-Host "Step 1: Creating self-signed certificate..." -ForegroundColor Yellow

$cert = New-SelfSignedCertificate `
    -Subject "CN=$CertificateName" `
    -CertStoreLocation "Cert:\CurrentUser\My" `
    -KeyExportPolicy Exportable `
    -KeySpec Signature `
    -KeyLength 2048 `
    -KeyAlgorithm RSA `
    -HashAlgorithm SHA256 `
    -NotAfter (Get-Date).AddYears(2)

Write-Host "✓ Certificate created with thumbprint: $($cert.Thumbprint)" -ForegroundColor Green

# Step 2: Export certificate to PFX file
Write-Host ""
Write-Host "Step 2: Exporting certificate..." -ForegroundColor Yellow

$pfxPath = Join-Path $CertPath "$CertificateName.pfx"
$password = ConvertTo-SecureString -String "P@ssw0rd123!" -Force -AsPlainText

Export-PfxCertificate `
    -Cert $cert `
    -FilePath $pfxPath `
    -Password $password | Out-Null

Write-Host "✓ Certificate exported to: $pfxPath" -ForegroundColor Green

# Step 3: Export public certificate (.cer)
Write-Host ""
Write-Host "Step 3: Exporting public certificate..." -ForegroundColor Yellow

$cerPath = Join-Path $CertPath "$CertificateName.cer"
Export-Certificate -Cert $cert -FilePath $cerPath | Out-Null

Write-Host "✓ Public certificate exported to: $cerPath" -ForegroundColor Green

# Step 4: Get Base64 encoded certificate for Azure AD
Write-Host ""
Write-Host "Step 4: Preparing certificate for Azure AD..." -ForegroundColor Yellow

$certBase64 = [System.Convert]::ToBase64String($cert.RawData)

# Save certificate info to file
$certInfo = @{
    Thumbprint = $cert.Thumbprint
    Subject = $cert.Subject
    NotAfter = $cert.NotAfter
    TenantId = $TenantId
    ClientId = $ClientId
    PfxPath = $pfxPath
    CerPath = $cerPath
    Base64 = $certBase64
}

$certInfoPath = Join-Path $CertPath "$CertificateName-info.json"
$certInfo | ConvertTo-Json | Out-File -FilePath $certInfoPath

Write-Host "✓ Certificate info saved to: $certInfoPath" -ForegroundColor Green

# Step 5: Display instructions for Azure AD configuration
Write-Host ""
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host "  NEXT STEPS - Azure AD Configuration" -ForegroundColor Cyan
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Go to Azure Portal (https://portal.azure.com)" -ForegroundColor Yellow
Write-Host "2. Navigate to: Azure Active Directory > App registrations" -ForegroundColor Yellow
Write-Host "3. Find your app: 'SharePoint PnP PowerShell' (Client ID: $ClientId)" -ForegroundColor Yellow
Write-Host "4. Go to: Certificates & secrets > Certificates tab" -ForegroundColor Yellow
Write-Host "5. Click 'Upload certificate' and upload: $cerPath" -ForegroundColor Yellow
Write-Host "6. Verify the thumbprint matches: $($cert.Thumbprint)" -ForegroundColor Yellow
Write-Host ""
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host "  TEST CONNECTION" -ForegroundColor Cyan
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "To test the certificate authentication, run:" -ForegroundColor Yellow
Write-Host ""
Write-Host "Connect-PnPOnline -Url 'https://saberrenewables.sharepoint.com/sites/SaberEPCPartners' -ClientId '$ClientId' -Tenant '$TenantId' -Thumbprint '$($cert.Thumbprint)'" -ForegroundColor White
Write-Host ""
Write-Host "Or use the test script:" -ForegroundColor Yellow
Write-Host "$PSScriptRoot/test-certificate-auth.ps1" -ForegroundColor White
Write-Host ""

# Create test script
$testScript = @"
#!/snap/bin/pwsh
# Test Certificate Authentication Script

`$certInfo = Get-Content '$certInfoPath' | ConvertFrom-Json

Write-Host "Testing certificate authentication..." -ForegroundColor Yellow
Write-Host "Thumbprint: `$(`$certInfo.Thumbprint)" -ForegroundColor Cyan

try {
    Connect-PnPOnline ``
        -Url 'https://saberrenewables.sharepoint.com/sites/SaberEPCPartners' ``
        -ClientId `$certInfo.ClientId ``
        -Tenant `$certInfo.TenantId ``
        -Thumbprint `$certInfo.Thumbprint
    
    Write-Host "✓ Connection successful!" -ForegroundColor Green
    
    # Test by getting site info
    `$web = Get-PnPWeb
    Write-Host "Connected to: `$(`$web.Title)" -ForegroundColor Green
    
    # Test list access
    `$lists = Get-PnPList
    Write-Host "Found `$(`$lists.Count) lists" -ForegroundColor Green
    
    Disconnect-PnPOnline
    Write-Host "✓ Test completed successfully!" -ForegroundColor Green
    
} catch {
    Write-Host "✗ Connection failed: `$_" -ForegroundColor Red
}
"@

$testScriptPath = Join-Path $PSScriptRoot "test-certificate-auth.ps1"
$testScript | Out-File -FilePath $testScriptPath
chmod +x $testScriptPath

Write-Host "✓ Test script created: $testScriptPath" -ForegroundColor Green

# Create updated cron script with certificate auth
$cronScript = @"
#!/snap/bin/pwsh
# Automated EPC Processor Script with Certificate Authentication

`$certInfo = Get-Content '$certInfoPath' | ConvertFrom-Json
`$logPath = "`$HOME/saber_business_ops/logs/epc_processor.log"

function Write-Log {
    param([string]`$Message, [string]`$Level = "INFO")
    `$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    "[`$timestamp] [`$Level] `$Message" | Add-Content -Path `$logPath
}

Write-Log "Starting automated processor with certificate auth"

try {
    # Connect using certificate
    Connect-PnPOnline ``
        -Url 'https://saberrenewables.sharepoint.com/sites/SaberEPCPartners' ``
        -ClientId `$certInfo.ClientId ``
        -Tenant `$certInfo.TenantId ``
        -Thumbprint `$certInfo.Thumbprint
    
    Write-Log "Connected to SharePoint using certificate"
    
    # Run the processor
    & "$HOME/saber_business_ops/scripts/process-epc.ps1" ``
        -SiteUrl 'https://saberrenewables.sharepoint.com/sites/SaberEPCPartners' ``
        -ClientId `$certInfo.ClientId ``
        -Tenant `$certInfo.TenantId
    
    Disconnect-PnPOnline
    Write-Log "Processor completed successfully"
    
} catch {
    Write-Log "Error: `$_" "ERROR"
}
"@

$cronScriptPath = "$HOME/saber_business_ops/run-processor-cert.sh"
$cronScript | Out-File -FilePath $cronScriptPath
chmod +x $cronScriptPath

Write-Host ""
Write-Host "✓ Cron script with certificate auth created: $cronScriptPath" -ForegroundColor Green
Write-Host ""
Write-Host "To update your cron job to use certificate authentication:" -ForegroundColor Yellow
Write-Host "crontab -e" -ForegroundColor White
Write-Host "# Then replace the existing line with:" -ForegroundColor Gray
Write-Host "*/5 * * * * $cronScriptPath >> $HOME/saber_business_ops/logs/cron.log 2>&1" -ForegroundColor White
Write-Host ""
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host "  Setup Complete!" -ForegroundColor Green
Write-Host "===============================================" -ForegroundColor Cyan
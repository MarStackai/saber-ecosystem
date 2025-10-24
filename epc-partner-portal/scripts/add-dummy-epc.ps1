#!/usr/bin/pwsh
param(
    [Parameter(Mandatory=$true)]
    [string]$SiteUrl,
    
    [Parameter(Mandatory=$true)]
    [string]$ClientId,
    
    [Parameter(Mandatory=$true)]
    [string]$Tenant,
    
    [string]$AttachmentPath = "$HOME/Mark.png",
    
    [string]$CompanyName = "Test EPC Ltd",
    
    [switch]$SubmitImmediately
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "EPC Onboarding Test Item Creator" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

try {
    # Connect to SharePoint
    Write-Host "`nConnecting to SharePoint..." -ForegroundColor Yellow
    Connect-PnPOnline -Url $SiteUrl -ClientId $ClientId -Tenant $Tenant -DeviceLogin -WarningAction SilentlyContinue
    Write-Host "✓ Connected successfully" -ForegroundColor Green
    
    # Generate unique test data
    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $uniqueCompanyName = "$CompanyName $timestamp"
    
    # Create test item
    Write-Host "`nCreating test EPC onboarding item..." -ForegroundColor Yellow
    
    $itemValues = @{
        CompanyName = $uniqueCompanyName
        TradingName = "Test Trading Name"
        PrimaryContactName = "John Doe"
        PrimaryContactEmail = "john.doe@testepc.com"
        PrimaryContactPhone = "+44 1234 567890"
        RegisteredOffice = "123 Test Street, London, UK"
        CompanyRegNo = "TEST123456"
        VATNo = "GB123456789"
        Status = if ($SubmitImmediately) { "Submitted" } else { "Draft" }
        ISOStandards = @("ISO 9001", "ISO 14001")
        YearsTrading = 5
        ActsAsPrincipalContractor = "Yes"
        ActsAsPrincipalDesigner = "No"
        HasGDPRPolicy = "Yes"
        HSEQIncidentsLast5y = 0
        RIDDORLast3y = 0
        AgreeToSaberTerms = "Yes"
        CoverageRegion = @("North West", "Yorkshire")
    }
    
    $newItem = Add-PnPListItem -List "EPC Onboarding" -Values $itemValues
    $itemId = $newItem.Id
    
    Write-Host "✓ Created item with ID: $itemId" -ForegroundColor Green
    Write-Host "  Company Name: $uniqueCompanyName" -ForegroundColor Gray
    Write-Host "  Status: $($itemValues.Status)" -ForegroundColor Gray
    
    # Add attachment if file exists
    if (Test-Path $AttachmentPath) {
        Write-Host "`nAttaching file: $AttachmentPath" -ForegroundColor Yellow
        
        try {
            $fileName = Split-Path $AttachmentPath -Leaf
            $fileBytes = [System.IO.File]::ReadAllBytes($AttachmentPath)
            
            Add-PnPListItemAttachment -List "EPC Onboarding" -Identity $itemId `
                -FileName $fileName -ContentBytes $fileBytes
            
            Write-Host "✓ Attached $fileName successfully" -ForegroundColor Green
            Write-Host "  File size: $([Math]::Round($fileBytes.Length / 1KB, 2)) KB" -ForegroundColor Gray
        } catch {
            Write-Host "⚠ Could not attach file: $_" -ForegroundColor Yellow
        }
    } else {
        Write-Host "`n⚠ No attachment added (file not found: $AttachmentPath)" -ForegroundColor Yellow
        Write-Host "  To test with attachment, ensure Mark.png exists at $HOME/" -ForegroundColor Gray
    }
    
    # Display item URL
    $itemUrl = "$SiteUrl/Lists/EPC Onboarding/DispForm.aspx?ID=$itemId"
    Write-Host "`n========================================" -ForegroundColor Cyan
    Write-Host "Test item created successfully!" -ForegroundColor Green
    Write-Host "Item ID: $itemId" -ForegroundColor White
    Write-Host "View at: $itemUrl" -ForegroundColor White
    
    if ($SubmitImmediately) {
        Write-Host "`n⚡ Item created with Status=Submitted" -ForegroundColor Magenta
        Write-Host "   Ready for processor to handle!" -ForegroundColor Magenta
    } else {
        Write-Host "`nℹ Item created in Draft status" -ForegroundColor Blue
        Write-Host "  To trigger processing, manually change Status to 'Submitted'" -ForegroundColor Blue
        Write-Host "  Or run with -SubmitImmediately flag" -ForegroundColor Blue
    }
    
    Write-Host "========================================" -ForegroundColor Cyan
    
} catch {
    Write-Host "❌ Error: $_" -ForegroundColor Red
    exit 1
} finally {
    Disconnect-PnPOnline -ErrorAction SilentlyContinue
}
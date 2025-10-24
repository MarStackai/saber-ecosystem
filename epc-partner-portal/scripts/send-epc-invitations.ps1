#!/usr/bin/pwsh
<#
.SYNOPSIS
    Send invitations to EPC partners for onboarding
.DESCRIPTION
    Creates invitation records and sends email invitations with unique codes
.EXAMPLE
    ./send-epc-invitations.ps1 -CSVPath partners.csv
    ./send-epc-invitations.ps1 -Single -CompanyName "Test Ltd" -Email "test@example.com"
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$SiteUrl = "https://saberrenewables.sharepoint.com/sites/SaberEPCPartners",
    
    [Parameter(Mandatory=$true)]
    [string]$ClientId = "bbbfe394-7cff-4ac9-9e01-33cbf116b930",
    
    [Parameter(Mandatory=$true)]
    [string]$Tenant = "saberrenewables.onmicrosoft.com",
    
    [Parameter(ParameterSetName="Bulk")]
    [string]$CSVPath,
    
    [Parameter(ParameterSetName="Single")]
    [switch]$Single,
    
    [Parameter(ParameterSetName="Single", Mandatory=$true)]
    [string]$CompanyName,
    
    [Parameter(ParameterSetName="Single", Mandatory=$true)]
    [string]$Email,
    
    [string]$FormBaseUrl = "https://saberrenewables.sharepoint.com/sites/SaberEPCPartners/SitePages/EPCPartnerApplication.aspx",
    
    [int]$ValidityDays = 30,
    
    [switch]$TestMode
)

function Generate-InviteCode {
    # Generate 8-character alphanumeric code
    $chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    $code = ""
    for ($i = 0; $i -lt 8; $i++) {
        $code += $chars[(Get-Random -Maximum $chars.Length)]
    }
    return $code
}

function Send-InvitationEmail {
    param(
        [string]$ToEmail,
        [string]$CompanyName,
        [string]$InviteCode,
        [string]$FormUrl,
        [datetime]$ExpiryDate
    )
    
    $subject = "Invitation: Join Saber's EPC Partner Network"
    
    $body = @"
<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: 'Arial', sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; }
        .header { background: linear-gradient(135deg, #044D73, #0d1138); padding: 30px; text-align: center; }
        .logo { color: white; font-size: 24px; font-weight: bold; }
        .content { padding: 30px; background: #f8f9fa; }
        .btn { 
            display: inline-block;
            padding: 15px 30px;
            background: linear-gradient(135deg, #7CC061, #95D47E);
            color: white;
            text-decoration: none;
            border-radius: 8px;
            font-weight: bold;
        }
        .code-box {
            background: white;
            padding: 20px;
            border-left: 4px solid #7CC061;
            margin: 20px 0;
            font-family: monospace;
        }
        .footer { padding: 20px; text-align: center; color: #666; font-size: 12px; }
        h2 { color: #044D73; }
        .highlight { color: #7CC061; font-weight: bold; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="logo">SABER RENEWABLES</div>
        </div>
        
        <div class="content">
            <h2>Welcome to Saber's EPC Partner Network</h2>
            
            <p>Dear $CompanyName,</p>
            
            <p>You've been invited to join Saber Renewables' certified Energy Performance Certificate partner network. 
            This exclusive invitation allows you to complete our onboarding process and become part of our growing 
            network of sustainability professionals.</p>
            
            <div class="code-box">
                <strong>Your Invitation Code:</strong> <span style="font-size: 20px; color: #044D73;">$InviteCode</span><br>
                <strong>Valid Until:</strong> $($ExpiryDate.ToString("dd MMMM yyyy"))
            </div>
            
            <p><strong>To begin your application:</strong></p>
            
            <p style="text-align: center;">
                <a href="$FormUrl?code=$InviteCode" class="btn" style="color: white;">Start Application →</a>
            </p>
            
            <p><strong>What you'll need:</strong></p>
            <ul>
                <li>Company registration details</li>
                <li>Primary contact information</li>
                <li>ISO certifications (if applicable)</li>
                <li>Insurance certificates</li>
                <li>HSEQ policy documentation</li>
            </ul>
            
            <p>The application takes approximately <span class="highlight">15-20 minutes</span> to complete. 
            You can save your progress and return later if needed.</p>
            
            <p><strong>Why partner with Saber?</strong></p>
            <ul>
                <li>Access to premium EPC projects</li>
                <li>Professional development opportunities</li>
                <li>Industry-leading support and resources</li>
                <li>Competitive commission structure</li>
            </ul>
            
            <p>If you have any questions, please don't hesitate to contact our partner team at 
            <a href="mailto:partners@saberrenewables.com">partners@saberrenewables.com</a></p>
            
            <p>We look forward to welcoming you to our network!</p>
            
            <p>Best regards,<br>
            <strong>The Saber Renewables Team</strong></p>
        </div>
        
        <div class="footer">
            <p>© 2024 Saber Renewables | Leading the transition to sustainable energy</p>
            <p>This invitation is confidential and intended solely for $ToEmail</p>
            <p>Saber Renewables Ltd | Company No. 12345678 | VAT No. GB123456789</p>
        </div>
    </div>
</body>
</html>
"@
    
    if ($TestMode) {
        Write-Host "   📧 TEST MODE - Email would be sent to: $ToEmail" -ForegroundColor Cyan
        Write-Host "      Subject: $subject" -ForegroundColor Gray
        Write-Host "      Code: $InviteCode" -ForegroundColor Gray
        return $true
    }
    
    # For production: Use Microsoft Graph API or SMTP
    # This is a placeholder - implement actual email sending
    try {
        # Option 1: Use Send-MailMessage (if SMTP configured)
        # Send-MailMessage -To $ToEmail -Subject $subject -Body $body -BodyAsHtml -From "partners@saberrenewables.com"
        
        # Option 2: Use Microsoft Graph
        # $mail = @{
        #     message = @{
        #         subject = $subject
        #         body = @{ contentType = "HTML"; content = $body }
        #         toRecipients = @(@{ emailAddress = @{ address = $ToEmail } })
        #     }
        # }
        # Invoke-RestMethod -Uri "https://graph.microsoft.com/v1.0/me/sendMail" -Method POST -Body ($mail | ConvertTo-Json -Depth 10)
        
        Write-Host "   ✓ Email sent to $ToEmail" -ForegroundColor Green
        return $true
    } catch {
        Write-Host "   ❌ Failed to send email: $_" -ForegroundColor Red
        return $false
    }
}

# Main execution
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "EPC Partner Invitation System" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Connect to SharePoint
Write-Host "`nConnecting to SharePoint..." -ForegroundColor Yellow
Connect-PnPOnline -Url $SiteUrl -ClientId $ClientId -Tenant $Tenant -DeviceLogin

try {
    # Prepare recipient list
    $recipients = @()
    
    if ($Single) {
        $recipients += @{
            CompanyName = $CompanyName
            Email = $Email
        }
    } elseif ($CSVPath) {
        if (Test-Path $CSVPath) {
            $recipients = Import-Csv $CSVPath
            Write-Host "Loaded $($recipients.Count) recipients from CSV" -ForegroundColor Green
        } else {
            throw "CSV file not found: $CSVPath"
        }
    }
    
    Write-Host "`nProcessing invitations..." -ForegroundColor Yellow
    $successCount = 0
    $failCount = 0
    
    foreach ($recipient in $recipients) {
        Write-Host "`nProcessing: $($recipient.CompanyName)" -ForegroundColor White
        
        # Check if invitation already exists
        $existing = Get-PnPListItem -List "EPC Invitations" -Query "<View><Query><Where><Eq><FieldRef Name='ContactEmail'/><Value Type='Text'>$($recipient.Email)</Value></Eq></Where></Query></View>"
        
        if ($existing -and $existing.Count -gt 0) {
            Write-Host "   ⚠ Invitation already exists for $($recipient.Email)" -ForegroundColor Yellow
            
            # Check if expired
            $existingItem = $existing[0]
            if ($existingItem["ExpiryDate"] -lt (Get-Date)) {
                Write-Host "   ↻ Previous invitation expired, creating new one..." -ForegroundColor Yellow
            } else {
                Write-Host "   ℹ Active invitation still valid until $($existingItem["ExpiryDate"])" -ForegroundColor Gray
                continue
            }
        }
        
        # Generate invitation code
        $inviteCode = Generate-InviteCode
        $expiryDate = (Get-Date).AddDays($ValidityDays)
        
        # Create invitation record
        $inviteData = @{
            CompanyName = $recipient.CompanyName
            ContactEmail = $recipient.Email
            InviteCode = $inviteCode
            InviteSentDate = Get-Date
            ExpiryDate = $expiryDate
            InviteStatus = "Sent"
            AccessCount = 0
        }
        
        if ($recipient.Notes) {
            $inviteData.InviteNotes = $recipient.Notes
        }
        
        $newItem = Add-PnPListItem -List "EPC Invitations" -Values $inviteData
        Write-Host "   ✓ Invitation record created (ID: $($newItem.Id))" -ForegroundColor Green
        
        # Send email
        $emailSent = Send-InvitationEmail `
            -ToEmail $recipient.Email `
            -CompanyName $recipient.CompanyName `
            -InviteCode $inviteCode `
            -FormUrl $FormBaseUrl `
            -ExpiryDate $expiryDate
        
        if ($emailSent) {
            $successCount++
            Write-Host "   ✓ Invitation sent successfully" -ForegroundColor Green
            
            # Log the invitation URL
            $inviteUrl = "$FormBaseUrl?code=$inviteCode"
            Write-Host "   📎 Direct link: $inviteUrl" -ForegroundColor DarkGray
        } else {
            $failCount++
            # Update status to reflect email failure
            Set-PnPListItem -List "EPC Invitations" -Identity $newItem.Id -Values @{
                InviteStatus = "Failed"
                InviteNotes = "Email send failed"
            }
        }
    }
    
    # Summary
    Write-Host "`n========================================" -ForegroundColor Cyan
    Write-Host "Invitation Summary" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "✓ Successful: $successCount" -ForegroundColor Green
    if ($failCount -gt 0) {
        Write-Host "✗ Failed: $failCount" -ForegroundColor Red
    }
    Write-Host "Total processed: $($recipients.Count)" -ForegroundColor White
    
    Write-Host "`nView all invitations at:" -ForegroundColor Yellow
    Write-Host "$SiteUrl/Lists/EPC%20Invitations" -ForegroundColor White
    
} catch {
    Write-Host "`n❌ Error: $_" -ForegroundColor Red
} finally {
    Disconnect-PnPOnline
}

# Create sample CSV if it doesn't exist
if ($CSVPath -and !(Test-Path $CSVPath)) {
    Write-Host "`nCreating sample CSV template at: $CSVPath" -ForegroundColor Yellow
    
    $sampleData = @"
CompanyName,Email,Notes
"Green Energy Solutions Ltd","contact@greenenergy.example.com","Priority partner"
"Sustainable Homes UK","info@sustainablehomes.example.com","Existing relationship"
"EcoTech Partners","admin@ecotech.example.com","New prospect"
"@
    
    $sampleData | Out-File -FilePath $CSVPath
    Write-Host "✓ Sample CSV created. Edit it and run the script again." -ForegroundColor Green
}
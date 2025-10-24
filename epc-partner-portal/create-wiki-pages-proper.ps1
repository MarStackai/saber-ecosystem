#!/snap/bin/pwsh
# Create SharePoint Wiki Pages with Proper HTML Content
# This script creates actual wiki pages that display content immediately

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  Creating SharePoint Wiki Pages" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Configuration
$SiteUrl = "https://saberrenewables.sharepoint.com/sites/SaberEPCPartners"

Write-Host "Connecting to SharePoint..." -ForegroundColor Yellow

try {
    # Connect to SharePoint
    Connect-PnPOnline `
        -Url $SiteUrl `
        -ClientId "bbbfe394-7cff-4ac9-9e01-33cbf116b930" `
        -Tenant "saberrenewables.onmicrosoft.com" `
        -CertificatePath "$HOME/.certs/SaberEPCAutomation.pfx" `
        -CertificatePassword (ConvertTo-SecureString -String "P@ssw0rd123!" -AsPlainText -Force) `
        -WarningAction SilentlyContinue
    
    Write-Host "✅ Connected to SharePoint" -ForegroundColor Green
    Write-Host ""
    
    # Create EPC Operations Hub Page
    Write-Host "Creating EPC Operations Hub page..." -ForegroundColor Yellow
    $hubPage = Add-PnPPage -Name "EPC-Operations-Hub" -Title "EPC Operations Hub" -LayoutType Article -ErrorAction SilentlyContinue
    
    $hubContent = @"
<div style="font-family: 'Gotham', 'Segoe UI', sans-serif; padding: 20px;">
    <h1 style="color: #044D73; border-bottom: 3px solid #7CC061; padding-bottom: 10px;">EPC Partner Operations Hub</h1>
    
    <p style="font-size: 16px; color: #333; margin: 20px 0;">
        Your central resource for managing EPC partner relationships, from initial invitation through full onboarding.
    </p>
    
    <div style="background: linear-gradient(135deg, #044D73 0%, #066FA3 100%); color: white; padding: 30px; border-radius: 10px; margin: 20px 0;">
        <h2 style="color: white; margin-top: 0;">Welcome to the EPC Operations System</h2>
        <p>This platform streamlines our partner engagement process, ensuring consistent communication and efficient onboarding.</p>
    </div>
    
    <h2 style="color: #044D73; margin-top: 30px;">Quick Start Resources</h2>
    
    <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; margin: 20px 0;">
        <div style="border: 1px solid #ddd; padding: 20px; border-radius: 8px;">
            <h3 style="color: #044D73; margin-top: 0;">📋 System Overview</h3>
            <p>Understand the complete invitation and onboarding workflow.</p>
            <a href="/sites/SaberEPCPartners/SitePages/System-Overview.aspx" style="color: #7CC061; font-weight: bold;">Learn More →</a>
        </div>
        
        <div style="border: 1px solid #ddd; padding: 20px; border-radius: 8px;">
            <h3 style="color: #044D73; margin-top: 0;">🚀 Quick Start Guide</h3>
            <p>Get up and running with EPC operations in minutes.</p>
            <a href="/sites/SaberEPCPartners/SitePages/Quick-Start-Guide.aspx" style="color: #7CC061; font-weight: bold;">Get Started →</a>
        </div>
        
        <div style="border: 1px solid #ddd; padding: 20px; border-radius: 8px;">
            <h3 style="color: #044D73; margin-top: 0;">✉️ Creating Invitations</h3>
            <p>Step-by-step guide to inviting new EPC partners.</p>
            <a href="/sites/SaberEPCPartners/SitePages/Creating-Invitations.aspx" style="color: #7CC061; font-weight: bold;">View Guide →</a>
        </div>
        
        <div style="border: 1px solid #ddd; padding: 20px; border-radius: 8px;">
            <h3 style="color: #044D73; margin-top: 0;">🔧 Troubleshooting</h3>
            <p>Quick solutions to common issues and problems.</p>
            <a href="/sites/SaberEPCPartners/SitePages/Troubleshooting-Guide.aspx" style="color: #7CC061; font-weight: bold;">Get Help →</a>
        </div>
    </div>
    
    <h2 style="color: #044D73; margin-top: 30px;">Key Tools & Lists</h2>
    
    <ul style="line-height: 2;">
        <li><a href="/sites/SaberEPCPartners/Lists/EPC%20Invitations" style="color: #044D73;">📝 EPC Invitations List</a> - Manage partner invitations</li>
        <li><a href="/sites/SaberEPCPartners/Lists/EPC%20Onboarding" style="color: #044D73;">📋 EPC Onboarding List</a> - Track partner applications</li>
        <li><a href="https://epc.saberrenewable.energy" style="color: #044D73;">🌐 Partner Portal</a> - External partner application site</li>
        <li><a href="https://make.powerautomate.com" style="color: #044D73;">⚡ Power Automate</a> - Workflow management</li>
    </ul>
    
    <div style="background: #f5f5f5; padding: 20px; border-left: 4px solid #7CC061; margin: 30px 0;">
        <h3 style="color: #044D73; margin-top: 0;">Need Support?</h3>
        <p>Contact the system administrator at <a href="mailto:sysadmin@saberrenewables.com" style="color: #7CC061;">sysadmin@saberrenewables.com</a></p>
    </div>
</div>
"@
    
    Set-PnPPageTextPart -Page $hubPage -Text $hubContent
    Set-PnPPage -Identity $hubPage -Publish
    Write-Host "  ✅ Created: EPC Operations Hub" -ForegroundColor Green
    
    # Create System Overview Page
    Write-Host "Creating System Overview page..." -ForegroundColor Yellow
    $overviewPage = Add-PnPPage -Name "System-Overview" -Title "System Overview" -LayoutType Article -ErrorAction SilentlyContinue
    
    $overviewContent = @"
<div style="font-family: 'Gotham', 'Segoe UI', sans-serif; padding: 20px;">
    <h1 style="color: #044D73; border-bottom: 3px solid #7CC061; padding-bottom: 10px;">System Overview</h1>
    
    <p style="font-size: 16px; color: #333; margin: 20px 0;">
        The EPC Partner Management System streamlines the entire partner engagement lifecycle through automated workflows and integrated tools.
    </p>
    
    <h2 style="color: #044D73; margin-top: 30px;">Key Components</h2>
    
    <div style="background: #f9f9f9; padding: 20px; border-radius: 8px; margin: 20px 0;">
        <h3 style="color: #044D73;">1. SharePoint Lists</h3>
        <ul>
            <li><strong>EPC Invitations:</strong> Stores invitation codes and partner details</li>
            <li><strong>EPC Onboarding:</strong> Tracks submitted applications and partner data</li>
        </ul>
    </div>
    
    <div style="background: #f9f9f9; padding: 20px; border-radius: 8px; margin: 20px 0;">
        <h3 style="color: #044D73;">2. Power Automate Flows</h3>
        <ul>
            <li><strong>Invitation Email Flow:</strong> Automatically sends emails when invitations are created</li>
            <li><strong>Application Processor:</strong> Processes submitted applications and updates SharePoint</li>
        </ul>
    </div>
    
    <div style="background: #f9f9f9; padding: 20px; border-radius: 8px; margin: 20px 0;">
        <h3 style="color: #044D73;">3. External Portal</h3>
        <ul>
            <li><strong>URL:</strong> <a href="https://epc.saberrenewable.energy" style="color: #7CC061;">epc.saberrenewable.energy</a></li>
            <li><strong>Purpose:</strong> Partner-facing application form</li>
            <li><strong>Technology:</strong> Cloudflare Pages with Worker API</li>
        </ul>
    </div>
    
    <h2 style="color: #044D73; margin-top: 30px;">Process Flow</h2>
    
    <ol style="line-height: 2;">
        <li><strong>Invitation Creation:</strong> Operations team creates invitation with unique 8-character code</li>
        <li><strong>Email Notification:</strong> Power Automate sends invitation email to partner</li>
        <li><strong>Partner Application:</strong> Partner uses code to access and submit application form</li>
        <li><strong>Data Processing:</strong> Cloudflare Worker validates code and triggers Power Automate</li>
        <li><strong>SharePoint Update:</strong> Application data stored in EPC Onboarding list</li>
        <li><strong>Status Tracking:</strong> Invitation marked as used, preventing duplicate applications</li>
    </ol>
    
    <h2 style="color: #044D73; margin-top: 30px;">Security Features</h2>
    
    <ul style="line-height: 2;">
        <li>✅ Unique 8-character invitation codes (avoiding confusing characters)</li>
        <li>✅ Single-use codes prevent duplicate submissions</li>
        <li>✅ 30-day expiration on invitation codes</li>
        <li>✅ Certificate-based authentication for automation</li>
        <li>✅ Audit trail in SharePoint for all activities</li>
    </ul>
    
    <div style="background: linear-gradient(135deg, #044D73 0%, #066FA3 100%); color: white; padding: 20px; border-radius: 8px; margin: 30px 0;">
        <h3 style="color: white;">Integration Points</h3>
        <p>The system integrates with Microsoft 365, Azure AD, Power Platform, and Cloudflare to provide a seamless experience for both internal teams and external partners.</p>
    </div>
</div>
"@
    
    Set-PnPPageTextPart -Page $overviewPage -Text $overviewContent
    Set-PnPPage -Identity $overviewPage -Publish
    Write-Host "  ✅ Created: System Overview" -ForegroundColor Green
    
    # Create Quick Start Guide Page
    Write-Host "Creating Quick Start Guide page..." -ForegroundColor Yellow
    $quickStartPage = Add-PnPPage -Name "Quick-Start-Guide" -Title "Quick Start Guide" -LayoutType Article -ErrorAction SilentlyContinue
    
    $quickStartContent = @"
<div style="font-family: 'Gotham', 'Segoe UI', sans-serif; padding: 20px;">
    <h1 style="color: #044D73; border-bottom: 3px solid #7CC061; padding-bottom: 10px;">Quick Start Guide</h1>
    
    <p style="font-size: 16px; color: #333; margin: 20px 0;">
        Get started with EPC partner management in just a few steps.
    </p>
    
    <h2 style="color: #044D73; margin-top: 30px;">Creating Your First Invitation</h2>
    
    <div style="background: #e8f4f8; padding: 20px; border-radius: 8px; margin: 20px 0;">
        <h3 style="color: #044D73;">Option 1: SharePoint Interface</h3>
        <ol>
            <li>Navigate to <a href="/sites/SaberEPCPartners/Lists/EPC%20Invitations" style="color: #7CC061;">EPC Invitations List</a></li>
            <li>Click "New" to create an invitation</li>
            <li>Enter partner details:
                <ul>
                    <li>Company Name</li>
                    <li>Contact Name</li>
                    <li>Contact Email</li>
                </ul>
            </li>
            <li>A unique code will be generated automatically</li>
            <li>Save to trigger the invitation email</li>
        </ol>
    </div>
    
    <div style="background: #f0f9f0; padding: 20px; border-radius: 8px; margin: 20px 0;">
        <h3 style="color: #044D73;">Option 2: PowerShell Script</h3>
        <pre style="background: #333; color: #7CC061; padding: 15px; border-radius: 5px; overflow-x: auto;">
./create-invitation.ps1 \
    -CompanyName "Partner Company Ltd" \
    -ContactEmail "contact@partner.com" \
    -ContactName "John Smith"
        </pre>
    </div>
    
    <h2 style="color: #044D73; margin-top: 30px;">Monitoring Applications</h2>
    
    <ol style="line-height: 2;">
        <li>Go to <a href="/sites/SaberEPCPartners/Lists/EPC%20Onboarding" style="color: #7CC061;">EPC Onboarding List</a></li>
        <li>Use custom views:
            <ul>
                <li><strong>Active Applications:</strong> New submissions</li>
                <li><strong>Pending Review:</strong> In review process</li>
                <li><strong>Approved Partners:</strong> Completed onboarding</li>
            </ul>
        </li>
        <li>Click any partner for detailed view</li>
    </ol>
    
    <h2 style="color: #044D73; margin-top: 30px;">Common Tasks</h2>
    
    <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; margin: 20px 0;">
        <div style="border: 1px solid #ddd; padding: 15px; border-radius: 5px;">
            <h4 style="color: #044D73;">📧 Resend Invitation Email</h4>
            <p>Edit invitation → Set InvitationSent = No → Save</p>
        </div>
        
        <div style="border: 1px solid #ddd; padding: 15px; border-radius: 5px;">
            <h4 style="color: #044D73;">🔍 Check Code Status</h4>
            <p>Filter invitations by Code column → View Used status</p>
        </div>
        
        <div style="border: 1px solid #ddd; padding: 15px; border-radius: 5px;">
            <h4 style="color: #044D73;">📊 Export Partner Data</h4>
            <p>Select items → Export to Excel → Download</p>
        </div>
        
        <div style="border: 1px solid #ddd; padding: 15px; border-radius: 5px;">
            <h4 style="color: #044D73;">⚡ Check Workflow Status</h4>
            <p>Power Automate → Run history → Review status</p>
        </div>
    </div>
    
    <h2 style="color: #044D73; margin-top: 30px;">Tips for Success</h2>
    
    <ul style="line-height: 2;">
        <li>✅ Always verify email addresses before sending invitations</li>
        <li>✅ Monitor Power Automate for failed runs daily</li>
        <li>✅ Archive expired invitations monthly</li>
        <li>✅ Test with internal email addresses first</li>
        <li>✅ Keep partner communication professional and timely</li>
    </ul>
    
    <div style="background: #f5f5f5; padding: 20px; border-left: 4px solid #7CC061; margin: 30px 0;">
        <h3 style="color: #044D73;">Next Steps</h3>
        <p>Ready to dive deeper? Check out our <a href="/sites/SaberEPCPartners/SitePages/Creating-Invitations.aspx" style="color: #7CC061;">detailed invitation guide</a> or explore <a href="/sites/SaberEPCPartners/SitePages/Troubleshooting-Guide.aspx" style="color: #7CC061;">troubleshooting resources</a>.</p>
    </div>
</div>
"@
    
    Set-PnPPageTextPart -Page $quickStartPage -Text $quickStartContent
    Set-PnPPage -Identity $quickStartPage -Publish
    Write-Host "  ✅ Created: Quick Start Guide" -ForegroundColor Green
    
    # Create Creating Invitations Page
    Write-Host "Creating Invitations Guide page..." -ForegroundColor Yellow
    $invitationsPage = Add-PnPPage -Name "Creating-Invitations" -Title "Creating Invitations" -LayoutType Article -ErrorAction SilentlyContinue
    
    $invitationsContent = @"
<div style="font-family: 'Gotham', 'Segoe UI', sans-serif; padding: 20px;">
    <h1 style="color: #044D73; border-bottom: 3px solid #7CC061; padding-bottom: 10px;">Creating Invitations</h1>
    
    <p style="font-size: 16px; color: #333; margin: 20px 0;">
        Complete guide to creating and managing EPC partner invitations.
    </p>
    
    <h2 style="color: #044D73; margin-top: 30px;">Methods for Creating Invitations</h2>
    
    <h3 style="color: #044D73;">Method 1: SharePoint List (Recommended)</h3>
    
    <ol style="line-height: 2;">
        <li>Navigate to <a href="/sites/SaberEPCPartners/Lists/EPC%20Invitations" style="color: #7CC061;">EPC Invitations List</a></li>
        <li>Click the <strong>"New"</strong> button</li>
        <li>Fill in required fields:
            <ul>
                <li><strong>Company Name:</strong> Full legal name of partner company</li>
                <li><strong>Contact Name:</strong> Primary contact person</li>
                <li><strong>Contact Email:</strong> Valid email address (will receive invitation)</li>
            </ul>
        </li>
        <li>Optional fields:
            <ul>
                <li><strong>Notes:</strong> Internal notes about the partner</li>
                <li><strong>Region:</strong> Geographic coverage area</li>
            </ul>
        </li>
        <li>Click <strong>"Save"</strong> - the system will:
            <ul>
                <li>Generate unique 8-character code</li>
                <li>Set 30-day expiration</li>
                <li>Trigger email via Power Automate</li>
            </ul>
        </li>
    </ol>
    
    <h3 style="color: #044D73;">Method 2: PowerShell Script</h3>
    
    <div style="background: #f0f9f0; padding: 20px; border-radius: 8px; margin: 20px 0;">
        <h4>Single Invitation:</h4>
        <pre style="background: #333; color: #7CC061; padding: 15px; border-radius: 5px; overflow-x: auto;">
./create-invitation.ps1 \
    -CompanyName "Solar Excellence Ltd" \
    -ContactEmail "john@solarexcellence.com" \
    -ContactName "John Smith" \
    -DaysValid 30 \
    -SendEmail
        </pre>
    </div>
    
    <div style="background: #f0f9f0; padding: 20px; border-radius: 8px; margin: 20px 0;">
        <h4>Batch Invitations:</h4>
        <pre style="background: #333; color: #7CC061; padding: 15px; border-radius: 5px; overflow-x: auto;">
# Edit batch-create-invitations.ps1 with partner list
./batch-create-invitations.ps1
# Outputs CSV with all generated codes
        </pre>
    </div>
    
    <h2 style="color: #044D73; margin-top: 30px;">Invitation Code Format</h2>
    
    <div style="background: #e8f4f8; padding: 20px; border-radius: 8px; margin: 20px 0;">
        <h3 style="color: #044D73;">Code Specifications:</h3>
        <ul>
            <li><strong>Length:</strong> 8 characters</li>
            <li><strong>Characters:</strong> A-Z (except O, I) and 2-9 (except 0, 1)</li>
            <li><strong>Example:</strong> ABCD2345, XYZW6789</li>
            <li><strong>Purpose:</strong> Avoids confusion between similar characters</li>
        </ul>
    </div>
    
    <h2 style="color: #044D73; margin-top: 30px;">Email Template</h2>
    
    <div style="background: #f9f9f9; padding: 20px; border-radius: 8px; margin: 20px 0;">
        <p><strong>Subject:</strong> Invitation to Join Saber EPC Partner Network</p>
        <hr style="border: 1px solid #ddd;">
        <p>Dear [Contact Name],</p>
        <p>We're pleased to invite [Company Name] to join the Saber EPC Partner Network.</p>
        <p><strong>Your Invitation Code:</strong> [CODE]</p>
        <p><strong>Application Portal:</strong> <a href="https://epc.saberrenewable.energy/epc/apply">https://epc.saberrenewable.energy/epc/apply</a></p>
        <p>This code expires in 30 days. Please complete your application promptly.</p>
        <p>Best regards,<br>Saber EPC Team</p>
    </div>
    
    <h2 style="color: #044D73; margin-top: 30px;">Managing Invitations</h2>
    
    <h3 style="color: #044D73;">Checking Invitation Status</h3>
    <ol>
        <li>Go to EPC Invitations list</li>
        <li>Find invitation by code or company name</li>
        <li>Check fields:
            <ul>
                <li><strong>Used:</strong> Yes/No</li>
                <li><strong>ExpiryDate:</strong> Valid until date</li>
                <li><strong>InvitationSent:</strong> Email status</li>
            </ul>
        </li>
    </ol>
    
    <h3 style="color: #044D73;">Common Actions</h3>
    
    <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
        <tr style="background: #044D73; color: white;">
            <th style="padding: 10px; text-align: left;">Action</th>
            <th style="padding: 10px; text-align: left;">Steps</th>
        </tr>
        <tr style="background: #f9f9f9;">
            <td style="padding: 10px; border: 1px solid #ddd;"><strong>Resend Email</strong></td>
            <td style="padding: 10px; border: 1px solid #ddd;">Edit → Set InvitationSent = No → Save</td>
        </tr>
        <tr>
            <td style="padding: 10px; border: 1px solid #ddd;"><strong>Extend Expiry</strong></td>
            <td style="padding: 10px; border: 1px solid #ddd;">Edit → Update ExpiryDate → Save</td>
        </tr>
        <tr style="background: #f9f9f9;">
            <td style="padding: 10px; border: 1px solid #ddd;"><strong>Cancel Invitation</strong></td>
            <td style="padding: 10px; border: 1px solid #ddd;">Edit → Set Status = Cancelled → Save</td>
        </tr>
        <tr>
            <td style="padding: 10px; border: 1px solid #ddd;"><strong>View Application</strong></td>
            <td style="padding: 10px; border: 1px solid #ddd;">Check EPC Onboarding list for matching code</td>
        </tr>
    </table>
    
    <h2 style="color: #044D73; margin-top: 30px;">Best Practices</h2>
    
    <ul style="line-height: 2;">
        <li>✅ Verify email addresses before sending</li>
        <li>✅ Include partner's legal company name</li>
        <li>✅ Add internal notes for context</li>
        <li>✅ Monitor for bounced emails</li>
        <li>✅ Follow up if no response within 7 days</li>
        <li>✅ Archive expired invitations monthly</li>
    </ul>
    
    <div style="background: linear-gradient(135deg, #044D73 0%, #066FA3 100%); color: white; padding: 20px; border-radius: 8px; margin: 30px 0;">
        <h3 style="color: white;">Pro Tip</h3>
        <p>Create test invitations with your own email first to verify the system is working correctly before sending to partners.</p>
    </div>
</div>
"@
    
    Set-PnPPageTextPart -Page $invitationsPage -Text $invitationsContent
    Set-PnPPage -Identity $invitationsPage -Publish
    Write-Host "  ✅ Created: Creating Invitations" -ForegroundColor Green
    
    # Create Troubleshooting Guide Page
    Write-Host "Creating Troubleshooting Guide page..." -ForegroundColor Yellow
    $troublePage = Add-PnPPage -Name "Troubleshooting-Guide" -Title "Troubleshooting Guide" -LayoutType Article -ErrorAction SilentlyContinue
    
    $troubleContent = @"
<div style="font-family: 'Gotham', 'Segoe UI', sans-serif; padding: 20px;">
    <h1 style="color: #044D73; border-bottom: 3px solid #7CC061; padding-bottom: 10px;">Troubleshooting Guide</h1>
    
    <p style="font-size: 16px; color: #333; margin: 20px 0;">
        Quick solutions to common issues with the EPC Partner Management System.
    </p>
    
    <h2 style="color: #044D73; margin-top: 30px;">Common Issues</h2>
    
    <div style="background: #fff3cd; padding: 20px; border-left: 4px solid #ffc107; margin: 20px 0;">
        <h3 style="color: #856404;">Issue: Invitation Email Not Sent</h3>
        <p><strong>Symptoms:</strong> Partner reports no email received</p>
        <p><strong>Solutions:</strong></p>
        <ol>
            <li>Check Power Automate run history for errors</li>
            <li>Verify email address is correct</li>
            <li>Ask partner to check spam/junk folders</li>
            <li>Manually resend: Edit invitation → Set InvitationSent = No → Save</li>
        </ol>
    </div>
    
    <div style="background: #fff3cd; padding: 20px; border-left: 4px solid #ffc107; margin: 20px 0;">
        <h3 style="color: #856404;">Issue: Code Not Working on Portal</h3>
        <p><strong>Symptoms:</strong> "Invalid or expired invitation code" error</p>
        <p><strong>Solutions:</strong></p>
        <ol>
            <li>Verify code status in EPC Invitations list</li>
            <li>Check: Used = No, ExpiryDate > Today</li>
            <li>Ensure code is entered exactly (case-sensitive)</li>
            <li>Create new invitation if expired</li>
        </ol>
    </div>
    
    <div style="background: #fff3cd; padding: 20px; border-left: 4px solid #ffc107; margin: 20px 0;">
        <h3 style="color: #856404;">Issue: Application Not in SharePoint</h3>
        <p><strong>Symptoms:</strong> Partner submitted but no entry in EPC Onboarding</p>
        <p><strong>Solutions:</strong></p>
        <ol>
            <li>Check Power Automate "Application Processor" flow</li>
            <li>Look for failed runs in history</li>
            <li>Verify Cloudflare Worker is running</li>
            <li>Create manual entry if needed</li>
        </ol>
    </div>
    
    <h2 style="color: #044D73; margin-top: 30px;">PowerShell Script Errors</h2>
    
    <div style="background: #f8d7da; padding: 20px; border-left: 4px solid #dc3545; margin: 20px 0;">
        <h3 style="color: #721c24;">Error: Certificate Authentication Failed</h3>
        <pre style="background: #333; color: #ff6b6b; padding: 10px; border-radius: 5px;">
The specified certificate could not be read
        </pre>
        <p><strong>Fix:</strong></p>
        <ol>
            <li>Verify certificate exists: <code>Test-Path "~/.certs/SaberEPCAutomation.pfx"</code></li>
            <li>Check password is correct: P@ssw0rd123!</li>
            <li>Ensure certificate uploaded to Azure AD app</li>
        </ol>
    </div>
    
    <h2 style="color: #044D73; margin-top: 30px;">Power Automate Issues</h2>
    
    <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
        <tr style="background: #044D73; color: white;">
            <th style="padding: 10px;">Problem</th>
            <th style="padding: 10px;">Solution</th>
        </tr>
        <tr style="background: #f9f9f9;">
            <td style="padding: 10px; border: 1px solid #ddd;">Flow not triggering</td>
            <td style="padding: 10px; border: 1px solid #ddd;">Ensure flow is ON, check connections valid</td>
        </tr>
        <tr>
            <td style="padding: 10px; border: 1px solid #ddd;">HTTP 500 error</td>
            <td style="padding: 10px; border: 1px solid #ddd;">Verify JSON schema matches request format</td>
        </tr>
        <tr style="background: #f9f9f9;">
            <td style="padding: 10px; border: 1px solid #ddd;">Email not sending</td>
            <td style="padding: 10px; border: 1px solid #ddd;">Check Office 365 connection, verify quotas</td>
        </tr>
    </table>
    
    <h2 style="color: #044D73; margin-top: 30px;">Quick Checks</h2>
    
    <div style="background: #d4edda; padding: 20px; border-left: 4px solid #28a745; margin: 20px 0;">
        <h3 style="color: #155724;">Daily Health Checks</h3>
        <ul>
            <li>✅ Review Power Automate run history</li>
            <li>✅ Check for pending invitations</li>
            <li>✅ Monitor new applications</li>
            <li>✅ Verify email delivery status</li>
        </ul>
    </div>
    
    <h2 style="color: #044D73; margin-top: 30px;">Emergency Procedures</h2>
    
    <div style="background: linear-gradient(135deg, #dc3545 0%, #c82333 100%); color: white; padding: 20px; border-radius: 8px; margin: 20px 0;">
        <h3 style="color: white;">System Complete Failure</h3>
        <ol>
            <li>Switch to manual process immediately</li>
            <li>Document all invitations offline</li>
            <li>Contact: sysadmin@saberrenewables.com</li>
            <li>Check all components: SharePoint, Power Automate, Cloudflare</li>
        </ol>
    </div>
    
    <h2 style="color: #044D73; margin-top: 30px;">Support Escalation</h2>
    
    <ol style="line-height: 2;">
        <li><strong>Level 1:</strong> Check this documentation</li>
        <li><strong>Level 2:</strong> Contact sysadmin@saberrenewables.com (4-hour response)</li>
        <li><strong>Level 3:</strong> Microsoft Support (SharePoint/Power Automate issues)</li>
        <li><strong>Level 4:</strong> Development team for custom modifications</li>
    </ol>
    
    <div style="background: #f5f5f5; padding: 20px; border-left: 4px solid #7CC061; margin: 30px 0;">
        <h3 style="color: #044D73;">Prevention Tips</h3>
        <ul>
            <li>Archive expired invitations monthly</li>
            <li>Test with internal emails first</li>
            <li>Monitor system performance weekly</li>
            <li>Keep documentation updated</li>
        </ul>
    </div>
</div>
"@
    
    Set-PnPPageTextPart -Page $troublePage -Text $troubleContent
    Set-PnPPage -Identity $troublePage -Publish
    Write-Host "  ✅ Created: Troubleshooting Guide" -ForegroundColor Green
    
    Write-Host ""
    Write-Host "================================================" -ForegroundColor Cyan
    Write-Host "  Wiki Pages Created Successfully!" -ForegroundColor Cyan
    Write-Host "================================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Pages created:" -ForegroundColor Green
    Write-Host "  ✅ EPC-Operations-Hub" -ForegroundColor White
    Write-Host "  ✅ System-Overview" -ForegroundColor White
    Write-Host "  ✅ Quick-Start-Guide" -ForegroundColor White
    Write-Host "  ✅ Creating-Invitations" -ForegroundColor White
    Write-Host "  ✅ Troubleshooting-Guide" -ForegroundColor White
    Write-Host ""
    Write-Host "To view the pages:" -ForegroundColor Yellow
    Write-Host "1. Go to: $SiteUrl/SitePages" -ForegroundColor White
    Write-Host "2. Look for the newly created pages" -ForegroundColor White
    Write-Host "3. Add to navigation menu as needed" -ForegroundColor White
    Write-Host ""
    Write-Host "The pages include:" -ForegroundColor Yellow
    Write-Host "- Formatted HTML content with Saber branding" -ForegroundColor Gray
    Write-Host "- Interactive links between pages" -ForegroundColor Gray
    Write-Host "- Styled sections and highlights" -ForegroundColor Gray
    Write-Host "- Direct links to lists and tools" -ForegroundColor Gray
    Write-Host ""
    
    Disconnect-PnPOnline
    
} catch {
    Write-Host "❌ Error: $_" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Wiki pages creation complete!" -ForegroundColor Green
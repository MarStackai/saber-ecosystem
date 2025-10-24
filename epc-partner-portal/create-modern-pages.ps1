#!/snap/bin/pwsh
# Create Modern SharePoint Pages with Content
# Uses ClientSidePage commands for better reliability

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  Creating Modern SharePoint Pages" -ForegroundColor Cyan
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
    
    # Remove existing page if it exists
    Remove-PnPPage -Identity "EPC-Operations-Hub" -Force -ErrorAction SilentlyContinue
    
    # Create new client-side page
    $hubPage = Add-PnPClientSidePage -Name "EPC-Operations-Hub" -Title "EPC Operations Hub" -LayoutType Article
    
    # Add text web part with content
    Add-PnPClientSideText -Page $hubPage -Text @"
<h1>EPC Partner Operations Hub</h1>
<p><strong>Your central resource for managing EPC partner relationships, from initial invitation through full onboarding.</strong></p>

<h2>Welcome to the EPC Operations System</h2>
<p>This platform streamlines our partner engagement process, ensuring consistent communication and efficient onboarding.</p>

<h2>Quick Start Resources</h2>
<ul>
<li><strong>System Overview</strong> - Understand the complete invitation and onboarding workflow</li>
<li><strong>Quick Start Guide</strong> - Get up and running with EPC operations in minutes</li>
<li><strong>Creating Invitations</strong> - Step-by-step guide to inviting new EPC partners</li>
<li><strong>Troubleshooting</strong> - Quick solutions to common issues and problems</li>
</ul>

<h2>Key Tools & Lists</h2>
<ul>
<li><a href="/sites/SaberEPCPartners/Lists/EPC%20Invitations">📝 EPC Invitations List</a> - Manage partner invitations</li>
<li><a href="/sites/SaberEPCPartners/Lists/EPC%20Onboarding">📋 EPC Onboarding List</a> - Track partner applications</li>
<li><a href="https://epc.saberrenewable.energy">🌐 Partner Portal</a> - External partner application site</li>
<li><a href="https://make.powerautomate.com">⚡ Power Automate</a> - Workflow management</li>
</ul>

<h3>Need Support?</h3>
<p>Contact the system administrator at <a href="mailto:sysadmin@saberrenewables.com">sysadmin@saberrenewables.com</a></p>
"@
    
    # Publish the page
    Set-PnPClientSidePage -Identity $hubPage -Publish
    Write-Host "  ✅ Created: EPC Operations Hub" -ForegroundColor Green
    
    # Create System Overview Page
    Write-Host "Creating System Overview page..." -ForegroundColor Yellow
    
    Remove-PnPPage -Identity "System-Overview" -Force -ErrorAction SilentlyContinue
    $overviewPage = Add-PnPClientSidePage -Name "System-Overview" -Title "System Overview" -LayoutType Article
    
    Add-PnPClientSideText -Page $overviewPage -Text @"
<h1>System Overview</h1>
<p><strong>The EPC Partner Management System streamlines the entire partner engagement lifecycle through automated workflows and integrated tools.</strong></p>

<h2>Key Components</h2>

<h3>1. SharePoint Lists</h3>
<ul>
<li><strong>EPC Invitations:</strong> Stores invitation codes and partner details</li>
<li><strong>EPC Onboarding:</strong> Tracks submitted applications and partner data</li>
</ul>

<h3>2. Power Automate Flows</h3>
<ul>
<li><strong>Invitation Email Flow:</strong> Automatically sends emails when invitations are created</li>
<li><strong>Application Processor:</strong> Processes submitted applications and updates SharePoint</li>
</ul>

<h3>3. External Portal</h3>
<ul>
<li><strong>URL:</strong> <a href="https://epc.saberrenewable.energy">epc.saberrenewable.energy</a></li>
<li><strong>Purpose:</strong> Partner-facing application form</li>
<li><strong>Technology:</strong> Cloudflare Pages with Worker API</li>
</ul>

<h2>Process Flow</h2>
<ol>
<li><strong>Invitation Creation:</strong> Operations team creates invitation with unique 8-character code</li>
<li><strong>Email Notification:</strong> Power Automate sends invitation email to partner</li>
<li><strong>Partner Application:</strong> Partner uses code to access and submit application form</li>
<li><strong>Data Processing:</strong> Cloudflare Worker validates code and triggers Power Automate</li>
<li><strong>SharePoint Update:</strong> Application data stored in EPC Onboarding list</li>
<li><strong>Status Tracking:</strong> Invitation marked as used, preventing duplicate applications</li>
</ol>

<h2>Security Features</h2>
<ul>
<li>✅ Unique 8-character invitation codes (avoiding confusing characters)</li>
<li>✅ Single-use codes prevent duplicate submissions</li>
<li>✅ 30-day expiration on invitation codes</li>
<li>✅ Certificate-based authentication for automation</li>
<li>✅ Audit trail in SharePoint for all activities</li>
</ul>

<h3>Integration Points</h3>
<p>The system integrates with Microsoft 365, Azure AD, Power Platform, and Cloudflare to provide a seamless experience for both internal teams and external partners.</p>
"@
    
    Set-PnPClientSidePage -Identity $overviewPage -Publish
    Write-Host "  ✅ Created: System Overview" -ForegroundColor Green
    
    # Create Quick Start Guide Page
    Write-Host "Creating Quick Start Guide page..." -ForegroundColor Yellow
    
    Remove-PnPPage -Identity "Quick-Start-Guide" -Force -ErrorAction SilentlyContinue
    $quickStartPage = Add-PnPClientSidePage -Name "Quick-Start-Guide" -Title "Quick Start Guide" -LayoutType Article
    
    Add-PnPClientSideText -Page $quickStartPage -Text @"
<h1>Quick Start Guide</h1>
<p><strong>Get started with EPC partner management in just a few steps.</strong></p>

<h2>Creating Your First Invitation</h2>

<h3>Option 1: SharePoint Interface</h3>
<ol>
<li>Navigate to <a href="/sites/SaberEPCPartners/Lists/EPC%20Invitations">EPC Invitations List</a></li>
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

<h3>Option 2: PowerShell Script</h3>
<pre>
./create-invitation.ps1 -CompanyName "Partner Company Ltd" -ContactEmail "contact@partner.com" -ContactName "John Smith"
</pre>

<h2>Monitoring Applications</h2>
<ol>
<li>Go to <a href="/sites/SaberEPCPartners/Lists/EPC%20Onboarding">EPC Onboarding List</a></li>
<li>Use custom views:
<ul>
<li><strong>Active Applications:</strong> New submissions</li>
<li><strong>Pending Review:</strong> In review process</li>
<li><strong>Approved Partners:</strong> Completed onboarding</li>
</ul>
</li>
<li>Click any partner for detailed view</li>
</ol>

<h2>Common Tasks</h2>
<ul>
<li><strong>📧 Resend Invitation Email:</strong> Edit invitation → Set InvitationSent = No → Save</li>
<li><strong>🔍 Check Code Status:</strong> Filter invitations by Code column → View Used status</li>
<li><strong>📊 Export Partner Data:</strong> Select items → Export to Excel → Download</li>
<li><strong>⚡ Check Workflow Status:</strong> Power Automate → Run history → Review status</li>
</ul>

<h2>Tips for Success</h2>
<ul>
<li>✅ Always verify email addresses before sending invitations</li>
<li>✅ Monitor Power Automate for failed runs daily</li>
<li>✅ Archive expired invitations monthly</li>
<li>✅ Test with internal email addresses first</li>
<li>✅ Keep partner communication professional and timely</li>
</ul>
"@
    
    Set-PnPClientSidePage -Identity $quickStartPage -Publish
    Write-Host "  ✅ Created: Quick Start Guide" -ForegroundColor Green
    
    # Create Creating Invitations Page
    Write-Host "Creating Invitations Guide page..." -ForegroundColor Yellow
    
    Remove-PnPPage -Identity "Creating-Invitations" -Force -ErrorAction SilentlyContinue
    $invitationsPage = Add-PnPClientSidePage -Name "Creating-Invitations" -Title "Creating Invitations" -LayoutType Article
    
    Add-PnPClientSideText -Page $invitationsPage -Text @"
<h1>Creating Invitations</h1>
<p><strong>Complete guide to creating and managing EPC partner invitations.</strong></p>

<h2>Methods for Creating Invitations</h2>

<h3>Method 1: SharePoint List (Recommended)</h3>
<ol>
<li>Navigate to <a href="/sites/SaberEPCPartners/Lists/EPC%20Invitations">EPC Invitations List</a></li>
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

<h3>Method 2: PowerShell Script</h3>
<p><strong>Single Invitation:</strong></p>
<pre>
./create-invitation.ps1 -CompanyName "Solar Excellence Ltd" -ContactEmail "john@solarexcellence.com" -ContactName "John Smith" -DaysValid 30 -SendEmail
</pre>

<p><strong>Batch Invitations:</strong></p>
<pre>
# Edit batch-create-invitations.ps1 with partner list
./batch-create-invitations.ps1
# Outputs CSV with all generated codes
</pre>

<h2>Invitation Code Format</h2>
<ul>
<li><strong>Length:</strong> 8 characters</li>
<li><strong>Characters:</strong> A-Z (except O, I) and 2-9 (except 0, 1)</li>
<li><strong>Example:</strong> ABCD2345, XYZW6789</li>
<li><strong>Purpose:</strong> Avoids confusion between similar characters</li>
</ul>

<h2>Managing Invitations</h2>

<h3>Checking Invitation Status</h3>
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

<h3>Common Actions</h3>
<ul>
<li><strong>Resend Email:</strong> Edit → Set InvitationSent = No → Save</li>
<li><strong>Extend Expiry:</strong> Edit → Update ExpiryDate → Save</li>
<li><strong>Cancel Invitation:</strong> Edit → Set Status = Cancelled → Save</li>
<li><strong>View Application:</strong> Check EPC Onboarding list for matching code</li>
</ul>

<h2>Best Practices</h2>
<ul>
<li>✅ Verify email addresses before sending</li>
<li>✅ Include partner's legal company name</li>
<li>✅ Add internal notes for context</li>
<li>✅ Monitor for bounced emails</li>
<li>✅ Follow up if no response within 7 days</li>
<li>✅ Archive expired invitations monthly</li>
</ul>

<p><strong>Pro Tip:</strong> Create test invitations with your own email first to verify the system is working correctly before sending to partners.</p>
"@
    
    Set-PnPClientSidePage -Identity $invitationsPage -Publish
    Write-Host "  ✅ Created: Creating Invitations" -ForegroundColor Green
    
    # Create Troubleshooting Guide Page
    Write-Host "Creating Troubleshooting Guide page..." -ForegroundColor Yellow
    
    Remove-PnPPage -Identity "Troubleshooting-Guide" -Force -ErrorAction SilentlyContinue
    $troublePage = Add-PnPClientSidePage -Name "Troubleshooting-Guide" -Title "Troubleshooting Guide" -LayoutType Article
    
    Add-PnPClientSideText -Page $troublePage -Text @"
<h1>Troubleshooting Guide</h1>
<p><strong>Quick solutions to common issues with the EPC Partner Management System.</strong></p>

<h2>Common Issues</h2>

<h3>Issue: Invitation Email Not Sent</h3>
<p><strong>Symptoms:</strong> Partner reports no email received</p>
<p><strong>Solutions:</strong></p>
<ol>
<li>Check Power Automate run history for errors</li>
<li>Verify email address is correct</li>
<li>Ask partner to check spam/junk folders</li>
<li>Manually resend: Edit invitation → Set InvitationSent = No → Save</li>
</ol>

<h3>Issue: Code Not Working on Portal</h3>
<p><strong>Symptoms:</strong> "Invalid or expired invitation code" error</p>
<p><strong>Solutions:</strong></p>
<ol>
<li>Verify code status in EPC Invitations list</li>
<li>Check: Used = No, ExpiryDate > Today</li>
<li>Ensure code is entered exactly (case-sensitive)</li>
<li>Create new invitation if expired</li>
</ol>

<h3>Issue: Application Not in SharePoint</h3>
<p><strong>Symptoms:</strong> Partner submitted but no entry in EPC Onboarding</p>
<p><strong>Solutions:</strong></p>
<ol>
<li>Check Power Automate "Application Processor" flow</li>
<li>Look for failed runs in history</li>
<li>Verify Cloudflare Worker is running</li>
<li>Create manual entry if needed</li>
</ol>

<h2>PowerShell Script Errors</h2>

<h3>Error: Certificate Authentication Failed</h3>
<pre>The specified certificate could not be read</pre>
<p><strong>Fix:</strong></p>
<ol>
<li>Verify certificate exists: Test-Path "~/.certs/SaberEPCAutomation.pfx"</li>
<li>Check password is correct: P@ssw0rd123!</li>
<li>Ensure certificate uploaded to Azure AD app</li>
</ol>

<h2>Power Automate Issues</h2>
<ul>
<li><strong>Flow not triggering:</strong> Ensure flow is ON, check connections valid</li>
<li><strong>HTTP 500 error:</strong> Verify JSON schema matches request format</li>
<li><strong>Email not sending:</strong> Check Office 365 connection, verify quotas</li>
</ul>

<h2>Quick Checks</h2>
<h3>Daily Health Checks</h3>
<ul>
<li>✅ Review Power Automate run history</li>
<li>✅ Check for pending invitations</li>
<li>✅ Monitor new applications</li>
<li>✅ Verify email delivery status</li>
</ul>

<h2>Emergency Procedures</h2>
<h3>System Complete Failure</h3>
<ol>
<li>Switch to manual process immediately</li>
<li>Document all invitations offline</li>
<li>Contact: sysadmin@saberrenewables.com</li>
<li>Check all components: SharePoint, Power Automate, Cloudflare</li>
</ol>

<h2>Support Escalation</h2>
<ol>
<li><strong>Level 1:</strong> Check this documentation</li>
<li><strong>Level 2:</strong> Contact sysadmin@saberrenewables.com (4-hour response)</li>
<li><strong>Level 3:</strong> Microsoft Support (SharePoint/Power Automate issues)</li>
<li><strong>Level 4:</strong> Development team for custom modifications</li>
</ol>

<h3>Prevention Tips</h3>
<ul>
<li>Archive expired invitations monthly</li>
<li>Test with internal emails first</li>
<li>Monitor system performance weekly</li>
<li>Keep documentation updated</li>
</ul>
"@
    
    Set-PnPClientSidePage -Identity $troublePage -Publish
    Write-Host "  ✅ Created: Troubleshooting Guide" -ForegroundColor Green
    
    Write-Host ""
    Write-Host "================================================" -ForegroundColor Cyan
    Write-Host "  Modern Pages Created Successfully!" -ForegroundColor Cyan
    Write-Host "================================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Pages created:" -ForegroundColor Green
    Write-Host "  ✅ EPC-Operations-Hub.aspx" -ForegroundColor White
    Write-Host "  ✅ System-Overview.aspx" -ForegroundColor White
    Write-Host "  ✅ Quick-Start-Guide.aspx" -ForegroundColor White
    Write-Host "  ✅ Creating-Invitations.aspx" -ForegroundColor White
    Write-Host "  ✅ Troubleshooting-Guide.aspx" -ForegroundColor White
    Write-Host ""
    Write-Host "To view the pages:" -ForegroundColor Yellow
    Write-Host "1. Go to: $SiteUrl/SitePages" -ForegroundColor White
    Write-Host "2. The pages should now have visible content" -ForegroundColor White
    Write-Host "3. Team members can edit pages directly in SharePoint" -ForegroundColor White
    Write-Host ""
    Write-Host "Page Features:" -ForegroundColor Yellow
    Write-Host "- Modern SharePoint page layout" -ForegroundColor Gray
    Write-Host "- Formatted text with headers and lists" -ForegroundColor Gray
    Write-Host "- Interactive links to lists and tools" -ForegroundColor Gray
    Write-Host "- Easy editing in SharePoint interface" -ForegroundColor Gray
    Write-Host ""
    
    Disconnect-PnPOnline
    
} catch {
    Write-Host "❌ Error: $_" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Modern pages creation complete!" -ForegroundColor Green
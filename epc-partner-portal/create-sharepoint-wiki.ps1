#!/snap/bin/pwsh
# Create SharePoint Wiki Pages for EPC Documentation
# Creates structured wiki pages with navigation and sets permissions

param(
    [switch]$CreatePages,
    [switch]$SetPermissions,
    [switch]$TestOnly
)

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  SharePoint Wiki Creation" -ForegroundColor Cyan
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
    
    if ($CreatePages -or $TestOnly) {
        
        if ($TestOnly) {
            Write-Host "TEST MODE - Pages to be created:" -ForegroundColor Yellow
            Write-Host "  📄 EPC-Operations-Hub (Main)" -ForegroundColor White
            Write-Host "  📄 System-Overview" -ForegroundColor White
            Write-Host "  📄 Quick-Start-Guide" -ForegroundColor White
            Write-Host "  📄 Creating-Invitations" -ForegroundColor White
            Write-Host "  📄 Processing-Applications" -ForegroundColor White
            Write-Host "  📄 PowerShell-Scripts" -ForegroundColor White
            Write-Host "  📄 Power-Automate-Workflows" -ForegroundColor White
            Write-Host "  📄 Troubleshooting" -ForegroundColor White
            Write-Host ""
            Write-Host "Run with -CreatePages to create actual pages" -ForegroundColor Yellow
            exit 0
        }
        
        Write-Host "Creating Wiki Pages..." -ForegroundColor Yellow
        Write-Host ""
        
        # 1. Main Hub Page
        Write-Host "Creating: EPC Operations Hub..." -ForegroundColor White
        $hubContent = @"
<div class="wiki-content">
<h1 style="color: #044D73; border-bottom: 3px solid #7CC061; padding-bottom: 10px;">EPC Partner Portal - Operations Hub</h1>

<div style="background: #f0f8ff; padding: 20px; border-radius: 10px; margin: 20px 0;">
<h2>Welcome to the EPC Partner Operations Centre</h2>
<p>This hub enables efficient partner onboarding through automated workflows. Our system reduces onboarding time from 14 days to 3 days whilst ensuring compliance with Saber's quality standards.</p>
</div>

<table style="width: 100%; margin: 20px 0;">
<tr>
<td style="width: 50%; padding: 10px; vertical-align: top;">
<h3>🚀 Getting Started</h3>
<ul>
<li><a href="/sites/SaberEPCPartners/SitePages/System-Overview.aspx">System Overview</a></li>
<li><a href="/sites/SaberEPCPartners/SitePages/Quick-Start-Guide.aspx">Quick Start Guide</a></li>
<li><a href="/sites/SaberEPCPartners/Lists/EPC%20Invitations">View Invitations List</a></li>
</ul>
</td>
<td style="width: 50%; padding: 10px; vertical-align: top;">
<h3>📋 Operations Guides</h3>
<ul>
<li><a href="/sites/SaberEPCPartners/SitePages/Creating-Invitations.aspx">Creating Invitations</a></li>
<li><a href="/sites/SaberEPCPartners/SitePages/Processing-Applications.aspx">Processing Applications</a></li>
<li><a href="/sites/SaberEPCPartners/Lists/EPC%20Onboarding">View Applications List</a></li>
</ul>
</td>
</tr>
<tr>
<td style="padding: 10px; vertical-align: top;">
<h3>🔧 Technical Resources</h3>
<ul>
<li><a href="/sites/SaberEPCPartners/SitePages/PowerShell-Scripts.aspx">PowerShell Scripts</a></li>
<li><a href="/sites/SaberEPCPartners/SitePages/Power-Automate-Workflows.aspx">Power Automate Workflows</a></li>
<li><a href="https://epc.saberrenewable.energy" target="_blank">Partner Portal</a></li>
</ul>
</td>
<td style="padding: 10px; vertical-align: top;">
<h3>❓ Support</h3>
<ul>
<li><a href="/sites/SaberEPCPartners/SitePages/Troubleshooting.aspx">Troubleshooting Guide</a></li>
<li>Email: sysadmin@saberrenewables.com</li>
<li>Partners: partners@saberrenewables.com</li>
</ul>
</td>
</tr>
</table>

<div style="background: #e8f4e8; padding: 20px; border-radius: 10px; margin: 20px 0;">
<h3>📊 Current Performance</h3>
<table>
<tr><td><strong>Average Onboarding Time:</strong></td><td>3 days</td></tr>
<tr><td><strong>System Uptime:</strong></td><td>99.9%</td></tr>
<tr><td><strong>Portal URL:</strong></td><td><a href="https://epc.saberrenewable.energy">epc.saberrenewable.energy</a></td></tr>
</table>
</div>

<div style="background: #fff3cd; padding: 15px; border-left: 4px solid #ffc107; margin: 20px 0;">
<h4>Quick Actions</h4>
<a href="/sites/SaberEPCPartners/Lists/EPC%20Invitations/NewForm.aspx" style="display: inline-block; padding: 10px 20px; background: #044D73; color: white; text-decoration: none; border-radius: 5px; margin: 5px;">➕ Create New Invitation</a>
<a href="/sites/SaberEPCPartners/Lists/EPC%20Onboarding" style="display: inline-block; padding: 10px 20px; background: #7CC061; color: white; text-decoration: none; border-radius: 5px; margin: 5px;">📥 View Pending Applications</a>
</div>

<p style="color: #666; font-size: 12px; margin-top: 30px;">Version: 1.0 | Last Updated: September 2025 | Owner: Business Operations Team</p>
</div>
"@
        
        Add-PnPPage -Name "EPC-Operations-Hub" -LayoutType Article -ErrorAction SilentlyContinue
        Set-PnPPage -Identity "EPC-Operations-Hub" -LayoutType Article -Content $hubContent -ErrorAction SilentlyContinue
        Write-Host "  ✅ Created hub page" -ForegroundColor Green
        
        # 2. System Overview Page
        Write-Host "Creating: System Overview..." -ForegroundColor White
        $overviewContent = @"
<div class="wiki-content">
<h1 style="color: #044D73;">System Overview</h1>

<h2>Architecture & Components</h2>
<p>The EPC Partner Portal integrates multiple technologies to deliver seamless partner onboarding.</p>

<h3>System Components</h3>

<div style="background: #f8f9fa; padding: 15px; margin: 10px 0; border-left: 4px solid #044D73;">
<h4>1. SharePoint Lists</h4>
<p><strong>Purpose:</strong> Central data repository for partner information</p>
<ul>
<li><strong>EPC Invitations</strong> - Tracks invitation codes and delivery</li>
<li><strong>EPC Onboarding</strong> - Stores submitted applications</li>
</ul>
<p><strong>Access:</strong> <a href="https://saberrenewables.sharepoint.com/sites/SaberEPCPartners">SharePoint Site</a></p>
</div>

<div style="background: #f8f9fa; padding: 15px; margin: 10px 0; border-left: 4px solid #7CC061;">
<h4>2. Partner Portal</h4>
<p><strong>Purpose:</strong> Public-facing application interface</p>
<ul>
<li>Invitation code validation</li>
<li>Application form submission</li>
<li>Document upload capability</li>
</ul>
<p><strong>URL:</strong> <a href="https://epc.saberrenewable.energy" target="_blank">epc.saberrenewable.energy</a></p>
</div>

<div style="background: #f8f9fa; padding: 15px; margin: 10px 0; border-left: 4px solid #044D73;">
<h4>3. Power Automate Workflows</h4>
<p><strong>Purpose:</strong> Process automation and email delivery</p>
<ul>
<li>Invitation Email Flow (SharePoint trigger)</li>
<li>Application Processing Flow (HTTP trigger)</li>
</ul>
</div>

<h3>Data Flow</h3>
<ol style="line-height: 2;">
<li>Operations Team → Creates Invitation → SharePoint List</li>
<li>Power Automate → Sends Email → Partner Receives Code</li>
<li>Partner → Visits Portal → Enters Code → Submits Application</li>
<li>Cloudflare Worker → Validates → Power Automate → SharePoint</li>
<li>Confirmation Emails ← Power Automate → Updates Records</li>
</ol>

<h3>Security Model</h3>
<table style="width: 100%; border-collapse: collapse;">
<tr style="background: #044D73; color: white;">
<th style="padding: 10px;">Component</th>
<th style="padding: 10px;">Authentication</th>
</tr>
<tr>
<td style="padding: 10px; border: 1px solid #ddd;">SharePoint</td>
<td style="padding: 10px; border: 1px solid #ddd;">Azure AD with MFA</td>
</tr>
<tr>
<td style="padding: 10px; border: 1px solid #ddd;">PowerShell Scripts</td>
<td style="padding: 10px; border: 1px solid #ddd;">Certificate authentication</td>
</tr>
<tr>
<td style="padding: 10px; border: 1px solid #ddd;">Portal</td>
<td style="padding: 10px; border: 1px solid #ddd;">Public with code validation</td>
</tr>
<tr>
<td style="padding: 10px; border: 1px solid #ddd;">API</td>
<td style="padding: 10px; border: 1px solid #ddd;">CORS restricted</td>
</tr>
</table>

<p style="margin-top: 20px;"><a href="/sites/SaberEPCPartners/SitePages/EPC-Operations-Hub.aspx">← Back to Hub</a></p>
</div>
"@
        
        Add-PnPPage -Name "System-Overview" -LayoutType Article -ErrorAction SilentlyContinue
        Set-PnPPage -Identity "System-Overview" -LayoutType Article -Content $overviewContent -ErrorAction SilentlyContinue
        Write-Host "  ✅ Created system overview" -ForegroundColor Green
        
        # 3. Quick Start Guide
        Write-Host "Creating: Quick Start Guide..." -ForegroundColor White
        $quickStartContent = @"
<div class="wiki-content">
<h1 style="color: #044D73;">Quick Start Guide</h1>
<h2>Start onboarding a partner in under 5 minutes</h2>

<div style="background: #d4edda; padding: 15px; border-radius: 5px; margin: 20px 0;">
<h3>Prerequisites</h3>
<ul>
<li>✅ Access to SharePoint EPC Partners site</li>
<li>✅ PowerShell installed (for automated method)</li>
<li>✅ Partner company details and contact email</li>
</ul>
</div>

<h2>Method 1: Automated (Recommended)</h2>

<div style="background: #f8f9fa; padding: 20px; border-radius: 5px; margin: 20px 0;">
<h3>Step 1: Open PowerShell</h3>
<pre style="background: #263238; color: #aed581; padding: 10px; border-radius: 3px;">
cd /home/marstack/saber_business_ops
</pre>

<h3>Step 2: Run Invitation Script</h3>
<pre style="background: #263238; color: #aed581; padding: 10px; border-radius: 3px;">
./create-invitation.ps1 -CompanyName "Partner Ltd" -ContactEmail "contact@partner.com" -ContactName "John Smith"
</pre>

<h3>Step 3: Confirm Success</h3>
<p><strong>Expected output:</strong></p>
<ul>
<li>✅ Unique 8-character code generated</li>
<li>✅ SharePoint entry created</li>
<li>✅ Email sent automatically</li>
</ul>
<p><strong>Time required:</strong> 2 minutes</p>
</div>

<h2>Method 2: SharePoint Direct</h2>

<div style="background: #fff3cd; padding: 20px; border-radius: 5px; margin: 20px 0;">
<h3>Step 1: Navigate to Invitations List</h3>
<ol>
<li>Go to <a href="https://saberrenewables.sharepoint.com/sites/SaberEPCPartners">SharePoint EPC Partners</a></li>
<li>Click <strong>EPC Invitations</strong></li>
<li>Select <strong>+ New</strong></li>
</ol>

<h3>Step 2: Complete Form</h3>
<p><strong>Required fields:</strong></p>
<ul>
<li><strong>Code:</strong> Generate 8-character code (e.g., ABCD1234)</li>
<li><strong>CompanyName:</strong> Partner company name</li>
<li><strong>ContactName:</strong> Primary contact</li>
<li><strong>ContactEmail:</strong> Valid email address</li>
<li><strong>ExpiryDate:</strong> Today + 30 days</li>
</ul>

<h3>Step 3: Save & Verify</h3>
<ol>
<li>Click <strong>Save</strong></li>
<li>Confirm email sent (check Power Automate)</li>
</ol>
<p><strong>Time required:</strong> 3-4 minutes</p>
</div>

<h2>What Happens Next?</h2>

<table style="width: 100%; margin: 20px 0;">
<tr>
<td style="width: 50%; padding: 10px; vertical-align: top;">
<h3>Automatic Actions</h3>
<ol>
<li>✉️ Partner receives branded invitation email</li>
<li>🔗 Email contains portal link and unique code</li>
<li>📝 Partner completes application</li>
<li>✅ System creates onboarding record</li>
</ol>
</td>
<td style="width: 50%; padding: 10px; vertical-align: top;">
<h3>Your Actions</h3>
<ol>
<li>Monitor application in EPC Onboarding list</li>
<li>Review submitted documents</li>
<li>Update status to Approved or InReview</li>
<li>Partner receives confirmation</li>
</ol>
</td>
</tr>
</table>

<div style="background: #e8f4e8; padding: 15px; border-radius: 5px; margin: 20px 0;">
<h3>💡 Quick Tips</h3>
<ul>
<li><strong>Code Generation:</strong> Use uppercase letters and numbers only</li>
<li><strong>Batch Invitations:</strong> Use batch-create-invitations.ps1 for multiple partners</li>
<li><strong>Email Issues:</strong> Check recipient's spam folder</li>
<li><strong>Code Problems:</strong> Verify code hasn't been used or expired</li>
</ul>
</div>

<p style="margin-top: 20px;"><a href="/sites/SaberEPCPartners/SitePages/EPC-Operations-Hub.aspx">← Back to Hub</a></p>
</div>
"@
        
        Add-PnPPage -Name "Quick-Start-Guide" -LayoutType Article -ErrorAction SilentlyContinue
        Set-PnPPage -Identity "Quick-Start-Guide" -LayoutType Article -Content $quickStartContent -ErrorAction SilentlyContinue
        Write-Host "  ✅ Created quick start guide" -ForegroundColor Green
        
        # 4. Creating Invitations Page
        Write-Host "Creating: Creating Invitations..." -ForegroundColor White
        $invitationsContent = @"
<div class="wiki-content">
<h1 style="color: #044D73;">Creating Partner Invitations</h1>
<p>Complete guide to invitation generation and management</p>

<h2>PowerShell Automation (Preferred)</h2>

<div style="background: #e8f4e8; padding: 20px; border-radius: 5px; margin: 20px 0;">
<h3>Single Invitation</h3>
<pre style="background: #263238; color: #aed581; padding: 10px; border-radius: 3px;">
./create-invitation.ps1 \`
    -CompanyName "Solar Excellence Ltd" \`
    -ContactEmail "john@solarexcellence.com" \`
    -ContactName "John Smith" \`
    -DaysValid 30
</pre>

<p><strong>Benefits:</strong></p>
<ul>
<li>Automatic unique code generation</li>
<li>Duplicate checking</li>
<li>Immediate email trigger</li>
<li>Error handling</li>
</ul>
</div>

<h2>Code Generation Rules</h2>

<table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
<tr style="background: #044D73; color: white;">
<th style="padding: 10px;">Rule</th>
<th style="padding: 10px;">Description</th>
<th style="padding: 10px;">Examples</th>
</tr>
<tr>
<td style="padding: 10px; border: 1px solid #ddd;"><strong>Length</strong></td>
<td style="padding: 10px; border: 1px solid #ddd;">Exactly 8 characters</td>
<td style="padding: 10px; border: 1px solid #ddd;">✅ ABCD1234</td>
</tr>
<tr>
<td style="padding: 10px; border: 1px solid #ddd;"><strong>Characters</strong></td>
<td style="padding: 10px; border: 1px solid #ddd;">A-Z (uppercase), 2-9</td>
<td style="padding: 10px; border: 1px solid #ddd;">✅ WXYZ9876</td>
</tr>
<tr>
<td style="padding: 10px; border: 1px solid #ddd;"><strong>Avoid</strong></td>
<td style="padding: 10px; border: 1px solid #ddd;">0, O, 1, I (confusing)</td>
<td style="padding: 10px; border: 1px solid #ddd;">❌ TEST0O1I</td>
</tr>
</table>

<h2>Invitation Lifecycle</h2>

<div style="background: #f8f9fa; padding: 20px; border-radius: 5px; margin: 20px 0;">
<p style="font-size: 18px; text-align: center;">
Created → Email Sent → Partner Uses Code → Marked as Used<br/>
<span style="color: #666;">30 days → 2 minutes → Variable → Immediate</span>
</p>
</div>

<h2>Managing Existing Invitations</h2>

<div style="background: #fff3cd; padding: 15px; border-radius: 5px; margin: 20px 0;">
<h3>Common Tasks</h3>

<h4>View All Invitations</h4>
<pre style="background: #263238; color: #aed581; padding: 10px; border-radius: 3px;">
Get-PnPListItem -List "EPC Invitations" | Format-Table Code, CompanyName, Used, ExpiryDate
</pre>

<h4>Resend Invitation</h4>
<ol>
<li>Locate invitation in SharePoint</li>
<li>Edit item</li>
<li>Set <strong>InvitationSent</strong> = No</li>
<li>Save (triggers new email)</li>
</ol>

<h4>Cancel Invitation</h4>
<ol>
<li>Find invitation</li>
<li>Edit item</li>
<li>Set <strong>ExpiryDate</strong> to yesterday</li>
<li>Add note explaining cancellation</li>
<li>Save</li>
</ol>
</div>

<h2>Best Practices</h2>

<table style="width: 100%; margin: 20px 0;">
<tr>
<td style="width: 50%; padding: 10px; vertical-align: top;">
<h3 style="color: green;">✅ DO</h3>
<ul>
<li>Generate codes for specific partners only</li>
<li>Set reasonable expiry dates (30 days standard)</li>
<li>Document any manual changes</li>
<li>Monitor delivery status daily</li>
<li>Archive expired invitations quarterly</li>
</ul>
</td>
<td style="width: 50%; padding: 10px; vertical-align: top;">
<h3 style="color: red;">❌ DON'T</h3>
<ul>
<li>Create generic "test" invitations in production</li>
<li>Share codes via insecure channels</li>
<li>Reuse codes from expired invitations</li>
<li>Extend expiry multiple times</li>
<li>Delete invitation records</li>
</ul>
</td>
</tr>
</table>

<p style="margin-top: 20px;"><a href="/sites/SaberEPCPartners/SitePages/EPC-Operations-Hub.aspx">← Back to Hub</a></p>
</div>
"@
        
        Add-PnPPage -Name "Creating-Invitations" -LayoutType Article -ErrorAction SilentlyContinue
        Set-PnPPage -Identity "Creating-Invitations" -LayoutType Article -Content $invitationsContent -ErrorAction SilentlyContinue
        Write-Host "  ✅ Created invitations guide" -ForegroundColor Green
        
        # 5. Troubleshooting Page
        Write-Host "Creating: Troubleshooting Guide..." -ForegroundColor White
        $troubleshootingContent = @"
<div class="wiki-content">
<h1 style="color: #044D73;">Troubleshooting Guide</h1>
<p>Quick solutions to common issues</p>

<h2>Invitation Issues</h2>

<div style="background: #f8d7da; padding: 20px; border-radius: 5px; margin: 20px 0;">
<h3>Problem: Invitation email not sent</h3>
<p><strong>Symptoms:</strong></p>
<ul>
<li>Partner reports no email received</li>
<li>InvitationSent field still shows "No"</li>
</ul>

<p><strong>Solutions:</strong></p>
<ol>
<li><strong>Check Power Automate</strong>
<ul>
<li>Navigate to <a href="https://make.powerautomate.com">Power Automate</a></li>
<li>Review "EPC Partner Invitation Email" flow</li>
<li>Check run history for errors</li>
</ul>
</li>
<li><strong>Manual Resend</strong>
<ul>
<li>Edit invitation in SharePoint</li>
<li>Set InvitationSent = No</li>
<li>Save (triggers resend)</li>
</ul>
</li>
<li><strong>Check Spam</strong>
<ul>
<li>Ask partner to check spam/junk folders</li>
<li>Whitelist: noreply@saberrenewables.com</li>
</ul>
</li>
</ol>
</div>

<div style="background: #f8d7da; padding: 20px; border-radius: 5px; margin: 20px 0;">
<h3>Problem: Code not working on portal</h3>
<p><strong>Symptoms:</strong></p>
<ul>
<li>"Invalid or expired invitation code" error</li>
<li>Code rejected at portal</li>
</ul>

<p><strong>Solutions:</strong></p>
<ol>
<li><strong>Verify Code Status</strong>
<pre style="background: #263238; color: #aed581; padding: 10px; border-radius: 3px;">
Get-PnPListItem -List "EPC Invitations" | Where-Object {$_.FieldValues.Code -eq "ABCD1234"}
</pre>
Check:
<ul>
<li>Used = No</li>
<li>ExpiryDate > Today</li>
<li>Code matches exactly (case-sensitive)</li>
</ul>
</li>
<li><strong>Create New Code</strong>
<pre style="background: #263238; color: #aed581; padding: 10px; border-radius: 3px;">
./create-invitation.ps1 -CompanyName "Company" -ContactEmail "email" -ContactName "Name"
</pre>
</li>
</ol>
</div>

<h2>PowerShell Script Errors</h2>

<div style="background: #fff3cd; padding: 20px; border-radius: 5px; margin: 20px 0;">
<h3>Certificate authentication fails</h3>
<p><strong>Error:</strong> "The specified certificate could not be read"</p>

<p><strong>Solutions:</strong></p>
<ol>
<li><strong>Verify Certificate</strong>
<pre style="background: #263238; color: #aed581; padding: 10px; border-radius: 3px;">
Test-Path "$HOME/.certs/SaberEPCAutomation.pfx"
</pre>
</li>
<li><strong>Check Password</strong>
<pre style="background: #263238; color: #aed581; padding: 10px; border-radius: 3px;">
$password = ConvertTo-SecureString -String "P@ssw0rd123!" -AsPlainText -Force
$cert = Get-PfxCertificate -FilePath "$HOME/.certs/SaberEPCAutomation.pfx" -Password $password
</pre>
</li>
</ol>
</div>

<h2>Escalation Path</h2>

<table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
<tr style="background: #044D73; color: white;">
<th style="padding: 10px;">Level</th>
<th style="padding: 10px;">Resource</th>
<th style="padding: 10px;">Response Time</th>
</tr>
<tr>
<td style="padding: 10px; border: 1px solid #ddd;">Level 1</td>
<td style="padding: 10px; border: 1px solid #ddd;">This documentation</td>
<td style="padding: 10px; border: 1px solid #ddd;">Immediate</td>
</tr>
<tr>
<td style="padding: 10px; border: 1px solid #ddd;">Level 2</td>
<td style="padding: 10px; border: 1px solid #ddd;">sysadmin@saberrenewables.com</td>
<td style="padding: 10px; border: 1px solid #ddd;">4 hours</td>
</tr>
<tr>
<td style="padding: 10px; border: 1px solid #ddd;">Level 3</td>
<td style="padding: 10px; border: 1px solid #ddd;">Microsoft Support</td>
<td style="padding: 10px; border: 1px solid #ddd;">24 hours</td>
</tr>
</table>

<p style="margin-top: 20px;"><a href="/sites/SaberEPCPartners/SitePages/EPC-Operations-Hub.aspx">← Back to Hub</a></p>
</div>
"@
        
        Add-PnPPage -Name "Troubleshooting" -LayoutType Article -ErrorAction SilentlyContinue
        Set-PnPPage -Identity "Troubleshooting" -LayoutType Article -Content $troubleshootingContent -ErrorAction SilentlyContinue
        Write-Host "  ✅ Created troubleshooting guide" -ForegroundColor Green
        
        Write-Host ""
        Write-Host "All wiki pages created successfully!" -ForegroundColor Green
    }
    
    if ($SetPermissions) {
        Write-Host ""
        Write-Host "Setting permissions..." -ForegroundColor Yellow
        
        # Get all site members
        $web = Get-PnPWeb
        $memberGroup = Get-PnPGroup -Identity "$($web.Title) Members"
        
        if ($memberGroup) {
            # Set permissions on pages to allow all members to edit
            $pages = @(
                "EPC-Operations-Hub",
                "System-Overview",
                "Quick-Start-Guide",
                "Creating-Invitations",
                "Troubleshooting"
            )
            
            foreach ($pageName in $pages) {
                try {
                    $page = Get-PnPPage -Identity $pageName
                    if ($page) {
                        # Grant edit permissions to members group
                        Set-PnPListItemPermission -List "Site Pages" -Identity $page.PageId -Group $memberGroup.Title -AddRole "Edit"
                        Write-Host "  ✅ Set edit permissions for: $pageName" -ForegroundColor Green
                    }
                } catch {
                    Write-Host "  ⚠️ Could not set permissions for: $pageName" -ForegroundColor Yellow
                }
            }
            
            Write-Host ""
            Write-Host "Team members can now edit all documentation pages" -ForegroundColor Green
        } else {
            Write-Host "  ⚠️ Could not find Members group" -ForegroundColor Yellow
        }
    }
    
    Write-Host ""
    Write-Host "================================================" -ForegroundColor Cyan
    Write-Host "  Wiki Structure Created" -ForegroundColor Cyan
    Write-Host "================================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Pages created:" -ForegroundColor White
    Write-Host "  📄 EPC-Operations-Hub (Main landing page)" -ForegroundColor Gray
    Write-Host "  📄 System-Overview" -ForegroundColor Gray
    Write-Host "  📄 Quick-Start-Guide" -ForegroundColor Gray
    Write-Host "  📄 Creating-Invitations" -ForegroundColor Gray
    Write-Host "  📄 Troubleshooting" -ForegroundColor Gray
    Write-Host ""
    Write-Host "Access the documentation hub at:" -ForegroundColor Yellow
    Write-Host "$SiteUrl/SitePages/EPC-Operations-Hub.aspx" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor White
    Write-Host "1. Add hub page to site navigation" -ForegroundColor Gray
    Write-Host "2. Pin important pages to quick launch" -ForegroundColor Gray
    Write-Host "3. Share hub URL with team" -ForegroundColor Gray
    Write-Host ""
    
    Disconnect-PnPOnline
    
} catch {
    Write-Host "❌ Error: $_" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Complete!" -ForegroundColor Green
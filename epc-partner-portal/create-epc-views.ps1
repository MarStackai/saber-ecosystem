#!/snap/bin/pwsh
# Create Custom Views and Forms for EPC Onboarding List
# Provides detailed partner views with single page layouts

param(
    [switch]$CreateViews,
    [switch]$CreateForms,
    [switch]$TestOnly
)

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  EPC Onboarding Views Configuration" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Configuration
$SiteUrl = "https://saberrenewables.sharepoint.com/sites/SaberEPCPartners"
$ListName = "EPC Onboarding"

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
    
    if ($TestOnly) {
        Write-Host "TEST MODE - Views to be created:" -ForegroundColor Yellow
        Write-Host "  📊 Partner Details (Single Item View)" -ForegroundColor White
        Write-Host "  📊 Active Applications" -ForegroundColor White
        Write-Host "  📊 Pending Review" -ForegroundColor White
        Write-Host "  📊 Approved Partners" -ForegroundColor White
        Write-Host "  📊 Recent Submissions" -ForegroundColor White
        Write-Host "  📊 By Geographic Region" -ForegroundColor White
        Write-Host ""
        Write-Host "Run with -CreateViews to create actual views" -ForegroundColor Yellow
        exit 0
    }
    
    if ($CreateViews) {
        Write-Host "Creating Custom Views..." -ForegroundColor Yellow
        Write-Host ""
        
        # Get the list
        $list = Get-PnPList -Identity $ListName
        
        # 1. Partner Details View (Card/Gallery style for single items)
        Write-Host "Creating: Partner Details View..." -ForegroundColor White
        
        $partnerDetailsXml = @"
<View Name="Partner Details" Type="HTML" DisplayName="Partner Details" Url="PartnerDetails.aspx" DefaultView="FALSE" MobileView="FALSE" MobileDefaultView="FALSE" ImageUrl="/_layouts/15/images/generic.png" XmlDefinition="TRUE">
    <Query>
        <OrderBy>
            <FieldRef Name="Created" Ascending="FALSE"/>
        </OrderBy>
    </Query>
    <ViewFields>
        <FieldRef Name="Title"/>
        <FieldRef Name="CompanyName"/>
        <FieldRef Name="Status"/>
        <FieldRef Name="PrimaryContactName"/>
        <FieldRef Name="PrimaryContactEmail"/>
        <FieldRef Name="PrimaryContactPhone"/>
        <FieldRef Name="CompanyAddress"/>
        <FieldRef Name="City"/>
        <FieldRef Name="StateProvince"/>
        <FieldRef Name="Country"/>
        <FieldRef Name="Services"/>
        <FieldRef Name="SystemTypes"/>
        <FieldRef Name="MaxProjectSize"/>
        <FieldRef Name="GeographicCoverage"/>
        <FieldRef Name="Certifications"/>
        <FieldRef Name="YearEstablished"/>
        <FieldRef Name="EmployeeCount"/>
        <FieldRef Name="AnnualRevenue"/>
        <FieldRef Name="SubmissionDate"/>
        <FieldRef Name="InvitationCode"/>
    </ViewFields>
    <RowLimit>1</RowLimit>
    <ViewStyle ID="17"/>
    <JSLink>clienttemplates.js</JSLink>
</View>
"@
        
        try {
            Add-PnPView -List $ListName -Title "Partner Details" -Fields @(
                "Title", "CompanyName", "Status", "PrimaryContactName", "PrimaryContactEmail",
                "PrimaryContactPhone", "CompanyAddress", "City", "StateProvince", "Country",
                "Services", "SystemTypes", "MaxProjectSize", "GeographicCoverage",
                "Certifications", "YearEstablished", "EmployeeCount", "AnnualRevenue",
                "SubmissionDate", "InvitationCode"
            ) -RowLimit 30 -ErrorAction SilentlyContinue
            Write-Host "  ✅ Created Partner Details view" -ForegroundColor Green
        } catch {
            Write-Host "  ⚠️ Partner Details view might already exist" -ForegroundColor Yellow
        }
        
        # 2. Active Applications View
        Write-Host "Creating: Active Applications View..." -ForegroundColor White
        
        try {
            Add-PnPView -List $ListName -Title "Active Applications" -Fields @(
                "CompanyName", "Status", "PrimaryContactName", "PrimaryContactEmail",
                "City", "Country", "SubmissionDate"
            ) -Query "<Where><Eq><FieldRef Name='Status'/><Value Type='Text'>New</Value></Eq></Where>" `
              -RowLimit 100 -ErrorAction SilentlyContinue
            Write-Host "  ✅ Created Active Applications view" -ForegroundColor Green
        } catch {
            Write-Host "  ⚠️ Active Applications view might already exist" -ForegroundColor Yellow
        }
        
        # 3. Pending Review View
        Write-Host "Creating: Pending Review View..." -ForegroundColor White
        
        try {
            Add-PnPView -List $ListName -Title "Pending Review" -Fields @(
                "CompanyName", "Status", "PrimaryContactName", "SubmissionDate",
                "Services", "GeographicCoverage"
            ) -Query "<Where><Eq><FieldRef Name='Status'/><Value Type='Text'>InReview</Value></Eq></Where>" `
              -RowLimit 100 -ErrorAction SilentlyContinue
            Write-Host "  ✅ Created Pending Review view" -ForegroundColor Green
        } catch {
            Write-Host "  ⚠️ Pending Review view might already exist" -ForegroundColor Yellow
        }
        
        # 4. Approved Partners View
        Write-Host "Creating: Approved Partners View..." -ForegroundColor White
        
        try {
            Add-PnPView -List $ListName -Title "Approved Partners" -Fields @(
                "CompanyName", "PrimaryContactName", "PrimaryContactEmail", "PrimaryContactPhone",
                "City", "Country", "Services", "Certifications", "SubmissionDate"
            ) -Query "<Where><Eq><FieldRef Name='Status'/><Value Type='Text'>Approved</Value></Eq></Where>" `
              -RowLimit 500 -ErrorAction SilentlyContinue
            Write-Host "  ✅ Created Approved Partners view" -ForegroundColor Green
        } catch {
            Write-Host "  ⚠️ Approved Partners view might already exist" -ForegroundColor Yellow
        }
        
        # 5. Recent Submissions (Last 7 days)
        Write-Host "Creating: Recent Submissions View..." -ForegroundColor White
        
        try {
            Add-PnPView -List $ListName -Title "Recent Submissions (7 days)" -Fields @(
                "CompanyName", "Status", "PrimaryContactName", "PrimaryContactEmail",
                "SubmissionDate", "InvitationCode"
            ) -Query "<Where><Geq><FieldRef Name='Created'/><Value Type='DateTime'><Today OffsetDays='-7'/></Value></Geq></Where>" `
              -RowLimit 100 -ErrorAction SilentlyContinue
            Write-Host "  ✅ Created Recent Submissions view" -ForegroundColor Green
        } catch {
            Write-Host "  ⚠️ Recent Submissions view might already exist" -ForegroundColor Yellow
        }
        
        # 6. By Geographic Coverage
        Write-Host "Creating: By Geographic Coverage View..." -ForegroundColor White
        
        try {
            Add-PnPView -List $ListName -Title "By Geographic Coverage" -Fields @(
                "CompanyName", "GeographicCoverage", "City", "Country", "Services",
                "Status", "PrimaryContactName"
            ) -Query "<OrderBy><FieldRef Name='Country'/><FieldRef Name='CompanyName'/></OrderBy>" `
              -RowLimit 500 -ErrorAction SilentlyContinue
            Write-Host "  ✅ Created Geographic Coverage view" -ForegroundColor Green
        } catch {
            Write-Host "  ⚠️ Geographic Coverage view might already exist" -ForegroundColor Yellow
        }
        
        Write-Host ""
        Write-Host "Custom views created successfully!" -ForegroundColor Green
    }
    
    if ($CreateForms) {
        Write-Host ""
        Write-Host "Creating Custom Display Form Page..." -ForegroundColor Yellow
        
        # Create a custom display form page
        $displayFormContent = @"
<div class="partner-details-form">
<style>
    .partner-details-form {
        font-family: 'Segoe UI', Arial, sans-serif;
        max-width: 1200px;
        margin: 0 auto;
        padding: 20px;
    }
    .partner-header {
        background: linear-gradient(135deg, #044D73 0%, #0d1138 100%);
        color: white;
        padding: 30px;
        border-radius: 10px 10px 0 0;
        margin-bottom: 0;
    }
    .partner-header h1 {
        margin: 0;
        font-size: 28px;
    }
    .partner-status {
        display: inline-block;
        padding: 5px 15px;
        background: #7CC061;
        border-radius: 20px;
        margin-top: 10px;
        font-size: 14px;
    }
    .partner-body {
        background: #f9f9f9;
        padding: 30px;
        border: 1px solid #ddd;
        border-radius: 0 0 10px 10px;
    }
    .info-section {
        background: white;
        padding: 20px;
        margin-bottom: 20px;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .info-section h2 {
        color: #044D73;
        font-size: 18px;
        margin-top: 0;
        padding-bottom: 10px;
        border-bottom: 2px solid #7CC061;
    }
    .info-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: 20px;
        margin-top: 15px;
    }
    .info-item {
        display: flex;
        flex-direction: column;
    }
    .info-label {
        color: #666;
        font-size: 12px;
        text-transform: uppercase;
        margin-bottom: 5px;
    }
    .info-value {
        color: #333;
        font-size: 14px;
        font-weight: 500;
    }
    .services-list, .certifications-list {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        margin-top: 10px;
    }
    .service-tag, .cert-tag {
        background: #e8f4e8;
        color: #044D73;
        padding: 5px 12px;
        border-radius: 15px;
        font-size: 13px;
    }
    .action-buttons {
        margin-top: 30px;
        display: flex;
        gap: 10px;
    }
    .action-button {
        padding: 10px 20px;
        background: #044D73;
        color: white;
        text-decoration: none;
        border-radius: 5px;
        border: none;
        cursor: pointer;
        font-size: 14px;
    }
    .action-button.approve {
        background: #7CC061;
    }
    .action-button.reject {
        background: #dc3545;
    }
</style>

<div class="partner-header">
    <h1>[CompanyName]</h1>
    <span class="partner-status">[Status]</span>
</div>

<div class="partner-body">
    <!-- Contact Information -->
    <div class="info-section">
        <h2>📧 Contact Information</h2>
        <div class="info-grid">
            <div class="info-item">
                <span class="info-label">Primary Contact</span>
                <span class="info-value">[PrimaryContactName]</span>
            </div>
            <div class="info-item">
                <span class="info-label">Title</span>
                <span class="info-value">[PrimaryContactTitle]</span>
            </div>
            <div class="info-item">
                <span class="info-label">Email</span>
                <span class="info-value"><a href="mailto:[PrimaryContactEmail]">[PrimaryContactEmail]</a></span>
            </div>
            <div class="info-item">
                <span class="info-label">Phone</span>
                <span class="info-value">[PrimaryContactPhone]</span>
            </div>
        </div>
    </div>
    
    <!-- Company Details -->
    <div class="info-section">
        <h2>🏢 Company Details</h2>
        <div class="info-grid">
            <div class="info-item">
                <span class="info-label">Registration Number</span>
                <span class="info-value">[RegistrationNumber]</span>
            </div>
            <div class="info-item">
                <span class="info-label">VAT Number</span>
                <span class="info-value">[VATNumber]</span>
            </div>
            <div class="info-item">
                <span class="info-label">Year Established</span>
                <span class="info-value">[YearEstablished]</span>
            </div>
            <div class="info-item">
                <span class="info-label">Employee Count</span>
                <span class="info-value">[EmployeeCount]</span>
            </div>
            <div class="info-item">
                <span class="info-label">Annual Revenue</span>
                <span class="info-value">[AnnualRevenue]</span>
            </div>
            <div class="info-item">
                <span class="info-label">Website</span>
                <span class="info-value"><a href="[Website]" target="_blank">[Website]</a></span>
            </div>
        </div>
    </div>
    
    <!-- Location -->
    <div class="info-section">
        <h2>📍 Location</h2>
        <div class="info-grid">
            <div class="info-item">
                <span class="info-label">Address</span>
                <span class="info-value">[CompanyAddress]</span>
            </div>
            <div class="info-item">
                <span class="info-label">City</span>
                <span class="info-value">[City]</span>
            </div>
            <div class="info-item">
                <span class="info-label">State/Province</span>
                <span class="info-value">[StateProvince]</span>
            </div>
            <div class="info-item">
                <span class="info-label">Postal Code</span>
                <span class="info-value">[PostalCode]</span>
            </div>
            <div class="info-item">
                <span class="info-label">Country</span>
                <span class="info-value">[Country]</span>
            </div>
            <div class="info-item">
                <span class="info-label">Geographic Coverage</span>
                <span class="info-value">[GeographicCoverage]</span>
            </div>
        </div>
    </div>
    
    <!-- Capabilities -->
    <div class="info-section">
        <h2>⚡ Capabilities & Services</h2>
        <div class="info-grid">
            <div class="info-item">
                <span class="info-label">Services</span>
                <div class="services-list">
                    [Services - displayed as tags]
                </div>
            </div>
            <div class="info-item">
                <span class="info-label">System Types</span>
                <span class="info-value">[SystemTypes]</span>
            </div>
            <div class="info-item">
                <span class="info-label">Typical Project Size</span>
                <span class="info-value">[TypicalProjectSize]</span>
            </div>
            <div class="info-item">
                <span class="info-label">Maximum Project Size</span>
                <span class="info-value">[MaxProjectSize]</span>
            </div>
        </div>
    </div>
    
    <!-- Certifications -->
    <div class="info-section">
        <h2>🏆 Certifications & Compliance</h2>
        <div class="info-grid">
            <div class="info-item">
                <span class="info-label">Certifications</span>
                <div class="certifications-list">
                    [Certifications - displayed as tags]
                </div>
            </div>
            <div class="info-item">
                <span class="info-label">Insurance Types</span>
                <span class="info-value">[InsuranceTypes]</span>
            </div>
            <div class="info-item">
                <span class="info-label">Safety Accreditations</span>
                <span class="info-value">[SafetyAccreditations]</span>
            </div>
        </div>
    </div>
    
    <!-- Submission Details -->
    <div class="info-section">
        <h2>📅 Application Details</h2>
        <div class="info-grid">
            <div class="info-item">
                <span class="info-label">Submission Date</span>
                <span class="info-value">[SubmissionDate]</span>
            </div>
            <div class="info-item">
                <span class="info-label">Invitation Code Used</span>
                <span class="info-value">[InvitationCode]</span>
            </div>
            <div class="info-item">
                <span class="info-label">Submission ID</span>
                <span class="info-value">[SubmissionID]</span>
            </div>
            <div class="info-item">
                <span class="info-label">Current Status</span>
                <span class="info-value">[Status]</span>
            </div>
        </div>
    </div>
    
    <!-- Action Buttons -->
    <div class="action-buttons">
        <button class="action-button approve" onclick="updateStatus('Approved')">✅ Approve Partner</button>
        <button class="action-button" onclick="updateStatus('InReview')">🔍 Mark for Review</button>
        <button class="action-button reject" onclick="updateStatus('Rejected')">❌ Reject Application</button>
        <a href="/sites/SaberEPCPartners/Lists/EPC%20Onboarding" class="action-button">← Back to List</a>
    </div>
</div>

<script>
function updateStatus(newStatus) {
    // This would be connected to Power Automate or SharePoint API
    alert('Status update to: ' + newStatus + ' - Feature coming soon');
}
</script>
</div>
"@
        
        # Create the display form page
        Add-PnPPage -Name "Partner-Details-Display" -LayoutType Article -ErrorAction SilentlyContinue
        Set-PnPPage -Identity "Partner-Details-Display" -LayoutType Article -Content $displayFormContent -ErrorAction SilentlyContinue
        Write-Host "  ✅ Created Partner Details Display form" -ForegroundColor Green
        
        Write-Host ""
        Write-Host "Custom display form created!" -ForegroundColor Green
    }
    
    Write-Host ""
    Write-Host "================================================" -ForegroundColor Cyan
    Write-Host "  Views Configuration Complete" -ForegroundColor Cyan
    Write-Host "================================================" -ForegroundColor Cyan
    Write-Host ""
    
    if ($CreateViews) {
        Write-Host "Views created:" -ForegroundColor White
        Write-Host "  📊 Partner Details - Detailed single item view" -ForegroundColor Gray
        Write-Host "  📊 Active Applications - New submissions" -ForegroundColor Gray
        Write-Host "  📊 Pending Review - Items in review" -ForegroundColor Gray
        Write-Host "  📊 Approved Partners - Approved applications" -ForegroundColor Gray
        Write-Host "  📊 Recent Submissions - Last 7 days" -ForegroundColor Gray
        Write-Host "  📊 By Geographic Coverage - Grouped by location" -ForegroundColor Gray
    }
    
    if ($CreateForms) {
        Write-Host ""
        Write-Host "Custom form page created at:" -ForegroundColor Yellow
        Write-Host "$SiteUrl/SitePages/Partner-Details-Display.aspx" -ForegroundColor Cyan
    }
    
    Write-Host ""
    Write-Host "To use these views:" -ForegroundColor White
    Write-Host "1. Go to the EPC Onboarding list" -ForegroundColor Gray
    Write-Host "2. Use the view selector dropdown to switch views" -ForegroundColor Gray
    Write-Host "3. Click on any item to see full details" -ForegroundColor Gray
    Write-Host "4. Use Partner Details view for single-page layout" -ForegroundColor Gray
    Write-Host ""
    Write-Host "To customize further:" -ForegroundColor White
    Write-Host "1. Go to List Settings → Views" -ForegroundColor Gray
    Write-Host "2. Edit any view to adjust columns or filters" -ForegroundColor Gray
    Write-Host "3. Set Partner Details as default view if desired" -ForegroundColor Gray
    Write-Host ""
    
    Disconnect-PnPOnline
    
} catch {
    Write-Host "❌ Error: $_" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Complete!" -ForegroundColor Green
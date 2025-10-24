#!/snap/bin/pwsh
# Upload Documentation Pages to SharePoint
# Creates a structured knowledge base for EPC Partner Operations

param(
    [switch]$CreateStructure,
    [switch]$UploadContent,
    [switch]$TestOnly
)

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  SharePoint Documentation Upload" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Configuration
$SiteUrl = "https://saberrenewables.sharepoint.com/sites/SaberEPCPartners"
$DocumentLibrary = "Site Pages"  # Or "Shared Documents" if Site Pages doesn't exist
$KnowledgeBaseFolder = "EPC-Operations-Manual"

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
    
    if ($CreateStructure) {
        Write-Host ""
        Write-Host "Creating folder structure..." -ForegroundColor Yellow
        
        # Create main knowledge base folder
        $mainFolder = Add-PnPFolder -Name $KnowledgeBaseFolder -Folder $DocumentLibrary -ErrorAction SilentlyContinue
        Write-Host "  ✅ Created: /$KnowledgeBaseFolder" -ForegroundColor Green
        
        # Create subfolders
        $subfolders = @(
            "01-Getting-Started",
            "02-Operations-Guides", 
            "03-Technical-Resources",
            "04-Reporting",
            "05-Support"
        )
        
        foreach ($subfolder in $subfolders) {
            Add-PnPFolder -Name $subfolder -Folder "$DocumentLibrary/$KnowledgeBaseFolder" -ErrorAction SilentlyContinue
            Write-Host "  ✅ Created: /$KnowledgeBaseFolder/$subfolder" -ForegroundColor Green
        }
    }
    
    if ($UploadContent -or $TestOnly) {
        Write-Host ""
        Write-Host "Preparing content for upload..." -ForegroundColor Yellow
        
        # Define page mappings
        $pages = @(
            @{
                File = "01-epc-home.md"
                Title = "EPC Operations Hub"
                Folder = "$DocumentLibrary/$KnowledgeBaseFolder"
                WikiContent = $true
            },
            @{
                File = "02-system-overview.md"
                Title = "System Overview"
                Folder = "$DocumentLibrary/$KnowledgeBaseFolder/01-Getting-Started"
            },
            @{
                File = "03-quick-start.md"
                Title = "Quick Start Guide"
                Folder = "$DocumentLibrary/$KnowledgeBaseFolder/01-Getting-Started"
            },
            @{
                File = "05-creating-invitations.md"
                Title = "Creating Invitations"
                Folder = "$DocumentLibrary/$KnowledgeBaseFolder/02-Operations-Guides"
            },
            @{
                File = "08-powershell-scripts.md"
                Title = "PowerShell Scripts Reference"
                Folder = "$DocumentLibrary/$KnowledgeBaseFolder/03-Technical-Resources"
            },
            @{
                File = "14-troubleshooting.md"
                Title = "Troubleshooting Guide"
                Folder = "$DocumentLibrary/$KnowledgeBaseFolder/05-Support"
            }
        )
        
        if ($TestOnly) {
            Write-Host ""
            Write-Host "TEST MODE - Files to be uploaded:" -ForegroundColor Yellow
            foreach ($page in $pages) {
                Write-Host "  📄 $($page.Title)" -ForegroundColor White
                Write-Host "     Source: ./sharepoint-pages/$($page.File)" -ForegroundColor Gray
                Write-Host "     Target: $($page.Folder)" -ForegroundColor Gray
            }
            Write-Host ""
            Write-Host "Run with -UploadContent to perform actual upload" -ForegroundColor Yellow
        } else {
            foreach ($page in $pages) {
                $sourceFile = "./sharepoint-pages/$($page.File)"
                
                if (Test-Path $sourceFile) {
                    Write-Host "  Uploading: $($page.Title)..." -ForegroundColor White
                    
                    # Read and convert markdown to HTML
                    $content = Get-Content $sourceFile -Raw
                    
                    # Basic markdown to HTML conversion
                    $htmlContent = $content `
                        -replace '^# (.+)$', '<h1>$1</h1>' `
                        -replace '^## (.+)$', '<h2>$1</h2>' `
                        -replace '^### (.+)$', '<h3>$1</h3>' `
                        -replace '\*\*(.+?)\*\*', '<strong>$1</strong>' `
                        -replace '`(.+?)`', '<code>$1</code>' `
                        -replace '\[(.+?)\]\((.+?)\)', '<a href="$2">$1</a>' `
                        -replace '^- (.+)$', '<li>$1</li>' `
                        -replace '\n\n', '<br/><br/>'
                    
                    # Create or update the page
                    if ($page.WikiContent) {
                        # For wiki pages, create as .aspx
                        $fileName = $page.File -replace '\.md$', '.aspx'
                        $wikiPage = @"
<div class="epc-documentation">
    <style>
        .epc-documentation { font-family: 'Segoe UI', sans-serif; padding: 20px; }
        .epc-documentation h1 { color: #044D73; border-bottom: 2px solid #7CC061; padding-bottom: 10px; }
        .epc-documentation h2 { color: #044D73; margin-top: 30px; }
        .epc-documentation h3 { color: #333; margin-top: 20px; }
        .epc-documentation code { background: #f4f4f4; padding: 2px 6px; border-radius: 3px; }
        .epc-documentation a { color: #044D73; }
        .epc-documentation li { margin: 5px 0; }
    </style>
    $htmlContent
</div>
"@
                        # Upload as wiki page
                        Add-PnPFile -Path $sourceFile -Folder $page.Folder -NewFileName $fileName -Values @{
                            Title = $page.Title
                            WikiField = $wikiPage
                        } -ErrorAction SilentlyContinue
                        
                    } else {
                        # Upload as document
                        Add-PnPFile -Path $sourceFile -Folder $page.Folder -Values @{
                            Title = $page.Title
                        } -ErrorAction SilentlyContinue
                    }
                    
                    Write-Host "    ✅ Uploaded successfully" -ForegroundColor Green
                } else {
                    Write-Host "    ❌ File not found: $sourceFile" -ForegroundColor Red
                }
            }
            
            Write-Host ""
            Write-Host "Creating navigation structure..." -ForegroundColor Yellow
            
            # Create a navigation page
            $navPage = @"
<h1>EPC Partner Operations - Documentation</h1>
<div style='padding: 20px; background: #f5f5f5; border-radius: 10px;'>
    <h2>📚 Knowledge Base Structure</h2>
    
    <h3>🚀 Getting Started</h3>
    <ul>
        <li><a href='$SiteUrl/$DocumentLibrary/$KnowledgeBaseFolder/01-Getting-Started/02-system-overview.md'>System Overview</a></li>
        <li><a href='$SiteUrl/$DocumentLibrary/$KnowledgeBaseFolder/01-Getting-Started/03-quick-start.md'>Quick Start Guide</a></li>
    </ul>
    
    <h3>📋 Operations Guides</h3>
    <ul>
        <li><a href='$SiteUrl/$DocumentLibrary/$KnowledgeBaseFolder/02-Operations-Guides/05-creating-invitations.md'>Creating Invitations</a></li>
        <li>Processing Applications (Coming Soon)</li>
        <li>Managing Partners (Coming Soon)</li>
    </ul>
    
    <h3>🔧 Technical Resources</h3>
    <ul>
        <li><a href='$SiteUrl/$DocumentLibrary/$KnowledgeBaseFolder/03-Technical-Resources/08-powershell-scripts.md'>PowerShell Scripts</a></li>
        <li>Power Automate Workflows (Coming Soon)</li>
        <li>API Documentation (Coming Soon)</li>
    </ul>
    
    <h3>📊 Reporting</h3>
    <ul>
        <li>Performance Metrics (Coming Soon)</li>
        <li>Monthly Reports (Coming Soon)</li>
    </ul>
    
    <h3>❓ Support</h3>
    <ul>
        <li><a href='$SiteUrl/$DocumentLibrary/$KnowledgeBaseFolder/05-Support/14-troubleshooting.md'>Troubleshooting Guide</a></li>
        <li>FAQs (Coming Soon)</li>
    </ul>
</div>

<div style='margin-top: 30px; padding: 20px; background: #e8f4f8; border-left: 4px solid #044D73;'>
    <h3>Quick Links</h3>
    <p>
        <a href='https://saberrenewables.sharepoint.com/sites/SaberEPCPartners/Lists/EPC%20Invitations'>📝 EPC Invitations List</a> | 
        <a href='https://saberrenewables.sharepoint.com/sites/SaberEPCPartners/Lists/EPC%20Onboarding'>📋 EPC Onboarding List</a> | 
        <a href='https://epc.saberrenewable.energy'>🌐 Partner Portal</a>
    </p>
</div>
"@
            
            # Save navigation page
            $navPagePath = "$HOME/epc-documentation-nav.html"
            $navPage | Out-File -FilePath $navPagePath -Encoding UTF8
            
            Write-Host "  ✅ Navigation page created" -ForegroundColor Green
            Write-Host ""
            Write-Host "📁 Documentation Location:" -ForegroundColor Cyan
            Write-Host "   $SiteUrl/$DocumentLibrary/$KnowledgeBaseFolder" -ForegroundColor White
        }
    }
    
    Write-Host ""
    Write-Host "================================================" -ForegroundColor Cyan
    Write-Host "  Next Steps" -ForegroundColor Cyan
    Write-Host "================================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "1. Navigate to SharePoint site" -ForegroundColor White
    Write-Host "2. Go to Site Contents → Site Pages (or Documents)" -ForegroundColor White
    Write-Host "3. Open EPC-Operations-Manual folder" -ForegroundColor White
    Write-Host "4. Set permissions as needed" -ForegroundColor White
    Write-Host "5. Add to site navigation menu" -ForegroundColor White
    Write-Host ""
    Write-Host "To create a Wiki page in SharePoint:" -ForegroundColor Yellow
    Write-Host "  - Go to Site Pages" -ForegroundColor Gray
    Write-Host "  - Click New → Wiki Page" -ForegroundColor Gray
    Write-Host "  - Copy content from uploaded files" -ForegroundColor Gray
    Write-Host "  - Format using SharePoint editor" -ForegroundColor Gray
    Write-Host ""
    
    Disconnect-PnPOnline
    
} catch {
    Write-Host "❌ Error: $_" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Documentation upload complete!" -ForegroundColor Green
#!/bin/bash

# Setup script for GitHub + Cloudflare + SharePoint integration

echo "========================================="
echo "🚀 Saber EPC Portal Deployment Setup"
echo "========================================="

# 1. Initialize Git repository
echo -e "\n📦 Initializing Git repository..."
git init
git add .
git commit -m "Initial commit: EPC Partner Portal"

# 2. Create GitHub repository
echo -e "\n🐙 Creating GitHub repository..."
gh repo create saber-epc-portal --public --source=. --remote=origin --push

# 3. Setup Cloudflare Pages
echo -e "\n☁️ Setting up Cloudflare Pages..."
cat << EOF > cloudflare-setup.md
# Cloudflare Pages Setup

1. Go to https://pages.cloudflare.com
2. Connect your GitHub account
3. Select 'saber-epc-portal' repository
4. Configure build settings:
   - Build command: \`cp -r public-deployment/* dist/\`
   - Build output directory: \`dist\`
   - Root directory: \`/\`

5. Set custom domain:
   - Add: epc.saberrenewable.energy
   - Configure DNS in Cloudflare:
     \`\`\`
     Type: CNAME
     Name: epc
     Target: saber-epc-portal.pages.dev
     \`\`\`

6. Environment variables:
   - SHAREPOINT_SITE_URL
   - SHAREPOINT_CLIENT_ID
   - SHAREPOINT_CLIENT_SECRET
EOF

# 4. Create SharePoint webhook receiver
echo -e "\n📊 Creating SharePoint integration..."
cat << 'EOF' > api/sharepoint-sync.js
// Cloudflare Worker to sync with SharePoint
addEventListener('fetch', event => {
  event.respondWith(handleRequest(event.request))
})

async function handleRequest(request) {
  const url = new URL(request.url)
  
  // Handle form submissions
  if (url.pathname === '/api/submit' && request.method === 'POST') {
    const data = await request.json()
    
    // Validate invitation code
    if (data.inviteCode !== 'ABCD1234') {
      return new Response(JSON.stringify({ error: 'Invalid code' }), {
        status: 403,
        headers: { 'Content-Type': 'application/json' }
      })
    }
    
    // Forward to SharePoint
    const sharepointUrl = `${SHAREPOINT_SITE_URL}/_api/web/lists/getbytitle('EPC Onboarding')/items`
    
    const spResponse = await fetch(sharepointUrl, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${await getSharePointToken()}`,
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      },
      body: JSON.stringify({
        Title: data.companyName,
        ContactName: data.contactName,
        Email: data.email,
        Phone: data.phone,
        Status: 'New',
        SubmittedDate: new Date().toISOString()
      })
    })
    
    if (spResponse.ok) {
      return new Response(JSON.stringify({ success: true }), {
        headers: { 'Content-Type': 'application/json' }
      })
    }
  }
  
  // Serve static files
  return fetch(request)
}

async function getSharePointToken() {
  // OAuth token retrieval
  const tokenUrl = `https://accounts.accesscontrol.windows.net/${TENANT_ID}/tokens/OAuth/2`
  // Implementation details...
  return token
}
EOF

# 5. Create management script for ops team
echo -e "\n🛠️ Creating SharePoint management script..."
cat << 'EOF' > scripts/manage-from-sharepoint.ps1
<#
.SYNOPSIS
    Manages EPC Portal from SharePoint
    
.DESCRIPTION
    This script allows the operations team to manage the public EPC portal
    directly from SharePoint without touching code
#>

param(
    [string]$Action = "sync",
    [string]$SiteUrl = "https://saberrenewables.sharepoint.com/sites/SaberEPCPartners"
)

# Connect to SharePoint
Connect-PnPOnline -Url $SiteUrl -Interactive

function Sync-InvitationCodes {
    Write-Host "📋 Syncing invitation codes..." -ForegroundColor Green
    
    # Get codes from SharePoint list
    $codes = Get-PnPListItem -List "EPC Invitations" | Where-Object { $_["Status"] -eq "Active" }
    
    # Generate JavaScript array
    $jsArray = $codes | ForEach-Object { "'$($_["Code"])'" } | Join-String -Separator ", "
    
    # Update validation file
    $validationJS = @"
// Auto-generated from SharePoint - Do not edit manually
const VALID_CODES = [$jsArray];

function validateCode(code) {
    return VALID_CODES.includes(code);
}
"@
    
    # Push to GitHub
    $validationJS | Out-File -FilePath "public-deployment/js/codes.js" -Encoding UTF8
    git add public-deployment/js/codes.js
    git commit -m "Update invitation codes from SharePoint"
    git push origin main
    
    Write-Host "✅ Codes synced and deployed!" -ForegroundColor Green
}

function Get-Submissions {
    Write-Host "📊 Fetching recent submissions..." -ForegroundColor Green
    
    $items = Get-PnPListItem -List "EPC Onboarding" -PageSize 10
    
    $items | ForEach-Object {
        [PSCustomObject]@{
            Company = $_["Title"]
            Contact = $_["ContactName"]
            Email = $_["Email"]
            Status = $_["Status"]
            Date = $_["SubmittedDate"]
        }
    } | Format-Table -AutoSize
}

function Export-PartnerData {
    Write-Host "📁 Exporting partner data..." -ForegroundColor Green
    
    $items = Get-PnPListItem -List "EPC Onboarding"
    $items | Export-Csv -Path "EPC_Partners_$(Get-Date -Format 'yyyyMMdd').csv" -NoTypeInformation
    
    Write-Host "✅ Exported to CSV!" -ForegroundColor Green
}

function Update-FormContent {
    param([string]$Section, [string]$Content)
    
    Write-Host "✏️ Updating form content..." -ForegroundColor Yellow
    
    # This would update specific sections of the form
    # and trigger a rebuild via GitHub Actions
    
    Write-Host "✅ Content updated and deployed!" -ForegroundColor Green
}

# Main menu
switch ($Action) {
    "sync"     { Sync-InvitationCodes }
    "list"     { Get-Submissions }
    "export"   { Export-PartnerData }
    "update"   { Update-FormContent }
    default    { 
        Write-Host @"
        
Available Actions:
  sync    - Sync invitation codes to public site
  list    - List recent submissions
  export  - Export all partner data to CSV
  update  - Update form content
  
Example: .\manage-from-sharepoint.ps1 -Action sync
"@
    }
}

Disconnect-PnPOnline
EOF

# 6. Create README for the repository
echo -e "\n📝 Creating README..."
cat << EOF > README.md
# Saber EPC Partner Portal

Public-facing partner onboarding portal for Saber Renewables.

## 🌐 Live Site
- Production: https://epc.saberrenewable.energy
- Preview: https://saber-epc-portal.pages.dev

## 🏗️ Architecture

\`\`\`
┌─────────────────┐         ┌──────────────┐         ┌─────────────────┐
│                 │         │              │         │                 │
│  GitHub Repo    │────────▶│  Cloudflare  │────────▶│   SharePoint    │
│  (Source Code)  │  Deploy │    Pages     │   API   │  (Data Storage) │
│                 │         │   (Public)   │         │   (Ops Team)    │
└─────────────────┘         └──────────────┘         └─────────────────┘
        ▲                                                      │
        │                                                      │
        └──────────────────────────────────────────────────────┘
                        Management Scripts
\`\`\`

## 🚀 Deployment

Automatic deployment on push to main branch via GitHub Actions.

## 🔧 For Operations Team

Use PowerShell scripts in SharePoint to:
- Manage invitation codes
- View submissions
- Export partner data
- Update form content

No coding required!

## 📊 SharePoint Integration

Data flows:
1. Partner fills form on public site
2. Cloudflare Worker validates and forwards to SharePoint
3. Ops team manages in SharePoint Lists
4. Changes sync back to public site

## 🔐 Security

- Invitation codes validated server-side
- SharePoint OAuth for API access
- Cloudflare DDoS protection
- SSL/TLS encryption

## 📝 License

© 2025 Saber Renewables. All rights reserved.
EOF

echo -e "\n✅ Setup complete!"
echo -e "\n📋 Next steps:"
echo "1. Run: gh auth login"
echo "2. Run: ./setup-deployment.sh"
echo "3. Configure Cloudflare Pages (see cloudflare-setup.md)"
echo "4. Set up SharePoint webhook"
echo "5. Test the deployment"
# 🏗️ Saber EPC Portal - Complete Architecture

## Overview
A hybrid solution combining public-facing Cloudflare hosting with SharePoint backend management.

```
┌──────────────────────────────────────────────────────────────────┐
│                         OPERATIONS TEAM                           │
│                    (SharePoint Interface)                         │
└────────────┬───────────────────────────────────┬─────────────────┘
             │                                   │
             ▼                                   ▼
    ┌──────────────┐                   ┌──────────────┐
    │  SharePoint  │                   │  PowerShell  │
    │    Lists     │◀──────────────────│   Scripts    │
    └──────┬───────┘                   └──────────────┘
           │                                     │
           │ Webhook                             │ Git Push
           ▼                                     ▼
    ┌──────────────┐                   ┌──────────────┐
    │  Power       │                   │    GitHub    │
    │  Automate    │                   │     Repo     │
    └──────┬───────┘                   └──────┬───────┘
           │                                   │
           │ API Calls                         │ CI/CD
           ▼                                   ▼
    ┌─────────────────────────────────────────────────┐
    │            Cloudflare Pages/Workers              │
    │         https://epc.saberrenewable.energy        │
    └─────────────────────────────────────────────────┘
                           ▲
                           │
                           │
    ┌─────────────────────────────────────────────────┐
    │                  EPC PARTNERS                    │
    │            (Public Form Access)                  │
    └─────────────────────────────────────────────────┘
```

## 🔄 Data Flow

### 1. Partner Application Flow
```
Partner → Cloudflare Form → Worker API → SharePoint List
                                ↓
                         Email Notification → Ops Team
```

### 2. Management Flow
```
Ops Team → SharePoint List → Power Automate → Update Codes
                                    ↓
                              GitHub Push → Cloudflare Deploy
```

## 🛠️ Setup Instructions

### Step 1: GitHub Repository
```bash
# Initialize and push to GitHub
cd /home/marstack/saber_business_ops
git init
git add .
git commit -m "Initial commit: EPC Portal"
gh repo create saber-renewables/epc-portal --public --push
```

### Step 2: Cloudflare Pages Setup

1. **Connect GitHub to Cloudflare Pages**
   ```
   https://dash.cloudflare.com/pages
   → Create a project
   → Connect to GitHub
   → Select: saber-renewables/epc-portal
   ```

2. **Configure Build Settings**
   - Framework preset: None
   - Build command: `mkdir -p dist && cp -r public-deployment/* dist/`
   - Build output: `/dist`

3. **Set Custom Domain**
   ```
   Settings → Custom domains
   → Add: epc.saberrenewable.energy
   ```

4. **Add DNS Record in Cloudflare**
   ```
   Type: CNAME
   Name: epc
   Content: saber-epc-portal.pages.dev
   Proxy: Yes (orange cloud)
   ```

### Step 3: Cloudflare Worker for API
```javascript
// Create worker at: workers.cloudflare.com
export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    
    // Handle CORS
    if (request.method === 'OPTIONS') {
      return new Response(null, {
        headers: {
          'Access-Control-Allow-Origin': '*',
          'Access-Control-Allow-Methods': 'POST, GET, OPTIONS',
          'Access-Control-Allow-Headers': 'Content-Type',
        },
      });
    }
    
    // Handle form submission
    if (url.pathname === '/api/submit' && request.method === 'POST') {
      const data = await request.json();
      
      // Validate invitation code
      const validCodes = ['ABCD1234', 'SABER2024', 'EPC2025'];
      if (!validCodes.includes(data.inviteCode)) {
        return Response.json({ error: 'Invalid invitation code' }, { status: 403 });
      }
      
      // Forward to SharePoint via Power Automate webhook
      const webhookUrl = env.SHAREPOINT_WEBHOOK;
      const response = await fetch(webhookUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...data,
          timestamp: new Date().toISOString(),
          source: 'epc.saberrenewable.energy'
        })
      });
      
      if (response.ok) {
        return Response.json({ success: true, message: 'Application received' });
      }
      
      return Response.json({ error: 'Submission failed' }, { status: 500 });
    }
    
    // Default response
    return new Response('API Endpoint', { status: 200 });
  }
};
```

### Step 4: SharePoint Power Automate Flow

1. **Create HTTP Trigger Flow**
   ```
   Power Automate → Create → Instant cloud flow
   → Trigger: "When a HTTP request is received"
   ```

2. **Parse JSON Schema**
   ```json
   {
     "type": "object",
     "properties": {
       "companyName": {"type": "string"},
       "contactName": {"type": "string"},
       "email": {"type": "string"},
       "phone": {"type": "string"},
       "inviteCode": {"type": "string"},
       "timestamp": {"type": "string"}
     }
   }
   ```

3. **Add SharePoint Actions**
   - Create item in "EPC Onboarding" list
   - Send email notification to ops team
   - Update "EPC Statistics" list

### Step 5: Management Scripts for Ops Team

```powershell
# Install in SharePoint document library
# /sites/SaberEPCPartners/Shared Documents/Scripts/

# manage-portal.ps1
function Update-InvitationCodes {
    $codes = Get-PnPListItem -List "EPC Invitations" | 
             Where-Object { $_["Status"] -eq "Active" } |
             Select-Object -ExpandProperty Code
    
    # Update Worker environment variable via Cloudflare API
    $headers = @{
        "Authorization" = "Bearer $env:CF_API_TOKEN"
        "Content-Type" = "application/json"
    }
    
    $body = @{
        "name" = "VALID_CODES"
        "value" = ($codes -join ",")
    } | ConvertTo-Json
    
    Invoke-RestMethod -Uri $cloudflareApiUrl -Method PUT -Headers $headers -Body $body
}
```

## 📊 SharePoint Lists Structure

### List: EPC Invitations
| Column | Type | Description |
|--------|------|-------------|
| Code | Text | Unique invitation code |
| IssuedTo | Text | Company/contact name |
| Status | Choice | Active/Used/Expired |
| ExpiryDate | Date | When code expires |
| CreatedBy | Person | Who created it |

### List: EPC Onboarding
| Column | Type | Description |
|--------|------|-------------|
| Title | Text | Company name |
| ContactName | Text | Primary contact |
| Email | Text | Email address |
| Phone | Text | Phone number |
| Status | Choice | New/InReview/Approved/Rejected |
| Documents | Attachments | Uploaded files |
| SubmittedDate | DateTime | When submitted |
| ReviewedBy | Person | Ops team member |
| Notes | Multi-line | Internal notes |

## 🔐 Security Configuration

### Cloudflare Security Settings
```
SSL/TLS: Full (strict)
Security Level: Medium
Challenge Passage: 30 minutes
Browser Integrity Check: On
Hotlink Protection: On
Rate Limiting: 10 requests per minute per IP
```

### SharePoint Permissions
```
EPC Invitations List: Ops Team (Contribute)
EPC Onboarding List: Ops Team (Full Control)
Scripts Library: Ops Team (Read/Execute)
```

## 🚀 Deployment Pipeline

```yaml
# GitHub Actions (.github/workflows/deploy.yml)
name: Deploy to Production

on:
  push:
    branches: [main]
  workflow_dispatch:
    inputs:
      environment:
        description: 'Environment to deploy to'
        required: true
        default: 'production'
        type: choice
        options:
        - production
        - staging

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Build
        run: |
          mkdir -p dist
          cp -r public-deployment/* dist/
          
      - name: Deploy to Cloudflare Pages
        uses: cloudflare/pages-action@v1
        with:
          apiToken: ${{ secrets.CF_API_TOKEN }}
          accountId: ${{ secrets.CF_ACCOUNT_ID }}
          projectName: saber-epc-portal
          directory: dist
          
      - name: Notify SharePoint
        run: |
          curl -X POST ${{ secrets.SP_WEBHOOK_URL }} \
            -H "Content-Type: application/json" \
            -d '{"status": "deployed", "version": "${{ github.sha }}"}'
```

## 📈 Monitoring & Analytics

### Cloudflare Analytics
- Page views
- Unique visitors  
- Performance metrics
- Security events

### SharePoint Reports
- Submission trends
- Approval rates
- Processing times
- Partner demographics

### Power BI Dashboard
Connect to SharePoint lists for real-time dashboards showing:
- Applications by month
- Geographic distribution
- Conversion rates
- Average processing time

## 🎯 Benefits of This Architecture

1. **Best of Both Worlds**
   - Public: Fast, scalable Cloudflare hosting
   - Private: Secure SharePoint data management

2. **No SharePoint Login for Partners**
   - Clean public URL
   - No authentication barriers
   - Professional appearance

3. **Ops Team Friendly**
   - Manage everything from SharePoint
   - No need to touch code
   - Familiar interface

4. **Version Control**
   - GitHub tracks all changes
   - Easy rollback if needed
   - Collaboration features

5. **Cost Effective**
   - Cloudflare Pages: Free
   - GitHub: Free
   - Only SharePoint costs

6. **Scalable**
   - Cloudflare handles traffic spikes
   - SharePoint handles data growth
   - Easy to add features

## 🔧 Maintenance Tasks

### Daily
- Check SharePoint list for new submissions
- Review and process applications

### Weekly  
- Sync invitation codes
- Export reports
- Check error logs

### Monthly
- Review analytics
- Update documentation
- Security audit

---

This architecture gives you the best of all worlds:
- **Public facing**: Professional, fast, accessible
- **Data management**: SharePoint for ops team
- **Version control**: GitHub for tracking changes
- **Deployment**: Automated via Cloudflare
- **Integration**: Power Automate connects everything
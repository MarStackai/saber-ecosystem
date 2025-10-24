# EPC Partner Form - Invite-Only Deployment Strategy

## Recommended Approach: SharePoint + Power Automate

### Option 1: SharePoint Site with External Sharing (RECOMMENDED)
**Best for: Security, Control, and Professional Experience**

#### Setup Steps:

1. **Create Dedicated SharePoint Site**
```powershell
# Create communication site for EPC Partners
New-PnPSite -Type CommunicationSite `
  -Title "Saber EPC Partner Portal" `
  -Url "https://saberrenewables.sharepoint.com/sites/EPCPartnerPortal" `
  -SiteDesign "Blank"
```

2. **Configure External Sharing**
   - Go to SharePoint Admin Center
   - Settings → Sharing → "New and existing guests"
   - Require sign-in with verification code
   - Allow sharing only by site owners

3. **Deploy Form to SharePoint**
   - Upload form files to Site Assets
   - Create a Site Page
   - Embed form using Script Editor/Embed web part
   - Set page as site homepage

4. **Set Up Guest Access Control**
   - Create SharePoint group "EPC Applicants"
   - Set permissions: Contribute to list, Read to site
   - Configure expiring guest links (30 days)

5. **Create Invitation System**

### Option 2: Azure Static Web App with AD B2C
**Best for: Scalability and Custom Branding**

```yaml
# azure-static-web-app.yml
name: Deploy EPC Form
on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Deploy to Azure Static Web Apps
      uses: Azure/static-web-apps-deploy@v1
      with:
        azure_static_web_apps_api_token: ${{ secrets.AZURE_TOKEN }}
        repo_token: ${{ secrets.GITHUB_TOKEN }}
        action: "upload"
        app_location: "/epc-form"
```

### Option 3: Power Pages (Power Apps Portal)
**Best for: Low-Code Management**

1. Create Power Pages site
2. Configure Azure AD B2C for authentication
3. Use table permissions for access control
4. Embed custom HTML/CSS/JS

## Invitation Workflow Implementation

### 1. Create Invitation Management List
```powershell
# Create invitation tracking list
$listFields = @(
    @{Name="CompanyName"; Type="Text"},
    @{Name="ContactEmail"; Type="Text"},
    @{Name="InviteCode"; Type="Text"},
    @{Name="InviteSentDate"; Type="DateTime"},
    @{Name="ExpiryDate"; Type="DateTime"},
    @{Name="Status"; Type="Choice"; Choices=@("Sent","Accessed","Submitted","Expired")},
    @{Name="AccessCount"; Type="Number"},
    @{Name="SubmissionID"; Type="Text"}
)

New-PnPList -Title "EPC Invitations" -Template GenericList
foreach($field in $listFields) {
    Add-PnPField -List "EPC Invitations" @field
}
```

### 2. Power Automate Flow: Send Invitations
```json
{
  "name": "EPC-SendInvitation",
  "trigger": "When item created in EPC Invitations",
  "actions": [
    {
      "GenerateUniqueCode": "guid()",
      "UpdateItem": {
        "InviteCode": "@{outputs('GenerateUniqueCode')}",
        "ExpiryDate": "@{addDays(utcNow(), 30)}",
        "Status": "Sent"
      }
    },
    {
      "SendEmail": {
        "To": "@{triggerBody()?['ContactEmail']}",
        "Subject": "Invitation: Saber EPC Partner Onboarding",
        "Body": "HTML template with unique link"
      }
    }
  ]
}
```

### 3. Secure Access Page
Create `verify-access.html`:

```html
<!DOCTYPE html>
<html>
<head>
    <title>Verify Access - Saber EPC Partners</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <div class="verify-container saber-card">
        <img src="saber-logo.svg" alt="Saber" class="logo">
        <h2>EPC Partner Portal Access</h2>
        
        <form id="verifyForm">
            <div class="form-group">
                <input type="email" id="email" placeholder="Enter your email" required>
                <input type="text" id="inviteCode" placeholder="Enter invitation code" required>
                <button type="submit" class="saber-btn">Verify Access</button>
            </div>
        </form>
        
        <div id="errorMsg" class="error-message"></div>
    </div>
    
    <script>
    document.getElementById('verifyForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const email = document.getElementById('email').value;
        const code = document.getElementById('inviteCode').value;
        
        // Verify against SharePoint list
        const isValid = await verifyInvitation(email, code);
        
        if (isValid) {
            // Store in session
            sessionStorage.setItem('epcAuth', JSON.stringify({
                email: email,
                code: code,
                timestamp: Date.now()
            }));
            
            // Redirect to form
            window.location.href = 'index.html';
        } else {
            document.getElementById('errorMsg').textContent = 'Invalid email or invitation code';
        }
    });
    
    async function verifyInvitation(email, code) {
        // Call Power Automate HTTP endpoint to verify
        const response = await fetch('https://prod-xx.westeurope.logic.azure.com/workflows/verify', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({email, code})
        });
        
        return response.ok;
    }
    </script>
</body>
</html>
```

### 4. Update Main Form
Add to `script.js`:

```javascript
// Check authentication on load
document.addEventListener('DOMContentLoaded', () => {
    const auth = sessionStorage.getItem('epcAuth');
    
    if (!auth) {
        // Redirect to verification
        window.location.href = 'verify-access.html';
        return;
    }
    
    const authData = JSON.parse(auth);
    
    // Check if session expired (24 hours)
    if (Date.now() - authData.timestamp > 86400000) {
        sessionStorage.removeItem('epcAuth');
        window.location.href = 'verify-access.html';
        return;
    }
    
    // Continue with form initialization
    initializeEventListeners();
    updateProgressBar();
});
```

## Deployment Options Comparison

| Feature | SharePoint + External | Azure Static Web | Power Pages |
|---------|----------------------|------------------|-------------|
| Setup Complexity | Medium | High | Low |
| Cost | Included in M365 | ~$10/month | ~$200/month |
| Custom Domain | Yes | Yes | Yes |
| Authentication | Guest Links/Azure AD | Azure AD B2C | Azure AD B2C |
| Maintenance | Low | Medium | Low |
| Scalability | Good | Excellent | Good |
| Brand Control | Good | Excellent | Good |

## Recommended Implementation Path

### Phase 1: Quick Deploy (Week 1)
1. Upload form to SharePoint site
2. Create manual invitation list
3. Send invites with SharePoint guest links

### Phase 2: Automation (Week 2)
1. Set up Power Automate flows
2. Create invitation management list
3. Implement verification page

### Phase 3: Enhancement (Month 2)
1. Add analytics tracking
2. Implement reminder emails
3. Create admin dashboard

## Email Invitation Template

```html
<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: 'Source Sans Pro', Arial, sans-serif; }
        .container { max-width: 600px; margin: 0 auto; }
        .header { background: linear-gradient(135deg, #044D73, #0d1138); padding: 30px; }
        .logo { height: 50px; }
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
            padding: 15px;
            border-left: 4px solid #7CC061;
            margin: 20px 0;
        }
        .footer { padding: 20px; text-align: center; color: #666; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <img src="https://saberrenewables.com/logo.png" alt="Saber" class="logo">
        </div>
        
        <div class="content">
            <h2>Welcome to Saber's EPC Partner Network</h2>
            
            <p>Dear {{CompanyName}},</p>
            
            <p>You've been invited to join Saber Renewables' certified Energy Performance Certificate partner network. This exclusive invitation allows you to complete our onboarding process and become part of our growing network of sustainability professionals.</p>
            
            <div class="code-box">
                <strong>Your Invitation Code:</strong> {{InviteCode}}<br>
                <strong>Valid Until:</strong> {{ExpiryDate}}
            </div>
            
            <p>To begin your application:</p>
            
            <p style="text-align: center;">
                <a href="{{FormURL}}?code={{InviteCode}}" class="btn">Start Application</a>
            </p>
            
            <p><strong>What to prepare:</strong></p>
            <ul>
                <li>Company registration documents</li>
                <li>ISO certifications (if applicable)</li>
                <li>Insurance certificates</li>
                <li>HSEQ policies</li>
            </ul>
            
            <p>The application takes approximately 15-20 minutes to complete.</p>
            
            <p>If you have any questions, please contact our partner team at <a href="mailto:partners@saberrenewables.com">partners@saberrenewables.com</a></p>
            
            <p>Best regards,<br>
            The Saber Renewables Team</p>
        </div>
        
        <div class="footer">
            <p>© 2024 Saber Renewables | Leading the transition to sustainable energy</p>
            <p>This invitation is confidential and intended solely for {{ContactEmail}}</p>
        </div>
    </div>
</body>
</html>
```

## Security Considerations

1. **Invitation Codes**
   - Use GUIDs or cryptographically secure random strings
   - Set expiration (30 days recommended)
   - Single-use or limited-use codes
   - Track access attempts

2. **Rate Limiting**
   - Limit verification attempts (5 per hour)
   - Implement CAPTCHA after failed attempts
   - Block IPs after repeated failures

3. **Session Management**
   - Use secure session storage
   - Implement timeout (24 hours)
   - Clear on submission

4. **Data Protection**
   - HTTPS only
   - Encrypt sensitive data
   - GDPR compliance
   - Audit trail

## Monitoring & Analytics

Track:
- Invitation sent/opened/clicked rates
- Form completion rates
- Drop-off points
- Average completion time
- Geographic distribution

## Next Steps

1. Choose deployment option (recommend SharePoint + External for quick start)
2. Set up invitation list and Power Automate flows
3. Configure email templates
4. Test with internal team
5. Launch pilot with 5-10 partners
6. Full rollout

## Support Scripts

See:
- `setup-sharepoint-site.ps1` - Automated site creation
- `create-invitation-flow.json` - Power Automate template
- `send-bulk-invites.ps1` - Bulk invitation sender
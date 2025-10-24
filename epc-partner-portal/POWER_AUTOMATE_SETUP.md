# 🔗 Power Automate Setup for EPC Portal

## Overview
Connect the EPC portal at `epc.saberrenewable.energy` to SharePoint Lists via Power Automate

## Step 1: Create SharePoint Lists

### List 1: EPC Invitations
Go to SharePoint site: https://saberrenewables.sharepoint.com/sites/SaberEPCPartners

Create new list with these columns:
| Column Name | Type | Required | Notes |
|------------|------|----------|-------|
| Title | Single line | Yes | Invitation code (e.g., ABCD1234) |
| IssuedTo | Single line | No | Company/contact name |
| Email | Single line | No | Contact email |
| Status | Choice | Yes | Active, Used, Expired |
| UsedDate | Date/Time | No | When code was used |
| ExpiryDate | Date/Time | No | When code expires |
| Notes | Multi-line | No | Internal notes |

### List 2: EPC Onboarding
Create list with these columns:
| Column Name | Type | Required | Notes |
|------------|------|----------|-------|
| Title | Single line | Yes | Company name |
| RegistrationNumber | Single line | Yes | Company registration |
| ContactName | Single line | Yes | Primary contact |
| ContactTitle | Single line | Yes | Contact's title |
| Email | Single line | Yes | Email address |
| Phone | Single line | Yes | Phone number |
| Address | Multi-line | Yes | Business address |
| Services | Multi-line | No | EPC services offered |
| YearsExperience | Number | Yes | Years in business |
| TeamSize | Number | Yes | Team size |
| Coverage | Multi-line | Yes | Geographic coverage |
| Certifications | Multi-line | No | Certifications held |
| InvitationCode | Single line | Yes | Code used |
| SubmissionDate | Date/Time | Yes | When submitted |
| Status | Choice | Yes | New, InReview, Approved, Rejected |
| ReviewedBy | Person | No | Who reviewed |
| ReviewDate | Date/Time | No | When reviewed |
| Notes | Multi-line | No | Internal notes |

## Step 2: Create Power Automate Flow

### 2.1 Go to Power Automate
1. Navigate to: https://make.powerautomate.com
2. Click **"Create"** → **"Instant cloud flow"**
3. Name it: **"EPC Portal Submission Handler"**
4. Choose trigger: **"When a HTTP request is received"**
5. Click **Create**

### 2.2 Configure HTTP Trigger
In the trigger, set the Request Body JSON Schema:
```json
{
  "type": "object",
  "properties": {
    "invitationCode": {
      "type": "string"
    },
    "companyName": {
      "type": "string"
    },
    "registrationNumber": {
      "type": "string"
    },
    "contactName": {
      "type": "string"
    },
    "contactTitle": {
      "type": "string"
    },
    "email": {
      "type": "string"
    },
    "phone": {
      "type": "string"
    },
    "address": {
      "type": "string"
    },
    "services": {
      "type": "array",
      "items": {
        "type": "string"
      }
    },
    "yearsExperience": {
      "type": "number"
    },
    "teamSize": {
      "type": "number"
    },
    "coverage": {
      "type": "string"
    },
    "certifications": {
      "type": "string"
    },
    "timestamp": {
      "type": "string"
    },
    "source": {
      "type": "string"
    }
  },
  "required": [
    "invitationCode",
    "companyName",
    "email"
  ]
}
```

### 2.3 Add Actions to Flow

#### Action 1: Validate Invitation Code
1. Add action: **"Get items"** (SharePoint)
2. Site: SaberEPCPartners
3. List: EPC Invitations
4. Filter Query: `Title eq '@{triggerBody()?['invitationCode']}' and Status eq 'Active'`

#### Action 2: Condition - Check if Code Valid
1. Add **"Condition"** action
2. Check if: `length(outputs('Get_items')?['value'])` is greater than 0

#### If Yes Branch:

##### Action 3: Create SharePoint Item
1. Add action: **"Create item"** (SharePoint)
2. Site: SaberEPCPartners
3. List: EPC Onboarding
4. Map fields:
   - Title: `@{triggerBody()?['companyName']}`
   - RegistrationNumber: `@{triggerBody()?['registrationNumber']}`
   - ContactName: `@{triggerBody()?['contactName']}`
   - ContactTitle: `@{triggerBody()?['contactTitle']}`
   - Email: `@{triggerBody()?['email']}`
   - Phone: `@{triggerBody()?['phone']}`
   - Address: `@{triggerBody()?['address']}`
   - Services: `@{join(triggerBody()?['services'], ', ')}`
   - YearsExperience: `@{triggerBody()?['yearsExperience']}`
   - TeamSize: `@{triggerBody()?['teamSize']}`
   - Coverage: `@{triggerBody()?['coverage']}`
   - Certifications: `@{triggerBody()?['certifications']}`
   - InvitationCode: `@{triggerBody()?['invitationCode']}`
   - SubmissionDate: `@{utcNow()}`
   - Status: `New`

##### Action 4: Update Invitation Code Status
1. Add action: **"Update item"** (SharePoint)
2. Site: SaberEPCPartners
3. List: EPC Invitations
4. Id: `@{first(outputs('Get_items')?['value'])?['ID']}`
5. Status: `Used`
6. UsedDate: `@{utcNow()}`

##### Action 5: Send Confirmation Email
1. Add action: **"Send an email (V2)"** (Outlook)
2. To: `@{triggerBody()?['email']}`
3. Subject: `EPC Partner Application Received - Saber Renewables`
4. Body:
```html
<p>Dear @{triggerBody()?['contactName']},</p>

<p>Thank you for submitting your EPC Partner application to Saber Renewables.</p>

<p><strong>Application Details:</strong></p>
<ul>
  <li>Company: @{triggerBody()?['companyName']}</li>
  <li>Submission Date: @{utcNow()}</li>
  <li>Reference Code: @{triggerBody()?['invitationCode']}</li>
</ul>

<p>Our team will review your application within 2-3 business days. You will receive an email once the review is complete.</p>

<p>Best regards,<br>
Saber Renewables Partner Team</p>
```

##### Action 6: Send Notification to Team
1. Add action: **"Send an email (V2)"** (Outlook)
2. To: `partners@saberrenewables.com`
3. Subject: `New EPC Partner Application: @{triggerBody()?['companyName']}`
4. Body: Include all submission details

##### Action 7: Response - Success
1. Add action: **"Response"** (Request)
2. Status Code: `200`
3. Body:
```json
{
  "success": true,
  "message": "Application submitted successfully",
  "referenceNumber": "@{outputs('Create_item')?['ID']}"
}
```

#### If No Branch (Invalid Code):

##### Action 8: Response - Invalid Code
1. Add action: **"Response"** (Request)
2. Status Code: `403`
3. Body:
```json
{
  "success": false,
  "message": "Invalid or expired invitation code"
}
```

### 2.4 Save and Get Webhook URL
1. Click **Save**
2. The HTTP trigger will generate a URL
3. Copy the **HTTP POST URL** - it looks like:
```
https://prod-xx.westus.logic.azure.com:443/workflows/xxxxx/triggers/manual/paths/invoke?api-version=2016-10-01&sp=%2Ftriggers%2Fmanual%2Frun&sv=1.0&sig=xxxxx
```

## Step 3: Create Cloudflare Worker

### 3.1 Create Worker Script
Create file: `/home/marstack/saber_business_ops/worker.js`

```javascript
export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    
    // CORS headers
    const corsHeaders = {
      'Access-Control-Allow-Origin': 'https://epc.saberrenewable.energy',
      'Access-Control-Allow-Methods': 'POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type',
    };
    
    // Handle preflight
    if (request.method === 'OPTIONS') {
      return new Response(null, { headers: corsHeaders });
    }
    
    // Handle form submission
    if (url.pathname === '/api/submit' && request.method === 'POST') {
      try {
        const data = await request.json();
        
        // Add metadata
        data.timestamp = new Date().toISOString();
        data.source = 'epc.saberrenewable.energy';
        
        // Forward to Power Automate
        const powerAutomateUrl = env.POWER_AUTOMATE_WEBHOOK;
        
        const response = await fetch(powerAutomateUrl, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(data),
        });
        
        const result = await response.json();
        
        return new Response(JSON.stringify(result), {
          status: response.status,
          headers: {
            ...corsHeaders,
            'Content-Type': 'application/json',
          },
        });
      } catch (error) {
        return new Response(
          JSON.stringify({ 
            success: false, 
            message: 'Server error' 
          }),
          { 
            status: 500,
            headers: {
              ...corsHeaders,
              'Content-Type': 'application/json',
            },
          }
        );
      }
    }
    
    // Default response
    return new Response('EPC Portal API', { status: 200 });
  },
};
```

### 3.2 Deploy Worker
```bash
cd /home/marstack/saber_business_ops

# Create wrangler.toml
cat > wrangler.toml << EOF
name = "epc-portal-api"
main = "worker.js"
compatibility_date = "2024-01-01"

[vars]
# Add your Power Automate webhook URL here
POWER_AUTOMATE_WEBHOOK = "YOUR_WEBHOOK_URL_HERE"

[[routes]]
pattern = "epc.saberrenewable.energy/api/*"
zone_name = "saberrenewable.energy"
EOF

# Deploy
wrangler deploy
```

## Step 4: Update Form JavaScript

Update the form to use the API endpoint:

```javascript
// In your form submission handler
async function submitForm(formData) {
  try {
    const response = await fetch('https://epc.saberrenewable.energy/api/submit', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(formData),
    });
    
    const result = await response.json();
    
    if (result.success) {
      // Show success message
      alert('Application submitted successfully!');
      // Clear form
      document.getElementById('epcForm').reset();
    } else {
      alert('Error: ' + result.message);
    }
  } catch (error) {
    console.error('Submission error:', error);
    alert('Failed to submit form. Please try again.');
  }
}
```

## Step 5: Test the Integration

### Test Invitation Codes
Add test codes to SharePoint EPC Invitations list:
- Code: `ABCD1234`, Status: `Active`
- Code: `TEST2024`, Status: `Active`
- Code: `DEMO2024`, Status: `Active`

### Test Submission
1. Go to: https://epc.saberrenewable.energy/epc/apply.html
2. Enter test code: `ABCD1234`
3. Fill out form
4. Submit
5. Check:
   - SharePoint list for new entry
   - Email confirmation sent
   - Code marked as "Used"

## Monitoring & Maintenance

### View Flow Runs
1. Go to Power Automate
2. Click on your flow
3. View run history
4. Check for failures

### Common Issues
- **403 Error**: Invalid invitation code
- **500 Error**: Power Automate flow failed
- **CORS Error**: Check Worker CORS headers
- **No Response**: Check webhook URL in Worker

### Update Invitation Codes
1. Go to SharePoint EPC Invitations list
2. Add new item with:
   - Title: New code
   - Status: Active
   - ExpiryDate: Future date

## Security Notes

1. **Webhook URL**: Keep the Power Automate webhook URL secret
2. **Rate Limiting**: Consider adding rate limiting in Worker
3. **Validation**: Validate all inputs in Power Automate
4. **Monitoring**: Set up alerts for failed submissions

---

## Quick Reference

- **SharePoint Site**: https://saberrenewables.sharepoint.com/sites/SaberEPCPartners
- **Power Automate**: https://make.powerautomate.com
- **Test Portal**: https://epc.saberrenewable.energy
- **Test Code**: ABCD1234

Ready to implement!
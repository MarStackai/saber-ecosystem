# Power Automate - EPC Application Submission Processing Flow

## Flow Overview
This flow processes new EPC partner applications when they're submitted through the web portal and creates the corresponding SharePoint entries.

## Step-by-Step Setup

### 1. Create New Flow
1. Go to https://make.powerautomate.com
2. Click **+ Create** → **Instant cloud flow**
3. Name: `EPC Application Submission Processor`
4. Choose trigger: **When an HTTP request is received**

### 2. Configure HTTP Trigger

**When a HTTP request is received**

Request Body JSON Schema:
```json
{
  "type": "object",
  "properties": {
    "submissionId": {"type": "string"},
    "invitationCode": {"type": "string"},
    "timestamp": {"type": "string"},
    "companyInfo": {
      "type": "object",
      "properties": {
        "companyName": {"type": "string"},
        "tradingName": {"type": "string"},
        "registrationNumber": {"type": "string"},
        "vatNumber": {"type": "string"},
        "website": {"type": "string"},
        "yearEstablished": {"type": "string"},
        "employeeCount": {"type": "string"},
        "annualRevenue": {"type": "string"}
      }
    },
    "contactInfo": {
      "type": "object",
      "properties": {
        "primaryContactName": {"type": "string"},
        "primaryContactTitle": {"type": "string"},
        "primaryContactEmail": {"type": "string"},
        "primaryContactPhone": {"type": "string"},
        "companyAddress": {"type": "string"},
        "city": {"type": "string"},
        "stateProvince": {"type": "string"},
        "postalCode": {"type": "string"},
        "country": {"type": "string"}
      }
    },
    "capabilities": {
      "type": "object",
      "properties": {
        "services": {"type": "array"},
        "systemTypes": {"type": "array"},
        "maxProjectSize": {"type": "string"},
        "typicalProjectSize": {"type": "string"},
        "geographicCoverage": {"type": "array"}
      }
    },
    "certifications": {
      "type": "object",
      "properties": {
        "certificationsList": {"type": "array"},
        "insuranceTypes": {"type": "array"},
        "safetyAccreditations": {"type": "array"}
      }
    },
    "documents": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "type": {"type": "string"},
          "fileName": {"type": "string"},
          "url": {"type": "string"}
        }
      }
    }
  }
}
```

**Method**: POST

After configuration, copy the HTTP POST URL that's generated.

### 3. Update Invitation Record

#### Action: Get items - SharePoint
**Get the invitation that was used**

- Site Address: `https://saberrenewables.sharepoint.com/sites/SaberEPCPartners`
- List Name: `EPC Invitations`
- Filter Query: `Code eq '@{triggerBody()?['invitationCode']}'`

### 4. Condition - Check Valid Invitation

**Condition**
- Check if invitation exists and is Active:
  ```
  length(outputs('Get_items')?['body/value']) is greater than 0
  AND
  first(outputs('Get_items')?['body/value'])?['Status'] is equal to Active
  ```

### 5. If Yes - Process Application

#### Action: Create item - SharePoint
**Create EPC Onboarding Entry**

- Site Address: `https://saberrenewables.sharepoint.com/sites/SaberEPCPartners`
- List Name: `EPC Onboarding`
- Title: `@{triggerBody()?['companyInfo']?['companyName']}`
- Status: `New`
- SubmissionID: `@{triggerBody()?['submissionId']}`
- InvitationCode: `@{triggerBody()?['invitationCode']}`
- CompanyName: `@{triggerBody()?['companyInfo']?['companyName']}`
- TradingName: `@{triggerBody()?['companyInfo']?['tradingName']}`
- RegistrationNumber: `@{triggerBody()?['companyInfo']?['registrationNumber']}`
- VATNumber: `@{triggerBody()?['companyInfo']?['vatNumber']}`
- Website: `@{triggerBody()?['companyInfo']?['website']}`
- YearEstablished: `@{triggerBody()?['companyInfo']?['yearEstablished']}`
- EmployeeCount: `@{triggerBody()?['companyInfo']?['employeeCount']}`
- AnnualRevenue: `@{triggerBody()?['companyInfo']?['annualRevenue']}`
- PrimaryContactName: `@{triggerBody()?['contactInfo']?['primaryContactName']}`
- PrimaryContactTitle: `@{triggerBody()?['contactInfo']?['primaryContactTitle']}`
- PrimaryContactEmail: `@{triggerBody()?['contactInfo']?['primaryContactEmail']}`
- PrimaryContactPhone: `@{triggerBody()?['contactInfo']?['primaryContactPhone']}`
- CompanyAddress: `@{triggerBody()?['contactInfo']?['companyAddress']}`
- City: `@{triggerBody()?['contactInfo']?['city']}`
- StateProvince: `@{triggerBody()?['contactInfo']?['stateProvince']}`
- PostalCode: `@{triggerBody()?['contactInfo']?['postalCode']}`
- Country: `@{triggerBody()?['contactInfo']?['country']}`
- Services: `@{join(triggerBody()?['capabilities']?['services'], ', ')}`
- SystemTypes: `@{join(triggerBody()?['capabilities']?['systemTypes'], ', ')}`
- MaxProjectSize: `@{triggerBody()?['capabilities']?['maxProjectSize']}`
- TypicalProjectSize: `@{triggerBody()?['capabilities']?['typicalProjectSize']}`
- GeographicCoverage: `@{join(triggerBody()?['capabilities']?['geographicCoverage'], ', ')}`
- Certifications: `@{join(triggerBody()?['certifications']?['certificationsList'], ', ')}`
- InsuranceTypes: `@{join(triggerBody()?['certifications']?['insuranceTypes'], ', ')}`
- SafetyAccreditations: `@{join(triggerBody()?['certifications']?['safetyAccreditations'], ', ')}`
- SubmissionDate: `@{utcNow()}`
- DocumentsJSON: `@{string(triggerBody()?['documents'])}`

#### Action: Update item - SharePoint
**Mark invitation as used**

- Site Address: `https://saberrenewables.sharepoint.com/sites/SaberEPCPartners`
- List Name: `EPC Invitations`
- Id: `@{first(outputs('Get_items')?['body/value'])?['ID']}`
- Status: `Used`
- Used: `Yes`
- UsedBy: `@{triggerBody()?['contactInfo']?['primaryContactEmail']}`
- UsedDate: `@{utcNow()}`

### 6. Send Confirmation Emails

#### Action: Send an email (V2) - To Applicant
**Confirmation to Partner**

**To**: `@{triggerBody()?['contactInfo']?['primaryContactEmail']}`

**Subject**: 
```
Application Received - @{triggerBody()?['companyInfo']?['companyName']}
```

**Body**:
```html
<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: 'Segoe UI', Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background: linear-gradient(135deg, #044D73 0%, #0d1138 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }
        .content { background: #f9f9f9; padding: 30px; border: 1px solid #ddd; border-radius: 0 0 10px 10px; }
        .info-box { background: white; padding: 20px; margin: 20px 0; border-left: 4px solid #7CC061; }
        .footer { margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd; font-size: 12px; color: #666; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Application Received</h1>
            <p>Thank you for applying to join our EPC Partner Network</p>
        </div>
        
        <div class="content">
            <p>Dear @{triggerBody()?['contactInfo']?['primaryContactName']},</p>
            
            <p>We have successfully received your application to join the Saber Renewables EPC Partner Network.</p>
            
            <div class="info-box">
                <h3>Application Details:</h3>
                <p><strong>Company:</strong> @{triggerBody()?['companyInfo']?['companyName']}<br>
                <strong>Submission ID:</strong> @{triggerBody()?['submissionId']}<br>
                <strong>Date Received:</strong> @{formatDateTime(utcNow(), 'dd MMMM yyyy HH:mm')} UTC</p>
            </div>
            
            <h3>What Happens Next?</h3>
            <ol>
                <li><strong>Initial Review (1-2 business days):</strong> Our team will review your application and submitted documents</li>
                <li><strong>Due Diligence (3-5 business days):</strong> We'll verify certifications and may request additional information</li>
                <li><strong>Decision:</strong> You'll receive our decision via email within 5 business days</li>
                <li><strong>Onboarding:</strong> Approved partners will receive access credentials and onboarding materials</li>
            </ol>
            
            <p>If you have any questions about your application, please contact us at <a href="mailto:partners@saberrenewables.com">partners@saberrenewables.com</a> referencing your Submission ID.</p>
            
            <div class="footer">
                <p><strong>Saber Renewables</strong><br>
                Expert • Clear • Strategic<br>
                <a href="https://saberrenewables.com">www.saberrenewables.com</a></p>
            </div>
        </div>
    </div>
</body>
</html>
```

#### Action: Send an email (V2) - To Internal Team
**Notification to Saber Team**

**To**: `partners@saberrenewables.com; sysadmin@saberrenewables.com`

**Subject**: 
```
New EPC Application - @{triggerBody()?['companyInfo']?['companyName']} - Review Required
```

**Body**:
```html
<h2>New EPC Partner Application Received</h2>

<h3>Company Information:</h3>
<table border="1" cellpadding="5" style="border-collapse: collapse;">
    <tr><td><strong>Company Name:</strong></td><td>@{triggerBody()?['companyInfo']?['companyName']}</td></tr>
    <tr><td><strong>Trading Name:</strong></td><td>@{triggerBody()?['companyInfo']?['tradingName']}</td></tr>
    <tr><td><strong>Registration #:</strong></td><td>@{triggerBody()?['companyInfo']?['registrationNumber']}</td></tr>
    <tr><td><strong>Website:</strong></td><td>@{triggerBody()?['companyInfo']?['website']}</td></tr>
    <tr><td><strong>Employees:</strong></td><td>@{triggerBody()?['companyInfo']?['employeeCount']}</td></tr>
    <tr><td><strong>Annual Revenue:</strong></td><td>@{triggerBody()?['companyInfo']?['annualRevenue']}</td></tr>
</table>

<h3>Primary Contact:</h3>
<table border="1" cellpadding="5" style="border-collapse: collapse;">
    <tr><td><strong>Name:</strong></td><td>@{triggerBody()?['contactInfo']?['primaryContactName']}</td></tr>
    <tr><td><strong>Title:</strong></td><td>@{triggerBody()?['contactInfo']?['primaryContactTitle']}</td></tr>
    <tr><td><strong>Email:</strong></td><td>@{triggerBody()?['contactInfo']?['primaryContactEmail']}</td></tr>
    <tr><td><strong>Phone:</strong></td><td>@{triggerBody()?['contactInfo']?['primaryContactPhone']}</td></tr>
</table>

<h3>Capabilities:</h3>
<ul>
    <li><strong>Services:</strong> @{join(triggerBody()?['capabilities']?['services'], ', ')}</li>
    <li><strong>System Types:</strong> @{join(triggerBody()?['capabilities']?['systemTypes'], ', ')}</li>
    <li><strong>Max Project Size:</strong> @{triggerBody()?['capabilities']?['maxProjectSize']}</li>
    <li><strong>Geographic Coverage:</strong> @{join(triggerBody()?['capabilities']?['geographicCoverage'], ', ')}</li>
</ul>

<h3>Documents Submitted:</h3>
<ul>
@{join(createArray(
    if(contains(triggerBody()?['documents'], 'Company Registration'), '<li>✅ Company Registration</li>', ''),
    if(contains(triggerBody()?['documents'], 'Insurance'), '<li>✅ Insurance Documentation</li>', ''),
    if(contains(triggerBody()?['documents'], 'Certifications'), '<li>✅ Certifications</li>', ''),
    if(contains(triggerBody()?['documents'], 'Safety'), '<li>✅ Safety Documentation</li>', '')
), '')}
</ul>

<h3>Action Required:</h3>
<p><strong>Review the application in SharePoint:</strong><br>
<a href="https://saberrenewables.sharepoint.com/sites/SaberEPCPartners/Lists/EPC%20Onboarding">View in EPC Onboarding List</a></p>

<p><strong>Submission ID:</strong> @{triggerBody()?['submissionId']}<br>
<strong>Invitation Code Used:</strong> @{triggerBody()?['invitationCode']}<br>
<strong>Submitted:</strong> @{formatDateTime(utcNow(), 'dd MMMM yyyy HH:mm')} UTC</p>
```

### 7. If No - Invalid or Expired Invitation

#### Action: Send an email (V2) - Error Notification
**To**: `sysadmin@saberrenewables.com`

**Subject**: 
```
Invalid EPC Application Attempt - @{triggerBody()?['invitationCode']}
```

**Body**:
```
An application was submitted with an invalid or expired invitation code.

Code Attempted: @{triggerBody()?['invitationCode']}
Email: @{triggerBody()?['contactInfo']?['primaryContactEmail']}
Company: @{triggerBody()?['companyInfo']?['companyName']}
Time: @{utcNow()}

This may indicate:
1. Expired invitation code
2. Already used invitation code
3. Invalid/fake invitation code
4. System error

Please investigate in SharePoint.
```

### 8. Response to Caller

#### Action: Response
**Return success or error to the calling system**

**Status Code**: 
- If success: `200`
- If invalid: `400`

**Body**:
```json
{
  "success": @{if(greater(length(outputs('Get_items')?['body/value']), 0), true, false)},
  "message": "@{if(greater(length(outputs('Get_items')?['body/value']), 0), 'Application submitted successfully', 'Invalid or expired invitation code')}",
  "submissionId": "@{triggerBody()?['submissionId']}",
  "timestamp": "@{utcNow()}"
}
```

## Integration with Cloudflare Worker

### Update Worker Endpoint
The Cloudflare Worker at `epc.saberrenewable.energy` needs to call this Power Automate flow.

In your Worker code, add:
```javascript
// After successful validation and data preparation
const powerAutomateUrl = 'YOUR_POWER_AUTOMATE_HTTP_TRIGGER_URL';

const response = await fetch(powerAutomateUrl, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    submissionId: generateSubmissionId(),
    invitationCode: invitationCode,
    timestamp: new Date().toISOString(),
    companyInfo: formData.companyInfo,
    contactInfo: formData.contactInfo,
    capabilities: formData.capabilities,
    certifications: formData.certifications,
    documents: uploadedDocuments
  })
});

const result = await response.json();
```

## Testing the Flow

### 1. Manual Test with Sample Data
1. Click **Test** → **Manually**
2. Use this sample JSON:
```json
{
  "submissionId": "TEST-2024-001",
  "invitationCode": "ABCD1234",
  "timestamp": "2024-01-09T10:00:00Z",
  "companyInfo": {
    "companyName": "Test Solar Solutions",
    "tradingName": "Test Solar",
    "registrationNumber": "12345678",
    "vatNumber": "GB123456789",
    "website": "www.testsolar.com",
    "yearEstablished": "2015",
    "employeeCount": "50-100",
    "annualRevenue": "$5M-$10M"
  },
  "contactInfo": {
    "primaryContactName": "John Test",
    "primaryContactTitle": "Business Development Manager",
    "primaryContactEmail": "john@testsolar.com",
    "primaryContactPhone": "+44 20 1234 5678",
    "companyAddress": "123 Solar Street",
    "city": "London",
    "stateProvince": "Greater London",
    "postalCode": "SW1A 1AA",
    "country": "United Kingdom"
  },
  "capabilities": {
    "services": ["Installation", "Maintenance", "Design"],
    "systemTypes": ["Rooftop Solar", "Ground Mount", "Battery Storage"],
    "maxProjectSize": "10MW",
    "typicalProjectSize": "500kW-2MW",
    "geographicCoverage": ["United Kingdom", "Ireland"]
  },
  "certifications": {
    "certificationsList": ["MCS", "NICEIC", "ISO 9001"],
    "insuranceTypes": ["Public Liability", "Professional Indemnity"],
    "safetyAccreditations": ["SafeContractor", "CHAS"]
  },
  "documents": [
    {"type": "registration", "fileName": "company-reg.pdf", "url": "https://example.com/doc1"},
    {"type": "insurance", "fileName": "insurance.pdf", "url": "https://example.com/doc2"}
  ]
}
```

### 2. Verify Results
- Check SharePoint "EPC Onboarding" list for new entry
- Check "EPC Invitations" list shows code as "Used"
- Verify confirmation emails were sent
- Check response returned correct status

## Complete Application Flow

1. **Partner receives invitation** (from invitation flow)
2. **Partner visits** `https://epc.saberrenewable.energy/epc/apply`
3. **Partner enters code** and proceeds to application
4. **Partner fills form** and uploads documents
5. **Form submits to Worker** which validates and stores files
6. **Worker calls Power Automate** with application data
7. **Power Automate creates SharePoint entry** and marks code as used
8. **Confirmation emails sent** to partner and internal team
9. **Automated processor** picks up from SharePoint for further processing

## Troubleshooting

### Flow not triggering:
- Verify HTTP trigger URL is correct in Worker
- Check flow is turned ON
- Review run history for errors

### SharePoint errors:
- Verify all column names match exactly
- Check list permissions
- Ensure all required columns exist

### Email issues:
- Check Office 365 connection
- Verify email addresses
- Check spam folders

### Invalid invitation codes:
- Check code exists in "EPC Invitations" list
- Verify Status = "Active"
- Check expiry date hasn't passed

## Security Considerations

1. **HTTP Trigger Security**:
   - Consider adding API key validation
   - Implement rate limiting in Worker
   - Log all submission attempts

2. **Data Validation**:
   - Validate all inputs in Worker before calling flow
   - Sanitize data to prevent injection attacks
   - Verify file types and sizes

3. **Audit Trail**:
   - All submissions logged in SharePoint
   - Email notifications create paper trail
   - Flow run history provides debugging

## Notes
- HTTP trigger URL is unique and should be kept secure
- Flow handles both successful and failed submissions
- Invitation codes are single-use only
- System maintains complete audit trail
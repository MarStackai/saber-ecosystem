# SharePoint Integration - Technology Guide

> **Microsoft 365 SharePoint Integration for Business Operations**

## 📋 Overview

SharePoint serves as the central data management and collaboration platform for Saber Renewables' business operations, providing secure data storage, workflow automation, and team collaboration capabilities through Microsoft 365 integration.

---

## 🏗️ **SharePoint Architecture**

### **Site Structure**
```
https://saberrenewables.sharepoint.com/
└── sites/SaberEPCPartners/
    ├── Lists/
    │   ├── EPC Invitations           # Partner invitation management
    │   └── EPC Onboarding           # Application submissions
    ├── Document Libraries/
    │   ├── EPC Submissions          # Partner documents
    │   └── Scripts                  # PowerShell automation
    ├── Pages/
    │   ├── Partner Dashboard        # Operations overview
    │   └── Reports                  # Analytics pages
    └── Workflows/
        ├── Invitation Generator     # Power Automate flows
        └── Application Processor    # Processing automation
```

### **Integration Points**
```
SharePoint ←→ Cloudflare
    │
    ├── Power Automate Webhooks
    ├── REST API Calls
    ├── Certificate Authentication
    └── Real-time Data Sync
```

---

## 📊 **List Schemas**

### **EPC Invitations List**

| Column | Type | Required | Description |
|--------|------|----------|-------------|
| Title | Single line of text | Yes | Company name |
| InvitationCode | Single line of text | Yes | 8-character unique code |
| ContactEmail | Single line of text | Yes | Primary contact email |
| ContactTitle | Choice | No | Mr, Ms, Dr, Prof |
| ContactName | Single line of text | No | Full contact name |
| CompanyAddress | Multiple lines of text | No | Full company address |
| Status | Choice | Yes | Active, Used, Expired, Cancelled |
| ExpiryDate | Date and time | No | Invitation expiration |
| Notes | Multiple lines of text | No | Additional notes |
| CreatedBy | Person or Group | Auto | Operations team member |
| Created | Date and time | Auto | Creation timestamp |
| Modified | Date and time | Auto | Last modification |

**Choice Values**:
- **ContactTitle**: Mr, Ms, Mrs, Dr, Prof, Eng, Other
- **Status**: Active, Used, Expired, Cancelled

### **EPC Onboarding List**

| Column | Type | Required | Description |
|--------|------|----------|-------------|
| Title | Single line of text | Yes | Company name |
| InvitationCode | Single line of text | Yes | Source invitation code |
| ContactName | Single line of text | Yes | Primary contact name |
| ContactEmail | Single line of text | Yes | Contact email address |
| ContactPhone | Single line of text | No | Phone number |
| ApplicationData | Multiple lines of text | Yes | Complete form JSON |
| Status | Choice | Yes | Application status |
| Priority | Choice | No | Processing priority |
| SubmittedDate | Date and time | Auto | Submission timestamp |
| ReviewedBy | Person or Group | No | Assigned reviewer |
| ReviewDate | Date and time | No | Review completion date |
| ReviewNotes | Multiple lines of text | No | Reviewer comments |
| ApprovalStatus | Choice | No | Final approval status |
| DocumentLinks | Hyperlink | No | Links to uploaded files |
| CompanySize | Choice | No | Partner company size |
| GeographicFocus | Multiple lines of text | No | Operating regions |
| TechnicalCapabilities | Multiple lines of text | No | Technical skills |

**Choice Values**:
- **Status**: Submitted, Under Review, Information Required, Approved, Rejected
- **Priority**: Low, Medium, High, Urgent
- **ApprovalStatus**: Pending, Approved, Conditional, Rejected
- **CompanySize**: Startup (1-10), Small (11-50), Medium (51-200), Large (201+)

---

## 🔄 **Power Automate Workflows**

### **1. Invitation Code Generator**

**Trigger**: When item is created in EPC Invitations list

**Actions**:
```
1. Generate random 8-character code (alphanumeric, uppercase)
2. Check for code uniqueness in existing invitations
3. Update invitation item with generated code
4. Send email to partner with invitation link
5. Sync invitation to Cloudflare D1 database
6. Log success/failure in workflow history
```

**Flow Definition**:
```json
{
  "trigger": {
    "type": "SharePointListItemCreated",
    "listId": "EPC Invitations"
  },
  "actions": [
    {
      "name": "GenerateInvitationCode",
      "type": "Compose",
      "expression": "substring(guid(), 0, 8)"
    },
    {
      "name": "UpdateInvitationItem",
      "type": "SharePointUpdateItem",
      "inputs": {
        "InvitationCode": "@outputs('GenerateInvitationCode')",
        "Status": "Active"
      }
    },
    {
      "name": "SendInvitationEmail",
      "type": "OutlookSendEmail",
      "template": "Partner Invitation Template"
    },
    {
      "name": "SyncToCloudflare",
      "type": "HTTP",
      "method": "POST",
      "uri": "https://epc.saberrenewable.energy/api/sync-invitation"
    }
  ]
}
```

### **2. Application Processor**

**Trigger**: HTTP request from Cloudflare Worker

**Actions**:
```
1. Receive application data from Cloudflare
2. Parse and validate JSON payload
3. Create new item in EPC Onboarding list
4. Update invitation status to "Used"
5. Send notification emails to operations team
6. Create calendar reminder for review
7. Return success confirmation
```

### **3. Automated Notifications**

**Triggers**:
- New application submitted
- Application status changed
- Review deadline approaching

**Email Templates**:
- **Partner Welcome**: Sent after invitation acceptance
- **Operations Alert**: New application notification
- **Review Reminder**: Deadline approaching
- **Status Update**: Application progress notification

---

## 🔐 **Authentication & Security**

### **Certificate-Based Authentication**

**Setup Process**:
```powershell
# Generate self-signed certificate
$cert = New-SelfSignedCertificate -Subject "CN=SaberEPCApp" -CertStoreLocation "Cert:\CurrentUser\My" -KeyExportPolicy Exportable -KeySpec Signature

# Export certificate
Export-Certificate -Cert $cert -FilePath "SaberEPCApp.cer"
Export-PfxCertificate -Cert $cert -FilePath "SaberEPCApp.pfx" -Password (ConvertTo-SecureString -String "YourPassword" -Force -AsPlainText)

# Register in Azure AD
Connect-AzureAD
$app = New-AzureADApplication -DisplayName "Saber EPC Portal" -IdentifierUris "https://saber-epc-portal"
New-AzureADApplicationKeyCredential -ObjectId $app.ObjectId -CustomKeyIdentifier "SaberEPCCert" -Value ([System.Convert]::ToBase64String($cert.RawData))
```

**Configuration Details**:
- **Client ID**: `bbbfe394-7cff-4ac9-9e01-33cbf116b930`
- **Tenant ID**: Microsoft 365 tenant
- **Certificate Thumbprint**: Stored securely in Cloudflare Workers
- **Permissions**: Sites.ReadWrite.All, Mail.Send

### **API Permissions**

**Required Permissions**:
```
Microsoft Graph:
├── Sites.ReadWrite.All      # SharePoint list access
├── Mail.Send               # Email notifications
├── User.Read.All           # User information
└── Directory.Read.All      # Azure AD integration

SharePoint:
├── AllSites.Write          # List and library access
├── TermStore.ReadWrite.All # Metadata management
└── User.ReadWrite.All      # User profile access
```

---

## 📡 **REST API Integration**

### **Authentication Headers**
```javascript
const headers = {
  'Authorization': `Bearer ${accessToken}`,
  'Accept': 'application/json;odata=verbose',
  'Content-Type': 'application/json;odata=verbose',
  'X-RequestDigest': digestValue
};
```

### **Common API Endpoints**

#### **Get List Items**
```javascript
// GET /sites/{site-id}/lists/{list-id}/items
const invitations = await fetch(
  'https://saberrenewables.sharepoint.com/sites/SaberEPCPartners/_api/web/lists/getbytitle(\'EPC Invitations\')/items',
  { headers }
);
```

#### **Create List Item**
```javascript
// POST /sites/{site-id}/lists/{list-id}/items
const newApplication = await fetch(
  'https://saberrenewables.sharepoint.com/sites/SaberEPCPartners/_api/web/lists/getbytitle(\'EPC Onboarding\')/items',
  {
    method: 'POST',
    headers,
    body: JSON.stringify({
      Title: 'Example Company',
      ContactEmail: 'contact@example.com',
      ApplicationData: JSON.stringify(formData)
    })
  }
);
```

#### **Update List Item**
```javascript
// PATCH /sites/{site-id}/lists/{list-id}/items/{item-id}
const updateStatus = await fetch(
  `https://saberrenewables.sharepoint.com/sites/SaberEPCPartners/_api/web/lists/getbytitle('EPC Onboarding')/items(${itemId})`,
  {
    method: 'PATCH',
    headers: {
      ...headers,
      'IF-MATCH': '*',
      'X-HTTP-Method': 'MERGE'
    },
    body: JSON.stringify({
      Status: 'Under Review'
    })
  }
);
```

---

## 🔧 **PowerShell Management Scripts**

### **Invitation Management**
```powershell
# create-invitation.ps1
param(
    [Parameter(Mandatory=$true)]
    [string]$CompanyName,

    [Parameter(Mandatory=$true)]
    [string]$ContactEmail,

    [string]$ContactTitle = "Mr",
    [string]$Notes = ""
)

Connect-PnPOnline -Url "https://saberrenewables.sharepoint.com/sites/SaberEPCPartners" -ClientId $ClientId -CertificatePath $CertPath

$listItem = Add-PnPListItem -List "EPC Invitations" -Values @{
    "Title" = $CompanyName
    "ContactEmail" = $ContactEmail
    "ContactTitle" = $ContactTitle
    "Notes" = $Notes
    "Status" = "Active"
}

Write-Host "Invitation created with ID: $($listItem.Id)"
```

### **Bulk Operations**
```powershell
# batch-create-invitations.ps1
param(
    [Parameter(Mandatory=$true)]
    [string]$CsvFilePath
)

$invitations = Import-Csv $CsvFilePath

foreach ($invitation in $invitations) {
    try {
        Add-PnPListItem -List "EPC Invitations" -Values @{
            "Title" = $invitation.CompanyName
            "ContactEmail" = $invitation.ContactEmail
            "ContactTitle" = $invitation.ContactTitle
            "Notes" = $invitation.Notes
        }
        Write-Host "✓ Created invitation for $($invitation.CompanyName)"
    }
    catch {
        Write-Error "✗ Failed to create invitation for $($invitation.CompanyName): $($_.Exception.Message)"
    }
}
```

### **Monitoring and Reports**
```powershell
# generate-partner-report.ps1
$invitations = Get-PnPListItem -List "EPC Invitations"
$applications = Get-PnPListItem -List "EPC Onboarding"

$report = @{
    TotalInvitations = $invitations.Count
    ActiveInvitations = ($invitations | Where-Object { $_.FieldValues.Status -eq "Active" }).Count
    UsedInvitations = ($invitations | Where-Object { $_.FieldValues.Status -eq "Used" }).Count
    TotalApplications = $applications.Count
    PendingApplications = ($applications | Where-Object { $_.FieldValues.Status -eq "Submitted" }).Count
    ApprovedApplications = ($applications | Where-Object { $_.FieldValues.Status -eq "Approved" }).Count
}

$report | ConvertTo-Json | Out-File "partner-report-$(Get-Date -Format 'yyyy-MM-dd').json"
```

---

## 📊 **Monitoring & Analytics**

### **Built-in SharePoint Analytics**
- **List Usage**: Item creation and modification trends
- **User Activity**: Team member engagement metrics
- **Storage Usage**: Document library growth tracking
- **Performance**: Page load times and responsiveness

### **Custom Power BI Integration**
```powershell
# Connect Power BI to SharePoint Lists
$dataSource = @{
    "SharePointUrl" = "https://saberrenewables.sharepoint.com/sites/SaberEPCPartners"
    "Lists" = @("EPC Invitations", "EPC Onboarding")
    "RefreshSchedule" = "Daily at 6:00 AM"
}
```

### **Key Performance Indicators**
- **Invitation Conversion Rate**: Used invitations / Total invitations
- **Application Processing Time**: Average days from submission to decision
- **Partner Pipeline Health**: Applications by status distribution
- **Team Productivity**: Applications processed per team member

---

## 🛠️ **Maintenance & Operations**

### **Regular Maintenance Tasks**

#### **Daily**
```powershell
# Check for failed Power Automate flows
Get-PnPFlow | Where-Object { $_.Properties.State -eq "Failed" }

# Monitor new applications
Get-PnPListItem -List "EPC Onboarding" -Query "<View><Query><Where><Geq><FieldRef Name='Created'/><Value Type='DateTime'><Today/></Value></Geq></Where></Query></View>"
```

#### **Weekly**
```powershell
# Clean expired invitations
$expiredInvitations = Get-PnPListItem -List "EPC Invitations" -Query "<View><Query><Where><And><Eq><FieldRef Name='Status'/><Value Type='Text'>Active</Value></Eq><Lt><FieldRef Name='ExpiryDate'/><Value Type='DateTime'><Today/></Value></Lt></And></Where></Query></View>"

foreach ($invitation in $expiredInvitations) {
    Set-PnPListItem -List "EPC Invitations" -Identity $invitation.Id -Values @{"Status" = "Expired"}
}
```

#### **Monthly**
```powershell
# Archive old applications
$oldApplications = Get-PnPListItem -List "EPC Onboarding" -Query "<View><Query><Where><Lt><FieldRef Name='Created'/><Value Type='DateTime'><Today OffsetDays='-90'/></Value></Lt></Where></Query></View>"

# Export to archive and remove from active list
$oldApplications | Export-Csv "archive-applications-$(Get-Date -Format 'yyyy-MM').csv"
```

---

## 🔮 **Future Enhancements**

### **Planned Improvements**
1. **SharePoint Syntex**: AI-powered document processing
2. **Microsoft Viva**: Enhanced collaboration tools
3. **Power Platform Integration**: Advanced workflow automation
4. **Microsoft Teams**: Embedded partner collaboration

### **Integration Roadmap**
- **Microsoft 365 Copilot**: AI-assisted operations
- **Azure Logic Apps**: Advanced integration scenarios
- **Power BI Premium**: Real-time analytics dashboards
- **Microsoft Purview**: Enhanced data governance

---

**Document Version**: 1.0
**Last Updated**: September 17, 2025
**Next Review**: December 1, 2025
**Owner**: Saber Renewables SharePoint Administrator
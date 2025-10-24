# Data Flow Architecture - Saber Business Operations

> **Comprehensive Data Movement and Processing Architecture**

## Overview

This document describes the complete data flow architecture for the Saber Business Operations platform, detailing how information moves through the system from partner interaction to business intelligence reporting.

---

## **Primary Data Flows**

### **1. Partner Onboarding Flow**

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   OPERATIONS    │    │   SHAREPOINT    │    │  POWER AUTOMATE │
│      TEAM       │───▶│      LISTS      │───▶│   WORKFLOWS     │
│                 │    │                 │    │                 │
│ Create Partner  │    │ EPC Invitations │    │ Generate Code   │
│   Invitation    │    │      List       │    │   Send Email    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                        │
                                                        ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   CLOUDFLARE    │    │   CLOUDFLARE    │    │     PARTNER     │
│       D1        │◀───│     WORKER      │◀───│                 │
│                 │    │                 │    │ Receives Email  │
│ Store Invitation│    │ Validate Code   │    │  Clicks Link    │
│     Details     │    │    via API      │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                ▼
                    ┌─────────────────┐
                    │   CLOUDFLARE    │
                    │      PAGES      │
                    │                 │
                    │ Pre-fill Form   │
                    │  Start Session  │
                    └─────────────────┘
```

### **2. Application Submission Flow**

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│     PARTNER     │    │   CLOUDFLARE    │    │   CLOUDFLARE    │
│                 │───▶│      PAGES      │───▶│       D1        │
│   Fills Form    │    │                 │    │                 │
│  Uploads Files  │    │ React Frontend  │    │ Auto-save Draft │
│                 │    │   Auto-save     │    │  Store Session  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        ▼
                    ┌─────────────────┐    ┌─────────────────┐
                    │   CLOUDFLARE    │    │   CLOUDFLARE    │
                    │       R2        │    │     WORKER      │
                    │                 │    │                 │
                    │  Store Files    │    │ Process Submit  │
                    │   Generate      │    │   Validate      │
                    │     URLs        │    │    Complete     │
                    └─────────────────┘    └─────────────────┘
                                                    │
                                                    ▼
                    ┌─────────────────┐    ┌─────────────────┐
                    │   SHAREPOINT    │    │  POWER AUTOMATE │
                    │                 │◀───│                 │
                    │ EPC Onboarding  │    │ Sync Application│
                    │      List       │    │  Send Notifications│
                    │  Store Final    │    │  Update Status  │
                    │   Application   │    │                 │
                    └─────────────────┘    └─────────────────┘
```

### **3. File Management Flow**

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│     PARTNER     │    │   FRONTEND      │    │   CLOUDFLARE    │
│                 │───▶│                 │───▶│     WORKER      │
│ Select Files    │    │ File Validation │    │                 │
│ Drag & Drop     │    │ Progress UI     │    │ Generate        │
│                 │    │                 │    │ Presigned URL   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                        │
                                                        ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   CLOUDFLARE    │    │   CLOUDFLARE    │    │   CLOUDFLARE    │
│       D1        │◀───│       R2        │◀───│     WORKER      │
│                 │    │                 │    │                 │
│  Store File     │    │   Store File    │    │ Upload Direct   │
│   Metadata      │    │    Content      │    │   to R2 Bucket  │
│   References    │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                    ┌─────────────────┐
                    │   SHAREPOINT    │
                    │                 │
                    │ Reference URLs  │
                    │  in Application │
                    │     Record      │
                    └─────────────────┘
```

---

## **Database Schema & Relationships**

### **Cloudflare D1 Database**

#### **Table: invitations**
```sql
CREATE TABLE invitations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT UNIQUE NOT NULL,           -- 8-character invitation code
    company_name TEXT NOT NULL,          -- Partner company name
    contact_email TEXT NOT NULL,         -- Primary contact email
    contact_title TEXT,                  -- Contact title (Mr, Ms, Dr)
    notes TEXT,                          -- Additional notes
    status TEXT DEFAULT 'active',        -- active, used, expired
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    expires_at DATETIME,                 -- Expiration date
    used_at DATETIME,                    -- When code was used
    source TEXT DEFAULT 'sharepoint'     -- Origin tracking
);
```

#### **Table: applications**
```sql
CREATE TABLE applications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    invitation_code TEXT NOT NULL,       -- Links to invitation

    -- Company Information (Step 1)
    company_name TEXT NOT NULL,
    company_registration TEXT,
    company_address TEXT,
    company_city TEXT,
    company_state TEXT,
    company_postal TEXT,
    company_country TEXT,
    company_phone TEXT,
    company_website TEXT,

    -- Contact Details (Step 2)
    primary_contact_name TEXT,
    primary_contact_title TEXT,
    primary_contact_email TEXT,
    primary_contact_phone TEXT,
    technical_contact_name TEXT,
    technical_contact_email TEXT,

    -- Capabilities (Step 3)
    installation_capacity TEXT,
    geographic_coverage TEXT,
    equipment_brands TEXT,
    certifications TEXT,
    experience_years INTEGER,

    -- ... (97 total columns for complete application)

    status TEXT DEFAULT 'draft',         -- draft, submitted, reviewed, approved
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    submitted_at DATETIME,
    FOREIGN KEY (invitation_code) REFERENCES invitations(code)
);
```

#### **Table: application_files**
```sql
CREATE TABLE application_files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    application_id INTEGER NOT NULL,
    file_name TEXT NOT NULL,
    file_type TEXT NOT NULL,
    file_size INTEGER NOT NULL,
    r2_key TEXT NOT NULL,               -- R2 storage key
    r2_url TEXT NOT NULL,               -- Public access URL
    upload_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (application_id) REFERENCES applications(id)
);
```

#### **Table: draft_data**
```sql
CREATE TABLE draft_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    invitation_code TEXT NOT NULL,
    step_number INTEGER NOT NULL,
    form_data TEXT NOT NULL,            -- JSON blob of form state
    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(invitation_code, step_number)
);
```

### **SharePoint Lists Structure**

#### **List: EPC Invitations**
| Column | Type | Description |
|--------|------|-------------|
| Title | Text | Company name |
| InvitationCode | Text | 8-character unique code |
| ContactEmail | Text | Primary contact email |
| ContactTitle | Choice | Mr, Ms, Dr, etc. |
| Status | Choice | Active, Used, Expired |
| ExpiryDate | DateTime | When invitation expires |
| CreatedBy | Person | Operations team member |
| Notes | Multi-line | Additional information |

#### **List: EPC Onboarding**
| Column | Type | Description |
|--------|------|-------------|
| Title | Text | Company name |
| InvitationCode | Text | Source invitation code |
| ContactName | Text | Primary contact name |
| ContactEmail | Text | Email address |
| ApplicationData | Multi-line | Complete form JSON |
| Status | Choice | Submitted, Under Review, Approved, Rejected |
| SubmittedDate | DateTime | Submission timestamp |
| ReviewedBy | Person | Reviewer |
| ReviewNotes | Multi-line | Review comments |
| DocumentLinks | Hyperlink | Links to uploaded files |

---

## **Real-Time Data Synchronization**

### **Invitation Sync Process**
```
SharePoint List Change
    ↓
Power Automate Trigger
    ↓
HTTP POST to /api/sync-invitation
    ↓
Cloudflare Worker Processes
    ↓
Update D1 Database
    ↓
Return Success/Failure
    ↓
Power Automate Logs Result
```

### **Application Sync Process**
```
D1 Application Submitted
    ↓
Cloudflare Worker API Call
    ↓
HTTP POST to Power Automate Webhook
    ↓
Power Automate Processes
    ↓
Create SharePoint List Item
    ↓
Send Email Notifications
    ↓
Update Application Status in D1
```

---

## **API Data Contracts**

### **Invitation Validation API**
```javascript
// POST /api/validate-invitation
{
  "invitationCode": "C1D94680"
}

// Response (Success)
{
  "valid": true,
  "message": "Valid invitation code",
  "invitation": {
    "code": "C1D94680",
    "title": "Mr",
    "companyName": "Marstack",
    "contactEmail": "rob@marstack.ai",
    "notes": "Synced from Power Automate"
  },
  "source": "d1"
}

// Response (Invalid)
{
  "valid": false,
  "message": "Invalid or expired invitation code",
  "invitation": null,
  "source": "d1"
}
```

### **Application Submission API**
```javascript
// POST /api/epc-application
{
  "invitationCode": "C1D94680",
  "step1": {
    "companyName": "Example Corp",
    "companyRegistration": "12345678",
    // ... all step 1 fields
  },
  "step2": {
    // ... step 2 fields
  },
  // ... steps 3-6
  "fileReferences": [
    {
      "fileName": "certificate.pdf",
      "r2Key": "uploads/C1D94680/certificate_123.pdf",
      "fileType": "application/pdf",
      "fileSize": 256789
    }
  ]
}

// Response
{
  "success": true,
  "applicationId": "12345",
  "message": "Application submitted successfully",
  "sharepointSynced": true,
  "emailsSent": true
}
```

### **File Upload API**
```javascript
// POST /api/upload-file
{
  "invitationCode": "C1D94680",
  "fileName": "document.pdf",
  "fileType": "application/pdf",
  "fileSize": 256789
}

// Response
{
  "success": true,
  "uploadUrl": "https://r2-presigned-url...",
  "r2Key": "uploads/C1D94680/document_123.pdf",
  "expiresIn": 3600
}
```

---

## **Security & Data Protection**

### **Data Encryption**
- **In Transit**: All API calls use HTTPS/TLS 1.3
- **At Rest**: D1 database encrypted by default
- **File Storage**: R2 encryption with customer-managed keys
- **SharePoint**: Microsoft 365 enterprise encryption

### **Access Control**
```
Partner Data Isolation:
├── Invitation codes as unique identifiers
├── D1 queries filtered by invitation code
├── R2 file paths include invitation code
└── SharePoint permissions by group membership

API Security:
├── Cloudflare WAF protection
├── Rate limiting by IP address
├── CORS policies restricting origins
└── Input validation and sanitization
```

### **Data Retention**
- **Draft Data**: 30 days after invitation expiry
- **Applications**: Permanent retention in SharePoint
- **Files**: 7 years in R2 storage
- **Logs**: 90 days in Cloudflare Analytics

---

## **Performance Optimization**

### **Database Optimization**
```sql
-- Indexes for fast queries
CREATE INDEX idx_invitations_code ON invitations(code);
CREATE INDEX idx_invitations_status ON invitations(status);
CREATE INDEX idx_applications_invitation ON applications(invitation_code);
CREATE INDEX idx_applications_status ON applications(status);
CREATE INDEX idx_draft_invitation ON draft_data(invitation_code);
```

### **Caching Strategy**
- **Static Assets**: Cloudflare CDN (24 hour cache)
- **API Responses**: Edge caching for invitation validation
- **Database Queries**: D1 connection pooling
- **File Access**: R2 CDN distribution

### **Data Flow Optimization**
- **Async Processing**: Non-blocking API calls
- **Batch Operations**: Bulk SharePoint updates
- **Queue Management**: Power Automate retry logic
- **Error Handling**: Graceful degradation patterns

---

## **Monitoring & Analytics**

### **Data Quality Metrics**
- **Invitation Sync Success Rate**: >99.5%
- **Application Completion Rate**: >90%
- **File Upload Success Rate**: >99%
- **API Response Times**: <200ms median

### **Business Intelligence Tracking**
```
Partner Journey Analytics:
├── Invitation → Click conversion rate
├── Form start → Completion rate
├── Step abandonment points
└── Time to application submission

System Performance:
├── API endpoint response times
├── Database query performance
├── File upload speeds
└── Error rates by component
```

### **Real-Time Dashboards**
- **Cloudflare Analytics**: Traffic and performance
- **D1 Insights**: Database health and usage
- **SharePoint Reports**: Business process metrics
- **Custom Monitoring**: Application-specific KPIs

---

## **Data Recovery & Backup**

### **Backup Strategy**
```
Primary Data (D1):
├── Automatic Cloudflare backups (point-in-time)
├── Daily exports to R2 storage
├── Weekly full database snapshots
└── Cross-region replication

Secondary Data (SharePoint):
├── Microsoft 365 native backups
├── Weekly manual exports
├── Version history (90 days)
└── Recycle bin recovery (93 days)

File Storage (R2):
├── Multiple availability zones
├── Object versioning enabled
├── Lifecycle policies for archival
└── Cross-region replication
```

### **Disaster Recovery**
- **RTO (Recovery Time Objective)**: 15 minutes
- **RPO (Recovery Point Objective)**: 1 hour
- **Failover Process**: Automated via Cloudflare
- **Data Consistency**: ACID compliance maintained

---

## **Future Data Architecture**

### **Planned Enhancements**
- **Real-Time Analytics**: Stream processing for live insights
- **Machine Learning Pipeline**: Partner scoring algorithms
- **Data Lake Integration**: Historical analysis capabilities
- **API Gateway**: Centralized API management

### **Scalability Roadmap**
- **Horizontal Scaling**: Multi-region D1 deployment
- **Event Sourcing**: Immutable event log implementation
- **CQRS Pattern**: Separate read/write data models
- **GraphQL API**: Flexible data querying interface

---

**Document Version**: 1.0
**Last Updated**: September 17, 2025
**Next Review**: November 1, 2025
**Owner**: Saber Renewables Data Architecture Team
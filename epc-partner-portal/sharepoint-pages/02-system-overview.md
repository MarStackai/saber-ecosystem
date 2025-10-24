# System Overview

## Architecture & Components

The EPC Partner Portal integrates multiple technologies to deliver seamless partner onboarding.

---

## System Components

### 1. SharePoint Lists
**Purpose:** Central data repository for partner information

**Lists:**
- **EPC Invitations** - Tracks invitation codes and delivery
- **EPC Onboarding** - Stores submitted applications

**Access:** https://saberrenewables.sharepoint.com/sites/SaberEPCPartners

### 2. Partner Portal
**Purpose:** Public-facing application interface

**Features:**
- Invitation code validation
- Application form submission
- Document upload capability

**URL:** https://epc.saberrenewable.energy

### 3. Power Automate Workflows
**Purpose:** Process automation and email delivery

**Workflows:**
- Invitation Email Flow (SharePoint trigger)
- Application Processing Flow (HTTP trigger)

### 4. Cloudflare Infrastructure
**Purpose:** Hosting and API management

**Components:**
- Cloudflare Pages (static hosting)
- Cloudflare Worker (API endpoint)
- GitHub integration for CI/CD

---

## Data Flow

```
1. Operations Team → Creates Invitation → SharePoint List
                                           ↓
2. Power Automate → Sends Email → Partner Receives Code
                                      ↓
3. Partner → Visits Portal → Enters Code → Submits Application
                                              ↓
4. Cloudflare Worker → Validates → Power Automate → SharePoint
                                                       ↓
5. Confirmation Emails ← Power Automate → Updates Records
```

---

## Integration Points

### SharePoint ↔ Power Automate
- **Method:** Native Microsoft integration
- **Authentication:** Service account
- **Frequency:** Real-time triggers

### Portal ↔ Cloudflare Worker
- **Method:** JavaScript fetch API
- **Endpoint:** /api/submit
- **Format:** JSON

### Cloudflare Worker ↔ Power Automate
- **Method:** HTTP POST
- **Authentication:** Webhook URL with signature
- **Response:** Synchronous

---

## Security Model

### Authentication
- **SharePoint:** Azure AD with MFA
- **PowerShell Scripts:** Certificate authentication
- **Portal:** Public with invitation code validation
- **API:** CORS restricted to portal domain

### Data Protection
- Invitation codes expire after 30 days
- Single-use code enforcement
- Audit trail for all operations
- No sensitive data in public endpoints

---

## Performance Specifications

### Response Times
- **Portal Load:** < 2 seconds
- **Code Validation:** < 1 second
- **Application Submission:** < 5 seconds
- **Email Delivery:** < 2 minutes

### Capacity
- **Concurrent Users:** 100
- **Daily Applications:** 500
- **Storage:** 10GB SharePoint quota

---

## Maintenance Windows

**Scheduled Maintenance:** Sundays 02:00-04:00 GMT
**Emergency Updates:** As required with 1-hour notice

---

[← Back to Home](./01-epc-home.md) | [Next: Quick Start Guide →](./03-quick-start.md)

**Version:** 1.0 | **Last Updated:** September 2025
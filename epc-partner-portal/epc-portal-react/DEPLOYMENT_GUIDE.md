# SharePoint Schema Deployment Guide

## Status: ✅ Ready for Manual Deployment

The SharePoint schema provisioning script is ready but requires manual execution due to authentication requirements. Here's how to deploy:

## Prerequisites

1. **PnP PowerShell Module**
   ```powershell
   Install-Module -Name PnP.PowerShell -Scope CurrentUser
   ```

2. **SharePoint Admin Rights**
   - Site Collection Admin on `https://saberrenewables.sharepoint.com/sites/SaberEPCPartners`
   - Or sufficient permissions to create lists and fields

## Deployment Steps

### 1. Run the Provisioning Script

```powershell
# Navigate to the project directory
cd C:\path\to\epc-portal-react

# Execute the provisioning script
.\provision-epc-onboarding.ps1 -SiteUrl "https://saberrenewables.sharepoint.com/sites/SaberEPCPartners"
```

You'll be prompted for authentication - use your SharePoint admin credentials.

### 2. Expected Output

```
Creating list 'EPC Onboarding'...
Provisioning fields...
Creating library 'EPC Onboarding Evidence'...
Schema provisioning complete.
```

### 3. Verify Deployment

After successful deployment, verify these components exist:

#### SharePoint List: "EPC Onboarding"
- **Location**: `Lists/EPC Onboarding`
- **Fields**: 60+ custom fields across 6 form sections
- **Views**: 
  - All Items (default)
  - Submissions
  - Under Review  
  - Approved

#### Document Library: "EPC Onboarding Evidence"
- **Purpose**: Stores uploaded certificates, policies, CVs
- **Custom Fields**:
  - `EpcItemId` (Number) - Links files to form submissions
  - `EvidenceSection` (Choice) - Categorizes file types

## What Gets Created

### Form Fields by Section

#### Section 1: Company Information (8 fields)
- CompanyName, TradingName, RegisteredOffice, HeadOffice
- CompanyRegNo, VATNumber, ParentCompany, YearsTrading

#### Section 2: Contact & Services (12 fields)  
- Primary contact: Name, Title, Phone, Email
- Services: Multi-choice services, specializations, software tools
- Roles: Principal contractor/designer flags with conditional fields

#### Section 3: Certifications & Insurance (11 fields)
- ISO certifications (multi-choice)
- Construction schemes (multi-choice)
- NICEIC, MCS flags
- Insurance types with expiry dates

#### Section 4: Health, Safety & Policies (13 fields)
- HSE notices, RIDDOR incidents
- Policy date tracking (H&S, Environmental, Modern Slavery, etc.)
- Training and evidence tracking

#### Section 5: Delivery Capability (4 fields)
- Coverage areas (nationwide flag + regions)
- Resource planning approach
- Client reference notes

#### Section 6: Legal & Agreement (9 fields)
- Legal compliance tracking
- Agreement confirmations (5 required checkboxes)
- Additional information

#### System Fields (3 fields)
- SubmissionStatus (Choice): Draft/Submitted/Under Review/Approved/Rejected
- Reviewer (Person)
- ReviewNotes (Multi-line text)

## Next Steps After Deployment

1. **Test the Schema**
   - Manually create a test item in the EPC Onboarding list
   - Verify all fields are accessible
   - Test file uploads to the Evidence library

2. **Update Cloudflare Worker** (Next Task)
   - Map new SharePoint field names to API payload
   - Handle multi-select field transformations
   - Implement conditional field logic

3. **Update Power Automate Flow**
   - Add new field mappings to notification templates
   - Handle extended form data in approval workflows

## Troubleshooting

### Authentication Issues
If you get authentication errors:
```powershell
Connect-PnPOnline -Url "https://saberrenewables.sharepoint.com/sites/SaberEPCPartners" -Interactive
```

### Missing Permissions
Ensure you have:
- Site Collection Administrator rights, OR
- Full Control permissions on the site

### PnP PowerShell Version
Use the latest version:
```powershell
Update-Module -Name PnP.PowerShell
```

## Schema Summary

**Total Fields**: 60+ custom fields
**List Types**: 1 main list + 1 document library  
**Views**: 4 custom views
**Field Types**: Text, Number, Boolean, DateTime, Choice, MultiChoice, Note, User
**Integration Points**: Ready for Cloudflare Worker + Power Automate

The schema is production-ready and follows SharePoint best practices with proper indexing, validation, and organization.
# EPC Partner Onboarding - SharePoint Operations Guide

## System Purpose
This system enables efficient partner onboarding through automated workflows. It reduces onboarding time from 14 days to 3 days whilst ensuring compliance with Saber's quality standards.

## Quick Links
- **SharePoint Site:** https://saberrenewables.sharepoint.com/sites/SaberEPCPartners
- **Portal:** https://epc.saberrenewable.energy
- **Support:** sysadmin@saberrenewables.com

## SharePoint Lists Structure

### EPC Invitations List
Manages partner invitation codes and tracks email delivery.

**Required Fields:**
- **Code** - Unique 8-character invitation code
- **CompanyName** - Prospective partner company
- **ContactName** - Primary contact person
- **ContactEmail** - Email for invitation delivery
- **ExpiryDate** - Invitation validity period (default: 30 days)
- **Used** - Whether code has been redeemed
- **InvitationSent** - Email delivery status
- **InvitationSentDate** - When invitation was sent

### EPC Onboarding List
Captures partner applications for compliance review and approval.

**Data Structure:**
- **CompanyName** - Applicant company name
- **Status** - Application status (New/InReview/Approved/Rejected)
- **PrimaryContactName** - Main point of contact
- **PrimaryContactEmail** - Contact email
- **SubmissionDate** - When application was received
- **DocumentsJSON** - Uploaded document references

---

## Operational Workflows

### Creating Partner Invitations

#### Automated Method (Recommended)
```bash
./create-invitation.ps1 -CompanyName "Partner Company" -ContactEmail "contact@partner.com" -ContactName "John Smith"
```
Expected outcome: Partner receives invitation within 2 minutes

#### Manual SharePoint Entry
1. Navigate to **EPC Invitations** list
2. Click **+ New**
3. Enter required information:
   - Generate unique 8-character code (uppercase letters/numbers)
   - Complete company and contact details
   - Set expiry date (typically 30 days)
4. Save entry
5. Workflow triggers email delivery

### Invitation Management

#### Active Invitation Review
1. Open **EPC Invitations** list
2. Filter by **Used** = No
3. Check **ExpiryDate** for validity

#### Resending Invitations
Steps:
1. Locate invitation in list
2. Edit entry
3. Set **InvitationSent** to No
4. Save

Expected outcome: Email resent within 2 minutes

#### Cancel Invitation
1. Find invitation entry
2. Edit item
3. Set **Status** to "Cancelled" (if field exists)
4. Or set **ExpiryDate** to past date

### Application Processing

#### New Application Review
1. Open **EPC Onboarding** list
2. Filter by **Status** = "New"
3. Review submitted information
4. Access documents via DocumentsJSON field

#### Status Updates
Steps:
1. Select application entry
2. Edit item
3. Update **Status**:
   - **InReview** - Compliance check in progress
   - **Approved** - Partner meets requirements
   - **Rejected** - Does not meet current criteria
4. Document decision rationale
5. Save

Expected outcome: Partner notified within 24 hours

---

## Automated Workflows

### Invitation Email Workflow
**Trigger:** New item created in EPC Invitations
**Actions:**
1. Send branded partner invitation
2. Update delivery status
3. Log timestamp

**Success criteria:** Email delivered within 2 minutes

### Application Submission Workflow
**Trigger:** Portal form submission
**Actions:**
1. Validate invitation code
2. Create onboarding record
3. Mark code as used
4. Send confirmations

**Success criteria:** SharePoint entry created within 30 seconds

---

## Operating Standards

### Invitation Management
- Weekly review of pending invitations
- System generates unique 8-character codes
- Document cancellation rationale
- Monitor delivery status daily

### Application Processing
- Review within 3 business days
- Maintain clear audit trail
- Document all decisions
- Quarterly archival process

### Data Hygiene
- Remove test entries from production lists
- Update contact information when changes occur
- Monitor for duplicate submissions
- Regular backup of list data

---

## Issue Resolution

### Email Delivery Failure
- Check Power Automate run history
- Verify ContactEmail is valid
- Ensure InvitationSent = No to trigger flow
- Check spam folders

### Invalid Code Issues
- Verify code exists in EPC Invitations
- Check Used status (must be No)
- Confirm ExpiryDate hasn't passed
- Ensure exact 8-character match

### Missing Applications
- Check Power Automate execution
- Verify invitation code was valid
- Review Cloudflare Worker logs
- Check both SharePoint lists

---

## Compliance & Security

### Access Management
- Role-based list permissions
- Certificate authentication (App ID: bbbfe394-7cff-4ac9-9e01-33cbf116b930)
- Automated audit logging

### Data Protection
- No sensitive financial data in lists
- Email addresses protected
- Document links secured
- Regular access reviews

---

## Performance Metrics

### Key Indicators
- Invitations sent
- Conversion rate (invitations to applications)
- Average processing time
- Approval/rejection ratio

### Monthly Reporting Process
Steps:
1. Export both SharePoint lists
2. Generate pivot analysis
3. Calculate conversion metrics
4. Distribute to stakeholders

Expected outcome: Report delivered by 5th of each month

---

## Support Structure

### Technical Support
- **Level 1:** This documentation
- **Level 2:** sysadmin@saberrenewables.com (4-hour response)
- **Escalation:** IT Service Desk

### Business Support
- **Partner queries:** partners@saberrenewables.com
- **Operational issues:** Team lead escalation

---

## Quick Reference

### Useful PowerShell Commands
```powershell
# Create single invitation
./create-invitation.ps1 -CompanyName "Company" -ContactEmail "email" -ContactName "Name"

# Batch create invitations
./batch-create-invitations.ps1

# Test system
./test-complete-system.sh
```

### Operational Cadence
- **Daily:** Review new applications
- **Weekly:** Audit pending invitations
- **Monthly:** Generate performance report
- **Quarterly:** Archive completed records

---

**Version:** 1.0
**Last Updated:** September 2025
**Next Review:** December 2025
**Owner:** Business Operations Team
# 📘 EPC Partner Onboarding - Operations Team Guide

## 🚀 Quick Start Guide

### Your Main URLs
- **Invitations List**: https://saberrenewables.sharepoint.com/sites/SaberEPCPartners/Lists/EPC%20Invitations
- **Submissions List**: https://saberrenewables.sharepoint.com/sites/SaberEPCPartners/Lists/EPC%20Onboarding  
- **Form Page**: https://saberrenewables.sharepoint.com/sites/SaberEPCPartners/SiteAssets/EPCForm/verify-access.html

---

## 📋 Daily Operations Tasks

### 1️⃣ **Send New Invitations**

#### Method A: Using SharePoint List (EASIEST)
1. Go to **[EPC Invitations List](https://saberrenewables.sharepoint.com/sites/SaberEPCPartners/Lists/EPC%20Invitations)**
2. Click **"+ New"**
3. Fill in:
   - **Company Name**: Partner company name
   - **Contact Email**: Partner's email address
   - **Status**: Set to "Pending"
   - **Expiry Date**: Set 30 days from today
4. Click **Save**
5. Copy the generated **Invite Code**
6. Email the partner with:
   - Link: `https://saberrenewables.sharepoint.com/sites/SaberEPCPartners/SiteAssets/EPCForm/verify-access.html`
   - Their unique code

#### Method B: Bulk Invitations (Advanced)
1. Create Excel file with columns: CompanyName, Email
2. Run PowerShell script (see Advanced section)

### 2️⃣ **Monitor Submissions**

1. Go to **[EPC Onboarding List](https://saberrenewables.sharepoint.com/sites/SaberEPCPartners/Lists/EPC%20Onboarding)**
2. Filter by **Status = "Submitted"**
3. Review new applications
4. Check **SubmissionFolder** for uploaded documents

### 3️⃣ **Process Applications**

1. Open submission from list
2. Review all fields
3. Check documents in **EPC Submissions** folder
4. Update Status:
   - ✅ **Approved** - Partner accepted
   - ⏸️ **Under Review** - Need more info
   - ❌ **Rejected** - Does not meet criteria
5. Send follow-up email to partner

---

## 📊 Managing Invitations

### View All Invitations
1. Navigate to **EPC Invitations** list
2. Use views:
   - **Active Invitations** - Not expired
   - **All Items** - Complete history
   - **Expired** - Past expiry date

### Invitation Statuses
- 🔵 **Pending** - Created but not sent
- 📧 **Sent** - Email delivered
- 👁️ **Accessed** - Partner viewed form
- ✅ **Submitted** - Application completed
- ⏰ **Expired** - Past expiry date

### Resend/Extend Invitations
1. Find invitation in list
2. Click item to edit
3. Update **Expiry Date** (add 30 days)
4. Generate new **Invite Code** if needed
5. Update **Status** to "Sent"
6. Email partner with new details

---

## 📁 Document Management

### Where Documents Are Stored
- **Location**: `EPC Submissions` document library
- **Structure**: `{ID} - {Company Name}/` folders
- Each partner's documents in their own folder

### Accessing Documents
1. From submission: Click **SubmissionFolder** link
2. Direct: Go to **EPC Submissions** library
3. Find folder named with ID and company

---

## 📧 Email Templates

### Initial Invitation
```
Subject: Invitation to Join Saber's EPC Partner Network

Dear [Company Name],

You're invited to join Saber Renewables' certified EPC partner network.

To complete your application:
1. Visit: https://saberrenewables.sharepoint.com/sites/SaberEPCPartners/SiteAssets/EPCForm/verify-access.html
2. Enter your email: [Email]
3. Enter code: [INVITE CODE]

This invitation expires on [Expiry Date].

Please have ready:
- Company registration details
- Insurance certificates
- ISO certifications (if applicable)
- HSEQ policies

The form takes 15-20 minutes to complete.

Best regards,
Saber Partner Team
```

### Approval Email
```
Subject: Welcome to Saber's EPC Partner Network

Dear [Company Name],

Congratulations! Your application has been approved.

Next steps:
1. We'll send your partner agreement within 2 business days
2. Complete onboarding training (link to follow)
3. Access partner portal for project opportunities

Welcome to the Saber family!

Best regards,
Saber Partner Team
```

### Request More Information
```
Subject: EPC Partner Application - Additional Information Required

Dear [Company Name],

Thank you for your application. We need additional information:

[List specific items needed]

Please reply with the requested information within 5 business days.

Best regards,
Saber Partner Team
```

---

## 🔧 Troubleshooting

### Partner Can't Access Form
1. Check invitation hasn't expired
2. Verify email address matches exactly
3. Ensure code is correct (case-sensitive)
4. Create new invitation if needed

### Documents Not Uploading
1. Check file size (max 10MB each)
2. Verify file type (PDF, DOC, DOCX, JPG, PNG)
3. Try different browser
4. Ask partner to zip files if multiple

### Can't See Submissions
1. Refresh the list page
2. Check your view filter
3. Ensure you have correct permissions
4. Contact IT if access issues persist

---

## 📈 Reports & Analytics

### Weekly Metrics to Track
- New invitations sent
- Form completion rate
- Average time to review
- Approval vs rejection rate

### Export Data
1. Go to either list
2. Click **Export to Excel**
3. Use for reporting

### Key Performance Indicators
- **Target**: 80% invitation to submission rate
- **Goal**: 48-hour review turnaround
- **Quality**: 90% approval rate

---

## 🎯 Best Practices

### DO's ✅
- Send invitations promptly after partner inquiry
- Review applications within 48 hours
- Keep notes in the Notes field
- Follow up on expired invitations
- Archive old records quarterly

### DON'Ts ❌
- Don't share invitation codes between partners
- Don't delete records (archive instead)
- Don't approve without document review
- Don't let invitations expire without follow-up

---

## 🚨 Emergency Contacts

- **SharePoint Admin**: IT Support (ext. 1234)
- **Technical Issues**: support@saberrenewables.com
- **Partner Questions**: Forward to partners@saberrenewables.com
- **Escalation**: Operations Manager

---

## 📝 Quick Reference Card

| Task | Where to Go | Action |
|------|------------|--------|
| Send invitation | EPC Invitations list | + New → Fill form → Save |
| Check submissions | EPC Onboarding list | Filter: Status = Submitted |
| View documents | EPC Submissions library | Open partner folder |
| Update status | EPC Onboarding list | Edit item → Change Status |
| Resend code | EPC Invitations list | Edit → New code → Save |
| Export data | Any list | Export to Excel button |

---

## 🎓 Training Videos

1. **[How to Send Invitations]** (5 min)
2. **[Processing Applications]** (8 min)
3. **[Managing Documents]** (4 min)
4. **[Generating Reports]** (6 min)

*(Videos to be created and linked)*

---

## 💡 Tips for Success

1. **Check daily** at 9 AM and 3 PM for new submissions
2. **Use filters** to see only what needs attention
3. **Add to calendar** - Set reminders for invitation expiries
4. **Keep notes** - Document all partner interactions
5. **Team communication** - Use Teams channel for questions

---

## 📅 Standard Operating Procedure

### Morning Routine (9:00 AM)
1. Check new submissions (5 min)
2. Review pending applications (20 min)
3. Send new invitations from queue (10 min)
4. Update statuses (5 min)

### Afternoon Check (3:00 PM)
1. Follow up on "Under Review" items
2. Check for expired invitations
3. Prepare next day's invitation list

### Weekly Tasks (Friday)
1. Export weekly metrics
2. Archive completed applications
3. Review and clean up expired invitations
4. Send summary report to management

---

## 🔐 Security Reminders

- Never share invitation codes publicly
- Each partner gets unique code
- Codes expire after 30 days
- Report suspicious activity immediately
- Don't process applications from personal email

---

## 📞 Need Help?

**First Steps:**
1. Check this guide
2. Try refreshing the page
3. Clear browser cache

**Still stuck?**
- Email: epc-support@saberrenewables.com
- Teams: #epc-partner-support channel
- Phone: Extension 5678

---

*Last updated: September 2024*
*Version: 1.0*
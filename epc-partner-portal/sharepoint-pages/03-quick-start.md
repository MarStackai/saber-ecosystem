# Quick Start Guide

## Start onboarding a partner in under 5 minutes

---

## Prerequisites

Before you begin, ensure you have:
- ✅ Access to SharePoint EPC Partners site
- ✅ PowerShell installed (for automated method)
- ✅ Partner company details and contact email

---

## Method 1: Automated (Recommended)

### Step 1: Open PowerShell
```powershell
cd /home/marstack/saber_business_ops
```

### Step 2: Run Invitation Script
```powershell
./create-invitation.ps1 -CompanyName "Partner Ltd" -ContactEmail "contact@partner.com" -ContactName "John Smith"
```

### Step 3: Confirm Success
**Expected output:**
- ✅ Unique 8-character code generated
- ✅ SharePoint entry created
- ✅ Email sent automatically

**Time required:** 2 minutes

---

## Method 2: SharePoint Direct

### Step 1: Navigate to Invitations List
1. Go to [SharePoint EPC Partners](https://saberrenewables.sharepoint.com/sites/SaberEPCPartners)
2. Click **EPC Invitations**
3. Select **+ New**

### Step 2: Complete Form
**Required fields:**
- **Code:** Generate 8-character code (e.g., ABCD1234)
- **CompanyName:** Partner company name
- **ContactName:** Primary contact
- **ContactEmail:** Valid email address
- **ExpiryDate:** Today + 30 days

### Step 3: Save & Verify
1. Click **Save**
2. Confirm email sent (check Power Automate)

**Time required:** 3-4 minutes

---

## What Happens Next?

### Automatic Actions
1. ✉️ Partner receives branded invitation email
2. 🔗 Email contains portal link and unique code
3. 📝 Partner completes application
4. ✅ System creates onboarding record

### Your Actions
1. Monitor application in **EPC Onboarding** list
2. Review submitted documents
3. Update status to **Approved** or **InReview**
4. Partner receives confirmation

---

## Common Tasks

### Check Invitation Status
```powershell
Get-PnPListItem -List "EPC Invitations" | Where-Object {$_.FieldValues.Code -eq "ABCD1234"}
```

### View Recent Applications
1. Open **EPC Onboarding** list
2. Sort by **SubmissionDate** (descending)
3. Filter **Status** = "New"

### Resend Invitation Email
1. Find invitation in list
2. Edit item
3. Set **InvitationSent** = No
4. Save (triggers resend)

---

## Quick Tips

💡 **Code Generation:** Use uppercase letters and numbers only  
💡 **Batch Invitations:** Use `batch-create-invitations.ps1` for multiple partners  
💡 **Email Issues:** Check recipient's spam folder  
💡 **Code Problems:** Verify code hasn't been used or expired  

---

## Need Help?

**Can't access SharePoint?**  
Contact: sysadmin@saberrenewables.com

**PowerShell script errors?**  
Check certificate: `~/.certs/SaberEPCAutomation.pfx`

**Partner didn't receive email?**  
Review Power Automate run history

---

[← Back to Home](./01-epc-home.md) | [Next: Access & Permissions →](./04-access-permissions.md)

**Version:** 1.0 | **Last Updated:** September 2025
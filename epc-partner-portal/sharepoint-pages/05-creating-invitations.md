# Creating Partner Invitations

## Complete guide to invitation generation and management

---

## Overview

Partner invitations are the entry point to our onboarding system. Each invitation includes a unique 8-character code that grants one-time access to the application portal.

---

## Invitation Methods

### PowerShell Automation (Preferred)

#### Single Invitation
```powershell
./create-invitation.ps1 `
    -CompanyName "Solar Excellence Ltd" `
    -ContactEmail "john@solarexcellence.com" `
    -ContactName "John Smith" `
    -DaysValid 30
```

**Benefits:**
- Automatic unique code generation
- Duplicate checking
- Immediate email trigger
- Error handling

#### Batch Invitations
```powershell
./batch-create-invitations.ps1
```

Edit the script to include multiple partners, then run. Creates CSV record of all generated codes.

### Manual SharePoint Entry

#### Step-by-Step Process

1. **Access List**
   - Navigate to [EPC Invitations](https://saberrenewables.sharepoint.com/sites/SaberEPCPartners/Lists/EPC%20Invitations)
   - Click **+ New**

2. **Generate Code**
   - Format: 8 characters
   - Use: A-Z and 2-9 only
   - Avoid: 0, O, 1, I (confusing characters)
   - Example: ABCD5678

3. **Complete Fields**
   ```
   Code: [Generated code]
   CompanyName: [Partner company name]
   ContactName: [Primary contact]
   ContactEmail: [Valid email]
   ExpiryDate: [Today + 30 days]
   Used: No
   InvitationSent: No
   ```

4. **Save & Verify**
   - Click **Save**
   - Check Power Automate for email trigger
   - Verify delivery status

---

## Code Generation Rules

### Valid Format
- **Length:** Exactly 8 characters
- **Characters:** A-Z (uppercase), 2-9
- **Structure:** Random alphanumeric

### Invalid Examples
❌ TEST123 (only 7 characters)  
❌ test1234 (lowercase)  
❌ TEST-001 (contains hyphen)  
❌ 12345678 (numbers only)  

### Valid Examples
✅ ABCD1234  
✅ WXYZ9876  
✅ TEAM2025  
✅ PART5678  

---

## Invitation Lifecycle

```
Created → Email Sent → Partner Uses Code → Marked as Used
   ↓           ↓              ↓                    ↓
30 days    2 minutes      Variable           Immediate
```

### Status Tracking

| Status | Description | Action Required |
|--------|-------------|-----------------|
| Active | Ready for use | None |
| Used | Code redeemed | None |
| Expired | Past expiry date | Create new if needed |
| Cancelled | Manually cancelled | Document reason |

---

## Email Delivery

### Automatic Process
1. New invitation saved in SharePoint
2. Power Automate detects new item
3. Email sent within 2 minutes
4. InvitationSent flag updated

### Email Contains
- Personalised greeting
- Company name
- Unique invitation code
- Portal link
- Expiry date
- Instructions

### Delivery Issues
If email not received:
1. Check **InvitationSent** field
2. Review Power Automate history
3. Verify email address
4. Check spam folders
5. Manually resend if needed

---

## Managing Existing Invitations

### View All Invitations
```powershell
Get-PnPListItem -List "EPC Invitations" | Format-Table Code, CompanyName, Used, ExpiryDate
```

### Find Specific Code
```powershell
Get-PnPListItem -List "EPC Invitations" | Where-Object {$_.FieldValues.Code -eq "ABCD1234"}
```

### Resend Invitation
1. Locate invitation in SharePoint
2. Edit item
3. Set **InvitationSent** = No
4. Save (triggers new email)

### Cancel Invitation
1. Find invitation
2. Edit item
3. Set **ExpiryDate** to yesterday
4. Add note explaining cancellation
5. Save

### Extend Expiry
1. Locate invitation
2. Edit item
3. Update **ExpiryDate**
4. Save
5. Notify partner of extension

---

## Best Practices

### DO
✅ Generate codes for specific partners only  
✅ Set reasonable expiry dates (30 days standard)  
✅ Document any manual changes  
✅ Monitor delivery status daily  
✅ Archive expired invitations quarterly  

### DON'T
❌ Create generic "test" invitations in production  
❌ Share codes via insecure channels  
❌ Reuse codes from expired invitations  
❌ Extend expiry multiple times  
❌ Delete invitation records  

---

## Reporting

### Weekly Metrics
- Invitations sent
- Codes used
- Conversion rate
- Average time to use

### Monthly Analysis
```powershell
# Export for analysis
$invitations = Get-PnPListItem -List "EPC Invitations"
$invitations | Export-Csv "invitations-$(Get-Date -Format 'yyyy-MM').csv"
```

---

## Troubleshooting

### "Code already exists"
- System preventing duplicates
- Script will generate new code automatically

### "Email not sending"
1. Check Power Automate is ON
2. Verify InvitationSent field
3. Check email address format
4. Review flow run history

### "Partner can't use code"
1. Verify code exactly matches (case-sensitive)
2. Check Used status (must be No)
3. Confirm not expired
4. Test code yourself

---

[← Back to Home](./01-epc-home.md) | [Next: Processing Applications →](./06-processing-applications.md)

**Version:** 1.0 | **Last Updated:** September 2025
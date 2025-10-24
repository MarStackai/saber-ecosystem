# Troubleshooting Guide

## Quick solutions to common issues

---

## Invitation Issues

### Problem: Invitation email not sent

**Symptoms:**
- Partner reports no email received
- InvitationSent field still shows "No"

**Solutions:**
1. **Check Power Automate**
   - Navigate to [Power Automate](https://make.powerautomate.com)
   - Review "EPC Partner Invitation Email" flow
   - Check run history for errors
   
2. **Verify Email Address**
   ```powershell
   Get-PnPListItem -List "EPC Invitations" | 
       Where-Object {$_.FieldValues.Code -eq "CODEHERE"} |
       Select-Object -ExpandProperty FieldValues
   ```
   
3. **Manual Resend**
   - Edit invitation in SharePoint
   - Set InvitationSent = No
   - Save (triggers resend)

4. **Check Spam**
   - Ask partner to check spam/junk folders
   - Whitelist: noreply@saberrenewables.com

---

### Problem: Code not working on portal

**Symptoms:**
- "Invalid or expired invitation code" error
- Code rejected at portal

**Solutions:**
1. **Verify Code Status**
   ```powershell
   $code = "ABCD1234"
   Get-PnPListItem -List "EPC Invitations" | 
       Where-Object {$_.FieldValues.Code -eq $code} |
       Select-Object -ExpandProperty FieldValues
   ```
   Check:
   - Used = No
   - ExpiryDate > Today
   - Code matches exactly (case-sensitive)

2. **Test Code Directly**
   ```bash
   curl -X POST https://epc.saberrenewable.energy/api/validate-code \
       -H "Content-Type: application/json" \
       -d '{"code": "ABCD1234"}'
   ```

3. **Create New Code**
   ```powershell
   ./create-invitation.ps1 -CompanyName "Company" -ContactEmail "email" -ContactName "Name"
   ```

---

## Application Processing Issues

### Problem: Application not appearing in SharePoint

**Symptoms:**
- Partner submitted form
- No entry in EPC Onboarding list

**Solutions:**
1. **Check Power Automate**
   - Review "EPC Application Submission Processor" flow
   - Look for failed runs
   - Check error messages

2. **Verify Cloudflare Worker**
   - Check Worker logs in Cloudflare dashboard
   - Test API endpoint directly

3. **Manual Entry**
   - Create entry directly in SharePoint
   - Mark invitation as Used
   - Notify partner of issue resolution

---

### Problem: Duplicate applications

**Symptoms:**
- Multiple entries for same company
- Same code used multiple times

**Solutions:**
1. **Identify Duplicates**
   ```powershell
   Get-PnPListItem -List "EPC Onboarding" | 
       Group-Object {$_.FieldValues.CompanyName} | 
       Where-Object {$_.Count -gt 1}
   ```

2. **Merge Records**
   - Keep most recent submission
   - Archive older entries
   - Update invitation status

3. **Prevent Future Issues**
   - Ensure code marked as Used immediately
   - Add duplicate checking to workflow

---

## PowerShell Script Errors

### Problem: Certificate authentication fails

**Error Message:**
```
The specified certificate could not be read
```

**Solutions:**
1. **Verify Certificate**
   ```powershell
   Test-Path "$HOME/.certs/SaberEPCAutomation.pfx"
   ```

2. **Check Password**
   ```powershell
   $password = ConvertTo-SecureString -String "P@ssw0rd123!" -AsPlainText -Force
   $cert = Get-PfxCertificate -FilePath "$HOME/.certs/SaberEPCAutomation.pfx" -Password $password
   ```

3. **Recreate Certificate**
   - Generate new certificate
   - Upload to Azure AD
   - Update scripts with new thumbprint

---

### Problem: "Column 'Status' does not exist"

**Error Message:**
```
Column 'Status' does not exist
```

**Solutions:**
1. **Scripts handle automatically**
   - Modern scripts try with and without Status
   - No action needed

2. **Add Status Column (Optional)**
   - Go to List Settings
   - Create Column
   - Type: Choice
   - Values: Active, Used, Expired, Cancelled

---

## Power Automate Issues

### Problem: Flow not triggering

**Symptoms:**
- New items created but flow doesn't run
- No entries in run history

**Solutions:**
1. **Check Flow Status**
   - Ensure flow is ON
   - Check connections are valid
   - Review trigger conditions

2. **Test Manually**
   - Use "Test" feature in Power Automate
   - Create test item in SharePoint
   - Monitor execution

3. **Reconnect SharePoint**
   - Edit flow
   - Remove and re-add SharePoint connection
   - Save and test

---

### Problem: HTTP trigger returns 500 error

**Symptoms:**
- API calls fail with Internal Server Error
- Flow shows in run history but fails

**Solutions:**
1. **Check Request Format**
   ```json
   {
     "invitationCode": "ABCD1234",
     "companyName": "Test Company",
     "contactEmail": "test@example.com"
   }
   ```

2. **Verify Schema**
   - Edit flow
   - Check JSON schema in trigger
   - Update if fields missing

3. **Test with Postman**
   - Use exact URL from flow
   - Send test payload
   - Review response

---

## Performance Issues

### Problem: Slow SharePoint queries

**Symptoms:**
- Scripts timeout
- Long delays loading lists

**Solutions:**
1. **Use Pagination**
   ```powershell
   Get-PnPListItem -List "EPC Invitations" -PageSize 100
   ```

2. **Add Indexes**
   - Go to List Settings
   - Indexed Columns
   - Add index on Code, CompanyName

3. **Archive Old Data**
   ```powershell
   $oldItems = Get-PnPListItem -List "EPC Invitations" | 
       Where-Object {$_.FieldValues.ExpiryDate -lt (Get-Date).AddDays(-90)}
   # Export and remove
   ```

---

## Email Delivery Issues

### Problem: Emails delayed or not delivered

**Symptoms:**
- Long delays between trigger and delivery
- Some emails never arrive

**Solutions:**
1. **Check Email Quotas**
   - Office 365 daily limits
   - Power Automate throttling

2. **Verify SPF/DKIM**
   - DNS records configured
   - Domain authentication

3. **Use Alternative Sender**
   - Change from address
   - Use dedicated mailbox

---

## Data Integrity Issues

### Problem: Missing or corrupted data

**Symptoms:**
- Fields blank when shouldn't be
- Data doesn't match between systems

**Solutions:**
1. **Audit Trail Review**
   ```powershell
   Get-PnPListItem -List "EPC Onboarding" -Id 123 | 
       Select-Object -ExpandProperty FieldValues
   ```

2. **Restore from Version History**
   - SharePoint maintains versions
   - Restore previous version if needed

3. **Validation Rules**
   - Add column validation
   - Implement Power Automate checks

---

## Emergency Procedures

### System Complete Failure

1. **Immediate Actions:**
   - Switch to manual process
   - Document all invitations offline
   - Notify partners of delays

2. **Diagnosis:**
   - Check all system components
   - Review error logs
   - Identify failure point

3. **Recovery:**
   - Restore from backup
   - Rebuild workflows if needed
   - Test thoroughly before resuming

### Data Loss

1. **SharePoint Recovery:**
   - Check Recycle Bin
   - Contact Microsoft Support
   - Restore from backup

2. **Document Recovery:**
   - Check version history
   - Review audit logs
   - Reconstruct from emails

---

## Escalation Path

### Level 1: Self-Service
- This documentation
- Power Automate run history
- SharePoint audit logs

### Level 2: Technical Support
- **Contact:** sysadmin@saberrenewables.com
- **Response:** 4 hours
- **Include:** Error messages, screenshots

### Level 3: Microsoft Support
- SharePoint issues
- Power Automate platform problems
- Azure AD authentication

### Level 4: Development Team
- Custom script modifications
- Workflow redesign
- System architecture changes

---

## Preventive Measures

### Daily Checks
- Review failed Power Automate runs
- Check for pending invitations
- Monitor email delivery status

### Weekly Maintenance
- Archive expired invitations
- Review error patterns
- Update documentation

### Monthly Reviews
- Performance analysis
- Capacity planning
- Security audit

---

[← Back to Home](./01-epc-home.md) | [Next: FAQs →](./15-faqs.md)

**Version:** 1.0 | **Last Updated:** September 2025
# Power Automate Workflow Specification
## EPC Partner Invitation with D1 Sync

### **Trigger**: When an item is created in "EPC Invitations" SharePoint list

### **Actions**:

#### 1. **Generate 8-Character Invitation Code**
```
Set variable: InvitationCode
Value: substring(guid(), 0, 8)
Transform: UPPERCASE
Example: "ABC12345"
```

#### 2. **Update SharePoint Item** 
```
Update item in "EPC Invitations"
Set "Invitation Code" = @{variables('InvitationCode')}
Set "Invitation Status" = "Sent"
Set "Code Expiry Date" = @{addDays(utcNow(), 30)}
```

#### 3. **Sync Invitation to Portal Database**
```
HTTP POST Request:
URL: https://epc.saberrenewable.energy/api/sync-invitation
Headers:
  Content-Type: application/json
  User-Agent: Power-Automate-EPC-Sync/1.0

Body:
{
  "Title": "@{triggerOutputs()?['body/Title']}",
  "CompanyName": "@{triggerOutputs()?['body/CompanyName']}",
  "ContactEmail": "@{triggerOutputs()?['body/ContactEmail']}",
  "Notes": "@{triggerOutputs()?['body/Notes']}",
  "AuthCode": "@{variables('InvitationCode')}"
}
```

#### 4. **Send Invitation Email**
```
Send Email (Outlook/Exchange):
To: @{triggerOutputs()?['body/ContactEmail']}
Subject: "Saber Renewables EPC Partner Application - Your Access Code"

Body (HTML):
```html
<h2>Welcome to the Saber Renewables EPC Partner Program</h2>

<p>Dear @{triggerOutputs()?['body/Title']},</p>

<p>Thank you for your interest in becoming an EPC partner with Saber Renewables.</p>

<p><strong>Your invitation code is: <span style="background: #f0f8ff; padding: 8px; font-size: 18px; font-weight: bold; color: #0066cc;">@{variables('InvitationCode')}</span></strong></p>

<p>To complete your application:</p>
<ol>
  <li>Visit: <a href="https://epc.saberrenewable.energy/apply">https://epc.saberrenewable.energy/apply</a></li>
  <li>Enter your 8-character invitation code: <strong>@{variables('InvitationCode')}</strong></li>
  <li>Complete the multi-step application form</li>
  <li>Upload required documents and certificates</li>
</ol>

<p>Your invitation code expires in 30 days. If you need assistance, contact our team at sysadmin@saberrenewables.com</p>

<p>We look forward to working with you!</p>

<p>Best regards,<br/>
Saber Renewables Operations Team</p>
```

#### 5. **Error Handling**
```
If HTTP request to sync-invitation fails:
- Send notification to operations team
- Set SharePoint item status to "Sync Failed" 
- Log error details in Notes field
```

#### 6. **Success Confirmation**
```
If all steps successful:
- Update SharePoint invitation status to "Sent"
- Log success timestamp in Notes field
```

---

## **Testing the Workflow**

### Test SharePoint List Item:
```
Title: "Mr."
Company Name: "Test Solar Solutions Ltd"
Contact Email: "test@example.com"  
Notes: "Test invitation for workflow validation"
```

### Expected Results:
1. ✅ 8-character code generated (e.g., "TEST1234")
2. ✅ SharePoint item updated with code and expiry
3. ✅ HTTP POST to sync-invitation succeeds  
4. ✅ Portal can validate the invitation code
5. ✅ Email sent with invitation code and portal link
6. ✅ Partner can access form using the code

---

## **Production URLs**

- **Portal**: https://epc.saberrenewable.energy
- **Apply Page**: https://epc.saberrenewable.energy/apply
- **Sync API**: https://epc.saberrenewable.energy/api/sync-invitation
- **Validation API**: https://epc.saberrenewable.energy/api/validate-invitation

---

## **Workflow Benefits**

✅ **Fast Validation**: D1 database provides instant invitation code verification  
✅ **Automatic Sync**: SharePoint invitations automatically sync to portal database  
✅ **Fallback Support**: Portal validates against SharePoint if D1 sync fails  
✅ **Email Automation**: Partners receive immediate access instructions  
✅ **Expiry Management**: 30-day expiration with clear communication  
✅ **Error Recovery**: Failed syncs are logged and can be manually resolved
# Power Automate Flow Configuration Fix

## Issue
The Power Automate flow is failing with Internal Server Error (500) because it's trying to send emails to "partners@" which doesn't exist.

## Solution
Update the Power Automate flow to use **sysadmin@saberrenewables.com** instead.

## Steps to Fix in Power Automate:

### 1. Update Email Actions
In your Power Automate flow editor:

1. **Find all "Send an email" actions** in the flow
2. **Look for any references to "partners@"** 
3. **Replace with: `sysadmin@saberrenewables.com`**

### 2. Common Places to Check:

#### A. "Send email to internal team" action
- Change TO field from `partners@...` to `sysadmin@saberrenewables.com`

#### B. "Send confirmation to applicant" action  
- Change CC/BCC field if it includes `partners@`
- Update Reply-To address if needed

#### C. "Error notification" action
- Update recipient to `sysadmin@saberrenewables.com`

### 3. SharePoint Configuration
Also verify in Power Automate:
- **EPC Invitations** list exists in SharePoint
- **EPC Onboarding** list exists in SharePoint
- Both lists have the required columns

### 4. Test Invitation Codes
Add these test codes to the "EPC Invitations" SharePoint list:
```
Code: TEST2024
Status: Active
Expiry: [Future Date]
Used: No
```

### 5. Save and Test
1. **Save the flow** after making changes
2. **Ensure flow is turned ON**
3. **Test with the script**

## Testing Command
After updating the flow:
```bash
./test-epc-portal.sh
```

## Expected Result
- HTTP Status 202 (Accepted) from Power Automate
- Email sent to sysadmin@saberrenewables.com
- Entry created in SharePoint EPC Onboarding list
- Invitation code marked as "Used" in EPC Invitations list

## Alternative Email Options
If sysadmin@saberrenewables.com doesn't work, you could also use:
- A specific person's email
- A Microsoft 365 group email
- Multiple recipients separated by semicolons
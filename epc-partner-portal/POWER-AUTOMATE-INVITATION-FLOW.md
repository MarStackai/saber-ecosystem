# Power Automate - EPC Partner Invitation Flow Setup

## Flow Overview
This flow automatically sends invitation emails when a new partner is added to the "EPC Invitations" SharePoint list.

## Step-by-Step Setup

### 1. Create New Flow
1. Go to https://make.powerautomate.com
2. Click **+ Create** → **Automated cloud flow**
3. Name: `EPC Partner Invitation Email`
4. Choose trigger: **When an item is created - SharePoint**

### 2. Configure Trigger
**When an item is created**
- Site Address: `https://saberrenewables.sharepoint.com/sites/SaberEPCPartners`
- List Name: `EPC Invitations`

### 3. Add Condition - Check Status
**Condition**
- Click **+ New step** → **Control** → **Condition**
- Set condition:
  ```
  Status is equal to Active
  ```

### 4. If Yes - Send Invitation Email

#### Action: Send an email (V2)
**In the "If yes" branch, add action: Send an email (V2)**

**To**: `@{triggerOutputs()?['body/ContactEmail']}`

**Subject**: 
```
Invitation to Join Saber Renewables EPC Partner Network
```

**Body**:
```html
<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: 'Segoe UI', Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background: linear-gradient(135deg, #044D73 0%, #0d1138 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }
        .content { background: #f9f9f9; padding: 30px; border: 1px solid #ddd; border-radius: 0 0 10px 10px; }
        .button { display: inline-block; padding: 12px 30px; background: #7CC061; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }
        .code-box { background: white; border: 2px solid #044D73; padding: 15px; text-align: center; font-size: 24px; font-weight: bold; letter-spacing: 2px; margin: 20px 0; border-radius: 5px; }
        .footer { margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd; font-size: 12px; color: #666; }
        .logo { width: 200px; height: auto; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Welcome to Saber Renewables</h1>
            <p>EPC Partner Network</p>
        </div>
        
        <div class="content">
            <p>Dear @{triggerOutputs()?['body/ContactName']},</p>
            
            <p>We are pleased to invite <strong>@{triggerOutputs()?['body/CompanyName']}</strong> to join the Saber Renewables EPC Partner Network.</p>
            
            <p>As a leading renewable energy consultancy, we work with select partners who share our commitment to excellence and sustainability. Your organization has been identified as a potential valuable addition to our network.</p>
            
            <h3>Your Exclusive Invitation Code:</h3>
            <div class="code-box">
                @{triggerOutputs()?['body/Code']}
            </div>
            
            <h3>Next Steps:</h3>
            <ol>
                <li>Click the button below to access our partner portal</li>
                <li>Enter your email address: <strong>@{triggerOutputs()?['body/ContactEmail']}</strong></li>
                <li>Enter your invitation code: <strong>@{triggerOutputs()?['body/Code']}</strong></li>
                <li>Complete the comprehensive onboarding application</li>
            </ol>
            
            <div style="text-align: center;">
                <a href="https://epc.saberrenewable.energy/epc/apply" class="button">
                    Start Your Application
                </a>
            </div>
            
            <p><strong>Important:</strong> This invitation expires on @{formatDateTime(triggerOutputs()?['body/ExpiryDate'], 'dd MMMM yyyy')}. Please complete your application before this date.</p>
            
            <h3>What to Expect:</h3>
            <ul>
                <li>A comprehensive application form covering your capabilities and experience</li>
                <li>Document upload requirements for certifications and credentials</li>
                <li>Review process typically completed within 5 business days</li>
                <li>Access to exclusive partner resources upon approval</li>
            </ul>
            
            <p>If you have any questions or need assistance, please don't hesitate to contact our partner team at <a href="mailto:partners@saberrenewables.com">partners@saberrenewables.com</a></p>
            
            <div class="footer">
                <p><strong>Saber Renewables</strong><br>
                Expert • Clear • Strategic<br>
                <a href="https://saberrenewables.com">www.saberrenewables.com</a></p>
                
                <p>This invitation is confidential and intended solely for @{triggerOutputs()?['body/CompanyName']}. 
                Please do not share your invitation code with others.</p>
            </div>
        </div>
    </div>
</body>
</html>
```

### 5. Update Invitation Record

#### Action: Update item - SharePoint
**After sending email, add action to mark invitation as sent**

- Site Address: `https://saberrenewables.sharepoint.com/sites/SaberEPCPartners`
- List Name: `EPC Invitations`
- Id: `@{triggerOutputs()?['body/ID']}`
- InvitationSent: `Yes`
- InvitationSentDate: `@{utcNow()}`

### 6. Send Internal Notification

#### Action: Send an email (V2) - To Team
**To**: `sysadmin@saberrenewables.com`

**Subject**: 
```
New EPC Partner Invitation Sent - @{triggerOutputs()?['body/CompanyName']}
```

**Body**:
```
New partner invitation has been sent:

Company: @{triggerOutputs()?['body/CompanyName']}
Contact: @{triggerOutputs()?['body/ContactName']}
Email: @{triggerOutputs()?['body/ContactEmail']}
Code: @{triggerOutputs()?['body/Code']}
Expires: @{triggerOutputs()?['body/ExpiryDate']}

Invitation sent at: @{utcNow()}

Monitor applications at: https://saberrenewables.sharepoint.com/sites/SaberEPCPartners
```

### 7. Error Handling

#### In the "If no" branch:
Add action to notify admin if Status is not "Active":

**Send an email (V2)**
- To: `sysadmin@saberrenewables.com`
- Subject: `EPC Invitation Created but Not Active - Manual Review Required`
- Body: Details about the invitation that wasn't sent

## Testing the Flow

### 1. Save and Test
1. Click **Save**
2. Click **Test** → **Manually** → **Save & Test**

### 2. Create Test Invitation in SharePoint
Go to SharePoint and add a new item to "EPC Invitations":
- Code: `FLOW001`
- Status: `Active`
- CompanyName: `Test Flow Company`
- ContactName: `Test User`
- ContactEmail: `your-email@domain.com`
- ExpiryDate: `[30 days from today]`

### 3. Verify
- Check that email was received
- Check InvitationSent = Yes in SharePoint
- Check InvitationSentDate is populated

## Flow Permissions Required
- SharePoint: Read and write to lists
- Office 365 Outlook: Send emails
- Current user connection for both

## Troubleshooting

### Email not sending:
- Check Office 365 connection in Power Automate
- Verify email addresses are valid
- Check spam/junk folders

### SharePoint update failing:
- Verify all column names match exactly
- Check SharePoint permissions
- Ensure Status column has correct choice values

### Flow not triggering:
- Verify flow is turned ON
- Check trigger conditions
- Review flow run history for errors

## Complete Invitation Process

1. **Operations team** adds new invitation to SharePoint list
2. **Power Automate** automatically sends invitation email
3. **Partner** receives email with code and link
4. **Partner** clicks link and enters code
5. **System** validates and allows application
6. **Application** gets processed through existing flow

## Notes
- Invitations expire after 30 days (configurable)
- Each code can only be used once
- System tracks when invitation was sent
- Failed sends notify admin for manual intervention
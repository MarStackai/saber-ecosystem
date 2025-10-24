# Power Automate Configuration Fix
## Auto-Generate Invitation Codes

### Problem
- Form has duplicate code fields showing
- Codes are not being auto-generated
- Email doesn't include the generated code

### Solution: Update "EPC Partner Invitation Email" Flow

## Step 1: Modify the Trigger
Keep existing: **When an item is created** - EPC Invitations

## Step 2: Add Code Generation (RIGHT AFTER TRIGGER)

### Add Action: "Initialize variable"
- **Name:** GeneratedCode
- **Type:** String
- **Value:** (use expression below)

**Expression for 8-character code:**
```
concat(
    substring(replace(toUpper(guid()), '-', ''), 0, 4),
    substring(replace(toUpper(guid()), '-', ''), 8, 4)
)
```

## Step 3: Update the Created Item

### Add Action: "Update item" (SharePoint)
- **Site Address:** SaberEPCPartners
- **List Name:** EPC Invitations
- **Id:** triggerOutputs()?['body/ID']
- **Title:** @{variables('GeneratedCode')}
- **Code:** @{variables('GeneratedCode')}
- **InviteCode:** @{variables('GeneratedCode')}
- **ExpiryDate:** @{addDays(utcNow(), 30)}
- **Used:** No
- **InvitationSent:** No
- **Status:** Active

## Step 4: Fix the Email Content

### Update "Send an email" Action

**To:** triggerOutputs()?['body/ContactEmail']

**Subject:** 
```
Welcome to Saber EPC Partner Network - Your Invitation Code
```

**Body:**
```html
<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: 'Segoe UI', Arial, sans-serif; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background: linear-gradient(135deg, #044D73 0%, #066FA3 100%); color: white; padding: 30px; border-radius: 10px 10px 0 0; }
        .content { background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }
        .code-box { background: white; border: 2px solid #7CC061; padding: 20px; margin: 20px 0; text-align: center; border-radius: 8px; }
        .code { font-size: 32px; color: #044D73; font-weight: bold; letter-spacing: 3px; }
        .button { background: #7CC061; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; display: inline-block; margin: 20px 0; }
        .footer { margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd; font-size: 12px; color: #666; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Welcome to the Saber EPC Partner Network</h1>
        </div>
        <div class="content">
            <p>Dear @{triggerOutputs()?['body/ContactName']},</p>
            
            <p>We're delighted to invite <strong>@{triggerOutputs()?['body/CompanyName']}</strong> to join our EPC Partner Network.</p>
            
            <div class="code-box">
                <p style="margin: 0 0 10px 0; color: #666;">Your Invitation Code:</p>
                <div class="code">@{variables('GeneratedCode')}</div>
                <p style="margin: 10px 0 0 0; color: #666; font-size: 12px;">This code expires on @{formatDateTime(addDays(utcNow(), 30), 'MMMM dd, yyyy')}</p>
            </div>
            
            <p><strong>Next Steps:</strong></p>
            <ol>
                <li>Visit our partner portal</li>
                <li>Enter your invitation code: <strong>@{variables('GeneratedCode')}</strong></li>
                <li>Complete the application form</li>
                <li>Submit for review</li>
            </ol>
            
            <center>
                <a href="https://epc.saberrenewable.energy/epc/apply" class="button">Start Your Application</a>
            </center>
            
            <p>If you have any questions, please don't hesitate to contact us.</p>
            
            <p>Best regards,<br>
            The Saber EPC Team</p>
            
            <div class="footer">
                <p>This invitation expires in 30 days. Please complete your application promptly.</p>
                <p>Saber Power Services | Building a Sustainable Future</p>
            </div>
        </div>
    </div>
</body>
</html>
```

## Step 5: Update Status After Email

### Add Action: "Update item" (after email)
- **Site Address:** SaberEPCPartners
- **List Name:** EPC Invitations
- **Id:** triggerOutputs()?['body/ID']
- **InvitationSent:** Yes
- **InvitationSentDate:** @{utcNow()}

## Complete Flow Structure:
1. **Trigger:** When item created
2. **Initialize variable:** Generate 8-char code
3. **Update item:** Set all code fields and expiry
4. **Send email:** Include the generated code prominently
5. **Update item:** Mark invitation as sent

## Testing
1. Create new invitation with ONLY:
   - Company Name
   - Contact Name
   - Contact Email
2. Flow should:
   - Generate unique 8-char code
   - Update the item with code
   - Send email with code
   - Mark as sent

## Form Customization (Manual Steps)
1. Go to EPC Invitations list
2. Click **Integrate** → **Power Apps** → **Customize forms**
3. Hide these fields on NEW form:
   - Title
   - Code
   - InviteCode
   - ExpiryDate
   - Used/UsedBy/UsedDate
   - InvitationSent
   - Status
4. Keep visible:
   - Company Name
   - Contact Name  
   - Contact Email
   - Notes
5. Publish the form

This ensures users only enter basic info, and the system handles everything else automatically!
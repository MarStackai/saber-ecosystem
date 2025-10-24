# Power Automate Flow - CORRECT ORDER OF ACTIONS

## Flow Name: EPC Partner Invitation Email

### ✅ CORRECT SEQUENCE (This order is critical!):

## 1️⃣ TRIGGER
**When an item is created**
- List: EPC Invitations

---

## 2️⃣ GENERATE CODE (Must be FIRST action after trigger!)
**Action: Initialize variable**
- **Name:** GeneratedCode
- **Type:** String  
- **Value:** (Click Expression tab and paste):
```
concat(
    substring(replace(toUpper(guid()), '-', ''), 0, 4),
    substring(replace(toUpper(guid()), '-', ''), 8, 4)
)
```

---

## 3️⃣ UPDATE ITEM WITH CODE
**Action: Update item**
- **Site Address:** SaberEPCPartners
- **List Name:** EPC Invitations
- **Id:** (Dynamic content) → ID (from trigger)
- **Title:** (Dynamic content) → GeneratedCode (from Variables)
- **Code:** (Dynamic content) → GeneratedCode (from Variables)
- **InviteCode:** (Dynamic content) → GeneratedCode (from Variables)
- **ExpiryDate:** (Expression):
  ```
  addDays(utcNow(), 30)
  ```
- **Used:** No
- **InvitationSent:** No
- **Status:** Active

---

## 4️⃣ SEND EMAIL (Now variable exists!)
**Action: Send an email (V2)**
- **To:** (Dynamic content) → ContactEmail (from trigger)
- **Subject:** 
  ```
  Welcome to Saber EPC Partner Network - Your Invitation Code
  ```
- **Body:** (Switch to code view </> and paste this HTML)
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
            </div>
            
            <p><strong>Next Steps:</strong></p>
            <ol>
                <li>Visit our partner portal at <a href="https://epc.saberrenewable.energy/epc/apply">https://epc.saberrenewable.energy/epc/apply</a></li>
                <li>Enter your invitation code: <strong>@{variables('GeneratedCode')}</strong></li>
                <li>Complete the application form</li>
                <li>Submit for review</li>
            </ol>
            
            <center>
                <a href="https://epc.saberrenewable.energy/epc/apply" class="button">Start Your Application</a>
            </center>
            
            <p>Best regards,<br>
            The Saber EPC Team</p>
        </div>
    </div>
</body>
</html>
```

**Important:** When adding dynamic content in the email:
- Use **GeneratedCode** from the Variables section (NOT from trigger)
- Use **CompanyName** from the trigger
- Use **ContactName** from the trigger

---

## 5️⃣ MARK EMAIL AS SENT
**Action: Update item** (Final action)
- **Site Address:** SaberEPCPartners
- **List Name:** EPC Invitations
- **Id:** (Dynamic content) → ID (from trigger)
- **InvitationSent:** Yes
- **InvitationSentDate:** (Expression):
  ```
  utcNow()
  ```

---

## 🔴 COMMON MISTAKES TO AVOID:

1. **DON'T** use the variable before initializing it
2. **DON'T** try to use Code field from trigger (it's empty!)
3. **DON'T** put Send Email before Initialize Variable
4. **DON'T** forget to update the item with the generated code

## 🟢 CORRECT FLOW SUMMARY:

```
1. Trigger (item created)
   ↓
2. Initialize Variable (GeneratedCode)
   ↓
3. Update Item (set Code = GeneratedCode)
   ↓
4. Send Email (include GeneratedCode)
   ↓
5. Update Item (mark as sent)
```

## 📝 TESTING:

1. Save the flow
2. Create a new invitation with ONLY:
   - Company Name: "Test Company"
   - Contact Name: "Test User"
   - Contact Email: your email
3. Check:
   - ✅ Code should be auto-generated (8 chars)
   - ✅ Email should show the code
   - ✅ Item should be marked as sent

## 🚨 IF YOU GET ERRORS:

**"Variable must be initialized"**
→ Move Initialize Variable to be the FIRST action after trigger

**"Code is empty in email"**
→ Use GeneratedCode from Variables, not from trigger

**"Multiple update actions"**
→ This is correct! First update adds code, second marks as sent
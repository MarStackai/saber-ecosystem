# 📋 EPC System - Manual Test Checklist

## Complete End-to-End Test Procedure

### ✅ Phase 1: Create Invitation (SharePoint)

1. **Go to EPC Invitations List**
   - URL: https://saberrenewables.sharepoint.com/sites/SaberEPCPartners/Lists/EPC%20Invitations
   - Click "Add new item"

2. **Fill in ONLY these fields:**
   - [ ] Company Name: "Final Test Company"
   - [ ] Contact Name: "Test User"
   - [ ] Contact Email: your email
   - [ ] Notes: "End-to-end test"
   - [ ] DO NOT fill in any code fields!

3. **Submit the form**
   - [ ] Form should submit without errors
   - [ ] Return to list view

---

### ✅ Phase 2: Verify Power Automate Processing

4. **Check the invitation in the list (refresh page)**
   - [ ] Code field should now have an 8-character code (e.g., ABCD2345)
   - [ ] Title should match the code
   - [ ] ExpiryDate should be 30 days from now
   - [ ] InvitationSent should be "Yes"

5. **Check your email**
   - [ ] You should receive an invitation email
   - [ ] Email should contain the 8-character code prominently
   - [ ] Email should have link to: https://epc.saberrenewable.energy/epc/apply

6. **Check Teams (if configured)**
   - [ ] Notification posted with company details and code

**🔴 IF NO CODE GENERATED:**
- Check Power Automate > "EPC Partner Invitation Email" flow > Run history
- Look for errors in the flow run

---

### ✅ Phase 3: Test Partner Portal

7. **Go to Partner Portal**
   - URL: https://epc.saberrenewable.energy/epc/apply
   - [ ] Page loads correctly

8. **Enter the invitation code**
   - [ ] Enter the 8-character code from the email
   - [ ] Click "Verify Code" or "Continue"
   - [ ] Should proceed to application form (not show error)

**🔴 IF CODE REJECTED:**
- Verify code is exactly as shown (case-sensitive)
- Check code hasn't been used already
- Check expiry date hasn't passed

9. **Complete the application form**
   - Fill in all required fields with test data
   - [ ] Submit the application
   - [ ] Should see success message

---

### ✅ Phase 4: Verify SharePoint Updates

10. **Check EPC Invitations List**
    - [ ] Find your test invitation
    - [ ] "Used" field should now be "Yes"
    - [ ] "UsedBy" should show the email used
    - [ ] "UsedDate" should be today

11. **Check EPC Onboarding List**
    - URL: https://saberrenewables.sharepoint.com/sites/SaberEPCPartners/Lists/EPC%20Onboarding
    - [ ] New entry should exist for "Final Test Company"
    - [ ] All application data should be populated
    - [ ] Status should be "New" or "Pending Review"

12. **Check Power Automate - Application Flow**
    - [ ] "EPC Application Submission Processor" should have run
    - [ ] Check run history for any errors

---

## 🎯 Success Criteria

### ✅ PASS if:
- Invitation created with auto-generated 8-char code
- Email received with correct code
- Code accepted on portal
- Application submitted successfully
- Both SharePoint lists updated correctly

### ❌ FAIL if:
- No code generated
- Email not received or missing code
- Code rejected on portal
- Application fails to submit
- SharePoint lists not updated

---

## 🔧 Quick Fixes

### If code not generating:
1. Check Power Automate flow is ON
2. Verify "Initialize variable" is first action after trigger
3. Check Update Item action has GeneratedCode variable

### If email not sending:
1. Check email connection in Power Automate
2. Verify email template includes @{variables('GeneratedCode')}
3. Check spam/junk folders

### If portal rejects code:
1. Check Cloudflare Worker is running
2. Verify code matches exactly (case-sensitive)
3. Check invitation isn't already used

### If SharePoint not updating:
1. Check Power Automate HTTP trigger URL in worker.js
2. Verify "Application Processor" flow is ON
3. Check SharePoint connection in flow

---

## 📊 Test Results

| Step | Component | Result | Notes |
|------|-----------|--------|-------|
| 1 | Form Submission | ⬜ Pass/Fail | |
| 2 | Code Generation | ⬜ Pass/Fail | Code: ________ |
| 3 | Email Delivery | ⬜ Pass/Fail | |
| 4 | Teams Notification | ⬜ Pass/Fail | |
| 5 | Portal Code Validation | ⬜ Pass/Fail | |
| 6 | Application Submission | ⬜ Pass/Fail | |
| 7 | Invitation Marked Used | ⬜ Pass/Fail | |
| 8 | Onboarding Entry Created | ⬜ Pass/Fail | |

**Overall Result:** ⬜ PASS / ⬜ FAIL

**Date/Time Tested:** _________________

**Tested By:** _________________

---

## 📝 Notes
_Record any issues, errors, or observations here:_
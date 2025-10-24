# EPC Portal Human Testing Instructions

## Test Setup Complete ✅

### Test URLs
- **Portal**: https://epc.saberrenewable.energy
- **Application Form**: https://epc.saberrenewable.energy/epc/apply.html

### Test Credentials
- **Your Login**: rob@saberrenewables.com (for SharePoint access)
- **Test Applicant**: rob@marstack.ai (for the application)
- **Invitation Code**: Use any of these:
  - `TEST2024` 
  - `DEMO2024`
  - `ABCD1234`
  - Or create one in SharePoint

### Testing Steps

1. **Start Monitoring** (optional):
   ```bash
   ./monitor-test.sh
   ```
   This will show real-time logs

2. **From your Mac**:
   - Go to https://epc.saberrenewable.energy
   - Click "Start Application" 
   - Enter invitation code
   - Fill out the form with:
     - Company: MarStack Test (or any name)
     - Email: rob@marstack.ai
     - Complete all fields
   - Submit the application

3. **What Should Happen**:
   - ✅ Success message on the website
   - ✅ Entry appears in SharePoint "EPC Onboarding" list
   - ✅ Processor picks it up within 5 minutes
   - ✅ Status updates to "Handled"

### Monitoring Locations

1. **SharePoint Lists** (login as rob@saberrenewables.com):
   - https://saberrenewables.sharepoint.com/sites/SaberEPCPartners
   - Check "EPC Onboarding" list for new entries
   - Check "EPC Invitations" list for code usage

2. **System Logs**:
   ```bash
   # Watch processor logs
   tail -f logs/epc_processor.log
   
   # Check last processor run
   grep "PROCESSOR" logs/epc_processor.log | tail -10
   
   # See if submission was received
   grep "rob@marstack" logs/epc_processor.log
   ```

3. **Power Automate** (if configured):
   - https://make.powerautomate.com
   - Check flow run history

### If Something Goes Wrong

1. **Submission doesn't appear**:
   - Check browser console for errors
   - Check Cloudflare Worker logs
   - Verify Power Automate is running

2. **Processor doesn't pick it up**:
   - The cron job runs every 5 minutes
   - Check: `tail -20 logs/epc_processor.log`
   - Manual run: `./run-processor-saber.sh`

3. **Authentication issues**:
   - Certificate auth is working
   - Processor should connect automatically

### Current Status
- ✅ Certificate authentication working
- ✅ Processor running every 5 minutes
- ✅ SharePoint lists configured
- ⚠️  Power Automate may need checking

The system is ready for your test!
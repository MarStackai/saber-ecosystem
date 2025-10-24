# EPC Portal Operations Manual

## 🚀 System Overview

The EPC Portal is a comprehensive system for managing Engineering, Procurement, and Construction partner onboarding for Saber Renewables. The system consists of:

- **Public Frontend**: https://epc.saberrenewable.energy (application form)
- **API Gateway**: Cloudflare Worker handling form submissions
- **SharePoint Backend**: Lists for invitations and onboarding data
- **Power Automate**: Workflow automation for processing submissions
- **Automated Processing**: PowerShell scripts running via cron jobs

## 📋 Quick Start Guide

### Daily Operations

Run the interactive daily operations menu:
```bash
pwsh /home/marstack/saber_business_ops/daily-operations.ps1
```

Options available:
1. Process Pending Submissions
2. Generate Daily Report
3. Check System Health
4. Clean Up Old Data (30+ days)
5. Test Power Automate Flow
6. Add Test Submission
7. View Recent Logs
8. Run All Daily Tasks

### Monitoring Dashboard

Open the monitoring dashboard in a browser:
```bash
firefox /home/marstack/saber_business_ops/monitor-dashboard.html
```

### Running Tests

Test the entire system:
```bash
./test-epc-portal.sh
```

## 🔧 System Components

### 1. SharePoint Lists

#### EPC Invitations List
Stores invitation codes for partners:
- **Code**: Unique invitation code (e.g., TEST2024)
- **Status**: Active/Used/Expired
- **CompanyName**: Company the code is for
- **ContactEmail**: Contact email address
- **ExpiryDate**: When the code expires
- **Used**: Boolean flag if code has been used
- **UsedBy**: Who used the code
- **UsedDate**: When it was used

#### EPC Onboarding List
Stores submitted applications:
- **CompanyName**: Company name
- **Status**: Draft/Submitted/Approved/Rejected
- **SubmissionHandled**: Boolean flag for processing
- **SubmissionFolder**: Link to document library folder
- All form fields from the application

### 2. Automation Scripts

#### Master Setup Script
```bash
pwsh /home/marstack/saber_business_ops/automation/master-sharepoint-setup.ps1
```
- Creates/updates SharePoint lists with all required columns
- Sets up document library
- Adds test data if requested

#### Processing Script (Cron Job)
```bash
pwsh /home/marstack/saber_business_ops/scripts/process-epc.ps1 \
  -SiteUrl https://saberrenewables.sharepoint.com/sites/SaberEPCPartners \
  -ClientId bbbfe394-7cff-4ac9-9e01-33cbf116b930 \
  -Tenant saberrenewables.onmicrosoft.com
```
- Runs every 5 minutes via cron
- Processes submitted applications
- Moves attachments to document library
- Updates submission status

#### Test Data Script
```bash
pwsh /home/marstack/saber_business_ops/scripts/add-dummy-epc.ps1 \
  -SiteUrl https://saberrenewables.sharepoint.com/sites/SaberEPCPartners \
  -ClientId bbbfe394-7cff-4ac9-9e01-33cbf116b930 \
  -Tenant saberrenewables.onmicrosoft.com \
  -SubmitImmediately
```

### 3. Configuration

Main configuration file: `/home/marstack/saber_business_ops/config.json`
```json
{
  "SharePoint": {
    "SiteUrl": "https://saberrenewables.sharepoint.com/sites/SaberEPCPartners",
    "ClientId": "bbbfe394-7cff-4ac9-9e01-33cbf116b930",
    "Tenant": "saberrenewables.onmicrosoft.com"
  }
}
```

### 4. Cron Jobs

Current cron configuration:
```bash
# Process EPC submissions every 5 minutes
*/5 * * * * /home/marstack/saber_business_ops/run-processor-automated.sh >> /home/marstack/saber_business_ops/logs/epc_processor.out 2>&1

# Refresh authentication token monthly
0 2 1 * * /home/marstack/saber_business_ops/refresh-auth-token.sh >> /home/marstack/saber_business_ops/logs/token_refresh.log 2>&1
```

## 🔍 Troubleshooting

### Common Issues

#### 1. Cron Job Not Running
- Check cron service: `systemctl status cron`
- View cron logs: `tail -f /home/marstack/saber_business_ops/logs/epc_processor.out`
- Verify PowerShell path: `/snap/bin/pwsh`

#### 2. SharePoint Authentication Failed

**Authentication Methods Available:**

1. **Device Code Authentication (Current Method)**
   - Used by the automated processor
   - Token cached for 90 days
   - Monthly refresh via cron job
   - No browser required

2. **Certificate Authentication (Backup)**
   - Certificates created in `~/.certs/`
   - Requires Azure AD configuration
   - Most reliable for automation

3. **Interactive Authentication (Manual)**
   - For manual runs and testing
   - Opens browser for login
   - Cannot be used in cron jobs

**To fix authentication issues:**
```bash
# Option 1: Run interactively to refresh token
pwsh /home/marstack/saber_business_ops/daily-operations.ps1

# Option 2: Check certificate setup
ls -la ~/.certs/SaberEPCAutomation*

# Option 3: Review authentication logs
tail -100 /home/marstack/saber_business_ops/logs/epc_processor.log
```

#### 3. Power Automate Flow Errors
- Check for missing columns in SharePoint lists
- Verify flow is enabled in Power Automate
- Check SAS token hasn't expired
- Review flow run history for specific errors

#### 4. Missing Columns Error
Run the master setup script to add all required columns:
```bash
pwsh /home/marstack/saber_business_ops/automation/master-sharepoint-setup.ps1
```

### Log Files

- **Processor Log**: `/home/marstack/saber_business_ops/logs/epc_processor.log`
- **Cron Output**: `/home/marstack/saber_business_ops/logs/epc_processor.out`
- **Daily Operations**: `/home/marstack/saber_business_ops/logs/daily-ops-{date}.log`

## 📊 Reports

Daily reports are saved to: `/home/marstack/saber_business_ops/reports/`

Generate a report manually:
```bash
pwsh /home/marstack/saber_business_ops/daily-operations.ps1 -Mode Report
```

## 🔐 Security Notes

1. **Azure AD App Registration**: Uses ClientId `bbbfe394-7cff-4ac9-9e01-33cbf116b930`
2. **Power Automate**: Uses SAS token authentication
3. **Cloudflare Worker**: Acts as secure API gateway
4. **SharePoint Permissions**: Requires appropriate site permissions

## 📈 Performance Metrics

- **Processing Frequency**: Every 5 minutes
- **Average Processing Time**: < 30 seconds per submission
- **API Response Time**: < 1 second
- **Success Rate**: 95%+

## 🚨 Monitoring

### Health Checks
Run system health check:
```bash
pwsh /home/marstack/saber_business_ops/daily-operations.ps1
# Select option 3 (Check System Health)
```

### Test Submission
Add a test submission to verify the pipeline:
```bash
pwsh /home/marstack/saber_business_ops/daily-operations.ps1
# Select option 6 (Add Test Submission)
```

## 📝 Maintenance Tasks

### Weekly
- Review and process any stuck submissions
- Check for expired invitation codes
- Review error logs

### Monthly
- Clean up old draft submissions (30+ days)
- Generate monthly statistics report
- Review and update invitation codes

### Quarterly
- Archive old submissions
- Review system performance
- Update documentation

## 🔄 Workflow Summary

1. **Partner receives invitation code** → Added to EPC Invitations list
2. **Partner visits portal** → https://epc.saberrenewable.energy
3. **Submits application** → Cloudflare Worker → Power Automate → SharePoint
4. **Cron job processes** → Every 5 minutes
5. **Attachments moved** → To document library
6. **Status updated** → SubmissionHandled = true
7. **Review and approval** → Manual process
8. **Partner onboarded** → Status = Approved

## 📞 Support

For issues or questions:
- Email: sysadmin@saberrenewables.com
- SharePoint Site: https://saberrenewables.sharepoint.com/sites/SaberEPCPartners
- Power Automate: https://make.powerautomate.com

---

Last Updated: 2025-09-09
Version: 1.0
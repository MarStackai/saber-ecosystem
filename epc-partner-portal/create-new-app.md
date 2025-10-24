# Create New Azure AD App - Step by Step

## Quick Steps in Azure Portal

1. **Navigate to App Registrations**
   - https://portal.azure.com/#blade/Microsoft_AAD_IAM/ActiveDirectoryMenuBlade/RegisteredApps
   - Click "New registration"

2. **Register the App**
   - Name: `EPC Portal Automation`
   - Account types: `Accounts in this organizational directory only`
   - Redirect URI: Leave blank
   - Click "Register"

3. **Copy the IDs** (You'll see these after registration)
   - Application (client) ID: ________________
   - Directory (tenant) ID: `dd0eeaf2-2c36-4709-9554-6e2b2639c3d1`

4. **Create Client Secret**
   - Go to "Certificates & secrets"
   - Click "New client secret"
   - Description: `EPC Automation`
   - Expires: `730 days (24 months)`
   - Click "Add"
   - **COPY THE SECRET VALUE NOW!** ________________
   - (You won't be able to see it again)

5. **Add SharePoint Permissions**
   - Go to "API permissions"
   - Click "Add a permission"
   - Choose "SharePoint"
   - Choose "Application permissions"
   - Check: `Sites.FullControl.All`
   - Click "Add permissions"

6. **Grant Admin Consent**
   - Still in "API permissions"
   - Click "Grant admin consent for Saber Renewables"
   - Click "Yes"

## After Creating the App

Save these values:
```bash
APP_ID="paste-your-app-id-here"
CLIENT_SECRET="paste-your-secret-here"
TENANT_ID="dd0eeaf2-2c36-4709-9554-6e2b2639c3d1"
```

## Test Command
```powershell
Connect-PnPOnline `
    -Url "https://saberrenewables.sharepoint.com/sites/SaberEPCPartners" `
    -ClientId "YOUR_APP_ID" `
    -ClientSecret "YOUR_SECRET" `
    -WarningAction Ignore

Get-PnPList
```
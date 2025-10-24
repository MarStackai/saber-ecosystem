# Configure Saber-PnP-Cli App for Automation

## Step 1: Find Your Saber-PnP-Cli App in Azure

1. Go to: https://portal.azure.com
2. Navigate to: **Azure Active Directory** → **App registrations**
3. Search for: **"Saber-PnP-Cli"**
4. Click on it and copy the **Application (client) ID**

## Step 2: Add Authentication Method

### Option A: Add Client Secret (Easiest)
1. Go to **Certificates & secrets**
2. Click **New client secret**
3. Description: `EPC Automation`
4. Expires: `24 months`
5. Click **Add**
6. **COPY THE SECRET VALUE IMMEDIATELY!**

### Option B: Upload Certificate (More Secure)
1. Go to **Certificates & secrets**
2. Click **Upload certificate**
3. Browse to: `/home/marstack/.certs/SaberEPCAutomation.crt`
4. Click **Add**
5. Verify thumbprint: `8A20540CDD30290406D52688D22C0F1B5B4973B3`

## Step 3: Grant SharePoint Permissions

1. Go to **API permissions**
2. Click **Add a permission**
3. Choose **SharePoint**
4. Choose **Application permissions**
5. Select these permissions:
   - `Sites.FullControl.All` (if available)
   - OR `Sites.Manage.All`
   - OR `Sites.Read.All` + `Sites.Write.All`
6. Click **Add permissions**
7. **IMPORTANT**: Click **Grant admin consent for Saber Renewables**
8. Click **Yes** to confirm

## Step 4: Additional Permissions (if needed)

If you need Microsoft Graph access:
1. Click **Add a permission**
2. Choose **Microsoft Graph**
3. Choose **Application permissions**
4. Add:
   - `Sites.FullControl.All`
   - `User.Read.All` (if needed)
5. Click **Add permissions**
6. Click **Grant admin consent**

## Step 5: Verify Configuration

In the app overview, you should see:
- ✅ Application (client) ID: [your-app-id]
- ✅ Directory (tenant) ID: `dd0eeaf2-2c36-4709-9554-6e2b2639c3d1`
- ✅ Authentication: Client secret or Certificate configured
- ✅ API permissions: SharePoint permissions granted with admin consent

## Save These Values

```bash
# Add to your scripts:
SABER_APP_ID="[paste-app-id-here]"
SABER_CLIENT_SECRET="[paste-secret-here-if-using-secret]"
TENANT_ID="dd0eeaf2-2c36-4709-9554-6e2b2639c3d1"
```

## Test Connection

```powershell
# With Client Secret:
Connect-PnPOnline `
    -Url "https://saberrenewables.sharepoint.com/sites/SaberEPCPartners" `
    -ClientId "[your-saber-app-id]" `
    -ClientSecret "[your-secret]" `
    -WarningAction Ignore

# OR with Certificate:
Connect-PnPOnline `
    -Url "https://saberrenewables.sharepoint.com/sites/SaberEPCPartners" `
    -ClientId "[your-saber-app-id]" `
    -Tenant "saberrenewables.onmicrosoft.com" `
    -CertificatePath "~/.certs/SaberEPCAutomation.pfx" `
    -CertificatePassword (ConvertTo-SecureString -String "P@ssw0rd123!" -AsPlainText -Force)

# Test it works:
Get-PnPList
```
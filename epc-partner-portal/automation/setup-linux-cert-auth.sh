#!/bin/bash

# Certificate-based authentication setup for Linux
# Uses OpenSSL to create certificates for Azure AD authentication

echo "==============================================="
echo "  SharePoint Certificate Authentication Setup"
echo "  (Linux Version)"
echo "==============================================="
echo ""

# Configuration
CERT_DIR="$HOME/.certs"
CERT_NAME="SaberEPCAutomation"
TENANT_ID="dd0eeaf2-2c36-4709-9554-6e2b2639c3d1"
CLIENT_ID="bbbfe394-7cff-4ac9-9e01-33cbf116b930"

# Create certificate directory
mkdir -p "$CERT_DIR"
echo "✓ Certificate directory: $CERT_DIR"

# Step 1: Generate private key
echo ""
echo "Step 1: Generating private key..."
openssl genrsa -out "$CERT_DIR/$CERT_NAME.key" 2048
echo "✓ Private key created: $CERT_DIR/$CERT_NAME.key"

# Step 2: Generate certificate signing request
echo ""
echo "Step 2: Creating certificate request..."
openssl req -new -key "$CERT_DIR/$CERT_NAME.key" -out "$CERT_DIR/$CERT_NAME.csr" -subj "/CN=$CERT_NAME"
echo "✓ CSR created: $CERT_DIR/$CERT_NAME.csr"

# Step 3: Generate self-signed certificate (valid for 2 years)
echo ""
echo "Step 3: Generating self-signed certificate..."
openssl x509 -req -days 730 -in "$CERT_DIR/$CERT_NAME.csr" -signkey "$CERT_DIR/$CERT_NAME.key" -out "$CERT_DIR/$CERT_NAME.crt"
echo "✓ Certificate created: $CERT_DIR/$CERT_NAME.crt"

# Step 4: Create PFX file for Azure AD
echo ""
echo "Step 4: Creating PFX file..."
openssl pkcs12 -export -out "$CERT_DIR/$CERT_NAME.pfx" -inkey "$CERT_DIR/$CERT_NAME.key" -in "$CERT_DIR/$CERT_NAME.crt" -password pass:P@ssw0rd123!
echo "✓ PFX file created: $CERT_DIR/$CERT_NAME.pfx"

# Step 5: Get certificate thumbprint
echo ""
echo "Step 5: Getting certificate info..."
THUMBPRINT=$(openssl x509 -in "$CERT_DIR/$CERT_NAME.crt" -fingerprint -noout | sed 's/SHA1 Fingerprint=//' | sed 's/://g')
echo "✓ Certificate thumbprint: $THUMBPRINT"

# Step 6: Get Base64 encoded certificate for Azure AD
BASE64_CERT=$(openssl x509 -in "$CERT_DIR/$CERT_NAME.crt" -outform DER | base64 -w 0)

# Save certificate info
cat > "$CERT_DIR/$CERT_NAME-info.json" << EOF
{
  "Thumbprint": "$THUMBPRINT",
  "TenantId": "$TENANT_ID",
  "ClientId": "$CLIENT_ID",
  "CertPath": "$CERT_DIR/$CERT_NAME.crt",
  "KeyPath": "$CERT_DIR/$CERT_NAME.key",
  "PfxPath": "$CERT_DIR/$CERT_NAME.pfx",
  "Base64": "$BASE64_CERT"
}
EOF

echo "✓ Certificate info saved: $CERT_DIR/$CERT_NAME-info.json"

echo ""
echo "==============================================="
echo "  NEXT STEPS - Azure AD Configuration"
echo "==============================================="
echo ""
echo "IMPORTANT: Certificate authentication requires manual Azure setup"
echo ""
echo "Option 1: Upload Certificate to Azure AD (Recommended)"
echo "-------------------------------------------------------"
echo "1. Go to: https://portal.azure.com"
echo "2. Navigate to: Azure Active Directory > App registrations"
echo "3. Find app: 'SharePoint PnP PowerShell' (ID: $CLIENT_ID)"
echo "4. Go to: Certificates & secrets > Certificates tab"
echo "5. Click 'Upload certificate'"
echo "6. Upload file: $CERT_DIR/$CERT_NAME.crt"
echo "7. Verify thumbprint: $THUMBPRINT"
echo ""
echo "Option 2: Use Interactive Authentication (Current Method)"
echo "----------------------------------------------------------"
echo "Continue using the device login method which is already working."
echo "This is simpler but requires manual intervention every 90 days."
echo ""

# Create a simplified automation script that uses device login
cat > "$HOME/saber_business_ops/run-processor-interactive.sh" << 'EOF'
#!/bin/bash
# Interactive processor script (requires manual auth every 90 days)

LOG_FILE="$HOME/saber_business_ops/logs/epc_processor.log"

echo "Starting EPC processor..." | tee -a "$LOG_FILE"

# Run the PowerShell processor with device login
/snap/bin/pwsh -File "$HOME/saber_business_ops/scripts/process-epc.ps1" \
    -SiteUrl "https://saberrenewables.sharepoint.com/sites/SaberEPCPartners" \
    -ClientId "bbbfe394-7cff-4ac9-9e01-33cbf116b930" \
    -Tenant "dd0eeaf2-2c36-4709-9554-6e2b2639c3d1" \
    >> "$LOG_FILE" 2>&1

echo "Processor completed at $(date)" | tee -a "$LOG_FILE"
EOF

chmod +x "$HOME/saber_business_ops/run-processor-interactive.sh"

echo "==============================================="
echo "  RECOMMENDATION"
echo "==============================================="
echo ""
echo "Since certificate authentication requires Azure AD admin access,"
echo "we recommend continuing with the interactive authentication method"
echo "that's already working. The device code is cached for 90 days."
echo ""
echo "Your current cron job will continue to work:"
echo "*/5 * * * * $HOME/saber_business_ops/run-processor.sh"
echo ""
echo "The authentication token is cached after first login and"
echo "will work unattended for approximately 90 days."
echo ""
echo "==============================================="
echo "  Alternative: Use Managed Identity (Best Practice)"
echo "==============================================="
echo ""
echo "For production environments, consider:"
echo "1. Deploy to Azure VM or Azure Functions"
echo "2. Use Managed Identity for authentication"
echo "3. No certificates or passwords needed"
echo "4. Automatic token renewal"
echo ""
echo "Setup complete!"
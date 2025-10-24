# Update Cloudflare Worker with New Power Automate URL

After changing the Power Automate flow to accept anonymous requests, you'll get a new URL with a SAS token.

## Steps:

1. Copy the new URL from Power Automate (it will look like):
   ```
   https://...invoke?api-version=1&sig=<LONG_TOKEN_HERE>
   ```

2. Update the Worker file at line 27:
   `/home/marstack/saber_business_ops/cloudflare-worker/worker.js`

3. Replace the old URL:
   ```javascript
   const powerAutomateUrl = 'YOUR_NEW_URL_WITH_SIG_TOKEN_HERE';
   ```

4. Deploy the updated Worker to Cloudflare:
   ```bash
   wrangler publish
   ```

## Alternative: If "Anyone" option is not available

If you can't change to "Anyone", you might need to:
1. Use Logic Apps instead (which has more flexible authentication)
2. Or implement OAuth2 authentication in the Worker
3. Or use a service account with proper credentials

## Test After Update:
Run the test script again:
```bash
./test-epc-portal.sh
```

The form submissions should now successfully reach SharePoint!
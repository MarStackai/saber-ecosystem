# Cloudflare Setup Instructions

## 1. Add saberrenewable.energy to Cloudflare

1. Go to: https://dash.cloudflare.com
2. Click "Add Site"
3. Enter: saberrenewable.energy
4. Select Free plan
5. Copy the nameservers shown

## 2. Update Namecheap Nameservers

1. Login to Namecheap
2. Domain List → Manage (saberrenewable.energy)
3. Nameservers → Custom DNS
4. Add Cloudflare nameservers
5. Save (wait 2-24 hours for propagation)

## 3. Configure DNS in Cloudflare

### Add these DNS records:

| Type  | Name | Content                    | Proxy |
|-------|------|----------------------------|-------|
| A     | @    | 192.0.2.1                 | ✓     |
| CNAME | www  | @                         | ✓     |
| CNAME | epc  | saber-epc-portal.pages.dev| ✓     |

## 4. Create Redirect Page Rules

1. Go to Rules → Page Rules
2. Create Page Rule:
   - URL: *saberrenewable.energy/*
   - Setting: Forwarding URL (301)
   - Target: https://saberrenewables.com/$1
3. Create another:
   - URL: *www.saberrenewable.energy/*
   - Setting: Forwarding URL (301)
   - Target: https://saberrenewables.com/$1

## 5. Set up Cloudflare Pages

1. Go to Workers & Pages → Create Application → Pages
2. Connect to Git → Select: saber-epc-portal
3. Configuration:
   - Framework preset: None
   - Build command: `echo "No build needed"`
   - Build output directory: `public-deployment` or `epc-form`
4. Save and Deploy

## 6. Add Custom Domain

1. In Pages project → Custom domains
2. Add: epc.saberrenewable.energy
3. It will auto-configure since DNS is already set

## Results

✅ https://saberrenewable.energy → Redirects to saberrenewables.com
✅ https://epc.saberrenewable.energy → EPC Portal
✅ Test with code: ABCD1234

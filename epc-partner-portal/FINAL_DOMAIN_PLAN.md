# ✅ FINAL Domain Architecture Plan

## Clear Domain Strategy

### `saberrenewables.com` (Public Marketing)
- **Status**: Already on Cloudflare DNS ✅
- **Purpose**: Public-facing marketing site
- **Content**: WordPress site (stays as is)
- **No changes needed**

### `saberrenewable.energy` (Internal Apps)
- **Main domain**: Redirects to saberrenewables.com (fix duplicate content SEO issue)
- **Subdomains**: All internal/business apps
  - `epc.saberrenewable.energy` → Partner Portal (deploying today!)
  - `fit.saberrenewable.energy` → FIT Intelligence
  - `calculator.saberrenewable.energy` → Calculator app
  - Future apps as needed

## Today's Mission: Deploy EPC Portal

```
https://epc.saberrenewable.energy
```

## Implementation Steps

### Step 1: Configure saberrenewable.energy on Cloudflare

#### 1.1 Add to Cloudflare
```bash
1. Cloudflare Dashboard → Add Site
2. Enter: saberrenewable.energy
3. Copy nameservers
4. Update at Namecheap
```

#### 1.2 DNS Configuration
```
# Main domain - Redirect to marketing site
Type    Name    Target                  Proxy   Purpose
A       @       192.0.2.1              Yes     Dummy IP for redirect
CNAME   www     @                      Yes     Also redirects

# Subdomains - Internal apps
CNAME   epc     saber-epc-portal.pages.dev    Yes     EPC Portal
CNAME   fit     [future]                      Yes     FIT Intelligence
CNAME   calc    [future]                      Yes     Calculator
```

#### 1.3 Page Rule for Main Domain Redirect
```
URL: *saberrenewable.energy/*
Setting: Forwarding URL (301 Permanent)
Destination: https://saberrenewables.com/$1

URL: *www.saberrenewable.energy/*
Setting: Forwarding URL (301 Permanent)  
Destination: https://saberrenewables.com/$1
```

### Step 2: Deploy EPC Portal to epc.saberrenewable.energy

```bash
cd /home/marstack/saber_business_ops

# The existing deploy-to-cloudflare.sh already targets .energy
# Just run it!
./deploy-to-cloudflare.sh
```

### Step 3: Remove Duplicate Content from .energy

Since main saberrenewable.energy redirects to .com, we need to:
1. Remove WordPress from EasyWP for .energy domain
2. Set up redirect at Cloudflare level
3. This fixes the duplicate content SEO issue

## Quick Deployment Script

```bash
#!/bin/bash
# deploy-epc-today.sh

echo "Deploying EPC Portal to epc.saberrenewable.energy"

# 1. Ensure we're using .energy domain
DOMAIN="saberrenewable.energy"
SUBDOMAIN="epc"

# 2. Create/update GitHub repo
cd /home/marstack/saber_business_ops
git init
git add .
git commit -m "EPC Portal for $SUBDOMAIN.$DOMAIN"

# 3. Push to GitHub
gh repo create saber-epc-portal --public --source=. --push

# 4. Ready for Cloudflare Pages
echo "✅ Ready!"
echo "Next: Connect Cloudflare Pages to GitHub repo"
echo "URL will be: https://$SUBDOMAIN.$DOMAIN"
```

## Cloudflare Configuration

### For saberrenewable.energy

```yaml
# Page Rules
1. Main domain redirect:
   - URL: *saberrenewable.energy/*
   - Action: Forwarding URL (301)
   - Target: https://saberrenewables.com/$1

2. WWW redirect:
   - URL: *www.saberrenewable.energy/*
   - Action: Forwarding URL (301)
   - Target: https://saberrenewables.com/$1

# DNS Records
- A @ 192.0.2.1 (Proxied) - Dummy IP for redirect
- CNAME epc saber-epc-portal.pages.dev (Proxied)
- CNAME fit [future-deployment] (Proxied)
```

## Result After Today

```
✅ saberrenewables.com → Marketing site (unchanged)
✅ saberrenewable.energy → Redirects to .com (fixes SEO)
✅ epc.saberrenewable.energy → EPC Portal (live!)
✅ fit.saberrenewable.energy → Ready for FIT Intelligence
✅ No duplicate content issues
✅ Clean separation of public/internal
```

## Testing Checklist

- [ ] saberrenewable.energy redirects to saberrenewables.com
- [ ] www.saberrenewable.energy redirects to saberrenewables.com  
- [ ] epc.saberrenewable.energy loads EPC portal
- [ ] Form submission works (test code: ABCD1234)
- [ ] No duplicate content warnings in Google

## Future Apps on .energy

```
epc.saberrenewable.energy ✅ (Today)
fit.saberrenewable.energy (Next week)
calculator.saberrenewable.energy (Later)
dashboard.saberrenewable.energy
api.saberrenewable.energy
dev.saberrenewable.energy
```

## SEO Benefits

1. **No duplicate content** - Main domain redirects
2. **Clear domain purpose** - .com for public, .energy for apps
3. **Better crawling** - Google sees one marketing site
4. **Preserved authority** - 301 redirects pass SEO value

---

## Let's Do This!

1. Add saberrenewable.energy to Cloudflare
2. Set up redirects for main domain
3. Deploy EPC to epc.saberrenewable.energy
4. Test everything works

Ready to execute?
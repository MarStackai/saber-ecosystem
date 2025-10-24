# 🚀 DNS Transfer: Namecheap → Cloudflare

## Step-by-Step Guide (Do This Now!)

### Step 1: Add Domain to Cloudflare

1. **Go to Cloudflare Dashboard**
   - URL: https://dash.cloudflare.com
   - Click the **"Add a Site"** button

2. **Enter Your Domain**
   - Type: `saberrenewable.energy`
   - Click **Continue**

3. **Select Plan**
   - Choose **Free** plan ($0/month)
   - Click **Continue**

4. **Cloudflare Will Scan DNS Records**
   - Wait for scan to complete (30 seconds)
   - It will show existing DNS records from Namecheap

### Step 2: Review DNS Records

Cloudflare will show detected records. You should see something like:

| Type | Name | Content | Proxy Status | TTL |
|------|------|---------|--------------|-----|
| A | @ | [EasyWP IP] | Proxied | Auto |
| A | www | [EasyWP IP] | Proxied | Auto |
| MX | @ | [mail server] | DNS only | Auto |

**Important Actions:**
- ✅ Keep any MX records (for email)
- ✅ Keep any TXT records (for verification)
- ❌ Delete the A records pointing to EasyWP (we'll redirect instead)

### Step 3: Copy Cloudflare Nameservers

Cloudflare will show you 2 nameservers like:
```
adam.ns.cloudflare.com
bella.ns.cloudflare.com
```

**📝 WRITE THESE DOWN!**

### Step 4: Update Nameservers at Namecheap

1. **Login to Namecheap**
   - URL: https://www.namecheap.com
   - Go to **Domain List**

2. **Find saberrenewable.energy**
   - Click **Manage**

3. **Change Nameservers**
   - Find **NAMESERVERS** section
   - Change from **Namecheap BasicDNS** to **Custom DNS**
   - Add Cloudflare nameservers:
     - Nameserver 1: `[your-first].ns.cloudflare.com`
     - Nameserver 2: `[your-second].ns.cloudflare.com`
   - Click **✓** (checkmark) to save

### Step 5: Wait for Propagation

- **Typical time**: 5 minutes - 2 hours
- **Maximum**: 24-48 hours (rare)
- **Check status**: Cloudflare will email you when active

### Step 6: Configure DNS in Cloudflare (After Active)

Once Cloudflare shows "Active" status, configure these records:

```yaml
# For redirect to .com
Type: A
Name: @
Content: 192.0.2.1  # Dummy IP for redirect
Proxy: ON (orange cloud)

Type: CNAME
Name: www
Content: @
Proxy: ON

# For EPC Portal
Type: CNAME
Name: epc
Content: saber-epc-portal.pages.dev
Proxy: ON

# Future apps
Type: CNAME
Name: fit
Content: fit-intelligence.pages.dev
Proxy: ON (when ready)
```

### Step 7: Set Up Redirects

1. **Go to Rules → Page Rules**

2. **Create Page Rule #1**
   - URL: `*saberrenewable.energy/*`
   - Setting: **Forwarding URL** (301 Permanent)
   - Destination: `https://saberrenewables.com/$1`
   - Save

3. **Create Page Rule #2**
   - URL: `*www.saberrenewable.energy/*`
   - Setting: **Forwarding URL** (301 Permanent)
   - Destination: `https://saberrenewables.com/$1`
   - Save

## Quick Check Commands

After DNS propagates, test from terminal:

```bash
# Check nameservers
dig NS saberrenewable.energy

# Check if Cloudflare is active
dig saberrenewable.energy @1.1.1.1

# Test redirect (should show 301)
curl -I https://saberrenewable.energy
```

## What Happens Next

### Immediately After DNS Transfer:
- Email still works (MX records preserved)
- Site might be temporarily down (use dummy IP)
- Cloudflare starts providing SSL

### After Page Rules Setup:
- ✅ saberrenewable.energy → redirects to saberrenewables.com
- ✅ www.saberrenewable.energy → redirects to saberrenewables.com
- ✅ epc.saberrenewable.energy → ready for portal
- ✅ Duplicate content issue FIXED

## Troubleshooting

### If Email Stops Working:
- Check MX records are present in Cloudflare
- Set MX records to "DNS only" (gray cloud)

### If Site Doesn't Redirect:
- Check Page Rules are active
- Ensure A record uses dummy IP (192.0.2.1)
- Clear browser cache

### If DNS Won't Propagate:
- Double-check nameservers spelling
- Remove any extra nameservers (only 2)
- Wait full 24 hours before panicking

## Benefits You Get Immediately

1. **Free SSL Certificate** - Automatic HTTPS
2. **DDoS Protection** - Cloudflare shields your site
3. **Global CDN** - Faster loading worldwide
4. **Analytics** - See traffic patterns
5. **Page Rules** - Powerful redirects and caching
6. **API Access** - Programmatic control

---

## Ready? Start Now!

1. Open https://dash.cloudflare.com
2. Click "Add a Site"
3. Enter: saberrenewable.energy
4. Follow the steps above

I'll help you through each step!
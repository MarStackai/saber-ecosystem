# 🚀 Complete Migration Plan: Namecheap → Cloudflare

## Current Situation
- **Domain**: saberrenewable.energy (at Namecheap) 
- **Main Site**: Hosted on EasyWP (keep for now)
- **DNS**: Managed at Namecheap (needs migration)
- **Goal**: Host EPC portal at epc.saberrenewable.energy via Cloudflare

## Migration Strategy

### Phase 1: DNS Migration (Day 1)
**Move DNS from Namecheap to Cloudflare while keeping existing site working**

#### Step 1.1: Add Domain to Cloudflare
```bash
# 1. Login to Cloudflare Dashboard
# 2. Add Site → Enter: saberrenewable.energy
# 3. Select Free Plan
# 4. Cloudflare will scan existing DNS records
```

#### Step 1.2: Review & Import DNS Records
Cloudflare will auto-detect these (verify all are present):
```
Type    Name    Content                 Proxy   Notes
A       @       [EasyWP IP address]     Yes     Main site
A       www     [EasyWP IP address]     Yes     Main site redirect
MX      @       [Email server]          No      Keep email working
TXT     @       [SPF/verification]      No      Keep existing
```

#### Step 1.3: Update Nameservers at Namecheap
```
1. Login to Namecheap
2. Domain List → Manage → Nameservers
3. Change from "Namecheap BasicDNS" to "Custom DNS"
4. Add Cloudflare nameservers:
   - xxxx.ns.cloudflare.com
   - yyyy.ns.cloudflare.com
5. Save changes
```

**⏱️ DNS Propagation: 5 minutes - 48 hours (usually 2-4 hours)**

### Phase 2: Verify Migration (Day 1-2)

#### Check DNS Propagation
```bash
# Check if Cloudflare is active
dig saberrenewable.energy +short
nslookup saberrenewable.energy

# Verify nameservers
dig NS saberrenewable.energy

# Test website still works
curl -I https://saberrenewable.energy
```

#### Cloudflare Quick Wins (Immediate)
Once DNS is active in Cloudflare:
```
1. SSL/TLS → Full (Strict)
2. Security → Enable WAF
3. Speed → Auto Minify (JS, CSS, HTML)
4. Caching → Standard Level
5. Page Rules → Force HTTPS
```

### Phase 3: Deploy EPC Portal (Day 2)

#### Step 3.1: Create GitHub Repository
```bash
cd /home/marstack/saber_business_ops
git init
git add .
git commit -m "Initial commit: EPC Portal"
gh repo create saber-renewables/epc-portal --public --push
```

#### Step 3.2: Set Up Cloudflare Pages
```
1. Go to: dash.cloudflare.com → Pages
2. Create a project → Connect to Git
3. Select: saber-renewables/epc-portal
4. Configure:
   - Build command: cp -r public-deployment/* dist/
   - Build output: dist
   - Root directory: /
5. Deploy
```

#### Step 3.3: Add Subdomain in Cloudflare DNS
```
Type    Name    Content                         Proxy
CNAME   epc     saber-epc-portal.pages.dev     Yes (Orange)
```

✅ **Result**: `https://epc.saberrenewable.energy` → EPC Portal

### Phase 4: SharePoint Integration (Day 2-3)

#### Step 4.1: Create Cloudflare Worker
```javascript
// workers.cloudflare.com → Create Worker
export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    
    // CORS headers
    const corsHeaders = {
      'Access-Control-Allow-Origin': 'https://epc.saberrenewable.energy',
      'Access-Control-Allow-Methods': 'POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type',
    };
    
    if (request.method === 'OPTIONS') {
      return new Response(null, { headers: corsHeaders });
    }
    
    if (url.pathname === '/api/submit') {
      const data = await request.json();
      
      // Forward to Power Automate
      const response = await fetch(env.SHAREPOINT_WEBHOOK, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      });
      
      return new Response(
        JSON.stringify({ success: response.ok }),
        { headers: { ...corsHeaders, 'Content-Type': 'application/json' }}
      );
    }
    
    return new Response('API Ready', { status: 200 });
  }
};
```

#### Step 4.2: Add Worker Route
```
Workers → Your Worker → Triggers → Add Route
Route: epc.saberrenewable.energy/api/*
Zone: saberrenewable.energy
```

#### Step 4.3: Power Automate Flow
```
1. Create HTTP webhook in Power Automate
2. Add webhook URL to Worker environment variable
3. Configure flow to create SharePoint list items
```

### Phase 5: Keep Main Site Stable (Ongoing)

#### Current Setup (No Changes Needed)
```
saberrenewable.energy → EasyWP (via Cloudflare proxy)
www.saberrenewable.energy → EasyWP (via Cloudflare proxy)
```

#### Benefits of Cloudflare Proxy
- ✅ DDoS protection
- ✅ CDN caching
- ✅ SSL certificate
- ✅ Performance boost
- ✅ EasyWP continues working

### Phase 6: Future Migration (Optional)

#### Option A: Migrate Everything to Cloudflare Pages
```
Pros:
- Free hosting
- Better performance
- Git-based deployment
- No EasyWP limitations

Cons:
- Need to convert WordPress to static
- Time investment
```

#### Option B: Keep Hybrid Setup
```
Main site: EasyWP (WordPress)
EPC Portal: Cloudflare Pages (Static)
API: Cloudflare Workers
Data: SharePoint Lists
```

## 📋 Migration Checklist

### Day 1: DNS Migration
- [ ] Add domain to Cloudflare
- [ ] Copy all DNS records
- [ ] Update Namecheap nameservers
- [ ] Wait for propagation
- [ ] Verify site still works

### Day 2: Cloudflare Setup
- [ ] Configure SSL/TLS settings
- [ ] Enable security features
- [ ] Create GitHub repository
- [ ] Set up Cloudflare Pages
- [ ] Deploy EPC portal

### Day 3: Integration
- [ ] Create Cloudflare Worker
- [ ] Set up Power Automate
- [ ] Test form submission
- [ ] Verify SharePoint integration
- [ ] Document for ops team

## 🚨 Rollback Plan

If anything goes wrong:

### DNS Rollback (if needed)
```
1. Go to Namecheap
2. Change nameservers back to Namecheap defaults
3. Re-add DNS records in Namecheap
4. Wait for propagation
```

### Keep Main Site Safe
- Main site stays on EasyWP (no changes)
- Only new subdomain uses Cloudflare Pages
- Zero downtime for existing site

## 💰 Cost Analysis

### Current Costs
- Namecheap: ~$15/year (domain)
- EasyWP: ~$15-50/month (hosting)
- Total: ~$195-615/year

### After Migration
- Namecheap: ~$15/year (domain only)
- EasyWP: ~$15-50/month (main site)
- Cloudflare: FREE (DNS, CDN, Pages, Workers)
- Total: ~$195-615/year (SAME!)

### Added Benefits (FREE)
- ✅ DDoS protection
- ✅ Global CDN
- ✅ SSL certificates
- ✅ EPC portal hosting
- ✅ API endpoints
- ✅ Analytics
- ✅ Performance boost

## 🎯 Success Metrics

### Technical Success
- [ ] DNS resolves via Cloudflare
- [ ] Main site loads normally
- [ ] EPC portal accessible at subdomain
- [ ] Form submissions reach SharePoint
- [ ] No email disruption

### Business Success
- [ ] Partners can access forms
- [ ] Ops team can manage in SharePoint
- [ ] Faster page load times
- [ ] Improved security
- [ ] Professional appearance

## 📞 Support Contacts

### During Migration
- Cloudflare Support: dash.cloudflare.com/support
- Namecheap Support: namecheap.com/support
- EasyWP Support: easywp.com/support

### Documentation
- Cloudflare DNS: developers.cloudflare.com/dns
- Cloudflare Pages: developers.cloudflare.com/pages
- Power Automate: docs.microsoft.com/power-automate

---

## 🚀 Ready to Start?

**Step 1**: Login to Cloudflare and add saberrenewable.energy
**Step 2**: Follow the checklist above
**Step 3**: EPC portal live in 48 hours!

The beauty of this approach:
- Main site stays untouched on EasyWP
- New portal gets modern Cloudflare hosting
- Everything works together seamlessly
- Zero risk to existing operations
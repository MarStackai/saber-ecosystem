# 🎯 Strategic Domain Management Plan

## Current Situation
- **Domain Owner**: Ex-director (being difficult)
- **DNS Control**: You have it (good!)
- **Company Owner**: On your side
- **Risk**: Ex-director could pull domain anytime

## Strategic Approach: Parallel Operations

### Phase 1: Immediate Actions (While You Have DNS Control)

#### 1.1 Move .com DNS to Cloudflare NOW
```bash
# Since you control DNS, move it to Cloudflare immediately
1. Add saberrenewables.com to Cloudflare
2. Update nameservers (you control this!)
3. Lock down with these Cloudflare features:
   - Enable "Always Use HTTPS"
   - Turn on "Automatic HTTPS Rewrites"
   - Set up Page Rules for redirects
   - Enable full caching
```

#### 1.2 Create Critical Backups
```bash
# Document everything while you have access
- Screenshot all DNS records
- Export zone file
- Document all subdomains
- Save all configurations
- Email yourself the backups
```

#### 1.3 Set Up Both Domains in Parallel
```
saberrenewables.com (public face - while we have it)
├── www → WordPress site
├── epc → Partner portal (public facing)
└── [Keep using while available]

saberrenewable.energy (backup & internal)
├── epc → Same portal (backup/internal access)
├── fit → FIT Intelligence
├── ops → Business operations
└── [All critical operations]
```

### Phase 2: Dual Deployment Strategy

#### Deploy EPC to BOTH Domains
```bash
# Primary (public): epc.saberrenewables.com
# Backup (internal): epc.saberrenewable.energy

# Both pointing to same Cloudflare Pages project
# Users can access either URL
```

#### Configuration for Dual Domains
```javascript
// Cloudflare Worker - Accept both domains
export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const validDomains = [
      'epc.saberrenewables.com',
      'epc.saberrenewable.energy'
    ];
    
    // Accept requests from either domain
    const origin = url.hostname;
    if (!validDomains.includes(origin)) {
      return new Response('Invalid domain', { status: 403 });
    }
    
    // Process normally
    return handleRequest(request, env);
  }
}
```

### Phase 3: Legal/Business Strategy

#### Document Evidence
```
1. Email trails showing you manage DNS
2. Invoices showing company pays for hosting
3. Screenshots of current DNS control
4. Document that ex-director is not involved in operations
5. Keep records of his uncooperative behavior
```

#### Pressure Points
```
- Company owner should formally request domain transfer
- Document refusal in writing
- Consider legal action for business asset
- Domain is company property, not personal
- Threaten to stop using it publicly (damages its value)
```

#### Negotiation Tactics
```
Option 1: Buy him out
- Offer a one-time payment
- Get it in writing
- Transfer immediately

Option 2: Legal pressure
- Company lawyer sends demand letter
- Domain is company asset
- Holding it hostage = theft

Option 3: Public pressure
- Start messaging "We're moving to saberrenewable.energy"
- Reduces value of .com domain
- He might give in
```

### Phase 4: Migration Timeline

#### Month 1: Parallel Operations
- Both domains fully operational
- Start adding "Also visit us at saberrenewable.energy" to materials
- Email signatures include both

#### Month 2-3: Gradual Shift
- New materials use .energy
- SEO focus shifts to .energy
- Tell partners about "new domain"

#### Month 6: Full Transition (if needed)
- Primary operations on .energy
- .com becomes just a redirect
- Or abandoned if he won't cooperate

## Technical Implementation

### Immediate Cloudflare Setup (TODAY)

```bash
# 1. Add BOTH domains to Cloudflare
cloudflare-add saberrenewables.com    # While you have DNS control
cloudflare-add saberrenewable.energy  # Your backup

# 2. Deploy to both
git clone saber-epc-portal
cd saber-epc-portal

# 3. Configure for both domains
cat > wrangler.toml << EOF
name = "saber-epc-portal"
routes = [
  { pattern = "epc.saberrenewables.com/*", zone_name = "saberrenewables.com" },
  { pattern = "epc.saberrenewable.energy/*", zone_name = "saberrenewable.energy" }
]
EOF

# 4. Deploy
wrangler pages publish public-deployment
```

### DNS Configuration (Both Domains)

#### On saberrenewables.com (while you control it)
```
Type    Name    Target                      Proxy
A       @       [WordPress IP]              Yes
CNAME   www     @                          Yes
CNAME   epc     saber-epc-portal.pages.dev Yes
```

#### On saberrenewable.energy (your safety net)
```
Type    Name    Target                      Proxy
CNAME   epc     saber-epc-portal.pages.dev Yes
CNAME   fit     fit-intelligence.pages.dev Yes
CNAME   ops     business-ops.pages.dev     Yes
```

### Monitoring & Alerts

```javascript
// Cloudflare Worker - Domain monitoring
addEventListener('scheduled', event => {
  event.waitUntil(checkDomainControl())
})

async function checkDomainControl() {
  // Check if we still control .com DNS
  const dnsCheck = await fetch('https://saberrenewables.com/dns-check');
  
  if (!dnsCheck.ok) {
    // Alert immediately if we lose control
    await sendAlert('WARNING: Lost DNS control of saberrenewables.com');
    await triggerBackupPlan();
  }
}
```

## Communication Strategy

### Internal Team
```
"We're implementing redundancy with dual domains.
Primary: saberrenewables.com (while available)
Backup: saberrenewable.energy (always ours)
All systems work on both."
```

### Partners/Customers
```
"We're expanding our digital presence!
Visit us at either:
- saberrenewables.com
- saberrenewable.energy
Both work perfectly!"
```

### If Domain is Pulled
```
"We've upgraded to saberrenewable.energy!
Better performance, same great service.
Update your bookmarks!"
```

## Risk Mitigation

### If He Pulls Domain Tomorrow
✅ Cloudflare has cached everything
✅ You have DNS records backed up
✅ .energy domain ready to go
✅ Just update marketing materials
✅ Business continues uninterrupted

### If He Transfers DNS Control
✅ You already have everything on Cloudflare
✅ Switch to .energy as primary
✅ Email customers about "upgrade"
✅ His domain becomes worthless

### If He Cooperates Eventually
✅ Great! Transfer it properly
✅ Keep both domains forever
✅ Use .energy for internal ops
✅ Use .com for public face

## Action Items (DO TODAY)

### Critical (Today)
- [ ] Add saberrenewables.com to Cloudflare NOW
- [ ] Screenshot current DNS settings
- [ ] Export DNS zone file
- [ ] Add saberrenewable.energy to Cloudflare
- [ ] Deploy EPC portal to both domains

### Important (This Week)
- [ ] Set up monitoring alerts
- [ ] Document everything
- [ ] Brief company owner on situation
- [ ] Consult lawyer about domain ownership

### Strategic (This Month)
- [ ] Start dual-domain messaging
- [ ] Update business cards (both domains)
- [ ] SEO work on .energy domain
- [ ] Pressure ex-director for transfer

## Bottom Line

**Use the DNS control while you have it!** Get everything on Cloudflare TODAY. Deploy to both domains. If he pulls the domain, you're ready. If he doesn't, you have redundancy. Either way, you win.

The ex-director is holding a domain hostage that becomes worthless the moment you stop using it. Make sure he knows that.
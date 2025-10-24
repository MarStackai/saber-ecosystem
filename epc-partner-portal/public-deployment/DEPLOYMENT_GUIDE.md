# 🌐 Saber EPC Portal - Public Domain Deployment Guide

## Domain: saberrenewable.energy

This is a much better solution than SharePoint! Here's how to deploy the EPC Partner Portal to your public domain.

## 📁 File Structure

```
saberrenewable.energy/
├── index.html              # Main landing page
├── epc/
│   ├── apply.html         # Partner application (with invite code)
│   ├── form.html          # Main onboarding form
│   ├── login.html         # Partner login (future)
│   └── resources.html     # Resources page (future)
├── assets/
│   ├── css/
│   │   └── styles.css
│   ├── js/
│   │   └── form.js
│   └── images/
│       └── saber-logo.svg
└── api/
    └── submit.php         # Form submission handler
```

## 🚀 Deployment Steps

### 1. Upload Files via FTP/SFTP
```bash
# Connect to your server
sftp user@saberrenewable.energy

# Upload the public-deployment folder contents
put -r /home/marstack/saber_business_ops/public-deployment/* /var/www/html/
```

### 2. Set Proper Permissions
```bash
# Make files readable
chmod -R 755 /var/www/html/
chmod 644 /var/www/html/*.html
chmod 644 /var/www/html/epc/*.html
```

### 3. Configure Web Server

#### For Apache (.htaccess)
```apache
# Enable clean URLs
RewriteEngine On
RewriteCond %{REQUEST_FILENAME} !-f
RewriteCond %{REQUEST_FILENAME} !-d
RewriteRule ^epc/apply$ /epc/apply.html [L]
RewriteRule ^epc/form$ /epc/form.html [L]

# Security headers
Header set X-Frame-Options "SAMEORIGIN"
Header set X-Content-Type-Options "nosniff"
Header set X-XSS-Protection "1; mode=block"
```

#### For Nginx
```nginx
location /epc/ {
    try_files $uri $uri.html $uri/ =404;
}

# Security headers
add_header X-Frame-Options "SAMEORIGIN";
add_header X-Content-Type-Options "nosniff";
add_header X-XSS-Protection "1; mode=block";
```

## 🔗 Public URLs

### Main Portal
```
https://saberrenewable.energy/
```

### Partner Application (Invite Only)
```
https://saberrenewable.energy/epc/apply
```
- Test Code: `ABCD1234`

### Direct Form Access
```
https://saberrenewable.energy/epc/form
```

## 🔐 Backend Integration

### Option 1: Direct to SharePoint (via Power Automate)
Create a Power Automate flow that:
1. Receives POST requests from the form
2. Creates items in SharePoint lists
3. Sends confirmation emails

### Option 2: PHP Backend
```php
<?php
// api/submit.php
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: https://saberrenewable.energy');

$data = json_decode(file_get_contents('php://input'), true);

// Validate invitation code
if ($data['inviteCode'] !== 'ABCD1234') {
    http_response_code(403);
    echo json_encode(['error' => 'Invalid invitation code']);
    exit;
}

// Process form data
// Save to database or send to SharePoint API

echo json_encode(['success' => true, 'message' => 'Application submitted']);
?>
```

### Option 3: Node.js/Express Backend
```javascript
// api/server.js
const express = require('express');
const app = express();

app.post('/api/submit', (req, res) => {
    const { inviteCode, formData } = req.body;
    
    if (inviteCode !== 'ABCD1234') {
        return res.status(403).json({ error: 'Invalid code' });
    }
    
    // Process and save to database
    // Or forward to SharePoint
    
    res.json({ success: true });
});

app.listen(3000);
```

## ✅ Advantages Over SharePoint

| Feature | SharePoint | saberrenewable.energy |
|---------|------------|----------------------|
| Public Access | ❌ Requires login | ✅ Open to partners |
| Clean URLs | ❌ Complex paths | ✅ Simple, memorable |
| File Serving | ❌ Downloads files | ✅ Displays properly |
| Customization | ❌ Limited | ✅ Full control |
| Performance | ❌ Slower | ✅ Fast loading |
| SEO | ❌ Poor | ✅ Excellent |
| Mobile | ❌ Clunky | ✅ Responsive |
| Branding | ❌ SharePoint UI | ✅ Full Saber brand |

## 🎨 Features Included

- ✅ Saber blue header (#044D73)
- ✅ White logo on blue background
- ✅ 4-step application wizard
- ✅ Invite-only access control
- ✅ Drag-and-drop file uploads
- ✅ Mobile responsive design
- ✅ Loading animations
- ✅ Glass morphism effects
- ✅ Form validation
- ✅ Success notifications

## 📊 Analytics

Add Google Analytics or similar:
```html
<!-- Add to head of each HTML file -->
<script async src="https://www.googletagmanager.com/gtag/js?id=GA_MEASUREMENT_ID"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'GA_MEASUREMENT_ID');
</script>
```

## 🔧 Maintenance

### Update Invitation Codes
Edit the validation in:
- `/epc/apply.html` (JavaScript)
- Backend API endpoint

### Add New Partners
1. Generate unique invitation codes
2. Add to validation system
3. Track in database

### Monitor Applications
- Check server logs
- Review form submissions
- Track conversion rates

## 🚨 SSL Certificate

Ensure HTTPS is configured:
```bash
# Using Let's Encrypt
sudo certbot --nginx -d saberrenewable.energy -d www.saberrenewable.energy
```

## 📱 Testing Checklist

- [ ] Form displays correctly (no download)
- [ ] Logo and branding visible
- [ ] Invitation code validation works
- [ ] 4-step process functions
- [ ] File upload works
- [ ] Form submission successful
- [ ] Mobile responsive
- [ ] SSL certificate active
- [ ] Clean URLs working

## 🎉 Benefits

1. **Professional Image** - Clean domain for partners
2. **Easy Access** - No SharePoint login required  
3. **Full Control** - Complete customization
4. **Better Performance** - Fast, reliable hosting
5. **Scalability** - Easy to add features
6. **SEO Friendly** - Better search visibility
7. **Analytics** - Track user behavior
8. **Security** - Full control over access

---

**Ready to Deploy!** 🚀

The public domain solution at `saberrenewable.energy` is definitely the way to go for a professional, accessible partner portal!
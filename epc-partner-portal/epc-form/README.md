# EPC Partner Onboarding Form

Elegant, on-brand web form for Saber Renewables EPC partner onboarding submissions.

## Features

### 🎨 Saber Brand Implementation
- Custom gradient backgrounds with energy pulse animations
- Glass morphism effects on cards
- Montserrat/Source Sans Pro typography
- Green (#7CC061) and Blue (#044D73) brand colors
- Hover lift animations and smooth transitions

### 📝 Multi-Step Form
- 4-step progressive disclosure
- Visual progress indicator
- Form validation at each step
- Data persistence between steps

### 📋 Form Sections
1. **Company Details** - Business information and registration
2. **Contact Information** - Primary contact and coverage regions  
3. **Compliance & Accreditations** - ISO standards, HSEQ, policies
4. **Documents & Terms** - File uploads and agreement

### 📎 File Upload
- Drag & drop interface
- Multiple file support
- File type validation (PDF, DOC, DOCX, JPG, PNG)
- 10MB size limit per file
- Visual file list with remove option

### ✅ Validation
- Real-time field validation
- Email and phone format checking
- Required field enforcement
- Clear error messaging

### 📱 Responsive Design
- Mobile-first approach
- Touch-friendly interface
- Adaptive layouts for all screens

## Setup

### 1. Direct Hosting
```bash
# Copy files to web server
cp -r epc-form/* /var/www/html/epc-onboarding/

# Ensure logo is present
cp saber-logo.svg /var/www/html/epc-onboarding/
```

### 2. SharePoint Integration

#### Option A: SharePoint Page
1. Upload files to Site Assets
2. Create new Site Page
3. Embed using Content Editor web part
4. Reference uploaded assets

#### Option B: Power Apps Portal
1. Create new portal page
2. Add custom HTML/CSS/JS
3. Configure entity forms for SharePoint list

#### Option C: Direct REST API
```javascript
// Update sharepoint-integration.js with:
const connector = new SharePointConnector({
    siteUrl: 'YOUR_SITE_URL',
    clientId: 'YOUR_CLIENT_ID',
    tenant: 'YOUR_TENANT'
});
```

### 3. Power Automate Integration
1. Create HTTP trigger flow
2. Add "Create item" action for EPC Onboarding list
3. Map JSON fields to list columns
4. Return success response
5. Update flow URL in sharepoint-integration.js

## File Structure
```
epc-form/
├── index.html                 # Main form HTML
├── styles.css                 # Saber branded styles
├── script.js                  # Form logic & validation
├── sharepoint-integration.js # SharePoint connector
├── saber-logo.svg            # Company logo (add this)
└── README.md                 # Documentation
```

## Customization

### Brand Colors
Edit CSS variables in styles.css:
```css
:root {
    --saber-blue: #044D73;
    --saber-green: #7CC061;
    --dark-blue: #091922;
}
```

### Form Fields
Modify HTML form inputs and update SharePoint mapping in sharepoint-integration.js

### Validation Rules
Adjust validation logic in script.js validateField() function

## Testing

### Local Testing
```bash
# Start local server
python3 -m http.server 8000

# Open browser
http://localhost:8000/index.html
```

### Test Checklist
- [ ] All form steps navigate correctly
- [ ] Required fields validated
- [ ] File upload accepts correct types
- [ ] Responsive on mobile devices
- [ ] SharePoint submission successful
- [ ] Success modal displays
- [ ] Form resets after submission

## SharePoint Fields Mapping

| Form Field | SharePoint Column | Type |
|------------|------------------|------|
| companyName | CompanyName | Text |
| tradingName | TradingName | Text |
| registeredOffice | RegisteredOffice | Note |
| companyRegNo | CompanyRegNo | Text |
| vatNo | VATNo | Text |
| yearsTrading | YearsTrading | Number |
| primaryContactName | PrimaryContactName | Text |
| primaryContactEmail | PrimaryContactEmail | Text |
| primaryContactPhone | PrimaryContactPhone | Text |
| coverageRegion | CoverageRegion | MultiChoice |
| isoStandards | ISOStandards | MultiChoice |
| actsAsPrincipalContractor | ActsAsPrincipalContractor | Choice |
| actsAsPrincipalDesigner | ActsAsPrincipalDesigner | Choice |
| hasGDPRPolicy | HasGDPRPolicy | Choice |
| hsqIncidents | HSEQIncidentsLast5y | Number |
| riddor | RIDDORLast3y | Number |
| notes | NotesOrClarifications | Note |
| agreeToTerms | AgreeToSaberTerms | Choice |

## Browser Support
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Security Notes
- Implement MSAL authentication for production
- Use HTTPS for all connections
- Validate input server-side
- Sanitize file uploads
- Implement CAPTCHA for public forms

## Support
For issues or enhancements, contact the Saber Business Operations team.
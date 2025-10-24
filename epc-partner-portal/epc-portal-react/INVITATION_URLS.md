# Invitation URL Formats

Due to Cloudflare Pages limitations with query parameters in Next.js edge runtime, we use a static HTML handler for invitation codes.

## ✅ Working URL Formats

1. **Direct Link with Invitation Code (For SharePoint Emails)**
   - Format: `https://epc.saberrenewable.energy/invite.html?invitationCode=CODE`
   - Example: `https://epc.saberrenewable.energy/invite.html?invitationCode=C1D94680`
   - Automatically validates and redirects to the form

2. **Manual Entry Page**
   - URL: `https://epc.saberrenewable.energy/invite.html`
   - Shows a form where users can manually enter their invitation code
   - Validates the code and redirects to the form

## ❌ Non-Working Routes (Due to Edge Runtime Issues)

- `/apply` - Returns 500 error with query parameters
- `/apply?invitationCode=CODE` - Does not work

## SharePoint Email Template

Update the SharePoint email template to use:
```
https://epc.saberrenewable.energy/invite.html?invitationCode={{InvitationCode}}
```

## Technical Notes

- Query parameters with Next.js App Router on Cloudflare Pages have compatibility issues
- The static HTML handler (`invite.html`) bypasses these issues
- All invitation codes are automatically converted to uppercase
- Validation is performed against the D1 database
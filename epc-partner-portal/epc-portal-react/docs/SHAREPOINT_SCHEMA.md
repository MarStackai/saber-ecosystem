# SharePoint Schema for Extended EPC Form

## Current Basic Schema (Working)
Based on successful integration test with reference `EPC-1757531850900`:

### Existing Columns
- **Company Name** (Single line of text) - Required
- **Trading Name** (Single line of text) - Optional  
- **Email** (Single line of text) - Required
- **Phone** (Single line of text) - Optional
- **Registration Number** (Single line of text) - Optional
- **VAT Number** (Single line of text) - Optional
- **Address** (Multiple lines of text) - Optional
- **Reference Number** (Single line of text) - Auto-generated
- **Submission Date** (Date and Time) - Auto-populated

## Extended Schema Requirements (6-Page Form)

### Page 1: Company Information & Contacts
```
Company Information:
- Company Name* (existing)
- Trading Name (existing) 
- Registered Office Address* (existing - expand)
- Head Office Address (Multiple lines of text) - NEW
- Company Registration Number* (existing)
- VAT Number (existing)
- Parent or Holding Company (Single line of text) - NEW
- Years Trading (Number) - NEW

Primary Contact:
- Full Name* (Single line of text) - NEW
- Job Title (Single line of text) - NEW  
- Phone Number* (existing)
- Email Address* (existing)
```

### Page 2: Services, Roles & Experience
```
Services & Experience:
- Services Provided (Choice - Multi-select) - NEW
  Options: [EPC Assessment, Retrofit Assessment, Air Testing, Thermography, Energy Auditing, Renewable Installation, Other]
- Specializations (Multiple lines of text) - NEW
- Software Tools Used (Multiple lines of text) - NEW
- Average Projects Per Month (Number) - NEW

Roles & Capabilities:
- Acts as Principal Contractor (Yes/No) - NEW
- PC Scale of Projects Last Year (Single line of text) - NEW [Conditional]
- Acts as Principal Designer (Yes/No) - NEW  
- PD Scale of Projects Last Year (Single line of text) - NEW [Conditional]
- Internal Staff Percentage (Number) - NEW
- Subcontract Labour Percentage (Number) - NEW
```

### Page 3: Certifications & Insurance
```
Certifications & Accreditations:
- ISO Certifications (Choice - Multi-select) - NEW
  Options: [ISO 9001, ISO 14001, ISO 27001, ISO 45001]
- Construction Scheme Accreditations (Choice - Multi-select) - NEW
  Options: [ConstructionLine, CHAS, SMAS, SafeContractor]
- NICEIC CPS Contractor (Yes/No) - NEW
- MCS Approved Contractor (Yes/No) - NEW
- Supporting Certificates (Attachment) - NEW

Insurance:
- Public Product Liability Insurance (Yes/No) - NEW
- PPL Policy Document (Attachment) - NEW [Conditional]
- PPL Indemnity in Principle Clause (Yes/No) - NEW [Conditional]
- Employers Liability Insurance (Yes/No) - NEW
- EL Policy Document (Attachment) - NEW [Conditional]
- Professional Indemnity Insurance (Yes/No) - NEW
- PI Policy Document (Attachment) - NEW [Conditional]
- PPL Expiry Date (Date) - NEW
- EL Expiry Date (Date) - NEW  
- PI Expiry Date (Date) - NEW
```

### Page 4: Health, Safety, Quality & Policies
```
Health & Safety:
- HSE Improvement Notices Last 5 Years (Yes/No) - NEW
- HSE Notice Details (Multiple lines of text) - NEW [Conditional]
- RIDDOR Incidents Last 3 Years (Number) - NEW
- RIDDOR Incident Details (Multiple lines of text) - NEW [Conditional]
- HS CDM Management Evidence (Attachment) - NEW
- Named Principal Designer (Single line of text) - NEW
- Principal Designer Qualifications (Attachment) - NEW
- Training Records (Attachment) - NEW
- Accident Near Miss Reporting Procedure (Yes/No) - NEW
- Accident Procedure Details (Multiple lines of text) - NEW [Conditional]
- Quality Assurance Evidence (Attachment) - NEW

Policies:
- Health Safety Policy (Attachment) - NEW
- Environmental Sustainability Policy (Attachment) - NEW
- Modern Slavery Policy (Attachment) - NEW
- Misuse of Substances Policy (Attachment) - NEW
- Right to Work Monitoring Method (Multiple lines of text) - NEW
- Training Certifications List (Attachment) - NEW

Data Protection & IT:
- GDPR Policy (Attachment) - NEW
- Cyber Incident Last 3 Years (Yes/No) - NEW
- Cyber Incident Details (Multiple lines of text) - NEW [Conditional]
```

### Page 5: Delivery Capability & References
```
Delivery Capability:
- Capability Statement (Attachment) - NEW
- Works Methodology (Attachment) - NEW
- Resourcing Approach (Multiple lines of text) - NEW
- Team CVs (Attachment) - NEW
- Subcontractors Consultants List (Attachment) - NEW

Project References:
- Nationwide Coverage (Yes/No) - NEW
- Regions Covered (Choice - Multi-select) - NEW [Conditional]
  Options: [London, South East, South West, West Midlands, East Midlands, East of England, Yorkshire Humber, North West, North East, Scotland, Wales, Northern Ireland]
- Client Reference Case Study (Attachment) - NEW
```

### Page 6: Legal, Agreement & Submission
```
Legal & Compliance:
- Pending Prosecutions (Yes/No) - NEW
- Prosecution Details (Multiple lines of text) - NEW [Conditional]
- EPC OM Contracts Reviewed (Yes/No) - NEW
- Legal Clarifications (Multiple lines of text) - NEW

Agreement:
- Received Contract Overview Pack (Yes/No) - NEW
- Willing to Work Under Saber Terms (Yes/No) - NEW
- Agree to Codes of Practice (Yes/No) - NEW
- Consent to Data Processing (Yes/No) - NEW
- Consent to Marketing Communications (Yes/No) - NEW

Submission:
- Additional Information (Multiple lines of text) - NEW
- Submission Complete (Yes/No) - Auto-calculated
- Evidence Checklist Score (Number) - Auto-calculated
```

## Document Libraries Required

### Primary Document Library: "EPC_Application_Documents"
Folder structure per application (by Reference Number):
```
/EPC-{reference}/
  /certificates/
  /policies/  
  /insurance/
  /cvs/
  /case-studies/
  /capability-statements/
```

### Document Types by Category
```
Certificates: PDF, JPG, PNG
Policies: PDF, DOCX
Insurance: PDF
CVs: PDF, DOCX  
Case Studies: PDF, DOCX, PPT
Capability Statements: PDF, DOCX
Evidence Documents: PDF, JPG, PNG
```

## Implementation Notes

### Data Validation Rules
- Percentage fields (Internal Staff % + Subcontract %) must total 100%
- Conditional fields only show when trigger condition is met
- Required attachments based on Yes/No responses
- Date validations for policy expiry dates

### Permissions
- EPC Application list: Contribute for service account
- Document library: Contribute with versioning enabled
- View access for Saber team members

### Indexing for Performance  
- Index on: Reference Number, Company Name, Email, Submission Date
- Search scope: Company Name, Email, Services Provided

## Migration Strategy
1. Add new columns in phases to avoid disruption
2. Test with sample data before production deployment  
3. Update Cloudflare Worker mappings incrementally
4. Maintain backward compatibility during transition
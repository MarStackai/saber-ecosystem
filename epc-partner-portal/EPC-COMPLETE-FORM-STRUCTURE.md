# Complete EPC Partner Onboarding Form Structure

## 6-Step Form Design

### Step 1: Company Information
**Purpose:** Basic company registration and legal details
- `companyName` (text) * - Legal company name
- `tradingName` (text) - Trading name (if different)
- `registeredOffice` (textarea) * - Full registered address
- `companyRegNo` (text) * - Companies House registration number
- `vatNo` (text) - VAT registration number
- `yearsTrading` (number) * - Years in business
- `companyType` (select) * - Sole Trader/Partnership/Limited Company/PLC
- `annualTurnover` (select) * - <£100k/£100k-£500k/£500k-£2M/£2M+

### Step 2: Contact & Personnel Information
**Purpose:** Key contact details and team structure
- `primaryContactName` (text) * - Main contact person
- `contactTitle` (text) * - Job title/position
- `primaryContactEmail` (email) * - Primary email
- `primaryContactPhone` (tel) * - Contact telephone
- `secondaryContactName` (text) - Backup contact
- `secondaryContactEmail` (email) - Backup email
- `teamSize` (number) * - Total employees
- `technicalStaff` (number) * - Number of qualified engineers
- `coverageRegion` (checkbox) * - Service areas

### Step 3: Services & Experience
**Purpose:** Technical capabilities and service offerings
- `services` (checkbox) * - EPC services offered:
  - Energy Performance Certificates (Commercial)
  - Energy Performance Certificates (Residential)
  - Display Energy Certificates (DEC)
  - Air Conditioning Inspections (ACI)
  - Non-Domestic RdSAP
  - SBEM Assessments
- `specializations` (checkbox) - Building specializations:
  - Offices
  - Retail
  - Industrial
  - Healthcare
  - Education
  - Hospitality
  - Residential
- `softwareUsed` (checkbox) * - Assessment software:
  - iQ Energy
  - Elmhurst Energy
  - Stroma
  - Other (specify)
- `projectsPerMonth` (select) * - Average monthly EPC volume:
  - 1-10/11-50/51-100/100+

### Step 4: Qualifications & Compliance
**Purpose:** Professional qualifications and compliance status
- `leadAssessorName` (text) * - Lead assessor name
- `leadAssessorAccreditation` (select) * - Accreditation scheme:
  - Elmhurst Energy/Stroma/Sterling/Other
- `accreditationNumber` (text) * - Lead assessor accreditation number
- `accreditationExpiry` (date) * - Accreditation expiry date
- `isoStandards` (checkbox) - ISO certifications held
- `insuranceProvider` (text) * - Professional indemnity insurer
- `insuranceAmount` (select) * - Coverage amount
- `insuranceExpiry` (date) * - Insurance expiry date
- `actsAsPrincipalContractor` (radio) - CDM principal contractor role
- `actsAsPrincipalDesigner` (radio) - CDM principal designer role
- `hasGDPRPolicy` (radio) - GDPR compliance policy
- `dataProtectionRegistration` (text) - ICO registration number

### Step 5: Health, Safety & Quality
**Purpose:** Safety record and quality management
- `healthSafetyPolicy` (radio) * - Written H&S policy in place
- `hsqIncidents` (number) * - HSEQ incidents (last 5 years)
- `riddor` (number) * - RIDDOR reportables (last 3 years)
- `safetyTraining` (checkbox) * - Safety training provided:
  - Manual Handling
  - Working at Height
  - Electrical Safety
  - Asbestos Awareness
  - Site Safety
- `qualityAssurance` (radio) * - Quality management system in place
- `complaintsProcedure` (radio) * - Formal complaints procedure
- `publicLiabilityInsurance` (text) * - Public liability insurer
- `employersLiabilityInsurance` (text) * - Employers liability insurer

### Step 6: Documents & Agreement
**Purpose:** Document upload and final agreement
- `documents` (file upload) - Supporting documents:
  - Public/Employers Liability Insurance
  - Professional Indemnity Insurance
  - Assessor Accreditation Certificates
  - Company Registration Certificate
  - Sample EPC Reports
  - Health & Safety Policy
  - GDPR Privacy Notice
- `additionalInfo` (textarea) - Additional information
- `notes` (textarea) - Internal notes/clarifications
- `marketingConsent` (checkbox) - Marketing communications consent
- `dataProcessingConsent` (checkbox) * - Data processing consent
- `agreeToTerms` (checkbox) * - Terms and conditions agreement
- `agreeToCodes` (checkbox) * - Professional codes of conduct

## Field Validation Rules

### Required Fields (*)
All fields marked with * are mandatory for form submission

### Data Validation
- Email addresses: Standard email format validation
- Phone numbers: UK format validation
- Dates: Future dates for expiry fields
- Numbers: Non-negative integers only
- Files: PDF, DOC, DOCX, JPG, PNG (max 10MB each)

### Conditional Logic
- If `companyType` = "Sole Trader", hide VAT field
- If `teamSize` < 5, require justification for technical capability
- If any insurance expiry < 30 days, show warning
- If `hsqIncidents` > 0, require explanation

## Progress Tracking
- Step completion percentage
- Save progress functionality
- Field validation on step change
- Summary review before submission

## Enhanced Features
- Auto-save draft every 30 seconds
- Field hints and help tooltips
- Document upload with preview
- Real-time validation feedback
- Mobile-responsive design
- Accessibility compliance (WCAG 2.1)

## Data Flow Integration
- All fields mapped to SharePoint EPC Onboarding list
- Document uploads to SharePoint document library
- Email notifications with complete application data
- Automated compliance scoring based on responses
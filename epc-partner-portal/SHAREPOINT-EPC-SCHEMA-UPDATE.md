# EPC Onboarding List - Complete Schema Update

## Overview
This document outlines the required SharePoint list schema updates to support the enhanced 6-step EPC partner onboarding form with 50+ comprehensive assessment fields.

## Current Basic Schema (19 fields)
The existing EPC Onboarding list contains these basic fields:
- CompanyName (Single line of text)
- RegistrationNumber (Single line of text)
- ContactName (Single line of text)
- ContactTitle (Single line of text)
- Email (Single line of text)
- Phone (Single line of text)
- Address (Multiple lines of text)
- Services (Multiple lines of text)
- YearsExperience (Number)
- TeamSize (Number)
- Coverage (Multiple lines of text)
- Certifications (Multiple lines of text)
- InvitationCode (Single line of text)
- SubmissionDate (Date and Time)
- Status (Choice: New/InReview/Approved/Rejected)

## Required New Columns for Complete Form

### Step 1: Enhanced Company Information
```powershell
# Company Type
Add-PnPField -List "EPC Onboarding" -DisplayName "Company Type" -InternalName "CompanyType" -Type Choice -Choices "Sole Trader","Partnership","Limited Company","Public Limited Company"

# Trading Name
Add-PnPField -List "EPC Onboarding" -DisplayName "Trading Name" -InternalName "TradingName" -Type Text

# VAT Number
Add-PnPField -List "EPC Onboarding" -DisplayName "VAT Number" -InternalName "VATNumber" -Type Text

# Annual Turnover
Add-PnPField -List "EPC Onboarding" -DisplayName "Annual Turnover" -InternalName "AnnualTurnover" -Type Choice -Choices "Under £100,000","£100,000 - £500,000","£500,000 - £2,000,000","Over £2,000,000"
```

### Step 2: Enhanced Contact & Personnel
```powershell
# Secondary Contact Fields
Add-PnPField -List "EPC Onboarding" -DisplayName "Secondary Contact Name" -InternalName "SecondaryContactName" -Type Text

Add-PnPField -List "EPC Onboarding" -DisplayName "Secondary Contact Email" -InternalName "SecondaryContactEmail" -Type Text

# Technical Staff
Add-PnPField -List "EPC Onboarding" -DisplayName "Technical Staff Count" -InternalName "TechnicalStaff" -Type Number

# Enhanced Coverage Regions (Multi-choice)
Add-PnPField -List "EPC Onboarding" -DisplayName "Coverage Regions" -InternalName "CoverageRegions" -Type MultiChoice -Choices "North West","North East","Yorkshire","Midlands","South East","South West","Scotland","Wales","Northern Ireland"
```

### Step 3: Services & Experience
```powershell
# EPC Services Offered
Add-PnPField -List "EPC Onboarding" -DisplayName "EPC Services Offered" -InternalName "EPCServicesOffered" -Type MultiChoice -Choices "Commercial EPC","Residential EPC","Display Energy Certificates","Air Conditioning Inspections","Non-Domestic RdSAP","SBEM Assessments"

# Building Specializations
Add-PnPField -List "EPC Onboarding" -DisplayName "Building Specializations" -InternalName "BuildingSpecializations" -Type MultiChoice -Choices "Offices","Retail","Industrial","Healthcare","Education","Hospitality","Residential"

# Assessment Software
Add-PnPField -List "EPC Onboarding" -DisplayName "Assessment Software" -InternalName "AssessmentSoftware" -Type MultiChoice -Choices "iQ Energy","Elmhurst Energy","Stroma","Other"

# Monthly Project Volume
Add-PnPField -List "EPC Onboarding" -DisplayName "Monthly EPC Volume" -InternalName "MonthlyEPCVolume" -Type Choice -Choices "1-10","11-50","51-100","100+"
```

### Step 4: Qualifications & Compliance
```powershell
# Lead Assessor Details
Add-PnPField -List "EPC Onboarding" -DisplayName "Lead Assessor Name" -InternalName "LeadAssessorName" -Type Text

Add-PnPField -List "EPC Onboarding" -DisplayName "Accreditation Scheme" -InternalName "AccreditationScheme" -Type Choice -Choices "Elmhurst Energy","Stroma","Sterling","Other"

Add-PnPField -List "EPC Onboarding" -DisplayName "Accreditation Number" -InternalName "AccreditationNumber" -Type Text

Add-PnPField -List "EPC Onboarding" -DisplayName "Accreditation Expiry" -InternalName "AccreditationExpiry" -Type DateTime

# Insurance Details
Add-PnPField -List "EPC Onboarding" -DisplayName "PI Insurance Provider" -InternalName "PIInsuranceProvider" -Type Text

Add-PnPField -List "EPC Onboarding" -DisplayName "PI Insurance Amount" -InternalName "PIInsuranceAmount" -Type Choice -Choices "£100,000","£250,000","£500,000","£1,000,000","£2,000,000+"

Add-PnPField -List "EPC Onboarding" -DisplayName "PI Insurance Expiry" -InternalName "PIInsuranceExpiry" -Type DateTime

# Compliance Fields
Add-PnPField -List "EPC Onboarding" -DisplayName "ICO Registration" -InternalName "ICORegistration" -Type Text

Add-PnPField -List "EPC Onboarding" -DisplayName "Acts as Principal Contractor" -InternalName "ActsAsPrincipalContractor" -Type Choice -Choices "Yes","No" -DefaultValue "No"

Add-PnPField -List "EPC Onboarding" -DisplayName "Acts as Principal Designer" -InternalName "ActsAsPrincipalDesigner" -Type Choice -Choices "Yes","No" -DefaultValue "No"

Add-PnPField -List "EPC Onboarding" -DisplayName "Has GDPR Policy" -InternalName "HasGDPRPolicy" -Type Choice -Choices "Yes","No" -DefaultValue "No"
```

### Step 5: Health, Safety & Quality
```powershell
# Health & Safety
Add-PnPField -List "EPC Onboarding" -DisplayName "Health Safety Policy" -InternalName "HealthSafetyPolicy" -Type Choice -Choices "Yes","No" -DefaultValue "No"

Add-PnPField -List "EPC Onboarding" -DisplayName "HSEQ Incidents (5yr)" -InternalName "HSEQIncidents" -Type Number

Add-PnPField -List "EPC Onboarding" -DisplayName "RIDDOR Reportable (3yr)" -InternalName "RIDDORReportable" -Type Number

Add-PnPField -List "EPC Onboarding" -DisplayName "Safety Training Provided" -InternalName "SafetyTrainingProvided" -Type MultiChoice -Choices "Manual Handling","Working at Height","Electrical Safety","Asbestos Awareness","Site Safety"

# Quality Management
Add-PnPField -List "EPC Onboarding" -DisplayName "Quality Assurance System" -InternalName "QualityAssuranceSystem" -Type Choice -Choices "Yes","No" -DefaultValue "No"

Add-PnPField -List "EPC Onboarding" -DisplayName "Complaints Procedure" -InternalName "ComplaintsProcedure" -Type Choice -Choices "Yes","No" -DefaultValue "No"

# Additional Insurance
Add-PnPField -List "EPC Onboarding" -DisplayName "Public Liability Insurer" -InternalName "PublicLiabilityInsurer" -Type Text

Add-PnPField -List "EPC Onboarding" -DisplayName "Employers Liability Insurer" -InternalName "EmployersLiabilityInsurer" -Type Text
```

### Step 6: Documents & Agreements
```powershell
# Additional Information
Add-PnPField -List "EPC Onboarding" -DisplayName "Additional Information" -InternalName "AdditionalInformation" -Type Note

Add-PnPField -List "EPC Onboarding" -DisplayName "Internal Notes" -InternalName "InternalNotes" -Type Note

# Consent & Agreements
Add-PnPField -List "EPC Onboarding" -DisplayName "Marketing Consent" -InternalName "MarketingConsent" -Type Boolean -DefaultValue 0

Add-PnPField -List "EPC Onboarding" -DisplayName "Data Processing Consent" -InternalName "DataProcessingConsent" -Type Boolean -DefaultValue 0

Add-PnPField -List "EPC Onboarding" -DisplayName "Terms Agreement" -InternalName "TermsAgreement" -Type Boolean -DefaultValue 0

Add-PnPField -List "EPC Onboarding" -DisplayName "Codes of Conduct Agreement" -InternalName "CodesOfConductAgreement" -Type Boolean -DefaultValue 0

# Metadata
Add-PnPField -List "EPC Onboarding" -DisplayName "Form Version" -InternalName "FormVersion" -Type Text -DefaultValue "Complete-v2.0"

Add-PnPField -List "EPC Onboarding" -DisplayName "Attachment Count" -InternalName "AttachmentCount" -Type Number -DefaultValue 0
```

## PowerShell Script for Complete Schema Update

```powershell
# Complete EPC Onboarding Schema Update Script
# Run this script to add all new columns for the enhanced form

Connect-PnPOnline -Url "https://saberrenewables.sharepoint.com/sites/SaberEPCPartners" -Interactive

$listName = "EPC Onboarding"

Write-Host "Adding enhanced company information fields..." -ForegroundColor Green

# Step 1: Enhanced Company Information
Add-PnPField -List $listName -DisplayName "Company Type" -InternalName "CompanyType" -Type Choice -Choices "Sole Trader","Partnership","Limited Company","Public Limited Company"
Add-PnPField -List $listName -DisplayName "Trading Name" -InternalName "TradingName" -Type Text
Add-PnPField -List $listName -DisplayName "VAT Number" -InternalName "VATNumber" -Type Text
Add-PnPField -List $listName -DisplayName "Annual Turnover" -InternalName "AnnualTurnover" -Type Choice -Choices "Under £100,000","£100,000 - £500,000","£500,000 - £2,000,000","Over £2,000,000"

Write-Host "Adding enhanced contact and personnel fields..." -ForegroundColor Green

# Step 2: Enhanced Contact & Personnel
Add-PnPField -List $listName -DisplayName "Secondary Contact Name" -InternalName "SecondaryContactName" -Type Text
Add-PnPField -List $listName -DisplayName "Secondary Contact Email" -InternalName "SecondaryContactEmail" -Type Text
Add-PnPField -List $listName -DisplayName "Technical Staff Count" -InternalName "TechnicalStaff" -Type Number
Add-PnPField -List $listName -DisplayName "Coverage Regions" -InternalName "CoverageRegions" -Type MultiChoice -Choices "North West","North East","Yorkshire","Midlands","South East","South West","Scotland","Wales","Northern Ireland"

Write-Host "Adding services and experience fields..." -ForegroundColor Green

# Step 3: Services & Experience
Add-PnPField -List $listName -DisplayName "EPC Services Offered" -InternalName "EPCServicesOffered" -Type MultiChoice -Choices "Commercial EPC","Residential EPC","Display Energy Certificates","Air Conditioning Inspections","Non-Domestic RdSAP","SBEM Assessments"
Add-PnPField -List $listName -DisplayName "Building Specializations" -InternalName "BuildingSpecializations" -Type MultiChoice -Choices "Offices","Retail","Industrial","Healthcare","Education","Hospitality","Residential"
Add-PnPField -List $listName -DisplayName "Assessment Software" -InternalName "AssessmentSoftware" -Type MultiChoice -Choices "iQ Energy","Elmhurst Energy","Stroma","Other"
Add-PnPField -List $listName -DisplayName "Monthly EPC Volume" -InternalName "MonthlyEPCVolume" -Type Choice -Choices "1-10","11-50","51-100","100+"

Write-Host "Adding qualifications and compliance fields..." -ForegroundColor Green

# Step 4: Qualifications & Compliance
Add-PnPField -List $listName -DisplayName "Lead Assessor Name" -InternalName "LeadAssessorName" -Type Text
Add-PnPField -List $listName -DisplayName "Accreditation Scheme" -InternalName "AccreditationScheme" -Type Choice -Choices "Elmhurst Energy","Stroma","Sterling","Other"
Add-PnPField -List $listName -DisplayName "Accreditation Number" -InternalName "AccreditationNumber" -Type Text
Add-PnPField -List $listName -DisplayName "Accreditation Expiry" -InternalName "AccreditationExpiry" -Type DateTime
Add-PnPField -List $listName -DisplayName "PI Insurance Provider" -InternalName "PIInsuranceProvider" -Type Text
Add-PnPField -List $listName -DisplayName "PI Insurance Amount" -InternalName "PIInsuranceAmount" -Type Choice -Choices "£100,000","£250,000","£500,000","£1,000,000","£2,000,000+"
Add-PnPField -List $listName -DisplayName "PI Insurance Expiry" -InternalName "PIInsuranceExpiry" -Type DateTime
Add-PnPField -List $listName -DisplayName "ICO Registration" -InternalName "ICORegistration" -Type Text

Write-Host "Adding health, safety and quality fields..." -ForegroundColor Green

# Step 5: Health, Safety & Quality
Add-PnPField -List $listName -DisplayName "Health Safety Policy" -InternalName "HealthSafetyPolicy" -Type Choice -Choices "Yes","No"
Add-PnPField -List $listName -DisplayName "HSEQ Incidents (5yr)" -InternalName "HSEQIncidents" -Type Number
Add-PnPField -List $listName -DisplayName "RIDDOR Reportable (3yr)" -InternalName "RIDDORReportable" -Type Number
Add-PnPField -List $listName -DisplayName "Safety Training Provided" -InternalName "SafetyTrainingProvided" -Type MultiChoice -Choices "Manual Handling","Working at Height","Electrical Safety","Asbestos Awareness","Site Safety"
Add-PnPField -List $listName -DisplayName "Quality Assurance System" -InternalName "QualityAssuranceSystem" -Type Choice -Choices "Yes","No"
Add-PnPField -List $listName -DisplayName "Complaints Procedure" -InternalName "ComplaintsProcedure" -Type Choice -Choices "Yes","No"
Add-PnPField -List $listName -DisplayName "Public Liability Insurer" -InternalName "PublicLiabilityInsurer" -Type Text
Add-PnPField -List $listName -DisplayName "Employers Liability Insurer" -InternalName "EmployersLiabilityInsurer" -Type Text

Write-Host "Adding documents and agreement fields..." -ForegroundColor Green

# Step 6: Documents & Agreements
Add-PnPField -List $listName -DisplayName "Additional Information" -InternalName "AdditionalInformation" -Type Note
Add-PnPField -List $listName -DisplayName "Internal Notes" -InternalName "InternalNotes" -Type Note
Add-PnPField -List $listName -DisplayName "Marketing Consent" -InternalName "MarketingConsent" -Type Boolean
Add-PnPField -List $listName -DisplayName "Data Processing Consent" -InternalName "DataProcessingConsent" -Type Boolean
Add-PnPField -List $listName -DisplayName "Terms Agreement" -InternalName "TermsAgreement" -Type Boolean
Add-PnPField -List $listName -DisplayName "Codes of Conduct Agreement" -InternalName "CodesOfConductAgreement" -Type Boolean
Add-PnPField -List $listName -DisplayName "Form Version" -InternalName "FormVersion" -Type Text
Add-PnPField -List $listName -DisplayName "Attachment Count" -InternalName "AttachmentCount" -Type Number

Write-Host "Schema update complete! Total new fields added: 35" -ForegroundColor Green
Write-Host "Total EPC Onboarding fields: 50+" -ForegroundColor Yellow
```

## Updated Power Automate Schema

The Power Automate workflow will need to be updated to handle the new fields. The HTTP trigger schema should include all new fields:

```json
{
  "type": "object",
  "properties": {
    // Existing fields (19)...
    
    // New Step 1 fields
    "companyType": {"type": "string"},
    "tradingName": {"type": "string"},
    "vatNumber": {"type": "string"},
    "annualTurnover": {"type": "string"},
    
    // New Step 2 fields
    "secondaryContactName": {"type": "string"},
    "secondaryContactEmail": {"type": "string"},
    "technicalStaff": {"type": "number"},
    
    // New Step 3 fields
    "servicesOffered": {"type": "string"},
    "buildingSpecializations": {"type": "string"},
    "softwareUsed": {"type": "string"},
    "projectsPerMonth": {"type": "string"},
    
    // New Step 4 fields
    "leadAssessorName": {"type": "string"},
    "leadAssessorAccreditation": {"type": "string"},
    "accreditationNumber": {"type": "string"},
    "accreditationExpiry": {"type": "string"},
    "insuranceProvider": {"type": "string"},
    "insuranceAmount": {"type": "string"},
    "insuranceExpiry": {"type": "string"},
    "dataProtectionRegistration": {"type": "string"},
    
    // New Step 5 fields
    "healthSafetyPolicy": {"type": "string"},
    "safetyTraining": {"type": "string"},
    "qualityAssurance": {"type": "string"},
    "complaintsProcedure": {"type": "string"},
    "publicLiabilityInsurance": {"type": "string"},
    "employersLiabilityInsurance": {"type": "string"},
    
    // New Step 6 fields
    "additionalInfo": {"type": "string"},
    "marketingConsent": {"type": "boolean"},
    "dataProcessingConsent": {"type": "boolean"},
    "agreeToCodes": {"type": "boolean"},
    "formVersion": {"type": "string"}
  }
}
```

## Migration Strategy

1. **Phase 1**: Add all new columns to existing SharePoint list
2. **Phase 2**: Update Power Automate workflow to handle new fields
3. **Phase 3**: Deploy enhanced Cloudflare Worker
4. **Phase 4**: Switch frontend to use complete form
5. **Phase 5**: Maintain backward compatibility with basic form

## Benefits of Enhanced Schema

- **Comprehensive Assessment**: 50+ fields for thorough partner evaluation
- **Regulatory Compliance**: Enhanced H&S, insurance, and qualification tracking
- **Business Intelligence**: Detailed service capabilities and specialization data
- **Risk Management**: Insurance tracking, incident history, and compliance status
- **Quality Assurance**: Formal training, procedures, and quality management
- **Legal Protection**: Clear consent tracking and agreement documentation

## Testing Requirements

- [ ] Verify all new columns are created successfully
- [ ] Test form submission with complete data set
- [ ] Validate Power Automate workflow processes all fields
- [ ] Confirm SharePoint list displays all data correctly
- [ ] Test backward compatibility with existing basic submissions
- [ ] Verify email notifications include relevant new field data

---

**Version**: 2.0  
**Created**: September 2025  
**Status**: Ready for Implementation
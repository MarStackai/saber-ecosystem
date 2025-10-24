# React Form to SharePoint Field Mapping

## Overview
This document maps the React form field names to the SharePoint internal names defined in the PnP PowerShell provisioning script.

## Page 1: Company Information & Contacts

### Company Information Section
| React Form Field | React Field Name | SharePoint Internal Name | SharePoint Type | Required | Notes |
|---|---|---|---|---|---|
| Company Name | `companyName` | `CompanyName` | Text | ✅ | Main identifier |
| Trading Name | `tradingName` | `TradingName` | Text | ❌ | Optional |
| Registered Office Address | `registeredAddress` | `RegisteredOffice` | Note | ✅ | Multi-line text |
| Head Office Address | `headOfficeAddress` | `HeadOffice` | Note | ❌ | Multi-line text |
| Company Registration Number | `registrationNumber` | `CompanyRegNo` | Text | ✅ | Required |
| VAT Number | `vatNumber` | `VATNumber` | Text | ❌ | Optional |
| Parent/Holding Company | `parentCompany` | `ParentCompany` | Text | ❌ | Optional |
| Years Trading | `yearsTrading` | `YearsTrading` | Number | ❌ | Min: 0 |

### Primary Contact Section
| React Form Field | React Field Name | SharePoint Internal Name | SharePoint Type | Required | Notes |
|---|---|---|---|---|---|
| Full Name | `fullName` | `PrimaryContactName` | Text | ✅ | Primary contact |
| Job Title | `jobTitle` | `PrimaryContactTitle` | Text | ❌ | Optional |
| Phone Number | `phone` | `PrimaryContactPhone` | Text | ✅ | Required |
| Email Address | `email` | `PrimaryContactEmail` | Text | ✅ | Primary email |

## Page 2: Services, Roles & Experience

### Services & Experience Section
| React Form Field | React Field Name | SharePoint Internal Name | SharePoint Type | Required | Notes |
|---|---|---|---|---|---|
| Services Provided | `servicesProvided` | `Services` | MultiChoice | ❌ | Array → `;` separated |
| Specializations | `specializations` | `Specialisations` | Note | ❌ | Multi-line text |
| Software Tools Used | `softwareTools` | `SoftwareUsed` | Note | ❌ | Multi-line text |
| Average Projects Per Month | `averageProjectsPerMonth` | `ProjectsPerMonth` | Number | ❌ | Min: 0 |

**Services Choices:**
```javascript
["EPC", "Design", "O&M", "Roof Solar", "Ground Solar", "Carports", 
 "Battery Storage", "CHP", "HV/LV Electrical", "Civils", "Structural", "Other"]
```

### Roles & Capabilities Section
| React Form Field | React Field Name | SharePoint Internal Name | SharePoint Type | Required | Notes |
|---|---|---|---|---|---|
| Acts as Principal Contractor | `principalContractor` | `ActsAsPrincipalContractor` | Boolean | ❌ | Triggers conditional |
| PC Scale Last Year | `pcScaleLastYear` | `PrincipalContractor_LastYearScale` | Note | 🔄 | If PC = true |
| Acts as Principal Designer | `principalDesigner` | `ActsAsPrincipalDesigner` | Boolean | ❌ | Triggers conditional |
| PD Scale Last Year | `pdScaleLastYear` | `PrincipalDesigner_LastYearScale` | Note | 🔄 | If PD = true |
| Internal Staff % | `internalStaffPercentage` | `LabourMix_InternalPct` | Number | ❌ | 0-100, must total 100% with subcontract |
| Subcontract Labour % | `subcontractPercentage` | `LabourMix_SubcontractPct` | Number | ❌ | 0-100, must total 100% with internal |

## Page 3: Certifications & Insurance

### Certifications Section
| React Form Field | React Field Name | SharePoint Internal Name | SharePoint Type | Required | Notes |
|---|---|---|---|---|---|
| ISO Certifications | `isoCertifications` | `ISOStandards` | MultiChoice | ❌ | Array → `;` separated |
| Construction Schemes | `constructionSchemes` | `ConstructionSchemes` | MultiChoice | ❌ | Array → `;` separated |
| NICEIC CPS Contractor | `niceicContractor` | `NICEIC_CPS` | Boolean | ❌ | Yes/No |
| MCS Approved Contractor | `mcsApproved` | `MCS_Approved` | Boolean | ❌ | Yes/No |

**ISO Choices:**
```javascript
["ISO 9001", "ISO 14001", "ISO 27001", "ISO 45001"]
```

**Construction Scheme Choices:**
```javascript
["ConstructionLine", "CHAS", "SMAS", "SafeContractor", "Other"]
```

### Insurance Section
| React Form Field | React Field Name | SharePoint Internal Name | SharePoint Type | Required | Notes |
|---|---|---|---|---|---|
| Public & Product Liability Present | `publicLiabilityInsurance` | `PublicProductLiability_Present` | Boolean | ❌ | Triggers conditional |
| PPL Indemnity in Principle | `pplIndemnityClause` | `PublicProductLiability_IndemnityInPrinciple` | Boolean | 🔄 | If PPL = true |
| Employers' Liability Present | `employersLiabilityInsurance` | `EmployersLiability_Present` | Boolean | ❌ | Triggers conditional |
| Professional Indemnity Present | `professionalIndemnityInsurance` | `ProfIndemnity_Present` | Boolean | ❌ | Triggers conditional |
| PPL Expiry Date | `pplExpiryDate` | `PublicProductLiability_Expiry` | DateTime | 🔄 | If PPL = true |
| EL Expiry Date | `elExpiryDate` | `EmployersLiability_Expiry` | DateTime | 🔄 | If EL = true |
| PI Expiry Date | `piExpiryDate` | `ProfIndemnity_Expiry` | DateTime | 🔄 | If PI = true |

## Page 4: Health, Safety, Quality & Policies

### Health & Safety Section
| React Form Field | React Field Name | SharePoint Internal Name | SharePoint Type | Required | Notes |
|---|---|---|---|---|---|
| HSE Notices Last 5 Years | `hseNotices` | `HSE_ImprovementOrProhibition_Last5Y` | Text | ❌ | Yes/No/Details |
| RIDDOR Incidents Count | `riddorCount` | `RIDDOR_Incidents_Last3Y_Count` | Number | ❌ | Min: 0 |
| RIDDOR Details | `riddorDetails` | `RIDDOR_Incidents_Last3Y_Details` | Note | 🔄 | If count > 0 |
| H&S/CDM Management Evidence | `hsCdmEvidence` | `HSE_CDM_Management_Evidence` | Note | ❌ | Multi-line notes |
| Named Principal Designer | `namedPrincipalDesigner` | `Named_PrincipalDesigner` | Text | ❌ | Name |
| PD Qualifications | `pdQualifications` | `PD_Qualifications` | Note | ❌ | Multi-line notes |
| Training Records | `trainingRecords` | `TrainingRecords_Summary` | Note | ❌ | Multi-line notes |
| Near-Miss Procedure | `nearMissProcedure` | `NearMiss_Procedure` | Text | ❌ | Yes/No/Details |
| Quality CI Evidence | `qualityEvidence` | `Quality_Procedure_Evidence` | Note | ❌ | Multi-line notes |

### Policies Section
| React Form Field | React Field Name | SharePoint Internal Name | SharePoint Type | Required | Notes |
|---|---|---|---|---|---|
| H&S Policy Date | `hsPolicyDate` | `Policy_HS_DateSigned` | DateTime | ❌ | Must be < 12 months |
| Environmental Policy Date | `envPolicyDate` | `Policy_Env_DateSigned` | DateTime | ❌ | Must be < 12 months |
| Modern Slavery Policy Date | `msPolicyDate` | `Policy_MS_DateSigned` | DateTime | ❌ | Must be < 12 months |
| Misuse of Substances Date | `mosPolicyDate` | `Policy_MOS_DateSigned` | DateTime | ❌ | Must be < 12 months |
| Right-to-Work Method | `rightToWorkMethod` | `RightToWork_Monitoring_Method` | Note | ❌ | Multi-line text |

### Data Protection & IT Section
| React Form Field | React Field Name | SharePoint Internal Name | SharePoint Type | Required | Notes |
|---|---|---|---|---|---|
| GDPR Policy Date | `gdprPolicyDate` | `GDPRPolicy_DateSigned` | DateTime | ❌ | Must be < 12 months |
| Cyber Incident Last 3 Years | `cyberIncident` | `CyberIncident_Last3Y` | Text | ❌ | Yes/No/Details |

## Page 5: Delivery Capability & References

### Delivery Capability Section
| React Form Field | React Field Name | SharePoint Internal Name | SharePoint Type | Required | Notes |
|---|---|---|---|---|---|
| Resourcing Approach | `resourcingApproach` | `Resources_PerProject` | Note | ❌ | Multi-line text |

### Project References Section
| React Form Field | React Field Name | SharePoint Internal Name | SharePoint Type | Required | Notes |
|---|---|---|---|---|---|
| Nationwide Coverage | `nationwideCoverage` | `Coverage_Nationwide` | Boolean | ❌ | Triggers conditional |
| Regions Covered | `regionsCovered` | `Coverage_Regions` | MultiChoice | 🔄 | If nationwide = false |
| Client Reference | `clientReference` | `Client_Reference` | Note | ❌ | Multi-line notes |

**Region Choices:**
```javascript
["North East", "North West", "Yorkshire & Humber", "East Midlands", "West Midlands", 
 "East of England", "London", "South East", "South West", "Wales", "Scotland", "Northern Ireland"]
```

## Page 6: Legal, Agreement & Submission

### Legal & Compliance Section
| React Form Field | React Field Name | SharePoint Internal Name | SharePoint Type | Required | Notes |
|---|---|---|---|---|---|
| Pending Prosecutions | `pendingProsecutions` | `PendingProsecutions_Details` | Note | ❌ | Yes/No/Details |
| Contracts Reviewed | `contractsReviewed` | `Contracts_ReviewedBySignatory` | Boolean | ❌ | Yes/No |
| Legal Clarifications | `legalClarifications` | `Legal_Clarifications` | Note | ❌ | Multi-line text |

### Agreement Section
| React Form Field | React Field Name | SharePoint Internal Name | SharePoint Type | Required | Notes |
|---|---|---|---|---|---|
| Received Contract Pack | `receivedContractPack` | `Received_ContractOverviewPack` | Boolean | ✅ | Required |
| Willing to Work Under Terms | `agreeToTerms` | `Willing_To_WorkToSaberTerms` | Boolean | ✅ | Required |
| Agree to Codes | `agreeToCodes` | `AgreeToCodes` | Boolean | ✅ | Required |
| Data Processing Consent | `dataProcessingConsent` | `DataProcessingConsent` | Boolean | ✅ | Required |
| Marketing Consent | `marketingConsent` | `MarketingConsent` | Boolean | ❌ | Optional |

### Submission Section
| React Form Field | React Field Name | SharePoint Internal Name | SharePoint Type | Required | Notes |
|---|---|---|---|---|---|
| Additional Information | `additionalInformation` | `AdditionalInfo` | Note | ❌ | Multi-line text |

## System Fields (Auto-Generated)

| System Field | SharePoint Internal Name | SharePoint Type | Source | Notes |
|---|---|---|---|---|
| Submission Status | `SubmissionStatus` | Choice | Auto | Draft/Submitted/Under Review/Approved/Rejected |
| Reviewer | `Reviewer` | User | Manual | Assigned reviewer |
| Review Notes | `ReviewNotes` | Note | Manual | Review comments |

## File Upload Mapping

Files are stored in the **"EPC Onboarding Evidence"** document library with these metadata fields:

| File Category | React Field Name | Evidence Section | Notes |
|---|---|---|---|
| Supporting Certificates | `supportingCertificates` | "Certifications" | Multiple files allowed |
| PPL Policy | `pplPolicy` | "Insurance" | Single PDF |
| EL Policy | `elPolicy` | "Insurance" | Single PDF |
| PI Policy | `piPolicy` | "Insurance" | Single PDF |
| H&S Policy | `hsPolicyFile` | "Policies" | Single PDF |
| Environmental Policy | `envPolicyFile` | "Policies" | Single PDF |
| Modern Slavery Policy | `msPolicyFile` | "Policies" | Single PDF |
| Misuse of Substances Policy | `mosPolicyFile` | "Policies" | Single PDF |
| GDPR Policy | `gdprPolicyFile` | "Data Protection" | Single PDF |
| Capability Statement | `capabilityStatement` | "Delivery" | Single PDF/DOCX |
| Works Methodology | `worksMethodology` | "Delivery" | Single PDF/DOCX |
| Team CVs | `teamCvs` | "Delivery" | Multiple PDF/DOCX |
| Subcontractors List | `subcontractorsList` | "Delivery" | Single PDF/DOCX |
| Client Reference/Case Study | `clientReferenceFile` | "References" | Single PDF/DOCX/PPT |

## Data Transformation Rules

### Multi-Select Fields
```javascript
// React: ["ISO 9001", "ISO 14001"]
// SharePoint: "ISO 9001;ISO 14001"
const transformMultiSelect = (array) => array?.join(';') || ''
```

### Boolean Fields
```javascript
// React: true/false
// SharePoint: true/false (direct mapping)
```

### Date Fields
```javascript
// React: "2024-12-31"
// SharePoint: new Date("2024-12-31").toISOString()
```

### Conditional Fields
```javascript
// Only include if condition is met
if (payload.principalContractor) {
  sharePointData.PrincipalContractor_LastYearScale = payload.pcScaleLastYear
}
```

### File References
```javascript
// Store file URLs after upload to Evidence library
sharePointData.SupportingCertificatesUrl = fileUrls.supportingCertificates
```

## Validation Rules Summary

1. **Required Fields**: CompanyName, PrimaryContactEmail, Agreement fields
2. **Conditional Required**: Scale fields if Principal roles = true
3. **Percentage Validation**: Internal + Subcontract must = 100%
4. **Date Validation**: Policy dates must be within 12 months
5. **File Validation**: Required files based on Yes/No responses
6. **Business Logic**: Various conditional field requirements

## Backward Compatibility

### Legacy Field Mapping
| Legacy Field | New SharePoint Field | Transformation |
|---|---|---|
| `isoAccreditations` | `ISOStandards` | Direct mapping |
| `coverageRegion` | `Coverage_Regions` | String → Array |

## Implementation Notes

- Use the `EpcItemId` in the Evidence library to link files to list items
- Set `SubmissionStatus` to "Submitted" after successful form submission
- Power Automate will validate dates and move to "Under Review" or "Approved"
- All file uploads should include the `EvidenceSection` metadata for organization
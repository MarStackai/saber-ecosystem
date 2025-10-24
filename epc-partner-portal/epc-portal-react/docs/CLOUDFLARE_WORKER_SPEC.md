# Cloudflare Worker Extension Specification

## Current Working Endpoint
**URL**: `https://epc-api-worker.robjamescarroll.workers.dev/submit-epc-application`
**Method**: POST
**Status**: ✅ Working - Successfully tested with React integration

## Current Payload Structure (Working)
```json
{
  "companyName": "Test EPC Company Ltd",
  "tradingName": "EPC Test Trading", 
  "registrationNumber": "12345678",
  "vatNumber": "GB123456789",
  "registeredAddress": "123 Test Street, Test City, TC1 2AB",
  "fullName": "John Smith",
  "email": "john.smith@testepc.co.uk", 
  "phone": "+44 123 456 7890",
  "certifications": "",
  "experience": "",
  "serviceAreas": ""
}
```

## Current Response Format (Working)
```json
{
  "success": true,
  "message": "Application submitted successfully", 
  "referenceNumber": "EPC-1757531850900"
}
```

## Extended Payload Structure Required

### Page 1: Company Information & Contacts
```json
{
  "companyInfo": {
    "companyName": "string (required)",
    "tradingName": "string (optional)",
    "registeredAddress": "string (required)",
    "headOfficeAddress": "string (optional)", 
    "registrationNumber": "string (required)",
    "vatNumber": "string (optional)",
    "parentCompany": "string (optional)",
    "yearsTrading": "number (optional)"
  },
  "primaryContact": {
    "fullName": "string (required)",
    "jobTitle": "string (optional)",
    "phone": "string (required)",
    "email": "string (required)"
  }
}
```

### Page 2: Services, Roles & Experience  
```json
{
  "servicesExperience": {
    "servicesProvided": ["string array (multi-select)"],
    "specializations": "string (optional)",
    "softwareTools": "string (optional)", 
    "averageProjectsPerMonth": "number (optional)"
  },
  "rolesCapabilities": {
    "principalContractor": "boolean",
    "pcScaleLastYear": "string (conditional - if principalContractor = true)",
    "principalDesigner": "boolean", 
    "pdScaleLastYear": "string (conditional - if principalDesigner = true)",
    "internalStaffPercentage": "number (0-100)",
    "subcontractLabourPercentage": "number (0-100)"
  }
}
```

### Page 3: Certifications & Insurance
```json
{
  "certifications": {
    "isoCertifications": ["string array (multi-select)"],
    "constructionSchemes": ["string array (multi-select)"], 
    "niceicContractor": "boolean",
    "mcsApproved": "boolean",
    "supportingCertificates": "file upload array"
  },
  "insurance": {
    "publicLiabilityInsurance": "boolean",
    "pplPolicy": "file upload (conditional)",
    "pplIndemnityClause": "boolean (conditional)",
    "employersLiabilityInsurance": "boolean", 
    "elPolicy": "file upload (conditional)",
    "professionalIndemnityInsurance": "boolean",
    "piPolicy": "file upload (conditional)",
    "pplExpiryDate": "date (conditional)",
    "elExpiryDate": "date (conditional)", 
    "piExpiryDate": "date (conditional)"
  }
}
```

### Page 4: Health, Safety, Quality & Policies
```json
{
  "healthSafety": {
    "hseNoticesLast5Years": "boolean",
    "hseNoticeDetails": "string (conditional)",
    "riddorIncidentsLast3Years": "number",
    "riddorIncidentDetails": "string (conditional)", 
    "hsCdmEvidence": "file upload",
    "namedPrincipalDesigner": "string",
    "pdQualifications": "file upload",
    "trainingRecords": "file upload",
    "accidentReportingProcedure": "boolean",
    "accidentProcedureDetails": "string (conditional)",
    "qualityAssuranceEvidence": "file upload"
  },
  "policies": {
    "healthSafetyPolicy": "file upload", 
    "environmentalPolicy": "file upload",
    "modernSlaveryPolicy": "file upload",
    "substanceMisusePolicy": "file upload",
    "rightToWorkMethod": "string",
    "trainingCertificationsList": "file upload"
  },
  "dataProtectionIT": {
    "gdprPolicy": "file upload",
    "cyberIncidentLast3Years": "boolean",
    "cyberIncidentDetails": "string (conditional)"
  }
}
```

### Page 5: Delivery Capability & References
```json
{
  "deliveryCapability": {
    "capabilityStatement": "file upload",
    "worksMethodology": "file upload", 
    "resourcingApproach": "string",
    "teamCvs": "file upload array",
    "subcontractorsList": "file upload"
  },
  "projectReferences": {
    "nationwideCoverage": "boolean",
    "regionsCovered": ["string array (conditional - if nationwideCoverage = false)"],
    "clientReferenceStudy": "file upload"
  }
}
```

### Page 6: Legal, Agreement & Submission
```json
{
  "legalCompliance": {
    "pendingProsecutions": "boolean", 
    "prosecutionDetails": "string (conditional)",
    "epcContractsReviewed": "boolean",
    "legalClarifications": "string (optional)"
  },
  "agreement": {
    "receivedContractPack": "boolean",
    "willingToWorkUnderTerms": "boolean",
    "agreeToCodes": "boolean", 
    "consentDataProcessing": "boolean",
    "consentMarketing": "boolean"
  },
  "submission": {
    "additionalInformation": "string (optional)",
    "submissionTimestamp": "datetime (auto-generated)",
    "evidenceChecklistComplete": "boolean (auto-calculated)"
  }
}
```

## File Upload Handling Strategy

### Option 1: Direct SharePoint Upload (Recommended)
```javascript
// In Cloudflare Worker
const uploadToSharePoint = async (fileData, fileName, referenceNumber) => {
  const folderPath = `/EPC-${referenceNumber}/${getFileCategory(fileName)}/`
  // Upload to SharePoint document library
  // Return SharePoint file URL
}
```

### Option 2: Temporary Storage + Async Processing
```javascript
// Store files temporarily, process async
const processFiles = async (files, referenceNumber) => {
  for (const file of files) {
    await uploadFileToSharePoint(file, referenceNumber)
    await updateSharePointListWithFileLink(referenceNumber, file.type, file.url)
  }
}
```

## Validation Logic Required

### Field Validation
```javascript
const validateExtendedForm = (payload) => {
  const errors = []
  
  // Required field validation
  if (!payload.companyInfo.companyName) errors.push("Company name is required")
  if (!payload.primaryContact.email) errors.push("Email is required")
  
  // Conditional field validation  
  if (payload.rolesCapabilities.principalContractor && !payload.rolesCapabilities.pcScaleLastYear) {
    errors.push("Principal contractor scale is required")
  }
  
  // Percentage validation
  const totalPercentage = payload.rolesCapabilities.internalStaffPercentage + 
                         payload.rolesCapabilities.subcontractLabourPercentage
  if (totalPercentage !== 100) {
    errors.push("Internal staff and subcontract percentages must total 100%")
  }
  
  // File upload validation
  if (payload.insurance.publicLiabilityInsurance && !payload.insurance.pplPolicy) {
    errors.push("Public liability policy document is required")
  }
  
  return errors
}
```

## SharePoint Mapping Functions

### Column Mapping
```javascript
const mapToSharePointColumns = (payload) => {
  return {
    // Basic fields (existing)
    CompanyName: payload.companyInfo.companyName,
    Email: payload.primaryContact.email,
    
    // Extended fields (new)
    TradingName: payload.companyInfo.tradingName,
    HeadOfficeAddress: payload.companyInfo.headOfficeAddress,
    ParentCompany: payload.companyInfo.parentCompany,
    YearsTrading: payload.companyInfo.yearsTrading,
    
    // Multi-select fields  
    ServicesProvided: payload.servicesExperience.servicesProvided?.join(';'),
    ISOCertifications: payload.certifications.isoCertifications?.join(';'),
    ConstructionSchemes: payload.certifications.constructionSchemes?.join(';'),
    
    // Boolean fields
    PrincipalContractor: payload.rolesCapabilities.principalContractor,
    NICEICContractor: payload.certifications.niceicContractor,
    PublicLiabilityInsurance: payload.insurance.publicLiabilityInsurance,
    
    // Conditional fields
    PCScaleLastYear: payload.rolesCapabilities.principalContractor ? 
                     payload.rolesCapabilities.pcScaleLastYear : null,
                     
    // File references (links to document library)
    SupportingCertificatesUrl: payload.fileUrls?.supportingCertificates,
    CapabilityStatementUrl: payload.fileUrls?.capabilityStatement,
    
    // Auto-generated
    ReferenceNumber: generateReferenceNumber(),
    SubmissionDate: new Date().toISOString()
  }
}
```

## Error Handling Enhancement
```javascript
const handleExtendedSubmission = async (request) => {
  try {
    const payload = await request.json()
    
    // Validate payload structure
    const validationErrors = validateExtendedForm(payload)
    if (validationErrors.length > 0) {
      return new Response(JSON.stringify({
        success: false,
        errors: validationErrors
      }), { 
        status: 400,
        headers: { 'Content-Type': 'application/json' }
      })
    }
    
    // Process file uploads
    const fileUrls = await processFileUploads(payload.files)
    
    // Map to SharePoint format
    const sharePointData = mapToSharePointColumns({...payload, fileUrls})
    
    // Submit to SharePoint
    const result = await submitToSharePoint(sharePointData)
    
    return new Response(JSON.stringify({
      success: true,
      message: "Application submitted successfully",
      referenceNumber: result.referenceNumber,
      submissionId: result.id
    }), {
      status: 200, 
      headers: { 'Content-Type': 'application/json' }
    })
    
  } catch (error) {
    console.error('Extended form submission error:', error)
    return new Response(JSON.stringify({
      success: false,
      message: "Internal server error processing application"
    }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    })
  }
}
```

## Backward Compatibility
The worker should maintain compatibility with the current simple form structure while supporting the extended format:

```javascript
const determineFormType = (payload) => {
  // Check if it's the extended format
  if (payload.companyInfo && payload.primaryContact) {
    return 'extended'
  }
  // Legacy simple format
  return 'simple'
}

const processSubmission = async (payload) => {
  const formType = determineFormType(payload)
  
  if (formType === 'extended') {
    return await handleExtendedSubmission(payload)
  } else {
    return await handleSimpleSubmission(payload) // existing logic
  }
}
```

## Testing Strategy
1. **Unit tests** for validation functions
2. **Integration tests** with SharePoint  
3. **File upload tests** with various file types
4. **Conditional logic tests** for all scenarios
5. **Performance tests** with large file uploads
6. **Backward compatibility tests** with existing simple form
# Updated Cloudflare Worker for Extended EPC Form

## Current Status
✅ Basic form integration working with reference: `EPC-1757531850900`
🔄 Ready to extend for 6-page form with new SharePoint schema

## Updated Field Mapping Functions

### 1. Extended Payload Structure Handling

```javascript
const determineFormType = (payload) => {
  // Extended format detection
  if (payload.companyInfo && payload.primaryContact) {
    return 'extended'
  }
  // Legacy simple format
  return 'simple'
}

const handleExtendedSubmission = async (payload) => {
  try {
    // Validate extended form
    const validationErrors = validateExtendedForm(payload)
    if (validationErrors.length > 0) {
      return errorResponse(400, validationErrors)
    }
    
    // Process file uploads first
    const fileUrls = await processFileUploads(payload.files)
    
    // Map to SharePoint format
    const sharePointData = mapExtendedToSharePoint({...payload, fileUrls})
    
    // Submit to SharePoint
    const result = await submitToSharePoint(sharePointData)
    
    return successResponse(result)
    
  } catch (error) {
    console.error('Extended form submission error:', error)
    return errorResponse(500, 'Internal server error processing application')
  }
}
```

### 2. Extended Field Mapping to SharePoint

```javascript
const mapExtendedToSharePoint = (payload) => {
  const mapped = {
    // System fields
    ReferenceNumber: generateReferenceNumber(),
    SubmissionDate: new Date().toISOString(),
    SubmissionStatus: 'Submitted',
    
    // Page 1: Company Information
    CompanyName: payload.companyInfo?.companyName || '',
    TradingName: payload.companyInfo?.tradingName || '',
    RegisteredOffice: payload.companyInfo?.registeredAddress || '',
    HeadOffice: payload.companyInfo?.headOfficeAddress || '',
    CompanyRegNo: payload.companyInfo?.registrationNumber || '',
    VATNumber: payload.companyInfo?.vatNumber || '',
    ParentCompany: payload.companyInfo?.parentCompany || '',
    YearsTrading: payload.companyInfo?.yearsTrading || null,
    
    // Primary Contact
    PrimaryContactName: payload.primaryContact?.fullName || '',
    PrimaryContactTitle: payload.primaryContact?.jobTitle || '',
    PrimaryContactPhone: payload.primaryContact?.phone || '',
    PrimaryContactEmail: payload.primaryContact?.email || '',
    
    // Page 2: Services & Experience
    Services: transformMultiSelect(payload.servicesExperience?.servicesProvided),
    Specialisations: payload.servicesExperience?.specializations || '',
    SoftwareUsed: payload.servicesExperience?.softwareTools || '',
    ProjectsPerMonth: payload.servicesExperience?.averageProjectsPerMonth || null,
    
    // Roles & Capabilities
    ActsAsPrincipalContractor: payload.rolesCapabilities?.principalContractor || false,
    ActsAsPrincipalDesigner: payload.rolesCapabilities?.principalDesigner || false,
    LabourMix_InternalPct: payload.rolesCapabilities?.internalStaffPercentage || null,
    LabourMix_SubcontractPct: payload.rolesCapabilities?.subcontractPercentage || null,
    
    // Page 3: Certifications & Insurance
    ISOStandards: transformMultiSelect(payload.certifications?.isoCertifications),
    ConstructionSchemes: transformMultiSelect(payload.certifications?.constructionSchemes),
    NICEIC_CPS: payload.certifications?.niceicContractor || false,
    MCS_Approved: payload.certifications?.mcsApproved || false,
    
    PublicProductLiability_Present: payload.insurance?.publicLiabilityInsurance || false,
    PublicProductLiability_IndemnityInPrinciple: payload.insurance?.pplIndemnityClause || false,
    EmployersLiability_Present: payload.insurance?.employersLiabilityInsurance || false,
    ProfIndemnity_Present: payload.insurance?.professionalIndemnityInsurance || false,
    
    // Page 4: Health, Safety & Policies
    HSE_ImprovementOrProhibition_Last5Y: payload.healthSafety?.hseNotices || '',
    RIDDOR_Incidents_Last3Y_Count: payload.healthSafety?.riddorCount || 0,
    HSE_CDM_Management_Evidence: payload.healthSafety?.hsCdmEvidence || '',
    Named_PrincipalDesigner: payload.healthSafety?.namedPrincipalDesigner || '',
    TrainingRecords_Summary: payload.healthSafety?.trainingRecords || '',
    NearMiss_Procedure: payload.healthSafety?.nearMissProcedure || '',
    Quality_Procedure_Evidence: payload.healthSafety?.qualityEvidence || '',
    
    // Policy dates
    Policy_HS_DateSigned: transformDate(payload.policies?.hsPolicyDate),
    Policy_Env_DateSigned: transformDate(payload.policies?.envPolicyDate),
    Policy_MS_DateSigned: transformDate(payload.policies?.msPolicyDate),
    Policy_MOS_DateSigned: transformDate(payload.policies?.mosPolicyDate),
    GDPRPolicy_DateSigned: transformDate(payload.dataProtectionIT?.gdprPolicyDate),
    
    RightToWork_Monitoring_Method: payload.policies?.rightToWorkMethod || '',
    CyberIncident_Last3Y: payload.dataProtectionIT?.cyberIncident || '',
    
    // Page 5: Delivery Capability
    Resources_PerProject: payload.deliveryCapability?.resourcingApproach || '',
    Coverage_Nationwide: payload.projectReferences?.nationwideCoverage || false,
    Coverage_Regions: transformMultiSelect(payload.projectReferences?.regionsCovered),
    Client_Reference: payload.projectReferences?.clientReference || '',
    
    // Page 6: Legal & Agreement
    PendingProsecutions_Details: payload.legalCompliance?.pendingProsecutions || '',
    Contracts_ReviewedBySignatory: payload.legalCompliance?.contractsReviewed || false,
    Legal_Clarifications: payload.legalCompliance?.legalClarifications || '',
    
    Received_ContractOverviewPack: payload.agreement?.receivedContractPack || false,
    Willing_To_WorkToSaberTerms: payload.agreement?.agreeToTerms || false,
    AgreeToCodes: payload.agreement?.agreeToCodes || false,
    DataProcessingConsent: payload.agreement?.dataProcessingConsent || false,
    MarketingConsent: payload.agreement?.marketingConsent || false,
    
    AdditionalInfo: payload.submission?.additionalInformation || ''
  }
  
  // Add conditional fields
  addConditionalFields(mapped, payload)
  
  // Add file URLs
  addFileReferences(mapped, payload.fileUrls)
  
  return mapped
}
```

### 3. Conditional Field Logic

```javascript
const addConditionalFields = (mapped, payload) => {
  // Principal Contractor scale
  if (payload.rolesCapabilities?.principalContractor) {
    mapped.PrincipalContractor_LastYearScale = payload.rolesCapabilities?.pcScaleLastYear || ''
  }
  
  // Principal Designer scale  
  if (payload.rolesCapabilities?.principalDesigner) {
    mapped.PrincipalDesigner_LastYearScale = payload.rolesCapabilities?.pdScaleLastYear || ''
  }
  
  // Insurance expiry dates
  if (payload.insurance?.publicLiabilityInsurance) {
    mapped.PublicProductLiability_Expiry = transformDate(payload.insurance?.pplExpiryDate)
  }
  
  if (payload.insurance?.employersLiabilityInsurance) {
    mapped.EmployersLiability_Expiry = transformDate(payload.insurance?.elExpiryDate)
  }
  
  if (payload.insurance?.professionalIndemnityInsurance) {
    mapped.ProfIndemnity_Expiry = transformDate(payload.insurance?.piExpiryDate)
  }
  
  // RIDDOR details
  if (payload.healthSafety?.riddorCount > 0) {
    mapped.RIDDOR_Incidents_Last3Y_Details = payload.healthSafety?.riddorDetails || ''
  }
  
  // PD Qualifications
  if (payload.healthSafety?.namedPrincipalDesigner) {
    mapped.PD_Qualifications = payload.healthSafety?.pdQualifications || ''
  }
  
  // Regional coverage (only if not nationwide)
  if (!payload.projectReferences?.nationwideCoverage) {
    mapped.Coverage_Regions = transformMultiSelect(payload.projectReferences?.regionsCovered)
  }
}
```

### 4. Data Transformation Utilities

```javascript
const transformMultiSelect = (array) => {
  if (!array || !Array.isArray(array)) return ''
  return array.join(';')
}

const transformDate = (dateString) => {
  if (!dateString) return null
  try {
    return new Date(dateString).toISOString()
  } catch (error) {
    console.warn('Invalid date format:', dateString)
    return null
  }
}

const addFileReferences = (mapped, fileUrls) => {
  if (!fileUrls) return
  
  // Map file URLs to SharePoint fields
  const fileMapping = {
    supportingCertificates: 'SupportingCertificatesUrl',
    pplPolicy: 'PPL_PolicyUrl',
    elPolicy: 'EL_PolicyUrl',
    piPolicy: 'PI_PolicyUrl',
    hsPolicyFile: 'HS_PolicyUrl',
    envPolicyFile: 'Env_PolicyUrl',
    msPolicyFile: 'MS_PolicyUrl',
    mosPolicyFile: 'MOS_PolicyUrl',
    gdprPolicyFile: 'GDPR_PolicyUrl',
    capabilityStatement: 'CapabilityStatementUrl',
    worksMethodology: 'WorksMethodologyUrl',
    teamCvs: 'TeamCVsUrl',
    subcontractorsList: 'SubcontractorsListUrl',
    clientReferenceFile: 'ClientReferenceUrl'
  }
  
  Object.entries(fileMapping).forEach(([key, field]) => {
    if (fileUrls[key]) {
      mapped[field] = fileUrls[key]
    }
  })
}
```

### 5. Extended Validation

```javascript
const validateExtendedForm = (payload) => {
  const errors = []
  
  // Required fields validation
  if (!payload.companyInfo?.companyName) {
    errors.push('Company name is required')
  }
  
  if (!payload.companyInfo?.registeredAddress) {
    errors.push('Registered office address is required')
  }
  
  if (!payload.companyInfo?.registrationNumber) {
    errors.push('Company registration number is required')
  }
  
  if (!payload.primaryContact?.fullName) {
    errors.push('Primary contact name is required')
  }
  
  if (!payload.primaryContact?.phone) {
    errors.push('Primary contact phone is required')
  }
  
  if (!payload.primaryContact?.email) {
    errors.push('Primary contact email is required')
  }
  
  // Conditional validation
  if (payload.rolesCapabilities?.principalContractor && !payload.rolesCapabilities?.pcScaleLastYear) {
    errors.push('Principal contractor scale is required when acting as principal contractor')
  }
  
  if (payload.rolesCapabilities?.principalDesigner && !payload.rolesCapabilities?.pdScaleLastYear) {
    errors.push('Principal designer scale is required when acting as principal designer')
  }
  
  // Percentage validation
  const internalPct = payload.rolesCapabilities?.internalStaffPercentage || 0
  const subcontractPct = payload.rolesCapabilities?.subcontractPercentage || 0
  
  if (internalPct + subcontractPct !== 0 && internalPct + subcontractPct !== 100) {
    errors.push('Internal staff and subcontract percentages must total 100%')
  }
  
  // Required agreement fields
  const agreements = payload.agreement || {}
  const requiredAgreements = [
    { field: 'receivedContractPack', name: 'Contract pack acknowledgment' },
    { field: 'agreeToTerms', name: 'Agreement to Saber terms' },
    { field: 'agreeToCodes', name: 'Agreement to codes of practice' },
    { field: 'dataProcessingConsent', name: 'Data processing consent' }
  ]
  
  requiredAgreements.forEach(({ field, name }) => {
    if (!agreements[field]) {
      errors.push(`${name} is required`)
    }
  })
  
  // File upload validation based on form responses
  validateRequiredFiles(payload, errors)
  
  return errors
}

const validateRequiredFiles = (payload, errors) => {
  const insurance = payload.insurance || {}
  const files = payload.files || {}
  
  // Insurance policy files required if insurance present
  if (insurance.publicLiabilityInsurance && !files.pplPolicy) {
    errors.push('Public liability policy document is required')
  }
  
  if (insurance.employersLiabilityInsurance && !files.elPolicy) {
    errors.push('Employers liability policy document is required')
  }
  
  if (insurance.professionalIndemnityInsurance && !files.piPolicy) {
    errors.push('Professional indemnity policy document is required')
  }
  
  // Policy files validation
  const policies = payload.policies || {}
  if (policies.hsPolicyDate && !files.hsPolicyFile) {
    errors.push('Health & safety policy document is required')
  }
  
  if (policies.envPolicyDate && !files.envPolicyFile) {
    errors.push('Environmental policy document is required')
  }
  
  if (policies.msPolicyDate && !files.msPolicyFile) {
    errors.push('Modern slavery policy document is required')
  }
  
  if (policies.mosPolicyDate && !files.mosPolicyFile) {
    errors.push('Misuse of substances policy document is required')
  }
}
```

### 6. File Upload Processing

```javascript
const processFileUploads = async (files) => {
  if (!files || Object.keys(files).length === 0) {
    return {}
  }
  
  const fileUrls = {}
  const referenceNumber = generateReferenceNumber()
  
  // Process each file category
  for (const [category, fileData] of Object.entries(files)) {
    try {
      if (Array.isArray(fileData)) {
        // Multiple files (e.g., supporting certificates, CVs)
        const urls = []
        for (const file of fileData) {
          const url = await uploadToSharePointLibrary(file, referenceNumber, category)
          urls.push(url)
        }
        fileUrls[category] = urls.join(';')
      } else {
        // Single file
        const url = await uploadToSharePointLibrary(fileData, referenceNumber, category)
        fileUrls[category] = url
      }
    } catch (error) {
      console.error(`Error uploading ${category}:`, error)
      throw new Error(`Failed to upload ${category} files`)
    }
  }
  
  return fileUrls
}

const uploadToSharePointLibrary = async (fileData, referenceNumber, category) => {
  // Implementation depends on chosen upload strategy
  // Could be direct SharePoint upload or temporary storage + async processing
  
  const fileName = `${referenceNumber}_${category}_${fileData.name}`
  const folderPath = `EPC-${referenceNumber}/${getCategoryFolder(category)}/`
  
  // Upload to SharePoint Evidence library
  const uploadResult = await uploadFileToSharePoint(fileData, folderPath, fileName)
  
  // Update evidence metadata
  await updateEvidenceMetadata(uploadResult.id, referenceNumber, category)
  
  return uploadResult.webUrl
}

const getCategoryFolder = (category) => {
  const folderMap = {
    supportingCertificates: 'certificates',
    pplPolicy: 'insurance',
    elPolicy: 'insurance', 
    piPolicy: 'insurance',
    hsPolicyFile: 'policies',
    envPolicyFile: 'policies',
    msPolicyFile: 'policies',
    mosPolicyFile: 'policies',
    gdprPolicyFile: 'policies',
    capabilityStatement: 'capability',
    worksMethodology: 'methodology',
    teamCvs: 'cvs',
    subcontractorsList: 'subcontractors',
    clientReferenceFile: 'references'
  }
  
  return folderMap[category] || 'other'
}
```

### 7. Backward Compatibility

```javascript
const processSubmission = async (request) => {
  const payload = await request.json()
  const formType = determineFormType(payload)
  
  if (formType === 'extended') {
    return await handleExtendedSubmission(payload)
  } else {
    return await handleSimpleSubmission(payload) // existing logic
  }
}

// Updated main handler
export default {
  async fetch(request) {
    if (request.method === 'POST' && request.url.includes('/submit-epc-application')) {
      return await processSubmission(request)
    }
    
    return new Response('EPC Application API', { status: 200 })
  }
}
```

## Implementation Priority

1. ✅ **Validate current simple form still works**
2. 🔄 **Add extended field mapping functions**
3. 🔄 **Implement validation logic**
4. 🔄 **Add file upload processing**
5. 🔄 **Test with extended form payload**
6. 🔄 **Deploy and verify integration**

## Testing Strategy

- Unit tests for field mapping functions
- Integration tests with SharePoint API
- File upload tests with various formats
- Validation tests for all conditional scenarios
- Backward compatibility tests with existing simple form

The extended worker maintains full backward compatibility while supporting the comprehensive 6-page form structure with proper validation, file handling, and SharePoint integration.
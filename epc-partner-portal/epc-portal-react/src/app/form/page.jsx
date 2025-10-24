'use client'

export const dynamic = 'force-dynamic'
// Removed edge runtime to fix query parameter handling on Cloudflare Pages
// export const runtime = 'edge'

import { useState, useEffect } from 'react'
import { CheckCircleIcon, CheckIcon } from '@heroicons/react/24/solid'

export default function FormPage() {
  const [currentStep, setCurrentStep] = useState(1)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [uploadingFiles, setUploadingFiles] = useState({})
  const [formData, setFormData] = useState({
    // Page 1: Company Information
    companyName: '',
    tradingName: '',
    registrationNumber: '',
    companyRegNo: '', // Alternative field name expected by PowerShell
    vatNumber: '',
    registeredAddress: '',
    registeredOffice: '', // Alternative field name
    headOffice: '',
    address: '', // General address field
    parentCompany: '',
    yearsTrading: '',
    
    // Page 2: Contact Information
    contactName: '',
    contactTitle: '',
    email: '',
    phone: '',
    companyWebsite: '',
    companyLogo: '',
    
    // Page 3: Capabilities & Experience
    specializations: '',
    softwareTools: '',
    projectsPerMonth: '',
    teamSize: '',
    yearsExperience: '',
    services: '',
    coverage: '',
    coverageRegion: '',
    coverageRegions: [],
    resourcesPerProject: '',
    clientReference: '',
    
    // Page 4: Roles & Certifications
    principalContractor: false,
    principalDesigner: false,
    principalContractorScale: '',
    principalDesignerScale: '',
    internalStaffPercentage: '',
    subcontractPercentage: '',
    niceicContractor: false,
    mcsApproved: false,
    accreditations: '',
    certificationDetails: '',
    isoStandards: '',
    namedPrincipalDesigner: '',
    principalDesignerQualifications: '',
    trainingRecordsSummary: '',
    
    // Page 5: Insurance & Compliance
    publicLiabilityInsurance: false,
    publicLiabilityExpiry: '',
    publicLiabilityIndemnity: false,
    employersLiabilityInsurance: false,
    employersLiabilityExpiry: '',
    professionalIndemnityInsurance: false,
    professionalIndemnityExpiry: '',
    hseNoticesLast5Years: '',
    pendingProsecutions: '',
    riddorIncidentCount: '',
    riddorIncidentDetails: '',
    cdmManagementEvidence: '',
    nearMissProcedure: '',
    qualityProcedureEvidence: '',
    hseqIncidents: '',
    riddorIncidents: '',
    
    // Page 5b: Policy & Compliance Dates
    healthSafetyPolicyDate: '',
    environmentalPolicyDate: '',
    modernSlaveryPolicyDate: '',
    substanceMisusePolicyDate: '',
    rightToWorkMethod: '',
    gdprPolicyDate: '',
    cyberIncidentLast3Years: '',
    legalClarifications: '',
    
    // Page 6: Agreement & Submission
    agreeToTerms: false,
    agreeToCodes: false,
    dataProcessingConsent: false,
    marketingConsent: false,
    nationwideCoverage: false,
    contractsReviewed: false,
    receivedContractPack: false,
    additionalInformation: '',
    notes: '',
    clarifications: '',
    invitationCode: '',
    submissionDate: '',
    reviewDate: '',
    referenceNumber: '',
    registrationNumberField: '', // Different from registrationNumber
    
    // File uploads
    files: {
      // Page 4 - Certifications
      niceicCertificate: null,
      mcsCertificate: null,
      isoCertificates: null,
      otherCertifications: null,
      
      // Page 5 - Insurance & Compliance  
      publicLiabilityCertificate: null,
      employersLiabilityCertificate: null,
      professionalIndemnityCertificate: null,
      healthSafetyPolicy: null,
      environmentalPolicy: null,
      modernSlaveryPolicy: null,
      gdprPolicy: null,
      riddorReports: null,
      
      // Page 6 - Additional Documents
      companyRegistration: null,
      additionalDocuments: null
    }
  })

  const steps = [
    { id: 1, name: 'Company', description: 'Business Details' },
    { id: 2, name: 'Contact', description: 'Your Information' },
    { id: 3, name: 'Capabilities', description: 'Experience & Services' },
    { id: 4, name: 'Roles', description: 'Certifications' },
    { id: 5, name: 'Compliance', description: 'Insurance & Policies' },
    { id: 6, name: 'Agreement', description: 'Terms & Submission' },
  ]
  const uiSteps = steps.map(s => ({
    ...s,
    displayId: String(s.id).padStart(2, '0'),
    status: s.id < currentStep ? 'complete' : s.id === currentStep ? 'current' : 'upcoming'
  }))

  // Auto-save state
  const [lastSaved, setLastSaved] = useState(null)
  const [saving, setSaving] = useState(false)
  const [draftLoaded, setDraftLoaded] = useState(false)
  const [autoSaveStatus, setAutoSaveStatus] = useState('') // '', 'saving', 'saved', 'error'

  // Auto-save function with status updates
  const saveDraft = async (showStatus = false) => {
    if (!formData.invitationCode || saving) return
    
    setSaving(true)
    if (showStatus) setAutoSaveStatus('saving')
    
    try {
      const response = await fetch('/api/save-draft', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          invitationCode: formData.invitationCode,
          formData,
          currentStep
        })
      })
      
      if (response.ok) {
        const result = await response.json()
        setLastSaved(new Date())
        if (showStatus) {
          setAutoSaveStatus('saved')
          setTimeout(() => setAutoSaveStatus(''), 3000) // Clear after 3 seconds
        }
        console.log('✅ Draft saved automatically')
      } else {
        throw new Error('Save failed')
      }
    } catch (error) {
      console.error('❌ Auto-save failed:', error)
      if (showStatus) {
        setAutoSaveStatus('error')
        setTimeout(() => setAutoSaveStatus(''), 5000) // Clear after 5 seconds
      }
    } finally {
      setSaving(false)
    }
  }

  // Load existing draft
  const loadDraft = async (invitationCode, invitationData = null) => {
    if (!invitationCode || draftLoaded) return
    
    try {
      const response = await fetch(`/api/save-draft?invitationCode=${invitationCode}`)
      const result = await response.json()
      
      if (result.success && result.data) {
        // Merge draft data with existing form data (draft takes priority)
        setFormData(prev => ({
          ...prev,
          ...result.data.formData,
          // Always preserve the invitation code
          invitationCode: invitationCode
        }))
        setCurrentStep(result.data.currentStep)
        setLastSaved(new Date(result.data.lastSaved))
        setDraftLoaded(true)
        console.log('📖 Draft loaded successfully, resuming at step:', result.data.currentStep)
      } else {
        // No draft found - use invitation data if available
        if (invitationData) {
          setFormData(prev => ({
            ...prev,
            invitationCode: invitationCode,
            companyName: invitationData.companyName || '',
            email: invitationData.contactEmail || ''
          }))
          console.log('📋 No draft found, using invitation data:', invitationData.companyName)
        }
        setDraftLoaded(true)
      }
    } catch (error) {
      console.error('❌ Failed to load draft:', error)
      // On error, still use invitation data if available
      if (invitationData) {
        setFormData(prev => ({
          ...prev,
          invitationCode: invitationCode,
          companyName: invitationData.companyName || '',
          email: invitationData.contactEmail || ''
        }))
      }
      setDraftLoaded(true)
    }
  }

  // Draft loading is now handled in the initialization effect above
  // This prevents duplicate loading and timing issues

  // Auto-save when moving between steps
  useEffect(() => {
    if (formData.invitationCode && currentStep > 1) {
      saveDraft()
    }
  }, [currentStep])

  // Debounced auto-save on form data changes (continuous auto-save)
  useEffect(() => {
    if (!formData.invitationCode || !draftLoaded) return
    
    // Debounce auto-save by 3 seconds after user stops typing
    const timeoutId = setTimeout(() => {
      saveDraft() // Silent save without status indicator
    }, 3000)
    
    return () => clearTimeout(timeoutId)
  }, [formData, draftLoaded])

  // Initialize invitation code from URL parameters and fetch company data
  useEffect(() => {
    if (typeof window !== 'undefined') {
      const urlParams = new URLSearchParams(window.location.search)
      const invitationCode = urlParams.get('invitationCode')
      if (invitationCode && !formData.invitationCode) {
        console.log('🔗 Initializing invitation code from URL:', invitationCode)
        
        // Set invitation code immediately
        setFormData(prev => ({
          ...prev,
          invitationCode: invitationCode
        }))
        
        // Fetch company data from invitation and load draft
        fetch('/api/validate-invitation', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ invitationCode })
        })
        .then(res => res.json())
        .then(result => {
          if (result.valid && result.invitation) {
            console.log('📋 Fetched invitation data:', result.invitation.companyName)
            // Load draft with invitation data as fallback
            loadDraft(invitationCode, result.invitation)
          } else {
            // Load draft without invitation data
            loadDraft(invitationCode)
          }
        })
        .catch(err => {
          console.error('Failed to fetch invitation data:', err)
          // Still try to load draft
          loadDraft(invitationCode)
        })
      }
    }
  }, [])

  const handleInputChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    })
  }
  // Toggle a region in the multi-select array
  const toggleCoverageRegion = (region) => {
    setFormData((prev) => {
      const set = new Set(prev.coverageRegions || [])
      if (set.has(region)) set.delete(region)
      else set.add(region)
      return { ...prev, coverageRegions: Array.from(set) }
    })
  }

  const handleFileUpload = async (e, fieldName) => {
    const file = e.target.files[0]
    if (!file) return

    // Validate file type and size
    const allowedTypes = ['application/pdf', 'image/jpeg', 'image/png', 'image/jpg', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']
    const maxSize = 10 * 1024 * 1024 // 10MB

    if (!allowedTypes.includes(file.type)) {
      alert('Please upload only PDF, DOC, DOCX, JPG, or PNG files')
      return
    }

    if (file.size > maxSize) {
      alert('File size must be less than 10MB')
      return
    }

    if (!formData.invitationCode) {
      alert('Invitation code is required for file upload')
      return
    }

    // Set uploading state
    setUploadingFiles(prev => ({ ...prev, [fieldName]: true }))

    try {
      // Upload file to portal storage (R2) via API
      const uploadFormData = new FormData()
      uploadFormData.append('file', file)
      uploadFormData.append('invitationCode', formData.invitationCode)
      uploadFormData.append('fieldName', fieldName)

      console.log(`📁 Uploading ${fieldName} for invitation: ${formData.invitationCode}`)

      const response = await fetch('/api/upload-file', {
        method: 'POST',
        body: uploadFormData
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.message || 'Upload failed')
      }

      const result = await response.json()
      console.log('✅ File uploaded successfully:', result)

      // Store file metadata in form state
      setFormData(prev => ({
        ...prev,
        files: {
          ...prev.files,
          [fieldName]: {
            name: file.name,
            size: file.size,
            type: file.type,
            uploadedAt: result.uploadedAt || new Date().toISOString(),
            storagePath: result.r2Key || result.storagePath,
            fileName: file.name
          }
        }
      }))

      alert(`✅ ${file.name} uploaded successfully (stored securely until submission)`) 

    } catch (error) {
      console.error('File upload error:', error)
      alert(`❌ Failed to upload ${file.name}: ${error.message}`)
    } finally {
      setUploadingFiles(prev => ({ ...prev, [fieldName]: false }))
    }
  }

  const removeFile = (fieldName) => {
    setFormData(prev => ({
      ...prev,
      files: {
        ...prev.files,
        [fieldName]: null
      }
    }))
  }

  const generateJSON = () => {
    const jsonData = {
      metadata: {
        version: "1.0",
        exportedAt: new Date().toISOString(),
        applicationId: `EPC-${Date.now()}`,
        formFields: Object.keys(formData).filter(key => key !== 'files').length,
        filesAttached: Object.values(formData.files).filter(file => file !== null).length
      },
      companyInfo: {
        companyName: formData.companyName,
        tradingName: formData.tradingName,
        registrationNumber: formData.registrationNumber,
        companyRegNo: formData.companyRegNo,
        vatNumber: formData.vatNumber,
        registeredAddress: formData.registeredAddress,
        registeredOffice: formData.registeredOffice,
        headOffice: formData.headOffice,
        address: formData.address,
        parentCompany: formData.parentCompany,
        yearsTrading: formData.yearsTrading
      },
      primaryContact: {
        fullName: formData.contactName,
        jobTitle: formData.contactTitle,
        email: formData.email,
        phone: formData.phone
      },
      servicesExperience: {
        specializations: formData.specializations,
        softwareTools: formData.softwareTools,
        averageProjectsPerMonth: formData.projectsPerMonth,
        teamSize: formData.teamSize,
        yearsExperience: formData.yearsExperience,
        services: formData.services,
        coverage: formData.coverage,
        coverageRegion: formData.coverageRegion,
        resourcesPerProject: formData.resourcesPerProject,
        clientReference: formData.clientReference
      },
      rolesCapabilities: {
        principalContractor: formData.principalContractor,
        principalDesigner: formData.principalDesigner,
        principalContractorScale: formData.principalContractorScale,
        principalDesignerScale: formData.principalDesignerScale,
        internalStaffPercentage: formData.internalStaffPercentage,
        subcontractPercentage: formData.subcontractPercentage
      },
      certifications: {
        niceicContractor: formData.niceicContractor,
        mcsApproved: formData.mcsApproved,
        accreditations: formData.accreditations,
        certificationDetails: formData.certificationDetails,
        isoStandards: formData.isoStandards,
        namedPrincipalDesigner: formData.namedPrincipalDesigner,
        principalDesignerQualifications: formData.principalDesignerQualifications,
        trainingRecordsSummary: formData.trainingRecordsSummary
      },
      insurance: {
        publicLiabilityInsurance: formData.publicLiabilityInsurance,
        employersLiabilityInsurance: formData.employersLiabilityInsurance,
        professionalIndemnityInsurance: formData.professionalIndemnityInsurance,
        publicLiabilityExpiry: formData.publicLiabilityExpiry,
        employersLiabilityExpiry: formData.employersLiabilityExpiry,
        professionalIndemnityExpiry: formData.professionalIndemnityExpiry,
        publicLiabilityIndemnity: formData.publicLiabilityIndemnity
      },
      compliance: {
        hseNoticesLast5Years: formData.hseNoticesLast5Years,
        pendingProsecutions: formData.pendingProsecutions,
        riddorIncidentCount: formData.riddorIncidentCount,
        riddorIncidentDetails: formData.riddorIncidentDetails,
        cdmManagementEvidence: formData.cdmManagementEvidence,
        nearMissProcedure: formData.nearMissProcedure,
        qualityProcedureEvidence: formData.qualityProcedureEvidence,
        hseqIncidents: formData.hseqIncidents,
        riddorIncidents: formData.riddorIncidents,
        healthSafetyPolicyDate: formData.healthSafetyPolicyDate,
        environmentalPolicyDate: formData.environmentalPolicyDate,
        modernSlaveryPolicyDate: formData.modernSlaveryPolicyDate,
        substanceMisusePolicyDate: formData.substanceMisusePolicyDate,
        rightToWorkMethod: formData.rightToWorkMethod,
        gdprPolicyDate: formData.gdprPolicyDate,
        cyberIncidentLast3Years: formData.cyberIncidentLast3Years,
        legalClarifications: formData.legalClarifications,
        hasGdprPolicy: formData.hasGdprPolicy
      },
      agreement: {
        dataProcessingConsent: formData.dataProcessingConsent,
        marketingConsent: formData.marketingConsent,
        agreeToCodes: formData.agreeToCodes,
        agreeToTerms: formData.agreeToTerms,
        nationwideCoverage: formData.nationwideCoverage,
        contractsReviewed: formData.contractsReviewed,
        receivedContractPack: formData.receivedContractPack
      },
      submission: {
        additionalInformation: formData.additionalInformation,
        notes: formData.notes,
        clarifications: formData.clarifications,
        invitationCode: formData.invitationCode,
        submissionDate: formData.submissionDate,
        reviewDate: formData.reviewDate,
        referenceNumber: formData.referenceNumber
      },
      files: Object.keys(formData.files).reduce((acc, fieldName) => {
        if (formData.files[fieldName]) {
          acc[fieldName] = {
            fileName: formData.files[fieldName].name,
            fileSize: formData.files[fieldName].size,
            fileType: formData.files[fieldName].type,
            uploadedAt: formData.files[fieldName].uploadedAt
          }
        }
        return acc
      }, {})
    }
    
    return jsonData
  }

  const downloadJSON = () => {
    const jsonData = generateJSON()
    const blob = new Blob([JSON.stringify(jsonData, null, 2)], {
      type: 'application/json'
    })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `epc-application-${formData.companyName || 'draft'}-${new Date().toISOString().split('T')[0]}.json`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    console.log('handleSubmit called, currentStep:', currentStep)
    setIsSubmitting(true)

    try {
      // Transform flat form data to nested structure expected by Power Automate
      const transformedData = {
        // Basic company info
        companyName: formData.companyName,
        tradingName: formData.tradingName,
        registrationNumber: formData.registrationNumber,
        vatNumber: formData.vatNumber,
        registeredAddress: formData.registeredAddress,
        headOffice: formData.headOffice,
        parentCompany: formData.parentCompany,
        yearsTrading: formData.yearsTrading,
        
        // Contact info
        contactName: formData.contactName,
        contactTitle: formData.contactTitle,
        email: formData.email,
        phone: formData.phone,
        
        // Services and experience nested object
        servicesExperience: {
          specializations: formData.specializations,
          softwareTools: formData.softwareTools,
          averageProjectsPerMonth: formData.projectsPerMonth,
          teamSize: formData.teamSize,
          yearsExperience: formData.yearsExperience,
          services: formData.services,
          coverage: formData.coverage,
          coverageRegion: formData.coverageRegion,
          coverageRegions: formData.coverageRegions,
          resourcesPerProject: formData.resourcesPerProject,
          clientReference: formData.clientReference
        },
        
        // Roles and capabilities nested object
        rolesCapabilities: {
          principalContractor: formData.principalContractor,
          principalDesigner: formData.principalDesigner,
          principalContractorScale: formData.principalContractorScale,
          principalDesignerScale: formData.principalDesignerScale,
          internalStaffPercentage: formData.internalStaffPercentage,
          subcontractPercentage: formData.subcontractPercentage,
          namedPrincipalDesigner: formData.namedPrincipalDesigner,
          principalDesignerQualifications: formData.principalDesignerQualifications,
          trainingRecordsSummary: formData.trainingRecordsSummary
        },
        
        // Certifications nested object
        certifications: {
          niceicContractor: formData.niceicContractor,
          mcsApproved: formData.mcsApproved,
          accreditations: formData.accreditations,
          certificationDetails: formData.certificationDetails,
          isoStandards: formData.isoStandards
        },
        
        // Insurance nested object
        insurance: {
          publicLiabilityInsurance: formData.publicLiabilityInsurance,
          publicLiabilityExpiry: formData.publicLiabilityExpiry,
          publicLiabilityIndemnity: formData.publicLiabilityIndemnity,
          employersLiabilityInsurance: formData.employersLiabilityInsurance,
          employersLiabilityExpiry: formData.employersLiabilityExpiry,
          professionalIndemnityInsurance: formData.professionalIndemnityInsurance,
          professionalIndemnityExpiry: formData.professionalIndemnityExpiry
        },
        
        // Compliance information
        compliance: {
          hseNoticesLast5Years: formData.hseNoticesLast5Years,
          pendingProsecutions: formData.pendingProsecutions,
          riddorIncidentCount: formData.riddorIncidentCount,
          riddorIncidentDetails: formData.riddorIncidentDetails,
          cdmManagementEvidence: formData.cdmManagementEvidence,
          nearMissProcedure: formData.nearMissProcedure,
          qualityProcedureEvidence: formData.qualityProcedureEvidence,
          hseqIncidents: formData.hseqIncidents,
          riddorIncidents: formData.riddorIncidents,
          healthSafetyPolicyDate: formData.healthSafetyPolicyDate,
          environmentalPolicyDate: formData.environmentalPolicyDate,
          modernSlaveryPolicyDate: formData.modernSlaveryPolicyDate,
          substanceMisusePolicyDate: formData.substanceMisusePolicyDate,
          rightToWorkMethod: formData.rightToWorkMethod,
          gdprPolicyDate: formData.gdprPolicyDate,
          cyberIncidentLast3Years: formData.cyberIncidentLast3Years,
          legalClarifications: formData.legalClarifications
        },
        
        // Agreement nested object
        agreement: {
          agreeToTerms: formData.agreeToTerms,
          agreeToCodes: formData.agreeToCodes,
          dataProcessingConsent: formData.dataProcessingConsent,
          marketingConsent: formData.marketingConsent,
          nationwideCoverage: formData.nationwideCoverage,
          contractsReviewed: formData.contractsReviewed,
          receivedContractPack: formData.receivedContractPack
        },
        
        // Submission information
        submission: {
          additionalInformation: formData.additionalInformation,
          notes: formData.notes,
          clarifications: formData.clarifications,
          invitationCode: formData.invitationCode
        }
      }

      const response = await fetch('/api/epc-application', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(transformedData),
      })

      if (response.ok) {
        // Clear draft on successful submission
        if (formData.invitationCode) {
          try {
            await fetch('/api/clear-draft', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ invitationCode: formData.invitationCode })
            })
            console.log('✅ Draft cleared after successful submission')
          } catch (error) {
            console.error('⚠️ Failed to clear draft:', error)
          }
        }
        window.location.href = '/success'
      } else {
        alert('There was an error submitting your application. Please try again.')
      }
    } catch (error) {
      console.error('Error:', error)
      alert('There was an error submitting your application. Please try again.')
    }

    setIsSubmitting(false)
  }

  const nextStep = () => {
    console.log('nextStep called, currentStep:', currentStep)
    const newStep = Math.min(currentStep + 1, 6)
    console.log('Setting step to:', newStep)
    setCurrentStep(newStep)
  }
  const prevStep = () => setCurrentStep(Math.max(currentStep - 1, 1))

  // File Upload Component
  const FileUpload = ({ fieldName, label, accept = ".pdf,.doc,.docx,.jpg,.jpeg,.png", required = false }) => {
    const uploadedFile = formData.files[fieldName]
    const isUploading = uploadingFiles[fieldName]

    return (
      <div className="space-y-2">
        <label className="block text-sm font-medium text-slate-300">
          {label} {required && '*'}
        </label>
        
        {!uploadedFile ? (
          <div className="relative">
            <input
              type="file"
              accept={accept}
              onChange={(e) => handleFileUpload(e, fieldName)}
              disabled={isUploading}
              className="block w-full text-sm text-slate-400
                file:mr-4 file:py-2 file:px-4
                file:rounded-lg file:border-0
                file:text-sm file:font-medium
                file:bg-green-600 file:text-white
                hover:file:bg-green-500
                file:disabled:opacity-50
                bg-slate-700/30 border border-slate-600/50 rounded-lg
                focus:border-green-500/50 focus:ring-1 focus:ring-green-500/50"
            />
            {isUploading && (
              <div className="absolute inset-0 flex items-center justify-center bg-slate-800/80 rounded-lg">
                <div className="text-sm text-slate-300">Uploading...</div>
              </div>
            )}
          </div>
        ) : (
          <div className="flex items-center justify-between p-3 bg-green-900/20 border border-green-500/30 rounded-lg">
            <div className="flex items-center space-x-2">
              <svg className="w-5 h-5 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <div>
                <div className="text-sm font-medium text-green-400">{uploadedFile.name}</div>
                <div className="text-xs text-slate-400">{(uploadedFile.size / 1024 / 1024).toFixed(2)} MB</div>
              </div>
            </div>
            <button
              type="button"
              onClick={() => removeFile(fieldName)}
              className="text-red-400 hover:text-red-300 p-1"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        )}
        
        <p className="text-xs text-slate-400">
          Accepted formats: PDF, DOC, DOCX, JPG, PNG (max 10MB)
        </p>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-slate-900 py-12">
      <div className="mx-auto max-w-3xl px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-3xl font-bold tracking-tight text-white sm:text-4xl">
            EPC Partner Application
          </h1>
          <p className="mt-4 text-lg text-slate-400 max-w-2xl mx-auto">
            Complete your EPC Contractor Registration and Join Us On Our Renewable Journey
          </p>
          
          {/* Auto-save Notice */}
          <div className="mt-6 p-3 bg-blue-500/10 border border-blue-400/20 rounded-lg max-w-xl mx-auto">
            <div className="flex items-center text-sm text-blue-200">
              <svg className="w-4 h-4 mr-2 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span><strong>Auto-Save:</strong> Your progress is automatically saved as you type (every 3 seconds after you stop typing) and when you navigate between pages.</span>
            </div>
          </div>
        </div>

        {/* Full-width Progress Steps */}
        <div className="mb-8 relative left-1/2 right-1/2 -ml-[50vw] -mr-[50vw] w-screen">
          <nav aria-label="Progress" className="px-4 sm:px-6 lg:px-8">
            <ol role="list" className="divide-y divide-white/15 rounded-md border border-white/15 md:flex md:divide-y-0">
              {uiSteps.map((step, stepIdx) => (
                <li key={step.name} className="relative md:flex md:flex-1">
                  {step.status === 'complete' ? (
                    <a href="#" onClick={(e)=>{e.preventDefault(); setCurrentStep(step.id);}} className="group flex w-full items-center">
                      <span className="flex items-center px-6 py-4 text-sm font-medium">
                        <span className="flex size-10 shrink-0 items-center justify-center rounded-full bg-green-600 group-hover:bg-green-700">
                          <CheckIcon aria-hidden="true" className="size-6 text-white" />
                        </span>
                        <span className="ml-4 text-sm font-medium text-white">{step.name}</span>
                      </span>
                    </a>
                  ) : step.status === 'current' ? (
                    <a href="#" onClick={(e)=>e.preventDefault()} aria-current="step" className="flex items-center px-6 py-4 text-sm font-medium">
                      <span className="flex size-10 shrink-0 items-center justify-center rounded-full border-2 border-green-500">
                        <span className="text-green-400">{String(step.displayId).padStart(2,'0')}</span>
                      </span>
                      <span className="ml-4 text-sm font-medium text-green-400">{step.name}</span>
                    </a>
                  ) : (
                    <a href="#" onClick={(e)=>{e.preventDefault(); setCurrentStep(step.id);}} className="group flex items-center">
                      <span className="flex items-center px-6 py-4 text-sm font-medium">
                        <span className="flex size-10 shrink-0 items-center justify-center rounded-full border-2 border-white/15 group-hover:border-white/30">
                          <span className="text-slate-400 group-hover:text-white">{String(step.displayId).padStart(2,'0')}</span>
                        </span>
                        <span className="ml-4 text-sm font-medium text-slate-400 group-hover:text-white">{step.name}</span>
                      </span>
                    </a>
                  )}

                  {stepIdx !== uiSteps.length - 1 ? (
                    <div aria-hidden="true" className="absolute top-0 right-0 hidden h-full w-5 md:block">
                      <svg fill="none" viewBox="0 0 22 80" preserveAspectRatio="none" className="size-full text-white/15">
                        <path d="M0 -2L20 40L0 82" stroke="currentcolor" vectorEffect="non-scaling-stroke" strokeLinejoin="round" />
                      </svg>
                    </div>
                  ) : null}
                </li>
              ))}
            </ol>
          </nav>
        </div>

        {/* Auto-save Indicator */}
        {formData.invitationCode && (
          <div className="mb-6 flex items-center justify-between text-sm">
            <div className="flex items-center space-x-2">
              {saving ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-2 border-blue-400 border-t-transparent"></div>
                  <span className="text-slate-400">Saving draft...</span>
                </>
              ) : lastSaved ? (
                <>
                  <div className="h-2 w-2 rounded-full bg-green-400"></div>
                  <span className="text-slate-400">
                    Draft saved {lastSaved.toLocaleTimeString()}
                  </span>
                </>
              ) : (
                <span className="text-slate-500">Progress will be auto-saved</span>
              )}
            </div>
            {draftLoaded && (
              <span className="text-green-400 text-xs bg-green-400/10 px-2 py-1 rounded-full">
                📖 Resumed from draft
              </span>
            )}
          </div>
        )}

        {/* Form Card */}
        <div className="relative">
          {/* Subtle background blur effects */}
          <div className="absolute inset-0 rounded-2xl bg-gradient-to-tr from-green-300/5 via-green-300/3 to-blue-300/5 opacity-50 blur-lg" />
          
          {/* Main form container */}
          <div className="relative rounded-2xl bg-slate-800/60 ring-1 ring-white/5 backdrop-blur-sm">
            {/* Subtle top and bottom borders */}
            <div className="absolute -top-px right-16 left-16 h-px bg-gradient-to-r from-green-300/0 via-green-300/20 to-green-300/0" />
            <div className="absolute right-16 -bottom-px left-16 h-px bg-gradient-to-r from-blue-400/0 via-blue-400/20 to-blue-400/0" />
            
            <form onSubmit={handleSubmit} className="p-8 space-y-8">
              {/* Step 1: Company Information */}
              {currentStep === 1 && (
                <div className="space-y-6">
                  <h2 className="text-xl font-semibold text-white mb-6">Company Information</h2>
                  
                  <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
                    <div>
                      <label htmlFor="companyName" className="block text-sm font-medium text-slate-300 mb-2">
                        Company Name *
                      </label>
                      <input
                        type="text"
                        name="companyName"
                        id="companyName"
                        required
                        className="block w-full rounded-lg border-0 bg-slate-700/30 px-4 py-3 text-white placeholder-slate-400 ring-1 ring-slate-600/50 focus:ring-2 focus:ring-green-500/50 focus:ring-offset-0 sm:text-sm transition-all"
                        placeholder="Enter your registered company name"
                        value={formData.companyName}
                        onChange={handleInputChange}
                      />
                    </div>

                    <div>
                      <label htmlFor="tradingName" className="block text-sm font-medium text-slate-300 mb-2">
                        Trading Name
                      </label>
                      <input
                        type="text"
                        name="tradingName"
                        id="tradingName"
                        className="block w-full rounded-lg border-0 bg-slate-700/30 px-4 py-3 text-white placeholder-slate-400 ring-1 ring-slate-600/50 focus:ring-2 focus:ring-green-500/50 focus:ring-offset-0 sm:text-sm transition-all"
                        placeholder="Trading or operating name"
                        value={formData.tradingName}
                        onChange={handleInputChange}
                      />
                    </div>

                    <div>
                      <label htmlFor="registrationNumber" className="block text-sm font-medium text-slate-300 mb-2">
                        Company Registration Number *
                      </label>
                      <input
                        type="text"
                        name="registrationNumber"
                        id="registrationNumber"
                        required
                        className="block w-full rounded-lg border-0 bg-slate-700/30 px-4 py-3 text-white placeholder-slate-400 ring-1 ring-slate-600/50 focus:ring-2 focus:ring-green-500/50 focus:ring-offset-0 sm:text-sm transition-all"
                        placeholder="e.g., 12345678"
                        value={formData.registrationNumber}
                        onChange={handleInputChange}
                      />
                    </div>

                    <div>
                      <label htmlFor="vatNumber" className="block text-sm font-medium text-slate-300 mb-2">
                        VAT Number
                      </label>
                      <input
                        type="text"
                        name="vatNumber"
                        id="vatNumber"
                        className="block w-full rounded-lg border-0 bg-slate-700/30 px-4 py-3 text-white placeholder-slate-400 ring-1 ring-slate-600/50 focus:ring-2 focus:ring-green-500/50 focus:ring-offset-0 sm:text-sm transition-all"
                        placeholder="GB123456789"
                        value={formData.vatNumber}
                        onChange={handleInputChange}
                      />
                    </div>

                    <div>
                      <label htmlFor="parentCompany" className="block text-sm font-medium text-slate-300 mb-2">
                        Parent Company
                      </label>
                      <input
                        type="text"
                        name="parentCompany"
                        id="parentCompany"
                        className="block w-full rounded-lg border-0 bg-slate-700/30 px-4 py-3 text-white placeholder-slate-400 ring-1 ring-slate-600/50 focus:ring-2 focus:ring-green-500/50 focus:ring-offset-0 sm:text-sm transition-all"
                        placeholder="Parent or holding company name"
                        value={formData.parentCompany}
                        onChange={handleInputChange}
                      />
                    </div>

                    <div>
                      <label htmlFor="yearsTrading" className="block text-sm font-medium text-slate-300 mb-2">
                        Years Trading
                      </label>
                      <input
                        type="number"
                        name="yearsTrading"
                        id="yearsTrading"
                        className="block w-full rounded-lg border-0 bg-slate-700/30 px-4 py-3 text-white placeholder-slate-400 ring-1 ring-slate-600/50 focus:ring-2 focus:ring-green-500/50 focus:ring-offset-0 sm:text-sm transition-all"
                        placeholder="Number of years"
                        value={formData.yearsTrading}
                        onChange={handleInputChange}
                      />
                    </div>
                  </div>

                  <div>
                    <label htmlFor="registeredAddress" className="block text-sm font-medium text-slate-300 mb-2">
                      Registered Office Address *
                    </label>
                    <textarea
                      name="registeredAddress"
                      id="registeredAddress"
                      rows={3}
                      required
                      className="block w-full rounded-lg border-0 bg-slate-700/30 px-4 py-3 text-white placeholder-slate-400 ring-1 ring-slate-600/50 focus:ring-2 focus:ring-green-500/50 focus:ring-offset-0 sm:text-sm transition-all"
                      placeholder="Enter your complete registered office address including postcode"
                      value={formData.registeredAddress}
                      onChange={handleInputChange}
                    />
                  </div>

                  <div>
                    <label htmlFor="headOffice" className="block text-sm font-medium text-slate-300 mb-2">
                      Head Office Address
                    </label>
                    <textarea
                      name="headOffice"
                      id="headOffice"
                      rows={3}
                      className="block w-full rounded-lg border-0 bg-slate-700/30 px-4 py-3 text-white placeholder-slate-400 ring-1 ring-slate-600/50 focus:ring-2 focus:ring-green-500/50 focus:ring-offset-0 sm:text-sm transition-all"
                      placeholder="Head office address if different from registered office"
                      value={formData.headOffice}
                      onChange={handleInputChange}
                    />
                  </div>
                </div>
              )}

              {/* Step 2: Contact Information */}
              {currentStep === 2 && (
                <div className="space-y-6">
                  <h2 className="text-xl font-semibold text-white mb-6">Contact Information</h2>
                  
                  <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
                    <div>
                      <label htmlFor="contactName" className="block text-sm font-medium text-slate-300 mb-2">
                        Primary Contact Name *
                      </label>
                      <input
                        type="text"
                        name="contactName"
                        id="contactName"
                        required
                        className="block w-full rounded-lg border-0 bg-slate-700/30 px-4 py-3 text-white placeholder-slate-400 ring-1 ring-slate-600/50 focus:ring-2 focus:ring-green-500/50 focus:ring-offset-0 sm:text-sm transition-all"
                        placeholder="Full name of primary contact"
                        value={formData.contactName}
                        onChange={handleInputChange}
                      />
                    </div>

                    <div>
                      <label htmlFor="contactTitle" className="block text-sm font-medium text-slate-300 mb-2">
                        Job Title *
                      </label>
                      <input
                        type="text"
                        name="contactTitle"
                        id="contactTitle"
                        required
                        className="block w-full rounded-lg border-0 bg-slate-700/30 px-4 py-3 text-white placeholder-slate-400 ring-1 ring-slate-600/50 focus:ring-2 focus:ring-green-500/50 focus:ring-offset-0 sm:text-sm transition-all"
                        placeholder="e.g., Director, Project Manager"
                        value={formData.contactTitle}
                        onChange={handleInputChange}
                      />
                    </div>

                    <div>
                      <label htmlFor="email" className="block text-sm font-medium text-slate-300 mb-2">
                        Email Address *
                      </label>
                      <input
                        type="email"
                        name="email"
                        id="email"
                        required
                        className="block w-full rounded-lg border-0 bg-slate-700/30 px-4 py-3 text-white placeholder-slate-400 ring-1 ring-slate-600/50 focus:ring-2 focus:ring-green-500/50 focus:ring-offset-0 sm:text-sm transition-all"
                        placeholder="contact@company.com"
                        value={formData.email}
                        onChange={handleInputChange}
                      />
                    </div>

                    <div>
                      <label htmlFor="phone" className="block text-sm font-medium text-slate-300 mb-2">
                        Phone Number *
                      </label>
                      <input
                        type="tel"
                        name="phone"
                        id="phone"
                        required
                        className="block w-full rounded-lg border-0 bg-slate-700/30 px-4 py-3 text-white placeholder-slate-400 ring-1 ring-slate-600/50 focus:ring-2 focus:ring-green-500/50 focus:ring-offset-0 sm:text-sm transition-all"
                        placeholder="+44 1234 567890"
                        value={formData.phone}
                        onChange={handleInputChange}
                      />
                    </div>

                    <div>
                      <label htmlFor="companyWebsite" className="block text-sm font-medium text-slate-300 mb-2">
                        Company Website
                      </label>
                      <input
                        type="url"
                        name="companyWebsite"
                        id="companyWebsite"
                        className="block w-full rounded-lg border-0 bg-slate-700/30 px-4 py-3 text-white placeholder-slate-400 ring-1 ring-slate-600/50 focus:ring-2 focus:ring-green-500/50 focus:ring-offset-0 sm:text-sm transition-all"
                        placeholder="https://www.yourcompany.com"
                        value={formData.companyWebsite}
                        onChange={handleInputChange}
                      />
                    </div>

                    <div>
                      <label htmlFor="companyLogo" className="block text-sm font-medium text-slate-300 mb-2">
                        Company Logo
                      </label>
                      <div className="flex items-center space-x-4">
                        <input
                          type="file"
                          name="companyLogo"
                          id="companyLogo"
                          accept="image/*,.svg"
                          className="block w-full text-sm text-slate-300 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-medium file:bg-green-600 file:text-white hover:file:bg-green-700 file:cursor-pointer"
                          onChange={(e) => handleFileUpload(e, 'companyLogo')}
                        />
                        {uploadingFiles.companyLogo && (
                          <div className="text-sm text-yellow-400">Uploading...</div>
                        )}
                        {formData.companyLogo && !uploadingFiles.companyLogo && (
                          <div className="text-sm text-green-400">✓ Uploaded</div>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Step 3: Capabilities & Experience */}
              {currentStep === 3 && (
                <div className="space-y-6">
                  <h2 className="text-xl font-semibold text-white mb-6">Capabilities & Experience</h2>
                  
                  <div>
                    <label htmlFor="specializations" className="block text-sm font-medium text-slate-300 mb-2">
                      Specializations *
                    </label>
                    <textarea
                      name="specializations"
                      id="specializations"
                      rows={3}
                      required
                      className="block w-full rounded-lg border-0 bg-slate-700/30 px-4 py-3 text-white placeholder-slate-400 ring-1 ring-slate-600/50 focus:ring-2 focus:ring-green-500/50 focus:ring-offset-0 sm:text-sm transition-all"
                      placeholder="Describe your areas of specialization (e.g., solar PV, battery storage, heat pumps)"
                      value={formData.specializations}
                      onChange={handleInputChange}
                    />
                  </div>

                  <div>
                    <label htmlFor="softwareTools" className="block text-sm font-medium text-slate-300 mb-2">
                      Software & Tools Used
                    </label>
                    <textarea
                      name="softwareTools"
                      id="softwareTools"
                      rows={3}
                      className="block w-full rounded-lg border-0 bg-slate-700/30 px-4 py-3 text-white placeholder-slate-400 ring-1 ring-slate-600/50 focus:ring-2 focus:ring-green-500/50 focus:ring-offset-0 sm:text-sm transition-all"
                      placeholder="List design software, project management tools, etc."
                      value={formData.softwareTools}
                      onChange={handleInputChange}
                    />
                  </div>

                  <div className="grid grid-cols-1 gap-6 sm:grid-cols-3">
                    <div>
                      <label htmlFor="projectsPerMonth" className="block text-sm font-medium text-slate-300 mb-2">
                        Projects Per Month
                      </label>
                      <input
                        type="number"
                        name="projectsPerMonth"
                        id="projectsPerMonth"
                        className="block w-full rounded-lg border-0 bg-slate-700/30 px-4 py-3 text-white placeholder-slate-400 ring-1 ring-slate-600/50 focus:ring-2 focus:ring-green-500/50 focus:ring-offset-0 sm:text-sm transition-all"
                        placeholder="Average number"
                        value={formData.projectsPerMonth}
                        onChange={handleInputChange}
                      />
                    </div>

                    <div>
                      <label htmlFor="teamSize" className="block text-sm font-medium text-slate-300 mb-2">
                        Team Size
                      </label>
                      <input
                        type="number"
                        name="teamSize"
                        id="teamSize"
                        className="block w-full rounded-lg border-0 bg-slate-700/30 px-4 py-3 text-white placeholder-slate-400 ring-1 ring-slate-600/50 focus:ring-2 focus:ring-green-500/50 focus:ring-offset-0 sm:text-sm transition-all"
                        placeholder="Number of staff"
                        value={formData.teamSize}
                        onChange={handleInputChange}
                      />
                    </div>

                    <div>
                      <label htmlFor="yearsExperience" className="block text-sm font-medium text-slate-300 mb-2">
                        Years Experience
                      </label>
                      <input
                        type="number"
                        name="yearsExperience"
                        id="yearsExperience"
                        className="block w-full rounded-lg border-0 bg-slate-700/30 px-4 py-3 text-white placeholder-slate-400 ring-1 ring-slate-600/50 focus:ring-2 focus:ring-green-500/50 focus:ring-offset-0 sm:text-sm transition-all"
                        placeholder="In renewable energy"
                        value={formData.yearsExperience}
                        onChange={handleInputChange}
                      />
                    </div>
                  </div>

                  <div>
                    <label htmlFor="services" className="block text-sm font-medium text-slate-300 mb-2">
                      Services Offered
                    </label>
                    <textarea
                      name="services"
                      id="services"
                      rows={3}
                      className="block w-full rounded-lg border-0 bg-slate-700/30 px-4 py-3 text-white placeholder-slate-400 ring-1 ring-slate-600/50 focus:ring-2 focus:ring-green-500/50 focus:ring-offset-0 sm:text-sm transition-all"
                      placeholder="Detail the services your company provides"
                      value={formData.services}
                      onChange={handleInputChange}
                    />
                  </div>

                  <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
                    <div>
                      <label htmlFor="coverage" className="block text-sm font-medium text-slate-300 mb-2">
                        Geographic Coverage (summary)
                      </label>
                      <input
                        type="text"
                        name="coverage"
                        id="coverage"
                        className="block w-full rounded-lg border-0 bg-slate-700/30 px-4 py-3 text-white placeholder-slate-400 ring-1 ring-slate-600/50 focus:ring-2 focus:ring-green-500/50 focus:ring-offset-0 sm:text-sm transition-all"
                        placeholder="e.g., South East England"
                        value={formData.coverage}
                        onChange={handleInputChange}
                      />
                      <p className="mt-2 text-xs text-slate-400">Optional summary; select specific regions on the right.</p>
                    </div>

                    <div>
                      <span className="block text-sm font-medium text-slate-300 mb-2">Coverage Regions *</span>
                      <div className="grid grid-cols-2 gap-2 text-sm">
                        {['North West','North East','Yorkshire','Midlands','South East','South West','Scotland','Wales'].map((region) => (
                          <label key={region} className="inline-flex items-center gap-2 p-2 rounded-md bg-slate-700/20 ring-1 ring-slate-600/40 cursor-pointer">
                            <input
                              type="checkbox"
                              className="h-4 w-4 rounded border-slate-600 bg-slate-800 text-green-500 focus:ring-green-500"
                              checked={(formData.coverageRegions || []).includes(region)}
                              onChange={() => toggleCoverageRegion(region)}
                            />
                            <span className="text-slate-200">{region}</span>
                          </label>
                        ))}
                      </div>
                      <div className="mt-3">
                        <label htmlFor="coverageRegion" className="block text-xs font-medium text-slate-400 mb-1">Other regions (comma separated)</label>
                        <input
                          type="text"
                          name="coverageRegion"
                          id="coverageRegion"
                          className="block w-full rounded-lg border-0 bg-slate-700/30 px-3 py-2 text-white placeholder-slate-400 ring-1 ring-slate-600/50 focus:ring-2 focus:ring-green-500/50 focus:ring-offset-0 sm:text-xs transition-all"
                          placeholder="e.g., Midlands, Republic of Ireland"
                          value={formData.coverageRegion}
                          onChange={handleInputChange}
                        />
                        {formData.coverageRegions?.length > 0 && (
                          <p className="mt-2 text-xs text-slate-400">Selected: {formData.coverageRegions.join(', ')}</p>
                        )}
                      </div>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
                    <div>
                      <label htmlFor="resourcesPerProject" className="block text-sm font-medium text-slate-300 mb-2">
                        Resources Per Project
                      </label>
                      <input
                        type="text"
                        name="resourcesPerProject"
                        id="resourcesPerProject"
                        className="block w-full rounded-lg border-0 bg-slate-700/30 px-4 py-3 text-white placeholder-slate-400 ring-1 ring-slate-600/50 focus:ring-2 focus:ring-green-500/50 focus:ring-offset-0 sm:text-sm transition-all"
                        placeholder="Typical resources allocated per project"
                        value={formData.resourcesPerProject}
                        onChange={handleInputChange}
                      />
                    </div>

                    <div>
                      <label htmlFor="clientReference" className="block text-sm font-medium text-slate-300 mb-2">
                        Client Reference
                      </label>
                      <input
                        type="text"
                        name="clientReference"
                        id="clientReference"
                        className="block w-full rounded-lg border-0 bg-slate-700/30 px-4 py-3 text-white placeholder-slate-400 ring-1 ring-slate-600/50 focus:ring-2 focus:ring-green-500/50 focus:ring-offset-0 sm:text-sm transition-all"
                        placeholder="Key client reference contact"
                        value={formData.clientReference}
                        onChange={handleInputChange}
                      />
                    </div>
                  </div>
                </div>
              )}

              {/* Step 4: Roles & Certifications */}
              {currentStep === 4 && (
                <div className="space-y-6">
                  <h2 className="text-xl font-semibold text-white mb-6">Roles & Certifications</h2>
                  
                  <div className="space-y-4">
                    <h3 className="text-lg font-medium text-white">Primary Roles</h3>
                    
                    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                      <div className="flex items-center">
                        <input
                          type="checkbox"
                          name="principalContractor"
                          id="principalContractor"
                          checked={formData.principalContractor}
                          onChange={(e) => setFormData({...formData, principalContractor: e.target.checked})}
                          className="h-4 w-4 rounded border-slate-600 bg-slate-700 text-green-600 focus:ring-green-500 focus:ring-offset-slate-900"
                        />
                        <label htmlFor="principalContractor" className="ml-3 text-sm text-slate-300">
                          Acts as Principal Contractor
                        </label>
                      </div>

                      <div className="flex items-center">
                        <input
                          type="checkbox"
                          name="principalDesigner"
                          id="principalDesigner"
                          checked={formData.principalDesigner}
                          onChange={(e) => setFormData({...formData, principalDesigner: e.target.checked})}
                          className="h-4 w-4 rounded border-slate-600 bg-slate-700 text-green-600 focus:ring-green-500 focus:ring-offset-slate-900"
                        />
                        <label htmlFor="principalDesigner" className="ml-3 text-sm text-slate-300">
                          Acts as Principal Designer
                        </label>
                      </div>
                    </div>

                    <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
                      <div>
                        <label htmlFor="principalContractorScale" className="block text-sm font-medium text-slate-300 mb-2">
                          Principal Contractor Scale (Last Year)
                        </label>
                        <input
                          type="text"
                          name="principalContractorScale"
                          id="principalContractorScale"
                          className="block w-full rounded-lg border-0 bg-slate-700/30 px-4 py-3 text-white placeholder-slate-400 ring-1 ring-slate-600/50 focus:ring-2 focus:ring-green-500/50 focus:ring-offset-0 sm:text-sm transition-all"
                          placeholder="e.g., 1-50 projects, £500k-£2M"
                          value={formData.principalContractorScale}
                          onChange={handleInputChange}
                        />
                      </div>

                      <div>
                        <label htmlFor="principalDesignerScale" className="block text-sm font-medium text-slate-300 mb-2">
                          Principal Designer Scale (Last Year)
                        </label>
                        <input
                          type="text"
                          name="principalDesignerScale"
                          id="principalDesignerScale"
                          className="block w-full rounded-lg border-0 bg-slate-700/30 px-4 py-3 text-white placeholder-slate-400 ring-1 ring-slate-600/50 focus:ring-2 focus:ring-green-500/50 focus:ring-offset-0 sm:text-sm transition-all"
                          placeholder="e.g., 1-50 projects, £500k-£2M"
                          value={formData.principalDesignerScale}
                          onChange={handleInputChange}
                        />
                      </div>
                    </div>

                    <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
                      <div>
                        <label htmlFor="internalStaffPercentage" className="block text-sm font-medium text-slate-300 mb-2">
                          Internal Staff Percentage
                        </label>
                        <input
                          type="number"
                          name="internalStaffPercentage"
                          id="internalStaffPercentage"
                          className="block w-full rounded-lg border-0 bg-slate-700/30 px-4 py-3 text-white placeholder-slate-400 ring-1 ring-slate-600/50 focus:ring-2 focus:ring-green-500/50 focus:ring-offset-0 sm:text-sm transition-all"
                          placeholder="% of work done by internal staff"
                          value={formData.internalStaffPercentage}
                          onChange={handleInputChange}
                        />
                      </div>

                      <div>
                        <label htmlFor="subcontractPercentage" className="block text-sm font-medium text-slate-300 mb-2">
                          Subcontract Percentage
                        </label>
                        <input
                          type="number"
                          name="subcontractPercentage"
                          id="subcontractPercentage"
                          className="block w-full rounded-lg border-0 bg-slate-700/30 px-4 py-3 text-white placeholder-slate-400 ring-1 ring-slate-600/50 focus:ring-2 focus:ring-green-500/50 focus:ring-offset-0 sm:text-sm transition-all"
                          placeholder="% of work subcontracted"
                          value={formData.subcontractPercentage}
                          onChange={handleInputChange}
                        />
                      </div>
                    </div>
                  </div>

                  <div className="space-y-4">
                    <h3 className="text-lg font-medium text-white">Certifications</h3>
                    
                    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                      <div className="flex items-center">
                        <input
                          type="checkbox"
                          name="niceicContractor"
                          id="niceicContractor"
                          checked={formData.niceicContractor}
                          onChange={(e) => setFormData({...formData, niceicContractor: e.target.checked})}
                          className="h-4 w-4 rounded border-slate-600 bg-slate-700 text-green-600 focus:ring-green-500 focus:ring-offset-slate-900"
                        />
                        <label htmlFor="niceicContractor" className="ml-3 text-sm text-slate-300">
                          NICEIC CPS Approved
                        </label>
                      </div>

                      <div className="flex items-center">
                        <input
                          type="checkbox"
                          name="mcsApproved"
                          id="mcsApproved"
                          checked={formData.mcsApproved}
                          onChange={(e) => setFormData({...formData, mcsApproved: e.target.checked})}
                          className="h-4 w-4 rounded border-slate-600 bg-slate-700 text-green-600 focus:ring-green-500 focus:ring-offset-slate-900"
                        />
                        <label htmlFor="mcsApproved" className="ml-3 text-sm text-slate-300">
                          MCS Approved
                        </label>
                      </div>
                    </div>

                    <div>
                      <label htmlFor="accreditations" className="block text-sm font-medium text-slate-300 mb-2">
                        Other Accreditations
                      </label>
                      <textarea
                        name="accreditations"
                        id="accreditations"
                        rows={3}
                        className="block w-full rounded-lg border-0 bg-slate-700/30 px-4 py-3 text-white placeholder-slate-400 ring-1 ring-slate-600/50 focus:ring-2 focus:ring-green-500/50 focus:ring-offset-0 sm:text-sm transition-all"
                        placeholder="List additional certifications and accreditations"
                        value={formData.accreditations}
                        onChange={handleInputChange}
                      />
                    </div>

                    <div>
                      <label htmlFor="certificationDetails" className="block text-sm font-medium text-slate-300 mb-2">
                        Certification Details
                      </label>
                      <textarea
                        name="certificationDetails"
                        id="certificationDetails"
                        rows={3}
                        className="block w-full rounded-lg border-0 bg-slate-700/30 px-4 py-3 text-white placeholder-slate-400 ring-1 ring-slate-600/50 focus:ring-2 focus:ring-green-500/50 focus:ring-offset-0 sm:text-sm transition-all"
                        placeholder="Provide details about your certifications"
                        value={formData.certificationDetails}
                        onChange={handleInputChange}
                      />
                    </div>

                    <div>
                      <label htmlFor="isoStandards" className="block text-sm font-medium text-slate-300 mb-2">
                        ISO Standards
                      </label>
                      <input
                        type="text"
                        name="isoStandards"
                        id="isoStandards"
                        className="block w-full rounded-lg border-0 bg-slate-700/30 px-4 py-3 text-white placeholder-slate-400 ring-1 ring-slate-600/50 focus:ring-2 focus:ring-green-500/50 focus:ring-offset-0 sm:text-sm transition-all"
                        placeholder="e.g., ISO 9001, ISO 14001, ISO 45001"
                        value={formData.isoStandards}
                        onChange={handleInputChange}
                      />
                    </div>

                    <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
                      <div>
                        <label htmlFor="namedPrincipalDesigner" className="block text-sm font-medium text-slate-300 mb-2">
                          Named Principal Designer
                        </label>
                        <input
                          type="text"
                          name="namedPrincipalDesigner"
                          id="namedPrincipalDesigner"
                          className="block w-full rounded-lg border-0 bg-slate-700/30 px-4 py-3 text-white placeholder-slate-400 ring-1 ring-slate-600/50 focus:ring-2 focus:ring-green-500/50 focus:ring-offset-0 sm:text-sm transition-all"
                          placeholder="Name of designated principal designer"
                          value={formData.namedPrincipalDesigner}
                          onChange={handleInputChange}
                        />
                      </div>

                      <div>
                        <label htmlFor="principalDesignerQualifications" className="block text-sm font-medium text-slate-300 mb-2">
                          PD Qualifications
                        </label>
                        <input
                          type="text"
                          name="principalDesignerQualifications"
                          id="principalDesignerQualifications"
                          className="block w-full rounded-lg border-0 bg-slate-700/30 px-4 py-3 text-white placeholder-slate-400 ring-1 ring-slate-600/50 focus:ring-2 focus:ring-green-500/50 focus:ring-offset-0 sm:text-sm transition-all"
                          placeholder="Principal designer qualifications"
                          value={formData.principalDesignerQualifications}
                          onChange={handleInputChange}
                        />
                      </div>
                    </div>

                    <div>
                      <label htmlFor="trainingRecordsSummary" className="block text-sm font-medium text-slate-300 mb-2">
                        Training Records Summary
                      </label>
                      <textarea
                        name="trainingRecordsSummary"
                        id="trainingRecordsSummary"
                        rows={3}
                        className="block w-full rounded-lg border-0 bg-slate-700/30 px-4 py-3 text-white placeholder-slate-400 ring-1 ring-slate-600/50 focus:ring-2 focus:ring-green-500/50 focus:ring-offset-0 sm:text-sm transition-all"
                        placeholder="Summary of staff training records and competency development"
                        value={formData.trainingRecordsSummary}
                        onChange={handleInputChange}
                      />
                    </div>
                  </div>
                  
                  {/* Document Uploads for Certifications */}
                  <div className="mt-8 space-y-6">
                    <h3 className="text-lg font-medium text-white">Supporting Documents</h3>
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <FileUpload
                        fieldName="niceicCertificate"
                        label="NICEIC Certificate"
                        accept=".pdf,.jpg,.jpeg,.png"
                      />
                      
                      <FileUpload
                        fieldName="mcsCertificate"
                        label="MCS Certificate"
                        accept=".pdf,.jpg,.jpeg,.png"
                      />
                      
                      <FileUpload
                        fieldName="isoCertificates"
                        label="ISO Standards Certificates"
                        accept=".pdf,.jpg,.jpeg,.png"
                      />
                      
                      <FileUpload
                        fieldName="otherCertifications"
                        label="Other Certifications"
                        accept=".pdf,.doc,.docx,.jpg,.jpeg,.png"
                      />
                    </div>
                  </div>
                </div>
              )}

              {/* Step 5: Insurance & Compliance */}
              {currentStep === 5 && (
                <div className="space-y-6">
                  <h2 className="text-xl font-semibold text-white mb-6">Insurance & Compliance</h2>
                  
                  <div className="space-y-4">
                    <h3 className="text-lg font-medium text-white">Insurance Coverage</h3>
                    
                    <div className="space-y-4">
                      <div className="flex items-center">
                        <input
                          type="checkbox"
                          name="publicLiabilityInsurance"
                          id="publicLiabilityInsurance"
                          checked={formData.publicLiabilityInsurance}
                          onChange={(e) => setFormData({...formData, publicLiabilityInsurance: e.target.checked})}
                          className="h-4 w-4 rounded border-slate-600 bg-slate-700 text-green-600 focus:ring-green-500 focus:ring-offset-slate-900"
                        />
                        <label htmlFor="publicLiabilityInsurance" className="ml-3 text-sm text-slate-300">
                          Public/Product Liability Insurance
                        </label>
                      </div>

                      {formData.publicLiabilityInsurance && (
                        <div className="ml-7 grid grid-cols-1 gap-4 sm:grid-cols-2">
                          <div>
                            <label htmlFor="publicLiabilityExpiry" className="block text-sm font-medium text-slate-300 mb-2">
                              Expiry Date
                            </label>
                            <input
                              type="date"
                              name="publicLiabilityExpiry"
                              id="publicLiabilityExpiry"
                              className="block w-full rounded-lg border-0 bg-slate-700/30 px-4 py-3 text-white placeholder-slate-400 ring-1 ring-slate-600/50 focus:ring-2 focus:ring-green-500/50 focus:ring-offset-0 sm:text-sm transition-all"
                              value={formData.publicLiabilityExpiry}
                              onChange={handleInputChange}
                            />
                          </div>
                          <div className="flex items-center">
                            <input
                              type="checkbox"
                              name="publicLiabilityIndemnity"
                              id="publicLiabilityIndemnity"
                              checked={formData.publicLiabilityIndemnity}
                              onChange={(e) => setFormData({...formData, publicLiabilityIndemnity: e.target.checked})}
                              className="h-4 w-4 rounded border-slate-600 bg-slate-700 text-green-600 focus:ring-green-500 focus:ring-offset-slate-900"
                            />
                            <label htmlFor="publicLiabilityIndemnity" className="ml-3 text-sm text-slate-300">
                              Indemnity Coverage
                            </label>
                          </div>
                        </div>
                      )}

                      <div className="flex items-center">
                        <input
                          type="checkbox"
                          name="employersLiabilityInsurance"
                          id="employersLiabilityInsurance"
                          checked={formData.employersLiabilityInsurance}
                          onChange={(e) => setFormData({...formData, employersLiabilityInsurance: e.target.checked})}
                          className="h-4 w-4 rounded border-slate-600 bg-slate-700 text-green-600 focus:ring-green-500 focus:ring-offset-slate-900"
                        />
                        <label htmlFor="employersLiabilityInsurance" className="ml-3 text-sm text-slate-300">
                          Employers Liability Insurance
                        </label>
                      </div>

                      {formData.employersLiabilityInsurance && (
                        <div className="ml-7">
                          <div>
                            <label htmlFor="employersLiabilityExpiry" className="block text-sm font-medium text-slate-300 mb-2">
                              Expiry Date
                            </label>
                            <input
                              type="date"
                              name="employersLiabilityExpiry"
                              id="employersLiabilityExpiry"
                              className="block w-full rounded-lg border-0 bg-slate-700/30 px-4 py-3 text-white placeholder-slate-400 ring-1 ring-slate-600/50 focus:ring-2 focus:ring-green-500/50 focus:ring-offset-0 sm:text-sm transition-all sm:max-w-xs"
                              value={formData.employersLiabilityExpiry}
                              onChange={handleInputChange}
                            />
                          </div>
                        </div>
                      )}

                      <div className="flex items-center">
                        <input
                          type="checkbox"
                          name="professionalIndemnityInsurance"
                          id="professionalIndemnityInsurance"
                          checked={formData.professionalIndemnityInsurance}
                          onChange={(e) => setFormData({...formData, professionalIndemnityInsurance: e.target.checked})}
                          className="h-4 w-4 rounded border-slate-600 bg-slate-700 text-green-600 focus:ring-green-500 focus:ring-offset-slate-900"
                        />
                        <label htmlFor="professionalIndemnityInsurance" className="ml-3 text-sm text-slate-300">
                          Professional Indemnity Insurance
                        </label>
                      </div>

                      {formData.professionalIndemnityInsurance && (
                        <div className="ml-7">
                          <div>
                            <label htmlFor="professionalIndemnityExpiry" className="block text-sm font-medium text-slate-300 mb-2">
                              Expiry Date
                            </label>
                            <input
                              type="date"
                              name="professionalIndemnityExpiry"
                              id="professionalIndemnityExpiry"
                              className="block w-full rounded-lg border-0 bg-slate-700/30 px-4 py-3 text-white placeholder-slate-400 ring-1 ring-slate-600/50 focus:ring-2 focus:ring-green-500/50 focus:ring-offset-0 sm:text-sm transition-all sm:max-w-xs"
                              value={formData.professionalIndemnityExpiry}
                              onChange={handleInputChange}
                            />
                          </div>
                        </div>
                      )}
                    </div>
                  </div>

                  <div className="space-y-4">
                    <h3 className="text-lg font-medium text-white">Compliance Information</h3>
                    
                    <div>
                      <label htmlFor="hseNoticesLast5Years" className="block text-sm font-medium text-slate-300 mb-2">
                        HSE Improvement or Prohibition Notices (Last 5 Years)
                      </label>
                      <textarea
                        name="hseNoticesLast5Years"
                        id="hseNoticesLast5Years"
                        rows={3}
                        className="block w-full rounded-lg border-0 bg-slate-700/30 px-4 py-3 text-white placeholder-slate-400 ring-1 ring-slate-600/50 focus:ring-2 focus:ring-green-500/50 focus:ring-offset-0 sm:text-sm transition-all"
                        placeholder="Please provide details of any HSE notices received, or enter 'None' if applicable"
                        value={formData.hseNoticesLast5Years}
                        onChange={handleInputChange}
                      />
                    </div>

                    <div>
                      <label htmlFor="pendingProsecutions" className="block text-sm font-medium text-slate-300 mb-2">
                        Pending Prosecutions or Legal Issues
                      </label>
                      <textarea
                        name="pendingProsecutions"
                        id="pendingProsecutions"
                        rows={3}
                        className="block w-full rounded-lg border-0 bg-slate-700/30 px-4 py-3 text-white placeholder-slate-400 ring-1 ring-slate-600/50 focus:ring-2 focus:ring-green-500/50 focus:ring-offset-0 sm:text-sm transition-all"
                        placeholder="Details of any pending legal issues, or enter 'None' if applicable"
                        value={formData.pendingProsecutions}
                        onChange={handleInputChange}
                      />
                    </div>

                    <div>
                      <label htmlFor="riddorIncidentCount" className="block text-sm font-medium text-slate-300 mb-2">
                        RIDDOR Incidents Count (Last 3 Years)
                      </label>
                      <input
                        type="number"
                        name="riddorIncidentCount"
                        id="riddorIncidentCount"
                        className="block w-full rounded-lg border-0 bg-slate-700/30 px-4 py-3 text-white placeholder-slate-400 ring-1 ring-slate-600/50 focus:ring-2 focus:ring-green-500/50 focus:ring-offset-0 sm:text-sm transition-all"
                        placeholder="Number of RIDDOR incidents"
                        value={formData.riddorIncidentCount}
                        onChange={handleInputChange}
                      />
                    </div>

                    <div>
                      <label htmlFor="riddorIncidentDetails" className="block text-sm font-medium text-slate-300 mb-2">
                        RIDDOR Incidents Details (Last 3 Years)
                      </label>
                      <textarea
                        name="riddorIncidentDetails"
                        id="riddorIncidentDetails"
                        rows={3}
                        className="block w-full rounded-lg border-0 bg-slate-700/30 px-4 py-3 text-white placeholder-slate-400 ring-1 ring-slate-600/50 focus:ring-2 focus:ring-green-500/50 focus:ring-offset-0 sm:text-sm transition-all"
                        placeholder="Details of any RIDDOR incidents, or enter 'None' if applicable"
                        value={formData.riddorIncidentDetails}
                        onChange={handleInputChange}
                      />
                    </div>

                    <div>
                      <label htmlFor="cdmManagementEvidence" className="block text-sm font-medium text-slate-300 mb-2">
                        CDM Management Evidence
                      </label>
                      <textarea
                        name="cdmManagementEvidence"
                        id="cdmManagementEvidence"
                        rows={3}
                        className="block w-full rounded-lg border-0 bg-slate-700/30 px-4 py-3 text-white placeholder-slate-400 ring-1 ring-slate-600/50 focus:ring-2 focus:ring-green-500/50 focus:ring-offset-0 sm:text-sm transition-all"
                        placeholder="Evidence of CDM management procedures and systems"
                        value={formData.cdmManagementEvidence}
                        onChange={handleInputChange}
                      />
                    </div>

                    <div>
                      <label htmlFor="nearMissProcedure" className="block text-sm font-medium text-slate-300 mb-2">
                        Near Miss Procedure
                      </label>
                      <textarea
                        name="nearMissProcedure"
                        id="nearMissProcedure"
                        rows={3}
                        className="block w-full rounded-lg border-0 bg-slate-700/30 px-4 py-3 text-white placeholder-slate-400 ring-1 ring-slate-600/50 focus:ring-2 focus:ring-green-500/50 focus:ring-offset-0 sm:text-sm transition-all"
                        placeholder="Description of near miss reporting and investigation procedures"
                        value={formData.nearMissProcedure}
                        onChange={handleInputChange}
                      />
                    </div>

                    <div>
                      <label htmlFor="qualityProcedureEvidence" className="block text-sm font-medium text-slate-300 mb-2">
                        Quality Procedure Evidence
                      </label>
                      <textarea
                        name="qualityProcedureEvidence"
                        id="qualityProcedureEvidence"
                        rows={3}
                        className="block w-full rounded-lg border-0 bg-slate-700/30 px-4 py-3 text-white placeholder-slate-400 ring-1 ring-slate-600/50 focus:ring-2 focus:ring-green-500/50 focus:ring-offset-0 sm:text-sm transition-all"
                        placeholder="Evidence of quality management procedures and controls"
                        value={formData.qualityProcedureEvidence}
                        onChange={handleInputChange}
                      />
                    </div>
                  </div>

                  <div className="space-y-4">
                    <h3 className="text-lg font-medium text-white">Policy Documentation</h3>
                    
                    <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
                      <div>
                        <label htmlFor="healthSafetyPolicyDate" className="block text-sm font-medium text-slate-300 mb-2">
                          Health & Safety Policy Date
                        </label>
                        <input
                          type="date"
                          name="healthSafetyPolicyDate"
                          id="healthSafetyPolicyDate"
                          className="block w-full rounded-lg border-0 bg-slate-700/30 px-4 py-3 text-white placeholder-slate-400 ring-1 ring-slate-600/50 focus:ring-2 focus:ring-green-500/50 focus:ring-offset-0 sm:text-sm transition-all"
                          value={formData.healthSafetyPolicyDate}
                          onChange={handleInputChange}
                        />
                      </div>

                      <div>
                        <label htmlFor="environmentalPolicyDate" className="block text-sm font-medium text-slate-300 mb-2">
                          Environmental Policy Date
                        </label>
                        <input
                          type="date"
                          name="environmentalPolicyDate"
                          id="environmentalPolicyDate"
                          className="block w-full rounded-lg border-0 bg-slate-700/30 px-4 py-3 text-white placeholder-slate-400 ring-1 ring-slate-600/50 focus:ring-2 focus:ring-green-500/50 focus:ring-offset-0 sm:text-sm transition-all"
                          value={formData.environmentalPolicyDate}
                          onChange={handleInputChange}
                        />
                      </div>

                      <div>
                        <label htmlFor="modernSlaveryPolicyDate" className="block text-sm font-medium text-slate-300 mb-2">
                          Modern Slavery Policy Date
                        </label>
                        <input
                          type="date"
                          name="modernSlaveryPolicyDate"
                          id="modernSlaveryPolicyDate"
                          className="block w-full rounded-lg border-0 bg-slate-700/30 px-4 py-3 text-white placeholder-slate-400 ring-1 ring-slate-600/50 focus:ring-2 focus:ring-green-500/50 focus:ring-offset-0 sm:text-sm transition-all"
                          value={formData.modernSlaveryPolicyDate}
                          onChange={handleInputChange}
                        />
                      </div>

                      <div>
                        <label htmlFor="substanceMisusePolicyDate" className="block text-sm font-medium text-slate-300 mb-2">
                          Substance Misuse Policy Date
                        </label>
                        <input
                          type="date"
                          name="substanceMisusePolicyDate"
                          id="substanceMisusePolicyDate"
                          className="block w-full rounded-lg border-0 bg-slate-700/30 px-4 py-3 text-white placeholder-slate-400 ring-1 ring-slate-600/50 focus:ring-2 focus:ring-green-500/50 focus:ring-offset-0 sm:text-sm transition-all"
                          value={formData.substanceMisusePolicyDate}
                          onChange={handleInputChange}
                        />
                      </div>

                      <div>
                        <label htmlFor="gdprPolicyDate" className="block text-sm font-medium text-slate-300 mb-2">
                          GDPR Policy Date
                        </label>
                        <input
                          type="date"
                          name="gdprPolicyDate"
                          id="gdprPolicyDate"
                          className="block w-full rounded-lg border-0 bg-slate-700/30 px-4 py-3 text-white placeholder-slate-400 ring-1 ring-slate-600/50 focus:ring-2 focus:ring-green-500/50 focus:ring-offset-0 sm:text-sm transition-all"
                          value={formData.gdprPolicyDate}
                          onChange={handleInputChange}
                        />
                      </div>
                    </div>

                    <div>
                      <label htmlFor="rightToWorkMethod" className="block text-sm font-medium text-slate-300 mb-2">
                        Right to Work Monitoring Method
                      </label>
                      <textarea
                        name="rightToWorkMethod"
                        id="rightToWorkMethod"
                        rows={3}
                        className="block w-full rounded-lg border-0 bg-slate-700/30 px-4 py-3 text-white placeholder-slate-400 ring-1 ring-slate-600/50 focus:ring-2 focus:ring-green-500/50 focus:ring-offset-0 sm:text-sm transition-all"
                        placeholder="Method used to monitor and verify right to work for all employees"
                        value={formData.rightToWorkMethod}
                        onChange={handleInputChange}
                      />
                    </div>

                    <div>
                      <label htmlFor="cyberIncidentLast3Years" className="block text-sm font-medium text-slate-300 mb-2">
                        Cyber Security Incidents (Last 3 Years)
                      </label>
                      <textarea
                        name="cyberIncidentLast3Years"
                        id="cyberIncidentLast3Years"
                        rows={3}
                        className="block w-full rounded-lg border-0 bg-slate-700/30 px-4 py-3 text-white placeholder-slate-400 ring-1 ring-slate-600/50 focus:ring-2 focus:ring-green-500/50 focus:ring-offset-0 sm:text-sm transition-all"
                        placeholder="Details of any cyber security incidents, or enter 'None' if applicable"
                        value={formData.cyberIncidentLast3Years}
                        onChange={handleInputChange}
                      />
                    </div>

                    <div>
                      <label htmlFor="legalClarifications" className="block text-sm font-medium text-slate-300 mb-2">
                        Legal Clarifications
                      </label>
                      <textarea
                        name="legalClarifications"
                        id="legalClarifications"
                        rows={3}
                        className="block w-full rounded-lg border-0 bg-slate-700/30 px-4 py-3 text-white placeholder-slate-400 ring-1 ring-slate-600/50 focus:ring-2 focus:ring-green-500/50 focus:ring-offset-0 sm:text-sm transition-all"
                        placeholder="Any legal clarifications or additional information required"
                        value={formData.legalClarifications}
                        onChange={handleInputChange}
                      />
                    </div>
                  </div>
                  
                  {/* Document Uploads for Insurance & Compliance */}
                  <div className="mt-8 space-y-6">
                    <h3 className="text-lg font-medium text-white">Supporting Documents</h3>
                    
                    <div className="space-y-6">
                      <h4 className="text-md font-medium text-slate-200">Insurance Certificates</h4>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <FileUpload
                          fieldName="publicLiabilityCertificate"
                          label="Public Liability Certificate"
                          accept=".pdf,.jpg,.jpeg,.png"
                          required={true}
                        />
                        
                        <FileUpload
                          fieldName="employersLiabilityCertificate"
                          label="Employers Liability Certificate"
                          accept=".pdf,.jpg,.jpeg,.png"
                          required={true}
                        />
                        
                        <FileUpload
                          fieldName="professionalIndemnityCertificate"
                          label="Professional Indemnity Certificate"
                          accept=".pdf,.jpg,.jpeg,.png"
                        />
                      </div>
                      
                      <h4 className="text-md font-medium text-slate-200 mt-8">Policy Documents</h4>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <FileUpload
                          fieldName="healthSafetyPolicy"
                          label="Health & Safety Policy"
                          accept=".pdf,.doc,.docx"
                        />
                        
                        <FileUpload
                          fieldName="environmentalPolicy"
                          label="Environmental Policy"
                          accept=".pdf,.doc,.docx"
                        />
                        
                        <FileUpload
                          fieldName="modernSlaveryPolicy"
                          label="Modern Slavery Policy"
                          accept=".pdf,.doc,.docx"
                        />
                        
                        <FileUpload
                          fieldName="gdprPolicy"
                          label="GDPR Policy"
                          accept=".pdf,.doc,.docx"
                        />
                      </div>
                      
                      <h4 className="text-md font-medium text-slate-200 mt-8">Compliance Reports</h4>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <FileUpload
                          fieldName="riddorReports"
                          label="RIDDOR Reports (if applicable)"
                          accept=".pdf,.doc,.docx"
                        />
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Step 6: Agreement & Submission */}
              {currentStep === 6 && (
                <div className="space-y-6">
                  <h2 className="text-xl font-semibold text-white mb-6">Agreement & Submission</h2>
                  
                  {/* Review Summary */}
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    <div className="rounded-lg bg-slate-800/60 ring-1 ring-white/10 p-5">
                      <h3 className="text-sm font-medium text-slate-200 mb-3">Company & Contact</h3>
                      <dl className="text-sm text-slate-300 space-y-2">
                        <div className="flex justify-between"><dt>Company</dt><dd className="text-slate-100">{formData.companyName || '—'}</dd></div>
                        <div className="flex justify-between"><dt>Contact</dt><dd className="text-slate-100">{formData.contactName || '—'}</dd></div>
                        <div className="flex justify-between"><dt>Email</dt><dd className="text-slate-100">{formData.email || '—'}</dd></div>
                      </dl>
                    </div>
                    <div className="rounded-lg bg-slate-800/60 ring-1 ring-white/10 p-5">
                      <h3 className="text-sm font-medium text-slate-200 mb-3">Geographic Coverage</h3>
                      <div className="text-sm text-slate-300">
                        <div><span className="text-slate-400">Summary:</span> <span className="text-slate-100">{formData.coverage || '—'}</span></div>
                        <div className="mt-2"><span className="text-slate-400">Regions:</span> <span className="text-slate-100">{(formData.coverageRegions && formData.coverageRegions.length) ? formData.coverageRegions.join(', ') : '—'}</span></div>
                        {formData.coverageRegion && (<div className="mt-2"><span className="text-slate-400">Other:</span> <span className="text-slate-100">{formData.coverageRegion}</span></div>)}
                      </div>
                    </div>
                  </div>
                  
                  <div className="space-y-4">
                    <h3 className="text-lg font-medium text-white">Terms & Agreements</h3>
                    
                    <div className="space-y-4">
                      <div className="flex items-start">
                        <input
                          type="checkbox"
                          name="agreeToTerms"
                          id="agreeToTerms"
                          checked={formData.agreeToTerms}
                          onChange={(e) => setFormData({...formData, agreeToTerms: e.target.checked})}
                          className="h-4 w-4 rounded border-slate-600 bg-slate-700 text-green-600 focus:ring-green-500 focus:ring-offset-slate-900 mt-1"
                        />
                        <label htmlFor="agreeToTerms" className="ml-3 text-sm text-slate-300">
                          I agree to work to Saber Renewables terms and conditions *
                        </label>
                      </div>

                      <div className="flex items-start">
                        <input
                          type="checkbox"
                          name="agreeToCodes"
                          id="agreeToCodes"
                          checked={formData.agreeToCodes}
                          onChange={(e) => setFormData({...formData, agreeToCodes: e.target.checked})}
                          className="h-4 w-4 rounded border-slate-600 bg-slate-700 text-green-600 focus:ring-green-500 focus:ring-offset-slate-900 mt-1"
                        />
                        <label htmlFor="agreeToCodes" className="ml-3 text-sm text-slate-300">
                          I agree to adhere to industry codes of practice and safety standards *
                        </label>
                      </div>

                      <div className="flex items-start">
                        <input
                          type="checkbox"
                          name="dataProcessingConsent"
                          id="dataProcessingConsent"
                          checked={formData.dataProcessingConsent}
                          onChange={(e) => setFormData({...formData, dataProcessingConsent: e.target.checked})}
                          className="h-4 w-4 rounded border-slate-600 bg-slate-700 text-green-600 focus:ring-green-500 focus:ring-offset-slate-900 mt-1"
                        />
                        <label htmlFor="dataProcessingConsent" className="ml-3 text-sm text-slate-300">
                          I consent to the processing of my personal data for partnership purposes *
                        </label>
                      </div>

                      <div className="flex items-start">
                        <input
                          type="checkbox"
                          name="marketingConsent"
                          id="marketingConsent"
                          checked={formData.marketingConsent}
                          onChange={(e) => setFormData({...formData, marketingConsent: e.target.checked})}
                          className="h-4 w-4 rounded border-slate-600 bg-slate-700 text-green-600 focus:ring-green-500 focus:ring-offset-slate-900 mt-1"
                        />
                        <label htmlFor="marketingConsent" className="ml-3 text-sm text-slate-300">
                          I consent to receiving marketing communications (optional)
                        </label>
                      </div>

                      <div className="flex items-center">
                        <input
                          type="checkbox"
                          name="nationwideCoverage"
                          id="nationwideCoverage"
                          checked={formData.nationwideCoverage}
                          onChange={(e) => setFormData({...formData, nationwideCoverage: e.target.checked})}
                          className="h-4 w-4 rounded border-slate-600 bg-slate-700 text-green-600 focus:ring-green-500 focus:ring-offset-slate-900"
                        />
                        <label htmlFor="nationwideCoverage" className="ml-3 text-sm text-slate-300">
                          Nationwide coverage available
                        </label>
                      </div>

                      <div className="flex items-center">
                        <input
                          type="checkbox"
                          name="contractsReviewed"
                          id="contractsReviewed"
                          checked={formData.contractsReviewed}
                          onChange={(e) => setFormData({...formData, contractsReviewed: e.target.checked})}
                          className="h-4 w-4 rounded border-slate-600 bg-slate-700 text-green-600 focus:ring-green-500 focus:ring-offset-slate-900"
                        />
                        <label htmlFor="contractsReviewed" className="ml-3 text-sm text-slate-300">
                          Contracts have been reviewed by an authorized signatory
                        </label>
                      </div>

                      <div className="flex items-center">
                        <input
                          type="checkbox"
                          name="receivedContractPack"
                          id="receivedContractPack"
                          checked={formData.receivedContractPack}
                          onChange={(e) => setFormData({...formData, receivedContractPack: e.target.checked})}
                          className="h-4 w-4 rounded border-slate-600 bg-slate-700 text-green-600 focus:ring-green-500 focus:ring-offset-slate-900"
                        />
                        <label htmlFor="receivedContractPack" className="ml-3 text-sm text-slate-300">
                          I have received and reviewed the contract overview pack
                        </label>
                      </div>
                    </div>
                  </div>

                  <div className="space-y-4">
                    <h3 className="text-lg font-medium text-white">Additional Information</h3>
                    
                    <div>
                      <label htmlFor="additionalInformation" className="block text-sm font-medium text-slate-300 mb-2">
                        Additional Information
                      </label>
                      <textarea
                        name="additionalInformation"
                        id="additionalInformation"
                        rows={4}
                        className="block w-full rounded-lg border-0 bg-slate-700/30 px-4 py-3 text-white placeholder-slate-400 ring-1 ring-slate-600/50 focus:ring-2 focus:ring-green-500/50 focus:ring-offset-0 sm:text-sm transition-all"
                        placeholder="Any additional information you would like to provide about your company, capabilities, or partnership interests"
                        value={formData.additionalInformation}
                        onChange={handleInputChange}
                      />
                    </div>

                    <div>
                      <label htmlFor="notes" className="block text-sm font-medium text-slate-300 mb-2">
                        Notes
                      </label>
                      <textarea
                        name="notes"
                        id="notes"
                        rows={3}
                        className="block w-full rounded-lg border-0 bg-slate-700/30 px-4 py-3 text-white placeholder-slate-400 ring-1 ring-slate-600/50 focus:ring-2 focus:ring-green-500/50 focus:ring-offset-0 sm:text-sm transition-all"
                        placeholder="Internal notes or comments"
                        value={formData.notes}
                        onChange={handleInputChange}
                      />
                    </div>

                    <div>
                      <label htmlFor="clarifications" className="block text-sm font-medium text-slate-300 mb-2">
                        Clarifications
                      </label>
                      <textarea
                        name="clarifications"
                        id="clarifications"
                        rows={3}
                        className="block w-full rounded-lg border-0 bg-slate-700/30 px-4 py-3 text-white placeholder-slate-400 ring-1 ring-slate-600/50 focus:ring-2 focus:ring-green-500/50 focus:ring-offset-0 sm:text-sm transition-all"
                        placeholder="Any clarifications needed or questions you have"
                        value={formData.clarifications}
                        onChange={handleInputChange}
                      />
                    </div>

                    <div>
                      <label htmlFor="invitationCode" className="block text-sm font-medium text-slate-300 mb-2">
                        Invitation Code
                      </label>
                      <input
                        type="text"
                        name="invitationCode"
                        id="invitationCode"
                        className="block w-full rounded-lg border-0 bg-slate-700/30 px-4 py-3 text-white placeholder-slate-400 ring-1 ring-slate-600/50 focus:ring-2 focus:ring-green-500/50 focus:ring-offset-0 sm:text-sm transition-all"
                        placeholder="Enter your invitation code if provided"
                        value={formData.invitationCode}
                        onChange={handleInputChange}
                      />
                    </div>
                  </div>
                  
                  {/* Document Uploads for Additional Documents */}
                  <div className="mt-8 space-y-6">
                    <h3 className="text-lg font-medium text-white">Additional Documents</h3>
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <FileUpload
                        fieldName="companyRegistration"
                        label="Company Registration Certificate"
                        accept=".pdf,.jpg,.jpeg,.png"
                      />
                      
                      <FileUpload
                        fieldName="additionalDocuments"
                        label="Other Supporting Documents"
                        accept=".pdf,.doc,.docx,.jpg,.jpeg,.png"
                      />
                    </div>
                  </div>

                  <div className="bg-slate-800/40 border border-slate-700/50 rounded-lg p-4">
                    <p className="text-sm text-slate-300">
                      By submitting this application, you confirm that all information provided is accurate and complete. 
                      This application will be reviewed by our partner development team and you will be contacted within 5 business days.
                    </p>
                  </div>
                </div>
              )}

              {/* Navigation Buttons */}
              <div className="flex justify-between items-center pt-8 border-t border-slate-700/50">
                <button
                  type="button"
                  onClick={prevStep}
                  disabled={currentStep === 1}
                  className="inline-flex items-center px-4 py-2 text-sm font-medium text-slate-300 hover:text-white disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  ← Previous
                </button>

                {/* Save Progress Button & Status */}
                <div className="flex items-center space-x-4">
                  <button
                    type="button"
                    onClick={() => saveDraft(true)}
                    disabled={saving || !formData.invitationCode}
                    className="inline-flex items-center px-4 py-2 text-sm font-medium text-blue-400 hover:text-blue-300 disabled:opacity-50 disabled:cursor-not-allowed transition-colors border border-blue-400/30 rounded-md hover:border-blue-400/50"
                  >
                    {saving ? (
                      <>
                        <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-blue-400" fill="none" viewBox="0 0 24 24">
                          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                        </svg>
                        Saving...
                      </>
                    ) : (
                      <>
                        <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-3m-1 4l-3 3m0 0l-3-3m3 3V4" />
                        </svg>
                        Save Progress
                      </>
                    )}
                  </button>
                  
                  {/* Auto-save Status Indicator */}
                  {autoSaveStatus && (
                    <div className={`text-xs px-2 py-1 rounded ${
                      autoSaveStatus === 'saving' ? 'text-yellow-400 bg-yellow-400/10' :
                      autoSaveStatus === 'saved' ? 'text-green-400 bg-green-400/10' :
                      autoSaveStatus === 'error' ? 'text-red-400 bg-red-400/10' : ''
                    }`}>
                      {autoSaveStatus === 'saving' && '💾 Saving...'}
                      {autoSaveStatus === 'saved' && '✅ Saved'}
                      {autoSaveStatus === 'error' && '❌ Save failed'}
                    </div>
                  )}
                  
                  {/* Last Saved Indicator */}
                  {lastSaved && !autoSaveStatus && (
                    <div className="text-xs text-slate-400">
                      Last saved: {lastSaved.toLocaleTimeString()}
                    </div>
                  )}
                </div>

                <div className="flex space-x-3">
                  {currentStep < 6 ? (
                    <button
                      type="button"
                      onClick={nextStep}
                      className="inline-flex items-center px-6 py-2 text-sm font-semibold text-white bg-green-600 rounded-lg hover:bg-green-500 focus:outline-none focus:ring-2 focus:ring-green-500/50 transition-colors"
                    >
                      Next →
                    </button>
                  ) : (
                    <>
                      <button
                        type="button"
                        onClick={downloadJSON}
                        className="inline-flex items-center px-6 py-2 text-sm font-semibold text-slate-200 bg-slate-600 rounded-lg hover:bg-slate-500 focus:outline-none focus:ring-2 focus:ring-slate-400/50 transition-colors"
                      >
                        <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                        </svg>
                        Download JSON
                      </button>
                      <button
                        type="button"
                        onClick={handleSubmit}
                        disabled={isSubmitting}
                        className="inline-flex items-center px-6 py-2 text-sm font-semibold text-white bg-green-600 rounded-lg hover:bg-green-500 focus:outline-none focus:ring-2 focus:ring-green-500/50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                      >
                        {isSubmitting ? 'Submitting...' : 'Submit Application'}
                      </button>
                    </>
                  )}
                </div>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  )
}
